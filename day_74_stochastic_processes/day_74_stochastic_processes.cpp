#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;

enum class State {
    OPERATIONAL,
    DEGRADED,
    FAILED,
    RECOVERING
};

string stateName(State state) {
    switch (state) {
        case State::OPERATIONAL: return "OPERATIONAL";
        case State::DEGRADED: return "DEGRADED";
        case State::FAILED: return "FAILED";
        case State::RECOVERING: return "RECOVERING";
    }
    throw runtime_error("Unknown state.");
}

struct Transition {
    State destination;
    double probability;
};

struct SimulationResult {
    vector<State> path;
    State finalState;
    bool absorbed;
    size_t steps;
};

class MarkovModel {
private:
    unordered_map<State, vector<Transition>> transitions;

public:
    void addState(
        State source,
        const vector<Transition>& destinations
    ) {
        if (destinations.empty()) {
            throw invalid_argument("A state needs outgoing transitions.");
        }

        if (transitions.count(source)) {
            throw invalid_argument("Duplicate state definition.");
        }

        double total = 0.0;

        for (const auto& edge : destinations) {
            if (
                !isfinite(edge.probability) ||
                edge.probability < 0.0 ||
                edge.probability > 1.0
            ) {
                throw invalid_argument("Invalid transition probability.");
            }

            total += edge.probability;
        }

        if (abs(total - 1.0) > 1e-9) {
            throw invalid_argument(
                "Transition probabilities must sum to one."
            );
        }

        transitions.emplace(source, destinations);
    }

    void validate() const {
        for (const auto& entry : transitions) {
            for (const auto& edge : entry.second) {
                if (!transitions.count(edge.destination)) {
                    throw invalid_argument(
                        "Transition references undefined state."
                    );
                }
            }
        }
    }

    bool contains(State state) const {
        return transitions.count(state) != 0;
    }

    bool isAbsorbing(State state) const {
        auto iterator = transitions.find(state);

        if (iterator == transitions.end()) {
            throw invalid_argument("Unknown state.");
        }

        const auto& edges = iterator->second;

        return edges.size() == 1 &&
            edges.front().destination == state &&
            abs(edges.front().probability - 1.0) < 1e-9;
    }

    State nextState(
        State current,
        mt19937_64& generator
    ) const {
        auto iterator = transitions.find(current);

        if (iterator == transitions.end()) {
            throw invalid_argument("Unknown current state.");
        }

        uniform_real_distribution<double> distribution(0.0, 1.0);
        double value = distribution(generator);
        double cumulative = 0.0;

        for (const auto& edge : iterator->second) {
            cumulative += edge.probability;

            if (value < cumulative) {
                return edge.destination;
            }
        }

        return iterator->second.back().destination;
    }

    SimulationResult simulate(
        State initial,
        size_t maximumSteps,
        uint64_t seed
    ) const {
        if (!contains(initial)) {
            throw invalid_argument("Invalid initial state.");
        }

        mt19937_64 generator(seed);

        vector<State> path;
        path.push_back(initial);

        State current = initial;

        for (size_t step = 0; step < maximumSteps; ++step) {
            if (isAbsorbing(current)) {
                break;
            }

            current = nextState(current, generator);
            path.push_back(current);
        }

        return {
            path,
            current,
            isAbsorbing(current),
            path.size() - 1
        };
    }

    vector<State> getStates() const {
        vector<State> result;

        for (const auto& entry : transitions) {
            result.push_back(entry.first);
        }

        sort(
            result.begin(),
            result.end(),
            [](State a, State b) {
                return static_cast<int>(a) < static_cast<int>(b);
            }
        );

        return result;
    }
};

struct GovernancePolicy {
    size_t requiredApprovals = 2;
    size_t requiredChecks = 3;
    bool requireNoOpenConversations = true;
    bool requireLinearHistory = false;
    bool permitForcePush = false;
    bool permitDirectPush = false;
};

struct PullRequest {
    string id;
    string sourceBranch;
    string targetBranch;
    bool open = true;
    bool draft = false;
    bool sourceUpToDate = true;
    bool mergeConflict = false;
    bool linearHistory = true;
    size_t approvals = 0;
    size_t openConversations = 0;
    map<string, bool> checks;
};

struct Eligibility {
    bool eligible;
    vector<string> reasons;
};

