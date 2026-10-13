#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

class TreeError : public runtime_error {
public:
    explicit TreeError(const string& message) : runtime_error(message) {}
};

struct Edge {
    string from;
    string to;
    double weight;
};

class DisjointSet {
private:
    unordered_map<string, string> parent;
    unordered_map<string, int> rank;

public:
    explicit DisjointSet(const vector<string>& vertices) {
        for (const string& vertex : vertices) {
            parent[vertex] = vertex;
            rank[vertex] = 0;
        }
    }

    string find(const string& vertex) {
        auto it = parent.find(vertex);
        if (it == parent.end()) {
            throw TreeError("Unknown vertex in disjoint-set operation.");
        }

        if (it->second != vertex) {
            it->second = find(it->second);
        }
        return it->second;
    }

    bool unite(const string& a, const string& b) {
        string rootA = find(a);
        string rootB = find(b);

        if (rootA == rootB) return false;

        // Union by rank prevents the representative forest from becoming tall.
        if (rank[rootA] < rank[rootB]) swap(rootA, rootB);
        parent[rootB] = rootA;

        if (rank[rootA] == rank[rootB]) ++rank[rootA];
        return true;
    }
};

class Network {
private:
    vector<string> vertices;
    unordered_map<string, vector<pair<string, double>>> adjacency;
    vector<Edge> edges;

public:
    explicit Network(vector<string> nodes) : vertices(move(nodes)) {
        if (vertices.empty()) {
            throw TreeError("The network must contain at least one vertex.");
        }

        unordered_set<string> unique;
        for (const string& vertex : vertices) {
            if (vertex.empty() || !unique.insert(vertex).second) {
                throw TreeError("Vertex names must be unique and nonempty.");
            }
            adjacency[vertex] = {};
        }
    }

    void addEdge(const string& from, const string& to, double weight) {
        if (!adjacency.count(from) || !adjacency.count(to)) {
            throw TreeError("Both edge endpoints must exist.");
        }
        if (from == to) throw TreeError("Self-loops are not accepted.");
        if (!isfinite(weight)) throw TreeError("Edge weight must be finite.");

        for (const auto& [neighbor, existingWeight] : adjacency[from]) {
            (void)existingWeight;
            if (neighbor == to) throw TreeError("Duplicate edge rejected.");
        }

        adjacency[from].push_back({to, weight});
        adjacency[to].push_back({from, weight});
        edges.push_back({from, to, weight});
    }

    bool connected() const {
        if (vertices.empty()) return false;

        unordered_set<string> visited;
        queue<string> pending;
        pending.push(vertices.front());
        visited.insert(vertices.front());

        while (!pending.empty()) {
            string current = pending.front();
            pending.pop();

            for (const auto& [neighbor, weight] : adjacency.at(current)) {
                (void)weight;
                if (visited.insert(neighbor).second) {
                    pending.push(neighbor);
                }
            }
        }

        return visited.size() == vertices.size();
    }

    bool hasCycle() const {
        unordered_set<string> visited;

        for (const string& start : vertices) {
            if (visited.count(start)) continue;

            vector<pair<string, string>> stack;
            stack.push_back({start, ""});

            while (!stack.empty()) {
                auto [vertex, parentVertex] = stack.back();
                stack.pop_back();

                if (visited.count(vertex)) continue;
                visited.insert(vertex);

                for (const auto& [neighbor, weight] : adjacency.at(vertex)) {
                    (void)weight;
                    if (neighbor == parentVertex) continue;
                    if (visited.count(neighbor)) return true;
                    stack.push_back({neighbor, vertex});
                }
            }
        }

        return false;
    }

    bool isTree() const {
        return !vertices.empty() &&
               edges.size() == vertices.size() - 1 &&
               connected();
    }

    vector<Edge> minimumSpanningTree(double& totalWeight) const {
        vector<Edge> ordered = edges;
        sort(ordered.begin(), ordered.end(),
             [](const Edge& a, const Edge& b) {
                 if (a.weight != b.weight) return a.weight < b.weight;
                 if (a.from != b.from) return a.from < b.from;
                 return a.to < b.to;
             });

        DisjointSet sets(vertices);
        vector<Edge> result;
        totalWeight = 0.0;

        // Kruskal accepts an edge only when it joins two different components.
        for (const Edge& edge : ordered) {
            if (sets.unite(edge.from, edge.to)) {
                result.push_back(edge);
                totalWeight += edge.weight;
            }
        }

        if (result.size() != vertices.size() - 1) {
            throw TreeError("The network is disconnected; no spanning tree exists.");
        }

        return result;
    }

