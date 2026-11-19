#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>
#include <limits>

using namespace std;

/*
 * Statistical Estimation Engine
 *
 * C++17 implementation of:
 * - Point estimation
 * - Interval estimation
 * - Maximum likelihood estimation
 * - Sampling-based estimator evaluation
 * - Bias, variance, and MSE
 * - Wilson confidence intervals
 * - Bootstrap confidence intervals
 */

enum class EstimatorType {
    ArithmeticMean,
    UnbiasedVariance,
    MaximumLikelihoodVariance,
    SampleProportion
};

enum class IntervalType {
    Normal,
    StudentT,
    Wilson,
    Bootstrap
};

struct Estimate {
    string parameter;
    double value;
    size_t sampleSize;
    string method;
};

struct ConfidenceInterval {
    string parameter;
    double lower;
    double upper;
    double confidence;
    string method;

    double width() const {
        return upper - lower;
    }

    bool contains(double value) const {
        return value >= lower && value <= upper;
    }
};

struct EstimatorMetrics {
    string name;
    double trueValue;
    double average;
    double bias;
    double variance;
    double mse;
};

class StatisticalEstimation {
private:
    static vector<double> validate(
        const vector<double>& data
    ) {
        if (data.empty()) {
            throw invalid_argument("Sample cannot be empty.");
        }

        for (double value : data) {
            if (!isfinite(value)) {
                throw invalid_argument(
                    "Sample contains a non-finite value."
                );
            }
        }

        return data;
    }

    static void validateConfidence(double confidence) {
        if (!(confidence > 0 && confidence < 1)) {
            throw invalid_argument(
                "Confidence must be between zero and one."
            );
        }
    }

    static double betaFraction(
        double a,
        double b,
        double x
    ) {
        constexpr double tiny = 1e-300;
        constexpr double epsilon = 3e-14;

        double qab = a + b;
        double qap = a + 1;
        double qam = a - 1;

        double c = 1;
        double d = 1 - qab * x / qap;

        if (abs(d) < tiny) d = tiny;

        d = 1 / d;

        double h = d;

        for (int m = 1; m <= 300; ++m) {
            int m2 = 2 * m;

            double aa = m * (b - m) * x /
                ((qam + m2) * (a + m2));

            d = 1 + aa * d;
            if (abs(d) < tiny) d = tiny;

            c = 1 + aa / c;
            if (abs(c) < tiny) c = tiny;

            d = 1 / d;
            h *= d * c;

            aa = -(a + m) * (qab + m) * x /
                ((a + m2) * (qap + m2));

            d = 1 + aa * d;
            if (abs(d) < tiny) d = tiny;

            c = 1 + aa / c;
            if (abs(c) < tiny) c = tiny;

            d = 1 / d;

            double delta = d * c;
            h *= delta;

            if (abs(delta - 1) < epsilon) {
                return h;
            }
        }

        throw runtime_error("Incomplete beta failed to converge.");
    }

    static double regularizedBeta(
        double x,
        double a,
        double b
    ) {
        if (x <= 0) return 0;
        if (x >= 1) return 1;

        double logBT =
            lgamma(a + b)
            - lgamma(a)
            - lgamma(b)
            + a * log(x)
            + b * log1p(-x);

        double bt = exp(logBT);

        if (x < (a + 1) / (a + b + 2)) {
            return bt * betaFraction(a, b, x) / a;
        }

        return 1 - bt * betaFraction(b, a, 1 - x) / b;
    }

    static double studentTCDF(
        double t,
        int degrees
    ) {
        double x = degrees / (
            degrees + t * t
        );

        double beta = regularizedBeta(
            x,
            degrees / 2.0,
            0.5
        );

        return t >= 0 ? 1 - beta / 2 : beta / 2;
    }

public:
    static double mean(const vector<double>& data) {
        auto values = validate(data);

        return accumulate(
            values.begin(),
            values.end(),
            0.0
        ) / values.size();
    }

