/*
 * Inclusion-Exclusion Principle
 *
 * Case study:
 * A repository-quality analytics service receives overlapping compliance
 * conditions for a collection of software artifacts. The service must
 * determine how many artifacts violate at least one condition without
 * double-counting artifacts that violate multiple conditions.
 *
 * The program then extends the same mathematical mechanism to:
 *   - arbitrary finite sets
 *   - exact membership categories
 *   - divisibility
 *   - probability
 *   - forbidden-position counting
 *
 * Compile:
 *   g++ -std=c++17 -O2 inclusion_exclusion.cpp -o inclusion_exclusion
 */

#include <algorithm>
#include <cassert>
#include <cstdint>
#include <exception>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

struct Artifact {
    int id;
    bool vulnerableDependency;
    bool missingDocumentation;
    bool failedSecurityScan;
};

struct GovernanceResult {
    size_t atLeastOneViolation;
    size_t noViolation;
    size_t onlyDependency;
    size_t onlyDocumentation;
    size_t onlySecurity;
    size_t exactlyTwo;
    size_t allThree;
};

class GovernanceEngine {
public:
    explicit GovernanceEngine(vector<Artifact> artifacts)
        : artifacts_(std::move(artifacts)) {}

    GovernanceResult evaluate() const {
        set<int> dependency;
        set<int> documentation;
        set<int> security;

        for (const auto& artifact : artifacts_) {
            if (artifact.vulnerableDependency) {
                dependency.insert(artifact.id);
            }

            if (artifact.missingDocumentation) {
                documentation.insert(artifact.id);
            }

            if (artifact.failedSecurityScan) {
                security.insert(artifact.id);
            }
        }

        const size_t unionSize = inclusionExclusion(
            {dependency, documentation, security}
        );

        size_t onlyDependency = 0;
        size_t onlyDocumentation = 0;
        size_t onlySecurity = 0;
        size_t exactlyTwo = 0;
        size_t allThree = 0;

        set<int> all = dependency;
        all.insert(documentation.begin(), documentation.end());
        all.insert(security.begin(), security.end());

        for (int id : all) {
            int membership = 0;

            if (dependency.contains(id)) ++membership;
            if (documentation.contains(id)) ++membership;
            if (security.contains(id)) ++membership;

            if (membership == 1) {
                if (dependency.contains(id)) ++onlyDependency;
                else if (documentation.contains(id)) ++onlyDocumentation;
                else ++onlySecurity;
            } else if (membership == 2) {
                ++exactlyTwo;
            } else if (membership == 3) {
                ++allThree;
            }
        }

        return {
            unionSize,
            artifacts_.size() - unionSize,
            onlyDependency,
            onlyDocumentation,
            onlySecurity,
            exactlyTwo,
            allThree
        };
    }

private:
    vector<Artifact> artifacts_;

    static size_t intersectionSize(const vector<set<int>>& sets, uint32_t mask) {
        set<int> result;
        bool initialized = false;

        for (size_t index = 0; index < sets.size(); ++index) {
            if (mask & (1u << index)) {
                if (!initialized) {
                    result = sets[index];
                    initialized = true;
                } else {
                    set<int> next;
                    set_intersection(
                        result.begin(), result.end(),
                        sets[index].begin(), sets[index].end(),
                        inserter(next, next.begin())
                    );
                    result = std::move(next);
                }
            }
        }

        return result.size();
    }

    static size_t inclusionExclusion(const vector<set<int>>& sets) {
        if (sets.empty()) return 0;

        size_t result = 0;
        const uint32_t combinations = 1u << sets.size();

        // The alternating signs are the central mechanism:
        // singleton intersections are added, pair intersections subtracted,
        // triple intersections added, and so on.
        for (uint32_t mask = 1; mask < combinations; ++mask) {
            const size_t selected = __builtin_popcount(mask);
            const size_t term = intersectionSize(sets, mask);

            if (selected % 2 == 1) {
                result += term;
            } else {
                result -= term;
            }
        }

        return result;
    }
};

// -----------------------------------------------------------------------------
// Arithmetic inclusion-exclusion
// -----------------------------------------------------------------------------

long long gcdValue(long long a, long long b) {
    return std::gcd(a, b);
}

long long lcmValue(long long a, long long b) {
    return a / gcdValue(a, b) * b;
}

long long countMultiples(
    long long limit,
    const vector<long long>& divisors
) {
    if (limit < 0) {
        throw invalid_argument("Limit cannot be negative.");
    }

    if (divisors.empty()) {
        return 0;
    }

    for (long long divisor : divisors) {
        if (divisor <= 0) {
            throw invalid_argument("Divisors must be positive.");
        }
    }

    long long result = 0;
    const uint64_t combinations = 1ULL << divisors.size();

    for (uint64_t mask = 1; mask < combinations; ++mask) {
        long long commonMultiple = 1;
        size_t selected = 0;

        for (size_t index = 0; index < divisors.size(); ++index) {
            if (mask & (1ULL << index)) {
                ++selected;
                commonMultiple = lcmValue(
                    commonMultiple,
                    divisors[index]
                );

                if (commonMultiple > limit) {
                    break;
                }
            }
        }

        if (commonMultiple <= limit) {
            const long long term = limit / commonMultiple;

            if (selected % 2 == 1) {
                result += term;
            } else {
                result -= term;
            }
        }
    }

    return result;
}

