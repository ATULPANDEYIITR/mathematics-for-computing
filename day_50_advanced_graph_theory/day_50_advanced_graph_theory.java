import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Queue;
import java.util.Set;
import java.util.TreeSet;

public class AdvancedGraphTheory {

    record Edge(String first, String second) {
        Edge {
            if (first.equals(second)) {
                throw new IllegalArgumentException(
                    "Simple graphs cannot contain self-loops."
                );
            }

            if (first.compareTo(second) > 0) {
                String temporary = first;
                first = second;
                second = temporary;
            }
        }
    }

    enum GraphRelation {
        ISOMORPHIC,
        NON_ISOMORPHIC,
        UNKNOWN
    }

    enum PlanarityStatus {
        PLANAR,
        NON_PLANAR_CERTIFIED,
        UNDETERMINED
    }

    record PlanarityAssessment(
        PlanarityStatus status,
        String reason
    ) {}

    static final class Graph {
        private final Set<String> vertices = new TreeSet<>();
        private final Map<String, Set<String>> adjacency =
            new TreeSetMap<>();

        void addVertex(String vertex) {
            Objects.requireNonNull(vertex, "vertex");
            vertices.add(vertex);
            adjacency.computeIfAbsent(vertex, ignored -> new TreeSet<>());
        }

        void addEdge(String first, String second) {
            if (first.equals(second)) {
                throw new IllegalArgumentException(
                    "Self-loops are not allowed."
                );
            }

            addVertex(first);
            addVertex(second);
            adjacency.get(first).add(second);
            adjacency.get(second).add(first);
        }

        boolean hasEdge(String first, String second) {
            return adjacency.containsKey(first)
                && adjacency.get(first).contains(second);
        }

        int degree(String vertex) {
            Set<String> neighbors = adjacency.get(vertex);

            if (neighbors == null) {
                throw new IllegalArgumentException(
                    "Unknown vertex: " + vertex
                );
            }

            return neighbors.size();
        }

        Set<String> vertices() {
            return Set.copyOf(vertices);
        }

        Set<Edge> edges() {
            Set<Edge> result = new TreeSet<>(
                Comparator.comparing(Edge::first)
                    .thenComparing(Edge::second)
            );

            for (String first : vertices) {
                for (String second : adjacency.get(first)) {
                    result.add(new Edge(first, second));
                }
            }

            return Set.copyOf(result);
        }

        Graph contract(String first, String second) {
            if (!hasEdge(first, second)) {
                throw new IllegalArgumentException(
                    "Cannot contract an absent edge."
                );
            }

            Graph result = new Graph();
            String merged = "(" + first + "+" + second + ")";

            for (String vertex : vertices) {
                if (!vertex.equals(first) && !vertex.equals(second)) {
                    result.addVertex(vertex);
                }
            }

            result.addVertex(merged);

            for (Edge edge : edges()) {
                if (edge.equals(new Edge(first, second))) {
                    continue;
                }

                String left = edge.first();
                String right = edge.second();

                if (left.equals(first) || left.equals(second)) {
                    left = merged;
                }

                if (right.equals(first) || right.equals(second)) {
                    right = merged;
                }

                if (!left.equals(right)) {
                    result.addEdge(left, right);
                }
            }

            return result;
        }

        boolean connected() {
            if (vertices.isEmpty()) {
                return true;
            }

            String source = vertices.iterator().next();
            Set<String> visited = new HashSet<>();
            Queue<String> queue = new ArrayDeque<>();

            queue.add(source);

            while (!queue.isEmpty()) {
                String current = queue.remove();

                if (!visited.add(current)) {
                    continue;
                }

                queue.addAll(adjacency.get(current));
            }

            return visited.size() == vertices.size();
        }
    }

    /*
     * TreeSetMap supplies deterministic ordered maps while keeping the
     * implementation dependency-free. The graph itself remains mutable so
     * contractions can construct derived graphs without aliasing state.
     */
    static final class TreeSetMap<K, V> extends HashMap<K, V> {
        @Override
        public V get(Object key) {
            return super.get(key);
        }
    }

    static Graph completeGraph(int size) {
        if (size < 0) {
            throw new IllegalArgumentException("Size cannot be negative.");
        }

        Graph graph = new Graph();

        for (int i = 0; i < size; i++) {
            graph.addVertex(String.valueOf(i));
        }

        for (int i = 0; i < size; i++) {
            for (int j = i + 1; j < size; j++) {
                graph.addEdge(String.valueOf(i), String.valueOf(j));
            }
        }

        return graph;
    }

    static Graph completeBipartiteGraph(int left, int right) {
        if (left <= 0 || right <= 0) {
            throw new IllegalArgumentException(
                "Both partition sizes must be positive."
            );
        }

        Graph graph = new Graph();

        for (int i = 0; i < left; i++) {
            graph.addVertex("L" + i);
        }

        for (int j = 0; j < right; j++) {
            graph.addVertex("R" + j);
        }

        for (int i = 0; i < left; i++) {
            for (int j = 0; j < right; j++) {
                graph.addEdge("L" + i, "R" + j);
            }
        }

        return graph;
    }

