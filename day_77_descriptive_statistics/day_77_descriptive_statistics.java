import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeMap;
import java.util.stream.Collectors;

/**
 * Descriptive Statistics Enterprise Analytics System.
 *
 * Java 17 implementation covering:
 * - Mean, median and mode
 * - Population and sample variance
 * - Standard deviation
 * - Quantiles and percentiles
 * - Interquartile range
 * - Outlier identification
 * - Frequency distributions
 * - Dataset validation
 * - Immutable statistical reports
 * - Enterprise data-quality policies
 * - Service-based statistical processing
 *
 * Compile:
 * javac DescriptiveStatistics.java
 *
 * Run:
 * java DescriptiveStatistics
 */

public class DescriptiveStatistics {

    enum VarianceType {
        POPULATION,
        SAMPLE
    }

    enum QualityStatus {
        ACCEPTED,
        REJECTED,
        WARNING
    }

    record Measurement(
        String department,
        String metric,
        double value
    ) {
        Measurement {
            if (department == null || department.isBlank()) {
                throw new IllegalArgumentException(
                    "Department is required."
                );
            }

            if (metric == null || metric.isBlank()) {
                throw new IllegalArgumentException(
                    "Metric is required."
                );
            }

            if (!Double.isFinite(value)) {
                throw new IllegalArgumentException(
                    "Measurement must be finite."
                );
            }
        }
    }

    record QualityResult(
        QualityStatus status,
        String message,
        int acceptedRecords,
        int rejectedRecords
    ) {}

    record StatisticsReport(
        String metric,
        int count,
        double mean,
        double median,
        List<Double> modes,
        double populationVariance,
        Double sampleVariance,
        double populationStandardDeviation,
        Double sampleStandardDeviation,
        double minimum,
        double maximum,
        double q1,
        double q2,
        double q3,
        double iqr,
        double p90,
        double p95,
        List<Double> outliers,
        Map<Double, Long> frequencies
    ) {
        StatisticsReport {
            modes = List.copyOf(modes);
            outliers = List.copyOf(outliers);
            frequencies = Map.copyOf(frequencies);
        }
    }

    interface AnalysisPolicy {
        QualityResult evaluate(
            List<Measurement> measurements
        );
    }

    static final class MeasurementQualityPolicy
            implements AnalysisPolicy {

        private final int minimumRecords;
        private final double minimumAllowed;
        private final double maximumAllowed;

        MeasurementQualityPolicy(
            int minimumRecords,
            double minimumAllowed,
            double maximumAllowed
        ) {
            if (minimumRecords < 1) {
                throw new IllegalArgumentException(
                    "Minimum records must be positive."
                );
            }

            if (
                !Double.isFinite(minimumAllowed) ||
                !Double.isFinite(maximumAllowed) ||
                minimumAllowed > maximumAllowed
            ) {
                throw new IllegalArgumentException(
                    "Invalid measurement boundaries."
                );
            }

            this.minimumRecords = minimumRecords;
            this.minimumAllowed = minimumAllowed;
            this.maximumAllowed = maximumAllowed;
        }

        @Override
        public QualityResult evaluate(
            List<Measurement> measurements
        ) {
            Objects.requireNonNull(measurements);

            int accepted = 0;
            int rejected = 0;

            for (Measurement measurement : measurements) {
                if (
                    measurement.value() >= minimumAllowed &&
                    measurement.value() <= maximumAllowed
                ) {
                    accepted++;
                } else {
                    rejected++;
                }
            }

            if (rejected > 0) {
                return new QualityResult(
                    QualityStatus.REJECTED,
                    "Measurements outside permitted boundaries.",
                    accepted,
                    rejected
                );
            }

            if (accepted < minimumRecords) {
                return new QualityResult(
                    QualityStatus.WARNING,
                    "Insufficient observations for reporting.",
                    accepted,
                    0
                );
            }

            return new QualityResult(
                QualityStatus.ACCEPTED,
                "Data quality requirements satisfied.",
                accepted,
                0
            );
        }
    }

    static final class StatisticalDataset {

        private final String metric;
        private final List<Double> values;
        private final Map<Double, Long> frequencies;

        StatisticalDataset(
            String metric,
            List<Measurement> measurements
        ) {
            if (metric == null || metric.isBlank()) {
                throw new IllegalArgumentException(
                    "Metric name is required."
                );
            }

            if (measurements == null || measurements.isEmpty()) {
                throw new IllegalArgumentException(
                    "Dataset cannot be empty."
                );
            }

            this.metric = metric;

            this.values = measurements.stream()
                .filter(m -> metric.equals(m.metric()))
                .map(Measurement::value)
                .sorted()
                .collect(Collectors.toCollection(ArrayList::new));

            if (this.values.isEmpty()) {
                throw new IllegalArgumentException(
                    "No observations found for metric: " + metric
                );
            }

            this.frequencies = this.values.stream()
                .collect(Collectors.groupingBy(
                    value -> value,
                    TreeMap::new,
                    Collectors.counting()
                ));
        }

