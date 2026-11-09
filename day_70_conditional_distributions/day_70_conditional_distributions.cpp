#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

/*
 * Conditional Distribution and Repository-Independent
 * Statistical Analysis Engine.
 *
 * Implements:
 * - Joint PMF
 * - Marginal PMF
 * - Conditional PMF
 * - Conditional expectation
 * - Conditional variance
 * - Conditional covariance
 * - Bivariate normal conditional density
 * - Law of total expectation
 * - Law of total variance
 *
 * Standard: C++17
 */

class DistributionError : public std::runtime_error {
public:
    explicit DistributionError(const std::string& message)
        : std::runtime_error(message) {}
};

struct Outcome {
    int x;
    int y;
    double probability;
};

struct Statistics {
    double conditioningProbability;
    double expectation;
    double variance;
};

class DiscreteJointDistribution {
private:
    std::vector<Outcome> outcomes;

    void validate() const {
        if (outcomes.empty()) {
            throw DistributionError("Joint distribution is empty.");
        }

        double total = 0.0;

        for (const auto& outcome : outcomes) {
            if (!std::isfinite(outcome.probability) ||
                outcome.probability < 0.0) {
                throw DistributionError("Invalid joint probability.");
            }

            total += outcome.probability;
        }

        if (std::abs(total - 1.0) > 1e-10) {
            throw DistributionError("Joint probabilities must sum to one.");
        }
    }

public:
    explicit DiscreteJointDistribution(
        std::vector<Outcome> data
    ) : outcomes(std::move(data)) {
        validate();
    }

    double jointProbability(int x, int y) const {
        double result = 0.0;

        for (const auto& outcome : outcomes) {
            if (outcome.x == x && outcome.y == y) {
                result += outcome.probability;
            }
        }

        return result;
    }

    double marginalX(int x) const {
        double result = 0.0;

        for (const auto& outcome : outcomes) {
            if (outcome.x == x) {
                result += outcome.probability;
            }
        }

        return result;
    }

    double marginalY(int y) const {
        double result = 0.0;

        for (const auto& outcome : outcomes) {
            if (outcome.y == y) {
                result += outcome.probability;
            }
        }

        return result;
    }

    std::map<int, double> conditionalYGivenX(int x) const {
        const double denominator = marginalX(x);

        if (denominator <= 0.0) {
            throw DistributionError(
                "Conditioning event X=x has zero probability."
            );
        }

        std::map<int, double> result;

        for (const auto& outcome : outcomes) {
            result[outcome.y] +=
                outcome.probability / denominator;
        }

        return result;
    }

    std::map<int, double> conditionalXGivenY(int y) const {
        const double denominator = marginalY(y);

        if (denominator <= 0.0) {
            throw DistributionError(
                "Conditioning event Y=y has zero probability."
            );
        }

        std::map<int, double> result;

        for (const auto& outcome : outcomes) {
            result[outcome.x] +=
                outcome.probability / denominator;
        }

        return result;
    }

    static double expectation(
        const std::map<int, double>& pmf
    ) {
        double result = 0.0;

        for (const auto& [value, probability] : pmf) {
            result += value * probability;
        }

        return result;
    }

    static double variance(
        const std::map<int, double>& pmf
    ) {
        const double mean = expectation(pmf);

        double result = 0.0;

        for (const auto& [value, probability] : pmf) {
            result += probability * std::pow(value - mean, 2);
        }

        return std::max(0.0, result);
    }

    Statistics conditionalStatistics(int x) const {
        const auto pmf = conditionalYGivenX(x);

        return {
            marginalX(x),
            expectation(pmf),
            variance(pmf)
        };
    }

    double covariance() const {
        double meanX = 0.0;
        double meanY = 0.0;

        for (const auto& outcome : outcomes) {
            meanX += outcome.x * outcome.probability;
            meanY += outcome.y * outcome.probability;
        }

        double result = 0.0;

        for (const auto& outcome : outcomes) {
            result +=
                (outcome.x - meanX) *
                (outcome.y - meanY) *
                outcome.probability;
        }

        return result;
    }

    double totalExpectation() const {
        double result = 0.0;

        std::map<int, double> marginal;

        for (const auto& outcome : outcomes) {
            marginal[outcome.x] += outcome.probability;
        }

        for (const auto& [x, probability] : marginal) {
            if (probability == 0.0) continue;

            result += probability *
                expectation(conditionalYGivenX(x));
        }

        return result;
    }

    double totalVariance() const {
        std::map<int, double> marginal;

        for (const auto& outcome : outcomes) {
            marginal[outcome.x] += outcome.probability;
        }

        double expectedConditionalVariance = 0.0;
        std::vector<std::pair<double, double>> means;

        for (const auto& [x, probability] : marginal) {
            if (probability == 0.0) continue;

            const auto pmf = conditionalYGivenX(x);

            const double mean = expectation(pmf);
            const double varianceValue = variance(pmf);

            expectedConditionalVariance +=
                probability * varianceValue;

            means.emplace_back(mean, probability);
        }

        double overallMean = 0.0;

        for (const auto& [mean, probability] : means) {
            overallMean += mean * probability;
        }

        double varianceOfConditionalMeans = 0.0;

        for (const auto& [mean, probability] : means) {
            varianceOfConditionalMeans +=
                probability * std::pow(mean - overallMean, 2);
        }

        return expectedConditionalVariance
            + varianceOfConditionalMeans;
    }

    double marginalVarianceY() const {
        std::map<int, double> marginal;

        for (const auto& outcome : outcomes) {
            marginal[outcome.y] += outcome.probability;
        }

        return variance(marginal);
    }

