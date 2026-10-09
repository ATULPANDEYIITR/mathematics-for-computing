/*
 * Recurrence Relations and Computational Complexity
 * P, NP, NP-Completeness, and Polynomial-Time Reductions
 *
 * Java 17+
 *
 * Enterprise-oriented case study:
 * A repository-independent computational policy service evaluates decision
 * problems, validates certificates, represents problem classifications, and
 * demonstrates a polynomial reduction from 3-SAT to CLIQUE.
 *
 * The domain model deliberately distinguishes:
 * - a problem definition
 * - a proposed certificate
 * - certificate verification
 * - a classification claim
 * - a reduction
 *
 * This distinction is important because membership in NP concerns efficient
 * verification of certificates, while NP-hardness concerns reductions.
 */

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.function.Predicate;
import java.util.stream.Collectors;

public class ComplexityEnterpriseDemo {

    // -------------------------------------------------------------------------
    // Recurrence domain
    // -------------------------------------------------------------------------

    static long fibonacciRecursive(int n) {
        validateNonNegative(n);

        if (n <= 1) {
            return n;
        }

        return fibonacciRecursive(n - 1)
                + fibonacciRecursive(n - 2);
    }

    static long fibonacciIterative(int n) {
        validateNonNegative(n);

        long previous = 0;
        long current = 1;

        for (int i = 0; i < n; i++) {
            long next = previous + current;
            previous = current;
            current = next;
        }

        return previous;
    }

    static long fibonacciMemoized(
            int n,
            Map<Integer, Long> memo
    ) {
        validateNonNegative(n);

        if (memo.containsKey(n)) {
            return memo.get(n);
        }

        long value =
                fibonacciMemoized(n - 1, memo)
                + fibonacciMemoized(n - 2, memo);

        memo.put(n, value);
        return value;
    }

    static void validateNonNegative(int value) {
        if (value < 0) {
            throw new IllegalArgumentException(
                    "Value must be non-negative"
            );
        }
    }

    // -------------------------------------------------------------------------
    // Decision-problem taxonomy
    // -------------------------------------------------------------------------

    enum ComplexityClass {
        P,
        NP,
        NP_COMPLETE,
        UNKNOWN
    }

    record DecisionProblem(
            String name,
            ComplexityClass complexityClass,
            String certificateDescription,
            String verificationRule
    ) {
        DecisionProblem {
            Objects.requireNonNull(name);
            Objects.requireNonNull(complexityClass);
            Objects.requireNonNull(certificateDescription);
            Objects.requireNonNull(verificationRule);

            if (name.isBlank()) {
                throw new IllegalArgumentException(
                        "Problem name cannot be blank"
                );
            }
        }
    }

    interface Certificate {
        String description();
    }

    interface CertificateVerifier<C extends Certificate> {
        boolean verify(CertificateContext context, C certificate);
    }

    record CertificateContext(
            DecisionProblem problem
    ) {}

    record VerificationResult(
            boolean accepted,
            String reason
    ) {}

    // -------------------------------------------------------------------------
    // SAT model
    // -------------------------------------------------------------------------

    record Literal(
            String variable,
            boolean positive
    ) {
        Literal {
            if (variable == null || variable.isBlank()) {
                throw new IllegalArgumentException(
                        "Literal variable cannot be blank"
                );
            }
        }

        boolean evaluate(Map<String, Boolean> assignment) {
            Boolean value = assignment.get(variable);

            if (value == null) {
                throw new IllegalArgumentException(
                        "Missing assignment for " + variable
                );
            }

            return positive ? value : !value;
        }

        String display() {
            return positive ? variable : "¬" + variable;
        }
    }

    record Clause(
            List<Literal> literals
    ) {
        Clause {
            if (literals == null || literals.isEmpty()) {
                throw new IllegalArgumentException(
                        "Clause requires at least one literal"
                );
            }

            literals = List.copyOf(literals);
        }

        boolean evaluate(Map<String, Boolean> assignment) {
            return literals.stream()
                    .anyMatch(literal ->
                            literal.evaluate(assignment));
        }
    }

