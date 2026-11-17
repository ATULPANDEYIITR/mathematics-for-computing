#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

/*
 * Correlation and Covariance Analysis Engine
 *
 * C++17
 *
 * Implements:
 * - Sample and population covariance
 * - Pearson correlation
 * - Covariance matrices
 * - Correlation matrices
 * - Missing observation handling
 * - Portfolio dependence analysis
 * - High-correlation detection
 * - Matrix validation
 * - Merge-free, cache-friendly numerical processing
 */

class StatisticalException : public runtime_error {
public:
    explicit StatisticalException(const string& message)
        : runtime_error(message) {}
};

enum class MissingPolicy {
    REJECT,
    PAIRWISE,
    LISTWISE
};

enum class CorrelationCategory {
    NEGLIGIBLE,
    WEAK,
    MODERATE,
    STRONG,
    VERY_STRONG
};

struct Observation {
    string variable;
    vector<double> values;
};

struct PairResult {
    string first;
    string second;
    double covariance;
    double correlation;
    size_t observations;
    bool correlationDefined;
};

class Dataset {
private:
    string name;
    vector<Observation> observations;

public:
    Dataset(
        string datasetName,
        vector<Observation> data
    ) : name(move(datasetName)), observations(move(data)) {
        validate();
    }

    void validate() const {
        if (name.empty()) {
            throw StatisticalException(
                "Dataset name cannot be empty."
            );
        }

        if (observations.size() < 2) {
            throw StatisticalException(
                "At least two variables are required."
            );
        }

        const size_t expected = observations.front().values.size();

        if (expected < 2) {
            throw StatisticalException(
                "At least two observation positions are required."
            );
        }

        for (const auto& observation : observations) {
            if (observation.variable.empty()) {
                throw StatisticalException(
                    "Variable name cannot be empty."
                );
            }

            if (observation.values.size() != expected) {
                throw StatisticalException(
                    "All variables must have equal lengths."
                );
            }

            for (double value : observation.values) {
                if (
                    !std::isfinite(value) &&
                    !std::isnan(value)
                ) {
                    throw StatisticalException(
                        "Infinite values are not permitted."
                    );
                }
            }
        }
    }

    const string& getName() const {
        return name;
    }

    const vector<Observation>& getObservations() const {
        return observations;
    }

    size_t size() const {
        return observations.size();
    }

    const Observation& get(size_t index) const {
        if (index >= observations.size()) {
            throw StatisticalException(
                "Variable index out of range."
            );
        }

        return observations[index];
    }

    int findVariable(const string& variable) const {
        for (size_t i = 0; i < observations.size(); ++i) {
            if (observations[i].variable == variable) {
                return static_cast<int>(i);
            }
        }

        return -1;
    }
};

class Statistics {
public:
    static double mean(const vector<double>& values) {
        if (values.empty()) {
            throw StatisticalException(
                "Mean requires observations."
            );
        }

        long double sum = 0.0L;

        for (double value : values) {
            if (!std::isfinite(value)) {
                throw StatisticalException(
                    "Mean input must contain finite values."
                );
            }

            sum += static_cast<long double>(value);
        }

        return static_cast<double>(
            sum / values.size()
        );
    }

    static double variance(
        const vector<double>& values,
        bool sample = true
    ) {
        const size_t minimum = sample ? 2 : 1;

        if (values.size() < minimum) {
            throw StatisticalException(
                "Insufficient observations for variance."
            );
        }

        const double average = mean(values);

        long double sum = 0.0L;

        for (double value : values) {
            const long double difference =
                static_cast<long double>(value) - average;

            sum += difference * difference;
        }

        const size_t denominator =
            values.size() - (sample ? 1 : 0);

        return static_cast<double>(sum / denominator);
    }

    static double covariance(
        const vector<double>& x,
        const vector<double>& y,
        bool sample = true
    ) {
        if (x.size() != y.size()) {
            throw StatisticalException(
                "Observation counts must match."
            );
        }

        const size_t minimum = sample ? 2 : 1;

        if (x.size() < minimum) {
            throw StatisticalException(
                "Insufficient observations for covariance."
            );
        }

        const double mx = mean(x);
        const double my = mean(y);

        long double sum = 0.0L;

        for (size_t i = 0; i < x.size(); ++i) {
            sum += (
                static_cast<long double>(x[i]) - mx
            ) * (
                static_cast<long double>(y[i]) - my
            );
        }

        const size_t denominator =
            x.size() - (sample ? 1 : 0);

        return static_cast<double>(sum / denominator);
    }

