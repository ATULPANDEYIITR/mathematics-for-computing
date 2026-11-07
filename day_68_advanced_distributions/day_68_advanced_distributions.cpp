#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

constexpr double EPSILON = 1e-12;
constexpr int MAX_ITERATIONS = 10000;

class StatisticalError : public runtime_error {
public:
    explicit StatisticalError(const string& message)
        : runtime_error(message) {}
};

void validatePositive(double value, const string& name) {
    if (!isfinite(value) || value <= 0) {
        throw StatisticalError(name + " must be finite and positive.");
    }
}

void validateNonnegative(double value, const string& name) {
    if (!isfinite(value) || value < 0) {
        throw StatisticalError(name + " must be finite and nonnegative.");
    }
}

double regularizedGammaP(double a, double x) {
    validatePositive(a, "Shape");
    validateNonnegative(x, "x");

    if (x == 0) return 0;
    if (isinf(x)) return 1;

    const double factor = exp(a * log(x) - x - lgamma(a));

    if (x < a + 1) {
        double term = 1 / a;
        double sum = term;
        double ap = a;

        for (int i = 0; i < MAX_ITERATIONS; ++i) {
            ap++;
            term *= x / ap;
            sum += term;

            if (abs(term) <= abs(sum) * EPSILON) {
                return clamp(factor * sum, 0.0, 1.0);
            }
        }

        throw runtime_error("Gamma series failed to converge.");
    }

    double b = x + 1 - a;
    double c = 1e300;
    double d = 1 / b;
    double h = d;

    for (int i = 1; i <= MAX_ITERATIONS; ++i) {
        const double an = -i * (i - a);
        b += 2;

        d = an * d + b;
        if (abs(d) < 1e-300) d = 1e-300;

        c = b + an / c;
        if (abs(c) < 1e-300) c = 1e-300;

        d = 1 / d;

        const double delta = d * c;
        h *= delta;

        if (abs(delta - 1) <= EPSILON) {
            return clamp(1 - factor * h, 0.0, 1.0);
        }
    }

    throw runtime_error("Gamma continued fraction failed.");
}

double betaFraction(double a, double b, double x) {
    const double qab = a + b;
    const double qap = a + 1;
    const double qam = a - 1;

    double c = 1;
    double d = 1 - qab * x / qap;

    if (abs(d) < 1e-300) d = 1e-300;

    d = 1 / d;
    double h = d;

    for (int m = 1; m <= MAX_ITERATIONS; ++m) {
        const int m2 = 2 * m;

        double term = m * (b - m) * x
            / ((qam + m2) * (a + m2));

        d = 1 + term * d;
        if (abs(d) < 1e-300) d = 1e-300;

        c = 1 + term / c;
        if (abs(c) < 1e-300) c = 1e-300;

        d = 1 / d;
        h *= d * c;

        term = -(a + m) * (qab + m) * x
            / ((a + m2) * (qap + m2));

        d = 1 + term * d;
        if (abs(d) < 1e-300) d = 1e-300;

        c = 1 + term / c;
        if (abs(c) < 1e-300) c = 1e-300;

        d = 1 / d;

        const double delta = d * c;
        h *= delta;

        if (abs(delta - 1) <= EPSILON) return h;
    }

    throw runtime_error("Beta continued fraction failed.");
}

double regularizedBeta(double x, double a, double b) {
    validatePositive(a, "Alpha");
    validatePositive(b, "Beta");

    if (!isfinite(x) || x < 0 || x > 1) {
        throw StatisticalError("x must be between zero and one.");
    }

    if (x == 0) return 0;
    if (x == 1) return 1;

    const double factor = exp(
        lgamma(a + b) - lgamma(a) - lgamma(b)
        + a * log(x) + b * log1p(-x)
    );

    double result;

    if (x < (a + 1) / (a + b + 2)) {
        result = factor * betaFraction(a, b, x) / a;
    } else {
        result = 1 - factor * betaFraction(b, a, 1 - x) / b;
    }

    return clamp(result, 0.0, 1.0);
}

