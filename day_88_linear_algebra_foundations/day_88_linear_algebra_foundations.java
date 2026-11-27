import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.stream.IntStream;

/*
 * Linear Algebra Foundations
 *
 * Enterprise-oriented Java 17 implementation.
 *
 * Domain model:
 * - Scalar
 * - Vector
 * - VectorSpace
 * - LinearCombination
 * - Basis
 * - MatrixRank
 * - VectorSpaceService
 *
 * The implementation uses immutable domain objects,
 * explicit validation, interfaces, records and services.
 */

public class Main {

    private static final double EPSILON = 1e-9;

    // --------------------------------------------------
    // Domain exceptions
    // --------------------------------------------------

    static class LinearAlgebraException extends RuntimeException {
        LinearAlgebraException(String message) {
            super(message);
        }
    }

    static class DimensionException extends LinearAlgebraException {
        DimensionException(String message) {
            super(message);
        }
    }

    static class ValidationException extends LinearAlgebraException {
        ValidationException(String message) {
            super(message);
        }
    }

    // --------------------------------------------------
    // Scalar domain object
    // --------------------------------------------------

    record Scalar(double value) {

        Scalar {
            if (!Double.isFinite(value)) {
                throw new ValidationException(
                    "A scalar must be finite."
                );
            }
        }

        Scalar add(Scalar other) {
            return new Scalar(value + other.value);
        }

        Scalar multiply(Scalar other) {
            return new Scalar(value * other.value);
        }
    }

    // --------------------------------------------------
    // Immutable vector domain object
    // --------------------------------------------------

    static final class Vector {

        private final List<Double> components;

        Vector(List<Double> components) {
            Objects.requireNonNull(
                components,
                "Components cannot be null."
            );

            if (components.isEmpty()) {
                throw new DimensionException(
                    "A vector must have at least one component."
                );
            }

            List<Double> validated = new ArrayList<>();

            for (Double component : components) {
                if (
                    component == null ||
                    !Double.isFinite(component)
                ) {
                    throw new ValidationException(
                        "Every vector component must be finite."
                    );
                }

                validated.add(component);
            }

            this.components = Collections.unmodifiableList(
                validated
            );
        }

        static Vector of(double... values) {
            List<Double> components = new ArrayList<>();

            for (double value : values) {
                components.add(value);
            }

            return new Vector(components);
        }

        List<Double> components() {
            return components;
        }

        int dimension() {
            return components.size();
        }

        double component(int index) {
            return components.get(index);
        }

        void requireSameDimension(Vector other) {
            Objects.requireNonNull(other);

            if (dimension() != other.dimension()) {
                throw new DimensionException(
                    "Vector dimensions do not match."
                );
            }
        }

        Vector add(Vector other) {
            requireSameDimension(other);

            return new Vector(
                IntStream.range(0, dimension())
                    .mapToObj(i ->
                        component(i) + other.component(i)
                    )
                    .toList()
            );
        }

        Vector subtract(Vector other) {
            requireSameDimension(other);

            return new Vector(
                IntStream.range(0, dimension())
                    .mapToObj(i ->
                        component(i) - other.component(i)
                    )
                    .toList()
            );
        }

        Vector negate() {
            return scale(-1.0);
        }

        Vector scale(double scalar) {
            if (!Double.isFinite(scalar)) {
                throw new ValidationException(
                    "Scalar must be finite."
                );
            }

            return new Vector(
                components.stream()
                    .map(value -> value * scalar)
                    .toList()
            );
        }

        double dot(Vector other) {
            requireSameDimension(other);

            double result = 0.0;

            for (int i = 0; i < dimension(); i++) {
                result += component(i) * other.component(i);
            }

            return result;
        }

        double norm() {
            return Math.sqrt(dot(this));
        }

        Vector normalize() {
            double magnitude = norm();

            if (magnitude <= EPSILON) {
                throw new LinearAlgebraException(
                    "The zero vector cannot be normalized."
                );
            }

            return scale(1.0 / magnitude);
        }

