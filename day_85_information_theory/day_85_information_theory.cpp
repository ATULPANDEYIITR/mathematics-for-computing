#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <numeric>
#include <queue>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

/*
 * Information Theory Engine
 *
 * Models probability distributions, information content,
 * uncertainty, dependence and optimal prefix coding.
 *
 * C++17, standard library only.
 */

namespace InformationTheory {

constexpr double EPSILON = 1e-9;

class InformationError : public runtime_error {
public:
    explicit InformationError(const string& message)
        : runtime_error(message) {}
}

;

using Distribution = map<string, double>;

void validateProbability(double probability) {
    if (!isfinite(probability) ||
        probability < 0.0 ||
        probability > 1.0) {
        throw InformationError(
            "Probability must be finite and between 0 and 1."
        );
    }
}

void validateDistribution(const Distribution& distribution) {
    if (distribution.empty()) {
        throw InformationError("Distribution cannot be empty.");
    }

    double total = 0.0;

    for (const auto& [symbol, probability] : distribution) {
        if (symbol.empty()) {
            throw InformationError("Empty outcome identifier.");
        }

        validateProbability(probability);
        total += probability;
    }

    if (abs(total - 1.0) > EPSILON) {
        throw InformationError(
            "Distribution probabilities must sum to 1."
        );
    }
}

double selfInformation(double probability, double base = 2.0) {
    validateProbability(probability);

    if (!isfinite(base) || base <= 0.0 || base == 1.0) {
        throw InformationError("Invalid logarithm base.");
    }

    if (probability == 0.0) {
        return numeric_limits<double>::infinity();
    }

    return -log(probability) / log(base);
}

double entropy(
    const Distribution& distribution,
    double base = 2.0
) {
    validateDistribution(distribution);

    if (!isfinite(base) || base <= 0.0 || base == 1.0) {
        throw InformationError("Invalid logarithm base.");
    }

    double result = 0.0;

    for (const auto& [symbol, probability] : distribution) {
        if (probability > 0.0) {
            result -= probability * log(probability) / log(base);
        }
    }

    return result;
}

double maximumEntropy(size_t outcomes, double base = 2.0) {
    if (outcomes == 0) {
        throw InformationError("Outcome count must be positive.");
    }

    if (!isfinite(base) || base <= 0.0 || base == 1.0) {
        throw InformationError("Invalid logarithm base.");
    }

    return log(static_cast<double>(outcomes)) / log(base);
}

using JointDistribution = map<pair<string, string>, double>;

Distribution marginal(
    const JointDistribution& joint,
    int axis
) {
    if (axis != 0 && axis != 1) {
        throw InformationError("Axis must be 0 or 1.");
    }

    double total = 0.0;

    for (const auto& [pair, probability] : joint) {
        validateProbability(probability);
        total += probability;
    }

    if (joint.empty() || abs(total - 1.0) > EPSILON) {
        throw InformationError("Invalid joint distribution.");
    }

    Distribution result;

    for (const auto& [pair, probability] : joint) {
        const string& symbol = axis == 0 ? pair.first : pair.second;
        result[symbol] += probability;
    }

    return result;
}

double conditionalEntropy(
    const JointDistribution& joint,
    int givenAxis = 1
) {
    Distribution conditioned = marginal(joint, givenAxis);
    double result = 0.0;

    for (const auto& [symbol, groupProbability] : conditioned) {
        Distribution conditional;

        for (const auto& [pair, probability] : joint) {
            const string& group =
                givenAxis == 0 ? pair.first : pair.second;

            if (group == symbol) {
                const string& target =
                    givenAxis == 0 ? pair.second : pair.first;

                conditional[target] += probability / groupProbability;
            }
        }

        result += groupProbability * entropy(conditional);
    }

    return result;
}

double mutualInformation(const JointDistribution& joint) {
    const double hx = entropy(marginal(joint, 0));
    const double hy = entropy(marginal(joint, 1));

    Distribution combined;
    double hxy = 0.0;

    for (const auto& [pair, probability] : joint) {
        if (probability > 0.0) {
            hxy -= probability * log2(probability);
        }
    }

    return max(0.0, hx + hy - hxy);
}

double crossEntropy(
    const Distribution& actual,
    const Distribution& predicted
) {
    validateDistribution(actual);
    validateDistribution(predicted);

    if (actual.size() != predicted.size()) {
        throw InformationError("Outcome sets must match.");
    }

    double result = 0.0;

    for (const auto& [symbol, probability] : actual) {
        auto found = predicted.find(symbol);

        if (found == predicted.end()) {
            throw InformationError("Missing predicted outcome.");
        }

        if (probability == 0.0) {
            continue;
        }

        if (found->second == 0.0) {
            return numeric_limits<double>::infinity();
        }

        result -= probability * log2(found->second);
    }

    return result;
}

double klDivergence(
    const Distribution& actual,
    const Distribution& predicted
) {
    validateDistribution(actual);
    validateDistribution(predicted);

    if (actual.size() != predicted.size()) {
        throw InformationError("Outcome sets must match.");
    }

    double result = 0.0;

    for (const auto& [symbol, probability] : actual) {
        auto found = predicted.find(symbol);

        if (found == predicted.end()) {
            throw InformationError("Missing predicted outcome.");
        }

        if (probability == 0.0) {
            continue;
        }

        if (found->second == 0.0) {
            return numeric_limits<double>::infinity();
        }

        result += probability *
                  log2(probability / found->second);
    }

    return max(0.0, result);
}

struct HuffmanNode {
    double probability;
    string symbol;
    shared_ptr<HuffmanNode> left;
    shared_ptr<HuffmanNode> right;
    size_t order;
};

struct NodeComparator {
    bool operator()(
        const shared_ptr<HuffmanNode>& a,
        const shared_ptr<HuffmanNode>& b
    ) const {
        if (abs(a->probability - b->probability) > EPSILON) {
            return a->probability > b->probability;
        }

        return a->order > b->order;
    }
};

class HuffmanEncoder {
private:
    unordered_map<string, string> codes;

