import java.util.*;
import java.util.function.DoubleUnaryOperator;

/**
 * Probability Inequalities: Markov, Chebyshev, Jensen, and Chernoff.
 *
 * Enterprise-oriented probability analysis service.
 * Java 17, no external dependencies.
 */
public class ProbabilityInequalities {

    enum InequalityType {
        MARKOV,
        CHEBYSHEV,
        JENSEN,
        CHERNOFF
    }

    enum ExperimentStatus {
        REGISTERED,
        VALIDATED,
        EVALUATED,
        FAILED
    }

    static class ProbabilityException extends RuntimeException {
        ProbabilityException(String message) {
            super(message);
        }
    }

    record Outcome(double value, double probability) {
        Outcome {
            if (!Double.isFinite(value)) {
                throw new ProbabilityException("Outcome must be finite.");
            }

            if (!Double.isFinite(probability) || probability < 0) {
                throw new ProbabilityException(
                    "Probability must be finite and nonnegative."
                );
            }
        }
    }

    record BoundResult(
        InequalityType type,
        double threshold,
        double bound,
        double exactProbability,
        double parameter
    ) {
        BoundResult {
            Objects.requireNonNull(type);

            if (!Double.isFinite(bound) || bound < 0 || bound > 1) {
                throw new ProbabilityException("Invalid bound.");
            }

            if (!Double.isFinite(exactProbability) ||
                exactProbability < 0 ||
                exactProbability > 1) {
                throw new ProbabilityException("Invalid exact probability.");
            }
        }
    }

    record ExperimentReport(
        String experimentName,
        double mean,
        double variance,
        double threshold,
        Map<InequalityType, BoundResult> results,
        ExperimentStatus status
    ) {
        ExperimentReport {
            results = Collections.unmodifiableMap(
                new EnumMap<>(results)
            );
        }
    }

    static final class DiscreteDistribution {
        private final List<Outcome> outcomes;
        private final double mean;
        private final double variance;

        DiscreteDistribution(List<Outcome> outcomes) {
            if (outcomes == null || outcomes.isEmpty()) {
                throw new ProbabilityException(
                    "Distribution cannot be empty."
                );
            }

            double total = outcomes.stream()
                .mapToDouble(Outcome::probability)
                .sum();

            if (Math.abs(total - 1.0) > 1e-10) {
                throw new ProbabilityException(
                    "Probabilities must sum to one."
                );
            }

            // Defensive copies prevent external mutation.
            this.outcomes = List.copyOf(outcomes);

            this.mean = this.outcomes.stream()
                .mapToDouble(o -> o.value() * o.probability())
                .sum();

            this.variance = this.outcomes.stream()
                .mapToDouble(o ->
                    o.probability() *
                    Math.pow(o.value() - mean, 2)
                )
                .sum();
        }

        double mean() {
            return mean;
        }

        double variance() {
            return variance;
        }

        double expectation(DoubleUnaryOperator function) {
            double result = outcomes.stream()
                .mapToDouble(o ->
                    o.probability() * function.applyAsDouble(o.value())
                )
                .sum();

            if (!Double.isFinite(result)) {
                throw new ProbabilityException(
                    "Expectation is not finite."
                );
            }

            return result;
        }

        double probability(
            java.util.function.DoublePredicate predicate
        ) {
            return outcomes.stream()
                .filter(o -> predicate.test(o.value()))
                .mapToDouble(Outcome::probability)
                .sum();
        }

        boolean isNonnegative() {
            return outcomes.stream().allMatch(
                o -> o.value() >= 0
            );
        }

        List<Outcome> outcomes() {
            return outcomes;
        }
    }

    interface ConvexFunction {
        double apply(double value);

        // The mathematical convexity contract belongs to the caller.
        String description();
    }

    static final class SquareFunction implements ConvexFunction {
        @Override
        public double apply(double value) {
            return value * value;
        }

        @Override
        public String description() {
            return "f(x) = x^2";
        }
    }

    static final class ExponentialFunction implements ConvexFunction {
        @Override
        public double apply(double value) {
            return Math.exp(value);
        }

        @Override
        public String description() {
            return "f(x) = exp(x)";
        }
    }

    static final class InequalityService {

        private static void requirePositive(
            double value,
            String name
        ) {
            if (!Double.isFinite(value) || value <= 0) {
                throw new ProbabilityException(
                    name + " must be positive and finite."
                );
            }
        }

        BoundResult markov(
            DiscreteDistribution distribution,
            double threshold
        ) {
            requirePositive(threshold, "Threshold");

            if (!distribution.isNonnegative()) {
                throw new ProbabilityException(
                    "Markov requires a nonnegative random variable."
                );
            }

            double bound = Math.min(
                1.0,
                distribution.mean() / threshold
            );

            double exact = distribution.probability(
                x -> x >= threshold
            );

            return new BoundResult(
                InequalityType.MARKOV,
                threshold,
                bound,
                exact,
                0
            );
        }

