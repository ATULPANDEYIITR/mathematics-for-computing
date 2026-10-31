import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Random;
import java.util.Set;
import java.util.function.Predicate;
import java.util.stream.Collectors;

public class ProbabilityFundamentals {

    enum ReviewState {
        DRAFT,
        OPEN,
        APPROVED,
        CHANGES_REQUESTED,
        MERGED,
        CLOSED
    }

    enum CheckState {
        PENDING,
        PASSING,
        FAILING
    }

    record Review(
        String reviewer,
        boolean eligible,
        ReviewState state
    ) {
        Review {
            Objects.requireNonNull(reviewer);
            Objects.requireNonNull(state);
            if (reviewer.isBlank()) {
                throw new IllegalArgumentException("Reviewer name cannot be blank.");
            }
        }
    }

    record StatusCheck(String name, CheckState state) {
        StatusCheck {
            Objects.requireNonNull(name);
            Objects.requireNonNull(state);
        }
    }

    record BranchProtectionPolicy(
        int requiredApprovals,
        boolean requirePassingChecks,
        boolean requireResolvedConversations,
        boolean allowDirectPush,
        boolean allowForcePush,
        boolean requireLinearHistory
    ) {
        BranchProtectionPolicy {
            if (requiredApprovals < 0) {
                throw new IllegalArgumentException(
                    "requiredApprovals cannot be negative."
                );
            }
        }
    }

    static final class ProbabilityException extends RuntimeException {
        ProbabilityException(String message) {
            super(message);
        }
    }

    static final class ProbabilitySpace<T> {
        private final Map<T, Double> probabilities;

        ProbabilitySpace(Map<T, Double> probabilities) {
            if (probabilities == null || probabilities.isEmpty()) {
                throw new ProbabilityException("Sample space cannot be empty.");
            }

            this.probabilities = Map.copyOf(probabilities);

            double total = 0.0;

            for (double probability : this.probabilities.values()) {
                if (!Double.isFinite(probability) ||
                    probability < 0.0 ||
                    probability > 1.0) {
                    throw new ProbabilityException(
                        "Every probability must be between zero and one."
                    );
                }
                total += probability;
            }

            if (Math.abs(total - 1.0) > 1e-12) {
                throw new ProbabilityException(
                    "Probabilities must sum to one. Total: " + total
                );
            }
        }

        double probability(Set<T> event) {
            if (!probabilities.keySet().containsAll(event)) {
                throw new ProbabilityException(
                    "Event contains an outcome outside the sample space."
                );
            }

            return event.stream()
                .mapToDouble(probabilities::get)
                .sum();
        }

        Set<T> outcomes() {
            return probabilities.keySet();
        }
    }

    record Event<T>(String name, Set<T> outcomes) {
        Event {
            Objects.requireNonNull(name);
            Objects.requireNonNull(outcomes);
            outcomes = Collections.unmodifiableSet(new HashSet<>(outcomes));
        }
    }

    record PullRequest(
        int id,
        String sourceBranch,
        String targetBranch,
        List<String> commits,
        List<Review> reviews,
        List<StatusCheck> checks,
        int unresolvedConversations,
        ReviewState state,
        boolean sourceUpToDate
    ) {
        PullRequest {
            if (id <= 0) {
                throw new IllegalArgumentException("Pull Request ID must be positive.");
            }
            if (sourceBranch == null || targetBranch == null) {
                throw new IllegalArgumentException("Branches are required.");
            }
            commits = List.copyOf(commits);
            reviews = List.copyOf(reviews);
            checks = List.copyOf(checks);
        }
    }

    static <T> Event<T> union(
        ProbabilitySpace<T> space,
        Event<T> first,
        Event<T> second
    ) {
        validateEvent(space, first);
        validateEvent(space, second);

        Set<T> result = new HashSet<>(first.outcomes());
        result.addAll(second.outcomes());

        return new Event<>(
            first.name() + " OR " + second.name(),
            result
        );
    }

    static <T> Event<T> intersection(
        ProbabilitySpace<T> space,
        Event<T> first,
        Event<T> second
    ) {
        validateEvent(space, first);
        validateEvent(space, second);

        Set<T> result = new HashSet<>(first.outcomes());
        result.retainAll(second.outcomes());

        return new Event<>(
            first.name() + " AND " + second.name(),
            result
        );
    }

