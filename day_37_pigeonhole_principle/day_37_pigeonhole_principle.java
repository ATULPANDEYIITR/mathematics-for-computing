import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;

/**
 * Enterprise-oriented Pigeonhole Principle model.
 *
 * The scenario is an artifact distribution service. Build artifacts are
 * assigned to a finite set of storage partitions. The service uses domain
 * policies to calculate deterministic occupancy guarantees before considering
 * the actual distribution.
 *
 * Java-specific mechanisms demonstrated here include:
 * records for immutable domain values, enums for controlled states,
 * interfaces for policies, collections for occupancy tracking, validation,
 * Optional for duplicate-search results, and explicit service boundaries.
 */
public class PigeonholePrincipleEnterprise {

    enum PartitionState {
        AVAILABLE,
        DRAINING,
        OFFLINE
    }

    record Artifact(
        String id,
        String repository,
        long sizeBytes
    ) {
        Artifact {
            Objects.requireNonNull(id, "id");
            Objects.requireNonNull(repository, "repository");

            if (id.isBlank()) {
                throw new IllegalArgumentException(
                    "artifact id cannot be blank"
                );
            }

            if (repository.isBlank()) {
                throw new IllegalArgumentException(
                    "repository cannot be blank"
                );
            }

            if (sizeBytes < 0) {
                throw new IllegalArgumentException(
                    "artifact size cannot be negative"
                );
            }
        }
    }

    record Partition(
        int id,
        PartitionState state
    ) {
        Partition {
            if (id < 0) {
                throw new IllegalArgumentException(
                    "partition id cannot be negative"
                );
            }

            Objects.requireNonNull(
                state,
                "partition state"
            );
        }
    }

    record DistributionResult(
        Map<Integer, List<Artifact>> assignments
    ) {
        DistributionResult {
            assignments = deepCopy(assignments);
        }

        private static Map<Integer, List<Artifact>> deepCopy(
            Map<Integer, List<Artifact>> source
        ) {
            Map<Integer, List<Artifact>> copy =
                new HashMap<>();

            source.forEach(
                (partition, artifacts) ->
                    copy.put(
                        partition,
                        List.copyOf(artifacts)
                    )
            );

            return Collections.unmodifiableMap(copy);
        }
    }

    interface OccupancyPolicy {
        int guaranteedMaximumOccupancy(
            int objectCount,
            int containerCount
        );

        int objectsRequiredForTarget(
            int containerCount,
            int targetOccupancy
        );
    }

    static final class GeneralizedPigeonholePolicy
        implements OccupancyPolicy {

        @Override
        public int guaranteedMaximumOccupancy(
            int objectCount,
            int containerCount
        ) {
            validateCounts(
                objectCount,
                containerCount
            );

            if (objectCount == 0) {
                return 0;
            }

            return (objectCount + containerCount - 1)
                / containerCount;
        }

        @Override
        public int objectsRequiredForTarget(
            int containerCount,
            int targetOccupancy
        ) {
            if (containerCount <= 0) {
                throw new IllegalArgumentException(
                    "containerCount must be positive"
                );
            }

            if (targetOccupancy <= 0) {
                throw new IllegalArgumentException(
                    "targetOccupancy must be positive"
                );
            }

            return containerCount *
                (targetOccupancy - 1) + 1;
        }

        private void validateCounts(
            int objectCount,
            int containerCount
        ) {
            if (objectCount < 0) {
                throw new IllegalArgumentException(
                    "objectCount cannot be negative"
                );
            }

            if (containerCount <= 0) {
                throw new IllegalArgumentException(
                    "containerCount must be positive"
                );
            }
        }
    }

    static final class ArtifactDistributionService {

        private final OccupancyPolicy occupancyPolicy;
        private final List<Partition> partitions;

        ArtifactDistributionService(
            OccupancyPolicy occupancyPolicy,
            List<Partition> partitions
        ) {
            this.occupancyPolicy =
                Objects.requireNonNull(
                    occupancyPolicy,
                    "occupancyPolicy"
                );

            this.partitions =
                validatePartitions(partitions);
        }

        private List<Partition> validatePartitions(
            List<Partition> source
        ) {
            Objects.requireNonNull(
                source,
                "partitions"
            );

            if (source.isEmpty()) {
                throw new IllegalArgumentException(
                    "at least one partition is required"
                );
            }

            Set<Integer> ids = new HashSet<>();

            for (Partition partition : source) {
                if (!ids.add(partition.id())) {
                    throw new IllegalArgumentException(
                        "duplicate partition id: "
                            + partition.id()
                    );
                }
            }

            return List.copyOf(source);
        }

