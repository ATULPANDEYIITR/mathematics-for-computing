#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <queue>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace std;

class GraphError : public runtime_error {
public:
    explicit GraphError(const string& message) : runtime_error(message) {}
};

struct TraversalResult {
    vector<int> order;
    vector<int> parent;
    vector<int> distance;

    vector<int> pathTo(int target) const {
        if (target < 0 || target >= static_cast<int>(parent.size())) {
            throw GraphError("Target vertex is out of range.");
        }

        if (distance[target] == -1) {
            return {};
        }

        vector<int> path;
        for (int current = target; current != -1; current = parent[current]) {
            path.push_back(current);
        }

        reverse(path.begin(), path.end());
        return path;
    }
};

/*
 * Case study: a transport network whose intersections are vertices and
 * roads are represented by matrix entries.
 *
 * An unweighted matrix supports BFS for the fewest-road route.
 * A weighted matrix supports Dijkstra for minimum travel cost.
 */
class GraphMatrix {
private:
    vector<vector<double>> matrix;
    bool directed;
    bool weighted;
    int vertexCount;

    void validate() const {
        for (const auto& row : matrix) {
            if (static_cast<int>(row.size()) != vertexCount) {
                throw GraphError("Adjacency matrix must be square.");
            }
        }

        for (int i = 0; i < vertexCount; ++i) {
            for (int j = 0; j < vertexCount; ++j) {
                const double value = matrix[i][j];

                if (!isfinite(value)) {
                    throw GraphError("Matrix entries must be finite.");
                }

                if (weighted) {
                    if (i != j && value < 0) {
                        throw GraphError("Negative weights are unsupported.");
                    }
                } else if (value != 0.0 && value != 1.0) {
                    throw GraphError("Unweighted entries must be zero or one.");
                }

                if (!directed && !weighted && matrix[i][j] != matrix[j][i]) {
                    throw GraphError("Undirected matrix must be symmetric.");
                }
            }
        }
    }

    void checkVertex(int vertex) const {
        if (vertex < 0 || vertex >= vertexCount) {
            throw GraphError("Vertex index is outside the graph.");
        }
    }

public:
    GraphMatrix(
        vector<vector<double>> input,
        bool isDirected = false,
        bool isWeighted = false
    )
        : matrix(move(input)),
          directed(isDirected),
          weighted(isWeighted),
          vertexCount(static_cast<int>(matrix.size())) {
        validate();
    }

    int size() const {
        return vertexCount;
    }

    vector<int> neighbors(int vertex) const {
        checkVertex(vertex);

        vector<int> result;
        for (int neighbor = 0; neighbor < vertexCount; ++neighbor) {
            if (neighbor != vertex && matrix[vertex][neighbor] != 0.0) {
                result.push_back(neighbor);
            }
        }
        return result;
    }

    TraversalResult bfs(int start) const {
        checkVertex(start);

        TraversalResult result;
        result.parent.assign(vertexCount, -1);
        result.distance.assign(vertexCount, -1);

        queue<int> pending;
        vector<bool> discovered(vertexCount, false);

        discovered[start] = true;
        result.distance[start] = 0;
        pending.push(start);

        while (!pending.empty()) {
            const int current = pending.front();
            pending.pop();
            result.order.push_back(current);

            for (const int next : neighbors(current)) {
                if (discovered[next]) {
                    continue;
                }

                discovered[next] = true;
                result.parent[next] = current;
                result.distance[next] = result.distance[current] + 1;
                pending.push(next);
            }
        }

        return result;
    }

    TraversalResult dfs(int start) const {
        checkVertex(start);

        TraversalResult result;
        result.parent.assign(vertexCount, -1);
        result.distance.assign(vertexCount, -1);

        vector<bool> discovered(vertexCount, false);
        vector<pair<int, int>> pending;
        pending.emplace_back(start, 0);

        while (!pending.empty()) {
            const auto [current, depth] = pending.back();
            pending.pop_back();

            if (discovered[current]) {
                continue;
            }

            discovered[current] = true;
            result.order.push_back(current);
            result.distance[current] = depth;

            vector<int> adjacent = neighbors(current);
            for (auto iterator = adjacent.rbegin();
                 iterator != adjacent.rend(); ++iterator) {
                if (!discovered[*iterator]) {
                    result.parent[*iterator] = current;
                    pending.emplace_back(*iterator, depth + 1);
                }
            }
        }

        return result;
    }

