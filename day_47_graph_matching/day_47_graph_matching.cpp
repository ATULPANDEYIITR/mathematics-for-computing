#include <algorithm>
#include <functional>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace std;

class GovernanceMatchingEngine {
private:
    vector<string> reviewers;
    vector<string> pullRequests;
    map<string, set<string>> eligible;
    map<string, string> requestOwner;

public:
    GovernanceMatchingEngine(
        vector<string> reviewerNames,
        vector<string> requestIds
    ) : reviewers(move(reviewerNames)), pullRequests(move(requestIds)) {
        set<string> reviewerSet(reviewers.begin(), reviewers.end());
        set<string> requestSet(pullRequests.begin(), pullRequests.end());

        if (reviewerSet.size() != reviewers.size() ||
            requestSet.size() != pullRequests.size()) {
            throw invalid_argument("Duplicate vertices are not allowed.");
        }

        for (const auto& reviewer : reviewers) {
            if (requestSet.count(reviewer)) {
                throw invalid_argument("Partitions must be disjoint.");
            }
            eligible[reviewer] = {};
        }
    }

    void addEligibility(const string& reviewer, const string& request) {
        if (eligible.find(reviewer) == eligible.end()) {
            throw invalid_argument("Unknown reviewer.");
        }
        if (find(pullRequests.begin(), pullRequests.end(), request)
            == pullRequests.end()) {
            throw invalid_argument("Unknown pull request.");
        }
        eligible[reviewer].insert(request);
    }

    bool augment(
        const string& reviewer,
        set<string>& visitedRequests
    ) {
        for (const auto& request : eligible.at(reviewer)) {
            if (visitedRequests.count(request)) continue;
            visitedRequests.insert(request);

            auto owner = requestOwner.find(request);

            // An occupied request can be reassigned if its reviewer
            // can be moved along an augmenting path.
            if (owner == requestOwner.end() ||
                augment(owner->second, visitedRequests)) {
                requestOwner[request] = reviewer;
                return true;
            }
        }
        return false;
    }

    vector<pair<string, string>> maximumMatching() {
        requestOwner.clear();

        for (const auto& reviewer : reviewers) {
            set<string> visited;
            augment(reviewer, visited);
        }

        vector<pair<string, string>> assignments;
        for (const auto& [request, reviewer] : requestOwner) {
            assignments.emplace_back(reviewer, request);
        }

        return assignments;
    }

    bool validate(
        const vector<pair<string, string>>& assignments
    ) const {
        set<string> usedReviewers;
        set<string> usedRequests;

        for (const auto& [reviewer, request] : assignments) {
            auto reviewerIt = eligible.find(reviewer);

            if (reviewerIt == eligible.end()) return false;
            if (!reviewerIt->second.count(request)) return false;
            if (!usedReviewers.insert(reviewer).second) return false;
            if (!usedRequests.insert(request).second) return false;
        }

        return true;
    }

    void printAllocation() {
        const auto assignments = maximumMatching();

        if (!validate(assignments)) {
            throw logic_error("Matching integrity check failed.");
        }

        cout << "Reviewer allocation for repository pull requests\n";
        for (const auto& [reviewer, request] : assignments) {
            cout << "  " << reviewer << " -> " << request << '\n';
        }

        cout << "Maximum assignments found: "
             << assignments.size() << '\n';

        for (const auto& reviewer : reviewers) {
            bool assigned = any_of(
                assignments.begin(),
                assignments.end(),
                [&](const auto& pair) {
                    return pair.first == reviewer;
                }
            );

            if (!assigned) {
                cout << "Unassigned reviewer: " << reviewer << '\n';
            }
        }

        for (const auto& request : pullRequests) {
            bool assigned = any_of(
                assignments.begin(),
                assignments.end(),
                [&](const auto& pair) {
                    return pair.second == request;
                }
            );

            if (!assigned) {
                cout << "Unreviewed request: " << request << '\n';
            }
        }
    }
};

int main() {
    try {
        GovernanceMatchingEngine engine(
            {"Reviewer-A", "Reviewer-B", "Reviewer-C", "Reviewer-D"},
            {"PR-201", "PR-202", "PR-203", "PR-204"}
        );

        // Eligibility edges encode repository ownership, technical skill,
        // and review access. Matching never grants approval automatically.
        engine.addEligibility("Reviewer-A", "PR-201");
        engine.addEligibility("Reviewer-A", "PR-202");
        engine.addEligibility("Reviewer-B", "PR-201");
        engine.addEligibility("Reviewer-C", "PR-202");
        engine.addEligibility("Reviewer-C", "PR-203");
        engine.addEligibility("Reviewer-D", "PR-203");

        engine.printAllocation();

        cout << "\nConstrained review workload\n";
        GovernanceMatchingEngine constrained(
            {"Reviewer-X", "Reviewer-Y", "Reviewer-Z"},
            {"PR-301", "PR-302"}
        );

        constrained.addEligibility("Reviewer-X", "PR-301");
        constrained.addEligibility("Reviewer-Y", "PR-301");
        constrained.addEligibility("Reviewer-Z", "PR-302");
        constrained.printAllocation();

        try {
            constrained.addEligibility("Unknown", "PR-301");
        } catch (const invalid_argument& error) {
            cerr << "Eligibility rejected: " << error.what() << '\n';
        }
    } catch (const exception& error) {
        cerr << "Governance engine failed: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
