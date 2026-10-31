#include <algorithm>
#include <cmath>
#include <cstddef>
#include <exception>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

enum class ReviewState {
    Draft,
    Open,
    Approved,
    ChangesRequested,
    Merged,
    Closed
};

enum class CheckState {
    Pending,
    Passing,
    Failing
};

struct Review {
    std::string reviewer;
    bool eligible;
    ReviewState state;
};

struct StatusCheck {
    std::string name;
    CheckState state;
};

struct BranchProtection {
    int requiredApprovals{2};
    bool requirePassingChecks{true};
    bool requireConversationResolution{true};
    bool allowDirectPush{false};
    bool allowForcePush{false};
    bool requireLinearHistory{true};
};

struct PullRequest {
    int id;
    std::string sourceBranch;
    std::string targetBranch;
    std::vector<std::string> commits;
    std::vector<Review> reviews;
    std::vector<StatusCheck> checks;
    int unresolvedConversations{0};
    ReviewState state{ReviewState::Open};
    bool sourceUpToDate{false};
};

class ProbabilityError : public std::runtime_error {
public:
    explicit ProbabilityError(const std::string& message)
        : std::runtime_error(message) {}
};

class ProbabilitySpace {
private:
    std::map<int, double> probabilities_;

public:
    explicit ProbabilitySpace(std::map<int, double> probabilities)
        : probabilities_(std::move(probabilities)) {
        if (probabilities_.empty()) {
            throw ProbabilityError("Sample space cannot be empty.");
        }

        double total = 0.0;
        for (const auto& [outcome, probability] : probabilities_) {
            if (!std::isfinite(probability) || probability < 0.0 || probability > 1.0) {
                throw ProbabilityError("Invalid probability assigned to an outcome.");
            }
            total += probability;
        }

        if (std::abs(total - 1.0) > 1e-12) {
            throw ProbabilityError("Outcome probabilities must sum to one.");
        }
    }

    double probability(const std::set<int>& event) const {
        double result = 0.0;

        for (int outcome : event) {
            auto it = probabilities_.find(outcome);
            if (it == probabilities_.end()) {
                throw ProbabilityError("Event contains an outcome outside the sample space.");
            }
            result += it->second;
        }

        return result;
    }

    std::set<int> sampleSpace() const {
        std::set<int> result;
        for (const auto& [outcome, probability] : probabilities_) {
            static_cast<void>(probability);
            result.insert(outcome);
        }
        return result;
    }
};

std::set<int> setUnion(
    const std::set<int>& a,
    const std::set<int>& b
) {
    std::set<int> result;
    std::set_union(
        a.begin(), a.end(),
        b.begin(), b.end(),
        std::inserter(result, result.begin())
    );
    return result;
}

std::set<int> setIntersection(
    const std::set<int>& a,
    const std::set<int>& b
) {
    std::set<int> result;
    std::set_intersection(
        a.begin(), a.end(),
        b.begin(), b.end(),
        std::inserter(result, result.begin())
    );
    return result;
}

std::set<int> setComplement(
    const std::set<int>& sampleSpace,
    const std::set<int>& event
) {
    std::set<int> result;
    std::set_difference(
        sampleSpace.begin(), sampleSpace.end(),
        event.begin(), event.end(),
        std::inserter(result, result.begin())
    );
    return result;
}

double conditionalProbability(
    const ProbabilitySpace& space,
    const std::set<int>& event,
    const std::set<int>& condition
) {
    const double denominator = space.probability(condition);

    if (denominator == 0.0) {
        throw ProbabilityError(
            "Conditional probability is undefined for a zero-probability condition."
        );
    }

    const double numerator =
        space.probability(setIntersection(event, condition));

    return numerator / denominator;
}

double binomialProbability(int n, int k, double p) {
    if (n < 0 || k < 0 || k > n) {
        throw ProbabilityError("Require n >= 0 and 0 <= k <= n.");
    }

    if (p < 0.0 || p > 1.0) {
        throw ProbabilityError("p must be between zero and one.");
    }

    double coefficient = 1.0;

    // Multiplicative evaluation avoids constructing a large factorial.
    for (int i = 1; i <= k; ++i) {
        coefficient *= static_cast<double>(n - i + 1) / i;
    }

    return coefficient * std::pow(p, k) * std::pow(1.0 - p, n - k);
}

class MergeEligibilityEngine {
public:
    static bool eligible(
        const PullRequest& pr,
        const BranchProtection& policy
    ) {
        if (pr.state == ReviewState::Merged || pr.state == ReviewState::Closed) {
            return false;
        }

        if (pr.sourceBranch.empty() || pr.targetBranch.empty()) {
            return false;
        }

        if (pr.sourceBranch == pr.targetBranch) {
            return false;
        }

        if (pr.commits.empty()) {
            return false;
        }

        if (!pr.sourceUpToDate) {
            return false;
        }

        const long long approvals = std::count_if(
            pr.reviews.begin(),
            pr.reviews.end(),
            [](const Review& review) {
                return review.eligible &&
                       review.state == ReviewState::Approved;
            }
        );

        if (approvals < policy.requiredApprovals) {
            return false;
        }

        if (policy.requirePassingChecks) {
            const bool allPassing = std::all_of(
                pr.checks.begin(),
                pr.checks.end(),
                [](const StatusCheck& check) {
                    return check.state == CheckState::Passing;
                }
            );

            if (pr.checks.empty() || !allPassing) {
                return false;
            }
        }

        if (policy.requireConversationResolution &&
            pr.unresolvedConversations > 0) {
            return false;
        }

        return true;
    }
};