    static <T> Event<T> complement(
        ProbabilitySpace<T> space,
        Event<T> event
    ) {
        validateEvent(space, event);

        Set<T> result = new HashSet<>(space.outcomes());
        result.removeAll(event.outcomes());

        return new Event<>("NOT " + event.name(), result);
    }

    static <T> void validateEvent(
        ProbabilitySpace<T> space,
        Event<T> event
    ) {
        if (!space.outcomes().containsAll(event.outcomes())) {
            throw new ProbabilityException(
                "Event contains invalid outcomes."
            );
        }
    }

    static <T> double conditionalProbability(
        ProbabilitySpace<T> space,
        Event<T> event,
        Event<T> condition
    ) {
        double denominator = space.probability(condition.outcomes());

        if (denominator == 0.0) {
            throw new ProbabilityException(
                "Conditional probability is undefined for zero-probability conditions."
            );
        }

        double numerator =
            space.probability(
                intersection(space, event, condition).outcomes()
            );

        return numerator / denominator;
    }

    static double binomialProbability(int n, int k, double p) {
        if (n < 0 || k < 0 || k > n) {
            throw new IllegalArgumentException(
                "Require n >= 0 and 0 <= k <= n."
            );
        }

        if (p < 0.0 || p > 1.0) {
            throw new IllegalArgumentException(
                "p must be between zero and one."
            );
        }

        double coefficient = 1.0;

        for (int i = 1; i <= k; i++) {
            coefficient *= (double) (n - i + 1) / i;
        }

        return coefficient *
            Math.pow(p, k) *
            Math.pow(1.0 - p, n - k);
    }

    static final class Experiment<T> {
        private final Random random;

        Experiment(long seed) {
            this.random = new Random(seed);
        }

        double estimate(
            int trials,
            java.util.function.Supplier<T> generator,
            Predicate<T> event
        ) {
            if (trials <= 0) {
                throw new IllegalArgumentException("Trials must be positive.");
            }

            int successes = 0;

            for (int i = 0; i < trials; i++) {
                T outcome = generator.get();
                if (event.test(outcome)) {
                    successes++;
                }
            }

            return (double) successes / trials;
        }

        int fairDieRoll() {
            return random.nextInt(6) + 1;
        }
    }

    static final class MergeEligibilityService {
        boolean isEligible(
            PullRequest pullRequest,
            BranchProtectionPolicy policy
        ) {
            if (pullRequest.state() == ReviewState.MERGED ||
                pullRequest.state() == ReviewState.CLOSED) {
                return false;
            }

            if (pullRequest.sourceBranch().isBlank() ||
                pullRequest.targetBranch().isBlank() ||
                pullRequest.sourceBranch().equals(pullRequest.targetBranch())) {
                return false;
            }

            if (pullRequest.commits().isEmpty() ||
                !pullRequest.sourceUpToDate()) {
                return false;
            }

            long approvals = pullRequest.reviews().stream()
                .filter(Review::eligible)
                .filter(review -> review.state() == ReviewState.APPROVED)
                .count();

            if (approvals < policy.requiredApprovals()) {
                return false;
            }

            if (policy.requirePassingChecks()) {
                boolean allChecksPassing =
                    !pullRequest.checks().isEmpty() &&
                    pullRequest.checks().stream()
                        .allMatch(check -> check.state() == CheckState.PASSING);

                if (!allChecksPassing) {
                    return false;
                }
            }

            return !policy.requireResolvedConversations() ||
                pullRequest.unresolvedConversations() == 0;
        }
    }

    static void validateProbabilityModel() {
        Map<Integer, Double> probabilities = new java.util.LinkedHashMap<>();

        for (int i = 1; i <= 6; i++) {
            probabilities.put(i, 1.0 / 6.0);
        }

        ProbabilitySpace<Integer> die = new ProbabilitySpace<>(probabilities);

        Event<Integer> even =
            new Event<>("even", Set.of(2, 4, 6));

        Event<Integer> prime =
            new Event<>("prime", Set.of(2, 3, 5));

        assertClose(
            die.probability(even.outcomes()),
            0.5,
            "Even-event probability"
        );

        assertClose(
            die.probability(
                intersection(die, even, prime).outcomes()
            ),
            1.0 / 6.0,
            "Intersection probability"
        );

        assertClose(
            die.probability(
                union(die, even, prime).outcomes()
            ),
            5.0 / 6.0,
            "Union probability"
        );

        assertClose(
            die.probability(
                complement(die, even).outcomes()
            ),
            0.5,
            "Complement probability"
        );

        assertClose(
            conditionalProbability(die, prime, even),
            1.0 / 3.0,
            "Conditional probability"
        );

        assertClose(
            binomialProbability(5, 3, 0.5),
            0.3125,
            "Binomial probability"
        );
    }