        int count() {
            return values.size();
        }

        double mean() {
            // Compensated summation reduces floating-point error.
            double sum = 0.0;
            double compensation = 0.0;

            for (double value : values) {
                double adjusted = value - compensation;
                double temporary = sum + adjusted;

                compensation = (temporary - sum) - adjusted;
                sum = temporary;
            }

            return sum / count();
        }

        double median() {
            int n = count();
            int middle = n / 2;

            if (n % 2 == 1) {
                return values.get(middle);
            }

            return (
                values.get(middle - 1) +
                values.get(middle)
            ) / 2.0;
        }

        List<Double> mode() {
            long maximum = frequencies.values()
                .stream()
                .mapToLong(Long::longValue)
                .max()
                .orElse(0);

            if (maximum <= 1) {
                return List.of();
            }

            return frequencies.entrySet()
                .stream()
                .filter(entry -> entry.getValue() == maximum)
                .map(Map.Entry::getKey)
                .toList();
        }

        double variance(VarianceType type) {
            if (
                type == VarianceType.SAMPLE &&
                count() < 2
            ) {
                throw new IllegalStateException(
                    "Sample variance requires at least two observations."
                );
            }

            double average = mean();

            double sum = 0.0;
            double compensation = 0.0;

            for (double value : values) {
                double difference = value - average;
                double term = difference * difference;

                double adjusted = term - compensation;
                double temporary = sum + adjusted;

                compensation = (temporary - sum) - adjusted;
                sum = temporary;
            }

            int denominator = type == VarianceType.SAMPLE
                ? count() - 1
                : count();

            return sum / denominator;
        }

        double standardDeviation(VarianceType type) {
            return Math.sqrt(variance(type));
        }

        double quantile(double probability) {
            if (
                !Double.isFinite(probability) ||
                probability < 0 ||
                probability > 1
            ) {
                throw new IllegalArgumentException(
                    "Probability must be between 0 and 1."
                );
            }

            double position = (count() - 1) * probability;

            int lower = (int) Math.floor(position);
            int upper = (int) Math.ceil(position);

            if (lower == upper) {
                return values.get(lower);
            }

            double fraction = position - lower;

            return values.get(lower) * (1 - fraction)
                + values.get(upper) * fraction;
        }

        double percentile(double percentage) {
            if (
                !Double.isFinite(percentage) ||
                percentage < 0 ||
                percentage > 100
            ) {
                throw new IllegalArgumentException(
                    "Percentile must be between 0 and 100."
                );
            }

            return quantile(percentage / 100.0);
        }

        double interquartileRange() {
            return quantile(0.75) - quantile(0.25);
        }

        List<Double> outliers() {
            double q1 = quantile(0.25);
            double q3 = quantile(0.75);

            double spread = q3 - q1;

            double lower = q1 - 1.5 * spread;
            double upper = q3 + 1.5 * spread;

            return values.stream()
                .filter(value -> value < lower || value > upper)
                .toList();
        }

        StatisticsReport report() {
            return new StatisticsReport(
                metric,
                count(),
                mean(),
                median(),
                mode(),
                variance(VarianceType.POPULATION),
                count() >= 2
                    ? variance(VarianceType.SAMPLE)
                    : null,
                standardDeviation(VarianceType.POPULATION),
                count() >= 2
                    ? standardDeviation(VarianceType.SAMPLE)
                    : null,
                values.get(0),
                values.get(count() - 1),
                quantile(0.25),
                quantile(0.50),
                quantile(0.75),
                interquartileRange(),
                percentile(90),
                percentile(95),
                outliers(),
                frequencies
            );
        }
    }

    static final class AnalyticsService {

        private final AnalysisPolicy policy;

        AnalyticsService(AnalysisPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        StatisticsReport generateReport(
            String metric,
            List<Measurement> measurements
        ) {
            QualityResult quality = policy.evaluate(measurements);

            System.out.println("DATA QUALITY ASSESSMENT");
            System.out.println("-----------------------");
            System.out.println("Status: " + quality.status());
            System.out.println("Message: " + quality.message());
            System.out.println(
                "Accepted: " + quality.acceptedRecords()
            );
            System.out.println(
                "Rejected: " + quality.rejectedRecords()
            );

            if (quality.status() != QualityStatus.ACCEPTED) {
                throw new IllegalStateException(
                    "Statistical report generation blocked by data policy."
                );
            }

            StatisticalDataset dataset =
                new StatisticalDataset(metric, measurements);

            return dataset.report();
        }
    }

