import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;

/*
 * Statistical Tests: Enterprise Research Analytics.
 *
 * Java 17 implementation featuring immutable domain records,
 * test policies, experiment registration, validation, and reporting.
 *
 * Compile: javac StatisticalTests.java
 * Run:     java StatisticalTests
 */

public class StatisticalTests {

    enum TestCategory {
        ONE_SAMPLE_T,
        WELCH_T,
        PAIRED_T,
        Z_TEST,
        CHI_SQUARE,
        ANOVA
    }

    static class StatisticalException extends RuntimeException {
        StatisticalException(String message) {
            super(message);
        }
    }

    record TestPolicy(double alpha, boolean requireEffectSize) {
        TestPolicy {
            if (!(alpha > 0 && alpha < 1)) {
                throw new StatisticalException("Alpha must be between zero and one.");
            }
        }
    }

    record TestResult(
        String experimentId,
        TestCategory category,
        double statistic,
        double pValue,
        double degreesOfFreedom,
        Double effectSize,
        double alpha
    ) {
        TestResult {
            Objects.requireNonNull(experimentId);
            Objects.requireNonNull(category);

            if (!Double.isFinite(statistic)
                || !Double.isFinite(pValue)
                || pValue < 0
                || pValue > 1) {
                throw new StatisticalException("Invalid statistical result.");
            }
        }

        boolean rejectsNull() {
            return pValue < alpha;
        }

        String decision() {
            return rejectsNull() ? "REJECT H0" : "FAIL TO REJECT H0";
        }
    }

    record Sample(List<Double> observations, String identifier) {
        Sample {
            Objects.requireNonNull(identifier);

            if (observations == null || observations.size() < 2) {
                throw new StatisticalException("At least two observations are required.");
            }

            observations = List.copyOf(observations);

            if (observations.stream().anyMatch(
                x -> x == null || !Double.isFinite(x)
            )) {
                throw new StatisticalException("Sample contains invalid observations.");
            }
        }

        double mean() {
            return observations.stream()
                .mapToDouble(Double::doubleValue)
                .average()
                .orElseThrow();
        }

        double variance() {
            double avg = mean();

            return observations.stream()
                .mapToDouble(x -> Math.pow(x - avg, 2))
                .sum() / (observations.size() - 1);
        }

        int size() {
            return observations.size();
        }
    }

    interface StatisticalTest {
        TestResult execute(String experimentId);
    }

    static final class Distribution {

        private static final double EPS = 1e-300;

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

            return 0.5 * Math.log(2 * Math.PI)
                + (z + 0.5) * Math.log(t) - t + Math.log(x);
        }

        static double betaFraction(double a, double b, double x) {
            double qab = a + b;
            double qap = a + 1;
            double qam = a - 1;

            double c = 1;
            double d = 1 - qab * x / qap;

            if (Math.abs(d) < EPS) d = EPS;

            d = 1 / d;
            double h = d;

            for (int m = 1; m <= 10000; m++) {
                int m2 = 2 * m;

                double aa = m * (b - m) * x
                    / ((qam + m2) * (a + m2));

                d = 1 + aa * d;
                if (Math.abs(d) < EPS) d = EPS;

                c = 1 + aa / c;
                if (Math.abs(c) < EPS) c = EPS;

                d = 1 / d;
                h *= d * c;

                aa = -(a + m) * (qab + m) * x
                    / ((a + m2) * (qap + m2));

                d = 1 + aa * d;
                if (Math.abs(d) < EPS) d = EPS;

                c = 1 + aa / c;
                if (Math.abs(c) < EPS) c = EPS;

                d = 1 / d;
                double delta = d * c;
                h *= delta;

                if (Math.abs(delta - 1) < 3e-14) {
                    return h;
                }
            }

            throw new StatisticalException("Beta fraction did not converge.");
        }

        static double betaRegularized(double x, double a, double b) {
            if (a <= 0 || b <= 0 || x < 0 || x > 1) {
                throw new StatisticalException("Invalid beta parameters.");
            }

            if (x == 0) return 0;
            if (x == 1) return 1;

            double bt = Math.exp(
                logGamma(a + b) - logGamma(a) - logGamma(b)
                + a * Math.log(x) + b * Math.log1p(-x)
            );

            double result;

            if (x < (a + 1) / (a + b + 2)) {
                result = bt * betaFraction(a, b, x) / a;
            } else {
                result = 1 - bt * betaFraction(b, a, 1 - x) / b;
            }

            return Math.max(0, Math.min(1, result));
        }