    static double pearson(
        const vector<double>& x,
        const vector<double>& y
    ) {
        if (x.size() != y.size() || x.size() < 2) {
            throw StatisticalException(
                "Pearson correlation requires matched observations."
            );
        }

        const double mx = mean(x);
        const double my = mean(y);

        long double sumXX = 0.0L;
        long double sumYY = 0.0L;
        long double sumXY = 0.0L;

        for (size_t i = 0; i < x.size(); ++i) {
            const long double dx =
                static_cast<long double>(x[i]) - mx;

            const long double dy =
                static_cast<long double>(y[i]) - my;

            sumXX += dx * dx;
            sumYY += dy * dy;
            sumXY += dx * dy;
        }

        if (sumXX <= 0.0L || sumYY <= 0.0L) {
            throw StatisticalException(
                "Correlation is undefined for constant variables."
            );
        }

        const long double result =
            sumXY / sqrt(sumXX * sumYY);

        return static_cast<double>(
            max(-1.0L, min(1.0L, result))
        );
    }

    static CorrelationCategory classify(double value) {
        const double magnitude = abs(value);

        if (magnitude >= 0.90) {
            return CorrelationCategory::VERY_STRONG;
        }

        if (magnitude >= 0.70) {
            return CorrelationCategory::STRONG;
        }

        if (magnitude >= 0.40) {
            return CorrelationCategory::MODERATE;
        }

        if (magnitude >= 0.20) {
            return CorrelationCategory::WEAK;
        }

        return CorrelationCategory::NEGLIGIBLE;
    }

    static string categoryName(CorrelationCategory category) {
        switch (category) {
            case CorrelationCategory::VERY_STRONG:
                return "Very Strong";

            case CorrelationCategory::STRONG:
                return "Strong";

            case CorrelationCategory::MODERATE:
                return "Moderate";

            case CorrelationCategory::WEAK:
                return "Weak";

            default:
                return "Negligible";
        }
    }
};

class Matrix {
private:
    vector<vector<double>> values;
    vector<string> labels;

public:
    Matrix(
        vector<string> variableNames,
        double initialValue = 0.0
    ) : labels(move(variableNames)) {
        values.assign(
            labels.size(),
            vector<double>(labels.size(), initialValue)
        );
    }

    size_t dimension() const {
        return values.size();
    }

    void set(size_t row, size_t column, double value) {
        if (row >= dimension() || column >= dimension()) {
            throw StatisticalException(
                "Matrix index out of range."
            );
        }

        values[row][column] = value;
    }

    double get(size_t row, size_t column) const {
        if (row >= dimension() || column >= dimension()) {
            throw StatisticalException(
                "Matrix index out of range."
            );
        }

        return values[row][column];
    }

    void validateSymmetry(double tolerance = 1e-10) const {
        for (size_t i = 0; i < dimension(); ++i) {
            for (size_t j = i + 1; j < dimension(); ++j) {
                if (
                    abs(values[i][j] - values[j][i]) > tolerance
                ) {
                    throw StatisticalException(
                        "Matrix symmetry validation failed."
                    );
                }
            }
        }
    }

    void print(const string& title) const {
        cout << "\n" << title << "\n";

        cout << setw(16) << "";

        for (const auto& label : labels) {
            cout << setw(14) << label;
        }

        cout << "\n";

        for (size_t i = 0; i < dimension(); ++i) {
            cout << setw(16) << labels[i];

            for (size_t j = 0; j < dimension(); ++j) {
                cout << setw(14)
                     << fixed << setprecision(4)
                     << values[i][j];
            }

            cout << "\n";
        }
    }

    const vector<string>& getLabels() const {
        return labels;
    }
};

class PortfolioAnalyzer {
private:
    Dataset dataset;
    MissingPolicy missingPolicy;

