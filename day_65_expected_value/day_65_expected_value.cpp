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

/*
 * EXPECTED VALUE AND MOMENTS
 *
 * C++17 probability and financial risk engine.
 *
 * Features:
 * - Discrete probability distributions
 * - Mathematical expectation
 * - Variance and standard deviation
 * - Raw and central moments
 * - Skewness and kurtosis
 * - Conditional expectation
 * - Joint covariance and correlation
 * - Monte Carlo estimation
 * - Portfolio risk evaluation
 * - Input validation
 */

constexpr double EPSILON = 1e-9;

struct Outcome {
    double value;
    double probability;
};

struct Statistics {
    double mean;
    double variance;
    double standardDeviation;
    double skewness;
    double kurtosis;
};

class ProbabilityException : public runtime_error {
public:
    explicit ProbabilityException(const string& message)
        : runtime_error(message) {}
};

class Distribution {
private:
    string name;
    vector<Outcome> outcomes;

    void validate() const {
        if (outcomes.empty()) {
            throw ProbabilityException(
                "Distribution cannot be empty."
            );
        }

        double total = 0.0;

        for (const auto& outcome : outcomes) {
            if (
                !isfinite(outcome.value) ||
                !isfinite(outcome.probability)
            ) {
                throw ProbabilityException(
                    "Values and probabilities must be finite."
                );
            }

            if (
                outcome.probability < 0.0 ||
                outcome.probability > 1.0
            ) {
                throw ProbabilityException(
                    "Probability must be between 0 and 1."
                );
            }

            total += outcome.probability;
        }

        if (abs(total - 1.0) > EPSILON) {
            throw ProbabilityException(
                "Probabilities must sum to 1."
            );
        }
    }

public:
    Distribution(string distributionName, vector<Outcome> data)
        : name(move(distributionName)),
          outcomes(move(data)) {
        validate();
    }

    const string& getName() const {
        return name;
    }

    double expectation() const {
        double result = 0.0;

        for (const auto& item : outcomes) {
            result += item.value * item.probability;
        }

        return result;
    }

    double rawMoment(int order) const {
        if (order < 0) {
            throw invalid_argument(
                "Moment order cannot be negative."
            );
        }

        double result = 0.0;

        for (const auto& item : outcomes) {
            result += pow(item.value, order) * item.probability;
        }

        return result;
    }

    double centralMoment(int order) const {
        if (order < 0) {
            throw invalid_argument(
                "Moment order cannot be negative."
            );
        }

        const double mean = expectation();
        double result = 0.0;

        for (const auto& item : outcomes) {
            result +=
                pow(item.value - mean, order) *
                item.probability;
        }

        return result;
    }

    double variance() const {
        return max(0.0, centralMoment(2));
    }

    double standardDeviation() const {
        return sqrt(variance());
    }

    double probabilityGreaterThan(double threshold) const {
        double result = 0.0;

        for (const auto& item : outcomes) {
            if (item.value > threshold) {
                result += item.probability;
            }
        }

        return result;
    }

    double conditionalExpectation(
        double threshold,
        bool greaterThan = true
    ) const {
        double weightedSum = 0.0;
        double conditionalProbability = 0.0;

        for (const auto& item : outcomes) {
            const bool selected = greaterThan
                ? item.value > threshold
                : item.value <= threshold;

            if (selected) {
                weightedSum += item.value * item.probability;
                conditionalProbability += item.probability;
            }
        }

        if (conditionalProbability <= EPSILON) {
            throw ProbabilityException(
                "Conditional event has zero probability."
            );
        }

        return weightedSum / conditionalProbability;
    }

    Statistics calculate() const {
        const double mean = expectation();
        const double var = variance();
        const double sd = sqrt(var);

        double skewness = numeric_limits<double>::quiet_NaN();
        double kurtosis = numeric_limits<double>::quiet_NaN();

        if (var > EPSILON) {
            skewness = centralMoment(3) / pow(sd, 3);
            kurtosis = centralMoment(4) / pow(var, 2);
        }

        return {
            mean,
            var,
            sd,
            skewness,
            kurtosis
        };
    }

