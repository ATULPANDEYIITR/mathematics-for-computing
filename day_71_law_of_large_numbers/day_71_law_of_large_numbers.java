import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.time.Instant;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

/**
 * Law of Large Numbers: Enterprise statistical experiment service.
 *
 * Java 17, no external dependencies.
 *
 * Models:
 * - Statistical distributions.
 * - Weak and strong laws.
 * - Monte Carlo experiment execution.
 * - Online variance calculation.
 * - Chebyshev probability guarantees.
 * - Experiment lifecycle and validation.
 * - Immutable experiment results.
 * - Atomic report persistence.
 */

public class LawOfLargeNumbers {

    enum DistributionType {
        BERNOULLI,
        UNIFORM,
        NORMAL
    }

    enum ExperimentStatus {
        CREATED,
        RUNNING,
        COMPLETED,
        FAILED
    }

    record DistributionSpec(
        DistributionType type,
        String name,
        double mean,
        double variance
    ) {
        DistributionSpec {
            Objects.requireNonNull(type);
            Objects.requireNonNull(name);

            if (name.isBlank()) {
                throw new IllegalArgumentException("Name cannot be blank.");
            }

            if (!Double.isFinite(mean) ||
                !Double.isFinite(variance) ||
                variance < 0) {
                throw new IllegalArgumentException(
                    "Invalid distribution parameters."
                );
            }
        }
    }

    record ExperimentConfig(
        DistributionType distribution,
        List<Integer> sampleSizes,
        int trials,
        double epsilon,
        long seed
    ) {
        ExperimentConfig {
            Objects.requireNonNull(distribution);
            sampleSizes = List.copyOf(sampleSizes);

            if (sampleSizes.isEmpty()) {
                throw new IllegalArgumentException(
                    "Sample sizes cannot be empty."
                );
            }

            int previous = 0;

            for (int n : sampleSizes) {
                if (n <= previous) {
                    throw new IllegalArgumentException(
                        "Sample sizes must be positive and increasing."
                    );
                }
                previous = n;
            }

            if (trials <= 0) {
                throw new IllegalArgumentException(
                    "Trials must be positive."
                );
            }

            if (!Double.isFinite(epsilon) || epsilon <= 0) {
                throw new IllegalArgumentException(
                    "Tolerance must be positive and finite."
                );
            }
        }
    }

    record ExperimentResult(
        int sampleSize,
        int trials,
        double meanAbsoluteError,
        double meanSquaredError,
        double observedProbability,
        double chebyshevBound
    ) {}

    record StrongLawObservation(
        int sampleSize,
        double sampleMean,
        double populationMean,
        double absoluteError
    ) {}

    record ExperimentReport(
        UUID id,
        String distribution,
        double populationMean,
        double populationVariance,
        double epsilon,
        List<ExperimentResult> weakLawResults,
        List<StrongLawObservation> strongLawResults,
        Instant completedAt
    ) {
        ExperimentReport {
            weakLawResults = List.copyOf(weakLawResults);
            strongLawResults = List.copyOf(strongLawResults);
        }
    }

    interface Sampler {
        double sample();
    }

    static class OnlineStatistics {
        private long count;
        private double mean;
        private double m2;

        void add(double value) {
            if (!Double.isFinite(value)) {
                throw new IllegalArgumentException(
                    "Observation must be finite."
                );
            }

            count++;

            double delta = value - mean;
            mean += delta / count;
            double delta2 = value - mean;

            m2 += delta * delta2;
        }

        double mean() {
            if (count == 0) {
                throw new IllegalStateException("No observations.");
            }
            return mean;
        }

        double variance() {
            return count > 1 ? m2 / (count - 1) : 0.0;
        }

        long count() {
            return count;
        }
    }

    static class Experiment {
        private final UUID id = UUID.randomUUID();
        private ExperimentStatus status = ExperimentStatus.CREATED;

        UUID id() {
            return id;
        }

        ExperimentStatus status() {
            return status;
        }

        void transition(ExperimentStatus next) {
            boolean valid = switch (status) {
                case CREATED -> next == ExperimentStatus.RUNNING;
                case RUNNING ->
                    next == ExperimentStatus.COMPLETED ||
                    next == ExperimentStatus.FAILED;
                case COMPLETED, FAILED -> false;
            };

            if (!valid) {
                throw new IllegalStateException(
                    "Invalid experiment transition: " +
                    status + " -> " + next
                );
            }

            status = next;
        }
    }

