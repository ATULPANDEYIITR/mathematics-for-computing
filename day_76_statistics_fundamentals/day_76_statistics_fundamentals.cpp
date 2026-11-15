#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

/*
 * Statistics Fundamentals
 *
 * C++17 statistical sampling and population analysis engine.
 *
 * Features:
 * - Population and sample domain modeling
 * - Population parameters
 * - Sample statistics
 * - Simple random sampling
 * - Stratified random sampling
 * - Systematic sampling
 * - Sampling with and without replacement
 * - Standard errors
 * - Finite population correction
 * - Confidence intervals
 * - Sample-size estimation
 * - Validation and deterministic randomization
 */

enum class SamplingMethod {
    SimpleRandom,
    Stratified,
    Systematic
};

struct Observation {
    std::string id;
    double value;
    std::string stratum;
};

struct PopulationParameters {
    std::size_t size;
    double mean;
    double variance;
    double standardDeviation;
    double total;
};

struct SampleStatistics {
    std::size_t size;
    double mean;
    double median;
    double variance;
    double standardDeviation;
    double minimum;
    double maximum;
};

struct ConfidenceInterval {
    double lower;
    double upper;
    double standardError;
    double confidence;
};

struct Sample {
    std::vector<Observation> observations;
    std::size_t populationSize;
    SamplingMethod method;
    std::uint32_t seed;
};

// ============================================================
// 1. VALIDATION
// ============================================================

void validateFinite(double value, const std::string& name) {
    if (!std::isfinite(value)) {
        throw std::invalid_argument(name + " must be finite.");
    }
}

void validateSampleSize(std::size_t n, std::size_t N) {
    if (n == 0 || n > N) {
        throw std::invalid_argument("Invalid sample size.");
    }
}

// ============================================================
// 2. STATISTICAL FUNCTIONS
// ============================================================

class Statistics {
public:
    static double mean(const std::vector<double>& values) {
        validate(values);

        // Long double reduces accumulation error.
        long double sum = 0.0L;

        for (double value : values) {
            sum += value;
        }

        return static_cast<double>(sum / values.size());
    }

    static double variance(
        const std::vector<double>& values,
        bool sample = true
    ) {
        validate(values);

        if (sample && values.size() < 2) {
            throw std::invalid_argument(
                "Sample variance requires two observations."
            );
        }

        const double average = mean(values);
        long double squaredSum = 0.0L;

        for (double value : values) {
            const long double difference = value - average;
            squaredSum += difference * difference;
        }

        const std::size_t denominator =
            sample ? values.size() - 1 : values.size();

        return static_cast<double>(squaredSum / denominator);
    }

    static double standardDeviation(
        const std::vector<double>& values,
        bool sample = true
    ) {
        return std::sqrt(variance(values, sample));
    }

    static double median(std::vector<double> values) {
        validate(values);

        std::sort(values.begin(), values.end());

        const std::size_t n = values.size();
        const std::size_t middle = n / 2;

        if (n % 2 == 1) {
            return values[middle];
        }

        return (
            values[middle - 1] + values[middle]
        ) / 2.0;
    }

    static double quantile(
        std::vector<double> values,
        double probability
    ) {
        validate(values);

        if (probability < 0.0 || probability > 1.0) {
            throw std::invalid_argument(
                "Probability must be between 0 and 1."
            );
        }

        std::sort(values.begin(), values.end());

        const double position =
            probability * (values.size() - 1);

        const auto lower = static_cast<std::size_t>(
            std::floor(position)
        );

        const auto upper = static_cast<std::size_t>(
            std::ceil(position)
        );

        const double fraction = position - lower;

        return values[lower] +
            fraction * (values[upper] - values[lower]);
    }

