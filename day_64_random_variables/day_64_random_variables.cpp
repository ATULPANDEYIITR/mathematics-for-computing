#include <algorithm>
#include <cassert>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace std;

class DistributionError : public invalid_argument {
public:
    explicit DistributionError(const string& message)
        : invalid_argument(message) {}
};

void validateNotNaN(double value, const string& name) {
    if (isnan(value)) {
        throw DistributionError(name + " cannot be NaN.");
    }
}

void validateFinite(double value, const string& name) {
    if (!isfinite(value)) {
        throw DistributionError(name + " must be finite.");
    }
}

class RandomVariable {
public:
    virtual ~RandomVariable() = default;

    virtual double mean() const = 0;
    virtual double variance() const = 0;
    virtual double cdf(double x) const = 0;
    virtual double sample(mt19937_64& engine) const = 0;
};

class DiscreteRandomVariable : public RandomVariable {
private:
    vector<double> support_;
    vector<double> probabilities_;
    vector<double> cumulative_;
    double mean_ = 0.0;
    double variance_ = 0.0;

public:
    explicit DiscreteRandomVariable(
        vector<pair<double, double>> outcomes
    ) {
        if (outcomes.empty()) {
            throw DistributionError("Discrete support cannot be empty.");
        }

        for (const auto& [value, probability] : outcomes) {
            validateFinite(value, "Support value");
            validateFinite(probability, "Probability");

            if (probability < 0.0 || probability > 1.0) {
                throw DistributionError(
                    "Each probability must be between 0 and 1."
                );
            }
        }

        sort(
            outcomes.begin(),
            outcomes.end(),
            [](const auto& left, const auto& right) {
                return left.first < right.first;
            }
        );

        double total = 0.0;

        for (size_t index = 0; index < outcomes.size(); ++index) {
            const auto& [value, probability] = outcomes[index];

            if (
                index > 0 &&
                outcomes[index - 1].first == value
            ) {
                throw DistributionError("Duplicate support value.");
            }

            support_.push_back(value);
            probabilities_.push_back(probability);
            total += probability;
        }

        if (abs(total - 1.0) > 1e-9) {
            throw DistributionError(
                "Probabilities must sum to 1. Actual total: " +
                to_string(total)
            );
        }

        double cumulative = 0.0;

        for (double probability : probabilities_) {
            cumulative += probability;
            cumulative_.push_back(cumulative);
        }

        cumulative_.back() = 1.0;

        for (size_t index = 0; index < support_.size(); ++index) {
            mean_ += support_[index] * probabilities_[index];
        }

        for (size_t index = 0; index < support_.size(); ++index) {
            const double difference = support_[index] - mean_;

            variance_ += probabilities_[index] *
                         difference * difference;
        }
    }

    double pmf(double x) const {
        validateNotNaN(x, "PMF input");

        if (!isfinite(x)) {
            return 0.0;
        }

        auto position = lower_bound(
            support_.begin(),
            support_.end(),
            x
        );

        if (position == support_.end() || *position != x) {
            return 0.0;
        }

        size_t index = static_cast<size_t>(
            distance(support_.begin(), position)
        );

        return probabilities_[index];
    }

    double cdf(double x) const override {
        validateNotNaN(x, "CDF input");

        auto position = upper_bound(
            support_.begin(),
            support_.end(),
            x
        );

        if (position == support_.begin()) {
            return 0.0;
        }

        size_t index = static_cast<size_t>(
            distance(support_.begin(), position) - 1
        );

        return cumulative_[index];
    }

    double mean() const override {
        return mean_;
    }

    double variance() const override {
        return variance_;
    }

    double sample(mt19937_64& engine) const override {
        uniform_real_distribution<double> uniform(0.0, 1.0);
        const double draw = uniform(engine);

        auto position = lower_bound(
            cumulative_.begin(),
            cumulative_.end(),
            draw
        );

        if (position == cumulative_.end()) {
            return support_.back();
        }

        size_t index = static_cast<size_t>(
            distance(cumulative_.begin(), position)
        );

        return support_[index];
    }

