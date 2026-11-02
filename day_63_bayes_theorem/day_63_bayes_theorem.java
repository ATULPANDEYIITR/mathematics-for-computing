import java.util.*;
import java.util.stream.Collectors;

public class BayesianRepositoryGovernance {

    enum PullRequestState {
        DRAFT, OPEN, CLOSED, MERGED
    }

    enum ReviewState {
        COMMENTED, CHANGES_REQUESTED, APPROVED, DISMISSED
    }

    enum CheckState {
        PASS, FAIL, PENDING
    }

    enum MergeStrategy {
        MERGE_COMMIT, SQUASH, REBASE
    }

    record Commit(String sha, String message) {
        Commit {
            Objects.requireNonNull(sha);
            Objects.requireNonNull(message);
            if (sha.isBlank()) {
                throw new IllegalArgumentException("Commit SHA cannot be blank.");
            }
        }
    }

    record Review(
        String reviewer,
        ReviewState state,
        String commitSha
    ) {
        Review {
            Objects.requireNonNull(reviewer);
            Objects.requireNonNull(state);
            Objects.requireNonNull(commitSha);
        }
    }

    record StatusCheck(String name, CheckState state) {
        StatusCheck {
            Objects.requireNonNull(name);
            Objects.requireNonNull(state);
        }
    }

    record BranchProtection(
        int requiredApprovals,
        Set<String> requiredChecks,
        boolean requireConversationResolution,
        boolean requireLinearHistory,
        boolean allowDirectPush,
        boolean allowForcePush
    ) {
        BranchProtection {
            if (requiredApprovals < 0) {
                throw new IllegalArgumentException(
                    "Required approvals cannot be negative."
                );
            }
            requiredChecks = Set.copyOf(requiredChecks);
        }
    }

    record Branch(
        String name,
        boolean protectedBranch,
        BranchProtection protection
    ) {
        Branch {
            Objects.requireNonNull(name);
            if (name.isBlank()) {
                throw new IllegalArgumentException("Branch name cannot be blank.");
            }
            if (protectedBranch && protection == null) {
                throw new IllegalArgumentException(
                    "Protected branches require a protection policy."
                );
            }
        }
    }

    static final class PullRequest {
        private final int number;
        private final String source;
        private final String target;
        private PullRequestState state;
        private final List<Commit> commits;
        private final List<Review> reviews;
        private final List<StatusCheck> checks;
        private int openConversations;
        private MergeStrategy mergeStrategy;
        private boolean forcePushRequested;

        PullRequest(
            int number,
            String source,
            String target,
            PullRequestState state,
            List<Commit> commits,
            List<Review> reviews,
            List<StatusCheck> checks,
            int openConversations,
            MergeStrategy mergeStrategy
        ) {
            if (number <= 0) {
                throw new IllegalArgumentException(
                    "Pull Request number must be positive."
                );
            }
            if (source.equals(target)) {
                throw new IllegalArgumentException(
                    "Source and target branches must differ."
                );
            }

            this.number = number;
            this.source = source;
            this.target = target;
            this.state = Objects.requireNonNull(state);
            this.commits = new ArrayList<>(commits);
            this.reviews = new ArrayList<>(reviews);
            this.checks = new ArrayList<>(checks);
            this.openConversations = openConversations;
            this.mergeStrategy = Objects.requireNonNull(mergeStrategy);
        }

        int number() {
            return number;
        }

        String source() {
            return source;
        }

        String target() {
            return target;
        }

        PullRequestState state() {
            return state;
        }

        String headSha() {
            if (commits.isEmpty()) {
                throw new IllegalStateException(
                    "Pull Request has no commits."
                );
            }
            return commits.get(commits.size() - 1).sha();
        }

        List<Commit> commits() {
            return Collections.unmodifiableList(commits);
        }

        List<Review> reviews() {
            return Collections.unmodifiableList(reviews);
        }

        List<StatusCheck> checks() {
            return Collections.unmodifiableList(checks);
        }

        int openConversations() {
            return openConversations;
        }

        void setOpenConversations(int count) {
            if (count < 0) {
                throw new IllegalArgumentException(
                    "Conversation count cannot be negative."
                );
            }
            openConversations = count;
        }

        MergeStrategy mergeStrategy() {
            return mergeStrategy;
        }

        void setMergeStrategy(MergeStrategy strategy) {
            mergeStrategy = Objects.requireNonNull(strategy);
        }

        void addCommit(Commit commit) {
            commits.add(Objects.requireNonNull(commit));
        }

        void addReview(Review review) {
            reviews.add(Objects.requireNonNull(review));
        }

        void requestForcePush(boolean requested) {
            forcePushRequested = requested;
        }

        boolean forcePushRequested() {
            return forcePushRequested;
        }
    }

