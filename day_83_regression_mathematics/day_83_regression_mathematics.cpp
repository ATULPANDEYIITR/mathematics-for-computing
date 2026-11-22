#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

enum class ModelStatus {
    Unfitted,
    Fitted,
    Failed
};

struct Observation {
    double x;
    double y;
};

struct ResidualRecord {
    double actual;
    double fitted;
    double residual;
    double squaredResidual;
};

struct RegressionMetrics {
    double sse = 0.0;
    double ssr = 0.0;
    double sst = 0.0;
    double rSquared = 0.0;
    double rmse = 0.0;
    double mae = 0.0;
    double residualMean = 0.0;
};

class RegressionException : public runtime_error {
public:
    explicit RegressionException(const string& message)
        : runtime_error(message) {}
};

class RegressionEngine {
private:
    vector<Observation> observations;
    vector<double> fittedValues;
    vector<double> residuals;

    double slope = 0.0;
    double intercept = 0.0;

    double meanX = 0.0;
    double meanY = 0.0;

    RegressionMetrics metrics;
    ModelStatus status = ModelStatus::Unfitted;

    static bool finite(double value) {
        return std::isfinite(value);
    }

    void validateDataset() const {
        if (observations.size() < 3) {
            throw RegressionException(
                "At least three observations are required."
            );
        }

        bool distinctX = false;
        const double firstX = observations.front().x;

        for (const auto& observation : observations) {
            if (
                !finite(observation.x) ||
                !finite(observation.y)
            ) {
                throw RegressionException(
                    "Dataset contains non-finite values."
                );
            }

            if (observation.x != firstX) {
                distinctX = true;
            }
        }

        if (!distinctX) {
            throw RegressionException(
                "Independent variable has zero variance."
            );
        }
    }

    static double compensatedSum(const vector<double>& values) {
        // Kahan summation reduces accumulated floating-point error.
        double sum = 0.0;
        double compensation = 0.0;

        for (double value : values) {
            double adjusted = value - compensation;
            double temporary = sum + adjusted;

            compensation = (temporary - sum) - adjusted;
            sum = temporary;
        }

        return sum;
    }

public:
    explicit RegressionEngine(vector<Observation> data)
        : observations(std::move(data)) {
        validateDataset();
    }

    void fit() {
        status = ModelStatus::Failed;

        const size_t n = observations.size();

        vector<double> xValues;
        vector<double> yValues;

        xValues.reserve(n);
        yValues.reserve(n);

        for (const auto& observation : observations) {
            xValues.push_back(observation.x);
            yValues.push_back(observation.y);
        }

        meanX = compensatedSum(xValues) / n;
        meanY = compensatedSum(yValues) / n;

        vector<double> squaredX;
        vector<double> crossProducts;

        squaredX.reserve(n);
        crossProducts.reserve(n);

        for (const auto& observation : observations) {
            const double dx = observation.x - meanX;
            const double dy = observation.y - meanY;

            squaredX.push_back(dx * dx);
            crossProducts.push_back(dx * dy);
        }

        const double sxx = compensatedSum(squaredX);
        const double sxy = compensatedSum(crossProducts);

        if (
            !finite(sxx) ||
            !finite(sxy) ||
            sxx <= 0.0
        ) {
            throw RegressionException(
                "Cannot estimate regression coefficients."
            );
        }

        slope = sxy / sxx;
        intercept = meanY - slope * meanX;

        if (!finite(slope) || !finite(intercept)) {
            throw RegressionException(
                "Invalid regression coefficients."
            );
        }

        fittedValues.clear();
        residuals.clear();

        fittedValues.reserve(n);
        residuals.reserve(n);

        vector<double> squaredErrors;
        vector<double> explainedSquares;
        vector<double> totalSquares;
        vector<double> absoluteErrors;

        for (const auto& observation : observations) {
            const double fitted =
                intercept + slope * observation.x;

            const double residual =
                observation.y - fitted;

            if (!finite(fitted) || !finite(residual)) {
                throw RegressionException(
                    "Numerical overflow during model fitting."
                );
            }

            fittedValues.push_back(fitted);
            residuals.push_back(residual);

            squaredErrors.push_back(residual * residual);

            explainedSquares.push_back(
                (fitted - meanY) * (fitted - meanY)
            );

            totalSquares.push_back(
                (observation.y - meanY) *
                (observation.y - meanY)
            );

            absoluteErrors.push_back(abs(residual));
        }

        metrics.sse = compensatedSum(squaredErrors);
        metrics.ssr = compensatedSum(explainedSquares);
        metrics.sst = compensatedSum(totalSquares);

        if (
            !finite(metrics.sst) ||
            metrics.sst <= 0.0
        ) {
            throw RegressionException(
                "R-squared is undefined for constant Y."
            );
        }

        metrics.rSquared =
            1.0 - metrics.sse / metrics.sst;

        metrics.rSquared = std::clamp(
            metrics.rSquared,
            0.0,
            1.0
        );

        metrics.rmse = sqrt(
            metrics.sse / static_cast<double>(n)
        );

        metrics.mae =
            compensatedSum(absoluteErrors) /
            static_cast<double>(n);

        metrics.residualMean =
            accumulate(
                residuals.begin(),
                residuals.end(),
                0.0
            ) / static_cast<double>(n);

        const double decompositionError =
            abs(metrics.sst - metrics.sse - metrics.ssr);

        if (
            decompositionError >
            1e-8 * max(1.0, metrics.sst)
        ) {
            throw RegressionException(
                "Sum of squares decomposition failed."
            );
        }

        status = ModelStatus::Fitted;
    }

