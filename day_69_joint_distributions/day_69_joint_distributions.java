import java.util.*;
import java.util.stream.Collectors;

/*
 * Joint Distributions
 *
 * Enterprise scenario:
 * Employee training level and assessment outcome.
 *
 * Implements:
 * - Joint PMF
 * - Marginal distributions
 * - Conditional distributions
 * - Joint expectation
 * - Variance
 * - Covariance
 * - Correlation
 * - Independence
 * - Bivariate normal PDF
 *
 * Java 17, no external dependencies.
 */

public class JointDistributionAnalysis {

    private static final double EPSILON = 1e-10;

    static class DistributionException extends RuntimeException {
        public DistributionException(String message) {
            super(message);
        }
    }

    record Outcome(double x, double y, double probability) {
        Outcome {
            if (
                !Double.isFinite(x) ||
                !Double.isFinite(y) ||
                !Double.isFinite(probability)
            ) {
                throw new DistributionException(
                    "Outcome values must be finite."
                );
            }

            if (probability < 0) {
                throw new DistributionException(
                    "Probability cannot be negative."
                );
            }
        }
    }

    record JointKey(double x, double y) {}

    record DistributionMetrics(
        double expectedX,
        double expectedY,
        double varianceX,
        double varianceY,
        double expectedXY,
        double covariance,
        double correlation
    ) {}

    interface DistributionAnalyzer {
        double jointProbability(double x, double y);

        Map<Double, Double> marginalX();

        Map<Double, Double> marginalY();

        double covariance();

        double correlation();
    }