void validateProbabilityModel() {
    ProbabilitySpace die({
        {1, 1.0 / 6.0},
        {2, 1.0 / 6.0},
        {3, 1.0 / 6.0},
        {4, 1.0 / 6.0},
        {5, 1.0 / 6.0},
        {6, 1.0 / 6.0}
    });

    const std::set<int> even{2, 4, 6};
    const std::set<int> prime{2, 3, 5};

    if (std::abs(die.probability(even) - 0.5) > 1e-12) {
        throw std::runtime_error("Even-event probability failed.");
    }

    const auto overlap = setIntersection(even, prime);
    if (overlap != std::set<int>{2}) {
        throw std::runtime_error("Intersection failed.");
    }

    const auto unionEvent = setUnion(even, prime);
    if (std::abs(die.probability(unionEvent) - 5.0 / 6.0) > 1e-12) {
        throw std::runtime_error("Union failed.");
    }

    const auto notEven = setComplement(die.sampleSpace(), even);
    if (std::abs(die.probability(notEven) - 0.5) > 1e-12) {
        throw std::runtime_error("Complement failed.");
    }

    const double conditional =
        conditionalProbability(die, prime, even);

    if (std::abs(conditional - 1.0 / 3.0) > 1e-12) {
        throw std::runtime_error("Conditional probability failed.");
    }

    if (std::abs(binomialProbability(5, 3, 0.5) - 0.3125) > 1e-12) {
        throw std::runtime_error("Binomial probability failed.");
    }
}

void demonstrateSimulation() {
    std::mt19937_64 generator(20261031);
    std::uniform_int_distribution<int> die(1, 6);

    constexpr int trials = 100000;
    int sixes = 0;

    for (int i = 0; i < trials; ++i) {
        if (die(generator) == 6) {
            ++sixes;
        }
    }

    std::cout << "Simulation of a fair die\n";
    std::cout << "Trials: " << trials << '\n';
    std::cout << "Observed sixes: " << sixes << '\n';
    std::cout << std::fixed << std::setprecision(4)
              << "Estimated P(6): "
              << static_cast<double>(sixes) / trials << '\n';
    std::cout << "Theoretical P(6): 0.1667\n";
}

void demonstrateGovernanceCase() {
    BranchProtection policy;
    policy.requiredApprovals = 2;
    policy.requirePassingChecks = true;
    policy.requireConversationResolution = true;

    PullRequest pr{
        101,
        "feature/probability-engine",
        "main",
        {"a1b2c3", "d4e5f6"},
        {
            {"reviewer-alice", true, ReviewState::Approved},
            {"reviewer-bob", true, ReviewState::Approved},
            {"author", false, ReviewState::Approved}
        },
        {
            {"unit-tests", CheckState::Passing},
            {"security-scan", CheckState::Passing},
            {"integration-tests", CheckState::Passing}
        },
        0,
        ReviewState::Open,
        true
    };

    const bool eligible = MergeEligibilityEngine::eligible(pr, policy);

    std::cout << "\nRepository governance case\n";
    std::cout << "Pull Request #" << pr.id << '\n';
    std::cout << "Merge eligible: " << std::boolalpha << eligible << '\n';

    // A failing status check invalidates merge eligibility without changing
    // the recorded human review decisions.
    pr.checks[1].state = CheckState::Failing;

    const bool blocked =
        MergeEligibilityEngine::eligible(pr, policy);

    std::cout << "After security scan failure: "
              << blocked << '\n';
}

int main() {
    try {
        validateProbabilityModel();

        std::cout << "=== Probability Fundamentals ===\n";

        ProbabilitySpace space({
            {1, 1.0 / 6.0},
            {2, 1.0 / 6.0},
            {3, 1.0 / 6.0},
            {4, 1.0 / 6.0},
            {5, 1.0 / 6.0},
            {6, 1.0 / 6.0}
        });

        const std::set<int> even{2, 4, 6};
        const std::set<int> prime{2, 3, 5};

        std::cout << std::fixed << std::setprecision(4);
        std::cout << "P(even) = " << space.probability(even) << '\n';
        std::cout << "P(prime) = " << space.probability(prime) << '\n';
        std::cout << "P(even OR prime) = "
                  << space.probability(setUnion(even, prime)) << '\n';
        std::cout << "P(even AND prime) = "
                  << space.probability(setIntersection(even, prime)) << '\n';
        std::cout << "P(prime | even) = "
                  << conditionalProbability(space, prime, even) << '\n';

        std::cout << "\nP(exactly 3 successes in 5 fair trials) = "
                  << binomialProbability(5, 3, 0.5) << '\n';

        demonstrateSimulation();
        demonstrateGovernanceCase();

        std::cout << "\nAll validation checks passed.\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Execution failed: " << error.what() << '\n';
        return 1;
    }
}
