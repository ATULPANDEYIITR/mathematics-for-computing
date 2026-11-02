#include <algorithm>
#include <cmath>
#include <exception>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

enum class PullRequestState { Draft, Open, Closed, Merged };
enum class ReviewState { Commented, ChangesRequested, Approved, Dismissed };
enum class CheckState { Pass, Fail, Pending };
enum class MergeStrategy { MergeCommit, Squash, Rebase };

struct Commit {
    std::string sha;
    std::string message;
};

struct Review {
    std::string reviewer;
    ReviewState state;
    std::string commitSha;
};

struct StatusCheck {
    std::string name;
    CheckState state;
};

struct BranchProtection {
    std::size_t requiredApprovals{2};
    std::set<std::string> requiredChecks;
    bool requireConversationResolution{true};
    bool requireLinearHistory{false};
    bool allowDirectPush{false};
    bool allowForcePush{false};
};

struct Branch {
    std::string name;
    bool protectedBranch{false};
    BranchProtection protection;
};

struct PullRequest {
    int number{};
    std::string source;
    std::string target;
    PullRequestState state{PullRequestState::Draft};
    std::vector<Commit> commits;
    std::vector<Review> reviews;
    std::vector<StatusCheck> checks;
    int openConversations{0};
    MergeStrategy mergeStrategy{MergeStrategy::Squash};
    bool forcePushRequested{false};

    const std::string& headSha() const {
        if (commits.empty()) {
            throw std::logic_error("Pull Request has no commits.");
        }
        return commits.back().sha;
    }
};

struct BayesEvidence {
    std::string name;
    double likelihoodSafe;
    double likelihoodUnsafe;

    void validate() const {
        if (!(likelihoodSafe > 0.0 && likelihoodSafe <= 1.0) ||
            !(likelihoodUnsafe > 0.0 && likelihoodUnsafe <= 1.0)) {
            throw std::invalid_argument("Invalid likelihood for " + name);
        }
    }
};

struct Evaluation {
    bool eligible{false};
    double posterior{0.0};
    std::vector<std::string> reasons;
};

class BayesianEngine {
private:
    double priorSafe_;
    double threshold_;

public:
    BayesianEngine(double priorSafe, double threshold)
        : priorSafe_(priorSafe), threshold_(threshold) {
        if (!(priorSafe_ > 0.0 && priorSafe_ < 1.0)) {
            throw std::invalid_argument("Prior must be between zero and one.");
        }
        if (!(threshold_ > 0.0 && threshold_ < 1.0)) {
            throw std::invalid_argument("Threshold must be between zero and one.");
        }
    }

    double posterior(const std::vector<BayesEvidence>& evidence) const {
        double safe = priorSafe_;
        double unsafe = 1.0 - priorSafe_;

        for (const auto& item : evidence) {
            item.validate();
            safe *= item.likelihoodSafe;
            unsafe *= item.likelihoodUnsafe;
        }

        const double denominator = safe + unsafe;
        return denominator == 0.0 ? 0.0 : safe / denominator;
    }

    double threshold() const {
        return threshold_;
    }
};

class RepositoryGovernance {
private:
    std::map<std::string, Branch> branches_;
    BayesianEngine engine_;

    static bool hasPassingCheck(
        const PullRequest& pr,
        const std::string& name
    ) {
        return std::any_of(
            pr.checks.begin(),
            pr.checks.end(),
            [&](const StatusCheck& check) {
                return check.name == name && check.state == CheckState::Pass;
            }
        );
    }

    static std::set<std::string> currentApprovers(const PullRequest& pr) {
        std::set<std::string> approvers;

        for (const auto& review : pr.reviews) {
            if (review.state == ReviewState::Approved &&
                review.commitSha == pr.headSha()) {
                approvers.insert(review.reviewer);
            }
        }

        return approvers;
    }

    static bool changesRequested(const PullRequest& pr) {
        return std::any_of(
            pr.reviews.begin(),
            pr.reviews.end(),
            [&](const Review& review) {
                return review.state == ReviewState::ChangesRequested &&
                       review.commitSha == pr.headSha();
            }
        );
    }