    void generate(
        const shared_ptr<HuffmanNode>& node,
        const string& prefix
    ) {
        if (!node->left && !node->right) {
            codes[node->symbol] = prefix.empty() ? "0" : prefix;
            return;
        }

        if (node->left) {
            generate(node->left, prefix + "0");
        }

        if (node->right) {
            generate(node->right, prefix + "1");
        }
    }

public:
    explicit HuffmanEncoder(const Distribution& distribution) {
        validateDistribution(distribution);

        priority_queue<
            shared_ptr<HuffmanNode>,
            vector<shared_ptr<HuffmanNode>>,
            NodeComparator
        > heap;

        size_t order = 0;

        for (const auto& [symbol, probability] : distribution) {
            heap.push(make_shared<HuffmanNode>(
                HuffmanNode{
                    probability,
                    symbol,
                    nullptr,
                    nullptr,
                    order++
                }
            ));
        }

        while (heap.size() > 1) {
            auto left = heap.top();
            heap.pop();

            auto right = heap.top();
            heap.pop();

            heap.push(make_shared<HuffmanNode>(
                HuffmanNode{
                    left->probability + right->probability,
                    "",
                    left,
                    right,
                    order++
                }
            ));
        }

        generate(heap.top(), "");
    }

    const unordered_map<string, string>& getCodes() const {
        return codes;
    }

    double expectedLength(const Distribution& distribution) const {
        double result = 0.0;

        for (const auto& [symbol, probability] : distribution) {
            auto found = codes.find(symbol);

            if (found == codes.end()) {
                throw InformationError("Missing Huffman code.");
            }

            result += probability * found->second.size();
        }

        return result;
    }

    string encode(const vector<string>& message) const {
        string result;

        for (const string& symbol : message) {
            auto found = codes.find(symbol);

            if (found == codes.end()) {
                throw InformationError("Unknown source symbol.");
            }

            result += found->second;
        }

        return result;
    }
};

class OnlineEntropyEstimator {
private:
    map<string, size_t> counts;
    size_t observations = 0;

public:
    void observe(const string& symbol) {
        if (symbol.empty()) {
            throw InformationError("Observation cannot be empty.");
        }

        ++counts[symbol];
        ++observations;
    }

    size_t size() const {
        return observations;
    }

    Distribution estimate() const {
        if (observations == 0) {
            throw InformationError("No observations available.");
        }

        Distribution result;

        for (const auto& [symbol, count] : counts) {
            result[symbol] =
                static_cast<double>(count) / observations;
        }

        return result;
    }

    double currentEntropy() const {
        return entropy(estimate());
    }

