import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.PriorityQueue;
import java.util.Set;

public class GraphOptimizationEnterprise {

    enum OptimizationObjective {
        SHORTEST_PATH,
        MINIMUM_SPANNING_TREE,
        NETWORK_THROUGHPUT
    }

    enum NodeRole {
        DATA_CENTER,
        REGIONAL_HUB,
        SERVICE_SITE,
        BACKUP_SITE
    }

    record Link(String from, String to, double cost, int capacity) {
        Link {
            Objects.requireNonNull(from);
            Objects.requireNonNull(to);

            if (cost < 0 || !Double.isFinite(cost)) {
                throw new IllegalArgumentException("Link cost must be finite and non-negative.");
            }

            if (capacity < 0) {
                throw new IllegalArgumentException("Link capacity cannot be negative.");
            }
        }
    }

    record PathResult(double distance, List<String> path) {}

    static final class Site {
        private final String id;
        private final NodeRole role;

        Site(String id, NodeRole role) {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException("Site identifier is required.");
            }
            this.id = id;
            this.role = Objects.requireNonNull(role);
        }

        String id() {
            return id;
        }

        NodeRole role() {
            return role;
        }
    }

    static final class NetworkTopology {
        private final Map<String, Site> sites = new HashMap<>();
        private final Map<String, List<Link>> links = new HashMap<>();

        void registerSite(Site site) {
            if (sites.putIfAbsent(site.id(), site) != null) {
                throw new IllegalArgumentException(
                    "Site already exists: " + site.id()
                );
            }
            links.put(site.id(), new ArrayList<>());
        }

        void connect(String from, String to, double cost, int capacity) {
            requireSite(from);
            requireSite(to);

            Link link = new Link(from, to, cost, capacity);
            links.get(from).add(link);
        }

        Set<String> siteIds() {
            return Set.copyOf(sites.keySet());
        }

        List<Link> outgoing(String site) {
            requireSite(site);
            return List.copyOf(links.get(site));
        }

        private void requireSite(String site) {
            if (!sites.containsKey(site)) {
                throw new IllegalArgumentException("Unknown site: " + site);
            }
        }
    }

    record QueueEntry(String site, double distance) {}

    static final class RouteService {

        PathResult shortestPath(NetworkTopology topology, String source, String target) {
            if (!topology.siteIds().contains(source) || !topology.siteIds().contains(target)) {
                throw new IllegalArgumentException("Both route endpoints must exist.");
            }

            Map<String, Double> distance = new HashMap<>();
            Map<String, String> previous = new HashMap<>();
            PriorityQueue<QueueEntry> queue =
                new PriorityQueue<>(Comparator.comparingDouble(QueueEntry::distance));

            for (String site : topology.siteIds()) {
                distance.put(site, Double.POSITIVE_INFINITY);
            }

            distance.put(source, 0.0);
            queue.add(new QueueEntry(source, 0.0));

            while (!queue.isEmpty()) {
                QueueEntry current = queue.poll();

                if (current.distance() != distance.get(current.site())) {
                    continue;
                }

                for (Link link : topology.outgoing(current.site())) {
                    double candidate = current.distance() + link.cost();

                    if (candidate < distance.get(link.to())) {
                        distance.put(link.to(), candidate);
                        previous.put(link.to(), current.site());
                        queue.add(new QueueEntry(link.to(), candidate));
                    }
                }
            }

            if (Double.isInfinite(distance.get(target))) {
                return new PathResult(Double.POSITIVE_INFINITY, List.of());
            }

            ArrayList<String> path = new ArrayList<>();
            String current = target;

            while (current != null) {
                path.add(current);

                if (current.equals(source)) {
                    break;
                }

                current = previous.get(current);
            }

            java.util.Collections.reverse(path);

            if (!path.get(0).equals(source)) {
                return new PathResult(Double.POSITIVE_INFINITY, List.of());
            }

            return new PathResult(distance.get(target), List.copyOf(path));
        }
    }

    static final class ConnectivityPolicy {
        private final EnumSet<NodeRole> criticalRoles =
            EnumSet.of(NodeRole.DATA_CENTER, NodeRole.REGIONAL_HUB);

        boolean requiresRedundancy(Site site) {
            return criticalRoles.contains(site.role());
        }

        boolean validPrimaryRoute(PathResult result) {
            return !result.path().isEmpty()
                && Double.isFinite(result.distance());
        }
    }

    static final class MergeIndependentNetworkPlanner {
        private static final class ComponentSet {
            private final Map<String, String> parent = new HashMap<>();
            private final Map<String, Integer> rank = new HashMap<>();

            ComponentSet(Set<String> nodes) {
                for (String node : nodes) {
                    parent.put(node, node);
                    rank.put(node, 0);
                }
            }

            String find(String node) {
                String root = parent.get(node);

                if (!root.equals(node)) {
                    root = find(root);
                    parent.put(node, root);
                }

                return root;
            }

            boolean union(String first, String second) {
                String rootFirst = find(first);
                String rootSecond = find(second);

                if (rootFirst.equals(rootSecond)) {
                    return false;
                }

                if (rank.get(rootFirst) < rank.get(rootSecond)) {
                    String temp = rootFirst;
                    rootFirst = rootSecond;
                    rootSecond = temp;
                }

                parent.put(rootSecond, rootFirst);

                if (rank.get(rootFirst).equals(rank.get(rootSecond))) {
                    rank.put(rootFirst, rank.get(rootFirst) + 1);
                }

                return true;
            }
        }

        List<Link> minimumSpanningTree(
            NetworkTopology topology,
            List<Link> undirectedLinks
        ) {
            ComponentSet components = new ComponentSet(topology.siteIds());
            List<Link> sorted = new ArrayList<>(undirectedLinks);

            sorted.sort(Comparator.comparingDouble(Link::cost));

            List<Link> selected = new ArrayList<>();

            for (Link link : sorted) {
                if (components.union(link.from(), link.to())) {
                    selected.add(link);
                }

                if (selected.size() == topology.siteIds().size() - 1) {
                    break;
                }
            }

            if (selected.size() != topology.siteIds().size() - 1) {
                throw new IllegalStateException(
                    "Infrastructure cannot connect every registered site."
                );
            }

            return List.copyOf(selected);
        }
    }

    static void buildEnterpriseTopology(NetworkTopology topology) {
        topology.registerSite(new Site("DC-DEL", NodeRole.DATA_CENTER));
        topology.registerSite(new Site("HUB-LKO", NodeRole.REGIONAL_HUB));
        topology.registerSite(new Site("HUB-JPR", NodeRole.REGIONAL_HUB));
        topology.registerSite(new Site("SITE-AGR", NodeRole.SERVICE_SITE));
        topology.registerSite(new Site("SITE-PAT", NodeRole.SERVICE_SITE));
        topology.registerSite(new Site("BACKUP-BPL", NodeRole.BACKUP_SITE));

        topology.connect("DC-DEL", "HUB-LKO", 4.0, 80);
        topology.connect("DC-DEL", "HUB-JPR", 6.0, 70);
        topology.connect("HUB-LKO", "HUB-JPR", 2.0, 60);
        topology.connect("HUB-LKO", "SITE-AGR", 2.5, 30);
        topology.connect("HUB-JPR", "SITE-AGR", 4.0, 40);
        topology.connect("HUB-LKO", "SITE-PAT", 5.0, 50);
        topology.connect("HUB-JPR", "BACKUP-BPL", 3.0, 45);
        topology.connect("SITE-PAT", "BACKUP-BPL", 2.0, 25);
    }

    static void demonstrateRouteOptimization(NetworkTopology topology) {
        RouteService routeService = new RouteService();
        PathResult route =
            routeService.shortestPath(topology, "DC-DEL", "SITE-PAT");

        System.out.println("Enterprise route optimization");
        System.out.println("Route: " + route.path());
        System.out.println("Estimated route cost: " + route.distance());

        ConnectivityPolicy policy = new ConnectivityPolicy();

        if (!policy.validPrimaryRoute(route)) {
            throw new IllegalStateException("Primary service route is unavailable.");
        }

        System.out.println(
            "HUB-LKO requires redundancy: "
                + policy.requiresRedundancy(
                    new Site("HUB-LKO", NodeRole.REGIONAL_HUB)
                )
        );
    }

    static void demonstrateInfrastructurePlanning(NetworkTopology topology) {
        List<Link> physicalLinks = List.of(
            new Link("DC-DEL", "HUB-LKO", 4.0, 80),
            new Link("DC-DEL", "HUB-JPR", 6.0, 70),
            new Link("HUB-LKO", "HUB-JPR", 2.0, 60),
            new Link("HUB-LKO", "SITE-AGR", 2.5, 30),
            new Link("HUB-JPR", "SITE-AGR", 4.0, 40),
            new Link("HUB-LKO", "SITE-PAT", 5.0, 50),
            new Link("HUB-JPR", "BACKUP-BPL", 3.0, 45),
            new Link("SITE-PAT", "BACKUP-BPL", 2.0, 25)
        );

        MergeIndependentNetworkPlanner planner =
            new MergeIndependentNetworkPlanner();

        List<Link> mst = planner.minimumSpanningTree(topology, physicalLinks);

        System.out.println("\nMinimum infrastructure plan");
        mst.forEach(link ->
            System.out.println(
                link.from() + " -- " + link.to()
                    + " cost=" + link.cost()
            )
        );
    }

    static void demonstrateFailureState(NetworkTopology topology) {
        try {
            topology.connect("UNKNOWN", "HUB-LKO", 2.0, 10);
        } catch (IllegalArgumentException error) {
            System.out.println("\nRejected invalid topology change: "
                + error.getMessage());
        }
    }

    public static void main(String[] args) {
        NetworkTopology topology = new NetworkTopology();

        buildEnterpriseTopology(topology);
        demonstrateRouteOptimization(topology);
        demonstrateInfrastructurePlanning(topology);
        demonstrateFailureState(topology);

        System.out.println(
            "\nThe enterprise model separates route optimization from "
                + "global infrastructure design: a cheapest route serves "
                + "one demand, while an MST minimizes total connectivity cost."
        );
    }
}
