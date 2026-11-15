import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Random;
import java.util.Set;
import java.util.HashSet;
import java.util.stream.Collectors;

/**
 * Statistics Fundamentals
 *
 * Enterprise-oriented population and sampling management.
 *
 * Java 17 features:
 * - Records and immutable domain models
 * - Interfaces and policy-based sampling
 * - Generic statistical operations
 * - Population and sample validation
 * - Simple random sampling
 * - Systematic sampling
 * - Stratified sampling
 * - Statistical inference
 * - Finite population correction
 * - Confidence intervals
 * - Sample-size calculation
 * - Workflow state transitions
 * - Audit reporting
 *
 * No third-party dependencies.
 */
public class StatisticsFundamentals {

    // ========================================================
    // 1. ENUMERATIONS
    // ========================================================

    enum SamplingMethod {
        SIMPLE_RANDOM,
        SYSTEMATIC,
        STRATIFIED
    }

    enum WorkflowState {
        CREATED,
        VALIDATED,
        SAMPLED,
        ANALYZED,
        FAILED
    }

    // ========================================================
    // 2. CUSTOM EXCEPTIONS
    // ========================================================

    static class StatisticalException extends RuntimeException {
        public StatisticalException(String message) {
            super(message);
        }
    }

    static class ValidationException extends StatisticalException {
        public ValidationException(String message) {
            super(message);
        }
    }

    static class SamplingException extends StatisticalException {
        public SamplingException(String message) {
            super(message);
        }
    }

    // ========================================================
    // 3. IMMUTABLE DOMAIN RECORDS
    // ========================================================

    record Observation(
        String id,
        double value,
        String stratum,
        String cluster
    ) {
        Observation {
            if (id == null || id.isBlank()) {
                throw new ValidationException("Observation ID is required.");
            }

            if (!Double.isFinite(value)) {
                throw new ValidationException("Value must be finite.");
            }

            if (stratum == null || stratum.isBlank()) {
                throw new ValidationException("Stratum is required.");
            }

            if (cluster == null || cluster.isBlank()) {
                throw new ValidationException("Cluster is required.");
            }
        }
    }

    record PopulationParameters(
        int populationSize,
        double mean,
        double variance,
        double standardDeviation,
        double total
    ) {}

    record SampleStatistics(
        int count,
        double mean,
        double median,
        double variance,
        double standardDeviation,
        double minimum,
        double maximum
    ) {}

    record ConfidenceInterval(
        double lower,
        double upper,
        double standardError,
        double confidenceLevel
    ) {}

    record StatisticalSample(
        List<Observation> observations,
        int populationSize,
        SamplingMethod method,
        long seed
    ) {
        StatisticalSample {
            observations = List.copyOf(observations);

            if (observations.isEmpty()) {
                throw new ValidationException("Sample cannot be empty.");
            }

            if (observations.size() > populationSize) {
                throw new ValidationException(
                    "Sample exceeds population size."
                );
            }

            Set<String> ids = new HashSet<>();

            for (Observation observation : observations) {
                if (!ids.add(observation.id())) {
                    throw new ValidationException(
                        "Duplicate sample observation."
                    );
                }
            }
        }
    }

    // ========================================================
    // 4. POPULATION REPOSITORY
    // ========================================================

    static final class PopulationRepository {

        private final List<Observation> observations;
        private final Map<String, Observation> index;

        PopulationRepository(List<Observation> observations) {
            if (observations == null || observations.isEmpty()) {
                throw new ValidationException(
                    "Population cannot be empty."
                );
            }

            Map<String, Observation> temporary = new LinkedHashMap<>();

            for (Observation observation : observations) {
                Objects.requireNonNull(observation);

                if (temporary.putIfAbsent(
                    observation.id(),
                    observation
                ) != null) {
                    throw new ValidationException(
                        "Duplicate population identifier."
                    );
                }
            }

            this.index = Collections.unmodifiableMap(temporary);
            this.observations = List.copyOf(temporary.values());
        }

        int size() {
            return observations.size();
        }

        List<Observation> observations() {
            return observations;
        }

        List<Double> values() {
            return observations.stream()
                .map(Observation::value)
                .toList();
        }

        Map<String, List<Observation>> strata() {
            return observations.stream().collect(
                Collectors.groupingBy(
                    Observation::stratum,
                    LinkedHashMap::new,
                    Collectors.toList()
                )
            );
        }

        Observation find(String id) {
            Observation result = index.get(id);

            if (result == null) {
                throw new ValidationException(
                    "Unknown population identifier: " + id
                );
            }

            return result;
        }

