import java.math.BigInteger;
import java.util.List;
import java.util.Map;
import java.util.Objects;

public class CRTGovernanceDemo {

    enum ReviewState {
        COMMENTED,
        APPROVED,
        CHANGES_REQUESTED,
        DISMISSED
    }

    enum CheckState {
        PENDING,
        PASSED,
        FAILED
    }

    enum PullRequestState {
        DRAFT,
        OPEN,
        MERGED,
        CLOSED
    }

    record Congruence(BigInteger remainder, BigInteger modulus) {
        Congruence {
            Objects.requireNonNull(remainder);
            Objects.requireNonNull(modulus);

            if (modulus.compareTo(BigInteger.ONE) <= 0) {
                throw new IllegalArgumentException(
                    "Modulus must be greater than one."
                );
            }

            remainder = remainder.mod(modulus);
        }
    }

    record CRTResult(BigInteger remainder, BigInteger modulus) {
        boolean contains(BigInteger value) {
            return value.subtract(remainder)
                       .mod(modulus)
                       .equals(BigInteger.ZERO);
        }
    }

    record Review(
        String reviewer,
        ReviewState state,
        boolean eligibleReviewer,
        String commitId
    ) {}

    record StatusCheck(
        String name,
        CheckState state
    ) {}

    record BranchPolicy(
        String branch,
        int requiredApprovals,
        boolean requireStatusChecks,
        boolean requireConversationResolution,
        boolean restrictDirectPush,
        boolean restrictForcePush,
        boolean requireLinearHistory
    ) {}

    record PullRequest(
        String id,
        String sourceBranch,
        String targetBranch,
        String headCommit,
        PullRequestState state,
        boolean conflicts,
        List<Review> reviews,
        List<StatusCheck> checks,
        int unresolvedConversations,
        boolean linearHistory
    ) {}

    static class CRTService {

        static BigInteger modInverse(
            BigInteger value,
            BigInteger modulus
        ) {
            if (!value.gcd(modulus).equals(BigInteger.ONE)) {
                throw new ArithmeticException(
                    "Modular inverse does not exist."
                );
            }
            return value.modInverse(modulus);
        }

        static CRTResult solveCoprime(List<Congruence> system) {
            if (system.isEmpty()) {
                throw new IllegalArgumentException(
                    "The system cannot be empty."
                );
            }

            BigInteger product = BigInteger.ONE;

            for (int i = 0; i < system.size(); i++) {
                for (int j = i + 1; j < system.size(); j++) {
                    if (!system.get(i).modulus()
                            .gcd(system.get(j).modulus())
                            .equals(BigInteger.ONE)) {
                        throw new IllegalArgumentException(
                            "Moduli must be pairwise coprime."
                        );
                    }
                }
                product = product.multiply(system.get(i).modulus());
            }

            BigInteger value = BigInteger.ZERO;

            for (Congruence c : system) {
                BigInteger partial = product.divide(c.modulus());
                BigInteger inverse =
                    modInverse(partial.mod(c.modulus()), c.modulus());

                value = value.add(
                    c.remainder()
                     .multiply(partial)
                     .multiply(inverse)
                );
            }

            return new CRTResult(
                value.mod(product),
                product
            );
        }

        static CRTResult merge(
            Congruence first,
            Congruence second
        ) {
            BigInteger m1 = first.modulus();
            BigInteger m2 = second.modulus();
            BigInteger gcd = m1.gcd(m2);

            BigInteger difference =
                second.remainder().subtract(first.remainder());

            if (!difference.mod(gcd).equals(BigInteger.ZERO)) {
                throw new IllegalArgumentException(
                    "The congruences are inconsistent."
                );
            }

            BigInteger reducedM1 = m1.divide(gcd);
            BigInteger reducedM2 = m2.divide(gcd);
            BigInteger rhs = difference.divide(gcd);

            BigInteger inverse =
                modInverse(reducedM1.mod(reducedM2), reducedM2);

            BigInteger k = rhs.multiply(inverse).mod(reducedM2);
            BigInteger combinedModulus = m1.multiply(reducedM2);

            BigInteger combinedValue =
                first.remainder()
                     .add(m1.multiply(k))
                     .mod(combinedModulus);

            return new CRTResult(
                combinedValue,
                combinedModulus
            );
        }

        static CRTResult solveGeneral(List<Congruence> system) {
            if (system.isEmpty()) {
                throw new IllegalArgumentException(
                    "The system cannot be empty."
                );
            }

            CRTResult result = new CRTResult(
                system.get(0).remainder(),
                system.get(0).modulus()
            );

            for (int i = 1; i < system.size(); i++) {
                result = merge(
                    new Congruence(
                        result.remainder(),
                        result.modulus()
                    ),
                    system.get(i)
                );
            }

            return result;
        }
    }

