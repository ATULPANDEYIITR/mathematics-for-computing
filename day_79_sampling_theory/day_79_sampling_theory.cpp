#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

enum class SamplingMethod {
    SimpleRandom,
    Stratified,
    Systematic
};

struct Record {
    int id;
    string stratum;
    double value;
};

struct Sample {
    SamplingMethod method;
    vector<Record> records;
    size_t populationSize;
    uint32_t seed;
};

struct ProtectionResult {
    double populationMean;
    double sampleMean;
    double standardError;
    double lowerBound;
    double upperBound;
};

class SamplingException : public runtime_error {
public:
    explicit SamplingException(const string& message)
        : runtime_error(message) {}
};

class SamplingEngine {
private:
    vector<Record> population;
    mt19937 generator;

    void validateSampleSize(size_t n) const {
        if (n == 0 || n > population.size()) {
            throw SamplingException(
                "Sample size must be between 1 and population size."
            );
        }
    }

    static double mean(const vector<double>& values) {
        if (values.empty()) {
            throw SamplingException("Cannot calculate empty mean.");
        }

        return accumulate(
            values.begin(),
            values.end(),
            0.0
        ) / values.size();
    }

public:
    explicit SamplingEngine(
        vector<Record> records,
        uint32_t seed = 2026
    )
        : population(move(records)), generator(seed) {

        if (population.empty()) {
            throw SamplingException("Population cannot be empty.");
        }

        set<int> ids;

        for (const auto& record : population) {
            if (record.id <= 0 || !ids.insert(record.id).second) {
                throw SamplingException("Invalid or duplicate record ID.");
            }

            if (record.stratum.empty()) {
                throw SamplingException("Stratum cannot be empty.");
            }

            if (!isfinite(record.value)) {
                throw SamplingException("Outcome must be finite.");
            }
        }
    }

    size_t populationSize() const {
        return population.size();
    }

    Sample simpleRandom(size_t n) {
        validateSampleSize(n);

        vector<Record> shuffled = population;

        shuffle(
            shuffled.begin(),
            shuffled.end(),
            generator
        );

        shuffled.resize(n);

        return {
            SamplingMethod::SimpleRandom,
            move(shuffled),
            population.size(),
            0
        };
    }

    Sample stratified(size_t n) {
        validateSampleSize(n);

        map<string, vector<Record>> groups;

        for (const auto& record : population) {
            groups[record.stratum].push_back(record);
        }

        const size_t H = groups.size();

        if (n < H) {
            throw SamplingException(
                "Sample cannot represent every stratum."
            );
        }

        struct Allocation {
            string name;
            size_t capacity;
            size_t count;
            double remainder;
        };

        vector<Allocation> allocations;

        for (const auto& [name, members] : groups) {
            double raw =
                static_cast<double>(n) * members.size()
                / population.size();

            allocations.push_back({
                name,
                members.size(),
                static_cast<size_t>(floor(raw)),
                raw - floor(raw)
            });
        }

        for (auto& allocation : allocations) {
            if (allocation.count == 0) {
                allocation.count = 1;
            }
        }

        size_t allocated = 0;

        for (const auto& allocation : allocations) {
            allocated += allocation.count;
        }

        while (allocated > n) {
            auto candidate = allocations.end();

            for (auto it = allocations.begin();
                 it != allocations.end(); ++it) {

                if (it->count > 1 &&
                    (candidate == allocations.end() ||
                     it->remainder < candidate->remainder)) {
                    candidate = it;
                }
            }

            if (candidate == allocations.end()) {
                throw SamplingException("Allocation is infeasible.");
            }

            candidate->count--;
            allocated--;
        }

        while (allocated < n) {
            auto candidate = allocations.end();

            for (auto it = allocations.begin();
                 it != allocations.end(); ++it) {

                if (it->count < it->capacity &&
                    (candidate == allocations.end() ||
                     it->remainder > candidate->remainder)) {
                    candidate = it;
                }
            }

            if (candidate == allocations.end()) {
                throw SamplingException("Allocation capacity exceeded.");
            }

            candidate->count++;
            candidate->remainder = -1;
            allocated++;
        }

        vector<Record> selected;

        for (const auto& allocation : allocations) {
            auto members = groups.at(allocation.name);

            shuffle(
                members.begin(),
                members.end(),
                generator
            );

            selected.insert(
                selected.end(),
                members.begin(),
                members.begin() + allocation.count
            );
        }

        shuffle(
            selected.begin(),
            selected.end(),
            generator
        );

        return {
            SamplingMethod::Stratified,
            move(selected),
            population.size(),
            0
        };
    }

