/*
 * Inclusion-Exclusion Principle
 *
 * PostgreSQL-compatible relational demonstration.
 *
 * The schema represents a survey in which people may belong to multiple
 * overlapping activity groups. The database stores membership explicitly,
 * while queries calculate union size, exact membership categories,
 * intersections, and arithmetic-style inclusion-exclusion.
 *
 * The database also demonstrates constraints and indexes that preserve
 * the integrity of the underlying set-membership model.
 */

DROP SCHEMA IF EXISTS inclusion_exclusion_demo CASCADE;
CREATE SCHEMA inclusion_exclusion_demo;

SET search_path = inclusion_exclusion_demo;

-- ---------------------------------------------------------------------------
-- Domain model
-- ---------------------------------------------------------------------------

CREATE TABLE participant (
    participant_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    participant_name text NOT NULL,
    CONSTRAINT participant_name_not_blank
        CHECK (length(trim(participant_name)) > 0)
);

CREATE TABLE activity_set (
    activity_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    activity_name text NOT NULL UNIQUE,
    description text NOT NULL,
    CONSTRAINT activity_name_not_blank
        CHECK (length(trim(activity_name)) > 0)
);

CREATE TABLE activity_membership (
    participant_id integer NOT NULL
        REFERENCES participant(participant_id)
        ON DELETE CASCADE,

    activity_id integer NOT NULL
        REFERENCES activity_set(activity_id)
        ON DELETE CASCADE,

    joined_at date NOT NULL DEFAULT CURRENT_DATE,

    PRIMARY KEY (participant_id, activity_id)
);

CREATE INDEX idx_activity_membership_activity
    ON activity_membership(activity_id, participant_id);

CREATE INDEX idx_activity_membership_participant
    ON activity_membership(participant_id, activity_id);

-- ---------------------------------------------------------------------------
-- Sample population
-- ---------------------------------------------------------------------------

INSERT INTO participant (participant_name)
SELECT 'Participant-' || value
FROM generate_series(1, 100) AS value;

INSERT INTO activity_set (activity_name, description)
VALUES
    ('Python', 'Participants who use Python'),
    ('JavaScript', 'Participants who use JavaScript'),
    ('SQL', 'Participants who use SQL');

-- The ranges deliberately overlap so that adding individual set sizes
-- would double-count participants belonging to multiple activities.

INSERT INTO activity_membership (participant_id, activity_id)
SELECT p.participant_id, a.activity_id
FROM participant p
CROSS JOIN activity_set a
WHERE
    (a.activity_name = 'Python'
        AND p.participant_id BETWEEN 1 AND 62)
 OR (a.activity_name = 'JavaScript'
        AND p.participant_id BETWEEN 31 AND 83)
 OR (a.activity_name = 'SQL'
        AND p.participant_id BETWEEN 51 AND 91);

-- ---------------------------------------------------------------------------
-- Basic set cardinalities
-- ---------------------------------------------------------------------------

SELECT
    a.activity_name,
    COUNT(*) AS set_size
FROM activity_set a
JOIN activity_membership m
    ON m.activity_id = a.activity_id
GROUP BY a.activity_id, a.activity_name
ORDER BY a.activity_id;

-- ---------------------------------------------------------------------------
-- Pairwise intersections
-- ---------------------------------------------------------------------------

SELECT
    a1.activity_name AS first_set,
    a2.activity_name AS second_set,
    COUNT(*) AS intersection_size
FROM activity_membership m1
JOIN activity_membership m2
    ON m1.participant_id = m2.participant_id
   AND m1.activity_id < m2.activity_id
JOIN activity_set a1
    ON a1.activity_id = m1.activity_id
JOIN activity_set a2
    ON a2.activity_id = m2.activity_id
GROUP BY a1.activity_name, a2.activity_name
ORDER BY a1.activity_name, a2.activity_name;

-- ---------------------------------------------------------------------------
-- Three-set inclusion-exclusion
--
-- |A ∪ B ∪ C|
-- = |A| + |B| + |C|
-- - |A∩B| - |A∩C| - |B∩C|
-- + |A∩B∩C|
-- ---------------------------------------------------------------------------

WITH set_sizes AS (
    SELECT
        activity_id,
        COUNT(*)::bigint AS size
    FROM activity_membership
    GROUP BY activity_id
),
pair_intersections AS (
    SELECT
        m1.activity_id AS activity_a,
        m2.activity_id AS activity_b,
        COUNT(*)::bigint AS size
    FROM activity_membership m1
    JOIN activity_membership m2
      ON m1.participant_id = m2.participant_id
     AND m1.activity_id < m2.activity_id
    GROUP BY m1.activity_id, m2.activity_id
),
triple_intersection AS (
    SELECT COUNT(*)::bigint AS size
    FROM activity_membership m1
    JOIN activity_membership m2
      ON m1.participant_id = m2.participant_id
    JOIN activity_membership m3
      ON m1.participant_id = m3.participant_id
    WHERE m1.activity_id < m2.activity_id
      AND m2.activity_id < m3.activity_id
)
SELECT
    (
        SELECT SUM(size)
        FROM set_sizes
    )
    -
    (
        SELECT COALESCE(SUM(size), 0)
        FROM pair_intersections
    )
    +
    (
        SELECT size
        FROM triple_intersection
    ) AS inclusion_exclusion_union;

