import java.math.BigInteger;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.EnumSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

public class RSAMathematicsEnterprise {

    private static final SecureRandom RANDOM = new SecureRandom();
    private static final BigInteger PUBLIC_EXPONENT = BigInteger.valueOf(65537);

    enum ReviewState {
        DRAFT,
        OPEN,
        CHANGES_REQUESTED,
        APPROVED,
        MERGED,
        CLOSED
    }

    enum ReviewDecision {
        APPROVE,
        REQUEST_CHANGES,
        COMMENT
    }

    record StatusCheck(String name, boolean required, boolean passed) {
        StatusCheck {
            Objects.requireNonNull(name);
            if (name.isBlank()) {
                throw new IllegalArgumentException("Status-check name cannot be blank.");
            }
        }
    }

    record Review(
            String reviewer,
            ReviewDecision decision,
            boolean dismissed,
            boolean unresolvedConversation) {

        Review {
            Objects.requireNonNull(reviewer);
            Objects.requireNonNull(decision);

            if (reviewer.isBlank()) {
                throw new IllegalArgumentException("Reviewer cannot be blank.");
            }
        }

        boolean countsAsApproval() {
            return decision == ReviewDecision.APPROVE
                    && !dismissed
                    && !unresolvedConversation;
        }
    }

    record BranchProtectionPolicy(
            int requiredApprovals,
            Set<String> requiredStatusChecks,
            boolean requireResolvedConversations,
            boolean prohibitForcePush,
            boolean prohibitDirectPush,
            boolean requireLinearHistory) {

        BranchProtectionPolicy {
            if (requiredApprovals < 0) {
                throw new IllegalArgumentException("Approval count cannot be negative.");
            }

            requiredStatusChecks = Set.copyOf(requiredStatusChecks);

            if (requiredStatusChecks.stream().anyMatch(String::isBlank)) {
                throw new IllegalArgumentException("Status-check names cannot be blank.");
            }
        }
    }

    record PullRequest(
            long id,
            String sourceBranch,
            String targetBranch,
            ReviewState state,
            boolean draft,
            boolean branchSynchronized,
            boolean mergeConflict,
            List<Review> reviews,
            List<StatusCheck> statusChecks,
            boolean linearHistory) {

        PullRequest {
            if (id <= 0) {
                throw new IllegalArgumentException("Pull Request ID must be positive.");
            }

            Objects.requireNonNull(sourceBranch);
            Objects.requireNonNull(targetBranch);
            Objects.requireNonNull(state);

            if (sourceBranch.equals(targetBranch)) {
                throw new IllegalArgumentException("Source and target branches must differ.");
            }

            reviews = List.copyOf(reviews);
            statusChecks = List.copyOf(statusChecks);
        }
    }

    record RSAKeyPair(
            BigInteger p,
            BigInteger q,
            BigInteger n,
            BigInteger phi,
            BigInteger e,
            BigInteger d) {

        void validate() {
            if (!p.multiply(q).equals(n)) {
                throw new IllegalStateException("n must equal p*q.");
            }

            if (!e.gcd(phi).equals(BigInteger.ONE)) {
                throw new IllegalStateException("e must be coprime to phi(n).");
            }

            if (!e.multiply(d).mod(phi).equals(BigInteger.ONE)) {
                throw new IllegalStateException("d must be e^-1 mod phi(n).");
            }
        }
    }

    static final class RSAService {

        private RSAService() {
        }

        static RSAKeyPair generateKeys(int primeBits) {
            if (primeBits < 64) {
                throw new IllegalArgumentException(
                        "Educational enterprise model requires at least 64-bit primes.");
            }

            while (true) {
                BigInteger p = BigInteger.probablePrime(primeBits, RANDOM);
                BigInteger q = BigInteger.probablePrime(primeBits, RANDOM);

                if (p.equals(q)) {
                    continue;
                }

                BigInteger n = p.multiply(q);
                BigInteger phi = p.subtract(BigInteger.ONE)
                        .multiply(q.subtract(BigInteger.ONE));

                if (!PUBLIC_EXPONENT.gcd(phi).equals(BigInteger.ONE)) {
                    continue;
                }

                BigInteger d = PUBLIC_EXPONENT.modInverse(phi);

                RSAKeyPair keys = new RSAKeyPair(
                        p, q, n, phi, PUBLIC_EXPONENT, d);

                keys.validate();
                return keys;
            }
        }

