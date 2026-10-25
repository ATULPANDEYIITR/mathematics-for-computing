import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

public class ModularInverseGovernance {

    public record BezoutResult(BigInteger gcd, BigInteger x, BigInteger y) {}

    public static final class ModularInverseException
            extends IllegalArgumentException {
        public ModularInverseException(String message) {
            super(message);
        }
    }

    public static BezoutResult extendedGcd(BigInteger a, BigInteger b) {
        Objects.requireNonNull(a, "a");
        Objects.requireNonNull(b, "b");

        BigInteger oldR = a.abs();
        BigInteger r = b.abs();
        BigInteger oldS = BigInteger.ONE;
        BigInteger s = BigInteger.ZERO;
        BigInteger oldT = BigInteger.ZERO;
        BigInteger t = BigInteger.ONE;

        while (!r.equals(BigInteger.ZERO)) {
            BigInteger quotient = oldR.divide(r);

            BigInteger nextR = oldR.subtract(quotient.multiply(r));
            oldR = r;
            r = nextR;

            BigInteger nextS = oldS.subtract(quotient.multiply(s));
            oldS = s;
            s = nextS;

            BigInteger nextT = oldT.subtract(quotient.multiply(t));
            oldT = t;
            t = nextT;
        }

        if (a.signum() < 0) oldS = oldS.negate();
        if (b.signum() < 0) oldT = oldT.negate();

        return new BezoutResult(oldR, oldS, oldT);
    }

    public static BigInteger modularInverse(
            BigInteger value, BigInteger modulus) {
        Objects.requireNonNull(value, "value");
        Objects.requireNonNull(modulus, "modulus");

        if (modulus.compareTo(BigInteger.ONE) <= 0) {
            throw new ModularInverseException(
                    "Modulus must be greater than 1.");
        }

        BezoutResult result = extendedGcd(value, modulus);

        if (!result.gcd().equals(BigInteger.ONE)) {
            throw new ModularInverseException(
                    "Inverse does not exist; gcd = " + result.gcd());
        }

        return result.x().mod(modulus);
    }

    public static BigInteger modularPower(
            BigInteger base, BigInteger exponent, BigInteger modulus) {
        Objects.requireNonNull(base, "base");
        Objects.requireNonNull(exponent, "exponent");
        Objects.requireNonNull(modulus, "modulus");

        if (modulus.compareTo(BigInteger.ONE) <= 0) {
            throw new ModularInverseException(
                    "Modulus must be greater than 1.");
        }

        if (exponent.signum() < 0) {
            base = modularInverse(base, modulus);
            exponent = exponent.negate();
        }

        BigInteger result = BigInteger.ONE;
        base = base.mod(modulus);

        // Binary exponentiation avoids constructing the full power.
        while (exponent.signum() > 0) {
            if (exponent.testBit(0)) {
                result = result.multiply(base).mod(modulus);
            }
            base = base.multiply(base).mod(modulus);
            exponent = exponent.shiftRight(1);
        }

        return result;
    }

    enum ReviewState {
        APPROVED, CHANGES_REQUESTED, COMMENTED
    }

    enum PullRequestState {
        OPEN, DRAFT, CLOSED, MERGED
    }

    record Reviewer(String username, boolean eligible, boolean author) {
        Reviewer {
            if (username == null || username.isBlank()) {
                throw new IllegalArgumentException(
                        "Reviewer name must not be blank.");
            }
        }
    }

    record Review(
            Reviewer reviewer,
            ReviewState state,
            boolean dismissed,
            boolean stale) {
        Review {
            Objects.requireNonNull(reviewer);
            Objects.requireNonNull(state);
        }

        boolean countsAsApproval() {
            return !dismissed
                    && !stale
                    && reviewer.eligible()
                    && !reviewer.author()
                    && state == ReviewState.APPROVED;
        }

        boolean blocksMerge() {
            return !dismissed
                    && !stale
                    && reviewer.eligible()
                    && !reviewer.author()
                    && state == ReviewState.CHANGES_REQUESTED;
        }
    }