class MergeEligibilityEngine {
private:
    GovernancePolicy policy;

public:
    explicit MergeEligibilityEngine(GovernancePolicy configured)
        : policy(configured) {}

    Eligibility evaluate(const PullRequest& pr) const {
        vector<string> failures;

        if (pr.id.empty()) {
            failures.push_back("Pull request identifier is missing.");
        }

        if (pr.sourceBranch.empty() || pr.targetBranch.empty()) {
            failures.push_back("Both branches must be specified.");
        }

        if (pr.sourceBranch == pr.targetBranch) {
            failures.push_back("Source and target branches must differ.");
        }

        if (!pr.open) {
            failures.push_back("Pull request is not open.");
        }

        if (pr.draft) {
            failures.push_back("Draft pull requests cannot be merged.");
        }

        if (!pr.sourceUpToDate) {
            failures.push_back("Source branch requires synchronization.");
        }

        if (pr.mergeConflict) {
            failures.push_back("Merge conflicts must be resolved.");
        }

        if (pr.approvals < policy.requiredApprovals) {
            failures.push_back("Required approvals are not satisfied.");
        }

        if (
            policy.requireNoOpenConversations &&
            pr.openConversations > 0
        ) {
            failures.push_back("Review conversations remain unresolved.");
        }

        if (
            policy.requireLinearHistory &&
            !pr.linearHistory
        ) {
            failures.push_back("Linear history is required.");
        }

        size_t passingChecks = 0;

        for (const auto& check : pr.checks) {
            if (check.second) {
                passingChecks++;
            }
        }

        if (passingChecks < policy.requiredChecks) {
            failures.push_back("Required status checks are not satisfied.");
        }

        return {
            failures.empty(),
            failures
        };
    }

    void updatePolicy(const GovernancePolicy& configured) {
        policy = configured;
    }
};

class ReliabilityAnalyzer {
public:
    struct Statistics {
        double probability;
        double standardError;
        double lowerBound;
        double upperBound;
        double meanAbsorptionTime;
    };

    static Statistics estimateFailureProbability(
        const MarkovModel& model,
        State initial,
        size_t experiments,
        size_t maximumSteps,
        uint64_t seed
    ) {
        if (experiments == 0) {
            throw invalid_argument("Experiments must be positive.");
        }

        if (!model.isAbsorbing(State::FAILED)) {
            throw invalid_argument("FAILED must be absorbing.");
        }

        mt19937_64 generator(seed);

        uniform_int_distribution<uint64_t> seedDistribution(
            1,
            numeric_limits<uint64_t>::max()
        );

        size_t failures = 0;
        size_t totalFailureTime = 0;

        for (size_t i = 0; i < experiments; ++i) {
            auto result = model.simulate(
                initial,
                maximumSteps,
                seedDistribution(generator)
            );

            if (result.finalState == State::FAILED) {
                failures++;
                totalFailureTime += result.steps;
            }
        }

        double probability =
            static_cast<double>(failures) / experiments;

        double standardError = sqrt(
            probability * (1.0 - probability) / experiments
        );

        double meanTime = failures == 0
            ? numeric_limits<double>::quiet_NaN()
            : static_cast<double>(totalFailureTime) / failures;

        return {
            probability,
            standardError,
            max(0.0, probability - 1.96 * standardError),
            min(1.0, probability + 1.96 * standardError),
            meanTime
        };
    }
};

MarkovModel buildReliabilityModel() {
    MarkovModel model;

    model.addState(State::OPERATIONAL, {
        {State::OPERATIONAL, 0.65},
        {State::DEGRADED, 0.25},
        {State::FAILED, 0.10}
    });

    model.addState(State::DEGRADED, {
        {State::OPERATIONAL, 0.30},
        {State::DEGRADED, 0.40},
        {State::FAILED, 0.30}
    });

    model.addState(State::FAILED, {
        {State::FAILED, 1.0}
    });

    model.validate();

    return model;
}

void demonstrateRandomWalk() {
    cout << "\nRANDOM WALK\n";

    mt19937_64 generator(42);
    bernoulli_distribution upward(0.55);

    int position = 0;
    const int lower = -5;
    const int upper = 5;

    vector<int> path{position};

    for (int step = 0; step < 100; ++step) {
        if (position == lower || position == upper) {
            break;
        }

        position += upward(generator) ? 1 : -1;
        path.push_back(position);
    }

    cout << "Path: ";

    for (int value : path) {
        cout << value << " ";
    }

    cout << "\nFinal position: " << position;
    cout << "\nAbsorbed: "
         << boolalpha
         << (position == lower || position == upper)
         << "\n";
}