        PopulationParameters parameters() {
            List<Double> values = values();

            return new PopulationParameters(
                size(),
                Statistics.mean(values),
                Statistics.variance(values, false),
                Statistics.standardDeviation(values, false),
                values.stream().mapToDouble(Double::doubleValue).sum()
            );
        }
    }

    // ========================================================
    // 5. GENERIC STATISTICAL SERVICE
    // ========================================================

    static final class Statistics {

        private Statistics() {}

        static void validate(List<Double> values) {
            if (values == null || values.isEmpty()) {
                throw new ValidationException(
                    "At least one observation is required."
                );
            }

            for (Double value : values) {
                if (value == null || !Double.isFinite(value)) {
                    throw new ValidationException(
                        "Invalid numerical observation."
                    );
                }
            }
        }

        static double mean(List<Double> values) {
            validate(values);

            double sum = 0;
            double compensation = 0;

            for (double value : values) {
                double adjusted = value - compensation;
                double next = sum + adjusted;

                compensation = (next - sum) - adjusted;
                sum = next;
            }

            return sum / values.size();
        }

        static double median(List<Double> values) {
            validate(values);

            List<Double> sorted = new ArrayList<>(values);
            sorted.sort(Double::compareTo);

            int middle = sorted.size() / 2;

            if (sorted.size() % 2 == 1) {
                return sorted.get(middle);
            }

            return (
                sorted.get(middle - 1) + sorted.get(middle)
            ) / 2.0;
        }

        static double variance(
            List<Double> values,
            boolean sample
        ) {
            validate(values);

            if (sample && values.size() < 2) {
                throw new ValidationException(
                    "Sample variance requires two observations."
                );
            }

            double mean = mean(values);

            double sum = values.stream()
                .mapToDouble(value -> Math.pow(value - mean, 2))
                .sum();

            return sum / (
                sample ? values.size() - 1 : values.size()
            );
        }

        static double standardDeviation(
            List<Double> values,
            boolean sample
        ) {
            return Math.sqrt(variance(values, sample));
        }

        static double quantile(
            List<Double> values,
            double probability
        ) {
            validate(values);

            if (probability < 0 || probability > 1) {
                throw new ValidationException(
                    "Invalid quantile probability."
                );
            }

            List<Double> sorted = new ArrayList<>(values);
            sorted.sort(Double::compareTo);

            double position = probability * (sorted.size() - 1);

            int lower = (int) Math.floor(position);
            int upper = (int) Math.ceil(position);

            return sorted.get(lower)
                + (position - lower)
                * (sorted.get(upper) - sorted.get(lower));
        }

        static SampleStatistics describe(List<Double> values) {
            validate(values);

            return new SampleStatistics(
                values.size(),
                mean(values),
                median(values),
                variance(values, values.size() > 1),
                standardDeviation(values, values.size() > 1),
                Collections.min(values),
                Collections.max(values)
            );
        }
    }

    // ========================================================
    // 6. SAMPLING POLICY INTERFACE
    // ========================================================

    interface SamplingPolicy {
        StatisticalSample select(
            PopulationRepository population,
            int sampleSize,
            long seed
        );
    }

    // ========================================================
    // 7. SIMPLE RANDOM SAMPLING POLICY
    // ========================================================

    static final class SimpleRandomPolicy implements SamplingPolicy {

        @Override
        public StatisticalSample select(
            PopulationRepository population,
            int sampleSize,
            long seed
        ) {
            validateSampleSize(sampleSize, population.size());

            List<Observation> shuffled = new ArrayList<>(
                population.observations()
            );

            Collections.shuffle(shuffled, new Random(seed));

            return new StatisticalSample(
                shuffled.subList(0, sampleSize),
                population.size(),
                SamplingMethod.SIMPLE_RANDOM,
                seed
            );
        }
    }

    // ========================================================
    // 8. SYSTEMATIC SAMPLING POLICY
    // ========================================================

    static final class SystematicPolicy implements SamplingPolicy {

        @Override
        public StatisticalSample select(
            PopulationRepository population,
            int sampleSize,
            long seed
        ) {
            validateSampleSize(sampleSize, population.size());

            List<Observation> units = population.observations();

            if (sampleSize == units.size()) {
                return new StatisticalSample(
                    units,
                    population.size(),
                    SamplingMethod.SYSTEMATIC,
                    seed
                );
            }

            double interval = (double) units.size() / sampleSize;

            Random random = new Random(seed);

            double start = random.nextDouble() * interval;

            List<Observation> selected = new ArrayList<>();

            for (int i = 0; i < sampleSize; i++) {
                int index = Math.min(
                    (int) Math.floor(start + i * interval),
                    units.size() - 1
                );

                selected.add(units.get(index));
            }

            return new StatisticalSample(
                selected,
                population.size(),
                SamplingMethod.SYSTEMATIC,
                seed
            );
        }
    }

