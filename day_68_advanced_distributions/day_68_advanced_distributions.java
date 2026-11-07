import java.util.*;
import java.util.function.DoubleUnaryOperator;

/**
 * Advanced Distributions
 *
 * Poisson, Gamma, Beta and Chi-square distributions.
 *
 * Java 17, no external dependencies.
 *
 * Includes:
 * - Probability mass and density functions
 * - Cumulative distribution functions
 * - Numerical special functions
 * - Random sampling
 * - Bayesian updating
 * - Chi-square goodness-of-fit testing
 * - Statistical simulation and validation
 */
public class AdvancedDistributions {

    private static final double EPSILON = 1e-12;
    private static final int MAX_ITERATIONS = 10000;

    static class StatisticalException extends IllegalArgumentException {
        StatisticalException(String message) {
            super(message);
        }
    }

    static void positive(double value, String name) {
        if (!Double.isFinite(value) || value <= 0) {
            throw new StatisticalException(
                name + " must be finite and positive."
            );
        }
    }

    static void nonnegative(double value, String name) {
        if (!Double.isFinite(value) || value < 0) {
            throw new StatisticalException(
                name + " must be finite and nonnegative."
            );
        }
    }

    static double clamp(double value) {
        return Math.max(0, Math.min(1, value));
    }

    /**
     * Lanczos approximation of the logarithm of the gamma function.
     */
    static double logGamma(double z) {
        double[] coefficients = {
            676.5203681218851,
            -1259.1392167224028,
            771.3234287776531,
            -176.6150291621406,
            12.507343278686905,
            -0.13857109526572012,
            9.984369578019572e-6,
            1.5056327351493116e-7
        };

        if (!Double.isFinite(z) || z <= 0) {
            throw new StatisticalException(
                "Log-gamma requires positive input."
            );
        }

        if (z < 0.5) {
            return Math.log(Math.PI)
                - Math.log(Math.sin(Math.PI * z))
                - logGamma(1 - z);
        }

        z -= 1;

        double x = 0.9999999999998099;

        for (int i = 0; i < coefficients.length; i++) {
            x += coefficients[i] / (z + i + 1);
        }

        double t = z + coefficients.length - 0.5;

        return 0.9189385332046727
            + (z + 0.5) * Math.log(t)
            - t
            + Math.log(x);
    }

    static double regularizedGammaP(double a, double x) {
        positive(a, "Shape");
        nonnegative(x, "x");

        if (x == 0) return 0;
        if (Double.isInfinite(x)) return 1;

        double factor = Math.exp(
            a * Math.log(x) - x - logGamma(a)
        );

        if (x < a + 1) {
            double term = 1 / a;
            double sum = term;
            double ap = a;

            for (int i = 0; i < MAX_ITERATIONS; i++) {
                ap++;
                term *= x / ap;
                sum += term;

                if (Math.abs(term) <= Math.abs(sum) * EPSILON) {
                    return clamp(factor * sum);
                }
            }

            throw new ArithmeticException(
                "Gamma series did not converge."
            );
        }

        double b = x + 1 - a;
        double c = 1e300;
        double d = 1 / b;
        double h = d;

        for (int i = 1; i <= MAX_ITERATIONS; i++) {
            double an = -i * (i - a);
            b += 2;

            d = an * d + b;
            if (Math.abs(d) < 1e-300) d = 1e-300;

            c = b + an / c;
            if (Math.abs(c) < 1e-300) c = 1e-300;

            d = 1 / d;

            double delta = d * c;
            h *= delta;

            if (Math.abs(delta - 1) <= EPSILON) {
                return clamp(1 - factor * h);
            }
        }

        throw new ArithmeticException(
            "Gamma continued fraction did not converge."
        );
    }