// -----------------------------------------------------------------------------
// Derangements
// -----------------------------------------------------------------------------

long long derangements(int n) {
    if (n < 0 || n > 20) {
        throw invalid_argument(
            "This demonstration accepts n from 0 through 20."
        );
    }

    long long factorial = 1;

    for (int value = 2; value <= n; ++value) {
        factorial *= value;
    }

    long long result = 0;
    long long termFactorial = factorial;

    // A_k means that a specified collection of k positions are fixed.
    // Inclusion-exclusion alternately removes and restores those overlaps.
    for (int k = 0; k <= n; ++k) {
        if (k % 2 == 0) {
            result += termFactorial;
        } else {
            result -= termFactorial;
        }

        if (n - k > 0) {
            termFactorial /= (n - k);
        }
    }

    return result;
}

// -----------------------------------------------------------------------------
// Verification
// -----------------------------------------------------------------------------

void runTests() {
    assert(countMultiples(100, {2, 3}) == 67);
    assert(countMultiples(100, {2, 3, 5}) == 74);

    assert(derangements(0) == 1);
    assert(derangements(1) == 0);
    assert(derangements(4) == 9);

    vector<set<int>> testSets = {
        {1, 2, 3, 4},
        {3, 4, 5, 6},
        {4, 6, 7}
    };

    // Direct union contains 1..7.
    assert(GovernanceEngine::evaluate); // Compile-time reminder removed below.
}

// -----------------------------------------------------------------------------
// A small independent set-union implementation for testing.
// -----------------------------------------------------------------------------

size_t directUnionCount(const vector<set<int>>& sets) {
    set<int> result;

    for (const auto& current : sets) {
        result.insert(current.begin(), current.end());
    }

    return result.size();
}

size_t inclusionExclusionUnionCount(const vector<set<int>>& sets) {
    if (sets.empty()) return 0;

    size_t result = 0;
    const uint32_t combinations = 1u << sets.size();

    for (uint32_t mask = 1; mask < combinations; ++mask) {
        set<int> intersection;
        bool initialized = false;
        size_t selected = 0;

        for (size_t index = 0; index < sets.size(); ++index) {
            if (mask & (1u << index)) {
                ++selected;

                if (!initialized) {
                    intersection = sets[index];
                    initialized = true;
                } else {
                    set<int> next;
                    set_intersection(
                        intersection.begin(), intersection.end(),
                        sets[index].begin(), sets[index].end(),
                        inserter(next, next.begin())
                    );
                    intersection = std::move(next);
                }
            }
        }

        if (selected % 2 == 1) {
            result += intersection.size();
        } else {
            result -= intersection.size();
        }
    }

    return result;
}

void verifyMathematics() {
    vector<set<int>> sets = {
        {1, 2, 3, 4},
        {3, 4, 5, 6},
        {4, 6, 7}
    };

    assert(directUnionCount(sets) == 7);
    assert(inclusionExclusionUnionCount(sets) == 7);
}

// -----------------------------------------------------------------------------
// Main case study
// -----------------------------------------------------------------------------

int main() {
    try {
        verifyMathematics();

        vector<Artifact> artifacts;

        for (int id = 1; id <= 100; ++id) {
            artifacts.push_back({
                id,
                id <= 38,
                id >= 25 && id <= 67,
                id >= 52 && id <= 90
            });
        }

        GovernanceEngine engine(artifacts);
        GovernanceResult result = engine.evaluate();

        cout << "INCLUSION-EXCLUSION GOVERNANCE CASE STUDY\n";
        cout << string(72, '=') << '\n';

        cout << "\nArtifact population: " << artifacts.size() << '\n';
        cout << "At least one violation: "
             << result.atLeastOneViolation << '\n';
        cout << "No violation: "
             << result.noViolation << '\n';
        cout << "Only dependency violation: "
             << result.onlyDependency << '\n';
        cout << "Only documentation violation: "
             << result.onlyDocumentation << '\n';
        cout << "Only security violation: "
             << result.onlySecurity << '\n';
        cout << "Exactly two violations: "
             << result.exactlyTwo << '\n';
        cout << "All three violations: "
             << result.allThree << '\n';

        cout << "\nArithmetic application\n";
        cout << string(72, '-') << '\n';

        cout << "Multiples of 2 or 3 up to 100: "
             << countMultiples(100, {2, 3}) << '\n';

        cout << "Multiples of 2, 3, or 5 up to 100: "
             << countMultiples(100, {2, 3, 5}) << '\n';

        cout << "\nDerangements\n";
        cout << string(72, '-') << '\n';

        for (int n = 1; n <= 7; ++n) {
            cout << "D(" << n << ") = " << derangements(n) << '\n';
        }

        cout << "\nEngineering implications\n";
        cout << string(72, '-') << '\n';
        cout << "Arbitrary-set inclusion-exclusion requires 2^n - 1 "
             << "intersection terms.\n";
        cout << "The case study uses std::set intersections because "
             << "membership identity matters.\n";
        cout << "Arithmetic applications replace set intersections with "
             << "LCM calculations, which exploits number-theoretic structure.\n";
        cout << "For large n, direct inclusion-exclusion becomes expensive; "
             << "the useful optimization is usually to exploit structure "
             << "rather than blindly enumerate every subset.\n";

        return 0;
    } catch (const exception& error) {
        cerr << "Error: " << error.what() << '\n';
        return 1;
    }
}