    const vector<double>& support() const {
        return support_;
    }

    const vector<double>& probabilities() const {
        return probabilities_;
    }
};

class ContinuousRandomVariable : public RandomVariable {
public:
    virtual double pdf(double x) const = 0;
};

class NormalRandomVariable : public ContinuousRandomVariable {
private:
    double mean_;
    double standard_deviation_;

public:
    NormalRandomVariable(double mean, double standard_deviation)
        : mean_(mean),
          standard_deviation_(standard_deviation) {
        validateFinite(mean_, "Normal mean");
        validateFinite(standard_deviation_, "Standard deviation");

        if (standard_deviation_ <= 0.0) {
            throw DistributionError(
                "Normal standard deviation must be positive."
            );
        }
    }

    double mean() const override {
        return mean_;
    }

    double variance() const override {
        return standard_deviation_ * standard_deviation_;
    }

    double pdf(double x) const override {
        validateNotNaN(x, "PDF input");

        if (!isfinite(x)) {
            return 0.0;
        }

        const double z = (x - mean_) / standard_deviation_;

        const double denominator =
            standard_deviation_ * sqrt(2.0 * acos(-1.0));

        return exp(-0.5 * z * z) / denominator;
    }

    double cdf(double x) const override {
        validateNotNaN(x, "CDF input");

        if (x == numeric_limits<double>::infinity()) {
            return 1.0;
        }

        if (x == -numeric_limits<double>::infinity()) {
            return 0.0;
        }

        const double z =
            (x - mean_) / (standard_deviation_ * sqrt(2.0));

        return 0.5 * erfc(-z);
    }

    double sample(mt19937_64& engine) const override {
        normal_distribution<double> distribution(
            mean_,
            standard_deviation_
        );

        return distribution(engine);
    }
};

class UniformRandomVariable : public ContinuousRandomVariable {
private:
    double lower_;
    double upper_;

public:
    UniformRandomVariable(double lower, double upper)
        : lower_(lower), upper_(upper) {
        validateFinite(lower_, "Lower bound");
        validateFinite(upper_, "Upper bound");

        if (lower_ >= upper_) {
            throw DistributionError(
                "Uniform lower bound must be below upper bound."
            );
        }
    }

    double mean() const override {
        return (lower_ + upper_) / 2.0;
    }

    double variance() const override {
        const double width = upper_ - lower_;
        return width * width / 12.0;
    }

    double pdf(double x) const override {
        validateNotNaN(x, "PDF input");

        if (x >= lower_ && x <= upper_) {
            return 1.0 / (upper_ - lower_);
        }

        return 0.0;
    }

    double cdf(double x) const override {
        validateNotNaN(x, "CDF input");

        if (x <= lower_) {
            return 0.0;
        }

        if (x >= upper_) {
            return 1.0;
        }

        return (x - lower_) / (upper_ - lower_);
    }

    double sample(mt19937_64& engine) const override {
        uniform_real_distribution<double> distribution(
            lower_,
            upper_
        );

        return distribution(engine);
    }
};

DiscreteRandomVariable binomialDistribution(
    int trials,
    double probability
) {
    if (trials < 0 || trials > 1000) {
        throw DistributionError(
            "Trials must be between 0 and 1000."
        );
    }

    validateFinite(probability, "Success probability");

    if (probability < 0.0 || probability > 1.0) {
        throw DistributionError(
            "Success probability must be between 0 and 1."
        );
    }

    vector<pair<double, double>> outcomes;

    if (probability == 0.0) {
        outcomes.push_back({0.0, 1.0});
    } else if (probability == 1.0) {
        outcomes.push_back({
            static_cast<double>(trials), 1.0
        });
    } else {
        double currentProbability = pow(1.0 - probability, trials);

        for (int k = 0; k <= trials; ++k) {
            outcomes.push_back({
                static_cast<double>(k),
                currentProbability
            });

            if (k < trials) {
                currentProbability *=
                    (static_cast<double>(trials - k) /
                     static_cast<double>(k + 1)) *
                    (probability / (1.0 - probability));
            }
        }
    }

    return DiscreteRandomVariable(outcomes);
}

