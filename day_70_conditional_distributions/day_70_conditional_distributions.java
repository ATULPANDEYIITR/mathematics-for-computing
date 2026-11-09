import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeMap;

/*
 * Conditional Distributions
 *
 * Enterprise statistical analysis application.
 *
 * Java 17
 * No external dependencies.
 *
 * Features:
 * - Joint probability modeling
 * - Marginal distributions
 * - Conditional probability mass functions
 * - Conditional density functions
 * - Conditional expectation
 * - Conditional variance
 * - Conditional covariance
 * - Law of total expectation
 * - Law of total variance
 * - Immutable domain objects
 * - Statistical validation
 * - Analysis service
 * - Structured reporting
 */

public class ConditionalDistributionApp {

    private static final double TOLERANCE = 1e-10;

    enum Variable {
        X, Y
    }

    static class DistributionException extends RuntimeException {
        public DistributionException(String message) {
            super(message);
        }
    }

    record Outcome(
        int x,
        int y,
        double probability
    ) {
        Outcome {
            if (!Double.isFinite(probability) || probability < 0) {
                throw new DistributionException(
                    "Probability must be finite and nonnegative."
                );
            }
        }
    }

    record ConditionalResult(
        Variable conditioningVariable,
        int conditioningValue,
        double conditioningProbability,
        Map<Integer, Double> conditionalPMF,
        double expectation,
        double variance
    ) {
        ConditionalResult {
            Objects.requireNonNull(conditioningVariable);
            conditionalPMF = Collections.unmodifiableMap(
                new LinkedHashMap<>(conditionalPMF)
            );
        }
    }

    interface ConditionalDistribution {
        Map<Integer, Double> conditionalPMF(
            Variable variable,
            int value
        );

        double marginalProbability(
            Variable variable,
            int value
        );
    }

