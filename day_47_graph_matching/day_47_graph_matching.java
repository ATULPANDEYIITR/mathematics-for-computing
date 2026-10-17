import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

public class GraphMatchingEnterprise {
    enum ReviewRole {
        CODE_OWNER,
        SECURITY_REVIEWER,
        GENERAL_REVIEWER
    }

    record PullRequest(String id, String repository, String targetBranch) {
        PullRequest {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException("Pull request ID is required.");
            }
            Objects.requireNonNull(repository);
            Objects.requireNonNull(targetBranch);
        }
    }

    record Reviewer(String id, ReviewRole role, Set<String> repositories) {
        Reviewer {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException("Reviewer ID is required.");
            }
            Objects.requireNonNull(role);
            repositories = Set.copyOf(repositories);
        }

        boolean canReview(PullRequest request) {
            return repositories.contains(request.repository());
        }
    }

    record Assignment(Reviewer reviewer, PullRequest request) {}

    static final class BipartiteMatchingService {
        private final List<Reviewer> reviewers;
        private final List<PullRequest> requests;
        private final Map<Reviewer, Set<PullRequest>> eligible = new HashMap<>();
        private final Map<PullRequest, Reviewer> requestOwner = new HashMap<>();

        BipartiteMatchingService(
            List<Reviewer> reviewers,
            List<PullRequest> requests
        ) {
            this.reviewers = List.copyOf(reviewers);
            this.requests = List.copyOf(requests);

            if (new HashSet<>(reviewers).size() != reviewers.size()) {
                throw new IllegalArgumentException("Duplicate reviewers.");
            }
            if (new HashSet<>(requests).size() != requests.size()) {
                throw new IllegalArgumentException("Duplicate pull requests.");
            }

            for (Reviewer reviewer : reviewers) {
                eligible.put(reviewer, new LinkedHashSet<>());
            }
        }

        void addEligibility(Reviewer reviewer, PullRequest request) {
            if (!eligible.containsKey(reviewer)) {
                throw new IllegalArgumentException("Unknown reviewer.");
            }
            if (!requests.contains(request)) {
                throw new IllegalArgumentException("Unknown pull request.");
            }
            if (!reviewer.canReview(request)) {
                throw new IllegalArgumentException(
                    reviewer.id() + " lacks repository access for " + request.id()
                );
            }
            eligible.get(reviewer).add(request);
        }

        private boolean augment(
            Reviewer reviewer,
            Set<PullRequest> visited
        ) {
            for (PullRequest request : eligible.get(reviewer)) {
                if (!visited.add(request)) continue;

                Reviewer previous = requestOwner.get(request);

                if (previous == null || augment(previous, visited)) {
                    requestOwner.put(request, reviewer);
                    return true;
                }
            }
            return false;
        }

        List<Assignment> maximumMatching() {
            requestOwner.clear();

            for (Reviewer reviewer : reviewers) {
                augment(reviewer, new HashSet<>());
            }

            List<Assignment> result = new ArrayList<>();
            requestOwner.forEach(
                (request, reviewer) -> result.add(
                    new Assignment(reviewer, request)
                )
            );

            if (!validate(result)) {
                throw new IllegalStateException(
                    "Matching violates allocation constraints."
                );
            }

            return List.copyOf(result);
        }

        private boolean validate(List<Assignment> assignments) {
            Set<Reviewer> assignedReviewers = new HashSet<>();
            Set<PullRequest> assignedRequests = new HashSet<>();

            for (Assignment assignment : assignments) {
                if (!eligible.get(assignment.reviewer())
                    .contains(assignment.request())) {
                    return false;
                }
                if (!assignedReviewers.add(assignment.reviewer())) {
                    return false;
                }
                if (!assignedRequests.add(assignment.request())) {
                    return false;
                }
            }
            return true;
        }
    }

    public static void main(String[] args) {
        Reviewer securityA = new Reviewer(
            "SEC-A", ReviewRole.SECURITY_REVIEWER, Set.of("payments", "identity")
        );
        Reviewer ownerB = new Reviewer(
            "OWNER-B", ReviewRole.CODE_OWNER, Set.of("payments")
        );
        Reviewer generalC = new Reviewer(
            "GEN-C", ReviewRole.GENERAL_REVIEWER, Set.of("identity", "payments")
        );

        PullRequest payments = new PullRequest(
            "PR-501", "payments", "main"
        );
        PullRequest identity = new PullRequest(
            "PR-502", "identity", "main"
        );
        PullRequest hotfix = new PullRequest(
            "PR-503", "payments", "release"
        );

        BipartiteMatchingService service = new BipartiteMatchingService(
            List.of(securityA, ownerB, generalC),
            List.of(payments, identity, hotfix)
        );

        service.addEligibility(securityA, payments);
        service.addEligibility(securityA, identity);
        service.addEligibility(ownerB, payments);
        service.addEligibility(ownerB, hotfix);
        service.addEligibility(generalC, identity);
        service.addEligibility(generalC, payments);

        List<Assignment> assignments = service.maximumMatching();

        System.out.println("Repository review assignments");
        assignments.forEach(assignment ->
            System.out.printf(
                "%s -> %s (%s)%n",
                assignment.reviewer().id(),
                assignment.request().id(),
                assignment.request().targetBranch()
            )
        );
        System.out.println("Matched requests: " + assignments.size());

        try {
            service.addEligibility(
                securityA,
                new PullRequest("PR-999", "payments", "main")
            );
            throw new IllegalStateException(
                "Unknown request should have been rejected."
            );
        } catch (IllegalArgumentException expected) {
            System.out.println("Unknown request rejected: " + expected.getMessage());
        }

        Reviewer unauthorized = new Reviewer(
            "UNAUTH", ReviewRole.GENERAL_REVIEWER, Set.of("documentation")
        );

        try {
            BipartiteMatchingService isolated = new BipartiteMatchingService(
                List.of(unauthorized),
                List.of(payments)
            );
            isolated.addEligibility(unauthorized, payments);
        } catch (IllegalArgumentException expected) {
            System.out.println("Access restriction enforced: " + expected.getMessage());
        }
    }
}