    std::vector<BayesEvidence> evidenceFor(
        const PullRequest& pr,
        const Branch& branch
    ) const {
        const auto approvers = currentApprovers(pr);

        const bool requiredChecksPassed =
            std::all_of(
                branch.protection.requiredChecks.begin(),
                branch.protection.requiredChecks.end(),
                [&](const std::string& check) {
                    return hasPassingCheck(pr, check);
                }
            );

        const bool failedCheck =
            std::any_of(
                pr.checks.begin(),
                pr.checks.end(),
                [](const StatusCheck& check) {
                    return check.state == CheckState::Fail;
                }
            );

        const bool pendingCheck =
            std::any_of(
                pr.checks.begin(),
                pr.checks.end(),
                [](const StatusCheck& check) {
                    return check.state == CheckState::Pending;
                }
            );

        return {
            {
                "current-head-approval",
                approvers.size() >= branch.protection.requiredApprovals ? 0.92 : 0.20,
                approvers.size() >= branch.protection.requiredApprovals ? 0.08 : 0.80
            },
            {
                "required-status-checks",
                requiredChecksPassed ? 0.97 : 0.15,
                requiredChecksPassed ? 0.03 : 0.85
            },
            {
                "failed-check",
                failedCheck ? 0.05 : 0.98,
                failedCheck ? 0.95 : 0.02
            },
            {
                "pending-check",
                pendingCheck ? 0.35 : 0.94,
                pendingCheck ? 0.65 : 0.06
            },
            {
                "resolved-conversations",
                pr.openConversations == 0 ? 0.96 : 0.30,
                pr.openConversations == 0 ? 0.04 : 0.70
            },
            {
                "requested-changes",
                changesRequested(pr) ? 0.10 : 0.95,
                changesRequested(pr) ? 0.90 : 0.05
            }
        };
    }

public:
    explicit RepositoryGovernance(BayesianEngine engine)
        : engine_(std::move(engine)) {}

    void addBranch(const Branch& branch) {
        if (branch.name.empty()) {
            throw std::invalid_argument("Branch name cannot be empty.");
        }
        if (branches_.contains(branch.name)) {
            throw std::invalid_argument("Duplicate branch: " + branch.name);
        }
        branches_.emplace(branch.name, branch);
    }

    Evaluation evaluate(const PullRequest& pr) const {
        Evaluation result;

        if (pr.number <= 0) {
            result.reasons.emplace_back("Pull Request number must be positive.");
            return result;
        }

        if (pr.source == pr.target) {
            result.reasons.emplace_back(
                "Source and target branches must differ."
            );
            return result;
        }

        if (pr.state != PullRequestState::Open) {
            result.reasons.emplace_back("Pull Request is not open.");
            return result;
        }

        if (pr.commits.empty()) {
            result.reasons.emplace_back("Pull Request contains no commits.");
            return result;
        }

        const auto targetIt = branches_.find(pr.target);
        if (targetIt == branches_.end()) {
            result.reasons.emplace_back("Target branch does not exist.");
            return result;
        }

        const Branch& target = targetIt->second;

        if (target.protectedBranch) {
            const auto approvers = currentApprovers(pr);

            if (approvers.size() < target.protection.requiredApprovals) {
                result.reasons.push_back(
                    "Insufficient current-head approvals: " +
                    std::to_string(approvers.size()) + "/" +
                    std::to_string(target.protection.requiredApprovals)
                );
            }

            for (const auto& required : target.protection.requiredChecks) {
                if (!hasPassingCheck(pr, required)) {
                    result.reasons.push_back(
                        "Required check has not passed: " + required
                    );
                }
            }

            if (target.protection.requireConversationResolution &&
                pr.openConversations > 0) {
                result.reasons.emplace_back(
                    "Review conversations remain unresolved."
                );
            }

            if (target.protection.requireLinearHistory &&
                pr.mergeStrategy == MergeStrategy::MergeCommit) {
                result.reasons.emplace_back(
                    "Merge-commit strategy violates linear-history policy."
                );
            }

            if (!target.protection.allowForcePush && pr.forcePushRequested) {
                result.reasons.emplace_back(
                    "Force push is prohibited on the protected branch."
                );
            }
        }

        result.posterior = engine_.posterior(evidenceFor(pr, target));

        if (result.posterior < engine_.threshold()) {
            std::ostringstream message;
            message << std::fixed << std::setprecision(4)
                    << "Bayesian posterior " << result.posterior
                    << " is below policy threshold "
                    << engine_.threshold() << ".";
            result.reasons.push_back(message.str());
        }

        result.eligible = result.reasons.empty();
        return result;
    }
};

