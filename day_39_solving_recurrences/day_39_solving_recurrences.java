/*
 * Solving Recurrences
 * ====================
 *
 * Enterprise-oriented recurrence analysis engine.
 *
 * The program models a build-analysis service that uses recurrence
 * definitions to forecast computational workload. It explicitly separates
 * recurrence evaluation, characteristic-root solving, validation, and
 * policy-level reporting.
 *
 * Java 17 or later.
 */

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;


// ---------------------------------------------------------------------------
// Domain types
// ---------------------------------------------------------------------------

enum RecurrenceKind {
    FIRST_ORDER,
    SECOND_ORDER_HOMOGENEOUS,
    SECOND_ORDER_REPEATED_ROOT,
    NON_HOMOGENEOUS
}

record RecurrenceDefinition(
    String name,
    RecurrenceKind kind,
    double firstCoefficient,
    double secondCoefficient,
    double forcingTerm,
    double initial0,
    double initial1
) {
    RecurrenceDefinition {
        Objects.requireNonNull(name, "name");
        Objects.requireNonNull(kind, "kind");

        if (name.isBlank()) {
            throw new IllegalArgumentException("Name cannot be blank.");
        }
    }
}


// ---------------------------------------------------------------------------
// Immutable evaluation result
// ---------------------------------------------------------------------------

record EvaluationResult(
    RecurrenceDefinition definition,
    List<Double> values
) {
    EvaluationResult {
        Objects.requireNonNull(definition, "definition");
        Objects.requireNonNull(values, "values");
        values = Collections.unmodifiableList(new ArrayList<>(values));
    }
}


// ---------------------------------------------------------------------------
// Recurrence evaluator
// ---------------------------------------------------------------------------

final class RecurrenceEvaluator {

    private RecurrenceEvaluator() {
    }

    static EvaluationResult evaluate(
        RecurrenceDefinition definition,
        int count
    ) {
        if (count < 1) {
            throw new IllegalArgumentException(
                "At least one recurrence value is required."
            );
        }

        List<Double> values = new ArrayList<>();
        values.add(definition.initial0());

        if (count == 1) {
            return new EvaluationResult(definition, values);
        }

        values.add(definition.initial1());

        for (int n = 2; n < count; n++) {
            double previous = values.get(n - 1);
            double beforePrevious = values.get(n - 2);

            double next = switch (definition.kind()) {
                case SECOND_ORDER_HOMOGENEOUS ->
                    definition.firstCoefficient() * previous
                    + definition.secondCoefficient() * beforePrevious;

                case SECOND_ORDER_REPEATED_ROOT ->
                    definition.firstCoefficient() * previous
                    + definition.secondCoefficient() * beforePrevious;

                default -> throw new IllegalArgumentException(
                    "This evaluator requires a second-order recurrence."
                );
            };

            if (!Double.isFinite(next)) {
                throw new ArithmeticException(
                    "Recurrence produced a non-finite value at n=" + n
                );
            }

            values.add(next);
        }

        return new EvaluationResult(definition, values);
    }


    static EvaluationResult evaluateFirstOrder(
        RecurrenceDefinition definition,
        int count
    ) {
        if (count < 1) {
            throw new IllegalArgumentException(
                "Count must be positive."
            );
        }

        List<Double> values = new ArrayList<>();
        values.add(definition.initial0());

        for (int n = 1; n < count; n++) {
            double next =
                definition.firstCoefficient() * values.get(n - 1)
                + definition.forcingTerm();

            if (!Double.isFinite(next)) {
                throw new ArithmeticException(
                    "First-order recurrence overflowed at n=" + n
                );
            }

            values.add(next);
        }

        return new EvaluationResult(definition, values);
    }
}


// ---------------------------------------------------------------------------
// Characteristic equation
//
// r^2 - pr - q = 0
// ---------------------------------------------------------------------------

record CharacteristicRoots(
    double first,
    double second
) {
    boolean repeated() {
        return Double.compare(first, second) == 0;
    }
}

final class CharacteristicEquation {

    private CharacteristicEquation() {
    }

    static CharacteristicRoots solve(double p, double q) {
        double discriminant = p * p + 4.0 * q;

        if (discriminant < 0) {
            throw new IllegalArgumentException(
                "This implementation requires real characteristic roots."
            );
        }

        double squareRoot = Math.sqrt(discriminant);

        return new CharacteristicRoots(
            (p + squareRoot) / 2.0,
            (p - squareRoot) / 2.0
        );
    }
}