    record CNFFormula(
            List<String> variables,
            List<Clause> clauses
    ) {
        CNFFormula {
            variables = List.copyOf(variables);
            clauses = List.copyOf(clauses);

            if (variables.stream().anyMatch(String::isBlank)) {
                throw new IllegalArgumentException(
                        "Variable names cannot be blank"
                );
            }
        }

        boolean evaluate(Map<String, Boolean> assignment) {
            if (!assignment.keySet()
                    .equals(new HashSet<>(variables))) {
                throw new IllegalArgumentException(
                        "Assignment must contain exactly the formula variables"
                );
            }

            return clauses.stream()
                    .allMatch(clause ->
                            clause.evaluate(assignment));
        }
    }

    record SATCertificate(
            Map<String, Boolean> assignment
    ) implements Certificate {

        SATCertificate {
            assignment = Map.copyOf(assignment);
        }

        @Override
        public String description() {
            return "Boolean assignment";
        }
    }

    static final class SATVerifier
            implements CertificateVerifier<SATCertificate> {

        @Override
        public boolean verify(
                CertificateContext context,
                SATCertificate certificate
        ) {
            if (!(context.problem() instanceof DecisionProblem)) {
                return false;
            }

            return true;
        }

        boolean verify(
                CNFFormula formula,
                SATCertificate certificate
        ) {
            return formula.evaluate(certificate.assignment());
        }
    }

    // -------------------------------------------------------------------------
    // Graph / CLIQUE model
    // -------------------------------------------------------------------------

    static final class SimpleGraph {

        private final Set<Integer> vertices;
        private final Set<Edge> edges;

        SimpleGraph(Set<Integer> vertices) {
            this.vertices = Set.copyOf(vertices);
            this.edges = new HashSet<>();
        }

        void addEdge(int u, int v) {
            if (u == v) {
                throw new IllegalArgumentException(
                        "Self-loops are not allowed"
                );
            }

            if (!vertices.contains(u)
                    || !vertices.contains(v)) {
                throw new IllegalArgumentException(
                        "Both edge endpoints must be graph vertices"
                );
            }

            edges.add(new Edge(u, v));
        }

        boolean adjacent(int u, int v) {
            return edges.contains(new Edge(u, v));
        }

        Set<Integer> vertices() {
            return vertices;
        }

        int edgeCount() {
            return edges.size();
        }

        record Edge(int first, int second) {
            Edge {
                if (first > second) {
                    int temporary = first;
                    first = second;
                    second = temporary;
                }
            }
        }
    }

    record CliqueCertificate(
            Set<Integer> vertices
    ) implements Certificate {

        CliqueCertificate {
            vertices = Set.copyOf(vertices);
        }

        @Override
        public String description() {
            return "Set of vertices claimed to form a clique";
        }
    }

    static boolean verifyClique(
            SimpleGraph graph,
            CliqueCertificate certificate
    ) {
        List<Integer> vertices =
                new ArrayList<>(certificate.vertices());

        for (int vertex : vertices) {
            if (!graph.vertices().contains(vertex)) {
                return false;
            }
        }

        for (int i = 0; i < vertices.size(); i++) {
            for (int j = i + 1; j < vertices.size(); j++) {
                if (!graph.adjacent(
                        vertices.get(i),
                        vertices.get(j)
                )) {
                    return false;
                }
            }
        }

        return true;
    }

    // -------------------------------------------------------------------------
    // 3-SAT -> CLIQUE reduction
    // -------------------------------------------------------------------------

    record LiteralOccurrence(
            int clauseIndex,
            Literal literal
    ) {}

    record CliqueReduction(
            SimpleGraph graph,
            int requiredSize,
            Map<Integer, LiteralOccurrence> metadata
    ) {}

