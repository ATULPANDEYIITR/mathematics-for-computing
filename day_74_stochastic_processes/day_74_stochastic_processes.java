import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Random;
import java.util.Set;
import java.util.LinkedHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

/**
 * STOCHASTIC PROCESSES
 *
 * Enterprise-oriented stochastic simulation system.
 * Java 17, standard library only.
 */
public class StochasticProcesses {

    enum State {
        OPERATIONAL,
        DEGRADED,
        FAILED,
        RECOVERING
    }

    enum RunStatus {
        CREATED,
        RUNNING,
        COMPLETED,
        ABSORBED,
        FAILED
    }

    enum EventType {
        TRANSITION,
        ABSORPTION,
        VALIDATION_FAILURE
    }

    static class DomainException extends RuntimeException {
        DomainException(String message) {
            super(message);
        }
    }

    static class TransitionValidationException extends DomainException {
        TransitionValidationException(String message) {
            super(message);
        }
    }

    static class SimulationException extends DomainException {
        SimulationException(String message) {
            super(message);
        }
    }

    record Transition(
        State destination,
        double probability
    ) {
        Transition {
            Objects.requireNonNull(destination);

            if (
                !Double.isFinite(probability) ||
                probability < 0 ||
                probability > 1
            ) {
                throw new TransitionValidationException(
                    "Probability must be between zero and one."
                );
            }
        }
    }

    record SimulationEvent(
        long sequence,
        EventType type,
        State previousState,
        State currentState,
        int step
    ) {}

    record SimulationResult(
        String runId,
        State initialState,
        State finalState,
        List<State> path,
        int stepsExecuted,
        RunStatus status,
        long seed
    ) {
        SimulationResult {
            path = List.copyOf(path);
        }
    }

    record SimulationConfiguration(
        State initialState,
        int maximumSteps,
        long seed
    ) {
        SimulationConfiguration {
            Objects.requireNonNull(initialState);

            if (maximumSteps < 0) {
                throw new IllegalArgumentException(
                    "Maximum steps cannot be negative."
                );
            }
        }
    }

    static final class TransitionMatrix {
        private static final double TOLERANCE = 1e-9;

        private final Map<State, List<Transition>> matrix;

        TransitionMatrix(Map<State, List<Transition>> definitions) {
            Objects.requireNonNull(definitions);

            if (definitions.isEmpty()) {
                throw new TransitionValidationException(
                    "Transition matrix cannot be empty."
                );
            }

            EnumMap<State, List<Transition>> copy =
                new EnumMap<>(State.class);

            for (State source : State.values()) {
                if (!definitions.containsKey(source)) {
                    continue;
                }

                List<Transition> edges = definitions.get(source);

                if (edges == null || edges.isEmpty()) {
                    throw new TransitionValidationException(
                        "Every defined state requires outgoing transitions."
                    );
                }

                double total = 0;

                for (Transition edge : edges) {
                    if (!definitions.containsKey(edge.destination())) {
                        throw new TransitionValidationException(
                            "Undefined destination: " + edge.destination()
                        );
                    }

                    total += edge.probability();
                }

                if (Math.abs(total - 1.0) > TOLERANCE) {
                    throw new TransitionValidationException(
                        "Transition probabilities for " +
                        source + " sum to " + total
                    );
                }

                copy.put(source, List.copyOf(edges));
            }

            this.matrix = Collections.unmodifiableMap(copy);
        }

        Set<State> states() {
            return Collections.unmodifiableSet(matrix.keySet());
        }

        boolean contains(State state) {
            return matrix.containsKey(state);
        }

        List<Transition> outgoing(State state) {
            List<Transition> edges = matrix.get(state);

            if (edges == null) {
                throw new TransitionValidationException(
                    "Unknown state: " + state
                );
            }

            return edges;
        }

        boolean isAbsorbing(State state) {
            List<Transition> edges = outgoing(state);

            return edges.size() == 1
                && edges.get(0).destination() == state
                && Math.abs(edges.get(0).probability() - 1.0) < TOLERANCE;
        }

        State nextState(State current, Random random) {
            double value = random.nextDouble();
            double cumulative = 0;

            List<Transition> edges = outgoing(current);

            for (Transition edge : edges) {
                cumulative += edge.probability();

                if (value < cumulative) {
                    return edge.destination();
                }
            }

            return edges.get(edges.size() - 1).destination();
        }