    static double variance(
        const vector<double>& data,
        bool unbiased = true
    ) {
        auto values = validate(data);

        if (unbiased && values.size() < 2) {
            throw invalid_argument(
                "At least two observations are required."
            );
        }

        double average = mean(values);

        double sumSquares = 0;

        for (double value : values) {
            sumSquares += pow(value - average, 2);
        }

        return sumSquares / (
            unbiased ? values.size() - 1 : values.size()
        );
    }

    static double proportion(const vector<int>& data) {
        if (data.empty()) {
            throw invalid_argument("Binary sample cannot be empty.");
        }

        for (int value : data) {
            if (value != 0 && value != 1) {
                throw invalid_argument(
                    "Proportion requires binary observations."
                );
            }
        }

        double successes = accumulate(
            data.begin(),
            data.end(),
            0
        );

        return successes / data.size();
    }

    static double normalQuantile(double p) {
        if (!(p > 0 && p < 1)) {
            throw invalid_argument("Invalid probability.");
        }

        const double a[] = {
            -39.69683028665376,
            220.9460984245205,
            -275.9285104469687,
            138.3577518672690,
            -30.66479806614716,
            2.506628277459239
        };

        const double b[] = {
            -54.47609879822406,
            161.5858368580409,
            -155.6989798598866,
            66.80131188771972,
            -13.28068155288572
        };

        const double c[] = {
            -0.007784894002430293,
            -0.3223964580411365,
            -2.400758277161838,
            -2.549732539343734,
            4.374664141464968,
            2.938163982698783
        };

        const double d[] = {
            0.007784695709041462,
            0.3224671290700398,
            2.445134137142996,
            3.754408661907416
        };

        double low = 0.02425;
        double high = 1 - low;

        if (p < low || p > high) {
            double q = sqrt(
                -2 * log(p < low ? p : 1 - p)
            );

            double numerator = 0;
            double denominator = 1;

            for (int i = 0; i < 6; ++i) {
                numerator += c[i] * pow(q, 5 - i);
            }

            for (int i = 0; i < 4; ++i) {
                denominator += d[i] * pow(q, 3 - i);
            }

            double result = numerator / denominator;

            return p < low ? result : -result;
        }

        double q = p - 0.5;
        double r = q * q;

        double numerator = 0;
        double denominator = 1;

        for (int i = 0; i < 6; ++i) {
            numerator += a[i] * q * pow(r, 2 - i);
        }

        for (int i = 0; i < 5; ++i) {
            denominator += b[i] * pow(r, 2 - i);
        }

        return numerator / denominator;
    }

    static double studentTQuantile(
        double p,
        int degrees
    ) {
        if (degrees < 1 || !(p > 0 && p < 1)) {
            throw invalid_argument("Invalid Student t parameters.");
        }

        if (p == 0.5) return 0;

        if (p < 0.5) {
            return -studentTQuantile(1 - p, degrees);
        }

        double lower = 0;
        double upper = 1;

        while (studentTCDF(upper, degrees) < p) {
            upper *= 2;

            if (upper > 1e12) {
                throw runtime_error("Cannot bracket t quantile.");
            }
        }

        for (int i = 0; i < 150; ++i) {
            double middle = (lower + upper) / 2;

            if (studentTCDF(middle, degrees) < p) {
                lower = middle;
            } else {
                upper = middle;
            }
        }

        return (lower + upper) / 2;
    }

    static Estimate estimateMean(
        const vector<double>& data
    ) {
        auto values = validate(data);

        return {
            "population_mean",
            mean(values),
            values.size(),
            "arithmetic_mean"
        };
    }

    static Estimate estimateVariance(
        const vector<double>& data,
        bool unbiased = true
    ) {
        auto values = validate(data);

        return {
            "population_variance",
            variance(values, unbiased),
            values.size(),
            unbiased ? "sample_variance" : "maximum_likelihood"
        };
    }

