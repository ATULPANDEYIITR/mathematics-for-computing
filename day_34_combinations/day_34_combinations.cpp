#include <algorithm>
#include <cstdint>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

/*
 * Combinations Case Study: Repository Governance Planning Engine
 *
 * Scenario:
 * A large engineering organization wants to understand the number of possible
 * review committees that can be formed for different repository policies.
 *
 * The program models:
 *   - exact binomial coefficients
 *   - Pascal's recurrence
 *   - reviewer eligibility
 *   - committee enumeration
 *   - minimum approval policy analysis
 *   - policy edge cases
 *
 * The governance scenario is deliberately about combinatorial reasoning:
 * if n eligible reviewers exist and r distinct reviewers must participate,
 * C(n,r) represents the number of possible committees.
 *
 * Compile:
 *   g++ -std=c++17 -O2 combinations.cpp -o combinations
 */

using BigInteger = unsigned long long;

class CombinationError : public std::runtime_error {
public:
    explicit CombinationError(const std::string& message)
        : std::runtime_error(message) {}
};

class Combinatorics {
public:
    static BigInteger choose(std::size_t n, std::size_t r) {
        validate(n, r);

        r = std::min(r, n - r);

        BigInteger result = 1;

        for (std::size_t i = 1; i <= r; ++i) {
            const BigInteger numerator = n - r + i;

            if (result > std::numeric_limits<BigInteger>::max() / numerator) {
                throw CombinationError(
                    "Coefficient exceeds the exact unsigned 64-bit range."
                );
            }

            result *= numerator;

            /*
             * The product is mathematically divisible by i. Dividing after
             * multiplication preserves the exact integer coefficient.
             */
            result /= i;
        }

        return result;
    }

    static std::vector<BigInteger> pascalRow(std::size_t n) {
        std::vector<BigInteger> row;
        row.reserve(n + 1);
        row.push_back(1);

        for (std::size_t r = 1; r <= n; ++r) {
            const BigInteger previous = row.back();
            const BigInteger numerator = n - r + 1;

            if (previous > std::numeric_limits<BigInteger>::max() / numerator) {
                throw CombinationError("Pascal row exceeds 64-bit range.");
            }

            row.push_back((previous * numerator) / r);
        }

        return row;
    }

    static std::vector<std::vector<BigInteger>> triangle(std::size_t rows) {
        std::vector<std::vector<BigInteger>> result;
        result.reserve(rows);

        for (std::size_t n = 0; n < rows; ++n) {
            result.push_back(pascalRow(n));
        }

        return result;
    }

private:
    static void validate(std::size_t n, std::size_t r) {
        if (r > n) {
            throw CombinationError("r cannot be greater than n.");
        }
    }
};

struct Reviewer {
    std::string name;
    std::string team;
    bool eligible;
};

struct RepositoryPolicy {
    std::size_t requiredApprovals;
    bool requireDistinctTeams;
    std::set<std::string> forbiddenTeams;
};

class GovernanceEngine {
public:
    GovernanceEngine(
        std::vector<Reviewer> reviewers,
        RepositoryPolicy policy
    )
        : reviewers_(std::move(reviewers)),
          policy_(std::move(policy)) {}

    std::vector<Reviewer> eligibleReviewers() const {
        std::vector<Reviewer> result;

        for (const auto& reviewer : reviewers_) {
            if (!reviewer.eligible) {
                continue;
            }

            if (policy_.forbiddenTeams.count(reviewer.team) != 0) {
                continue;
            }

            result.push_back(reviewer);
        }

        return result;
    }

    BigInteger theoreticalCommitteeCount() const {
        const auto eligible = eligibleReviewers();

        if (policy_.requiredApprovals > eligible.size()) {
            return 0;
        }

        return Combinatorics::choose(
            eligible.size(),
            policy_.requiredApprovals
        );
    }

