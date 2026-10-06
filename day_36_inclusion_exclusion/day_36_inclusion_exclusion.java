/*
 * Inclusion-Exclusion Principle
 *
 * Enterprise-oriented case study:
 * An analytics service evaluates overlapping customer eligibility
 * populations. Customers may qualify through several independent rules,
 * and the service must distinguish "at least one rule", "exactly two",
 * "all rules", and "none".
 *
 * Compile:
 *   javac InclusionExclusion.java
 *
 * Run:
 *   java InclusionExclusion
 */

import java.util.ArrayList;
import java.util.EnumSet;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;

public class InclusionExclusion {

    enum EligibilityRule {
        ACTIVE_SUBSCRIPTION,
        VERIFIED_IDENTITY,
        RECENT_PURCHASE
    }

    enum MembershipCategory {
        NONE,
        ONLY_ONE,
        EXACTLY_TWO,
        ALL_THREE
    }

    record Customer(
        int id,
        String name,
        EnumSet<EligibilityRule> rules
    ) {
        Customer {
            if (id <= 0) {
                throw new IllegalArgumentException("Customer ID must be positive.");
            }

            Objects.requireNonNull(name, "name");
            Objects.requireNonNull(rules, "rules");

            // Defensive copying prevents callers from mutating the record's
            // rule state through the original mutable EnumSet.
            rules = EnumSet.copyOf(rules);
        }
    }

    record MembershipReport(
        int none,
        int onlyOne,
        int exactlyTwo,
        int allThree,
        int atLeastOne
    ) {}

    interface EligibilityPolicy {
        boolean accepts(Customer customer);
    }

    static final class RulePolicy implements EligibilityPolicy {
        private final EligibilityRule requiredRule;

        RulePolicy(EligibilityRule requiredRule) {
            this.requiredRule = Objects.requireNonNull(requiredRule);
        }

        @Override
        public boolean accepts(Customer customer) {
            return customer.rules().contains(requiredRule);
        }
    }

    static final class EligibilityService {

        private final List<EligibilityPolicy> policies;

        EligibilityService(List<EligibilityPolicy> policies) {
            if (policies == null || policies.isEmpty()) {
                throw new IllegalArgumentException(
                    "At least one eligibility policy is required."
                );
            }

            this.policies = List.copyOf(policies);
        }

        MembershipReport evaluate(List<Customer> customers) {
            Objects.requireNonNull(customers, "customers");

            int none = 0;
            int onlyOne = 0;
            int exactlyTwo = 0;
            int allThree = 0;

            for (Customer customer : customers) {
                int satisfied = 0;

                for (EligibilityPolicy policy : policies) {
                    if (policy.accepts(customer)) {
                        satisfied++;
                    }
                }

                switch (satisfied) {
                    case 0 -> none++;
                    case 1 -> onlyOne++;
                    case 2 -> exactlyTwo++;
                    default -> allThree++;
                }
            }

            return new MembershipReport(
                none,
                onlyOne,
                exactlyTwo,
                allThree,
                customers.size() - none
            );
        }
    }

    // -------------------------------------------------------------------------
    // Generic set-based inclusion-exclusion
    // -------------------------------------------------------------------------

    static int inclusionExclusion(Set<Integer>[] sets) {
        if (sets.length == 0) {
            return 0;
        }

        int result = 0;
        int combinations = 1 << sets.length;

        for (int mask = 1; mask < combinations; mask++) {
            Set<Integer> intersection = null;
            int selected = 0;

            for (int index = 0; index < sets.length; index++) {
                if ((mask & (1 << index)) != 0) {
                    selected++;

                    if (intersection == null) {
                        intersection = new HashSet<>(sets[index]);
                    } else {
                        intersection.retainAll(sets[index]);
                    }
                }
            }

            int term = intersection == null ? 0 : intersection.size();

            if (selected % 2 == 1) {
                result += term;
            } else {
                result -= term;
            }
        }

        return result;
    }

    // -------------------------------------------------------------------------
    // Divisibility counting
    // -------------------------------------------------------------------------

    static long gcd(long a, long b) {
        a = Math.abs(a);
        b = Math.abs(b);

        while (b != 0) {
            long remainder = a % b;
            a = b;
            b = remainder;
        }

        return a;
    }

    static long lcm(long a, long b) {
        return Math.abs((a / gcd(a, b)) * b);
    }

    static long countMultiples(long limit, List<Long> divisors) {
        if (limit < 0) {
            throw new IllegalArgumentException("Limit cannot be negative.");
        }

        if (divisors.isEmpty()) {
            return 0;
        }

        for (long divisor : divisors) {
            if (divisor <= 0) {
                throw new IllegalArgumentException(
                    "Divisors must be positive."
                );
            }
        }

        long result = 0;
        int combinations = 1 << divisors.size();

        for (int mask = 1; mask < combinations; mask++) {
            long commonMultiple = 1;
            int selected = 0;

            for (int index = 0; index < divisors.size(); index++) {
                if ((mask & (1 << index)) != 0) {
                    selected++;
                    commonMultiple = lcm(
                        commonMultiple,
                        divisors.get(index)
                    );

                    if (commonMultiple > limit) {
                        break;
                    }
                }
            }

            if (commonMultiple <= limit) {
                long term = limit / commonMultiple;

                result += selected % 2 == 1 ? term : -term;
            }
        }

        return result;
    }