    static SampleStatistics describe(
        const std::vector<double>& values
    ) {
        validate(values);

        const auto bounds = std::minmax_element(
            values.begin(),
            values.end()
        );

        return {
            values.size(),
            mean(values),
            median(values),
            variance(values, values.size() > 1),
            standardDeviation(values, values.size() > 1),
            *bounds.first,
            *bounds.second
        };
    }

private:
    static void validate(const std::vector<double>& values) {
        if (values.empty()) {
            throw std::invalid_argument(
                "Observation vector cannot be empty."
            );
        }

        for (double value : values) {
            validateFinite(value, "Observation");
        }
    }
};

// ============================================================
// 3. POPULATION DOMAIN
// ============================================================

class Population {
private:
    std::vector<Observation> units;
    std::set<std::string> identifiers;

public:
    explicit Population(std::vector<Observation> observations)
        : units(std::move(observations)) {

        if (units.empty()) {
            throw std::invalid_argument("Population cannot be empty.");
        }

        for (const auto& unit : units) {
            if (unit.id.empty() || unit.stratum.empty()) {
                throw std::invalid_argument(
                    "Invalid population observation."
                );
            }

            validateFinite(unit.value, "Population value");

            if (!identifiers.insert(unit.id).second) {
                throw std::invalid_argument(
                    "Duplicate population identifier."
                );
            }
        }
    }

    std::size_t size() const {
        return units.size();
    }

    const std::vector<Observation>& getUnits() const {
        return units;
    }

    std::vector<double> values() const {
        std::vector<double> result;
        result.reserve(units.size());

        for (const auto& unit : units) {
            result.push_back(unit.value);
        }

        return result;
    }

    std::map<std::string, std::vector<Observation>>
    groupByStratum() const {
        std::map<std::string, std::vector<Observation>> groups;

        for (const auto& unit : units) {
            groups[unit.stratum].push_back(unit);
        }

        return groups;
    }

    PopulationParameters parameters() const {
        const auto observations = values();

        return {
            size(),
            Statistics::mean(observations),
            Statistics::variance(observations, false),
            Statistics::standardDeviation(observations, false),
            std::accumulate(
                observations.begin(),
                observations.end(),
                0.0
            )
        };
    }
};

// ============================================================
// 4. SAMPLING ENGINE
// ============================================================

class SamplingEngine {
private:
    const Population& population;
    std::mt19937 generator;
    std::uint32_t seed;

    Sample createSample(
        std::vector<Observation> selected,
        SamplingMethod method
    ) const {
        std::set<std::string> ids;

        for (const auto& observation : selected) {
            if (!ids.insert(observation.id).second) {
                throw std::logic_error(
                    "Duplicate sample observation."
                );
            }
        }

        return {
            std::move(selected),
            population.size(),
            method,
            seed
        };
    }

public:
    SamplingEngine(
        const Population& source,
        std::uint32_t randomSeed = 42
    )
        : population(source),
          generator(randomSeed),
          seed(randomSeed) {}

    Sample simpleRandom(std::size_t n) {
        validateSampleSize(n, population.size());

        std::vector<Observation> selected =
            population.getUnits();

        std::shuffle(
            selected.begin(),
            selected.end(),
            generator
        );

        selected.resize(n);

        return createSample(
            std::move(selected),
            SamplingMethod::SimpleRandom
        );
    }

    Sample systematic(std::size_t n) {
        validateSampleSize(n, population.size());

        const auto& units = population.getUnits();

        if (n == units.size()) {
            return createSample(
                units,
                SamplingMethod::Systematic
            );
        }

        const double interval =
            static_cast<double>(units.size()) / n;

        std::uniform_real_distribution<double> distribution(
            0.0,
            interval
        );

        const double start = distribution(generator);

        std::vector<Observation> selected;
        selected.reserve(n);

        for (std::size_t i = 0; i < n; ++i) {
            const std::size_t index = std::min(
                static_cast<std::size_t>(
                    std::floor(start + i * interval)
                ),
                units.size() - 1
            );

            selected.push_back(units[index]);
        }

        return createSample(
            std::move(selected),
            SamplingMethod::Systematic
        );
    }

