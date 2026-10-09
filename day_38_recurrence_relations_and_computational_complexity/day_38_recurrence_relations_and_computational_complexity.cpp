/*
 * Recurrence Relations and Computational Complexity
 * P, NP, NP-Completeness, and Polynomial-Time Reductions
 *
 * C++17
 *
 * Case study:
 * A computational-governance engine receives decision problems represented
 * by SAT, CLIQUE, and SUBSET SUM instances. It can verify certificates,
 * estimate brute-force search spaces, and construct the standard polynomial
 * reduction from 3-SAT to CLIQUE.
 *
 * The implementation emphasizes C++ data structures, explicit ownership,
 * validation, algorithms, complexity reasoning, and the distinction between
 * finding a certificate and verifying one.
 */

#include <algorithm>
#include <chrono>
#include <cmath>
#include <functional>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

// -----------------------------------------------------------------------------
// Recurrence demonstration
// -----------------------------------------------------------------------------

long long fibonacciRecursive(int n) {
    if (n < 0) {
        throw invalid_argument("n must be non-negative");
    }

    if (n <= 1) {
        return n;
    }

    return fibonacciRecursive(n - 1) + fibonacciRecursive(n - 2);
}

long long fibonacciMemoized(int n, vector<long long>& memo) {
    if (n < 0) {
        throw invalid_argument("n must be non-negative");
    }

    if (memo[n] != -1) {
        return memo[n];
    }

    memo[n] =
        fibonacciMemoized(n - 1, memo) +
        fibonacciMemoized(n - 2, memo);

    return memo[n];
}

long long fibonacciIterative(int n) {
    if (n < 0) {
        throw invalid_argument("n must be non-negative");
    }

    long long previous = 0;
    long long current = 1;

    for (int i = 0; i < n; ++i) {
        long long next = previous + current;
        previous = current;
        current = next;
    }

    return previous;
}

// -----------------------------------------------------------------------------
// Complexity measurements
// -----------------------------------------------------------------------------

struct ComplexityEstimate {
    string name;
    string asymptotic;
    long double representativeWork;
};

ComplexityEstimate estimateGrowth(
    const string& name,
    const string& asymptotic,
    long double n,
    function<long double(long double)> work
) {
    return {name, asymptotic, work(n)};
}

// -----------------------------------------------------------------------------
// SAT model
// -----------------------------------------------------------------------------

struct Literal {
    string variable;
    bool positive;

    bool evaluate(const map<string, bool>& assignment) const {
        auto it = assignment.find(variable);

        if (it == assignment.end()) {
            throw invalid_argument(
                "Assignment does not contain variable: " + variable
            );
        }

        return positive ? it->second : !it->second;
    }

    string toString() const {
        return positive ? variable : "!" + variable;
    }
};

struct Clause {
    vector<Literal> literals;

    bool evaluate(const map<string, bool>& assignment) const {
        return any_of(
            literals.begin(),
            literals.end(),
            [&](const Literal& literal) {
                return literal.evaluate(assignment);
            }
        );
    }
};

struct CNFFormula {
    vector<string> variables;
    vector<Clause> clauses;

    bool evaluate(const map<string, bool>& assignment) const {
        set<string> expected(
            variables.begin(),
            variables.end()
        );

        set<string> actual;
        for (const auto& [name, value] : assignment) {
            (void)value;
            actual.insert(name);
        }

        if (expected != actual) {
            throw invalid_argument(
                "Assignment variables do not match the formula"
            );
        }

        return all_of(
            clauses.begin(),
            clauses.end(),
            [&](const Clause& clause) {
                return clause.evaluate(assignment);
            }
        );
    }
};

optional<map<string, bool>> solveSAT(const CNFFormula& formula) {
    const size_t variableCount = formula.variables.size();

    if (variableCount >= 63) {
        throw invalid_argument(
            "Brute-force demonstration intentionally limits instances to < 63 variables"
        );
    }

    const unsigned long long assignments =
        1ULL << variableCount;

    for (unsigned long long mask = 0; mask < assignments; ++mask) {
        map<string, bool> assignment;

        for (size_t i = 0; i < variableCount; ++i) {
            assignment[formula.variables[i]] =
                ((mask >> i) & 1ULL) != 0;
        }

        if (formula.evaluate(assignment)) {
            return assignment;
        }
    }

    return nullopt;
}