        boolean isZero() {
            return components.stream().allMatch(
                value -> Math.abs(value) <= EPSILON
            );
        }

        boolean approximatelyEquals(Vector other) {
            requireSameDimension(other);

            for (int i = 0; i < dimension(); i++) {
                if (
                    Math.abs(component(i) - other.component(i))
                    > EPSILON
                ) {
                    return false;
                }
            }

            return true;
        }

        @Override
        public String toString() {
            return components.toString();
        }
    }

    // --------------------------------------------------
    // Vector-space domain
    // --------------------------------------------------

    enum Field {
        REAL
    }

    record VectorSpace(int dimension, Field field) {

        VectorSpace {
            if (dimension <= 0) {
                throw new DimensionException(
                    "Vector-space dimension must be positive."
                );
            }

            Objects.requireNonNull(field);
        }

        void validate(Vector vector) {
            if (vector.dimension() != dimension) {
                throw new DimensionException(
                    "Vector does not belong to R^" + dimension
                );
            }
        }

        Vector zero() {
            return Vector.of(
                new double[dimension]
            );
        }
    }

    // --------------------------------------------------
    // Linear combination domain
    // --------------------------------------------------

    record LinearCombination(
        List<Vector> vectors,
        List<Scalar> coefficients
    ) {

        LinearCombination {
            vectors = List.copyOf(vectors);
            coefficients = List.copyOf(coefficients);

            if (vectors.size() != coefficients.size()) {
                throw new ValidationException(
                    "Vector and coefficient counts must match."
                );
            }
        }
    }

    // --------------------------------------------------
    // Basis domain
    // --------------------------------------------------

    record Basis(
        VectorSpace vectorSpace,
        List<Vector> vectors
    ) {

        Basis {
            Objects.requireNonNull(vectorSpace);
            vectors = List.copyOf(vectors);
        }
    }

    // --------------------------------------------------
    // Matrix-rank service interface
    // --------------------------------------------------

    interface RankCalculator {
        int calculate(List<Vector> vectors);
    }

    static final class GaussianEliminationRankCalculator
        implements RankCalculator {

        @Override
        public int calculate(List<Vector> vectors) {

            if (vectors.isEmpty()) {
                return 0;
            }

            int rows = vectors.get(0).dimension();
            int columns = vectors.size();

            for (Vector vector : vectors) {
                if (vector.dimension() != rows) {
                    throw new DimensionException(
                        "All vectors must have equal dimensions."
                    );
                }
            }

            // Treat each vector as one matrix column.
            double[][] matrix = new double[rows][columns];

            for (int row = 0; row < rows; row++) {
                for (int col = 0; col < columns; col++) {
                    matrix[row][col] =
                        vectors.get(col).component(row);
                }
            }

            int rank = 0;

            for (
                int col = 0;
                col < columns && rank < rows;
                col++
            ) {

                int pivot = rank;

                for (int row = rank + 1; row < rows; row++) {
                    if (
                        Math.abs(matrix[row][col]) >
                        Math.abs(matrix[pivot][col])
                    ) {
                        pivot = row;
                    }
                }

                if (Math.abs(matrix[pivot][col]) <= EPSILON) {
                    continue;
                }

                double[] temporary = matrix[rank];
                matrix[rank] = matrix[pivot];
                matrix[pivot] = temporary;

                double pivotValue = matrix[rank][col];

                for (int row = rank + 1; row < rows; row++) {
                    double factor =
                        matrix[row][col] / pivotValue;

                    for (int j = col; j < columns; j++) {
                        matrix[row][j] -=
                            factor * matrix[rank][j];
                    }
                }

                rank++;
            }

            return rank;
        }
    }

    // --------------------------------------------------
    // Enterprise vector-space service
    // --------------------------------------------------

    static final class VectorSpaceService {

