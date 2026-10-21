import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/*
 * Topic: Number Theory Fundamentals
 *
 * Enterprise scenario:
 * A repository platform assigns numeric identifiers to repositories and uses
 * number-theoretic validation to classify identifiers, partition workloads,
 * and enforce mathematical policies.
 *
 * Compile:
 * javac NumberTheoryEnterprise.java
 *
 * Run:
 * java NumberTheoryEnterprise
 */
public class NumberTheoryEnterprise {

    enum NumberClass {
        NEGATIVE,
        ZERO,
        UNIT,
        PRIME,
        COMPOSITE
    }

    record Repository(
            long id,
            String organization,
            String name
    ) {
        Repository {
            if (id <= 0) {
                throw new DomainException(
                        "Repository ID must be positive.");
            }
            if (organization == null || organization.isBlank()) {
                throw new DomainException(
                        "Organization is required.");
            }
            if (name == null || name.isBlank()) {
                throw new DomainException(
                        "Repository name is required.");
            }
        }
    }

    record ReviewBatch(
            long reviewers,
            long changes
    ) {
        ReviewBatch {
            if (reviewers <= 0 || changes <= 0) {
                throw new DomainException(
                        "Reviewers and changes must be positive.");
            }
        }

        long maximumEqualAssignment() {
            return NumberTheory.gcd(reviewers, changes);
        }
    }

    record NumberProfile(
            long value,
            NumberClass classification,
            List<Long> divisors,
            Map<Long, Integer> primeFactorization
    ) {
        NumberProfile {
            divisors = List.copyOf(divisors);
            primeFactorization = Collections.unmodifiableMap(
                    new LinkedHashMap<>(primeFactorization)
            );
        }
    }

    interface NumberPolicy {
        boolean accepts(long value);

        String reason();
    }

    static final class PrimeIdentifierPolicy implements NumberPolicy {
        @Override
        public boolean accepts(long value) {
            return NumberTheory.isPrime(value);
        }

        @Override
        public String reason() {
            return "Identifier must be prime.";
        }
    }

    static final class DivisibleByPolicy implements NumberPolicy {
        private final long divisor;

        DivisibleByPolicy(long divisor) {
            if (divisor == 0) {
                throw new DomainException(
                        "Policy divisor cannot be zero.");
            }
            this.divisor = Math.abs(divisor);
        }

        @Override
        public boolean accepts(long value) {
            return NumberTheory.divides(divisor, value);
        }

        @Override
        public String reason() {
            return "Identifier must be divisible by " + divisor + ".";
        }
    }

    static final class RepositoryGovernanceService {
        private final List<NumberPolicy> policies;

        RepositoryGovernanceService(List<NumberPolicy> policies) {
            if (policies == null || policies.isEmpty()) {
                throw new DomainException(
                        "At least one policy is required.");
            }
            this.policies = List.copyOf(policies);
        }

        boolean eligible(Repository repository) {
            return policies.stream()
                    .allMatch(policy -> policy.accepts(repository.id()));
        }

        List<String> violations(Repository repository) {
            return policies.stream()
                    .filter(policy -> !policy.accepts(repository.id()))
                    .map(NumberPolicy::reason)
                    .toList();
        }
    }

    static final class DomainException extends RuntimeException {
        DomainException(String message) {
            super(message);
        }
    }

    static final class NumberTheory {
        private NumberTheory() {
        }

        static boolean divides(long divisor, long value) {
            if (divisor == 0) {
                throw new DomainException(
                        "Zero cannot be a divisor.");
            }
            return value % divisor == 0;
        }

        static NumberClass classify(long value) {
            if (value < 0) return NumberClass.NEGATIVE;
            if (value == 0) return NumberClass.ZERO;
            if (value == 1) return NumberClass.UNIT;
            return isPrime(value)
                    ? NumberClass.PRIME
                    : NumberClass.COMPOSITE;
        }

        static boolean isPrime(long value) {
            if (value < 2) return false;
            if (value == 2) return true;
            if (value % 2 == 0) return false;

            for (long candidate = 3;
                 candidate <= value / candidate;
                 candidate += 2) {
                if (value % candidate == 0) {
                    return false;
                }
            }

            return true;
        }

        static boolean isComposite(long value) {
            if (value <= 0) {
                throw new DomainException(
                        "Composite classification requires a positive value.");
            }
            return value > 1 && !isPrime(value);
        }

        static List<Long> divisors(long value) {
            if (value <= 0) {
                throw new DomainException(
                        "Divisor enumeration requires a positive value.");
            }

            List<Long> result = new ArrayList<>();

            for (long candidate = 1;
                 candidate <= value / candidate;
                 candidate++) {
                if (value % candidate == 0) {
                    result.add(candidate);

                    long paired = value / candidate;
                    if (paired != candidate) {
                        result.add(paired);
                    }
                }
            }

            result.sort(Long::compareTo);
            return result;
        }

