import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

/*
 * Regression Mathematics
 *
 * Enterprise-oriented simple linear regression engine.
 *
 * Java version: 17
 *
 * Features:
 * - Immutable observations
 * - Dataset version management
 * - Regression service
 * - OLS coefficient estimation
 * - Residual analysis
 * - Model evaluation
 * - Prediction
 * - Validation policies
 * - Model lifecycle management
 * - Numerical integrity checks
 */

public class RegressionEnterprise {

    enum ModelStatus {
        UNFITTED,
        FITTED,
        FAILED
    }

    enum ValidationPolicy {
        REQUIRE_THREE_OBSERVATIONS,
        REQUIRE_VARIATION_IN_X,
        REQUIRE_VARIATION_IN_Y,
        REQUIRE_FINITE_VALUES
    }

    record Observation(double x, double y) {

        Observation {
            if (!Double.isFinite(x) || !Double.isFinite(y)) {
                throw new IllegalArgumentException(
                    "Observation values must be finite."
                );
            }
        }
    }

    record Residual(
        int observationNumber,
        double actual,
        double fitted,
        double error,
        double squaredError
    ) {}

    record Metrics(
        double sse,
        double ssr,
        double sst,
        double rSquared,
        double rmse,
        double mae,
        double residualMean,
        double residualStandardDeviation
    ) {}

    record ModelSnapshot(
        long datasetVersion,
        int observationCount,
        double slope,
        double intercept,
        Metrics metrics
    ) {}

    static class RegressionException extends RuntimeException {

        RegressionException(String message) {
            super(message);
        }
    }

    static class DatasetValidationException
        extends RegressionException {

        DatasetValidationException(String message) {
            super(message);
        }
    }

    static class RegressionDataset {

        private final List<Observation> observations =
            new ArrayList<>();

        private final AtomicLong version =
            new AtomicLong(0);

        public synchronized void add(
            Observation observation
        ) {
            Objects.requireNonNull(
                observation,
                "Observation cannot be null."
            );

            observations.add(observation);
            version.incrementAndGet();
        }

        public synchronized void addBatch(
            List<Observation> batch
        ) {
            Objects.requireNonNull(batch);

            if (batch.stream().anyMatch(Objects::isNull)) {
                throw new DatasetValidationException(
                    "Batch contains null observations."
                );
            }

            // Batch insertion is atomic with respect to validation.
            observations.addAll(batch);

            if (!batch.isEmpty()) {
                version.incrementAndGet();
            }
        }

        public synchronized List<Observation> snapshot() {
            return List.copyOf(observations);
        }

        public long getVersion() {
            return version.get();
        }

        public synchronized int size() {
            return observations.size();
        }
    }

    static class ValidationService {

        private final List<ValidationPolicy> policies;

        ValidationService(
            List<ValidationPolicy> policies
        ) {
            this.policies = List.copyOf(policies);
        }

        public void validate(
            List<Observation> observations
        ) {
            if (
                policies.contains(
                    ValidationPolicy.REQUIRE_THREE_OBSERVATIONS
                ) &&
                observations.size() < 3
            ) {
                throw new DatasetValidationException(
                    "At least three observations are required."
                );
            }

            if (
                policies.contains(
                    ValidationPolicy.REQUIRE_VARIATION_IN_X
                )
            ) {
                long distinctX = observations.stream()
                    .map(Observation::x)
                    .distinct()
                    .count();

                if (distinctX < 2) {
                    throw new DatasetValidationException(
                        "Independent variable has zero variance."
                    );
                }
            }

            if (
                policies.contains(
                    ValidationPolicy.REQUIRE_VARIATION_IN_Y
                )
            ) {
                long distinctY = observations.stream()
                    .map(Observation::y)
                    .distinct()
                    .count();

                if (distinctY < 2) {
                    throw new DatasetValidationException(
                        "Dependent variable has zero variance."
                    );
                }
            }

            if (
                policies.contains(
                    ValidationPolicy.REQUIRE_FINITE_VALUES
                )
            ) {
                boolean invalid = observations.stream()
                    .anyMatch(
                        observation ->
                            !Double.isFinite(observation.x()) ||
                            !Double.isFinite(observation.y())
                    );

                if (invalid) {
                    throw new DatasetValidationException(
                        "Non-finite values detected."
                    );
                }
            }
        }
    }

    static class RegressionModel {

        private final double slope;
        private final double intercept;

        private final double meanX;
        private final double meanY;

        private final List<Double> actualValues;
        private final List<Double> fittedValues;
        private final List<Double> residualValues;

        private final Metrics metrics;
        private final long datasetVersion;

        RegressionModel(
            double slope,
            double intercept,
            double meanX,
            double meanY,
            List<Double> actualValues,
            List<Double> fittedValues,
            List<Double> residualValues,
            Metrics metrics,
            long datasetVersion
        ) {
            this.slope = slope;
            this.intercept = intercept;
            this.meanX = meanX;
            this.meanY = meanY;

            this.actualValues = List.copyOf(actualValues);
            this.fittedValues = List.copyOf(fittedValues);
            this.residualValues = List.copyOf(residualValues);

            this.metrics = metrics;
            this.datasetVersion = datasetVersion;
        }

