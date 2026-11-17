import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeSet;
import java.util.stream.Collectors;

/*
 * Correlation and Covariance Analysis
 *
 * Java 17
 *
 * Enterprise-oriented statistical analysis system.
 *
 * Features:
 * - Immutable dataset records
 * - Pearson correlation
 * - Sample and population covariance
 * - Covariance matrices
 * - Correlation matrices
 * - Missing-data policies
 * - Statistical quality controls
 * - Dependence monitoring
 * - Correlation threshold policies
 * - Analysis service
 * - Exception-based failure handling
 */

public class CorrelationAnalysis {

    enum MissingPolicy {
        REJECT,
        PAIRWISE,
        LISTWISE
    }

    enum CorrelationStrength {
        NEGLIGIBLE,
        WEAK,
        MODERATE,
        STRONG,
        VERY_STRONG
    }

    enum AnalysisStatus {
        CREATED,
        VALIDATING,
        RUNNING,
        COMPLETED,
        FAILED
    }

    static class StatisticalException extends RuntimeException {
        StatisticalException(String message) {
            super(message);
        }
    }

    static class ValidationException extends StatisticalException {
        ValidationException(String message) {
            super(message);
        }
    }

    static class InsufficientDataException
            extends StatisticalException {
        InsufficientDataException(String message) {
            super(message);
        }
    }

    record Variable(
        String name,
        List<Double> observations
    ) {
        Variable {
            if (name == null || name.isBlank()) {
                throw new ValidationException(
                    "Variable name is required."
                );
            }

            Objects.requireNonNull(
                observations,
                "Observations cannot be null."
            );

            observations = Collections.unmodifiableList(
                new ArrayList<>(observations)
            );

            for (Double value : observations) {
                if (
                    value != null &&
                    !Double.isFinite(value)
                ) {
                    throw new ValidationException(
                        "Observations must be finite."
                    );
                }
            }
        }
    }

    record Dataset(
        String name,
        List<Variable> variables
    ) {
        Dataset {
            if (name == null || name.isBlank()) {
                throw new ValidationException(
                    "Dataset name is required."
                );
            }

            Objects.requireNonNull(variables);

            variables = List.copyOf(variables);

            if (variables.size() < 2) {
                throw new ValidationException(
                    "At least two variables are required."
                );
            }

            Set<String> names = new TreeSet<>();

            int expectedLength = variables.get(0)
                .observations()
                .size();

            if (expectedLength < 2) {
                throw new InsufficientDataException(
                    "At least two observation positions are required."
                );
            }

            for (Variable variable : variables) {
                if (!names.add(variable.name())) {
                    throw new ValidationException(
                        "Duplicate variable: " + variable.name()
                    );
                }

                if (
                    variable.observations().size() !=
                    expectedLength
                ) {
                    throw new ValidationException(
                        "Variable lengths must match."
                    );
                }
            }
        }

        Variable getVariable(String name) {
            return variables.stream()
                .filter(variable ->
                    variable.name().equals(name))
                .findFirst()
                .orElseThrow(() ->
                    new ValidationException(
                        "Unknown variable: " + name
                    )
                );
        }
    }

    record PairResult(
        String first,
        String second,
        double covariance,
        Double correlation,
        int observations,
        CorrelationStrength strength
    ) {}

    record AnalysisReport(
        String dataset,
        AnalysisStatus status,
        Map<String, Map<String, Double>> covarianceMatrix,
        Map<String, Map<String, Double>> correlationMatrix,
        List<PairResult> highCorrelationPairs,
        Map<String, Map<String, Double>> descriptiveStatistics
    ) {}

    interface AnalysisPolicy {
        boolean isEligible(PairResult result);
    }

    static final class CorrelationThresholdPolicy
            implements AnalysisPolicy {

        private final double threshold;

        CorrelationThresholdPolicy(double threshold) {
            if (
                !Double.isFinite(threshold) ||
                threshold <= 0 ||
                threshold > 1
            ) {
                throw new ValidationException(
                    "Threshold must be in (0, 1]."
                );
            }

            this.threshold = threshold;
        }

        @Override
        public boolean isEligible(PairResult result) {
            return result.correlation() != null &&
                Math.abs(result.correlation()) >= threshold;
        }
    }

    static final class NumericalStatistics {

        static double mean(List<Double> values) {
            if (values.isEmpty()) {
                throw new InsufficientDataException(
                    "Cannot calculate an empty mean."
                );
            }

            double sum = 0.0;
            double correction = 0.0;

            for (double value : values) {
                double adjusted = value - correction;
                double next = sum + adjusted;
                correction = (next - sum) - adjusted;
                sum = next;
            }

            return sum / values.size();
        }

