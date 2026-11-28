import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.function.DoubleBinaryOperator;

public class VectorOperations {

    public enum Operation {
        ADDITION,
        SUBTRACTION,
        SCALAR_MULTIPLICATION,
        DOT_PRODUCT,
        L1_NORM,
        L2_NORM,
        INFINITY_NORM,
        NORMALIZATION
    }

    public static class VectorException extends RuntimeException {
        public VectorException(String message) {
            super(message);
        }
    }

    public static class DimensionMismatchException
            extends VectorException {

        public DimensionMismatchException(int first, int second) {
            super("Dimension mismatch: " + first + " != " + second);
        }
    }

    public static class ZeroVectorException extends VectorException {
        public ZeroVectorException(String message) {
            super(message);
        }
    }

    public record VectorStatistics(
            int dimension,
            double l1Norm,
            double l2Norm,
            double infinityNorm
    ) {}

    public record CalculationResult(
            Operation operation,
            Object result,
            boolean successful,
            String error
    ) {
        public static CalculationResult success(
                Operation operation, Object result) {
            return new CalculationResult(
                    operation, result, true, null
            );
        }

        public static CalculationResult failure(
                Operation operation, String error) {
            return new CalculationResult(
                    operation, null, false, error
            );
        }
    }

    public static final class Vector {
        private final double[] values;

        public Vector(double... values) {
            if (values == null || values.length == 0) {
                throw new VectorException(
                        "A vector must contain at least one element."
                );
            }

            this.values = values.clone();

            for (double value : this.values) {
                if (!Double.isFinite(value)) {
                    throw new VectorException(
                            "Vector elements must be finite."
                    );
                }
            }
        }

        public int dimension() {
            return values.length;
        }

        public double[] components() {
            return values.clone();
        }

        private void validateCompatibility(Vector other) {
            Objects.requireNonNull(other, "Other vector cannot be null.");

            if (dimension() != other.dimension()) {
                throw new DimensionMismatchException(
                        dimension(), other.dimension()
                );
            }
        }

        private static double checked(double value, String operation) {
            if (!Double.isFinite(value)) {
                throw new VectorException(
                        operation + " produced a non-finite result."
                );
            }

            return value;
        }

        private Vector elementWise(
                Vector other,
                DoubleBinaryOperator operator
        ) {
            validateCompatibility(other);

            double[] result = new double[dimension()];

            for (int i = 0; i < dimension(); i++) {
                result[i] = checked(
                        operator.applyAsDouble(
                                values[i], other.values[i]
                        ),
                        "Element-wise operation"
                );
            }

            return new Vector(result);
        }

        public Vector add(Vector other) {
            return elementWise(other, Double::sum);
        }

        public Vector subtract(Vector other) {
            return elementWise(other, (a, b) -> a - b);
        }

        public Vector scale(double scalar) {
            if (!Double.isFinite(scalar)) {
                throw new VectorException(
                        "Scalar must be finite."
                );
            }

            double[] result = new double[dimension()];

            for (int i = 0; i < dimension(); i++) {
                result[i] = checked(
                        values[i] * scalar,
                        "Scalar multiplication"
                );
            }

            return new Vector(result);
        }

        public double dot(Vector other) {
            validateCompatibility(other);

            // Compensated summation reduces numerical accumulation error.
            double sum = 0.0;
            double correction = 0.0;

            for (int i = 0; i < dimension(); i++) {
                double product = checked(
                        values[i] * other.values[i],
                        "Dot product multiplication"
                );

                double adjusted = product - correction;
                double temporary = sum + adjusted;

                correction = (temporary - sum) - adjusted;
                sum = temporary;
            }

            return checked(sum, "Dot product");
        }

        public double l1Norm() {
            double sum = 0.0;
            double correction = 0.0;

            for (double value : values) {
                double adjusted = Math.abs(value) - correction;
                double temporary = sum + adjusted;

                correction = (temporary - sum) - adjusted;
                sum = temporary;
            }

            return checked(sum, "L1 norm");
        }