        private final RankCalculator rankCalculator;

        VectorSpaceService(RankCalculator rankCalculator) {
            this.rankCalculator = Objects.requireNonNull(
                rankCalculator
            );
        }

        Vector add(
            VectorSpace space,
            Vector first,
            Vector second
        ) {
            space.validate(first);
            space.validate(second);

            return first.add(second);
        }

        Vector scale(
            VectorSpace space,
            Scalar scalar,
            Vector vector
        ) {
            space.validate(vector);

            return vector.scale(scalar.value());
        }

        Vector combine(
            VectorSpace space,
            LinearCombination combination
        ) {

            Vector result = space.zero();

            for (
                int i = 0;
                i < combination.vectors().size();
                i++
            ) {

                Vector vector = combination.vectors().get(i);
                Scalar coefficient =
                    combination.coefficients().get(i);

                space.validate(vector);

                result = result.add(
                    vector.scale(coefficient.value())
                );
            }

            return result;
        }

        int rank(List<Vector> vectors) {
            return rankCalculator.calculate(vectors);
        }

        boolean linearlyIndependent(List<Vector> vectors) {
            return rank(vectors) == vectors.size();
        }

        Optional<Basis> createBasis(
            VectorSpace space,
            List<Vector> candidates
        ) {

            for (Vector vector : candidates) {
                space.validate(vector);
            }

            if (candidates.size() != space.dimension()) {
                return Optional.empty();
            }

            if (rank(candidates) != space.dimension()) {
                return Optional.empty();
            }

            return Optional.of(
                new Basis(space, candidates)
            );
        }

        boolean isClosedUnderAddition(
            VectorSpace space,
            Vector first,
            Vector second
        ) {

            Vector result = add(space, first, second);

            return result.dimension() == space.dimension();
        }

        boolean isClosedUnderScalarMultiplication(
            VectorSpace space,
            Scalar scalar,
            Vector vector
        ) {

            Vector result = scale(space, scalar, vector);

            return result.dimension() == space.dimension();
        }
    }

    // --------------------------------------------------
    // Demonstration and validation
    // --------------------------------------------------

