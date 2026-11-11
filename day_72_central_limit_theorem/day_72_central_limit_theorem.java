/*
 * Central Limit Theorem: Enterprise Statistical Experiment Platform
 *
 * Java 17
 *
 * Implements:
 * - Immutable statistical domain records
 * - Population validation
 * - Distribution generators
 * - Sampling policies
 * - Monte Carlo batch processing
 * - Online statistical aggregation
 * - Normal approximation diagnostics
 * - Confidence interval coverage
 * - Bootstrap percentile intervals
 * - Convergence reporting
 * - Enterprise-style experiment services
 *
 * Compile:
 * javac CentralLimitTheorem.java
 *
 * Run:
 * java CentralLimitTheorem
 */

import java.util.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.DoubleSupplier;
import java.util.stream.Collectors;

public class CentralLimitTheorem {

    private static final double Z_95 = 1.959963984540054;

    enum DistributionType {
        BERNOULLI,
        EXPONENTIAL,
        UNIFORM,
        SKEWED
    }

    enum SamplingPolicy {
        WITH_REPLACEMENT,
        WITHOUT_REPLACEMENT
    }

    enum ExperimentStatus {
        CREATED,
        RUNNING,
        COMPLETED,
        FAILED
    }

    static class ValidationException extends RuntimeException {
        ValidationException(String message) {
            super(message);
        }
    }

    static class ExperimentException extends RuntimeException {
        ExperimentException(String message, Throwable cause) {
            super(message, cause);
        }
    }

    record Population(
        String name,
        DistributionType distribution,
        List<Double> observations,
        double mean,
        double variance,
        double standardDeviation
    ) {
        Population {
            Objects.requireNonNull(name);
            Objects.requireNonNull(distribution);
            Objects.requireNonNull(observations);

            if (name.isBlank() || observations.size() < 2) {
                throw new ValidationException(
                    "Population must have a name and at least two values."
                );
            }

            observations = List.copyOf(observations);

            if (observations.stream().anyMatch(
                x -> x == null || !Double.isFinite(x)
            )) {
                throw new ValidationException(
                    "Population values must be finite."
                );
            }

            double calculatedMean = observations.stream()
                .mapToDouble(Double::doubleValue)
                .average()
                .orElseThrow();

            double calculatedVariance = observations.stream()
                .mapToDouble(x -> Math.pow(x - calculatedMean, 2))
                .average()
                .orElseThrow();

            if (
                Math.abs(mean - calculatedMean) > 1e-8 ||
                Math.abs(variance - calculatedVariance) > 1e-8
            ) {
                throw new ValidationException(
                    "Population statistics are inconsistent."
                );
            }

            if (standardDeviation < 0 ||
                Math.abs(standardDeviation * standardDeviation -
                    variance) > 1e-8) {
                throw new ValidationException(
                    "Invalid population standard deviation."
                );
            }
        }

        static Population create(
            String name,
            DistributionType type,
            List<Double> values
        ) {
            if (values == null || values.size() < 2) {
                throw new ValidationException("Invalid population data.");
            }

            double mean = values.stream()
                .mapToDouble(Double::doubleValue)
                .average()
                .orElseThrow();

            double variance = values.stream()
                .mapToDouble(x -> Math.pow(x - mean, 2))
                .average()
                .orElseThrow();

            return new Population(
                name,
                type,
                values,
                mean,
                variance,
                Math.sqrt(variance)
            );
        }
    }

    record ConfidenceInterval(
        double lower,
        double upper,
        double confidenceLevel
    ) {
        ConfidenceInterval {
            if (
                !Double.isFinite(lower) ||
                !Double.isFinite(upper) ||
                lower > upper ||
                confidenceLevel <= 0 ||
                confidenceLevel >= 1
            ) {
                throw new ValidationException(
                    "Invalid confidence interval."
                );
            }
        }

        boolean contains(double value) {
            return lower <= value && value <= upper;
        }
    }

    record ExperimentConfiguration(
        int sampleSize,
        int repetitions,
        SamplingPolicy samplingPolicy,
        long seed
    ) {
        ExperimentConfiguration {
            Objects.requireNonNull(samplingPolicy);

            if (sampleSize < 1 || repetitions < 2) {
                throw new ValidationException(
                    "Invalid experiment configuration."
                );
            }
        }
    }