        static double variance(
            List<Double> values,
            boolean sample
        ) {
            int minimum = sample ? 2 : 1;

            if (values.size() < minimum) {
                throw new InsufficientDataException(
                    "Insufficient observations for variance."
                );
            }

            double average = mean(values);

            double sum = values.stream()
                .mapToDouble(value ->
                    Math.pow(value - average, 2))
                .sum();

            return sum / (
                values.size() - (sample ? 1 : 0)
            );
        }

        static double covariance(
            List<Double> x,
            List<Double> y,
            boolean sample
        ) {
            if (x.size() != y.size()) {
                throw new ValidationException(
                    "Observation counts must match."
                );
            }

            int minimum = sample ? 2 : 1;

            if (x.size() < minimum) {
                throw new InsufficientDataException(
                    "Insufficient paired observations."
                );
            }

            double mx = mean(x);
            double my = mean(y);

            double sum = 0.0;

            for (int i = 0; i < x.size(); i++) {
                sum += (x.get(i) - mx) * (y.get(i) - my);
            }

            return sum / (
                x.size() - (sample ? 1 : 0)
            );
        }

        static double pearson(
            List<Double> x,
            List<Double> y
        ) {
            if (x.size() != y.size() || x.size() < 2) {
                throw new ValidationException(
                    "Pearson correlation requires matched observations."
                );
            }

            double mx = mean(x);
            double my = mean(y);

            double xx = 0.0;
            double yy = 0.0;
            double xy = 0.0;

            for (int i = 0; i < x.size(); i++) {
                double dx = x.get(i) - mx;
                double dy = y.get(i) - my;

                xx += dx * dx;
                yy += dy * dy;
                xy += dx * dy;
            }

            if (xx <= 0 || yy <= 0) {
                throw new ValidationException(
                    "Correlation is undefined for constant variables."
                );
            }

            return Math.max(
                -1.0,
                Math.min(
                    1.0,
                    xy / Math.sqrt(xx * yy)
                )
            );
        }

        static CorrelationStrength classify(double value) {
            double magnitude = Math.abs(value);

            if (magnitude >= 0.90) {
                return CorrelationStrength.VERY_STRONG;
            }

            if (magnitude >= 0.70) {
                return CorrelationStrength.STRONG;
            }

            if (magnitude >= 0.40) {
                return CorrelationStrength.MODERATE;
            }

            if (magnitude >= 0.20) {
                return CorrelationStrength.WEAK;
            }

            return CorrelationStrength.NEGLIGIBLE;
        }
    }

    static final class CorrelationService {

        private final Dataset dataset;
        private final MissingPolicy missingPolicy;
        private AnalysisStatus status = AnalysisStatus.CREATED;

        CorrelationService(
            Dataset dataset,
            MissingPolicy missingPolicy
        ) {
            this.dataset = Objects.requireNonNull(dataset);
            this.missingPolicy = Objects.requireNonNull(
                missingPolicy
            );
        }

        AnalysisStatus getStatus() {
            return status;
        }

        private List<List<Double>> pairedObservations(
            String first,
            String second
        ) {
            Variable x = dataset.getVariable(first);
            Variable y = dataset.getVariable(second);

            List<Double> pairedX = new ArrayList<>();
            List<Double> pairedY = new ArrayList<>();

            int size = x.observations().size();

            for (int i = 0; i < size; i++) {
                Double a = x.observations().get(i);
                Double b = y.observations().get(i);

                boolean complete = true;

                if (missingPolicy == MissingPolicy.LISTWISE) {
                    for (Variable variable : dataset.variables()) {
                        if (variable.observations().get(i) == null) {
                            complete = false;
                            break;
                        }
                    }
                }

                if (!complete) {
                    continue;
                }

                if (a == null || b == null) {
                    if (missingPolicy == MissingPolicy.REJECT) {
                        throw new ValidationException(
                            "Missing values are not permitted."
                        );
                    }

                    continue;
                }

                pairedX.add(a);
                pairedY.add(b);
            }

            return List.of(pairedX, pairedY);
        }

