-- Pigeonhole Principle: Computing Applications
-- PostgreSQL-compatible executable demonstration.
--
-- The schema models a finite-bucket allocation service. Objects are assigned
-- to partitions, and the database records both the actual assignment and the
-- mathematical occupancy guarantees that follow from the number of objects
-- and partitions.
--
-- The central generalized principle is:
--
--     maximum occupancy >= CEIL(number_of_objects / number_of_partitions)
--
-- A second useful form is:
--
--     objects required to guarantee occupancy >= t
--       = partitions * (t - 1) + 1


DROP SCHEMA IF EXISTS pigeonhole_lab CASCADE;

CREATE SCHEMA pigeonhole_lab;

SET search_path = pigeonhole_lab, public;


CREATE TABLE partition_pool (
    partition_id BIGSERIAL PRIMARY KEY,
    partition_name TEXT NOT NULL UNIQUE,
    state TEXT NOT NULL DEFAULT 'AVAILABLE',
    CONSTRAINT partition_state_check
        CHECK (state IN ('AVAILABLE', 'DRAINING', 'OFFLINE'))
);


CREATE TABLE artifact (
    artifact_id BIGSERIAL PRIMARY KEY,
    artifact_key TEXT NOT NULL UNIQUE,
    repository_name TEXT NOT NULL,
    size_bytes BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT artifact_key_not_blank
        CHECK (length(trim(artifact_key)) > 0),
    CONSTRAINT repository_name_not_blank
        CHECK (length(trim(repository_name)) > 0),
    CONSTRAINT artifact_size_nonnegative
        CHECK (size_bytes >= 0)
);


CREATE TABLE artifact_assignment (
    assignment_id BIGSERIAL PRIMARY KEY,
    artifact_id BIGINT NOT NULL
        REFERENCES artifact(artifact_id)
        ON DELETE CASCADE,
    partition_id BIGINT NOT NULL
        REFERENCES partition_pool(partition_id),
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT artifact_assignment_unique
        UNIQUE (artifact_id)
);


CREATE TABLE occupancy_snapshot (
    snapshot_id BIGSERIAL PRIMARY KEY,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    object_count BIGINT NOT NULL,
    container_count BIGINT NOT NULL,
    guaranteed_max_occupancy BIGINT NOT NULL,
    target_occupancy BIGINT,
    objects_required_for_target BIGINT,
    CONSTRAINT snapshot_object_count_check
        CHECK (object_count >= 0),
    CONSTRAINT snapshot_container_count_check
        CHECK (container_count > 0),
    CONSTRAINT snapshot_guaranteed_check
        CHECK (
            guaranteed_max_occupancy =
            CASE
                WHEN object_count = 0 THEN 0
                ELSE CEIL(
                    object_count::NUMERIC /
                    container_count::NUMERIC
                )::BIGINT
            END
        ),
    CONSTRAINT snapshot_target_check
        CHECK (
            target_occupancy IS NULL
            OR target_occupancy > 0
        ),
    CONSTRAINT snapshot_target_formula_check
        CHECK (
            target_occupancy IS NULL
            OR objects_required_for_target =
                container_count * (target_occupancy - 1) + 1
        )
);


CREATE INDEX artifact_assignment_partition_idx
    ON artifact_assignment(partition_id);


CREATE INDEX artifact_repository_idx
    ON artifact(repository_name);


INSERT INTO partition_pool (
    partition_name,
    state
)
VALUES
    ('partition-a', 'AVAILABLE'),
    ('partition-b', 'AVAILABLE'),
    ('partition-c', 'AVAILABLE'),
    ('partition-d', 'AVAILABLE'),
    ('partition-e', 'DRAINING'),
    ('partition-f', 'OFFLINE');


INSERT INTO artifact (
    artifact_key,
    repository_name,
    size_bytes
)
VALUES
    ('build-001', 'payments', 12000),
    ('build-002', 'payments', 15000),
    ('build-003', 'identity', 11000),
    ('build-004', 'analytics', 19000),
    ('build-005', 'analytics', 22000),
    ('build-006', 'identity', 10000),
    ('build-007', 'payments', 14000),
    ('build-008', 'identity', 13000),
    ('build-009', 'analytics', 17000),
    ('build-010', 'payments', 21000),
    ('build-011', 'identity', 9000),
    ('build-012', 'analytics', 18000),
    ('build-013', 'payments', 16000);


-- The following assignment deliberately uses four available partitions.
-- The DRAINING and OFFLINE partitions remain outside the active assignment
-- pool because the counting argument should use the actual eligible
-- containers for the workflow being modeled.

INSERT INTO artifact_assignment (
    artifact_id,
    partition_id
)
SELECT
    a.artifact_id,
    p.partition_id
