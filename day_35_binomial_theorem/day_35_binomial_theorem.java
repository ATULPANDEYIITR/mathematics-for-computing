import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumSet;
import java.util.List;
import java.util.Objects;

/**
 * Binomial Theorem Enterprise Domain Model.
 *
 * The program models a symbolic expansion service with explicit domain types
 * for finite expansions, generalized series, validation policies, and
 * calculation states.
 *
 * Java 17+.
 */
public class BinomialTheoremEnterprise {

    private static final MathContext MC =
            new MathContext(40, RoundingMode.HALF_EVEN);

    // -------------------------------------------------------------------------
    // Domain state
    // -------------------------------------------------------------------------

    enum CalculationMode {
        FINITE_EXACT,
        GENERALIZED_APPROXIMATION
    }

    enum RequestState {
        RECEIVED,
        VALIDATED,
        PROCESSED,
        REJECTED
    }

    enum ValidationRule {
        NON_NEGATIVE_EXPONENT,
        INTEGER_FINITE_COEFFICIENTS,
        SERIES_CONVERGENCE_DOMAIN,
        TERM_LIMIT
    }

    record ExpansionRequest(
            int exponent,
            BigDecimal a,
            BigDecimal b,
            CalculationMode mode,
            int seriesTerms
    ) {
        ExpansionRequest {
            Objects.requireNonNull(a, "a");
            Objects.requireNonNull(b, "b");
            Objects.requireNonNull(mode, "mode");
        }
    }

    record ExpansionTerm(
            int power,
            BigIntegerLike coefficient
    ) {}

    /*
     * A small exact-integer wrapper keeps the domain model explicit.
     * Java's BigInteger is used for arbitrary-size finite coefficients.
     */
    record BigIntegerLike(java.math.BigInteger value) {
        BigIntegerLike {
            Objects.requireNonNull(value, "value");
        }

        @Override
        public String toString() {
            return value.toString();
        }
    }

    record ValidationResult(
            boolean valid,
            List<String> failures
    ) {
        ValidationResult {
            failures = List.copyOf(failures);
        }
    }

    record ServiceResult(
            RequestState state,
            String message
    ) {}

    // -------------------------------------------------------------------------
    // Validation policy
    // -------------------------------------------------------------------------

    static final class ExpansionPolicy {
        private final EnumSet<ValidationRule> rules;
        private final int maximumExponent;
        private final int maximumSeriesTerms;

        ExpansionPolicy(
                EnumSet<ValidationRule> rules,
                int maximumExponent,
                int maximumSeriesTerms
        ) {
            this.rules = EnumSet.copyOf(rules);
            this.maximumExponent = maximumExponent;
            this.maximumSeriesTerms = maximumSeriesTerms;
        }

        ValidationResult validate(ExpansionRequest request) {
            List<String> failures = new ArrayList<>();

            if (rules.contains(ValidationRule.NON_NEGATIVE_EXPONENT)
                    && request.exponent() < 0) {
                failures.add("finite exponent must be non-negative");
            }

            if (request.exponent() > maximumExponent) {
                failures.add(
                        "exponent exceeds policy limit of "
                                + maximumExponent
                );
            }

            if (request.mode() == CalculationMode.FINITE_EXACT
                    && rules.contains(
                            ValidationRule.INTEGER_FINITE_COEFFICIENTS
                    )) {
                if (!isInteger(request.a())
                        || !isInteger(request.b())) {
                    failures.add(
                            "exact finite mode requires integral a and b"
                    );
                }
            }

            if (request.mode()
                    == CalculationMode.GENERALIZED_APPROXIMATION) {

                if (rules.contains(ValidationRule.TERM_LIMIT)
                        && (request.seriesTerms() <= 0
                        || request.seriesTerms() > maximumSeriesTerms)) {
                    failures.add(
                            "series term count must be between 1 and "
                                    + maximumSeriesTerms
                    );
                }

                if (rules.contains(
                        ValidationRule.SERIES_CONVERGENCE_DOMAIN)) {

                    boolean integerExponent =
                            request.a().stripTrailingZeros()
                                    .scale() <= 0;

                    if (!integerExponent
                            && request.b().abs()
                            .compareTo(BigDecimal.ONE) >= 0) {
                        failures.add(
                                "generalized expansion requires |b| < 1 "
                                        + "for the normalized series"
                        );
                    }
                }
            }

            return new ValidationResult(
                    failures.isEmpty(),
                    failures
            );
        }

        private static boolean isInteger(BigDecimal value) {
            return value.stripTrailingZeros().scale() <= 0;
        }
    }