    static class StatisticalService {
        private final Map<DistributionType, DistributionSpec> specs =
            new EnumMap<>(DistributionType.class);

        StatisticalService() {
            specs.put(
                DistributionType.BERNOULLI,
                new DistributionSpec(
                    DistributionType.BERNOULLI,
                    "Bernoulli(0.5)",
                    0.5,
                    0.25
                )
            );

            specs.put(
                DistributionType.UNIFORM,
                new DistributionSpec(
                    DistributionType.UNIFORM,
                    "Uniform(0,1)",
                    0.5,
                    1.0 / 12.0
                )
            );

            specs.put(
                DistributionType.NORMAL,
                new DistributionSpec(
                    DistributionType.NORMAL,
                    "Normal(0,1)",
                    0.0,
                    1.0
                )
            );
        }

        private Sampler createSampler(
            DistributionType type,
            java.util.Random random
        ) {
            return switch (type) {
                case BERNOULLI ->
                    () -> random.nextDouble() < 0.5 ? 1.0 : 0.0;

                case UNIFORM ->
                    random::nextDouble;

                case NORMAL ->
                    random::nextGaussian;
            };
        }

        private static double chebyshevBound(
            double variance,
            int n,
            double epsilon
        ) {
            return Math.min(
                1.0,
                variance / (n * epsilon * epsilon)
            );
        }

        List<ExperimentResult> runWeakLaw(
            ExperimentConfig config,
            DistributionSpec spec,
            Sampler sampler
        ) {
            List<ExperimentResult> results = new ArrayList<>();

            for (int n : config.sampleSizes()) {
                OnlineStatistics errors = new OnlineStatistics();
                OnlineStatistics squaredErrors = new OnlineStatistics();
                int deviations = 0;

                for (int trial = 0; trial < config.trials(); trial++) {
                    double sum = 0;

                    for (int i = 0; i < n; i++) {
                        sum += sampler.sample();
                    }

                    double error = Math.abs(
                        sum / n - spec.mean()
                    );

                    errors.add(error);
                    squaredErrors.add(error * error);

                    if (error >= config.epsilon()) {
                        deviations++;
                    }
                }

                results.add(new ExperimentResult(
                    n,
                    config.trials(),
                    errors.mean(),
                    squaredErrors.mean(),
                    (double) deviations / config.trials(),
                    chebyshevBound(
                        spec.variance(),
                        n,
                        config.epsilon()
                    )
                ));
            }

            return results;
        }

        List<StrongLawObservation> runStrongLaw(
            ExperimentConfig config,
            DistributionSpec spec,
            Sampler sampler
        ) {
            int maximum = config.sampleSizes()
                .get(config.sampleSizes().size() - 1);

            List<StrongLawObservation> results = new ArrayList<>();
            double sum = 0;

            for (int n = 1; n <= maximum; n++) {
                sum += sampler.sample();

                if (config.sampleSizes().contains(n)) {
                    double mean = sum / n;

                    results.add(new StrongLawObservation(
                        n,
                        mean,
                        spec.mean(),
                        Math.abs(mean - spec.mean())
                    ));
                }
            }

            return results;
        }

        ExperimentReport execute(ExperimentConfig config) {
            DistributionSpec spec = specs.get(config.distribution());

            Experiment experiment = new Experiment();
            experiment.transition(ExperimentStatus.RUNNING);

            try {
                java.util.Random weakRandom =
                    new java.util.Random(config.seed());

                Sampler weakSampler = createSampler(
                    config.distribution(),
                    weakRandom
                );

                List<ExperimentResult> weakResults = runWeakLaw(
                    config,
                    spec,
                    weakSampler
                );

                java.util.Random strongRandom =
                    new java.util.Random(config.seed() + 100);

                List<StrongLawObservation> strongResults =
                    runStrongLaw(
                        config,
                        spec,
                        createSampler(
                            config.distribution(),
                            strongRandom
                        )
                    );

                experiment.transition(ExperimentStatus.COMPLETED);

                return new ExperimentReport(
                    experiment.id(),
                    spec.name(),
                    spec.mean(),
                    spec.variance(),
                    config.epsilon(),
                    weakResults,
                    strongResults,
                    Instant.now()
                );

            } catch (RuntimeException exception) {
                experiment.transition(ExperimentStatus.FAILED);
                throw exception;
            }
        }
    }

    static class ReportWriter {

