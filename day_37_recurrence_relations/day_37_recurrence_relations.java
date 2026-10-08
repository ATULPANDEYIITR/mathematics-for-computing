import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.function.IntFunction;

/**
 * Recurrence Relations Enterprise Model
 *
 * Demonstrates linear homogeneous and non-homogeneous recurrences through
 * an enterprise demand-forecasting domain.
 *
 * Requires Java 17 or later.
 */
public class RecurrenceRelations {

    enum RecurrenceType {
        HOMOGENEOUS,
        NON_HOMOGENEOUS
    }

    record RecurrenceDefinition(
        List<Long> coefficients,
        List<Long> initialTerms,
        IntFunction<Long> forcing
    ) {
        RecurrenceDefinition {
            Objects.requireNonNull(coefficients);
            Objects.requireNonNull(initialTerms);
            Objects.requireNonNull(forcing);

            if (coefficients.isEmpty()) {
                throw new IllegalArgumentException(
                    "A recurrence must contain coefficients."
                );
            }

            if (coefficients.size() != initialTerms.size()) {
                throw new IllegalArgumentException(
                    "Initial terms must match recurrence order."
                );
            }

            coefficients = List.copyOf(coefficients);
            initialTerms = List.copyOf(initialTerms);
        }

        int order() {
            return coefficients.size();
        }

        RecurrenceType type() {
            for (int n = 0; n < 10; n++) {
                if (forcing.apply(n) != 0L) {
                    return RecurrenceType.NON_HOMOGENEOUS;
                }
            }

            return RecurrenceType.HOMOGENEOUS;
        }
    }

    static final class RecurrenceException extends RuntimeException {
        RecurrenceException(String message) {
            super(message);
        }
    }

    /**
     * Domain service responsible for evaluating recurrence definitions.
     *
     * The recurrence definition contains the mathematical rule, while the
     * service owns operational concerns such as validation and state checks.
     */
    static final class RecurrenceService {

        List<Long> generate(
            RecurrenceDefinition definition,
            int count
        ) {
            if (count < 0) {
                throw new RecurrenceException(
                    "Term count cannot be negative."
                );
            }

            List<Long> terms = new ArrayList<>(
                definition.initialTerms().subList(
                    0,
                    Math.min(
                        count,
                        definition.initialTerms().size()
                    )
                )
            );

            while (terms.size() < count) {
                int n = terms.size();

                long value = definition.forcing().apply(n);

                for (int i = 0;
                     i < definition.order();
                     i++) {

                    long coefficient =
                        definition.coefficients().get(i);

                    long previous =
                        terms.get(terms.size() - i - 1);

                    try {
                        value = Math.addExact(
                            value,
                            Math.multiplyExact(
                                coefficient,
                                previous
                            )
                        );
                    } catch (ArithmeticException overflow) {
                        throw new RecurrenceException(
                            "Long integer overflow at n=" + n
                        );
                    }
                }

                if (value < 0) {
                    throw new RecurrenceException(
                        "Domain validation rejected negative demand at n="
                            + n
                    );
                }

                terms.add(value);
            }

            return List.copyOf(terms);
        }

        boolean validate(
            RecurrenceDefinition definition,
            List<Long> observed
        ) {
            if (observed.size() < definition.order()) {
                return false;
            }

            for (int n = definition.order();
                 n < observed.size();
                 n++) {

                long expected =
                    definition.forcing().apply(n);

                for (int i = 0;
                     i < definition.order();
                     i++) {

                    expected +=
                        definition.coefficients().get(i)
                        * observed.get(n - i - 1);
                }

                if (expected != observed.get(n)) {
                    return false;
                }
            }

            return true;
        }

        long nthHomogeneousTerm(
            RecurrenceDefinition definition,
            int n
        ) {
            if (definition.type() != RecurrenceType.HOMOGENEOUS) {
                throw new RecurrenceException(
                    "Matrix-style nth-term evaluation in this service "
                        + "requires a homogeneous recurrence."
                );
            }

            if (n < 0) {
                throw new RecurrenceException(
                    "n cannot be negative."
                );
            }

            if (n < definition.order()) {
                return definition.initialTerms().get(n);
            }

            long[][] transition =
                companionMatrix(definition.coefficients());

            long[][] powered =
                matrixPower(
                    transition,
                    n - definition.order() + 1
                );

            long[][] state =
                new long[definition.order()][1];

            for (int i = 0;
                 i < definition.order();
                 i++) {
                state[i][0] =
                    definition.initialTerms().get(
                        definition.order() - 1 - i
                    );
            }

            return multiply(powered, state)[0][0];
        }
    }

    static long[][] companionMatrix(
        List<Long> coefficients
    ) {
        int order = coefficients.size();

        long[][] matrix =
            new long[order][order];

        for (int i = 0; i < order; i++) {
            matrix[0][i] = coefficients.get(i);
        }

        for (int row = 1; row < order; row++) {
            matrix[row][row - 1] = 1;
        }

        return matrix;
    }

    static long[][] identity(int size) {
        long[][] matrix =
            new long[size][size];

        for (int i = 0; i < size; i++) {
            matrix[i][i] = 1;
        }

        return matrix;
    }

    static long[][] multiply(
        long[][] a,
        long[][] b
    ) {
        if (a.length == 0 ||
            b.length == 0 ||
            a[0].length != b.length) {

            throw new IllegalArgumentException(
                "Incompatible matrix dimensions."
            );
        }

        long[][] result =
            new long[a.length][b[0].length];

        for (int i = 0; i < a.length; i++) {
            for (int k = 0; k < b.length; k++) {
                for (int j = 0; j < b[0].length; j++) {
                    result[i][j] +=
                        a[i][k] * b[k][j];
                }
            }
        }

        return result;
    }

