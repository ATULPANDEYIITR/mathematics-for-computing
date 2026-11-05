#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

constexpr double EPSILON = 1e-12;

class ProbabilityError : public runtime_error {
public:
    explicit ProbabilityError(const string& message)
        : runtime_error(message) {}
};

void validateProbability(double p) {
    if (!isfinite(p) || p < 0.0 || p > 1.0) {
        throw ProbabilityError(
            "Probability must be between 0 and 1."
        );
    }
}

void validateNonNegative(int value, const string& name) {
    if (value < 0) {
        throw ProbabilityError(name + " cannot be negative.");
    }
}

struct Statistics {
    double mean;
    double variance;
    double standardDeviation;
};

struct SimulationResult {
    long long sampleCount = 0;
    double empiricalMean = 0.0;
    double empiricalVariance = 0.0;
    map<int, long long> frequencies;
};

class Distribution {
protected:
    double p;

public:
    explicit Distribution(double probability) : p(probability) {
        validateProbability(probability);
    }

    virtual ~Distribution() = default;

    virtual double pmf(int outcome) const = 0;
    virtual double cdf(int outcome) const = 0;
    virtual int sample(mt19937& generator) const = 0;
    virtual Statistics statistics() const = 0;

    double probabilityAtLeast(int threshold) const {
        if (threshold <= numeric_limits<int>::min() + 1) {
            return 1.0;
        }

        return max(0.0, 1.0 - cdf(threshold - 1));
    }

    SimulationResult simulate(
        int count,
        mt19937& generator
    ) const {
        if (count <= 0) {
            throw ProbabilityError(
                "Simulation count must be positive."
            );
        }

        SimulationResult result;
        long double sum = 0.0L;
        long double sumSquares = 0.0L;

        for (int i = 0; i < count; ++i) {
            int outcome = sample(generator);

            result.frequencies[outcome]++;
            sum += outcome;
            sumSquares += static_cast<long double>(outcome) * outcome;
        }

        result.sampleCount = count;
        result.empiricalMean = static_cast<double>(sum / count);

        long double variance =
            sumSquares / count -
            static_cast<long double>(result.empiricalMean) *
            result.empiricalMean;

        result.empiricalVariance =
            max(0.0, static_cast<double>(variance));

        return result;
    }
};

class BernoulliDistribution : public Distribution {
public:
    explicit BernoulliDistribution(double probability)
        : Distribution(probability) {}

    double pmf(int outcome) const override {
        if (outcome == 1) return p;
        if (outcome == 0) return 1.0 - p;
        return 0.0;
    }

    double cdf(int outcome) const override {
        if (outcome < 0) return 0.0;
        if (outcome == 0) return 1.0 - p;
        return 1.0;
    }

    int sample(mt19937& generator) const override {
        bernoulli_distribution distribution(p);
        return distribution(generator);
    }

    Statistics statistics() const override {
        double variance = p * (1.0 - p);
        return {p, variance, sqrt(variance)};
    }
};

class BinomialDistribution : public Distribution {
private:
    int n;

public:
    BinomialDistribution(int trials, double probability)
        : Distribution(probability), n(trials) {
        validateNonNegative(n, "Number of trials");
    }

    double pmf(int outcome) const override {
        if (outcome < 0 || outcome > n) return 0.0;

        return exp(
            lgamma(n + 1.0)
            - lgamma(outcome + 1.0)
            - lgamma(n - outcome + 1.0)
            + outcome * log(p == 0 ? 1.0 : p)
            + (n - outcome) * log(p == 1 ? 1.0 : 1.0 - p)
        ) *
        pow(p, outcome) *
        pow(1.0 - p, n - outcome);
    }

    double cdf(int outcome) const override {
        if (outcome < 0) return 0.0;
        if (outcome >= n) return 1.0;

        long double total = 0.0L;

        for (int k = 0; k <= outcome; ++k) {
            total += pmf(k);
        }

        return min(1.0, static_cast<double>(total));
    }

