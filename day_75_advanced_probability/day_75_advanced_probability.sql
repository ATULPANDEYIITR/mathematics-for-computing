import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.SplittableRandom;
import java.util.stream.Collectors;

/*
 * Advanced Probability: Enterprise Stochastic Modeling
 *
 * Java 17 implementation.
 *
 * Features:
 * - Immutable stochastic models
 * - Finite-state Markov chains
 * - Stationary distributions
 * - Irreducibility and periodicity
 * - Ergodicity classification
 * - Martingale difference analysis
 * - Simulation services
 * - Statistical reporting
 * - Domain validation and exceptions
 */

public class AdvancedProbability {

    // ========================================================
    // 1. DOMAIN EXCEPTIONS
    // ========================================================

    static class ProbabilityException extends RuntimeException {
        ProbabilityException(String message) {
            super(message);
        }
    }

    // ========================================================
    // 2. ENUMERATIONS
    // ========================================================

    enum ChainType {
        ERGODIC,
        IRREDUCIBLE_PERIODIC,
        REDUCIBLE
    }

    enum SimulationStatus {
        CREATED,
        RUNNING,
        COMPLETED,
        FAILED
    }

    // ========================================================
    // 3. IMMUTABLE RESULT TYPES
    // ========================================================

    record StationaryResult(
        List<Double> probabilities,
        int iterations,
        boolean converged,
        double residual
    ) {
        StationaryResult {
            probabilities = List.copyOf(probabilities);
        }
    }

    record SimulationReport(
        String simulationId,
        SimulationStatus status,
        long transitions,
        List<String> path,
        Map<String, Double> empiricalDistribution,
        double maximumError
    ) {
        SimulationReport {
            path = List.copyOf(path);
            empiricalDistribution = Map.copyOf(
                empiricalDistribution
            );
        }
    }

    record Transition(
        String source,
        String destination,
        double probability
    ) {
        Transition {
            Objects.requireNonNull(source);
            Objects.requireNonNull(destination);

            if (source.isBlank() || destination.isBlank()) {
                throw new ProbabilityException(
                    "Transition states cannot be blank."
                );
            }

            if (!Double.isFinite(probability) ||
                probability < 0 || probability > 1) {
                throw new ProbabilityException(
                    "Invalid transition probability."
                );
            }
        }
    }

    // ========================================================
    // 4. STOCHASTIC MODEL
    // ========================================================

    static final class MarkovModel {

        private final List<String> states;
        private final Map<String, Integer> stateIndex;
        private final double[][] matrix;
        private final int size;

        MarkovModel(
            List<String> states,
            List<Transition> transitions
        ) {
            Objects.requireNonNull(states);
            Objects.requireNonNull(transitions);

            if (states.isEmpty()) {
                throw new ProbabilityException(
                    "At least one state is required."
                );
            }

            this.states = List.copyOf(states);
            this.size = states.size();

            if (new HashSet<>(states).size() != size ||
                states.stream().anyMatch(
                    state -> state == null || state.isBlank()
                )) {
                throw new ProbabilityException(
                    "State identifiers must be nonblank and unique."
                );
            }

            Map<String, Integer> indexes = new HashMap<>();

            for (int i = 0; i < size; i++) {
                indexes.put(states.get(i), i);
            }

            this.stateIndex = Collections.unmodifiableMap(indexes);
            this.matrix = new double[size][size];

            Set<String> suppliedTransitions = new HashSet<>();

            for (Transition transition : transitions) {
                Integer source = indexes.get(transition.source());
                Integer destination = indexes.get(
                    transition.destination()
                );

                if (source == null || destination == null) {
                    throw new ProbabilityException(
                        "Transition references an unknown state."
                    );
                }

                String key = source + ":" + destination;

                if (!suppliedTransitions.add(key)) {
                    throw new ProbabilityException(
                        "Duplicate transition definition."
                    );
                }

                matrix[source][destination] =
                    transition.probability();
            }

            validateRows();
        }

        private void validateRows() {
            for (int i = 0; i < size; i++) {
                double sum = Arrays.stream(matrix[i]).sum();

                if (Math.abs(sum - 1.0) > 1e-10) {
                    throw new ProbabilityException(
                        "Transition row " + i +
                        " must sum to one. Actual: " + sum
                    );
                }
            }
        }

        int size() {
            return size;
        }

        List<String> states() {
            return states;
        }

        int indexOf(String state) {
            Integer index = stateIndex.get(state);

            if (index == null) {
                throw new ProbabilityException(
                    "Unknown state: " + state
                );
            }

            return index;
        }

        double probability(int source, int destination) {
            return matrix[source][destination];
        }

        double[] row(int state) {
            return matrix[state].clone();
        }