    record ExperimentResult(
        String population,
        int sampleSize,
        int repetitions,
        double populationMean,
        double empiricalMean,
        double empiricalSD,
        double theoreticalSE,
        double relativeSEError,
        double ksDistance,
        double coverage
    ) {}

    static class OnlineStatistics {
        private long count = 0;
        private double mean = 0;
        private double m2 = 0;

        void add(double value) {
            if (!Double.isFinite(value)) {
                throw new ValidationException(
                    "Statistic must be finite."
                );
            }

            count++;

            double delta = value - mean;
            mean += delta / count;
            double delta2 = value - mean;

            m2 += delta * delta2;
        }

        long count() {
            return count;
        }

        double mean() {
            return mean;
        }

        double variance() {
            return count > 1 ? m2 / (count - 1) : 0;
        }

        double standardDeviation() {
            return Math.sqrt(variance());
        }
    }

    static class PopulationFactory {
        static Population create(
            DistributionType type,
            int size,
            long seed
        ) {
            if (size < 2) {
                throw new ValidationException(
                    "Population size must exceed one."
                );
            }

            SplittableRandom random = new SplittableRandom(seed);

            DoubleSupplier generator = switch (type) {
                case BERNOULLI ->
                    () -> random.nextDouble() < 0.3 ? 1.0 : 0.0;

                case EXPONENTIAL ->
                    () -> -Math.log(
                        1.0 - random.nextDouble()
                    );

                case UNIFORM ->
                    () -> random.nextDouble() * 100.0;

                case SKEWED ->
                    () -> Math.pow(
                        -2.0 * Math.log(1.0 - random.nextDouble()),
                        1.5
                    );
            };

            List<Double> values = new ArrayList<>(size);

            for (int i = 0; i < size; i++) {
                values.add(generator.getAsDouble());
            }

            return Population.create(
                type.name(), type, values
            );
        }
    }

    static class SamplingService {
        private final Population population;
        private final SplittableRandom random;

        SamplingService(Population population, long seed) {
            this.population = Objects.requireNonNull(population);
            this.random = new SplittableRandom(seed);
        }

        void validate(ExperimentConfiguration config) {
            if (
                config.samplingPolicy() ==
                    SamplingPolicy.WITHOUT_REPLACEMENT &&
                config.sampleSize() > population.observations().size()
            ) {
                throw new ValidationException(
                    "Sample size exceeds finite population."
                );
            }
        }

        List<Double> draw(int n, SamplingPolicy policy) {
            if (n < 1) {
                throw new ValidationException("Sample size must be positive.");
            }

            List<Double> source = population.observations();

            if (policy == SamplingPolicy.WITH_REPLACEMENT) {
                List<Double> sample = new ArrayList<>(n);

                for (int i = 0; i < n; i++) {
                    sample.add(
                        source.get(random.nextInt(source.size()))
                    );
                }

                return sample;
            }

            if (n > source.size()) {
                throw new ValidationException(
                    "Cannot sample more observations than population size."
                );
            }

            List<Double> shuffled = new ArrayList<>(source);

            for (int i = shuffled.size() - 1; i > 0; i--) {
                int j = random.nextInt(i + 1);
                Collections.swap(shuffled, i, j);
            }

            return List.copyOf(shuffled.subList(0, n));
        }

        double standardError(
            int n,
            SamplingPolicy policy
        ) {
            if (n < 1) {
                throw new ValidationException("Invalid sample size.");
            }

            double se = population.standardDeviation() / Math.sqrt(n);

            if (policy == SamplingPolicy.WITHOUT_REPLACEMENT) {
                int N = population.observations().size();

                if (n > N) {
                    throw new ValidationException("Invalid sample size.");
                }

                se *= Math.sqrt(
                    (double) (N - n) / (N - 1)
                );
            }

            return se;
        }
    }

    static class ApproximationService {

        static double normalCDF(double x) {
            // Numerical approximation to the standard normal CDF.
            double sign = x < 0 ? -1 : 1;
            double z = Math.abs(x) / Math.sqrt(2.0);

            double t = 1.0 / (1.0 + 0.3275911 * z);

            double polynomial =
                0.254829592 +
                t * (-0.284496736 +
                t * (1.421413741 +
                t * (-1.453152027 +
                t * 1.061405429)));

            double erf = sign * (
                1.0 - polynomial * t * Math.exp(-z * z)
            );

            return 0.5 * (1.0 + erf);
        }

