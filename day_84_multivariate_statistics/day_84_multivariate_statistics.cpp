#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

/*
 * MULTIVARIATE STATISTICS
 *
 * A repository-independent statistical engine for:
 * 1. Multiple linear regression.
 * 2. Covariance and correlation structures.
 * 3. Multivariate normal distributions.
 * 4. Mahalanobis distance.
 * 5. Multivariate anomaly detection.
 *
 * C++17, standard library only.
 */

using Matrix = vector<vector<double>>;
using Vector = vector<double>;

class StatisticalError : public runtime_error {
public:
    explicit StatisticalError(const string& message)
        : runtime_error(message) {}
};

class MatrixOperations {
public:
    static void validate(const Matrix& matrix) {
        if (matrix.empty() || matrix.front().empty()) {
            throw StatisticalError("Matrix cannot be empty.");
        }

        const size_t columns = matrix.front().size();

        for (const auto& row : matrix) {
            if (row.size() != columns) {
                throw StatisticalError("Matrix must be rectangular.");
            }

            for (double value : row) {
                if (!isfinite(value)) {
                    throw StatisticalError("Non-finite matrix value.");
                }
            }
        }
    }

    static Matrix transpose(const Matrix& matrix) {
        validate(matrix);

        Matrix result(
            matrix.front().size(),
            Vector(matrix.size())
        );

        for (size_t i = 0; i < matrix.size(); ++i) {
            for (size_t j = 0; j < matrix[i].size(); ++j) {
                result[j][i] = matrix[i][j];
            }
        }

        return result;
    }

    static Matrix multiply(const Matrix& a, const Matrix& b) {
        validate(a);
        validate(b);

        if (a.front().size() != b.size()) {
            throw StatisticalError("Incompatible matrix dimensions.");
        }

        Matrix result(
            a.size(),
            Vector(b.front().size(), 0.0)
        );

        for (size_t i = 0; i < a.size(); ++i) {
            for (size_t k = 0; k < b.size(); ++k) {
                for (size_t j = 0; j < b.front().size(); ++j) {
                    result[i][j] += a[i][k] * b[k][j];
                }
            }
        }

        return result;
    }

    static Vector solve(Matrix a, Vector b) {
        validate(a);

        const size_t n = a.size();

        if (a.front().size() != n || b.size() != n) {
            throw StatisticalError("Linear system must be square.");
        }

        for (double value : b) {
            if (!isfinite(value)) {
                throw StatisticalError("Invalid right-hand side.");
            }
        }

        // Partial pivoting improves numerical stability.
        for (size_t col = 0; col < n; ++col) {
            size_t pivot = col;

            for (size_t row = col + 1; row < n; ++row) {
                if (abs(a[row][col]) > abs(a[pivot][col])) {
                    pivot = row;
                }
            }

            if (abs(a[pivot][col]) < 1e-12) {
                throw StatisticalError("Singular matrix.");
            }

            swap(a[col], a[pivot]);
            swap(b[col], b[pivot]);

            double divisor = a[col][col];

            for (size_t j = col; j < n; ++j) {
                a[col][j] /= divisor;
            }

            b[col] /= divisor;

            for (size_t row = 0; row < n; ++row) {
                if (row == col) continue;

                double factor = a[row][col];

                for (size_t j = col; j < n; ++j) {
                    a[row][j] -= factor * a[col][j];
                }

                b[row] -= factor * b[col];
            }
        }

        return b;
    }
};

struct CovarianceResult {
    Vector means;
    Matrix covariance;
    Matrix correlation;
};