    record Evidence(
        String name,
        double likelihoodSafe,
        double likelihoodUnsafe
    ) {
        Evidence {
            if (!(likelihoodSafe > 0 && likelihoodSafe <= 1) ||
                !(likelihoodUnsafe > 0 && likelihoodUnsafe <= 1)) {
                throw new IllegalArgumentException(
                    "Likelihoods must be within (0, 1]."
                );
            }
        }
    }

    record Evaluation(
        boolean eligible,
        double posterior,
        List<String> reasons
    ) {
        Evaluation {
            reasons = List.copyOf(reasons);
        }
    }

    interface ProbabilityPolicy {
        double posterior(List<Evidence> evidence);
        double threshold();
    }

    static final class BayesianPolicy implements ProbabilityPolicy {
        private final double priorSafe;
        private final double threshold;

        BayesianPolicy(double priorSafe, double threshold) {
            if (!(priorSafe > 0 && priorSafe < 1)) {
                throw new IllegalArgumentException(
                    "Prior must be between zero and one."
                );
            }
            if (!(threshold > 0 && threshold < 1)) {
                throw new IllegalArgumentException(
                    "Threshold must be between zero and one."
                );
            }
            this.priorSafe = priorSafe;
            this.threshold = threshold;
        }

        @Override
        public double posterior(List<Evidence> evidence) {
            double safe = priorSafe;
            double unsafe = 1 - priorSafe;

            for (Evidence item : evidence) {
                safe *= item.likelihoodSafe();
                unsafe *= item.likelihoodUnsafe();
            }

            return safe / (safe + unsafe);
        }

        @Override
        public double threshold() {
            return threshold;
        }
    }

    static final class Repository {
        private final String name;
        private final Map<String, Branch> branches = new HashMap<>();

        Repository(String name) {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException(
                    "Repository name cannot be blank."
                );
            }
            this.name = name;
        }

        void addBranch(Branch branch) {
            if (branches.putIfAbsent(branch.name(), branch) != null) {
                throw new IllegalArgumentException(
                    "Branch already exists: " + branch.name()
                );
            }
        }

