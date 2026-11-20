import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.LinkedHashMap;

/*
 * HYPOTHESIS TESTING
 *
 * Enterprise statistical experiment management.
 *
 * Implements:
 * - Immutable hypothesis definitions
 * - One-sample Z-tests
 * - Null and alternative hypotheses
 * - P-value calculation
 * - Significance decisions
 * - Confidence intervals
 * - Bonferroni multiple-testing correction
 * - Experiment lifecycle management
 * - Audit events
 * - Validation and domain exceptions
 *
 * Java 17, standard library only.
 */

public class HypothesisTesting {

    enum Alternative {
        TWO_SIDED,
        GREATER,
        LESS
    }

    enum Decision {
        REJECT_NULL,
        FAIL_TO_REJECT
    }

    enum ExperimentStatus {
        CREATED,
        RUNNING,
        COMPLETED,
        FAILED
    }

    static class StatisticalException extends RuntimeException {
        StatisticalException(String message) {
            super(message);
        }
    }

    record Hypothesis(
        double nullMean,
        double alpha,
        Alternative alternative
    ) {
        Hypothesis {
            if (!Double.isFinite(nullMean)) {
                throw new StatisticalException(
                    "Null mean must be finite."
                );
            }

            if (
                !Double.isFinite(alpha) ||
                alpha <= 0 ||
                alpha >= 1
            ) {
                throw new StatisticalException(
                    "Alpha must be between 0 and 1."
                );
            }

            Objects.requireNonNull(
                alternative,
                "Alternative hypothesis is required."
            );
        }
    }

    record ConfidenceInterval(
        double lower,
        double upper
    ) {
        ConfidenceInterval {
            if (lower > upper) {
                throw new StatisticalException(
                    "Invalid confidence interval."
                );
            }
        }
    }

    record TestResult(
        int sampleSize,
        double sampleMean,
        double standardError,
        double zStatistic,
        double pValue,
        double alpha,
        ConfidenceInterval confidenceInterval,
        Decision decision,
        Alternative alternative
    ) {}

    record AuditEvent(
        String experimentId,
        String event,
        String detail
    ) {}

    interface StatisticalTest {
        TestResult execute(
            List<Double> observations,
            Hypothesis hypothesis,
            double populationSigma
        );
    }

    static final class NormalDistribution {

        private NormalDistribution() {}

        static double cdf(double z) {
            return 0.5 * erfc(-z / Math.sqrt(2.0));
        }

        static double survival(double z) {
            return 0.5 * erfc(z / Math.sqrt(2.0));
        }