        static BigInteger encrypt(BigInteger message, RSAKeyPair key) {
            validateRepresentative(message, key.n());
            return message.modPow(key.e(), key.n());
        }

        static BigInteger decrypt(BigInteger ciphertext, RSAKeyPair key) {
            validateRepresentative(ciphertext, key.n());
            return ciphertext.modPow(key.d(), key.n());
        }

        static BigInteger decryptWithCRT(
                BigInteger ciphertext,
                RSAKeyPair key) {

            validateRepresentative(ciphertext, key.n());

            BigInteger dp = key.d().mod(key.p().subtract(BigInteger.ONE));
            BigInteger dq = key.d().mod(key.q().subtract(BigInteger.ONE));

            BigInteger m1 = ciphertext.modPow(dp, key.p());
            BigInteger m2 = ciphertext.modPow(dq, key.q());

            BigInteger qInverse = key.q().modInverse(key.p());
            BigInteger h = m1.subtract(m2)
                    .multiply(qInverse)
                    .mod(key.p());

            return m2.add(h.multiply(key.q())).mod(key.n());
        }

        private static void validateRepresentative(
                BigInteger value,
                BigInteger modulus) {

            if (value == null) {
                throw new IllegalArgumentException("RSA representative cannot be null.");
            }

            if (value.signum() < 0 || value.compareTo(modulus) >= 0) {
                throw new IllegalArgumentException(
                        "RSA representative must satisfy 0 <= x < n.");
            }
        }
    }

    interface MergePolicy {
        Decision evaluate(PullRequest pullRequest);
    }

    record Decision(boolean eligible, List<String> reasons) {

        Decision {
            reasons = List.copyOf(reasons);
        }
    }

    static final class EnterpriseMergePolicy implements MergePolicy {

        private final BranchProtectionPolicy policy;

        EnterpriseMergePolicy(BranchProtectionPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        @Override
        public Decision evaluate(PullRequest pr) {
            List<String> failures = new ArrayList<>();

            if (pr.state() != ReviewState.OPEN &&
                    pr.state() != ReviewState.APPROVED) {
                failures.add("Pull Request is not open for merging.");
            }

            if (pr.draft()) {
                failures.add("Draft Pull Requests cannot merge.");
            }

            if (!pr.branchSynchronized()) {
                failures.add("Source branch is not synchronized with the target.");
            }

            if (pr.mergeConflict()) {
                failures.add("Merge conflict must be resolved.");
            }

            long approvals = pr.reviews()
                    .stream()
                    .filter(Review::countsAsApproval)
                    .count();

            if (approvals < policy.requiredApprovals()) {
                failures.add(
                        "Required approvals: "
                                + policy.requiredApprovals()
                                + ", effective approvals: "
                                + approvals + ".");
            }

            Map<String, StatusCheck> checksByName = pr.statusChecks()
                    .stream()
                    .collect(java.util.stream.Collectors.toMap(
                            StatusCheck::name,
                            check -> check,
                            (first, second) -> second));

            for (String required : policy.requiredStatusChecks()) {
                StatusCheck check = checksByName.get(required);

                if (check == null || !check.passed()) {
                    failures.add("Required status check failed: " + required);
                }
            }

            if (policy.requireResolvedConversations()) {
                boolean unresolved = pr.reviews()
                        .stream()
                        .anyMatch(Review::unresolvedConversation);

                if (unresolved) {
                    failures.add("Unresolved review conversations remain.");
                }
            }

            if (policy.requireLinearHistory() && !pr.linearHistory()) {
                failures.add("Linear-history policy is not satisfied.");
            }

            return new Decision(failures.isEmpty(), failures);
        }
    }