// ---------------------------------------------------------------------------
// Closed-form solutions
// ---------------------------------------------------------------------------

final class ClosedFormSolver {

    private ClosedFormSolver() {
    }

    static double firstOrder(
        int n,
        double a,
        double b,
        double initial
    ) {
        if (n < 0) {
            throw new IllegalArgumentException(
                "n cannot be negative."
            );
        }

        if (a == 1.0) {
            return initial + b * n;
        }

        double power = Math.pow(a, n);

        return initial * power
            + b * (power - 1.0) / (a - 1.0);
    }


    static double distinctRoots(
        int n,
        double r1,
        double r2,
        double initial0,
        double initial1
    ) {
        if (Double.compare(r1, r2) == 0) {
            throw new IllegalArgumentException(
                "Distinct-root solver received equal roots."
            );
        }

        double c1 =
            (initial1 - initial0 * r2) / (r1 - r2);

        double c2 = initial0 - c1;

        return c1 * Math.pow(r1, n)
            + c2 * Math.pow(r2, n);
    }


    static double repeatedRoot(
        int n,
        double root,
        double initial0,
        double initial1
    ) {
        if (n < 0) {
            throw new IllegalArgumentException(
                "n cannot be negative."
            );
        }

        if (root == 0.0) {
            if (n == 0) {
                return initial0;
            }

            if (n == 1) {
                return initial1;
            }

            return 0.0;
        }

        double c1 = initial0;
        double c2 = initial1 / root - c1;

        return (c1 + c2 * n) * Math.pow(root, n);
    }


    static double constantForcing(
        int n,
        double a,
        double forcing,
        double initial
    ) {
        if (a == 1.0) {
            return initial + forcing * n;
        }

        double particular = forcing / (1.0 - a);
        double homogeneousConstant = initial - particular;

        return homogeneousConstant * Math.pow(a, n)
            + particular;
    }
}


// ---------------------------------------------------------------------------
// Review-style validation service
//
// Validation here is mathematical rather than code-review related: the
// service checks whether generated recurrence values satisfy the recurrence
// definition and whether the closed form agrees with the recurrence.
// ---------------------------------------------------------------------------

record ValidationIssue(
    int n,
    double expected,
    double actual
) {}

record ValidationReport(
    boolean valid,
    List<ValidationIssue> issues
) {
    ValidationReport {
        issues = Collections.unmodifiableList(
            new ArrayList<>(issues)
        );
    }
}

final class RecurrenceValidator {

    private RecurrenceValidator() {
    }

    static ValidationReport validateSecondOrder(
        EvaluationResult result
    ) {
        RecurrenceDefinition definition =
            result.definition();

        List<Double> values = result.values();
        List<ValidationIssue> issues = new ArrayList<>();

        for (int n = 2; n < values.size(); n++) {
            double expected =
                definition.firstCoefficient()
                    * values.get(n - 1)
                + definition.secondCoefficient()
                    * values.get(n - 2);

            double actual = values.get(n);

            if (Math.abs(expected - actual) > 1e-9) {
                issues.add(
                    new ValidationIssue(n, expected, actual)
                );
            }
        }

        return new ValidationReport(
            issues.isEmpty(),
            issues
        );
    }
}


// ---------------------------------------------------------------------------
// Exact Fibonacci service
//
// BigInteger prevents the precision loss that occurs when large recurrence
// values are represented using double.
// ---------------------------------------------------------------------------

final class FibonacciService {

    private FibonacciService() {
    }

    static BigInteger iterative(int n) {
        if (n < 0) {
            throw new IllegalArgumentException(
                "n cannot be negative."
            );
        }

        BigInteger previous = BigInteger.ZERO;
        BigInteger current = BigInteger.ONE;

        for (int i = 0; i < n; i++) {
            BigInteger next = previous.add(current);
            previous = current;
            current = next;
        }

        return previous;
    }


    static BigInteger matrixPower(int n) {
        if (n < 0) {
            throw new IllegalArgumentException(
                "n cannot be negative."
            );
        }

        if (n == 0) {
            return BigInteger.ZERO;
        }

        Matrix matrix = new Matrix(
            BigInteger.ONE,
            BigInteger.ONE,
            BigInteger.ONE,
            BigInteger.ZERO
        );

        Matrix result = Matrix.identity();
        int exponent = n;

        while (exponent > 0) {
            if ((exponent & 1) == 1) {
                result = result.multiply(matrix);
            }

            matrix = matrix.multiply(matrix);
            exponent >>= 1;
        }

        return result.a01();
    }
}