        /*
         * Numerical approximation of complementary error function.
         */
        private static double erfc(double x) {
            double z = Math.abs(x);
            double t = 1.0 / (1.0 + 0.5 * z);

            double answer = t * Math.exp(
                -z * z - 1.26551223
                + t * (
                    1.00002368
                    + t * (
                        0.37409196
                        + t * (
                            0.09678418
                            + t * (
                                -0.18628806
                                + t * (
                                    0.27886807
                                    + t * (
                                        -1.13520398
                                        + t * (
                                            1.48851587
                                            + t * (
                                                -0.82215223
                                                + t * 0.17087277
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            );

            return x >= 0 ? answer : 2.0 - answer;
        }

        static double criticalZ(double alpha) {
            double low = 0;
            double high = 10;
            double target = alpha / 2;

            for (int i = 0; i < 100; i++) {
                double mid = (low + high) / 2;

                if (survival(mid) > target) {
                    low = mid;
                } else {
                    high = mid;
                }
            }

            return (low + high) / 2;
        }
    }

    static final class OneSampleZTest implements StatisticalTest {

        @Override
        public TestResult execute(
            List<Double> observations,
            Hypothesis hypothesis,
            double populationSigma
        ) {
            Objects.requireNonNull(
                observations,
                "Observations cannot be null."
            );

            Objects.requireNonNull(
                hypothesis,
                "Hypothesis cannot be null."
            );

            if (observations.size() < 2) {
                throw new StatisticalException(
                    "At least two observations are required."
                );
            }

            if (
                !Double.isFinite(populationSigma) ||
                populationSigma <= 0
            ) {
                throw new StatisticalException(
                    "Population sigma must be positive."
                );
            }

            double sum = 0;

            for (double observation : observations) {
                if (!Double.isFinite(observation)) {
                    throw new StatisticalException(
                        "Observations must be finite."
                    );
                }

                sum += observation;
            }

            int n = observations.size();

            double mean = sum / n;

            double standardError =
                populationSigma / Math.sqrt(n);

            double z = (
                mean - hypothesis.nullMean()
            ) / standardError;

            double p = calculatePValue(
                z,
                hypothesis.alternative()
            );

            Decision decision = p <= hypothesis.alpha()
                ? Decision.REJECT_NULL
                : Decision.FAIL_TO_REJECT;

            double critical =
                NormalDistribution.criticalZ(
                    hypothesis.alpha()
                );

            double margin = critical * standardError;

            ConfidenceInterval interval =
                new ConfidenceInterval(
                    mean - margin,
                    mean + margin
                );

            return new TestResult(
                n,
                mean,
                standardError,
                z,
                p,
                hypothesis.alpha(),
                interval,
                decision,
                hypothesis.alternative()
            );
        }

        private double calculatePValue(
            double z,
            Alternative alternative
        ) {
            return switch (alternative) {
                case TWO_SIDED ->
                    Math.min(
                        1,
                        2 * NormalDistribution.survival(
                            Math.abs(z)
                        )
                    );

                case GREATER ->
                    NormalDistribution.survival(z);

                case LESS ->
                    NormalDistribution.cdf(z);
            };
        }
    }

    record MultipleTestResult(
        int testNumber,
        double originalPValue,
        double adjustedPValue,
        double threshold,
        boolean significant
    ) {}

    static final class MultipleTestingService {

        List<MultipleTestResult> bonferroni(
            List<Double> pValues,
            double alpha
        ) {
            if (pValues == null || pValues.isEmpty()) {
                throw new StatisticalException(
                    "P-values are required."
                );
            }

            if (
                !Double.isFinite(alpha) ||
                alpha <= 0 ||
                alpha >= 1
            ) {
                throw new StatisticalException(
                    "Invalid significance level."
                );
            }

            double threshold = alpha / pValues.size();

            List<MultipleTestResult> results =
                new ArrayList<>();

            for (int i = 0; i < pValues.size(); i++) {
                double p = pValues.get(i);

                if (!Double.isFinite(p) || p < 0 || p > 1) {
                    throw new StatisticalException(
                        "Invalid p-value."
                    );
                }

                results.add(
                    new MultipleTestResult(
                        i + 1,
                        p,
                        Math.min(1, p * pValues.size()),
                        threshold,
                        p <= threshold
                    )
                );
            }

            return List.copyOf(results);
        }
    }

    static final class Experiment {

        private final String id;
        private final Hypothesis hypothesis;
        private final List<Double> observations;
        private final double sigma;
        private final StatisticalTest test;

        private ExperimentStatus status;
        private TestResult result;
        private String failureReason;

        Experiment(
            String id,
            Hypothesis hypothesis,
            List<Double> observations,
            double sigma,
            StatisticalTest test
        ) {
            if (id == null || id.isBlank()) {
                throw new StatisticalException(
                    "Experiment ID is required."
                );
            }

            this.id = id;
            this.hypothesis = Objects.requireNonNull(hypothesis);
            this.observations = List.copyOf(observations);
            this.sigma = sigma;
            this.test = Objects.requireNonNull(test);
            this.status = ExperimentStatus.CREATED;
        }

        synchronized TestResult execute() {
            if (status != ExperimentStatus.CREATED) {
                throw new StatisticalException(
                    "Experiment cannot execute from state " + status
                );
            }

            status = ExperimentStatus.RUNNING;

            try {
                result = test.execute(
                    observations,
                    hypothesis,
                    sigma
                );

                status = ExperimentStatus.COMPLETED;

                return result;

            } catch (RuntimeException exception) {
                status = ExperimentStatus.FAILED;
                failureReason = exception.getMessage();
                throw exception;
            }
        }

        String id() {
            return id;
        }

        ExperimentStatus status() {
            return status;
        }

        TestResult result() {
            return result;
        }

        String failureReason() {
            return failureReason;
        }
    }

    static final class ExperimentService {

        private final Map<String, Experiment> experiments =
            new LinkedHashMap<>();

        private final List<AuditEvent> auditEvents =
            new ArrayList<>();

        synchronized void register(Experiment experiment) {
            Objects.requireNonNull(experiment);

            if (experiments.containsKey(experiment.id())) {
                throw new StatisticalException(
                    "Duplicate experiment ID."
                );
            }

            experiments.put(experiment.id(), experiment);

            auditEvents.add(
                new AuditEvent(
                    experiment.id(),
                    "REGISTERED",
                    "Experiment registered."
                )
            );
        }

        synchronized TestResult execute(String id) {
            Experiment experiment = experiments.get(id);

            if (experiment == null) {
                throw new StatisticalException(
                    "Experiment not found: " + id
                );
            }

            auditEvents.add(
                new AuditEvent(
                    id,
                    "EXECUTION_STARTED",
                    "Statistical evaluation started."
                )
            );

            try {
                TestResult result = experiment.execute();

                auditEvents.add(
                    new AuditEvent(
                        id,
                        "EXECUTION_COMPLETED",
                        result.decision().toString()
                    )
                );

                return result;

            } catch (RuntimeException exception) {
                auditEvents.add(
                    new AuditEvent(
                        id,
                        "EXECUTION_FAILED",
                        exception.getMessage()
                    )
                );

                throw exception;
            }
        }

        List<AuditEvent> auditTrail() {
            return List.copyOf(auditEvents);
        }

        List<Experiment> allExperiments() {
            return List.copyOf(experiments.values());
        }
    }

    private static void printResult(TestResult result) {
        System.out.println("\nHYPOTHESIS TEST RESULTS");
        System.out.println("------------------------------------");

        System.out.printf(
            "Sample size: %d%n",
            result.sampleSize()
        );

        System.out.printf(
            "Sample mean: %.4f%n",
            result.sampleMean()
        );

        System.out.printf(
            "Standard error: %.4f%n",
            result.standardError()
        );

        System.out.printf(
            "Z statistic: %.4f%n",
            result.zStatistic()
        );

        System.out.printf(
            "P-value: %.8f%n",
            result.pValue()
        );

        System.out.printf(
            "Alpha: %.4f%n",
            result.alpha()
        );

        System.out.printf(
            "Confidence interval: [%.4f, %.4f]%n",
            result.confidenceInterval().lower(),
            result.confidenceInterval().upper()
        );

        System.out.println(
            "Decision: " + result.decision()
        );
    }

    private static void validate() {
        if (Math.abs(NormalDistribution.cdf(0) - 0.5) > 1e-6) {
            throw new AssertionError("Normal CDF test failed.");
        }

        if (
            NormalDistribution.survival(2) >= 0.03
        ) {
            throw new AssertionError("Tail probability test failed.");
        }

        List<MultipleTestResult> corrected =
            new MultipleTestingService().bonferroni(
                List.of(0.001, 0.018, 0.032),
                0.05
            );

        if (!corrected.get(0).significant()) {
            throw new AssertionError(
                "Bonferroni validation failed."
            );
        }

        if (corrected.get(1).significant()) {
            throw new AssertionError(
                "Unexpected adjusted significance."
            );
        }

        System.out.println("All validation tests passed.");
    }

    public static void main(String[] args) {
        validate();

        Hypothesis hypothesis = new Hypothesis(
            100.0,
            0.05,
            Alternative.TWO_SIDED
        );

        List<Double> productionData = List.of(
            104.0, 108.0, 102.0, 107.0, 105.0,
            110.0, 106.0, 103.0, 109.0, 107.0,
            105.0, 108.0, 111.0, 104.0, 106.0,
            109.0, 107.0, 105.0, 110.0, 108.0
        );

        Experiment experiment = new Experiment(
            "QUALITY-001",
            hypothesis,
            productionData,
            8.0,
            new OneSampleZTest()
        );

        ExperimentService service = new ExperimentService();

        service.register(experiment);

        TestResult result = service.execute("QUALITY-001");

        printResult(result);

        System.out.println("\nMULTIPLE HYPOTHESIS TESTING");

        List<MultipleTestResult> adjusted =
            new MultipleTestingService().bonferroni(
                List.of(0.001, 0.018, 0.032, 0.12, 0.40),
                0.05
            );

        adjusted.forEach(item -> System.out.printf(
            "Test %d | Original p=%.4f | Adjusted p=%.4f | Significant=%s%n",
            item.testNumber(),
            item.originalPValue(),
            item.adjustedPValue(),
            item.significant()
        ));

        System.out.println("\nAUDIT TRAIL");

        service.auditTrail().forEach(System.out::println);
    }
}
