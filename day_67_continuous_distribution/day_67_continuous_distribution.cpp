#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

namespace statistics_engine {

constexpr double PI = 3.14159265358979323846;
constexpr double SQRT_TWO = 1.41421356237309504880;

class DistributionError : public runtime_error {
public:
    explicit DistributionError(const string& message)
        : runtime_error(message) {}
};

void validateFinite(double value, const string& name) {
    if (!isfinite(value)) {
        throw DistributionError(name + " must be finite.");
    }
}

void validateProbability(double p) {
    validateFinite(p, "Probability");

    if (p < 0.0 || p > 1.0) {
        throw DistributionError("Probability must be in [0, 1].");
    }
}

void validateSampleSize(size_t n) {
    if (n == 0) {
        throw DistributionError("Sample size must be positive.");
    }
}

double standardNormalCDF(double z) {
    return 0.5 * erfc(-z / SQRT_TWO);
}

/*
 * Acklam approximation for inverse standard normal CDF.
 */
double standardNormalQuantile(double p) {
    validateProbability(p);

    if (p == 0.0) {
        return -numeric_limits<double>::infinity();
    }

    if (p == 1.0) {
        return numeric_limits<double>::infinity();
    }

    static constexpr array<double, 6> a = {
        -39.69683028665376,
        220.9460984245205,
        -275.9285104469687,
        138.3577518672690,
        -30.66479806614716,
        2.506628277459239
    };

    static constexpr array<double, 5> b = {
        -54.47609879822406,
        161.5858368580409,
        -155.6989798598866,
        66.80131188771972,
        -13.28068155288572
    };

    static constexpr array<double, 6> c = {
        -0.007784894002430293,
        -0.3223964580411365,
        -2.400758277161838,
        -2.549732539343734,
        4.374664141464968,
        2.938163982698783
    };

    static constexpr array<double, 4> d = {
        0.007784695709041462,
        0.3224671290700398,
        2.445134137142996,
        3.754408661907416
    };

    constexpr double low = 0.02425;
    constexpr double high = 1.0 - low;

    double x;

    if (p < low) {
        double q = sqrt(-2.0 * log(p));

        x = (((((c[0] * q + c[1]) * q + c[2]) * q +
            c[3]) * q + c[4]) * q + c[5]) /
            ((((d[0] * q + d[1]) * q + d[2]) * q +
                d[3]) * q + 1.0);

    } else if (p > high) {
        double q = sqrt(-2.0 * log1p(-p));

        x = -(((((c[0] * q + c[1]) * q + c[2]) * q +
            c[3]) * q + c[4]) * q + c[5]) /
            ((((d[0] * q + d[1]) * q + d[2]) * q +
                d[3]) * q + 1.0);

    } else {
        double q = p - 0.5;
        double r = q * q;

        x = (((((a[0] * r + a[1]) * r + a[2]) * r +
            a[3]) * r + a[4]) * r + a[5]) * q /
            (((((b[0] * r + b[1]) * r + b[2]) * r +
                b[3]) * r + b[4]) * r + 1.0);
    }

    // Newton refinement in the central range.
    if (p > 1e-12 && p < 1.0 - 1e-12) {
        double error = standardNormalCDF(x) - p;
        double density = exp(-0.5 * x * x) / sqrt(2.0 * PI);

        if (density > 1e-300) {
            x -= error / density;
        }
    }

    return x;
}

class RandomSource {
private:
    mt19937_64 engine;

public:
    explicit RandomSource(uint64_t seed = 42)
        : engine(seed) {}

    double uniform(double lower, double upper) {
        return uniform_real_distribution<double>(
            lower, upper
        )(engine);
    }

    double exponential(double rate) {
        return exponential_distribution<double>(
            rate
        )(engine);
    }

    double normal(double mean, double standardDeviation) {
        return normal_distribution<double>(
            mean, standardDeviation
        )(engine);
    }
};

class ContinuousDistribution {
public:
    virtual ~ContinuousDistribution() = default;

    virtual double pdf(double x) const = 0;
    virtual double cdf(double x) const = 0;
    virtual double quantile(double p) const = 0;

    virtual double sample(RandomSource& rng) const = 0;

    double probabilityBetween(
        double lower,
        double upper
    ) const {
        validateFinite(lower, "Lower bound");
        validateFinite(upper, "Upper bound");

        if (lower > upper) {
            throw DistributionError(
                "Lower bound cannot exceed upper bound."
            );
        }

        return cdf(upper) - cdf(lower);
    }

