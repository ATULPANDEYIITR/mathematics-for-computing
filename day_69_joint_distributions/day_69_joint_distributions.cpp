#include <iostream>
#include <vector>
#include <map>
#include <cmath>
#include <stdexcept>
#include <iomanip>
#include <string>
#include <limits>
#include <algorithm>

using namespace std;

class DistributionError : public runtime_error {
public:
    explicit DistributionError(const string& message)
        : runtime_error(message) {}
};

struct Outcome {
    double x;
    double y;
    double probability;
};

class JointDistribution {
private:
    map<pair<double, double>, double> pmf;
    double tolerance;

    static bool finite(double value) {
        return isfinite(value);
    }

public:
    explicit JointDistribution(
        const vector<Outcome>& outcomes,
        double tolerance = 1e-10
    ) : tolerance(tolerance) {

        if (outcomes.empty()) {
            throw DistributionError("Distribution cannot be empty.");
        }

        if (!finite(tolerance) || tolerance < 0) {
            throw DistributionError("Invalid tolerance.");
        }

        double total = 0.0;

        for (const auto& outcome : outcomes) {
            if (
                !finite(outcome.x) ||
                !finite(outcome.y) ||
                !finite(outcome.probability)
            ) {
                throw DistributionError(
                    "All outcome values must be finite."
                );
            }

            if (outcome.probability < 0) {
                throw DistributionError(
                    "Negative probability is invalid."
                );
            }

            auto key = make_pair(outcome.x, outcome.y);

            if (pmf.count(key)) {
                throw DistributionError(
                    "Duplicate joint outcome detected."
                );
            }

            pmf[key] = outcome.probability;
            total += outcome.probability;
        }

        if (abs(total - 1.0) > tolerance) {
            throw DistributionError(
                "Joint probabilities must sum to one."
            );
        }

        for (auto& entry : pmf) {
            entry.second /= total;
        }
    }

    double jointProbability(double x, double y) const {
        auto it = pmf.find({x, y});

        return it == pmf.end() ? 0.0 : it->second;
    }

    map<double, double> marginalX() const {
        map<double, double> result;

        for (const auto& [outcome, probability] : pmf) {
            result[outcome.first] += probability;
        }

        return result;
    }

    map<double, double> marginalY() const {
        map<double, double> result;

        for (const auto& [outcome, probability] : pmf) {
            result[outcome.second] += probability;
        }

        return result;
    }

    map<double, double> conditionalYGivenX(double x) const {
        auto marginal = marginalX();

        if (marginal[x] <= 0) {
            throw DistributionError(
                "Conditional distribution is undefined."
            );
        }

        map<double, double> result;

        for (const auto& [outcome, probability] : pmf) {
            if (outcome.first == x) {
                result[outcome.second] += probability / marginal[x];
            }
        }

        return result;
    }

    map<double, double> conditionalXGivenY(double y) const {
        auto marginal = marginalY();

        if (marginal[y] <= 0) {
            throw DistributionError(
                "Conditional distribution is undefined."
            );
        }

        map<double, double> result;

        for (const auto& [outcome, probability] : pmf) {
            if (outcome.second == y) {
                result[outcome.first] += probability / marginal[y];
            }
        }

        return result;
    }

    static double expectation(const map<double, double>& distribution) {
        double result = 0.0;

        for (const auto& [value, probability] : distribution) {
            result += value * probability;
        }

        return result;
    }

    static double variance(const map<double, double>& distribution) {
        double mean = expectation(distribution);
        double result = 0.0;

        for (const auto& [value, probability] : distribution) {
            result += probability * pow(value - mean, 2);
        }

        return result;
    }

    double expectedX() const {
        return expectation(marginalX());
    }

    double expectedY() const {
        return expectation(marginalY());
    }

    double varianceX() const {
        return variance(marginalX());
    }

    double varianceY() const {
        return variance(marginalY());
    }

    double expectedXY() const {
        double result = 0.0;

        for (const auto& [outcome, probability] : pmf) {
            result += outcome.first * outcome.second * probability;
        }

        return result;
    }

    double covariance() const {
        return expectedXY() - expectedX() * expectedY();
    }

    double correlation() const {
        double denominator = sqrt(varianceX() * varianceY());

        if (denominator <= 0) {
            throw DistributionError(
                "Correlation undefined for zero variance."
            );
        }

        return covariance() / denominator;
    }

    bool independent(double epsilon = 1e-9) const {
        auto mx = marginalX();
        auto my = marginalY();

        for (const auto& [x, px] : mx) {
            for (const auto& [y, py] : my) {
                double actual = jointProbability(x, y);
                double expected = px * py;

                if (abs(actual - expected) > epsilon) {
                    return false;
                }
            }
        }

        return true;
    }

    void printMarginal(
        const string& name,
        const map<double, double>& distribution
    ) const {
        cout << name << '\n';

        for (const auto& [value, probability] : distribution) {
            cout << "  " << value
                 << " : " << probability << '\n';
        }
    }

