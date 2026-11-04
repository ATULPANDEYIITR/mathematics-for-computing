import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Random;
import java.util.TreeMap;
import java.util.stream.Collectors;

/*
 * EXPECTED VALUE AND MOMENTS
 *
 * Enterprise probability analytics system.
 *
 * Java 17 features:
 * - Records
 * - Enums
 * - Immutable collections
 * - Generic statistical interfaces
 * - Service classes
 * - Custom exceptions
 * - Probability validation
 * - Financial risk policies
 * - Conditional expectation
 * - Moment calculations
 * - Portfolio analytics
 * - Monte Carlo simulation
 */

public class ExpectedValueAnalytics {

    private static final double EPSILON = 1e-9;

    enum RiskCategory {
        LOW,
        MODERATE,
        HIGH,
        CRITICAL
    }

    record Outcome(double value, double probability) {

        Outcome {
            if (!Double.isFinite(value)
                    || !Double.isFinite(probability)) {
                throw new IllegalArgumentException(
                        "Outcome values must be finite."
                );
            }

            if (probability < 0 || probability > 1) {
                throw new IllegalArgumentException(
                        "Probability must be between 0 and 1."
                );
            }
        }
    }

    record Statistics(
            double expectedValue,
            double variance,
            double standardDeviation,
            Map<Integer, Double> rawMoments,
            Map<Integer, Double> centralMoments,
            Double skewness,
            Double kurtosis
    ) {}

    record JointOutcome(
            double x,
            double y,
            double probability
    ) {
        JointOutcome {
            if (!Double.isFinite(x)
                    || !Double.isFinite(y)
                    || !Double.isFinite(probability)) {
                throw new IllegalArgumentException(
                        "Joint values must be finite."
                );
            }

            if (probability < 0 || probability > 1) {
                throw new IllegalArgumentException(
                        "Invalid joint probability."
                );
            }
        }
    }

    record RiskPolicy(
            double maximumStandardDeviation,
            double minimumExpectedReturn
    ) {
        RiskPolicy {
            if (!Double.isFinite(maximumStandardDeviation)
                    || !Double.isFinite(minimumExpectedReturn)
                    || maximumStandardDeviation < 0) {
                throw new IllegalArgumentException(
                        "Invalid risk policy."
                );
            }
        }
    }

    record RiskDecision(
            RiskCategory category,
            boolean accepted,
            String reason
    ) {}

    static class ProbabilityException extends RuntimeException {
        ProbabilityException(String message) {
            super(message);
        }
    }

    interface StatisticalModel<T> {
        T calculate();
    }

    static final class Distribution
            implements StatisticalModel<Statistics> {

        private final String name;
        private final List<Outcome> outcomes;

        Distribution(String name, List<Outcome> outcomes) {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException(
                        "Distribution name is required."
                );
            }

            if (outcomes == null || outcomes.isEmpty()) {
                throw new ProbabilityException(
                        "Distribution cannot be empty."
                );
            }

            this.name = name;
            this.outcomes = Collections.unmodifiableList(
                    new ArrayList<>(outcomes)
            );

            validate();
        }

        private void validate() {
            double total = outcomes.stream()
                    .mapToDouble(Outcome::probability)
                    .sum();

            if (Math.abs(total - 1.0) > EPSILON) {
                throw new ProbabilityException(
                        "Probabilities must sum to 1. Received "
                                + total
                );
            }
        }

        public String name() {
            return name;
        }

        public List<Outcome> outcomes() {
            return outcomes;
        }

        public double expectation() {
            return outcomes.stream()
                    .mapToDouble(
                            o -> o.value() * o.probability()
                    )
                    .sum();
        }

        public double rawMoment(int order) {
            if (order < 0) {
                throw new IllegalArgumentException(
                        "Moment order cannot be negative."
                );
            }

            return outcomes.stream()
                    .mapToDouble(
                            o -> Math.pow(o.value(), order)
                                    * o.probability()
                    )
                    .sum();
        }