    vector<vector<int>> connectedComponents() const {
        if (directed) {
            throw GraphError(
                "Use weakly or strongly connected components for directed graphs."
            );
        }

        vector<bool> assigned(vertexCount, false);
        vector<vector<int>> components;

        for (int start = 0; start < vertexCount; ++start) {
            if (assigned[start]) {
                continue;
            }

            TraversalResult result = bfs(start);
            components.push_back(result.order);

            for (const int vertex : result.order) {
                assigned[vertex] = true;
            }
        }

        return components;
    }

    vector<double> dijkstra(int start) const {
        checkVertex(start);

        if (!weighted) {
            throw GraphError("Dijkstra requires a weighted graph.");
        }

        const double infinity = numeric_limits<double>::infinity();
        vector<double> distances(vertexCount, infinity);
        vector<bool> settled(vertexCount, false);
        distances[start] = 0.0;

        // The matrix representation makes this O(V^2) implementation
        // natural because finding the next minimum scans all vertices.
        for (int iteration = 0; iteration < vertexCount; ++iteration) {
            int current = -1;

            for (int vertex = 0; vertex < vertexCount; ++vertex) {
                if (!settled[vertex] &&
                    (current == -1 || distances[vertex] < distances[current])) {
                    current = vertex;
                }
            }

            if (current == -1 || distances[current] == infinity) {
                break;
            }

            settled[current] = true;

            for (int neighbor = 0; neighbor < vertexCount; ++neighbor) {
                const double weight = matrix[current][neighbor];

                if (neighbor == current || weight == 0.0 ||
                    settled[neighbor]) {
                    continue;
                }

                distances[neighbor] = min(
                    distances[neighbor],
                    distances[current] + weight
                );
            }
        }

        return distances;
    }

    void printMatrix() const {
        for (const auto& row : matrix) {
            for (const double value : row) {
                cout << setw(5) << value;
            }
            cout << '\n';
        }
    }
};

template <typename T>
void printVector(const string& label, const vector<T>& values) {
    cout << label << ": ";
    for (const auto& value : values) {
        cout << value << ' ';
    }
    cout << '\n';
}

void demonstrateTransportNetwork() {
    cout << "\n=== Transport network ===\n";

    GraphMatrix roads({
        {0, 1, 1, 0, 0, 0},
        {1, 0, 0, 1, 1, 0},
        {1, 0, 0, 0, 1, 0},
        {0, 1, 0, 0, 0, 1},
        {0, 1, 1, 0, 0, 1},
        {0, 0, 0, 1, 1, 0}
    });

    cout << "Road adjacency matrix:\n";
    roads.printMatrix();

    const TraversalResult breadthFirst = roads.bfs(0);
    printVector("BFS visit order", breadthFirst.order);
    printVector("Minimum road counts", breadthFirst.distance);
    printVector("Route from 0 to 5", breadthFirst.pathTo(5));

    const TraversalResult depthFirst = roads.dfs(0);
    printVector("DFS visit order", depthFirst.order);

    const auto components = roads.connectedComponents();
    cout << "Connected components: " << components.size() << '\n';

    for (size_t i = 0; i < components.size(); ++i) {
        printVector("Component", components[i]);
    }
}

void demonstrateWeightedNetwork() {
    cout << "\n=== Weighted transport costs ===\n";

    GraphMatrix network({
        {0, 4, 2, 0},
        {4, 0, 1, 5},
        {2, 1, 0, 8},
        {0, 5, 8, 0}
    }, false, true);

    printVector("Minimum costs from intersection 0", network.dijkstra(0));
}

void demonstrateFailureHandling() {
    cout << "\n=== Invalid graph handling ===\n";

    try {
        GraphMatrix invalid({
            {0, 1},
            {0, 0}
        });
    } catch (const GraphError& error) {
        cout << "Rejected asymmetric matrix: " << error.what() << '\n';
    }

    try {
        GraphMatrix invalid({
            {0, -2},
            {-2, 0}
        }, false, true);
    } catch (const GraphError& error) {
        cout << "Rejected negative edge: " << error.what() << '\n';
    }

    try {
        GraphMatrix graph({{0, 1}, {1, 0}});
        graph.bfs(7);
    } catch (const GraphError& error) {
        cout << "Rejected invalid start: " << error.what() << '\n';
    }
}

int main() {
    try {
        demonstrateTransportNetwork();
        demonstrateWeightedNetwork();
        demonstrateFailureHandling();
    } catch (const exception& error) {
        cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