    static void assertClose(
        double actual,
        double expected,
        String description
    ) {
        if (Math.abs(actual - expected) > 1e-12) {
            throw new AssertionError(
                description +
                " expected " +
                expected +
                " but received " +
                actual
            );
        }
    }

    static void demonstrateGovernance() {
        BranchProtectionPolicy policy =
            new BranchProtectionPolicy(
                2,
                true,
                true,
                false,
                false,
                true
            );

        PullRequest pullRequest =
            new PullRequest(
                501,
                "feature/probability",
                "main",
                List.of("a100", "b200"),
                List.of(
                    new Review(
                        "alice",
                        true,
                        ReviewState.APPROVED
                    ),
                    new Review(
                        "bob",
                        true,
                        ReviewState.APPROVED
                    ),
                    new Review(
                        "author",
                        false,
                        ReviewState.APPROVED
                    )
                ),
                List.of(
                    new StatusCheck("unit-tests", CheckState.PASSING),
                    new StatusCheck("security-scan", CheckState.PASSING)
                ),
                0,
                ReviewState.OPEN,
                true
            );

        MergeEligibilityService service =
            new MergeEligibilityService();

        System.out.println(
            "Governance merge eligible: " +
            service.isEligible(pullRequest, policy)
        );

        PullRequest blocked =
            new PullRequest(
                pullRequest.id(),
                pullRequest.sourceBranch(),
                pullRequest.targetBranch(),
                pullRequest.commits(),
                pullRequest.reviews(),
                List.of(
                    new StatusCheck("unit-tests", CheckState.PASSING),
                    new StatusCheck("security-scan", CheckState.FAILING)
                ),
                pullRequest.unresolvedConversations(),
                pullRequest.state(),
                pullRequest.sourceUpToDate()
            );

        System.out.println(
            "After failing security scan: " +
            service.isEligible(blocked, policy)
        );
    }

    public static void main(String[] args) {
        try {
            validateProbabilityModel();

            System.out.println("=== Probability Fundamentals ===");

            Map<Integer, Double> probabilities =
                new java.util.LinkedHashMap<>();

            for (int i = 1; i <= 6; i++) {
                probabilities.put(i, 1.0 / 6.0);
            }

            ProbabilitySpace<Integer> die =
                new ProbabilitySpace<>(probabilities);

            Event<Integer> even =
                new Event<>("even", Set.of(2, 4, 6));

            Event<Integer> prime =
                new Event<>("prime", Set.of(2, 3, 5));

            System.out.printf(
                "P(even) = %.4f%n",
                die.probability(even.outcomes())
            );

            System.out.printf(
                "P(prime) = %.4f%n",
                die.probability(prime.outcomes())
            );

            System.out.printf(
                "P(even OR prime) = %.4f%n",
                die.probability(
                    union(die, even, prime).outcomes()
                )
            );

            System.out.printf(
                "P(even AND prime) = %.4f%n",
                die.probability(
                    intersection(die, even, prime).outcomes()
                )
            );

            System.out.printf(
                "P(prime | even) = %.4f%n",
                conditionalProbability(die, prime, even)
            );

            Experiment<Integer> experiment =
                new Experiment<>(20261031L);

            double estimate =
                experiment.estimate(
                    100_000,
                    experiment::fairDieRoll,
                    value -> value == 6
                );

            System.out.printf(
                "Estimated P(6) = %.4f%n",
                estimate
            );

            System.out.printf(
                "P(exactly 3 heads in 5 fair trials) = %.4f%n",
                binomialProbability(5, 3, 0.5)
            );

            demonstrateGovernance();

            System.out.println("All validation checks passed.");
        } catch (RuntimeException error) {
            System.err.println(
                "Execution failed: " + error.getMessage()
            );
            System.exit(1);
        }
    }
}