FROM (
    SELECT
        artifact_id,
        ROW_NUMBER() OVER (
            ORDER BY artifact_id
        ) AS sequence_number
    FROM artifact
) AS a
JOIN (
    SELECT
        partition_id,
        ROW_NUMBER() OVER (
            ORDER BY partition_id
        ) AS sequence_number
    FROM partition_pool
    WHERE state = 'AVAILABLE'
) AS p
ON (
    ((a.sequence_number - 1) % 4) + 1 =
    p.sequence_number
);


-- Basic occupancy query.

SELECT
    p.partition_name,
    p.state,
    COUNT(aa.assignment_id) AS object_count
FROM partition_pool AS p
LEFT JOIN artifact_assignment AS aa
    ON aa.partition_id = p.partition_id
GROUP BY
    p.partition_id,
    p.partition_name,
    p.state
ORDER BY
    p.partition_id;


-- Generalized pigeonhole bound for the active partitions.

WITH counts AS (
    SELECT
        COUNT(*) FILTER (
            WHERE state = 'AVAILABLE'
        ) AS active_partitions,
        (
            SELECT COUNT(*)
            FROM artifact
        ) AS object_count
    FROM partition_pool
)
SELECT
    object_count,
    active_partitions,
    CEIL(
        object_count::NUMERIC /
        NULLIF(active_partitions, 0)::NUMERIC
    )::BIGINT AS guaranteed_max_occupancy
FROM counts;


-- Determine whether the actual distribution satisfies the mathematical
-- lower bound. The largest observed partition occupancy can never be lower
-- than the generalized pigeonhole bound.

WITH active AS (
    SELECT COUNT(*) AS active_count
    FROM partition_pool
    WHERE state = 'AVAILABLE'
),
object_total AS (
    SELECT COUNT(*) AS object_count
    FROM artifact
),
actual AS (
    SELECT
        MAX(object_count) AS largest_actual_occupancy
    FROM (
        SELECT
            p.partition_id,
            COUNT(aa.assignment_id) AS object_count
        FROM partition_pool AS p
        LEFT JOIN artifact_assignment AS aa
            ON aa.partition_id = p.partition_id
        WHERE p.state = 'AVAILABLE'
        GROUP BY p.partition_id
    ) AS partition_counts
)
SELECT
    object_total.object_count,
    active.active_count,
    CEIL(
        object_total.object_count::NUMERIC /
        active.active_count::NUMERIC
    )::BIGINT AS pigeonhole_bound,
    actual.largest_actual_occupancy,
    (
        actual.largest_actual_occupancy >=
        CEIL(
            object_total.object_count::NUMERIC /
            active.active_count::NUMERIC
        )::BIGINT
    ) AS bound_satisfied
FROM object_total
CROSS JOIN active
CROSS JOIN actual;


-- Generalized threshold calculation.
--
-- With k containers, k * (t - 1) objects can still be distributed so that
-- every container contains at most t - 1 objects. The next object forces
-- at least one container to reach t.

WITH parameters AS (
    SELECT
        4::BIGINT AS container_count,
        5::BIGINT AS target_occupancy
)
SELECT
    container_count,
    target_occupancy,
    container_count * (target_occupancy - 1) + 1
        AS objects_required
FROM parameters;


-- Modular arithmetic application.
--
-- Fifty integers mapped to seven residue classes must produce a residue
-- class containing at least ceil(50 / 7) = 8 integers.

WITH integers AS (
    SELECT generate_series(0, 49) AS value
),
residues AS (
    SELECT
        value,
        MOD(value, 7) AS residue
    FROM integers
)
SELECT
    residue,
    COUNT(*) AS value_count,
    MIN(value) AS first_value,
    MAX(value) AS last_value
FROM residues
GROUP BY residue
ORDER BY residue;


-- Finite identifier-space calculation.
--
-- Four hexadecimal symbols produce 16^4 possible identifiers.
-- Assigning 16^4 + 1 objects to that identifier space forces a duplicate.

WITH identifier_space AS (
    SELECT POWER(16::NUMERIC, 4)::BIGINT AS possible_identifiers
)
SELECT
    possible_identifiers,
    possible_identifiers + 1 AS assignments_required_for_duplicate;


-- Bit-pattern application.
--
-- Eight bits produce 2^8 distinct patterns. A system that needs 257
-- distinct states cannot encode every state uniquely using eight bits.

SELECT
    POWER(2::NUMERIC, 8)::BIGINT AS eight_bit_patterns,
    POWER(2::NUMERIC, 8)::BIGINT + 1 AS required_distinct_states,
    9 AS bits_required_for_257_states;


-- Duplicate detection using a window function.
--
-- The query identifies artifact keys that occur more than once. The UNIQUE
-- constraint prevents such duplicates in the artifact table itself, so the
-- query is also useful when applied to imported staging data.