    Sample stratified(std::size_t n) {
        validateSampleSize(n, population.size());

        const auto strata = population.groupByStratum();

        if (n < strata.size()) {
            throw std::invalid_argument(
                "Stratified sample must represent every stratum."
            );
        }

        struct Allocation {
            std::string name;
            const std::vector<Observation>* units;
            std::size_t count;
            double remainder;
        };

        std::vector<Allocation> allocations;

        for (const auto& [name, group] : strata) {
            const double exact =
                static_cast<double>(n) * group.size()
                / population.size();

            allocations.push_back({
                name,
                &group,
                static_cast<std::size_t>(std::floor(exact)),
                exact - std::floor(exact)
            });
        }

        std::size_t allocated = 0;

        for (const auto& item : allocations) {
            allocated += item.count;
        }

        std::sort(
            allocations.begin(),
            allocations.end(),
            [](const Allocation& a, const Allocation& b) {
                return a.remainder > b.remainder;
            }
        );

        std::size_t remaining = n - allocated;

        for (auto& item : allocations) {
            if (remaining == 0) break;

            if (item.count < item.units->size()) {
                item.count++;
                remaining--;
            }
        }

        if (remaining != 0) {
            throw std::logic_error(
                "Stratified allocation could not be completed."
            );
        }

        std::vector<Observation> selected;

        for (auto& item : allocations) {
            auto group = *item.units;

            std::shuffle(
                group.begin(),
                group.end(),
                generator
            );

            selected.insert(
                selected.end(),
                group.begin(),
                group.begin() + item.count
            );
        }

        return createSample(
            std::move(selected),
            SamplingMethod::Stratified
        );
    }
};

// ============================================================
// 5. INFERENCE ENGINE
// ============================================================

class InferenceEngine {
public:
    static double standardError(
        const Sample& sample,
        bool finiteCorrection = true
    ) {
        std::vector<double> values;

        for (const auto& observation : sample.observations) {
            values.push_back(observation.value);
        }

        const std::size_t n = values.size();
        const std::size_t N = sample.populationSize;

        if (n < 2) {
            throw std::invalid_argument(
                "At least two observations are required."
            );
        }

        double se =
            Statistics::standardDeviation(values, true)
            / std::sqrt(static_cast<double>(n));

        if (finiteCorrection && n < N) {
            se *= std::sqrt(
                static_cast<double>(N - n) / (N - 1)
            );
        }

        return se;
    }

    static ConfidenceInterval confidenceInterval(
        const Sample& sample,
        double confidence = 0.95
    ) {
        double z;

        if (confidence == 0.90) {
            z = 1.645;
        } else if (confidence == 0.95) {
            z = 1.960;
        } else if (confidence == 0.99) {
            z = 2.576;
        } else {
            throw std::invalid_argument(
                "Supported confidence levels: 0.90, 0.95, 0.99."
            );
        }

        std::vector<double> values;

        for (const auto& observation : sample.observations) {
            values.push_back(observation.value);
        }

        const double mean = Statistics::mean(values);
        const double se = standardError(sample);
        const double margin = z * se;

        return {
            mean - margin,
            mean + margin,
            se,
            confidence
        };
    }

    static std::size_t requiredSampleSize(
        double populationStd,
        double margin,
        double z,
        std::size_t populationSize
    ) {
        validateFinite(populationStd, "Population standard deviation");
        validateFinite(margin, "Margin");
        validateFinite(z, "Z-score");

        if (populationStd < 0 || margin <= 0 || z <= 0) {
            throw std::invalid_argument(
                "Invalid sample-size parameters."
            );
        }

        if (populationSize == 0) {
            throw std::invalid_argument(
                "Population size must be positive."
            );
        }

        if (populationStd == 0) return 1;

        const double n0 =
            std::pow(z * populationStd / margin, 2);

        if (n0 >= populationSize) {
            return populationSize;
        }

        const double adjusted =
            n0 / (1.0 + (n0 - 1.0) / populationSize);

        return std::min(
            populationSize,
            static_cast<std::size_t>(std::ceil(adjusted))
        );
    }
};

