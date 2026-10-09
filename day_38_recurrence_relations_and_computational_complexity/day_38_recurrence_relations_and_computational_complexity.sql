-- Recurrence Relations and Computational Complexity
-- P, NP, NP-Completeness, and Polynomial-Time Reductions
--
-- PostgreSQL-compatible SQL.
--
-- This database models computational-complexity experiments rather than
-- treating complexity classes as ordinary database labels. It records:
--   * decision problems
--   * complexity classifications
--   * certificates
--   * verification results
--   * recurrence relations
--   * polynomial reductions
--   * source and target instances
--   * execution observations
--
-- The constraints distinguish a certificate from a verification result and
-- preserve the directional meaning of a reduction:
--
--     source problem --polynomial transformation--> target problem
--
-- A reduction from A to B does not mean that A and B are interchangeable.
-- It means an efficient solver for B could be composed with the transformation
-- to solve A efficiently.

DROP SCHEMA IF EXISTS complexity_lab CASCADE;

CREATE SCHEMA complexity_lab;

SET search_path TO complexity_lab;

-- ---------------------------------------------------------------------------
-- Complexity taxonomy
-- ---------------------------------------------------------------------------

CREATE TYPE complexity_class AS ENUM (
    'P',
    'NP',
    'NP_HARD',
    'NP_COMPLETE',
    'UNKNOWN'
);

CREATE TYPE problem_kind AS ENUM (
    'DECISION',
    'OPTIMIZATION',
    'SEARCH'
);

CREATE TYPE certificate_kind AS ENUM (
    'ASSIGNMENT',
    'VERTEX_SET',
    'SUBSET',
    'OTHER'
);

CREATE TYPE verification_status AS ENUM (
    'ACCEPTED',
    'REJECTED',
    'ERROR'
);

CREATE TABLE decision_problem (
    problem_id BIGSERIAL PRIMARY KEY,
    problem_name TEXT NOT NULL UNIQUE,
    kind problem_kind NOT NULL DEFAULT 'DECISION',
    complexity complexity_class NOT NULL,
    certificate_description TEXT,
    verification_bound TEXT,
    CHECK (
        kind <> 'DECISION'
        OR certificate_description IS NOT NULL
    )
);

COMMENT ON TABLE decision_problem IS
'Decision-problem catalog used to distinguish P, NP, NP-hard, and NP-complete classifications.';

INSERT INTO decision_problem (
    problem_name,
    kind,
    complexity,
    certificate_description,
    verification_bound
)
VALUES
(
    'PATH-EXISTENCE',
    'DECISION',
    'P',
    'A proposed path can be checked against graph edges.',
    'Polynomial in the graph representation.'
),
(
    'SAT',
    'DECISION',
    'NP_COMPLETE',
    'A Boolean assignment to all variables.',
    'Evaluate every literal and clause in polynomial time.'
),
(
    '3-SAT',
    'DECISION',
    'NP_COMPLETE',
    'A Boolean assignment satisfying every three-literal clause.',
    'Polynomial in the formula size.'
),
(
    'CLIQUE',
    'DECISION',
    'NP_COMPLETE',
    'A set of k vertices.',
    'Check membership and every selected vertex pair in polynomial time.'
),
(
    'SUBSET SUM',
    'DECISION',
    'NP_COMPLETE',
    'A subset of input numbers whose sum equals the target.',
    'Add selected values and validate their indices in polynomial time.'
);

-- ---------------------------------------------------------------------------
-- Recurrence relations
-- ---------------------------------------------------------------------------

CREATE TABLE recurrence_relation (
    recurrence_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    recurrence_expression TEXT NOT NULL,
    base_case TEXT NOT NULL,
    asymptotic_bound TEXT NOT NULL,
    interpretation TEXT NOT NULL
);