        static Map<Long, Integer> primeFactorization(long value) {
            if (value <= 0) {
                throw new DomainException(
                        "Factorization requires a positive value.");
            }

            Map<Long, Integer> factors = new LinkedHashMap<>();
            long remaining = value;

            while (remaining % 2 == 0 && remaining > 1) {
                factors.merge(2L, 1, Integer::sum);
                remaining /= 2;
            }

            for (long candidate = 3;
                 candidate <= remaining / candidate;
                 candidate += 2) {

                while (remaining % candidate == 0) {
                    factors.merge(candidate, 1, Integer::sum);
                    remaining /= candidate;
                }
            }

            if (remaining > 1) {
                factors.merge(remaining, 1, Integer::sum);
            }

            return factors;
        }

        static long gcd(long a, long b) {
            if (a == 0 && b == 0) {
                throw new DomainException(
                        "gcd(0, 0) is undefined.");
            }

            /*
             * The iterative Euclidean algorithm avoids constructing all
             * divisors and gives logarithmic-time behavior in input size.
             */
            a = Math.abs(a);
            b = Math.abs(b);

            while (b != 0) {
                long remainder = a % b;
                a = b;
                b = remainder;
            }

            return a;
        }

        static long gcdMany(List<Long> values) {
            if (values == null || values.isEmpty()) {
                throw new DomainException(
                        "At least one value is required.");
            }

            long result = 0;
            for (long value : values) {
                result = gcd(result, value);
            }

            return result;
        }
    }

    static NumberProfile profile(long value) {
        return new NumberProfile(
                value,
                NumberTheory.classify(value),
                NumberTheory.divisors(value),
                NumberTheory.primeFactorization(value)
        );
    }

    static String formatFactorization(Map<Long, Integer> factors) {
        StringBuilder output = new StringBuilder();

        for (Map.Entry<Long, Integer> entry : factors.entrySet()) {
            if (output.length() > 0) {
                output.append(" × ");
            }

            output.append(entry.getKey());

            if (entry.getValue() > 1) {
                output.append("^").append(entry.getValue());
            }
        }

        return output.toString();
    }

    public static void main(String[] args) {
        try {
            System.out.println("NUMBER THEORY ENTERPRISE MODEL");
            System.out.println("=".repeat(72));

            List<Repository> repositories = List.of(
                    new Repository(
                            84,
                            "platform",
                            "release-service"),
                    new Repository(
                            97,
                            "security",
                            "policy-engine"),
                    new Repository(
                            360,
                            "data",
                            "warehouse-loader")
            );

            NumberPolicy primePolicy = new PrimeIdentifierPolicy();
            NumberPolicy evenPolicy = new DivisibleByPolicy(2);

            RepositoryGovernanceService governance =
                    new RepositoryGovernanceService(
                            List.of(evenPolicy));

            for (Repository repository : repositories) {
                NumberProfile profile = profile(repository.id());

                System.out.println("\n"
                        + repository.organization()
                        + "/"
                        + repository.name());

                System.out.println("ID: " + profile.value());
                System.out.println(
                        "Class: " + profile.classification());
                System.out.println(
                        "Divisors: " + profile.divisors());
                System.out.println(
                        "Prime factorization: "
                                + formatFactorization(
                                        profile.primeFactorization()));

                System.out.println(
                        "Even-ID policy eligible: "
                                + governance.eligible(repository));

                if (!governance.eligible(repository)) {
                    System.out.println(
                            "Policy violations: "
                                    + governance.violations(repository));
                }

                System.out.println(
                        "Prime-ID policy: "
                                + primePolicy.accepts(repository.id()));
            }

            System.out.println("\nREVIEW WORKLOAD PARTITIONING");

            ReviewBatch batch = new ReviewBatch(84, 126);
            long equalUnit = batch.maximumEqualAssignment();

            System.out.println(
                    "Reviewers: " + batch.reviewers());
            System.out.println(
                    "Changes: " + batch.changes());
            System.out.println(
                    "Maximum equal assignment: " + equalUnit);

            System.out.println("\nMULTI-VALUE GCD");

            List<Long> workload = List.of(84L, 126L, 210L);
            long common = NumberTheory.gcdMany(workload);

            System.out.println("Workload: " + workload);
            System.out.println("GCD: " + common);

            System.out.println("\nFAILURE STATES");

            try {
                NumberTheory.divisors(0);
            } catch (DomainException exception) {
                System.out.println(
                        "Zero divisor enumeration rejected: "
                                + exception.getMessage());
            }

            try {
                NumberTheory.gcd(0, 0);
            } catch (DomainException exception) {
                System.out.println(
                        "Undefined GCD rejected: "
                                + exception.getMessage());
            }

            /*
             * Java long has fixed-width limits. For values exceeding signed
             * 64-bit range, BigInteger should replace long throughout the
             * domain model and algorithms.
             */
        } catch (DomainException exception) {
            System.err.println(
                    "Domain failure: " + exception.getMessage());
            System.exit(1);
        }
    }
}
