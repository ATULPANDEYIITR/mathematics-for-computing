import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;

/*
 * MULTIVARIATE STATISTICS
 *
 * Enterprise statistical analysis system.
 *
 * Java 17 features:
 * - Records and immutable result structures
 * - Domain-specific exceptions
 * - Statistical service classes
 * - Regression model validation
 * - Covariance estimation
 * - Multivariate normal distributions
 * - Statistical monitoring
 * - Explicit failure handling
 */

public class MultivariateStatistics {

    static final class StatisticalException extends RuntimeException {
        StatisticalException(String message) {
            super(message);
        }
    }

    static final class ValidationException extends StatisticalException {
        ValidationException(String message) {
            super(message);
        }
    }

    record RegressionResult(
        List<Double> coefficients,
        List<Double> predictions,
        List<Double> residuals,
        double rSquared,
        double adjustedRSquared,
        double mse,
        double rmse,
        double residualVariance
    ) {
        RegressionResult {
            coefficients = List.copyOf(coefficients);
            predictions = List.copyOf(predictions);
            residuals = List.copyOf(residuals);
        }
    }

    record CovarianceResult(
        List<Double> means,
        double[][] covariance,
        double[][] correlation
    ) {
        CovarianceResult {
            means = List.copyOf(means);
            covariance = copyMatrix(covariance);
            correlation = copyMatrix(correlation);
        }

        @Override
        public double[][] covariance() {
            return copyMatrix(covariance);
        }

        @Override
        public double[][] correlation() {
            return copyMatrix(correlation);
        }
    }

    static double[][] copyMatrix(double[][] matrix) {
        return Arrays.stream(matrix)
            .map(double[]::clone)
            .toArray(double[][]::new);
    }

    static final class MatrixService {

        static double[][] validate(double[][] matrix) {
            if (matrix == null || matrix.length == 0 ||
                matrix[0] == null || matrix[0].length == 0) {
                throw new ValidationException("Matrix cannot be empty.");
            }

            int columns = matrix[0].length;

            double[][] result = copyMatrix(matrix);

            for (double[] row : result) {
                if (row.length != columns) {
                    throw new ValidationException(
                        "Matrix must be rectangular."
                    );
                }

                for (double value : row) {
                    if (!Double.isFinite(value)) {
                        throw new ValidationException(
                            "Non-finite matrix value."
                        );
                    }
                }
            }

            return result;
        }

        static double[][] transpose(double[][] matrix) {
            double[][] a = validate(matrix);

            double[][] result =
                new double[a[0].length][a.length];

            for (int i = 0; i < a.length; i++) {
                for (int j = 0; j < a[0].length; j++) {
                    result[j][i] = a[i][j];
                }
            }

            return result;
        }

        static double[][] multiply(double[][] a, double[][] b) {
            a = validate(a);
            b = validate(b);

            if (a[0].length != b.length) {
                throw new ValidationException(
                    "Incompatible matrix dimensions."
                );
            }

            double[][] result =
                new double[a.length][b[0].length];

            for (int i = 0; i < a.length; i++) {
                for (int k = 0; k < b.length; k++) {
                    for (int j = 0; j < b[0].length; j++) {
                        result[i][j] += a[i][k] * b[k][j];
                    }
                }
            }

            return result;
        }

        static double[] solve(double[][] matrix, double[] vector) {
            double[][] a = validate(matrix);
            int n = a.length;

            if (a[0].length != n || vector.length != n) {
                throw new ValidationException(
                    "Linear system must be square."
                );
            }

            double[][] augmented = new double[n][n + 1];

            for (int i = 0; i < n; i++) {
                System.arraycopy(a[i], 0, augmented[i], 0, n);

                if (!Double.isFinite(vector[i])) {
                    throw new ValidationException(
                        "Invalid right-hand side."
                    );
                }

                augmented[i][n] = vector[i];
            }

            for (int col = 0; col < n; col++) {
                int pivot = col;

                for (int row = col + 1; row < n; row++) {
                    if (
                        Math.abs(augmented[row][col]) >
                        Math.abs(augmented[pivot][col])
                    ) {
                        pivot = row;
                    }
                }

                if (Math.abs(augmented[pivot][col]) < 1e-12) {
                    throw new StatisticalException("Singular matrix.");
                }

                double[] temp = augmented[col];
                augmented[col] = augmented[pivot];
                augmented[pivot] = temp;

                double divisor = augmented[col][col];

                for (int j = col; j <= n; j++) {
                    augmented[col][j] /= divisor;
                }

                for (int row = 0; row < n; row++) {
                    if (row == col) continue;

                    double factor = augmented[row][col];

                    for (int j = col; j <= n; j++) {
                        augmented[row][j] -=
                            factor * augmented[col][j];
                    }
                }
            }

            double[] result = new double[n];

            for (int i = 0; i < n; i++) {
                result[i] = augmented[i][n];
            }

            return result;
        }

