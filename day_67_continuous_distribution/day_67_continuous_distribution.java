import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.LinkedHashMap;
import java.util.Objects;
import java.util.SplittableRandom;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

/*
 * Continuous Distributions
 *
 * Enterprise-oriented reliability and service-capacity analysis.
 *
 * Models:
 * 1. Uniform: uncertain processing duration within known bounds.
 * 2. Exponential: time between independent service requests.
 * 3. Normal: measurement variation around an operational target.
 *
 * Java 17, no third-party dependencies.
 */
public class ContinuousDistributions {

    enum DistributionType {
        UNIFORM,
        EXPONENTIAL,
        NORMAL
    }

    static class DistributionException extends RuntimeException {
        DistributionException(String message) {
            super(message);
        }
    }

    static void validateFinite(double value, String field) {
        if (!Double.isFinite(value)) {
            throw new DistributionException(
                field + " must be finite."
            );
        }
    }

    static void validateProbability(double p) {
        validateFinite(p, "Probability");

        if (p < 0 || p > 1) {
            throw new DistributionException(
                "Probability must be between 0 and 1."
            );
        }
    }

    static void validateSampleSize(int size) {
        if (size <= 0) {
            throw new DistributionException(
                "Sample size must be positive."
            );
        }
    }

    interface ContinuousDistribution {
        double pdf(double x);

        double cdf(double x);

        double quantile(double p);

        double sample(SplittableRandom random);

        double mean();

        double variance();

        default double probabilityBetween(
            double lower,
            double upper
        ) {
            validateFinite(lower, "Lower bound");
            validateFinite(upper, "Upper bound");

            if (lower > upper) {
                throw new DistributionException(
                    "Invalid interval."
                );
            }

            return cdf(upper) - cdf(lower);
        }
    }

    record Interval(double lower, double upper) {
        Interval {
            validateFinite(lower, "Lower bound");
            validateFinite(upper, "Upper bound");

            if (lower > upper) {
                throw new DistributionException(
                    "Invalid interval."
                );
            }
        }
    }

    record DistributionReport(
        DistributionType type,
        int sampleCount,
        double theoreticalMean,
        double empiricalMean,
        double theoreticalVariance,
        double empiricalVariance,
        double standardDeviation,
        double minimum,
        double maximum,
        double theoreticalProbability,
        double observedProbability,
        double confidenceLower,
        double confidenceUpper,
        double ksDistance
    ) {}

    static final class UniformDistribution
        implements ContinuousDistribution {

        private final double a;
        private final double b;

        UniformDistribution(double a, double b) {
            validateFinite(a, "a");
            validateFinite(b, "b");

            if (a >= b) {
                throw new DistributionException(
                    "Uniform distribution requires a < b."
                );
            }

            this.a = a;
            this.b = b;
        }

        @Override
        public double pdf(double x) {
            validateFinite(x, "x");

            return x >= a && x <= b
                ? 1.0 / (b - a)
                : 0.0;
        }

        @Override
        public double cdf(double x) {
            validateFinite(x, "x");

            if (x < a) return 0;
            if (x >= b) return 1;

            return (x - a) / (b - a);
        }

        @Override
        public double quantile(double p) {
            validateProbability(p);

            return a + p * (b - a);
        }

        @Override
        public double sample(SplittableRandom random) {
            return random.nextDouble(a, b);
        }

        @Override
        public double mean() {
            return (a + b) / 2;
        }

        @Override
        public double variance() {
            return (b - a) * (b - a) / 12;
        }
    }