    // -------------------------------------------------------------------------
    // Exact binomial service
    // -------------------------------------------------------------------------

    static final class ExactBinomialService {

        java.math.BigInteger coefficient(int n, int k) {
            if (n < 0 || k < 0) {
                throw new IllegalArgumentException(
                        "n and k must be non-negative"
                );
            }

            if (k > n) {
                return java.math.BigInteger.ZERO;
            }

            k = Math.min(k, n - k);

            java.math.BigInteger result =
                    java.math.BigInteger.ONE;

            for (int i = 1; i <= k; i++) {
                result = result
                        .multiply(
                                java.math.BigInteger.valueOf(
                                        n - i + 1L
                                )
                        )
                        .divide(
                                java.math.BigInteger.valueOf(i)
                        );
            }

            return result;
        }

        List<ExpansionTerm> expand(
                int n,
                java.math.BigInteger a,
                java.math.BigInteger b
        ) {
            List<ExpansionTerm> terms = new ArrayList<>();

            for (int k = 0; k <= n; k++) {
                java.math.BigInteger value =
                        coefficient(n, k)
                                .multiply(
                                        a.pow(n - k)
                                )
                                .multiply(
                                        b.pow(k)
                                );

                terms.add(
                        new ExpansionTerm(
                                k,
                                new BigIntegerLike(value)
                        )
                );
            }

            return List.copyOf(terms);
        }

        java.math.BigInteger coefficientOfX(
                int n,
                int k,
                java.math.BigInteger a,
                java.math.BigInteger b
        ) {
            if (k < 0 || k > n) {
                return java.math.BigInteger.ZERO;
            }

            return coefficient(n, k)
                    .multiply(a.pow(n - k))
                    .multiply(b.pow(k));
        }
    }

    // -------------------------------------------------------------------------
    // Generalized binomial service
    // -------------------------------------------------------------------------

    static final class GeneralizedBinomialService {

        BigDecimal generalizedCoefficient(
                BigDecimal alpha,
                int k
        ) {
            if (k < 0) {
                throw new IllegalArgumentException(
                        "k must be non-negative"
                );
            }

            BigDecimal coefficient = BigDecimal.ONE;

            for (int j = 0; j < k; j++) {
                BigDecimal numerator =
                        alpha.subtract(
                                BigDecimal.valueOf(j),
                                MC
                        );

                coefficient = coefficient
                        .multiply(numerator, MC)
                        .divide(
                                BigDecimal.valueOf(j + 1L),
                                MC
                        );
            }

            return coefficient;
        }

        BigDecimal approximate(
                BigDecimal alpha,
                BigDecimal x,
                int terms
        ) {
            if (terms <= 0) {
                throw new IllegalArgumentException(
                        "terms must be positive"
                );
            }

            if (x.abs().compareTo(BigDecimal.ONE) >= 0) {
                throw new IllegalArgumentException(
                        "the generalized series requires |x| < 1"
                );
            }

            BigDecimal coefficient = BigDecimal.ONE;
            BigDecimal power = BigDecimal.ONE;
            BigDecimal total = BigDecimal.ONE;

            for (int k = 1; k < terms; k++) {
                coefficient = coefficient
                        .multiply(
                                alpha.subtract(
                                        BigDecimal.valueOf(k - 1L),
                                        MC
                                ),
                                MC
                        )
                        .divide(
                                BigDecimal.valueOf(k),
                                MC
                        );

                power = power.multiply(x, MC);
                total = total.add(
                        coefficient.multiply(power, MC),
                        MC
                );
            }

            return total;
        }
    }

    // -------------------------------------------------------------------------
    // Identity service
    // -------------------------------------------------------------------------

    static final class BinomialIdentityService {
        private final ExactBinomialService binomial;

        BinomialIdentityService(ExactBinomialService binomial) {
            this.binomial = binomial;
        }

        boolean pascal(int n, int k) {
            if (n <= 0 || k < 0 || k > n) {
                throw new IllegalArgumentException(
                        "invalid Pascal parameters"
                );
            }

            return binomial.coefficient(n, k).equals(
                    binomial.coefficient(n - 1, k - 1)
                            .add(
                                    binomial.coefficient(n - 1, k)
                            )
            );
        }

        boolean symmetry(int n, int k) {
            if (k < 0 || k > n) {
                throw new IllegalArgumentException(
                        "invalid symmetry parameters"
                );
            }

            return binomial.coefficient(n, k).equals(
                    binomial.coefficient(n, n - k)
            );
        }

