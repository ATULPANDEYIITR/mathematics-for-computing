import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Deque;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;

/**
 * Graph properties in an enterprise infrastructure dependency model.
 *
 * Compile: javac GraphProperties.java
 * Run:     java GraphProperties
 */
public class GraphProperties {

    enum ConnectivityMode {
        UNDIRECTED,
        DIRECTED
    }

    record Edge(String source, String target) {
        Edge {
            if (source == null || source.isBlank()
                    || target == null || target.isBlank()) {
                throw new IllegalArgumentException(
                    "Edge endpoints must be nonempty vertex names."
                );
            }
        }
    }

    record GraphReport(
        int vertexCount,
        int edgeCount,
        int componentCount,
        boolean connected,
        boolean containsCycle,
        Map<String, Integer> degreeByVertex
    ) {}

    static final class Graph {
        private final ConnectivityMode mode;
        private final Map<String, Set<String>> adjacency = new TreeMap<>();

        Graph(ConnectivityMode mode) {
            this.mode = Objects.requireNonNull(mode);
        }

        ConnectivityMode mode() {
            return mode;
        }

        void addVertex(String vertex) {
            validateVertex(vertex);
            adjacency.computeIfAbsent(vertex, ignored -> new TreeSet<>());
        }

        void addEdge(String source, String target) {
            validateVertex(source);
            validateVertex(target);
            addVertex(source);
            addVertex(target);

            adjacency.get(source).add(target);
            if (mode == ConnectivityMode.UNDIRECTED) {
                adjacency.get(target).add(source);
            }
        }

        private void validateVertex(String vertex) {
            if (vertex == null || vertex.isBlank()) {
                throw new IllegalArgumentException(
                    "Vertex names must not be null or blank."
                );
            }
        }

        private void requireVertex(String vertex) {
            if (!adjacency.containsKey(vertex)) {
                throw new IllegalArgumentException(
                    "Unknown vertex: " + vertex
                );
            }
        }

        Set<String> vertices() {
            return Collections.unmodifiableSet(adjacency.keySet());
        }

        Set<String> neighbors(String vertex) {
            requireVertex(vertex);
            return Collections.unmodifiableSet(adjacency.get(vertex));
        }

        List<Edge> edges() {
            List<Edge> result = new ArrayList<>();
            for (var entry : adjacency.entrySet()) {
                for (String target : entry.getValue()) {
                    if (mode == ConnectivityMode.DIRECTED
                            || entry.getKey().compareTo(target) <= 0) {
                        result.add(new Edge(entry.getKey(), target));
                    }
                }
            }
            return List.copyOf(result);
        }

        int outDegree(String vertex) {
            requireVertex(vertex);
            return adjacency.get(vertex).size();
        }

        int inDegree(String vertex) {
            requireVertex(vertex);
            int result = 0;
            for (Set<String> targets : adjacency.values()) {
                if (targets.contains(vertex)) {
                    result++;
                }
            }
            return result;
        }

        int degree(String vertex) {
            requireVertex(vertex);
            if (mode != ConnectivityMode.UNDIRECTED) {
                throw new IllegalStateException(
                    "Use inDegree() and outDegree() for directed graphs."
                );
            }

            int result = adjacency.get(vertex).size();
            // A loop is stored once in the set but contributes two incidences.
            if (adjacency.get(vertex).contains(vertex)) {
                result++;
            }
            return result;
        }

        List<String> breadthFirstSearch(String start) {
            requireVertex(start);
            Deque<String> queue = new ArrayDeque<>();
            Set<String> visited = new LinkedHashSet<>();

            visited.add(start);
            queue.addLast(start);

            while (!queue.isEmpty()) {
                String current = queue.removeFirst();
                for (String neighbor : adjacency.get(current)) {
                    if (visited.add(neighbor)) {
                        queue.addLast(neighbor);
                    }
                }
            }
            return List.copyOf(visited);
        }