    int sample(mt19937& generator) const override {
        binomial_distribution<int> distribution(n, p);
        return distribution(generator);
    }

    Statistics statistics() const override {
        double mean = n * p;
        double variance = n * p * (1.0 - p);

        return {mean, variance, sqrt(variance)};
    }
};

class GeometricDistribution : public Distribution {
public:
    explicit GeometricDistribution(double probability)
        : Distribution(probability) {}

    double pmf(int outcome) const override {
        if (outcome < 1 || p == 0.0) return 0.0;
        if (p == 1.0) return outcome == 1 ? 1.0 : 0.0;

        return pow(1.0 - p, outcome - 1) * p;
    }

    double cdf(int outcome) const override {
        if (outcome < 1 || p == 0.0) return 0.0;
        if (p == 1.0) return 1.0;

        return 1.0 - pow(1.0 - p, outcome);
    }

    int sample(mt19937& generator) const override {
        if (p == 0.0) {
            throw ProbabilityError(
                "A success cannot occur when p = 0."
            );
        }

        if (p == 1.0) return 1;

        geometric_distribution<int> distribution(p);
        return distribution(generator);
    }

    Statistics statistics() const override {
        if (p == 0.0) {
            return {
                numeric_limits<double>::infinity(),
                numeric_limits<double>::infinity(),
                numeric_limits<double>::infinity()
            };
        }

        double mean = 1.0 / p;
        double variance = (1.0 - p) / (p * p);

        return {mean, variance, sqrt(variance)};
    }
};

class NegativeBinomialDistribution : public Distribution {
private:
    int requiredSuccesses;

public:
    NegativeBinomialDistribution(int successes, double probability)
        : Distribution(probability),
          requiredSuccesses(successes) {
        if (successes < 1) {
            throw ProbabilityError(
                "Required successes must be at least one."
            );
        }
    }

    double pmf(int outcome) const override {
        if (outcome < requiredSuccesses || p == 0.0) {
            return 0.0;
        }

        if (p == 1.0) {
            return outcome == requiredSuccesses ? 1.0 : 0.0;
        }

        return exp(
            lgamma(outcome)
            - lgamma(requiredSuccesses)
            - lgamma(outcome - requiredSuccesses + 1.0)
        ) *
        pow(p, requiredSuccesses) *
        pow(1.0 - p, outcome - requiredSuccesses);
    }

    double cdf(int outcome) const override {
        if (outcome < requiredSuccesses || p == 0.0) {
            return 0.0;
        }

        if (p == 1.0) return 1.0;

        long double total = 0.0L;

        for (int k = requiredSuccesses; k <= outcome; ++k) {
            total += pmf(k);
        }

        return min(1.0, static_cast<double>(total));
    }

    int sample(mt19937& generator) const override {
        if (p == 0.0) {
            throw ProbabilityError(
                "Sampling is impossible when p = 0."
            );
        }

        if (p == 1.0) return requiredSuccesses;

        negative_binomial_distribution<int> distribution(
            requiredSuccesses, p
        );

        return requiredSuccesses + distribution(generator);
    }

    Statistics statistics() const override {
        if (p == 0.0) {
            return {
                numeric_limits<double>::infinity(),
                numeric_limits<double>::infinity(),
                numeric_limits<double>::infinity()
            };
        }

        double mean = requiredSuccesses / p;
        double variance =
            requiredSuccesses * (1.0 - p) / (p * p);

        return {mean, variance, sqrt(variance)};
    }
};

void printDistribution(
    const string& name,
    const Distribution& distribution,
    int start,
    int end
) {
    cout << "\n" << name << "\n";
    cout << string(65, '-') << "\n";

    cout << left << setw(12) << "Outcome"
         << setw(20) << "PMF"
         << setw(20) << "CDF" << "\n";

    for (int k = start; k <= end; ++k) {
        cout << left << setw(12) << k
             << setw(20) << fixed << setprecision(8)
             << distribution.pmf(k)
             << setw(20) << distribution.cdf(k)
             << "\n";
    }

    Statistics stats = distribution.statistics();

    cout << "Mean: " << stats.mean << "\n";
    cout << "Variance: " << stats.variance << "\n";
    cout << "Standard deviation: "
         << stats.standardDeviation << "\n";
}