    void report() const {
        cout << "\nJoint PMF\n";

        for (const auto& [outcome, probability] : pmf) {
            cout << "P(X=" << outcome.first
                 << ", Y=" << outcome.second
                 << ") = " << probability << '\n';
        }

        cout << '\n';

        printMarginal("Marginal X", marginalX());
        printMarginal("Marginal Y", marginalY());

        cout << "\nConditional P(Y | X=1)\n";

        for (const auto& [value, probability] :
             conditionalYGivenX(1)) {
            cout << "P(Y=" << value << " | X=1) = "
                 << probability << '\n';
        }

        cout << "\nStatistical Measures\n";

        cout << "E[X]       = " << expectedX() << '\n';
        cout << "E[Y]       = " << expectedY() << '\n';
        cout << "Var(X)     = " << varianceX() << '\n';
        cout << "Var(Y)     = " << varianceY() << '\n';
        cout << "E[XY]      = " << expectedXY() << '\n';
        cout << "Cov(X,Y)   = " << covariance() << '\n';
        cout << "Correlation= " << correlation() << '\n';
        cout << "Independent= "
             << boolalpha << independent() << '\n';
    }
};

class BivariateNormal {
private:
    double meanX;
    double meanY;
    double sigmaX;
    double sigmaY;
    double rho;

public:
    BivariateNormal(
        double meanX,
        double meanY,
        double sigmaX,
        double sigmaY,
        double rho
    ) : meanX(meanX),
        meanY(meanY),
        sigmaX(sigmaX),
        sigmaY(sigmaY),
        rho(rho) {

        if (
            !isfinite(meanX) ||
            !isfinite(meanY) ||
            !isfinite(sigmaX) ||
            !isfinite(sigmaY) ||
            !isfinite(rho)
        ) {
            throw DistributionError(
                "Parameters must be finite."
            );
        }

        if (sigmaX <= 0 || sigmaY <= 0) {
            throw DistributionError(
                "Standard deviations must be positive."
            );
        }

        if (rho <= -1 || rho >= 1) {
            throw DistributionError(
                "Correlation must be strictly between -1 and 1."
            );
        }
    }

    double pdf(double x, double y) const {
        if (!isfinite(x) || !isfinite(y)) {
            throw DistributionError("Invalid PDF input.");
        }

        double zx = (x - meanX) / sigmaX;
        double zy = (y - meanY) / sigmaY;

        double exponent = -(
            zx * zx - 2 * rho * zx * zy + zy * zy
        ) / (2 * (1 - rho * rho));

        const double PI = acos(-1.0);

        double denominator =
            2 * PI * sigmaX * sigmaY *
            sqrt(1 - rho * rho);

        return exp(exponent) / denominator;
    }

    double marginalXPDF(double x) const {
        const double PI = acos(-1.0);

        double z = (x - meanX) / sigmaX;

        return exp(-0.5 * z * z) /
            (sigmaX * sqrt(2 * PI));
    }

    double marginalYPDF(double y) const {
        const double PI = acos(-1.0);

        double z = (y - meanY) / sigmaY;

        return exp(-0.5 * z * z) /
            (sigmaY * sqrt(2 * PI));
    }

    double covariance() const {
        return rho * sigmaX * sigmaY;
    }

    double correlation() const {
        return rho;
    }
};

void runTests() {
    JointDistribution independent({
        {0, 0, 0.25},
        {0, 1, 0.25},
        {1, 0, 0.25},
        {1, 1, 0.25}
    });

    if (abs(independent.expectedX() - 0.5) > 1e-10) {
        throw runtime_error("Expected X test failed.");
    }

    if (abs(independent.varianceX() - 0.25) > 1e-10) {
        throw runtime_error("Variance test failed.");
    }

    if (abs(independent.covariance()) > 1e-10) {
        throw runtime_error("Covariance test failed.");
    }

    if (!independent.independent()) {
        throw runtime_error("Independence test failed.");
    }

    JointDistribution dependent({
        {0, 0, 0.5},
        {1, 1, 0.5}
    });

    if (dependent.independent()) {
        throw runtime_error("Dependence test failed.");
    }

    if (abs(dependent.correlation() - 1.0) > 1e-10) {
        throw runtime_error("Correlation test failed.");
    }

    try {
        JointDistribution invalid({
            {0, 0, 0.4},
            {1, 1, 0.4}
        });

        throw runtime_error("Invalid PMF was accepted.");
    } catch (const DistributionError&) {
        // Expected validation failure.
    }

    try {
        independent.conditionalYGivenX(5);

        throw runtime_error(
            "Undefined conditional distribution was accepted."
        );
    } catch (const DistributionError&) {
        // Expected validation failure.
    }

    cout << "\nAll C++17 tests passed.\n";
}

int main() {
    try {
        cout << fixed << setprecision(6);

        cout << "JOINT DISTRIBUTION ANALYSIS\n";
        cout << "===========================\n";

        // Employee training level and assessment outcome.
        JointDistribution distribution({
            {0, 0, 0.10},
            {0, 1, 0.15},
            {1, 0, 0.20},
            {1, 1, 0.30},
            {2, 0, 0.05},
            {2, 1, 0.20}
        });

        distribution.report();

        BivariateNormal continuous(
            70.0,
            75.0,
            10.0,
            12.0,
            0.65
        );

        cout << "\nBivariate Normal Distribution\n";

        cout << "Joint PDF at (70,75): "
             << continuous.pdf(70, 75) << '\n';

        cout << "Marginal X PDF at 70: "
             << continuous.marginalXPDF(70) << '\n';

        cout << "Marginal Y PDF at 75: "
             << continuous.marginalYPDF(75) << '\n';

        cout << "Covariance: "
             << continuous.covariance() << '\n';

        cout << "Correlation: "
             << continuous.correlation() << '\n';

        runTests();

    } catch (const exception& error) {
        cerr << "[ERROR] " << error.what() << '\n';
        return 1;
    }

    return 0;
}