    vector<string> shortestUnweightedPath(
        const string& source, const string& destination
    ) const {
        if (!adjacency.count(source) || !adjacency.count(destination)) {
            throw TreeError("Unknown path endpoint.");
        }

        queue<string> pending;
        unordered_map<string, string> parent;
        parent[source] = "";
        pending.push(source);

        while (!pending.empty()) {
            string current = pending.front();
            pending.pop();

            if (current == destination) break;

            for (const auto& [neighbor, weight] : adjacency.at(current)) {
                (void)weight;
                if (!parent.count(neighbor)) {
                    parent[neighbor] = current;
                    pending.push(neighbor);
                }
            }
        }

        if (!parent.count(destination)) return {};

        vector<string> path;
        for (string current = destination; !current.empty();
             current = parent.at(current)) {
            path.push_back(current);
        }

        reverse(path.begin(), path.end());
        return path;
    }

    size_t vertexCount() const { return vertices.size(); }
    size_t edgeCount() const { return edges.size(); }
};

struct BinaryNode {
    int key;
    BinaryNode* left = nullptr;
    BinaryNode* right = nullptr;

    explicit BinaryNode(int value) : key(value) {}
};

void inorder(const BinaryNode* root, vector<int>& output) {
    vector<const BinaryNode*> stack;
    const BinaryNode* current = root;

    while (current != nullptr || !stack.empty()) {
        while (current != nullptr) {
            stack.push_back(current);
            current = current->left;
        }

        current = stack.back();
        stack.pop_back();
        output.push_back(current->key);
        current = current->right;
    }
}

int treeHeight(const BinaryNode* root) {
    if (root == nullptr) return -1;

    // Iterative level-order traversal avoids recursive stack exhaustion.
    queue<pair<const BinaryNode*, int>> pending;
    pending.push({root, 0});
    int maximumDepth = 0;

    while (!pending.empty()) {
        auto [node, depth] = pending.front();
        pending.pop();
        maximumDepth = max(maximumDepth, depth);

        if (node->left) pending.push({node->left, depth + 1});
        if (node->right) pending.push({node->right, depth + 1});
    }

    return maximumDepth;
}

void destroyTree(BinaryNode* root) {
    if (root == nullptr) return;
    destroyTree(root->left);
    destroyTree(root->right);
    delete root;
}

int main() {
    try {
        cout << "REPOSITORY SERVICE NETWORK\n";

        // Vertices represent service endpoints. Edge weights represent
        // deployment-link cost, so the MST minimizes total installation cost.
        Network network({"gateway", "api", "cache", "database", "worker"});
        network.addEdge("gateway", "api", 4);
        network.addEdge("gateway", "cache", 7);
        network.addEdge("api", "cache", 2);
        network.addEdge("api", "database", 8);
        network.addEdge("cache", "database", 3);
        network.addEdge("cache", "worker", 6);
        network.addEdge("database", "worker", 1);

        cout << boolalpha;
        cout << "Vertices: " << network.vertexCount() << '\n';
        cout << "Edges: " << network.edgeCount() << '\n';
        cout << "Connected: " << network.connected() << '\n';
        cout << "Contains a cycle: " << network.hasCycle() << '\n';
        cout << "Original network is a tree: " << network.isTree() << '\n';

        double totalCost = 0.0;
        vector<Edge> mst = network.minimumSpanningTree(totalCost);

        cout << fixed << setprecision(2);
        cout << "\nMinimum-cost spanning tree\n";
        for (const Edge& edge : mst) {
            cout << edge.from << " -- " << edge.to
                 << " : " << edge.weight << '\n';
        }
        cout << "Total cost: " << totalCost << '\n';

        vector<string> path =
            network.shortestUnweightedPath("gateway", "worker");
        cout << "Fewest-link path from gateway to worker: ";
        for (size_t i = 0; i < path.size(); ++i) {
            if (i) cout << " -> ";
            cout << path[i];
        }
        cout << '\n';

        cout << "\nBINARY SEARCH TREE\n";
        BinaryNode* root = new BinaryNode(40);
        root->left = new BinaryNode(20);
        root->right = new BinaryNode(60);
        root->left->left = new BinaryNode(10);
        root->left->right = new BinaryNode(30);
        root->right->left = new BinaryNode(50);
        root->right->right = new BinaryNode(70);

        vector<int> sortedKeys;
        inorder(root, sortedKeys);

        cout << "Inorder keys: ";
        for (int key : sortedKeys) cout << key << ' ';
        cout << "\nHeight in edges: " << treeHeight(root) << '\n';

        destroyTree(root);

        cout << "\nEDGE CASE: disconnected graph\n";
        Network disconnected({"node-a", "node-b", "node-c"});
        disconnected.addEdge("node-a", "node-b", 2);

        try {
            double unusedCost = 0.0;
            disconnected.minimumSpanningTree(unusedCost);
        } catch (const TreeError& error) {
            cout << "Correctly rejected: " << error.what() << '\n';
        }

        cout << "\nAll case-study operations completed.\n";
    } catch (const exception& error) {
        cerr << "Failure: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
