/*
 * Proof Techniques: Industry-Style C++ Case Study
 *
 * Case study:
 *   A theorem-backed validation engine for a network routing system.
 *
 * The system models a collection of network nodes and routes. It uses
 * mathematical proof ideas to justify:
 *
 *   1. Graph invariants
 *   2. Reachability correctness
 *   3. Shortest-path relaxation
 *   4. Loop invariants
 *   5. Structural reasoning
 *   6. Counterexample detection
 *   7. Pigeonhole-style collision detection
 *   8. Preconditions, postconditions, and failure handling
 *
 * Compile:
 *   g++ -std=c++17 -O2 proof_techniques.cpp -o proof_techniques
 */

#include <algorithm>
#include <cassert>
#include <cstddef>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <optional>
#include <queue>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

// -----------------------------------------------------------------------------
// 1. Mathematical predicates
// -----------------------------------------------------------------------------

bool isEven(long long value) {
    return value % 2 == 0;
}

bool isOdd(long long value) {
    return value % 2 != 0;
}

bool implication(bool p, bool q) {
    return !p || q;
}

bool biconditional(bool p, bool q) {
    return p == q;
}

// -----------------------------------------------------------------------------
// 2. Proof-oriented utility: counterexample search
// -----------------------------------------------------------------------------

optional<long long> findCounterexample(
    const vector<long long>& values,
    const function<bool(long long)>& claim
) {
    for (long long value : values) {
        if (!claim(value)) {
            return value;
        }
    }

    return nullopt;
}

// -----------------------------------------------------------------------------
// 3. Network model
// -----------------------------------------------------------------------------

struct Edge {
    string destination;
    int weight;
};

class Network {
private:
    unordered_map<string, vector<Edge>> adjacency;

public:
    void addNode(const string& node) {
        adjacency.try_emplace(node);
    }

    void addEdge(
        const string& source,
        const string& destination,
        int weight
    ) {
        if (source.empty() || destination.empty()) {
            throw invalid_argument("Node names cannot be empty.");
        }

        if (weight <= 0) {
            throw invalid_argument("Edge weight must be positive.");
        }

        addNode(source);
        addNode(destination);

        adjacency[source].push_back({destination, weight});
    }

    bool containsNode(const string& node) const {
        return adjacency.find(node) != adjacency.end();
    }

    const vector<Edge>& neighbors(const string& node) const {
        auto iterator = adjacency.find(node);

        if (iterator == adjacency.end()) {
            throw out_of_range("Requested node does not exist.");
        }

        return iterator->second;
    }

    vector<string> nodes() const {
        vector<string> result;

        for (const auto& [node, edges] : adjacency) {
            result.push_back(node);
        }

        sort(result.begin(), result.end());
        return result;
    }

    size_t nodeCount() const {
        return adjacency.size();
    }

    size_t edgeCount() const {
        size_t total = 0;

        for (const auto& [node, edges] : adjacency) {
            total += edges.size();
        }

        return total;
    }
};

// -----------------------------------------------------------------------------
// 4. Graph invariant
// -----------------------------------------------------------------------------

bool verifyPositiveEdgeInvariant(const Network& network) {
    for (const string& node : network.nodes()) {
        for (const Edge& edge : network.neighbors(node)) {
            if (edge.weight <= 0) {
                return false;
            }

            if (!network.containsNode(edge.destination)) {
                return false;
            }
        }
    }

    return true;
}

// -----------------------------------------------------------------------------
// 5. Breadth-first reachability
// -----------------------------------------------------------------------------

bool isReachable(
    const Network& network,
    const string& source,
    const string& destination
) {
    if (!network.containsNode(source) || !network.containsNode(destination)) {
        return false;
    }

    queue<string> pending;
    unordered_set<string> visited;

    pending.push(source);
    visited.insert(source);

    while (!pending.empty()) {
        string current = pending.front();
        pending.pop();

        // Loop invariant:
        // every node in visited is reachable from source.
        if (current == destination) {
            return true;
        }

        for (const Edge& edge : network.neighbors(current)) {
            if (!visited.count(edge.destination)) {
                visited.insert(edge.destination);
                pending.push(edge.destination);
            }
        }
    }

    return false;
}

// -----------------------------------------------------------------------------
// 6. Shortest paths using Dijkstra's algorithm
// -----------------------------------------------------------------------------

struct PathResult {
    unordered_map<string, long long> distance;
    unordered_map<string, string> predecessor;
};