    static class DiscreteJointDistribution
            implements DistributionAnalyzer {

        private final Map<JointKey, Double> jointPMF;

        DiscreteJointDistribution(List<Outcome> outcomes) {
            this(outcomes, EPSILON);
        }

        DiscreteJointDistribution(
            List<Outcome> outcomes,
            double tolerance
        ) {
            if (outcomes == null || outcomes.isEmpty()) {
                throw new DistributionException(
                    "Distribution cannot be empty."
                );
            }

            if (!Double.isFinite(tolerance) || tolerance < 0) {
                throw new DistributionException(
                    "Invalid probability tolerance."
                );
            }

            Map<JointKey, Double> temporary = new LinkedHashMap<>();

            double total = 0.0;

            for (Outcome outcome : outcomes) {
                JointKey key = new JointKey(outcome.x(), outcome.y());

                if (temporary.containsKey(key)) {
                    throw new DistributionException(
                        "Duplicate joint outcome: " + key
                    );
                }

                temporary.put(key, outcome.probability());
                total += outcome.probability();
            }

            if (Math.abs(total - 1.0) > tolerance) {
                throw new DistributionException(
                    "Joint probabilities must sum to one."
                );
            }

            final double probabilityTotal = total;

            this.jointPMF = Collections.unmodifiableMap(
                temporary.entrySet().stream().collect(
                    Collectors.toMap(
                        Map.Entry::getKey,
                        entry -> entry.getValue() / probabilityTotal,
                        (a, b) -> a,
                        LinkedHashMap::new
                    )
                )
            );
        }

        @Override
        public double jointProbability(double x, double y) {
            return jointPMF.getOrDefault(
                new JointKey(x, y),
                0.0
            );
        }

        private Map<Double, Double> calculateMarginal(
            boolean useX
        ) {
            Map<Double, Double> result = new TreeMap<>();

            jointPMF.forEach((key, probability) -> {
                double value = useX ? key.x() : key.y();

                result.merge(
                    value,
                    probability,
                    Double::sum
                );
            });

            return Collections.unmodifiableMap(result);
        }

        @Override
        public Map<Double, Double> marginalX() {
            return calculateMarginal(true);
        }

        @Override
        public Map<Double, Double> marginalY() {
            return calculateMarginal(false);
        }

        private Map<Double, Double> conditional(
            double conditionValue,
            boolean conditionOnX
        ) {
            Map<Double, Double> marginal =
                conditionOnX ? marginalX() : marginalY();

            double denominator = marginal.getOrDefault(
                conditionValue,
                0.0
            );

            if (denominator == 0) {
                throw new DistributionException(
                    "Conditional distribution is undefined."
                );
            }

            Map<Double, Double> result = new TreeMap<>();

            jointPMF.forEach((key, probability) -> {
                double condition = conditionOnX ? key.x() : key.y();
                double target = conditionOnX ? key.y() : key.x();

                if (Double.compare(condition, conditionValue) == 0) {
                    result.merge(
                        target,
                        probability / denominator,
                        Double::sum
                    );
                }
            });

            return Collections.unmodifiableMap(result);
        }

        public Map<Double, Double> conditionalYGivenX(double x) {
            return conditional(x, true);
        }

        public Map<Double, Double> conditionalXGivenY(double y) {
            return conditional(y, false);
        }

        private static double expectation(
            Map<Double, Double> distribution
        ) {
            return distribution.entrySet()
                .stream()
                .mapToDouble(entry ->
                    entry.getKey() * entry.getValue()
                )
                .sum();
        }

        private static double variance(
            Map<Double, Double> distribution
        ) {
            double mean = expectation(distribution);

            return distribution.entrySet()
                .stream()
                .mapToDouble(entry ->
                    entry.getValue() *
                    Math.pow(entry.getKey() - mean, 2)
                )
                .sum();
        }

        public double expectedX() {
            return expectation(marginalX());
        }

        public double expectedY() {
            return expectation(marginalY());
        }

        public double varianceX() {
            return variance(marginalX());
        }

        public double varianceY() {
            return variance(marginalY());
        }

        public double expectedXY() {
            return jointPMF.entrySet()
                .stream()
                .mapToDouble(entry ->
                    entry.getKey().x() *
                    entry.getKey().y() *
                    entry.getValue()
                )
                .sum();
        }

        @Override
        public double covariance() {
            return expectedXY() - expectedX() * expectedY();
        }

        @Override
        public double correlation() {
            double denominator = Math.sqrt(
                varianceX() * varianceY()
            );

            if (denominator == 0) {
                throw new DistributionException(
                    "Correlation undefined for zero variance."
                );
            }

            return covariance() / denominator;
        }

        public boolean isIndependent() {
            for (Map.Entry<JointKey, Double> entry :
                    jointPMF.entrySet()) {

                JointKey key = entry.getKey();

                double expected =
                    marginalX().get(key.x()) *
                    marginalY().get(key.y());

                if (Math.abs(entry.getValue() - expected) > 1e-9) {
                    return false;
                }
            }

            for (double x : marginalX().keySet()) {
                for (double y : marginalY().keySet()) {
                    double expected =
                        marginalX().get(x) * marginalY().get(y);

                    if (
                        Math.abs(jointProbability(x, y) - expected)
                        > 1e-9
                    ) {
                        return false;
                    }
                }
            }

            return true;
        }

        public DistributionMetrics metrics() {
            return new DistributionMetrics(
                expectedX(),
                expectedY(),
                varianceX(),
                varianceY(),
                expectedXY(),
                covariance(),
                correlation()
            );
        }

        public void printReport() {
            System.out.println("\nJoint PMF");

            jointPMF.forEach((key, probability) ->
                System.out.printf(
                    Locale.ROOT,
                    "P(X=%.2f, Y=%.2f) = %.4f%n",
                    key.x(),
                    key.y(),
                    probability
                )
            );

            System.out.println("\nMarginal X: " + marginalX());
            System.out.println("Marginal Y: " + marginalY());

            System.out.println(
                "\nConditional P(Y | X=1): " +
                conditionalYGivenX(1)
            );

            DistributionMetrics metrics = metrics();

            System.out.println("\nStatistical Measures");

            System.out.printf(
                Locale.ROOT,
                "E[X]       : %.6f%n",
                metrics.expectedX()
            );

            System.out.printf(
                Locale.ROOT,
                "E[Y]       : %.6f%n",
                metrics.expectedY()
            );

            System.out.printf(
                Locale.ROOT,
                "Var(X)     : %.6f%n",
                metrics.varianceX()
            );

            System.out.printf(
                Locale.ROOT,
                "Var(Y)     : %.6f%n",
                metrics.varianceY()
            );

            System.out.printf(
                Locale.ROOT,
                "E[XY]      : %.6f%n",
                metrics.expectedXY()
            );

            System.out.printf(
                Locale.ROOT,
                "Covariance : %.6f%n",
                metrics.covariance()
            );

            System.out.printf(
                Locale.ROOT,
                "Correlation: %.6f%n",
                metrics.correlation()
            );

            System.out.println(
                "Independent: " + isIndependent()
            );
        }
    }

    static final class BivariateNormal {

        private final double meanX;
        private final double meanY;
        private final double sigmaX;
        private final double sigmaY;
        private final double rho;

        BivariateNormal(
            double meanX,
            double meanY,
            double sigmaX,
            double sigmaY,
            double rho
        ) {
            double[] values = {
                meanX, meanY, sigmaX, sigmaY, rho
            };

            for (double value : values) {
                if (!Double.isFinite(value)) {
                    throw new DistributionException(
                        "Parameters must be finite."
                    );
                }
            }

            if (sigmaX <= 0 || sigmaY <= 0) {
                throw new DistributionException(
                    "Standard deviations must be positive."
                );
            }

            if (rho <= -1 || rho >= 1) {
                throw new DistributionException(
                    "Correlation must be strictly between -1 and 1."
                );
            }

            this.meanX = meanX;
            this.meanY = meanY;
            this.sigmaX = sigmaX;
            this.sigmaY = sigmaY;
            this.rho = rho;
        }