        double[] multiply(double[] distribution) {
            if (distribution.length != size) {
                throw new ProbabilityException(
                    "Distribution dimension mismatch."
                );
            }

            double[] result = new double[size];

            for (int i = 0; i < size; i++) {
                if (!Double.isFinite(distribution[i]) ||
                    distribution[i] < 0) {
                    throw new ProbabilityException(
                        "Invalid distribution entry."
                    );
                }

                for (int j = 0; j < size; j++) {
                    result[j] +=
                        distribution[i] * matrix[i][j];
                }
            }

            return result;
        }

        // ----------------------------------------------------
        // 5. GRAPH ANALYSIS
        // ----------------------------------------------------

        private int[] distancesFrom(int start) {
            if (start < 0 || start >= size) {
                throw new ProbabilityException(
                    "Invalid starting state."
                );
            }

            int[] distance = new int[size];
            Arrays.fill(distance, -1);

            ArrayDeque<Integer> queue = new ArrayDeque<>();

            distance[start] = 0;
            queue.add(start);

            while (!queue.isEmpty()) {
                int current = queue.remove();

                for (int destination = 0;
                     destination < size;
                     destination++) {

                    if (matrix[current][destination] > 0 &&
                        distance[destination] == -1) {

                        distance[destination] =
                            distance[current] + 1;

                        queue.add(destination);
                    }
                }
            }

            return distance;
        }

        boolean isIrreducible() {
            for (int state = 0; state < size; state++) {
                int[] distances = distancesFrom(state);

                for (int distance : distances) {
                    if (distance < 0) {
                        return false;
                    }
                }
            }

            return true;
        }

        private int gcd(int a, int b) {
            return b == 0 ? a : gcd(b, a % b);
        }

        int period(int start) {
            int[] distances = distancesFrom(start);

            for (int distance : distances) {
                if (distance < 0) {
                    throw new ProbabilityException(
                        "Period requires an irreducible chain."
                    );
                }
            }

            int result = 0;

            for (int i = 0; i < size; i++) {
                for (int j = 0; j < size; j++) {
                    if (matrix[i][j] > 0) {
                        int difference = Math.abs(
                            distances[i] + 1 - distances[j]
                        );

                        result = gcd(result, difference);
                    }
                }
            }

            return result;
        }

        ChainType classify() {
            if (!isIrreducible()) {
                return ChainType.REDUCIBLE;
            }

            return period(0) == 1
                ? ChainType.ERGODIC
                : ChainType.IRREDUCIBLE_PERIODIC;
        }

        // ----------------------------------------------------
        // 6. STATIONARY DISTRIBUTION SERVICE
        // ----------------------------------------------------

        StationaryResult calculateStationary(
            double tolerance,
            int maxIterations
        ) {
            if (!Double.isFinite(tolerance) ||
                tolerance <= 0 ||
                maxIterations <= 0) {
                throw new ProbabilityException(
                    "Invalid stationary solver configuration."
                );
            }

            double[] current = new double[size];
            Arrays.fill(current, 1.0 / size);

            for (int iteration = 1;
                 iteration <= maxIterations;
                 iteration++) {

                double[] next = multiply(current);

                double residual = 0;

                for (int i = 0; i < size; i++) {
                    residual = Math.max(
                        residual,
                        Math.abs(next[i] - current[i])
                    );
                }

                current = next;

                if (residual < tolerance) {
                    return result(
                        current,
                        iteration,
                        true,
                        residual
                    );
                }
            }

            double[] next = multiply(current);

            double residual = 0;

            for (int i = 0; i < size; i++) {
                residual = Math.max(
                    residual,
                    Math.abs(next[i] - current[i])
                );
            }

            return result(
                current,
                maxIterations,
                false,
                residual
            );
        }

        private StationaryResult result(
            double[] probabilities,
            int iterations,
            boolean converged,
            double residual
        ) {
            List<Double> values = Arrays.stream(probabilities)
                .boxed()
                .collect(Collectors.toList());

            return new StationaryResult(
                values,
                iterations,
                converged,
                residual
            );
        }
    }

    // ========================================================
    // 7. MARTINGALE POLICY AND ANALYSIS
    // ========================================================

    @FunctionalInterface
    interface RewardPolicy {
        double reward(int source, int destination);
    }

    static final class MartingaleService {

        private final MarkovModel model;
        private final RewardPolicy reward;
        private final double[] conditionalMeans;

        MartingaleService(
            MarkovModel model,
            RewardPolicy reward
        ) {
            this.model = Objects.requireNonNull(model);
            this.reward = Objects.requireNonNull(reward);

            this.conditionalMeans = new double[model.size()];

            for (int source = 0;
                 source < model.size();
                 source++) {

                for (int destination = 0;
                     destination < model.size();
                     destination++) {

                    double value = reward.reward(
                        source,
                        destination
                    );

                    if (!Double.isFinite(value)) {
                        throw new ProbabilityException(
                            "Reward must be finite."
                        );
                    }

                    conditionalMeans[source] +=
                        model.probability(source, destination) * value;
                }
            }
        }

