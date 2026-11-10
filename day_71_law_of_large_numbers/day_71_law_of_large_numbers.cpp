#include <algorithm>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <random>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

/*
 * Law of Large Numbers: Repository-independent statistical engine.
 *
 * C++17 implementation of:
 * - Weak Law of Large Numbers.
 * - Strong Law of Large Numbers.
 * - Monte Carlo probability estimation.
 * - Chebyshev inequality.
 * - Distribution modeling.
 * - Repeated independent experiments.
 * - Running mean and variance.
 * - Merge eligibility-style validation of statistical reports.
 *
 * No external dependencies.
 */

enum class DistributionType {
    Bernoulli,
    Uniform,
    Normal
};

struct DistributionSpec {
    string name;
    double mean;
    double variance;
    DistributionType type;
};

struct ExperimentConfig {
    vector<size_t> sampleSizes{
        10, 50, 100, 500, 1000, 5000, 10000
    };

    size_t trials = 1000;
    double epsilon = 0.05;
    uint64_t seed = 42;
};

struct Result {
    size_t sampleSize;
    size_t trials;
    double meanAbsoluteError;
    double meanSquaredError;
    double observedProbability;
    double chebyshevBound;
};

class OnlineStatistics {
private:
    size_t count_ = 0;
    double mean_ = 0.0;
    double m2_ = 0.0;

public:
    void add(double value) {
        if (!isfinite(value)) {
            throw invalid_argument("Observation must be finite.");
        }

        ++count_;

        const double delta = value - mean_;
        mean_ += delta / static_cast<double>(count_);
        const double delta2 = value - mean_;

        m2_ += delta * delta2;
    }

    size_t count() const {
        return count_;
    }

    double mean() const {
        if (count_ == 0) {
            throw logic_error("No observations available.");
        }
        return mean_;
    }

    double variance() const {
        return count_ > 1
            ? m2_ / static_cast<double>(count_ - 1)
            : 0.0;
    }
};

class StatisticalEngine {
private:
    mt19937_64 generator_;
    uniform_real_distribution<double> uniform_{0.0, 1.0};
    normal_distribution<double> normal_{0.0, 1.0};

    double draw(const DistributionSpec& spec) {
        switch (spec.type) {
            case DistributionType::Bernoulli:
                return uniform_(generator_) < 0.5 ? 1.0 : 0.0;

            case DistributionType::Uniform:
                return uniform_(generator_);

            case DistributionType::Normal:
                return normal_(generator_);
        }

        throw logic_error("Unknown distribution type.");
    }

    static double chebyshevBound(
        double variance,
        size_t n,
        double epsilon
    ) {
        return min(
            1.0,
            variance /
            (static_cast<double>(n) * epsilon * epsilon)
        );
    }

public:
    explicit StatisticalEngine(uint64_t seed)
        : generator_(seed) {}

    vector<Result> runWeakLaw(
        const DistributionSpec& spec,
        const ExperimentConfig& config
    ) {
        vector<Result> results;

        for (size_t n : config.sampleSizes) {
            OnlineStatistics absoluteErrors;
            OnlineStatistics squaredErrors;
            size_t deviations = 0;

            for (size_t trial = 0; trial < config.trials; ++trial) {
                double sum = 0.0;

                for (size_t i = 0; i < n; ++i) {
                    sum += draw(spec);
                }

                const double error = abs(
                    sum / static_cast<double>(n) - spec.mean
                );

                absoluteErrors.add(error);
                squaredErrors.add(error * error);

                if (error >= config.epsilon) {
                    ++deviations;
                }
            }

            results.push_back({
                n,
                config.trials,
                absoluteErrors.mean(),
                squaredErrors.mean(),
                static_cast<double>(deviations) /
                    static_cast<double>(config.trials),
                chebyshevBound(spec.variance, n, config.epsilon)
            });
        }

        return results;
    }

    vector<pair<size_t, double>> runStrongLaw(
        const DistributionSpec& spec,
        const vector<size_t>& checkpoints
    ) {
        if (checkpoints.empty()) {
            throw invalid_argument("Checkpoints cannot be empty.");
        }

        set<size_t> selected(
            checkpoints.begin(),
            checkpoints.end()
        );

        if (selected.size() != checkpoints.size() ||
            *selected.begin() == 0) {
            throw invalid_argument(
                "Checkpoints must be unique and positive."
            );
        }

        const size_t maximum = *selected.rbegin();

        vector<pair<size_t, double>> results;
        double sum = 0.0;

        for (size_t n = 1; n <= maximum; ++n) {
            sum += draw(spec);

            if (selected.count(n)) {
                results.emplace_back(
                    n,
                    sum / static_cast<double>(n)
                );
            }
        }

        return results;
    }
};