static void demonstrateBayes() {
    const double prior = 0.20;
    const double likelihoodSafe = 0.90;
    const double likelihoodUnsafe = 0.30;

    const double numerator = likelihoodSafe * prior;
    const double denominator =
        numerator + likelihoodUnsafe * (1.0 - prior);
    const double posterior = numerator / denominator;

    std::cout << "Bayes theorem example\n"
              << "Prior: " << prior << "\n"
              << "Safe likelihood: " << likelihoodSafe << "\n"
              << "Unsafe likelihood: " << likelihoodUnsafe << "\n"
              << "Posterior: " << std::fixed << std::setprecision(4)
              << posterior << "\n\n";
}

int main() {
    try {
        demonstrateBayes();

        BayesianEngine engine(0.85, 0.90);
        RepositoryGovernance governance(engine);

        governance.addBranch({
            "main",
            true,
            {
                2,
                {"unit-tests", "security-scan"},
                true,
                true,
                false,
                false
            }
        });

        governance.addBranch({
            "feature/payment-validation",
            false,
            {}
        });

        PullRequest pr{
            42,
            "feature/payment-validation",
            "main",
            PullRequestState::Open,
            {
                {"a100", "Add payment validation"},
                {"a101", "Fix boundary validation"}
            },
            {
                {"alice", ReviewState::Approved, "a101"},
                {"bob", ReviewState::Approved, "a101"},
                {"carol", ReviewState::Commented, "a101"}
            },
            {
                {"unit-tests", CheckState::Pass},
                {"security-scan", CheckState::Pass},
                {"integration-tests", CheckState::Pass}
            },
            0,
            MergeStrategy::Squash,
            false
        };

        Evaluation evaluation = governance.evaluate(pr);

        std::cout << "Pull Request #" << pr.number << "\n"
                  << "Head: " << pr.headSha() << "\n"
                  << "Posterior merge safety: "
                  << std::fixed << std::setprecision(4)
                  << evaluation.posterior << "\n"
                  << "Merge eligible: "
                  << std::boolalpha << evaluation.eligible << "\n";

        for (const auto& reason : evaluation.reasons) {
            std::cout << "- " << reason << "\n";
        }

        // A new commit makes previous approvals stale because the review
        // evidence is explicitly associated with the current head SHA.
        pr.commits.push_back({
            "a102",
            "Address reviewer findings"
        });

        evaluation = governance.evaluate(pr);

        std::cout << "\nAfter a new commit:\n"
                  << "Posterior: "
                  << std::fixed << std::setprecision(4)
                  << evaluation.posterior << "\n"
                  << "Merge eligible: "
                  << evaluation.eligible << "\n";

        if (evaluation.reasons.empty()) {
            throw std::logic_error(
                "Stale approvals unexpectedly remained valid."
            );
        }

        pr.reviews.push_back({
            "alice",
            ReviewState::Approved,
            "a102"
        });
        pr.reviews.push_back({
            "bob",
            ReviewState::Approved,
            "a102"
        });

        pr.openConversations = 1;
        evaluation = governance.evaluate(pr);

        if (evaluation.eligible) {
            throw std::logic_error(
                "Unresolved conversation incorrectly permitted merge."
            );
        }

        std::cout << "Validation scenarios: passed\n";
        return 0;
    }
    catch (const std::exception& ex) {
        std::cerr << "Governance evaluation failed: "
                  << ex.what() << '\n';
        return 1;
    }
}