    static final class ExponentialDistribution
        implements ContinuousDistribution {

        private final double rate;

        ExponentialDistribution(double rate) {
            validateFinite(rate, "Rate");

            if (rate <= 0) {
                throw new DistributionException(
                    "Rate must be positive."
                );
            }

            this.rate = rate;
        }

        @Override
        public double pdf(double x) {
            validateFinite(x, "x");

            return x < 0
                ? 0
                : rate * Math.exp(-rate * x);
        }

        @Override
        public double cdf(double x) {
            validateFinite(x, "x");

            return x <= 0
                ? 0
                : -Math.expm1(-rate * x);
        }

        public double survival(double x) {
            validateFinite(x, "x");

            return x <= 0
                ? 1
                : Math.exp(-rate * x);
        }

        public double hazard() {
            return rate;
        }

        @Override
        public double quantile(double p) {
            validateProbability(p);

            if (p == 1) {
                return Double.POSITIVE_INFINITY;
            }

            return -Math.log1p(-p) / rate;
        }

        @Override
        public double sample(SplittableRandom random) {
            // Inverse transform sampling.
            double u = random.nextDouble();

            return -Math.log1p(-u) / rate;
        }

        @Override
        public double mean() {
            return 1 / rate;
        }

        @Override
        public double variance() {
            return 1 / (rate * rate);
        }
    }

    static double standardNormalCDF(double z) {
        return 0.5 * (1 + erf(z / Math.sqrt(2)));
    }

    /*
     * Numerical approximation to the error function.
     */
    static double erf(double x) {
        double sign = x < 0 ? -1 : 1;
        x = Math.abs(x);

        double t = 1 / (1 + 0.3275911 * x);

        double polynomial =
            (((((1.061405429 * t - 1.453152027) * t) +
                1.421413741) * t - 0.284496736) * t +
                0.254829592) * t;

        return sign * (1 - polynomial * Math.exp(-x * x));
    }

    /*
     * Acklam inverse standard normal approximation.
     */
    static double standardNormalQuantile(double p) {
        validateProbability(p);

        if (p == 0) return Double.NEGATIVE_INFINITY;
        if (p == 1) return Double.POSITIVE_INFINITY;

        double[] a = {
            -39.69683028665376,
            220.9460984245205,
            -275.9285104469687,
            138.3577518672690,
            -30.66479806614716,
            2.506628277459239
        };

        double[] b = {
            -54.47609879822406,
            161.5858368580409,
            -155.6989798598866,
            66.80131188771972,
            -13.28068155288572
        };

        double[] c = {
            -0.007784894002430293,
            -0.3223964580411365,
            -2.400758277161838,
            -2.549732539343734,
            4.374664141464968,
            2.938163982698783
        };

        double[] d = {
            0.007784695709041462,
            0.3224671290700398,
            2.445134137142996,
            3.754408661907416
        };

        double low = 0.02425;
        double high = 1 - low;

        double x;

        if (p < low) {
            double q = Math.sqrt(-2 * Math.log(p));

            x = (((((c[0] * q + c[1]) * q + c[2]) * q +
                c[3]) * q + c[4]) * q + c[5]) /
                ((((d[0] * q + d[1]) * q + d[2]) * q +
                    d[3]) * q + 1);

        } else if (p > high) {
            double q = Math.sqrt(-2 * Math.log1p(-p));

            x = -(((((c[0] * q + c[1]) * q + c[2]) * q +
                c[3]) * q + c[4]) * q + c[5]) /
                ((((d[0] * q + d[1]) * q + d[2]) * q +
                    d[3]) * q + 1);

        } else {
            double q = p - 0.5;
            double r = q * q;

            x = (((((a[0] * r + a[1]) * r + a[2]) * r +
                a[3]) * r + a[4]) * r + a[5]) * q /
                (((((b[0] * r + b[1]) * r + b[2]) * r +
                    b[3]) * r + b[4]) * r + 1);
        }

        if (p > 1e-12 && p < 1 - 1e-12) {
            double error = standardNormalCDF(x) - p;

            double density = Math.exp(-0.5 * x * x) /
                Math.sqrt(2 * Math.PI);

            if (density > 1e-300) {
                x -= error / density;
            }
        }

        return x;
    }