    record StatusCheck(String name, boolean required, boolean passed) {
        StatusCheck {
            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException(
                        "Status check name must not be blank.");
            }
        }
    }

    record BranchPolicy(
            String branch,
            boolean protectedBranch,
            int requiredApprovals,
            boolean requireChecks,
            boolean requireLinearHistory,
            boolean allowDirectPush,
            boolean allowForcePush,
            boolean allowDeletion,
            boolean administratorsMustComply) {
        BranchPolicy {
            if (branch == null || branch.isBlank()) {
                throw new IllegalArgumentException(
                        "Branch name must not be blank.");
            }
            if (requiredApprovals < 0) {
                throw new IllegalArgumentException(
                        "Required approvals cannot be negative.");
            }
        }
    }

    record PullRequest(
            int id,
            String sourceBranch,
            String targetBranch,
            PullRequestState state,
            boolean conflicts,
            boolean synchronizedWithBase,
            boolean discussionsResolved,
            boolean linearHistory) {
        PullRequest {
            if (id <= 0) {
                throw new IllegalArgumentException("ID must be positive.");
            }
            if (sourceBranch == null || sourceBranch.isBlank()
                    || targetBranch == null || targetBranch.isBlank()) {
                throw new IllegalArgumentException(
                        "Branch names must not be blank.");
            }
            Objects.requireNonNull(state);
        }
    }

    record Eligibility(boolean allowed, List<String> reasons) {
        Eligibility {
            reasons = List.copyOf(reasons);
        }
    }

    interface ReviewPolicy {
        boolean approvalCounts(Review review);
        boolean blocksMerge(Review review);
    }

    static final class StandardReviewPolicy implements ReviewPolicy {
        @Override
        public boolean approvalCounts(Review review) {
            return review.countsAsApproval();
        }

        @Override
        public boolean blocksMerge(Review review) {
            return review.blocksMerge();
        }
    }

    static final class MergeEligibilityService {
        private final ReviewPolicy reviewPolicy;

        MergeEligibilityService(ReviewPolicy reviewPolicy) {
            this.reviewPolicy = Objects.requireNonNull(reviewPolicy);
        }

        Eligibility evaluate(
                PullRequest pr,
                BranchPolicy policy,
                List<Review> reviews,
                List<StatusCheck> checks) {
            List<String> reasons = new ArrayList<>();

            if (pr.state() != PullRequestState.OPEN) {
                reasons.add("Pull Request must be open and not a draft.");
            }
            if (pr.targetBranch().equals(pr.sourceBranch())) {
                reasons.add("Source and target branches must differ.");
            }
            if (!pr.targetBranch().equals(policy.branch())) {
                reasons.add("Target branch does not match policy.");
            }
            if (pr.conflicts()) reasons.add("Merge conflicts exist.");
            if (!pr.synchronizedWithBase()) {
                reasons.add("Source branch is not synchronized with base.");
            }
            if (!pr.discussionsResolved()) {
                reasons.add("Review discussions remain unresolved.");
            }
            if (policy.protectedBranch()
                    && policy.requireLinearHistory()
                    && !pr.linearHistory()) {
                reasons.add("Linear history is required.");
            }

            long approvals = reviews.stream()
                    .filter(reviewPolicy::approvalCounts)
                    .count();

            boolean changesRequested = reviews.stream()
                    .anyMatch(reviewPolicy::blocksMerge);

            if (changesRequested) {
                reasons.add("An eligible reviewer has requested changes.");
            }

            if (policy.protectedBranch()
                    && approvals < policy.requiredApprovals()) {
                reasons.add("Insufficient eligible, current approvals.");
            }

            if (policy.protectedBranch() && policy.requireChecks()) {
                checks.stream()
                        .filter(StatusCheck::required)
                        .filter(check -> !check.passed())
                        .forEach(check -> reasons.add(
                                "Required check is not passing: "
                                        + check.name()));
            }

            return new Eligibility(reasons.isEmpty(), reasons);
        }
    }

    private static BigInteger bi(long value) {
        return BigInteger.valueOf(value);
    }

    private static void require(
            boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    private static void testArithmetic() {
        require(modularInverse(bi(3), bi(11)).equals(bi(4)),
                "3 inverse modulo 11");
        require(modularInverse(bi(-3), bi(11)).equals(bi(7)),
                "Negative value normalization");
        require(modularPower(bi(3), bi(-2), bi(11)).equals(bi(5)),
                "Negative exponent");

        try {
            modularInverse(bi(6), bi(15));
            throw new AssertionError("Non-invertible input was accepted.");
        } catch (ModularInverseException expected) {
            // Expected: gcd(6, 15) = 3.
        }
    }

    public static void main(String[] args) {
        testArithmetic();

        System.out.println("Modular arithmetic");
        for (long[] pair : new long[][]{{3, 11}, {10, 17}, {6, 15}}) {
            BigInteger value = bi(pair[0]);
            BigInteger modulus = bi(pair[1]);

            try {
                BigInteger inverse = modularInverse(value, modulus);
                System.out.printf(
                        "%d mod %d -> %s; verification=%s%n",
                        pair[0], pair[1], inverse,
                        value.multiply(inverse).mod(modulus));
            } catch (ModularInverseException error) {
                System.out.printf(
                        "%d mod %d -> unavailable (%s)%n",
                        pair[0], pair[1], error.getMessage());
            }
        }

        BranchPolicy policy = new BranchPolicy(
                "main", true, 2, true, true,
                false, false, false, true);

        PullRequest pr = new PullRequest(
                101, "feature/modular-inverse", "main",
                PullRequestState.OPEN, false, true, true, true);

        Reviewer alice = new Reviewer("alice", true, false);
        Reviewer bob = new Reviewer("bob", true, false);
        Reviewer author = new Reviewer("maintainer-author", true, true);

        List<Review> reviews = new ArrayList<>(List.of(
                new Review(alice, ReviewState.APPROVED, false, false),
                new Review(bob, ReviewState.APPROVED, false, false),
                new Review(author, ReviewState.APPROVED, false, false)));

        List<StatusCheck> checks = new ArrayList<>(List.of(
                new StatusCheck("unit-tests", true, true),
                new StatusCheck("static-analysis", true, true),
                new StatusCheck("integration-tests", true, false)));

        MergeEligibilityService service =
                new MergeEligibilityService(new StandardReviewPolicy());

        System.out.println("\nEnterprise merge evaluation");
        System.out.println(service.evaluate(pr, policy, reviews, checks));

        checks.set(2, new StatusCheck("integration-tests", true, true));
        System.out.println(service.evaluate(pr, policy, reviews, checks));

        reviews.set(1, new Review(bob, ReviewState.APPROVED, true, false));
        System.out.println(service.evaluate(pr, policy, reviews, checks));

        System.out.println(
                "\nArithmetic uses arbitrary-precision integers. "
                + "Merge evaluation takes O(r + c) time.");
    }
}