    double predict(double x) const {
        if (status != ModelStatus::Fitted) {
            throw RegressionException(
                "Model must be fitted before prediction."
            );
        }

        if (!finite(x)) {
            throw RegressionException(
                "Prediction input must be finite."
            );
        }

        const double prediction = intercept + slope * x;

        if (!finite(prediction)) {
            throw RegressionException(
                "Prediction exceeded numeric limits."
            );
        }

        return prediction;
    }

    vector<double> predictBatch(
        const vector<double>& values
    ) const {
        vector<double> predictions;
        predictions.reserve(values.size());

        for (double x : values) {
            predictions.push_back(predict(x));
        }

        return predictions;
    }

    vector<ResidualRecord> getResidualReport() const {
        if (status != ModelStatus::Fitted) {
            throw RegressionException(
                "Residual report requires a fitted model."
            );
        }

        vector<ResidualRecord> report;

        for (size_t i = 0; i < observations.size(); i++) {
            report.push_back({
                observations[i].y,
                fittedValues[i],
                residuals[i],
                residuals[i] * residuals[i]
            });
        }

        return report;
    }

    void printReport() const {
        if (status != ModelStatus::Fitted) {
            throw RegressionException(
                "Model is not fitted."
            );
        }

        cout << fixed << setprecision(6);

        cout << "\nSIMPLE LINEAR REGRESSION\n";
        cout << string(65, '=') << '\n';

        cout << "Regression equation: y = "
             << intercept
             << " + (" << slope << ")x\n";

        cout << "Observations: "
             << observations.size() << '\n';

        cout << "\nMODEL METRICS\n";

        cout << "SSE: " << metrics.sse << '\n';
        cout << "SSR: " << metrics.ssr << '\n';
        cout << "SST: " << metrics.sst << '\n';

        cout << "R-squared: "
             << metrics.rSquared << '\n';

        cout << "RMSE: "
             << metrics.rmse << '\n';

        cout << "MAE: "
             << metrics.mae << '\n';

        cout << "Residual mean: "
             << metrics.residualMean << '\n';

        cout << "\nRESIDUAL REPORT\n";

        cout << left
             << setw(8) << "No."
             << setw(14) << "Actual"
             << setw(14) << "Fitted"
             << setw(14) << "Residual"
             << '\n';

        const auto report = getResidualReport();

        for (size_t i = 0; i < report.size(); i++) {
            cout << left
                 << setw(8) << i + 1
                 << setw(14) << report[i].actual
                 << setw(14) << report[i].fitted
                 << setw(14) << report[i].residual
                 << '\n';
        }

        cout << "\nPREDICTIONS\n";

        for (double x : {6.0, 7.0, 8.0, 10.0}) {
            cout << "X = " << x
                 << " -> Y = " << predict(x)
                 << '\n';
        }
    }

    const RegressionMetrics& getMetrics() const {
        return metrics;
    }

    double getSlope() const {
        return slope;
    }

    double getIntercept() const {
        return intercept;
    }

    ModelStatus getStatus() const {
        return status;
    }
};

void runTests() {
    RegressionEngine model({
        {1, 3},
        {2, 5},
        {3, 7},
        {4, 9},
        {5, 11}
    });

    model.fit();

    if (abs(model.getSlope() - 2.0) > 1e-10) {
        throw RegressionException("Slope test failed.");
    }

    if (abs(model.getIntercept() - 1.0) > 1e-10) {
        throw RegressionException("Intercept test failed.");
    }

    if (
        abs(model.getMetrics().rSquared - 1.0) > 1e-10
    ) {
        throw RegressionException("R-squared test failed.");
    }

    if (abs(model.predict(6) - 13.0) > 1e-10) {
        throw RegressionException("Prediction test failed.");
    }

    bool invalidDatasetRejected = false;

    try {
        RegressionEngine invalid({
            {5, 2},
            {5, 4},
            {5, 6}
        });

        invalid.fit();
    } catch (const RegressionException&) {
        invalidDatasetRejected = true;
    }

    if (!invalidDatasetRejected) {
        throw RegressionException(
            "Constant X validation test failed."
        );
    }

    cout << "\nAll C++17 tests passed.\n";
}

int main() {
    try {
        vector<Observation> dataset = {
            {1, 2.1},
            {2, 3.9},
            {3, 6.2},
            {4, 7.8},
            {5, 10.1},
            {6, 11.9},
            {7, 14.2},
            {8, 15.8}
        };

        RegressionEngine model(std::move(dataset));

        model.fit();
        model.printReport();

        runTests();

    } catch (const exception& error) {
        cerr << "Regression failure: "
             << error.what() << '\n';

        return 1;
    }

    return 0;
}