    static final class DiscreteJointDistribution
        implements ConditionalDistribution {

        private final List<Outcome> outcomes;

        DiscreteJointDistribution(List<Outcome> outcomes) {
            if (outcomes == null || outcomes.isEmpty()) {
                throw new DistributionException(
                    "Joint distribution cannot be empty."
                );
            }

            Map<String, Boolean> uniqueOutcomes = new HashMap<>();

            double total = 0.0;

            for (Outcome outcome : outcomes) {
                String key = outcome.x() + ":" + outcome.y();

                if (uniqueOutcomes.put(key, true) != null) {
                    throw new DistributionException(
                        "Duplicate joint outcome: " + key
                    );
                }

                total += outcome.probability();
            }

            if (Math.abs(total - 1.0) > TOLERANCE) {
                throw new DistributionException(
                    "Joint probabilities must sum to one."
                );
            }

            this.outcomes = List.copyOf(outcomes);
        }

        public double jointProbability(int x, int y) {
            return outcomes.stream()
                .filter(row -> row.x() == x && row.y() == y)
                .mapToDouble(Outcome::probability)
                .sum();
        }

        @Override
        public double marginalProbability(
            Variable variable,
            int value
        ) {
            return outcomes.stream()
                .filter(row ->
                    variable == Variable.X
                        ? row.x() == value
                        : row.y() == value
                )
                .mapToDouble(Outcome::probability)
                .sum();
        }

        @Override
        public Map<Integer, Double> conditionalPMF(
            Variable variable,
            int value
        ) {
            double denominator =
                marginalProbability(variable, value);

            if (denominator <= 0.0) {
                throw new DistributionException(
                    "Conditioning event has zero probability."
                );
            }

            Map<Integer, Double> result = new TreeMap<>();

            for (Outcome outcome : outcomes) {
                int targetValue =
                    variable == Variable.X
                        ? outcome.y()
                        : outcome.x();

                int conditioningValue =
                    variable == Variable.X
                        ? outcome.x()
                        : outcome.y();

                if (conditioningValue == value) {
                    result.merge(
                        targetValue,
                        outcome.probability() / denominator,
                        Double::sum
                    );
                }
            }

            return Collections.unmodifiableMap(result);
        }

        public Map<Integer, Double> marginalPMF(Variable variable) {
            Map<Integer, Double> result = new TreeMap<>();

            for (Outcome outcome : outcomes) {
                int value = variable == Variable.X
                    ? outcome.x()
                    : outcome.y();

                result.merge(
                    value,
                    outcome.probability(),
                    Double::sum
                );
            }

            return Collections.unmodifiableMap(result);
        }

        public static double expectation(
            Map<Integer, Double> pmf
        ) {
            return pmf.entrySet().stream()
                .mapToDouble(entry ->
                    entry.getKey() * entry.getValue()
                )
                .sum();
        }

        public static double variance(
            Map<Integer, Double> pmf
        ) {
            double mean = expectation(pmf);

            return Math.max(
                0.0,
                pmf.entrySet().stream()
                    .mapToDouble(entry ->
                        Math.pow(entry.getKey() - mean, 2)
                            * entry.getValue()
                    )
                    .sum()
            );
        }

        public ConditionalResult analyze(
            Variable variable,
            int value
        ) {
            Map<Integer, Double> pmf =
                conditionalPMF(variable, value);

            return new ConditionalResult(
                variable,
                value,
                marginalProbability(variable, value),
                pmf,
                expectation(pmf),
                variance(pmf)
            );
        }

        public double covariance() {
            double meanX = expectation(marginalPMF(Variable.X));
            double meanY = expectation(marginalPMF(Variable.Y));

            return outcomes.stream()
                .mapToDouble(outcome ->
                    (outcome.x() - meanX)
                    * (outcome.y() - meanY)
                    * outcome.probability()
                )
                .sum();
        }

        public double totalExpectation() {
            double result = 0.0;

            for (Map.Entry<Integer, Double> entry :
                marginalPMF(Variable.X).entrySet()) {

                if (entry.getValue() == 0.0) {
                    continue;
                }

                ConditionalResult conditional =
                    analyze(Variable.X, entry.getKey());

                result += entry.getValue()
                    * conditional.expectation();
            }

            return result;
        }

        public double totalVariance() {
            double expectedConditionalVariance = 0.0;
            List<double[]> conditionalMeans = new ArrayList<>();

            for (Map.Entry<Integer, Double> entry :
                marginalPMF(Variable.X).entrySet()) {

                if (entry.getValue() == 0.0) {
                    continue;
                }

                ConditionalResult conditional =
                    analyze(Variable.X, entry.getKey());

                double probability = entry.getValue();

                expectedConditionalVariance +=
                    probability * conditional.variance();

                conditionalMeans.add(new double[] {
                    conditional.expectation(),
                    probability
                });
            }

            double mean = 0.0;

            for (double[] item : conditionalMeans) {
                mean += item[0] * item[1];
            }

            double varianceOfConditionalMeans = 0.0;

            for (double[] item : conditionalMeans) {
                varianceOfConditionalMeans +=
                    item[1] * Math.pow(item[0] - mean, 2);
            }

            return expectedConditionalVariance
                + varianceOfConditionalMeans;
        }

        public double marginalVarianceY() {
            return variance(marginalPMF(Variable.Y));
        }
    }

    static final class BivariateNormal {

        private final double muX;
        private final double muY;
        private final double sigmaX;
        private final double sigmaY;
        private final double rho;

        BivariateNormal(
            double muX,
            double muY,
            double sigmaX,
            double sigmaY,
            double rho
        ) {
            if (!Double.isFinite(muX)
                || !Double.isFinite(muY)
                || !Double.isFinite(sigmaX)
                || !Double.isFinite(sigmaY)
                || !Double.isFinite(rho)) {

                throw new DistributionException(
                    "Parameters must be finite."
                );
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

            this.muX = muX;
            this.muY = muY;
            this.sigmaX = sigmaX;
            this.sigmaY = sigmaY;
            this.rho = rho;
        }

        double conditionalMean(double x) {
            if (!Double.isFinite(x)) {
                throw new DistributionException(
                    "Conditioning value must be finite."
                );
            }

            return muY
                + rho * sigmaY / sigmaX * (x - muX);
        }

        double conditionalVariance() {
            return sigmaY * sigmaY * (1 - rho * rho);
        }

        double conditionalDensity(double y, double x) {
            if (!Double.isFinite(y)) {
                throw new DistributionException(
                    "Evaluation point must be finite."
                );
            }

            double mean = conditionalMean(x);
            double variance = conditionalVariance();

            return Math.exp(
                -Math.pow(y - mean, 2) / (2 * variance)
            ) / Math.sqrt(2 * Math.PI * variance);
        }
    }

