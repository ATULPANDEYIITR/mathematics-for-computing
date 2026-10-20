#include <algorithm>
#include <functional>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using Vertex = std::string;
using Edge = std::pair<Vertex, Vertex>;

class Graph {
private:
    std::set<Vertex> vertices_;
    std::map<Vertex, std::set<Vertex>> adjacency_;

    static Edge canonicalEdge(const Vertex& u, const Vertex& v) {
        if (u == v) {
            throw std::invalid_argument("Self-loops are not supported.");
        }
        return u < v ? Edge{u, v} : Edge{v, u};
    }

public:
    void addVertex(const Vertex& vertex) {
        vertices_.insert(vertex);
        adjacency_.try_emplace(vertex);
    }

    void addEdge(const Vertex& u, const Vertex& v) {
        if (u == v) {
            throw std::invalid_argument("Simple graphs cannot contain loops.");
        }

        addVertex(u);
        addVertex(v);
        adjacency_[u].insert(v);
        adjacency_[v].insert(u);
    }

    bool hasEdge(const Vertex& u, const Vertex& v) const {
        auto it = adjacency_.find(u);
        if (it == adjacency_.end()) {
            return false;
        }
        return it->second.count(v) != 0;
    }

    std::size_t degree(const Vertex& vertex) const {
        auto it = adjacency_.find(vertex);
        if (it == adjacency_.end()) {
            throw std::out_of_range("Unknown vertex.");
        }
        return it->second.size();
    }

    const std::set<Vertex>& vertices() const {
        return vertices_;
    }

    std::vector<Edge> edges() const {
        std::set<Edge> unique;

        for (const auto& [u, neighbors] : adjacency_) {
            for (const auto& v : neighbors) {
                unique.insert(canonicalEdge(u, v));
            }
        }

        return {unique.begin(), unique.end()};
    }

    Graph contractEdge(const Vertex& u, const Vertex& v) const {
        if (!hasEdge(u, v)) {
            throw std::invalid_argument("Cannot contract a missing edge.");
        }

        Graph result;

        const Vertex merged = "(" + u + "+" + v + ")";
        std::set<Vertex> neighbors;

        for (const auto& neighbor : adjacency_.at(u)) {
            if (neighbor != v) {
                neighbors.insert(neighbor);
            }
        }

        for (const auto& neighbor : adjacency_.at(v)) {
            if (neighbor != u) {
                neighbors.insert(neighbor);
            }
        }

        for (const auto& vertex : vertices_) {
            if (vertex != u && vertex != v) {
                result.addVertex(vertex);
            }
        }

        result.addVertex(merged);

        for (const auto& [a, b] : edges()) {
            if ((a == u && b == v) || (a == v && b == u)) {
                continue;
            }

            Vertex left = a;
            Vertex right = b;

            if (left == u || left == v) {
                left = merged;
            }

            if (right == u || right == v) {
                right = merged;
            }

            if (left != right) {
                result.addEdge(left, right);
            }
        }

        return result;
    }

    bool isConnected() const {
        if (vertices_.empty()) {
            return true;
        }

        std::set<Vertex> visited;
        std::vector<Vertex> stack{*vertices_.begin()};

        while (!stack.empty()) {
            Vertex current = stack.back();
            stack.pop_back();

            if (!visited.insert(current).second) {
                continue;
            }

            for (const auto& neighbor : adjacency_.at(current)) {
                if (!visited.count(neighbor)) {
                    stack.push_back(neighbor);
                }
            }
        }

        return visited.size() == vertices_.size();
    }
};

Graph completeGraph(int n) {
    if (n < 0) {
        throw std::invalid_argument("Graph size cannot be negative.");
    }

    Graph graph;

    for (int i = 0; i < n; ++i) {
        graph.addVertex(std::to_string(i));
    }

    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            graph.addEdge(std::to_string(i), std::to_string(j));
        }
    }

    return graph;
}

Graph completeBipartiteGraph(int left, int right) {
    if (left <= 0 || right <= 0) {
        throw std::invalid_argument("Bipartition sizes must be positive.");
    }

    Graph graph;

    for (int i = 0; i < left; ++i) {
        graph.addVertex("L" + std::to_string(i));
    }

    for (int j = 0; j < right; ++j) {
        graph.addVertex("R" + std::to_string(j));
    }

    for (int i = 0; i < left; ++i) {
        for (int j = 0; j < right; ++j) {
            graph.addEdge(
                "L" + std::to_string(i),
                "R" + std::to_string(j)
            );
        }
    }

    return graph;
}