    static final class NormalDistribution
        implements ContinuousDistribution {

        private final double mu;
        private final double sigma;

        NormalDistribution(double mu, double sigma) {
            validateFinite(mu, "Mean");
            validateFinite(sigma, "Standard deviation");

            if (sigma <= 0) {
                throw new DistributionException(
                    "Standard deviation must be positive."
                );
            }

            this.mu = mu;
            this.sigma = sigma;
        }

        @Override
        public double pdf(double x) {
            validateFinite(x, "x");

            double z = (x - mu) / sigma;

            return Math.exp(-0.5 * z * z) /
                (sigma * Math.sqrt(2 * Math.PI));
        }

        @Override
        public double cdf(double x) {
            validateFinite(x, "x");

            return standardNormalCDF((x - mu) / sigma);
        }

        @Override
        public double quantile(double p) {
            return mu + sigma * standardNormalQuantile(p);
        }

        @Override
        public double sample(SplittableRandom random) {
            /*
             * Box-Muller transformation.
             * SplittableRandom does not provide a Gaussian method.
             */
            double u1;

            do {
                u1 = random.nextDouble();
            } while (u1 == 0);

            double u2 = random.nextDouble();

            double z = Math.sqrt(-2 * Math.log(u1)) *
                Math.cos(2 * Math.PI * u2);

            return mu + sigma * z;
        }

        @Override
        public double mean() {
            return mu;
        }

        @Override
        public double variance() {
            return sigma * sigma;
        }

        public double standardize(double x) {
            validateFinite(x, "x");
            return (x - mu) / sigma;
        }
    }

    /*
     * Online statistics avoid retaining every observation.
     */
    static final class OnlineStatistics {
        private long count;
        private double mean;
        private double m2;
        private double minimum = Double.POSITIVE_INFINITY;
        private double maximum = Double.NEGATIVE_INFINITY;

        void add(double value) {
            validateFinite(value, "Observation");

            count++;

            double delta = value - mean;
            mean += delta / count;

            double delta2 = value - mean;
            m2 += delta * delta2;

            minimum = Math.min(minimum, value);
            maximum = Math.max(maximum, value);
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

        double minimum() {
            return minimum;
        }

        double maximum() {
            return maximum;
        }
    }

    static final class SimulationService {

        private final ContinuousDistribution distribution;
        private final DistributionType type;
        private final Interval interval;

        SimulationService(
            DistributionType type,
            ContinuousDistribution distribution,
            Interval interval
        ) {
            this.type = Objects.requireNonNull(type);
            this.distribution = Objects.requireNonNull(distribution);
            this.interval = Objects.requireNonNull(interval);
        }

        DistributionReport execute(
            int sampleCount,
            long seed
        ) {
            validateSampleSize(sampleCount);

            SplittableRandom random = new SplittableRandom(seed);

            OnlineStatistics stats = new OnlineStatistics();

            List<Double> observations = new ArrayList<>(sampleCount);

            int inside = 0;

            for (int i = 0; i < sampleCount; i++) {
                double value = distribution.sample(random);

                stats.add(value);
                observations.add(value);

                if (value >= interval.lower() &&
                    value <= interval.upper()) {
                    inside++;
                }
            }

            double z = 1.96;

            double margin = z * stats.standardDeviation() /
                Math.sqrt(sampleCount);

            return new DistributionReport(
                type,
                sampleCount,
                distribution.mean(),
                stats.mean(),
                distribution.variance(),
                stats.variance(),
                stats.standardDeviation(),
                stats.minimum(),
                stats.maximum(),
                distribution.probabilityBetween(
                    interval.lower(),
                    interval.upper()
                ),
                (double) inside / sampleCount,
                stats.mean() - margin,
                stats.mean() + margin,
                ksDistance(observations)
            );
        }

        private double ksDistance(List<Double> observations) {
            List<Double> sorted = new ArrayList<>(observations);
            Collections.sort(sorted);

            double n = sorted.size();
            double maximum = 0;

            for (int i = 0; i < sorted.size(); i++) {
                double theoretical = distribution.cdf(sorted.get(i));

                double dPlus = (i + 1.0) / n - theoretical;
                double dMinus = theoretical - i / n;

                maximum = Math.max(
                    maximum,
                    Math.max(dPlus, dMinus)
                );
            }

            return maximum;
        }
    }

