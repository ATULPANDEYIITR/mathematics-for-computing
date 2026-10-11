import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Deque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/*
 * Enterprise graph model for service dependency analysis.
 *
 * Java 17 standard library only. The model separates domain validation,
 * graph representation, traversal, and reporting.
 */
public class GraphFundamentals {

    enum GraphKind {
        DIRECTED,
        UNDIRECTED
    }

    record Edge<V>(V source, V target, double weight) {
        Edge {
            Objects.requireNonNull(source, "Edge source is required.");
            Objects.requireNonNull(target, "Edge target is required.");

            if (!Double.isFinite(weight)) {
                throw new IllegalArgumentException(
                    "Edge weight must be finite."
                );
            }
        }
    }

    static final class Graph<V> {
        private final GraphKind kind;
        private final Map<V, LinkedHashMap<V, Double>> adjacency =
            new LinkedHashMap<>();
        private int edgeCount;

        Graph(GraphKind kind) {
            this.kind = Objects.requireNonNull(kind);
        }

        GraphKind kind() {
            return kind;
        }

        int vertexCount() {
            return adjacency.size();
        }

        int edgeCount() {
            return edgeCount;
        }

        void addVertex(V vertex) {
            Objects.requireNonNull(vertex, "Vertex cannot be null.");
            adjacency.computeIfAbsent(vertex, ignored -> new LinkedHashMap<>());
        }

        private void requireVertex(V vertex) {
            if (!adjacency.containsKey(vertex)) {
                throw new IllegalArgumentException(
                    "Unknown vertex: " + vertex
                );
            }
        }

        void addEdge(V source, V target, double weight) {
            Edge<V> edge = new Edge<>(source, target, weight);

            addVertex(edge.source());
            addVertex(edge.target());

            Map<V, Double> outgoing = adjacency.get(edge.source());
            boolean existed = outgoing.containsKey(edge.target());

            outgoing.put(edge.target(), edge.weight());

            if (kind == GraphKind.UNDIRECTED
                    && !edge.source().equals(edge.target())) {
                adjacency.get(edge.target()).put(edge.source(), edge.weight());
            }

            if (!existed) {
                edgeCount++;
            }
        }

        boolean removeEdge(V source, V target) {
            requireVertex(source);
            requireVertex(target);

            if (!adjacency.get(source).containsKey(target)) {
                return false;
            }

            adjacency.get(source).remove(target);

            if (kind == GraphKind.UNDIRECTED && !source.equals(target)) {
                adjacency.get(target).remove(source);
            }

            edgeCount--;
            return true;
        }

        boolean hasEdge(V source, V target) {
            requireVertex(source);
            requireVertex(target);
            return adjacency.get(source).containsKey(target);
        }

        List<V> vertices() {
            return List.copyOf(adjacency.keySet());
        }

        Map<V, Double> neighbors(V vertex) {
            requireVertex(vertex);
            return Collections.unmodifiableMap(
                new LinkedHashMap<>(adjacency.get(vertex))
            );
        }

        int outDegree(V vertex) {
            requireVertex(vertex);
            return adjacency.get(vertex).size();
        }

        int inDegree(V vertex) {
            requireVertex(vertex);

            if (kind != GraphKind.DIRECTED) {
                throw new IllegalStateException(
                    "In-degree requires a directed graph."
                );
            }

            int count = 0;

            for (Map<V, Double> outgoing : adjacency.values()) {
                if (outgoing.containsKey(vertex)) {
                    count++;
                }
            }

            return count;
        }

        int degree(V vertex) {
            requireVertex(vertex);

            if (kind != GraphKind.UNDIRECTED) {
                throw new IllegalStateException(
                    "Use inDegree() and outDegree() for directed graphs."
                );
            }

            int result = 0;

            for (V neighbor : adjacency.get(vertex).keySet()) {
                result += neighbor.equals(vertex) ? 2 : 1;
            }

            return result;
        }

        List<Edge<V>> edges() {
            List<Edge<V>> result = new ArrayList<>();
            Map<V, Integer> order = new HashMap<>();
            int position = 0;

            for (V vertex : adjacency.keySet()) {
                order.put(vertex, position++);
            }

            for (Map.Entry<V, LinkedHashMap<V, Double>> entry
                    : adjacency.entrySet()) {
                V source = entry.getKey();

                for (Map.Entry<V, Double> neighbor
                        : entry.getValue().entrySet()) {
                    V target = neighbor.getKey();

                    if (kind == GraphKind.DIRECTED
                            || order.get(source) <= order.get(target)) {
                        result.add(
                            new Edge<>(source, target, neighbor.getValue())
                        );
                    }
                }
            }

            return List.copyOf(result);
        }