        static ConfidenceInterval interval(
            double mean,
            double se
        ) {
            if (!Double.isFinite(se) || se < 0) {
                throw new ValidationException(
                    "Standard error must be nonnegative."
                );
            }

            double margin = Z_95 * se;

            return new ConfidenceInterval(
                mean - margin,
                mean + margin,
                0.95
            );
        }

        static double ksDistance(
            List<Double> observations,
            double expectedMean,
            double expectedSE
        ) {
            if (observations.isEmpty()) {
                throw new ValidationException("Empty distribution.");
            }

            if (expectedSE == 0) {
                return 0;
            }

            List<Double> sorted = observations.stream()
                .sorted()
                .toList();

            int n = sorted.size();
            double maximum = 0;

            for (int i = 0; i < n; i++) {
                double z = (
                    sorted.get(i) - expectedMean
                ) / expectedSE;

                double expected = normalCDF(z);

                maximum = Math.max(
                    maximum,
                    Math.abs((i + 1.0) / n - expected)
                );

                maximum = Math.max(
                    maximum,
                    Math.abs(i / (double) n - expected)
                );
            }

            return maximum;
        }
    }

    static class BootstrapService {
        static ConfidenceInterval percentileInterval(
            List<Double> sample,
            int repetitions,
            long seed
        ) {
            if (sample == null || sample.size() < 2) {
                throw new ValidationException(
                    "Bootstrap requires at least two observations."
                );
            }

            if (repetitions < 100) {
                throw new ValidationException(
                    "Bootstrap requires at least 100 repetitions."
                );
            }

            SplittableRandom random = new SplittableRandom(seed);

            List<Double> bootstrapMeans = new ArrayList<>(repetitions);

            for (int i = 0; i < repetitions; i++) {
                double sum = 0;

                for (int j = 0; j < sample.size(); j++) {
                    sum += sample.get(random.nextInt(sample.size()));
                }

                bootstrapMeans.add(sum / sample.size());
            }

            bootstrapMeans.sort(Double::compareTo);

            int lowerIndex = (int) Math.floor(
                0.025 * (repetitions - 1)
            );

            int upperIndex = (int) Math.floor(
                0.975 * (repetitions - 1)
            );

            return new ConfidenceInterval(
                bootstrapMeans.get(lowerIndex),
                bootstrapMeans.get(upperIndex),
                0.95
            );
        }
    }

    static class ExperimentService {
        private final AtomicLong experimentCounter =
            new AtomicLong(0);

        private ExperimentStatus status = ExperimentStatus.CREATED;

        ExperimentResult execute(
            Population population,
            ExperimentConfiguration configuration
        ) {
            long experimentId = experimentCounter.incrementAndGet();

            if (status == ExperimentStatus.RUNNING) {
                throw new IllegalStateException(
                    "An experiment is already running."
                );
            }

            status = ExperimentStatus.RUNNING;

            try {
                SamplingService sampler = new SamplingService(
                    population,
                    configuration.seed()
                );

                sampler.validate(configuration);

                OnlineStatistics statistics = new OnlineStatistics();

                List<Double> means = new ArrayList<>(
                    configuration.repetitions()
                );

                for (
                    int i = 0;
                    i < configuration.repetitions();
                    i++
                ) {
                    List<Double> sample = sampler.draw(
                        configuration.sampleSize(),
                        configuration.samplingPolicy()
                    );

                    double mean = sample.stream()
                        .mapToDouble(Double::doubleValue)
                        .average()
                        .orElseThrow();

                    statistics.add(mean);
                    means.add(mean);
                }

                double theoreticalSE = sampler.standardError(
                    configuration.sampleSize(),
                    configuration.samplingPolicy()
                );

                double relativeError = theoreticalSE == 0
                    ? 0
                    : Math.abs(
                        statistics.standardDeviation() - theoreticalSE
                    ) / theoreticalSE;

                double coverage = calculateCoverage(
                    population,
                    configuration
                );

                double ks = ApproximationService.ksDistance(
                    means,
                    population.mean(),
                    theoreticalSE
                );

                status = ExperimentStatus.COMPLETED;

                return new ExperimentResult(
                    population.name() + "#" + experimentId,
                    configuration.sampleSize(),
                    configuration.repetitions(),
                    population.mean(),
                    statistics.mean(),
                    statistics.standardDeviation(),
                    theoreticalSE,
                    relativeError,
                    ks,
                    coverage
                );

            } catch (RuntimeException exception) {
                status = ExperimentStatus.FAILED;

                throw new ExperimentException(
                    "Experiment " + experimentId + " failed.",
                    exception
                );
            }
        }

