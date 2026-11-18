import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * Sampling Theory Enterprise Analytics.
 *
 * Java 17
 * No third-party dependencies.
 */
public class SamplingTheoryEnterprise {

    enum SamplingMethod {
        SIMPLE_RANDOM,
        STRATIFIED,
        SYSTEMATIC
    }

    enum BiasSeverity {
        LOW,
        MODERATE,
        HIGH
    }

    record Employee(
        int id,
        String department,
        int age,
        double income,
        double outcome
    ) {
        Employee {
            if (id <= 0) {
                throw new IllegalArgumentException("Invalid employee ID.");
            }

            Objects.requireNonNull(department);

            if (department.isBlank()) {
                throw new IllegalArgumentException("Department is required.");
            }

            if (age < 18 || age > 100) {
                throw new IllegalArgumentException("Invalid age.");
            }

            if (!Double.isFinite(income) || income < 0) {
                throw new IllegalArgumentException("Invalid income.");
            }

            if (!Double.isFinite(outcome)) {
                throw new IllegalArgumentException("Invalid outcome.");
            }
        }
    }

    record Sample(
        SamplingMethod method,
        List<Employee> employees,
        int populationSize,
        long seed
    ) {
        Sample {
            employees = List.copyOf(employees);

            if (employees.isEmpty()) {
                throw new IllegalArgumentException("Sample cannot be empty.");
            }

            if (employees.size() > populationSize) {
                throw new IllegalArgumentException("Invalid sample size.");
            }
        }

        double samplingFraction() {
            return (double) employees.size() / populationSize;
        }
    }

    record StatisticalEstimate(
        double mean,
        double variance,
        double standardError,
        double lowerBound,
        double upperBound
    ) {}

    record StratumStatistics(
        String department,
        int populationCount,
        int sampleCount,
        double populationWeight,
        double sampleWeight,
        double sampleMean
    ) {}

    static final class SamplingException extends RuntimeException {
        SamplingException(String message) {
            super(message);
        }
    }

    static final class SampleSizeCalculator {

        static int proportion(
            double z,
            double margin,
            double expectedProportion,
            int populationSize
        ) {
            if (
                z <= 0 ||
                margin <= 0 ||
                margin >= 1 ||
                expectedProportion <= 0 ||
                expectedProportion >= 1 ||
                populationSize <= 0
            ) {
                throw new IllegalArgumentException(
                    "Invalid sample-size parameters."
                );
            }

            double n0 = (
                z * z * expectedProportion *
                (1 - expectedProportion)
            ) / (margin * margin);

            if (populationSize == 1) {
                return 1;
            }

            double adjusted = n0 /
                (1 + (n0 - 1) / populationSize);

            return Math.min(
                populationSize,
                (int) Math.ceil(adjusted)
            );
        }

        static int mean(
            double z,
            double standardDeviation,
            double margin,
            int populationSize
        ) {
            if (
                z <= 0 ||
                standardDeviation <= 0 ||
                margin <= 0 ||
                populationSize <= 0
            ) {
                throw new IllegalArgumentException(
                    "Invalid mean sample-size parameters."
                );
            }

            double n0 = Math.pow(
                z * standardDeviation / margin,
                2
            );

            if (populationSize == 1) {
                return 1;
            }

            double adjusted = n0 /
                (1 + (n0 - 1) / populationSize);

            return Math.min(
                populationSize,
                (int) Math.ceil(adjusted)
            );
        }

        static int recruitmentTarget(
            int required,
            double responseRate
        ) {
            if (required <= 0 ||
                responseRate <= 0 ||
                responseRate > 1) {
                throw new IllegalArgumentException(
                    "Invalid recruitment parameters."
                );
            }

            return (int) Math.ceil(required / responseRate);
        }
    }

    static final class SamplingService {

        private final List<Employee> population;
        private final Random random;

        SamplingService(List<Employee> population, long seed) {
            if (population == null || population.isEmpty()) {
                throw new SamplingException("Population is empty.");
            }

            Set<Integer> ids = new HashSet<>();

            for (Employee employee : population) {
                if (!ids.add(employee.id())) {
                    throw new SamplingException("Duplicate employee ID.");
                }
            }

            this.population = List.copyOf(population);
            this.random = new Random(seed);
        }

