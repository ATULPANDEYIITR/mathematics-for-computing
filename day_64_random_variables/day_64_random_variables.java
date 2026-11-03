import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.random.RandomGenerator;
import java.util.Random;
import java.time.Instant;

/*
 * Random Variables: Enterprise Probability Assessment
 *
 * Java 17 implementation featuring:
 * - Discrete and continuous random-variable interfaces.
 * - Immutable distribution support and probability policies.
 * - Binomial, normal, and uniform distributions.
 * - Probability-density, probability-mass, and cumulative functions.
 * - Enterprise risk evaluation with multiple policy constraints.
 * - Explicit assessment states and online monitoring.
 *
 * Compile: javac Main.java
 * Run:     java Main
 */

class DistributionValidationException extends IllegalArgumentException {
    public DistributionValidationException(String message) {
        super(message);
    }
}

class AssessmentException extends IllegalStateException {
    public AssessmentException(String message) {
        super(message);
    }
}

interface RandomVariable {
    double cdf(double x);

    double mean();

    double variance();

    double sample(RandomGenerator random);
}

interface DiscreteVariable extends RandomVariable {
    double pmf(double x);
}

interface ContinuousVariable extends RandomVariable {
    double pdf(double x);
}

record Outcome(double value, double probability) {
    Outcome {
        if (!Double.isFinite(value)) {
            throw new DistributionValidationException(
                "Discrete support values must be finite."
            );
        }

        if (
            !Double.isFinite(probability) ||
            probability < 0.0 ||
            probability > 1.0
        ) {
            throw new DistributionValidationException(
                "Probability must be finite and between 0 and 1."
            );
        }
    }
}

final class DiscreteDistribution implements DiscreteVariable {
    private final List<Outcome> outcomes;
    private final Map<Double, Double> probabilityMass;
    private final double[] cumulative;
    private final double expectedValue;
    private final double variance;

    public DiscreteDistribution(List<Outcome> input) {
        if (input == null || input.isEmpty()) {
            throw new DistributionValidationException(
                "A non-empty support is required."
            );
        }

        List<Outcome> sorted = new ArrayList<>(input);
        sorted.sort((left, right) ->
            Double.compare(left.value(), right.value())
        );

        Map<Double, Double> masses = new TreeMap<>();
        double total = 0.0;

        for (Outcome outcome : sorted) {
            Objects.requireNonNull(outcome, "Outcome cannot be null.");

            if (masses.containsKey(outcome.value())) {
                throw new DistributionValidationException(
                    "Duplicate support value: " + outcome.value()
                );
            }

            masses.put(outcome.value(), outcome.probability());
            total += outcome.probability();
        }

        if (Math.abs(total - 1.0) > 1e-9) {
            throw new DistributionValidationException(
                "Probabilities must sum to 1. Actual total: " + total
            );
        }

        this.outcomes = List.copyOf(sorted);
        this.probabilityMass = Map.copyOf(masses);
        this.cumulative = new double[sorted.size()];

        double runningTotal = 0.0;
        double calculatedMean = 0.0;

        for (int index = 0; index < sorted.size(); index++) {
            Outcome outcome = sorted.get(index);

            runningTotal += outcome.probability();
            cumulative[index] = runningTotal;

            calculatedMean += outcome.value() * outcome.probability();
        }

        cumulative[cumulative.length - 1] = 1.0;
        this.expectedValue = calculatedMean;

        double calculatedVariance = 0.0;

        for (Outcome outcome : sorted) {
            double difference = outcome.value() - expectedValue;

            calculatedVariance +=
                outcome.probability() * difference * difference;
        }

        this.variance = calculatedVariance;
    }

    @Override
    public double pmf(double x) {
        if (Double.isNaN(x)) {
            throw new DistributionValidationException(
                "PMF input cannot be NaN."
            );
        }

        if (!Double.isFinite(x)) {
            return 0.0;
        }

        return probabilityMass.getOrDefault(x, 0.0);
    }

    @Override
    public double cdf(double x) {
        if (Double.isNaN(x)) {
            throw new DistributionValidationException(
                "CDF input cannot be NaN."
            );
        }

        int left = 0;
        int right = outcomes.size();

        // Find the first outcome greater than x.
        while (left < right) {
            int middle = left + (right - left) / 2;

            if (outcomes.get(middle).value() <= x) {
                left = middle + 1;
            } else {
                right = middle;
            }
        }

        return left == 0 ? 0.0 : cumulative[left - 1];
    }

