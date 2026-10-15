#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <map>
#include <optional>
#include <queue>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

/*
 * Case study: resilience analysis for a regional communications network.
 *
 * Undirected links connect physical sites. A bridge is a single link whose
 * loss increases the number of connected components. An articulation point
 * is a site whose removal increases that number.
 *
 * A separate directed graph models service dependencies. Strongly connected
 * components identify mutually reachable groups of services.
 *
 * Compile: g++ -std=c++17 -O2 -Wall -Wextra -pedantic connectivity.cpp -o connectivity
 */

class UndirectedNetwork {
public:
    using Vertex = std::string;

    struct Edge {
        int id;
        Vertex left;
        Vertex right;
    };

    explicit UndirectedNetwork(std::vector<Vertex> vertices) {
        for (const auto& vertex : vertices) {
            if (vertex.empty()) {
                throw std::invalid_argument("Vertex names cannot be empty.");
            }
            adjacency_.try_emplace(vertex);
        }
    }

    int add_edge(const Vertex& left, const Vertex& right) {
        if (adjacency_.find(left) == adjacency_.end() ||
            adjacency_.find(right) == adjacency_.end()) {
            throw std::invalid_argument("Both endpoints must be registered.");
        }

        const int id = static_cast<int>(edges_.size());
        edges_.push_back({id, left, right});
        adjacency_[left].push_back({right, id});
        adjacency_[right].push_back({left, id});
        return id;
    }

    std::size_t vertex_count() const {
        return adjacency_.size();
    }

    std::size_t edge_count() const {
        return edges_.size();
    }

    const std::vector<Edge>& edges() const {
        return edges_;
    }

    std::vector<std::set<Vertex>> components(
        const std::optional<Vertex>& excluded_vertex = std::nullopt,
        const std::optional<int>& excluded_edge = std::nullopt) const {
        if (excluded_vertex &&
            adjacency_.find(*excluded_vertex) == adjacency_.end()) {
            throw std::invalid_argument("Unknown vertex.");
        }
        if (excluded_edge &&
            (*excluded_edge < 0 ||
             static_cast<std::size_t>(*excluded_edge) >= edges_.size())) {
            throw std::invalid_argument("Unknown edge ID.");
        }

        std::unordered_set<Vertex> visited;
        std::vector<std::set<Vertex>> result;

        for (const auto& [start, ignored] : adjacency_) {
            (void)ignored;
            if ((excluded_vertex && start == *excluded_vertex) ||
                visited.count(start)) {
                continue;
            }

            std::queue<Vertex> pending;
            std::set<Vertex> component;
            pending.push(start);
            visited.insert(start);

            while (!pending.empty()) {
                Vertex current = pending.front();
                pending.pop();
                component.insert(current);

                for (const auto& [neighbor, edge_id] : adjacency_.at(current)) {
                    if ((excluded_edge && edge_id == *excluded_edge) ||
                        (excluded_vertex && neighbor == *excluded_vertex) ||
                        visited.count(neighbor)) {
                        continue;
                    }
                    visited.insert(neighbor);
                    pending.push(neighbor);
                }
            }

            result.push_back(std::move(component));
        }

        return result;
    }

    struct Analysis {
        std::vector<int> bridge_ids;
        std::set<Vertex> articulation_points;
    };

    Analysis analyze() const {
        std::unordered_map<Vertex, int> discovery;
        std::unordered_map<Vertex, int> low;
        std::unordered_map<Vertex, Vertex> parent;
        std::unordered_map<Vertex, int> parent_edge;
        std::unordered_map<Vertex, int> child_count;

        Analysis result;
        int clock = 0;

        // Iterative DFS avoids call-stack exhaustion on long infrastructure paths.
        struct Frame {
            Vertex vertex;
            std::size_t next_neighbor;
        };

        for (const auto& [root, ignored] : adjacency_) {
            (void)ignored;
            if (discovery.count(root)) {
                continue;
            }

            parent[root] = "";
            parent_edge[root] = -1;
            child_count[root] = 0;
            discovery[root] = low[root] = clock++;

            std::vector<Frame> stack{{root, 0}};

            while (!stack.empty()) {
                Frame& frame = stack.back();
                const Vertex vertex = frame.vertex;
                const auto& neighbors = adjacency_.at(vertex);

                if (frame.next_neighbor < neighbors.size()) {
                    const auto [neighbor, edge_id] =
                        neighbors[frame.next_neighbor++];

                    if (edge_id == parent_edge[vertex]) {
                        continue;
                    }

                    if (!discovery.count(neighbor)) {
                        parent[neighbor] = vertex;
                        parent_edge[neighbor] = edge_id;
                        child_count[vertex]++;
                        child_count[neighbor] = 0;
                        discovery[neighbor] = low[neighbor] = clock++;
                        stack.push_back({neighbor, 0});
                    } else {
                        low[vertex] =
                            std::min(low[vertex], discovery[neighbor]);
                    }
                } else {
                    stack.pop_back();

                    if (parent_edge[vertex] == -1) {
                        if (child_count[vertex] > 1) {
                            result.articulation_points.insert(vertex);
                        }
                        continue;
                    }

                    const Vertex ancestor = parent.at(vertex);
                    low[ancestor] = std::min(low[ancestor], low[vertex]);

                    if (low[vertex] > discovery[ancestor]) {
                        result.bridge_ids.push_back(parent_edge[vertex]);
                    }

                    if (parent_edge[ancestor] != -1 &&
                        low[vertex] >= discovery[ancestor]) {
                        result.articulation_points.insert(ancestor);
                    }
                }
            }
        }

        std::sort(result.bridge_ids.begin(), result.bridge_ids.end());
        return result;
    }

private:
    std::map<Vertex, std::vector<std::pair<Vertex, int>>> adjacency_;
    std::vector<Edge> edges_;
};