    // ========================================================
    // 9. STRATIFIED SAMPLING POLICY
    // ========================================================

    static final class StratifiedPolicy implements SamplingPolicy {

        @Override
        public StatisticalSample select(
            PopulationRepository population,
            int sampleSize,
            long seed
        ) {
            validateSampleSize(sampleSize, population.size());

            Map<String, List<Observation>> strata =
                population.strata();

            if (sampleSize < strata.size()) {
                throw new SamplingException(
                    "Sample must represent every stratum."
                );
            }

            record Allocation(
                String name,
                List<Observation> observations,
                int count,
                double remainder
            ) {}

            List<Allocation> allocations = new ArrayList<>();

            for (var entry : strata.entrySet()) {
                double exact = (double) sampleSize
                    * entry.getValue().size()
                    / population.size();

                allocations.add(new Allocation(
                    entry.getKey(),
                    entry.getValue(),
                    (int) Math.floor(exact),
                    exact - Math.floor(exact)
                ));
            }

            int allocated = allocations.stream()
                .mapToInt(Allocation::count)
                .sum();

            allocations.sort(
                Comparator.comparingDouble(
                    Allocation::remainder
                ).reversed()
            );

            int remaining = sampleSize - allocated;

            List<Observation> selected = new ArrayList<>();

            for (Allocation allocation : allocations) {
                int count = allocation.count();

                if (remaining > 0 &&
                    count < allocation.observations().size()) {
                    count++;
                    remaining--;
                }

                List<Observation> group = new ArrayList<>(
                    allocation.observations()
                );

                Collections.shuffle(
                    group,
                    new Random(seed + allocation.name().hashCode())
                );

                selected.addAll(group.subList(0, count));
            }

            if (remaining != 0 || selected.size() != sampleSize) {
                throw new SamplingException(
                    "Unable to complete stratified allocation."
                );
            }

            return new StatisticalSample(
                selected,
                population.size(),
                SamplingMethod.STRATIFIED,
                seed
            );
        }
    }

    // ========================================================
    // 10. INFERENCE SERVICE
    // ========================================================

    static final class InferenceService {

        static double standardError(
            StatisticalSample sample,
            boolean finiteCorrection
        ) {
            List<Double> values = sample.observations()
                .stream()
                .map(Observation::value)
                .toList();

            int n = values.size();
            int N = sample.populationSize();

            if (n < 2) {
                throw new ValidationException(
                    "At least two observations are required."
                );
            }

            double se = Statistics.standardDeviation(values, true)
                / Math.sqrt(n);

            if (finiteCorrection && n < N) {
                se *= Math.sqrt(
                    (double) (N - n) / (N - 1)
                );
            }

            return se;
        }

        static ConfidenceInterval confidenceInterval(
            StatisticalSample sample,
            double confidence
        ) {
            double z = switch (confidence) {
                case 0.90 -> 1.645;
                case 0.95 -> 1.960;
                case 0.99 -> 2.576;
                default -> throw new ValidationException(
                    "Unsupported confidence level."
                );
            };

            List<Double> values = sample.observations()
                .stream()
                .map(Observation::value)
                .toList();

            double mean = Statistics.mean(values);
            double se = standardError(sample, true);
            double margin = z * se;

            return new ConfidenceInterval(
                mean - margin,
                mean + margin,
                se,
                confidence
            );
        }

        static int requiredSampleSize(
            double populationStd,
            double margin,
            double z,
            int populationSize
        ) {
            if (!Double.isFinite(populationStd) ||
                !Double.isFinite(margin) ||
                !Double.isFinite(z) ||
                populationStd < 0 ||
                margin <= 0 ||
                z <= 0 ||
                populationSize <= 0) {
                throw new ValidationException(
                    "Invalid sample-size parameters."
                );
            }

            if (populationStd == 0) return 1;

            double n0 = Math.pow(
                z * populationStd / margin,
                2
            );

            if (n0 >= populationSize) {
                return populationSize;
            }

            double adjusted = n0 /
                (1 + (n0 - 1) / populationSize);

            return Math.min(
                populationSize,
                (int) Math.ceil(adjusted)
            );
        }
    }