        public double predict(double x) {
            if (!Double.isFinite(x)) {
                throw new IllegalArgumentException(
                    "Prediction input must be finite."
                );
            }

            double prediction = intercept + slope * x;

            if (!Double.isFinite(prediction)) {
                throw new RegressionException(
                    "Prediction exceeded numeric limits."
                );
            }

            return prediction;
        }

        public List<Double> predictBatch(
            List<Double> values
        ) {
            return values.stream()
                .map(this::predict)
                .collect(Collectors.toUnmodifiableList());
        }

        public List<Residual> residualReport() {
            List<Residual> report = new ArrayList<>();

            for (int i = 0; i < actualValues.size(); i++) {
                double error = residualValues.get(i);

                report.add(
                    new Residual(
                        i + 1,
                        actualValues.get(i),
                        fittedValues.get(i),
                        error,
                        error * error
                    )
                );
            }

            return Collections.unmodifiableList(report);
        }

        public double slope() {
            return slope;
        }

        public double intercept() {
            return intercept;
        }

        public Metrics metrics() {
            return metrics;
        }

        public long datasetVersion() {
            return datasetVersion;
        }

        public String equation() {
            String operator = slope >= 0 ? "+" : "-";

            return String.format(
                "y = %.6f %s %.6fx",
                intercept,
                operator,
                Math.abs(slope)
            );
        }
    }

    static class RegressionService {

        private final ValidationService validationService;

        private ModelStatus status = ModelStatus.UNFITTED;

        private Optional<RegressionModel> currentModel =
            Optional.empty();

        RegressionService(
            ValidationService validationService
        ) {
            this.validationService = validationService;
        }

        public synchronized RegressionModel fit(
            RegressionDataset dataset
        ) {
            Objects.requireNonNull(dataset);

            status = ModelStatus.FAILED;

            List<Observation> observations =
                dataset.snapshot();

            validationService.validate(observations);

            int n = observations.size();

            double meanX = observations.stream()
                .mapToDouble(Observation::x)
                .average()
                .orElseThrow();

            double meanY = observations.stream()
                .mapToDouble(Observation::y)
                .average()
                .orElseThrow();

            double sxx = observations.stream()
                .mapToDouble(
                    observation ->
                        Math.pow(observation.x() - meanX, 2)
                )
                .sum();

            double sxy = observations.stream()
                .mapToDouble(
                    observation ->
                        (observation.x() - meanX) *
                        (observation.y() - meanY)
                )
                .sum();

            if (
                !Double.isFinite(sxx) ||
                !Double.isFinite(sxy) ||
                sxx <= 0
            ) {
                throw new RegressionException(
                    "Unable to estimate regression coefficients."
                );
            }

            double slope = sxy / sxx;
            double intercept = meanY - slope * meanX;

            if (
                !Double.isFinite(slope) ||
                !Double.isFinite(intercept)
            ) {
                throw new RegressionException(
                    "Invalid regression coefficients."
                );
            }

            List<Double> actualValues = new ArrayList<>();
            List<Double> fittedValues = new ArrayList<>();
            List<Double> residuals = new ArrayList<>();

            double sse = 0;
            double ssr = 0;
            double sst = 0;
            double absoluteError = 0;
            double residualSum = 0;

            for (Observation observation : observations) {

                double fitted =
                    intercept + slope * observation.x();

                double residual =
                    observation.y() - fitted;

                if (
                    !Double.isFinite(fitted) ||
                    !Double.isFinite(residual)
                ) {
                    throw new RegressionException(
                        "Numerical overflow during fitting."
                    );
                }

                actualValues.add(observation.y());
                fittedValues.add(fitted);
                residuals.add(residual);

                sse += residual * residual;

                ssr += Math.pow(
                    fitted - meanY,
                    2
                );

                sst += Math.pow(
                    observation.y() - meanY,
                    2
                );

                absoluteError += Math.abs(residual);
                residualSum += residual;
            }

            if (
                !Double.isFinite(sst) ||
                sst <= 0
            ) {
                throw new RegressionException(
                    "R-squared is undefined for constant Y."
                );
            }

            double rSquared = 1.0 - sse / sst;

            double rmse = Math.sqrt(sse / n);
            double mae = absoluteError / n;

            double residualMean = residualSum / n;

            double residualStd = Math.sqrt(
                sse / (n - 2)
            );

            if (
                Math.abs(sst - sse - ssr) >
                1e-8 * Math.max(1, sst)
            ) {
                throw new RegressionException(
                    "Sum of squares validation failed."
                );
            }

            Metrics metrics = new Metrics(
                sse,
                ssr,
                sst,
                Math.max(0, Math.min(1, rSquared)),
                rmse,
                mae,
                residualMean,
                residualStd
            );

            RegressionModel model = new RegressionModel(
                slope,
                intercept,
                meanX,
                meanY,
                actualValues,
                fittedValues,
                residuals,
                metrics,
                dataset.getVersion()
            );

            currentModel = Optional.of(model);
            status = ModelStatus.FITTED;

            return model;
        }

        public ModelStatus status() {
            return status;
        }