// -----------------------------------------------------------------------------
// Graph and CLIQUE
// -----------------------------------------------------------------------------

class Graph {
private:
    set<int> vertices;
    set<pair<int, int>> edges;

    static pair<int, int> normalizedEdge(int u, int v) {
        if (u < v) {
            return {u, v};
        }
        return {v, u};
    }

public:
    explicit Graph(const set<int>& vertices)
        : vertices(vertices) {}

    void addEdge(int u, int v) {
        if (u == v) {
            throw invalid_argument("Self-loops are not permitted");
        }

        if (!vertices.contains(u) || !vertices.contains(v)) {
            throw invalid_argument(
                "Both edge endpoints must exist in the graph"
            );
        }

        edges.insert(normalizedEdge(u, v));
    }

    bool adjacent(int u, int v) const {
        return edges.contains(normalizedEdge(u, v));
    }

    const set<int>& getVertices() const {
        return vertices;
    }

    size_t edgeCount() const {
        return edges.size();
    }
};

bool verifyClique(
    const Graph& graph,
    const vector<int>& candidate
) {
    set<int> uniqueVertices(
        candidate.begin(),
        candidate.end()
    );

    if (uniqueVertices.size() != candidate.size()) {
        return false;
    }

    for (int vertex : candidate) {
        if (!graph.getVertices().contains(vertex)) {
            return false;
        }
    }

    for (size_t i = 0; i < candidate.size(); ++i) {
        for (size_t j = i + 1; j < candidate.size(); ++j) {
            if (!graph.adjacent(candidate[i], candidate[j])) {
                return false;
            }
        }
    }

    return true;
}

// -----------------------------------------------------------------------------
// 3-SAT -> CLIQUE reduction
// -----------------------------------------------------------------------------

struct VertexMetadata {
    int clauseIndex;
    Literal literal;
};

struct CliqueReduction {
    Graph graph;
    int requiredCliqueSize;
    map<int, VertexMetadata> metadata;
};

CliqueReduction reduce3SATToClique(
    const CNFFormula& formula
) {
    for (const Clause& clause : formula.clauses) {
        if (clause.literals.size() != 3) {
            throw invalid_argument(
                "3-SAT reduction requires exactly three literals per clause"
            );
        }
    }

    set<int> vertices;
    map<int, VertexMetadata> metadata;

    int nextVertex = 0;

    for (size_t clauseIndex = 0;
         clauseIndex < formula.clauses.size();
         ++clauseIndex) {

        for (const Literal& literal :
             formula.clauses[clauseIndex].literals) {

            vertices.insert(nextVertex);
            metadata[nextVertex] = {
                static_cast<int>(clauseIndex),
                literal
            };

            ++nextVertex;
        }
    }

    Graph graph(vertices);

    for (int u : vertices) {
        for (int v : vertices) {
            if (u >= v) {
                continue;
            }

            const auto& first = metadata.at(u);
            const auto& second = metadata.at(v);

            if (first.clauseIndex == second.clauseIndex) {
                continue;
            }

            const bool contradictory =
                first.literal.variable ==
                    second.literal.variable &&
                first.literal.positive !=
                    second.literal.positive;

            if (!contradictory) {
                graph.addEdge(u, v);
            }
        }
    }

    return {
        move(graph),
        static_cast<int>(formula.clauses.size()),
        move(metadata)
    };
}

bool findCliqueRecursive(
    const Graph& graph,
    const vector<int>& vertices,
    int requiredSize,
    size_t start,
    vector<int>& current,
    vector<int>& solution
) {
    if (static_cast<int>(current.size()) == requiredSize) {
        solution = current;
        return true;
    }

    const int remainingNeeded =
        requiredSize - static_cast<int>(current.size());

    if (vertices.size() - start <
        static_cast<size_t>(remainingNeeded)) {
        return false;
    }

    for (size_t i = start; i < vertices.size(); ++i) {
        const int candidate = vertices[i];

        bool compatible = true;

        for (int selected : current) {
            if (!graph.adjacent(selected, candidate)) {
                compatible = false;
                break;
            }
        }

        if (!compatible) {
            continue;
        }

        current.push_back(candidate);

        if (findCliqueRecursive(
                graph,
                vertices,
                requiredSize,
                i + 1,
                current,
                solution)) {
            return true;
        }

        current.pop_back();
    }

    return false;
}