    void displayConditionalDistributions() const {
        std::map<int, double> marginal;

        for (const auto& outcome : outcomes) {
            marginal[outcome.x] += outcome.probability;
        }

        for (const auto& [x, probability] : marginal) {
            if (probability == 0.0) continue;

            const auto pmf = conditionalYGivenX(x);
            const auto statistics = conditionalStatistics(x);

            std::cout << "\nCondition X = " << x << '\n';
            std::cout << "P(X=x): " << probability << '\n';

            for (const auto& [y, conditionalProbability] : pmf) {
                std::cout
                    << "P(Y=" << y << " | X=" << x << ") = "
                    << conditionalProbability << '\n';
            }

            std::cout
                << "Conditional expectation: "
                << statistics.expectation << '\n';

            std::cout
                << "Conditional variance: "
                << statistics.variance << '\n';
        }
    }
};

class BivariateNormal {
private:
    double muX;
    double muY;
    double sigmaX;
    double sigmaY;
    double rho;

    void validate() const {
        if (!std::isfinite(muX) ||
            !std::isfinite(muY) ||
            !std::isfinite(sigmaX) ||
            !std::isfinite(sigmaY) ||
            !std::isfinite(rho)) {
            throw DistributionError("Parameters must be finite.");
        }

        if (sigmaX <= 0.0 || sigmaY <= 0.0) {
            throw DistributionError(
                "Standard deviations must be positive."
            );
        }

        if (rho <= -1.0 || rho >= 1.0) {
            throw DistributionError(
                "Correlation must be between -1 and 1, exclusive."
            );
        }
    }

public:
    BivariateNormal(
        double meanX,
        double meanY,
        double standardDeviationX,
        double standardDeviationY,
        double correlation
    )
        : muX(meanX),
          muY(meanY),
          sigmaX(standardDeviationX),
          sigmaY(standardDeviationY),
          rho(correlation) {
        validate();
    }

    double conditionalMean(double x) const {
        if (!std::isfinite(x)) {
            throw DistributionError("Conditioning value must be finite.");
        }

        return muY +
            rho * sigmaY / sigmaX * (x - muX);
    }

    double conditionalVariance() const {
        return sigmaY * sigmaY * (1.0 - rho * rho);
    }

    double conditionalDensity(double y, double x) const {
        if (!std::isfinite(y)) {
            throw DistributionError("Evaluation value must be finite.");
        }

        const double mean = conditionalMean(x);
        const double variance = conditionalVariance();

        const double difference = y - mean;

        return std::exp(
            -(difference * difference) / (2.0 * variance)
        ) / std::sqrt(2.0 * M_PI * variance);
    }
};

int main() {
    try {
        std::cout << std::fixed << std::setprecision(6);

        std::cout
            << "CONDITIONAL DISTRIBUTION ENGINE\n"
            << "================================\n";

        std::vector<Outcome> data = {
            {0, 0, 0.10},
            {0, 1, 0.10},
            {0, 2, 0.05},
            {1, 0, 0.05},
            {1, 1, 0.20},
            {1, 2, 0.15},
            {2, 0, 0.05},
            {2, 1, 0.10},
            {2, 2, 0.20}
        };

        DiscreteJointDistribution distribution(data);

        std::cout << "\n1. Discrete conditional distributions\n";

        distribution.displayConditionalDistributions();

        std::cout << "\n2. Conditional probability statistics\n";

        const auto statistics =
            distribution.conditionalStatistics(1);

        std::cout
            << "P(X=1): "
            << statistics.conditioningProbability << '\n';

        std::cout
            << "E[Y|X=1]: "
            << statistics.expectation << '\n';

        std::cout
            << "Var(Y|X=1): "
            << statistics.variance << '\n';

        std::cout << "\n3. Conditional covariance\n";

        std::cout
            << "Cov(X,Y): "
            << distribution.covariance() << '\n';

        std::cout << "\n4. Law of total expectation\n";

        const double totalMean = distribution.totalExpectation();

        std::cout << "E[E[Y|X]] = " << totalMean << '\n';

        std::cout << "\n5. Law of total variance\n";

        const double decomposedVariance =
            distribution.totalVariance();

        const double directVariance =
            distribution.marginalVarianceY();

        std::cout
            << "E[Var(Y|X)] + Var(E[Y|X]) = "
            << decomposedVariance << '\n';

        std::cout
            << "Direct Var(Y) = "
            << directVariance << '\n';

        if (std::abs(
                decomposedVariance - directVariance
            ) > 1e-10) {
            throw DistributionError(
                "Total variance identity validation failed."
            );
        }

        std::cout << "\n6. Continuous conditional density\n";

        BivariateNormal normal(
            10.0,
            50.0,
            2.0,
            8.0,
            0.75
        );

        const double x = 12.0;
        const double y = 58.0;

        std::cout
            << "E[Y|X=12] = "
            << normal.conditionalMean(x) << '\n';

        std::cout
            << "Var(Y|X) = "
            << normal.conditionalVariance() << '\n';

        std::cout
            << "f(Y=58|X=12) = "
            << normal.conditionalDensity(y, x) << '\n';

        std::cout << "\n7. Edge case validation\n";

        try {
            distribution.conditionalYGivenX(99);

            throw DistributionError(
                "Expected zero-probability failure was not raised."
            );
        } catch (const DistributionError& error) {
            std::cout
                << "Handled conditioning failure: "
                << error.what() << '\n';
        }

        std::cout << "\nAll statistical checks passed.\n";

    } catch (const std::exception& error) {
        std::cerr
            << "Application error: "
            << error.what() << '\n';

        return 1;
    }

    return 0;
}