void demonstrateGovernance() {
    cout << "\nMERGE ELIGIBILITY ENGINE\n";

    GovernancePolicy policy;
    policy.requiredApprovals = 2;
    policy.requiredChecks = 3;
    policy.requireNoOpenConversations = true;
    policy.requireLinearHistory = true;

    PullRequest pr{
        "PR-104",
        "feature/payment-security",
        "main"
    };

    pr.approvals = 2;
    pr.sourceUpToDate = true;
    pr.mergeConflict = false;
    pr.linearHistory = true;
    pr.openConversations = 0;

    pr.checks = {
        {"unit-tests", true},
        {"integration-tests", true},
        {"security-scan", true},
        {"deployment-preview", true}
    };

    MergeEligibilityEngine engine(policy);
    Eligibility result = engine.evaluate(pr);

    cout << "Pull request: " << pr.id << "\n";
    cout << "Merge eligible: " << boolalpha << result.eligible << "\n";

    for (const auto& reason : result.reasons) {
        cout << "- " << reason << "\n";
    }

    // Demonstrate a failing governance condition.
    pr.checks["security-scan"] = false;
    pr.approvals = 1;
    pr.openConversations = 1;

    result = engine.evaluate(pr);

    cout << "\nAfter policy violations:\n";

    for (const auto& reason : result.reasons) {
        cout << "- " << reason << "\n";
    }
}

void runTests() {
    MarkovModel model = buildReliabilityModel();

    auto first = model.simulate(
        State::OPERATIONAL,
        50,
        42
    );

    auto second = model.simulate(
        State::OPERATIONAL,
        50,
        42
    );

    if (first.path.size() != second.path.size()) {
        throw runtime_error("Reproducibility test failed.");
    }

    for (size_t i = 0; i < first.path.size(); ++i) {
        if (first.path[i] != second.path[i]) {
            throw runtime_error("Seeded path mismatch.");
        }
    }

    GovernancePolicy policy;
    policy.requiredApprovals = 1;
    policy.requiredChecks = 2;

    PullRequest pr{
        "PR-TEST",
        "feature/test",
        "main"
    };

    pr.approvals = 1;
    pr.checks = {
        {"unit", true},
        {"security", true}
    };

    MergeEligibilityEngine engine(policy);

    if (!engine.evaluate(pr).eligible) {
        throw runtime_error("Valid pull request rejected.");
    }

    pr.mergeConflict = true;

    if (engine.evaluate(pr).eligible) {
        throw runtime_error("Conflicted pull request accepted.");
    }

    cout << "All C++17 validation tests passed.\n";
}

int main() {
    try {
        cout << fixed << setprecision(5);

        runTests();

        MarkovModel model = buildReliabilityModel();

        cout << "\nSTOCHASTIC PROCESS GOVERNANCE LAB\n";

        auto simulation = model.simulate(
            State::OPERATIONAL,
            30,
            42
        );

        cout << "\nMARKOV CHAIN\n";
        cout << "State path: ";

        for (State state : simulation.path) {
            cout << stateName(state) << " -> ";
        }

        cout << "\nFinal state: "
             << stateName(simulation.finalState);

        cout << "\nAbsorbed: "
             << boolalpha
             << simulation.absorbed
             << "\n";

        demonstrateRandomWalk();

        cout << "\nMONTE CARLO RELIABILITY\n";

        auto statistics =
            ReliabilityAnalyzer::estimateFailureProbability(
                model,
                State::OPERATIONAL,
                10000,
                100,
                12345
            );

        cout << "Failure probability: "
             << statistics.probability << "\n";

        cout << "Standard error: "
             << statistics.standardError << "\n";

        cout << "95% confidence interval: ["
             << statistics.lowerBound << ", "
             << statistics.upperBound << "]\n";

        cout << "Mean failure time: "
             << statistics.meanAbsorptionTime << "\n";

        demonstrateGovernance();

    } catch (const exception& error) {
        cerr << "Execution error: "
             << error.what() << "\n";

        return 1;
    }

    return 0;
}