std::vector<std::size_t> degreeSequence(const Graph& graph) {
    std::vector<std::size_t> sequence;

    for (const auto& vertex : graph.vertices()) {
        sequence.push_back(graph.degree(vertex));
    }

    std::sort(sequence.rbegin(), sequence.rend());
    return sequence;
}

bool isIsomorphic(const Graph& first, const Graph& second) {
    if (first.vertices().size() != second.vertices().size()) {
        return false;
    }

    if (first.edges().size() != second.edges().size()) {
        return false;
    }

    if (degreeSequence(first) != degreeSequence(second)) {
        return false;
    }

    std::map<std::size_t, std::vector<Vertex>> candidates;

    for (const auto& vertex : second.vertices()) {
        candidates[second.degree(vertex)].push_back(vertex);
    }

    std::vector<Vertex> source(first.vertices().begin(), first.vertices().end());

    std::sort(
        source.begin(),
        source.end(),
        [&first](const Vertex& a, const Vertex& b) {
            return first.degree(a) > first.degree(b);
        }
    );

    std::map<Vertex, Vertex> mapping;
    std::set<Vertex> used;

    std::function<bool(std::size_t)> search =
        [&](std::size_t index) -> bool {
            if (index == source.size()) {
                return true;
            }

            const Vertex& u = source[index];
            const auto& possible = candidates[first.degree(u)];

            for (const auto& candidate : possible) {
                if (used.count(candidate)) {
                    continue;
                }

                bool compatible = true;

                for (const auto& [mappedU, mappedV] : mapping) {
                    if (first.hasEdge(u, mappedU) !=
                        second.hasEdge(candidate, mappedV)) {
                        compatible = false;
                        break;
                    }
                }

                if (!compatible) {
                    continue;
                }

                mapping[u] = candidate;
                used.insert(candidate);

                if (search(index + 1)) {
                    return true;
                }

                used.erase(candidate);
                mapping.erase(u);
            }

            return false;
        };

    return search(0);
}

bool isBipartite(const Graph& graph) {
    std::map<Vertex, int> color;

    for (const auto& source : graph.vertices()) {
        if (color.count(source)) {
            continue;
        }

        color[source] = 0;
        std::vector<Vertex> queue{source};

        for (std::size_t index = 0; index < queue.size(); ++index) {
            const Vertex& current = queue[index];

            for (const auto& neighbor : graph.vertices()) {
                if (!graph.hasEdge(current, neighbor)) {
                    continue;
                }

                if (!color.count(neighbor)) {
                    color[neighbor] = 1 - color[current];
                    queue.push_back(neighbor);
                } else if (color[neighbor] == color[current]) {
                    return false;
                }
            }
        }
    }

    return true;
}

struct PlanarityResult {
    bool known;
    bool planar;
    std::string explanation;
};

PlanarityResult evaluatePlanarityBounds(const Graph& graph) {
    const long long n =
        static_cast<long long>(graph.vertices().size());

    const long long m =
        static_cast<long long>(graph.edges().size());

    if (n <= 4) {
        return {
            true,
            true,
            "Every simple graph with at most four vertices is planar."
        };
    }

    if (m > 3 * n - 6) {
        return {
            true,
            false,
            "The graph violates the simple planar bound m <= 3n - 6."
        };
    }

    if (isBipartite(graph) && m > 2 * n - 4) {
        return {
            true,
            false,
            "The bipartite graph violates m <= 2n - 4."
        };
    }

    return {
        false,
        false,
        "Necessary bounds hold; an exact planarity algorithm is required."
    };
}

struct RepositoryGraph {
    std::string repositoryName;
    Graph dependencyGraph;
};

class MinorAnalyzer {
public:
    static Graph contractFirstEdge(const Graph& graph) {
        const auto edges = graph.edges();

        if (edges.empty()) {
            throw std::invalid_argument(
                "A graph without edges has no contractible edge."
            );
        }

        return graph.contractEdge(edges.front().first, edges.front().second);
    }
};

class ExtremalAnalyzer {
public:
    static long long maximumSimpleEdges(long long n) {
        if (n < 0) {
            throw std::invalid_argument("n cannot be negative.");
        }

        return n * (n - 1) / 2;
    }

