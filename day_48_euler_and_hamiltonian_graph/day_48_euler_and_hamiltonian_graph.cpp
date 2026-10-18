#include <algorithm>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <vector>

using namespace std;

/*
 * Case study: an inspection team must traverse every road segment in a
 * maintenance district, while a separate planning task must visit every
 * inspection station exactly once.
 *
 * The first task is Eulerian: edges represent road segments.
 * The second task is Hamiltonian: vertices represent inspection stations.
 */

class DistrictGraph {
private:
    vector<string> names;
    vector<vector<int>> adjacency;
    vector<pair<int, int>> edges;

    static string edgeKey(int u, int v) {
        if (u > v) swap(u, v);
        return to_string(u) + ":" + to_string(v);
    }

    void validateVertex(int v) const {
        if (v < 0 || v >= static_cast<int>(names.size())) {
            throw out_of_range("Vertex index is outside the graph.");
        }
    }

public:
    explicit DistrictGraph(vector<string> vertices)
        : names(move(vertices)), adjacency(names.size()) {
        unordered_set<string> uniqueNames;
        for (const auto& name : names) {
            if (!uniqueNames.insert(name).second) {
                throw invalid_argument("Vertex names must be unique.");
            }
        }
    }

    void addEdge(int u, int v) {
        validateVertex(u);
        validateVertex(v);
        if (u == v) throw invalid_argument("Self-loops are unsupported.");

        const string key = edgeKey(u, v);
        for (const auto& [a, b] : edges) {
            if (edgeKey(a, b) == key) {
                throw invalid_argument("Duplicate undirected edge.");
            }
        }

        edges.emplace_back(u, v);
        adjacency[u].push_back(v);
        adjacency[v].push_back(u);
    }

    int vertexCount() const {
        return static_cast<int>(names.size());
    }

    int edgeCount() const {
        return static_cast<int>(edges.size());
    }

    bool connectedIgnoringIsolated() const {
        int start = -1;
        for (int v = 0; v < vertexCount(); ++v) {
            if (!adjacency[v].empty()) {
                start = v;
                break;
            }
        }
        if (start == -1) return true;

        vector<bool> visited(vertexCount(), false);
        vector<int> stack{start};

        while (!stack.empty()) {
            int u = stack.back();
            stack.pop_back();

            if (visited[u]) continue;
            visited[u] = true;

            for (int v : adjacency[u]) {
                if (!visited[v]) stack.push_back(v);
            }
        }

        for (int v = 0; v < vertexCount(); ++v) {
            if (!adjacency[v].empty() && !visited[v]) return false;
        }
        return true;
    }

    bool hasEulerTrail() const {
        if (!connectedIgnoringIsolated()) return false;

        int odd = 0;
        for (const auto& neighbors : adjacency) {
            if (neighbors.size() % 2 != 0) ++odd;
        }
        return odd == 0 || odd == 2;
    }

    bool hasEulerCircuit() const {
        if (!connectedIgnoringIsolated()) return false;

        for (const auto& neighbors : adjacency) {
            if (neighbors.size() % 2 != 0) return false;
        }
        return true;
    }

    vector<int> eulerTrail() const {
        if (!hasEulerTrail()) return {};

        if (edges.empty()) {
            return vertexCount() ? vector<int>{0} : vector<int>{};
        }

        int start = -1;
        for (int v = 0; v < vertexCount(); ++v) {
            if (adjacency[v].size() % 2 != 0) {
                start = v;
                break;
            }
        }
        if (start == -1) {
            for (int v = 0; v < vertexCount(); ++v) {
                if (!adjacency[v].empty()) {
                    start = v;
                    break;
                }
            }
        }

        vector<vector<pair<int, int>>> indexed(vertexCount());
        for (int id = 0; id < edgeCount(); ++id) {
            auto [u, v] = edges[id];
            indexed[u].push_back({v, id});
            indexed[v].push_back({u, id});
        }

        // Edge IDs are essential: an Euler trail uses every edge once,
        // including distinct edges that might share endpoints in a multigraph.
        vector<bool> used(edgeCount(), false);
        vector<int> stack{start};
        vector<int> result;

        while (!stack.empty()) {
            int u = stack.back();

            while (!indexed[u].empty() &&
                   used[indexed[u].back().second]) {
                indexed[u].pop_back();
            }

            if (indexed[u].empty()) {
                result.push_back(u);
                stack.pop_back();
            } else {
                auto [v, id] = indexed[u].back();
                indexed[u].pop_back();

                if (!used[id]) {
                    used[id] = true;
                    stack.push_back(v);
                }
            }
        }

        if (count(used.begin(), used.end(), true) != edgeCount()) return {};
        reverse(result.begin(), result.end());
        return result;
    }