    static void validateMathematics() {
        BigInteger value = BigInteger.valueOf(7)
                .modPow(BigInteger.valueOf(560), BigInteger.valueOf(561));

        if (!value.equals(BigInteger.ONE)) {
            throw new IllegalStateException("Modular exponentiation test failed.");
        }

        BigInteger inverse = BigInteger.valueOf(17)
                .modInverse(BigInteger.valueOf(3120));

        if (!inverse.equals(BigInteger.valueOf(2753))) {
            throw new IllegalStateException("Modular inverse test failed.");
        }
    }

    static PullRequest createEnterprisePullRequest() {
        List<Review> reviews = List.of(
                new Review(
                        "security-reviewer",
                        ReviewDecision.APPROVE,
                        false,
                        false),
                new Review(
                        "platform-reviewer",
                        ReviewDecision.APPROVE,
                        false,
                        false)
        );

        List<StatusCheck> checks = List.of(
                new StatusCheck("unit-tests", true, true),
                new StatusCheck("security-scan", true, true),
                new StatusCheck("documentation", false, false)
        );

        return new PullRequest(
                1042L,
                "feature/rsa-service",
                "main",
                ReviewState.APPROVED,
                false,
                true,
                false,
                reviews,
                checks,
                true
        );
    }

    public static void main(String[] args) {
        try {
            validateMathematics();

            RSAKeyPair keys = RSAService.generateKeys(128);

            System.out.println("RSA enterprise mathematics model");
            System.out.println("p   = " + keys.p());
            System.out.println("q   = " + keys.q());
            System.out.println("n   = " + keys.n());
            System.out.println("phi = " + keys.phi());
            System.out.println("e   = " + keys.e());
            System.out.println("d   = " + keys.d());

            BigInteger message = BigInteger.valueOf(123456789);
            BigInteger ciphertext = RSAService.encrypt(message, keys);
            BigInteger recovered = RSAService.decrypt(ciphertext, keys);
            BigInteger crtRecovered =
                    RSAService.decryptWithCRT(ciphertext, keys);

            if (!message.equals(recovered) ||
                    !message.equals(crtRecovered)) {
                throw new IllegalStateException("RSA round-trip failed.");
            }

            System.out.println("\nRSA operation");
            System.out.println("message    = " + message);
            System.out.println("ciphertext = " + ciphertext);
            System.out.println("decrypted  = " + recovered);
            System.out.println("CRT        = " + crtRecovered);

            BranchProtectionPolicy policy =
                    new BranchProtectionPolicy(
                            2,
                            Set.of("unit-tests", "security-scan"),
                            true,
                            true,
                            true,
                            true);

            PullRequest pullRequest = createEnterprisePullRequest();

            MergePolicy mergePolicy =
                    new EnterpriseMergePolicy(policy);

            Decision decision = mergePolicy.evaluate(pullRequest);

            System.out.println("\nEnterprise merge policy");
            System.out.println("Pull Request #" + pullRequest.id());
            System.out.println("Eligible: " + decision.eligible());

            if (!decision.eligible()) {
                decision.reasons().forEach(reason ->
                        System.out.println("Reason: " + reason));
            }

            // Stale approvals are represented explicitly by dismissal or
            // unresolved conversations rather than being treated as valid.
            PullRequest invalid = new PullRequest(
                    pullRequest.id(),
                    pullRequest.sourceBranch(),
                    pullRequest.targetBranch(),
                    ReviewState.OPEN,
                    false,
                    false,
                    false,
                    pullRequest.reviews(),
                    pullRequest.statusChecks(),
                    true
            );

            Decision invalidDecision = mergePolicy.evaluate(invalid);

            System.out.println("\nStale branch evaluation");
            System.out.println("Eligible: " + invalidDecision.eligible());
            invalidDecision.reasons()
                    .forEach(reason -> System.out.println("Reason: " + reason));

        } catch (RuntimeException exception) {
            System.err.println("Execution failed: " + exception.getMessage());
            System.exit(1);
        }
    }
}