        private void validateSize(int n) {
            if (n <= 0 || n > population.size()) {
                throw new SamplingException(
                    "Sample size must be between 1 and N."
                );
            }
        }

        Sample simpleRandom(int n, long seed) {
            validateSize(n);

            List<Employee> shuffled = new ArrayList<>(population);

            Collections.shuffle(
                shuffled,
                new Random(seed)
            );

            return new Sample(
                SamplingMethod.SIMPLE_RANDOM,
                shuffled.subList(0, n),
                population.size(),
                seed
            );
        }

        Sample stratified(int n, long seed) {
            validateSize(n);

            Map<String, List<Employee>> groups =
                population.stream().collect(
                    Collectors.groupingBy(
                        Employee::department,
                        TreeMap::new,
                        Collectors.toList()
                    )
                );

            int H = groups.size();

            if (n < H) {
                throw new SamplingException(
                    "Every stratum must be represented."
                );
            }

            record Allocation(
                String name,
                int capacity,
                int count,
                double remainder
            ) {}

            List<String> names = new ArrayList<>(groups.keySet());

            List<Integer> allocations = new ArrayList<>();
            List<Double> remainders = new ArrayList<>();

            for (String name : names) {
                int capacity = groups.get(name).size();

                double raw =
                    (double) n * capacity / population.size();

                int count = Math.max(1, (int) Math.floor(raw));

                allocations.add(count);
                remainders.add(raw - Math.floor(raw));
            }

            int allocated = allocations.stream()
                .mapToInt(Integer::intValue)
                .sum();

            while (allocated > n) {
                int selected = -1;

                for (int i = 0; i < names.size(); i++) {
                    if (allocations.get(i) > 1 &&
                        (selected == -1 ||
                         remainders.get(i) < remainders.get(selected))) {
                        selected = i;
                    }
                }

                if (selected == -1) {
                    throw new SamplingException(
                        "Allocation is infeasible."
                    );
                }

                allocations.set(
                    selected,
                    allocations.get(selected) - 1
                );

                allocated--;
            }

            while (allocated < n) {
                int selected = -1;

                for (int i = 0; i < names.size(); i++) {
                    if (allocations.get(i) < groups.get(names.get(i)).size() &&
                        (selected == -1 ||
                         remainders.get(i) > remainders.get(selected))) {
                        selected = i;
                    }
                }

                if (selected == -1) {
                    throw new SamplingException(
                        "Allocation exceeds stratum capacity."
                    );
                }

                allocations.set(
                    selected,
                    allocations.get(selected) + 1
                );

                remainders.set(selected, -1.0);
                allocated++;
            }

            Random localRandom = new Random(seed);
            List<Employee> selected = new ArrayList<>();

            for (int i = 0; i < names.size(); i++) {
                List<Employee> members =
                    new ArrayList<>(groups.get(names.get(i)));

                Collections.shuffle(members, localRandom);

                selected.addAll(
                    members.subList(0, allocations.get(i))
                );
            }

            Collections.shuffle(selected, localRandom);

            return new Sample(
                SamplingMethod.STRATIFIED,
                selected,
                population.size(),
                seed
            );
        }

        Sample systematic(int n, long seed) {
            validateSize(n);

            Random localRandom = new Random(seed);
            double interval = (double) population.size() / n;
            double start = localRandom.nextDouble() * interval;

            List<Employee> selected = new ArrayList<>();

            for (int i = 0; i < n; i++) {
                int index = Math.min(
                    population.size() - 1,
                    (int) Math.floor(start + i * interval)
                );

                selected.add(population.get(index));
            }

            return new Sample(
                SamplingMethod.SYSTEMATIC,
                selected,
                population.size(),
                seed
            );
        }

        List<Employee> population() {
            return population;
        }

        List<StratumStatistics> stratumReport(Sample sample) {
            Map<String, List<Employee>> populationGroups =
                population.stream().collect(
                    Collectors.groupingBy(Employee::department)
                );

            Map<String, List<Employee>> sampleGroups =
                sample.employees().stream().collect(
                    Collectors.groupingBy(Employee::department)
                );

            return populationGroups.entrySet()
                .stream()
                .sorted(Map.Entry.comparingByKey())
                .map(entry -> {
                    String name = entry.getKey();

                    List<Employee> full = entry.getValue();
                    List<Employee> selected =
                        sampleGroups.getOrDefault(name, List.of());

                    double average = selected.isEmpty()
                        ? Double.NaN
                        : selected.stream()
                            .mapToDouble(Employee::outcome)
                            .average()
                            .orElseThrow();

                    return new StratumStatistics(
                        name,
                        full.size(),
                        selected.size(),
                        (double) full.size() / population.size(),
                        (double) selected.size() / sample.employees().size(),
                        average
                    );
                })
                .toList();
        }
    }

