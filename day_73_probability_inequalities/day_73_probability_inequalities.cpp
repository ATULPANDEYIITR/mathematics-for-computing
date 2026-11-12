#include <algorithm>
#include <cassert>
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
 * Probability Inequality Evaluation Engine.
 * C++17, standard library only.
 */

enum class Inequality {
    Markov,
    Chebyshev,
    Jensen,
    Chernoff
};

struct Outcome {
    double value;
    double probability;
};

class Distribution {
private:
    vector<Outcome> outcomes;
    double meanValue = 0.0;
    double varianceValue = 0.0;

    void calculateMoments() {
        meanValue = 0.0;

        for (const auto& outcome : outcomes) {
            meanValue += outcome.value * outcome.probability;
        }

        varianceValue = 0.0;

        for (const auto& outcome : outcomes) {
            const double difference = outcome.value - meanValue;
            varianceValue +=
                outcome.probability * difference * difference;
        }
    }

public:
    explicit Distribution(vector<Outcome> data)
        : outcomes(std::move(data)) {

        if (outcomes.empty()) {
            throw invalid_argument("Distribution cannot be empty.");
        }

        double total = 0.0;

        for (const auto& outcome : outcomes) {
            if (!isfinite(outcome.value) ||
                !isfinite(outcome.probability) ||
                outcome.probability < 0.0) {
                throw invalid_argument("Invalid distribution outcome.");
            }

            total += outcome.probability;
        }

        if (abs(total - 1.0) > 1e-10) {
            throw invalid_argument("Probabilities must sum to one.");
        }

        calculateMoments();
    }

    double mean() const {
        return meanValue;
    }

    double variance() const {
        return varianceValue;
    }

    double standardDeviation() const {
        return sqrt(varianceValue);
    }

    double expectation(
        const function<double(double)>& function
    ) const {
        double result = 0.0;

        for (const auto& outcome : outcomes) {
            result += outcome.probability * function(outcome.value);
        }

        if (!isfinite(result)) {
            throw domain_error("Invalid expectation.");
        }

        return result;
    }

    double probability(
        const function<bool(double)>& predicate
    ) const {
        double result = 0.0;

        for (const auto& outcome : outcomes) {
            if (predicate(outcome.value)) {
                result += outcome.probability;
            }
        }

        return result;
    }

    bool isNonnegative() const {
        return all_of(
            outcomes.begin(),
            outcomes.end(),
            [](const Outcome& outcome) {
                return outcome.value >= 0.0;
            }
        );
    }

    const vector<Outcome>& data() const {
        return outcomes;
    }
};

struct BoundResult {
    Inequality inequality;
    double threshold;
    double bound;
    double exactProbability;
    double parameter;
};

class ProbabilityEngine {
private:
    map<string, Distribution> distributions;

    static void validatePositive(double value, const string& name) {
        if (!isfinite(value) || value <= 0.0) {
            throw invalid_argument(name + " must be positive.");
        }
    }

    static double logSumExp(const vector<double>& values) {
        if (values.empty()) {
            throw invalid_argument("Empty log-sum-exp input.");
        }

        const double maximum =
            *max_element(values.begin(), values.end());

        double sum = 0.0;

        for (double value : values) {
            sum += exp(value - maximum);
        }

        return maximum + log(sum);
    }

    static double logMGF(
        const Distribution& distribution,
        double lambda
    ) {
        vector<double> terms;

        for (const auto& outcome : distribution.data()) {
            if (outcome.probability > 0.0) {
                terms.push_back(
                    log(outcome.probability) +
                    lambda * outcome.value
                );
            }
        }

        return logSumExp(terms);
    }

public:
    void registerDistribution(
        const string& name,
        const Distribution& distribution
    ) {
        if (name.empty()) {
            throw invalid_argument("Distribution name is required.");
        }

        if (distributions.count(name)) {
            throw invalid_argument("Duplicate distribution name.");
        }

        distributions.emplace(name, distribution);
    }

    BoundResult evaluateMarkov(
        const Distribution& distribution,
        double threshold
    ) const {
        validatePositive(threshold, "Threshold");

        if (!distribution.isNonnegative()) {
            throw invalid_argument(
                "Markov requires a nonnegative random variable."
            );
        }

        const double bound = min(
            1.0,
            distribution.mean() / threshold
        );

        return {
            Inequality::Markov,
            threshold,
            bound,
            distribution.probability(
                [threshold](double x) {
                    return x >= threshold;
                }
            ),
            0.0
        };
    }

    BoundResult evaluateChebyshev(
        const Distribution& distribution,
        double deviation
    ) const {
        validatePositive(deviation, "Deviation");

        const double bound = min(
            1.0,
            distribution.variance() / (deviation * deviation)
        );

        const double mu = distribution.mean();

        return {
            Inequality::Chebyshev,
            deviation,
            bound,
            distribution.probability(
                [mu, deviation](double x) {
                    return abs(x - mu) >= deviation;
                }
            ),
            0.0
        };
    }

    BoundResult evaluateChernoff(
        const Distribution& distribution,
        double threshold,
        double lambdaMaximum = 20.0,
        int steps = 2000
    ) const {
        if (!isfinite(threshold) ||
            !isfinite(lambdaMaximum) ||
            lambdaMaximum <= 0.0 ||
            steps <= 0) {
            throw invalid_argument("Invalid Chernoff parameters.");
        }

        double bestBound = 1.0;
        double bestLambda = 0.0;

        for (int i = 0; i <= steps; ++i) {
            const double lambda =
                lambdaMaximum * i / steps;

            const double exponent =
                logMGF(distribution, lambda) -
                lambda * threshold;

            const double bound = exponent < -745.0
                ? 0.0
                : min(1.0, exp(exponent));

            if (bound < bestBound) {
                bestBound = bound;
                bestLambda = lambda;
            }
        }

        const double exact = distribution.probability(
            [threshold](double x) {
                return x >= threshold;
            }
        );

        return {
            Inequality::Chernoff,
            threshold,
            bestBound,
            exact,
            bestLambda
        };
    }