    static CliqueReduction reduce3SATToClique(
            CNFFormula formula
    ) {
        if (formula.clauses().stream()
                .anyMatch(clause ->
                        clause.literals().size() != 3)) {
            throw new IllegalArgumentException(
                    "Reduction requires a 3-SAT formula"
            );
        }

        Set<Integer> vertices = new HashSet<>();
        Map<Integer, LiteralOccurrence> metadata =
                new LinkedHashMap<>();

        int vertexId = 0;

        for (int clauseIndex = 0;
             clauseIndex < formula.clauses().size();
             clauseIndex++) {

            Clause clause = formula.clauses().get(clauseIndex);

            for (Literal literal : clause.literals()) {
                vertices.add(vertexId);
                metadata.put(
                        vertexId,
                        new LiteralOccurrence(
                                clauseIndex,
                                literal
                        )
                );
                vertexId++;
            }
        }

        SimpleGraph graph = new SimpleGraph(vertices);

        List<Integer> vertexList =
                new ArrayList<>(vertices);

        for (int i = 0; i < vertexList.size(); i++) {
            for (int j = i + 1;
                 j < vertexList.size();
                 j++) {

                int u = vertexList.get(i);
                int v = vertexList.get(j);

                LiteralOccurrence first =
                        metadata.get(u);

                LiteralOccurrence second =
                        metadata.get(v);

                if (first.clauseIndex()
                        == second.clauseIndex()) {
                    continue;
                }

                boolean contradictory =
                        first.literal().variable()
                                .equals(second.literal().variable())
                        && first.literal().positive()
                                != second.literal().positive();

                if (!contradictory) {
                    graph.addEdge(u, v);
                }
            }
        }

        return new CliqueReduction(
                graph,
                formula.clauses().size(),
                Map.copyOf(metadata)
        );
    }

    // -------------------------------------------------------------------------
    // Enterprise verification service
    // -------------------------------------------------------------------------

    static final class VerificationService {

        VerificationResult verifySAT(
                DecisionProblem problem,
                CNFFormula formula,
                SATCertificate certificate
        ) {
            if (problem.complexityClass()
                    != ComplexityClass.NP_COMPLETE) {
                return new VerificationResult(
                        false,
                        "Problem policy does not classify SAT correctly"
                );
            }

            boolean accepted =
                    formula.evaluate(
                            certificate.assignment()
                    );

            return accepted
                    ? new VerificationResult(
                            true,
                            "Every clause is satisfied"
                    )
                    : new VerificationResult(
                            false,
                            "At least one clause is unsatisfied"
                    );
        }

        VerificationResult verifyClique(
                DecisionProblem problem,
                SimpleGraph graph,
                int requiredSize,
                CliqueCertificate certificate
        ) {
            if (certificate.vertices().size()
                    != requiredSize) {
                return new VerificationResult(
                        false,
                        "Certificate has the wrong cardinality"
                );
            }

            boolean accepted =
                    verifyClique(graph, certificate);

            return accepted
                    ? new VerificationResult(
                            true,
                            "Every pair of selected vertices is adjacent"
                    )
                    : new VerificationResult(
                            false,
                            "Selected vertices do not form a clique"
                    );
        }
    }

    // -------------------------------------------------------------------------
    // Main enterprise demonstration
    // -------------------------------------------------------------------------

