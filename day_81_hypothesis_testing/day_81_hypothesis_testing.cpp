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
 * HYPOTHESIS TESTING ENGINE
 *
 * C++17 statistical decision system.
 *
 * Implements:
 * - Hypothesis representation
 * - One-sample Z-test
 * - P-value calculation
 * - Significance testing
 * - Confidence intervals
 * - Multiple-testing correction
 * - Experiment management
 * - Validation and exception handling
 */

enum class Alternative {
    TWO_SIDED,
    GREATER,
    LESS
};

enum class Decision {
    REJECT_NULL,
    FAIL_TO_REJECT
};

enum class ExperimentState {
    CREATED,
    COMPLETED,
    FAILED
};

std::string toString(Alternative alternative) {
    switch (alternative) {
        case Alternative::TWO_SIDED:
            return "Two-sided";

        case Alternative::GREATER:
            return "Greater";

        case Alternative::LESS:
            return "Less";
    }

    throw std::invalid_argument("Unknown alternative.");
}

std::string toString(Decision decision) {
    return decision == Decision::REJECT_NULL
        ? "Reject null hypothesis"
        : "Fail to reject null hypothesis";
}

double normalCDF(double z) {
    return 0.5 * std::erfc(-z / std::sqrt(2.0));
}

double normalSurvival(double z) {
    return 0.5 * std::erfc(z / std::sqrt(2.0));
}

double pValue(double z, Alternative alternative) {
    switch (alternative) {
        case Alternative::TWO_SIDED:
            return std::min(
                1.0,
                std::erfc(std::abs(z) / std::sqrt(2.0))
            );

        case Alternative::GREATER:
            return normalSurvival(z);

        case Alternative::LESS:
            return normalCDF(z);
    }

    throw std::invalid_argument("Invalid alternative.");
}

double criticalZ(double alpha) {
    double low = 0.0;
    double high = 10.0;
    const double target = alpha / 2.0;

    for (int i = 0; i < 100; ++i) {
        const double mid = (low + high) / 2.0;

        if (normalSurvival(mid) > target) {
            low = mid;
        } else {
            high = mid;
        }
    }

    return (low + high) / 2.0;
}

struct Hypothesis {
    double nullMean;
    double alpha;
    Alternative alternative;

    Hypothesis(
        double mean,
        double significance,
        Alternative direction
    )
        : nullMean(mean),
          alpha(significance),
          alternative(direction) {

        if (!std::isfinite(nullMean)) {
            throw std::invalid_argument(
                "Null mean must be finite."
            );
        }

        if (!std::isfinite(alpha) || alpha <= 0 || alpha >= 1) {
            throw std::invalid_argument(
                "Alpha must be between 0 and 1."
            );
        }
    }
};

struct TestResult {
    std::size_t sampleSize;
    double sampleMean;
    double standardError;
    double zStatistic;
    double pValue;
    double lowerConfidence;
    double upperConfidence;
    double alpha;
    Alternative alternative;
    Decision decision;
};

class StatisticalEngine {
public:
    static TestResult oneSampleZTest(
        const std::vector<double>& observations,
        const Hypothesis& hypothesis,
        double populationSigma
    ) {
        if (observations.size() < 2) {
            throw std::invalid_argument(
                "At least two observations are required."
            );
        }

        if (
            !std::isfinite(populationSigma) ||
            populationSigma <= 0
        ) {
            throw std::invalid_argument(
                "Population standard deviation must be positive."
            );
        }

        double total = 0.0;

        for (double value : observations) {
            if (!std::isfinite(value)) {
                throw std::invalid_argument(
                    "Observation must be finite."
                );
            }

            total += value;
        }

        const std::size_t n = observations.size();

        const double mean = total / static_cast<double>(n);

        const double standardError =
            populationSigma / std::sqrt(static_cast<double>(n));

        const double z =
            (mean - hypothesis.nullMean) / standardError;

        const double p = ::pValue(z, hypothesis.alternative);

        const Decision decision =
            p <= hypothesis.alpha
            ? Decision::REJECT_NULL
            : Decision::FAIL_TO_REJECT;

        const double critical = criticalZ(hypothesis.alpha);

        const double margin = critical * standardError;

        return {
            n,
            mean,
            standardError,
            z,
            p,
            mean - margin,
            mean + margin,
            hypothesis.alpha,
            hypothesis.alternative,
            decision
        };
    }
};

class MultipleTesting {
public:
    struct AdjustedResult {
        double originalP;
        double adjustedP;
        double threshold;
        bool significant;
    };

    static std::vector<AdjustedResult> bonferroni(
        const std::vector<double>& pValues,
        double alpha
    ) {
        if (pValues.empty()) {
            throw std::invalid_argument(
                "At least one p-value is required."
            );
        }

        if (!std::isfinite(alpha) || alpha <= 0 || alpha >= 1) {
            throw std::invalid_argument("Invalid alpha.");
        }

        const double threshold =
            alpha / static_cast<double>(pValues.size());

        std::vector<AdjustedResult> results;

        for (double p : pValues) {
            if (!std::isfinite(p) || p < 0 || p > 1) {
                throw std::invalid_argument("Invalid p-value.");
            }

            results.push_back({
                p,
                std::min(1.0, p * pValues.size()),
                threshold,
                p <= threshold
            });
        }

        return results;
    }
};