        double increment(int source, int destination) {
            return reward.reward(source, destination)
                - conditionalMeans[source];
        }

        boolean verify(double tolerance) {
            for (int source = 0;
                 source < model.size();
                 source++) {

                double expectation = 0;

                for (int destination = 0;
                     destination < model.size();
                     destination++) {

                    expectation +=
                        model.probability(source, destination) *
                        increment(source, destination);
                }

                if (Math.abs(expectation) > tolerance) {
                    return false;
                }
            }

            return true;
        }

        List<Double> evaluate(List<Integer> path) {
            if (path.size() < 2) {
                throw new ProbabilityException(
                    "Martingale path requires two observations."
                );
            }

            List<Double> values = new ArrayList<>();
            double cumulative = 0;

            values.add(cumulative);

            for (int i = 0; i < path.size() - 1; i++) {
                int source = path.get(i);
                int destination = path.get(i + 1);

                if (source < 0 || destination < 0 ||
                    source >= model.size() ||
                    destination >= model.size() ||
                    model.probability(source, destination) <= 0) {

                    throw new ProbabilityException(
                        "Observed transition is impossible."
                    );
                }

                cumulative += increment(source, destination);
                values.add(cumulative);
            }

            return List.copyOf(values);
        }

        double[] conditionalMeans() {
            return conditionalMeans.clone();
        }
    }

    // ========================================================
    // 8. ENTERPRISE SIMULATION SERVICE
    // ========================================================

    static final class SimulationService {

        private final MarkovModel model;
        private final long seed;

        SimulationService(MarkovModel model, long seed) {
            this.model = Objects.requireNonNull(model);
            this.seed = seed;
        }

        SimulationReport execute(
            int initialState,
            int steps,
            StationaryResult stationary
        ) {
            if (initialState < 0 ||
                initialState >= model.size() ||
                steps < 0) {
                throw new ProbabilityException(
                    "Invalid simulation request."
                );
            }

            if (stationary.probabilities().size() != model.size()) {
                throw new ProbabilityException(
                    "Stationary model mismatch."
                );
            }

            String simulationId = "SIM-" +
                Long.toUnsignedString(seed);

            SimulationStatus status = SimulationStatus.CREATED;

            try {
                status = SimulationStatus.RUNNING;

                SplittableRandom random =
                    new SplittableRandom(seed);

                int current = initialState;

                long[] visits = new long[model.size()];
                List<String> path = new ArrayList<>();

                path.add(model.states().get(current));
                visits[current]++;

                for (int step = 0; step < steps; step++) {
                    double draw = random.nextDouble();
                    double cumulative = 0;

                    int following = model.size() - 1;

                    for (int destination = 0;
                         destination < model.size();
                         destination++) {

                        cumulative +=
                            model.probability(current, destination);

                        if (draw < cumulative) {
                            following = destination;
                            break;
                        }
                    }

                    current = following;
                    visits[current]++;

                    path.add(model.states().get(current));
                }

                Map<String, Double> empirical = new HashMap<>();
                double total = steps + 1.0;
                double maximumError = 0;

                for (int i = 0; i < model.size(); i++) {
                    double observed = visits[i] / total;

                    empirical.put(
                        model.states().get(i),
                        observed
                    );

                    maximumError = Math.max(
                        maximumError,
                        Math.abs(
                            observed -
                            stationary.probabilities().get(i)
                        )
                    );
                }

                status = SimulationStatus.COMPLETED;

                return new SimulationReport(
                    simulationId,
                    status,
                    steps,
                    path,
                    empirical,
                    maximumError
                );

            } catch (RuntimeException exception) {
                status = SimulationStatus.FAILED;
                throw new ProbabilityException(
                    "Simulation failed with status " + status +
                    ": " + exception.getMessage()
                );
            }
        }
    }

    // ========================================================
    // 9. LONG-RUN EXPECTED REWARD
    // ========================================================

    static double expectedLongRunReward(
        StationaryResult stationary,
        List<Double> rewards
    ) {
        if (stationary.probabilities().size() != rewards.size()) {
            throw new ProbabilityException(
                "Reward and stationary dimensions differ."
            );
        }

        double result = 0;

        for (int i = 0; i < rewards.size(); i++) {
            result +=
                stationary.probabilities().get(i) * rewards.get(i);
        }

        return result;
    }

    // ========================================================
    // 10. SAMPLE MODEL AND EXECUTION
    // ========================================================