INSERT INTO recurrence_relation (
    name,
    recurrence_expression,
    base_case,
    asymptotic_bound,
    interpretation
)
VALUES
(
    'Factorial',
    'T(n) = T(n-1) + Theta(1)',
    'T(0) = Theta(1)',
    'Theta(n)',
    'One recursive predecessor is evaluated at each level.'
),
(
    'Naive Fibonacci',
    'T(n) = T(n-1) + T(n-2) + Theta(1)',
    'T(0), T(1) = Theta(1)',
    'Exponential',
    'Overlapping recursive subproblems are repeatedly recomputed.'
),
(
    'Merge Sort',
    'T(n) = 2T(n/2) + Theta(n)',
    'T(1) = Theta(1)',
    'Theta(n log n)',
    'Two half-sized subproblems are combined using linear merge work.'
),
(
    'Binary Search',
    'T(n) = T(n/2) + Theta(1)',
    'T(1) = Theta(1)',
    'Theta(log n)',
    'Each comparison removes roughly half of the remaining search space.'
);

-- ---------------------------------------------------------------------------
-- Reductions
-- ---------------------------------------------------------------------------

CREATE TABLE polynomial_reduction (
    reduction_id BIGSERIAL PRIMARY KEY,
    source_problem_id BIGINT NOT NULL
        REFERENCES decision_problem(problem_id),
    target_problem_id BIGINT NOT NULL
        REFERENCES decision_problem(problem_id),
    transformation_name TEXT NOT NULL,
    transformation_bound TEXT NOT NULL,
    correctness_statement TEXT NOT NULL,
    CHECK (source_problem_id <> target_problem_id),
    UNIQUE (
        source_problem_id,
        target_problem_id,
        transformation_name
    )
);

INSERT INTO polynomial_reduction (
    source_problem_id,
    target_problem_id,
    transformation_name,
    transformation_bound,
    correctness_statement
)
SELECT
    source.problem_id,
    target.problem_id,
    '3-SAT to CLIQUE literal-occurrence construction',
    'Polynomial in the number of clauses and literal occurrences',
    'A 3-SAT formula is satisfiable if and only if its constructed graph contains a clique whose size equals the number of clauses.'
FROM decision_problem AS source
CROSS JOIN decision_problem AS target
WHERE source.problem_name = '3-SAT'
  AND target.problem_name = 'CLIQUE';

-- ---------------------------------------------------------------------------
-- SAT instance model
-- ---------------------------------------------------------------------------

CREATE TABLE sat_instance (
    instance_id BIGSERIAL PRIMARY KEY,
    problem_id BIGINT NOT NULL
        REFERENCES decision_problem(problem_id),
    instance_name TEXT NOT NULL UNIQUE,
    variable_count INTEGER NOT NULL CHECK (variable_count > 0),
    clause_count INTEGER NOT NULL CHECK (clause_count > 0)
);

CREATE TABLE sat_variable (
    instance_id BIGINT NOT NULL
        REFERENCES sat_instance(instance_id)
        ON DELETE CASCADE,
    variable_name TEXT NOT NULL,
    PRIMARY KEY (instance_id, variable_name)
);

CREATE TABLE sat_clause (
    clause_id BIGSERIAL PRIMARY KEY,
    instance_id BIGINT NOT NULL
        REFERENCES sat_instance(instance_id)
        ON DELETE CASCADE,
    clause_position INTEGER NOT NULL CHECK (clause_position > 0),
    UNIQUE (instance_id, clause_position)
);

CREATE TABLE sat_literal (
    literal_id BIGSERIAL PRIMARY KEY,
    clause_id BIGINT NOT NULL
        REFERENCES sat_clause(clause_id)
        ON DELETE CASCADE,
    variable_name TEXT NOT NULL,
    is_positive BOOLEAN NOT NULL,
    literal_position INTEGER NOT NULL CHECK (literal_position > 0),
    UNIQUE (clause_id, literal_position)
);

CREATE INDEX idx_sat_literal_variable
    ON sat_literal(variable_name);

CREATE INDEX idx_sat_clause_instance
    ON sat_clause(instance_id, clause_position);

INSERT INTO sat_instance (
    problem_id,
    instance_name,
    variable_count,
    clause_count
)
SELECT
    problem_id,
    '3sat_demo_01',
    3,
    3
FROM decision_problem
WHERE problem_name = '3-SAT';

