import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.Deque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeSet;
import java.util.stream.Collectors;

/*
 * Enterprise case study: allocate compatible time slots to maintenance jobs.
 * Jobs sharing equipment, technicians, or an exclusive work area conflict.
 * A color represents a time slot; an edge prohibits equal slot assignments.
 */
public class GraphColoringEnterprise {

    enum JobState {
        PLANNED, VALIDATED, SCHEDULED, BLOCKED
    }

    record Job(String id, String description, Set<String> resources) {
        Job {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException("Job ID is required.");
            }
            if (description == null || description.isBlank()) {
                throw new IllegalArgumentException("Job description is required.");
            }
            resources = Set.copyOf(Objects.requireNonNull(resources));
            if (resources.stream().anyMatch(String::isBlank)) {
                throw new IllegalArgumentException("Resource names cannot be blank.");
            }
        }
    }

    record Conflict(String leftJob, String rightJob, Set<String> sharedResources) {
        Conflict {
            sharedResources = Set.copyOf(sharedResources);
        }
    }

    record Schedule(Map<String, Integer> slots, int slotCount, boolean valid) {
        Schedule {
            slots = Map.copyOf(slots);
        }
    }

    static final class MaintenanceGraph {
        private final Map<String, Job> jobs = new LinkedHashMap<>();
        private final Map<String, Set<String>> adjacency = new LinkedHashMap<>();
        private final List<Conflict> conflicts = new ArrayList<>();

        void addJob(Job job) {
            Objects.requireNonNull(job);
            if (jobs.putIfAbsent(job.id(), job) != null) {
                throw new IllegalArgumentException("Duplicate job ID: " + job.id());
            }
            adjacency.put(job.id(), new LinkedHashSet<>());
        }

        void buildConflicts() {
            conflicts.clear();
            for (Set<String> neighbors : adjacency.values()) {
                neighbors.clear();
            }

            List<Job> allJobs = new ArrayList<>(jobs.values());
            for (int i = 0; i < allJobs.size(); i++) {
                for (int j = i + 1; j < allJobs.size(); j++) {
                    Job left = allJobs.get(i);
                    Job right = allJobs.get(j);

                    Set<String> shared = new TreeSet<>(left.resources());
                    shared.retainAll(right.resources());

                    if (!shared.isEmpty()) {
                        adjacency.get(left.id()).add(right.id());
                        adjacency.get(right.id()).add(left.id());
                        conflicts.add(new Conflict(left.id(), right.id(), shared));
                    }
                }
            }
        }

        List<Conflict> conflicts() {
            return List.copyOf(conflicts);
        }

        Set<String> neighbors(String jobId) {
            if (!adjacency.containsKey(jobId)) {
                throw new IllegalArgumentException("Unknown job: " + jobId);
            }
            return Set.copyOf(adjacency.get(jobId));
        }

        boolean validate(Map<String, Integer> coloring) {
            if (!coloring.keySet().equals(jobs.keySet())) return false;
            if (coloring.values().stream().anyMatch(
                    color -> color == null || color < 0)) return false;

            for (Map.Entry<String, Set<String>> entry : adjacency.entrySet()) {
                for (String neighbor : entry.getValue()) {
                    if (Objects.equals(
                            coloring.get(entry.getKey()),
                            coloring.get(neighbor))) {
                        return false;
                    }
                }
            }
            return true;
        }

        boolean isBipartite() {
            Map<String, Integer> side = new HashMap<>();

            for (String start : jobs.keySet()) {
                if (side.containsKey(start)) continue;

                Deque<String> queue = new ArrayDeque<>();
                queue.addLast(start);
                side.put(start, 0);

                while (!queue.isEmpty()) {
                    String current = queue.removeFirst();
                    for (String neighbor : adjacency.get(current)) {
                        if (!side.containsKey(neighbor)) {
                            side.put(neighbor, 1 - side.get(current));
                            queue.addLast(neighbor);
                        } else if (side.get(neighbor).equals(side.get(current))) {
                            return false;
                        }
                    }
                }
            }
            return true;
        }

        Schedule dsaturSchedule() {
            Map<String, Integer> colors = new LinkedHashMap<>();

            while (colors.size() < jobs.size()) {
                String selected = null;
                int maximumSaturation = -1;
                int maximumDegree = -1;

                for (String jobId : jobs.keySet()) {
                    if (colors.containsKey(jobId)) continue;

                    Set<Integer> neighborColors = adjacency.get(jobId).stream()
                            .filter(colors::containsKey)
                            .map(colors::get)
                            .collect(Collectors.toSet());

                    int saturation = neighborColors.size();
                    int degree = adjacency.get(jobId).size();

                    if (saturation > maximumSaturation
                            || (saturation == maximumSaturation
                            && degree > maximumDegree)) {
                        selected = jobId;
                        maximumSaturation = saturation;
                        maximumDegree = degree;
                    }
                }

                Set<Integer> unavailable = adjacency.get(selected).stream()
                        .filter(colors::containsKey)
                        .map(colors::get)
                        .collect(Collectors.toSet());

                int slot = 0;
                while (unavailable.contains(slot)) slot++;
                colors.put(selected, slot);
            }

            if (!validate(colors)) {
                throw new IllegalStateException("Generated schedule violates conflicts.");
            }

            int count = colors.values().stream().max(Integer::compareTo)
                    .map(max -> max + 1).orElse(0);
            return new Schedule(colors, count, true);
        }
    }

    static final class SchedulingService {
        private final MaintenanceGraph graph;
        private final Map<String, JobState> states = new LinkedHashMap<>();

        SchedulingService(MaintenanceGraph graph) {
            this.graph = Objects.requireNonNull(graph);
        }

        void validateJobs() {
            if (graph.conflicts().isEmpty() && graph.neighborsOrEmpty().isEmpty()) {
                throw new IllegalStateException("The job model is empty.");
            }
            // A validation state records that the conflict model was reviewed.
            // It does not itself prove that a proposed slot assignment is valid.
            for (String jobId : graph.jobIds()) {
                states.put(jobId, JobState.VALIDATED);
            }
        }

        Schedule schedule() {
            if (states.values().stream().anyMatch(
                    state -> state != JobState.VALIDATED)) {
                throw new IllegalStateException("All jobs must be validated first.");
            }

            Schedule schedule = graph.dsaturSchedule();
            if (!schedule.valid() || !graph.validate(schedule.slots())) {
                states.replaceAll((id, state) -> JobState.BLOCKED);
                throw new IllegalStateException("Scheduling validation failed.");
            }

            states.replaceAll((id, state) -> JobState.SCHEDULED);
            return schedule;
        }

        Map<String, JobState> states() {
            return Map.copyOf(states);
        }
    }

    private static MaintenanceGraph createExample() {
        MaintenanceGraph graph = new MaintenanceGraph();

        graph.addJob(new Job(
                "J-101", "Inspect turbine bearings",
                Set.of("Technician-A", "Turbine-1", "Zone-North")));
        graph.addJob(new Job(
                "J-102", "Calibrate pressure sensors",
                Set.of("Technician-B", "Turbine-1")));
        graph.addJob(new Job(
                "J-103", "Replace cooling pump",
                Set.of("Technician-A", "Pump-4", "Zone-East")));
        graph.addJob(new Job(
                "J-104", "Test electrical isolation",
                Set.of("Technician-C", "Zone-North")));
        graph.addJob(new Job(
                "J-105", "Inspect backup generator",
                Set.of("Technician-B", "Generator-2")));
        graph.addJob(new Job(
                "J-106", "Verify emergency controls",
                Set.of("Technician-C", "Generator-2", "Zone-East")));

        graph.buildConflicts();
        return graph;
    }

    public static void main(String[] args) {
        MaintenanceGraph graph = createExample();

        System.out.println("MAINTENANCE RESOURCE CONFLICTS");
        for (Conflict conflict : graph.conflicts()) {
            System.out.printf(
                    "%s conflicts with %s through %s%n",
                    conflict.leftJob(),
                    conflict.rightJob(),
                    conflict.sharedResources());
        }

        System.out.println("\nBIPARTITE PROPERTY");
        System.out.println("Conflict graph bipartite: " + graph.isBipartite());

        SchedulingService service = new SchedulingService(graph);
        service.validateJobs();
        Schedule schedule = service.schedule();

        System.out.println("\nVALIDATED MAINTENANCE SCHEDULE");
        schedule.slots().entrySet().stream()
                .sorted(Map.Entry.comparingByValue())
                .forEach(entry -> System.out.printf(
                        "%s -> slot %d%n", entry.getKey(), entry.getValue()));

        System.out.println("Slots used: " + schedule.slotCount());
        System.out.println("Schedule valid: " + graph.validate(schedule.slots()));
        System.out.println("Job states: " + service.states());

        System.out.println("\nFAILURE HANDLING");
        Map<String, Integer> invalid = new HashMap<>(schedule.slots());
        List<Conflict> conflicts = graph.conflicts();
        if (!conflicts.isEmpty()) {
            Conflict conflict = conflicts.get(0);
            invalid.put(conflict.rightJob(), invalid.get(conflict.leftJob()));
            System.out.println("Conflicting assignment accepted: " + graph.validate(invalid));
        }

        try {
            graph.neighbors("J-UNKNOWN");
        } catch (IllegalArgumentException error) {
            System.out.println("Unknown job rejected: " + error.getMessage());
        }

        try {
            new Job(" ", "Invalid job", Set.of("Tool-A"));
        } catch (IllegalArgumentException error) {
            System.out.println("Invalid job rejected: " + error.getMessage());
        }

        System.out.println("\nDESIGN NOTES");
        System.out.println("Immutable records protect job definitions from accidental mutation.");
        System.out.println("Linked collections preserve deterministic output order.");
        System.out.println("BFS determines bipartiteness in O(V + E) time.");
        System.out.println("DSATUR is a scheduling heuristic, not an optimality proof.");
        System.out.println("The conflict model must be updated when resource availability changes.");
    }
}