class CovarianceAnalyzer {
public:
    static CovarianceResult analyze(const Matrix& observations) {
        MatrixOperations::validate(observations);

        const size_t n = observations.size();
        const size_t p = observations.front().size();

        if (n < 2) {
            throw StatisticalError("At least two observations required.");
        }

        Vector means(p, 0.0);

        for (const auto& row : observations) {
            for (size_t j = 0; j < p; ++j) {
                means[j] += row[j] / static_cast<double>(n);
            }
        }

        Matrix covariance(p, Vector(p, 0.0));

        for (const auto& row : observations) {
            for (size_t i = 0; i < p; ++i) {
                for (size_t j = 0; j < p; ++j) {
                    covariance[i][j] +=
                        (row[i] - means[i]) *
                        (row[j] - means[j]);
                }
            }
        }

        for (auto& row : covariance) {
            for (double& value : row) {
                value /= static_cast<double>(n - 1);
            }
        }

        Matrix correlation(p, Vector(p, 0.0));

        for (size_t i = 0; i < p; ++i) {
            if (covariance[i][i] <= 0) {
                throw StatisticalError(
                    "Correlation undefined for constant variables."
                );
            }

            for (size_t j = 0; j < p; ++j) {
                if (covariance[j][j] <= 0) {
                    throw StatisticalError(
                        "Invalid covariance diagonal."
                    );
                }

                correlation[i][j] =
                    covariance[i][j] /
                    sqrt(covariance[i][i] * covariance[j][j]);
            }
        }

        return {means, covariance, correlation};
    }
};

struct RegressionResult {
    Vector coefficients;
    Vector predictions;
    Vector residuals;
    double rSquared;
    double adjustedRSquared;
    double mse;
    double rmse;
    double residualVariance;
};

class MultipleRegression {
private:
    Matrix features;
    Vector target;

public:
    MultipleRegression(Matrix x, Vector y)
        : features(move(x)), target(move(y)) {

        MatrixOperations::validate(features);

        if (features.size() != target.size()) {
            throw StatisticalError("Observation counts differ.");
        }

        for (double value : target) {
            if (!isfinite(value)) {
                throw StatisticalError("Invalid target value.");
            }
        }
    }

    RegressionResult fit() const {
        const size_t n = features.size();
        const size_t p = features.front().size();

        if (n <= p + 1) {
            throw StatisticalError(
                "Insufficient observations for regression."
            );
        }

        // First column represents the intercept.
        Matrix design(n, Vector(p + 1, 1.0));

        for (size_t i = 0; i < n; ++i) {
            for (size_t j = 0; j < p; ++j) {
                design[i][j + 1] = features[i][j];
            }
        }

        Matrix xt = MatrixOperations::transpose(design);
        Matrix xtx = MatrixOperations::multiply(xt, design);

        Vector xty(p + 1, 0.0);

        for (size_t i = 0; i < p + 1; ++i) {
            for (size_t j = 0; j < n; ++j) {
                xty[i] += xt[i][j] * target[j];
            }
        }

        Vector beta = MatrixOperations::solve(xtx, xty);

        Vector predictions(n, 0.0);
        Vector residuals(n, 0.0);

        double meanTarget =
            accumulate(target.begin(), target.end(), 0.0) / n;

        double ssResidual = 0.0;
        double ssTotal = 0.0;

        for (size_t i = 0; i < n; ++i) {
            predictions[i] = inner_product(
                design[i].begin(),
                design[i].end(),
                beta.begin(),
                0.0
            );

            residuals[i] = target[i] - predictions[i];

            ssResidual += residuals[i] * residuals[i];

            ssTotal += pow(target[i] - meanTarget, 2);
        }

        if (ssTotal <= 0) {
            throw StatisticalError("R-squared is undefined.");
        }

        double r2 = 1.0 - ssResidual / ssTotal;

        double adjusted = 1.0 -
            (1.0 - r2) *
            static_cast<double>(n - 1) /
            static_cast<double>(n - p - 1);

        double mse = ssResidual / n;
        double residualVariance =
            ssResidual / static_cast<double>(n - p - 1);

        return {
            beta,
            predictions,
            residuals,
            r2,
            adjusted,
            mse,
            sqrt(mse),
            residualVariance
        };
    }
};