INSERT INTO sat_variable
SELECT
    instance_id,
    variable_name
FROM sat_instance
CROSS JOIN (
    VALUES ('a'), ('b'), ('c')
) AS variables(variable_name)
WHERE instance_name = '3sat_demo_01';

INSERT INTO sat_clause (
    instance_id,
    clause_position
)
SELECT instance_id, clause_position
FROM sat_instance
CROSS JOIN generate_series(1, 3) AS positions(clause_position)
WHERE instance_name = '3sat_demo_01';

INSERT INTO sat_literal (
    clause_id,
    variable_name,
    is_positive,
    literal_position
)
SELECT
    clause.clause_id,
    literal.variable_name,
    literal.is_positive,
    literal.literal_position
FROM sat_clause AS clause
JOIN sat_instance AS instance
    ON instance.instance_id = clause.instance_id
JOIN (
    VALUES
        (1, 1, 'a', TRUE),
        (1, 2, 'b', TRUE),
        (1, 3, 'c', FALSE),
        (2, 1, 'a', FALSE),
        (2, 2, 'b', TRUE),
        (2, 3, 'c', TRUE),
        (3, 1, 'a', TRUE),
        (3, 2, 'b', FALSE),
        (3, 3, 'c', TRUE)
) AS literal(
    clause_position,
    literal_position,
    variable_name,
    is_positive
)
    ON literal.clause_position = clause.clause_position
WHERE instance.instance_name = '3sat_demo_01';

-- ---------------------------------------------------------------------------
-- SAT certificates and verification
-- ---------------------------------------------------------------------------

CREATE TABLE sat_certificate (
    certificate_id BIGSERIAL PRIMARY KEY,
    instance_id BIGINT NOT NULL
        REFERENCES sat_instance(instance_id)
        ON DELETE CASCADE,
    certificate_name TEXT NOT NULL,
    UNIQUE (instance_id, certificate_name)
);

CREATE TABLE sat_certificate_assignment (
    certificate_id BIGINT NOT NULL
        REFERENCES sat_certificate(certificate_id)
        ON DELETE CASCADE,
    variable_name TEXT NOT NULL,
    assigned_value BOOLEAN NOT NULL,
    PRIMARY KEY (certificate_id, variable_name)
);

CREATE TABLE verification_result (
    verification_id BIGSERIAL PRIMARY KEY,
    problem_id BIGINT NOT NULL
        REFERENCES decision_problem(problem_id),
    certificate_id BIGINT,
    status verification_status NOT NULL,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    explanation TEXT NOT NULL
);

INSERT INTO sat_certificate (
    instance_id,
    certificate_name
)
SELECT
    instance_id,
    'certificate_true_true_true'
FROM sat_instance
WHERE instance_name = '3sat_demo_01';

INSERT INTO sat_certificate_assignment (
    certificate_id,
    variable_name,
    assigned_value
)
SELECT
    certificate.certificate_id,
    assignment.variable_name,
    assignment.assigned_value
FROM sat_certificate AS certificate
CROSS JOIN (
    VALUES
        ('a', TRUE),
        ('b', TRUE),
        ('c', TRUE)
) AS assignment(variable_name, assigned_value)
WHERE certificate.certificate_name = 'certificate_true_true_true';

-- The following query verifies the SAT certificate without relying on
-- application-side Boolean logic. A clause is satisfied when at least one
-- literal agrees with the certificate assignment.

WITH clause_evaluation AS (
    SELECT
        clause.clause_id,
        clause.clause_position,
        BOOL_OR(
            literal.is_positive = assignment.assigned_value
        ) AS clause_satisfied
    FROM sat_clause AS clause
    JOIN sat_literal AS literal
        ON literal.clause_id = clause.clause_id
    JOIN sat_certificate AS certificate
        ON certificate.instance_id = clause.instance_id
    JOIN sat_certificate_assignment AS assignment
        ON assignment.certificate_id = certificate.certificate_id
       AND assignment.variable_name = literal.variable_name
    WHERE certificate.certificate_name = 'certificate_true_true_true'
    GROUP BY
        clause.clause_id,
        clause.clause_position
)
SELECT
    clause_position,
    clause_satisfied