    static Estimate estimateExponentialRate(
        const vector<double>& data
    ) {
        auto values = validate(data);

        for (double value : values) {
            if (value < 0) {
                throw invalid_argument(
                    "Exponential observations cannot be negative."
                );
            }
        }

        double average = mean(values);

        if (average <= 0) {
            throw invalid_argument(
                "Exponential MLE is undefined for zero mean."
            );
        }

        return {
            "exponential_rate",
            1 / average,
            values.size(),
            "maximum_likelihood"
        };
    }

    static ConfidenceInterval meanInterval(
        const vector<double>& data,
        double confidence = 0.95,
        bool useStudentT = true
    ) {
        auto values = validate(data);
        validateConfidence(confidence);

        if (values.size() < 2) {
            throw invalid_argument(
                "At least two observations are required."
            );
        }

        double estimate = mean(values);

        double standardError = sqrt(
            variance(values) / values.size()
        );

        double critical = useStudentT
            ? studentTQuantile(
                (1 + confidence) / 2,
                static_cast<int>(values.size() - 1)
            )
            : normalQuantile((1 + confidence) / 2);

        double margin = critical * standardError;

        return {
            "population_mean",
            estimate - margin,
            estimate + margin,
            confidence,
            useStudentT ? "student_t" : "normal"
        };
    }

    static ConfidenceInterval wilsonInterval(
        const vector<int>& data,
        double confidence = 0.95
    ) {
        validateConfidence(confidence);

        double p = proportion(data);
        double n = data.size();

        double z = normalQuantile((1 + confidence) / 2);
        double z2 = z * z;

        double denominator = 1 + z2 / n;

        double center = (
            p + z2 / (2 * n)
        ) / denominator;

        double margin = z * sqrt(
            p * (1 - p) / n
            + z2 / (4 * n * n)
        ) / denominator;

        return {
            "population_proportion",
            max(0.0, center - margin),
            min(1.0, center + margin),
            confidence,
            "wilson"
        };
    }

    static ConfidenceInterval bootstrapInterval(
        const vector<double>& data,
        double confidence = 0.95,
        int repetitions = 5000,
        unsigned int seed = 42
    ) {
        auto values = validate(data);
        validateConfidence(confidence);

        if (repetitions < 100) {
            throw invalid_argument(
                "At least 100 bootstrap repetitions are required."
            );
        }

        mt19937 generator(seed);

        uniform_int_distribution<size_t> distribution(
            0,
            values.size() - 1
        );

        vector<double> estimates;
        estimates.reserve(repetitions);

        vector<double> sample(values.size());

        for (int i = 0; i < repetitions; ++i) {
            for (double& value : sample) {
                value = values[distribution(generator)];
            }

            estimates.push_back(mean(sample));
        }

        sort(estimates.begin(), estimates.end());

        double alpha = 1 - confidence;

        size_t lowerIndex = static_cast<size_t>(
            floor(alpha / 2 * repetitions)
        );

        size_t upperIndex = min(
            static_cast<size_t>(repetitions - 1),
            static_cast<size_t>(
                floor((1 - alpha / 2) * repetitions)
            )
        );

        return {
            "population_mean",
            estimates[lowerIndex],
            estimates[upperIndex],
            confidence,
            "bootstrap_percentile"
        };
    }

    static EstimatorMetrics evaluateMean(
        double trueValue,
        int repetitions = 2000,
        int sampleSize = 30,
        unsigned int seed = 42
    ) {
        if (
            !isfinite(trueValue) ||
            repetitions < 2 ||
            sampleSize < 1
        ) {
            throw invalid_argument(
                "Invalid estimator evaluation parameters."
            );
        }

        mt19937 generator(seed);
        normal_distribution<double> distribution(trueValue, 2.0);

        vector<double> estimates;
        estimates.reserve(repetitions);

        vector<double> sample(sampleSize);

        for (int i = 0; i < repetitions; ++i) {
            for (double& value : sample) {
                value = distribution(generator);
            }

            estimates.push_back(mean(sample));
        }

        double average = mean(estimates);

        double bias = average - trueValue;

        double estimatorVariance = variance(estimates, false);

        double mse = 0;

        for (double estimate : estimates) {
            mse += pow(estimate - trueValue, 2);
        }

        mse /= repetitions;

        return {
            "sample_mean",
            trueValue,
            average,
            bias,
            estimatorVariance,
            mse
        };
    }
};