        BoundResult chebyshev(
            DiscreteDistribution distribution,
            double deviation
        ) {
            requirePositive(deviation, "Deviation");

            double bound = Math.min(
                1.0,
                distribution.variance() / (deviation * deviation)
            );

            double mean = distribution.mean();

            double exact = distribution.probability(
                x -> Math.abs(x - mean) >= deviation
            );

            return new BoundResult(
                InequalityType.CHEBYSHEV,
                deviation,
                bound,
                exact,
                0
            );
        }

        BoundResult jensen(
            DiscreteDistribution distribution,
            ConvexFunction function
        ) {
            double left = function.apply(distribution.mean());

            double right = distribution.expectation(
                function::apply
            );

            if (!Double.isFinite(left) ||
                !Double.isFinite(right)) {
                throw new ProbabilityException(
                    "Jensen function returned a non-finite value."
                );
            }

            if (left > right + 1e-10) {
                throw new ProbabilityException(
                    "Jensen inequality failed. Verify convexity and domain."
                );
            }

            return new BoundResult(
                InequalityType.JENSEN,
                distribution.mean(),
                Math.min(1.0, Math.max(0.0, right - left)),
                0,
                0
            );
        }

        private double logSumExp(double[] values) {
            double maximum = Arrays.stream(values)
                .max()
                .orElseThrow();

            double sum = Arrays.stream(values)
                .map(value -> Math.exp(value - maximum))
                .sum();

            return maximum + Math.log(sum);
        }

        private double logMGF(
            DiscreteDistribution distribution,
            double lambda
        ) {
            double[] terms = distribution.outcomes().stream()
                .filter(o -> o.probability() > 0)
                .mapToDouble(o ->
                    Math.log(o.probability()) +
                    lambda * o.value()
                )
                .toArray();

            double result = logSumExp(terms);

            if (!Double.isFinite(result)) {
                throw new ProbabilityException(
                    "MGF calculation failed."
                );
            }

            return result;
        }

        BoundResult chernoff(
            DiscreteDistribution distribution,
            double threshold,
            double lambdaMaximum,
            int steps
        ) {
            if (!Double.isFinite(threshold) ||
                !Double.isFinite(lambdaMaximum) ||
                lambdaMaximum <= 0 ||
                steps <= 0) {
                throw new ProbabilityException(
                    "Invalid Chernoff parameters."
                );
            }

            double bestBound = 1.0;
            double bestLambda = 0.0;

            for (int i = 0; i <= steps; i++) {
                double lambda = lambdaMaximum * i / steps;

                double exponent =
                    logMGF(distribution, lambda) -
                    lambda * threshold;

                double bound = exponent < -745
                    ? 0
                    : Math.min(1.0, Math.exp(exponent));

                if (bound < bestBound) {
                    bestBound = bound;
                    bestLambda = lambda;
                }
            }

            double exact = distribution.probability(
                x -> x >= threshold
            );

            return new BoundResult(
                InequalityType.CH​ER​NO​FF,
                threshold,
                bestBound,
                exact,
                bestLambda
            );
        }
    }

    static final class ExperimentRegistry {
        private final Map<String, DiscreteDistribution> experiments =
            new LinkedHashMap<>();

        private final Map<String, ExperimentStatus> statuses =
            new HashMap<>();

        void register(
            String name,
            DiscreteDistribution distribution
        ) {
            if (name == null || name.isBlank()) {
                throw new ProbabilityException(
                    "Experiment name is required."
                );
            }

            Objects.requireNonNull(distribution);

            if (experiments.containsKey(name)) {
                throw new ProbabilityException(
                    "Experiment already registered."
                );
            }

            experiments.put(name, distribution);
            statuses.put(name, ExperimentStatus.REGISTERED);
        }

        DiscreteDistribution get(String name) {
            DiscreteDistribution distribution = experiments.get(name);

            if (distribution == null) {
                throw new ProbabilityException(
                    "Unknown experiment: " + name
                );
            }

            return distribution;
        }

        void updateStatus(
            String name,
            ExperimentStatus status
        ) {
            if (!statuses.containsKey(name)) {
                throw new ProbabilityException("Unknown experiment.");
            }

            statuses.put(name, status);
        }

        ExperimentStatus status(String name) {
            return statuses.get(name);
        }
    }

    static final class ProbabilityReportingService {
        private final ExperimentRegistry registry;
        private final InequalityService service;

        ProbabilityReportingService(
            ExperimentRegistry registry,
            InequalityService service
        ) {
            this.registry = registry;
            this.service = service;
        }