FROM clause_evaluation
ORDER BY clause_position;

-- A valid certificate must satisfy every clause.
INSERT INTO verification_result (
    problem_id,
    certificate_id,
    status,
    explanation
)
SELECT
    problem.problem_id,
    certificate.certificate_id,
    CASE
        WHEN COUNT(*) FILTER (
            WHERE clause_eval.clause_satisfied = FALSE
        ) = 0
        THEN 'ACCEPTED'::verification_status
        ELSE 'REJECTED'::verification_status
    END,
    CASE
        WHEN COUNT(*) FILTER (
            WHERE clause_eval.clause_satisfied = FALSE
        ) = 0
        THEN 'Every clause has at least one satisfied literal.'
        ELSE 'At least one clause is unsatisfied.'
    END
FROM decision_problem AS problem
JOIN sat_instance AS instance
    ON instance.problem_id = problem.problem_id
JOIN sat_certificate AS certificate
    ON certificate.instance_id = instance.instance_id
JOIN (
    SELECT
        clause.clause_id,
        clause.instance_id,
        BOOL_OR(
            literal.is_positive = assignment.assigned_value
        ) AS clause_satisfied
    FROM sat_clause AS clause
    JOIN sat_literal AS literal
        ON literal.clause_id = clause.clause_id
    JOIN sat_certificate AS certificate
        ON certificate.instance_id = clause.instance_id
    JOIN sat_certificate_assignment AS assignment
        ON assignment.certificate_id = certificate.certificate_id
       AND assignment.variable_name = literal.variable_name
    WHERE certificate.certificate_name = 'certificate_true_true_true'
    GROUP BY clause.clause_id, clause.instance_id
) AS clause_eval
    ON clause_eval.instance_id = instance.instance_id
WHERE problem.problem_name = '3-SAT'
  AND certificate.certificate_name = 'certificate_true_true_true'
GROUP BY
    problem.problem_id,
    certificate.certificate_id;

-- ---------------------------------------------------------------------------
-- CLIQUE target instance
-- ---------------------------------------------------------------------------

CREATE TABLE clique_instance (
    instance_id BIGSERIAL PRIMARY KEY,
    problem_id BIGINT NOT NULL
        REFERENCES decision_problem(problem_id),
    instance_name TEXT NOT NULL UNIQUE,
    required_size INTEGER NOT NULL CHECK (required_size > 0)
);

CREATE TABLE graph_vertex (
    vertex_id BIGSERIAL PRIMARY KEY,
    instance_id BIGINT NOT NULL
        REFERENCES clique_instance(instance_id)
        ON DELETE CASCADE,
    vertex_label TEXT NOT NULL,
    source_clause_position INTEGER,
    source_variable TEXT,
    source_is_positive BOOLEAN,
    UNIQUE (instance_id, vertex_label)
);

CREATE TABLE graph_edge (
    instance_id BIGINT NOT NULL
        REFERENCES clique_instance(instance_id)
        ON DELETE CASCADE,
    first_vertex_id BIGINT NOT NULL
        REFERENCES graph_vertex(vertex_id)
        ON DELETE CASCADE,
    second_vertex_id BIGINT NOT NULL
        REFERENCES graph_vertex(vertex_id)
        ON DELETE CASCADE,
    PRIMARY KEY (
        instance_id,
        first_vertex_id,
        second_vertex_id
    ),
    CHECK (first_vertex_id < second_vertex_id)
);

CREATE INDEX idx_graph_vertex_instance
    ON graph_vertex(instance_id);

CREATE INDEX idx_graph_edge_lookup
    ON graph_edge(instance_id, first_vertex_id, second_vertex_id);

-- ---------------------------------------------------------------------------
-- Construct the 3-SAT -> CLIQUE target graph
-- ---------------------------------------------------------------------------

INSERT INTO clique_instance (
    problem_id,
    instance_name,
    required_size
)
SELECT
    problem_id,
    'clique_from_3sat_demo_01',
    clause_count