void printEstimate(const Estimate& result) {
    cout << result.parameter
         << " = " << result.value
         << " | n = " << result.sampleSize
         << " | method = " << result.method
         << '\n';
}

void printInterval(const ConfidenceInterval& interval) {
    cout << interval.parameter
         << " [" << interval.lower
         << ", " << interval.upper << "]"
         << " | confidence = " << interval.confidence
         << " | method = " << interval.method
         << " | width = " << interval.width()
         << '\n';
}

void runTests() {
    vector<double> sample = {10, 12, 13, 15, 16};

    if (abs(StatisticalEstimation::mean(sample) - 13.2) > 1e-9) {
        throw runtime_error("Mean test failed.");
    }

    if (
        abs(StatisticalEstimation::variance(sample) - 5.7)
        > 1e-9
    ) {
        throw runtime_error("Variance test failed.");
    }

    vector<int> binary = {1, 0, 1, 1};

    if (
        abs(StatisticalEstimation::proportion(binary) - 0.75)
        > 1e-9
    ) {
        throw runtime_error("Proportion test failed.");
    }

    auto interval = StatisticalEstimation::meanInterval(sample);

    if (!interval.contains(13.2)) {
        throw runtime_error("Confidence interval test failed.");
    }

    bool rejected = false;

    try {
        StatisticalEstimation::variance({5});
    } catch (const invalid_argument&) {
        rejected = true;
    }

    if (!rejected) {
        throw runtime_error("Single-value variance test failed.");
    }

    cout << "All C++ tests passed.\n";
}

int main() {
    try {
        cout << fixed << setprecision(6);

        vector<double> observations = {
            48.2, 51.1, 49.5, 52.3, 47.8,
            50.6, 53.0, 49.9, 51.7, 48.9,
            52.1, 50.3
        };

        cout << "\nSTATISTICAL ESTIMATION ENGINE\n";
        cout << "====================================\n";

        cout << "\nPOINT ESTIMATION\n";

        printEstimate(
            StatisticalEstimation::estimateMean(observations)
        );

        printEstimate(
            StatisticalEstimation::estimateVariance(observations)
        );

        printEstimate(
            StatisticalEstimation::estimateVariance(
                observations,
                false
            )
        );

        cout << "\nINTERVAL ESTIMATION\n";

        printInterval(
            StatisticalEstimation::meanInterval(
                observations,
                0.95,
                true
            )
        );

        printInterval(
            StatisticalEstimation::meanInterval(
                observations,
                0.95,
                false
            )
        );

        printInterval(
            StatisticalEstimation::bootstrapInterval(
                observations,
                0.95,
                5000
            )
        );

        cout << "\nPROPORTION ESTIMATION\n";

        vector<int> outcomes = {
            1, 1, 0, 1, 0, 1, 1, 0, 1, 1,
            0, 1, 0, 1, 1, 1, 0, 1, 0, 1
        };

        cout << "Estimated proportion = "
             << StatisticalEstimation::proportion(outcomes)
             << '\n';

        printInterval(
            StatisticalEstimation::wilsonInterval(outcomes)
        );

        cout << "\nMAXIMUM LIKELIHOOD ESTIMATION\n";

        printEstimate(
            StatisticalEstimation::estimateExponentialRate(
                {1.2, 0.8, 2.1, 1.5, 0.9, 1.7}
            )
        );

        cout << "\nESTIMATOR QUALITY\n";

        auto metrics = StatisticalEstimation::evaluateMean(
            50.0,
            2000,
            30
        );

        cout << "True value: " << metrics.trueValue << '\n';
        cout << "Average estimate: " << metrics.average << '\n';
        cout << "Bias: " << metrics.bias << '\n';
        cout << "Variance: " << metrics.variance << '\n';
        cout << "MSE: " << metrics.mse << '\n';

        runTests();

    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
