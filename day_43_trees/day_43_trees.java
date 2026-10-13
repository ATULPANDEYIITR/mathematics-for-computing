import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.PriorityQueue;
import java.util.Set;

public class TreesEnterpriseCaseStudy {

    static final class TreeException extends RuntimeException {
        TreeException(String message) {
            super(message);
        }
    }

    enum NodeKind {
        ROOT,
        SERVICE,
        DATABASE,
        WORKER,
        GATEWAY
    }

    static final class RootedNode {
        private final String id;
        private final NodeKind kind;
        private RootedNode parent;
        private final List<RootedNode> children = new ArrayList<>();

        RootedNode(String id, NodeKind kind) {
            if (id == null || id.isBlank()) {
                throw new TreeException("Node identifier must not be blank.");
            }
            this.id = id;
            this.kind = Objects.requireNonNull(kind, "Node kind is required");
        }

        void addChild(RootedNode child) {
            Objects.requireNonNull(child, "Child is required");

            if (child == this || child.parent != null) {
                throw new TreeException("Self-links and multiple parents are forbidden.");
            }

            for (RootedNode ancestor = this; ancestor != null;
                 ancestor = ancestor.parent) {
                if (ancestor == child) {
                    throw new TreeException("Attachment would create a cycle.");
                }
            }

            child.parent = this;
            children.add(child);
        }

        String id() {
            return id;
        }

        NodeKind kind() {
            return kind;
        }

        List<RootedNode> children() {
            return Collections.unmodifiableList(children);
        }
    }

    record TreeMetrics(int nodes, int edges, int height, int leaves) {}

    static TreeMetrics measure(RootedNode root) {
        Objects.requireNonNull(root, "Root is required");

        record Visit(RootedNode node, int depth) {}

        ArrayDeque<Visit> stack = new ArrayDeque<>();
        Set<RootedNode> seen = new HashSet<>();
        stack.push(new Visit(root, 0));

        int count = 0;
        int leaves = 0;
        int height = 0;

        while (!stack.isEmpty()) {
            Visit visit = stack.pop();
            RootedNode node = visit.node();

            if (!seen.add(node)) {
                throw new TreeException("Repeated node detected.");
            }

            count++;
            height = Math.max(height, visit.depth());

            if (node.children().isEmpty()) leaves++;

            for (RootedNode child : node.children()) {
                stack.push(new Visit(child, visit.depth() + 1));
            }
        }

        return new TreeMetrics(count, count - 1, height, leaves);
    }

    record Edge(String from, String to, double weight) {
        Edge {
            if (from == null || to == null || from.isBlank() || to.isBlank()) {
                throw new TreeException("Edge endpoints must be nonempty.");
            }
            if (from.equals(to)) {
                throw new TreeException("Self-loops are forbidden.");
            }
            if (!Double.isFinite(weight)) {
                throw new TreeException("Weight must be finite.");
            }
        }
    }

    static final class Network {
        private final Set<String> vertices;
        private final Map<String, Map<String, Double>> adjacency = new HashMap<>();
        private final List<Edge> edges = new ArrayList<>();

        Network(List<String> vertexNames) {
            if (vertexNames == null || vertexNames.isEmpty()) {
                throw new TreeException("Network must contain vertices.");
            }

            vertices = new HashSet<>();

            for (String vertex : vertexNames) {
                if (vertex == null || vertex.isBlank() || !vertices.add(vertex)) {
                    throw new TreeException("Vertex names must be unique and nonempty.");
                }
                adjacency.put(vertex, new HashMap<>());
            }
        }

        void addEdge(String from, String to, double weight) {
            if (!vertices.contains(from) || !vertices.contains(to)) {
                throw new TreeException("Unknown edge endpoint.");
            }

            Edge edge = new Edge(from, to, weight);

            if (adjacency.get(from).containsKey(to)) {
                throw new TreeException("Duplicate edge rejected.");
            }

            adjacency.get(from).put(to, weight);
            adjacency.get(to).put(from, weight);
            edges.add(edge);
        }

        boolean connected() {
            String start = vertices.iterator().next();
            Set<String> visited = new HashSet<>();
            ArrayDeque<String> queue = new ArrayDeque<>();
            queue.add(start);
            visited.add(start);

            while (!queue.isEmpty()) {
                String current = queue.remove();

                for (String neighbor : adjacency.get(current).keySet()) {
                    if (visited.add(neighbor)) queue.add(neighbor);
                }
            }

            return visited.size() == vertices.size();
        }

        boolean hasCycle() {
            Set<String> visited = new HashSet<>();

            for (String start : vertices) {
                if (visited.contains(start)) continue;

                ArrayDeque<String[]> stack = new ArrayDeque<>();
                stack.push(new String[]{start, ""});

                while (!stack.isEmpty()) {
                    String[] state = stack.pop();
                    String current = state[0];
                    String parent = state[1];

                    if (!visited.add(current)) continue;

                    for (String neighbor : adjacency.get(current).keySet()) {
                        if (neighbor.equals(parent)) continue;
                        if (visited.contains(neighbor)) return true;
                        stack.push(new String[]{neighbor, current});
                    }
                }
            }

            return false;
        }

        boolean isTree() {
            return !vertices.isEmpty() &&
                   edges.size() == vertices.size() - 1 &&
                   connected();
        }