FROM decision_problem
JOIN sat_instance
    ON sat_instance.instance_name = '3sat_demo_01'
WHERE problem_name = 'CLIQUE';

INSERT INTO graph_vertex (
    instance_id,
    vertex_label,
    source_clause_position,
    source_variable,
    source_is_positive
)
SELECT
    clique.instance_id,
    CONCAT(
        'C',
        clause.clause_position,
        '_L',
        literal.literal_position
    ),
    clause.clause_position,
    literal.variable_name,
    literal.is_positive
FROM clique_instance AS clique
JOIN sat_instance AS sat
    ON sat.instance_name = '3sat_demo_01'
JOIN sat_clause AS clause
    ON clause.instance_id = sat.instance_id
JOIN sat_literal AS literal
    ON literal.clause_id = clause.clause_id
WHERE clique.instance_name = 'clique_from_3sat_demo_01';

-- Vertices from different clauses are connected unless their literals are
-- contradictory. Vertices from the same clause are intentionally not connected.
INSERT INTO graph_edge (
    instance_id,
    first_vertex_id,
    second_vertex_id
)
SELECT
    first_vertex.instance_id,
    first_vertex.vertex_id,
    second_vertex.vertex_id
FROM graph_vertex AS first_vertex
JOIN graph_vertex AS second_vertex
    ON second_vertex.instance_id = first_vertex.instance_id
   AND first_vertex.vertex_id < second_vertex.vertex_id
WHERE first_vertex.source_clause_position
      <> second_vertex.source_clause_position
  AND NOT (
      first_vertex.source_variable
          = second_vertex.source_variable
      AND first_vertex.source_is_positive
          <> second_vertex.source_is_positive
  );

-- ---------------------------------------------------------------------------
-- CLIQUE certificate
-- ---------------------------------------------------------------------------

CREATE TABLE clique_certificate (
    certificate_id BIGSERIAL PRIMARY KEY,
    instance_id BIGINT NOT NULL
        REFERENCES clique_instance(instance_id)
        ON DELETE CASCADE,
    certificate_name TEXT NOT NULL,
    UNIQUE (instance_id, certificate_name)
);

CREATE TABLE clique_certificate_vertex (
    certificate_id BIGINT NOT NULL
        REFERENCES clique_certificate(certificate_id)
        ON DELETE CASCADE,
    vertex_id BIGINT NOT NULL
        REFERENCES graph_vertex(vertex_id),
    PRIMARY KEY (certificate_id, vertex_id)
);

INSERT INTO clique_certificate (
    instance_id,
    certificate_name
)
SELECT
    instance_id,
    'clique_certificate_demo'
FROM clique_instance
WHERE instance_name = 'clique_from_3sat_demo_01';

-- Select one compatible positive literal occurrence from each source clause.
INSERT INTO clique_certificate_vertex (
    certificate_id,
    vertex_id
)
SELECT
    certificate.certificate_id,
    vertex.vertex_id
FROM clique_certificate AS certificate
JOIN graph_vertex AS vertex
    ON vertex.instance_id = certificate.instance_id
WHERE certificate.certificate_name = 'clique_certificate_demo'
  AND (
      (vertex.source_clause_position = 1
       AND vertex.source_variable = 'a'
       AND vertex.source_is_positive = TRUE)
      OR
      (vertex.source_clause_position = 2
       AND vertex.source_variable = 'b'
       AND vertex.source_is_positive = TRUE)
      OR
      (vertex.source_clause_position = 3
       AND vertex.source_variable = 'a'
       AND vertex.source_is_positive = TRUE)
  );