    private static MarkovModel createWeatherModel() {
        List<String> states = List.of(
            "Sunny",
            "Cloudy",
            "Rainy"
        );

        List<Transition> transitions = List.of(
            new Transition("Sunny", "Sunny", 0.70),
            new Transition("Sunny", "Cloudy", 0.20),
            new Transition("Sunny", "Rainy", 0.10),

            new Transition("Cloudy", "Sunny", 0.25),
            new Transition("Cloudy", "Cloudy", 0.50),
            new Transition("Cloudy", "Rainy", 0.25),

            new Transition("Rainy", "Sunny", 0.20),
            new Transition("Rainy", "Cloudy", 0.30),
            new Transition("Rainy", "Rainy", 0.50)
        );

        return new MarkovModel(states, transitions);
    }

    public static void main(String[] args) {
        try {
            System.out.println(
                "ADVANCED PROBABILITY: ENTERPRISE MODEL"
            );

            MarkovModel model = createWeatherModel();

            // Stationary analysis.
            StationaryResult stationary =
                model.calculateStationary(1e-12, 100000);

            if (!stationary.converged()) {
                throw new ProbabilityException(
                    "Stationary solver did not converge."
                );
            }

            System.out.println("\n1. STATIONARY DISTRIBUTION");

            for (int i = 0; i < model.size(); i++) {
                System.out.printf(
                    "%-12s %.6f%n",
                    model.states().get(i),
                    stationary.probabilities().get(i)
                );
            }

            System.out.println("Iterations: " + stationary.iterations());
            System.out.println("Residual: " + stationary.residual());

            // Chain properties.
            System.out.println("\n2. ERGODICITY");

            System.out.println(
                "Irreducible: " + model.isIrreducible()
            );

            System.out.println(
                "Period: " + model.period(0)
            );

            System.out.println(
                "Classification: " + model.classify()
            );

            // Enterprise simulation.
            System.out.println("\n3. SIMULATION");

            SimulationService service =
                new SimulationService(model, 2026);

            SimulationReport report = service.execute(
                model.indexOf("Sunny"),
                100000,
                stationary
            );

            System.out.println("Simulation ID: " +
                report.simulationId());

            System.out.println("Status: " + report.status());

            System.out.println("Transitions: " +
                report.transitions());

            System.out.println("Empirical distribution:");

            report.empiricalDistribution().forEach(
                (state, probability) ->
                    System.out.printf(
                        "%-12s %.6f%n",
                        state,
                        probability
                    )
            );

            System.out.println(
                "Maximum error: " + report.maximumError()
            );

            // Martingale analysis.
            System.out.println("\n4. MARTINGALE");

            MartingaleService martingale =
                new MartingaleService(
                    model,
                    (source, destination) ->
                        destination - source
                );

            System.out.println(
                "Conditional expectation verified: " +
                martingale.verify(1e-10)
            );

            List<Integer> path = List.of(
                0, 1, 2, 1, 0, 0, 2, 1
            );

            System.out.println(
                "Martingale values: " +
                martingale.evaluate(path)
            );

            // Long-run reward.
            System.out.println("\n5. LONG-RUN REWARD");

            double expectedReward = expectedLongRunReward(
                stationary,
                List.of(100.0, 60.0, 20.0)
            );

            System.out.println(
                "Expected reward: " + expectedReward
            );

            // Periodic-chain test.
            System.out.println("\n6. PERIODIC MODEL");

            MarkovModel periodic = new MarkovModel(
                List.of("A", "B"),
                List.of(
                    new Transition("A", "B", 1),
                    new Transition("B", "A", 1)
                )
            );

            System.out.println(
                "Period: " + periodic.period(0)
            );

            System.out.println(
                "Classification: " + periodic.classify()
            );

            System.out.println(
                "Power iteration converged: " +
                periodic.calculateStationary(1e-12, 100).converged()
            );

            // Reducible-chain test.
            System.out.println("\n7. REDUCIBLE MODEL");

            MarkovModel reducible = new MarkovModel(
                List.of("Transient", "Absorbing"),
                List.of(
                    new Transition("Transient", "Transient", 0.8),
                    new Transition("Transient", "Absorbing", 0.2),
                    new Transition("Absorbing", "Transient", 0.0),
                    new Transition("Absorbing", "Absorbing", 1.0)
                )
            );

            System.out.println(
                "Classification: " + reducible.classify()
            );

            System.out.println("\n8. VALIDATION");

            try {
                new Transition("A", "B", 1.5);
            } catch (ProbabilityException exception) {
                System.out.println(
                    "Invalid transition rejected: " +
                    exception.getMessage()
                );
            }

            System.out.println("\nExecution completed.");

        } catch (ProbabilityException exception) {
            System.err.println(
                "Probability error: " + exception.getMessage()
            );

            System.exitCode(1);
        } catch (RuntimeException exception) {
            System.err.println(
                "Execution error: " + exception.getMessage()
            );

            System.exitCode(1);
        }
    }
}