    public static void main(String[] args) {

        try {

            System.out.println("LINEAR ALGEBRA FOUNDATIONS");
            System.out.println("=".repeat(60));

            VectorSpace space2 = new VectorSpace(
                2,
                Field.REAL
            );

            VectorSpace space3 = new VectorSpace(
                3,
                Field.REAL
            );

            VectorSpaceService service =
                new VectorSpaceService(
                    new GaussianEliminationRankCalculator()
                );

            // 1. Scalars
            System.out.println("\n1. SCALARS");

            Scalar alpha = new Scalar(3);
            Scalar beta = new Scalar(2);

            System.out.println(
                "alpha + beta = " + alpha.add(beta).value()
            );

            System.out.println(
                "alpha * beta = " + alpha.multiply(beta).value()
            );

            // 2. Vectors
            System.out.println("\n2. VECTORS");

            Vector u = Vector.of(2, 3);
            Vector v = Vector.of(4, 1);

            System.out.println("u = " + u);
            System.out.println("v = " + v);
            System.out.println("Dimension = " + u.dimension());

            System.out.println("u + v = " + u.add(v));
            System.out.println("u - v = " + u.subtract(v));

            // 3. Scalar multiplication
            System.out.println("\n3. SCALAR MULTIPLICATION");

            System.out.println("3u = " + u.scale(3));
            System.out.println("(-2)u = " + u.scale(-2));

            // 4. Dot product and norm
            System.out.println("\n4. DOT PRODUCT AND NORM");

            System.out.println("u . v = " + u.dot(v));
            System.out.println("||u|| = " + u.norm());
            System.out.println("Normalized u = " + u.normalize());

            // 5. Vector-space identities
            System.out.println("\n5. VECTOR SPACE R^2");

            Vector zero = space2.zero();

            System.out.println("Zero vector = " + zero);
            System.out.println("u + 0 = " + u.add(zero));
            System.out.println("u + (-u) = " + u.add(u.negate()));

            System.out.println(
                "Addition closure = " +
                service.isClosedUnderAddition(space2, u, v)
            );

            System.out.println(
                "Scalar closure = " +
                service.isClosedUnderScalarMultiplication(
                    space2,
                    new Scalar(5),
                    u
                )
            );

            // 6. Linear combination
            System.out.println("\n6. LINEAR COMBINATION");

            LinearCombination combination =
                new LinearCombination(
                    List.of(u, v),
                    List.of(
                        new Scalar(2),
                        new Scalar(3)
                    )
                );

            System.out.println(
                "2u + 3v = " +
                service.combine(space2, combination)
            );

            // 7. Linear independence
            System.out.println("\n7. LINEAR INDEPENDENCE");

            Vector e1 = Vector.of(1, 0);
            Vector e2 = Vector.of(0, 1);

            List<Vector> standardBasis =
                List.of(e1, e2);

            System.out.println(
                "Rank = " + service.rank(standardBasis)
            );

            System.out.println(
                "Independent = " +
                service.linearlyIndependent(standardBasis)
            );

            // 8. Basis validation
            System.out.println("\n8. BASIS VALIDATION");

            Optional<Basis> basis =
                service.createBasis(space2, standardBasis);

            System.out.println(
                "Valid basis = " + basis.isPresent()
            );

            List<Vector> dependent = List.of(
                Vector.of(1, 2),
                Vector.of(2, 4)
            );

            System.out.println(
                "Dependent rank = " + service.rank(dependent)
            );

            System.out.println(
                "Dependent set is independent = " +
                service.linearlyIndependent(dependent)
            );

            // 9. Three-dimensional vector space
            System.out.println("\n9. VECTOR SPACE R^3");

            List<Vector> basis3 = List.of(
                Vector.of(1, 0, 0),
                Vector.of(0, 1, 0),
                Vector.of(0, 0, 1)
            );

            System.out.println(
                "R^3 basis rank = " + service.rank(basis3)
            );

            System.out.println(
                "R^3 basis valid = " +
                service.createBasis(space3, basis3).isPresent()
            );

            // 10. Failure handling
            System.out.println("\n10. VALIDATION");

            try {
                service.add(
                    space2,
                    u,
                    Vector.of(1, 2, 3)
                );
            } catch (DimensionException exception) {
                System.out.println(
                    "Dimension failure: " + exception.getMessage()
                );
            }

            try {
                zero.normalize();
            } catch (LinearAlgebraException exception) {
                System.out.println(
                    "Normalization failure: " +
                    exception.getMessage()
                );
            }

            try {
                new Scalar(Double.NaN);
            } catch (ValidationException exception) {
                System.out.println(
                    "Scalar failure: " + exception.getMessage()
                );
            }

            // 11. Assertions
            System.out.println("\n11. TESTS");

            if (!u.add(v).approximatelyEquals(Vector.of(6, 4))) {
                throw new AssertionError("Vector addition failed.");
            }

            if (u.dot(v) != 11) {
                throw new AssertionError("Dot product failed.");
            }

            if (service.rank(standardBasis) != 2) {
                throw new AssertionError("Rank calculation failed.");
            }

            if (!service.linearlyIndependent(standardBasis)) {
                throw new AssertionError(
                    "Independence test failed."
                );
            }

            if (service.linearlyIndependent(dependent)) {
                throw new AssertionError(
                    "Dependence test failed."
                );
            }

            if (!service.createBasis(space2, standardBasis).isPresent()) {
                throw new AssertionError("Basis validation failed.");
            }

            System.out.println("All tests passed.");

        } catch (Exception exception) {
            System.err.println(
                "Application failure: " + exception.getMessage()
            );

            System.exitCode = 1;
        }
    }
}