    public static void main(String[] args) {

        System.out.println("=== Recurrence Relations ===");

        System.out.println(
                "Naive Fibonacci F(10): "
                        + fibonacciRecursive(10)
        );

        Map<Integer, Long> memo =
                new HashMap<>();

        memo.put(0, 0L);
        memo.put(1, 1L);

        System.out.println(
                "Memoized Fibonacci F(30): "
                        + fibonacciMemoized(30, memo)
        );

        System.out.println(
                "Iterative Fibonacci F(30): "
                        + fibonacciIterative(30)
        );

        System.out.println(
                "\nNaive Fibonacci expands repeated subproblems. "
                        + "Memoization records each state once, "
                        + "changing the recurrence's practical growth "
                        + "from exponential to linear in n."
        );

        System.out.println("\n=== Decision Problem Policy ===");

        DecisionProblem satProblem =
                new DecisionProblem(
                        "3-SAT",
                        ComplexityClass.NP_COMPLETE,
                        "Truth assignment for all variables",
                        "Evaluate every clause and literal"
                );

        DecisionProblem cliqueProblem =
                new DecisionProblem(
                        "CLIQUE",
                        ComplexityClass.NP_COMPLETE,
                        "Set of k vertices",
                        "Check every pair for an edge"
                );

        System.out.println(satProblem);
        System.out.println(cliqueProblem);

        System.out.println("\n=== SAT Verification ===");

        CNFFormula formula =
                new CNFFormula(
                        List.of("a", "b", "c"),
                        List.of(
                                new Clause(List.of(
                                        new Literal("a", true),
                                        new Literal("b", true),
                                        new Literal("c", false)
                                )),
                                new Clause(List.of(
                                        new Literal("a", false),
                                        new Literal("b", true),
                                        new Literal("c", true)
                                )),
                                new Clause(List.of(
                                        new Literal("a", true),
                                        new Literal("b", false),
                                        new Literal("c", true)
                                ))
                        )
                );

        SATCertificate certificate =
                new SATCertificate(
                        Map.of(
                                "a", true,
                                "b", true,
                                "c", true
                        )
                );

        VerificationService service =
                new VerificationService();

        System.out.println(
                service.verifySAT(
                        satProblem,
                        formula,
                        certificate
                )
        );

        System.out.println(
                "\n=== Polynomial Reduction: 3-SAT -> CLIQUE ==="
        );

        CliqueReduction reduction =
                reduce3SATToClique(formula);

        System.out.println(
                "Generated vertices: "
                        + reduction.graph().vertices().size()
        );

        System.out.println(
                "Generated edges: "
                        + reduction.graph().edgeCount()
        );

        System.out.println(
                "Required clique size: "
                        + reduction.requiredSize()
        );

        Set<Integer> cliqueVertices =
                reduction.metadata()
                        .entrySet()
                        .stream()
                        .filter(entry ->
                                entry.getValue()
                                        .literal()
                                        .positive()
                        )
                        .map(Map.Entry::getKey)
                        .collect(Collectors.toCollection(
                                java.util.LinkedHashSet::new
                        ));

        /*
         * The reduction's graph encodes compatibility between literal
         * occurrences. A certificate is accepted only if it contains exactly
         * one compatible literal occurrence from each clause.
         */
        if (cliqueVertices.size()
                >= reduction.requiredSize()) {

            Set<Integer> selected =
                    cliqueVertices.stream()
                            .limit(reduction.requiredSize())
                            .collect(Collectors.toSet());

            CliqueCertificate cliqueCertificate =
                    new CliqueCertificate(selected);

            System.out.println(
                    service.verifyClique(
                            cliqueProblem,
                            reduction.graph(),
                            reduction.requiredSize(),
                            cliqueCertificate
                    )
            );
        }

        System.out.println("\n=== Complexity Relationships ===");

        System.out.println(
                "P: decision problems with polynomial-time algorithms."
        );

        System.out.println(
                "NP: decision problems whose proposed certificates "
                        + "can be verified in polynomial time."
        );

        System.out.println(
                "NP-hard: problems at least as difficult as every "
                        + "problem in NP under the selected reduction notion."
        );

        System.out.println(
                "NP-complete: problems that are both in NP and NP-hard."
        );

        System.out.println(
                "If A <=p B and B has a polynomial-time algorithm, "
                        + "then A also has a polynomial-time algorithm "
                        + "by composing the reduction with B's algorithm."
        );

        System.out.println(
                "\nThe distinction between finding and verifying is central: "
                        + "an NP certificate may be quick to check even when "
                        + "the fastest known general-purpose method for finding "
                        + "such a certificate requires super-polynomial search."
        );
    }
}
