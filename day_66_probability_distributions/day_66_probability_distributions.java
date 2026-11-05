import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.TreeMap;

/**
 * Probability distribution service for enterprise transaction
 * reliability and operational risk analysis.
 *
 * Java 17, no external dependencies.
 */
public class ProbabilityDistributionApp {

    private static final double EPSILON = 1e-10;

    public enum DistributionType {
        BERNOULLI,
        BINOMIAL,
        GEOMETRIC,
        NEGATIVE_BINOMIAL
    }

    public enum SimulationStatus {
        CREATED,
        RUNNING,
        COMPLETED,
        FAILED
    }

    public static class ProbabilityException extends RuntimeException {
        public ProbabilityException(String message) {
            super(message);
        }
    }

    public record Statistics(
        double mean,
        double variance,
        double standardDeviation
    ) {}

    public record SimulationReport(
        DistributionType type,
        int observations,
        double empiricalMean,
        double empiricalVariance,
        Statistics theoreticalStatistics,
        Map<Integer, Long> frequencies
    ) {
        public SimulationReport {
            frequencies = Collections.unmodifiableMap(
                new TreeMap<>(frequencies)
            );
        }
    }

    public record OperationalPolicy(
        String policyName,
        double minimumSuccessProbability,
        int maximumExpectedAttempts
    ) {
        public OperationalPolicy {
            if (policyName == null || policyName.isBlank()) {
                throw new ProbabilityException(
                    "Policy name cannot be empty."
                );
            }

            validateProbability(minimumSuccessProbability);

            if (maximumExpectedAttempts < 1) {
                throw new ProbabilityException(
                    "Maximum expected attempts must be positive."
                );
            }
        }
    }

    public interface DiscreteDistribution {
        double pmf(int outcome);

        double cdf(int outcome);

        int sample(Random random);

        Statistics statistics();

        DistributionType type();
    }

    private static void validateProbability(double p) {
        if (!Double.isFinite(p) || p < 0 || p > 1) {
            throw new ProbabilityException(
                "Probability must be between 0 and 1."
            );
        }
    }

    private static void validatePositive(int value, String name) {
        if (value < 1) {
            throw new ProbabilityException(
                name + " must be at least 1."
            );
        }
    }

    private static double choose(int n, int k) {
        if (k < 0 || k > n) return 0;

        k = Math.min(k, n - k);

        double result = 1.0;

        for (int i = 1; i <= k; i++) {
            result = result * (n - k + i) / i;
        }

        return result;
    }

    public abstract static class BaseDistribution
        implements DiscreteDistribution {

        protected final double p;

        protected BaseDistribution(double probability) {
            validateProbability(probability);
            this.p = probability;
        }

        public double probabilityAtLeast(int threshold) {
            if (threshold == Integer.MIN_VALUE) return 1.0;

            return Math.max(0.0, 1.0 - cdf(threshold - 1));
        }
    }

    public static final class Bernoulli
        extends BaseDistribution {

        public Bernoulli(double p) {
            super(p);
        }

        @Override
        public double pmf(int outcome) {
            if (outcome == 1) return p;
            if (outcome == 0) return 1 - p;
            return 0;
        }

        @Override
        public double cdf(int outcome) {
            if (outcome < 0) return 0;
            if (outcome == 0) return 1 - p;
            return 1;
        }

        @Override
        public int sample(Random random) {
            return random.nextDouble() < p ? 1 : 0;
        }

        @Override
        public Statistics statistics() {
            double variance = p * (1 - p);

            return new Statistics(
                p, variance, Math.sqrt(variance)
            );
        }

        @Override
        public DistributionType type() {
            return DistributionType.BERNOULLI;
        }
    }

    public static final class Binomial
        extends BaseDistribution {

        private final int n;

        public Binomial(int n, double p) {
            super(p);
            if (n < 0) {
                throw new ProbabilityException(
                    "Number of trials cannot be negative."
                );
            }
            this.n = n;
        }

        @Override
        public double pmf(int k) {
            if (k < 0 || k > n) return 0;

            return choose(n, k)
                * Math.pow(p, k)
                * Math.pow(1 - p, n - k);
        }

        @Override
        public double cdf(int k) {
            if (k < 0) return 0;
            if (k >= n) return 1;

            double total = 0;

            for (int i = 0; i <= k; i++) {
                total += pmf(i);
            }

            return Math.min(1, total);
        }

        @Override
        public int sample(Random random) {
            int successes = 0;

            for (int i = 0; i < n; i++) {
                if (random.nextDouble() < p) {
                    successes++;
                }
            }

            return successes;
        }

        @Override
        public Statistics statistics() {
            double mean = n * p;
            double variance = n * p * (1 - p);

            return new Statistics(
                mean, variance, Math.sqrt(variance)
            );
        }

        @Override
        public DistributionType type() {
            return DistributionType.BINOMIAL;
        }

        public int trials() {
            return n;
        }
    }

