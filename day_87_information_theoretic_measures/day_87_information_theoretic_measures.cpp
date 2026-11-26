#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>
#include <limits>

using namespace std;

constexpr double EPSILON = 1e-12;

class InformationTheoryError : public runtime_error {
public:
    explicit InformationTheoryError(const string& message)
        : runtime_error(message) {}
};

class Dataset {
private:
    vector<string> target_;
    map<string, vector<string>> features_;

public:
    Dataset(
        vector<string> target,
        map<string, vector<string>> features
    )
        : target_(move(target)),
          features_(move(features)) {

        if (target_.empty()) {
            throw InformationTheoryError(
                "Target dataset cannot be empty."
            );
        }

        if (features_.empty()) {
            throw InformationTheoryError(
                "At least one feature is required."
            );
        }

        for (const auto& [name, values] : features_) {
            if (name.empty()) {
                throw InformationTheoryError(
                    "Feature name cannot be empty."
                );
            }

            if (values.size() != target_.size()) {
                throw InformationTheoryError(
                    "Feature and target dimensions do not match."
                );
            }
        }
    }

    const vector<string>& target() const {
        return target_;
    }

    const map<string, vector<string>>& features() const {
        return features_;
    }
};

class InformationMetrics {
public:

    template <typename T>
    static double entropy(
        const vector<T>& values,
        double base = 2.0
    ) {

        if (values.empty()) {
            throw InformationTheoryError(
                "Entropy requires observations."
            );
        }

        if (
            !isfinite(base) ||
            base <= 0 ||
            abs(base - 1.0) < EPSILON
        ) {
            throw InformationTheoryError(
                "Invalid logarithm base."
            );
        }

        map<T, size_t> counts;

        for (const auto& value : values) {
            ++counts[value];
        }

        const double total =
            static_cast<double>(values.size());

        double result = 0.0;

        for (const auto& [value, count] : counts) {
            const double probability = count / total;

            if (probability > 0) {
                result -= probability *
                    log(probability) / log(base);
            }
        }

        return result;
    }

    template <typename X, typename Y>
    static double conditionalEntropy(
        const vector<Y>& target,
        const vector<X>& condition
    ) {

        validateDimensions(target, condition);

        map<X, vector<Y>> groups;

        for (size_t i = 0; i < target.size(); ++i) {
            groups[condition[i]].push_back(target[i]);
        }

        double result = 0.0;
        const double total =
            static_cast<double>(target.size());

        for (const auto& [key, group] : groups) {
            const double weight = group.size() / total;

            result += weight * entropy(group);
        }

        return result;
    }

    template <typename X, typename Y>
    static double mutualInformation(
        const vector<X>& x,
        const vector<Y>& y
    ) {

        validateDimensions(x, y);

        const double result =
            entropy(y) - conditionalEntropy(y, x);

        return max(0.0, result);
    }

    template <typename X, typename Y>
    static double informationGain(
        const vector<Y>& target,
        const vector<X>& feature
    ) {

        return mutualInformation(feature, target);
    }

    template <typename X, typename Y>
    static double normalizedMutualInformation(
        const vector<X>& x,
        const vector<Y>& y
    ) {

        validateDimensions(x, y);

        const double hx = entropy(x);
        const double hy = entropy(y);
        const double denominator = hx + hy;

        if (denominator <= EPSILON) {
            return 1.0;
        }

        return 2.0 * mutualInformation(x, y) /
            denominator;
    }

    template <typename X, typename Y>
    static double jointEntropy(
        const vector<X>& x,
        const vector<Y>& y
    ) {

        validateDimensions(x, y);

        map<pair<X, Y>, size_t> counts;

        for (size_t i = 0; i < x.size(); ++i) {
            ++counts[{x[i], y[i]}];
        }

        double result = 0.0;
        const double total = x.size();

        for (const auto& [pair, count] : counts) {
            const double p = count / total;
            result -= p * log2(p);
        }

        return result;
    }

private:

    template <typename X, typename Y>
    static void validateDimensions(
        const vector<X>& x,
        const vector<Y>& y
    ) {

        if (x.empty() || y.empty()) {
            throw InformationTheoryError(
                "Input vectors cannot be empty."
            );
        }

        if (x.size() != y.size()) {
            throw InformationTheoryError(
                "Input vectors must have equal lengths."
            );
        }
    }
};

struct FeatureEvaluation {
    string name;
    double targetEntropy;
    double conditionalEntropy;
    double mutualInformation;
    double informationGain;
    double normalizedMutualInformation;
};

class GovernanceEngine {
private:
    Dataset dataset_;

public:

    explicit GovernanceEngine(Dataset dataset)
        : dataset_(move(dataset)) {}

    FeatureEvaluation evaluate(
        const string& featureName
    ) const {

        auto iterator =
            dataset_.features().find(featureName);

        if (iterator == dataset_.features().end()) {
            throw InformationTheoryError(
                "Feature not found: " + featureName
            );
        }

        const auto& target = dataset_.target();
        const auto& feature = iterator->second;

        const double hy =
            InformationMetrics::entropy(target);

        const double hygx =
            InformationMetrics::conditionalEntropy(
                target,
                feature
            );

        const double mi =
            InformationMetrics::mutualInformation(
                feature,
                target
            );

        return {
            featureName,
            hy,
            hygx,
            mi,
            max(0.0, hy - hygx),
            InformationMetrics::normalizedMutualInformation(
                feature,
                target
            )
        };
    }

