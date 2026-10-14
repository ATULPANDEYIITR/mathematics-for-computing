import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Deque;
import java.util.List;

/**
 * Graph traversal matrix for an enterprise dependency network.
 *
 * Vertices represent services. Directed edges represent dependencies.
 * BFS identifies reachable services and shortest dependency-chain lengths.
 * DFS produces a depth-first exploration order.
 *
 * Compile: javac GraphTraversalMatrix.java
 * Run:     java GraphTraversalMatrix
 */
public final class GraphTraversalMatrix {

    private GraphTraversalMatrix() {
    }

    public enum GraphType {
        DIRECTED,
        UNDIRECTED
    }

    public static final class GraphException extends IllegalArgumentException {
        public GraphException(String message) {
            super(message);
        }
    }

    public record TraversalResult(
            List<Integer> order,
            List<Integer> parent,
            List<Integer> distance) {

        public TraversalResult {
            order = List.copyOf(order);
            parent = Collections.unmodifiableList(new ArrayList<>(parent));
            distance = Collections.unmodifiableList(new ArrayList<>(distance));
        }

        public List<Integer> pathTo(int target) {
            if (target < 0 || target >= parent.size()) {
                throw new GraphException("Target vertex is outside the graph.");
            }

            if (distance.get(target) == -1) {
                return List.of();
            }

            List<Integer> path = new ArrayList<>();
            Integer current = target;

            while (current != null) {
                path.add(current);
                int predecessor = parent.get(current);
                current = predecessor == -1 ? null : predecessor;
            }

            Collections.reverse(path);
            return List.copyOf(path);
        }
    }

    public static final class GraphMatrix {
        private final int[][] matrix;
        private final GraphType type;
        private final int size;

        public GraphMatrix(int[][] input, GraphType type) {
            if (input == null || type == null) {
                throw new GraphException("Matrix and graph type are required.");
            }

            this.size = input.length;
            this.type = type;
            this.matrix = new int[size][size];

            for (int row = 0; row < size; row++) {
                if (input[row] == null || input[row].length != size) {
                    throw new GraphException("Adjacency matrix must be square.");
                }

                for (int column = 0; column < size; column++) {
                    int value = input[row][column];

                    if (value != 0 && value != 1) {
                        throw new GraphException(
                                "An unweighted matrix must contain only zero and one.");
                    }

                    this.matrix[row][column] = value;
                }
            }

            if (type == GraphType.UNDIRECTED) {
                for (int row = 0; row < size; row++) {
                    for (int column = row + 1; column < size; column++) {
                        if (matrix[row][column] != matrix[column][row]) {
                            throw new GraphException(
                                    "An undirected matrix must be symmetric.");
                        }
                    }
                }
            }
        }

        private void checkVertex(int vertex) {
            if (vertex < 0 || vertex >= size) {
                throw new GraphException("Vertex index is outside the graph.");
            }
        }

        public List<Integer> neighbors(int vertex) {
            checkVertex(vertex);

            List<Integer> neighbors = new ArrayList<>();
            for (int column = 0; column < size; column++) {
                if (column != vertex && matrix[vertex][column] == 1) {
                    neighbors.add(column);
                }
            }

            return List.copyOf(neighbors);
        }

        public TraversalResult bfs(int start) {
            checkVertex(start);

            boolean[] discovered = new boolean[size];
            List<Integer> parent = new ArrayList<>(
                    Collections.nCopies(size, -1));
            List<Integer> distance = new ArrayList<>(
                    Collections.nCopies(size, -1));
            List<Integer> order = new ArrayList<>();
            Deque<Integer> queue = new ArrayDeque<>();

            discovered[start] = true;
            distance.set(start, 0);
            queue.addLast(start);

            while (!queue.isEmpty()) {
                int current = queue.removeFirst();
                order.add(current);

                for (int next : neighbors(current)) {
                    if (discovered[next]) {
                        continue;
                    }

                    discovered[next] = true;
                    parent.set(next, current);
                    distance.set(next, distance.get(current) + 1);
                    queue.addLast(next);
                }
            }

            return new TraversalResult(order, parent, distance);
        }

        public TraversalResult dfs(int start) {
            checkVertex(start);

            boolean[] discovered = new boolean[size];
            List<Integer> parent = new ArrayList<>(
                    Collections.nCopies(size, -1));
            List<Integer> depth = new ArrayList<>(
                    Collections.nCopies(size, -1));
            List<Integer> order = new ArrayList<>();

            // Explicit stack prevents a deep dependency chain from exhausting
            // the Java call stack through recursive DFS.
            Deque<Integer> stack = new ArrayDeque<>();
            stack.push(start);
            depth.set(start, 0);

            while (!stack.isEmpty()) {
                int current = stack.pop();

                if (discovered[current]) {
                    continue;
                }

                discovered[current] = true;
                order.add(current);

                List<Integer> adjacent = neighbors(current);

                for (int i = adjacent.size() - 1; i >= 0; i--) {
                    int next =