void validate(const ExperimentConfig& config) {
    if (config.sampleSizes.empty()) {
        throw invalid_argument("Sample sizes cannot be empty.");
    }

    if (!is_sorted(
        config.sampleSizes.begin(),
        config.sampleSizes.end()
    )) {
        throw invalid_argument("Sample sizes must be increasing.");
    }

    if (adjacent_find(
        config.sampleSizes.begin(),
        config.sampleSizes.end()
    ) != config.sampleSizes.end()) {
        throw invalid_argument("Sample sizes must be unique.");
    }

    if (config.sampleSizes.front() == 0) {
        throw invalid_argument("Sample sizes must be positive.");
    }

    if (config.trials == 0) {
        throw invalid_argument("Trials must be positive.");
    }

    if (!isfinite(config.epsilon) || config.epsilon <= 0.0) {
        throw invalid_argument("Tolerance must be positive and finite.");
    }
}

void printResults(
    const DistributionSpec& spec,
    const vector<Result>& results
) {
    cout << "\nWEAK LAW OF LARGE NUMBERS\n";
    cout << "Distribution: " << spec.name << '\n';
    cout << "Population mean: " << spec.mean << '\n';

    cout << left
         << setw(10) << "N"
         << setw(15) << "MAE"
         << setw(18) << "Observed P"
         << setw(18) << "Chebyshev"
         << setw(15) << "MSE"
         << '\n';

    for (const auto& r : results) {
        cout << left
             << setw(10) << r.sampleSize
             << setw(15) << r.meanAbsoluteError
             << setw(18) << r.observedProbability
             << setw(18) << r.chebyshevBound
             << setw(15) << r.meanSquaredError
             << '\n';
    }
}

void saveResults(
    const vector<Result>& results,
    const string& filename
) {
    const string temporary = filename + ".tmp";

    ofstream output(
        temporary,
        ios::out | ios::trunc
    );

    if (!output) {
        throw runtime_error("Unable to create output file.");
    }

    output << "sample_size,trials,mae,mse,observed_probability,"
              "chebyshev_bound\n";

    output << setprecision(12);

    for (const auto& r : results) {
        output << r.sampleSize << ','
               << r.trials << ','
               << r.meanAbsoluteError << ','
               << r.meanSquaredError << ','
               << r.observedProbability << ','
               << r.chebyshevBound << '\n';
    }

    output.close();

    if (!output) {
        remove(temporary.c_str());
        throw runtime_error("Failed while writing results.");
    }

    if (rename(temporary.c_str(), filename.c_str()) != 0) {
        remove(temporary.c_str());
        throw runtime_error("Unable to publish results file.");
    }
}

vector<DistributionSpec> distributions() {
    return {
        {
            "Bernoulli(0.5)",
            0.5,
            0.25,
            DistributionType::Bernoulli
        },
        {
            "Uniform(0,1)",
            0.5,
            1.0 / 12.0,
            DistributionType::Uniform
        },
        {
            "Normal(0,1)",
            0.0,
            1.0,
            DistributionType::Normal
        }
    };
}

int main() {
    try {
        ExperimentConfig config;
        validate(config);

        const auto specs = distributions();
        const DistributionSpec primary = specs.front();

        StatisticalEngine weakEngine(config.seed);

        const auto weakResults = weakEngine.runWeakLaw(
            primary,
            config
        );

        printResults(primary, weakResults);

        StatisticalEngine strongEngine(config.seed + 100);

        const auto strongResults = strongEngine.runStrongLaw(
            primary,
            config.sampleSizes
        );

        cout << "\nSTRONG LAW OF LARGE NUMBERS\n";
        cout << "Single realized sequence:\n";

        for (const auto& [n, mean] : strongResults) {
            cout << "N=" << setw(7) << n
                 << " Mean=" << fixed << setprecision(6)
                 << mean
                 << " Error=" << abs(mean - primary.mean)
                 << '\n';
        }

        cout << "\nDISTRIBUTION COMPARISON\n";

        for (size_t i = 0; i < specs.size(); ++i) {
            StatisticalEngine engine(config.seed + 200 + i);

            auto results = engine.runWeakLaw(
                specs[i],
                config
            );

            cout << specs[i].name
                 << " final MAE="
                 << results.back().meanAbsoluteError
                 << '\n';
        }

        saveResults(weakResults, "lln_results_cpp.csv");

        // Constant random variables have zero variance and no sampling error.
        DistributionSpec constant{
            "Constant(7)",
            7.0,
            0.0,
            DistributionType::Uniform
        };

        OnlineStatistics edgeCase;
        for (int i = 0; i < 100; ++i) {
            edgeCase.add(7.0);
        }

        cout << "\nEDGE CASE\n";
        cout << "Constant observations mean: "
             << edgeCase.mean() << '\n';
        cout << "Constant observations variance: "
             << edgeCase.variance() << '\n';

        cout << "\nResults saved to lln_results_cpp.csv\n";

    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