struct MonteCarloEstimate {
    double probability;
    size_t successes;
    size_t sampleCount;
    double standardError;
};

template <typename Variable, typename Predicate>
MonteCarloEstimate estimateProbability(
    const Variable& variable,
    Predicate event,
    size_t sampleCount,
    mt19937_64& engine
) {
    if (sampleCount == 0 || sampleCount > 5'000'000) {
        throw invalid_argument(
            "Sample count must be between 1 and 5,000,000."
        );
    }

    size_t successes = 0;

    for (size_t index = 0; index < sampleCount; ++index) {
        const double observation = variable.sample(engine);

        if (event(observation)) {
            ++successes;
        }
    }

    const double estimate =
        static_cast<double>(successes) /
        static_cast<double>(sampleCount);

    const double standardError = sqrt(
        estimate * (1.0 - estimate) /
        static_cast<double>(sampleCount)
    );

    return {
        estimate,
        successes,
        sampleCount,
        standardError
    };
}

class OnlineStatistics {
private:
    size_t count_ = 0;
    double mean_ = 0.0;
    double m2_ = 0.0;

public:
    void update(double value) {
        validateFinite(value, "Observation");

        ++count_;

        const double delta = value - mean_;
        mean_ += delta / static_cast<double>(count_);

        const double adjustedDelta = value - mean_;
        m2_ += delta * adjustedDelta;
    }

    size_t count() const {
        return count_;
    }

    double mean() const {
        return mean_;
    }

    double populationVariance() const {
        if (count_ == 0) {
            return 0.0;
        }

        return m2_ / static_cast<double>(count_);
    }

    double sampleVariance() const {
        if (count_ < 2) {
            return 0.0;
        }

        return m2_ / static_cast<double>(count_ - 1);
    }
};

void runValidationChecks() {
    DiscreteRandomVariable die({
        {1, 1.0 / 6.0},
        {2, 1.0 / 6.0},
        {3, 1.0 / 6.0},
        {4, 1.0 / 6.0},
        {5, 1.0 / 6.0},
        {6, 1.0 / 6.0}
    });

    assert(abs(die.pmf(3) - 1.0 / 6.0) < 1e-9);
    assert(abs(die.cdf(3) - 0.5) < 1e-9);
    assert(abs(die.mean() - 3.5) < 1e-9);

    NormalRandomVariable normal(0.0, 1.0);

    assert(abs(normal.cdf(0.0) - 0.5) < 1e-12);

    UniformRandomVariable uniform(0.0, 10.0);

    assert(abs(uniform.cdf(5.0) - 0.5) < 1e-12);
    assert(abs(uniform.pdf(5.0) - 0.1) < 1e-12);

    bool rejected = false;

    try {
        DiscreteRandomVariable invalid({
            {0, 0.4},
            {1, 0.4}
        });
    } catch (const DistributionError&) {
        rejected = true;
    }

    assert(rejected);
}