-- A valid CLIQUE certificate must:
--   * contain exactly k vertices
--   * contain vertices from distinct clauses
--   * have every selected pair connected by an edge
WITH certificate_vertices AS (
    SELECT
        certificate.certificate_id,
        certificate.instance_id,
        selected.vertex_id,
        vertex.source_clause_position
    FROM clique_certificate AS certificate
    JOIN clique_certificate_vertex AS selected
        ON selected.certificate_id = certificate.certificate_id
    JOIN graph_vertex AS vertex
        ON vertex.vertex_id = selected.vertex_id
),
certificate_size AS (
    SELECT
        certificate_id,
        instance_id,
        COUNT(*) AS selected_count,
        COUNT(DISTINCT source_clause_position)
            AS selected_clause_count
    FROM certificate_vertices
    GROUP BY certificate_id, instance_id
),
pair_count AS (
    SELECT
        first_selected.certificate_id,
        COUNT(*) AS connected_pairs
    FROM certificate_vertices AS first_selected
    JOIN certificate_vertices AS second_selected
        ON second_selected.certificate_id
            = first_selected.certificate_id
       AND first_selected.vertex_id
            < second_selected.vertex_id
    JOIN graph_edge AS edge
        ON edge.instance_id = first_selected.instance_id
       AND edge.first_vertex_id = first_selected.vertex_id
       AND edge.second_vertex_id = second_selected.vertex_id
    GROUP BY first_selected.certificate_id
)
SELECT
    size.certificate_id,
    size.selected_count,
    size.selected_clause_count,
    COALESCE(pair.connected_pairs, 0) AS connected_pairs,
    instance.required_size,
    CASE
        WHEN size.selected_count = instance.required_size
         AND size.selected_clause_count = instance.required_size
         AND COALESCE(pair.connected_pairs, 0)
             = instance.required_size
               * (instance.required_size - 1) / 2
        THEN TRUE
        ELSE FALSE
    END AS is_valid_clique
FROM certificate_size AS size
JOIN clique_instance AS instance
    ON instance.instance_id = size.instance_id
LEFT JOIN pair_count AS pair
    ON pair.certificate_id = size.certificate_id;

-- ---------------------------------------------------------------------------
-- SUBSET SUM certificate model
-- ---------------------------------------------------------------------------

CREATE TABLE subset_sum_instance (
    instance_id BIGSERIAL PRIMARY KEY,
    problem_id BIGINT NOT NULL
        REFERENCES decision_problem(problem_id),
    instance_name TEXT NOT NULL UNIQUE,
    target NUMERIC NOT NULL
);

CREATE TABLE subset_sum_value (
    value_id BIGSERIAL PRIMARY KEY,
    instance_id BIGINT NOT NULL
        REFERENCES subset_sum_instance(instance_id)
        ON DELETE CASCADE,
    position INTEGER NOT NULL CHECK (position > 0),
    value NUMERIC NOT NULL,
    UNIQUE (instance_id, position)
);

CREATE TABLE subset_sum_certificate (
    certificate_id BIGSERIAL PRIMARY KEY,
    instance_id BIGINT NOT NULL
        REFERENCES subset_sum_instance(instance_id)
        ON DELETE CASCADE,
    certificate_name TEXT NOT NULL,
    UNIQUE (instance_id, certificate_name)
);

CREATE TABLE subset_sum_selected_value (
    certificate_id BIGINT NOT NULL
        REFERENCES subset_sum_certificate(certificate_id)
        ON DELETE CASCADE,
    value_id BIGINT NOT NULL
        REFERENCES subset_sum_value(value_id),
    PRIMARY KEY (certificate_id, value_id)
);

INSERT INTO subset_sum_instance (
    problem_id,
    instance_name,
    target
)
SELECT
    problem_id,
    'subset_sum_demo_01',
    25
FROM decision_problem
WHERE problem_name = 'SUBSET SUM';

INSERT INTO subset_sum_value (
    instance_id,
    position,
    value
)
SELECT
    instance_id,
    input.position,
    input.value
FROM subset_sum_instance AS instance
CROSS JOIN (
    VALUES
        (1, 3),
        (2, 7),
        (3, 11),
        (4, 14),
        (5, 19)
) AS input(position, value)
WHERE instance.instance_name = 'subset_sum_demo_01';

INSERT INTO subset_sum_certificate (
    instance_id,
    certificate_name
)
SELECT
    instance_id,
    'subset_certificate_demo'
FROM subset_sum_instance
WHERE instance_name = 'subset_sum_demo_01';