    static final class StatisticalService {

        static StatisticalEstimate analyze(
            List<Employee> sample,
            int populationSize,
            double z
        ) {
            if (sample.size() < 2) {
                throw new SamplingException(
                    "At least two observations are required."
                );
            }

            if (populationSize < sample.size()) {
                throw new SamplingException(
                    "Invalid population size."
                );
            }

            double average = sample.stream()
                .mapToDouble(Employee::outcome)
                .average()
                .orElseThrow();

            double sumSquares = sample.stream()
                .mapToDouble(e -> Math.pow(
                    e.outcome() - average, 2
                ))
                .sum();

            double variance = sumSquares / (sample.size() - 1);

            double fpc = Math.sqrt(
                (double) (populationSize - sample.size()) /
                (populationSize - 1)
            );

            double standardError =
                Math.sqrt(variance / sample.size()) * fpc;

            double margin = z * standardError;

            return new StatisticalEstimate(
                average,
                variance,
                standardError,
                average - margin,
                average + margin
            );
        }

        static double weightedStratifiedMean(
            List<StratumStatistics> statistics
        ) {
            double total = 0;

            for (StratumStatistics item : statistics) {
                if (item.sampleCount() == 0) {
                    throw new SamplingException(
                        "Cannot estimate an unrepresented stratum."
                    );
                }

                total += item.populationWeight() * item.sampleMean();
            }

            return total;
        }
    }

    record BranchPolicy(
        String protectedBranch,
        int requiredApprovals,
        Set<String> requiredChecks,
        boolean requireResolvedConversations,
        boolean requireLinearHistory,
        boolean restrictDirectPush,
        boolean restrictForcePush
    ) {
        BranchPolicy {
            requiredChecks = Set.copyOf(requiredChecks);

            if (requiredApprovals < 0) {
                throw new IllegalArgumentException(
                    "Approval requirement cannot be negative."
                );
            }
        }
    }

    record PullRequest(
        int id,
        String sourceBranch,
        String targetBranch,
        boolean open,
        boolean draft,
        boolean conflicts,
        boolean synchronizedWithBase,
        Set<String> approvals,
        Set<String> requestedChanges,
        Map<String, Boolean> checks,
        int unresolvedConversations,
        boolean linearHistory
    ) {
        PullRequest {
            approvals = Set.copyOf(approvals);
            requestedChanges = Set.copyOf(requestedChanges);
            checks = Map.copyOf(checks);
        }
    }

    record MergeDecision(
        boolean eligible,
        List<String> reasons
    ) {
        MergeDecision {
            reasons = List.copyOf(reasons);
        }
    }

    interface MergePolicy {
        MergeDecision evaluate(
            PullRequest request,
            BranchPolicy policy
        );
    }

    static final class EnterpriseMergePolicy implements MergePolicy {

        @Override
        public MergeDecision evaluate(
            PullRequest request,
            BranchPolicy policy
        ) {
            List<String> reasons = new ArrayList<>();

            if (!request.open()) {
                reasons.add("Pull Request is not open.");
            }

            if (request.draft()) {
                reasons.add("Draft status blocks merging.");
            }

            if (request.id() <= 0 ||
                request.sourceBranch().isBlank() ||
                !request.targetBranch().equals(policy.protectedBranch())) {
                reasons.add("Invalid Pull Request branch configuration.");
            }

            if (request.sourceBranch().equals(request.targetBranch())) {
                reasons.add("Source and target branches must differ.");
            }

            if (request.conflicts()) {
                reasons.add("Merge conflicts exist.");
            }

            if (!request.synchronizedWithBase()) {
                reasons.add("Base branch synchronization is required.");
            }

            if (request.approvals().size() < policy.requiredApprovals()) {
                reasons.add("Required approvals are insufficient.");
            }

            if (!request.requestedChanges().isEmpty()) {
                reasons.add("Requested changes remain outstanding.");
            }

            for (String check : policy.requiredChecks()) {
                if (!Boolean.TRUE.equals(request.checks().get(check))) {
                    reasons.add("Required check failed or missing: " + check);
                }
            }

            if (policy.requireResolvedConversations() &&
                request.unresolvedConversations() > 0) {
                reasons.add("Unresolved conversations remain.");
            }

            if (policy.requireLinearHistory() &&
                !request.linearHistory()) {
                reasons.add("Linear history is required.");
            }

            return new MergeDecision(
                reasons.isEmpty(),
                reasons
            );
        }
    }

