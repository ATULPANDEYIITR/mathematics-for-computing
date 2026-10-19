#include <algorithm>
#include <cmath>
#include <iostream>
#include <limits>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

struct Edge {
    int from;
    int to;
    double weight;
};

struct PathResult {
    vector<double> distance;
    vector<int> previous;
};

class Graph {
public:
    explicit Graph(int vertices) : adjacency(vertices), vertexCount(vertices) {
        if (vertices <= 0) {
            throw invalid_argument("Graph must contain at least one vertex.");
        }
    }

    void addEdge(int from, int to, double weight, bool undirected = false) {
        validateVertex(from);
        validateVertex(to);

        if (!isfinite(weight) || weight < 0) {
            throw invalid_argument(
                "This shortest-path model requires non-negative finite weights."
            );
        }

        adjacency[from].push_back({to, weight});
        edges.push_back({from, to, weight});

        if (undirected) {
            adjacency[to].push_back({from, weight});
            edges.push_back({to, from, weight});
        }
    }

    const vector<Edge>& neighbors(int vertex) const {
        validateVertex(vertex);
        return adjacency[vertex];
    }

    const vector<Edge>& getEdges() const {
        return edges;
    }

    int size() const {
        return vertexCount;
    }

private:
    vector<vector<Edge>> adjacency;
    vector<Edge> edges;
    int vertexCount;

    void validateVertex(int vertex) const {
        if (vertex < 0 || vertex >= vertexCount) {
            throw out_of_range("Vertex index is outside the graph.");
        }
    }
};

PathResult dijkstra(const Graph& graph, int source) {
    const double infinity = numeric_limits<double>::infinity();

    vector<double> distance(graph.size(), infinity);
    vector<int> previous(graph.size(), -1);

    using QueueItem = pair<double, int>;
    priority_queue<QueueItem, vector<QueueItem>, greater<QueueItem>> frontier;

    distance[source] = 0;
    frontier.push({0, source});

    while (!frontier.empty()) {
        auto [currentDistance, current] = frontier.top();
        frontier.pop();

        // The heap can contain stale entries because std::priority_queue
        // has no decrease-key operation. Ignoring stale entries preserves
        // the normal O((V+E) log V) Dijkstra complexity.
        if (currentDistance != distance[current]) {
            continue;
        }

        for (const Edge& edge : graph.neighbors(current)) {
            double candidate = currentDistance + edge.weight;

            if (candidate < distance[edge.to]) {
                distance[edge.to] = candidate;
                previous[edge.to] = current;
                frontier.push({candidate, edge.to});
            }
        }
    }

    return {distance, previous};
}

vector<int> buildPath(
    const vector<int>& previous,
    int source,
    int destination
) {
    vector<int> path;

    for (int current = destination; current != -1; current = previous[current]) {
        path.push_back(current);

        if (current == source) {
            reverse(path.begin(), path.end());
            return path;
        }
    }

    return {};
}

class UnionFind {
public:
    explicit UnionFind(int size) : parent(size), rank(size, 0) {
        for (int i = 0; i < size; ++i) {
            parent[i] = i;
        }
    }

    int find(int value) {
        if (parent[value] != value) {
            parent[value] = find(parent[value]);
        }
        return parent[value];
    }

    bool unite(int first, int second) {
        first = find(first);
        second = find(second);

        if (first == second) {
            return false;
        }

        if (rank[first] < rank[second]) {
            swap(first, second);
        }

        parent[second] = first;

        if (rank[first] == rank[second]) {
            ++rank[first];
        }

        return true;
    }

private:
    vector<int> parent;
    vector<int> rank;
};

struct NetworkPlan {
    vector<Edge> edges;
    double totalCost;
};

NetworkPlan minimumSpanningTree(const Graph& graph) {
    vector<Edge> sorted = graph.getEdges();

    sort(
        sorted.begin(),
        sorted.end(),
        [](const Edge& left, const Edge& right) {
            return left.weight < right.weight;
        }
    );

    UnionFind sets(graph.size());
    NetworkPlan plan{{}, 0.0};

    for (const Edge& edge : sorted) {
        if (sets.unite(edge.from, edge.to)) {
            plan.edges.push_back(edge);
            plan.totalCost += edge.weight;

            if (plan.edges.size() == static_cast<size_t>(graph.size() - 1)) {
                break;
            }
        }
    }

    if (plan.edges.size() != static_cast<size_t>(graph.size() - 1)) {
        throw runtime_error(
            "The infrastructure graph is disconnected; "
            "a spanning network cannot be built."
        );
    }

    return plan;
}

struct CapacityArc {
    int to;
    int reverseIndex;
    int capacity;
};

class FlowNetwork {
public:
    explicit FlowNetwork(int vertices) : graph(vertices) {}

    void addArc(int from, int to, int capacity) {
        if (capacity < 0) {
            throw invalid_argument("Capacity cannot be negative.");
        }

        CapacityArc forward{to, static_cast<int>(graph[to].size()), capacity};
        CapacityArc reverse{from, static_cast<int>(graph[from].size()), 0};

        graph[from].push_back(forward);
        graph[to].push_back(reverse);
    }