        Map<State, Map<State, Double>> asMap() {
            Map<State, Map<State, Double>> result =
                new EnumMap<>(State.class);

            for (State source : matrix.keySet()) {
                Map<State, Double> row =
                    new EnumMap<>(State.class);

                for (State destination : matrix.keySet()) {
                    row.put(destination, 0.0);
                }

                for (Transition edge : outgoing(source)) {
                    row.put(edge.destination(), edge.probability());
                }

                result.put(source, Collections.unmodifiableMap(row));
            }

            return Collections.unmodifiableMap(result);
        }
    }

    interface SimulationListener {
        void onEvent(SimulationEvent event);
    }

    static final class SimulationService {
        private final TransitionMatrix matrix;
        private final AtomicLong runCounter = new AtomicLong();

        SimulationService(TransitionMatrix matrix) {
            this.matrix = Objects.requireNonNull(matrix);
        }

        SimulationResult execute(
            SimulationConfiguration configuration,
            SimulationListener listener
        ) {
            Objects.requireNonNull(configuration);

            if (!matrix.contains(configuration.initialState())) {
                throw new SimulationException(
                    "Initial state does not exist."
                );
            }

            long sequence = runCounter.incrementAndGet();
            String runId = "RUN-" + sequence;

            Random random = new Random(configuration.seed());

            List<State> path = new ArrayList<>();
            State current = configuration.initialState();

            path.add(current);

            int executed = 0;
            RunStatus status = RunStatus.RUNNING;

            while (executed < configuration.maximumSteps()) {
                if (matrix.isAbsorbing(current)) {
                    status = RunStatus.ABSORBED;
                    break;
                }

                State previous = current;

                current = matrix.nextState(current, random);
                path.add(current);
                executed++;

                if (listener != null) {
                    listener.onEvent(
                        new SimulationEvent(
                            sequence,
                            EventType.TRANSITION,
                            previous,
                            current,
                            executed
                        )
                    );
                }
            }

            if (status == RunStatus.RUNNING) {
                status = matrix.isAbsorbing(current)
                    ? RunStatus.ABSORBED
                    : RunStatus.COMPLETED;
            }

            if (
                status == RunStatus.ABSORBED &&
                listener != null
            ) {
                listener.onEvent(
                    new SimulationEvent(
                        sequence,
                        EventType.ABSORPTION,
                        current,
                        current,
                        executed
                    )
                );
            }

            return new SimulationResult(
                runId,
                configuration.initialState(),
                current,
                path,
                executed,
                status,
                configuration.seed()
            );
        }
    }

    record ApprovalPolicy(
        int requiredApprovals,
        int requiredChecks,
        boolean requireNoOpenDiscussions,
        boolean requireUpdatedSource,
        boolean requireLinearHistory
    ) {
        ApprovalPolicy {
            if (requiredApprovals < 0 || requiredChecks < 0) {
                throw new IllegalArgumentException(
                    "Requirements cannot be negative."
                );
            }
        }
    }

    record RepositoryChange(
        String pullRequestId,
        String sourceBranch,
        String targetBranch,
        boolean open,
        boolean draft,
        boolean sourceUpdated,
        boolean conflictFree,
        boolean linearHistory,
        int validApprovals,
        int openDiscussions,
        Map<String, Boolean> checks
    ) {
        RepositoryChange {
            if (
                pullRequestId == null ||
                pullRequestId.isBlank() ||
                sourceBranch == null ||
                targetBranch == null ||
                sourceBranch.isBlank() ||
                targetBranch.isBlank()
            ) {
                throw new IllegalArgumentException(
                    "Pull request and branch identifiers are required."
                );
            }

            if (validApprovals < 0 || openDiscussions < 0) {
                throw new IllegalArgumentException(
                    "Counts cannot be negative."
                );
            }

            checks = Map.copyOf(checks);
        }
    }

    record EligibilityResult(
        boolean eligible,
        List<String> violations
    ) {
        EligibilityResult {
            violations = List.copyOf(violations);
        }
    }

    static final class MergeEligibilityService {
        private final ApprovalPolicy policy;