        ExperimentReport evaluate(
            String name,
            double threshold
        ) {
            DiscreteDistribution distribution = registry.get(name);

            registry.updateStatus(
                name,
                ExperimentStatus.VALIDATED
            );

            try {
                Map<InequalityType, BoundResult> results =
                    new EnumMap<>(InequalityType.class);

                if (distribution.isNonnegative()) {
                    results.put(
                        InequalityType.MARKOV,
                        service.markov(distribution, threshold)
                    );
                }

                double deviation = Math.max(
                    0.01,
                    Math.abs(threshold - distribution.mean())
                );

                results.put(
                    InequalityType.CHEBYSHEV,
                    service.chebyshev(distribution, deviation)
                );

                results.put(
                    InequalityType.JENSEN,
                    service.jensen(
                        distribution,
                        new SquareFunction()
                    )
                );

                results.put(
                    InequalityType.CH​ER​NO​FF,
                    service.chernoff(
                        distribution,
                        threshold,
                        20,
                        2000
                    )
                );

                registry.updateStatus(
                    name,
                    ExperimentStatus.EVALUATED
                );

                return new ExperimentReport(
                    name,
                    distribution.mean(),
                    distribution.variance(),
                    threshold,
                    results,
                    registry.status(name)
                );

            } catch (RuntimeException exception) {
                registry.updateStatus(
                    name,
                    ExperimentStatus.FAILED
                );
                throw exception;
            }
        }
    }

    static DiscreteDistribution binomial(
        int trials,
        double probability
    ) {
        if (trials < 0 || trials > 1000 ||
            !Double.isFinite(probability) ||
            probability < 0 || probability > 1) {
            throw new ProbabilityException(
                "Invalid binomial parameters."
            );
        }

        double[] probabilities = new double[trials + 1];

        if (probability == 0) {
            probabilities[0] = 1;
        } else if (probability == 1) {
            probabilities[trials] = 1;
        } else {
            probabilities[0] = Math.pow(1 - probability, trials);

            for (int k = 1; k <= trials; k++) {
                probabilities[k] =
                    probabilities[k - 1] *
                    (trials - k + 1.0) / k *
                    probability / (1 - probability);
            }
        }

        List<Outcome> outcomes = new ArrayList<>();

        for (int k = 0; k <= trials; k++) {
            outcomes.add(new Outcome(k, probabilities[k]));
        }

        return new DiscreteDistribution(outcomes);
    }

    static void runTests() {
        DiscreteDistribution distribution =
            new DiscreteDistribution(List.of(
                new Outcome(0, 0.1),
                new Outcome(1, 0.2),
                new Outcome(2, 0.4),
                new Outcome(3, 0.2),
                new Outcome(4, 0.1)
            ));

        assert Math.abs(distribution.mean() - 2.0) < 1e-10;
        assert Math.abs(distribution.variance() - 1.4) < 1e-10;

        InequalityService service = new InequalityService();

        BoundResult markov = service.markov(distribution, 3);

        assert markov.bound() + 1e-10 >=
            markov.exactProbability();

        BoundResult chebyshev = service.chebyshev(distribution, 1);

        assert chebyshev.bound() + 1e-10 >=
            chebyshev.exactProbability();

        service.jensen(distribution, new SquareFunction());

        DiscreteDistribution binomial = binomial(20, 0.5);

        BoundResult chernoff = service.chernoff(
            binomial, 15, 20, 2000
        );

        assert chernoff.bound() + 1e-10 >=
            chernoff.exactProbability();

        try {
            service.markov(distribution, 0);
            throw new AssertionError("Invalid threshold accepted.");
        } catch (ProbabilityException expected) {
            // Expected validation failure.
        }

        System.out.println("All Java probability tests passed.");
    }

    public static void main(String[] args) {
        runTests();

        ExperimentRegistry registry = new ExperimentRegistry();

        registry.register(
            "operational-risk",
            new DiscreteDistribution(List.of(
                new Outcome(0, 0.05),
                new Outcome(1, 0.10),
                new Outcome(2, 0.20),
                new Outcome(3, 0.30),
                new Outcome(4, 0.20),
                new Outcome(5, 0.15)
            ))
        );

        registry.register(
            "binomial-failures",
            binomial(30, 0.5)
        );

        ProbabilityReportingService reporting =
            new ProbabilityReportingService(
                registry,
                new InequalityService()
            );

        for (String name : List.of(
            "operational-risk",
            "binomial-failures"
        )) {
            ExperimentReport report = reporting.evaluate(
                name,
                name.equals("operational-risk") ? 4 : 20
            );

            System.out.println("\nExperiment: " + report.experimentName());
            System.out.printf("Mean: %.6f%n", report.mean());
            System.out.printf("Variance: %.6f%n", report.variance());
            System.out.println("Status: " + report.status());

            report.results().forEach((type, result) -> {
                System.out.printf(
                    "%s | Bound: %.8f | Exact: %.8f%n",
                    type,
                    result.bound(),
                    result.exactProbability()
                );
            });
        }

        System.out.println("\nEnterprise probability evaluation completed.");
    }
}