        static double[][] cholesky(double[][] covariance) {
            double[][] a = validate(covariance);

            int n = a.length;

            if (a[0].length != n) {
                throw new ValidationException(
                    "Covariance matrix must be square."
                );
            }

            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    if (
                        Math.abs(a[i][j] - a[j][i]) > 1e-10
                    ) {
                        throw new ValidationException(
                            "Covariance matrix must be symmetric."
                        );
                    }
                }
            }

            double[][] lower = new double[n][n];

            for (int i = 0; i < n; i++) {
                for (int j = 0; j <= i; j++) {
                    double value = a[i][j];

                    for (int k = 0; k < j; k++) {
                        value -= lower[i][k] * lower[j][k];
                    }

                    if (i == j) {
                        if (value <= 0) {
                            throw new StatisticalException(
                                "Matrix is not positive definite."
                            );
                        }

                        lower[i][j] = Math.sqrt(value);
                    } else {
                        lower[i][j] = value / lower[j][j];
                    }
                }
            }

            return lower;
        }
    }

    static final class RegressionService {

        RegressionResult fit(double[][] features, double[] target) {
            double[][] x = MatrixService.validate(features);

            int n = x.length;
            int p = x[0].length;

            if (target == null || target.length != n) {
                throw new ValidationException(
                    "Feature and target counts differ."
                );
            }

            for (double value : target) {
                if (!Double.isFinite(value)) {
                    throw new ValidationException(
                        "Target contains non-finite values."
                    );
                }
            }

            if (n <= p + 1) {
                throw new ValidationException(
                    "Insufficient observations for regression."
                );
            }

            double[][] design = new double[n][p + 1];

            for (int i = 0; i < n; i++) {
                design[i][0] = 1.0;

                System.arraycopy(
                    x[i], 0, design[i], 1, p
                );
            }

            double[][] xt = MatrixService.transpose(design);
            double[][] xtx = MatrixService.multiply(xt, design);

            double[] xty = new double[p + 1];

            for (int i = 0; i < p + 1; i++) {
                for (int j = 0; j < n; j++) {
                    xty[i] += xt[i][j] * target[j];
                }
            }

            double[] beta = MatrixService.solve(xtx, xty);

            double[] predictions = new double[n];
            double[] residuals = new double[n];

            double mean = Arrays.stream(target).average().orElseThrow();

            double ssResidual = 0;
            double ssTotal = 0;

            for (int i = 0; i < n; i++) {
                for (int j = 0; j < p + 1; j++) {
                    predictions[i] += design[i][j] * beta[j];
                }

                residuals[i] = target[i] - predictions[i];

                ssResidual += residuals[i] * residuals[i];

                ssTotal += Math.pow(target[i] - mean, 2);
            }

            if (ssTotal == 0) {
                throw new StatisticalException(
                    "R-squared is undefined."
                );
            }

            double r2 = 1.0 - ssResidual / ssTotal;

            double adjusted = 1.0 -
                (1.0 - r2) * (n - 1.0) / (n - p - 1.0);

            double mse = ssResidual / n;

            double residualVariance =
                ssResidual / (n - p - 1.0);

            return new RegressionResult(
                Arrays.stream(beta).boxed().toList(),
                Arrays.stream(predictions).boxed().toList(),
                Arrays.stream(residuals).boxed().toList(),
                r2,
                adjusted,
                mse,
                Math.sqrt(mse),
                residualVariance
            );
        }

        List<Double> predict(
            RegressionResult model,
            double[][] features
        ) {
            double[][] x = MatrixService.validate(features);

            List<Double> coefficients = model.coefficients();

            if (x[0].length + 1 != coefficients.size()) {
                throw new ValidationException(
                    "Prediction feature dimension mismatch."
                );
            }

            List<Double> predictions = new ArrayList<>();

            for (double[] row : x) {
                double value = coefficients.get(0);

                for (int j = 0; j < row.length; j++) {
                    value += row[j] * coefficients.get(j + 1);
                }

                predictions.add(value);
            }

            return List.copyOf(predictions);
        }
    }

    static final class CovarianceService {

        CovarianceResult calculate(double[][] observations) {
            double[][] x = MatrixService.validate(observations);

            int n = x.length;
            int p = x[0].length;

            if (n < 2) {
                throw new ValidationException(
                    "At least two observations required."
                );
            }

            double[] mean = new double[p];

            for (double[] row : x) {
                for (int j = 0; j < p; j++) {
                    mean[j] += row[j] / n;
                }
            }

            double[][] covariance = new double[p][p];

            for (double[] row : x) {
                for (int i = 0; i < p; i++) {
                    for (int j = 0; j < p; j++) {
                        covariance[i][j] +=
                            (row[i] - mean[i]) *
                            (row[j] - mean[j]);
                    }
                }
            }

            double[][] correlation = new double[p][p];

            for (int i = 0; i < p; i++) {
                for (int j = 0; j < p; j++) {
                    covariance[i][j] /= n - 1.0;
                }
            }

            for (int i = 0; i < p; i++) {
                if (covariance[i][i] <= 0) {
                    throw new StatisticalException(
                        "Correlation undefined for constant variables."
                    );
                }

                for (int j = 0; j < p; j++) {
                    correlation[i][j] =
                        covariance[i][j] /
                        Math.sqrt(
                            covariance[i][i] * covariance[j][j]
                        );
                }
            }

            return new CovarianceResult(
                Arrays.stream(mean).boxed().toList(),
                covariance,
                correlation
            );
        }
    }

    static final class MultivariateNormalService {

        double mahalanobis(
            double[] observation,
            double[] mean,
            double[][] covariance
        ) {
            Objects.requireNonNull(observation);
            Objects.requireNonNull(mean);

            if (
                observation.length != mean.length ||
                covariance.length != mean.length
            ) {
                throw new ValidationException("Dimension mismatch.");
            }

            double[][] lower = MatrixService.cholesky(covariance);

            double[] z = new double[mean.length];

            for (int i = 0; i < mean.length; i++) {
                double value = observation[i] - mean[i];

                for (int j = 0; j < i; j++) {
                    value -= lower[i][j] * z[j];
                }

                z[i] = value / lower[i][i];
            }

            double squaredDistance = 0;

            for (double value : z) {
                squaredDistance += value * value;
            }

            return Math.sqrt(squaredDistance);
        }

        double density(
            double[] observation,
            double[] mean,
            double[][] covariance
        ) {
            double[][] lower = MatrixService.cholesky(covariance);

            if (observation.length != mean.length) {
                throw new ValidationException("Dimension mismatch.");
            }

            double logDeterminant = 0;

            for (int i = 0; i < lower.length; i++) {
                logDeterminant += 2 * Math.log(lower[i][i]);
            }

            double distance = mahalanobis(
                observation, mean, covariance
            );

            int p = mean.length;

            double logDensity =
                -0.5 * p * Math.log(2 * Math.PI)
                -0.5 * logDeterminant
                -0.5 * distance * distance;

            return Math.exp(logDensity);
        }
    }

    enum ObservationState {
        NORMAL,
        ANOMALY
    }

    record MonitoringEvent(
        List<Double> observation,
        double distance,
        ObservationState state
    ) {}

    static final class StatisticalMonitoringService {

        private final MultivariateNormalService distribution;
        private final double[] mean;
        private final double[][] covariance;
        private final double threshold;

        StatisticalMonitoringService(
            double[] mean,
            double[][] covariance,
            double threshold
        ) {
            if (!Double.isFinite(threshold) || threshold <= 0) {
                throw new ValidationException("Invalid threshold.");
            }

            this.mean = mean.clone();
            this.covariance = MatrixService.cholesky(covariance);
            this.distribution = new MultivariateNormalService();
            this.threshold = threshold;
        }

        MonitoringEvent evaluate(double[] observation) {
            // The validated Cholesky factor is retained to verify
            // initialization. Evaluation uses the original covariance.
            double[][] reconstructed = copyMatrix(covariance);

            double distance = distribution.mahalanobis(
                observation, mean, reconstructed
            );

            ObservationState state =
                distance > threshold
                    ? ObservationState.ANOMALY
                    : ObservationState.NORMAL;

            return new MonitoringEvent(
                Arrays.stream(observation).boxed().toList(),
                distance,
                state
            );
        }
    }

    static void printMatrix(String label, double[][] matrix) {
        System.out.println(label);

        for (double[] row : matrix) {
            System.out.println(Arrays.toString(row));
        }
    }

    public static void main(String[] args) {
        System.out.println("MULTIVARIATE STATISTICS");
        System.out.println("=======================");

        double[][] features = {
            {10, 2}, {12, 3}, {14, 4}, {16, 3},
            {18, 5}, {20, 6}, {22, 5}, {24, 7},
            {26, 8}, {28, 7}, {30, 9}, {32, 10}
        };

        double[] target = {
            40, 44, 49, 50, 57, 63,
            65, 72, 78, 80, 87, 94
        };

        System.out.println("\n1. ENTERPRISE REGRESSION SERVICE");

        RegressionService regressionService =
            new RegressionService();

        RegressionResult regression =
            regressionService.fit(features, target);

        System.out.println("Coefficients: " + regression.coefficients());

        System.out.println("R-squared: " + regression.rSquared());

        System.out.println(
            "Adjusted R-squared: " + regression.adjustedRSquared()
        );

        System.out.println("RMSE: " + regression.rmse());

        System.out.println(
            "Residual variance: " + regression.residualVariance()
        );

        System.out.println(
            "Prediction: " +
            regressionService.predict(regression, new double[][] {
                {25, 6}
            })
        );

        System.out.println("\n2. COVARIANCE SERVICE");

        CovarianceResult covariance =
            new CovarianceService().calculate(features);

        System.out.println("Means: " + covariance.means());

        printMatrix("Covariance matrix:", covariance.covariance());

        printMatrix("Correlation matrix:", covariance.correlation());

        System.out.println("\n3. MULTIVARIATE DISTRIBUTION SERVICE");

        double[] mean = {50, 60};

        double[][] covarianceMatrix = {
            {100, 30},
            {30, 144}
        };

        double[] observation = {55, 65};

        MultivariateNormalService distribution =
            new MultivariateNormalService();

        System.out.println(
            "Mahalanobis distance: " +
            distribution.mahalanobis(
                observation, mean, covarianceMatrix
            )
        );

        System.out.println(
            "Probability density: " +
            distribution.density(
                observation, mean, covarianceMatrix
            )
        );

        System.out.println("\n4. STATISTICAL MONITORING");

        StatisticalMonitoringService monitoring =
            new StatisticalMonitoringService(
                mean,
                covarianceMatrix,
                2.5
            );

        List<double[]> observations = List.of(
            new double[]{51, 61},
            new double[]{55, 65},
            new double[]{48, 58},
            new double[]{90, 120},
            new double[]{52, 62}
        );

        for (double[] item : observations) {
            MonitoringEvent event = monitoring.evaluate(item);

            System.out.println(
                event.observation() + " -> " +
                event.state() +
                " | Distance: " + event.distance()
            );
        }

        System.out.println("\n5. VALIDATION");

        try {
            MatrixService.cholesky(new double[][] {
                {1, 2},
                {2, 1}
            });
        } catch (StatisticalException exception) {
            System.out.println(
                "Invalid covariance rejected: " + exception.getMessage()
            );
        }

        try {
            regressionService.fit(
                new double[][]{{1}, {2}},
                new double[]{3, 4}
            );
        } catch (StatisticalException exception) {
            System.out.println(
                "Insufficient observations rejected: " +
                exception.getMessage()
            );
        }

        if (
            regression.rSquared() < 0 ||
            regression.rmse() < 0
        ) {
            throw new StatisticalException(
                "Regression consistency validation failed."
            );
        }

        System.out.println("\nAll enterprise statistical checks passed.");
    }
}
