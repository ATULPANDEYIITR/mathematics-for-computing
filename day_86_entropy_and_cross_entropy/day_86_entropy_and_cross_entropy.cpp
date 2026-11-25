#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace std;

/*
 * Entropy and Cross-Entropy Computation Engine
 *
 * C++17 implementation featuring:
 * - Domain-specific probability distributions
 * - Shannon entropy
 * - Cross-entropy
 * - KL divergence
 * - Joint and conditional entropy
 * - Mutual information
 * - Probability smoothing
 * - Classification loss
 * - Validation and numerical safeguards
 */

constexpr double EPSILON = 1e-10;

class ProbabilityError : public runtime_error {
public:
    explicit ProbabilityError(const string& message)
        : runtime_error(message) {}
};

class Distribution {
private:
    string name;
    vector<double> probabilities;

public:
    Distribution(
        string distributionName,
        vector<double> values
    ) : name(move(distributionName)),
        probabilities(move(values)) {

        if (name.empty()) {
            throw ProbabilityError(
                "Distribution name cannot be empty."
            );
        }

        if (probabilities.empty()) {
            throw ProbabilityError(
                "Distribution cannot be empty."
            );
        }

        double total = 0.0;

        for (double p : probabilities) {
            if (!isfinite(p) || p < 0.0 || p > 1.0) {
                throw ProbabilityError(
                    "Invalid probability encountered."
                );
            }

            total += p;
        }

        if (abs(total - 1.0) > EPSILON) {
            throw ProbabilityError(
                "Probabilities must sum to one."
            );
        }
    }

    const string& getName() const {
        return name;
    }

    const vector<double>& values() const {
        return probabilities;
    }

    size_t size() const {
        return probabilities.size();
    }
};

void validateCompatible(
    const Distribution& p,
    const Distribution& q
) {
    if (p.size() != q.size()) {
        throw ProbabilityError(
            "Distribution dimensions do not match."
        );
    }
}

double entropy(const Distribution& distribution) {
    double result = 0.0;

    for (double p : distribution.values()) {
        if (p > 0.0) {
            result -= p * log2(p);
        }
    }

    return result;
}

double crossEntropy(
    const Distribution& actual,
    const Distribution& predicted
) {
    validateCompatible(actual, predicted);

    double result = 0.0;

    for (size_t i = 0; i < actual.size(); ++i) {
        double p = actual.values()[i];
        double q = predicted.values()[i];

        if (p == 0.0) continue;

        if (q == 0.0) {
            return numeric_limits<double>::infinity();
        }

        result -= p * log2(q);
    }

    return result;
}

double klDivergence(
    const Distribution& actual,
    const Distribution& predicted
) {
    validateCompatible(actual, predicted);

    double result = 0.0;

    for (size_t i = 0; i < actual.size(); ++i) {
        double p = actual.values()[i];
        double q = predicted.values()[i];

        if (p == 0.0) continue;

        if (q == 0.0) {
            return numeric_limits<double>::infinity();
        }

        result += p * log2(p / q);
    }

    return max(0.0, result);
}

double binaryEntropy(double p) {
    if (!isfinite(p) || p < 0.0 || p > 1.0) {
        throw ProbabilityError(
            "Binary probability must belong to [0,1]."
        );
    }

    if (p == 0.0 || p == 1.0) {
        return 0.0;
    }

    return -p * log2(p) -
        (1.0 - p) * log2(1.0 - p);
}

Distribution smooth(
    const Distribution& distribution,
    double alpha
) {
    if (!isfinite(alpha) || alpha <= 0.0) {
        throw ProbabilityError(
            "Alpha must be positive and finite."
        );
    }

    vector<double> result;
    double denominator =
        1.0 + distribution.size() * alpha;

    for (double p : distribution.values()) {
        result.push_back(
            (p + alpha) / denominator
        );
    }

    return Distribution(
        distribution.getName() + "_smoothed",
        result
    );
}

class JointDistribution {
private:
    vector<vector<double>> matrix;
    vector<double> marginalX;
    vector<double> marginalY;

    void validate() {
        if (matrix.empty() || matrix[0].empty()) {
            throw ProbabilityError(
                "Joint matrix cannot be empty."
            );
        }

        size_t columns = matrix[0].size();

        marginalX.assign(matrix.size(), 0.0);
        marginalY.assign(columns, 0.0);

        double total = 0.0;

        for (size_t i = 0; i < matrix.size(); ++i) {
            if (matrix[i].size() != columns) {
                throw ProbabilityError(
                    "Joint matrix must be rectangular."
                );
            }

            for (size_t j = 0; j < columns; ++j) {
                double p = matrix[i][j];

                if (!isfinite(p) || p < 0.0 || p > 1.0) {
                    throw ProbabilityError(
                        "Invalid joint probability."
                    );
                }

                marginalX[i] += p;
                marginalY[j] += p;
                total += p;
            }
        }

        if (abs(total - 1.0) > EPSILON) {
            throw ProbabilityError(
                "Joint probabilities must sum to one."
            );
        }
    }

public:
    explicit JointDistribution(
        vector<vector<double>> values
    ) : matrix(move(values)) {
        validate();
    }

    double jointEntropy() const {
        double result = 0.0;

        for (const auto& row : matrix) {
            for (double p : row) {
                if (p > 0.0) {
                    result -= p * log2(p);
                }
            }
        }

        return result;
    }