    pair<vector<double>, vector<double>> getPairs(
        size_t first,
        size_t second
    ) const {
        const auto& x = dataset.get(first).values;
        const auto& y = dataset.get(second).values;

        vector<double> pairedX;
        vector<double> pairedY;

        const auto& observations = dataset.getObservations();

        for (size_t i = 0; i < x.size(); ++i) {
            bool complete = true;

            if (missingPolicy == MissingPolicy::LISTWISE) {
                for (const auto& variable : observations) {
                    if (std::isnan(variable.values[i])) {
                        complete = false;
                        break;
                    }
                }
            }

            if (!complete) {
                continue;
            }

            const bool missing =
                std::isnan(x[i]) || std::isnan(y[i]);

            if (missing) {
                if (missingPolicy == MissingPolicy::REJECT) {
                    throw StatisticalException(
                        "Missing values encountered."
                    );
                }

                continue;
            }

            pairedX.push_back(x[i]);
            pairedY.push_back(y[i]);
        }

        return {pairedX, pairedY};
    }

public:
    PortfolioAnalyzer(
        Dataset input,
        MissingPolicy policy = MissingPolicy::REJECT
    ) : dataset(move(input)), missingPolicy(policy) {}

    PairResult analyzePair(
        const string& first,
        const string& second
    ) const {
        const int firstIndex = dataset.findVariable(first);
        const int secondIndex = dataset.findVariable(second);

        if (firstIndex < 0 || secondIndex < 0) {
            throw StatisticalException(
                "Unknown portfolio variable."
            );
        }

        auto paired = getPairs(
            static_cast<size_t>(firstIndex),
            static_cast<size_t>(secondIndex)
        );

        const auto& x = paired.first;
        const auto& y = paired.second;

        if (x.size() < 2) {
            throw StatisticalException(
                "Insufficient paired observations."
            );
        }

        const double cov = Statistics::covariance(x, y);

        const bool defined =
            Statistics::variance(x) > 0.0 &&
            Statistics::variance(y) > 0.0;

        const double corr = defined
            ? Statistics::pearson(x, y)
            : numeric_limits<double>::quiet_NaN();

        return {
            first,
            second,
            cov,
            corr,
            x.size(),
            defined
        };
    }

    Matrix buildCovarianceMatrix() const {
        vector<string> names;

        for (const auto& observation : dataset.getObservations()) {
            names.push_back(observation.variable);
        }

        Matrix matrix(names);

        for (size_t i = 0; i < dataset.size(); ++i) {
            for (size_t j = i; j < dataset.size(); ++j) {
                auto pairs = getPairs(i, j);

                double value = Statistics::covariance(
                    pairs.first,
                    pairs.second
                );

                matrix.set(i, j, value);
                matrix.set(j, i, value);
            }
        }

        matrix.validateSymmetry();

        return matrix;
    }

    Matrix buildCorrelationMatrix() const {
        vector<string> names;

        for (const auto& observation : dataset.getObservations()) {
            names.push_back(observation.variable);
        }

        Matrix matrix(names);

        for (size_t i = 0; i < dataset.size(); ++i) {
            for (size_t j = i; j < dataset.size(); ++j) {
                auto pairs = getPairs(i, j);

                if (
                    Statistics::variance(pairs.first) == 0.0 ||
                    Statistics::variance(pairs.second) == 0.0
                ) {
                    throw StatisticalException(
                        "Correlation matrix contains a constant variable."
                    );
                }

                double value = Statistics::pearson(
                    pairs.first,
                    pairs.second
                );

                matrix.set(i, j, value);
                matrix.set(j, i, value);
            }
        }

        matrix.validateSymmetry();

        return matrix;
    }

    vector<PairResult> highCorrelationPairs(
        double threshold = 0.80
    ) const {
        if (threshold <= 0.0 || threshold > 1.0) {
            throw StatisticalException(
                "Threshold must be between zero and one."
            );
        }

        vector<PairResult> results;

        for (size_t i = 0; i < dataset.size(); ++i) {
            for (size_t j = i + 1; j < dataset.size(); ++j) {
                PairResult result = analyzePair(
                    dataset.get(i).variable,
                    dataset.get(j).variable
                );

                if (
                    result.correlationDefined &&
                    abs(result.correlation) >= threshold
                ) {
                    results.push_back(result);
                }
            }
        }

        return results;
    }