        PairResult analyzePair(
            String first,
            String second
        ) {
            List<List<Double>> paired =
                pairedObservations(first, second);

            List<Double> x = paired.get(0);
            List<Double> y = paired.get(1);

            if (x.size() < 2) {
                throw new InsufficientDataException(
                    "Insufficient paired observations."
                );
            }

            double cov = NumericalStatistics.covariance(
                x,
                y,
                true
            );

            Double corr = null;

            if (
                x.stream().distinct().count() > 1 &&
                y.stream().distinct().count() > 1
            ) {
                corr = NumericalStatistics.pearson(x, y);
            }

            CorrelationStrength strength = corr == null
                ? null
                : NumericalStatistics.classify(corr);

            return new PairResult(
                first,
                second,
                cov,
                corr,
                x.size(),
                strength
            );
        }

        Map<String, Map<String, Double>> buildMatrix(
            boolean covariance
        ) {
            Map<String, Map<String, Double>> matrix =
                new LinkedHashMap<>();

            for (Variable variable : dataset.variables()) {
                matrix.put(
                    variable.name(),
                    new LinkedHashMap<>()
                );
            }

            List<Variable> variables = dataset.variables();

            for (int i = 0; i < variables.size(); i++) {
                for (int j = i; j < variables.size(); j++) {
                    String first = variables.get(i).name();
                    String second = variables.get(j).name();

                    PairResult result = analyzePair(
                        first,
                        second
                    );

                    Double value = covariance
                        ? result.covariance()
                        : result.correlation();

                    if (value == null) {
                        throw new ValidationException(
                            "Correlation matrix contains undefined values."
                        );
                    }

                    matrix.get(first).put(second, value);
                    matrix.get(second).put(first, value);
                }
            }

            return matrix;
        }

        Map<String, Map<String, Double>> descriptiveStatistics() {
            Map<String, Map<String, Double>> result =
                new LinkedHashMap<>();

            for (Variable variable : dataset.variables()) {
                List<Double> values = variable.observations()
                    .stream()
                    .filter(Objects::nonNull)
                    .collect(Collectors.toList());

                Map<String, Double> metrics =
                    new LinkedHashMap<>();

                if (values.isEmpty()) {
                    metrics.put("observations", 0.0);
                    result.put(variable.name(), metrics);
                    continue;
                }

                metrics.put(
                    "observations",
                    (double) values.size()
                );

                metrics.put(
                    "missing",
                    (double) (
                        variable.observations().size() -
                        values.size()
                    )
                );

                metrics.put(
                    "mean",
                    NumericalStatistics.mean(values)
                );

                metrics.put(
                    "variance",
                    values.size() >= 2
                        ? NumericalStatistics.variance(values, true)
                        : Double.NaN
                );

                metrics.put(
                    "minimum",
                    Collections.min(values)
                );

                metrics.put(
                    "maximum",
                    Collections.max(values)
                );

                result.put(variable.name(), metrics);
            }

            return result;
        }

        List<PairResult> detectHighCorrelations(
            AnalysisPolicy policy
        ) {
            List<PairResult> result = new ArrayList<>();

            List<Variable> variables = dataset.variables();

            for (int i = 0; i < variables.size(); i++) {
                for (int j = i + 1; j < variables.size(); j++) {
                    PairResult pair = analyzePair(
                        variables.get(i).name(),
                        variables.get(j).name()
                    );

                    if (policy.isEligible(pair)) {
                        result.add(pair);
                    }
                }
            }

            return List.copyOf(result);
        }

        AnalysisReport execute() {
            try {
                status = AnalysisStatus.VALIDATING;

                for (Variable variable : dataset.variables()) {
                    if (
                        variable.observations().size() <
                        dataset.variables().get(0)
                            .observations().size()
                    ) {
                        throw new ValidationException(
                            "Dataset structure changed."
                        );
                    }
                }

                status = AnalysisStatus.RUNNING;

                Map<String, Map<String, Double>> covariance =
                    buildMatrix(true);

                Map<String, Map<String, Double>> correlation =
                    buildMatrix(false);

                List<PairResult> highCorrelations =
                    detectHighCorrelations(
                        new CorrelationThresholdPolicy(0.80)
                    );

                Map<String, Map<String, Double>> statistics =
                    descriptiveStatistics();

                status = AnalysisStatus.COMPLETED;

                return new AnalysisReport(
                    dataset.name(),
                    status,
                    covariance,
                    correlation,
                    highCorrelations,
                    statistics
                );

            } catch (RuntimeException exception) {
                status = AnalysisStatus.FAILED;
                throw exception;
            }
        }
    }