    virtual double theoreticalMean() const = 0;
    virtual double theoreticalVariance() const = 0;
};

class UniformDistribution final : public ContinuousDistribution {
private:
    double a;
    double b;

public:
    UniformDistribution(double lower, double upper)
        : a(lower), b(upper) {

        validateFinite(a, "a");
        validateFinite(b, "b");

        if (a >= b) {
            throw DistributionError("Require a < b.");
        }
    }

    double pdf(double x) const override {
        validateFinite(x, "x");

        return x >= a && x <= b
            ? 1.0 / (b - a)
            : 0.0;
    }

    double cdf(double x) const override {
        validateFinite(x, "x");

        if (x < a) return 0.0;
        if (x >= b) return 1.0;

        return (x - a) / (b - a);
    }

    double quantile(double p) const override {
        validateProbability(p);
        return a + p * (b - a);
    }

    double sample(RandomSource& rng) const override {
        return rng.uniform(a, b);
    }

    double theoreticalMean() const override {
        return (a + b) / 2.0;
    }

    double theoreticalVariance() const override {
        return (b - a) * (b - a) / 12.0;
    }
};

class ExponentialDistribution final : public ContinuousDistribution {
private:
    double rate;

public:
    explicit ExponentialDistribution(double lambda)
        : rate(lambda) {

        validateFinite(rate, "Rate");

        if (rate <= 0.0) {
            throw DistributionError("Rate must be positive.");
        }
    }

    double pdf(double x) const override {
        validateFinite(x, "x");

        if (x < 0.0) return 0.0;

        return rate * exp(-rate * x);
    }

    double cdf(double x) const override {
        validateFinite(x, "x");

        if (x <= 0.0) return 0.0;

        return -expm1(-rate * x);
    }

    double survival(double x) const {
        validateFinite(x, "x");

        return x <= 0.0
            ? 1.0
            : exp(-rate * x);
    }

    double quantile(double p) const override {
        validateProbability(p);

        if (p == 1.0) {
            return numeric_limits<double>::infinity();
        }

        return -log1p(-p) / rate;
    }

    double sample(RandomSource& rng) const override {
        return rng.exponential(rate);
    }

    double theoreticalMean() const override {
        return 1.0 / rate;
    }

    double theoreticalVariance() const override {
        return 1.0 / (rate * rate);
    }

    double hazard() const {
        return rate;
    }
};

class NormalDistribution final : public ContinuousDistribution {
private:
    double mu;
    double sigma;

public:
    NormalDistribution(double mean, double standardDeviation)
        : mu(mean), sigma(standardDeviation) {

        validateFinite(mu, "Mean");
        validateFinite(sigma, "Standard deviation");

        if (sigma <= 0.0) {
            throw DistributionError(
                "Standard deviation must be positive."
            );
        }
    }

    double pdf(double x) const override {
        validateFinite(x, "x");

        double z = (x - mu) / sigma;

        return exp(-0.5 * z * z) /
            (sigma * sqrt(2.0 * PI));
    }

    double cdf(double x) const override {
        validateFinite(x, "x");

        return standardNormalCDF((x - mu) / sigma);
    }

    double quantile(double p) const override {
        return mu + sigma * standardNormalQuantile(p);
    }

    double sample(RandomSource& rng) const override {
        return rng.normal(mu, sigma);
    }

    double theoreticalMean() const override {
        return mu;
    }

    double theoreticalVariance() const override {
        return sigma * sigma;
    }

    double standardize(double x) const {
        validateFinite(x, "x");
        return (x - mu) / sigma;
    }
};

struct RunningStatistics {
    size_t count = 0;
    double mean = 0.0;
    double m2 = 0.0;
    double minimum = numeric_limits<double>::infinity();
    double maximum = -numeric_limits<double>::infinity();

    void add(double value) {
        validateFinite(value, "Observation");

        ++count;

        double delta = value - mean;
        mean += delta / static_cast<double>(count);

        double delta2 = value - mean;
        m2 += delta * delta2;

        minimum = min(minimum, value);
        maximum = max(maximum, value);
    }

    double variance() const {
        return count > 1
            ? m2 / static_cast<double>(count - 1)
            : 0.0;
    }