void printSimulation(
    const string& name,
    const Distribution& distribution,
    mt19937& generator
) {
    SimulationResult result = distribution.simulate(
        10000, generator
    );

    Statistics theoretical = distribution.statistics();

    cout << "\nSimulation: " << name << "\n";
    cout << "Observations: " << result.sampleCount << "\n";
    cout << "Empirical mean: " << result.empiricalMean << "\n";
    cout << "Theoretical mean: " << theoretical.mean << "\n";
    cout << "Empirical variance: " << result.empiricalVariance << "\n";

    cout << "Observed frequencies:\n";

    for (const auto& [outcome, frequency] : result.frequencies) {
        cout << "  " << outcome << ": " << frequency << "\n";
    }
}

void runTests() {
    BernoulliDistribution bernoulli(0.3);
    BinomialDistribution binomial(5, 0.5);
    GeometricDistribution geometric(0.25);
    NegativeBinomialDistribution negativeBinomial(3, 0.5);

    if (abs(bernoulli.pmf(1) - 0.3) > EPSILON) {
        throw runtime_error("Bernoulli test failed.");
    }

    if (abs(binomial.pmf(2) - 0.3125) > EPSILON) {
        throw runtime_error("Binomial test failed.");
    }

    if (abs(geometric.cdf(2) - 0.4375) > EPSILON) {
        throw runtime_error("Geometric test failed.");
    }

    if (abs(negativeBinomial.pmf(4) - 0.1875) > EPSILON) {
        throw runtime_error("Negative binomial test failed.");
    }

    if (abs(negativeBinomial.cdf(4) - 0.3125) > EPSILON) {
        throw runtime_error("Negative binomial CDF test failed.");
    }

    if (binomial.pmf(-1) != 0.0 ||
        geometric.pmf(0) != 0.0 ||
        negativeBinomial.pmf(2) != 0.0) {
        throw runtime_error("Support validation test failed.");
    }

    bool rejected = false;

    try {
        BinomialDistribution invalid(-1, 0.5);
    } catch (const ProbabilityError&) {
        rejected = true;
    }

    if (!rejected) {
        throw runtime_error("Invalid parameter was accepted.");
    }

    cout << "All statistical tests passed.\n";
}

int main() {
    try {
        cout << fixed << setprecision(6);

        runTests();

        mt19937 generator(42);

        BernoulliDistribution bernoulli(0.8);
        BinomialDistribution binomial(12, 0.8);
        GeometricDistribution geometric(0.25);
        NegativeBinomialDistribution negativeBinomial(4, 0.25);

        printDistribution(
            "Bernoulli: Service availability",
            bernoulli, 0, 1
        );

        printDistribution(
            "Binomial: Successful operations",
            binomial, 0, 12
        );

        printDistribution(
            "Geometric: Attempts until first success",
            geometric, 1, 8
        );

        printDistribution(
            "Negative Binomial: Attempts for four successes",
            negativeBinomial, 4, 12
        );

        printSimulation("Bernoulli", bernoulli, generator);
        printSimulation("Binomial", binomial, generator);
        printSimulation("Geometric", geometric, generator);
        printSimulation(
            "Negative Binomial", negativeBinomial, generator
        );

        cout << "\nBusiness risk calculations\n";

        cout << "P(at least 10 successful operations): "
             << binomial.probabilityAtLeast(10) << "\n";

        cout << "P(first success within 4 attempts): "
             << geometric.cdf(4) << "\n";

        cout << "P(four successes within 10 attempts): "
             << negativeBinomial.cdf(10) << "\n";

        cout << "\nExecution completed successfully.\n";
    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