    @Override
    public double mean() {
        return expectedValue;
    }

    @Override
    public double variance() {
        return variance;
    }

    @Override
    public double sample(RandomGenerator random) {
        Objects.requireNonNull(random, "Random generator is required.");

        double draw = random.nextDouble();
        int left = 0;
        int right = cumulative.length;

        while (left < right) {
            int middle = left + (right - left) / 2;

            if (cumulative[middle] >= draw) {
                right = middle;
            } else {
                left = middle + 1;
            }
        }

        return outcomes.get(Math.min(left, outcomes.size() - 1)).value();
    }

    public List<Outcome> outcomes() {
        return outcomes;
    }
}

final class NormalDistribution implements ContinuousVariable {
    private final double mean;
    private final double standardDeviation;

    public NormalDistribution(double mean, double standardDeviation) {
        if (!Double.isFinite(mean)) {
            throw new DistributionValidationException(
                "Normal mean must be finite."
            );
        }

        if (
            !Double.isFinite(standardDeviation) ||
            standardDeviation <= 0.0
        ) {
            throw new DistributionValidationException(
                "Normal standard deviation must be positive."
            );
        }

        this.mean = mean;
        this.standardDeviation = standardDeviation;
    }

    @Override
    public double mean() {
        return mean;
    }

    @Override
    public double variance() {
        return standardDeviation * standardDeviation;
    }

    @Override
    public double pdf(double x) {
        if (Double.isNaN(x)) {
            throw new DistributionValidationException(
                "PDF input cannot be NaN."
            );
        }

        if (!Double.isFinite(x)) {
            return 0.0;
        }

        double z = (x - mean) / standardDeviation;

        return Math.exp(-0.5 * z * z) /
            (standardDeviation * Math.sqrt(2.0 * Math.PI));
    }

    @Override
    public double cdf(double x) {
        if (Double.isNaN(x)) {
            throw new DistributionValidationException(
                "CDF input cannot be NaN."
            );
        }

        if (x == Double.POSITIVE_INFINITY) return 1.0;
        if (x == Double.NEGATIVE_INFINITY) return 0.0;

        double z = (x - mean) /
            (standardDeviation * Math.sqrt(2.0));

        return 0.5 * (1.0 + ErrorFunction.erf(z));
    }

    @Override
    public double sample(RandomGenerator random) {
        Objects.requireNonNull(random, "Random generator is required.");
        return mean + standardDeviation * random.nextGaussian();
    }
}

final class UniformDistribution implements ContinuousVariable {
    private final double lower;
    private final double upper;

    public UniformDistribution(double lower, double upper) {
        if (!Double.isFinite(lower) || !Double.isFinite(upper)) {
            throw new DistributionValidationException(
                "Uniform bounds must be finite."
            );
        }

        if (lower >= upper) {
            throw new DistributionValidationException(
                "Uniform lower bound must be below upper bound."
            );
        }

        this.lower = lower;
        this.upper = upper;
    }

    @Override
    public double mean() {
        return (lower + upper) / 2.0;
    }

    @Override
    public double variance() {
        double width = upper - lower;
        return width * width / 12.0;
    }

    @Override
    public double pdf(double x) {
        if (Double.isNaN(x)) {
            throw new DistributionValidationException(
                "PDF input cannot be NaN."
            );
        }

        return x >= lower && x <= upper
            ? 1.0 / (upper - lower)
            : 0.0;
    }

    @Override
    public double cdf(double x) {
        if (Double.isNaN(x)) {
            throw new DistributionValidationException(
                "CDF input cannot be NaN."
            );
        }

        if (x <= lower) return 0.0;
        if (x >= upper) return 1.0;

        return (x - lower) / (upper - lower);
    }

    @Override
    public double sample(RandomGenerator random) {
        Objects.requireNonNull(random, "Random generator is required.");

        return lower + random.nextDouble() * (upper - lower);
    }
}

/* Abramowitz-Stegun approximation for the error function. */
final class ErrorFunction {
    private ErrorFunction() {}