    // -------------------------------------------------------------------------
    // Derangements
    // -------------------------------------------------------------------------

    static long factorial(int n) {
        long result = 1;

        for (int value = 2; value <= n; value++) {
            result *= value;
        }

        return result;
    }

    static long derangements(int n) {
        if (n < 0 || n > 20) {
            throw new IllegalArgumentException(
                "This implementation supports 0 <= n <= 20."
            );
        }

        long result = 0;

        for (int fixedPositions = 0;
             fixedPositions <= n;
             fixedPositions++) {

            long term = factorial(n) / factorial(fixedPositions);

            result += fixedPositions % 2 == 0
                ? term
                : -term;
        }

        return result;
    }

    // -------------------------------------------------------------------------
    // Test support
    // -------------------------------------------------------------------------

    static void require(boolean condition, String message) {
        if (!condition) {
            throw new IllegalStateException(message);
        }
    }

    static void runTests() {
        Set<Integer> a = Set.of(1, 2, 3, 4);
        Set<Integer> b = Set.of(3, 4, 5, 6);
        Set<Integer> c = Set.of(4, 6, 7);

        @SuppressWarnings("unchecked")
        Set<Integer>[] sets = new Set[]{a, b, c};

        require(
            inclusionExclusion(sets) == 7,
            "General set union calculation failed."
        );

        require(
            countMultiples(100, List.of(2L, 3L)) == 67,
            "Two-divisor count failed."
        );

        require(
            countMultiples(100, List.of(2L, 3L, 5L)) == 74,
            "Three-divisor count failed."
        );

        require(derangements(0) == 1, "D(0) failed.");
        require(derangements(4) == 9, "D(4) failed.");
    }

    // -------------------------------------------------------------------------
    // Enterprise case
    // -------------------------------------------------------------------------

    static List<Customer> createCustomers() {
        List<Customer> customers = new ArrayList<>();

        for (int id = 1; id <= 100; id++) {
            EnumSet<EligibilityRule> rules =
                EnumSet.noneOf(EligibilityRule.class);

            if (id <= 55) {
                rules.add(EligibilityRule.ACTIVE_SUBSCRIPTION);
            }

            if (id >= 31 && id <= 80) {
                rules.add(EligibilityRule.VERIFIED_IDENTITY);
            }

            if (id >= 61 && id <= 95) {
                rules.add(EligibilityRule.RECENT_PURCHASE);
            }

            customers.add(
                new Customer(id, "Customer-" + id, rules)
            );
        }

        return customers;
    }

    public static void main(String[] args) {
        runTests();

        System.out.println("INCLUSION-EXCLUSION ENTERPRISE CASE STUDY");
        System.out.println("=".repeat(72));

        List<EligibilityPolicy> policies = List.of(
            new RulePolicy(EligibilityRule.ACTIVE_SUBSCRIPTION),
            new RulePolicy(EligibilityRule.VERIFIED_IDENTITY),
            new RulePolicy(EligibilityRule.RECENT_PURCHASE)
        );

        EligibilityService service = new EligibilityService(policies);
        List<Customer> customers = createCustomers();

        MembershipReport report = service.evaluate(customers);

        System.out.println("\nEligibility population");
        System.out.println("-".repeat(72));
        System.out.println("Customers: " + customers.size());
        System.out.println("At least one rule: " + report.atLeastOne());
        System.out.println("None: " + report.none());
        System.out.println("Exactly one: " + report.onlyOne());
        System.out.println("Exactly two: " + report.exactlyTwo());
        System.out.println("All three: " + report.allThree());

        System.out.println("\nDivisibility application");
        System.out.println("-".repeat(72));
        System.out.println(
            "Multiples of 2 or 3 through 100: " +
            countMultiples(100, List.of(2L, 3L))
        );

        System.out.println(
            "Multiples of 2, 3, or 5 through 100: " +
            countMultiples(100, List.of(2L, 3L, 5L))
        );

        System.out.println("\nDerangement application");
        System.out.println("-".repeat(72));
        for (int n = 1; n <= 7; n++) {
            System.out.println("D(" + n + ") = " + derangements(n));
        }

        System.out.println("\nDesign characteristics");
        System.out.println("-".repeat(72));
        System.out.println(
            "Eligibility rules are represented as domain policies, so the "
            + "membership decision is not encoded as a collection of "
            + "unrelated print statements."
        );
        System.out.println(
            "EnumSet expresses a small closed set of rule memberships "
            + "efficiently and prevents invalid rule names."
        );
        System.out.println(
            "The general inclusion-exclusion implementation remains "
            + "exponential in the number of sets because it evaluates every "
            + "non-empty subset of the input sets."
        );
    }
}