class CholeskyDecomposition {
public:
    static Matrix factorize(const Matrix& covariance) {
        MatrixOperations::validate(covariance);

        const size_t n = covariance.size();

        if (covariance.front().size() != n) {
            throw StatisticalError("Covariance must be square.");
        }

        Matrix lower(n, Vector(n, 0.0));

        for (size_t i = 0; i < n; ++i) {
            for (size_t j = 0; j < n; ++j) {
                if (abs(covariance[i][j] - covariance[j][i]) > 1e-10) {
                    throw StatisticalError("Matrix is not symmetric.");
                }
            }
        }

        for (size_t i = 0; i < n; ++i) {
            for (size_t j = 0; j <= i; ++j) {
                double value = covariance[i][j];

                for (size_t k = 0; k < j; ++k) {
                    value -= lower[i][k] * lower[j][k];
                }

                if (i == j) {
                    if (value <= 0) {
                        throw StatisticalError(
                            "Matrix is not positive definite."
                        );
                    }

                    lower[i][j] = sqrt(value);
                } else {
                    lower[i][j] = value / lower[j][j];
                }
            }
        }

        return lower;
    }
};

class MultivariateDistribution {
public:
    static double mahalanobis(
        const Vector& observation,
        const Vector& mean,
        const Matrix& covariance
    ) {
        if (observation.size() != mean.size()) {
            throw StatisticalError("Dimension mismatch.");
        }

        Matrix lower = CholeskyDecomposition::factorize(covariance);

        if (lower.size() != observation.size()) {
            throw StatisticalError("Covariance dimension mismatch.");
        }

        Vector difference(observation.size());

        for (size_t i = 0; i < difference.size(); ++i) {
            difference[i] = observation[i] - mean[i];
        }

        // Solve Lz = x - mean.
        Vector z(difference.size(), 0.0);

        for (size_t i = 0; i < z.size(); ++i) {
            double value = difference[i];

            for (size_t j = 0; j < i; ++j) {
                value -= lower[i][j] * z[j];
            }

            z[i] = value / lower[i][i];
        }

        return sqrt(inner_product(z.begin(), z.end(), z.begin(), 0.0));
    }

    static double density(
        const Vector& observation,
        const Vector& mean,
        const Matrix& covariance
    ) {
        Matrix lower = CholeskyDecomposition::factorize(covariance);

        if (observation.size() != mean.size() ||
            lower.size() != mean.size()) {
            throw StatisticalError("Dimension mismatch.");
        }

        double logDeterminant = 0.0;

        for (size_t i = 0; i < lower.size(); ++i) {
            logDeterminant += 2.0 * log(lower[i][i]);
        }

        double distance = mahalanobis(
            observation, mean, covariance
        );

        const double n = static_cast<double>(mean.size());

        double logDensity =
            -0.5 * n * log(2.0 * acos(-1.0))
            -0.5 * logDeterminant
            -0.5 * distance * distance;

        return exp(logDensity);
    }
};

class AnomalyDetector {
private:
    Vector mean;
    Matrix covariance;
    double threshold;

public:
    AnomalyDetector(
        Vector center,
        Matrix covarianceMatrix,
        double distanceThreshold
    )
        : mean(move(center)),
          covariance(move(covarianceMatrix)),
          threshold(distanceThreshold) {

        if (!isfinite(threshold) || threshold <= 0) {
            throw StatisticalError("Invalid threshold.");
        }

        CholeskyDecomposition::factorize(covariance);
    }

    bool isAnomaly(const Vector& observation) const {
        return MultivariateDistribution::mahalanobis(
            observation, mean, covariance
        ) > threshold;
    }
};

void printVector(const string& label, const Vector& values) {
    cout << label << ": ";

    for (double value : values) {
        cout << fixed << setprecision(4) << value << " ";
    }

    cout << '\n';
}

void printMatrix(const string& label, const Matrix& matrix) {
    cout << label << ":\n";

    for (const auto& row : matrix) {
        for (double value : row) {
            cout << setw(12) << fixed << setprecision(4) << value;
        }

        cout << '\n';
    }
}