    static List<Integer> degreeSequence(Graph graph) {
        return graph.vertices()
            .stream()
            .map(graph::degree)
            .sorted(Comparator.reverseOrder())
            .toList();
    }

    static GraphRelation isomorphic(Graph first, Graph second) {
        if (first.vertices().size() != second.vertices().size()) {
            return GraphRelation.NON_ISOMORPHIC;
        }

        if (first.edges().size() != second.edges().size()) {
            return GraphRelation.NON_ISOMORPHIC;
        }

        if (!degreeSequence(first).equals(degreeSequence(second))) {
            return GraphRelation.NON_ISOMORPHIC;
        }

        Map<Integer, List<String>> candidates = new HashMap<>();

        for (String vertex : second.vertices()) {
            candidates
                .computeIfAbsent(second.degree(vertex), ignored -> new ArrayList<>())
                .add(vertex);
        }

        List<String> source = new ArrayList<>(first.vertices());

        source.sort(
            Comparator
                .comparingInt(first::degree)
                .reversed()
        );

        Map<String, String> mapping = new LinkedHashMap<>();
        Set<String> used = new HashSet<>();

        boolean found = searchIsomorphism(
            first,
            second,
            source,
            candidates,
            mapping,
            used,
            0
        );

        return found
            ? GraphRelation.ISOMORPHIC
            : GraphRelation.NON_ISOMORPHIC;
    }

    private static boolean searchIsomorphism(
        Graph first,
        Graph second,
        List<String> source,
        Map<Integer, List<String>> candidates,
        Map<String, String> mapping,
        Set<String> used,
        int index
    ) {
        if (index == source.size()) {
            return true;
        }

        String sourceVertex = source.get(index);

        for (String candidate :
            candidates.getOrDefault(
                first.degree(sourceVertex),
                List.of()
            )) {

            if (used.contains(candidate)) {
                continue;
            }

            boolean compatible = true;

            for (Map.Entry<String, String> entry : mapping.entrySet()) {
                if (
                    first.hasEdge(sourceVertex, entry.getKey())
                        != second.hasEdge(candidate, entry.getValue())
                ) {
                    compatible = false;
                    break;
                }
            }

            if (!compatible) {
                continue;
            }

            mapping.put(sourceVertex, candidate);
            used.add(candidate);

            if (
                searchIsomorphism(
                    first,
                    second,
                    source,
                    candidates,
                    mapping,
                    used,
                    index + 1
                )
            ) {
                return true;
            }

            used.remove(candidate);
            mapping.remove(sourceVertex);
        }

        return false;
    }

    static boolean isBipartite(Graph graph) {
        Map<String, Integer> colors = new HashMap<>();

        for (String source : graph.vertices()) {
            if (colors.containsKey(source)) {
                continue;
            }

            colors.put(source, 0);
            Queue<String> queue = new ArrayDeque<>();
            queue.add(source);

            while (!queue.isEmpty()) {
                String current = queue.remove();

                for (String neighbor :
                    graph.adjacency.get(current)) {

                    if (!colors.containsKey(neighbor)) {
                        colors.put(
                            neighbor,
                            1 - colors.get(current)
                        );
                        queue.add(neighbor);
                    } else if (
                        colors.get(neighbor)
                            .equals(colors.get(current))
                    ) {
                        return false;
                    }
                }
            }
        }

        return true;
    }

    static PlanarityAssessment assessPlanarity(Graph graph) {
        int n = graph.vertices.size();
        int m = graph.edges().size();

        if (n <= 4) {
            return new PlanarityAssessment(
                PlanarityStatus.PLANAR,
                "Every simple graph with at most four vertices is planar."
            );
        }

        if (m > 3 * n - 6) {
            return new PlanarityAssessment(
                PlanarityStatus.NON_PLANAR_CERTIFIED,
                "The graph violates the simple planar bound m <= 3n - 6."
            );
        }

        if (isBipartite(graph) && m > 2 * n - 4) {
            return new PlanarityAssessment(
                PlanarityStatus.NON_PLANAR_CERTIFIED,
                "The bipartite graph violates m <= 2n - 4."
            );
        }

        if (containsK5Subgraph(graph)) {
            return new PlanarityAssessment(
                PlanarityStatus.NON_PLANAR_CERTIFIED,
                "The graph contains K5 as a subgraph."
            );
        }

        return new PlanarityAssessment(
            PlanarityStatus.UNDETERMINED,
            "Necessary bounds hold; a complete planarity algorithm is required."
        );
    }