        MergeEligibilityService(ApprovalPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        EligibilityResult evaluate(RepositoryChange change) {
            List<String> violations = new ArrayList<>();

            if (change.sourceBranch().equals(change.targetBranch())) {
                violations.add("Source and target branches must differ.");
            }

            if (!change.open()) {
                violations.add("Pull request is not open.");
            }

            if (change.draft()) {
                violations.add("Draft pull request cannot be merged.");
            }

            if (
                policy.requireUpdatedSource() &&
                !change.sourceUpdated()
            ) {
                violations.add("Source branch is not synchronized.");
            }

            if (!change.conflictFree()) {
                violations.add("Merge conflicts remain.");
            }

            if (
                change.validApprovals() <
                policy.requiredApprovals()
            ) {
                violations.add("Insufficient eligible approvals.");
            }

            if (
                policy.requireNoOpenDiscussions() &&
                change.openDiscussions() > 0
            ) {
                violations.add("Review discussions remain open.");
            }

            if (
                policy.requireLinearHistory() &&
                !change.linearHistory()
            ) {
                violations.add("Linear history is required.");
            }

            long passingChecks = change.checks()
                .values()
                .stream()
                .filter(Boolean::booleanValue)
                .count();

            if (passingChecks < policy.requiredChecks()) {
                violations.add("Required status checks have not passed.");
            }

            return new EligibilityResult(
                violations.isEmpty(),
                violations
            );
        }
    }

    static final class MonteCarloService {

        record Estimate(
            int experiments,
            int successes,
            double probability,
            double standardError,
            double lower95,
            double upper95,
            double meanAbsorptionTime
        ) {}

        Estimate estimate(
            SimulationService service,
            State initialState,
            State targetState,
            int experiments,
            int maximumSteps,
            long seed
        ) {
            if (experiments <= 0 || maximumSteps < 0) {
                throw new IllegalArgumentException(
                    "Invalid Monte Carlo configuration."
                );
            }

            Random random = new Random(seed);

            int successes = 0;
            long totalTime = 0;

            for (int i = 0; i < experiments; i++) {
                long experimentSeed = random.nextLong();

                SimulationResult result = service.execute(
                    new SimulationConfiguration(
                        initialState,
                        maximumSteps,
                        experimentSeed
                    ),
                    null
                );

                if (result.finalState() == targetState) {
                    successes++;
                    totalTime += result.stepsExecuted();
                }
            }

            double probability =
                (double) successes / experiments;

            double standardError = Math.sqrt(
                probability * (1.0 - probability) / experiments
            );

            double meanTime = successes == 0
                ? Double.NaN
                : (double) totalTime / successes;

            return new Estimate(
                experiments,
                successes,
                probability,
                standardError,
                Math.max(0, probability - 1.96 * standardError),
                Math.min(1, probability + 1.96 * standardError),
                meanTime
            );
        }
    }

    static TransitionMatrix buildReliabilityMatrix() {
        Map<State, List<Transition>> definitions =
            new EnumMap<>(State.class);

        definitions.put(State.OPERATIONAL, List.of(
            new Transition(State.OPERATIONAL, 0.65),
            new Transition(State.DEGRADED, 0.25),
            new Transition(State.FAILED, 0.10)
        ));

        definitions.put(State.DEGRADED, List.of(
            new Transition(State.OPERATIONAL, 0.30),
            new Transition(State.DEGRADED, 0.40),
            new Transition(State.FAILED, 0.30)
        ));

        definitions.put(State.FAILED, List.of(
            new Transition(State.FAILED, 1.0)
        ));

        return new TransitionMatrix(definitions);
    }

    static TransitionMatrix buildWeatherMatrix() {
        Map<State, List<Transition>> definitions =
            new EnumMap<>(State.class);

        definitions.put(State.OPERATIONAL, List.of(
            new Transition(State.OPERATIONAL, 0.70),
            new Transition(State.DEGRADED, 0.20),
            new Transition(State.RECOVERING, 0.10)
        ));

        definitions.put(State.DEGRADED, List.of(
            new Transition(State.OPERATIONAL, 0.30),
            new Transition(State.DEGRADED, 0.40),
            new Transition(State.RECOVERING, 0.30)
        ));

        definitions.put(State.RECOVERING, List.of(
            new Transition(State.OPERATIONAL, 0.50),
            new Transition(State.DEGRADED, 0.25),
            new Transition(State.RECOVERING, 0.25)
        ));

        return new TransitionMatrix(definitions);
    }