    int maxFlow(int source, int sink) {
        int totalFlow = 0;

        while (true) {
            vector<int> parentVertex(graph.size(), -1);
            vector<int> parentEdge(graph.size(), -1);
            queue<int> queue;

            parentVertex[source] = source;
            queue.push(source);

            while (!queue.empty() && parentVertex[sink] == -1) {
                int current = queue.front();
                queue.pop();

                for (int index = 0; index < static_cast<int>(graph[current].size()); ++index) {
                    const CapacityArc& arc = graph[current][index];

                    if (arc.capacity > 0 && parentVertex[arc.to] == -1) {
                        parentVertex[arc.to] = current;
                        parentEdge[arc.to] = index;
                        queue.push(arc.to);

                        if (arc.to == sink) {
                            break;
                        }
                    }
                }
            }

            if (parentVertex[sink] == -1) {
                break;
            }

            int bottleneck = numeric_limits<int>::max();

            for (int current = sink; current != source; current = parentVertex[current]) {
                int previous = parentVertex[current];
                int edgeIndex = parentEdge[current];
                bottleneck = min(bottleneck, graph[previous][edgeIndex].capacity);
            }

            for (int current = sink; current != source; current = parentVertex[current]) {
                int previous = parentVertex[current];
                int edgeIndex = parentEdge[current];

                CapacityArc& forward = graph[previous][edgeIndex];
                CapacityArc& reverse = graph[current][forward.reverseIndex];

                forward.capacity -= bottleneck;
                reverse.capacity += bottleneck;
            }

            totalFlow += bottleneck;
        }

        return totalFlow;
    }

private:
    vector<vector<CapacityArc>> graph;
};

void runShortestPathCaseStudy() {
    // A logistics company routes shipments through regional facilities.
    // Edge weights represent expected travel time in hours.
    Graph logistics(6);

    logistics.addEdge(0, 1, 4);
    logistics.addEdge(0, 2, 2);
    logistics.addEdge(2, 1, 1);
    logistics.addEdge(1, 3, 3);
    logistics.addEdge(2, 3, 5);
    logistics.addEdge(3, 4, 2);
    logistics.addEdge(1, 4, 9);
    logistics.addEdge(4, 5, 3);

    PathResult result = dijkstra(logistics, 0);
    vector<int> route = buildPath(result.previous, 0, 5);

    cout << "Logistics shortest route\n";
    cout << "Route: ";

    for (size_t i = 0; i < route.size(); ++i) {
        if (i != 0) {
            cout << " -> ";
        }
        cout << route[i];
    }

    cout << "\nTravel time: " << result.distance[5] << " hours\n";
}

void runInfrastructureCaseStudy() {
    // For a physical network, the objective is different from routing:
    // connect every site while minimizing total cable/fiber deployment cost.
    Graph infrastructure(7);

    infrastructure.addEdge(0, 1, 8, true);
    infrastructure.addEdge(0, 2, 3, true);
    infrastructure.addEdge(1, 2, 2, true);
    infrastructure.addEdge(1, 3, 7, true);
    infrastructure.addEdge(2, 3, 4, true);
    infrastructure.addEdge(2, 4, 6, true);
    infrastructure.addEdge(3, 4, 1, true);
    infrastructure.addEdge(3, 5, 5, true);
    infrastructure.addEdge(4, 6, 4, true);
    infrastructure.addEdge(5, 6, 2, true);

    NetworkPlan plan = minimumSpanningTree(infrastructure);

    cout << "\nMinimum-cost infrastructure\n";
    for (const Edge& edge : plan.edges) {
        cout << edge.from << " -- " << edge.to
             << " cost=" << edge.weight << '\n';
    }
    cout << "Total deployment cost: " << plan.totalCost << '\n';
}

void runCapacityCaseStudy() {
    // This network models a service provider where links have hard capacity
    // limits. Shortest paths cannot answer the question "how much traffic
    // can the network carry?", so maximum-flow optimization is appropriate.
    FlowNetwork network(6);

    network.addArc(0, 1, 12);
    network.addArc(0, 2, 8);
    network.addArc(1, 3, 7);
    network.addArc(1, 4, 5);
    network.addArc(2, 3, 4);
    network.addArc(2, 4, 6);
    network.addArc(3, 5, 8);
    network.addArc(4, 5, 10);

    cout << "\nMaximum network throughput: "
         << network.maxFlow(0, 5) << " units\n";
}

void demonstrateTradeoffs() {
    cout << "\nOptimization trade-offs\n";
    cout << "Dijkstra prioritizes route cost from one source and requires "
            "non-negative weights.\n";
    cout << "Kruskal minimizes total edge cost while preserving connectivity; "
            "it does not minimize every source-to-destination route.\n";
    cout << "Maximum flow optimizes aggregate throughput under capacity "
            "constraints rather than path length.\n";
    cout << "Sparse adjacency lists use O(V + E) storage, while a dense "
            "all-pairs matrix requires O(V^2) storage.\n";
}

int main() {
    try {
        runShortestPathCaseStudy();
        runInfrastructureCaseStudy();
        runCapacityCaseStudy();
        demonstrateTradeoffs();
    } catch (const exception& error) {
        cerr << "Optimization failure: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