    private static void printReport(StatisticsReport report) {
        System.out.println("\nENTERPRISE STATISTICAL REPORT");
        System.out.println("=============================");

        System.out.println("Metric: " + report.metric());
        System.out.println("Observations: " + report.count());

        System.out.printf("Mean: %.4f%n", report.mean());
        System.out.printf("Median: %.4f%n", report.median());

        System.out.println("Mode: " + report.modes());

        System.out.printf(
            "Population variance: %.4f%n",
            report.populationVariance()
        );

        System.out.println(
            "Sample variance: " + report.sampleVariance()
        );

        System.out.printf(
            "Population standard deviation: %.4f%n",
            report.populationStandardDeviation()
        );

        System.out.println(
            "Sample standard deviation: "
                + report.sampleStandardDeviation()
        );

        System.out.printf("Minimum: %.4f%n", report.minimum());
        System.out.printf("Maximum: %.4f%n", report.maximum());

        System.out.printf("Q1: %.4f%n", report.q1());
        System.out.printf("Q2: %.4f%n", report.q2());
        System.out.printf("Q3: %.4f%n", report.q3());

        System.out.printf("IQR: %.4f%n", report.iqr());

        System.out.printf("P90: %.4f%n", report.p90());
        System.out.printf("P95: %.4f%n", report.p95());

        System.out.println("Outliers: " + report.outliers());

        System.out.println("Frequency distribution:");

        report.frequencies().forEach(
            (value, frequency) ->
                System.out.println(value + " -> " + frequency)
        );
    }

    private static void runTests() {
        List<Measurement> testData = List.of(
            new Measurement("Operations", "response_time", 2),
            new Measurement("Operations", "response_time", 4),
            new Measurement("Operations", "response_time", 4),
            new Measurement("Operations", "response_time", 4),
            new Measurement("Operations", "response_time", 5),
            new Measurement("Operations", "response_time", 5),
            new Measurement("Operations", "response_time", 7),
            new Measurement("Operations", "response_time", 9)
        );

        StatisticalDataset dataset =
            new StatisticalDataset("response_time", testData);

        assert Math.abs(dataset.mean() - 5.0) < 0.000001;
        assert Math.abs(dataset.median() - 4.5) < 0.000001;
        assert dataset.mode().equals(List.of(4.0));
        assert Math.abs(dataset.variance(
            VarianceType.POPULATION
        ) - 4.0) < 0.000001;

        assert Math.abs(dataset.quantile(0.25) - 4.0)
            < 0.000001;

        assert Math.abs(dataset.quantile(0.75) - 5.5)
            < 0.000001;

        System.out.println("\nAll statistical assertions passed.");
    }

    public static void main(String[] args) {

        List<Measurement> measurements = List.of(
            new Measurement("Operations", "response_time", 12),
            new Measurement("Operations", "response_time", 15),
            new Measurement("Operations", "response_time", 18),
            new Measurement("Operations", "response_time", 20),
            new Measurement("Operations", "response_time", 15),
            new Measurement("Operations", "response_time", 22),
            new Measurement("Operations", "response_time", 25),
            new Measurement("Operations", "response_time", 18),
            new Measurement("Operations", "response_time", 30),
            new Measurement("Operations", "response_time", 35),
            new Measurement("Operations", "response_time", 18),
            new Measurement("Operations", "response_time", 40),
            new Measurement("Operations", "response_time", 45),
            new Measurement("Operations", "response_time", 50),
            new Measurement("Operations", "response_time", 55),
            new Measurement("Operations", "response_time", 60)
        );

        try {
            AnalysisPolicy policy =
                new MeasurementQualityPolicy(
                    5,
                    0,
                    1000
                );

            AnalyticsService service =
                new AnalyticsService(policy);

            StatisticsReport report =
                service.generateReport(
                    "response_time",
                    measurements
                );

            printReport(report);

            runTests();

            // Demonstrate a policy rejection.
            List<Measurement> invalidMeasurements = List.of(
                new Measurement(
                    "Operations",
                    "response_time",
                    -10
                )
            );

            try {
                service.generateReport(
                    "response_time",
                    invalidMeasurements
                );
            } catch (IllegalStateException error) {
                System.out.println(
                    "\nExpected policy rejection: "
                        + error.getMessage()
                );
            }

        } catch (Exception error) {
            System.err.println(
                "Analytics processing failed: "
                    + error.getMessage()
            );

            System.exit(1);
        }
    }
}