        public double centralMoment(int order) {
            if (order < 0) {
                throw new IllegalArgumentException(
                        "Moment order cannot be negative."
                );
            }

            double mean = expectation();

            return outcomes.stream()
                    .mapToDouble(
                            o -> Math.pow(o.value() - mean, order)
                                    * o.probability()
                    )
                    .sum();
        }

        public double variance() {
            return Math.max(0.0, centralMoment(2));
        }

        public double standardDeviation() {
            return Math.sqrt(variance());
        }

        public double conditionalExpectation(
                java.util.function.DoublePredicate condition
        ) {
            Objects.requireNonNull(condition);

            double probability = outcomes.stream()
                    .filter(o -> condition.test(o.value()))
                    .mapToDouble(Outcome::probability)
                    .sum();

            if (probability <= EPSILON) {
                throw new ProbabilityException(
                        "Conditional event has zero probability."
                );
            }

            double weightedSum = outcomes.stream()
                    .filter(o -> condition.test(o.value()))
                    .mapToDouble(
                            o -> o.value() * o.probability()
                    )
                    .sum();

            return weightedSum / probability;
        }

        public double probabilityGreaterThan(double threshold) {
            return outcomes.stream()
                    .filter(o -> o.value() > threshold)
                    .mapToDouble(Outcome::probability)
                    .sum();
        }

