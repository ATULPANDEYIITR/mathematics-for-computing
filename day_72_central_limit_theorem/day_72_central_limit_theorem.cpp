/*
 * Central Limit Theorem: Repository-Independent Statistical Engine
 *
 * C++17 implementation of:
 * - Finite and theoretical populations
 * - Random sampling with and without replacement
 * - Sampling distributions
 * - Welford online statistics
 * - Finite population correction
 * - Normal approximation
 * - Confidence interval coverage
 * - Distribution convergence diagnostics
 * - Reproducible Monte Carlo experiments
 *
 * Build:
 * g++ -std=c++17 -O2 -Wall -Wextra -pedantic clt.cpp -o clt
 *
 * Run:
 * ./clt
 */

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

namespace clt {

constexpr double PI = 3.14159265358979323846;
constexpr double Z_95 = 1.959963984540054;

enum class Distribution {
    Bernoulli,
    Exponential,
    Uniform,
    Skewed
};

enum class SamplingMode {
    WithReplacement,
    WithoutReplacement
};

struct Population {
    std::string name;
    std::vector<double> values;
    double mean = 0.0;
    double variance = 0.0;
    double standardDeviation = 0.0;

    explicit Population(
        std::string populationName,
        std::vector<double> observations
    ) : name(std::move(populationName)),
        values(std::move(observations)) {

        if (values.size() < 2) {
            throw std::invalid_argument(
                "Population requires at least two values."
            );
        }

        for (double value : values) {
            if (!std::isfinite(value)) {
                throw std::invalid_argument(
                    "Population contains a non-finite value."
                );
            }
        }

        mean = std::accumulate(
            values.begin(), values.end(), 0.0
        ) / static_cast<double>(values.size());

        double squaredError = 0.0;

        for (double value : values) {
            squaredError += (value - mean) * (value - mean);
        }

        variance = squaredError / static_cast<double>(values.size());
        standardDeviation = std::sqrt(variance);
    }
};

class OnlineStatistics {
private:
    std::size_t count_ = 0;
    double mean_ = 0.0;
    double m2_ = 0.0;
    double minimum_ = 0.0;
    double maximum_ = 0.0;

public:
    void add(double value) {
        if (!std::isfinite(value)) {
            throw std::invalid_argument("Statistic must be finite.");
        }

        ++count_;

        if (count_ == 1) {
            minimum_ = maximum_ = value;
        } else {
            minimum_ = std::min(minimum_, value);
            maximum_ = std::max(maximum_, value);
        }

        const double delta = value - mean_;
        mean_ += delta / static_cast<double>(count_);
        const double delta2 = value - mean_;

        m2_ += delta * delta2;
    }

    std::size_t count() const {
        return count_;
    }

    double mean() const {
        return mean_;
    }

    double variance() const {
        return count_ > 1
            ? m2_ / static_cast<double>(count_ - 1)
            : 0.0;
    }

    double standardDeviation() const {
        return std::sqrt(variance());
    }

    double minimum() const {
        return minimum_;
    }

    double maximum() const {
        return maximum_;
    }
};

class SamplingEngine {
private:
    const Population& population_;
    std::mt19937_64 generator_;

public:
    SamplingEngine(
        const Population& population,
        std::uint64_t seed = 42
    ) : population_(population), generator_(seed) {}

    void validate(
        std::size_t sampleSize,
        std::size_t repetitions,
        SamplingMode mode
    ) const {
        if (sampleSize == 0 || repetitions < 2) {
            throw std::invalid_argument(
                "Invalid sample size or repetition count."
            );
        }

        if (
            mode == SamplingMode::WithoutReplacement &&
            sampleSize > population_.values.size()
        ) {
            throw std::invalid_argument(
                "Sample exceeds population size."
            );
        }
    }

    std::vector<double> drawSample(
        std::size_t sampleSize,
        SamplingMode mode
    ) {
        std::vector<double> sample;

        if (mode == SamplingMode::WithReplacement) {
            std::uniform_int_distribution<std::size_t> distribution(
                0, population_.values.size() - 1
            );

            sample.reserve(sampleSize);

            for (std::size_t i = 0; i < sampleSize; ++i) {
                sample.push_back(
                    population_.values[distribution(generator_)]
                );
            }
        } else {
            sample = population_.values;

            std::shuffle(
                sample.begin(),
                sample.end(),
                generator_
            );

            sample.resize(sampleSize);
        }

        return sample;
    }

    double standardError(
        std::size_t sampleSize,
        SamplingMode mode
    ) const {
        if (sampleSize == 0) {
            throw std::invalid_argument("Sample size cannot be zero.");
        }

        double se = population_.standardDeviation /
            std::sqrt(static_cast<double>(sampleSize));

        if (mode == SamplingMode::WithoutReplacement) {
            if (sampleSize > population_.values.size()) {
                throw std::invalid_argument("Invalid sample size.");
            }

            const double N =
                static_cast<double>(population_.values.size());

            se *= std::sqrt(
                (N - static_cast<double>(sampleSize)) / (N - 1.0)
            );
        }

        return se;
    }

