#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <queue>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

/*
 * Graph theory case study: campus network analysis.
 *
 * The model supports directed communication links and undirected physical
 * links, weighted edges, isolated vertices, BFS routing, and matrix output.
 * C++17 standard library only.
 */

class Graph {
public:
    using Vertex = std::string;
    using Weight = double;
    using NeighborMap = std::map<Vertex, Weight>;

private:
    bool directed_;
    bool weighted_;
    std::map<Vertex, NeighborMap> adjacency_;
    std::size_t edge_count_ = 0;

public:
    explicit Graph(bool directed = false, bool weighted = false)
        : directed_(directed), weighted_(weighted) {}

    bool directed() const { return directed_; }
    bool weighted() const { return weighted_; }

    std::size_t vertex_count() const {
        return adjacency_.size();
    }

    std::size_t edge_count() const {
        return edge_count_;
    }

    void add_vertex(const Vertex& vertex) {
        if (vertex.empty()) {
            throw std::invalid_argument("Vertex identifiers cannot be empty.");
        }

        adjacency_.try_emplace(vertex);
    }

    void require_vertex(const Vertex& vertex) const {
        if (adjacency_.find(vertex) == adjacency_.end()) {
            throw std::out_of_range("Unknown vertex: " + vertex);
        }
    }

    void add_edge(
        const Vertex& source,
        const Vertex& target,
        Weight weight = 1.0
    ) {
        if (!std::isfinite(weight)) {
            throw std::invalid_argument("Edge weight must be finite.");
        }

        add_vertex(source);
        add_vertex(target);

        auto& outgoing = adjacency_.at(source);
        const bool existed = outgoing.find(target) != outgoing.end();

        outgoing[target] = weight;

        if (!directed_ && source != target) {
            adjacency_.at(target)[source] = weight;
        }

        if (!existed) {
            ++edge_count_;
        }
    }

    bool remove_edge(const Vertex& source, const Vertex& target) {
        require_vertex(source);
        require_vertex(target);

        auto& outgoing = adjacency_.at(source);

        if (outgoing.erase(target) == 0) {
            return false;
        }

        if (!directed_ && source != target) {
            adjacency_.at(target).erase(source);
        }

        --edge_count_;
        return true;
    }

    bool has_edge(const Vertex& source, const Vertex& target) const {
        require_vertex(source);
        require_vertex(target);

        const auto& neighbors = adjacency_.at(source);
        return neighbors.find(target) != neighbors.end();
    }

    std::vector<Vertex> neighbors(const Vertex& vertex) const {
        require_vertex(vertex);

        std::vector<Vertex> result;

        for (const auto& [neighbor, weight] : adjacency_.at(vertex)) {
            (void)weight;
            result.push_back(neighbor);
        }

        return result;
    }

    std::size_t out_degree(const Vertex& vertex) const {
        require_vertex(vertex);
        return adjacency_.at(vertex).size();
    }

    std::size_t in_degree(const Vertex& vertex) const {
        require_vertex(vertex);

        if (!directed_) {
            throw std::logic_error(
                "Use degree() for undirected graphs."
            );
        }

        std::size_t result = 0;

        for (const auto& [source, neighbors] : adjacency_) {
            (void)source;

            if (neighbors.find(vertex) != neighbors.end()) {
                ++result;
            }
        }

        return result;
    }

    std::size_t degree(const Vertex& vertex) const {
        require_vertex(vertex);

        if (directed_) {
            throw std::logic_error(
                "Use in_degree() and out_degree() for directed graphs."
            );
        }

        std::size_t result = 0;

        for (const auto& [neighbor, weight] : adjacency_.at(vertex)) {
            (void)weight;
            result += neighbor == vertex ? 2 : 1;
        }

        return result;
    }

    std::vector<Vertex> breadth_first_search(const Vertex& start) const {
        require_vertex(start);

        std::set<Vertex> visited{start};
        std::queue<Vertex> frontier;
        std::vector<Vertex> order;

        frontier.push(start);

        while (!frontier.empty()) {
            Vertex current = frontier.front();
            frontier.pop();

            order.push_back(current);

            for (const auto& [neighbor, weight] : adjacency_.at(current)) {
                (void)weight;

                if (visited.insert(neighbor).second) {
                    frontier.push(neighbor);
                }
            }
        }

        return order;
    }

    std::vector<Vertex> shortest_unweighted_path(
        const Vertex& source,
        const Vertex& target
    ) const {
        require_vertex(source);
        require_vertex(target);

        std::map<Vertex, Vertex> parent;
        std::set<Vertex> visited{source};
        std::queue<Vertex> frontier;

        frontier.push(source);

        while (!frontier.empty()) {
            Vertex current = frontier.front();
            frontier.pop();

            if (current == target) {
                break;
            }

            for (const auto& [neighbor, weight] : adjacency_.at(current)) {
                (void)weight;

                if (visited.insert(neighbor).second) {
                    parent[neighbor] = current;
                    frontier.push(neighbor);
                }
            }
        }

        if (visited.find(target) == visited.end()) {
            return {};
        }

        std::vector<Vertex> path;
        Vertex current = target;
        path.push_back(current);

        while (current != source) {
            current = parent.at(current);
            path.push_back(current);
        }

        std::reverse(path.begin(), path.end());
        return path;
    }