    double standardDeviation() const {
        return sqrt(variance());
    }
};

struct HistogramBin {
    double lower;
    double upper;
    size_t count;
};

vector<HistogramBin> createHistogram(
    const vector<double>& values,
    size_t bins
) {
    if (values.empty() || bins == 0) {
        throw DistributionError("Invalid histogram input.");
    }

    double minimum = *min_element(values.begin(), values.end());
    double maximum = *max_element(values.begin(), values.end());

    if (minimum == maximum) {
        return {{minimum, maximum, values.size()}};
    }

    double width = (maximum - minimum) / bins;

    vector<size_t> counts(bins, 0);

    for (double value : values) {
        validateFinite(value, "Observation");

        size_t index = min(
            static_cast<size_t>((value - minimum) / width),
            bins - 1
        );

        ++counts[index];
    }

    vector<HistogramBin> result;

    for (size_t i = 0; i < bins; ++i) {
        result.push_back({
            minimum + i * width,
            minimum + (i + 1) * width,
            counts[i]
        });
    }

    return result;
}

double empiricalProbability(
    const vector<double>& values,
    double lower,
    double upper
) {
    if (values.empty()) {
        throw DistributionError("Sample cannot be empty.");
    }

    if (lower > upper) {
        throw DistributionError("Invalid interval.");
    }

    size_t matches = count_if(
        values.begin(),
        values.end(),
        [lower, upper](double value) {
            return value >= lower && value <= upper;
        }
    );

    return static_cast<double>(matches) / values.size();
}

double empiricalKSDistance(
    const vector<double>& values,
    const ContinuousDistribution& distribution
) {
    if (values.empty()) {
        throw DistributionError("Sample cannot be empty.");
    }

    vector<double> sorted = values;

    for (double value : sorted) {
        validateFinite(value, "Observation");
    }

    sort(sorted.begin(), sorted.end());

    double distance = 0.0;
    double n = static_cast<double>(sorted.size());

    for (size_t i = 0; i < sorted.size(); ++i) {
        double theoretical = distribution.cdf(sorted[i]);

        double dPlus = (i + 1.0) / n - theoretical;
        double dMinus = theoretical - i / n;

        distance = max(distance, max(dPlus, dMinus));
    }

    return distance;
}

struct SimulationResult {
    RunningStatistics statistics;
    double theoreticalProbability;
    double empiricalProbability;
    double confidenceLower;
    double confidenceUpper;
    double ksDistance;
};

SimulationResult simulate(
    const ContinuousDistribution& distribution,
    size_t sampleSize,
    uint64_t seed,
    double lower,
    double upper
) {
    validateSampleSize(sampleSize);

    RandomSource rng(seed);

    vector<double> observations;
    observations.reserve(sampleSize);

    RunningStatistics stats;

    size_t inside = 0;

    for (size_t i = 0; i < sampleSize; ++i) {
        double value = distribution.sample(rng);

        stats.add(value);
        observations.push_back(value);

        if (value >= lower && value <= upper) {
            ++inside;
        }
    }

    if (sampleSize < 2) {
        throw DistributionError(
            "At least two samples are needed for a confidence interval."
        );
    }

    constexpr double z = 1.96;

    double margin = z * stats.standardDeviation() /
        sqrt(static_cast<double>(sampleSize));

    return {
        stats,
        distribution.probabilityBetween(lower, upper),
        static_cast<double>(inside) / sampleSize,
        stats.mean - margin,
        stats.mean + margin,
        empiricalKSDistance(observations, distribution)
    };
}

void displayResult(
    const string& name,
    const ContinuousDistribution& distribution,
    const SimulationResult& result
) {
    cout << "\n============================================\n";
    cout << name << "\n";
    cout << "============================================\n";

    cout << "Sample count:              "
         << result.statistics.count << "\n";

    cout << "Theoretical mean:          "
         << distribution.theoreticalMean() << "\n";

    cout << "Empirical mean:            "
         << result.statistics.mean << "\n";

    cout << "Theoretical variance:      "
         << distribution.theoreticalVariance() << "\n";

    cout << "Empirical variance:        "
         << result.statistics.variance() << "\n";

    cout << "Standard deviation:        "
         << result.statistics.standardDeviation() << "\n";

    cout << "Minimum:                   "
         << result.statistics.minimum << "\n";

    cout << "Maximum:                   "
         << result.statistics.maximum << "\n";

    cout << "Theoretical interval P:    "
         << result.theoreticalProbability << "\n";

    cout << "Empirical interval P:      "
         << result.empiricalProbability << "\n";

    cout << "95% mean confidence range: "
         << "[" << result.confidenceLower
         << ", " << result.confidenceUpper << "]\n";

    cout << "Empirical KS distance:     "
         << result.ksDistance << "\n";
}

void runTests() {
    UniformDistribution uniform(0.0, 10.0);
    ExponentialDistribution exponential(0.5);
    NormalDistribution normal(100.0, 15.0);

    auto close = [](double a, double b, double tolerance = 1e-6) {
        return abs(a - b) <= tolerance;
    };

    if (!close(uniform.pdf(5.0), 0.1)) {
        throw runtime_error("Uniform PDF test failed.");
    }

    if (!close(uniform.cdf(5.0), 0.5)) {
        throw runtime_error("Uniform CDF test failed.");
    }

    if (!close(uniform.quantile(0.5), 5.0)) {
        throw runtime_error("Uniform quantile test failed.");
    }

    if (!close(exponential.cdf(2.0), 1.0 - exp(-1.0))) {
        throw runtime_error("Exponential CDF test failed.");
    }

    if (!close(exponential.quantile(0.5), log(2.0) / 0.5)) {
        throw runtime_error("Exponential quantile test failed.");
    }

    if (!close(normal.cdf(100.0), 0.5)) {
        throw runtime_error("Normal CDF test failed.");
    }

    if (!close(normal.quantile(0.5), 100.0)) {
        throw runtime_error("Normal quantile test failed.");
    }

    if (!close(normal.standardize(115.0), 1.0)) {
        throw runtime_error("Normal standardization test failed.");
    }

    if (!close(
        standardNormalQuantile(0.975),
        1.9599639845,
        1e-7
    )) {
        throw runtime_error("Inverse normal CDF test failed.");
    }

    auto mustFail = [](auto operation) {
        bool rejected = false;

        try {
            operation();
        } catch (const DistributionError&) {
            rejected = true;
        }

        if (!rejected) {
            throw runtime_error("Invalid input was accepted.");
        }
    };

    mustFail([] { UniformDistribution invalid(5, 5); });
    mustFail([] { ExponentialDistribution invalid(0); });
    mustFail([] { NormalDistribution invalid(0, -1); });
    mustFail([] { validateProbability(1.5); });

    cout << "All C++ validation tests passed.\n";
}

} // namespace statistics_engine