        DistributionResult distribute(
            List<Artifact> artifacts
        ) {
            Objects.requireNonNull(
                artifacts,
                "artifacts"
            );

            Map<Integer, List<Artifact>> assignments =
                new HashMap<>();

            for (Partition partition : partitions) {
                assignments.put(
                    partition.id(),
                    new ArrayList<>()
                );
            }

            List<Partition> active =
                partitions.stream()
                    .filter(
                        partition ->
                            partition.state()
                                == PartitionState.AVAILABLE
                    )
                    .toList();

            if (active.isEmpty() && !artifacts.isEmpty()) {
                throw new IllegalStateException(
                    "no available partition exists"
                );
            }

            for (int index = 0; index < artifacts.size(); index++) {
                Partition target =
                    active.get(index % active.size());

                assignments
                    .get(target.id())
                    .add(artifacts.get(index));
            }

            return new DistributionResult(assignments);
        }

        int guaranteedOccupancy(int artifactCount) {
            long activeCount =
                partitions.stream()
                    .filter(
                        partition ->
                            partition.state()
                                == PartitionState.AVAILABLE
                    )
                    .count();

            if (activeCount == 0) {
                throw new IllegalStateException(
                    "cannot calculate occupancy with no active partitions"
                );
            }

            return occupancyPolicy.guaranteedMaximumOccupancy(
                artifactCount,
                Math.toIntExact(activeCount)
            );
        }
    }

    record Duplicate<T>(
        T value,
        int firstPosition,
        int secondPosition
    ) {}

    static <T> Optional<Duplicate<T>> findDuplicate(
        List<T> values
    ) {
        Objects.requireNonNull(
            values,
            "values"
        );

        Map<T, Integer> positions = new HashMap<>();

        for (int index = 0; index < values.size(); index++) {
            T value = values.get(index);

            Integer firstPosition =
                positions.putIfAbsent(
                    value,
                    index
                );

            if (firstPosition != null) {
                return Optional.of(
                    new Duplicate<>(
                        value,
                        firstPosition,
                        index
                    )
                );
            }
        }

        return Optional.empty();
    }

    static Map<Integer, Integer> modularGroups(
        int count,
        int modulus
    ) {
        if (count < 0 || modulus <= 0) {
            throw new IllegalArgumentException(
                "invalid modular grouping parameters"
            );
        }

        Map<Integer, Integer> groups =
            new HashMap<>();

        for (int value = 0; value < count; value++) {
            int residue = value % modulus;

            groups.merge(
                residue,
                1,
                Integer::sum
            );
        }

        return groups;
    }

    static int requiredBits(int states) {
        if (states <= 0) {
            throw new IllegalArgumentException(
                "states must be positive"
            );
        }

        int bits = 0;
        int capacity = 1;

        while (capacity < states) {
            capacity *= 2;
            bits++;
        }

        return bits;
    }

    static void printAssignments(
        DistributionResult result
    ) {
        result.assignments()
            .entrySet()
            .stream()
            .sorted(Map.Entry.comparingByKey())
            .forEach(
                entry ->
                    System.out.println(
                        "Partition "
                            + entry.getKey()
                            + ": "
                            + entry.getValue().size()
                            + " artifact(s)"
                    )
            );
    }

    static void demonstrateBasicPrinciple() {
        System.out.println(
            "\n=== Basic Pigeonhole Principle ==="
        );

        int teams = 13;
        int weekdays = 7;

        GeneralizedPigeonholePolicy policy =
            new GeneralizedPigeonholePolicy();

        System.out.println(
            teams
                + " teams assigned to "
                + weekdays
                + " weekdays guarantees at least "
                + policy.guaranteedMaximumOccupancy(
                    teams,
                    weekdays
                )
                + " teams on one day."
        );
    }

    static void demonstrateEnterpriseDistribution() {
        System.out.println(
            "\n=== Enterprise Artifact Distribution ==="
        );

        List<Partition> partitions =
            List.of(
                new Partition(
                    0,
                    PartitionState.AVAILABLE
                ),
                new Partition(
                    1,
                    PartitionState.AVAILABLE
                ),
                new Partition(
                    2,
                    PartitionState.DRAINING
                ),
                new Partition(
                    3,
                    PartitionState.AVAILABLE
                )
            );

        List<Artifact> artifacts =
            List.of(
                new Artifact(
                    "build-001",
                    "payments",
                    12_000
                ),
                new Artifact(
                    "build-002",
                    "payments",
                    15_000
                ),
                new Artifact(
                    "build-003",
                    "identity",
                    11_000
                ),
                new Artifact(
                    "build-004",
                    "analytics",
                    19_000
                ),
                new Artifact(
                    "build-005",
                    "analytics",
                    22_000
                ),
                new Artifact(
                    "build-006",
                    "identity",
                    10_000
                ),
                new Artifact(
                    "build-007",
                    "payments",
                    14_000
                )
            );

        ArtifactDistributionService service =
            new ArtifactDistributionService(
                new GeneralizedPigeonholePolicy(),
                partitions
            );

        DistributionResult result =
            service.distribute(artifacts);

        printAssignments(result);

        System.out.println(
            "Guaranteed maximum occupancy among active "
                + "partitions: "
                + service.guaranteedOccupancy(
                    artifacts.size()
                )
        );
    }