    Sample systematic(size_t n) {
        validateSampleSize(n);

        const double interval =
            static_cast<double>(population.size()) / n;

        uniform_real_distribution<double> distribution(
            0.0,
            interval
        );

        const double start = distribution(generator);

        vector<Record> selected;

        for (size_t i = 0; i < n; ++i) {
            size_t index = static_cast<size_t>(
                floor(start + i * interval)
            );

            index = min(index, population.size() - 1);

            selected.push_back(population[index]);
        }

        return {
            SamplingMethod::Systematic,
            move(selected),
            population.size(),
            0
        };
    }

    static double sampleVariance(
        const vector<double>& values
    ) {
        if (values.size() < 2) {
            throw SamplingException(
                "At least two observations are required."
            );
        }

        const double average = mean(values);

        double sum = 0;

        for (double value : values) {
            sum += pow(value - average, 2);
        }

        return sum / (values.size() - 1);
    }

    static ProtectionResult analyze(
        const Sample& sample,
        const vector<Record>& population
    ) {
        if (sample.records.size() < 2) {
            throw SamplingException("Sample is too small.");
        }

        vector<double> values;
        vector<double> allValues;

        for (const auto& record : sample.records) {
            values.push_back(record.value);
        }

        for (const auto& record : population) {
            allValues.push_back(record.value);
        }

        const double sampleMean = mean(values);
        const double populationMean = mean(allValues);

        const double variance = sampleVariance(values);
        const double n = values.size();
        const double N = population.size();

        const double fpc = sqrt(
            (N - n) / (N - 1)
        );

        const double standardError =
            sqrt(variance / n) * fpc;

        const double margin = 1.96 * standardError;

        return {
            populationMean,
            sampleMean,
            standardError,
            sampleMean - margin,
            sampleMean + margin
        };
    }

    static double cochranSampleSize(
        double z,
        double margin,
        double proportion,
        size_t populationSize
    ) {
        if (
            z <= 0 ||
            margin <= 0 ||
            margin >= 1 ||
            proportion <= 0 ||
            proportion >= 1 ||
            populationSize == 0
        ) {
            throw SamplingException("Invalid sample-size parameters.");
        }

        const double n0 =
            z * z * proportion * (1 - proportion)
            / (margin * margin);

        if (populationSize == 1) {
            return 1;
        }

        const double adjusted =
            n0 / (
                1 + (n0 - 1) / populationSize
            );

        return min(
            static_cast<double>(populationSize),
            ceil(adjusted)
        );
    }

    const vector<Record>& getPopulation() const {
        return population;
    }
};

class GovernanceEngine {
public:
    struct BranchPolicy {
        string branchName;
        int requiredApprovals;
        vector<string> requiredChecks;
        bool blockDirectPush;
        bool blockForcePush;
        bool requireResolvedConversations;
        bool requireLinearHistory;
    };

    struct PullRequest {
        int id;
        string sourceBranch;
        string targetBranch;
        bool open;
        bool draft;
        bool conflicts;
        bool baseSynchronized;
        set<string> approvals;
        set<string> requestedChanges;
        map<string, bool> checks;
        int unresolvedConversations;
        bool linearHistory;
    };

    struct Decision {
        bool eligible;
        vector<string> reasons;
    };

    static Decision evaluate(
        const PullRequest& pr,
        const BranchPolicy& policy
    ) {
        vector<string> reasons;

        if (!pr.open) {
            reasons.push_back("Pull Request is not open.");
        }

        if (pr.draft) {
            reasons.push_back("Draft Pull Request cannot be merged.");
        }

        if (pr.sourceBranch.empty() ||
            pr.targetBranch != policy.branchName) {
            reasons.push_back("Invalid source or target branch.");
        }

        if (pr.sourceBranch == pr.targetBranch) {
            reasons.push_back("Source and target branches must differ.");
        }

        if (pr.conflicts) {
            reasons.push_back("Merge conflicts must be resolved.");
        }

        if (!pr.baseSynchronized) {
            reasons.push_back("Source branch must be synchronized.");
        }

        if (static_cast<int>(pr.approvals.size()) <
            policy.requiredApprovals) {
            reasons.push_back("Insufficient distinct approvals.");
        }

        if (!pr.requestedChanges.empty()) {
            reasons.push_back("Outstanding change requests exist.");
        }

        for (const auto& check : policy.requiredChecks) {
            auto it = pr.checks.find(check);

            if (it == pr.checks.end() || !it->second) {
                reasons.push_back(
                    "Required check missing or failed: " + check
                );
            }
        }

        if (policy.requireResolvedConversations &&
            pr.unresolvedConversations > 0) {
            reasons.push_back(
                "Unresolved review conversations remain."
            );
        }

        if (policy.requireLinearHistory &&
            !pr.linearHistory) {
            reasons.push_back("Linear history is required.");
        }

        return {
            reasons.empty(),
            move(reasons)
        };
    }
};