-- ---------------------------------------------------------------------------
-- Direct union verification
--
-- This query is intentionally independent of the arithmetic formula.
-- Comparing both results is useful when validating an implementation.
-- ---------------------------------------------------------------------------

SELECT COUNT(DISTINCT participant_id) AS direct_union_size
FROM activity_membership;

-- ---------------------------------------------------------------------------
-- Exact membership categories
-- ---------------------------------------------------------------------------

WITH participant_membership AS (
    SELECT
        p.participant_id,
        p.participant_name,
        COUNT(m.activity_id) AS activity_count
    FROM participant p
    LEFT JOIN activity_membership m
        ON m.participant_id = p.participant_id
    GROUP BY p.participant_id, p.participant_name
)
SELECT
    CASE activity_count
        WHEN 0 THEN 'none'
        WHEN 1 THEN 'exactly_one'
        WHEN 2 THEN 'exactly_two'
        WHEN 3 THEN 'all_three'
        ELSE 'unexpected'
    END AS membership_category,
    COUNT(*) AS participant_count
FROM participant_membership
GROUP BY activity_count
ORDER BY activity_count;

-- ---------------------------------------------------------------------------
-- Participants belonging to every activity
-- ---------------------------------------------------------------------------

SELECT
    p.participant_id,
    p.participant_name
FROM participant p
JOIN activity_membership m
    ON m.participant_id = p.participant_id
GROUP BY p.participant_id, p.participant_name
HAVING COUNT(DISTINCT m.activity_id) = (
    SELECT COUNT(*) FROM activity_set
)
ORDER BY p.participant_id;

-- ---------------------------------------------------------------------------
-- Participants belonging to exactly two sets
-- ---------------------------------------------------------------------------

SELECT
    p.participant_id,
    p.participant_name
FROM participant p
JOIN activity_membership m
    ON m.participant_id = p.participant_id
GROUP BY p.participant_id, p.participant_name
HAVING COUNT(DISTINCT m.activity_id) = 2
ORDER BY p.participant_id;

-- ---------------------------------------------------------------------------
-- Participants belonging to none of the sets
-- ---------------------------------------------------------------------------

SELECT
    p.participant_id,
    p.participant_name
FROM participant p
LEFT JOIN activity_membership m
    ON m.participant_id = p.participant_id
WHERE m.participant_id IS NULL
ORDER BY p.participant_id;

-- ---------------------------------------------------------------------------
-- Arithmetic inclusion-exclusion:
-- count integers in [1, 100] divisible by 2, 3, or 5.
--
-- The intersection of divisibility sets corresponds to divisibility by
-- the LCM of the selected divisors.
-- ---------------------------------------------------------------------------

WITH divisors AS (
    SELECT *
    FROM (VALUES (2), (3), (5)) AS d(divisor)
),
pairs AS (
    SELECT
        d1.divisor AS a,
        d2.divisor AS b,
        CASE
            WHEN mod(d1.divisor, d2.divisor) = 0 THEN d1.divisor
            WHEN mod(d2.divisor, d1.divisor) = 0 THEN d2.divisor
            ELSE d1.divisor * d2.divisor
        END AS common_multiple
    FROM divisors d1
    JOIN divisors d2
        ON d1.divisor < d2.divisor
),
triple AS (
    SELECT 30 AS common_multiple
)
SELECT
    100 / 2
    + 100 / 3
    + 100 / 5
    - (100 / (SELECT common_multiple FROM pairs WHERE a = 2 AND b = 3))
    - (100 / (SELECT common_multiple FROM pairs WHERE a = 2 AND b = 5))
    - (100 / (SELECT common_multiple FROM pairs WHERE a = 3 AND b = 5))
    + (100 / (SELECT common_multiple FROM triple))
    AS numbers_divisible_by_2_or_3_or_5;

-- ---------------------------------------------------------------------------
-- Transactional integrity example
--
-- The duplicate membership is rejected by the composite primary key.
-- PostgreSQL rolls back the failed statement while preserving prior data.
-- ---------------------------------------------------------------------------

BEGIN;

INSERT INTO activity_membership (participant_id, activity_id)
VALUES (
    1,
    (SELECT activity_id
     FROM activity_set
     WHERE activity_name = 'Python')
)
ON CONFLICT (participant_id, activity_id) DO NOTHING;

COMMIT;

-- ---------------------------------------------------------------------------
-- Query-plan inspection
-- ---------------------------------------------------------------------------

EXPLAIN (COSTS OFF)
SELECT COUNT(DISTINCT participant_id)
FROM activity_membership
WHERE activity_id = (
    SELECT activity_id
    FROM activity_set
    WHERE activity_name = 'Python'
);

-- The activity_id/participant_id index supports membership lookups by
-- activity and helps PostgreSQL avoid unnecessary table scanning as the
-- membership table grows.
