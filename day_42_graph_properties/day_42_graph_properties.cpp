#include <algorithm>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using Vertex = std::string;

class GovernanceNetwork {
private:
    // Ordered containers make reports deterministic across executions.
    std::map<Vertex, std::set<Vertex>> adjacency;
    bool directed;

    void requireVertex(const Vertex& vertex) const {
        if (adjacency.find(vertex) == adjacency.end()) {
            throw std::invalid_argument("Unknown vertex: " + vertex);
        }
    }

public:
    explicit GovernanceNetwork(bool isDirected = false)
        : directed(isDirected) {}

    void addVertex(const Vertex& vertex) {
        if (vertex.empty()) {
            throw std::invalid_argument("Vertex names cannot be empty.");
        }
        adjacency.try_emplace(vertex);
    }

    void addEdge(const Vertex& source, const Vertex& target) {
        addVertex(source);
        addVertex(target);
        adjacency[source].insert(target);
        if (!directed) {
            adjacency[target].insert(source);
        }
    }

    const std::map<Vertex, std::set<Vertex>>& vertices() const {
        return adjacency;
    }

    std::size_t outDegree(const Vertex& vertex) const {
        requireVertex(vertex);
        return adjacency.at(vertex).size();
    }

    std::size_t inDegree(const Vertex& vertex) const {
        requireVertex(vertex);
        std::size_t degree = 0;
        for (const auto& [source, neighbors] : adjacency) {
            if (neighbors.count(vertex) != 0) {
                ++degree;
            }
        }
        return degree;
    }

    std::size_t degree(const Vertex& vertex) const {
        requireVertex(vertex);
        if (directed) {
            throw std::logic_error("Use inDegree and outDegree for directed graphs.");
        }

        std::size_t result = adjacency.at(vertex).size();
        // An undirected self-loop contributes two to the degree but occupies
        // only one adjacency-set entry.
        if (adjacency.at(vertex).count(vertex) != 0) {
            ++result;
        }
        return result;
    }

    std::vector<Vertex> breadthFirstSearch(const Vertex& start) const {
        requireVertex(start);
        std::queue<Vertex> frontier;
        std::set<Vertex> visited;
        std::vector<Vertex> order;

        visited.insert(start);
        frontier.push(start);

        while (!frontier.empty()) {
            Vertex current = frontier.front();
            frontier.pop();
            order.push_back(current);

            for (const auto& neighbor : adjacency.at(current)) {
                if (visited.insert(neighbor).second) {
                    frontier.push(neighbor);
                }
            }
        }
        return order;
    }

    std::vector<Vertex> shortestPath(
        const Vertex& source,
        const Vertex& target
    ) const {
        requireVertex(source);
        requireVertex(target);

        std::queue<Vertex> frontier;
        std::map<Vertex, Vertex> predecessor;
        std::set<Vertex> visited;

        frontier.push(source);
        visited.insert(source);

        while (!frontier.empty()) {
            const Vertex current = frontier.front();
            frontier.pop();

            if (current == target) {
                std::vector<Vertex> path;
                Vertex cursor = target;

                while (true) {
                    path.push_back(cursor);
                    if (cursor == source) break;
                    cursor = predecessor.at(cursor);
                }
                std::reverse(path.begin(), path.end());
                return path;
            }

            for (const auto& neighbor : adjacency.at(current)) {
                if (visited.insert(neighbor).second) {
                    predecessor[neighbor] = current;
                    frontier.push(neighbor);
                }
            }
        }

        return {};
    }

    std::vector<std::set<Vertex>> connectedComponents() const {
        // For directed graphs this deliberately reports weak components.
        std::map<Vertex, std::set<Vertex>> undirected;

        for (const auto& [vertex, neighbors] : adjacency) {
            undirected[vertex];
            for (const auto& neighbor : neighbors) {
                undirected[vertex].insert(neighbor);
                undirected[neighbor].insert(vertex);
            }
        }

        std::set<Vertex> unseen;
        for (const auto& [vertex, neighbors] : undirected) {
            unseen.insert(vertex);
        }

        std::vector<std::set<Vertex>> components;
        while (!unseen.empty()) {
            const Vertex start = *unseen.begin();
            std::queue<Vertex> frontier;
            std::set<Vertex> component;

            unseen.erase(start);
            frontier.push(start);

            while (!frontier.empty()) {
                Vertex current = frontier.front();
                frontier.pop();
                component.insert(current);

                for (const auto& neighbor : undirected.at(current)) {
                    if (unseen.erase(neighbor) != 0) {
                        frontier.push(neighbor);
                    }
                }
            }
            components.push_back(std::move(component));
        }
        return components;
    }

    bool isConnected() const {
        return !adjacency.empty() && connectedComponents().size() == 1;
    }