        private double calculateCoverage(
            Population population,
            ExperimentConfiguration configuration
        ) {
            SamplingService sampler = new SamplingService(
                population,
                configuration.seed() + 1
            );

            int covered = 0;
            int repetitions = configuration.repetitions();

            for (int i = 0; i < repetitions; i++) {
                List<Double> sample = sampler.draw(
                    configuration.sampleSize(),
                    configuration.samplingPolicy()
                );

                double mean = sample.stream()
                    .mapToDouble(Double::doubleValue)
                    .average()
                    .orElseThrow();

                OnlineStatistics stats = new OnlineStatistics();
                sample.forEach(stats::add);

                double se = stats.standardDeviation() /
                    Math.sqrt(sample.size());

                if (
                    configuration.samplingPolicy() ==
                        SamplingPolicy.WITHOUT_REPLACEMENT
                ) {
                    int N = population.observations().size();
                    int n = configuration.sampleSize();

                    se *= Math.sqrt(
                        (double) (N - n) / (N - 1)
                    );
                }

                if (
                    ApproximationService.interval(mean, se)
                        .contains(population.mean())
                ) {
                    covered++;
                }
            }

            return (double) covered / repetitions;
        }

        ExperimentStatus getStatus() {
            return status;
        }
    }

    static void runTests() {
        OnlineStatistics stats = new OnlineStatistics();

        for (double value : List.of(1.0, 2.0, 3.0, 4.0, 5.0)) {
            stats.add(value);
        }

        if (Math.abs(stats.mean() - 3.0) > 1e-10) {
            throw new AssertionError("Mean calculation failed.");
        }

        if (Math.abs(stats.variance() - 2.5) > 1e-10) {
            throw new AssertionError("Variance calculation failed.");
        }

        if (Math.abs(
            ApproximationService.normalCDF(0) - 0.5
        ) > 0.001) {
            throw new AssertionError("Normal CDF calculation failed.");
        }

        Population population = Population.create(
            "Test",
            DistributionType.UNIFORM,
            List.of(1.0, 2.0, 3.0, 4.0)
        );

        if (Math.abs(population.mean() - 2.5) > 1e-10) {
            throw new AssertionError("Population mean failed.");
        }

        System.out.println("All Java tests passed.");
    }

    public static void main(String[] args) {
        runTests();

        List<Integer> sampleSizes = List.of(
            2, 5, 10, 30, 50, 100
        );

        List<ExperimentResult> report = new ArrayList<>();

        ExperimentService service = new ExperimentService();

        for (DistributionType type : DistributionType.values()) {
            Population population = PopulationFactory.create(
                type,
                10000,
                42 + type.ordinal()
            );

            System.out.printf(
                "%nPopulation: %s | Mean: %.5f | SD: %.5f%n",
                population.name(),
                population.mean(),
                population.standardDeviation()
            );

            for (int n : sampleSizes) {
                ExperimentConfiguration configuration =
                    new ExperimentConfiguration(
                        n,
                        3000,
                        SamplingPolicy.WITH_REPLACEMENT,
                        1000 + n
                    );

                ExperimentResult result = service.execute(
                    population,
                    configuration
                );

                report.add(result);

                System.out.printf(
                    "n=%3d | Empirical Mean=%.5f | "
                    + "Empirical SD=%.5f | Theoretical SE=%.5f | "
                    + "Relative Error=%.5f | KS=%.5f | "
                    + "Coverage=%.3f%n",
                    n,
                    result.empiricalMean(),
                    result.empiricalSD(),
                    result.theoreticalSE(),
                    result.relativeSEError(),
                    result.ksDistance(),
                    result.coverage()
                );
            }
        }

        Population bootstrapPopulation = PopulationFactory.create(
            DistributionType.EXPONENTIAL,
            1000,
            77
        );

        List<Double> observed = bootstrapPopulation.observations()
            .subList(0, 50);

        ConfidenceInterval bootstrap =
            BootstrapService.percentileInterval(
                observed, 2000, 99
            );

        System.out.printf(
            "%nBootstrap 95%% interval: [%.5f, %.5f]%n",
            bootstrap.lower(),
            bootstrap.upper()
        );

        System.out.println(
            "\nCompleted experiment records: " + report.size()
        );

        System.out.println(
            "Final experiment status: " + service.getStatus()
        );
    }
}
