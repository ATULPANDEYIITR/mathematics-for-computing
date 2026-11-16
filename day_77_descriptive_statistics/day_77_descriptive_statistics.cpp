#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

enum class VarianceType {
    Population,
    Sample
};

struct Observation {
    string category;
    double value;
};

struct StatisticalSummary {
    size_t count = 0;
    double mean = 0.0;
    double median = 0.0;
    double variance = 0.0;
    double standardDeviation = 0.0;
    double minimum = 0.0;
    double maximum = 0.0;
    double q1 = 0.0;
    double q3 = 0.0;
    double iqr = 0.0;
};

class DescriptiveStatistics {
private:
    vector<double> values;
    vector<double> sortedValues;
    map<double, size_t> frequencies;

    void validate(double value) const {
        if (!isfinite(value)) {
            throw invalid_argument(
                "Observation must be a finite number."
            );
        }
    }

    double quantileFromSorted(double probability) const {
        if (probability < 0.0 || probability > 1.0) {
            throw invalid_argument(
                "Quantile probability must be between 0 and 1."
            );
        }

        const double position =
            (sortedValues.size() - 1) * probability;

        const size_t lower =
            static_cast<size_t>(floor(position));

        const size_t upper =
            static_cast<size_t>(ceil(position));

        if (lower == upper) {
            return sortedValues[lower];
        }

        const double fraction = position - lower;

        return sortedValues[lower] * (1.0 - fraction)
             + sortedValues[upper] * fraction;
    }

public:
    explicit DescriptiveStatistics(
        const vector<double>& observations
    ) {
        if (observations.empty()) {
            throw invalid_argument(
                "Dataset cannot be empty."
            );
        }

        if (observations.size() > 1000000) {
            throw invalid_argument(
                "Dataset exceeds maximum observation count."
            );
        }

        for (double value : observations) {
            validate(value);
            values.push_back(value);
            frequencies[value]++;
        }

        sortedValues = values;

        sort(
            sortedValues.begin(),
            sortedValues.end()
        );
    }

    size_t count() const {
        return values.size();
    }

    double mean() const {
        // Long double reduces intermediate summation error.
        long double sum = accumulate(
            values.begin(),
            values.end(),
            0.0L
        );

        return static_cast<double>(
            sum / values.size()
        );
    }

    double median() const {
        const size_t n = sortedValues.size();
        const size_t middle = n / 2;

        if (n % 2 == 1) {
            return sortedValues[middle];
        }

        return (
            sortedValues[middle - 1] +
            sortedValues[middle]
        ) / 2.0;
    }

    vector<double> mode() const {
        size_t maximumFrequency = 0;

        for (const auto& entry : frequencies) {
            maximumFrequency = max(
                maximumFrequency,
                entry.second
            );
        }

        if (maximumFrequency <= 1) {
            return {};
        }

        vector<double> result;

        for (const auto& entry : frequencies) {
            if (entry.second == maximumFrequency) {
                result.push_back(entry.first);
            }
        }

        return result;
    }

    double variance(VarianceType type) const {
        const size_t n = values.size();

        if (type == VarianceType::Sample && n < 2) {
            throw domain_error(
                "Sample variance requires at least two observations."
            );
        }

        const long double average = mean();

        long double squaredDifferences = 0.0L;

        for (double value : values) {
            const long double difference =
                static_cast<long double>(value) - average;

            squaredDifferences += difference * difference;
        }

        const size_t denominator =
            type == VarianceType::Sample ? n - 1 : n;

        return static_cast<double>(
            squaredDifferences / denominator
        );
    }

    double standardDeviation(VarianceType type) const {
        return sqrt(variance(type));
    }

    double quantile(double probability) const {
        return quantileFromSorted(probability);
    }

    double percentile(double percentage) const {
        if (percentage < 0.0 || percentage > 100.0) {
            throw invalid_argument(
                "Percentile must be between 0 and 100."
            );
        }

        return quantile(percentage / 100.0);
    }

    double interquartileRange() const {
        return quantile(0.75) - quantile(0.25);
    }

