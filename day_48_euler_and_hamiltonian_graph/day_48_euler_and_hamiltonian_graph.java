import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;

/*
 * Enterprise scenario: a facilities department plans road inspection.
 * Edge coverage is used to determine whether every road can be inspected
 * in one continuous route. Vertex coverage is used to plan visits to each
 * inspection station exactly once.
 */
public class GraphRoutePlanner {

    public record Road(int from, int to) {
        public Road {
            if (from < 0 || to < 0) {
                throw new IllegalArgumentException("Vertex indices must be non-negative.");
            }
            if (from == to) {
                throw new IllegalArgumentException("Self-loops are not supported.");
            }
        }
    }

    public enum RouteType {
        EULER_TRAIL,
        EULER_CIRCUIT,
        HAMILTONIAN_PATH,
        HAMILTONIAN_CYCLE
    }

    public static final class Graph {
        private final List<String> vertices;
        private final List<List<Integer>> adjacency;
        private final List<Road> edges;
        private final Set<String> edgeKeys = new HashSet<>();

        public Graph(List<String> vertices) {
            Objects.requireNonNull(vertices, "vertices");
            if (new HashSet<>(vertices).size() != vertices.size()) {
                throw new IllegalArgumentException("Vertex names must be unique.");
            }

            this.vertices = List.copyOf(vertices);
            this.adjacency = new ArrayList<>();
            for (int i = 0; i < vertices.size(); i++) {
                adjacency.add(new ArrayList<>());
            }
            this.edges = new ArrayList<>();
        }

        private String edgeKey(int u, int v) {
            return Math.min(u, v) + ":" + Math.max(u, v);
        }

        private void validateVertex(int v) {
            if (v < 0 || v >= vertices.size()) {
                throw new IndexOutOfBoundsException("Unknown vertex index: " + v);
            }
        }

        public void addRoad(int u, int v) {
            validateVertex(u);
            validateVertex(v);
            if (u == v) throw new IllegalArgumentException("Self-loop rejected.");

            String key = edgeKey(u, v);
            if (!edgeKeys.add(key)) {
                throw new IllegalArgumentException("Duplicate undirected road.");
            }

            edges.add(new Road(u, v));
            adjacency.get(u).add(v);
            adjacency.get(v).add(u);
        }

        public int degree(int v) {
            validateVertex(v);
            return adjacency.get(v).size();
        }

        public boolean connectedIgnoringIsolated() {
            int start = -1;
            for (int v = 0; v < vertices.size(); v++) {
                if (degree(v) > 0) {
                    start = v;
                    break;
                }
            }
            if (start == -1) return true;

            boolean[] visited = new boolean[vertices.size()];
            ArrayDeque<Integer> stack = new ArrayDeque<>();
            stack.push(start);

            while (!stack.isEmpty()) {
                int u = stack.pop();
                if (visited[u]) continue;
                visited[u] = true;

                for (int v : adjacency.get(u)) {
                    if (!visited[v]) stack.push(v);
                }
            }

            for (int v = 0; v < vertices.size(); v++) {
                if (degree(v) > 0 && !visited[v]) return false;
            }
            return true;
        }

        public boolean hasEulerTrail() {
            if (!connectedIgnoringIsolated()) return false;
            long odd = adjacency.stream().filter(a -> a.size() % 2 != 0).count();
            return odd == 0 || odd == 2;
        }

        public boolean hasEulerCircuit() {
            return connectedIgnoringIsolated()
                    && adjacency.stream().allMatch(a -> a.size() % 2 == 0);
        }

        public List<Integer> eulerTrail() {
            if (!hasEulerTrail()) return List.of();
            if (edges.isEmpty()) {
                return vertices.isEmpty() ? List.of() : List.of(0);
            }

            int start = -1;
            for (int v = 0; v < vertices.size(); v++) {
                if (degree(v) % 2 != 0) {
                    start = v;
                    break;
                }
            }
            if (start == -1) {
                for (int v = 0; v < vertices.size(); v++) {
                    if (degree(v) > 0) {
                        start = v;
                        break;
                    }
                }
            }

            List<List<int[]>> indexed = new ArrayList<>();
            for (int i = 0; i < vertices.size(); i++) {
                indexed.add(new ArrayList<>());
            }

            for (int id = 0; id < edges.size(); id++) {
                Road edge = edges.get(id);
                indexed.get(edge.from()).add(new int[]{edge.to(), id});
                indexed.get(edge.to()).add(new int[]{edge.from(), id});
            }

            boolean[] used = new boolean[edges.size()];
            ArrayDeque<Integer> stack = new ArrayDeque<>();
            List<Integer> result = new ArrayList<>();
            stack.push(start);

            while (!stack.isEmpty()) {
                int u = stack.peek();
                List<int[]> list = indexed.get(u);

                while (!list.isEmpty() && used[list.get(list.size() - 1)[1]]) {
                    list.remove(list.size() - 1);
                }

                if (list.isEmpty()) {
                    result.add(stack.pop());
                } else {
                    int[] next = list.remove(list.size() - 1);
                    int v = next[0];
                    int edgeId = next[1];

                    if (!used[edgeId]) {
                        used[edgeId] = true;
                        stack.push(v);
                    }
                }
            }

            for (boolean value : used) {
                if (!value) return List.of();
            }

            java.util.Collections.reverse(result);
            return List.copyOf(result);
        }