    static void demonstrateTargetThreshold() {
        System.out.println(
            "\n=== Target Occupancy Threshold ==="
        );

        GeneralizedPigeonholePolicy policy =
            new GeneralizedPigeonholePolicy();

        int partitions = 16;
        int target = 20;

        System.out.println(
            "Objects required to force at least "
                + target
                + " objects into one of "
                + partitions
                + " partitions: "
                + policy.objectsRequiredForTarget(
                    partitions,
                    target
                )
        );
    }

    static void demonstrateDuplicateDetection() {
        System.out.println(
            "\n=== Duplicate Detection ==="
        );

        List<String> identifiers =
            List.of(
                "TX-100",
                "TX-101",
                "TX-102",
                "TX-103",
                "TX-101",
                "TX-104"
            );

        Optional<Duplicate<String>> duplicate =
            findDuplicate(identifiers);

        duplicate.ifPresent(
            value ->
                System.out.println(
                    "Duplicate "
                        + value.value()
                        + " found at positions "
                        + value.firstPosition()
                        + " and "
                        + value.secondPosition()
                )
        );
    }

    static void demonstrateModularClassification() {
        System.out.println(
            "\n=== Modular Classification ==="
        );

        Map<Integer, Integer> groups =
            modularGroups(
                50,
                7
            );

        groups.entrySet()
            .stream()
            .sorted(Map.Entry.comparingByKey())
            .forEach(
                entry ->
                    System.out.println(
                        "Residue "
                            + entry.getKey()
                            + ": "
                            + entry.getValue()
                            + " value(s)"
                    )
            );

        GeneralizedPigeonholePolicy policy =
            new GeneralizedPigeonholePolicy();

        System.out.println(
            "Guaranteed repeated-residue count: "
                + policy.guaranteedMaximumOccupancy(
                    50,
                    7
                )
        );
    }

    static void demonstrateBitRepresentation() {
        System.out.println(
            "\n=== Bit Representation ==="
        );

        int availablePatterns = 1 << 8;
        int logicalStates = availablePatterns + 1;

        System.out.println(
            "8-bit patterns: "
                + availablePatterns
        );

        System.out.println(
            "Logical states: "
                + logicalStates
        );

        System.out.println(
            "Bits required for "
                + logicalStates
                + " states: "
                + requiredBits(logicalStates)
        );
    }

    static void demonstratePolicyStates() {
        System.out.println(
            "\n=== Controlled Partition States ==="
        );

        EnumSet<PartitionState> operationalStates =
            EnumSet.of(
                PartitionState.AVAILABLE,
                PartitionState.DRAINING
            );

        System.out.println(
            "Operational states: "
                + operationalStates
        );

        System.out.println(
            "Offline is excluded from new assignments: "
                + !operationalStates.contains(
                    PartitionState.OFFLINE
                )
        );
    }

    static void demonstrateFailureState() {
        System.out.println(
            "\n=== Failure Handling ==="
        );

        try {
            new GeneralizedPigeonholePolicy()
                .guaranteedMaximumOccupancy(
                    100,
                    0
                );
        } catch (IllegalArgumentException error) {
            System.out.println(
                "Invalid container count rejected: "
                    + error.getMessage()
            );
        }

        try {
            new ArtifactDistributionService(
                new GeneralizedPigeonholePolicy(),
                List.of(
                    new Partition(
                        1,
                        PartitionState.OFFLINE
                    )
                )
            ).distribute(
                List.of(
                    new Artifact(
                        "build-failure",
                        "payments",
                        1_000
                    )
                )
            );
        } catch (IllegalStateException error) {
            System.out.println(
                "Unavailable storage rejected: "
                    + error.getMessage()
            );
        }
    }

    static void demonstrateComplexity() {
        System.out.println(
            "\n=== Complexity ==="
        );

        System.out.println(
            "Generalized bound calculation: O(1) time."
        );

        System.out.println(
            "Distribution of n artifacts: O(n) assignment operations."
        );

        System.out.println(
            "Duplicate detection with HashMap: expected O(n) time "
                + "and O(n) additional space."
        );

        System.out.println(
            "The deterministic bound requires no enumeration of "
                + "possible assignments."
        );
    }

    public static void main(String[] args) {
        demonstrateBasicPrinciple();
        demonstrateEnterpriseDistribution();
        demonstrateTargetThreshold();
        demonstrateDuplicateDetection();
        demonstrateModularClassification();
        demonstrateBitRepresentation();
        demonstratePolicyStates();
        demonstrateFailureState();
        demonstrateComplexity();
    }
}