    void printReport() const {
        const Statistics stats = calculate();

        cout << "\n" << name << "\n";
        cout << string(55, '-') << "\n";

        cout << "Expected value: "
             << stats.mean << "\n";

        cout << "Variance: "
             << stats.variance << "\n";

        cout << "Standard deviation: "
             << stats.standardDeviation << "\n";

        cout << "Skewness: "
             << stats.skewness << "\n";

        cout << "Kurtosis: "
             << stats.kurtosis << "\n";

        cout << "\nRaw moments:\n";

        for (int order = 1; order <= 4; ++order) {
            cout << "E[X^" << order << "] = "
                 << rawMoment(order) << "\n";
        }

        cout << "\nCentral moments:\n";

        for (int order = 1; order <= 4; ++order) {
            cout << "E[(X - mean)^" << order << "] = "
                 << centralMoment(order) << "\n";
        }
    }

    const vector<Outcome>& getOutcomes() const {
        return outcomes;
    }
};

struct JointOutcome {
    double x;
    double y;
    double probability;
};

class JointDistribution {
private:
    vector<JointOutcome> outcomes;

public:
    explicit JointDistribution(vector<JointOutcome> data)
        : outcomes(move(data)) {

        if (outcomes.empty()) {
            throw ProbabilityException(
                "Joint distribution cannot be empty."
            );
        }

        double total = 0.0;

        for (const auto& item : outcomes) {
            if (
                !isfinite(item.x) ||
                !isfinite(item.y) ||
                !isfinite(item.probability) ||
                item.probability < 0.0 ||
                item.probability > 1.0
            ) {
                throw ProbabilityException(
                    "Invalid joint outcome."
                );
            }

            total += item.probability;
        }

        if (abs(total - 1.0) > EPSILON) {
            throw ProbabilityException(
                "Joint probabilities must sum to 1."
            );
        }
    }

    double covariance() const {
        double meanX = 0.0;
        double meanY = 0.0;

        for (const auto& item : outcomes) {
            meanX += item.x * item.probability;
            meanY += item.y * item.probability;
        }

        double result = 0.0;

        for (const auto& item : outcomes) {
            result +=
                (item.x - meanX) *
                (item.y - meanY) *
                item.probability;
        }

        return result;
    }

    double correlation() const {
        double meanX = 0.0;
        double meanY = 0.0;

        for (const auto& item : outcomes) {
            meanX += item.x * item.probability;
            meanY += item.y * item.probability;
        }

        double varianceX = 0.0;
        double varianceY = 0.0;

        for (const auto& item : outcomes) {
            varianceX += pow(item.x - meanX, 2)
                       * item.probability;

            varianceY += pow(item.y - meanY, 2)
                       * item.probability;
        }

        if (varianceX <= EPSILON || varianceY <= EPSILON) {
            throw ProbabilityException(
                "Correlation is undefined for zero variance."
            );
        }

        return covariance() / sqrt(varianceX * varianceY);
    }
};

class MonteCarloSimulator {
public:
    static double estimate(
        const Distribution& distribution,
        size_t trials,
        unsigned int seed = 42
    ) {
        if (trials == 0) {
            throw invalid_argument(
                "Simulation trials must be positive."
            );
        }

        mt19937 generator(seed);

        vector<double> values;
        vector<double> probabilities;

        for (const auto& item : distribution.getOutcomes()) {
            values.push_back(item.value);
            probabilities.push_back(item.probability);
        }

        discrete_distribution<size_t> selector(
            probabilities.begin(),
            probabilities.end()
        );

        double sum = 0.0;

        for (size_t i = 0; i < trials; ++i) {
            size_t index = selector(generator);
            sum += values[index];
        }

        return sum / static_cast<double>(trials);
    }
};

struct PortfolioAsset {
    string name;
    double expectedReturn;
    double weight;
    double standardDeviation;
};

class Portfolio {
private:
    vector<PortfolioAsset> assets;

public:
    explicit Portfolio(vector<PortfolioAsset> data)
        : assets(move(data)) {

        if (assets.empty()) {
            throw invalid_argument(
                "Portfolio cannot be empty."
            );
        }

        double totalWeight = 0.0;

        for (const auto& asset : assets) {
            if (
                !isfinite(asset.weight) ||
                !isfinite(asset.expectedReturn) ||
                !isfinite(asset.standardDeviation) ||
                asset.weight < 0.0 ||
                asset.standardDeviation < 0.0
            ) {
                throw invalid_argument(
                    "Invalid portfolio asset."
                );
            }

            totalWeight += asset.weight;
        }

        if (abs(totalWeight - 1.0) > EPSILON) {
            throw invalid_argument(
                "Portfolio weights must sum to 1."
            );
        }
    }