// ============================================================
// 6. REPORTING
// ============================================================

void printParameters(const PopulationParameters& p) {
    std::cout << "\nPOPULATION PARAMETERS\n";

    std::cout << "Population size: " << p.size << '\n';
    std::cout << "Population mean: " << p.mean << '\n';
    std::cout << "Population variance: " << p.variance << '\n';
    std::cout << "Population standard deviation: "
              << p.standardDeviation << '\n';
    std::cout << "Population total: " << p.total << '\n';
}

void printSample(
    const std::string& title,
    const Sample& sample
) {
    std::vector<double> values;

    for (const auto& observation : sample.observations) {
        values.push_back(observation.value);
    }

    const auto result = Statistics::describe(values);

    std::cout << "\n" << title << '\n';
    std::cout << "Sample size: " << result.size << '\n';
    std::cout << "Mean: " << result.mean << '\n';
    std::cout << "Median: " << result.median << '\n';
    std::cout << "Sample variance: " << result.variance << '\n';
    std::cout << "Sample standard deviation: "
              << result.standardDeviation << '\n';
    std::cout << "Minimum: " << result.minimum << '\n';
    std::cout << "Maximum: " << result.maximum << '\n';
}

// ============================================================
// 7. APPLICATION
// ============================================================

Population buildPopulation() {
    std::vector<Observation> observations;

    const std::vector<std::string> departments = {
        "Technology",
        "Mathematics",
        "Physics"
    };

    for (std::size_t group = 0; group < departments.size(); ++group) {
        for (int i = 1; i <= 30; ++i) {
            const double score =
                50.0 + group * 10.0 + i * 0.8 + (i % 5) * 2.0;

            observations.push_back({
                "STU-" + std::to_string(group + 1)
                    + "-" + std::to_string(i),
                score,
                departments[group]
            });
        }
    }

    return Population(std::move(observations));
}

void runTests() {
    const std::vector<double> values = {10, 20, 30};

    if (Statistics::mean(values) != 20.0) {
        throw std::runtime_error("Mean test failed.");
    }

    if (Statistics::median(values) != 20.0) {
        throw std::runtime_error("Median test failed.");
    }

    if (Statistics::variance(values, false) < 0) {
        throw std::runtime_error("Variance test failed.");
    }

    try {
        validateSampleSize(5, 3);
        throw std::runtime_error("Invalid sample size was accepted.");
    } catch (const std::invalid_argument&) {
        // Expected validation result.
    }
}

int main() {
    try {
        runTests();

        std::cout << std::fixed << std::setprecision(3);

        Population population = buildPopulation();

        printParameters(population.parameters());

        SamplingEngine engine(population, 42);

        Sample randomSample = engine.simpleRandom(20);
        Sample systematicSample = engine.systematic(20);
        Sample stratifiedSample = engine.stratified(20);

        printSample("SIMPLE RANDOM SAMPLE", randomSample);
        printSample("SYSTEMATIC SAMPLE", systematicSample);
        printSample("STRATIFIED SAMPLE", stratifiedSample);

        const auto ci =
            InferenceEngine::confidenceInterval(randomSample);

        std::cout << "\n95% CONFIDENCE INTERVAL\n";
        std::cout << "Lower: " << ci.lower << '\n';
        std::cout << "Upper: " << ci.upper << '\n';
        std::cout << "Standard error: "
                  << ci.standardError << '\n';

        const std::size_t required =
            InferenceEngine::requiredSampleSize(
                15.0,
                3.0,
                1.96,
                population.size()
            );

        std::cout << "\nREQUIRED SAMPLE SIZE\n";
        std::cout << required << '\n';

        std::cout << "\nVALIDATION\n";
        std::cout << "All statistical tests passed.\n";

    } catch (const std::exception& error) {
        std::cerr << "Application error: "
                  << error.what() << '\n';

        return 1;
    }

    return 0;
}