int main(int argc, char* argv[]) {
    try {
        size_t sampleCount = 100'000;

        if (argc > 1) {
            const string input = argv[1];
            size_t processed = 0;

            try {
                sampleCount = stoull(input, &processed);
            } catch (...) {
                throw invalid_argument("Sample count must be a positive integer.");
            }

            if (processed != input.size()) {
                throw invalid_argument("Sample count contains invalid characters.");
            }
        }

        if (sampleCount == 0 || sampleCount > 5'000'000) {
            throw invalid_argument(
                "Sample count must be between 1 and 5,000,000."
            );
        }

        runValidationChecks();

        // Fixed seed supports repeatable experiments and debugging.
        mt19937_64 engine(20261103ULL);

        cout << fixed << setprecision(6);

        cout << "RANDOM VARIABLES: DISCRETE AND CONTINUOUS\n";
        cout << string(58, '=') << '\n';

        // Four independent requests with a 10% failure probability.
        DiscreteRandomVariable failures =
            binomialDistribution(4, 0.10);

        cout << "\n1. DISCRETE RANDOM VARIABLE\n";
        cout << "X = number of failed requests among four requests\n";

        for (size_t index = 0;
             index < failures.support().size();
             ++index) {
            cout << "P(X = "
                 << failures.support()[index]
                 << ") = "
                 << failures.probabilities()[index]
                 << '\n';
        }

        cout << "P(X = 2)  = " << failures.pmf(2) << '\n';
        cout << "P(X <= 2) = " << failures.cdf(2) << '\n';
        cout << "E[X]      = " << failures.mean() << '\n';
        cout << "Var(X)    = " << failures.variance() << '\n';

        auto failureEstimate = estimateProbability(
            failures,
            [](double value) {
                return value >= 2.0;
            },
            sampleCount,
            engine
        );

        cout << "Estimated P(X >= 2) = "
             << failureEstimate.probability << '\n';

        cout << "Monte Carlo standard error = "
             << failureEstimate.standardError << '\n';

        // API response time is modeled with a normal distribution.
        NormalRandomVariable latency(120.0, 25.0);

        cout << "\n2. CONTINUOUS NORMAL RANDOM VARIABLE\n";
        cout << "Y = API response time in milliseconds\n";
        cout << "Mean         = " << latency.mean() << " ms\n";
        cout << "Variance     = " << latency.variance() << " ms^2\n";
        cout << "PDF at 150   = " << latency.pdf(150.0) << '\n';
        cout << "CDF at 150   = " << latency.cdf(150.0) << '\n';
        cout << "P(Y > 180)   = "
             << 1.0 - latency.cdf(180.0) << '\n';

        auto latencyEstimate = estimateProbability(
            latency,
            [](double value) {
                return value > 180.0;
            },
            sampleCount,
            engine
        );

        cout << "Estimated P(Y > 180) = "
             << latencyEstimate.probability << '\n';

        // Sensor measurement error has a uniform distribution.
        UniformRandomVariable sensorError(-2.0, 2.0);

        cout << "\n3. CONTINUOUS UNIFORM RANDOM VARIABLE\n";
        cout << "Z = sensor measurement error\n";
        cout << "Mean       = " << sensorError.mean() << '\n';
        cout << "Variance   = " << sensorError.variance() << '\n';
        cout << "PDF at 0   = " << sensorError.pdf(0.0) << '\n';
        cout << "CDF at 1   = " << sensorError.cdf(1.0) << '\n';

        const double centralProbability =
            sensorError.cdf(1.0) - sensorError.cdf(-1.0);

        cout << "P(-1 <= Z <= 1) = "
             << centralProbability << '\n';

        // Welford's algorithm processes observations without storing them.
        OnlineStatistics statistics;

        for (size_t index = 0; index < sampleCount; ++index) {
            statistics.update(latency.sample(engine));
        }

        cout << "\n4. ONLINE LATENCY STATISTICS\n";
        cout << "Observations        = " << statistics.count() << '\n';
        cout << "Empirical mean      = " << statistics.mean() << " ms\n";
        cout << "Empirical variance  = "
             << statistics.sampleVariance() << '\n';

        cout << "\n5. VALIDATION\n";
        cout << "All deterministic checks passed.\n";
        cout << "The pseudorandom generator is for simulation, not cryptography.\n";

        return 0;
    } catch (const exception& error) {
        cerr << "Error: " << error.what() << '\n';
        return 1;
    }
}