    public static final class Geometric
        extends BaseDistribution {

        public Geometric(double p) {
            super(p);
        }

        @Override
        public double pmf(int k) {
            if (k < 1 || p == 0) return 0;
            if (p == 1) return k == 1 ? 1 : 0;

            return p * Math.pow(1 - p, k - 1);
        }

        @Override
        public double cdf(int k) {
            if (k < 1 || p == 0) return 0;
            if (p == 1) return 1;

            return 1 - Math.pow(1 - p, k);
        }

        @Override
        public int sample(Random random) {
            if (p == 0) {
                throw new ProbabilityException(
                    "No finite waiting time exists when p = 0."
                );
            }

            if (p == 1) return 1;

            return (int) Math.floor(
                Math.log1p(-random.nextDouble()) /
                Math.log1p(-p)
            ) + 1;
        }

        @Override
        public Statistics statistics() {
            if (p == 0) {
                return new Statistics(
                    Double.POSITIVE_INFINITY,
                    Double.POSITIVE_INFINITY,
                    Double.POSITIVE_INFINITY
                );
            }

            double mean = 1 / p;
            double variance = (1 - p) / (p * p);

            return new Statistics(
                mean, variance, Math.sqrt(variance)
            );
        }

        @Override
        public DistributionType type() {
            return DistributionType.GEOMETRIC;
        }
    }

    public static final class NegativeBinomial
        extends BaseDistribution {

        private final int requiredSuccesses;

        public NegativeBinomial(int requiredSuccesses, double p) {
            super(p);
            validatePositive(
                requiredSuccesses, "Required successes"
            );
            this.requiredSuccesses = requiredSuccesses;
        }

        @Override
        public double pmf(int k) {
            if (k < requiredSuccesses || p == 0) return 0;

            if (p == 1) {
                return k == requiredSuccesses ? 1 : 0;
            }

            return choose(k - 1, requiredSuccesses - 1)
                * Math.pow(p, requiredSuccesses)
                * Math.pow(1 - p, k - requiredSuccesses);
        }

        @Override
        public double cdf(int k) {
            if (k < requiredSuccesses || p == 0) return 0;
            if (p == 1) return 1;

            double total = 0;

            for (int i = requiredSuccesses; i <= k; i++) {
                total += pmf(i);
            }

            return Math.min(1, total);
        }

        @Override
        public int sample(Random random) {
            if (p == 0) {
                throw new ProbabilityException(
                    "Required successes cannot be reached."
                );
            }

            if (p == 1) return requiredSuccesses;

            int successes = 0;
            int trials = 0;

            while (successes < requiredSuccesses) {
                trials++;

                if (random.nextDouble() < p) {
                    successes++;
                }
            }

            return trials;
        }

        @Override
        public Statistics statistics() {
            if (p == 0) {
                return new Statistics(
                    Double.POSITIVE_INFINITY,
                    Double.POSITIVE_INFINITY,
                    Double.POSITIVE_INFINITY
                );
            }

            double mean = requiredSuccesses / p;
            double variance =
                requiredSuccesses * (1 - p) / (p * p);

            return new Statistics(
                mean, variance, Math.sqrt(variance)
            );
        }

        @Override
        public DistributionType type() {
            return DistributionType.NEGATIVE_BINOMIAL;
        }
    }

    public static final class SimulationService {

        private SimulationStatus status = SimulationStatus.CREATED;

        public SimulationStatus status() {
            return status;
        }

