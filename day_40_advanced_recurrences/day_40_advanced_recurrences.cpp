#include <algorithm>
#include <cmath>
#include <cstdint>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;

/*
 * Case study: estimate the work performed by a parallel data-processing
 * service that recursively partitions an input into smaller tasks.
 *
 * The engine separates:
 * - the recurrence definition,
 * - exact integer cost evaluation,
 * - recursion-tree aggregation,
 * - Master Theorem classification.
 *
 * Costs are illustrative operation units rather than wall-clock times.
 */

struct Recurrence {
    string name;
    uint64_t a;
    uint64_t b;
    function<uint64_t(uint64_t)> combineCost;
    uint64_t baseCost = 1;
};

struct TreeLevel {
    uint64_t depth;
    uint64_t nodes;
    uint64_t subproblemSize;
    uint64_t workPerNode;
    uint64_t aggregateWork;
};

enum class MasterCase {
    LeafDominated,
    Balanced,
    CombineDominated
};

struct Classification {
    MasterCase category;
    double criticalExponent;
    string explanation;
};

class RecurrenceEngine {
private:
    Recurrence recurrence;
    unordered_map<uint64_t, uint64_t> memo;

    static uint64_t checkedMultiply(uint64_t x, uint64_t y) {
        if (y != 0 && x > numeric_limits<uint64_t>::max() / y) {
            throw overflow_error("Unsigned multiplication overflow");
        }
        return x * y;
    }

    static uint64_t checkedAdd(uint64_t x, uint64_t y) {
        if (x > numeric_limits<uint64_t>::max() - y) {
            throw overflow_error("Unsigned addition overflow");
        }
        return x + y;
    }

public:
    explicit RecurrenceEngine(Recurrence definition)
        : recurrence(std::move(definition)) {
        if (recurrence.a < 1 || recurrence.b <= 1) {
            throw invalid_argument("Require a >= 1 and b > 1");
        }
        if (!recurrence.combineCost) {
            throw invalid_argument("Combine-cost function is required");
        }
    }

    uint64_t cost(uint64_t n) {
        if (n == 0) {
            throw invalid_argument("Problem size must be positive");
        }
        if (n == 1) {
            return recurrence.baseCost;
        }

        const auto cached = memo.find(n);
        if (cached != memo.end()) {
            return cached->second;
        }

        // Ceiling division avoids floating-point rounding in subproblem size.
        const uint64_t childSize = n / recurrence.b
            + (n % recurrence.b != 0 ? 1 : 0);

        const uint64_t childrenCost = checkedMultiply(
            recurrence.a, cost(childSize)
        );
        const uint64_t localWork = recurrence.combineCost(n);
        const uint64_t result = checkedAdd(childrenCost, localWork);

        memo.emplace(n, result);
        return result;
    }

    vector<TreeLevel> tree(uint64_t n) const {
        if (n == 0) {
            throw invalid_argument("Problem size must be positive");
        }

        vector<TreeLevel> levels;
        uint64_t nodes = 1;
        uint64_t size = n;
        uint64_t depth = 0;

        while (size > 1) {
            const uint64_t work = recurrence.combineCost(size);
            const uint64_t aggregate = checkedMultiply(nodes, work);

            levels.push_back({
                depth, nodes, size, work, aggregate
            });

            nodes = checkedMultiply(nodes, recurrence.a);
            size = max<uint64_t>(1, size / recurrence.b);
            ++depth;
        }

        levels.push_back({
            depth,
            nodes,
            1,
            recurrence.baseCost,
            checkedMultiply(nodes, recurrence.baseCost)
        });

        return levels;
    }

    const Recurrence& definition() const {
        return recurrence;
    }
};