        List<String> shortestPath(String source, String target) {
            requireVertex(source);
            requireVertex(target);

            Deque<String> queue = new ArrayDeque<>();
            Map<String, String> predecessor = new HashMap<>();
            Set<String> visited = new HashSet<>();

            queue.addLast(source);
            visited.add(source);

            while (!queue.isEmpty()) {
                String current = queue.removeFirst();

                if (current.equals(target)) {
                    List<String> path = new ArrayList<>();
                    String cursor = target;

                    while (cursor != null) {
                        path.add(cursor);
                        cursor = predecessor.get(cursor);
                    }
                    Collections.reverse(path);
                    return List.copyOf(path);
                }

                for (String neighbor : adjacency.get(current)) {
                    if (visited.add(neighbor)) {
                        predecessor.put(neighbor, current);
                        queue.addLast(neighbor);
                    }
                }
            }
            return List.of();
        }

        List<Set<String>> connectedComponents() {
            // For directed graphs, components mean weak connectivity.
            Map<String, Set<String>> undirected = new TreeMap<>();
            for (String vertex : adjacency.keySet()) {
                undirected.put(vertex, new TreeSet<>());
            }

            for (Edge edge : edges()) {
                undirected.get(edge.source()).add(edge.target());
                undirected.get(edge.target()).add(edge.source());
            }

            Set<String> unseen = new TreeSet<>(adjacency.keySet());
            List<Set<String>> components = new ArrayList<>();

            while (!unseen.isEmpty()) {
                String start = unseen.iterator().next();
                Set<String> component = new TreeSet<>();
                Deque<String> queue = new ArrayDeque<>();

                unseen.remove(start);
                queue.addLast(start);

                while (!queue.isEmpty()) {
                    String current = queue.removeFirst();
                    component.add(current);

                    for (String neighbor : undirected.get(current)) {
                        if (unseen.remove(neighbor)) {
                            queue.addLast(neighbor);
                        }
                    }
                }
                components.add(Collections.unmodifiableSet(component));
            }
            return List.copyOf(components);
        }

        boolean isConnected() {
            return !adjacency.isEmpty() && connectedComponents().size() == 1;
        }

        boolean hasCycle() {
            if (mode == ConnectivityMode.DIRECTED) {
                return hasDirectedCycle();
            }

            Set<String> visited = new HashSet<>();

            for (String start : adjacency.keySet()) {
                if (visited.contains(start)) continue;

                Deque<String> stack = new ArrayDeque<>();
                Map<String, String> parent = new HashMap<>();
                stack.push(start);
                parent.put(start, null);

                while (!stack.isEmpty()) {
                    String current = stack.pop();
                    if (!visited.add(current)) continue;

                    for (String neighbor : adjacency.get(current)) {
                        if (neighbor.equals(current)) return true;
                        if (!visited.contains(neighbor)) {
                            parent.put(neighbor, current);
                            stack.push(neighbor);
                        } else if (!Objects.equals(parent.get(current), neighbor)) {
                            return true;
                        }
                    }
                }
            }
            return false;
        }

        private boolean hasDirectedCycle() {
            // 0 = unvisited, 1 = active DFS path, 2 = complete.
            Map<String, Integer> state = new HashMap<>();
            for (String vertex : adjacency.keySet()) {
                state.put(vertex, 0);
            }

            for (String vertex : adjacency.keySet()) {
                if (state.get(vertex) == 0 && visitDirected(vertex, state)) {
                    return true;
                }
            }
            return false;
        }

        private boolean visitDirected(
            String vertex,
            Map<String, Integer> state
        ) {
            state.put(vertex, 1);

            for (String neighbor : adjacency.get(vertex)) {
                if (state.get(neighbor) == 1) return true;
                if (state.get(neighbor) == 0
                        && visitDirected(neighbor, state)) {
                    return true;
                }
            }

            state.put(vertex, 2);
            return false;
        }