        public SimulationReport simulate(
            DiscreteDistribution distribution,
            int count,
            long seed
        ) {
            if (distribution == null) {
                throw new ProbabilityException(
                    "Distribution cannot be null."
                );
            }

            validatePositive(count, "Sample count");

            if (status == SimulationStatus.RUNNING) {
                throw new ProbabilityException(
                    "A simulation is already running."
                );
            }

            status = SimulationStatus.RUNNING;

            try {
                Random random = new Random(seed);

                Map<Integer, Long> frequencies = new TreeMap<>();

                double sum = 0;
                double sumSquares = 0;

                for (int i = 0; i < count; i++) {
                    int value = distribution.sample(random);

                    frequencies.merge(value, 1L, Long::sum);

                    sum += value;
                    sumSquares += (double) value * value;
                }

                double mean = sum / count;
                double variance = Math.max(
                    0, sumSquares / count - mean * mean
                );

                status = SimulationStatus.COMPLETED;

                return new SimulationReport(
                    distribution.type(),
                    count,
                    mean,
                    variance,
                    distribution.statistics(),
                    frequencies
                );

            } catch (RuntimeException exception) {
                status = SimulationStatus.FAILED;
                throw exception;
            }
        }
    }

    public static final class PolicyEvaluator {

        public boolean evaluate(
            Geometric distribution,
            OperationalPolicy policy
        ) {
            if (distribution == null || policy == null) {
                throw new ProbabilityException(
                    "Distribution and policy are required."
                );
            }

            Statistics stats = distribution.statistics();

            return distribution.p >= policy.minimumSuccessProbability()
                && stats.mean() <= policy.maximumExpectedAttempts();
        }
    }

    private static void assertClose(
        double actual,
        double expected
    ) {
        if (Math.abs(actual - expected) > EPSILON) {
            throw new AssertionError(
                "Expected " + expected + " but got " + actual
            );
        }
    }

    private static void runTests() {
        Bernoulli bernoulli = new Bernoulli(0.3);
        Binomial binomial = new Binomial(5, 0.5);
        Geometric geometric = new Geometric(0.25);
        NegativeBinomial negative =
            new NegativeBinomial(3, 0.5);

        assertClose(bernoulli.pmf(1), 0.3);
        assertClose(binomial.pmf(2), 0.3125);
        assertClose(geometric.cdf(2), 0.4375);
        assertClose(negative.pmf(4), 0.1875);
        assertClose(negative.cdf(4), 0.3125);

        assertClose(binomial.cdf(5), 1);
        assertClose(geometric.pmf(0), 0);

        System.out.println("All statistical tests passed.");
    }

    private static void printReport(SimulationReport report) {
        System.out.println("\nDistribution: " + report.type());
        System.out.println("Observations: " + report.observations());

        System.out.printf(
            "Empirical mean: %.6f%n",
            report.empiricalMean()
        );

        System.out.printf(
            "Theoretical mean: %.6f%n",
            report.theoreticalStatistics().mean()
        );

        System.out.printf(
            "Empirical variance: %.6f%n",
            report.empiricalVariance()
        );

        System.out.printf(
            "Theoretical variance: %.6f%n",
            report.theoreticalStatistics().variance()
        );

        System.out.println("Outcome frequencies:");

        report.frequencies().forEach(
            (outcome, frequency) ->
                System.out.printf("  %d: %d%n", outcome, frequency)
        );
    }

    public static void main(String[] args) {
        try {
            runTests();

            List<DiscreteDistribution> distributions =
                new ArrayList<>();

            distributions.add(new Bernoulli(0.95));
            distributions.add(new Binomial(20, 0.95));
            distributions.add(new Geometric(0.3));
            distributions.add(new NegativeBinomial(5, 0.3));

            SimulationService service = new SimulationService();

            for (DiscreteDistribution distribution : distributions) {
                SimulationReport report = service.simulate(
                    distribution, 10000, 42
                );

                printReport(report);
            }

            Geometric connectionAttempts = new Geometric(0.3);

            OperationalPolicy policy = new OperationalPolicy(
                "Connection Reliability Policy",
                0.25,
                4
            );

            PolicyEvaluator evaluator = new PolicyEvaluator();

            System.out.println(
                "\nConnection policy accepted: " +
                evaluator.evaluate(connectionAttempts, policy)
            );

            Binomial payments = new Binomial(20, 0.95);

            System.out.printf(
                "Probability of at least 18 successful payments: %.6f%n",
                payments.probabilityAtLeast(18)
            );

            NegativeBinomial support = new NegativeBinomial(5, 0.6);

            System.out.printf(
                "Probability of five successes within eight attempts: %.6f%n",
                support.cdf(8)
            );

            System.out.println("\nFinal service status: " + service.status());

        } catch (ProbabilityException exception) {
            System.err.println(
                "Business validation failure: " + exception.getMessage()
            );
            System.exit(1);
        }
    }
}