    // ========================================================
    // 11. WORKFLOW AND AUDIT MANAGEMENT
    // ========================================================

    static final class SamplingWorkflow {

        private WorkflowState state = WorkflowState.CREATED;

        private final List<String> auditLog = new ArrayList<>();

        void transition(WorkflowState next) {
            boolean allowed = switch (state) {
                case CREATED -> next == WorkflowState.VALIDATED
                    || next == WorkflowState.FAILED;

                case VALIDATED -> next == WorkflowState.SAMPLED
                    || next == WorkflowState.FAILED;

                case SAMPLED -> next == WorkflowState.ANALYZED
                    || next == WorkflowState.FAILED;

                case ANALYZED, FAILED -> false;
            };

            if (!allowed) {
                throw new StatisticalException(
                    "Invalid workflow transition: "
                    + state + " -> " + next
                );
            }

            state = next;

            auditLog.add(
                java.time.Instant.now()
                    + " | " + state
            );
        }

        WorkflowState state() {
            return state;
        }

        List<String> auditLog() {
            return List.copyOf(auditLog);
        }
    }

    static void validateSampleSize(int n, int N) {
        if (n < 1 || n > N) {
            throw new SamplingException(
                "Sample size must be between 1 and N."
            );
        }
    }

    // ========================================================
    // 12. REALISTIC ENTERPRISE APPLICATION
    // ========================================================

    static PopulationRepository buildPopulation() {
        List<Observation> observations = new ArrayList<>();

        String[] departments = {
            "Technology",
            "Mathematics",
            "Physics"
        };

        for (int group = 0; group < departments.length; group++) {
            for (int i = 1; i <= 30; i++) {
                double score = 50
                    + group * 10
                    + i * 0.8
                    + (i % 5) * 2;

                observations.add(new Observation(
                    "STU-" + (group + 1) + "-"
                        + String.format("%03d", i),
                    score,
                    departments[group],
                    "CLASS-" + ((i - 1) / 10 + 1)
                ));
            }
        }

        return new PopulationRepository(observations);
    }

    static void runTests() {
        List<Double> values = List.of(10.0, 20.0, 30.0);

        if (Statistics.mean(values) != 20.0) {
            throw new StatisticalException("Mean test failed.");
        }

        if (Statistics.median(values) != 20.0) {
            throw new StatisticalException("Median test failed.");
        }

        try {
            validateSampleSize(10, 5);
            throw new StatisticalException(
                "Invalid sample size was accepted."
            );
        } catch (SamplingException expected) {
            // Expected validation behavior.
        }
    }

    public static void main(String[] args) {
        try {
            runTests();

            PopulationRepository population = buildPopulation();

            System.out.println("STATISTICS FUNDAMENTALS");
            System.out.println("=======================");

            System.out.println("\nPOPULATION PARAMETERS");
            System.out.println(population.parameters());

            SamplingWorkflow workflow = new SamplingWorkflow();

            workflow.transition(WorkflowState.VALIDATED);

            Map<String, SamplingPolicy> policies = Map.of(
                "Simple Random", new SimpleRandomPolicy(),
                "Systematic", new SystematicPolicy(),
                "Stratified", new StratifiedPolicy()
            );

            for (var entry : policies.entrySet()) {
                StatisticalSample sample = entry.getValue().select(
                    population,
                    20,
                    42
                );

                workflow.transition(WorkflowState.SAMPLED);

                List<Double> values = sample.observations()
                    .stream()
                    .map(Observation::value)
                    .toList();

                System.out.println(
                    "\n" + entry.getKey() + " Sampling"
                );

                System.out.println(
                    Statistics.describe(values)
                );

                System.out.println(
                    InferenceService.confidenceInterval(
                        sample,
                        0.95
                    )
                );

                if (workflow.state() == WorkflowState.SAMPLED) {
                    // Each sampling policy is analyzed independently.
                    workflow.transition(WorkflowState.ANALYZED);
                    System.out.println("Analysis completed.");
                    break;
                }
            }

            System.out.println("\nREQUIRED SAMPLE SIZE");

            System.out.println(
                InferenceService.requiredSampleSize(
                    15,
                    3,
                    1.96,
                    population.size()
                )
            );

            System.out.println("\nWORKFLOW AUDIT");

            workflow.auditLog().forEach(System.out::println);

            System.out.println("\nAll tests passed.");

        } catch (StatisticalException error) {
            System.err.println(
                "Statistical processing failed: "
                + error.getMessage()
            );

            System.exit(1);
        }
    }
}
