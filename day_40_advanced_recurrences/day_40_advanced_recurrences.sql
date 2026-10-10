-- Advanced recurrence analysis using PostgreSQL.
-- The schema records recurrence definitions, evaluated tree levels,
-- analytical classifications, and observed execution costs.
--
-- Run in a PostgreSQL database with permission to create tables and views.

BEGIN;

DROP VIEW IF EXISTS recurrence_analysis CASCADE;
DROP TABLE IF EXISTS observed_runs CASCADE;
DROP TABLE IF EXISTS tree_levels CASCADE;
DROP TABLE IF EXISTS recurrence_models CASCADE;

CREATE TABLE recurrence_models (
    recurrence_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    model_name TEXT NOT NULL UNIQUE,
    branching_factor INTEGER NOT NULL CHECK (branching_factor >= 1),
    shrink_factor INTEGER NOT NULL CHECK (shrink_factor > 1),
    polynomial_power NUMERIC NOT NULL CHECK (polynomial_power >= 0),
    combine_coefficient NUMERIC NOT NULL CHECK (combine_coefficient >= 0),
    base_cost NUMERIC NOT NULL DEFAULT 1 CHECK (base_cost >= 0),
    description TEXT NOT NULL
);

CREATE TABLE tree_levels (
    recurrence_id BIGINT NOT NULL
        REFERENCES recurrence_models(recurrence_id) ON DELETE CASCADE,
    input_size BIGINT NOT NULL CHECK (input_size >= 1),
    depth INTEGER NOT NULL CHECK (depth >= 0),
    node_count NUMERIC NOT NULL CHECK (node_count >= 1),
    subproblem_size BIGINT NOT NULL CHECK (subproblem_size >= 1),
    local_cost_per_node NUMERIC NOT NULL CHECK (local_cost_per_node >= 0),
    aggregate_level_cost NUMERIC NOT NULL CHECK (aggregate_level_cost >= 0),
    PRIMARY KEY (recurrence_id, input_size, depth)
);