    /*
     * Independent jobs can run concurrently.
     * Each task owns its random generator and statistics.
     */
    static Map<DistributionType, DistributionReport> executeBatch(
        int sampleCount
    ) {
        ExecutorService executor = Executors.newFixedThreadPool(3);

        try {
            Map<DistributionType, CompletableFuture<DistributionReport>>
                tasks = new LinkedHashMap<>();

            tasks.put(
                DistributionType.UNIFORM,
                CompletableFuture.supplyAsync(
                    () -> new SimulationService(
                        DistributionType.UNIFORM,
                        new UniformDistribution(0, 100),
                        new Interval(20, 80)
                    ).execute(sampleCount, 42),
                    executor
                )
            );

            tasks.put(
                DistributionType.EXPONENTIAL,
                CompletableFuture.supplyAsync(
                    () -> new SimulationService(
                        DistributionType.EXPONENTIAL,
                        new ExponentialDistribution(0.2),
                        new Interval(1, 5)
                    ).execute(sampleCount, 42),
                    executor
                )
            );

            tasks.put(
                DistributionType.NORMAL,
                CompletableFuture.supplyAsync(
                    () -> new SimulationService(
                        DistributionType.NORMAL,
                        new NormalDistribution(50, 10),
                        new Interval(40, 60)
                    ).execute(sampleCount, 42),
                    executor
                )
            );

            CompletableFuture.allOf(
                tasks.values().toArray(CompletableFuture[]::new)
            ).join();

            Map<DistributionType, DistributionReport> reports =
                new LinkedHashMap<>();

            tasks.forEach(
                (type, future) -> reports.put(type, future.join())
            );

            return reports;

        } catch (CompletionException error) {
            throw new DistributionException(
                "Batch simulation failed: " + error.getCause()
            );
        } finally {
            executor.shutdown();

            try {
                if (!executor.awaitTermination(30, TimeUnit.SECONDS)) {
                    executor.shutdownNow();
                }
            } catch (InterruptedException error) {
                executor.shutdownNow();
                Thread.currentThread().interrupt();

                throw new DistributionException(
                    "Simulation interrupted."
                );
            }
        }
    }

    static void printReport(DistributionReport report) {
        System.out.println("\n======================================");
        System.out.println(report.type());
        System.out.println("======================================");

        System.out.printf(
            "Sample count:              %d%n",
            report.sampleCount()
        );

        System.out.printf(
            "Theoretical mean:          %.6f%n",
            report.theoreticalMean()
        );

        System.out.printf(
            "Empirical mean:            %.6f%n",
            report.empiricalMean()
        );

        System.out.printf(
            "Theoretical variance:      %.6f%n",
            report.theoreticalVariance()
        );

        System.out.printf(
            "Empirical variance:        %.6f%n",
            report.empiricalVariance()
        );

        System.out.printf(
            "Standard deviation:        %.6f%n",
            report.standardDeviation()
        );

        System.out.printf(
            "Minimum:                   %.6f%n",
            report.minimum()
        );

        System.out.printf(
            "Maximum:                   %.6f%n",
            report.maximum()
        );

        System.out.printf(
            "Theoretical interval P:    %.6f%n",
            report.theoreticalProbability()
        );

        System.out.printf(
            "Empirical interval P:      %.6f%n",
            report.observedProbability()
        );

        System.out.printf(
            "Mean confidence interval:  [%.6f, %.6f]%n",
            report.confidenceLower(),
            report.confidenceUpper()
        );

        System.out.printf(
            "Empirical KS distance:     %.6f%n",
            report.ksDistance()
        );
    }