        public List<Integer> findHamiltonianPath() {
            if (vertices.isEmpty()) return List.of();

            List<Integer> path = new ArrayList<>();
            boolean[] visited = new boolean[vertices.size()];

            for (int start = 0; start < vertices.size(); start++) {
                if (searchPath(start, path, visited)) {
                    return List.copyOf(path);
                }
            }
            return List.of();
        }

        private boolean searchPath(
                int u, List<Integer> path, boolean[] visited) {
            path.add(u);
            visited[u] = true;

            if (path.size() == vertices.size()) return true;

            for (int v : adjacency.get(u)) {
                if (!visited[v] && searchPath(v, path, visited)) return true;
            }

            visited[u] = false;
            path.remove(path.size() - 1);
            return false;
        }

        public List<Integer> findHamiltonianCycle() {
            if (vertices.size() < 3) return List.of();

            // Anchor the cycle at vertex zero to reduce rotational duplicates.
            List<Integer> path = new ArrayList<>();
            boolean[] visited = new boolean[vertices.size()];
            path.add(0);
            visited[0] = true;

            return searchCycle(0, path, visited)
                    ? List.copyOf(path) : List.of();
        }

        private boolean searchCycle(
                int u, List<Integer> path, boolean[] visited) {
            if (path.size() == vertices.size()) {
                return adjacency.get(u).contains(0);
            }

            for (int v : adjacency.get(u)) {
                if (visited[v]) continue;

                visited[v] = true;
                path.add(v);

                if (searchCycle(v, path, visited)) return true;

                path.remove(path.size() - 1);
                visited[v] = false;
            }
            return false;
        }

        public boolean isHamiltonianPath(List<Integer> path) {
            if (path.size() != vertices.size()) return false;

            boolean[] seen = new boolean[vertices.size()];
            for (int i = 0; i < path.size(); i++) {
                int u = path.get(i);
                validateVertex(u);
                if (seen[u]) return false;
                seen[u] = true;

                if (i > 0 && !adjacency.get(path.get(i - 1)).contains(u)) {
                    return false;
                }
            }
            return true;
        }

        public boolean isHamiltonianCycle(List<Integer> cycle) {
            if (vertices.size() < 3 || !isHamiltonianPath(cycle)) return false;
            return adjacency.get(cycle.get(cycle.size() - 1)).contains(cycle.get(0));
        }

        public void report(String title) {
            System.out.println("\n" + title);
            for (int v = 0; v < vertices.size(); v++) {
                System.out.printf("%s degree=%d%n", vertices.get(v), degree(v));
            }

            printRoute("Euler trail", eulerTrail());
            System.out.println("Euler circuit exists: " + hasEulerCircuit());
            printRoute("Hamiltonian path", findHamiltonianPath());
            printRoute("Hamiltonian cycle", findHamiltonianCycle());
        }

        private void printRoute(String label, List<Integer> route) {
            if (route.isEmpty()) {
                System.out.println(label + ": unavailable");
                return;
            }

            List<String> names = route.stream()
                    .map(vertices::get)
                    .toList();
            System.out.println(label + ": " + String.join(" -> ", names));
        }
    }

    public static void main(String[] args) {
        Graph ring = new Graph(List.of("Depot", "North", "East", "South", "West"));
        ring.addRoad(0, 1);
        ring.addRoad(1, 2);
        ring.addRoad(2, 3);
        ring.addRoad(3, 4);
        ring.addRoad(4, 0);
        ring.report("Road inspection ring");

        Graph complete = new Graph(List.of("Hub", "Store", "Clinic", "School"));
        complete.addRoad(0, 1);
        complete.addRoad(0, 2);
        complete.addRoad(0, 3);
        complete.addRoad(1, 2);
        complete.addRoad(1, 3);
        complete.addRoad(2, 3);
        complete.report("Complete inspection network");

        Graph disconnected = new Graph(List.of("A", "B", "C", "D"));
        disconnected.addRoad(0, 1);
        disconnected.addRoad(2, 3);
        disconnected.report("Disconnected network");

        try {
            disconnected.addRoad(1, 0);
            throw new AssertionError("Duplicate road was not rejected.");
        } catch (IllegalArgumentException expected) {
            System.out.println("Duplicate-road validation passed.");
        }
    }
}