int main() {
    try {
        cout << "MULTIVARIATE STATISTICS ENGINE\n";
        cout << "==============================\n";

        // Business analytics: sales as a function of advertising
        // expenditure and employee training.
        Matrix features = {
            {10, 2}, {12, 3}, {14, 4}, {16, 3},
            {18, 5}, {20, 6}, {22, 5}, {24, 7},
            {26, 8}, {28, 7}, {30, 9}, {32, 10}
        };

        Vector target = {
            40, 44, 49, 50, 57, 63,
            65, 72, 78, 80, 87, 94
        };

        cout << "\n1. MULTIPLE REGRESSION\n";

        MultipleRegression model(features, target);
        RegressionResult result = model.fit();

        printVector("Coefficients", result.coefficients);

        cout << "R-squared: "
             << result.rSquared << '\n';

        cout << "Adjusted R-squared: "
             << result.adjustedRSquared << '\n';

        cout << "RMSE: " << result.rmse << '\n';

        cout << "Residual variance: "
             << result.residualVariance << '\n';

        cout << "\n2. COVARIANCE STRUCTURE\n";

        CovarianceResult covariance =
            CovarianceAnalyzer::analyze(features);

        printVector("Means", covariance.means);

        printMatrix(
            "Covariance matrix",
            covariance.covariance
        );

        printMatrix(
            "Correlation matrix",
            covariance.correlation
        );

        cout << "\n3. MULTIVARIATE NORMAL DISTRIBUTION\n";

        Vector mean = {50, 60};

        Matrix covarianceMatrix = {
            {100, 30},
            {30, 144}
        };

        Vector observation = {55, 65};

        double distance = MultivariateDistribution::mahalanobis(
            observation, mean, covarianceMatrix
        );

        double probabilityDensity = MultivariateDistribution::density(
            observation, mean, covarianceMatrix
        );

        cout << "Mahalanobis distance: " << distance << '\n';

        cout << "Probability density: "
             << probabilityDensity << '\n';

        cout << "\n4. MULTIVARIATE ANOMALY DETECTION\n";

        AnomalyDetector detector(
            mean,
            covarianceMatrix,
            2.5
        );

        vector<Vector> observations = {
            {51, 61},
            {55, 65},
            {48, 58},
            {90, 120},
            {52, 62}
        };

        for (const auto& item : observations) {
            cout << "Observation ";

            printVector("", item);

            cout << "Classification: "
                 << (detector.isAnomaly(item)
                     ? "ANOMALY"
                     : "NORMAL")
                 << "\n\n";
        }

        cout << "5. REPRODUCIBLE MULTIVARIATE SAMPLING\n";

        mt19937 generator(42);
        normal_distribution<double> normal(0.0, 1.0);

        Matrix lower =
            CholeskyDecomposition::factorize(covarianceMatrix);

        vector<Vector> samples;

        for (int i = 0; i < 1000; ++i) {
            Vector z = {
                normal(generator),
                normal(generator)
            };

            Vector sample(2);

            for (size_t j = 0; j < 2; ++j) {
                sample[j] = mean[j];

                for (size_t k = 0; k <= j; ++k) {
                    sample[j] += lower[j][k] * z[k];
                }
            }

            samples.push_back(sample);
        }

        cout << "Generated observations: "
             << samples.size() << '\n';

        cout << "\n6. FAILURE HANDLING\n";

        try {
            Matrix invalid = {
                {1, 2},
                {2, 1}
            };

            CholeskyDecomposition::factorize(invalid);
        } catch (const StatisticalError& error) {
            cout << "Invalid covariance rejected: "
                 << error.what() << '\n';
        }

        try {
            MultipleRegression invalidModel(
                {{1}, {2}},
                {3, 4}
            );

            invalidModel.fit();
        } catch (const StatisticalError& error) {
            cout << "Insufficient data rejected: "
                 << error.what() << '\n';
        }

        if (result.rmse < 0 || result.rSquared > 1.0 + 1e-9) {
            throw StatisticalError("Regression consistency failure.");
        }

        cout << "\nAll statistical operations completed.\n";
    }
    catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