    static long long planarUpperBound(long long n) {
        if (n < 3) {
            return maximumSimpleEdges(n);
        }

        return 3 * n - 6;
    }

    static long long bipartiteUpperBound(long long n) {
        if (n < 3) {
            return maximumSimpleEdges(n);
        }

        return 2 * n - 4;
    }
};

void printGraphMetrics(const std::string& name, const Graph& graph) {
    const auto result = evaluatePlanarityBounds(graph);

    std::cout
        << name
        << ": vertices=" << graph.vertices().size()
        << ", edges=" << graph.edges().size()
        << ", connected=" << std::boolalpha << graph.isConnected()
        << ", bipartite=" << isBipartite(graph)
        << "\n"
        << "  Planarity result: ";

    if (result.known) {
        std::cout << std::boolalpha << result.planar;
    } else {
        std::cout << "undetermined by bounded test";
    }

    std::cout << "\n  Reason: " << result.explanation << "\n";
}

int main() {
    try {
        std::cout << "Advanced Graph Theory Case Study\n";
        std::cout << "================================\n\n";

        Graph cycle5;
        for (int i = 0; i < 5; ++i) {
            cycle5.addEdge(
                std::to_string(i),
                std::to_string((i + 1) % 5)
            );
        }

        Graph renamedCycle;
        for (const auto& vertex :
             {"A", "B", "C", "D", "E"}) {
            renamedCycle.addVertex(vertex);
        }

        renamedCycle.addEdge("A", "C");
        renamedCycle.addEdge("C", "E");
        renamedCycle.addEdge("E", "B");
        renamedCycle.addEdge("B", "D");
        renamedCycle.addEdge("D", "A");

        std::cout << "Graph isomorphism\n";
        std::cout << "-----------------\n";
        std::cout
            << "C5 isomorphic to renamed C5: "
            << std::boolalpha
            << isIsomorphic(cycle5, renamedCycle)
            << "\n\n";

        Graph k5 = completeGraph(5);
        Graph k33 = completeBipartiteGraph(3, 3);

        std::cout << "Planarity evidence\n";
        std::cout << "------------------\n";
        printGraphMetrics("C5", cycle5);
        printGraphMetrics("K5", k5);
        printGraphMetrics("K3,3", k33);

        std::cout << "\nGraph minors\n";
        std::cout << "------------\n";

        Graph k6 = completeGraph(6);
        Graph contracted = MinorAnalyzer::contractFirstEdge(k6);

        std::cout
            << "K6: "
            << k6.vertices().size()
            << " vertices, "
            << k6.edges().size()
            << " edges\n";

        std::cout
            << "After one contraction: "
            << contracted.vertices().size()
            << " vertices, "
            << contracted.edges().size()
            << " edges\n";

        std::cout << "\nExtremal graph bounds\n";
        std::cout << "--------------------\n";

        for (long long n = 3; n <= 10; ++n) {
            std::cout
                << "n=" << n
                << ": maximum simple edges="
                << ExtremalAnalyzer::maximumSimpleEdges(n)
                << ", planar upper bound="
                << ExtremalAnalyzer::planarUpperBound(n)
                << ", bipartite planar upper bound="
                << ExtremalAnalyzer::bipartiteUpperBound(n)
                << "\n";
        }

        std::cout << "\nRepository dependency interpretation\n";
        std::cout << "-----------------------------------\n";

        RepositoryGraph repository{
            "distributed-service-platform",
            completeBipartiteGraph(3, 3)
        };

        std::cout
            << "Repository dependency graph '"
            << repository.repositoryName
            << "' contains "
            << repository.dependencyGraph.vertices().size()
            << " services and "
            << repository.dependencyGraph.edges().size()
            << " dependency links.\n";

        std::cout << "\nImplementation constraints\n";
        std::cout << "---------------------------\n";
        std::cout
            << "* Isomorphism is exact but exponential in the worst case.\n"
            << "* Minor enumeration is combinatorial because contractions create many states.\n"
            << "* Euler inequalities provide fast rejection certificates, not a complete planarity test.\n"
            << "* Adjacency maps provide logarithmic ordered-set lookup in this implementation.\n"
            << "* Production systems should use a proven linear-time planarity implementation for large graphs.\n"
            << "* Input validation prevents self-loops and invalid contraction requests.\n";

        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }
}
