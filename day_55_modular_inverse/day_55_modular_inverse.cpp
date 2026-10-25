#include <algorithm>
#include <cstdint>
#include <exception>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

using int64 = int64_t;

struct BezoutResult {
    int64 gcd;
    int64 x;
    int64 y;
};

struct BranchPolicy {
    string branch_name;
    bool protected_branch = true;
    bool require_approval = true;
    bool require_passing_checks = true;
    bool require_linear_history = false;
    bool allow_direct_push = false;
    bool allow_force_push = false;
    bool allow_deletion = false;
    int required_approvals = 1;
};

struct PullRequest {
    int id;
    string source_branch;
    string target_branch;
    bool open = true;
    bool draft = false;
    bool conflicts = false;
    bool discussions_resolved = true;
    bool up_to_date = true;
    bool linear_history = true;
    vector<string> commits;
};

struct Review {
    string reviewer;
    bool eligible = false;
    bool author = false;
    bool dismissed = false;
    string state; // APPROVED, CHANGES_REQUESTED, COMMENTED
};

struct StatusCheck {
    string name;
    bool required = true;
    bool passed = false;
};

struct Eligibility {
    bool eligible = false;
    vector<string> reasons;
};

BezoutResult extendedGcd(int64 a, int64 b) {
    // This demonstration uses ordinary signed 64-bit integers.
    // Negating INT64_MIN is undefined, so reject it explicitly.
    if (a == INT64_MIN || b == INT64_MIN) {
        throw overflow_error("INT64_MIN is outside the supported input range.");
    }

    int64 oldR = abs(a), r = abs(b);
    int64 oldS = 1, s = 0;
    int64 oldT = 0, t = 1;

    while (r != 0) {
        int64 q = oldR / r;
        int64 nextR = oldR - q * r;
        oldR = r;
        r = nextR;

        int64 nextS = oldS - q * s;
        oldS = s;
        s = nextS;

        int64 nextT = oldT - q * t;
        oldT = t;
        t = nextT;
    }

    if (a < 0) oldS = -oldS;
    if (b < 0) oldT = -oldT;

    return {oldR, oldS, oldT};
}

int64 normalize(int64 value, int64 modulus) {
    int64 remainder = value % modulus;
    return remainder < 0 ? remainder + modulus : remainder;
}

optional<int64> modularInverse(int64 value, int64 modulus) {
    if (modulus <= 1) {
        throw invalid_argument("Modulus must be greater than 1.");
    }

    BezoutResult result = extendedGcd(value, modulus);
    if (result.gcd != 1) return nullopt;

    return normalize(result.x, modulus);
}

Eligibility evaluateMerge(
    const PullRequest& pr,
    const BranchPolicy& policy,
    const vector<Review>& reviews,
    const vector<StatusCheck>& checks
) {
    Eligibility result{true, {}};

    auto fail = [&](const string& reason) {
        result.eligible = false;
        result.reasons.push_back(reason);
    };

    if (!pr.open) fail("Pull Request is closed.");
    if (pr.draft) fail("Draft Pull Requests cannot be merged.");
    if (pr.target_branch != policy.branch_name) {
        fail("Target branch does not match the evaluated policy.");
    }
    if (pr.source_branch == pr.target_branch) {
        fail("Source and target branches must differ.");
    }
    if (pr.conflicts) fail("Merge conflicts must be resolved.");
    if (!pr.up_to_date) fail("Source branch must be synchronized.");
    if (!pr.discussions_resolved) fail("Review discussions remain unresolved.");

    if (policy.protected_branch && policy.require_linear_history &&
        !pr.linear_history) {
        fail("Target branch requires linear history.");
    }

    int approvals = 0;
    bool changesRequested = false;

    for (const auto& review : reviews) {
        if (review.dismissed || !review.eligible || review.author) continue;

        if (review.state == "CHANGES_REQUESTED") {
            changesRequested = true;
        } else if (review.state == "APPROVED") {
            ++approvals;
        }
    }

    if (changesRequested) {
        fail("An eligible reviewer has requested changes.");
    }

    if (policy.protected_branch && policy.require_approval &&
        approvals < policy.required_approvals) {
        fail("Insufficient eligible approvals.");
    }

    if (policy.protected_branch && policy.require_passing_checks) {
        for (const auto& check : checks) {
            if (check.required && !check.passed) {
                fail("Required status check failed or is pending: " + check.name);
            }
        }
    }

    return result;
}

void printEligibility(const Eligibility& result) {
    cout << (result.eligible ? "MERGE ELIGIBLE" : "MERGE BLOCKED") << '\n';
    for (const auto& reason : result.reasons) {
        cout << " - " << reason << '\n';
    }
}

int main() {
    try {
        cout << "Modular inverse calculations\n";

        for (const auto& item : vector<pair<int64, int64>>{
                 {3, 11}, {10, 17}, {-3, 11}, {6, 15}}) {
            auto inverse = modularInverse(item.first, item.second);
            cout << item.first << " mod " << item.second << ": ";

            if (inverse) {
                cout << *inverse
                     << ", verification="
                     << normalize(item.first * *inverse, item.second)
                     << '\n';
            } else {
                cout << "no inverse\n";
            }
        }

        BezoutResult identity = extendedGcd(30, 18);
        cout << "Bezout identity: "
             << 30 << "*" << identity.x << " + "
             << 18 << "*" << identity.y << " = "
             << identity.gcd << "\n\n";

        BranchPolicy policy{
            "main", true, true, true, true, false, false, false, 2
        };

        PullRequest pr{
            42, "feature/modular-inverses", "main",
            true, false, false, true, true, true,
            {"c101", "c102", "c103"}
        };

        vector<Review> reviews{
            {"reviewer-alice", true, false, false, "APPROVED"},
            {"reviewer-bob", true, false, false, "APPROVED"},
            {"author", true, true, false, "APPROVED"}
        };

        vector<StatusCheck> checks{
            {"unit-tests", true, true},
            {"static-analysis", true, true},
            {"integration-tests", true, false}
        };

        cout << "Repository merge eligibility\n";
        Eligibility first = evaluateMerge(pr, policy, reviews, checks);
        printEligibility(first);

        cout << "\nAfter integration tests pass\n";
        checks[2].passed = true;
        printEligibility(evaluateMerge(pr, policy, reviews, checks));

        cout << "\nAfter an approval is dismissed\n";
        reviews[1].dismissed = true;
        printEligibility(evaluateMerge(pr, policy, reviews, checks));

        cout << "\nComplexity: O(log m) for the Euclidean algorithm; "
             << "O(r + c) for merge evaluation.\n";
    } catch (const exception& error) {
        cerr << "Error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