PathResult dijkstra(
    const Network& network,
    const string& source
) {
    if (!network.containsNode(source)) {
        throw invalid_argument("Source node does not exist.");
    }

    const long long INF = numeric_limits<long long>::max() / 4;

    unordered_map<string, long long> distance;
    unordered_map<string, string> predecessor;

    for (const string& node : network.nodes()) {
        distance[node] = INF;
    }

    distance[source] = 0;

    using QueueItem = pair<long long, string>;

    priority_queue<
        QueueItem,
        vector<QueueItem>,
        greater<QueueItem>
    > pending;

    pending.push({0, source});

    while (!pending.empty()) {
        auto [currentDistance, current] = pending.top();
        pending.pop();

        // Stale queue entries do not represent the current best distance.
        if (currentDistance != distance[current]) {
            continue;
        }

        /*
         * Proof invariant:
         *
         * For every vertex permanently processed by Dijkstra's algorithm,
         * distance[vertex] equals the shortest possible path distance from
         * source under the positive-edge precondition.
         *
         * The next unprocessed vertex has the smallest tentative distance.
         * Any alternative path reaching it through another unprocessed vertex
         * would have to be at least as long.
         */

        for (const Edge& edge : network.neighbors(current)) {
            if (currentDistance > INF - edge.weight) {
                throw overflow_error("Distance arithmetic overflow.");
            }

            long long candidate = currentDistance + edge.weight;

            if (candidate < distance[edge.destination]) {
                distance[edge.destination] = candidate;
                predecessor[edge.destination] = current;
                pending.push({candidate, edge.destination});
            }
        }
    }

    return {distance, predecessor};
}

// -----------------------------------------------------------------------------
// 7. Path reconstruction
// -----------------------------------------------------------------------------

vector<string> reconstructPath(
    const PathResult& result,
    const string& source,
    const string& destination
) {
    auto distanceIterator = result.distance.find(destination);

    if (distanceIterator == result.distance.end()) {
        throw invalid_argument("Destination was not present in result.");
    }

    const long long INF = numeric_limits<long long>::max() / 4;

    if (distanceIterator->second >= INF) {
        return {};
    }

    vector<string> reversedPath;
    string current = destination;

    reversedPath.push_back(current);

    while (current != source) {
        auto predecessorIterator = result.predecessor.find(current);

        if (predecessorIterator == result.predecessor.end()) {
            throw logic_error("Broken predecessor chain.");
        }

        current = predecessorIterator->second;
        reversedPath.push_back(current);

        if (reversedPath.size() > result.distance.size()) {
            throw logic_error("Predecessor cycle detected.");
        }
    }

    reverse(reversedPath.begin(), reversedPath.end());
    return reversedPath;
}

// -----------------------------------------------------------------------------
// 8. Route validation
// -----------------------------------------------------------------------------

long long calculatePathCost(
    const Network& network,
    const vector<string>& path
) {
    if (path.empty()) {
        throw invalid_argument("Path cannot be empty.");
    }

    long long total = 0;

    for (size_t index = 0; index + 1 < path.size(); ++index) {
        const string& source = path[index];
        const string& destination = path[index + 1];

        bool found = false;

        for (const Edge& edge : network.neighbors(source)) {
            if (edge.destination == destination) {
                total += edge.weight;
                found = true;
                break;
            }
        }

        if (!found) {
            throw logic_error(
                "Path contains a transition that does not exist."
            );
        }
    }

    return total;
}

// -----------------------------------------------------------------------------
// 9. Proof by cases: classify network nodes
// -----------------------------------------------------------------------------

enum class NodeClass {
    Isolated,
    SourceOnly,
    DestinationOnly,
    Intermediate,
    Bidirectional
};

NodeClass classifyNode(
    const Network& network,
    const string& node
) {
    if (!network.containsNode(node)) {
        throw invalid_argument("Unknown node.");
    }

    bool hasOutgoing = !network.neighbors(node).empty();
    bool hasIncoming = false;

    for (const string& candidate : network.nodes()) {
        for (const Edge& edge : network.neighbors(candidate)) {
            if (edge.destination == node) {
                hasIncoming = true;
            }
        }
    }

    if (!hasIncoming && !hasOutgoing) {
        return NodeClass::Isolated;
    }

    if (!hasIncoming && hasOutgoing) {
        return NodeClass::SourceOnly;
    }

    if (hasIncoming && !hasOutgoing) {
        return NodeClass::DestinationOnly;
    }

    bool hasReverseEdge = false;

    for (const string& candidate : network.nodes()) {
        for (const Edge& edge : network.neighbors(candidate)) {
            if (candidate == node) {
                continue;
            }

            if (edge.destination == node) {
                for (const Edge& reverse : network.neighbors(node)) {
                    if (reverse.destination == candidate) {
                        hasReverseEdge = true;
                    }
                }
            }
        }
    }

    return hasReverseEdge
        ? NodeClass::Bidirectional
        : NodeClass::Intermediate;
}