    bool hasUndirectedCycle() const {
        if (directed) {
            throw std::logic_error("Undirected cycle detection requires an undirected graph.");
        }

        std::set<Vertex> visited;
        for (const auto& [start, neighbors] : adjacency) {
            if (visited.count(start) != 0) continue;

            std::vector<std::pair<Vertex, Vertex>> stack;
            stack.emplace_back(start, "");
            std::map<Vertex, Vertex> parent;

            while (!stack.empty()) {
                auto [current, ignoredParent] = stack.back();
                stack.pop_back();

                if (!visited.insert(current).second) continue;

                for (const auto& neighbor : adjacency.at(current)) {
                    if (neighbor == current) return true;
                    if (visited.count(neighbor) == 0) {
                        parent[neighbor] = current;
                        stack.emplace_back(neighbor, current);
                    } else if (
                        parent.count(current) != 0 &&
                        neighbor != parent.at(current)
                    ) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    bool hasDirectedCycle() const {
        if (!directed) {
            throw std::logic_error("Directed cycle detection requires a directed graph.");
        }

        // WHITE vertices have not been visited, GRAY vertices are on the
        // active recursion stack, and BLACK vertices are fully processed.
        enum Color { WHITE, GRAY, BLACK };
        std::map<Vertex, Color> color;
        for (const auto& [vertex, neighbors] : adjacency) {
            color[vertex] = WHITE;
        }

        std::function<bool(const Vertex&)> visit = [&](const Vertex& vertex) {
            color[vertex] = GRAY;

            for (const auto& neighbor : adjacency.at(vertex)) {
                if (color[neighbor] == GRAY) return true;
                if (color[neighbor] == WHITE && visit(neighbor)) return true;
            }

            color[vertex] = BLACK;
            return false;
        };

        for (const auto& [vertex, neighbors] : adjacency) {
            if (color[vertex] == WHITE && visit(vertex)) return true;
        }
        return false;
    }

    void printDegrees() const {
        for (const auto& [vertex, neighbors] : adjacency) {
            std::cout << vertex << ": ";
            if (directed) {
                std::cout << "in=" << inDegree(vertex)
                          << ", out=" << outDegree(vertex);
            } else {
                std::cout << "degree=" << degree(vertex);
            }
            std::cout << '\n';
        }
    }
};

void printPath(const std::vector<Vertex>& path) {
    if (path.empty()) {
        std::cout << "unreachable";
        return;
    }

    for (std::size_t index = 0; index < path.size(); ++index) {
        if (index != 0) std::cout << " -> ";
        std::cout << path[index];
    }
}

void runCampusCaseStudy() {
    std::cout << "=== Campus connectivity analysis ===\n";

    GovernanceNetwork campus;
    campus.addEdge("North Gate", "Library");
    campus.addEdge("Library", "Laboratory");
    campus.addEdge("Library", "Cafeteria");
    campus.addEdge("Cafeteria", "Hostel");
    campus.addEdge("Hostel", "Sports Center");
    campus.addVertex("Remote Annex");

    campus.printDegrees();

    std::cout << "Connected: "
              << (campus.isConnected() ? "yes" : "no") << '\n';

    const auto components = campus.connectedComponents();
    std::cout << "Component count: " << components.size() << '\n';
    for (const auto& component : components) {
        std::cout << "Component: ";
        for (const auto& vertex : component) {
            std::cout << vertex << ' ';
        }
        std::cout << '\n';
    }

    std::cout << "Route from North Gate to Sports Center: ";
    printPath(campus.shortestPath("North Gate", "Sports Center"));
    std::cout << '\n';

    std::cout << "Route to Remote Annex: ";
    printPath(campus.shortestPath("Library", "Remote Annex"));
    std::cout << '\n';

    campus.addEdge("Sports Center", "North Gate");
    std::cout << "Cycle after adding a perimeter road: "
              << (campus.hasUndirectedCycle() ? "yes" : "no") << '\n';
}

void runDirectedCaseStudy() {
    std::cout << "\n=== Service dependency analysis ===\n";

    GovernanceNetwork services(true);
    services.addEdge("identity-service", "api-gateway");
    services.addEdge("api-gateway", "order-service");
    services.addEdge("order-service", "inventory-service");
    services.addEdge("inventory-service", "database");

    services.printDegrees();

    std::cout << "Deployment dependency path: ";
    printPath(services.shortestPath("identity-service", "database"));
    std::cout << '\n';

    std::cout << "Directed cycle: "
              << (services.hasDirectedCycle() ? "yes" : "no") << '\n';

    services.addEdge("database", "identity-service");
    std::cout << "Cycle after adding a reverse dependency: "
              << (services.hasDirectedCycle() ? "yes" : "no") << '\n';
}

void runValidationChecks() {
    std::cout << "\n=== Validation checks ===\n";

    GovernanceNetwork graph;
    graph.addEdge("A", "B");
    graph.addEdge("B", "C");

    if (graph.degree("B") != 2) {
        throw std::runtime_error("Degree invariant failed.");
    }
    if (graph.hasUndirectedCycle()) {
        throw std::runtime_error("A path graph must be acyclic.");
    }
    if (graph.shortestPath("A", "C").size() != 3) {
        throw std::runtime_error("Shortest path calculation failed.");
    }

    try {
        graph.degree("unknown");
        throw std::runtime_error("Unknown vertex was not rejected.");
    } catch (const std::invalid_argument&) {
        std::cout << "Unknown vertex rejected correctly.\n";
    }

    GovernanceNetwork empty;
    std::cout << "Empty graph connected: "
              << (empty.isConnected() ? "yes" : "no") << '\n';

    std::cout << "All C++ graph checks passed.\n";
}

int main() {
    try {
        runCampusCaseStudy();
        runDirectedCaseStudy();
        runValidationChecks();
    } catch (const std::exception& error) {
        std::cerr << "Graph analysis failed: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