        public Optional<RegressionModel> currentModel() {
            return currentModel;
        }

        public ModelSnapshot snapshot() {
            RegressionModel model = currentModel.orElseThrow(
                () -> new RegressionException(
                    "No fitted model is available."
                )
            );

            return new ModelSnapshot(
                model.datasetVersion(),
                model.actualValues.size(),
                model.slope(),
                model.intercept(),
                model.metrics()
            );
        }
    }

    private static void printReport(
        RegressionModel model
    ) {
        System.out.println("\nSIMPLE LINEAR REGRESSION");
        System.out.println("=".repeat(65));

        System.out.println("Equation: " + model.equation());

        System.out.printf(
            "Slope: %.6f%n",
            model.slope()
        );

        System.out.printf(
            "Intercept: %.6f%n",
            model.intercept()
        );

        System.out.println(
            "Dataset version: " + model.datasetVersion()
        );

        Metrics metrics = model.metrics();

        System.out.println("\nMODEL METRICS");

        System.out.printf("SSE: %.6f%n", metrics.sse());
        System.out.printf("SSR: %.6f%n", metrics.ssr());
        System.out.printf("SST: %.6f%n", metrics.sst());

        System.out.printf(
            "R-squared: %.6f%n",
            metrics.rSquared()
        );

        System.out.printf("RMSE: %.6f%n", metrics.rmse());
        System.out.printf("MAE: %.6f%n", metrics.mae());

        System.out.printf(
            "Residual mean: %.10f%n",
            metrics.residualMean()
        );

        System.out.printf(
            "Residual standard deviation: %.6f%n",
            metrics.residualStandardDeviation()
        );

        System.out.println("\nRESIDUAL REPORT");

        System.out.printf(
            "%-8s %-12s %-12s %-12s%n",
            "No.",
            "Actual",
            "Fitted",
            "Residual"
        );

        for (Residual residual : model.residualReport()) {
            System.out.printf(
                "%-8d %-12.3f %-12.3f %-12.3f%n",
                residual.observationNumber(),
                residual.actual(),
                residual.fitted(),
                residual.error()
            );
        }

        System.out.println("\nPREDICTIONS");

        for (double x : List.of(6.0, 7.0, 8.0, 10.0)) {
            System.out.printf(
                "X = %.2f -> Y = %.4f%n",
                x,
                model.predict(x)
            );
        }
    }

    private static void runTests() {

        RegressionDataset dataset = new RegressionDataset();

        dataset.addBatch(
            List.of(
                new Observation(1, 3),
                new Observation(2, 5),
                new Observation(3, 7),
                new Observation(4, 9),
                new Observation(5, 11)
            )
        );

        ValidationService validation =
            new ValidationService(
                List.of(
                    ValidationPolicy.REQUIRE_THREE_OBSERVATIONS,
                    ValidationPolicy.REQUIRE_VARIATION_IN_X,
                    ValidationPolicy.REQUIRE_VARIATION_IN_Y,
                    ValidationPolicy.REQUIRE_FINITE_VALUES
                )
            );

        RegressionService service =
            new RegressionService(validation);

        RegressionModel model = service.fit(dataset);

        if (Math.abs(model.slope() - 2.0) > 1e-10) {
            throw new AssertionError("Slope test failed.");
        }

        if (Math.abs(model.intercept() - 1.0) > 1e-10) {
            throw new AssertionError("Intercept test failed.");
        }

        if (
            Math.abs(model.metrics().rSquared() - 1.0) > 1e-10
        ) {
            throw new AssertionError("R-squared test failed.");
        }

        if (Math.abs(model.predict(6) - 13.0) > 1e-10) {
            throw new AssertionError("Prediction test failed.");
        }

        System.out.println("\nAll Java 17 tests passed.");
    }

    public static void main(String[] args) {

        try {
            RegressionDataset dataset = new RegressionDataset();

            dataset.addBatch(
                List.of(
                    new Observation(1, 2.1),
                    new Observation(2, 3.9),
                    new Observation(3, 6.2),
                    new Observation(4, 7.8),
                    new Observation(5, 10.1),
                    new Observation(6, 11.9),
                    new Observation(7, 14.2),
                    new Observation(8, 15.8)
                )
            );

            ValidationService validation =
                new ValidationService(
                    List.of(
                        ValidationPolicy.REQUIRE_THREE_OBSERVATIONS,
                        ValidationPolicy.REQUIRE_VARIATION_IN_X,
                        ValidationPolicy.REQUIRE_VARIATION_IN_Y,
                        ValidationPolicy.REQUIRE_FINITE_VALUES
                    )
                );

            RegressionService service =
                new RegressionService(validation);

            RegressionModel model = service.fit(dataset);

            printReport(model);

            ModelSnapshot snapshot = service.snapshot();

            System.out.println(
                "\nModel lifecycle status: " + service.status()
            );

            System.out.println(
                "Model snapshot: " + snapshot
            );

            runTests();

        } catch (RegressionException | IllegalArgumentException error) {
            System.err.println(
                "Regression processing failed: " +
                error.getMessage()
            );

            System.exit(1);
        }
    }
}