        Branch branch(String name) {
            return branches.get(name);
        }
    }

    static final class MergeEligibilityService {
        private final Repository repository;
        private final ProbabilityPolicy policy;

        MergeEligibilityService(
            Repository repository,
            ProbabilityPolicy policy
        ) {
            this.repository = repository;
            this.policy = policy;
        }

        private Set<String> currentApprovers(PullRequest pr) {
            return pr.reviews().stream()
                .filter(r ->
                    r.state() == ReviewState.APPROVED &&
                    r.commitSha().equals(pr.headSha())
                )
                .map(Review::reviewer)
                .collect(Collectors.toSet());
        }

        private boolean requiredCheckPassed(
            PullRequest pr,
            String name
        ) {
            return pr.checks().stream().anyMatch(
                check ->
                    check.name().equals(name) &&
                    check.state() == CheckState.PASS
            );
        }

        private List<Evidence> evidence(
            PullRequest pr,
            Branch branch
        ) {
            Set<String> approvers = currentApprovers(pr);

            boolean allChecksPassed =
                branch.protection().requiredChecks().stream()
                    .allMatch(name -> requiredCheckPassed(pr, name));

            boolean failed =
                pr.checks().stream()
                    .anyMatch(c -> c.state() == CheckState.FAIL);

            boolean pending =
                pr.checks().stream()
                    .anyMatch(c -> c.state() == CheckState.PENDING);

            boolean changesRequested =
                pr.reviews().stream().anyMatch(
                    r ->
                        r.state() == ReviewState.CHANGES_REQUESTED &&
                        r.commitSha().equals(pr.headSha())
                );

            return List.of(
                new Evidence(
                    "current-head-approval",
                    approvers.size() >= branch.protection().requiredApprovals()
                        ? 0.92 : 0.20,
                    approvers.size() >= branch.protection().requiredApprovals()
                        ? 0.08 : 0.80
                ),
                new Evidence(
                    "required-status-checks",
                    allChecksPassed ? 0.97 : 0.15,
                    allChecksPassed ? 0.03 : 0.85
                ),
                new Evidence(
                    "failed-checks",
                    failed ? 0.05 : 0.98,
                    failed ? 0.95 : 0.02
                ),
                new Evidence(
                    "pending-checks",
                    pending ? 0.35 : 0.94,
                    pending ? 0.65 : 0.06
                ),
                new Evidence(
                    "resolved-conversations",
                    pr.openConversations() == 0 ? 0.96 : 0.30,
                    pr.openConversations() == 0 ? 0.04 : 0.70
                ),
                new Evidence(
                    "requested-changes",
                    changesRequested ? 0.10 : 0.95,
                    changesRequested ? 0.90 : 0.05
                )
            );
        }

        Evaluation evaluate(PullRequest pr) {
            List<String> reasons = new ArrayList<>();

            if (pr.state() != PullRequestState.OPEN) {
                reasons.add("Pull Request is not open.");
                return new Evaluation(false, 0, reasons);
            }

            if (pr.commits().isEmpty()) {
                reasons.add("Pull Request contains no commits.");
                return new Evaluation(false, 0, reasons);
            }

            Branch target = repository.branch(pr.target());

            if (target == null) {
                reasons.add("Target branch does not exist.");
                return new Evaluation(false, 0, reasons);
            }

            if (target.protectedBranch()) {
                BranchProtection protection = target.protection();
                Set<String> approvers = currentApprovers(pr);

                if (approvers.size() < protection.requiredApprovals()) {
                    reasons.add(
                        "Required approvals: " +
                        protection.requiredApprovals() +
                        ", current-head approvals: " +
                        approvers.size()
                    );
                }

                for (String required : protection.requiredChecks()) {
                    if (!requiredCheckPassed(pr, required)) {
                        reasons.add(
                            "Required check has not passed: " + required
                        );
                    }
                }

                if (protection.requireConversationResolution() &&
                    pr.openConversations() > 0) {
                    reasons.add(
                        "Review conversations remain unresolved."
                    );
                }

                if (protection.requireLinearHistory() &&
                    pr.mergeStrategy() == MergeStrategy.MERGE_COMMIT) {
                    reasons.add(
                        "Merge commits violate linear-history policy."
                    );
                }

                if (!protection.allowForcePush() &&
                    pr.forcePushRequested()) {
                    reasons.add(
                        "Force push is prohibited."
                    );
                }
            }

            double posterior = policy.posterior(evidence(pr, target));

            if (posterior < policy.threshold()) {
                reasons.add(
                    String.format(
                        Locale.ROOT,
                        "Bayesian posterior %.4f is below %.2f.",
                        posterior,
                        policy.threshold()
                    )
                );
            }

            return new Evaluation(
                reasons.isEmpty(),
                posterior,
                reasons
            );
        }
    }

    public static void main(String[] args) {
        double prior = 0.20;
        double safeLikelihood = 0.90;
        double unsafeLikelihood = 0.30;

        double numerator = safeLikelihood * prior;
        double posterior = numerator /
            (numerator + unsafeLikelihood * (1 - prior));

        System.out.printf(
            Locale.ROOT,
            "Basic Bayes posterior: %.4f%n%n",
            posterior
        );

        Repository repository = new Repository("payments-service");

        repository.addBranch(
            new Branch(
                "main",
                true,
                new BranchProtection(
                    2,
                    Set.of("unit-tests", "security-scan"),
                    true,
                    true,
                    false,
                    false
                )
            )
        );

        repository.addBranch(
            new Branch("feature/payment-validation", false, null)
        );

        PullRequest pr = new PullRequest(
            42,
            "feature/payment-validation",
            "main",
            PullRequestState.OPEN,
            List.of(
                new Commit("a100", "Add payment validation"),
                new Commit("a101", "Fix boundary validation")
            ),
            List.of(
                new Review("alice", ReviewState.APPROVED, "a101"),
                new Review("bob", ReviewState.APPROVED, "a101"),
                new Review("carol", ReviewState.COMMENTED, "a101")
            ),
            List.of(
                new StatusCheck("unit-tests", CheckState.PASS),
                new StatusCheck("security-scan", CheckState.PASS),
                new StatusCheck("integration-tests", CheckState.PASS)
            ),
            0,
            MergeStrategy.SQUASH
        );

        MergeEligibilityService service =
            new MergeEligibilityService(
                repository,
                new BayesianPolicy(0.85, 0.90)
            );

        Evaluation evaluation = service.evaluate(pr);

        System.out.printf(
            Locale.ROOT,
            "Pull Request #%d%nPosterior: %.4f%nEligible: %s%n",
            pr.number(),
            evaluation.posterior(),
            evaluation.eligible()
        );

        evaluation.reasons().forEach(reason -> System.out.println("- " + reason));

        // A new head invalidates approvals tied to the previous commit.
        pr.addCommit(
            new Commit("a102", "Address reviewer findings")
        );

        Evaluation staleApprovalEvaluation = service.evaluate(pr);

        if (staleApprovalEvaluation.eligible()) {
            throw new IllegalStateException(
                "Stale approvals incorrectly remained valid."
            );
        }

        pr.addReview(
            new Review("alice", ReviewState.APPROVED, "a102")
        );
        pr.addReview(
            new Review("bob", ReviewState.APPROVED, "a102")
        );

        pr.setOpenConversations(1);

        Evaluation unresolvedEvaluation = service.evaluate(pr);

        if (unresolvedEvaluation.eligible()) {
            throw new IllegalStateException(
                "Unresolved conversations incorrectly permitted merge."
            );
        }

        System.out.println("Validation scenarios: passed");
    }
}