    static final class AnalysisService {

        private final DiscreteJointDistribution distribution;
        private final List<ConditionalResult> auditLog =
            new ArrayList<>();

        AnalysisService(DiscreteJointDistribution distribution) {
            this.distribution = Objects.requireNonNull(distribution);
        }

        public synchronized ConditionalResult analyze(
            Variable variable,
            int value
        ) {
            ConditionalResult result =
                distribution.analyze(variable, value);

            auditLog.add(result);

            return result;
        }

        public synchronized List<ConditionalResult> getAuditLog() {
            return List.copyOf(auditLog);
        }
    }

    private static void printResult(ConditionalResult result) {
        System.out.println(
            "\nConditioning variable: "
                + result.conditioningVariable()
        );

        System.out.println(
            "Conditioning value: "
                + result.conditioningValue()
        );

        System.out.printf(
            "Conditioning probability: %.6f%n",
            result.conditioningProbability()
        );

        System.out.println("Conditional PMF:");

        result.conditionalPMF().forEach((value, probability) ->
            System.out.printf(
                "P(Y=%d | condition) = %.6f%n",
                value,
                probability
            )
        );

        System.out.printf(
            "Conditional expectation: %.6f%n",
            result.expectation()
        );

        System.out.printf(
            "Conditional variance: %.6f%n",
            result.variance()
        );
    }

    public static void main(String[] args) {

        try {
            List<Outcome> observations = List.of(
                new Outcome(0, 0, 0.10),
                new Outcome(0, 1, 0.10),
                new Outcome(0, 2, 0.05),
                new Outcome(1, 0, 0.05),
                new Outcome(1, 1, 0.20),
                new Outcome(1, 2, 0.15),
                new Outcome(2, 0, 0.05),
                new Outcome(2, 1, 0.10),
                new Outcome(2, 2, 0.20)
            );

            DiscreteJointDistribution distribution =
                new DiscreteJointDistribution(observations);

            AnalysisService service =
                new AnalysisService(distribution);

            System.out.println(
                "CONDITIONAL DISTRIBUTION ANALYSIS"
            );

            for (int x = 0; x <= 2; x++) {
                printResult(service.analyze(Variable.X, x));
            }

            System.out.println("\nCONDITIONAL COVARIANCE");

            System.out.printf(
                "Cov(X,Y) = %.6f%n",
                distribution.covariance()
            );

            System.out.println("\nTOTAL EXPECTATION");

            double totalExpectation =
                distribution.totalExpectation();

            System.out.printf(
                "E[E[Y|X]] = %.6f%n",
                totalExpectation
            );

            System.out.println("\nTOTAL VARIANCE");

            double totalVariance = distribution.totalVariance();
            double directVariance = distribution.marginalVarianceY();

            System.out.printf(
                "Variance decomposition = %.6f%n",
                totalVariance
            );

            System.out.printf(
                "Direct marginal variance = %.6f%n",
                directVariance
            );

            if (Math.abs(totalVariance - directVariance) > TOLERANCE) {
                throw new DistributionException(
                    "Total variance validation failed."
                );
            }

            System.out.println("\nCONTINUOUS CONDITIONAL DENSITY");

            BivariateNormal normal = new BivariateNormal(
                10.0, 50.0, 2.0, 8.0, 0.75
            );

            double x = 12.0;
            double y = 58.0;

            System.out.printf(
                "E[Y|X=12] = %.6f%n",
                normal.conditionalMean(x)
            );

            System.out.printf(
                "Var(Y|X) = %.6f%n",
                normal.conditionalVariance()
            );

            System.out.printf(
                "f(Y=58|X=12) = %.8f%n",
                normal.conditionalDensity(y, x)
            );

            System.out.println("\nAUDIT INFORMATION");

            System.out.println(
                "Completed analyses: "
                    + service.getAuditLog().size()
            );

            try {
                service.analyze(Variable.X, 99);
            } catch (DistributionException exception) {
                System.out.println(
                    "Expected validation failure: "
                        + exception.getMessage()
                );
            }

            System.out.println(
                "\nAll mathematical validation checks passed."
            );

        } catch (DistributionException exception) {
            System.err.println(
                "Statistical processing error: "
                    + exception.getMessage()
            );

            System.exitCode = 1;
        }
    }
}