        public double pdf(double x, double y) {
            if (!Double.isFinite(x) || !Double.isFinite(y)) {
                throw new DistributionException(
                    "PDF inputs must be finite."
                );
            }

            double zx = (x - meanX) / sigmaX;
            double zy = (y - meanY) / sigmaY;

            double exponent = -(
                zx * zx -
                2 * rho * zx * zy +
                zy * zy
            ) / (2 * (1 - rho * rho));

            double denominator =
                2 * Math.PI *
                sigmaX *
                sigmaY *
                Math.sqrt(1 - rho * rho);

            return Math.exp(exponent) / denominator;
        }

        public double marginalXPDF(double x) {
            double z = (x - meanX) / sigmaX;

            return Math.exp(-0.5 * z * z) /
                (sigmaX * Math.sqrt(2 * Math.PI));
        }

        public double marginalYPDF(double y) {
            double z = (y - meanY) / sigmaY;

            return Math.exp(-0.5 * z * z) /
                (sigmaY * Math.sqrt(2 * Math.PI));
        }

        public double covariance() {
            return rho * sigmaX * sigmaY;
        }

        public double correlation() {
            return rho;
        }
    }

    private static void runTests() {
        DiscreteJointDistribution independent =
            new DiscreteJointDistribution(List.of(
                new Outcome(0, 0, 0.25),
                new Outcome(0, 1, 0.25),
                new Outcome(1, 0, 0.25),
                new Outcome(1, 1, 0.25)
            ));

        assertClose(independent.expectedX(), 0.5);
        assertClose(independent.expectedY(), 0.5);
        assertClose(independent.varianceX(), 0.25);
        assertClose(independent.covariance(), 0.0);

        if (!independent.isIndependent()) {
            throw new AssertionError(
                "Independence validation failed."
            );
        }

        DiscreteJointDistribution dependent =
            new DiscreteJointDistribution(List.of(
                new Outcome(0, 0, 0.5),
                new Outcome(1, 1, 0.5)
            ));

        if (dependent.isIndependent()) {
            throw new AssertionError(
                "Dependence validation failed."
            );
        }

        assertClose(dependent.correlation(), 1.0);

        try {
            new DiscreteJointDistribution(List.of(
                new Outcome(0, 0, 0.4),
                new Outcome(1, 1, 0.4)
            ));

            throw new AssertionError(
                "Invalid PMF was accepted."
            );
        } catch (DistributionException expected) {
            // Expected failure.
        }

        try {
            independent.conditionalYGivenX(5);

            throw new AssertionError(
                "Undefined conditional PMF was accepted."
            );
        } catch (DistributionException expected) {
            // Expected failure.
        }

        System.out.println("\nAll Java 17 tests passed.");
    }

    private static void assertClose(
        double actual,
        double expected
    ) {
        if (Math.abs(actual - expected) > EPSILON) {
            throw new AssertionError(
                "Expected " + expected + " but found " + actual
            );
        }
    }

    public static void main(String[] args) {
        try {
            System.out.println("JOINT DISTRIBUTION ANALYSIS");
            System.out.println("============================");

            DiscreteJointDistribution distribution =
                new DiscreteJointDistribution(List.of(
                    new Outcome(0, 0, 0.10),
                    new Outcome(0, 1, 0.15),
                    new Outcome(1, 0, 0.20),
                    new Outcome(1, 1, 0.30),
                    new Outcome(2, 0, 0.05),
                    new Outcome(2, 1, 0.20)
                ));

            distribution.printReport();

            BivariateNormal continuous =
                new BivariateNormal(
                    70.0,
                    75.0,
                    10.0,
                    12.0,
                    0.65
                );

            System.out.println(
                "\nBivariate Normal Distribution"
            );

            System.out.printf(
                Locale.ROOT,
                "Joint PDF: %.8f%n",
                continuous.pdf(70, 75)
            );

            System.out.printf(
                Locale.ROOT,
                "Marginal X PDF: %.8f%n",
                continuous.marginalXPDF(70)
            );

            System.out.printf(
                Locale.ROOT,
                "Marginal Y PDF: %.8f%n",
                continuous.marginalYPDF(75)
            );

            System.out.printf(
                Locale.ROOT,
                "Covariance: %.4f%n",
                continuous.covariance()
            );

            System.out.printf(
                Locale.ROOT,
                "Correlation: %.4f%n",
                continuous.correlation()
            );

            runTests();

        } catch (DistributionException exception) {
            System.err.println(
                "[DISTRIBUTION ERROR] " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