        @Override
        public Statistics calculate() {
            double mean = expectation();
            double variance = variance();
            double sd = Math.sqrt(variance);

            Map<Integer, Double> raw = new TreeMap<>();
            Map<Integer, Double> central = new TreeMap<>();

            for (int order = 1; order <= 4; order++) {
                raw.put(order, rawMoment(order));
                central.put(order, centralMoment(order));
            }

            Double skewness = variance == 0
                    ? null
                    : central.get(3) / Math.pow(sd, 3);

            Double kurtosis = variance == 0
                    ? null
                    : central.get(4) / Math.pow(variance, 2);

            return new Statistics(
                    mean,
                    variance,
                    sd,
                    Collections.unmodifiableMap(raw),
                    Collections.unmodifiableMap(central),
                    skewness,
                    kurtosis
            );
        }
    }

    static final class JointDistribution {

        private final List<JointOutcome> outcomes;

        JointDistribution(List<JointOutcome> outcomes) {
            if (outcomes == null || outcomes.isEmpty()) {
                throw new ProbabilityException(
                        "Joint distribution cannot be empty."
                );
            }

            this.outcomes = List.copyOf(outcomes);

            double total = outcomes.stream()
                    .mapToDouble(JointOutcome::probability)
                    .sum();

            if (Math.abs(total - 1.0) > EPSILON) {
                throw new ProbabilityException(
                        "Joint probabilities must sum to 1."
                );
            }
        }

        public double covariance() {
            double meanX = outcomes.stream()
                    .mapToDouble(
                            o -> o.x() * o.probability()
                    )
                    .sum();

            double meanY = outcomes.stream()
                    .mapToDouble(
                            o -> o.y() * o.probability()
                    )
                    .sum();

            return outcomes.stream()
                    .mapToDouble(
                            o -> (o.x() - meanX)
                                    * (o.y() - meanY)
                                    * o.probability()
                    )
                    .sum();
        }

        public double correlation() {
            double meanX = outcomes.stream()
                    .mapToDouble(
                            o -> o.x() * o.probability()
                    )
                    .sum();

            double meanY = outcomes.stream()
                    .mapToDouble(
                            o -> o.y() * o.probability()
                    )
                    .sum();

            double varianceX = outcomes.stream()
                    .mapToDouble(
                            o -> Math.pow(o.x() - meanX, 2)
                                    * o.probability()
                    )
                    .sum();

            double varianceY = outcomes.stream()
                    .mapToDouble(
                            o -> Math.pow(o.y() - meanY, 2)
                                    * o.probability()
                    )
                    .sum();

            if (varianceX == 0 || varianceY == 0) {
                throw new ProbabilityException(
                        "Correlation undefined for zero variance."
                );
            }

            return covariance()
                    / Math.sqrt(varianceX * varianceY);
        }
    }

    static final class RiskPolicyService {

        private final RiskPolicy policy;

        RiskPolicyService(RiskPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        public RiskDecision evaluate(Statistics statistics) {
            if (statistics == null) {
                throw new IllegalArgumentException(
                        "Statistics are required."
                );
            }

            double risk = statistics.standardDeviation();
            double expectedReturn = statistics.expectedValue();

            RiskCategory category;

            if (risk <= policy.maximumStandardDeviation() * 0.25) {
                category = RiskCategory.LOW;
            } else if (
                    risk <= policy.maximumStandardDeviation() * 0.50
            ) {
                category = RiskCategory.MODERATE;
            } else if (
                    risk <= policy.maximumStandardDeviation()
            ) {
                category = RiskCategory.HIGH;
            } else {
                category = RiskCategory.CRITICAL;
            }

            boolean accepted =
                    risk <= policy.maximumStandardDeviation()
                    && expectedReturn >= policy.minimumExpectedReturn();

            String reason = accepted
                    ? "Distribution satisfies the risk policy."
                    : "Expected return or risk violates the policy.";

            return new RiskDecision(
                    category,
                    accepted,
                    reason
            );
        }
    }

    static final class MonteCarloService {

        public double estimate(
                Distribution distribution,
                int trials,
                long seed
        ) {
            if (trials <= 0) {
                throw new IllegalArgumentException(
                        "Trials must be positive."
                );
            }

            List<Outcome> outcomes = distribution.outcomes();
            Random random = new Random(seed);

            double sum = 0.0;

            for (int i = 0; i < trials; i++) {
                double randomValue = random.nextDouble();
                double cumulative = 0.0;

                for (Outcome outcome : outcomes) {
                    cumulative += outcome.probability();

                    if (randomValue < cumulative) {
                        sum += outcome.value();
                        break;
                    }
                }
            }

            return sum / trials;
        }
    }

    record PortfolioAsset(
            String name,
            double expectedReturn,
            double weight,
            double standardDeviation
    ) {}

    static final class PortfolioService {

        public double expectedReturn(
                List<PortfolioAsset> assets
        ) {
            validateAssets(assets);

            return assets.stream()
                    .mapToDouble(
                            a -> a.weight() * a.expectedReturn()
                    )
                    .sum();
        }

        public double varianceAssumingIndependence(
                List<PortfolioAsset> assets
        ) {
            validateAssets(assets);

            return assets.stream()
                    .mapToDouble(
                            a -> Math.pow(
                                    a.weight() * a.standardDeviation(),
                                    2
                            )
                    )
                    .sum();
        }

        private void validateAssets(
                List<PortfolioAsset> assets
        ) {
            if (assets == null || assets.isEmpty()) {
                throw new IllegalArgumentException(
                        "Portfolio cannot be empty."
                );
            }

            double totalWeight = assets.stream()
                    .mapToDouble(PortfolioAsset::weight)
                    .sum();

            if (Math.abs(totalWeight - 1.0) > EPSILON) {
                throw new IllegalArgumentException(
                        "Portfolio weights must sum to 1."
                );
            }

            for (PortfolioAsset asset : assets) {
                if (asset.weight() < 0
                        || asset.standardDeviation() < 0
                        || !Double.isFinite(asset.expectedReturn())
                        || !Double.isFinite(asset.weight())
                        || !Double.isFinite(asset.standardDeviation())) {
                    throw new IllegalArgumentException(
                            "Invalid portfolio asset."
                    );
                }
            }
        }
    }

    private static void printStatistics(Distribution distribution) {
        Statistics statistics = distribution.calculate();

        System.out.println("\n" + distribution.name());
        System.out.println("------------------------------------------");

        System.out.printf(
                "Expected value: %.6f%n",
                statistics.expectedValue()
        );

        System.out.printf(
                "Variance: %.6f%n",
                statistics.variance()
        );

        System.out.printf(
                "Standard deviation: %.6f%n",
                statistics.standardDeviation()
        );

        System.out.println("\nRaw moments:");

        statistics.rawMoments().forEach(
                (order, value) -> System.out.printf(
                        "Moment %d: %.6f%n",
                        order,
                        value
                )
        );

        System.out.println("\nCentral moments:");

        statistics.centralMoments().forEach(
                (order, value) -> System.out.printf(
                        "Moment %d: %.6f%n",
                        order,
                        value
                )
        );

        System.out.println("Skewness: " + statistics.skewness());
        System.out.println("Kurtosis: " + statistics.kurtosis());
    }

    public static void main(String[] args) {

        System.out.println("EXPECTED VALUE AND MOMENTS");
        System.out.println("=".repeat(60));

        List<Outcome> dieOutcomes = new ArrayList<>();

        for (int face = 1; face <= 6; face++) {
            dieOutcomes.add(
                    new Outcome(face, 1.0 / 6.0)
            );
        }

        Distribution die = new Distribution(
                "Fair Six-Sided Die",
                dieOutcomes
        );

        Distribution investment = new Distribution(
                "Investment Returns",
                List.of(
                        new Outcome(-1000, 0.10),
                        new Outcome(-200, 0.20),
                        new Outcome(300, 0.40),
                        new Outcome(1000, 0.20),
                        new Outcome(2500, 0.10)
                )
        );

        printStatistics(die);
        printStatistics(investment);

        System.out.println("\nConditional analysis");

        System.out.println(
                "Probability of positive return: "
                        + investment.probabilityGreaterThan(0)
        );

        System.out.println(
                "Expected positive return: "
                        + investment.conditionalExpectation(
                                value -> value > 0
                        )
        );

        JointDistribution joint = new JointDistribution(
                List.of(
                        new JointOutcome(10, 20, 0.20),
                        new JointOutcome(20, 30, 0.30),
                        new JointOutcome(30, 20, 0.10),
                        new JointOutcome(40, 50, 0.40)
                )
        );

        System.out.println("\nJoint distribution");

        System.out.println(
                "Covariance: " + joint.covariance()
        );

        System.out.println(
                "Correlation: " + joint.correlation()
        );

        RiskPolicy policy = new RiskPolicy(
                1200,
                100
        );

        RiskPolicyService policyService =
                new RiskPolicyService(policy);

        RiskDecision decision = policyService.evaluate(
                investment.calculate()
        );

        System.out.println("\nEnterprise risk decision");
        System.out.println("Category: " + decision.category());
        System.out.println("Accepted: " + decision.accepted());
        System.out.println("Reason: " + decision.reason());

        List<PortfolioAsset> assets = List.of(
                new PortfolioAsset("Equity", 0.12, 0.60, 0.20),
                new PortfolioAsset("Bonds", 0.05, 0.30, 0.06),
                new PortfolioAsset("Cash", 0.03, 0.10, 0.01)
        );

        PortfolioService portfolio = new PortfolioService();

        System.out.println("\nPortfolio analytics");

        System.out.println(
                "Expected return: "
                        + portfolio.expectedReturn(assets)
        );

        System.out.println(
                "Variance assuming independence: "
                        + portfolio.varianceAssumingIndependence(assets)
        );

        MonteCarloService simulator = new MonteCarloService();

        double estimatedMean = simulator.estimate(
                die,
                100000,
                42L
        );

        System.out.println("\nMonte Carlo simulation");

        System.out.println(
                "Estimated expectation: " + estimatedMean
        );

        System.out.println(
                "Theoretical expectation: " + die.expectation()
        );

        // Deterministic distribution.
        Distribution constant = new Distribution(
                "Constant Outcome",
                List.of(new Outcome(50, 1.0))
        );

        System.out.println(
                "\nDeterministic variance: " + constant.variance()
        );

        // Mathematical validation.
        if (Math.abs(die.expectation() - 3.5) > EPSILON) {
            throw new AssertionError("Expected value test failed.");
        }

        if (Math.abs(die.variance() - 35.0 / 12.0) > EPSILON) {
            throw new AssertionError("Variance test failed.");
        }

        if (constant.variance() != 0.0) {
            throw new AssertionError(
                    "Deterministic variance test failed."
            );
        }

        System.out.println("\nAll validation tests passed.");
    }
}