    vector<double> outliers(double multiplier = 1.5) const {
        if (!isfinite(multiplier) || multiplier < 0.0) {
            throw invalid_argument(
                "Invalid outlier multiplier."
            );
        }

        const double q1 = quantile(0.25);
        const double q3 = quantile(0.75);
        const double spread = q3 - q1;

        const double lower = q1 - multiplier * spread;
        const double upper = q3 + multiplier * spread;

        vector<double> result;

        for (double value : values) {
            if (value < lower || value > upper) {
                result.push_back(value);
            }
        }

        return result;
    }

    StatisticalSummary summary(
        VarianceType type = VarianceType::Population
    ) const {
        StatisticalSummary result;

        result.count = count();
        result.mean = mean();
        result.median = median();
        result.variance = variance(type);
        result.standardDeviation = sqrt(result.variance);
        result.minimum = sortedValues.front();
        result.maximum = sortedValues.back();
        result.q1 = quantile(0.25);
        result.q3 = quantile(0.75);
        result.iqr = result.q3 - result.q1;

        return result;
    }

    void printReport() const {
        const auto result = summary();

        cout << fixed << setprecision(4);

        cout << "\nDESCRIPTIVE STATISTICS REPORT\n";
        cout << "-----------------------------\n";

        cout << "Observations: " << result.count << '\n';
        cout << "Mean: " << result.mean << '\n';
        cout << "Median: " << result.median << '\n';

        cout << "Mode: ";

        const auto modes = mode();

        if (modes.empty()) {
            cout << "No unique mode";
        } else {
            for (double value : modes) {
                cout << value << " ";
            }
        }

        cout << '\n';

        cout << "Population variance: "
             << variance(VarianceType::Population) << '\n';

        if (count() >= 2) {
            cout << "Sample variance: "
                 << variance(VarianceType::Sample) << '\n';
        }

        cout << "Population standard deviation: "
             << standardDeviation(
                    VarianceType::Population
                ) << '\n';

        cout << "Minimum: " << result.minimum << '\n';
        cout << "Maximum: " << result.maximum << '\n';

        cout << "Q1: " << result.q1 << '\n';
        cout << "Q2: " << result.median << '\n';
        cout << "Q3: " << result.q3 << '\n';

        cout << "IQR: " << result.iqr << '\n';

        cout << "P90: " << percentile(90) << '\n';
        cout << "P95: " << percentile(95) << '\n';

        cout << "Outliers: ";

        const auto detected = outliers();

        if (detected.empty()) {
            cout << "None";
        } else {
            for (double value : detected) {
                cout << value << " ";
            }
        }

        cout << "\n\nFrequency Distribution\n";

        for (const auto& entry : frequencies) {
            cout << entry.first
                 << " -> "
                 << entry.second
                 << '\n';
        }
    }
};

int main() {
    try {
        // Operational measurements from a production system.
        vector<double> measurements = {
            12, 15, 18, 20, 15, 22, 25, 18,
            30, 35, 18, 40, 45, 50, 55, 60,
            18, 15, 22, 25
        };

        DescriptiveStatistics analysis(measurements);

        analysis.printReport();

        cout << "\nSAMPLE STATISTICS\n";

        cout << "Sample standard deviation: "
             << analysis.standardDeviation(
                    VarianceType::Sample
                ) << '\n';

        cout << "25th percentile: "
             << analysis.percentile(25) << '\n';

        cout << "95th percentile: "
             << analysis.percentile(95) << '\n';

        // Edge case: identical observations.
        DescriptiveStatistics identical({5, 5, 5, 5});

        cout << "\nIDENTICAL OBSERVATIONS\n";
        cout << "Mean: " << identical.mean() << '\n';
        cout << "Variance: "
             << identical.variance(
                    VarianceType::Population
                ) << '\n';

        // Edge case: insufficient sample size.
        DescriptiveStatistics single({10});

        try {
            single.variance(VarianceType::Sample);
        } catch (const domain_error& error) {
            cout << "Expected validation: "
                 << error.what() << '\n';
        }

        // Edge case: invalid numerical input.
        try {
            DescriptiveStatistics invalid({
                1.0,
                numeric_limits<double>::quiet_NaN()
            });
        } catch (const invalid_argument& error) {
            cout << "Expected validation: "
                 << error.what() << '\n';
        }

    } catch (const exception& error) {
        cerr << "Analysis failed: "
             << error.what() << '\n';

        return 1;
    }

    return 0;
}