    static void demonstrateGovernance() {
        System.out.println("\nENTERPRISE MERGE GOVERNANCE");

        ApprovalPolicy policy = new ApprovalPolicy(
            2,
            3,
            true,
            true,
            true
        );

        RepositoryChange change = new RepositoryChange(
            "PR-2026-104",
            "feature/payment-security",
            "main",
            true,
            false,
            true,
            true,
            true,
            2,
            0,
            Map.of(
                "unit-tests", true,
                "integration-tests", true,
                "security-scan", true,
                "deployment-preview", true
            )
        );

        MergeEligibilityService service =
            new MergeEligibilityService(policy);

        EligibilityResult result = service.evaluate(change);

        System.out.println("Eligible: " + result.eligible());

        result.violations().forEach(
            violation -> System.out.println("- " + violation)
        );

        RepositoryChange invalid = new RepositoryChange(
            "PR-2026-105",
            "feature/unstable",
            "main",
            true,
            false,
            false,
            false,
            false,
            1,
            2,
            Map.of(
                "unit-tests", true,
                "integration-tests", false,
                "security-scan", false
            )
        );

        System.out.println("\nInvalid change:");

        service.evaluate(invalid)
            .violations()
            .forEach(
                violation -> System.out.println("- " + violation)
            );
    }

    static void runTests() {
        TransitionMatrix matrix = buildReliabilityMatrix();

        SimulationService service = new SimulationService(matrix);

        SimulationConfiguration configuration =
            new SimulationConfiguration(
                State.OPERATIONAL,
                50,
                42
            );

        SimulationResult first =
            service.execute(configuration, null);

        SimulationResult second =
            service.execute(configuration, null);

        if (!first.path().equals(second.path())) {
            throw new AssertionError("Reproducibility failed.");
        }

        if (!matrix.isAbsorbing(State.FAILED)) {
            throw new AssertionError("Absorbing state validation failed.");
        }

        ApprovalPolicy policy = new ApprovalPolicy(
            1, 1, true, true, false
        );

        RepositoryChange change = new RepositoryChange(
            "PR-TEST",
            "feature/test",
            "main",
            true,
            false,
            true,
            true,
            true,
            1,
            0,
            Map.of("tests", true)
        );

        EligibilityResult eligibility =
            new MergeEligibilityService(policy).evaluate(change);

        if (!eligibility.eligible()) {
            throw new AssertionError("Valid governance case rejected.");
        }

        boolean invalidRejected = false;

        try {
            new Transition(
                State.OPERATIONAL,
                1.5
            );
        } catch (TransitionValidationException exception) {
            invalidRejected = true;
        }

        if (!invalidRejected) {
            throw new AssertionError("Invalid probability accepted.");
        }

        System.out.println("All Java 17 validation tests passed.");
    }

    public static void main(String[] args) {
        try {
            runTests();

            System.out.println("\nSTOCHASTIC PROCESSES");
            System.out.println("====================");

            TransitionMatrix weather = buildWeatherMatrix();

            SimulationService weatherService =
                new SimulationService(weather);

            SimulationResult weatherResult =
                weatherService.execute(
                    new SimulationConfiguration(
                        State.OPERATIONAL,
                        15,
                        42
                    ),
                    event -> System.out.printf(
                        "Step %d: %s -> %s%n",
                        event.step(),
                        event.previousState(),
                        event.currentState()
                    )
                );

            System.out.println("\nWeather path:");
            System.out.println(
                weatherResult.path()
                    .stream()
                    .map(Enum::name)
                    .collect(Collectors.joining(" -> "))
            );

            TransitionMatrix reliability = buildReliabilityMatrix();

            SimulationService reliabilityService =
                new SimulationService(reliability);

            MonteCarloService monteCarlo =
                new MonteCarloService();

            MonteCarloService.Estimate estimate =
                monteCarlo.estimate(
                    reliabilityService,
                    State.OPERATIONAL,
                    State.FAILED,
                    10000,
                    100,
                    12345
                );

            System.out.println("\nRELIABILITY ESTIMATION");
            System.out.println(estimate);

            demonstrateGovernance();

            System.out.println("\nTransition matrix:");

            reliability.asMap().forEach((state, row) ->
                System.out.println(state + " -> " + row)
            );

        } catch (Exception exception) {
            System.err.println(
                "Execution failed: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