    static double betaFraction(double a, double b, double x) {
        double qab = a + b;
        double qap = a + 1;
        double qam = a - 1;

        double c = 1;
        double d = 1 - qab * x / qap;

        if (Math.abs(d) < 1e-300) d = 1e-300;

        d = 1 / d;
        double h = d;

        for (int m = 1; m <= MAX_ITERATIONS; m++) {
            int m2 = 2 * m;

            double term = m * (b - m) * x
                / ((qam + m2) * (a + m2));

            d = 1 + term * d;
            if (Math.abs(d) < 1e-300) d = 1e-300;

            c = 1 + term / c;
            if (Math.abs(c) < 1e-300) c = 1e-300;

            d = 1 / d;
            h *= d * c;

            term = -(a + m) * (qab + m) * x
                / ((a + m2) * (qap + m2));

            d = 1 + term * d;
            if (Math.abs(d) < 1e-300) d = 1e-300;

            c = 1 + term / c;
            if (Math.abs(c) < 1e-300) c = 1e-300;

            d = 1 / d;

            double delta = d * c;
            h *= delta;

            if (Math.abs(delta - 1) <= EPSILON) {
                return h;
            }
        }

        throw new ArithmeticException(
            "Beta continued fraction did not converge."
        );
    }

    static double regularizedBeta(double x, double a, double b) {
        positive(a, "Alpha");
        positive(b, "Beta");

        if (!Double.isFinite(x) || x < 0 || x > 1) {
            throw new StatisticalException(
                "x must be between zero and one."
            );
        }

        if (x == 0) return 0;
        if (x == 1) return 1;

        double factor = Math.exp(
            logGamma(a + b) - logGamma(a) - logGamma(b)
            + a * Math.log(x)
            + b * Math.log1p(-x)
        );

        double result;

        if (x < (a + 1) / (a + b + 2)) {
            result = factor * betaFraction(a, b, x) / a;
        } else {
            result = 1 - factor * betaFraction(b, a, 1 - x) / b;
        }

        return clamp(result);
    }

    interface Distribution {
        double density(double x);

        double cdf(double x);

        double mean();

        double variance();

        double sample(RandomGenerator random);
    }

    static class RandomGenerator {
        private final Random random;

        RandomGenerator(long seed) {
            random = new Random(seed);
        }

        double uniform() {
            return random.nextDouble();
        }

        double normal() {
            return random.nextGaussian();
        }

        double gamma(double shape, double scale) {
            positive(shape, "Gamma shape");
            positive(scale, "Gamma scale");

            if (shape < 1) {
                return gamma(shape + 1, scale)
                    * Math.pow(uniform(), 1 / shape);
            }

            double d = shape - 1.0 / 3;
            double c = 1 / Math.sqrt(9 * d);

            for (int i = 0; i < 100000; i++) {
                double x = normal();
                double v0 = 1 + c * x;

                if (v0 <= 0) continue;

                double v = v0 * v0 * v0;
                double u = uniform();

                if (
                    u < 1 - 0.0331 * Math.pow(x, 4)
                    || Math.log(u)
                        < 0.5 * x * x + d * (1 - v + Math.log(v))
                ) {
                    return scale * d * v;
                }
            }

            throw new ArithmeticException(
                "Gamma sampling failed."
            );
        }

        double beta(double a, double b) {
            double x = gamma(a, 1);
            double y = gamma(b, 1);
            return x / (x + y);
        }

        long poisson(double rate) {
            positive(rate, "Poisson rate");

            if (rate < 30) {
                double limit = Math.exp(-rate);
                double product = 1;
                long count = 0;

                do {
                    count++;
                    product *= uniform();
                } while (product > limit);

                return count - 1;
            }

            double sqrtRate = Math.sqrt(rate);
            double b = 0.931 + 2.53 * sqrtRate;
            double a = -0.059 + 0.02483 * b;
            double inverseAlpha = 1.1239 + 1.1328 / (b - 3.4);
            double vr = 0.9277 - 3.6224 / (b - 2);

            for (int i = 0; i < 100000; i++) {
                double u = uniform() - 0.5;
                double v = uniform();
                double us = 0.5 - Math.abs(u);

                if (us <= 0) continue;

                double candidate = Math.floor(
                    (2 * a / us + b) * u + rate + 0.43
                );

                if (candidate > Long.MAX_VALUE || candidate < 0) {
                    continue;
                }

                long k = (long) candidate;

                if (us >= 0.07 && v <= vr) return k;
                if (us < 0.013 && v > us) continue;

                double lhs = Math.log(
                    v * inverseAlpha / (a / (us * us) + b)
                );

                double rhs = -rate
                    + k * Math.log(rate)
                    - logGamma(k + 1);

                if (lhs <= rhs) return k;
            }

            throw new ArithmeticException(
                "Poisson sampling failed."
            );
        }
    }