        GraphReport report() {
            Map<String, Integer> degrees = new TreeMap<>();

            for (String vertex : adjacency.keySet()) {
                int value = mode == ConnectivityMode.UNDIRECTED
                    ? degree(vertex)
                    : inDegree(vertex) + outDegree(vertex);
                degrees.put(vertex, value);
            }

            int components = connectedComponents().size();
            return new GraphReport(
                adjacency.size(),
                edges().size(),
                components,
                !adjacency.isEmpty() && components == 1,
                hasCycle(),
                Collections.unmodifiableMap(degrees)
            );
        }
    }

    interface GraphPolicy {
        boolean evaluate(Graph graph);
        String description();
    }

    static final class RequireConnected implements GraphPolicy {
        @Override
        public boolean evaluate(Graph graph) {
            return graph.isConnected();
        }

        @Override
        public String description() {
            return "Every infrastructure node must be reachable.";
        }
    }

    static final class RequireAcyclic implements GraphPolicy {
        @Override
        public boolean evaluate(Graph graph) {
            return !graph.hasCycle();
        }

        @Override
        public String description() {
            return "Dependency graphs must not contain directed cycles.";
        }
    }

    static void runEnterpriseScenario() {
        Graph network = new Graph(ConnectivityMode.UNDIRECTED);
        network.addEdge("edge-router", "api-gateway");
        network.addEdge("api-gateway", "identity-service");
        network.addEdge("api-gateway", "order-service");
        network.addEdge("order-service", "inventory-service");
        network.addEdge("inventory-service", "database");
        network.addVertex("disaster-recovery-site");

        System.out.println("Infrastructure graph report:");
        System.out.println(network.report());
        System.out.println("Route to database: "
            + network.shortestPath("edge-router", "database"));
        System.out.println("Connected components: "
            + network.connectedComponents());

        List<GraphPolicy> policies = List.of(new RequireConnected());
        for (GraphPolicy policy : policies) {
            System.out.println(
                policy.description() + " Result: " + policy.evaluate(network)
            );
        }

        network.addEdge("database", "edge-router");
        System.out.println("Cycle after redundant connection: "
            + network.hasCycle());

        Graph dependencies = new Graph(ConnectivityMode.DIRECTED);
        dependencies.addEdge("compile", "test");
        dependencies.addEdge("test", "package");
        dependencies.addEdge("package", "deploy");

        GraphPolicy acyclic = new RequireAcyclic();
        System.out.println("Deployment dependency report: "
            + dependencies.report());
        System.out.println(
            acyclic.description() + " Result: "
                + acyclic.evaluate(dependencies)
        );

        dependencies.addEdge("deploy", "compile");
        System.out.println("Cycle after invalid dependency: "
            + dependencies.hasCycle());
    }

    static void runInvariantChecks() {
        Graph path = new Graph(ConnectivityMode.UNDIRECTED);
        path.addEdge("A", "B");
        path.addEdge("B", "C");

        if (path.degree("B") != 2 || path.hasCycle() || !path.isConnected()) {
            throw new IllegalStateException("Path graph invariant failed.");
        }

        if (!path.shortestPath("A", "C").equals(List.of("A", "B", "C"))) {
            throw new IllegalStateException("Shortest path invariant failed.");
        }

        path.addEdge("C", "A");
        if (!path.hasCycle()) {
            throw new IllegalStateException("Triangle cycle was not detected.");
        }

        Graph directed = new Graph(ConnectivityMode.DIRECTED);
        directed.addEdge("A", "B");
        if (directed.inDegree("B") != 1 || directed.outDegree("A") != 1) {
            throw new IllegalStateException("Directed degree invariant failed.");
        }

        try {
            path.degree("missing");
            throw new IllegalStateException("Missing vertex was accepted.");
        } catch (IllegalArgumentException expected) {
            System.out.println("Unknown vertex rejected: " + expected.getMessage());
        }

        Graph empty = new Graph(ConnectivityMode.UNDIRECTED);
        if (empty.isConnected()) {
            throw new IllegalStateException("Empty graph policy is inconsistent.");
        }

        System.out.println("All Java graph checks passed.");
    }

    public static void main(String[] args) {
        runEnterpriseScenario();
        runInvariantChecks();
    }
}