    static List<Employee> createPopulation(int size) {
        Random random = new Random(2026);

        String[] departments = {
            "Engineering",
            "Finance",
            "Operations",
            "Research"
        };

        double[] weights = {0.40, 0.20, 0.25, 0.15};

        List<Employee> population = new ArrayList<>();

        for (int i = 1; i <= size; i++) {
            double value = random.nextDouble();
            double cumulative = 0;
            String department = departments[departments.length - 1];

            for (int j = 0; j < departments.length; j++) {
                cumulative += weights[j];

                if (value < cumulative) {
                    department = departments[j];
                    break;
                }
            }

            int age = 21 + random.nextInt(45);

            double outcome = 35
                + random.nextDouble() * 20
                + age * 0.3
                + random.nextGaussian() * 8;

            double income = 25000 + random.nextDouble() * 155000;

            population.add(
                new Employee(
                    i,
                    department,
                    age,
                    income,
                    outcome
                )
            );
        }

        return List.copyOf(population);
    }

    public static void main(String[] args) {
        try {
            List<Employee> population = createPopulation(1000);

            SamplingService service = new SamplingService(
                population,
                17
            );

            int required = SampleSizeCalculator.proportion(
                1.96,
                0.05,
                0.5,
                population.size()
            );

            int recruitment = SampleSizeCalculator.recruitmentTarget(
                required,
                0.85
            );

            System.out.println("SAMPLING THEORY ENTERPRISE ENGINE");
            System.out.println("Population: " + population.size());
            System.out.println("Required sample: " + required);
            System.out.println("Recruitment target: " + recruitment);

            List<Sample> samples = List.of(
                service.simpleRandom(100, 17),
                service.stratified(100, 17),
                service.systematic(100, 17)
            );

            for (Sample sample : samples) {
                StatisticalEstimate estimate =
                    StatisticalService.analyze(
                        sample.employees(),
                        sample.populationSize(),
                        1.96
                    );

                System.out.println("\nMethod: " + sample.method());
                System.out.println("Sample size: " + sample.employees().size());
                System.out.printf(
                    Locale.ROOT,
                    "Mean: %.3f%nSE: %.3f%n95%% CI: [%.3f, %.3f]%n",
                    estimate.mean(),
                    estimate.standardError(),
                    estimate.lowerBound(),
                    estimate.upperBound()
                );

                List<StratumStatistics> report =
                    service.stratumReport(sample);

                report.forEach(System.out::println);

                if (sample.method() == SamplingMethod.STRATIFIED) {
                    System.out.printf(
                        Locale.ROOT,
                        "Weighted estimate: %.3f%n",
                        StatisticalService.weightedStratifiedMean(report)
                    );
                }
            }

            BranchPolicy policy = new BranchPolicy(
                "main",
                2,
                Set.of("build", "unit-tests", "security-scan"),
                true,
                false,
                true,
                true
            );

            PullRequest request = new PullRequest(
                501,
                "feature/sampling-analysis",
                "main",
                true,
                false,
                false,
                true,
                Set.of("reviewer-a", "reviewer-b"),
                Set.of(),
                Map.of(
                    "build", true,
                    "unit-tests", true,
                    "security-scan", true
                ),
                0,
                true
            );

            MergePolicy mergePolicy = new EnterpriseMergePolicy();

            MergeDecision decision = mergePolicy.evaluate(
                request,
                policy
            );

            System.out.println("\nEnterprise governance:");
            System.out.println(
                "Merge eligible: " + decision.eligible()
            );

            decision.reasons().forEach(System.out::println);

        } catch (RuntimeException exception) {
            System.err.println(
                "Execution failed: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