    vector<FeatureEvaluation> rankFeatures() const {

        vector<FeatureEvaluation> results;

        for (const auto& [name, values] :
             dataset_.features()) {

            results.push_back(evaluate(name));
        }

        sort(
            results.begin(),
            results.end(),
            [](const auto& a, const auto& b) {

                if (
                    abs(a.informationGain - b.informationGain)
                    > EPSILON
                ) {
                    return a.informationGain >
                        b.informationGain;
                }

                return a.name < b.name;
            }
        );

        return results;
    }

    vector<string> selectFeatures(
        double minimumGain
    ) const {

        if (
            !isfinite(minimumGain) ||
            minimumGain < 0
        ) {
            throw InformationTheoryError(
                "Minimum gain must be non-negative."
            );
        }

        vector<string> selected;

        for (const auto& result : rankFeatures()) {
            if (result.informationGain >= minimumGain) {
                selected.push_back(result.name);
            }
        }

        return selected;
    }

    void printReport() const {

        const auto results = rankFeatures();

        cout << "\nINFORMATION-THEORETIC ANALYSIS\n";
        cout << string(88, '=') << '\n';

        cout << left
             << setw(20) << "Feature"
             << right
             << setw(13) << "H(Y)"
             << setw(13) << "H(Y|X)"
             << setw(13) << "MI"
             << setw(13) << "IG"
             << setw(13) << "NMI"
             << '\n';

        cout << string(88, '-') << '\n';

        for (const auto& result : results) {

            cout << left
                 << setw(20) << result.name
                 << right
                 << fixed << setprecision(5)
                 << setw(13) << result.targetEntropy
                 << setw(13) << result.conditionalEntropy
                 << setw(13) << result.mutualInformation
                 << setw(13) << result.informationGain
                 << setw(13) << result.normalizedMutualInformation
                 << '\n';
        }

        if (!results.empty()) {
            cout << "\nBest feature: "
                 << results.front().name << '\n';
        }
    }
};

void runTests() {

    vector<string> fairCoin = {
        "H", "T", "H", "T"
    };

    if (
        abs(InformationMetrics::entropy(fairCoin) - 1.0)
        > EPSILON
    ) {
        throw InformationTheoryError(
            "Fair coin entropy test failed."
        );
    }

    vector<int> x = {0, 0, 1, 1};
    vector<int> y = {0, 0, 1, 1};

    if (
        abs(InformationMetrics::mutualInformation(x, y) - 1.0)
        > EPSILON
    ) {
        throw InformationTheoryError(
            "Mutual information test failed."
        );
    }

    if (
        abs(InformationMetrics::conditionalEntropy(y, x))
        > EPSILON
    ) {
        throw InformationTheoryError(
            "Conditional entropy test failed."
        );
    }

    vector<int> independent = {0, 1, 0, 1};

    if (
        abs(InformationMetrics::mutualInformation(
            x,
            independent
        )) > EPSILON
    ) {
        throw InformationTheoryError(
            "Independence test failed."
        );
    }

    if (
        abs(InformationMetrics::jointEntropy(x, y) - 1.0)
        > EPSILON
    ) {
        throw InformationTheoryError(
            "Joint entropy test failed."
        );
    }

    bool rejected = false;

    try {
        InformationMetrics::entropy(
            vector<int>{}
        );
    } catch (const InformationTheoryError&) {
        rejected = true;
    }

    if (!rejected) {
        throw InformationTheoryError(
            "Empty dataset validation failed."
        );
    }

    cout << "All mathematical tests passed.\n";
}

int main() {

    try {

        runTests();

        vector<string> target = {
            "No", "No", "Yes", "Yes",
            "Yes", "No", "Yes", "No",
            "Yes", "Yes", "Yes", "Yes",
            "Yes", "No"
        };

        map<string, vector<string>> features = {

            {
                "Outlook",
                {
                    "Sunny", "Sunny", "Overcast", "Rain",
                    "Rain", "Rain", "Overcast", "Sunny",
                    "Sunny", "Rain", "Sunny", "Overcast",
                    "Overcast", "Rain"
                }
            },

            {
                "Temperature",
                {
                    "Hot", "Hot", "Hot", "Mild",
                    "Cool", "Cool", "Cool", "Mild",
                    "Cool", "Mild", "Mild", "Mild",
                    "Hot", "Mild"
                }
            },

            {
                "Humidity",
                {
                    "High", "High", "High", "High",
                    "Normal", "Normal", "Normal", "High",
                    "Normal", "Normal", "Normal", "High",
                    "Normal", "High"
                }
            },

            {
                "Wind",
                {
                    "Weak", "Strong", "Weak", "Weak",
                    "Weak", "Strong", "Strong", "Weak",
                    "Weak", "Weak", "Strong", "Strong",
                    "Weak", "Strong"
                }
            }
        };

        Dataset dataset(
            move(target),
            move(features)
        );

        GovernanceEngine engine(
            move(dataset)
        );

        engine.printReport();

        cout << "\nSelected features:\n";

        for (const auto& name :
             engine.selectFeatures(0.05)) {

            cout << " - " << name << '\n';
        }

        cout << "\nAnalysis completed successfully.\n";

    } catch (const exception& error) {

        cerr << "Execution error: "
             << error.what() << '\n';

        return 1;
    }

    return 0;
}