    static long[][] matrixPower(
        long[][] base,
        int exponent
    ) {
        if (exponent < 0) {
            throw new IllegalArgumentException(
                "Matrix exponent cannot be negative."
            );
        }

        if (base.length == 0 ||
            base.length != base[0].length) {

            throw new IllegalArgumentException(
                "Matrix must be square."
            );
        }

        long[][] result =
            identity(base.length);

        long[][] current = base;

        int remaining = exponent;

        while (remaining > 0) {
            if ((remaining & 1) == 1) {
                result = multiply(result, current);
            }

            current =
                multiply(current, current);

            remaining >>= 1;
        }

        return result;
    }

    static void printTerms(
        String label,
        List<Long> terms
    ) {
        System.out.println(label + ": " + terms);
    }

    static void demandForecastScenario() {
        System.out.println(
            "\n=== Enterprise Demand Forecast ==="
        );

        RecurrenceService service =
            new RecurrenceService();

        /*
         * The recurrence models demand where each period depends on the
         * previous two periods.
         *
         * Homogeneous:
         *   D_n = D_(n-1) + D_(n-2)
         *
         * Non-homogeneous:
         *   D_n = D_(n-1) + D_(n-2) + campaign(n)
         *
         * The forcing function represents an external business effect rather
         * than another historical-demand coefficient.
         */
        RecurrenceDefinition homogeneous =
            new RecurrenceDefinition(
                List.of(1L, 1L),
                List.of(120L, 180L),
                n -> 0L
            );

        RecurrenceDefinition campaignModel =
            new RecurrenceDefinition(
                List.of(1L, 1L),
                List.of(120L, 180L),
                n -> n % 4 == 0 ? 30L : 0L
            );

        List<Long> normalDemand =
            service.generate(homogeneous, 10);

        List<Long> campaignDemand =
            service.generate(campaignModel, 10);

        printTerms(
            "Homogeneous demand",
            normalDemand
        );

        printTerms(
            "Campaign-adjusted demand",
            campaignDemand
        );

        System.out.println(
            "Homogeneous type: "
                + homogeneous.type()
        );

        System.out.println(
            "Campaign model type: "
                + campaignModel.type()
        );

        System.out.println(
            "Normal sequence valid: "
                + service.validate(
                    homogeneous,
                    normalDemand
                )
        );

        System.out.println(
            "Campaign sequence valid: "
                + service.validate(
                    campaignModel,
                    campaignDemand
                )
        );

        List<Long> corrupted =
            new ArrayList<>(campaignDemand);

        corrupted.set(
            6,
            corrupted.get(6) + 100
        );

        System.out.println(
            "Corrupted campaign sequence valid: "
                + service.validate(
                    campaignModel,
                    corrupted
                )
        );
    }

    static void characteristicEquationScenario() {
        System.out.println(
            "\n=== Characteristic Equation ==="
        );

        /*
         * For
         *
         *   a_n = 3a_(n-1) - 2a_(n-2)
         *
         * assume a_n = r^n:
         *
         *   r^2 = 3r - 2
         *
         * so
         *
         *   r^2 - 3r + 2 = 0
         *
         * and
         *
         *   (r - 1)(r - 2) = 0.
         *
         * The roots are therefore 1 and 2.
         */
        RecurrenceDefinition definition =
            new RecurrenceDefinition(
                List.of(3L, -2L),
                List.of(1L, 3L),
                n -> 0L
            );

        RecurrenceService service =
            new RecurrenceService();

        printTerms(
            "Direct evaluation",
            service.generate(definition, 8)
        );

        for (int n : List.of(10, 20, 30)) {
            System.out.println(
                "a_" + n + " via matrix exponentiation = "
                    + service.nthHomogeneousTerm(
                        definition,
                        n
                    )
            );
        }
    }

    static void recurrencePolicyScenario() {
        System.out.println(
            "\n=== Model Policy Validation ==="
        );

        RecurrenceService service =
            new RecurrenceService();

        RecurrenceDefinition model =
            new RecurrenceDefinition(
                List.of(2L),
                List.of(100L),
                n -> n % 3 == 0 ? 25L : -10L
            );

        List<Long> forecast =
            service.generate(model, 8);

        printTerms(
            "Operational forecast",
            forecast
        );

        System.out.println(
            "Forecast satisfies model: "
                + service.validate(
                    model,
                    forecast
                )
        );
    }

    static void failureScenarios() {
        System.out.println(
            "\n=== Failure Scenarios ==="
        );

        RecurrenceService service =
            new RecurrenceService();

        try {
            service.generate(
                new RecurrenceDefinition(
                    List.of(1L, 1L),
                    List.of(1L),
                    n -> 0L
                ),
                5
            );
        } catch (Exception exception) {
            System.out.println(
                "Invalid definition rejected: "
                    + exception.getMessage()
            );
        }

        try {
            service.generate(
                new RecurrenceDefinition(
                    List.of(Long.MAX_VALUE),
                    List.of(Long.MAX_VALUE),
                    n -> 0L
                ),
                4
            );
        } catch (Exception exception) {
            System.out.println(
                "Overflow or invalid state rejected: "
                    + exception.getMessage()
            );
        }
    }

    public static void main(String[] args) {
        System.out.println(
            "RECURRENCE RELATIONS ENTERPRISE LABORATORY"
        );

        demandForecastScenario();
        characteristicEquationScenario();
        recurrencePolicyScenario();
        failureScenarios();

        System.out.println(
            "\nThe implementation separates recurrence definitions, "
                + "forcing functions, evaluation strategies, validation, "
                + "and domain-level failure handling."
        );
    }
}