    void reset() {
        counts.clear();
        observations = 0;
    }
};

} // namespace InformationTheory

int main() {
    using namespace InformationTheory;

    cout << fixed << setprecision(4);

    try {
        cout << "INFORMATION THEORY ENGINE\n";
        cout << string(60, '=') << "\n";

        Distribution source = {
            {"A", 0.50},
            {"B", 0.25},
            {"C", 0.125},
            {"D", 0.125}
        };

        cout << "\n1. SELF-INFORMATION\n";

        for (const auto& [symbol, probability] : source) {
            cout << symbol << ": "
                 << selfInformation(probability)
                 << " bits\n";
        }

        cout << "\n2. SHANNON ENTROPY\n";
        cout << "Entropy: " << entropy(source) << " bits\n";
        cout << "Maximum entropy: "
             << maximumEntropy(source.size()) << " bits\n";

        cout << "\n3. JOINT AND CONDITIONAL ENTROPY\n";

        JointDistribution joint = {
            {{"Sunny", "Hot"}, 0.30},
            {{"Sunny", "Cold"}, 0.20},
            {{"Rainy", "Hot"}, 0.10},
            {{"Rainy", "Cold"}, 0.40}
        };

        double hx = entropy(marginal(joint, 0));
        double hy = entropy(marginal(joint, 1));

        cout << "H(X): " << hx << "\n";
        cout << "H(Y): " << hy << "\n";
        cout << "H(X|Y): " << conditionalEntropy(joint, 1) << "\n";
        cout << "H(Y|X): " << conditionalEntropy(joint, 0) << "\n";
        cout << "I(X;Y): " << mutualInformation(joint) << "\n";

        cout << "\n4. DISTRIBUTION COMPARISON\n";

        Distribution actual = {
            {"A", 0.50},
            {"B", 0.30},
            {"C", 0.20}
        };

        Distribution predicted = {
            {"A", 0.40},
            {"B", 0.40},
            {"C", 0.20}
        };

        cout << "Cross-entropy: "
             << crossEntropy(actual, predicted) << "\n";

        cout << "KL divergence: "
             << klDivergence(actual, predicted) << "\n";

        cout << "\n5. HUFFMAN SOURCE CODING\n";

        HuffmanEncoder encoder(source);

        for (const auto& [symbol, code] : encoder.getCodes()) {
            cout << symbol << ": " << code << "\n";
        }

        cout << "Expected code length: "
             << encoder.expectedLength(source) << " bits\n";

        vector<string> message = {"A", "B", "C", "D", "A"};

        cout << "Encoded message: "
             << encoder.encode(message) << "\n";

        cout << "\n6. ONLINE ENTROPY ESTIMATION\n";

        OnlineEntropyEstimator estimator;

        vector<string> observations = {
            "success", "success", "failure",
            "success", "failure", "success"
        };

        for (const string& observation : observations) {
            estimator.observe(observation);
        }

        cout << "Observation count: " << estimator.size() << "\n";
        cout << "Estimated entropy: "
             << estimator.currentEntropy() << " bits\n";

        cout << "\n7. EDGE CASES\n";
        cout << "Certain event: "
             << selfInformation(1.0) << " bits\n";

        cout << "Impossible event: "
             << selfInformation(0.0) << "\n";

        cout << "Deterministic entropy: "
             << entropy({{"fixed", 1.0}}) << "\n";

        cout << "\n8. MATHEMATICAL VALIDATION\n";

        if (abs(entropy(source) - 1.75) > EPSILON) {
            throw InformationError("Entropy test failed.");
        }

        if (klDivergence(actual, actual) > EPSILON) {
            throw InformationError("KL divergence test failed.");
        }

        if (mutualInformation(joint) > min(hx, hy) + EPSILON) {
            throw InformationError("Mutual information bound failed.");
        }

        if (encoder.expectedLength(source) + EPSILON < entropy(source)) {
            throw InformationError("Source coding bound failed.");
        }

        cout << "All mathematical invariants passed.\n";

        cout << "\n9. INVALID INPUT HANDLING\n";

        try {
            validateDistribution({{"A", 0.7}, {"B", 0.7}});
        } catch (const InformationError& error) {
            cout << "Correctly rejected input: "
                 << error.what() << "\n";
        }

    } catch (const exception& error) {
        cerr << "Fatal error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