    static class GovernanceService {

        static boolean eligible(
            PullRequest pr,
            BranchPolicy policy
        ) {
            if (pr.state() != PullRequestState.OPEN) {
                return false;
            }

            if (pr.conflicts()) {
                return false;
            }

            if (pr.unresolvedConversations() > 0 &&
                policy.requireConversationResolution()) {
                return false;
            }

            if (policy.requireLinearHistory() && !pr.linearHistory()) {
                return false;
            }

            if (policy.requireStatusChecks()) {
                boolean allPassed = pr.checks()
                    .stream()
                    .allMatch(check -> check.state() == CheckState.PASSED);

                if (!allPassed) {
                    return false;
                }
            }

            long approvals = pr.reviews()
                .stream()
                .filter(review ->
                    review.state() == ReviewState.APPROVED &&
                    review.eligibleReviewer() &&
                    review.commitId().equals(pr.headCommit())
                )
                .count();

            return approvals >= policy.requiredApprovals();
        }
    }

    static void printEligibility(
        PullRequest pr,
        BranchPolicy policy
    ) {
        boolean eligible = GovernanceService.eligible(pr, policy);

        System.out.println(
            pr.id() + " -> merge eligible: " +
            (eligible ? "yes" : "no")
        );
    }

    public static void main(String[] args) {
        List<Congruence> system = List.of(
            new Congruence(BigInteger.valueOf(2), BigInteger.valueOf(3)),
            new Congruence(BigInteger.valueOf(3), BigInteger.valueOf(5)),
            new Congruence(BigInteger.valueOf(2), BigInteger.valueOf(7))
        );

        CRTResult result = CRTService.solveCoprime(system);

        System.out.println("Coprime CRT:");
        System.out.println(
            "x = " + result.remainder() +
            " (mod " + result.modulus() + ")"
        );

        if (!system.stream().allMatch(
            c -> result.contains(c.remainder())
        )) {
            throw new IllegalStateException(
                "CRT verification failed."
            );
        }

        List<Congruence> generalized = List.of(
            new Congruence(BigInteger.valueOf(2), BigInteger.valueOf(6)),
            new Congruence(BigInteger.valueOf(8), BigInteger.valueOf(9))
        );

        CRTResult generalizedResult =
            CRTService.solveGeneral(generalized);

        System.out.println("\nGeneralized CRT:");
        System.out.println(
            "x = " + generalizedResult.remainder() +
            " (mod " + generalizedResult.modulus() + ")"
        );

        try {
            CRTService.solveGeneral(List.of(
                new Congruence(
                    BigInteger.ONE,
                    BigInteger.valueOf(4)
                ),
                new Congruence(
                    BigInteger.TWO,
                    BigInteger.valueOf(6)
                )
            ));
        } catch (IllegalArgumentException ex) {
            System.out.println(
                "\nExpected inconsistency: " + ex.getMessage()
            );
        }

        BranchPolicy policy = new BranchPolicy(
            "main",
            2,
            true,
            true,
            true,
            true,
            true
        );

        String headCommit = "abc123";

        PullRequest pullRequest = new PullRequest(
            "PR-2048",
            "feature/payment-retry",
            "main",
            headCommit,
            PullRequestState.OPEN,
            false,
            List.of(
                new Review(
                    "reviewer-a",
                    ReviewState.APPROVED,
                    true,
                    headCommit
                ),
                new Review(
                    "reviewer-b",
                    ReviewState.APPROVED,
                    true,
                    headCommit
                ),
                new Review(
                    "reviewer-c",
                    ReviewState.COMMENTED,
                    true,
                    headCommit
                )
            ),
            List.of(
                new StatusCheck("unit-tests", CheckState.PASSED),
                new StatusCheck("security-scan", CheckState.PASSED),
                new StatusCheck("integration-tests", CheckState.PASSED)
            ),
            0,
            true
        );

        System.out.println("\nEnterprise repository governance:");
        printEligibility(pullRequest, policy);

        PullRequest staleApproval = new PullRequest(
            "PR-2049",
            "feature/audit",
            "main",
            "new-head",
            PullRequestState.OPEN,
            false,
            List.of(
                new Review(
                    "reviewer-a",
                    ReviewState.APPROVED,
                    true,
                    "old-head"
                ),
                new Review(
                    "reviewer-b",
                    ReviewState.APPROVED,
                    true,
                    "new-head"
                )
            ),
            List.of(
                new StatusCheck("unit-tests", CheckState.PASSED)
            ),
            0,
            true
        );

        printEligibility(staleApproval, policy);
    }
}