    static void runTests() {
        UniformDistribution uniform = new UniformDistribution(0, 10);
        ExponentialDistribution exponential =
            new ExponentialDistribution(0.5);
        NormalDistribution normal = new NormalDistribution(100, 15);

        assert Math.abs(uniform.pdf(5) - 0.1) < 1e-9;
        assert Math.abs(uniform.cdf(5) - 0.5) < 1e-9;
        assert Math.abs(uniform.quantile(0.5) - 5) < 1e-9;

        assert exponential.pdf(-1) == 0;
        assert Math.abs(
            exponential.cdf(2) - (1 - Math.exp(-1))
        ) < 1e-9;

        assert Math.abs(
            exponential.quantile(0.5) - Math.log(2) / 0.5
        ) < 1e-9;

        assert Math.abs(normal.cdf(100) - 0.5) < 1e-6;
        assert Math.abs(normal.quantile(0.5) - 100) < 1e-6;
        assert Math.abs(normal.standardize(115) - 1) < 1e-9;

        assert Math.abs(
            standardNormalQuantile(0.975) - 1.9599639845
        ) < 1e-7;

        List<Runnable> invalidCases = List.of(
            () -> new UniformDistribution(5, 5),
            () -> new ExponentialDistribution(0),
            () -> new NormalDistribution(0, -1),
            () -> uniform.quantile(1.5),
            () -> uniform.probabilityBetween(10, 5)
        );

        for (Runnable operation : invalidCases) {
            boolean rejected = false;

            try {
                operation.run();
            } catch (DistributionException error) {
                rejected = true;
            }

            if (!rejected) {
                throw new AssertionError(
                    "Invalid input was accepted."
                );
            }
        }

        System.out.println("All Java validation tests passed.");
    }

    public static void main(String[] args) {
        try {
            System.out.println(
                "CONTINUOUS DISTRIBUTIONS: ENTERPRISE ANALYSIS"
            );

            runTests();

            Map<DistributionType, DistributionReport> reports =
                executeBatch(100000);

            reports.values().forEach(
                ContinuousDistributions::printReport
            );

            System.out.println("\nQUANTILE COMPARISON");

            ContinuousDistribution[] distributions = {
                new UniformDistribution(0, 100),
                new ExponentialDistribution(0.2),
                new NormalDistribution(50, 10)
            };

            double[] probabilities = {
                0.05, 0.25, 0.50, 0.75, 0.95
            };

            System.out.printf(
                "%12s%18s%18s%18s%n",
                "Probability",
                "Uniform",
                "Exponential",
                "Normal"
            );

            for (double p : probabilities) {
                System.out.printf(
                    "%12.2f",
                    p
                );

                for (ContinuousDistribution distribution :
                    distributions) {

                    System.out.printf(
                        "%18.4f",
                        distribution.quantile(p)
                    );
                }

                System.out.println();
            }

            ExponentialDistribution arrivals =
                new ExponentialDistribution(0.2);

            double t = 3;
            double s = 5;

            double conditionalSurvival =
                arrivals.survival(t + s) / arrivals.survival(t);

            System.out.println("\nSERVICE ARRIVAL ANALYSIS");

            System.out.printf(
                "Arrival rate: %.4f per time unit%n",
                arrivals.hazard()
            );

            System.out.printf(
                "Expected waiting time: %.4f%n",
                arrivals.mean()
            );

            System.out.printf(
                "Conditional survival: %.6f%n",
                conditionalSurvival
            );

            System.out.printf(
                "Unconditional survival: %.6f%n",
                arrivals.survival(s)
            );

            NormalDistribution measurements =
                new NormalDistribution(100, 15);

            System.out.println("\nMEASUREMENT QUALITY CONTROL");

            System.out.printf(
                "Measurement 130 Z-score: %.4f%n",
                measurements.standardize(130)
            );

            System.out.printf(
                "Probability measurement <= 130: %.6f%n",
                measurements.cdf(130)
            );

            System.out.println("\nEnterprise analysis completed.");

        } catch (Exception error) {
            System.err.println(
                "Execution failed: " + error.getMessage()
            );

            System.exit(1);
        }
    }
}