optional<vector<int>> findClique(
    const CliqueReduction& reduction
) {
    vector<int> vertices(
        reduction.graph.getVertices().begin(),
        reduction.graph.getVertices().end()
    );

    vector<int> current;
    vector<int> solution;

    if (findCliqueRecursive(
            reduction.graph,
            vertices,
            reduction.requiredCliqueSize,
            0,
            current,
            solution)) {
        return solution;
    }

    return nullopt;
}

// -----------------------------------------------------------------------------
// SUBSET SUM
// -----------------------------------------------------------------------------

bool verifySubsetSum(
    const vector<int>& numbers,
    int target,
    const vector<size_t>& selected
) {
    set<size_t> unique;

    long long sum = 0;

    for (size_t index : selected) {
        if (index >= numbers.size()) {
            return false;
        }

        if (!unique.insert(index).second) {
            return false;
        }

        sum += numbers[index];
    }

    return sum == target;
}

// -----------------------------------------------------------------------------
// Enterprise-style problem classification
// -----------------------------------------------------------------------------

enum class ProblemClass {
    P,
    NP,
    NP_COMPLETE_CANDIDATE,
    UNKNOWN
};

string toString(ProblemClass problemClass) {
    switch (problemClass) {
        case ProblemClass::P:
            return "P";
        case ProblemClass::NP:
            return "NP";
        case ProblemClass::NP_COMPLETE_CANDIDATE:
            return "NP-complete candidate";
        case ProblemClass::UNKNOWN:
            return "Unknown";
    }

    return "Unknown";
}

struct DecisionProblem {
    string name;
    ProblemClass classification;
    string certificateDescription;
    string verificationComplexity;
};

class ComplexityGovernanceEngine {
public:
    static void validate(const DecisionProblem& problem) {
        if (problem.name.empty()) {
            throw invalid_argument("Decision problem requires a name");
        }

        if (problem.certificateDescription.empty()) {
            throw invalid_argument(
                "Certificate description cannot be empty"
            );
        }

        if (problem.verificationComplexity.empty()) {
            throw invalid_argument(
                "Verification complexity cannot be empty"
            );
        }
    }

    static void print(const DecisionProblem& problem) {
        validate(problem);

        cout << problem.name << '\n';
        cout << "Class: "
             << toString(problem.classification)
             << '\n';
        cout << "Certificate: "
             << problem.certificateDescription
             << '\n';
        cout << "Verification: "
             << problem.verificationComplexity
             << "\n\n";
    }
};

// -----------------------------------------------------------------------------
// Main case study
// -----------------------------------------------------------------------------