// ---------------------------------------------------------------------------
// Immutable 2x2 matrix
// ---------------------------------------------------------------------------

record Matrix(
    BigInteger a00,
    BigInteger a01,
    BigInteger a10,
    BigInteger a11
) {
    static Matrix identity() {
        return new Matrix(
            BigInteger.ONE,
            BigInteger.ZERO,
            BigInteger.ZERO,
            BigInteger.ONE
        );
    }

    Matrix multiply(Matrix other) {
        return new Matrix(
            a00.multiply(other.a00())
                .add(a01.multiply(other.a10())),

            a00.multiply(other.a01())
                .add(a01.multiply(other.a11())),

            a10.multiply(other.a00())
                .add(a11.multiply(other.a10())),

            a10.multiply(other.a01())
                .add(a11.multiply(other.a11()))
        );
    }
}


// ---------------------------------------------------------------------------
// Enterprise reporting service
// ---------------------------------------------------------------------------

final class RecurrenceReportService {

    private RecurrenceReportService() {
    }

    static void print(
        EvaluationResult result
    ) {
        System.out.println(
            "\n" + result.definition().name()
        );
        System.out.println(
            "-".repeat(result.definition().name().length())
        );

        for (int n = 0; n < result.values().size(); n++) {
            System.out.printf(
                "T(%d) = %.2f%n",
                n,
                result.values().get(n)
            );
        }
    }
}


// ---------------------------------------------------------------------------
// Main enterprise scenario
// ---------------------------------------------------------------------------

public class SolvingRecurrences {

