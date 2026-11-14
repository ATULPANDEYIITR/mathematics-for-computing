#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <queue>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

/*
 * Advanced Probability: Stochastic Modeling Engine
 *
 * C++17 implementation of:
 * - Finite-state Markov chains
 * - Transition probability validation
 * - Stationary distribution computation
 * - Irreducibility and periodicity
 * - Ergodicity classification
 * - Martingale difference processes
 * - Long-run empirical estimation
 *
 * No external libraries.
 */

using namespace std;

// ============================================================
// 1. DOMAIN TYPES
// ============================================================

enum class Classification {
    Ergodic,
    IrreduciblePeriodic,
    Reducible
};

string classificationName(Classification value) {
    switch (value) {
        case Classification::Ergodic:
            return "Ergodic";
        case Classification::IrreduciblePeriodic:
            return "Irreducible but periodic";
        case Classification::Reducible:
            return "Reducible";
    }

    return "Unknown";
}

struct StationaryResult {
    vector<double> distribution;
    int iterations;
    bool converged;
    double residual;
};

struct SimulationResult {
    vector<int> path;
    vector<double> empirical;
    vector<vector<int>> transitionCounts;
};

// ============================================================
// 2. VALIDATION
// ============================================================

class ProbabilityException : public runtime_error {
public:
    explicit ProbabilityException(const string& message)
        : runtime_error(message) {}
};

void validateProbability(double probability) {
    if (!isfinite(probability) ||
        probability < 0.0 ||
        probability > 1.0) {
        throw ProbabilityException("Invalid probability.");
    }
}

double maximumDifference(
    const vector<double>& a,
    const vector<double>& b
) {
    if (a.size() != b.size()) {
        throw ProbabilityException("Vector dimension mismatch.");
    }

    double result = 0.0;

    for (size_t i = 0; i < a.size(); ++i) {
        result = max(result, abs(a[i] - b[i]));
    }

    return result;
}

// ============================================================
// 3. MARKOV CHAIN ENGINE
// ============================================================

class MarkovChain {
private:
    vector<vector<double>> transition;
    vector<string> labels;
    size_t n;

public:
    MarkovChain(
        vector<vector<double>> matrix,
        vector<string> stateLabels
    )
        : transition(move(matrix)),
          labels(move(stateLabels)),
          n(transition.size()) {

        if (n == 0 || labels.size() != n) {
            throw ProbabilityException("Invalid state configuration.");
        }

        for (const auto& row : transition) {
            if (row.size() != n) {
                throw ProbabilityException("Matrix must be square.");
            }

            double sum = 0.0;

            for (double probability : row) {
                validateProbability(probability);
                sum += probability;
            }

            if (abs(sum - 1.0) > 1e-10) {
                throw ProbabilityException(
                    "Transition row must sum to one."
                );
            }
        }

        sort(labels.begin(), labels.end());

        if (adjacent_find(labels.begin(), labels.end()) != labels.end()) {
            throw ProbabilityException("Duplicate state labels.");
        }
    }

    size_t size() const {
        return n;
    }

    const vector<string>& getLabels() const {
        return labels;
    }

    const vector<vector<double>>& matrix() const {
        return transition;
    }

    int sampleNext(int current, mt19937_64& generator) const {
        if (current < 0 || static_cast<size_t>(current) >= n) {
            throw ProbabilityException("Invalid state index.");
        }

        discrete_distribution<int> distribution(
            transition[current].begin(),
            transition[current].end()
        );

        return distribution(generator);
    }

    vector<double> multiply(
        const vector<double>& distribution
    ) const {
        if (distribution.size() != n) {
            throw ProbabilityException("Distribution size mismatch.");
        }

        vector<double> result(n, 0.0);

        for (size_t i = 0; i < n; ++i) {
            if (!isfinite(distribution[i]) || distribution[i] < 0) {
                throw ProbabilityException("Invalid distribution.");
            }

            for (size_t j = 0; j < n; ++j) {
                result[j] += distribution[i] * transition[i][j];
            }
        }

        return result;
    }

    // --------------------------------------------------------
    // 4. GRAPH ANALYSIS
    // --------------------------------------------------------

    vector<int> distancesFrom(int start) const {
        if (start < 0 || static_cast<size_t>(start) >= n) {
            throw ProbabilityException("Invalid starting state.");
        }

        vector<int> distance(n, -1);
        queue<int> pending;

        distance[start] = 0;
        pending.push(start);

        while (!pending.empty()) {
            int current = pending.front();
            pending.pop();

            for (size_t destination = 0; destination < n; ++destination) {
                if (transition[current][destination] > 0 &&
                    distance[destination] == -1) {

                    distance[destination] = distance[current] + 1;
                    pending.push(static_cast<int>(destination));
                }
            }
        }

        return distance;
    }