string nodeClassName(NodeClass nodeClass) {
    switch (nodeClass) {
        case NodeClass::Isolated:
            return "isolated";
        case NodeClass::SourceOnly:
            return "source-only";
        case NodeClass::DestinationOnly:
            return "destination-only";
        case NodeClass::Intermediate:
            return "intermediate";
        case NodeClass::Bidirectional:
            return "bidirectional";
    }

    return "unknown";
}

// -----------------------------------------------------------------------------
// 10. Pigeonhole-style collision detection
// -----------------------------------------------------------------------------

optional<pair<string, string>> findHashCollision(
    const vector<string>& nodes,
    size_t bucketCount
) {
    if (bucketCount == 0) {
        throw invalid_argument("bucketCount must be positive.");
    }

    vector<optional<string>> buckets(bucketCount);

    for (const string& node : nodes) {
        size_t hashValue = hash<string>{}(node);
        size_t bucket = hashValue % bucketCount;

        if (buckets[bucket].has_value()) {
            return make_pair(*buckets[bucket], node);
        }

        buckets[bucket] = node;
    }

    return nullopt;
}

// -----------------------------------------------------------------------------
// 11. Proof by contradiction: invalid negative edge
// -----------------------------------------------------------------------------

void validateDijkstraPrecondition(const Network& network) {
    /*
     * Dijkstra's correctness depends on nonnegative edge weights.
     *
     * If a negative edge were accepted, the greedy choice used in the
     * correctness proof could become invalid because a supposedly finalized
     * vertex might later be improved through a negative edge.
     *
     * The implementation therefore rejects the condition before execution.
     */
    if (!verifyPositiveEdgeInvariant(network)) {
        throw invalid_argument(
            "Dijkstra precondition violated: invalid edge detected."
        );
    }
}

// -----------------------------------------------------------------------------
// 12. Formal proof-style assertion
// -----------------------------------------------------------------------------

void assertShortestPathCorrectness(
    const Network& network,
    const string& source,
    const string& destination
) {
    validateDijkstraPrecondition(network);

    PathResult result = dijkstra(network, source);
    vector<string> path = reconstructPath(result, source, destination);

    if (path.empty()) {
        if (isReachable(network, source, destination)) {
            throw logic_error(
                "Reachable destination has no reconstructed path."
            );
        }

        return;
    }

    long long pathCost = calculatePathCost(network, path);

    if (pathCost != result.distance.at(destination)) {
        throw logic_error(
            "Path reconstruction contradicts computed shortest distance."
        );
    }
}

// -----------------------------------------------------------------------------
// 13. Full case-study execution
// -----------------------------------------------------------------------------