        public double l2Norm() {
            double result = 0.0;

            for (double value : values) {
                result = Math.hypot(result, value);
            }

            return checked(result, "L2 norm");
        }

        public double infinityNorm() {
            double maximum = 0.0;

            for (double value : values) {
                maximum = Math.max(maximum, Math.abs(value));
            }

            return maximum;
        }

        public double pNorm(double p) {
            if (p == Double.POSITIVE_INFINITY) {
                return infinityNorm();
            }

            if (!Double.isFinite(p) || p < 1.0) {
                throw new VectorException(
                        "Norm order must be >= 1 or positive infinity."
                );
            }

            if (p == 1.0) return l1Norm();
            if (p == 2.0) return l2Norm();

            double maximum = infinityNorm();

            if (maximum == 0.0) return 0.0;

            double sum = 0.0;

            for (double value : values) {
                sum += Math.pow(Math.abs(value) / maximum, p);
            }

            return checked(
                    maximum * Math.pow(sum, 1.0 / p),
                    "p-norm"
            );
        }

        public Vector normalize() {
            double magnitude = l2Norm();

            if (magnitude == 0.0) {
                throw new ZeroVectorException(
                        "Cannot normalize a zero vector."
                );
            }

            return scale(1.0 / magnitude);
        }

        public double cosineSimilarity(Vector other) {
            validateCompatibility(other);

            double firstNorm = l2Norm();
            double secondNorm = other.l2Norm();

            if (firstNorm == 0.0 || secondNorm == 0.0) {
                throw new ZeroVectorException(
                        "Cosine similarity is undefined for zero vectors."
                );
            }

            return Math.max(
                    -1.0,
                    Math.min(
                            1.0,
                            dot(other) / firstNorm / secondNorm
                    )
            );
        }

        public double distance(Vector other) {
            return subtract(other).l2Norm();
        }

        public boolean isOrthogonal(
                Vector other,
                double tolerance
        ) {
            if (!Double.isFinite(tolerance) || tolerance < 0.0) {
                throw new VectorException("Invalid tolerance.");
            }

            return Math.abs(dot(other)) <= tolerance;
        }

        public VectorStatistics statistics() {
            return new VectorStatistics(
                    dimension(),
                    l1Norm(),
                    l2Norm(),
                    infinityNorm()
            );
        }

        @Override
        public String toString() {
            StringBuilder result = new StringBuilder("[");

            for (int i = 0; i < values.length; i++) {
                result.append(values[i]);

                if (i < values.length - 1) {
                    result.append(", ");
                }
            }

            return result.append("]").toString();
        }
    }

    public static final class VectorService {

        public Object execute(
                Operation operation,
                Vector first,
                Vector second,
                Double scalar
        ) {
            Objects.requireNonNull(operation);
            Objects.requireNonNull(first);

            return switch (operation) {
                case ADDITION -> first.add(requireSecond(second));
                case SUBTRACTION -> first.subtract(requireSecond(second));
                case SCALAR_MULTIPLICATION ->
                        first.scale(requireScalar(scalar));
                case DOT_PRODUCT ->
                        first.dot(requireSecond(second));
                case L1_NORM -> first.l1Norm();
                case L2_NORM -> first.l2Norm();
                case INFINITY_NORM -> first.infinityNorm();
                case NORMALIZATION -> first.normalize();
            };
        }

        private Vector requireSecond(Vector second) {
            if (second == null) {
                throw new VectorException(
                        "This operation requires a second vector."
                );
            }

            return second;
        }

        private double requireScalar(Double scalar) {
            if (scalar == null) {
                throw new VectorException(
                        "Scalar multiplication requires a scalar."
                );
            }

            return scalar;
        }