-- 7 + 14 + 3 = 24 would not satisfy target 25.
-- The selected values below intentionally use 11 + 14 = 25.
INSERT INTO subset_sum_selected_value (
    certificate_id,
    value_id
)
SELECT
    certificate.certificate_id,
    value.value_id
FROM subset_sum_certificate AS certificate
JOIN subset_sum_value AS value
    ON value.instance_id = certificate.instance_id
WHERE certificate.certificate_name = 'subset_certificate_demo'
  AND value.position IN (3, 4);

SELECT
    certificate.certificate_name,
    instance.target,
    SUM(value.value) AS certificate_sum,
    SUM(value.value) = instance.target AS accepted
FROM subset_sum_certificate AS certificate
JOIN subset_sum_instance AS instance
    ON instance.instance_id = certificate.instance_id
JOIN subset_sum_selected_value AS selected
    ON selected.certificate_id = certificate.certificate_id
JOIN subset_sum_value AS value
    ON value.value_id = selected.value_id
GROUP BY
    certificate.certificate_name,
    instance.target;

-- ---------------------------------------------------------------------------
-- Complexity search-space observation
-- ---------------------------------------------------------------------------

CREATE TABLE search_space_observation (
    observation_id BIGSERIAL PRIMARY KEY,
    problem_name TEXT NOT NULL,
    input_size INTEGER NOT NULL CHECK (input_size >= 0),
    candidate_count NUMERIC NOT NULL CHECK (candidate_count >= 0),
    growth_description TEXT NOT NULL
);

INSERT INTO search_space_observation (
    problem_name,
    input_size,
    candidate_count,
    growth_description
)
SELECT
    'SAT',
    n,
    power(2::numeric, n),
    'All Boolean assignments'
FROM generate_series(5, 20, 5) AS n;

-- The query exposes why certificate verification and certificate search are
-- different computational tasks.
SELECT
    input_size,
    candidate_count,
    growth_description
FROM search_space_observation
ORDER BY input_size;

-- ---------------------------------------------------------------------------
-- Reduction report
-- ---------------------------------------------------------------------------

SELECT
    source.problem_name AS source_problem,
    target.problem_name AS target_problem,
    reduction.transformation_name,
    reduction.transformation_bound,
    reduction.correctness_statement
FROM polynomial_reduction AS reduction
JOIN decision_problem AS source
    ON source.problem_id = reduction.source_problem_id
JOIN decision_problem AS target
    ON target.problem_id = reduction.target_problem_id;

-- ---------------------------------------------------------------------------
-- Transactional integrity demonstration
-- ---------------------------------------------------------------------------

BEGIN;

-- This transaction demonstrates that a certificate assignment can be changed
-- atomically. The database does not claim that arbitrary SAT semantics can be
-- encoded only through simple CHECK constraints; formula evaluation remains a
-- relational query over literals and assignments.

UPDATE sat_certificate_assignment
SET assigned_value = FALSE
WHERE certificate_id = (
    SELECT certificate_id
    FROM sat_certificate
    WHERE certificate_name = 'certificate_true_true_true'
)
AND variable_name = 'c';

-- Re-run the verification query after the mutation.
WITH clause_evaluation AS (
    SELECT
        clause.clause_position,
        BOOL_OR(
            literal.is_positive = assignment.assigned_value
        ) AS clause_satisfied
    FROM sat_clause AS clause
    JOIN sat_literal AS literal
        ON literal.clause_id = clause.clause_id
    JOIN sat_certificate AS certificate
        ON certificate.instance_id = clause.instance_id
    JOIN sat_certificate_assignment AS assignment
        ON assignment.certificate_id = certificate.certificate_id
       AND assignment.variable_name = literal.variable_name
    WHERE certificate.certificate_name = 'certificate_true_true_true'
    GROUP BY clause.clause_position
)
SELECT
    clause_position,
    clause_satisfied
FROM clause_evaluation
ORDER BY clause_position;

ROLLBACK;

-- ROLLBACK keeps the demonstration mutation from permanently altering the
-- original certificate.