    void printReport() const {
        cout << "\nDATASET: " << dataset.getName() << "\n";

        cout << "\nVARIABLE STATISTICS\n";

        for (const auto& observation :
             dataset.getObservations()) {
            vector<double> valid;

            for (double value : observation.values) {
                if (!std::isnan(value)) {
                    valid.push_back(value);
                }
            }

            cout << "\n" << observation.variable
                 << "\nObservations: " << valid.size();

            if (valid.size() >= 2) {
                cout << "\nMean: "
                     << Statistics::mean(valid);

                cout << "\nSample variance: "
                     << Statistics::variance(valid);
            }

            cout << "\n";
        }

        buildCovarianceMatrix().print(
            "SAMPLE COVARIANCE MATRIX"
        );

        buildCorrelationMatrix().print(
            "PEARSON CORRELATION MATRIX"
        );

        cout << "\nHIGH CORRELATION PAIRS\n";

        for (const auto& result : highCorrelationPairs()) {
            cout << result.first << " <-> "
                 << result.second
                 << " | r = "
                 << result.correlation
                 << " | "
                 << Statistics::categoryName(
                     Statistics::classify(result.correlation)
                 )
                 << "\n";
        }
    }
};

void runTests() {
    vector<double> x = {1, 2, 3, 4};
    vector<double> y = {2, 4, 6, 8};
    vector<double> z = {8, 6, 4, 2};

    if (abs(Statistics::pearson(x, y) - 1.0) > 1e-10) {
        throw StatisticalException(
            "Positive correlation test failed."
        );
    }

    if (abs(Statistics::pearson(x, z) + 1.0) > 1e-10) {
        throw StatisticalException(
            "Negative correlation test failed."
        );
    }

    if (
        abs(
            Statistics::variance(x) -
            1.6666666666666667
        ) > 1e-10
    ) {
        throw StatisticalException(
            "Variance test failed."
        );
    }

    if (
        abs(
            Statistics::covariance(x, y) -
            3.3333333333333335
        ) > 1e-10
    ) {
        throw StatisticalException(
            "Covariance test failed."
        );
    }

    bool rejected = false;

    try {
        Statistics::pearson(
            {1, 1, 1},
            {2, 3, 4}
        );
    } catch (const StatisticalException&) {
        rejected = true;
    }

    if (!rejected) {
        throw StatisticalException(
            "Constant variable test failed."
        );
    }

    cout << "All C++17 tests passed.\n";
}

int main() {
    try {
        Dataset dataset(
            "Investment Portfolio Risk Analysis",
            {
                {"Equity_A", {10, 12, 14, 16, 18, 20}},
                {"Equity_B", {8, 10, 12, 14, 16, 18}},
                {"Bonds", {20, 19, 21, 18, 22, 17}},
                {"Gold", {15, 17, 14, 18, 13, 19}},
                {"Market_Index", {11, 13, 15, 17, 19, 21}}
            }
        );

        PortfolioAnalyzer analyzer(dataset);

        cout << "CORRELATION AND COVARIANCE ENGINE\n";
        cout << "=================================\n";

        analyzer.printReport();

        cout << "\nPAIRWISE ANALYSIS\n";

        PairResult result = analyzer.analyzePair(
            "Equity_A",
            "Bonds"
        );

        cout << "Covariance: "
             << result.covariance << "\n";

        cout << "Correlation: "
             << result.correlation << "\n";

        cout << "Observations: "
             << result.observations << "\n";

        Dataset missingDataset(
            "Missing Data Example",
            {
                {"A", {1, 2, NAN, 4, 5}},
                {"B", {2, 4, 6, NAN, 10}}
            }
        );

        PortfolioAnalyzer pairwiseAnalyzer(
            missingDataset,
            MissingPolicy::PAIRWISE
        );

        PairResult missingResult =
            pairwiseAnalyzer.analyzePair("A", "B");

        cout << "\nPAIRWISE MISSING-DATA ANALYSIS\n";
        cout << "Valid pairs: "
             << missingResult.observations << "\n";

        runTests();

        cout << "\nAnalysis completed successfully.\n";

        return 0;

    } catch (const exception& error) {
        cerr << "Analysis error: "
             << error.what() << "\n";

        return 1;
    }
}