    static double erf(double value) {
        double sign = value < 0.0 ? -1.0 : 1.0;
        double absolute = Math.abs(value);
        double t = 1.0 / (1.0 + 0.5 * absolute);

        double polynomial = t * Math.exp(
            -absolute * absolute - 1.26551223 +
            t * (
                1.00002368 +
                t * (
                    0.37409196 +
                    t * (
                        0.09678418 +
                        t * (
                            -0.18628806 +
                            t * (
                                0.27886807 +
                                t * (
                                    -1.13520398 +
                                    t * (
                                        1.48851587 +
                                        t * (
                                            -0.82215223 +
                                            t * 0.17087277
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        );

        return sign * (1.0 - polynomial);
    }
}

final class DistributionFactory {
    private DistributionFactory() {}

    static DiscreteDistribution binomial(
        int trials,
        double probability
    ) {
        if (trials < 0 || trials > 1000) {
            throw new DistributionValidationException(
                "Trials must be between 0 and 1000."
            );
        }

        if (
            !Double.isFinite(probability) ||
            probability < 0.0 ||
            probability > 1.0
        ) {
            throw new DistributionValidationException(
                "Success probability must be between 0 and 1."
            );
        }

        List<Outcome> outcomes = new ArrayList<>();

        if (probability == 0.0) {
            outcomes.add(new Outcome(0, 1.0));
        } else if (probability == 1.0) {
            outcomes.add(new Outcome(trials, 1.0));
        } else {
            double current = Math.pow(1.0 - probability, trials);

            for (int k = 0; k <= trials; k++) {
                outcomes.add(new Outcome(k, current));

                if (k < trials) {
                    current *=
                        ((double) (trials - k) / (k + 1)) *
                        (probability / (1.0 - probability));
                }
            }
        }

        return new DiscreteDistribution(outcomes);
    }
}

record ProbabilityPolicy(
    String policyId,
    double maximumTailProbability,
    boolean active
) {
    ProbabilityPolicy {
        if (policyId == null || policyId.isBlank()) {
            throw new DistributionValidationException(
                "Policy ID cannot be empty."
            );
        }

        if (
            !Double.isFinite(maximumTailProbability) ||
            maximumTailProbability < 0.0 ||
            maximumTailProbability > 1.0
        ) {
            throw new DistributionValidationException(
                "Maximum tail probability must be between 0 and 1."
            );
        }
    }
}

record PolicyResult(
    String policyId,
    double maximumAllowedProbability,
    boolean passed
) {}

enum AssessmentDecision {
    APPROVED,
    REJECTED
}

record RiskEvaluation(
    String variableName,
    double threshold,
    double modeledTailProbability,
    List<PolicyResult> policyResults,
    AssessmentDecision decision,
    Instant evaluatedAt
) {
    RiskEvaluation {
        policyResults = List.copyOf(policyResults);
        Objects.requireNonNull(decision);
        Objects.requireNonNull(evaluatedAt);
    }
}

/*
 * Each active policy is evaluated independently.
 * A failed policy prevents the overall assessment from being approved.
 */
final class ProbabilityAssessmentService {
    public RiskEvaluation evaluateUpperTail(
        String variableName,
        RandomVariable variable,
        double threshold,
        List<ProbabilityPolicy> policies
    ) {
        if (variableName == null || variableName.isBlank()) {
            throw new AssessmentException(
                "Variable name is required."
            );
        }

        Objects.requireNonNull(variable, "Random variable is required.");
        Objects.requireNonNull(policies, "Policy list is required.");

        if (!Double.isFinite(threshold)) {
            throw new AssessmentException(
                "Assessment threshold must be finite."
            );
        }

        List<ProbabilityPolicy> activePolicies = policies.stream()
            .filter(ProbabilityPolicy::active)
            .toList();

        if (activePolicies.isEmpty()) {
            throw new AssessmentException(
                "At least one active policy is required."
            );
        }

        Set<String> uniqueIds = new HashSet<>();

        for (ProbabilityPolicy policy : activePolicies) {
            if (!uniqueIds.add(policy.policyId())) {
                throw new AssessmentException(
                    "Duplicate active policy ID: " + policy.policyId()
                );
            }
        }

        // The event being assessed is X > threshold.
        double tailProbability = 1.0 - variable.cdf(threshold);
        tailProbability = Math.max(0.0, Math.min(1.0, tailProbability));

        List<PolicyResult> results = activePolicies.stream()
            .map(policy -> new PolicyResult(
                policy.policyId(),
                policy.maximumTailProbability(),
                tailProbability <= policy.maximumTailProbability()
            ))
            .toList();

        boolean allPoliciesPassed = results.stream()
            .allMatch(PolicyResult::passed);

        AssessmentDecision decision = allPoliciesPassed
            ? AssessmentDecision.APPROVED
            : AssessmentDecision.REJECTED;

        return new RiskEvaluation(
            variableName,
            threshold,
            tailProbability,
            results,
            decision,
            Instant.now()
        );
    }
}

/*
 * OnlineStatistics uses Welford's algorithm.
 * It stores only aggregate state, not the entire observation history.
 */
final class OnlineStatistics {
    private long count;
    private double mean;
    private double m2;

    public void add(double observation) {
        if (!Double.isFinite(observation)) {
            throw new DistributionValidationException(
                "Observation must be finite."
            );
        }

        count++;

        double delta = observation - mean;
        mean += delta / count;

        double adjustedDelta = observation - mean;
        m2 += delta * adjustedDelta;
    }

    public long count() {
        return count;
    }

    public double mean() {
        return mean;
    }

    public double sampleVariance() {
        return count < 2 ? 0.0 : m2 / (count - 1);
    }
}

public class Main {
    private static void runValidationChecks() {
        DiscreteDistribution die = new DiscreteDistribution(
            List.of(
                new Outcome(1, 1.0 / 6.0),
                new Outcome(2, 1.0 / 6.0),
                new Outcome(3, 1.0 / 6.0),
                new Outcome(4, 1.0 / 6.0),
                new Outcome(5, 1.0 / 6.0),
                new Outcome(6, 1.0 / 6.0)
            )
        );

        assert Math.abs(die.pmf(3) - 1.0 / 6.0) < 1e-9;
        assert Math.abs(die.cdf(3) - 0.5) < 1e-9;
        assert Math.abs(die.mean() - 3.5) < 1e-9;

        NormalDistribution normal = new NormalDistribution(0.0, 1.0);

        assert Math.abs(normal.cdf(0.0) - 0.5) < 1e-6;

        UniformDistribution uniform = new UniformDistribution(0, 10);

        assert Math.abs(uniform.cdf(5) - 0.5) < 1e-12;
        assert Math.abs(uniform.pdf(5) - 0.1) < 1e-12;

        boolean invalidTotalRejected = false;

        try {
            new DiscreteDistribution(
                List.of(
                    new Outcome(0, 0.4),
                    new Outcome(1, 0.4)
                )
            );
        } catch (DistributionValidationException exception) {
            invalidTotalRejected = true;
        }

        if (!invalidTotalRejected) {
            throw new AssertionError(
                "An invalid probability total was accepted."
            );
        }
    }

    private static void printEvaluation(RiskEvaluation evaluation) {
        System.out.printf(
            "Variable: %s%n",
            evaluation.variableName()
        );

        System.out.printf(
            "Threshold: %.4f%n",
            evaluation.threshold()
        );

        System.out.printf(
            "Modeled upper-tail probability: %.6f%n",
            evaluation.modeledTailProbability()
        );

        for (PolicyResult result : evaluation.policyResults()) {
            System.out.printf(
                "Policy %-28s limit=%.4f result=%s%n",
                result.policyId(),
                result.maximumAllowedProbability(),
                result.passed() ? "PASS" : "FAIL"
            );
        }

        System.out.println("Decision: " + evaluation.decision());
        System.out.println("Evaluated at: " + evaluation.evaluatedAt());
    }

    public static void main(String[] args) {
        try {
            runValidationChecks();

            RandomGenerator random = new Random(20261103L);

            System.out.println("RANDOM VARIABLES: ENTERPRISE PROBABILITY MODEL");
            System.out.println("================================================");

            // Operational risk: failed requests across five requests.
            DiscreteDistribution failureCount =
                DistributionFactory.binomial(5, 0.10);

            System.out.println("\n1. DISCRETE DISTRIBUTION");
            System.out.println("X = failed requests among five requests");

            for (Outcome outcome : failureCount.outcomes()) {
                System.out.printf(
                    "P(X = %.0f) = %.6f%n",
                    outcome.value(),
                    outcome.probability()
                );
            }

            System.out.printf(
                "P(X <= 1) = %.6f%n",
                failureCount.cdf(1)
            );

            System.out.printf(
                "P(X > 1) = %.6f%n",
                1.0 - failureCount.cdf(1)
            );

            System.out.printf(
                "Expected failures = %.6f%n",
                failureCount.mean()
            );

            System.out.printf(
                "Failure-count variance = %.6f%n",
                failureCount.variance()
            );

            // Two active policies demonstrate a policy conflict.
            List<ProbabilityPolicy> failurePolicies = List.of(
                new ProbabilityPolicy(
                    "operations-limit-10-percent",
                    0.10,
                    true
                ),
                new ProbabilityPolicy(
                    "critical-service-limit-7.5-percent",
                    0.075,
                    true
                ),
                new ProbabilityPolicy(
                    "inactive-retired-policy",
                    0.01,
                    false
                )
            );

            ProbabilityAssessmentService service =
                new ProbabilityAssessmentService();

            System.out.println("\n2. ENTERPRISE POLICY EVALUATION");

            RiskEvaluation failureEvaluation =
                service.evaluateUpperTail(
                    "failed_requests",
                    failureCount,
                    1.0,
                    failurePolicies
                );

            printEvaluation(failureEvaluation);

            // Continuous response-time model.
            NormalDistribution latency =
                new NormalDistribution(120.0, 25.0);

            System.out.println("\n3. CONTINUOUS NORMAL DISTRIBUTION");

            System.out.printf("PDF at 150 ms = %.8f%n", latency.pdf(150));
            System.out.printf("CDF at 150 ms = %.6f%n", latency.cdf(150));

            List<ProbabilityPolicy> latencyPolicies = List.of(
                new ProbabilityPolicy(
                    "api-latency-service-limit",
                    0.01,
                    true
                )
            );

            RiskEvaluation latencyEvaluation =
                service.evaluateUpperTail(
                    "api_latency_ms",
                    latency,
                    180.0,
                    latencyPolicies
                );

            printEvaluation(latencyEvaluation);

            // Continuous sensor error.
            UniformDistribution sensorError =
                new UniformDistribution(-2.0, 2.0);

            System.out.println("\n4. CONTINUOUS UNIFORM DISTRIBUTION");
            System.out.printf("Mean = %.4f%n", sensorError.mean());
            System.out.printf("Variance = %.4f%n", sensorError.variance());
            System.out.printf("PDF at 0 = %.4f%n", sensorError.pdf(0));
            System.out.printf("CDF at 1 = %.4f%n", sensorError.cdf(1));

            // Simulate observations without retaining a full event history.
            int sampleCount = 25_000;
            OnlineStatistics latencyStatistics = new OnlineStatistics();

            long highLatencyCount = 0;

            for (int index = 0; index < sampleCount; index++) {
                double observation = latency.sample(random);
                latencyStatistics.add(observation);

                if (observation > 180.0) {
                    highLatencyCount++;
                }
            }

            System.out.println("\n5. EMPIRICAL MONITORING");
            System.out.println("Latency observations: " + latencyStatistics.count());

            System.out.printf(
                "Empirical mean: %.4f ms%n",
                latencyStatistics.mean()
            );

            System.out.printf(
                "Empirical sample variance: %.4f%n",
                latencyStatistics.sampleVariance()
            );

            System.out.printf(
                "Empirical P(Y > 180): %.6f%n",
                (double) highLatencyCount / sampleCount
            );

            // Validation of boundary cases.
            if (failureCount.cdf(Double.NEGATIVE_INFINITY) != 0.0) {
                throw new AssertionError("Discrete CDF lower boundary failed.");
            }

            if (Math.abs(latency.cdf(Double.POSITIVE_INFINITY) - 1.0) > 1e-12) {
                throw new AssertionError("Normal CDF upper boundary failed.");
            }

            if (sensorError.cdf(-2.0) != 0.0 || sensorError.cdf(2.0) != 1.0) {
                throw new AssertionError("Uniform CDF boundary failed.");
            }

            System.out.println("\n6. VALIDATION");
            System.out.println("All deterministic checks passed.");
            System.out.println(
                "Seeded pseudorandom simulation is not suitable for cryptographic use."
            );

        } catch (RuntimeException exception) {
            System.err.println(
                exception.getClass().getSimpleName() +
                ": " + exception.getMessage()
            );

            System.exitCode = 1;
        }
    }
}