class RandomGenerator {
private:
    mt19937_64 engine;

public:
    explicit RandomGenerator(uint64_t seed = 42) : engine(seed) {}

    double uniform() {
        return generate_canonical<double, 53>(engine);
    }

    double normal() {
        static normal_distribution<double> distribution(0, 1);
        return distribution(engine);
    }

    double gamma(double shape, double scale = 1) {
        validatePositive(shape, "Gamma shape");
        validatePositive(scale, "Gamma scale");

        gamma_distribution<double> distribution(shape, scale);
        return distribution(engine);
    }

    double beta(double a, double b) {
        const double x = gamma(a);
        const double y = gamma(b);
        return x / (x + y);
    }

    long long poisson(double rate) {
        validatePositive(rate, "Poisson rate");

        poisson_distribution<long long> distribution(rate);
        return distribution(engine);
    }
};

struct Statistics {
    double mean;
    double variance;
};

class PoissonDistribution {
private:
    double lambda;

public:
    explicit PoissonDistribution(double rate) : lambda(rate) {
        validatePositive(lambda, "Lambda");
    }

    double pmf(int k) const {
        if (k < 0) return 0;

        return exp(
            k * log(lambda) - lambda - lgamma(k + 1.0)
        );
    }

    double cdf(int k) const {
        if (k < 0) return 0;

        return regularizedGammaP(k + 1.0, lambda);
    }

    Statistics moments() const {
        return {lambda, lambda};
    }

    long long sample(RandomGenerator& rng) const {
        return rng.poisson(lambda);
    }
};

class GammaDistribution {
private:
    double shape;
    double scale;

public:
    GammaDistribution(double a, double b) : shape(a), scale(b) {
        validatePositive(shape, "Shape");
        validatePositive(scale, "Scale");
    }

    double pdf(double x) const {
        if (x < 0) return 0;

        if (x == 0) {
            if (shape < 1) return numeric_limits<double>::infinity();
            if (shape == 1) return 1 / scale;
            return 0;
        }

        return exp(
            (shape - 1) * log(x)
            - x / scale
            - lgamma(shape)
            - shape * log(scale)
        );
    }

    double cdf(double x) const {
        if (x <= 0) return 0;
        return regularizedGammaP(shape, x / scale);
    }

    Statistics moments() const {
        return {shape * scale, shape * scale * scale};
    }

    double sample(RandomGenerator& rng) const {
        return rng.gamma(shape, scale);
    }
};

class BetaDistribution {
private:
    double alpha;
    double betaParameter;

public:
    BetaDistribution(double a, double b)
        : alpha(a), betaParameter(b) {
        validatePositive(alpha, "Alpha");
        validatePositive(betaParameter, "Beta");
    }

    double pdf(double x) const {
        if (x < 0 || x > 1) return 0;

        const double logNormalizer =
            lgamma(alpha + betaParameter)
            - lgamma(alpha)
            - lgamma(betaParameter);

        if (x == 0) {
            if (alpha < 1) return numeric_limits<double>::infinity();
            if (alpha > 1) return 0;
            return exp(logNormalizer);
        }

        if (x == 1) {
            if (betaParameter < 1) {
                return numeric_limits<double>::infinity();
            }
            if (betaParameter > 1) return 0;
            return exp(logNormalizer);
        }

        return exp(
            (alpha - 1) * log(x)
            + (betaParameter - 1) * log1p(-x)
            + logNormalizer
        );
    }

    double cdf(double x) const {
        return regularizedBeta(x, alpha, betaParameter);
    }

    Statistics moments() const {
        const double total = alpha + betaParameter;

        return {
            alpha / total,
            alpha * betaParameter
                / (total * total * (total + 1))
        };
    }

    double sample(RandomGenerator& rng) const {
        return rng.beta(alpha, betaParameter);
    }
};

class ChiSquareDistribution {
private:
    double degreesOfFreedom;

public:
    explicit ChiSquareDistribution(double df) : degreesOfFreedom(df) {
        validatePositive(degreesOfFreedom, "Degrees of freedom");
    }