    double expectedReturn() const {
        double result = 0.0;

        for (const auto& asset : assets) {
            result += asset.weight * asset.expectedReturn;
        }

        return result;
    }

    double varianceAssumingIndependence() const {
        double result = 0.0;

        for (const auto& asset : assets) {
            result +=
                pow(asset.weight * asset.standardDeviation, 2);
        }

        return result;
    }

    double standardDeviationAssumingIndependence() const {
        return sqrt(varianceAssumingIndependence());
    }
};

int main() {
    try {
        cout << fixed << setprecision(6);

        cout << string(65, '=') << "\n";
        cout << "EXPECTED VALUE AND MOMENTS ENGINE\n";
        cout << string(65, '=') << "\n";

        // Fair six-sided die.
        vector<Outcome> dieOutcomes;

        for (int face = 1; face <= 6; ++face) {
            dieOutcomes.push_back({
                static_cast<double>(face),
                1.0 / 6.0
            });
        }

        Distribution die("Fair Die", dieOutcomes);
        die.printReport();

        // Financial investment scenario.
        Distribution investment(
            "Investment Return",
            {
                {-1000, 0.10},
                {-200, 0.20},
                {300, 0.40},
                {1000, 0.20},
                {2500, 0.10}
            }
        );

        investment.printReport();

        cout << "\nInvestment risk evaluation\n";

        cout << "Probability of positive return: "
             << investment.probabilityGreaterThan(0)
             << "\n";

        cout << "Expected return conditional on positive outcome: "
             << investment.conditionalExpectation(0)
             << "\n";

        // Joint distribution for two financial variables.
        JointDistribution joint({
            {10, 20, 0.20},
            {20, 30, 0.30},
            {30, 20, 0.10},
            {40, 50, 0.40}
        });

        cout << "\nJoint distribution\n";

        cout << "Covariance: "
             << joint.covariance() << "\n";

        cout << "Correlation: "
             << joint.correlation() << "\n";

        // Portfolio expectation and independent-risk model.
        Portfolio portfolio({
            {"Equity", 0.12, 0.60, 0.20},
            {"Bonds", 0.05, 0.30, 0.06},
            {"Cash", 0.03, 0.10, 0.01}
        });

        cout << "\nPortfolio evaluation\n";

        cout << "Expected return: "
             << portfolio.expectedReturn() << "\n";

        cout << "Variance assuming independence: "
             << portfolio.varianceAssumingIndependence()
             << "\n";

        cout << "Standard deviation assuming independence: "
             << portfolio.standardDeviationAssumingIndependence()
             << "\n";

        // Monte Carlo approximation.
        double estimate = MonteCarloSimulator::estimate(
            die,
            100000,
            42
        );

        cout << "\nMonte Carlo simulation\n";

        cout << "Estimated expectation: "
             << estimate << "\n";

        cout << "Theoretical expectation: "
             << die.expectation() << "\n";

        cout << "Absolute error: "
             << abs(estimate - die.expectation()) << "\n";

        // Deterministic distribution.
        Distribution constant(
            "Deterministic Outcome",
            {{50, 1.0}}
        );

        cout << "\nDeterministic variance: "
             << constant.variance() << "\n";

        // Mathematical validation.
        if (abs(die.expectation() - 3.5) > EPSILON) {
            throw runtime_error("Die expectation test failed.");
        }

        if (abs(die.variance() - 35.0 / 12.0) > EPSILON) {
            throw runtime_error("Die variance test failed.");
        }

        if (constant.variance() != 0.0) {
            throw runtime_error(
                "Deterministic variance test failed."
            );
        }

        cout << "\nAll mathematical tests passed.\n";

    } catch (const exception& error) {
        cerr << "Application error: "
             << error.what() << "\n";

        return 1;
    }

    return 0;
}