        static double gammaQ(double a, double x) {
            if (a <= 0 || x < 0) {
                throw new StatisticalException("Invalid gamma parameters.");
            }

            if (x == 0) return 1;

            double gln = logGamma(a);

            if (x < a + 1) {
                double ap = a;
                double term = 1 / a;
                double sum = term;

                for (int i = 0; i < 10000; i++) {
                    ap++;
                    term *= x / ap;
                    sum += term;

                    if (Math.abs(term) < Math.abs(sum) * 3e-14) {
                        return Math.max(
                            0,
                            Math.min(
                                1,
                                1 - sum * Math.exp(-x + a * Math.log(x) - gln)
                            )
                        );
                    }
                }

                throw new StatisticalException("Gamma series did not converge.");
            }

            double b = x + 1 - a;
            double c = 1e300;
            double d = 1 / b;
            double h = d;

            for (int i = 1; i <= 10000; i++) {
                double an = -i * (i - a);
                b += 2;

                d = an * d + b;
                if (Math.abs(d) < EPS) d = EPS;

                c = b + an / c;
                if (Math.abs(c) < EPS) c = EPS;

                d = 1 / d;
                double delta = d * c;
                h *= delta;

                if (Math.abs(delta - 1) < 3e-14) {
                    return Math.max(
                        0,
                        Math.min(
                            1,
                            Math.exp(-x + a * Math.log(x) - gln) * h
                        )
                    );
                }
            }

            throw new StatisticalException("Gamma continued fraction failed.");
        }

        static double normalCDF(double z) {
            return 0.5 * (1 + erf(z / Math.sqrt(2)));
        }

        static double erf(double x) {
            double sign = x < 0 ? -1 : 1;
            x = Math.abs(x);

            double t = 1 / (1 + 0.3275911 * x);

            double polynomial = (((((1.061405429 * t
                - 1.453152027) * t + 1.421413741) * t
                - 0.284496736) * t + 0.254829592) * t);

            return sign * (1 - polynomial * Math.exp(-x * x));
        }

        static double normalP(double z) {
            return 2 * (1 - normalCDF(Math.abs(z)));
        }

        static double tP(double t, double df) {
            return betaRegularized(
                df / (df + t * t),
                df / 2,
                0.5
            );
        }

        static double chiSquareP(double x, double df) {
            return gammaQ(df / 2, x / 2);
        }