    static class PoissonDistribution implements Distribution {
        private final double lambda;

        PoissonDistribution(double lambda) {
            positive(lambda, "Lambda");
            this.lambda = lambda;
        }

        double pmf(int k) {
            if (k < 0) return 0;

            return Math.exp(
                k * Math.log(lambda)
                - lambda
                - logGamma(k + 1)
            );
        }

        @Override
        public double density(double x) {
            if (!Double.isFinite(x) || x != Math.rint(x)) {
                return 0;
            }

            if (x < 0 || x > Integer.MAX_VALUE) return 0;

            return pmf((int) x);
        }

        @Override
        public double cdf(double x) {
            if (x < 0) return 0;

            if (x > Integer.MAX_VALUE) return 1;

            return regularizedGammaP(
                Math.floor(x) + 1,
                lambda
            );
        }

        public double mean() { return lambda; }

        public double variance() { return lambda; }

        public double sample(RandomGenerator rng) {
            return rng.poisson(lambda);
        }
    }

    static class GammaDistribution implements Distribution {
        private final double shape;
        private final double scale;

        GammaDistribution(double shape, double scale) {
            positive(shape, "Shape");
            positive(scale, "Scale");

            this.shape = shape;
            this.scale = scale;
        }

        @Override
        public double density(double x) {
            if (x < 0) return 0;

            if (x == 0) {
                if (shape < 1) return Double.POSITIVE_INFINITY;
                if (shape == 1) return 1 / scale;
                return 0;
            }

            return Math.exp(
                (shape - 1) * Math.log(x)
                - x / scale
                - logGamma(shape)
                - shape * Math.log(scale)
            );
        }

        @Override
        public double cdf(double x) {
            return x <= 0 ? 0
                : regularizedGammaP(shape, x / scale);
        }

        @Override
        public double mean() {
            return shape * scale;
        }

        @Override
        public double variance() {
            return shape * scale * scale;
        }

        @Override
        public double sample(RandomGenerator rng) {
            return rng.gamma(shape, scale);
        }
    }

    static class BetaDistribution implements Distribution {
        private final double alpha;
        private final double beta;

        BetaDistribution(double alpha, double beta) {
            positive(alpha, "Alpha");
            positive(beta, "Beta");

            this.alpha = alpha;
            this.beta = beta;
        }

        @Override
        public double density(double x) {
            if (x < 0 || x > 1) return 0;

            double normalizer = logGamma(alpha + beta)
                - logGamma(alpha)
                - logGamma(beta);

            if (x == 0) {
                if (alpha < 1) return Double.POSITIVE_INFINITY;
                if (alpha > 1) return 0;
                return Math.exp(normalizer);
            }

            if (x == 1) {
                if (beta < 1) return Double.POSITIVE_INFINITY;
                if (beta > 1) return 0;
                return Math.exp(normalizer);
            }

            return Math.exp(
                (alpha - 1) * Math.log(x)
                + (beta - 1) * Math.log1p(-x)
                + normalizer
            );
        }

        @Override
        public double cdf(double x) {
            return regularizedBeta(x, alpha, beta);
        }

        @Override
        public double mean() {
            return alpha / (alpha + beta);
        }

        @Override
        public double variance() {
            double total = alpha + beta;

            return alpha * beta
                / (total * total * (total + 1));
        }

        @Override
        public double sample(RandomGenerator rng) {
            return rng.beta(alpha, beta);
        }
    }

    static class ChiSquareDistribution implements Distribution {
        private final double df;