    double entropyX() const {
        Distribution d("X", marginalX);
        return entropy(d);
    }

    double entropyY() const {
        Distribution d("Y", marginalY);
        return entropy(d);
    }

    double conditionalYGivenX() const {
        return max(
            0.0,
            jointEntropy() - entropyX()
        );
    }

    double mutualInformation() const {
        return max(
            0.0,
            entropyX() + entropyY() - jointEntropy()
        );
    }
};

double classificationLoss(
    size_t actualClass,
    const Distribution& predicted
) {
    if (actualClass >= predicted.size()) {
        throw ProbabilityError(
            "Actual class index is out of range."
        );
    }

    double probability =
        predicted.values()[actualClass];

    if (probability == 0.0) {
        return numeric_limits<double>::infinity();
    }

    return -log2(probability);
}

struct Evaluation {
    double entropy;
    double crossEntropy;
    double divergence;

    bool identityVerified() const {
        if (!isfinite(crossEntropy) ||
            !isfinite(divergence)) {
            return false;
        }

        return abs(
            crossEntropy - entropy - divergence
        ) < 1e-8;
    }
};

class EntropyEngine {
public:
    Evaluation evaluate(
        const Distribution& actual,
        const Distribution& predicted
    ) const {
        return {
            entropy(actual),
            crossEntropy(actual, predicted),
            klDivergence(actual, predicted)
        };
    }
};

void runTests(const EntropyEngine& engine) {
    Distribution uniform("uniform", {0.5, 0.5});

    if (abs(entropy(uniform) - 1.0) > EPSILON) {
        throw runtime_error("Uniform entropy test failed.");
    }

    if (abs(binaryEntropy(0.5) - 1.0) > EPSILON) {
        throw runtime_error("Binary entropy test failed.");
    }

    Distribution p("p", {0.5, 0.3, 0.2});
    Distribution q("q", {0.4, 0.4, 0.2});

    Evaluation result = engine.evaluate(p, q);

    if (!result.identityVerified()) {
        throw runtime_error(
            "Cross-entropy identity test failed."
        );
    }

    if (klDivergence(p, p) > EPSILON) {
        throw runtime_error(
            "KL identity test failed."
        );
    }

    if (klDivergence(p, q) < 0.0) {
        throw runtime_error(
            "KL non-negativity test failed."
        );
    }

    JointDistribution joint({
        {0.4, 0.1},
        {0.1, 0.4}
    });

    if (joint.mutualInformation() <= 0.0) {
        throw runtime_error(
            "Mutual information test failed."
        );
    }

    Distribution sparse("sparse", {1.0, 0.0});
    Distribution smoothed = smooth(sparse, 0.1);

    if (smoothed.values()[1] <= 0.0) {
        throw runtime_error("Smoothing test failed.");
    }

    cout << "All tests passed.\n";
}

int main() {
    try {
        cout << fixed << setprecision(6);

        EntropyEngine engine;

        Distribution actual(
            "observed_distribution",
            {0.50, 0.30, 0.20}
        );

        Distribution predicted(
            "predicted_distribution",
            {0.40, 0.40, 0.20}
        );

        Evaluation result =
            engine.evaluate(actual, predicted);

        cout << "ENTROPY AND CROSS-ENTROPY ENGINE\n";
        cout << string(55, '=') << "\n";

        cout << "Shannon entropy: "
             << result.entropy << " bits\n";

        cout << "Cross-entropy: "
             << result.crossEntropy << " bits\n";

        cout << "KL divergence: "
             << result.divergence << " bits\n";

        cout << "Identity H(P,Q)=H(P)+KL: "
             << boolalpha
             << result.identityVerified() << "\n";

        cout << "\nBINARY ENTROPY\n";

        for (double p : {
            0.0, 0.1, 0.25, 0.5, 0.75, 1.0
        }) {
            cout << "p=" << p
                 << " H(X)="
                 << binaryEntropy(p)
                 << " bits\n";
        }

        cout << "\nJOINT DISTRIBUTION ANALYSIS\n";

        JointDistribution joint({
            {0.4, 0.1},
            {0.1, 0.4}
        });

        cout << "H(X,Y): "
             << joint.jointEntropy() << "\n";

        cout << "H(X): "
             << joint.entropyX() << "\n";

        cout << "H(Y): "
             << joint.entropyY() << "\n";

        cout << "H(Y|X): "
             << joint.conditionalYGivenX() << "\n";

        cout << "I(X;Y): "
             << joint.mutualInformation() << "\n";

        cout << "\nCLASSIFICATION LOSS\n";

        Distribution prediction(
            "classifier",
            {0.15, 0.70, 0.15}
        );

        cout << "Negative log-likelihood: "
             << classificationLoss(1, prediction)
             << " bits\n";

        cout << "\nPROBABILITY SMOOTHING\n";

        Distribution sparse(
            "sparse",
            {1.0, 0.0, 0.0}
        );

        Distribution smoothed = smooth(sparse, 0.1);

        for (double p : smoothed.values()) {
            cout << p << " ";
        }

        cout << "\n\nVALIDATION\n";

        runTests(engine);

        cout << "Execution completed successfully.\n";

    } catch (const exception& error) {
        cerr << "Execution error: "
             << error.what() << "\n";

        return 1;
    }

    return 0;
}