class DirectedDependencyGraph {
public:
    using Vertex = std::string;

    void add_edge(const Vertex& source, const Vertex& target) {
        if (source.empty() || target.empty()) {
            throw std::invalid_argument("Service names cannot be empty.");
        }
        adjacency_.try_emplace(source);
        adjacency_.try_emplace(target);
        adjacency_[source].push_back(target);
    }

    std::vector<std::set<Vertex>> strongly_connected_components() const {
        std::unordered_map<Vertex, int> index;
        std::unordered_map<Vertex, int> low;
        std::vector<Vertex> active;
        std::unordered_set<Vertex> on_stack;
        std::vector<std::set<Vertex>> components;
        int clock = 0;

        struct Frame {
            Vertex vertex;
            std::size_t next_neighbor;
        };

        for (const auto& [root, ignored] : adjacency_) {
            (void)ignored;
            if (index.count(root)) {
                continue;
            }

            index[root] = low[root] = clock++;
            active.push_back(root);
            on_stack.insert(root);
            std::vector<Frame> frames{{root, 0}};

            while (!frames.empty()) {
                Frame& frame = frames.back();
                const Vertex vertex = frame.vertex;
                const auto& neighbors = adjacency_.at(vertex);

                if (frame.next_neighbor < neighbors.size()) {
                    const Vertex neighbor = neighbors[frame.next_neighbor++];

                    if (!index.count(neighbor)) {
                        index[neighbor] = low[neighbor] = clock++;
                        active.push_back(neighbor);
                        on_stack.insert(neighbor);
                        frames.push_back({neighbor, 0});
                    } else if (on_stack.count(neighbor)) {
                        low[vertex] = std::min(low[vertex], index[neighbor]);
                    }
                } else {
                    frames.pop_back();

                    if (!frames.empty()) {
                        const Vertex ancestor = frames.back().vertex;
                        low[ancestor] =
                            std::min(low[ancestor], low[vertex]);
                    }

                    if (low[vertex] == index[vertex]) {
                        std::set<Vertex> component;

                        while (true) {
                            Vertex member = active.back();
                            active.pop_back();
                            on_stack.erase(member);
                            component.insert(member);

                            if (member == vertex) {
                                break;
                            }
                        }

                        components.push_back(std::move(component));
                    }
                }
            }
        }

        return components;
    }

private:
    std::map<Vertex, std::vector<Vertex>> adjacency_;
};

static void run_infrastructure_case_study() {
    std::cout << "=== Regional communications network ===\n";

    UndirectedNetwork network({
        "central-office",
        "relay-north",
        "relay-east",
        "relay-west",
        "hospital",
        "data-center",
        "remote-clinic"
    });

    network.add_edge("central-office", "relay-north");
    network.add_edge("relay-north", "relay-east");
    network.add_edge("relay-east", "relay-west");
    network.add_edge("relay-west", "relay-east");
    network.add_edge("relay-west", "hospital");
    network.add_edge("hospital", "data-center");
    network.add_edge("data-center", "hospital");

    const auto analysis = network.analyze();

    std::cout << "Sites: " << network.vertex_count()
              << ", physical links: " << network.edge_count() << '\n';

    std::cout << "Bridges:\n";
    for (int edge_id : analysis.bridge_ids) {
        const auto& edge = network.edges().at(static_cast<std::size_t>(edge_id));
        std::cout << "  " << edge.left << " -- " << edge.right
                  << " (edge " << edge.id << ")\n";
    }

    std::cout << "Articulation points:\n";
    for (const auto& vertex : analysis.articulation_points) {
        std::cout << "  " << vertex << '\n';
    }

    std::cout << "Connected components after relay-north failure: "
              << network.components("relay-north").size() << '\n';

    std::cout << "Components after hospital-data-center link failure: "
              << network.components(std::nullopt, 6).size() << '\n';

    // Validate the bridge theorem against explicit edge deletion on this small graph.
    const auto original_component_count = network.components().size();
    std::set<int> expected_bridges;

    for (std::size_t id = 0; id < network.edge_count(); ++id) {
        if (network.components(std::nullopt, static_cast<int>(id)).size() >
            original_component_count) {
            expected_bridges.insert(static_cast<int>(id));
        }
    }

    assert(expected_bridges ==
           std::set<int>(analysis.bridge_ids.begin(), analysis.bridge_ids.end()));
}

static void run_service_dependency_case() {
    std::cout << "\n=== Directed service dependencies ===\n";

    DirectedDependencyGraph services;
    services.add_edge("gateway", "identity");
    services.add_edge("identity", "token-store");
    services.add_edge("token-store", "identity");
    services.add_edge("gateway", "message-bus");
    services.add_edge("message-bus", "worker");
    services.add_edge("worker", "message-bus");
    services.add_edge("worker", "warehouse");

    const auto components = services.strongly_connected_components();

    for (std::size_t index = 0; index < components.size(); ++index) {
        std::cout << "SCC " << index << ':';
        for (const auto& service : components[index]) {
            std::cout << ' ' << service;
        }
        std::cout << '\n';
    }
}

int main() {
    try {
        run_infrastructure_case_study();
        run_service_dependency_case();
    } catch (const std::exception& error) {
        std::cerr << "Analysis failed: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