    std::vector<double> generateMeans(
        std::size_t sampleSize,
        std::size_t repetitions,
        SamplingMode mode
    ) {
        validate(sampleSize, repetitions, mode);

        std::vector<double> means;
        means.reserve(repetitions);

        for (std::size_t i = 0; i < repetitions; ++i) {
            const auto sample = drawSample(sampleSize, mode);

            const double sum = std::accumulate(
                sample.begin(), sample.end(), 0.0
            );

            means.push_back(
                sum / static_cast<double>(sampleSize)
            );
        }

        return means;
    }
};

double normalCDF(double x) {
    return 0.5 * std::erfc(-x / std::sqrt(2.0));
}

double normalPDF(double x) {
    return std::exp(-0.5 * x * x) / std::sqrt(2.0 * PI);
}

struct ConfidenceInterval {
    double lower;
    double upper;
};

ConfidenceInterval calculateInterval(
    double mean,
    double standardError,
    double z = Z_95
) {
    if (
        !std::isfinite(mean) ||
        !std::isfinite(standardError) ||
        standardError < 0 ||
        z <= 0
    ) {
        throw std::invalid_argument(
            "Invalid confidence interval parameters."
        );
    }

    const double margin = z * standardError;

    return {
        mean - margin,
        mean + margin
    };
}

struct ExperimentResult {
    std::size_t sampleSize;
    std::size_t repetitions;
    double empiricalMean;
    double theoreticalMean;
    double empiricalSD;
    double theoreticalSE;
    double relativeSEError;
    double ksDistance;
    double coverage;
};

double kolmogorovSmirnovDistance(
    std::vector<double> observations,
    double expectedMean,
    double expectedSE
) {
    if (observations.empty()) {
        throw std::invalid_argument("Observations cannot be empty.");
    }

    if (expectedSE == 0) {
        return 0.0;
    }

    std::sort(observations.begin(), observations.end());

    const std::size_t n = observations.size();
    double maximum = 0.0;

    for (std::size_t i = 0; i < n; ++i) {
        const double z =
            (observations[i] - expectedMean) / expectedSE;

        const double expected = normalCDF(z);

        const double empiricalUpper =
            static_cast<double>(i + 1) / n;

        const double empiricalLower =
            static_cast<double>(i) / n;

        maximum = std::max({
            maximum,
            std::abs(empiricalUpper - expected),
            std::abs(empiricalLower - expected)
        });
    }

    return maximum;
}

double confidenceCoverage(
    SamplingEngine& engine,
    const Population& population,
    std::size_t sampleSize,
    std::size_t repetitions,
    SamplingMode mode
) {
    std::size_t covered = 0;

    for (std::size_t i = 0; i < repetitions; ++i) {
        const auto sample = engine.drawSample(sampleSize, mode);

        const double mean = std::accumulate(
            sample.begin(), sample.end(), 0.0
        ) / static_cast<double>(sampleSize);

        OnlineStatistics sampleStatistics;

        for (double value : sample) {
            sampleStatistics.add(value);
        }

        double se = sampleStatistics.standardDeviation() /
            std::sqrt(static_cast<double>(sampleSize));

        if (mode == SamplingMode::WithoutReplacement) {
            const double N =
                static_cast<double>(population.values.size());

            se *= std::sqrt(
                (N - static_cast<double>(sampleSize)) / (N - 1.0)
            );
        }

        const auto interval = calculateInterval(mean, se);

        if (
            interval.lower <= population.mean &&
            population.mean <= interval.upper
        ) {
            ++covered;
        }
    }

    return static_cast<double>(covered) / repetitions;
}

ExperimentResult runExperiment(
    const Population& population,
    std::size_t sampleSize,
    std::size_t repetitions,
    SamplingMode mode,
    std::uint64_t seed
) {
    SamplingEngine engine(population, seed);

    auto means = engine.generateMeans(
        sampleSize, repetitions, mode
    );

    OnlineStatistics statistics;

    for (double mean : means) {
        statistics.add(mean);
    }

    const double theoreticalSE =
        engine.standardError(sampleSize, mode);

    const double relativeError = theoreticalSE == 0
        ? 0.0
        : std::abs(
            statistics.standardDeviation() - theoreticalSE
        ) / theoreticalSE;

    const double ks = kolmogorovSmirnovDistance(
        means, population.mean, theoreticalSE
    );

    const double coverage = confidenceCoverage(
        engine,
        population,
        sampleSize,
        repetitions,
        mode
    );

    return {
        sampleSize,
        repetitions,
        statistics.mean(),
        population.mean,
        statistics.standardDeviation(),
        theoreticalSE,
        relativeError,
        ks,
        coverage
    };
}

Population generatePopulation(
    Distribution distribution,
    std::size_t size,
    std::uint64_t seed
) {
    if (size < 2) {
        throw std::invalid_argument("Population size must exceed one.");
    }

    std::mt19937_64 generator(seed);

    std::vector<double> values;
    values.reserve(size);

    std::uniform_real_distribution<double> uniform(0.0, 1.0);
    std::exponential_distribution<double> exponential(1.0);

    for (std::size_t i = 0; i < size; ++i) {
        double value = 0.0;

        switch (distribution) {
            case Distribution::Bernoulli:
                value = uniform(generator) < 0.3 ? 1.0 : 0.0;
                break;

            case Distribution::Exponential:
                value = exponential(generator);
                break;

            case Distribution::Uniform:
                value = uniform(generator) * 100.0;
                break;

            case Distribution::Skewed:
                value = std::pow(exponential(generator) * 2.0, 1.5);
                break;
        }

        values.push_back(value);
    }

    std::string name;

    switch (distribution) {
        case Distribution::Bernoulli:
            name = "Bernoulli";
            break;
        case Distribution::Exponential:
            name = "Exponential";
            break;
        case Distribution::Uniform:
            name = "Uniform";
            break;
        case Distribution::Skewed:
            name = "HighlySkewed";
            break;
    }

    return Population(name, std::move(values));
}

void runTests() {
    OnlineStatistics stats;

    for (double x : {1.0, 2.0, 3.0, 4.0, 5.0}) {
        stats.add(x);
    }

    if (std::abs(stats.mean() - 3.0) > 1e-10) {
        throw std::runtime_error("Online mean test failed.");
    }

    if (std::abs(stats.variance() - 2.5) > 1e-10) {
        throw std::runtime_error("Online variance test failed.");
    }

    if (std::abs(normalCDF(0.0) - 0.5) > 1e-10) {
        throw std::runtime_error("Normal CDF test failed.");
    }

    const auto interval = calculateInterval(100.0, 5.0);

    if (!(interval.lower < 100 && interval.upper > 100)) {
        throw std::runtime_error("Confidence interval test failed.");
    }

    bool rejected = false;

    try {
        Population invalid("invalid", {1.0});
    } catch (const std::invalid_argument&) {
        rejected = true;
    }

    if (!rejected) {
        throw std::runtime_error("Population validation test failed.");
    }

    std::cout << "All C++ tests passed.\n";
}

} // namespace clt