        ChiSquareDistribution(double df) {
            positive(df, "Degrees of freedom");
            this.df = df;
        }

        @Override
        public double density(double x) {
            if (x < 0) return 0;

            if (x == 0) {
                if (df < 2) return Double.POSITIVE_INFINITY;
                if (df == 2) return 0.5;
                return 0;
            }

            return Math.exp(
                (df / 2 - 1) * Math.log(x)
                - x / 2
                - df / 2 * Math.log(2)
                - logGamma(df / 2)
            );
        }

        @Override
        public double cdf(double x) {
            return x <= 0 ? 0
                : regularizedGammaP(df / 2, x / 2);
        }

        @Override
        public double mean() {
            return df;
        }

        @Override
        public double variance() {
            return 2 * df;
        }

        @Override
        public double sample(RandomGenerator rng) {
            return rng.gamma(df / 2, 2);
        }
    }

    record GoodnessOfFitResult(
        double statistic,
        int degreesOfFreedom,
        double pValue,
        double alpha,
        boolean rejectNull
    ) {}

    static class StatisticalService {

        GoodnessOfFitResult goodnessOfFit(
            List<Integer> observed,
            List<Double> expected,
            double alpha
        ) {
            if (
                observed == null
                || expected == null
                || observed.size() < 2
                || observed.size() != expected.size()
            ) {
                throw new StatisticalException(
                    "Frequency arrays must have equal lengths."
                );
            }

            if (!Double.isFinite(alpha) || alpha <= 0 || alpha >= 1) {
                throw new StatisticalException(
                    "Alpha must be between zero and one."
                );
            }

            double observedTotal = 0;
            double expectedTotal = 0;
            double statistic = 0;

            for (int i = 0; i < observed.size(); i++) {
                int actual = observed.get(i);
                double predicted = expected.get(i);

                if (actual < 0) {
                    throw new StatisticalException(
                        "Observed frequencies cannot be negative."
                    );
                }

                if (!Double.isFinite(predicted) || predicted < 5) {
                    throw new StatisticalException(
                        "Expected frequencies must be at least five."
                    );
                }

                observedTotal += actual;
                expectedTotal += predicted;

                statistic += Math.pow(actual - predicted, 2)
                    / predicted;
            }

            if (
                Math.abs(observedTotal - expectedTotal)
                > 1e-9 * Math.max(1, observedTotal)
            ) {
                throw new StatisticalException(
                    "Frequency totals must match."
                );
            }

            int df = observed.size() - 1;

            double pValue = 1 - regularizedGammaP(
                df / 2.0,
                statistic / 2
            );

            return new GoodnessOfFitResult(
                statistic,
                df,
                Math.max(0, pValue),
                alpha,
                pValue < alpha
            );
        }
    }

    record SimulationResult(
        int sampleSize,
        double empiricalMean,
        double empiricalVariance,
        double theoreticalMean,
        double theoreticalVariance,
        double minimum,
        double maximum
    ) {}

    static SimulationResult simulate(
        Distribution distribution,
        RandomGenerator rng,
        int sampleSize
    ) {
        if (sampleSize <= 0) {
            throw new StatisticalException(
                "Sample size must be positive."
            );
        }

        double[] samples = new double[sampleSize];

        double sum = 0;

        for (int i = 0; i < sampleSize; i++) {
            samples[i] = distribution.sample(rng);
            sum += samples[i];
        }

        double mean = sum / sampleSize;
        double variance = 0;

        double minimum = Double.POSITIVE_INFINITY;
        double maximum = Double.NEGATIVE_INFINITY;

        for (double value : samples) {
            variance += Math.pow(value - mean, 2);
            minimum = Math.min(minimum, value);
            maximum = Math.max(maximum, value);
        }

        variance /= sampleSize;

        return new SimulationResult(
            sampleSize,
            mean,
            variance,
            distribution.mean(),
            distribution.variance(),
            minimum,
            maximum
        );
    }