    BoundResult evaluateJensen(
        const Distribution& distribution,
        const function<double(double)>& convexFunction
    ) const {
        const double left = convexFunction(distribution.mean());
        const double right = distribution.expectation(convexFunction);

        if (!isfinite(left) || !isfinite(right)) {
            throw domain_error("Invalid Jensen function result.");
        }

        return {
            Inequality::Jensen,
            distribution.mean(),
            right - left,
            right,
            0.0
        };
    }

    const Distribution& get(const string& name) const {
        auto iterator = distributions.find(name);

        if (iterator == distributions.end()) {
            throw out_of_range("Distribution not found.");
        }

        return iterator->second;
    }

    void printReport(const string& name, double threshold) const {
        const Distribution& distribution = get(name);

        cout << "\nExperiment: " << name << '\n';
        cout << "Mean: " << distribution.mean() << '\n';
        cout << "Variance: " << distribution.variance() << '\n';

        if (distribution.isNonnegative()) {
            const auto result =
                evaluateMarkov(distribution, threshold);

            cout << "Markov bound: " << result.bound << '\n';
            cout << "Exact upper-tail probability: "
                 << result.exactProbability << '\n';
        } else {
            cout << "Markov: Not applicable to this variable.\n";
        }

        const double deviation =
            max(0.01, abs(threshold - distribution.mean()));

        const auto cheb =
            evaluateChebyshev(distribution, deviation);

        cout << "Chebyshev bound: " << cheb.bound << '\n';

        const auto chernoff =
            evaluateChernoff(distribution, threshold);

        cout << "Chernoff bound: " << chernoff.bound << '\n';
        cout << "Optimized lambda: " << chernoff.parameter << '\n';

        const auto jensen = evaluateJensen(
            distribution,
            [](double x) {
                return x * x;
            }
        );

        cout << "Jensen left side: "
             << distribution.mean() * distribution.mean() << '\n';

        cout << "Jensen right side: "
             << jensen.exactProbability << '\n';
    }
};

Distribution createBinomial(int trials, double probability) {
    if (trials < 0 || trials > 1000 ||
        !isfinite(probability) ||
        probability < 0.0 || probability > 1.0) {
        throw invalid_argument("Invalid binomial parameters.");
    }

    vector<Outcome> outcomes;
    vector<double> probabilities(trials + 1, 0.0);

    if (probability == 0.0) {
        probabilities[0] = 1.0;
    } else if (probability == 1.0) {
        probabilities[trials] = 1.0;
    } else {
        probabilities[0] = pow(1.0 - probability, trials);

        for (int k = 1; k <= trials; ++k) {
            probabilities[k] =
                probabilities[k - 1] *
                (trials - k + 1) / k *
                probability / (1.0 - probability);
        }
    }

    for (int k = 0; k <= trials; ++k) {
        outcomes.push_back({
            static_cast<double>(k),
            probabilities[k]
        });
    }

    return Distribution(std::move(outcomes));
}

void runTests() {
    Distribution distribution({
        {0, 0.1},
        {1, 0.2},
        {2, 0.4},
        {3, 0.2},
        {4, 0.1}
    });

    assert(abs(distribution.mean() - 2.0) < 1e-10);
    assert(abs(distribution.variance() - 1.4) < 1e-10);

    ProbabilityEngine engine;

    const auto markov = engine.evaluateMarkov(distribution, 3.0);

    assert(markov.bound + 1e-10 >= markov.exactProbability);

    const auto chebyshev = engine.evaluateChebyshev(
        distribution, 1.0
    );

    assert(
        chebyshev.bound + 1e-10 >= chebyshev.exactProbability
    );

    const auto jensen = engine.evaluateJensen(
        distribution,
        [](double x) { return x * x; }
    );

    assert(jensen.bound >= -1e-10);

    const auto binomial = createBinomial(20, 0.5);
    const auto chernoff = engine.evaluateChernoff(binomial, 15);

    assert(
        chernoff.bound + 1e-10 >= chernoff.exactProbability
    );

    bool rejected = false;

    try {
        engine.evaluateMarkov(distribution, 0.0);
    } catch (const invalid_argument&) {
        rejected = true;
    }

    assert(rejected);

    cout << "All C++ probability tests passed.\n";
}

int main() {
    try {
        cout << fixed << setprecision(8);

        runTests();

        ProbabilityEngine engine;

        Distribution operationalRisk({
            {0, 0.05},
            {1, 0.10},
            {2, 0.20},
            {3, 0.30},
            {4, 0.20},
            {5, 0.15}
        });

        engine.registerDistribution(
            "operational-risk",
            operationalRisk
        );

        engine.registerDistribution(
            "binomial-failures",
            createBinomial(30, 0.5)
        );

        engine.printReport("operational-risk", 4.0);
        engine.printReport("binomial-failures", 20.0);

        cout << "\nNONNEGATIVE VARIABLE VALIDATION\n";

        Distribution centered({
            {-2, 0.25},
            {0, 0.50},
            {2, 0.25}
        });

        try {
            engine.evaluateMarkov(centered, 2.0);
        } catch (const invalid_argument& error) {
            cout << error.what() << '\n';
        }

        cout << "\nAnalysis completed successfully.\n";

    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