        public CompletableFuture<List<CalculationResult>> executeBatch(
                List<Vector> vectors,
                ExecutorService executor
        ) {
            Objects.requireNonNull(vectors);
            Objects.requireNonNull(executor);

            List<CompletableFuture<CalculationResult>> tasks =
                    new ArrayList<>();

            for (Vector vector : vectors) {
                tasks.add(
                        CompletableFuture.supplyAsync(() -> {
                            try {
                                return CalculationResult.success(
                                        Operation.L2_NORM,
                                        vector.l2Norm()
                                );
                            } catch (RuntimeException error) {
                                return CalculationResult.failure(
                                        Operation.L2_NORM,
                                        error.getMessage()
                                );
                            }
                        }, executor)
                );
            }

            CompletableFuture<Void> combined =
                    CompletableFuture.allOf(
                            tasks.toArray(new CompletableFuture[0])
                    );

            return combined.thenApply(ignored ->
                    tasks.stream()
                            .map(CompletableFuture::join)
                            .toList()
            );
        }
    }

    private static void assertClose(
            double actual,
            double expected,
            double tolerance
    ) {
        if (Math.abs(actual - expected) > tolerance) {
            throw new AssertionError(
                    "Expected " + expected + " but got " + actual
            );
        }
    }

    public static void main(String[] args) {
        try {
            Vector first = new Vector(3, 4);
            Vector second = new Vector(4, 3);

            VectorService service = new VectorService();

            System.out.println("VECTOR OPERATIONS ENGINE");
            System.out.println("========================");

            System.out.println("\nFundamental operations");

            System.out.println("First: " + first);
            System.out.println("Second: " + second);

            System.out.println("Addition: " + first.add(second));
            System.out.println("Subtraction: " + first.subtract(second));
            System.out.println("Scalar multiplication: " + first.scale(3));
            System.out.println("Dot product: " + first.dot(second));

            System.out.println("\nNorms");

            VectorStatistics stats = first.statistics();

            System.out.println("L1: " + stats.l1Norm());
            System.out.println("L2: " + stats.l2Norm());
            System.out.println("Infinity: " + stats.infinityNorm());
            System.out.println("L3: " + first.pNorm(3));

            System.out.println("\nAdvanced calculations");

            System.out.println("Normalized: " + first.normalize());
            System.out.println("Distance: " + first.distance(second));
            System.out.println(
                    "Cosine similarity: " +
                    first.cosineSimilarity(second)
            );

            System.out.println(
                    "Orthogonal: " +
                    new Vector(1, 0).isOrthogonal(
                            new Vector(0, 1), 1e-10
                    )
            );

            System.out.println("\nService layer");

            Object result = service.execute(
                    Operation.ADDITION,
                    first,
                    second,
                    null
            );

            System.out.println("Service addition: " + result);

            System.out.println("\nAsynchronous enterprise batch");

            ExecutorService executor = Executors.newFixedThreadPool(3);

            try {
                List<Vector> batch = List.of(
                        new Vector(3, 4),
                        new Vector(1, 2, 2),
                        new Vector(5, 12),
                        new Vector(0, 0)
                );

                List<CalculationResult> results =
                        service.executeBatch(batch, executor)
                                .get(5, TimeUnit.SECONDS);

                for (CalculationResult calculation : results) {
                    System.out.println(calculation);
                }
            } finally {
                executor.shutdown();

                if (!executor.awaitTermination(5, TimeUnit.SECONDS)) {
                    executor.shutdownNow();
                }
            }

            System.out.println("\nFailure handling");

            try {
                first.add(new Vector(1, 2, 3));
            } catch (DimensionMismatchException error) {
                System.out.println(error.getMessage());
            }

            try {
                new Vector(0, 0).normalize();
            } catch (ZeroVectorException error) {
                System.out.println(error.getMessage());
            }

            try {
                new Vector(1, Double.NaN);
            } catch (VectorException error) {
                System.out.println(error.getMessage());
            }

            System.out.println("\nAssertions");

            assertClose(first.dot(second), 24.0, 1e-12);
            assertClose(first.l2Norm(), 5.0, 1e-12);
            assertClose(first.normalize().l2Norm(), 1.0, 1e-12);

            if (!first.add(second).toString().equals("[7.0, 7.0]")) {
                throw new AssertionError("Addition failed.");
            }

            System.out.println("All assertions passed.");

        } catch (Exception error) {
            System.err.println("Execution failed: " + error.getMessage());
            System.exit(1);
        }
    }
}