    double pdf(double x) const {
        if (x < 0) return 0;

        if (x == 0) {
            if (degreesOfFreedom < 2) {
                return numeric_limits<double>::infinity();
            }
            if (degreesOfFreedom == 2) return 0.5;
            return 0;
        }

        const double df = degreesOfFreedom;

        return exp(
            (df / 2 - 1) * log(x)
            - x / 2
            - df / 2 * log(2)
            - lgamma(df / 2)
        );
    }

    double cdf(double x) const {
        return x <= 0
            ? 0
            : regularizedGammaP(degreesOfFreedom / 2, x / 2);
    }

    Statistics moments() const {
        return {degreesOfFreedom, 2 * degreesOfFreedom};
    }

    double sample(RandomGenerator& rng) const {
        return rng.gamma(degreesOfFreedom / 2, 2);
    }
};

struct GoodnessOfFitResult {
    double statistic;
    int degreesOfFreedom;
    double pValue;
    bool rejectNull;
};

GoodnessOfFitResult chiSquareGoodnessOfFit(
    const vector<int>& observed,
    const vector<double>& expected,
    double alpha = 0.05
) {
    if (observed.size() < 2 || observed.size() != expected.size()) {
        throw StatisticalError("Frequency arrays must have equal lengths.");
    }

    if (!isfinite(alpha) || alpha <= 0 || alpha >= 1) {
        throw StatisticalError("Alpha must be between zero and one.");
    }

    double observedTotal = 0;
    double expectedTotal = 0;
    double statistic = 0;

    for (size_t i = 0; i < observed.size(); ++i) {
        if (observed[i] < 0) {
            throw StatisticalError("Observed counts cannot be negative.");
        }

        if (!isfinite(expected[i]) || expected[i] < 5) {
            throw StatisticalError("Expected frequencies must be at least five.");
        }

        observedTotal += observed[i];
        expectedTotal += expected[i];

        const double difference = observed[i] - expected[i];

        statistic += difference * difference / expected[i];
    }

    if (abs(observedTotal - expectedTotal) > 1e-9 * max(1.0, observedTotal)) {
        throw StatisticalError("Observed and expected totals must match.");
    }

    const int df = static_cast<int>(observed.size()) - 1;

    const double pValue =
        1 - regularizedGammaP(df / 2.0, statistic / 2);

    return {
        statistic,
        df,
        max(0.0, pValue),
        pValue < alpha
    };
}

template <typename Distribution>
Statistics simulate(
    const Distribution& distribution,
    RandomGenerator& rng,
    int sampleSize = 10000
) {
    if (sampleSize <= 0) {
        throw StatisticalError("Sample size must be positive.");
    }

    vector<double> values;
    values.reserve(sampleSize);

    for (int i = 0; i < sampleSize; ++i) {
        values.push_back(distribution.sample(rng));
    }

    const double mean =
        accumulate(values.begin(), values.end(), 0.0) / sampleSize;

    double variance = 0;

    for (double value : values) {
        variance += (value - mean) * (value - mean);
    }

    variance /= sampleSize;

    const auto [minimum, maximum] =
        minmax_element(values.begin(), values.end());

    cout << "Empirical mean: " << mean << '\n';
    cout << "Empirical variance: " << variance << '\n';
    cout << "Minimum: " << *minimum << '\n';
    cout << "Maximum: " << *maximum << '\n';

    return {mean, variance};
}

template <typename Distribution>
void printReport(
    const string& name,
    const Distribution& distribution,
    const vector<double>& points
) {
    const Statistics stats = distribution.moments();

    cout << "\n" << name << "\n";
    cout << string(55, '-') << '\n';

    cout << "Mean: " << stats.mean << '\n';
    cout << "Variance: " << stats.variance << '\n';

    for (double x : points) {
        cout << "x = " << x
             << " | PDF/PMF = " << distribution.pdf(x)
             << " | CDF = " << distribution.cdf(
                    name == "Poisson" ? static_cast<int>(x) : x
                )
             << '\n';
    }
}