int main() {
    try {
        cout << string(72, '=') << '\n';
        cout << "PROOF TECHNIQUES: NETWORK ROUTING CASE STUDY\n";
        cout << string(72, '=') << "\n\n";

        // ---------------------------------------------------------------------
        // Basic logical proof demonstration
        // ---------------------------------------------------------------------

        cout << "=== Logical implication ===\n";

        cout << boolalpha;

        cout << "p=true, q=true:  p->q = "
             << implication(true, true) << '\n';

        cout << "p=true, q=false: p->q = "
             << implication(true, false) << '\n';

        cout << "p=false, q=true: p->q = "
             << implication(false, true) << '\n';

        // ---------------------------------------------------------------------
        // Direct proof
        // ---------------------------------------------------------------------

        cout << "\n=== Direct proof ===\n";

        long long a = 18;
        long long b = 26;

        assert(isEven(a));
        assert(isEven(b));

        long long m = a / 2;
        long long n = b / 2;

        cout << a << " = 2(" << m << ")\n";
        cout << b << " = 2(" << n << ")\n";
        cout << a + b << " = 2(" << m + n << ")\n";
        cout << "Therefore the sum is even.\n";

        // ---------------------------------------------------------------------
        // Counterexample
        // ---------------------------------------------------------------------

        cout << "\n=== Counterexample ===\n";

        vector<long long> candidates;
        for (long long value = 2; value <= 20; ++value) {
            candidates.push_back(value);
        }

        auto counterexample = findCounterexample(
            candidates,
            [](long long value) {
                // False universal claim: every prime is odd.
                return value % 2 == 1;
            }
        );

        if (counterexample.has_value()) {
            cout << "Counterexample to 'every prime is odd': "
                 << *counterexample << '\n';
        }

        // ---------------------------------------------------------------------
        // Build the realistic routing network
        // ---------------------------------------------------------------------

        cout << "\n=== Building network ===\n";

        Network network;

        network.addEdge("Gateway", "RouterA", 4);
        network.addEdge("Gateway", "RouterB", 2);
        network.addEdge("RouterA", "RouterC", 5);
        network.addEdge("RouterB", "RouterC", 1);
        network.addEdge("RouterB", "RouterA", 2);
        network.addEdge("RouterC", "Database", 3);
        network.addEdge("RouterA", "Database", 10);
        network.addEdge("Database", "Backup", 2);
        network.addEdge("RouterC", "Backup", 8);

        cout << "Nodes: " << network.nodeCount() << '\n';
        cout << "Directed edges: " << network.edgeCount() << '\n';

        // ---------------------------------------------------------------------
        // Graph invariant
        // ---------------------------------------------------------------------

        cout << "\n=== Graph invariant ===\n";

        bool invariantValid = verifyPositiveEdgeInvariant(network);

        cout << "Every edge has a positive weight and valid destination: "
             << invariantValid << '\n';

        if (!invariantValid) {
            throw logic_error("Network invariant failed.");
        }

        // ---------------------------------------------------------------------
        // Reachability
        // ---------------------------------------------------------------------

        cout << "\n=== Reachability ===\n";

        cout << "Gateway -> Backup reachable: "
             << isReachable(network, "Gateway", "Backup") << '\n';

        cout << "Backup -> Gateway reachable: "
             << isReachable(network, "Backup", "Gateway") << '\n';

        // ---------------------------------------------------------------------
        // Dijkstra
        // ---------------------------------------------------------------------

        cout << "\n=== Shortest-path proof ===\n";

        const string source = "Gateway";
        const string destination = "Backup";

        PathResult shortestPaths = dijkstra(network, source);
        vector<string> path =
            reconstructPath(shortestPaths, source, destination);

        cout << "Shortest distance from " << source
             << " to " << destination << ": "
             << shortestPaths.distance.at(destination) << '\n';

        cout << "Path: ";

        for (size_t index = 0; index < path.size(); ++index) {
            if (index != 0) {
                cout << " -> ";
            }

            cout << path[index];
        }

        cout << '\n';

        cout << "Reconstructed path cost: "
             << calculatePathCost(network, path) << '\n';

        // ---------------------------------------------------------------------
        // Correctness assertion
        // ---------------------------------------------------------------------

        cout << "\n=== Correctness contract ===\n";

        assertShortestPathCorrectness(
            network,
            "Gateway",
            "Backup"
        );

        cout << "Shortest-path correctness checks passed.\n";

        // ---------------------------------------------------------------------
        // Proof by cases
        // ---------------------------------------------------------------------

        cout << "\n=== Proof by cases: node classification ===\n";

        for (const string& node : network.nodes()) {
            cout << left << setw(10)
                 << node
                 << " : "
                 << nodeClassName(classifyNode(network, node))
                 << '\n';
        }

        // ---------------------------------------------------------------------
        // Pigeonhole principle
        // ---------------------------------------------------------------------

        cout << "\n=== Pigeonhole-style hash collision ===\n";

        vector<string> nodeNames = network.nodes();

        // Intentionally small bucket count makes the pigeonhole condition
        // visible. Seven nodes placed into three buckets guarantee a collision.
        auto collision = findHashCollision(nodeNames, 3);

        if (collision.has_value()) {
            cout << "Collision detected between: "
                 << collision->first
                 << " and "
                 << collision->second
                 << '\n';
        }

        // ---------------------------------------------------------------------
        // Edge cases
        // ---------------------------------------------------------------------

        cout << "\n=== Edge cases ===\n";

        cout << "Unknown source reachable result: "
             << isReachable(network, "Unknown", "Backup")
             << '\n';

        cout << "Unknown destination reachable result: "
             << isReachable(network, "Gateway", "Unknown")
             << '\n';

        try {
            network.addEdge("Gateway", "Invalid", -4);
        } catch (const invalid_argument& error) {
            cout << "Rejected invalid edge: "
                 << error.what() << '\n';
        }

        try {
            dijkstra(network, "Unknown");
        } catch (const invalid_argument& error) {
            cout << "Rejected invalid source: "
                 << error.what() << '\n';
        }

        // ---------------------------------------------------------------------
        // Complexity
        // ---------------------------------------------------------------------

        cout << "\n=== Complexity considerations ===\n";

        cout << "BFS reachability: O(V + E)\n";
        cout << "Dijkstra with binary heap: O((V + E) log V)\n";
        cout << "Path reconstruction: O(V) in the worst case\n";
        cout << "Network invariant validation: O(V + E)\n";

        // ---------------------------------------------------------------------
        // Final proof perspective
        // ---------------------------------------------------------------------

        cout << "\n=== Proof perspective ===\n";

        cout
            << "The case study uses assumptions, invariants, preconditions, "
               "postconditions, case analysis, counterexamples, and "
               "algorithmic correctness arguments.\n";

        cout
            << "Execution validates concrete instances. The correctness "
               "argument explains why the algorithm works for every input "
               "satisfying its stated assumptions.\n";

        cout << "\nCase study completed successfully.\n";
    }
    catch (const exception& error) {
        cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