    static void printReport(
        String name,
        Distribution distribution,
        double[] points
    ) {
        System.out.println("\n" + name);
        System.out.println("--------------------------------");

        System.out.printf("Mean: %.6f%n", distribution.mean());
        System.out.printf(
            "Variance: %.6f%n",
            distribution.variance()
        );

        for (double x : points) {
            System.out.printf(
                "x=%.3f | density=%.8f | CDF=%.8f%n",
                x,
                distribution.density(x),
                distribution.cdf(x)
            );
        }
    }

    static void validateImplementation() {
        PoissonDistribution poisson = new PoissonDistribution(4);
        GammaDistribution gamma = new GammaDistribution(3, 2);
        BetaDistribution beta = new BetaDistribution(2, 5);
        ChiSquareDistribution chi = new ChiSquareDistribution(4);

        if (Math.abs(poisson.mean() - 4) > EPSILON) {
            throw new AssertionError("Poisson mean failed.");
        }

        if (Math.abs(gamma.variance() - 12) > EPSILON) {
            throw new AssertionError("Gamma variance failed.");
        }

        if (Math.abs(beta.mean() - 2.0 / 7) > EPSILON) {
            throw new AssertionError("Beta mean failed.");
        }

        if (Math.abs(chi.variance() - 8) > EPSILON) {
            throw new AssertionError("Chi-square variance failed.");
        }

        if (Math.abs(gamma.cdf(0)) > EPSILON) {
            throw new AssertionError("Gamma boundary failed.");
        }

        if (Math.abs(beta.cdf(1) - 1) > EPSILON) {
            throw new AssertionError("Beta boundary failed.");
        }

        System.out.println("All validation tests passed.");
    }

    public static void main(String[] args) {
        try {
            validateImplementation();

            RandomGenerator rng = new RandomGenerator(42);

            Map<String, Distribution> distributions =
                new LinkedHashMap<>();

            distributions.put(
                "Poisson",
                new PoissonDistribution(4.5)
            );

            distributions.put(
                "Gamma",
                new GammaDistribution(3, 2)
            );

            distributions.put(
                "Beta",
                new BetaDistribution(2, 5)
            );

            distributions.put(
                "Chi-square",
                new ChiSquareDistribution(4)
            );

            System.out.println("\nADVANCED DISTRIBUTIONS");

            for (var entry : distributions.entrySet()) {
                printReport(
                    entry.getKey(),
                    entry.getValue(),
                    new double[]{0.5, 1, 2, 4, 8}
                );
            }

            System.out.println("\nBAYESIAN CONVERSION ESTIMATION");

            BetaDistribution prior =
                new BetaDistribution(2, 2);

            int successes = 45;
            int failures = 55;

            BetaDistribution posterior =
                new BetaDistribution(
                    prior.alpha + successes,
                    prior.beta + failures
                );

            System.out.printf(
                "Prior mean: %.6f%n",
                prior.mean()
            );

            System.out.printf(
                "Posterior mean: %.6f%n",
                posterior.mean()
            );

            System.out.printf(
                "P(rate <= 0.5): %.6f%n",
                posterior.cdf(0.5)
            );

            System.out.println("\nSIMULATION");

            distributions.forEach((name, distribution) -> {
                System.out.println("\n" + name);

                SimulationResult result = simulate(
                    distribution,
                    rng,
                    10000
                );

                System.out.println(result);
            });

            System.out.println("\nCHI-SQUARE GOODNESS-OF-FIT");

            StatisticalService service =
                new StatisticalService();

            GoodnessOfFitResult result = service.goodnessOfFit(
                List.of(48, 32, 15, 5),
                List.of(50.0, 30.0, 15.0, 5.0),
                0.05
            );

            System.out.println(result);

            if (result.rejectNull()) {
                System.out.println("Reject the null hypothesis.");
            } else {
                System.out.println(
                    "Insufficient evidence to reject the null hypothesis."
                );
            }

        } catch (Exception exception) {
            System.err.println(
                "Statistical execution failed: "
                + exception.getMessage()
            );

            System.exitCode = 1;
        }
    }
}