int main() {
    try {
        cout << fixed << setprecision(6);

        RandomGenerator rng(42);

        PoissonDistribution poisson(4.5);
        GammaDistribution gamma(3, 2);
        BetaDistribution beta(2, 5);
        ChiSquareDistribution chiSquare(4);

        cout << "ADVANCED DISTRIBUTIONS\n";

        // Discrete event-count modeling.
        cout << "\nPOISSON DISTRIBUTION\n";
        cout << "P(X = 3): " << poisson.pmf(3) << '\n';
        cout << "P(X <= 5): " << poisson.cdf(5) << '\n';

        // Continuous waiting-time modeling.
        cout << "\nGAMMA DISTRIBUTION\n";
        cout << "Density at 5: " << gamma.pdf(5) << '\n';
        cout << "P(X <= 5): " << gamma.cdf(5) << '\n';

        // Probability uncertainty modeling.
        cout << "\nBETA DISTRIBUTION\n";
        cout << "Density at 0.4: " << beta.pdf(0.4) << '\n';
        cout << "P(X <= 0.4): " << beta.cdf(0.4) << '\n';

        // Statistical goodness-of-fit modeling.
        cout << "\nCHI-SQUARE DISTRIBUTION\n";
        cout << "Density at 5: " << chiSquare.pdf(5) << '\n';
        cout << "P(X <= 5): " << chiSquare.cdf(5) << '\n';

        cout << "\nTHEORETICAL MOMENTS\n";

        const vector<pair<string, Statistics>> moments = {
            {"Poisson", poisson.moments()},
            {"Gamma", gamma.moments()},
            {"Beta", beta.moments()},
            {"Chi-square", chiSquare.moments()}
        };

        for (const auto& [name, value] : moments) {
            cout << name
                 << ": mean=" << value.mean
                 << ", variance=" << value.variance
                 << '\n';
        }

        cout << "\nBAYESIAN CONVERSION RATE\n";

        BetaDistribution prior(2, 2);

        const int successes = 45;
        const int failures = 55;

        BetaDistribution posterior(
            2 + successes,
            2 + failures
        );

        cout << "Prior mean: " << prior.moments().mean << '\n';
        cout << "Posterior mean: " << posterior.moments().mean << '\n';
        cout << "P(rate <= 0.5): " << posterior.cdf(0.5) << '\n';

        cout << "\nCHI-SQUARE GOODNESS-OF-FIT TEST\n";

        const auto result = chiSquareGoodnessOfFit(
            {48, 32, 15, 5},
            {50, 30, 15, 5},
            0.05
        );

        cout << "Statistic: " << result.statistic << '\n';
        cout << "Degrees of freedom: "
             << result.degreesOfFreedom << '\n';
        cout << "P-value: " << result.pValue << '\n';
        cout << "Reject null: "
             << boolalpha << result.rejectNull << '\n';

        cout << "\nMONTE CARLO SIMULATION\n";

        cout << "\nPoisson:\n";
        simulate(poisson, rng);

        cout << "\nGamma:\n";
        simulate(gamma, rng);

        cout << "\nBeta:\n";
        simulate(beta, rng);

        cout << "\nChi-square:\n";
        simulate(chiSquare, rng);

        cout << "\nVALIDATION TESTS\n";

        if (abs(poisson.pmf(0) - exp(-4.5)) > 1e-10) {
            throw runtime_error("Poisson validation failed.");
        }

        if (abs(beta.moments().mean - 2.0 / 7) > 1e-10) {
            throw runtime_error("Beta validation failed.");
        }

        if (abs(chiSquare.moments().variance - 8) > 1e-10) {
            throw runtime_error("Chi-square validation failed.");
        }

        if (abs(gamma.cdf(0)) > EPSILON) {
            throw runtime_error("Gamma boundary validation failed.");
        }

        cout << "All tests passed.\n";
    }
    catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