vector<Record> generatePopulation(size_t size) {
    mt19937 rng(2026);

    vector<string> departments = {
        "Engineering",
        "Finance",
        "Operations",
        "Research"
    };

    vector<double> probabilities = {
        0.40,
        0.20,
        0.25,
        0.15
    };

    discrete_distribution<int> departmentDistribution(
        probabilities.begin(),
        probabilities.end()
    );

    uniform_real_distribution<double> outcomeDistribution(
        40.0,
        90.0
    );

    vector<Record> population;

    for (size_t i = 0; i < size; ++i) {
        population.push_back({
            static_cast<int>(i + 1),
            departments[departmentDistribution(rng)],
            outcomeDistribution(rng)
        });
    }

    return population;
}

void printSample(
    const string& name,
    const Sample& sample,
    const vector<Record>& population
) {
    auto result = SamplingEngine::analyze(
        sample,
        population
    );

    cout << "\n" << name << "\n";
    cout << "Sample size: " << sample.records.size() << "\n";
    cout << fixed << setprecision(3);
    cout << "Population mean: " << result.populationMean << "\n";
    cout << "Sample mean: " << result.sampleMean << "\n";
    cout << "Standard error: " << result.standardError << "\n";
    cout << "Approximate 95% CI: ["
         << result.lowerBound << ", "
         << result.upperBound << "]\n";

    map<string, int> counts;

    for (const auto& record : sample.records) {
        counts[record.stratum]++;
    }

    cout << "Stratum counts:\n";

    for (const auto& [name, count] : counts) {
        cout << "  " << name << ": " << count << "\n";
    }
}

int main() {
    try {
        auto population = generatePopulation(1000);

        SamplingEngine engine(population, 17);

        const size_t required = static_cast<size_t>(
            SamplingEngine::cochranSampleSize(
                1.96,
                0.05,
                0.5,
                population.size()
            )
        );

        cout << "SAMPLING THEORY AND GOVERNANCE ENGINE\n";
        cout << "Population: " << population.size() << "\n";
        cout << "Required sample: " << required << "\n";

        auto randomSample = engine.simpleRandom(100);
        auto stratifiedSample = engine.stratified(100);
        auto systematicSample = engine.systematic(100);

        printSample(
            "Simple random sampling",
            randomSample,
            population
        );

        printSample(
            "Stratified sampling",
            stratifiedSample,
            population
        );

        printSample(
            "Systematic sampling",
            systematicSample,
            population
        );

        GovernanceEngine::BranchPolicy policy {
            "main",
            2,
            {"build", "unit-tests", "security-scan"},
            true,
            true,
            true,
            false
        };

        GovernanceEngine::PullRequest pr {
            101,
            "feature/sampling",
            "main",
            true,
            false,
            false,
            true,
            {"reviewer-1", "reviewer-2"},
            {},
            {
                {"build", true},
                {"unit-tests", true},
                {"security-scan", true}
            },
            0,
            true
        };

        auto decision = GovernanceEngine::evaluate(
            pr,
            policy
        );

        cout << "\nGovernance eligibility: "
             << (decision.eligible ? "ELIGIBLE" : "BLOCKED")
             << "\n";

        for (const auto& reason : decision.reasons) {
            cout << "  " << reason << "\n";
        }

        // Demonstrate invalid input handling.
        try {
            engine.simpleRandom(0);
        } catch (const SamplingException& error) {
            cout << "\nInvalid sample rejected: "
                 << error.what() << "\n";
        }

    } catch (const exception& error) {
        cerr << "Application error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