struct Experiment {
    std::string id;
    Hypothesis hypothesis;
    std::vector<double> observations;
    double sigma;
    ExperimentState state;
    TestResult result;

    Experiment(
        std::string identifier,
        Hypothesis h,
        std::vector<double> values,
        double populationSigma
    )
        : id(std::move(identifier)),
          hypothesis(h),
          observations(std::move(values)),
          sigma(populationSigma),
          state(ExperimentState::CREATED),
          result{} {

        if (id.empty()) {
            throw std::invalid_argument(
                "Experiment ID cannot be empty."
            );
        }
    }
};

class ExperimentManager {
private:
    std::map<std::string, Experiment> experiments;

public:
    void registerExperiment(Experiment experiment) {
        auto result = experiments.emplace(
            experiment.id,
            std::move(experiment)
        );

        if (!result.second) {
            throw std::invalid_argument(
                "Duplicate experiment ID."
            );
        }
    }

    void executeAll() {
        for (auto& entry : experiments) {
            Experiment& experiment = entry.second;

            if (experiment.state != ExperimentState::CREATED) {
                continue;
            }

            try {
                experiment.result =
                    StatisticalEngine::oneSampleZTest(
                        experiment.observations,
                        experiment.hypothesis,
                        experiment.sigma
                    );

                experiment.state = ExperimentState::COMPLETED;
            } catch (const std::exception& error) {
                experiment.state = ExperimentState::FAILED;

                std::cerr
                    << "Experiment "
                    << experiment.id
                    << " failed: "
                    << error.what()
                    << '\n';
            }
        }
    }

    void displayResults() const {
        for (const auto& entry : experiments) {
            const Experiment& experiment = entry.second;

            std::cout << "\nExperiment: "
                      << experiment.id << '\n';

            if (experiment.state == ExperimentState::FAILED) {
                std::cout << "State: FAILED\n";
                continue;
            }

            if (experiment.state != ExperimentState::COMPLETED) {
                std::cout << "State: CREATED\n";
                continue;
            }

            const TestResult& r = experiment.result;

            std::cout << std::fixed << std::setprecision(6);

            std::cout << "Sample size: "
                      << r.sampleSize << '\n';

            std::cout << "Sample mean: "
                      << r.sampleMean << '\n';

            std::cout << "Standard error: "
                      << r.standardError << '\n';

            std::cout << "Z statistic: "
                      << r.zStatistic << '\n';

            std::cout << "P-value: "
                      << r.pValue << '\n';

            std::cout << "Alpha: "
                      << r.alpha << '\n';

            std::cout << "Alternative: "
                      << toString(r.alternative) << '\n';

            std::cout << "Confidence interval: ["
                      << r.lowerConfidence << ", "
                      << r.upperConfidence << "]\n";

            std::cout << "Decision: "
                      << toString(r.decision) << '\n';
        }
    }
};

void runValidationTests() {
    if (std::abs(normalCDF(0) - 0.5) > 1e-10) {
        throw std::runtime_error("Normal CDF validation failed.");
    }

    if (std::abs(
        pValue(0, Alternative::TWO_SIDED) - 1.0
    ) > 1e-10) {
        throw std::runtime_error("P-value validation failed.");
    }

    const auto corrected =
        MultipleTesting::bonferroni(
            {0.001, 0.018, 0.032},
            0.05
        );

    if (!corrected[0].significant) {
        throw std::runtime_error(
            "Bonferroni validation failed."
        );
    }

    if (corrected[1].significant) {
        throw std::runtime_error(
            "Unexpected statistical significance."
        );
    }

    std::cout << "All validation tests passed.\n";
}

int main() {
    try {
        runValidationTests();

        Hypothesis hypothesis(
            100.0,
            0.05,
            Alternative::TWO_SIDED
        );

        std::vector<double> productionData = {
            104, 108, 102, 107, 105,
            110, 106, 103, 109, 107,
            105, 108, 111, 104, 106,
            109, 107, 105, 110, 108
        };

        ExperimentManager manager;

        manager.registerExperiment(
            Experiment(
                "QUALITY-001",
                hypothesis,
                productionData,
                8.0
            )
        );

        manager.executeAll();
        manager.displayResults();

        std::cout << "\nMULTIPLE TESTING\n";

        const auto adjusted =
            MultipleTesting::bonferroni(
                {0.001, 0.018, 0.032, 0.12, 0.40},
                0.05
            );

        for (std::size_t i = 0; i < adjusted.size(); ++i) {
            std::cout
                << "Test " << i + 1
                << " | Original p: " << adjusted[i].originalP
                << " | Adjusted p: " << adjusted[i].adjustedP
                << " | Significant: "
                << (adjusted[i].significant ? "Yes" : "No")
                << '\n';
        }

        return 0;

    } catch (const std::exception& error) {
        std::cerr << "Fatal error: "
                  << error.what() << '\n';

        return 1;
    }
}