    std::vector<std::vector<Weight>> adjacency_matrix(
        std::vector<Vertex>& vertices
    ) const {
        vertices.clear();

        for (const auto& [vertex, neighbors] : adjacency_) {
            (void)neighbors;
            vertices.push_back(vertex);
        }

        const std::size_t n = vertices.size();
        const Weight missing = std::numeric_limits<Weight>::infinity();

        std::vector<std::vector<Weight>> matrix(
            n, std::vector<Weight>(n, missing)
        );

        std::map<Vertex, std::size_t> index;

        for (std::size_t i = 0; i < n; ++i) {
            index[vertices[i]] = i;
        }

        for (const auto& [source, neighbors] : adjacency_) {
            for (const auto& [target, weight] : neighbors) {
                matrix[index.at(source)][index.at(target)] = weight;
            }
        }

        return matrix;
    }

    void print_adjacency_list() const {
        std::cout << (directed_ ? "Directed" : "Undirected")
                  << (weighted_ ? " weighted" : " unweighted")
                  << " graph\n";

        for (const auto& [vertex, neighbors] : adjacency_) {
            std::cout << "  " << vertex << ": ";

            for (const auto& [neighbor, weight] : neighbors) {
                std::cout << neighbor;

                if (weighted_) {
                    std::cout << "(" << weight << ")";
                }

                std::cout << " ";
            }

            std::cout << "\n";
        }

        std::cout << "Vertices: " << vertex_count()
                  << ", logical edges: " << edge_count() << "\n";
    }

    void print_matrix() const {
        std::vector<Vertex> vertices;
        const auto matrix = adjacency_matrix(vertices);

        std::cout << "\nAdjacency matrix; INF means no edge\n    ";

        for (const auto& vertex : vertices) {
            std::cout << std::setw(12) << vertex;
        }

        std::cout << "\n";

        for (std::size_t i = 0; i < vertices.size(); ++i) {
            std::cout << std::setw(4) << vertices[i];

            for (std::size_t j = 0; j < vertices.size(); ++j) {
                if (std::isinf(matrix[i][j])) {
                    std::cout << std::setw(12) << "INF";
                } else {
                    std::cout << std::setw(12) << matrix[i][j];
                }
            }

            std::cout << "\n";
        }
    }
};

void print_path(const std::vector<std::string>& path) {
    if (path.empty()) {
        std::cout << "No route exists\n";
        return;
    }

    for (std::size_t i = 0; i < path.size(); ++i) {
        if (i != 0) std::cout << " -> ";
        std::cout << path[i];
    }

    std::cout << "\n";
}

void campus_network_case_study() {
    std::cout << "=== Campus physical network ===\n";

    Graph campus(false, true);

    campus.add_vertex("Research lab");
    campus.add_edge("Internet gateway", "Core switch", 2.0);
    campus.add_edge("Core switch", "Server room", 1.0);
    campus.add_edge("Core switch", "Library", 3.0);
    campus.add_edge("Library", "Lecture hall", 2.0);
    campus.add_edge("Server room", "Research lab", 4.0);

    campus.print_adjacency_list();
    campus.print_matrix();

    std::cout << "\nMinimum-hop route from gateway to lab: ";
    print_path(
        campus.shortest_unweighted_path(
            "Internet gateway", "Research lab"
        )
    );

    std::cout << "Core switch degree: "
              << campus.degree("Core switch") << "\n";

    // BFS minimizes the number of edges, not the sum of edge weights.
    // Weights could represent latency, but weighted routing needs an
    // algorithm such as Dijkstra's algorithm with nonnegative costs.
}

void directed_dependency_case_study() {
    std::cout << "\n=== Directed service dependencies ===\n";

    Graph services(true, false);

    services.add_edge("Identity service", "Order API");
    services.add_edge("Order API", "Inventory service");
    services.add_edge("Order API", "Payment service");
    services.add_edge("Payment service", "Audit pipeline");

    services.print_adjacency_list();

    std::cout << "Order API outgoing dependencies: "
              << services.out_degree("Order API") << "\n";

    std::cout << "Audit pipeline incoming dependencies: "
              << services.in_degree("Audit pipeline") << "\n";

    std::cout << "Identity service reaches audit pipeline: ";

    const auto traversal = services.breadth_first_search("Identity service");
    const bool found = std::find(
        traversal.begin(), traversal.end(), "Audit pipeline"
    ) != traversal.end();

    std::cout << (found ? "yes" : "no") << "\n";
}

void validation_case_study() {
    std::cout << "\n=== Integrity and edge cases ===\n";

    Graph graph(false, false);
    graph.add_edge("A", "B");

    graph.add_edge("A", "B");
    if (graph.edge_count() != 1) {
        throw std::logic_error("Duplicate edge count is incorrect.");
    }

    graph.add_edge("Loop", "Loop");

    if (graph.degree("Loop") != 2) {
        throw std::logic_error("Undirected self-loop degree is incorrect.");
    }

    graph.remove_edge("A", "B");

    if (graph.edge_count() != 1) {
        throw std::logic_error("Edge removal failed.");
    }

    try {
        graph.out_degree("Unknown");
    } catch (const std::out_of_range& error) {
        std::cout << "Invalid vertex rejected: " << error.what() << "\n";
    }

    std::cout << "Validation checks passed.\n";
}

int main() {
    try {
        campus_network_case_study();
        directed_dependency_case_study();
        validation_case_study();
    } catch (const std::exception& error) {
        std::cerr << "Graph analysis failed: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