    bool isIrreducible() const {
        for (size_t state = 0; state < n; ++state) {
            auto distance = distancesFrom(static_cast<int>(state));

            if (find(distance.begin(), distance.end(), -1)
                != distance.end()) {
                return false;
            }
        }

        return true;
    }

    int period(int start = 0) const {
        auto distance = distancesFrom(start);

        if (find(distance.begin(), distance.end(), -1)
            != distance.end()) {
            throw ProbabilityException(
                "Period requires an irreducible chain."
            );
        }

        int result = 0;

        for (size_t i = 0; i < n; ++i) {
            for (size_t j = 0; j < n; ++j) {
                if (transition[i][j] > 0) {
                    int difference = abs(
                        distance[i] + 1 - distance[j]
                    );

                    result = gcd(result, difference);
                }
            }
        }

        return result;
    }

    Classification classify() const {
        if (!isIrreducible()) {
            return Classification::Reducible;
        }

        return period() == 1
            ? Classification::Ergodic
            : Classification::IrreduciblePeriodic;
    }

    // --------------------------------------------------------
    // 5. STATIONARY DISTRIBUTION
    // --------------------------------------------------------

    StationaryResult stationary(
        double tolerance = 1e-12,
        int maxIterations = 100000
    ) const {
        if (!isfinite(tolerance) || tolerance <= 0 ||
            maxIterations <= 0) {
            throw ProbabilityException("Invalid iteration settings.");
        }

        vector<double> current(n, 1.0 / n);

        for (int iteration = 1; iteration <= maxIterations; ++iteration) {
            vector<double> next = multiply(current);

            double residual = maximumDifference(current, next);

            current = move(next);

            if (residual < tolerance) {
                return {
                    current,
                    iteration,
                    true,
                    residual
                };
            }
        }

        return {
            current,
            maxIterations,
            false,
            maximumDifference(current, multiply(current))
        };
    }

    // --------------------------------------------------------
    // 6. MONTE CARLO SIMULATION
    // --------------------------------------------------------

    SimulationResult simulate(
        int initialState,
        int steps,
        uint64_t seed
    ) const {
        if (initialState < 0 ||
            static_cast<size_t>(initialState) >= n ||
            steps < 0) {
            throw ProbabilityException("Invalid simulation settings.");
        }

        mt19937_64 generator(seed);

        SimulationResult result;
        result.path.reserve(static_cast<size_t>(steps) + 1);

        result.transitionCounts.assign(
            n, vector<int>(n, 0)
        );

        vector<int> visits(n, 0);

        int current = initialState;
        result.path.push_back(current);
        visits[current]++;

        for (int step = 0; step < steps; ++step) {
            int following = sampleNext(current, generator);

            result.transitionCounts[current][following]++;
            result.path.push_back(following);

            visits[following]++;
            current = following;
        }

        result.empirical.resize(n);

        const double total = static_cast<double>(steps + 1);

        for (size_t i = 0; i < n; ++i) {
            result.empirical[i] = visits[i] / total;
        }

        return result;
    }
};

// ============================================================
// 7. MARTINGALE DIFFERENCE PROCESS
// ============================================================

class MartingaleAnalyzer {
private:
    const MarkovChain& chain;
    vector<double> conditionalMeans;

public:
    using Reward = function<double(int, int)>;

    MartingaleAnalyzer(
        const MarkovChain& model,
        Reward reward
    )
        : chain(model) {

        const auto& matrix = chain.matrix();

        conditionalMeans.resize(chain.size(), 0.0);

        for (size_t source = 0; source < chain.size(); ++source) {
            for (size_t destination = 0;
                 destination < chain.size();
                 ++destination) {

                double value = reward(
                    static_cast<int>(source),
                    static_cast<int>(destination)
                );

                if (!isfinite(value)) {
                    throw ProbabilityException("Invalid reward.");
                }

                conditionalMeans[source] +=
                    matrix[source][destination] * value;
            }
        }

        this->reward = move(reward);
    }

    vector<double> analyze(const vector<int>& path) const {
        if (path.size() < 2) {
            throw ProbabilityException("Insufficient observations.");
        }

        vector<double> martingale{0.0};

        for (size_t i = 0; i + 1 < path.size(); ++i) {
            int source = path[i];
            int destination = path[i + 1];

            if (source < 0 || destination < 0 ||
                static_cast<size_t>(source) >= chain.size() ||
                static_cast<size_t>(destination) >= chain.size() ||
                chain.matrix()[source][destination] <= 0) {

                throw ProbabilityException("Invalid observed transition.");
            }

            double increment =
                reward(source, destination) -
                conditionalMeans[source];

            martingale.push_back(
                martingale.back() + increment
            );
        }

        return martingale;
    }