        List<V> breadthFirstSearch(V start) {
            requireVertex(start);

            Set<V> visited = new LinkedHashSet<>();
            Deque<V> queue = new ArrayDeque<>();
            List<V> order = new ArrayList<>();

            visited.add(start);
            queue.addLast(start);

            while (!queue.isEmpty()) {
                V current = queue.removeFirst();
                order.add(current);

                for (V neighbor : adjacency.get(current).keySet()) {
                    if (visited.add(neighbor)) {
                        queue.addLast(neighbor);
                    }
                }
            }

            return List.copyOf(order);
        }

        List<V> shortestPath(V source, V target) {
            requireVertex(source);
            requireVertex(target);

            Map<V, V> parent = new HashMap<>();
            Set<V> visited = new HashSet<>();
            Deque<V> queue = new ArrayDeque<>();

            visited.add(source);
            queue.addLast(source);

            while (!queue.isEmpty()) {
                V current = queue.removeFirst();

                if (current.equals(target)) {
                    break;
                }

                for (V neighbor : adjacency.get(current).keySet()) {
                    if (visited.add(neighbor)) {
                        parent.put(neighbor, current);
                        queue.addLast(neighbor);
                    }
                }
            }

            if (!visited.contains(target)) {
                return List.of();
            }

            List<V> path = new ArrayList<>();
            V current = target;
            path.add(current);

            while (!current.equals(source)) {
                current = parent.get(current);
                path.add(current);
            }

            Collections.reverse(path);
            return List.copyOf(path);
        }

        List<List<V>> connectedComponents() {
            if (kind != GraphKind.UNDIRECTED) {
                throw new IllegalStateException(
                    "Connected components require an undirected graph."
                );
            }

            Set<V> unseen = new LinkedHashSet<>(adjacency.keySet());
            List<List<V>> components = new ArrayList<>();

            while (!unseen.isEmpty()) {
                V start = unseen.iterator().next();
                List<V> component = breadthFirstSearch(start);
                unseen.removeAll(component);
                components.add(component);
            }

            return List.copyOf(components);
        }

        void printAdjacencyList() {
            System.out.printf(
                "%s graph: %d vertices, %d edges%n",
                kind, vertexCount(), edgeCount
            );

            for (Map.Entry<V, LinkedHashMap<V, Double>> entry
                    : adjacency.entrySet()) {
                System.out.printf("  %s -> %s%n",
                    entry.getKey(), entry.getValue());
            }
        }
    }

    static final class ServiceRegistry {
        private final Graph<String> dependencies =
            new Graph<>(GraphKind.DIRECTED);

        void registerService(String name) {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException(
                    "Service name must not be blank."
                );
            }

            dependencies.addVertex(name);
        }

        void declareDependency(String dependent, String prerequisite) {
            // The edge dependent -> prerequisite records a dependency.
            dependencies.addEdge(dependent, prerequisite, 1.0);
        }

        List<String> dependencyChain(String service) {
            return dependencies.breadthFirstSearch(service);
        }

        void report() {
            dependencies.printAdjacencyList();

            for (String service : dependencies.vertices()) {
                System.out.printf(
                    "%s: direct dependencies=%d, dependents=%d%n",
                    service,
                    dependencies.outDegree(service),
                    dependencies.inDegree(service)
                );
            }
        }
    }

    private static void runAssertions() {
        Graph<String> graph = new Graph<>(GraphKind.UNDIRECTED);
        graph.addEdge("Gateway", "Switch", 1.0);
        graph.addEdge("Switch", "Server", 1.0);
        graph.addVertex("Offline workstation");

        if (graph.edgeCount() != 2 || graph.degree("Switch") != 2) {
            throw new AssertionError("Undirected graph invariant failed.");
        }

        if (!graph.shortestPath("Gateway", "Server")
                .equals(List.of("Gateway", "Switch", "Server"))) {
            throw new AssertionError("Shortest path calculation failed.");
        }

        if (graph.connectedComponents().size() != 2) {
            throw new AssertionError("Disconnected components were lost.");
        }

        Graph<String> directed = new Graph<>(GraphKind.DIRECTED);
        directed.addEdge("API", "Database", 1.0);

        if (directed.inDegree("Database") != 1
                || directed.outDegree("API") != 1
                || directed.hasEdge("Database", "API")) {
            throw new AssertionError("Directed edge semantics failed.");
        }

        try {
            graph.outDegree("Missing");
            throw new AssertionError("Unknown vertex should be rejected.");
        } catch (IllegalArgumentException expected) {
            System.out.println("Unknown-vertex validation passed.");
        }
    }

    public static void main(String[] args) {
        System.out.println("=== Enterprise service dependency model ===");

        ServiceRegistry registry = new ServiceRegistry();

        registry.registerService("Monitoring");
        registry.registerService("Audit storage");
        registry.declareDependency("Checkout API", "Identity service");
        registry.declareDependency("Checkout API", "Inventory service");
        registry.declareDependency("Inventory service", "Audit storage");
        registry.declareDependency("Identity service", "Monitoring");

        registry.report();

        System.out.println(
            "Checkout dependency traversal: "
                + registry.dependencyChain("Checkout API")
        );

        runAssertions();
        System.out.println("All graph tests passed.");
    }
}