int main() {
    using namespace clt;

    try {
        runTests();

        const std::vector<Distribution> distributions = {
            Distribution::Bernoulli,
            Distribution::Exponential,
            Distribution::Uniform,
            Distribution::Skewed
        };

        const std::vector<std::size_t> sampleSizes = {
            2, 5, 10, 30, 50, 100
        };

        constexpr std::size_t POPULATION_SIZE = 10000;
        constexpr std::size_t REPETITIONS = 5000;

        std::cout << std::fixed << std::setprecision(5);

        std::cout
            << "\nCENTRAL LIMIT THEOREM EXPERIMENT\n"
            << std::string(100, '=') << "\n";

        for (std::size_t d = 0; d < distributions.size(); ++d) {
            const Population population = generatePopulation(
                distributions[d],
                POPULATION_SIZE,
                42 + d
            );

            std::cout << "\nPopulation: " << population.name
                      << "\nMean: " << population.mean
                      << "\nPopulation SD: "
                      << population.standardDeviation << "\n\n";

            std::cout
                << "N\tEmpirical Mean\tEmpirical SD\tTheoretical SE"
                << "\tRelative Error\tKS Distance\tCoverage\n";

            for (std::size_t n : sampleSizes) {
                const auto result = runExperiment(
                    population,
                    n,
                    REPETITIONS,
                    SamplingMode::WithReplacement,
                    1000 + n + d
                );

                std::cout
                    << result.sampleSize << '\t'
                    << result.empiricalMean << '\t'
                    << result.empiricalSD << '\t'
                    << result.theoreticalSE << '\t'
                    << result.relativeSEError << '\t'
                    << result.ksDistance << '\t'
                    << result.coverage << '\n';
            }
        }

        // Demonstrate finite population correction.
        const Population finitePopulation(
            "FiniteExample",
            {10, 20, 30, 40, 50, 60, 70, 80, 90, 100}
        );

        SamplingEngine finiteEngine(finitePopulation);

        std::cout << "\nFINITE POPULATION SAMPLING\n";

        for (std::size_t n : {2U, 5U, 10U}) {
            std::cout
                << "n=" << n
                << " | FPC-adjusted SE="
                << finiteEngine.standardError(
                    n,
                    SamplingMode::WithoutReplacement
                )
                << '\n';
        }

        std::cout << "\nNormal CDF at 1.96: "
                  << normalCDF(1.96) << '\n';

        std::cout << "Normal PDF at 0: "
                  << normalPDF(0.0) << '\n';

    } catch (const std::exception& error) {
        std::cerr << "Simulation error: "
                  << error.what() << '\n';

        return 1;
    }

    return 0;
}