        static void write(
            ExperimentReport report,
            Path destination
        ) throws IOException {
            StringBuilder json = new StringBuilder();

            json.append("{\n");
            json.append("  \"experimentId\": \"")
                .append(report.id()).append("\",\n");
            json.append("  \"distribution\": \"")
                .append(report.distribution()).append("\",\n");
            json.append("  \"populationMean\": ")
                .append(report.populationMean()).append(",\n");
            json.append("  \"populationVariance\": ")
                .append(report.populationVariance()).append(",\n");
            json.append("  \"epsilon\": ")
                .append(report.epsilon()).append(",\n");
            json.append("  \"weakLawResults\": [\n");

            for (int i = 0; i < report.weakLawResults().size(); i++) {
                ExperimentResult r = report.weakLawResults().get(i);

                json.append("    {")
                    .append("\"sampleSize\": ").append(r.sampleSize())
                    .append(", \"trials\": ").append(r.trials())
                    .append(", \"meanAbsoluteError\": ")
                    .append(r.meanAbsoluteError())
                    .append(", \"meanSquaredError\": ")
                    .append(r.meanSquaredError())
                    .append(", \"observedProbability\": ")
                    .append(r.observedProbability())
                    .append(", \"chebyshevBound\": ")
                    .append(r.chebyshevBound())
                    .append("}");

                if (i + 1 < report.weakLawResults().size()) {
                    json.append(",");
                }

                json.append("\n");
            }

            json.append("  ],\n");
            json.append("  \"completedAt\": \"")
                .append(report.completedAt())
                .append("\"\n");
            json.append("}\n");

            Path absolute = destination.toAbsolutePath();
            Path parent = absolute.getParent();

            Files.createDirectories(parent);

            Path temporary = Files.createTempFile(
                parent,
                "lln-report-",
                ".tmp"
            );

            try {
                Files.writeString(
                    temporary,
                    json.toString(),
                    StandardCharsets.UTF_8,
                    StandardOpenOption.TRUNCATE_EXISTING
                );

                try {
                    Files.move(
                        temporary,
                        absolute,
                        StandardCopyOption.ATOMIC_MOVE,
                        StandardCopyOption.REPLACE_EXISTING
                    );
                } catch (java.nio.file.AtomicMoveNotSupportedException e) {
                    Files.move(
                        temporary,
                        absolute,
                        StandardCopyOption.REPLACE_EXISTING
                    );
                }
            } finally {
                Files.deleteIfExists(temporary);
            }
        }
    }

    static void printReport(ExperimentReport report) {
        System.out.println("\nWEAK LAW OF LARGE NUMBERS");
        System.out.println("Distribution: " + report.distribution());

        System.out.printf(
            "%8s %14s %16s %16s %14s%n",
            "N",
            "MAE",
            "Observed P",
            "Chebyshev",
            "MSE"
        );

        for (ExperimentResult r : report.weakLawResults()) {
            System.out.printf(
                "%8d %14.6f %16.6f %16.6f %14.6f%n",
                r.sampleSize(),
                r.meanAbsoluteError(),
                r.observedProbability(),
                r.chebyshevBound(),
                r.meanSquaredError()
            );
        }

        System.out.println("\nSTRONG LAW OBSERVATIONS");

        for (StrongLawObservation r : report.strongLawResults()) {
            System.out.printf(
                "N=%6d Mean=% .6f Error=%.6f%n",
                r.sampleSize(),
                r.sampleMean(),
                r.absoluteError()
            );
        }
    }

    public static void main(String[] args) {
        try {
            ExperimentConfig config = new ExperimentConfig(
                DistributionType.BERNOULLI,
                List.of(10, 50, 100, 500, 1000, 5000, 10000),
                1000,
                0.05,
                42
            );

            StatisticalService service = new StatisticalService();
            ExperimentReport report = service.execute(config);

            printReport(report);

            ReportWriter.write(
                report,
                Path.of("lln_results_java.json")
            );

            System.out.println(
                "\nReport saved to lln_results_java.json"
            );

            // Constant observations are a zero-variance edge case.
            OnlineStatistics constant = new OnlineStatistics();

            for (int i = 0; i < 100; i++) {
                constant.add(7.0);
            }

            System.out.println("\nCONSTANT VARIABLE EDGE CASE");
            System.out.println("Mean: " + constant.mean());
            System.out.println("Variance: " + constant.variance());

        } catch (IllegalArgumentException |
                 IllegalStateException |
                 IOException exception) {
            System.err.println(
                "Experiment failed: " + exception.getMessage()
            );
            System.exit(1);
        }
    }
}
