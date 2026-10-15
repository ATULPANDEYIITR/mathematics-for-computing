import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
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

/*
 * Enterprise connectivity service for a distributed operations platform.
 *
 * The domain model distinguishes network inventory, connectivity queries,
 * failure simulation, and a policy-driven service that reports availability.
 *
 * Compatible with Java 17+.
 */

public class GraphConnectivityEnterprise {

    enum SiteType {
        CONTROL_CENTER,
        DATA_CENTER,
        FIELD_GATEWAY,
        SENSOR_STATION
    }

    enum ServiceStatus {
        AVAILABLE,
        DEGRADED,
        ISOLATED
    }

    record Site(String id, SiteType type, String region) {
        Site {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException("Site ID is required.");
            }
            Objects.requireNonNull(type, "Site type is required.");
            if (region == null || region.isBlank()) {
                throw new IllegalArgumentException("Region is required.");
            }
        }
    }

    record Link(String first, String second) {
        Link {
            if (first == null || first.isBlank()
                    || second == null || second.isBlank()) {
                throw new IllegalArgumentException("Link endpoints are required.");
            }
            if (first.equals(second)) {
                throw new IllegalArgumentException("Self-links are not permitted.");
            }
            // A canonical endpoint order makes an undirected link comparable
            // regardless of which endpoint the caller supplied first.
            if (first.compareTo(second) > 0) {
                String temporary = first;
                first = second;
                second = temporary;
            }
        }
    }

    static final class NetworkInventory {
        private final Map<String, Site> sites = new LinkedHashMap<>();
        private final Map<String, Set<String>> adjacency = new LinkedHashMap<>();
        private final Set<Link> links = new LinkedHashSet<>();

        void registerSite(Site site) {
            Objects.requireNonNull(site, "Site is required.");
            if (sites.putIfAbsent(site.id(), site) != null) {
                throw new IllegalArgumentException(
                        "Duplicate site ID: " + site.id());
            }
            adjacency.put(site.id(), new TreeSet<>());
        }

        void establishLink(Link link) {
            requireSite(link.first());
            requireSite(link.second());

            if (!links.add(link)) {
                throw new IllegalStateException(
                        "Link already exists: " + link);
            }

            adjacency.get(link.first()).add(link.second());
            adjacency.get(link.second()).add(link.first());
        }

        void removeLink(Link link) {
            requireSite(link.first());
            requireSite(link.second());

            if (!links.remove(link)) {
                throw new IllegalStateException(
                        "Cannot remove nonexistent link: " + link);
            }

            adjacency.get(link.first()).remove(link.second());
            adjacency.get(link.second()).remove(link.first());
        }

        private void requireSite(String id) {
            if (!sites.containsKey(id)) {
                throw new IllegalArgumentException("Unknown site: " + id);
            }
        }

        Map<String, Site> sites() {
            return Collections.unmodifiableMap(sites);
        }

        Map<String, Set<String>> adjacencySnapshot() {
            Map<String, Set<String>> snapshot = new LinkedHashMap<>();
            adjacency.forEach((site, neighbors) ->
                    snapshot.put(site, Set.copyOf(neighbors)));
            return Collections.unmodifiableMap(snapshot);
        }

        Set<Link> links() {
            return Collections.unmodifiableSet(links);
        }

        NetworkInventory copy() {
            NetworkInventory clone = new NetworkInventory();
            sites.values().forEach(clone::registerSite);
            links.forEach(clone::establishLink);
            return clone;
        }
    }

    static final class ConnectivityAnalyzer {
        List<Set<String>> connectedComponents(NetworkInventory inventory) {
            Map<String, Set<String>> adjacency = inventory.adjacencySnapshot();
            Set<String> visited = new HashSet<>();
            List<Set<String>> components = new ArrayList<>();

            for (String start : adjacency.keySet()) {
                if (visited.contains(start)) {
                    continue;
                }

                Set<String> component = new LinkedHashSet<>();
                Deque<String> queue = new ArrayDeque<>();
                queue.addLast(start);
                visited.add(start);

                while (!queue.isEmpty()) {
                    String current = queue.removeFirst();
                    component.add(current);

                    for (String neighbor : adjacency.get(current)) {
                        if (visited.add(neighbor)) {
                            queue.addLast(neighbor);
                        }
                    }
                }
                components.add(Collections.unmodifiableSet(component));
            }

            return List.copyOf(components);
        }

        boolean connected(NetworkInventory inventory) {
            List<Set<String>> components = connectedComponents(inventory);
            return components.size() <= 1;
        }

        Set<String> reachableFrom(
                NetworkInventory inventory,
                String start
        ) {
            Map<String, Set<String>> adjacency = inventory.adjacencySnapshot();
            if (!adjacency.containsKey(start)) {
                throw new IllegalArgumentException("Unknown start site: " + start);
            }

            Set<String> visited = new LinkedHashSet<>();
            Deque<String> queue = new ArrayDeque<>();
            queue.add(start);
            visited.add(start);

            while (!queue.isEmpty()) {
                String current = queue.removeFirst();
                for (String neighbor : adjacency.get(current)) {
                    if (visited.add(neighbor)) {
                        queue.addLast(neighbor);
                    }
                }
            }
            return Collections.unmodifiableSet(visited);
        }
    }

    record AvailabilityReport(
            String serviceName,
            ServiceStatus status,
            int requiredSiteCount,
            int reachableSiteCount,
            List<Set<String>> components,
            String explanation
    ) {}

    static final class AvailabilityService {
        private final ConnectivityAnalyzer analyzer = new ConnectivityAnalyzer();

        AvailabilityReport evaluate(
                String serviceName,
                NetworkInventory inventory,
                Set<String> requiredSites,
                String primaryControl
        ) {
            Objects.requireNonNull(inventory);
            Objects.requireNonNull(requiredSites);

            if (serviceName == null || serviceName.isBlank()) {
                throw new IllegalArgumentException("Service name is required.");
            }
            if (!inventory.sites().containsKey(primaryControl)) {
                throw new IllegalArgumentException(
                        "Primary control site is not registered.");
            }
            if (requiredSites.isEmpty()) {
                throw new IllegalArgumentException(
                        "At least one required site must be specified.");
            }
            if (!inventory.sites().keySet().containsAll(requiredSites)) {
                throw new IllegalArgumentException(
                        "Required-site policy references an unknown site.");
            }

            Set<String> reachable = analyzer.reachableFrom(
                    inventory, primaryControl);
            long reachableRequired = requiredSites.stream()
                    .filter(reachable::contains)
                    .count();

            ServiceStatus status;
            String explanation;

            if (reachableRequired == requiredSites.size()) {
                status = ServiceStatus.AVAILABLE;
                explanation = "Every required site is reachable from primary control.";
            } else if (reachableRequired > 0) {
                status = ServiceStatus.DEGRADED;
                explanation = "Some required sites are isolated from primary control.";
            } else {
                status = ServiceStatus.ISOLATED;
                explanation = "No required site is reachable from primary control.";
            }

            return new AvailabilityReport(
                    serviceName,
                    status,
                    requiredSites.size(),
                    Math.toIntExact(reachableRequired),
                    analyzer.connectedComponents(inventory),
                    explanation
            );
        }
    }

    public static void main(String[] args) {
        NetworkInventory inventory = new NetworkInventory();

        inventory.registerSite(new Site(
                "CTRL-EAST", SiteType.CONTROL_CENTER, "East"));
        inventory.registerSite(new Site(
                "DC-EAST", SiteType.DATA_CENTER, "East"));
        inventory.registerSite(new Site(
                "GATEWAY-17", SiteType.FIELD_GATEWAY, "East"));
        inventory.registerSite(new Site(
                "SENSOR-17", SiteType.SENSOR_STATION, "East"));
        inventory.registerSite(new Site(
                "CTRL-BACKUP", SiteType.CONTROL_CENTER, "Central"));

        inventory.establishLink(new Link("CTRL-EAST", "DC-EAST"));
        inventory.establishLink(new Link("DC-EAST", "GATEWAY-17"));
        inventory.establishLink(new Link("GATEWAY-17", "SENSOR-17"));
        inventory.establishLink(new Link("CTRL-EAST", "GATEWAY-17"));

        Set<String> requiredSites = Set.of("GATEWAY-17", "SENSOR-17");
        AvailabilityService service = new AvailabilityService();

        AvailabilityReport baseline = service.evaluate(
                "Remote telemetry",
                inventory,
                requiredSites,
                "CTRL-EAST"
        );

        System.out.println("Baseline service state");
        printReport(baseline);

        // Failure simulation operates on a copy, preserving live inventory.
        NetworkInventory degraded = inventory.copy();
        degraded.removeLink(new Link("CTRL-EAST", "GATEWAY-17"));
        degraded.removeLink(new Link("DC-EAST", "GATEWAY-17"));

        AvailabilityReport failureReport = service.evaluate(
                "Remote telemetry",
                degraded,
                requiredSites,
                "CTRL-EAST"
        );

        System.out.println("\nAfter gateway isolation");
        printReport(failureReport);

        System.out.println("\nInventory consistency");
        System.out.println("Live links: " + inventory.links().size());
        System.out.println("Simulated links: " + degraded.links().size());

        try {
            inventory.establishLink(new Link("CTRL-EAST", "UNKNOWN-SITE"));
        } catch (IllegalArgumentException exception) {
            System.out.println("Rejected invalid link: " + exception.getMessage());
        }

        try {
            service.evaluate(
                    "Invalid policy",
                    inventory,
                    Set.of("UNREGISTERED-SENSOR"),
                    "CTRL-EAST"
            );
        } catch (IllegalArgumentException exception) {
            System.out.println("Rejected invalid policy: " + exception.getMessage());
        }
    }

    private static void printReport(AvailabilityReport report) {
        System.out.println("Service: " + report.serviceName());
        System.out.println("Status: " + report.status());
        System.out.println(
                "Required sites reachable: " + report.reachableSiteCount()
                        + "/" + report.requiredSiteCount());
        System.out.println("Components: " + report.components());
        System.out.println(report.explanation());
    }
}
