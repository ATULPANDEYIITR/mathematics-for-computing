import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.LongUnaryOperator;

/*
 * Enterprise-oriented recurrence analysis for a distributed analytics
 * platform. Each workload has a branching factor, shrink factor, local
 * processing cost, and base-task cost.
 *
 * Compile:
 *   javac AdvancedRecurrences.java
 *
 * Run:
 *   java AdvancedRecurrences
 */
public class AdvancedRecurrences {

    enum MasterCase {
        LEAF_DOMINATED,
        BALANCED,
        COMBINE_DOMINATED_CANDIDATE
    }

    record Classification(
        MasterCase category,
        double criticalExponent,
        String explanation
    ) {}

    record TreeLevel(
        long depth,
        long nodes,
        long subproblemSize,
        long localCost,
        long aggregateCost
    ) {}

    static final class WorkloadPolicy {
        private final String name;
        private final long branchingFactor;
        private final long shrinkFactor;
        private final LongUnaryOperator localCost;
        private final long baseCost;

        WorkloadPolicy(
            String name,
            long branchingFactor,
            long shrinkFactor,
            LongUnaryOperator localCost,
            long baseCost
        ) {
            this.name = Objects.requireNonNull(name);
            this.localCost = Objects.requireNonNull(localCost);

            if (branchingFactor < 1) {
                throw new IllegalArgumentException(
                    "Branching factor must be positive"
                );
            }
            if (shrinkFactor <= 1) {
                throw new IllegalArgumentException(
                    "Shrink factor must exceed one"
                );
            }
            if (baseCost < 0) {
                throw new IllegalArgumentException(
                    "Base cost cannot be negative"
                );
            }

            this.branchingFactor = branchingFactor;
            this.shrinkFactor = shrinkFactor;
            this.baseCost = baseCost;
        }

        String name() {
            return name;
        }

        long branchingFactor() {
            return branchingFactor;
        }

        long shrinkFactor() {
            return shrinkFactor;
        }

        long baseCost() {
            return baseCost;
        }

        long localCost(long n) {
            long value = localCost.applyAsLong(n);
            if (value < 0) {
                throw new IllegalArgumentException(
                    "Local work cannot be negative"
                );
            }
            return value;
        }
    }

    static final class CostEvaluator {
        private final WorkloadPolicy policy;
        private final Map<Long, Long> memo = new HashMap<>();

        CostEvaluator(WorkloadPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        long evaluate(long n) {
            if (n < 1) {
                throw new IllegalArgumentException(
                    "Problem size must be positive"
                );
            }
            if (n == 1) {
                return policy.baseCost();
            }

            Long cached = memo.get(n);
            if (cached != null) {
                return cached;
            }

            // Ceiling division keeps every nonempty input represented
            // when a size is not divisible by the shrink factor.
            long b = policy.shrinkFactor();
            long childSize = n / b + (n % b == 0 ? 0 : 1);

            long descendants = Math.multiplyExact(
                policy.branchingFactor(),
                evaluate(childSize)
            );
            long result = Math.addExact(
                descendants,
                policy.localCost(n)
            );

            memo.put(n, result);
            return result;
        }

        List<TreeLevel> tree(long n) {
            if (n < 1) {
                throw new IllegalArgumentException(
                    "Problem size must be positive"
                );
            }

            List<TreeLevel> levels = new ArrayList<>();
            long nodes = 1;
            long size = n;
            long depth = 0;

            while (size > 1) {
                long local = policy.localCost(size);
                levels.add(new TreeLevel(
                    depth,
                    nodes,
                    size,
                    local,
                    Math.multiplyExact(nodes, local)
                ));

                nodes = Math.multiplyExact(
                    nodes,
                    policy.branchingFactor()
                );
                size = Math.max(1, size / policy.shrinkFactor());
                depth++;
            }

            levels.add(new TreeLevel(
                depth,
                nodes,
                1,
                policy.baseCost(),
                Math.multiplyExact(nodes, policy.baseCost())
            ));

            return List.copyOf(levels);
        }
    }

    static Classification classify(
        long a,
        long b,
        double polynomialPower
    ) {
        if (a < 1 || b <= 1 || !Double.isFinite(polynomialPower)
            || polynomialPower < 0) {
            throw new IllegalArgumentException(
                "Invalid Master Theorem parameters"
            );
        }

        double critical = Math.log(a) / Math.log(b);
        double epsilon = 1e-10;

        if (polynomialPower < critical - epsilon) {
            return new Classification(
                MasterCase.LEAF_DOMINATED,
                critical,
                "Leaf contribution determines the asymptotic order."
            );
        }

        if (Math.abs(polynomialPower - critical) <= epsilon) {
            return new Classification(
                MasterCase.BALANCED,
                critical,
                "Every level contributes the same asymptotic order."
            );
        }

        return new Classification(
            MasterCase.COMBINE_DOMINATED_CANDIDATE,
            critical,
            "Combine work dominates if the regularity condition holds."
        );
    }

    static void report(WorkloadPolicy policy, long n) {
        CostEvaluator evaluator = new CostEvaluator(policy);
        List<TreeLevel> levels = evaluator.tree(n);

        System.out.println("\nWorkload: " + policy.name());
        System.out.printf(
            "%-8s %-12s %-16s %-16s %-16s%n",
            "Depth", "Nodes", "Subproblem", "Local cost", "Level cost"
        );

        for (TreeLevel level : levels) {
            System.out.printf(
                "%-8d %-12d %-16d %-16d %-16d%n",
                level.depth(),
                level.nodes(),
                level.subproblemSize(),
                level.localCost(),
                level.aggregateCost()
            );
        }

        System.out.println(
            "Recurrence evaluation: " + evaluator.evaluate(n)
        );
    }

    public static void main(String[] args) {
        WorkloadPolicy batchMerge = new WorkloadPolicy(
            "Batch merge and aggregation",
            2,
            2,
            n -> n,
            1
        );

        WorkloadPolicy indexedLookup = new WorkloadPolicy(
            "Indexed search",
            1,
            2,
            n -> 1,
            1
        );

        WorkloadPolicy expensiveTransform = new WorkloadPolicy(
            "Quadratic data transformation",
            2,
            2,
            n -> Math.multiplyExact(n, n),
            1
        );

        report(batchMerge, 16);
        report(indexedLookup, 16);
        report(expensiveTransform, 8);

        System.out.println("\nMaster Theorem classifications");
        long[][] configurations = {
            {2, 2, 1},
            {1, 2, 0},
            {2, 2, 2},
            {4, 2, 1}
        };

        for (long[] configuration : configurations) {
            Classification result = classify(
                configuration[0],
                configuration[1],
                configuration[2]
            );

            System.out.printf(
                "a=%d, b=%d, p=%d: %s, critical exponent=%.4f%n",
                configuration[0],
                configuration[1],
                configuration[2],
                result.category(),
                result.criticalExponent()
            );
            System.out.println(result.explanation());
        }

        System.out.println("\nFailure handling");
        try {
            new CostEvaluator(batchMerge).evaluate(0);
        } catch (IllegalArgumentException exception) {
            System.out.println(
                "Rejected invalid workload: " + exception.getMessage()
            );
        }

        try {
            new CostEvaluator(expensiveTransform).evaluate(1_000_000_000L);
        } catch (ArithmeticException exception) {
            System.out.println(
                "Rejected overflowing cost calculation: "
                    + exception.getMessage()
            );
        }

        System.out.println(
            "\nInteger cost models describe operation counts, not elapsed "
            + "time. Network delay, contention, scheduling, and unequal "
            + "subproblems require separate measurements."
        );
    }
}