        boolean hockeyStick(int n, int k) {
            if (k < 0 || k > n) {
                throw new IllegalArgumentException(
                        "require n >= k >= 0"
                );
            }

            java.math.BigInteger left =
                    java.math.BigInteger.ZERO;

            for (int row = k; row <= n; row++) {
                left = left.add(
                        binomial.coefficient(row, k)
                );
            }

            return left.equals(
                    binomial.coefficient(n + 1, k + 1)
            );
        }

        boolean vandermonde(int r, int s, int n) {
            java.math.BigInteger left =
                    java.math.BigInteger.ZERO;

            for (int k = 0; k <= n; k++) {
                if (k <= r && n - k <= s) {
                    left = left.add(
                            binomial.coefficient(r, k)
                                    .multiply(
                                            binomial.coefficient(
                                                    s,
                                                    n - k
                                            )
                                    )
                    );
                }
            }

            return left.equals(
                    binomial.coefficient(r + s, n)
            );
        }
    }

    // -------------------------------------------------------------------------
    // Stateful enterprise service
    // -------------------------------------------------------------------------

    static final class ExpansionWorkflow {
        private final ExpansionPolicy policy;
        private final ExactBinomialService exactService;
        private final GeneralizedBinomialService generalizedService;

        private RequestState state = RequestState.RECEIVED;

        ExpansionWorkflow(
                ExpansionPolicy policy,
                ExactBinomialService exactService,
                GeneralizedBinomialService generalizedService
        ) {
            this.policy = policy;
            this.exactService = exactService;
            this.generalizedService = generalizedService;
        }

        ServiceResult process(ExpansionRequest request) {
            if (state == RequestState.PROCESSED) {
                throw new IllegalStateException(
                        "workflow cannot process the same request twice"
                );
            }

            ValidationResult validation =
                    policy.validate(request);

            if (!validation.valid()) {
                state = RequestState.REJECTED;

                return new ServiceResult(
                        state,
                        String.join("; ", validation.failures())
                );
            }

            state = RequestState.VALIDATED;

            if (request.mode() == CalculationMode.FINITE_EXACT) {
                java.math.BigInteger a =
                        request.a().toBigIntegerExact();

                java.math.BigInteger b =
                        request.b().toBigIntegerExact();

                List<ExpansionTerm> terms =
                        exactService.expand(
                                request.exponent(),
                                a,
                                b
                        );

                state = RequestState.PROCESSED;

                return new ServiceResult(
                        state,
                        formatTerms(terms)
                );
            }

            BigDecimal approximation =
                    generalizedService.approximate(
                            request.a(),
                            request.b(),
                            request.seriesTerms()
                    );

            state = RequestState.PROCESSED;

            return new ServiceResult(
                    state,
                    "generalized approximation = "
                            + approximation.toPlainString()
            );
        }

        private static String formatTerms(
                List<ExpansionTerm> terms
        ) {
            List<String> formatted = new ArrayList<>();

            for (ExpansionTerm term : terms) {
                formatted.add(
                        term.coefficient()
                                + "x^"
                                + term.power()
                );
            }

            return String.join(" + ", formatted);
        }
    }

    // -------------------------------------------------------------------------
    // Application entry point
    // -------------------------------------------------------------------------