    std::vector<std::vector<Reviewer>> validCommittees() const {
        const auto eligible = eligibleReviewers();

        if (policy_.requiredApprovals > eligible.size()) {
            return {};
        }

        std::vector<std::vector<Reviewer>> committees;
        std::vector<Reviewer> current;

        enumerate(eligible, 0, current, committees);
        return committees;
    }

private:
    void enumerate(
        const std::vector<Reviewer>& eligible,
        std::size_t start,
        std::vector<Reviewer>& current,
        std::vector<std::vector<Reviewer>>& output
    ) const {
        if (current.size() == policy_.requiredApprovals) {
            if (meetsTeamDiversity(current)) {
                output.push_back(current);
            }
            return;
        }

        const std::size_t remainingNeeded =
            policy_.requiredApprovals - current.size();

        if (eligible.size() - start < remainingNeeded) {
            return;
        }

        for (std::size_t index = start; index < eligible.size(); ++index) {
            current.push_back(eligible[index]);
            enumerate(eligible, index + 1, current, output);
            current.pop_back();
        }
    }

    bool meetsTeamDiversity(
        const std::vector<Reviewer>& committee
    ) const {
        if (!policy_.requireDistinctTeams) {
            return true;
        }

        std::set<std::string> teams;

        for (const auto& reviewer : committee) {
            teams.insert(reviewer.team);
        }

        return teams.size() == committee.size();
    }

    std::vector<Reviewer> reviewers_;
    RepositoryPolicy policy_;
};

void printRow(const std::vector<BigInteger>& row) {
    for (std::size_t i = 0; i < row.size(); ++i) {
        if (i > 0) {
            std::cout << ' ';
        }
        std::cout << row[i];
    }
    std::cout << '\n';
}

void printCommittee(
    const std::vector<Reviewer>& committee
) {
    std::cout << "  ";

    for (std::size_t i = 0; i < committee.size(); ++i) {
        if (i > 0) {
            std::cout << ", ";
        }

        std::cout << committee[i].name
                  << " [" << committee[i].team << "]";
    }

    std::cout << '\n';
}

void verifyPascalIdentity(std::size_t n) {
    if (n < 2) {
        return;
    }

    for (std::size_t r = 1; r < n; ++r) {
        const auto left = Combinatorics::choose(n, r);
        const auto right =
            Combinatorics::choose(n - 1, r - 1)
            + Combinatorics::choose(n - 1, r);

        if (left != right) {
            throw CombinationError("Pascal recurrence verification failed.");
        }
    }
}

void runSelfTests() {
    for (std::size_t n = 0; n <= 30; ++n) {
        const auto row = Combinatorics::pascalRow(n);

        if (row.size() != n + 1) {
            throw CombinationError("Pascal row has incorrect length.");
        }

        if (row.front() != 1 || row.back() != 1) {
            throw CombinationError("Pascal boundary values are invalid.");
        }

        for (std::size_t r = 0; r <= n; ++r) {
            if (row[r] != Combinatorics::choose(n, r)) {
                throw CombinationError(
                    "Pascal row does not match binomial coefficient."
                );
            }

            if (row[r] != Combinatorics::choose(n, n - r)) {
                throw CombinationError(
                    "Binomial symmetry verification failed."
                );
            }
        }

        verifyPascalIdentity(n);
    }

    std::cout << "\nSelf-tests: all passed\n";
}