        static double fP(double f, double df1, double df2) {
            return betaRegularized(
                df2 / (df2 + df1 * f),
                df2 / 2,
                df1 / 2
            );
        }
    }

    static final class TestService {

        private final TestPolicy policy;

        TestService(TestPolicy policy) {
            this.policy = policy;
        }

        TestResult oneSampleT(
            String id,
            Sample sample,
            double reference
        ) {
            double sd = Math.sqrt(sample.variance());
            double se = sd / Math.sqrt(sample.size());

            if (se == 0) {
                throw new StatisticalException("Zero sample variance.");
            }

            double statistic = (sample.mean() - reference) / se;
            double df = sample.size() - 1;

            return new TestResult(
                id,
                TestCategory.ONE_SAMPLE_T,
                statistic,
                Distribution.tP(statistic, df),
                df,
                (sample.mean() - reference) / sd,
                policy.alpha()
            );
        }

        TestResult welchT(
            String id,
            Sample first,
            Sample second
        ) {
            double va = first.variance();
            double vb = second.variance();

            double x = va / first.size();
            double y = vb / second.size();
            double se2 = x + y;

            if (se2 == 0) {
                throw new StatisticalException("Zero combined variance.");
            }

            double df = se2 * se2 / (
                x * x / (first.size() - 1)
                + y * y / (second.size() - 1)
            );

            double statistic = (first.mean() - second.mean()) / Math.sqrt(se2);

            return new TestResult(
                id,
                TestCategory.WELCH_T,
                statistic,
                Distribution.tP(statistic, df),
                df,
                null,
                policy.alpha()
            );
        }

        TestResult pairedT(
            String id,
            Sample before,
            Sample after
        ) {
            if (before.size() != after.size()) {
                throw new StatisticalException("Paired sample lengths differ.");
            }

            List<Double> differences = new ArrayList<>();

            for (int i = 0; i < before.size(); i++) {
                differences.add(
                    after.observations().get(i)
                    - before.observations().get(i)
                );
            }

            return oneSampleT(
                id,
                new Sample(differences, "paired-differences"),
                0
            );
        }

        TestResult zTest(
            String id,
            double sampleMean,
            double populationMean,
            double populationSD,
            int sampleSize
        ) {
            if (populationSD <= 0 || sampleSize <= 0) {
                throw new StatisticalException("Invalid population parameters.");
            }

            double z = (sampleMean - populationMean)
                / (populationSD / Math.sqrt(sampleSize));

            return new TestResult(
                id,
                TestCategory.Z_TEST,
                z,
                Distribution.normalP(z),
                Double.NaN,
                null,
                policy.alpha()
            );
        }

        TestResult chiSquare(
            String id,
            double[][] table
        ) {
            if (table == null || table.length < 2 || table[0].length < 2) {
                throw new StatisticalException("Contingency table must be at least 2x2.");
            }

            int rows = table.length;
            int cols = table[0].length;

            double[] rowTotals = new double[rows];
            double[] colTotals = new double[cols];
            double total = 0;

            for (int i = 0; i < rows; i++) {
                if (table[i].length != cols) {
                    throw new StatisticalException("Invalid table dimensions.");
                }

                for (int j = 0; j < cols; j++) {
                    double value = table[i][j];

                    if (!Double.isFinite(value) || value < 0) {
                        throw new StatisticalException("Invalid frequency.");
                    }

                    rowTotals[i] += value;
                    colTotals[j] += value;
                    total += value;
                }
            }

            if (total <= 0) {
                throw new StatisticalException("Empty contingency table.");
            }

            double statistic = 0;

            for (int i = 0; i < rows; i++) {
                for (int j = 0; j < cols; j++) {
                    double expected = rowTotals[i] * colTotals[j] / total;

                    if (expected <= 0) {
                        throw new StatisticalException("Zero expected frequency.");
                    }

                    statistic += Math.pow(table[i][j] - expected, 2) / expected;
                }
            }

            int df = (rows - 1) * (cols - 1);

            double cramerV = Math.sqrt(
                statistic / (total * Math.min(rows - 1, cols - 1))
            );

            return new TestResult(
                id,
                TestCategory.CHI_SQUARE,
                statistic,
                Distribution.chiSquareP(statistic, df),
                df,
                cramerV,
                policy.alpha()
            );
        }

        TestResult anova(
            String id,
            List<Sample> groups
        ) {
            if (groups == null || groups.size() < 2) {
                throw new StatisticalException("ANOVA needs at least two groups.");
            }

            int totalN = groups.stream().mapToInt(Sample::size).sum();

            double grandTotal = groups.stream()
                .mapToDouble(g -> g.mean() * g.size())
                .sum();

            double grandMean = grandTotal / totalN;

            double ssBetween = 0;
            double ssWithin = 0;

            for (Sample group : groups) {
                double avg = group.mean();

                ssBetween += group.size() * Math.pow(avg - grandMean, 2);

                for (double value : group.observations()) {
                    ssWithin += Math.pow(value - avg, 2);
                }
            }

            int df1 = groups.size() - 1;
            int df2 = totalN - groups.size();

            double msWithin = ssWithin / df2;

            if (msWithin == 0) {
                throw new StatisticalException("Within-group variance is zero.");
            }

            double f = (ssBetween / df1) / msWithin;

            return new TestResult(
                id,
                TestCategory.ANOVA,
                f,
                Distribution.fP(f, df1, df2),
                df2,
                ssBetween / (ssBetween + ssWithin),
                policy.alpha()
            );
        }
    }

    static final class ExperimentRegistry {

        private final Map<String, StatisticalTest> experiments =
            new LinkedHashMap<>();

        void register(String id, StatisticalTest test) {
            if (id == null || id.isBlank() || test == null) {
                throw new StatisticalException("Invalid experiment registration.");
            }

            if (experiments.putIfAbsent(id, test) != null) {
                throw new StatisticalException("Duplicate experiment ID: " + id);
            }
        }

        CompletableFuture<TestResult> execute(String id) {
            StatisticalTest test = experiments.get(id);

            if (test == null) {
                throw new StatisticalException("Unknown experiment: " + id);
            }

            return CompletableFuture.supplyAsync(() -> test.execute(id));
        }

        List<TestResult> executeAll() {
            List<CompletableFuture<TestResult>> futures =
                experiments.values().stream()
                    .map(test -> CompletableFuture.supplyAsync(
                        () -> test.execute("registered-experiment")
                    ))
                    .toList();

            return futures.stream()
                .map(CompletableFuture::join)
                .toList();
        }
    }

    static final class ResearchReport {

        private final List<TestResult> results = new ArrayList<>();

        void add(TestResult result) {
            Objects.requireNonNull(result);
            results.add(result);
        }

        void print() {
            System.out.println("\nENTERPRISE RESEARCH REPORT");

            System.out.printf(
                "%-25s %-14s %-14s %-14s %s%n",
                "Experiment",
                "Statistic",
                "P-value",
                "DF",
                "Decision"
            );

            for (TestResult r : results) {
                System.out.printf(
                    "%-25s %-14.5f %-14.8f %-14.2f %s%n",
                    r.experimentId(),
                    r.statistic(),
                    r.pValue(),
                    r.degreesOfFreedom(),
                    r.decision()
                );
            }
        }

        Map<String, Double> bonferroniAdjusted() {
            Map<String, Double> adjusted = new LinkedHashMap<>();

            for (TestResult r : results) {
                adjusted.put(
                    r.experimentId(),
                    Math.min(1, r.pValue() * results.size())
                );
            }

            return Collections.unmodifiableMap(adjusted);
        }
    }

    public static void main(String[] args) {
        try {
            TestPolicy policy = new TestPolicy(0.05, false);
            TestService service = new TestService(policy);
            ResearchReport report = new ResearchReport();

            Sample quality = new Sample(
                List.of(51.0, 53.0, 49.0, 52.0, 55.0, 50.0, 54.0, 52.0),
                "quality-control"
            );

            report.add(service.oneSampleT("quality-control", quality, 50));

            Sample control = new Sample(
                List.of(68.0, 70.0, 72.0, 65.0, 71.0, 69.0, 67.0),
                "control"
            );

            Sample treatment = new Sample(
                List.of(75.0, 78.0, 74.0, 80.0, 77.0, 76.0, 79.0),
                "treatment"
            );

            report.add(service.welchT(
                "treatment-comparison", control, treatment
            ));

            report.add(service.pairedT(
                "before-after",
                new Sample(List.of(70.0, 72.0, 68.0, 75.0, 71.0, 69.0), "before"),
                new Sample(List.of(74.0, 76.0, 72.0, 78.0, 75.0, 73.0), "after")
            ));

            report.add(service.zTest(
                "population-mean", 102, 100, 10, 100
            ));

            report.add(service.chiSquare(
                "customer-preferences",
                new double[][] {
                    {40, 20},
                    {30, 50}
                }
            ));

            report.add(service.anova(
                "production-lines",
                List.of(
                    new Sample(List.of(18.0, 20.0, 19.0, 21.0, 17.0), "A"),
                    new Sample(List.of(24.0, 25.0, 23.0, 26.0, 22.0), "B"),
                    new Sample(List.of(29.0, 30.0, 28.0, 31.0, 27.0), "C")
                )
            ));

            report.print();

            System.out.println("\nBONFERRONI-ADJUSTED P-VALUES");
            report.bonferroniAdjusted().forEach(
                (id, p) -> System.out.printf("%s: %.8f%n", id, p)
            );

            if (Math.abs(Distribution.normalCDF(0) - 0.5) > 1e-5) {
                throw new StatisticalException("Normal distribution validation failed.");
            }

            if (Math.abs(Distribution.chiSquareP(0, 2) - 1) > 1e-10) {
                throw new StatisticalException("Chi-square validation failed.");
            }

            System.out.println("\nValidation completed successfully.");

        } catch (CompletionException | StatisticalException error) {
            System.err.println("Research processing failed: " + error.getMessage());
            System.exit(1);
        }
    }
}