    private static Dataset sampleDataset() {
        return new Dataset(
            "Enterprise Investment Portfolio",
            List.of(
                new Variable(
                    "Equity_A",
                    List.of(10.0, 12.0, 14.0, 16.0, 18.0, 20.0)
                ),
                new Variable(
                    "Equity_B",
                    List.of(8.0, 10.0, 12.0, 14.0, 16.0, 18.0)
                ),
                new Variable(
                    "Bonds",
                    List.of(20.0, 19.0, 21.0, 18.0, 22.0, 17.0)
                ),
                new Variable(
                    "Gold",
                    List.of(15.0, 17.0, 14.0, 18.0, 13.0, 19.0)
                ),
                new Variable(
                    "Market_Index",
                    List.of(11.0, 13.0, 15.0, 17.0, 19.0, 21.0)
                )
            )
        );
    }

    private static void printMatrix(
        String title,
        Map<String, Map<String, Double>> matrix
    ) {
        System.out.println("\n" + title);

        List<String> names = new ArrayList<>(matrix.keySet());

        System.out.printf("%16s", "");

        for (String name : names) {
            System.out.printf("%14s", name);
        }

        System.out.println();

        for (String first : names) {
            System.out.printf("%16s", first);

            for (String second : names) {
                System.out.printf(
                    "%14.4f",
                    matrix.get(first).get(second)
                );
            }

            System.out.println();
        }
    }

    private static void runTests() {
        List<Double> x = List.of(1.0, 2.0, 3.0, 4.0);
        List<Double> y = List.of(2.0, 4.0, 6.0, 8.0);
        List<Double> z = List.of(8.0, 6.0, 4.0, 2.0);

        if (
            Math.abs(
                NumericalStatistics.pearson(x, y) - 1.0
            ) > 1e-10
        ) {
            throw new AssertionError(
                "Positive correlation test failed."
            );
        }

        if (
            Math.abs(
                NumericalStatistics.pearson(x, z) + 1.0
            ) > 1e-10
        ) {
            throw new AssertionError(
                "Negative correlation test failed."
            );
        }

        if (
            Math.abs(
                NumericalStatistics.variance(x, true) -
                1.6666666666666667
            ) > 1e-10
        ) {
            throw new AssertionError(
                "Variance test failed."
            );
        }

        boolean rejected = false;

        try {
            NumericalStatistics.pearson(
                List.of(1.0, 1.0, 1.0),
                List.of(2.0, 3.0, 4.0)
            );
        } catch (ValidationException exception) {
            rejected = true;
        }

        if (!rejected) {
            throw new AssertionError(
                "Constant variable test failed."
            );
        }

        System.out.println(
            "All Java 17 statistical tests passed."
        );
    }

    public static void main(String[] args) {
        try {
            Dataset dataset = sampleDataset();

            CorrelationService service = new CorrelationService(
                dataset,
                MissingPolicy.REJECT
            );

            AnalysisReport report = service.execute();

            System.out.println(
                "CORRELATION AND COVARIANCE ANALYSIS"
            );

            System.out.println(
                "Dataset: " + report.dataset()
            );

            System.out.println(
                "Status: " + report.status()
            );

            System.out.println("\nDESCRIPTIVE STATISTICS");

            report.descriptiveStatistics().forEach(
                (name, metrics) -> {
                    System.out.println("\n" + name);
                    metrics.forEach(
                        (metric, value) ->
                            System.out.println(
                                metric + ": " + value
                            )
                    );
                }
            );

            printMatrix(
                "SAMPLE COVARIANCE MATRIX",
                report.covarianceMatrix()
            );

            printMatrix(
                "PEARSON CORRELATION MATRIX",
                report.correlationMatrix()
            );

            System.out.println("\nHIGH CORRELATION PAIRS");

            report.highCorrelationPairs().forEach(
                pair -> System.out.println(
                    pair.first() + " / " +
                    pair.second() + " = " +
                    pair.correlation() + " (" +
                    pair.strength() + ")"
                )
            );

            Dataset missingDataset = new Dataset(
                "Missing Observation Dataset",
                List.of(
                    new Variable(
                        "A",
                        java.util.Arrays.asList(
                            1.0, 2.0, null, 4.0, 5.0
                        )
                    ),
                    new Variable(
                        "B",
                        java.util.Arrays.asList(
                            2.0, 4.0, 6.0, null, 10.0
                        )
                    )
                )
            );

            CorrelationService missingService =
                new CorrelationService(
                    missingDataset,
                    MissingPolicy.PAIRWISE
                );

            System.out.println(
                "\nPAIRWISE MISSING-DATA ANALYSIS"
            );

            System.out.println(
                missingService.analyzePair("A", "B")
            );

            runTests();

        } catch (StatisticalException exception) {
            System.err.println(
                "Statistical analysis failed: " +
                exception.getMessage()
            );

            System.exit(1);
        }
    }
}