    public static void main(String[] args) {
        System.out.println(
            "RECURRENCE ANALYSIS SERVICE"
        );
        System.out.println(
            "==========================="
        );

        /*
         * Iteration case:
         *
         * T(n)=T(n-1)+n
         *
         * This models cumulative work introduced by successive processing
         * stages.
         */
        RecurrenceDefinition stagedWork =
            new RecurrenceDefinition(
                "Staged build workload",
                RecurrenceKind.SECOND_ORDER_HOMOGENEOUS,
                1.0,
                0.0,
                0.0,
                10.0,
                11.0
            );

        List<Double> stagedValues = new ArrayList<>();
        stagedValues.add(10.0);

        for (int n = 1; n <= 7; n++) {
            stagedValues.add(
                stagedValues.get(n - 1) + n
            );
        }

        System.out.println("\nIteration-derived sequence");
        System.out.println("--------------------------");

        for (int n = 0; n < stagedValues.size(); n++) {
            double closed =
                10.0 + n * (n + 1) / 2.0;

            System.out.printf(
                "T(%d) = %.2f, closed form = %.2f%n",
                n,
                stagedValues.get(n),
                closed
            );

            if (Math.abs(
                stagedValues.get(n) - closed
            ) > 1e-9) {
                throw new AssertionError(
                    "Iteration formula mismatch."
                );
            }
        }

        /*
         * First-order non-homogeneous recurrence:
         *
         * T(n)=3T(n-1)+4
         *
         * The particular constant is 4/(1-3)=-2.
         * Therefore:
         *
         * T(n)=C*3^n-2.
         */
        RecurrenceDefinition branchingWork =
            new RecurrenceDefinition(
                "Branching pipeline workload",
                RecurrenceKind.NON_HOMOGENEOUS,
                3.0,
                0.0,
                4.0,
                2.0,
                0.0
            );

        EvaluationResult branchingResult =
            RecurrenceEvaluator.evaluateFirstOrder(
                branchingWork,
                8
            );

        RecurrenceReportService.print(branchingResult);

        for (int n = 0; n < 8; n++) {
            double expected =
                ClosedFormSolver.constantForcing(
                    n,
                    3.0,
                    4.0,
                    2.0
                );

            if (Math.abs(
                branchingResult.values().get(n) - expected
            ) > 1e-9) {
                throw new AssertionError(
                    "Non-homogeneous solution mismatch."
                );
            }
        }

        /*
         * Characteristic-equation scenario:
         *
         * T(n)=5T(n-1)-6T(n-2)
         *
         * r^2-5r+6=0
         *
         * roots = 2 and 3.
         */
        RecurrenceDefinition dependencyGrowth =
            new RecurrenceDefinition(
                "Dependency growth",
                RecurrenceKind.SECOND_ORDER_HOMOGENEOUS,
                5.0,
                -6.0,
                0.0,
                1.0,
                4.0
            );

        EvaluationResult dependencyResult =
            RecurrenceEvaluator.evaluate(
                dependencyGrowth,
                9
            );

        RecurrenceReportService.print(dependencyResult);

        CharacteristicRoots roots =
            CharacteristicEquation.solve(
                5.0,
                -6.0
            );

        System.out.println(
            "\nCharacteristic roots: "
            + roots.first()
            + ", "
            + roots.second()
        );

        for (int n = 0; n < 9; n++) {
            double expected =
                ClosedFormSolver.distinctRoots(
                    n,
                    roots.first(),
                    roots.second(),
                    1.0,
                    4.0
                );

            double actual =
                dependencyResult.values().get(n);

            if (Math.abs(actual - expected) > 1e-9) {
                throw new AssertionError(
                    "Characteristic solution mismatch at n=" + n
                );
            }
        }

        ValidationReport dependencyValidation =
            RecurrenceValidator.validateSecondOrder(
                dependencyResult
            );

        System.out.println(
            "Recurrence validation: "
            + dependencyValidation.valid()
        );

        if (!dependencyValidation.valid()) {
            throw new AssertionError(
                "Valid recurrence was rejected."
            );
        }

        /*
         * Repeated root:
         *
         * T(n)=4T(n-1)-4T(n-2)
         *
         * r^2-4r+4=(r-2)^2
         *
         * The repeated-root solution is:
         *
         * (C1+C2*n)2^n
         */
        RecurrenceDefinition repeated =
            new RecurrenceDefinition(
                "Repeated dependency factor",
                RecurrenceKind.SECOND_ORDER_REPEATED_ROOT,
                4.0,
                -4.0,
                0.0,
                2.0,
                8.0
            );

        EvaluationResult repeatedResult =
            RecurrenceEvaluator.evaluate(
                repeated,
                8
            );

        RecurrenceReportService.print(repeatedResult);

        for (int n = 0; n < 8; n++) {
            double expected =
                ClosedFormSolver.repeatedRoot(
                    n,
                    2.0,
                    2.0,
                    8.0
                );

            if (Math.abs(
                repeatedResult.values().get(n) - expected
            ) > 1e-9) {
                throw new AssertionError(
                    "Repeated-root solution mismatch."
                );
            }
        }

        /*
         * Fibonacci demonstrates the distinction between an O(n) iterative
         * recurrence evaluation and O(log n) matrix exponentiation.
         *
         * BigInteger is used because Fibonacci values quickly exceed the
         * exact integer range of primitive floating-point types.
         */
        System.out.println(
            "\nExact Fibonacci computation"
        );
        System.out.println(
            "---------------------------"
        );

        BigInteger iterative =
            FibonacciService.iterative(100);

        BigInteger logarithmic =
            FibonacciService.matrixPower(100);

        System.out.println(
            "F(100) iterative:  " + iterative
        );

        System.out.println(
            "F(100) matrix:     " + logarithmic
        );

        if (!iterative.equals(logarithmic)) {
            throw new AssertionError(
                "Fibonacci algorithms disagree."
            );
        }

        /*
         * Stream processing is useful for recurrence results once the values
         * have already been generated. It does not magically change the
         * mathematical recurrence itself; it provides a declarative way to
         * filter and aggregate its evaluated states.
         */
        double average =
            dependencyResult.values()
                .stream()
                .mapToDouble(Double::doubleValue)
                .average()
                .orElseThrow();

        double maximum =
            dependencyResult.values()
                .stream()
                .mapToDouble(Double::doubleValue)
                .max()
                .orElseThrow();

        System.out.println(
            "\nDependency workload average: "
            + average
        );

        System.out.println(
            "Dependency workload maximum: "
            + maximum
        );

        System.out.println(
            "\nComplexity characteristics"
        );
        System.out.println(
            "--------------------------"
        );
        System.out.println(
            "Iterative recurrence evaluation: O(n) time."
        );
        System.out.println(
            "Memoized recurrence evaluation: O(n) distinct states."
        );
        System.out.println(
            "Characteristic closed form: O(1) per requested n, "
                + "subject to arithmetic precision."
        );
        System.out.println(
            "Matrix exponentiation: O(log n) matrix multiplications."
        );

        System.out.println(
            "\nRecurrence analysis completed successfully."
        );
    }
}