int main() {
    try {
        std::cout
            << "COMBINATIONS, BINOMIAL COEFFICIENTS, AND PASCAL'S TRIANGLE\n"
            << "============================================================\n";

        std::cout << "\nPascal's triangle\n";

        const auto triangle = Combinatorics::triangle(9);

        for (const auto& row : triangle) {
            printRow(row);
        }

        std::cout << "\nCore coefficients\n";
        std::cout << "C(5,2)   = "
                  << Combinatorics::choose(5, 2) << '\n';
        std::cout << "C(10,4)  = "
                  << Combinatorics::choose(10, 4) << '\n';
        std::cout << "C(20,10) = "
                  << Combinatorics::choose(20, 10) << '\n';

        /*
         * Repository governance case:
         *
         * Six engineers are candidates for a protected repository's review
         * committee. Only eligible engineers are considered. A governance
         * policy requires three approvals and requires those reviewers to
         * come from different teams.
         */
        std::vector<Reviewer> reviewers = {
            {"Asha", "Platform", true},
            {"Bharat", "Security", true},
            {"Chen", "Data", true},
            {"Divya", "Platform", true},
            {"Ethan", "Web", true},
            {"Fatima", "Security", true},
            {"Gopal", "Research", false}
        };

        RepositoryPolicy policy{
            3,
            true,
            {}
        };

        GovernanceEngine engine(reviewers, policy);

        const auto eligible = engine.eligibleReviewers();

        std::cout << "\nRepository review governance case study\n";
        std::cout << "Eligible reviewers: " << eligible.size() << '\n';
        std::cout << "Required approvals: "
                  << policy.requiredApprovals << '\n';
        std::cout << "Theoretical committees without diversity constraint: "
                  << Combinatorics::choose(
                         eligible.size(),
                         policy.requiredApprovals
                     )
                  << '\n';

        const auto validCommittees = engine.validCommittees();

        std::cout << "Committees satisfying team diversity: "
                  << validCommittees.size() << '\n';

        for (const auto& committee : validCommittees) {
            printCommittee(committee);
        }

        /*
         * A disabled reviewer is removed before counting. This distinction is
         * important: C(n,r) counts selections from the eligible population,
         * not selections from every person whose name exists in a directory.
         */
        std::cout << "\nEligibility impact\n";

        RepositoryPolicy stricterPolicy{
            4,
            true,
            {}
        };

        GovernanceEngine stricterEngine(reviewers, stricterPolicy);

        std::cout << "Four-approval theoretical count: "
                  << stricterEngine.theoreticalCommitteeCount()
                  << '\n';

        /*
         * Demonstrate a policy that excludes an entire team. This changes the
         * input population before the combinatorial calculation is performed.
         */
        RepositoryPolicy restrictedPolicy{
            3,
            false,
            {"Security"}
        };

        GovernanceEngine restrictedEngine(reviewers, restrictedPolicy);

        std::cout << "Count after excluding Security reviewers: "
                  << restrictedEngine.theoreticalCommitteeCount()
                  << '\n';

        std::cout << "\nCombinatorial identities\n";

        const std::size_t n = 12;

        std::cout << "Symmetry C(12,3) = C(12,9): "
                  << (Combinatorics::choose(12, 3)
                      == Combinatorics::choose(12, 9)
                          ? "true"
                          : "false")
                  << '\n';

        BigInteger rowSum = 0;

        for (const auto value : Combinatorics::pascalRow(n)) {
            rowSum += value;
        }

        std::cout << "Sum of row 12: " << rowSum << '\n';
        std::cout << "Expected 2^12: " << (BigInteger{1} << n) << '\n';

        verifyPascalIdentity(12);

        std::cout << "\nComplexity characteristics\n";
        std::cout
            << "Coefficient calculation uses O(min(r,n-r)) arithmetic steps.\n";
        std::cout
            << "A Pascal row requires O(n) stored coefficients.\n";
        std::cout
            << "Enumerating every r-member committee is output-sensitive and "
               "requires O(C(n,r)) generated combinations.\n";

        /*
         * An invalid request is treated as an input error rather than silently
         * producing zero. C(n,r) is defined for 0 <= r <= n in this program.
         */
        std::cout << "\nValidation example\n";

        try {
            Combinatorics::choose(4, 7);
        } catch (const CombinationError& error) {
            std::cout << "Rejected invalid coefficient: "
                      << error.what() << '\n';
        }

        runSelfTests();
    }
    catch (const std::exception& error) {
        std::cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