    bool verify(double tolerance = 1e-10) const {
        const auto& matrix = chain.matrix();

        for (size_t source = 0; source < chain.size(); ++source) {
            double conditionalExpectation = 0.0;

            for (size_t destination = 0;
                 destination < chain.size();
                 ++destination) {

                double residual =
                    reward(
                        static_cast<int>(source),
                        static_cast<int>(destination)
                    ) - conditionalMeans[source];

                conditionalExpectation +=
                    matrix[source][destination] * residual;
            }

            if (abs(conditionalExpectation) > tolerance) {
                return false;
            }
        }

        return true;
    }

private:
    Reward reward;
};

// ============================================================
// 8. LONG-RUN REWARD
// ============================================================

double expectedLongRunReward(
    const vector<double>& stationary,
    const vector<double>& rewards
) {
    if (stationary.size() != rewards.size()) {
        throw ProbabilityException("Reward dimension mismatch.");
    }

    double result = 0.0;

    for (size_t i = 0; i < rewards.size(); ++i) {
        result += stationary[i] * rewards[i];
    }

    return result;
}

// ============================================================
// 9. PRESENTATION AND EXECUTION
// ============================================================

void printDistribution(
    const vector<string>& labels,
    const vector<double>& distribution
) {
    cout << fixed << setprecision(6);

    for (size_t i = 0; i < labels.size(); ++i) {
        cout << setw(12) << left << labels[i]
             << distribution[i] << '\n';
    }
}

int main() {
    try {
        cout << "ADVANCED PROBABILITY ENGINE\n";
        cout << "===========================\n";

        MarkovChain weather(
            {
                {0.70, 0.20, 0.10},
                {0.25, 0.50, 0.25},
                {0.20, 0.30, 0.50}
            },
            {"Sunny", "Cloudy", "Rainy"}
        );

        cout << "\n1. STATIONARY DISTRIBUTION\n";

        StationaryResult stationary = weather.stationary();

        if (!stationary.converged) {
            throw runtime_error(
                "Stationary iteration did not converge."
            );
        }

        printDistribution(
            weather.getLabels(),
            stationary.distribution
        );

        cout << "Iterations: " << stationary.iterations << '\n';
        cout << "Residual: " << stationary.residual << '\n';

        cout << "\n2. CHAIN CLASSIFICATION\n";

        cout << "Irreducible: "
             << boolalpha << weather.isIrreducible() << '\n';

        cout << "Period: " << weather.period() << '\n';

        cout << "Classification: "
             << classificationName(weather.classify()) << '\n';

        cout << "\n3. MONTE CARLO SIMULATION\n";

        SimulationResult simulation = weather.simulate(
            0, 100000, 2026
        );

        printDistribution(
            weather.getLabels(),
            simulation.empirical
        );

        cout << "\n4. DISTRIBUTION ERROR\n";

        double maximumError = maximumDifference(
            stationary.distribution,
            simulation.empirical
        );

        cout << "Maximum absolute error: "
             << maximumError << '\n';

        cout << "\n5. LONG-RUN REWARD\n";

        vector<double> rewards = {100.0, 60.0, 20.0};

        cout << "Expected reward: "
             << expectedLongRunReward(
                 stationary.distribution,
                 rewards
             ) << '\n';

        cout << "\n6. MARTINGALE ANALYSIS\n";

        auto rewardFunction = [](int source, int destination) {
            return static_cast<double>(destination - source);
        };

        MartingaleAnalyzer analyzer(
            weather,
            rewardFunction
        );

        cout << "Conditional identities verified: "
             << analyzer.verify() << '\n';

        vector<int> shortPath(
            simulation.path.begin(),
            simulation.path.begin() + 101
        );

        vector<double> martingale =
            analyzer.analyze(shortPath);

        cout << "First 10 martingale values:\n";

        for (size_t i = 0;
             i < min<size_t>(10, martingale.size());
             ++i) {
            cout << martingale[i] << ' ';
        }

        cout << '\n';

        cout << "\n7. PERIODIC CHAIN\n";

        MarkovChain periodic(
            {
                {0.0, 1.0},
                {1.0, 0.0}
            },
            {"A", "B"}
        );

        cout << "Period: " << periodic.period() << '\n';

        cout << "Classification: "
             << classificationName(periodic.classify()) << '\n';

        StationaryResult periodicResult =
            periodic.stationary(1e-12, 100);

        cout << "Power iteration converged: "
             << periodicResult.converged << '\n';

        cout << "\n8. REDUCIBLE CHAIN\n";

        MarkovChain reducible(
            {
                {0.8, 0.2},
                {0.0, 1.0}
            },
            {"Transient", "Absorbing"}
        );

        cout << "Classification: "
             << classificationName(reducible.classify()) << '\n';

        cout << "\n9. INPUT VALIDATION\n";

        try {
            MarkovChain invalid(
                {
                    {0.4, 0.4},
                    {0.2, 0.9}
                },
                {"A", "B"}
            );
        } catch (const ProbabilityException& error) {
            cout << "Invalid matrix rejected: "
                 << error.what() << '\n';
        }

        cout << "\nExecution completed successfully.\n";

    } catch (const exception& error) {
        cerr << "Execution failed: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