    bool isHamiltonianPath(const vector<int>& path) const {
        if (path.size() != names.size()) return false;

        vector<bool> seen(vertexCount(), false);
        for (int i = 0; i < static_cast<int>(path.size()); ++i) {
            int u = path[i];
            if (u < 0 || u >= vertexCount() || seen[u]) return false;
            seen[u] = true;

            if (i > 0) {
                int previous = path[i - 1];
                if (find(adjacency[previous].begin(),
                         adjacency[previous].end(), u) == adjacency[previous].end()) {
                    return false;
                }
            }
        }
        return true;
    }

    vector<int> findHamiltonianPath() const {
        vector<int> path;
        vector<bool> visited(vertexCount(), false);

        function<bool(int)> search = [&](int u) {
            path.push_back(u);
            visited[u] = true;

            if (static_cast<int>(path.size()) == vertexCount()) return true;

            for (int v : adjacency[u]) {
                if (!visited[v] && search(v)) return true;
            }

            visited[u] = false;
            path.pop_back();
            return false;
        };

        if (vertexCount() == 0) return {};
        for (int start = 0; start < vertexCount(); ++start) {
            if (search(start)) return path;
        }
        return {};
    }

    vector<int> findHamiltonianCycle() const {
        if (vertexCount() < 3) return {};

        // A fixed starting vertex avoids searching equivalent rotations.
        vector<int> path{0};
        vector<bool> visited(vertexCount(), false);
        visited[0] = true;

        function<bool(int)> search = [&](int u) {
            if (static_cast<int>(path.size()) == vertexCount()) {
                return find(adjacency[u].begin(), adjacency[u].end(), 0)
                    != adjacency[u].end();
            }

            for (int v : adjacency[u]) {
                if (visited[v]) continue;

                visited[v] = true;
                path.push_back(v);

                if (search(v)) return true;

                path.pop_back();
                visited[v] = false;
            }
            return false;
        };

        return search(0) ? path : vector<int>{};
    }

    void printRoute(const vector<int>& route) const {
        if (route.empty()) {
            cout << "No route found\n";
            return;
        }

        for (size_t i = 0; i < route.size(); ++i) {
            if (i) cout << " -> ";
            cout << names[route[i]];
        }
        cout << '\n';
    }

    void report(const string& title) const {
        cout << "\n" << title << '\n';
        for (int v = 0; v < vertexCount(); ++v) {
            cout << names[v] << " degree: " << adjacency[v].size() << '\n';
        }

        cout << "Euler trail exists: "
             << (hasEulerTrail() ? "yes" : "no") << '\n';
        cout << "Euler circuit exists: "
             << (hasEulerCircuit() ? "yes" : "no") << '\n';

        cout << "Euler route: ";
        printRoute(eulerTrail());

        cout << "Hamiltonian path: ";
        printRoute(findHamiltonianPath());

        cout << "Hamiltonian cycle: ";
        printRoute(findHamiltonianCycle());
    }
};

int main() {
    try {
        DistrictGraph maintenance({
            "Depot", "North", "East", "South", "West"
        });

        maintenance.addEdge(0, 1);
        maintenance.addEdge(1, 2);
        maintenance.addEdge(2, 3);
        maintenance.addEdge(3, 4);
        maintenance.addEdge(4, 0);

        maintenance.report("Maintenance district: five-segment ring");

        DistrictGraph delivery({
            "Hub", "Warehouse", "Hospital", "School"
        });

        delivery.addEdge(0, 1);
        delivery.addEdge(0, 2);
        delivery.addEdge(0, 3);
        delivery.addEdge(1, 2);
        delivery.addEdge(1, 3);
        delivery.addEdge(2, 3);

        delivery.report("Inspection stations: complete network K4");

        DistrictGraph broken({
            "SiteA", "SiteB", "SiteC", "SiteD"
        });

        broken.addEdge(0, 1);
        broken.addEdge(2, 3);
        broken.report("Disconnected road segments");

    } catch (const exception& error) {
        cerr << "Graph construction or analysis failed: "
             << error.what() << '\n';
        return 1;
    }

    return 0;
}