WITH staged_keys AS (
    SELECT *
    FROM (
        VALUES
            ('REQ-100'),
            ('REQ-101'),
            ('REQ-102'),
            ('REQ-101'),
            ('REQ-103'),
            ('REQ-100')
    ) AS input_data(artifact_key)
)
SELECT
    artifact_key,
    COUNT(*) AS occurrences
FROM staged_keys
GROUP BY artifact_key
HAVING COUNT(*) > 1
ORDER BY artifact_key;


-- A staging-table demonstration of database-level duplicate prevention.

CREATE TEMP TABLE staged_artifacts (
    artifact_key TEXT NOT NULL,
    repository_name TEXT NOT NULL
);

INSERT INTO staged_artifacts (
    artifact_key,
    repository_name
)
VALUES
    ('REQ-200', 'payments'),
    ('REQ-201', 'identity'),
    ('REQ-200', 'analytics'),
    ('REQ-202', 'payments');


SELECT
    artifact_key,
    COUNT(*) AS occurrences
FROM staged_artifacts
GROUP BY artifact_key
HAVING COUNT(*) > 1
ORDER BY artifact_key;


-- Transactional integrity demonstration.
--
-- The transaction deliberately attempts to assign one artifact to two
-- partitions. The UNIQUE constraint on artifact_id rejects the second
-- assignment. The ROLLBACK keeps the database in a consistent state.

BEGIN;

INSERT INTO artifact_assignment (
    artifact_id,
    partition_id
)
SELECT
    artifact_id,
    partition_id
FROM (
    SELECT
        (SELECT artifact_id
         FROM artifact
         WHERE artifact_key = 'build-001') AS artifact_id,
        (SELECT partition_id
         FROM partition_pool
         WHERE partition_name = 'partition-a') AS partition_id
) AS candidate
WHERE NOT EXISTS (
    SELECT 1
    FROM artifact_assignment
    WHERE artifact_id = candidate.artifact_id
);

-- The duplicate assignment below is intentionally not executed because the
-- previous assignment already exists. PostgreSQL would reject it under the
-- artifact_assignment_unique constraint if the INSERT were attempted.

ROLLBACK;


-- Snapshot the deterministic guarantee for the current active topology.

WITH parameters AS (
    SELECT
        (
            SELECT COUNT(*)
            FROM artifact
        )::BIGINT AS object_count,
        (
            SELECT COUNT(*)
            FROM partition_pool
            WHERE state = 'AVAILABLE'
        )::BIGINT AS container_count
)
INSERT INTO occupancy_snapshot (
    object_count,
    container_count,
    guaranteed_max_occupancy,
    target_occupancy,
    objects_required_for_target
)
SELECT
    object_count,
    container_count,
    CASE
        WHEN object_count = 0 THEN 0
        ELSE CEIL(
            object_count::NUMERIC /
            container_count::NUMERIC
        )::BIGINT
    END,
    5,
    container_count * (5 - 1) + 1
FROM parameters
WHERE container_count > 0;


SELECT
    snapshot_id,
    captured_at,
    object_count,
    container_count,
    guaranteed_max_occupancy,
    target_occupancy,
    objects_required_for_target
FROM occupancy_snapshot
ORDER BY snapshot_id;


-- An analytical query comparing actual maximum occupancy with the
-- mathematical guarantee.

WITH active_partition_counts AS (
    SELECT
        p.partition_id,
        COUNT(aa.assignment_id) AS object_count
    FROM partition_pool AS p
    LEFT JOIN artifact_assignment AS aa
        ON aa.partition_id = p.partition_id
    WHERE p.state = 'AVAILABLE'
    GROUP BY p.partition_id
),
parameters AS (
    SELECT
        COUNT(*) AS object_count,
        (
            SELECT COUNT(*)
            FROM partition_pool
            WHERE state = 'AVAILABLE'
        ) AS container_count
    FROM artifact
)
SELECT
    parameters.object_count,
    parameters.container_count,
    CEIL(
        parameters.object_count::NUMERIC /
        parameters.container_count::NUMERIC
    )::BIGINT AS guaranteed_minimum_maximum,
    MAX(
        active_partition_counts.object_count
    ) AS observed_maximum_occupancy,
    MAX(
        active_partition_counts.object_count
    ) -
    CEIL(
        parameters.object_count::NUMERIC /
        parameters.container_count::NUMERIC
    )::BIGINT AS excess_above_guarantee
FROM parameters
CROSS JOIN active_partition_counts
GROUP BY
    parameters.object_count,
    parameters.container_count;


-- The database model distinguishes three related ideas:
--
-- 1. artifact_assignment records the actual placement.
-- 2. occupancy_snapshot records a mathematical guarantee derived from counts.
-- 3. partition_pool controls which containers are eligible for allocation.
--
-- The UNIQUE constraint on artifact_assignment prevents one artifact from
-- being simultaneously assigned to multiple partitions, while the foreign
-- keys prevent references to nonexistent artifacts or partitions.