        List<Edge> kruskal() {
            Map<String, String> parent = new HashMap<>();
            Map<String, Integer> rank = new HashMap<>();

            for (String vertex : vertices) {
                parent.put(vertex, vertex);
                rank.put(vertex, 0);
            }

            List<Edge> ordered = new ArrayList<>(edges);
            ordered.sort(Comparator.comparingDouble(Edge::weight)
                .thenComparing(Edge::from)
                .thenComparing(Edge::to));

            List<Edge> selected = new ArrayList<>();

            for (Edge edge : ordered) {
                String rootA = find(parent, edge.from());
                String rootB = find(parent, edge.to());

                if (rootA.equals(rootB)) continue;

                // Union by rank keeps the disjoint-set forest shallow.
                int rankA = rank.get(rootA);
                int rankB = rank.get(rootB);

                if (rankA < rankB) {
                    parent.put(rootA, rootB);
                } else if (rankA > rankB) {
                    parent.put(rootB, rootA);
                } else {
                    parent.put(rootB, rootA);
                    rank.put(rootA, rankA + 1);
                }

                selected.add(edge);
            }

            if (selected.size() != vertices.size() - 1) {
                throw new TreeException("Disconnected graph has no spanning tree.");
            }

            return List.copyOf(selected);
        }

        private String find(Map<String, String> parent, String vertex) {
            String current = vertex;

            while (!parent.get(current).equals(current)) {
                String grandparent = parent.get(parent.get(current));
                parent.put(current, grandparent);
                current = grandparent;
            }

            return current;
        }

        double totalWeight(List<Edge> selected) {
            return selected.stream().mapToDouble(Edge::weight).sum();
        }

        int vertexCount() {
            return vertices.size();
        }
    }

    static final class BinaryNode {
        final int key;
        final BinaryNode left;
        final BinaryNode right;

        BinaryNode(int key, BinaryNode left, BinaryNode right) {
            this.key = key;
            this.left = left;
            this.right = right;
        }
    }

    static List<Integer> inorder(BinaryNode root) {
        List<Integer> result = new ArrayList<>();
        ArrayDeque<BinaryNode> stack = new ArrayDeque<>();
        BinaryNode current = root;

        while (current != null || !stack.isEmpty()) {
            while (current != null) {
                stack.push(current);
                current = current.left;
            }

            current = stack.pop();
            result.add(current.key);
            current = current.right;
        }

        return List.copyOf(result);
    }

    static int binaryHeight(BinaryNode root) {
        if (root == null) return -1;

        record LevelNode(BinaryNode node, int depth) {}

        ArrayDeque<LevelNode> queue = new ArrayDeque<>();
        queue.add(new LevelNode(root, 0));
        int height = 0;

        while (!queue.isEmpty()) {
            LevelNode current = queue.remove();
            height = Math.max(height, current.depth());

            if (current.node().left != null) {
                queue.add(new LevelNode(current.node().left, current.depth() + 1));
            }
            if (current.node().right != null) {
                queue.add(new LevelNode(current.node().right, current.depth() + 1));
            }
        }

        return height;
    }

    static void printSection(String title) {
        System.out.println("\n" + title);
    }

    public static void main(String[] args) {
        printSection("ENTERPRISE DEPLOYMENT HIERARCHY");

        RootedNode production = new RootedNode("production", NodeKind.ROOT);
        RootedNode regionEast = new RootedNode("region-east", NodeKind.SERVICE);
        RootedNode regionWest = new RootedNode("region-west", NodeKind.SERVICE);

        production.addChild(regionEast);
        production.addChild(regionWest);
        regionEast.addChild(new RootedNode("api", NodeKind.SERVICE));
        regionEast.addChild(new RootedNode("cache", NodeKind.SERVICE));
        regionWest.addChild(new RootedNode("database", NodeKind.DATABASE));
        regionWest.addChild(new RootedNode("worker", NodeKind.WORKER));

        TreeMetrics metrics = measure(production);
        System.out.println("Root: " + production.id());
        System.out.println("Nodes: " + metrics.nodes());
        System.out.println("Edges: " + metrics.edges());
        System.out.println("Height in edges: " + metrics.height());
        System.out.println("Leaves: " + metrics.leaves());

        printSection("NETWORK SPANNING TREE");

        Network network = new Network(
            List.of("gateway", "api", "cache", "database", "worker")
        );
        network.addEdge("gateway", "api", 4);
        network.addEdge("gateway", "cache", 7);
        network.addEdge("api", "cache", 2);
        network.addEdge("api", "database", 8);
        network.addEdge("cache", "database", 3);
        network.addEdge("cache", "worker", 6);
        network.addEdge("database", "worker", 1);

        System.out.println("Connected: " + network.connected());
        System.out.println("Has cycle: " + network.hasCycle());
        System.out.println("Is a tree: " + network.isTree());

        List<Edge> selected = network.kruskal();
        for (Edge edge : selected) {
            System.out.printf("%s -- %s : %.2f%n",
                edge.from(), edge.to(), edge.weight());
        }
        System.out.printf("Minimum total weight: %.2f%n",
            network.totalWeight(selected));

        printSection("BINARY TREE ORDERING");

        BinaryNode binaryRoot = new BinaryNode(
            20,
            new BinaryNode(10, new BinaryNode(5, null, null),
                new BinaryNode(15, null, null)),
            new BinaryNode(30, new BinaryNode(25, null, null),
                new BinaryNode(35, null, null))
        );

        System.out.println("Inorder: " + inorder(binaryRoot));
        System.out.println("Height: " + binaryHeight(binaryRoot));

        printSection("FAILURE HANDLING");

        Network disconnected = new Network(List.of("a", "b", "c"));
        disconnected.addEdge("a", "b", 1);

        try {
            disconnected.kruskal();
            throw new AssertionError("Expected disconnected graph rejection.");
        } catch (TreeException expected) {
            System.out.println("Rejected correctly: " + expected.getMessage());
        }

        System.out.println("\nEnterprise tree model completed.");
    }
}