Classification classifyMasterTheorem(
    uint64_t a,
    uint64_t b,
    double polynomialPower
) {
    if (a < 1 || b <= 1 || !isfinite(polynomialPower)
        || polynomialPower < 0) {
        throw invalid_argument("Invalid Master Theorem parameters");
    }

    const double critical = log(static_cast<double>(a))
        / log(static_cast<double>(b));
    const double epsilon = 1e-10;

    if (polynomialPower < critical - epsilon) {
        return {
            MasterCase::LeafDominated,
            critical,
            "Leaf contribution dominates the total."
        };
    }

    if (abs(polynomialPower - critical) <= epsilon) {
        return {
            MasterCase::Balanced,
            critical,
            "Every level contributes the same asymptotic order."
        };
    }

    return {
        MasterCase::CombineDominated,
        critical,
        "Combine work dominates if the regularity condition holds."
    };
}

string caseName(MasterCase category) {
    switch (category) {
        case MasterCase::LeafDominated:
            return "Case 1";
        case MasterCase::Balanced:
            return "Case 2";
        case MasterCase::CombineDominated:
            return "Case 3 candidate";
    }
    throw logic_error("Unknown Master Theorem case");
}

void printTree(const RecurrenceEngine& engine, uint64_t n) {
    const auto& definition = engine.definition();
    const auto levels = engine.tree(n);

    cout << "\nSystem: " << definition.name
         << ", input size = " << n << '\n';

    cout << left
         << setw(8) << "Depth"
         << setw(14) << "Nodes"
         << setw(18) << "Subproblem"
         << setw(18) << "Work per node"
         << setw(18) << "Level work"
         << '\n';

    uint64_t total = 0;

    for (const auto& level : levels) {
        cout << left
             << setw(8) << level.depth
             << setw(14) << level.nodes
             << setw(18) << level.subproblemSize
             << setw(18) << level.workPerNode
             << setw(18) << level.aggregateWork
             << '\n';

        total += level.aggregateWork;
    }

    cout << "Tree aggregate: " << total << '\n';
}

int main() {
    try {
        RecurrenceEngine partitionSort({
            "Parallel partition-and-combine service",
            2,
            2,
            [](uint64_t n) {
                return n;
            },
            1
        });

        RecurrenceEngine distributedSearch({
            "Single-branch search service",
            1,
            2,
            [](uint64_t) {
                return uint64_t{1};
            },
            1
        });

        RecurrenceEngine matrixDecomposition({
            "Quadratic local-work decomposition",
            2,
            2,
            [](uint64_t n) {
                if (n > 0 && n >
                    numeric_limits<uint64_t>::max() / n) {
                    throw overflow_error("Quadratic work overflow");
                }
                return n * n;
            },
            1
        });

        printTree(partitionSort, 16);
        printTree(distributedSearch, 16);
        printTree(matrixDecomposition, 8);

        cout << "\nMaster Theorem policy evaluation\n";
        const vector<tuple<uint64_t, uint64_t, double>> scenarios = {
            {2, 2, 1},
            {1, 2, 0},
            {2, 2, 2},
            {4, 2, 1},
            {3, 2, 1}
        };

        for (const auto& [a, b, p] : scenarios) {
            const auto result = classifyMasterTheorem(a, b, p);
            cout << "a=" << a
                 << ", b=" << b
                 << ", p=" << p
                 << ": " << caseName(result.category)
                 << ", critical exponent="
                 << fixed << setprecision(4)
                 << result.criticalExponent
                 << "; " << result.explanation
                 << '\n';
        }

        cout << "\nOperational implications\n";
        cout << "Parallel partition-and-combine has linear work per "
                "level when a=2, b=2, and f(n)=Theta(n).\n";
        cout << "A single-branch search has logarithmic depth because "
                "each step halves the input.\n";
        cout << "Quadratic local work dominates only when the "
                "Master Theorem regularity condition is satisfied.\n";

        try {
            partitionSort.cost(0);
        } catch (const invalid_argument& error) {
            cout << "Rejected invalid workload: "
                 << error.what() << '\n';
        }

    } catch (const exception& error) {
        cerr << "Analysis failed: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