CREATE TABLE observed_runs (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    recurrence_id BIGINT NOT NULL
        REFERENCES recurrence_models(recurrence_id) ON DELETE CASCADE,
    input_size BIGINT NOT NULL CHECK (input_size >= 1),
    measured_operations NUMERIC NOT NULL CHECK (measured_operations >= 0),
    elapsed_ms NUMERIC NOT NULL CHECK (elapsed_ms >= 0),
    environment_name TEXT NOT NULL,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tree_levels_input
    ON tree_levels (input_size, recurrence_id);

CREATE INDEX idx_observed_runs_model_time
    ON observed_runs (recurrence_id, executed_at DESC);

INSERT INTO recurrence_models (
    model_name,
    branching_factor,
    shrink_factor,
    polynomial_power,
    combine_coefficient,
    base_cost,
    description
)
VALUES
(
    'Merge-style aggregation',
    2, 2, 1, 1, 1,
    'Two half-size tasks plus linear merge work.'
),
(
    'Single-branch search',
    1, 2, 0, 1, 1,
    'One half-size task plus constant decision work.'
),
(
    'Quadratic combine',
    2, 2, 2, 1, 1,
    'Two half-size tasks plus quadratic local processing.'
),
(
    'Four-way decomposition',
    4, 2, 1, 1, 1,
    'Four half-size tasks plus linear local processing.'
);

-- Record sample recursion-tree levels for power-of-two workloads.
-- The level counts describe a full tree; aggregate costs use the model's
-- polynomial local-work assumption.
WITH RECURSIVE level_data AS (
    SELECT
        m.recurrence_id,
        n.input_size,
        0 AS depth,
        1::NUMERIC AS node_count,
        n.input_size AS subproblem_size,
        m.polynomial_power,
        m.combine_coefficient,
        m.base_cost,
        m.branching_factor,
        m.shrink_factor
    FROM recurrence_models AS m
    CROSS JOIN (
        VALUES (8::BIGINT), (16::BIGINT), (32::BIGINT)
    ) AS n(input_size)

    UNION ALL

    SELECT
        recurrence_id,
        input_size,
        depth + 1,
        node_count * branching_factor,
        GREATEST(
            1,
            FLOOR(subproblem_size::NUMERIC / shrink_factor)::BIGINT
        ),
        polynomial_power,
        combine_coefficient,
        base_cost,
        branching_factor,
        shrink_factor
    FROM level_data
    WHERE subproblem_size > 1
),
computed AS (
    SELECT
        recurrence_id,
        input_size,
        depth,
        node_count,
        subproblem_size,
        CASE
            WHEN subproblem_size = 1 THEN base_cost
            ELSE combine_coefficient
                 * POWER(subproblem_size::NUMERIC, polynomial_power)
        END AS local_cost
    FROM level_data
)
INSERT INTO tree_levels (
    recurrence_id,
    input_size,
    depth,
    node_count,
    subproblem_size,
    local_cost_per_node,
    aggregate_level_cost
)
SELECT
    recurrence_id,
    input_size,
    depth,
    node_count,
    subproblem_size,
    local_cost,
    node_count * local_cost
FROM computed
ON CONFLICT (recurrence_id, input_size, depth)
DO UPDATE SET
    node_count = EXCLUDED.node_count,
    subproblem_size = EXCLUDED.subproblem_size,
    local_cost_per_node = EXCLUDED.local_cost_per_node,
    aggregate_level_cost = EXCLUDED.aggregate_level_cost;

INSERT INTO observed_runs (
    recurrence_id,
    input_size,
    measured_operations,
    elapsed_ms,
    environment_name
)
SELECT
    recurrence_id,
    input_size,
    CASE
        WHEN model_name = 'Merge-style aggregation'
            THEN input_size * LOG(2, input_size) + input_size
        WHEN model_name = 'Single-branch search'
            THEN LOG(2, input_size) + 1
        WHEN model_name = 'Quadratic combine'
            THEN input_size * input_size
        ELSE input_size * input_size
    END,
    input_size::NUMERIC / 100.0,
    'illustrative-reference-environment'
FROM recurrence_models
CROSS JOIN (VALUES (16::BIGINT), (32::BIGINT)) AS sizes(input_size);

-- The Master Theorem comparison separates the critical exponent
-- log_b(a) from the polynomial exponent of the nonrecursive work.
CREATE VIEW recurrence_analysis AS
SELECT
    recurrence_id,
    model_name,
    branching_factor,
    shrink_factor,
    polynomial_power,
    LN(branching_factor::NUMERIC)
        / LN(shrink_factor::NUMERIC) AS critical_exponent,
    CASE
        WHEN polynomial_power <
             LN(branching_factor::NUMERIC)
             / LN(shrink_factor::NUMERIC)
            THEN 'Case 1: recursive leaves dominate'
        WHEN polynomial_power =
             LN(branching_factor::NUMERIC)
             / LN(shrink_factor::NUMERIC)
            THEN 'Case 2: balanced levels'
        ELSE
            'Case 3 candidate: combine work may dominate'
    END AS master_theorem_classification,
    CASE
        WHEN polynomial_power <
             LN(branching_factor::NUMERIC)
             / LN(shrink_factor::NUMERIC)
            THEN 'Theta(n^log_b(a))'
        WHEN polynomial_power =
             LN(branching_factor::NUMERIC)
             / LN(shrink_factor::NUMERIC)
            THEN 'Theta(n^p log n)'
        ELSE
            'Theta(n^p), subject to regularity'
    END AS expected_complexity
FROM recurrence_models;

-- Inspect analytical classifications.
SELECT *
FROM recurrence_analysis
ORDER BY recurrence_id;

-- Sum tree work by input size. This is the aggregate of the stored
-- level model, not necessarily the exact integer recurrence evaluation.
SELECT
    m.model_name,
    t.input_size,
    SUM(t.aggregate_level_cost) AS total_tree_work,
    MAX(t.depth) AS tree_depth,
    SUM(t.node_count) AS total_nodes_across_levels
FROM tree_levels AS t
JOIN recurrence_models AS m USING (recurrence_id)
GROUP BY m.model_name, t.input_size
ORDER BY m.model_name, t.input_size;

-- Compare illustrative measured operation counts with tree predictions.
SELECT
    m.model_name,
    r.input_size,
    r.measured_operations,
    r.elapsed_ms,
    r.environment_name,
    r.executed_at
FROM observed_runs AS r
JOIN recurrence_models AS m USING (recurrence_id)
ORDER BY m.model_name, r.input_size;

-- A database constraint rejects an invalid shrink factor.
-- This block demonstrates the error without aborting the surrounding
-- transaction by handling the expected constraint violation.
DO $$
BEGIN
    BEGIN
        INSERT INTO recurrence_models (
            model_name,
            branching_factor,
            shrink_factor,
            polynomial_power,
            combine_coefficient,
            base_cost,
            description
        )
        VALUES (
            'Invalid shrink factor example',
            2, 1, 1, 1, 1,
            'This row must be rejected.'
        );
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'Invalid recurrence rejected by CHECK constraint.';
    END;
END
$$;

COMMIT;