int main() {
    using namespace statistics_engine;

    try {
        cout << fixed << setprecision(6);

        cout << "CONTINUOUS DISTRIBUTION SIMULATION ENGINE\n";
        cout << "Uniform, Exponential, Normal\n";

        runTests();

        constexpr size_t N = 100000;

        UniformDistribution uniform(0.0, 100.0);
        ExponentialDistribution exponential(0.2);
        NormalDistribution normal(50.0, 10.0);

        auto uniformResult = simulate(
            uniform, N, 42, 20.0, 80.0
        );

        auto exponentialResult = simulate(
            exponential, N, 42, 1.0, 5.0
        );

        auto normalResult = simulate(
            normal, N, 42, 40.0, 60.0
        );

        displayResult("UNIFORM DISTRIBUTION", uniform, uniformResult);
        displayResult(
            "EXPONENTIAL DISTRIBUTION",
            exponential,
            exponentialResult
        );

        displayResult("NORMAL DISTRIBUTION", normal, normalResult);

        cout << "\nQUANTILE COMPARISON\n";

        array<double, 5> probabilities = {
            0.05, 0.25, 0.50, 0.75, 0.95
        };

        cout << setw(12) << "Probability"
             << setw(18) << "Uniform"
             << setw(18) << "Exponential"
             << setw(18) << "Normal" << "\n";

        for (double p : probabilities) {
            cout << setw(12) << p
                 << setw(18) << uniform.quantile(p)
                 << setw(18) << exponential.quantile(p)
                 << setw(18) << normal.quantile(p)
                 << "\n";
        }

        cout << "\nEXPONENTIAL MEMORYLESS PROPERTY\n";

        double t = 3.0;
        double s = 5.0;

        double conditionalSurvival =
            exponential.survival(t + s) /
            exponential.survival(t);

        cout << "P(X > t+s | X > t): "
             << conditionalSurvival << "\n";

        cout << "P(X > s):             "
             << exponential.survival(s) << "\n";

        cout << "\nNORMAL STANDARDIZATION\n";
        cout << "Observation 70, mean 50, SD 10\n";
        cout << "Z-score: " << normal.standardize(70) << "\n";

        cout << "\nAll simulations completed.\n";

    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