    public static void main(String[] args) {
        ExactBinomialService exactService =
                new ExactBinomialService();

        GeneralizedBinomialService generalizedService =
                new GeneralizedBinomialService();

        BinomialIdentityService identityService =
                new BinomialIdentityService(exactService);

        ExpansionPolicy policy =
                new ExpansionPolicy(
                        EnumSet.of(
                                ValidationRule.NON_NEGATIVE_EXPONENT,
                                ValidationRule.INTEGER_FINITE_COEFFICIENTS,
                                ValidationRule.SERIES_CONVERGENCE_DOMAIN,
                                ValidationRule.TERM_LIMIT
                        ),
                        5000,
                        500
                );

        System.out.println("=".repeat(72));
        System.out.println(
                "BINOMIAL THEOREM - JAVA ENTERPRISE DOMAIN MODEL"
        );
        System.out.println("=".repeat(72));

        System.out.println("\nFinite expansion");

        List<ExpansionTerm> terms =
                exactService.expand(
                        5,
                        java.math.BigInteger.ONE,
                        java.math.BigInteger.ONE
                );

        System.out.println(formatTerms(terms));

        System.out.println("\nScaled expansion");

        terms = exactService.expand(
                4,
                java.math.BigInteger.valueOf(2),
                java.math.BigInteger.valueOf(3)
        );

        System.out.println(formatTerms(terms));

        System.out.println("\nCoefficient extraction");

        System.out.println(
                "[x^4](1+x)^10 = "
                        + exactService.coefficientOfX(
                                10,
                                4,
                                java.math.BigInteger.ONE,
                                java.math.BigInteger.ONE
                        )
        );

        System.out.println(
                "[x^3](2+5x)^7 = "
                        + exactService.coefficientOfX(
                                7,
                                3,
                                java.math.BigInteger.valueOf(2),
                                java.math.BigInteger.valueOf(5)
                        )
        );

        System.out.println("\nIdentity service");

        System.out.println(
                "Pascal = "
                        + identityService.pascal(15, 6)
        );

        System.out.println(
                "Symmetry = "
                        + identityService.symmetry(15, 6)
        );

        System.out.println(
                "Hockey-stick = "
                        + identityService.hockeyStick(15, 6)
        );

        System.out.println(
                "Vandermonde = "
                        + identityService.vandermonde(8, 7, 6)
        );

        System.out.println("\nGeneralized expansion");

        BigDecimal approximation =
                generalizedService.approximate(
                        new BigDecimal("0.5"),
                        new BigDecimal("0.25"),
                        30
                );

        System.out.println(
                "(1.25)^(1/2) ≈ "
                        + approximation
                );

        System.out.println(
                "Reference ≈ "
                        + new BigDecimal(
                                Math.sqrt(1.25),
                                MC
                        )
        );

        System.out.println("\nWorkflow service");

        ExpansionWorkflow exactWorkflow =
                new ExpansionWorkflow(
                        policy,
                        exactService,
                        generalizedService
                );

        ServiceResult result =
                exactWorkflow.process(
                        new ExpansionRequest(
                                6,
                                new BigDecimal("2"),
                                new BigDecimal("3"),
                                CalculationMode.FINITE_EXACT,
                                0
                        )
                );

        System.out.println(
                result.state() + ": " + result.message()
        );

        System.out.println("\nPolicy rejection");

        ExpansionWorkflow invalidWorkflow =
                new ExpansionWorkflow(
                        policy,
                        exactService,
                        generalizedService
                );

        ServiceResult rejected =
                invalidWorkflow.process(
                        new ExpansionRequest(
                                5,
                                new BigDecimal("2.5"),
                                new BigDecimal("3"),
                                CalculationMode.FINITE_EXACT,
                                0
                        )
                );

        System.out.println(
                rejected.state() + ": " + rejected.message()
        );

        System.out.println("\nGeneralized-series workflow");

        ExpansionWorkflow generalizedWorkflow =
                new ExpansionWorkflow(
                        policy,
                        exactService,
                        generalizedService
                );

        ServiceResult generalizedResult =
                generalizedWorkflow.process(
                        new ExpansionRequest(
                                0,
                                new BigDecimal("0.5"),
                                new BigDecimal("0.25"),
                                CalculationMode.GENERALIZED_APPROXIMATION,
                                25
                        )
                );

        System.out.println(
                generalizedResult.state()
                        + ": "
                        + generalizedResult.message()
        );

        System.out.println("\nEdge cases");

        System.out.println(
                "C(10,20) = "
                        + exactService.coefficientOfX(
                                10,
                                20,
                                java.math.BigInteger.ONE,
                                java.math.BigInteger.ONE
                        )
        );

        System.out.println(
                "C(0,0) = "
                        + exactService.coefficientOfX(
                                0,
                                0,
                                java.math.BigInteger.ONE,
                                java.math.BigInteger.ONE
                        )
        );

        try {
            generalizedService.approximate(
                    new BigDecimal("0.5"),
                    new BigDecimal("1.2"),
                    20
            );
        } catch (IllegalArgumentException exception) {
            System.out.println(
                    "Rejected divergent generalized series: "
                            + exception.getMessage()
            );
        }

        System.out.println("\nDomain design observations");
        System.out.println(
                "BigInteger keeps finite coefficients exact even when "
                        + "they exceed primitive integer ranges."
        );
        System.out.println(
                "ExpansionPolicy separates validation rules from the "
                        + "workflow that executes a request."
        );
        System.out.println(
                "ExpansionWorkflow explicitly models RECEIVED, VALIDATED, "
                        + "PROCESSED, and REJECTED states."
        );
        System.out.println(
                "Generalized real-valued expansion uses BigDecimal with "
                        + "a defined MathContext instead of pretending that "
                        + "finite binary floating-point arithmetic is exact."
        );
    }

    private static String formatTerms(
            List<ExpansionTerm> terms
    ) {
        List<String> values = new ArrayList<>();

        for (ExpansionTerm term : terms) {
            values.add(
                    term.coefficient()
                            + "x^"
                            + term.power()
            );
        }

        return String.join(" + ", values);
    }
}