int main() {
    try {
        cout << "=== Recurrence Relations ===\n";

        cout << "Fibonacci F(10), naive recursion: "
             << fibonacciRecursive(10)
             << '\n';

        vector<long long> memo(31, -1);
        memo[0] = 0;
        memo[1] = 1;

        cout << "Fibonacci F(30), memoized: "
             << fibonacciMemoized(30, memo)
             << '\n';

        cout << "Fibonacci F(30), iterative: "
             << fibonacciIterative(30)
             << "\n\n";

        cout << "The naive recurrence "
             << "T(n)=T(n-1)+T(n-2)+O(1) "
             << "has exponential growth, while memoization "
             << "reduces the number of distinct states to O(n).\n\n";

        cout << "=== Complexity Growth ===\n";

        const double n = 32.0;

        vector<ComplexityEstimate> estimates = {
            estimateGrowth(
                "constant",
                "O(1)",
                n,
                [](double) { return 1.0; }
            ),
            estimateGrowth(
                "logarithmic",
                "O(log n)",
                n,
                [](double value) { return log2(value); }
            ),
            estimateGrowth(
                "linear",
                "O(n)",
                n,
                [](double value) { return value; }
            ),
            estimateGrowth(
                "linearithmic",
                "O(n log n)",
                n,
                [](double value) { return value * log2(value); }
            ),
            estimateGrowth(
                "quadratic",
                "O(n^2)",
                n,
                [](double value) { return value * value; }
            ),
            estimateGrowth(
                "exponential",
                "O(2^n)",
                n,
                [](double value) { return pow(2.0, value); }
            )
        };

        cout << fixed << setprecision(2);

        for (const auto& estimate : estimates) {
            cout << setw(14)
                 << estimate.name
                 << " "
                 << setw(12)
                 << estimate.asymptotic
                 << " representative work="
                 << estimate.representativeWork
                 << '\n';
        }

        cout << "\n=== SAT ===\n";

        CNFFormula formula{
            {"a", "b", "c"},
            {
                {
                    {
                        {"a", true},
                        {"b", true},
                        {"c", false}
                    }
                },
                {
                    {
                        {"a", false},
                        {"b", true},
                        {"c", true}
                    }
                },
                {
                    {
                        {"a", true},
                        {"b", false},
                        {"c", true}
                    }
                }
            }
        };

        auto satisfyingAssignment = solveSAT(formula);

        if (satisfyingAssignment.has_value()) {
            cout << "Satisfying certificate found:\n";

            for (const auto& [variable, value] :
                 satisfyingAssignment.value()) {
                cout << "  "
                     << variable
                     << " = "
                     << boolalpha
                     << value
                     << '\n';
            }

            cout << "Certificate verification: "
                 << formula.evaluate(
                        satisfyingAssignment.value()
                    )
                 << '\n';
        } else {
            cout << "Formula is unsatisfiable.\n";
        }

        cout << "\n=== 3-SAT -> CLIQUE ===\n";

        CliqueReduction reduction =
            reduce3SATToClique(formula);

        cout << "Source clauses: "
             << formula.clauses.size()
             << '\n';

        cout << "Target graph vertices: "
             << reduction.graph.getVertices().size()
             << '\n';

        cout << "Target graph edges: "
             << reduction.graph.edgeCount()
             << '\n';

        cout << "Required clique size: "
             << reduction.requiredCliqueSize
             << '\n';

        auto clique = findClique(reduction);

        if (clique.has_value()) {
            cout << "Clique certificate: ";

            for (int vertex : clique.value()) {
                cout << vertex << ' ';
            }

            cout << "\nVerified clique: "
                 << verifyClique(
                        reduction.graph,
                        clique.value()
                    )
                 << '\n';

            cout << "Corresponding literals: ";

            for (int vertex : clique.value()) {
                cout << reduction.metadata.at(vertex)
                            .literal.toString()
                     << ' ';
            }

            cout << '\n';
        } else {
            cout << "No target clique was found.\n";
        }

        cout << "\n=== SUBSET SUM Certificate ===\n";

        vector<int> numbers = {3, 7, 11, 14, 19};
        vector<size_t> certificate = {1, 3};

        cout << "Certificate verifies: "
             << verifySubsetSum(numbers, 21, certificate)
             << '\n';

        cout << "\n=== Problem Classification ===\n";

        ComplexityGovernanceEngine::print({
            "Sorting",
            ProblemClass::P,
            "No certificate is required for the decision version "
            "of whether a permutation satisfies a specified ordering property.",
            "Polynomial-time algorithms exist."
        });

        ComplexityGovernanceEngine::print({
            "SAT",
            ProblemClass::NP_COMPLETE_CANDIDATE,
            "A Boolean assignment specifying one truth value per variable.",
            "Evaluate every clause and literal in polynomial time."
        });

        ComplexityGovernanceEngine::print({
            "CLIQUE",
            ProblemClass::NP_COMPLETE_CANDIDATE,
            "A set of k vertices.",
            "Check every pair of proposed vertices for adjacency in O(k^2)."
        });

        cout << "=== Reduction Principle ===\n";
        cout << "If A <=p B, an efficient algorithm for B would give "
             << "an efficient algorithm for A by first transforming "
             << "A's instance into B's instance.\n";

        cout << "\nFor 3-SAT -> CLIQUE, each literal occurrence becomes "
             << "a graph vertex. Vertices from different clauses connect "
             << "unless their literals contradict. A clique of size equal "
             << "to the number of clauses therefore selects mutually "
             << "compatible literals, one from each clause.\n";

        return 0;
    }
    catch (const exception& error) {
        cerr << "Execution failed: "
             << error.what()
             << '\n';

        return 1;
    }
}