    static boolean containsK5Subgraph(Graph graph) {
        List<String> vertices = new ArrayList<>(graph.vertices());

        if (vertices.size() < 5) {
            return false;
        }

        for (int a = 0; a < vertices.size(); a++) {
            for (int b = a + 1; b < vertices.size(); b++) {
                for (int c = b + 1; c < vertices.size(); c++) {
                    for (int d = c + 1; d < vertices.size(); d++) {
                        for (int e = d + 1; e < vertices.size(); e++) {
                            List<String> selected = List.of(
                                vertices.get(a),
                                vertices.get(b),
                                vertices.get(c),
                                vertices.get(d),
                                vertices.get(e)
                            );

                            boolean complete = true;

                            for (int i = 0; i < selected.size(); i++) {
                                for (int j = i + 1; j < selected.size(); j++) {
                                    if (!graph.hasEdge(
                                        selected.get(i),
                                        selected.get(j)
                                    )) {
                                        complete = false;
                                    }
                                }
                            }

                            if (complete) {
                                return true;
                            }
                        }
                    }
                }
            }
        }

        return false;
    }

    interface MergeRule {
        boolean permits(Graph graph);

        String name();
    }

    record DenseGraphRule(int maximumEdges) implements MergeRule {
        @Override
        public boolean permits(Graph graph) {
            return graph.edges().size() <= maximumEdges;
        }

        @Override
        public String name() {
            return "maximum-edge policy";
        }
    }

    static final class GovernanceService {
        private final List<MergeRule> rules;

        GovernanceService(List<MergeRule> rules) {
            this.rules = List.copyOf(rules);
        }

        List<String> violations(Graph graph) {
            List<String> violations = new ArrayList<>();

            for (MergeRule rule : rules) {
                if (!rule.permits(graph)) {
                    violations.add(rule.name());
                }
            }

            return List.copyOf(violations);
        }
    }

    public static void main(String[] args) {
        System.out.println("Advanced Graph Theory");
        System.out.println("=====================");
        System.out.println();

        Graph firstCycle = completeGraph(5);
        Graph secondCycle = new Graph();

        for (String vertex : List.of("A", "B", "C", "D", "E")) {
            secondCycle.addVertex(vertex);
        }

        secondCycle.addEdge("A", "C");
        secondCycle.addEdge("C", "E");
        secondCycle.addEdge("E", "B");
        secondCycle.addEdge("B", "D");
        secondCycle.addEdge("D", "A");

        System.out.println("Graph isomorphism");
        System.out.println("-----------------");
        System.out.println(
            "K5 and the five-cycle are: "
                + isomorphic(firstCycle, secondCycle)
        );

        Graph cycle = new Graph();
        for (int i = 0; i < 5; i++) {
            cycle.addEdge(
                String.valueOf(i),
                String.valueOf((i + 1) % 5)
            );
        }

        System.out.println(
            "C5 and renamed C5 are: "
                + isomorphic(cycle, secondCycle)
        );

        System.out.println();
        System.out.println("Planarity assessment");
        System.out.println("--------------------");

        for (Map.Entry<String, Graph> entry :
            Map.of(
                "C5", cycle,
                "K5", completeGraph(5),
                "K3,3", completeBipartiteGraph(3, 3)
            ).entrySet()) {

            PlanarityAssessment assessment =
                assessPlanarity(entry.getValue());

            System.out.println(
                entry.getKey()
                    + ": "
                    + assessment.status()
                    + " - "
                    + assessment.reason()
            );
        }

        System.out.println();
        System.out.println("Graph minors");
        System.out.println("------------");

        Graph k6 = completeGraph(6);
        Graph contraction = k6.contract("0", "1");

        System.out.println(
            "K6 has "
                + k6.vertices().size()
                + " vertices and "
                + k6.edges().size()
                + " edges."
        );

        System.out.println(
            "After contracting one edge: "
                + contraction.vertices().size()
                + " vertices and "
                + contraction.edges().size()
                + " edges."
        );

        System.out.println();
        System.out.println("Extremal concepts");
        System.out.println("-----------------");

        for (int n = 3; n <= 9; n++) {
            int simpleMaximum = n * (n - 1) / 2;
            int planarMaximum = 3 * n - 6;
            int bipartitePlanarMaximum = 2 * n - 4;

            System.out.printf(
                "n=%d: simple=%d, planar<=%d, bipartite-planar<=%d%n",
                n,
                simpleMaximum,
                planarMaximum,
                bipartitePlanarMaximum
            );
        }

        System.out.println();
        System.out.println("Enterprise domain policy");
        System.out.println("------------------------");

        GovernanceService service = new GovernanceService(
            List.of(new DenseGraphRule(12))
        );

        Graph dependencyGraph = completeBipartiteGraph(3, 4);

        System.out.println(
            "Dependency graph edges: "
                + dependencyGraph.edges().size()
        );

        System.out.println(
            "Policy violations: "
                + service.violations(dependencyGraph)
        );

        System.out.println();
        System.out.println("Implementation boundaries");
        System.out.println("-------------------------");
        System.out.println(
            "The isomorphism service uses exact backtracking and is exponential "
                + "in the worst case."
        );
        System.out.println(
            "The planarity service returns an explicit UNDETERMINED state "
                + "instead of treating necessary inequalities as sufficient."
        );
        System.out.println(
            "Edge contraction removes parallel-edge duplication naturally "
                + "through adjacency sets."
        );
        System.out.println(
            "Immutable records and List.copyOf are used for policy configuration "
                + "to reduce accidental mutation."
        );
    }
}
