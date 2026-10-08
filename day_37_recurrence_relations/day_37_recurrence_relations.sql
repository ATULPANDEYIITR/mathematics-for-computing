-- Recurrence Relations Laboratory
-- PostgreSQL-compatible SQL
--
-- The schema models recurrence definitions and generated sequence terms.
-- It distinguishes:
--   * linear recurrence structure
--   * homogeneous recurrence where forcing is zero
--   * non-homogeneous recurrence where forcing contributes an external term
--
-- Recursive CTEs are used to generate terms directly inside PostgreSQL.

DROP SCHEMA IF EXISTS recurrence_lab CASCADE;
CREATE SCHEMA recurrence_lab;

SET search_path TO recurrence_lab;

-- A recurrence definition describes the mathematical rule.
CREATE TABLE recurrence_definition (
    recurrence_id       BIGSERIAL PRIMARY KEY,
    recurrence_name     TEXT NOT NULL UNIQUE,
    recurrence_order    INTEGER NOT NULL CHECK (recurrence_order > 0),
    recurrence_type     TEXT NOT NULL
        CHECK (recurrence_type IN ('HOMOGENEOUS', 'NON_HOMOGENEOUS')),
    description         TEXT NOT NULL
);

-- Coefficients are stored by lag:
--
-- lag 1 -> coefficient applied to a_(n-1)
-- lag 2 -> coefficient applied to a_(n-2)
-- ...
CREATE TABLE recurrence_coefficient (
    recurrence_id       BIGINT NOT NULL
        REFERENCES recurrence_definition(recurrence_id)
        ON DELETE CASCADE,
    lag                  INTEGER NOT NULL CHECK (lag > 0),
    coefficient          NUMERIC NOT NULL,
    PRIMARY KEY (recurrence_id, lag)
);

CREATE TABLE recurrence_initial_term (
    recurrence_id       BIGINT NOT NULL
        REFERENCES recurrence_definition(recurrence_id)
        ON DELETE CASCADE,
    term_index           INTEGER NOT NULL CHECK (term_index >= 0),
    term_value           NUMERIC NOT NULL,
    PRIMARY KEY (recurrence_id, term_index)
);

-- A forcing term is represented as data rather than hidden inside the
-- recurrence coefficients. This keeps homogeneous and non-homogeneous
-- behavior distinguishable at the database layer.
CREATE TABLE recurrence_forcing (
    recurrence_id       BIGINT NOT NULL
        REFERENCES recurrence_definition(recurrence_id)
        ON DELETE CASCADE,
    term_index           INTEGER NOT NULL CHECK (term_index >= 0),
    forcing_value        NUMERIC NOT NULL,
    PRIMARY KEY (recurrence_id, term_index)
);

CREATE TABLE generated_term (
    recurrence_id       BIGINT NOT NULL
        REFERENCES recurrence_definition(recurrence_id)
        ON DELETE CASCADE,
    term_index           INTEGER NOT NULL CHECK (term_index >= 0),
    term_value           NUMERIC NOT NULL,
    generated_at         TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (recurrence_id, term_index)
);

CREATE INDEX idx_generated_term_recurrence_index
    ON generated_term (recurrence_id, term_index);

CREATE INDEX idx_forcing_recurrence_index
    ON recurrence_forcing (recurrence_id, term_index);

-- ---------------------------------------------------------------------------
-- Definitions
-- ---------------------------------------------------------------------------

INSERT INTO recurrence_definition (
    recurrence_name,
    recurrence_order,
    recurrence_type,
    description
)
VALUES
(
    'fibonacci',
    2,
    'HOMOGENEOUS',
    'F_n = F_(n-1) + F_(n-2)'
),
(
    'growth_with_linear_forcing',
    1,
    'NON_HOMOGENEOUS',
    'A_n = 2A_(n-1) + n'
),
(
    'inventory_with_campaign_effect',
    2,
    'NON_HOMOGENEOUS',
    'D_n = D_(n-1) + D_(n-2) + campaign(n)'
);

-- Fibonacci:
-- F_n = 1*F_(n-1) + 1*F_(n-2)
INSERT INTO recurrence_coefficient
(recurrence_id, lag, coefficient)
SELECT recurrence_id, lag, coefficient
FROM recurrence_definition d
CROSS JOIN LATERAL (
    VALUES
        (1, 1::NUMERIC),
        (2, 1::NUMERIC)
) AS c(lag, coefficient)
WHERE d.recurrence_name = 'fibonacci';

INSERT INTO recurrence_initial_term
(recurrence_id, term_index, term_value)
SELECT recurrence_id, term_index, term_value
FROM recurrence_definition d
CROSS JOIN LATERAL (
    VALUES
        (0, 0::NUMERIC),
        (1, 1::NUMERIC)
) AS t(term_index, term_value)
WHERE d.recurrence_name = 'fibonacci';

-- A_n = 2A_(n-1) + n
INSERT INTO recurrence_coefficient
(recurrence_id, lag, coefficient)
SELECT recurrence_id, 1, 2
FROM recurrence_definition
WHERE recurrence_name = 'growth_with_linear_forcing';

INSERT INTO recurrence_initial_term
(recurrence_id, term_index, term_value)
SELECT recurrence_id, 0, 1
FROM recurrence_definition
WHERE recurrence_name = 'growth_with_linear_forcing';

INSERT INTO recurrence_forcing
(recurrence_id, term_index, forcing_value)
SELECT
    d.recurrence_id,
    n,
    n::NUMERIC
FROM recurrence_definition d
CROSS JOIN generate_series(1, 12) AS n
WHERE d.recurrence_name = 'growth_with_linear_forcing';

-- Inventory model:
-- D_n = D_(n-1) + D_(n-2) + campaign(n)
INSERT INTO recurrence_coefficient
(recurrence_id, lag, coefficient)
SELECT recurrence_id, lag, coefficient
FROM recurrence_definition d
CROSS JOIN LATERAL (
    VALUES
        (1, 1::NUMERIC),
        (2, 1::NUMERIC)
) AS c(lag, coefficient)
WHERE d.recurrence_name = 'inventory_with_campaign_effect';

INSERT INTO recurrence_initial_term
(recurrence_id, term_index, term_value)
SELECT recurrence_id, term_index, term_value
FROM recurrence_definition d
CROSS JOIN LATERAL (
    VALUES
        (0, 120::NUMERIC),
        (1, 180::NUMERIC)
) AS t(term_index, term_value)
WHERE d.recurrence_name = 'inventory_with_campaign_effect';

-- Campaign forcing is non-zero only every fourth period.
INSERT INTO recurrence_forcing
(recurrence_id, term_index, forcing_value)
SELECT
    d.recurrence_id,
    n,
    CASE WHEN n % 4 = 0 THEN 30 ELSE 0 END
FROM recurrence_definition d
CROSS JOIN generate_series(2, 12) AS n
WHERE d.recurrence_name = 'inventory_with_campaign_effect';

-- ---------------------------------------------------------------------------
-- Inspect the mathematical definitions
-- ---------------------------------------------------------------------------

SELECT
    d.recurrence_name,
    d.recurrence_type,
    d.recurrence_order,
    c.lag,
    c.coefficient
FROM recurrence_definition d
JOIN recurrence_coefficient c
    ON c.recurrence_id = d.recurrence_id
ORDER BY
    d.recurrence_name,
    c.lag;

SELECT
    d.recurrence_name,
    i.term_index,
    i.term_value
FROM recurrence_definition d
JOIN recurrence_initial_term i
    ON i.recurrence_id = d.recurrence_id
ORDER BY
    d.recurrence_name,
    i.term_index;

-- ---------------------------------------------------------------------------
-- Recursive CTE: Fibonacci
-- ---------------------------------------------------------------------------

WITH RECURSIVE fibonacci_sequence AS (
    SELECT
        i.term_index,
        i.term_value
    FROM recurrence_initial_term i
    JOIN recurrence_definition d
        ON d.recurrence_id = i.recurrence_id
    WHERE d.recurrence_name = 'fibonacci'
      AND i.term_index = 0

    UNION ALL

    SELECT
        fs.term_index + 1,
        fs.term_value +
            COALESCE(
                (
                    SELECT i2.term_value
                    FROM recurrence_initial_term i2
                    JOIN recurrence_definition d2
                        ON d2.recurrence_id = i2.recurrence_id
                    WHERE d2.recurrence_name = 'fibonacci'
                      AND i2.term_index = fs.term_index - 1
                ),
                1
            )
    FROM fibonacci_sequence fs
    WHERE fs.term_index < 1
)
SELECT *
FROM fibonacci_sequence
ORDER BY term_index;

-- The previous CTE is intentionally limited because a generic recursive
-- relation is easier to express using a state containing the required
-- historical terms. The following CTE demonstrates that state explicitly.

WITH RECURSIVE fibonacci_state AS (
    SELECT
        1::INTEGER AS n,
        0::NUMERIC AS previous,
        1::NUMERIC AS current

    UNION ALL

    SELECT
        n + 1,
        current,
        previous + current
    FROM fibonacci_state
    WHERE n < 15
)
SELECT
    n AS term_index,
    previous AS fibonacci_value
FROM fibonacci_state
ORDER BY n;

-- ---------------------------------------------------------------------------
-- Recursive CTE: first-order non-homogeneous recurrence
-- ---------------------------------------------------------------------------

WITH RECURSIVE growth_sequence AS (
    SELECT
        0::INTEGER AS term_index,
        1::NUMERIC AS term_value

    UNION ALL

    SELECT
        gs.term_index + 1,
        2 * gs.term_value
            + (gs.term_index + 1)::NUMERIC
    FROM growth_sequence gs
    WHERE gs.term_index < 10
)
SELECT *
FROM growth_sequence
ORDER BY term_index;

-- ---------------------------------------------------------------------------
-- Recursive CTE: second-order non-homogeneous inventory recurrence
-- ---------------------------------------------------------------------------

WITH RECURSIVE inventory_sequence AS (
    SELECT
        1::INTEGER AS term_index,
        120::NUMERIC AS previous_value,
        180::NUMERIC AS current_value

    UNION ALL

    SELECT
        s.term_index + 1,
        s.current_value,
        s.previous_value
            + s.current_value
            + CASE
                WHEN (s.term_index + 1) % 4 = 0
                THEN 30
                ELSE 0
              END
    FROM inventory_sequence s
    WHERE s.term_index < 12
)
SELECT
    term_index,
    current_value AS demand
FROM inventory_sequence
ORDER BY term_index;

-- ---------------------------------------------------------------------------
-- Store generated terms
-- ---------------------------------------------------------------------------

INSERT INTO generated_term (
    recurrence_id,
    term_index,
    term_value
)
SELECT
    d.recurrence_id,
    s.term_index,
    s.current_value
FROM recurrence_definition d
CROSS JOIN LATERAL (
    SELECT
        term_index,
        current_value
    FROM (
        WITH RECURSIVE sequence AS (
            SELECT
                1::INTEGER AS term_index,
                120::NUMERIC AS previous_value,
                180::NUMERIC AS current_value

            UNION ALL

            SELECT
                s.term_index + 1,
                s.current_value,
                s.previous_value
                    + s.current_value
                    + CASE
                        WHEN (s.term_index + 1) % 4 = 0
                        THEN 30
                        ELSE 0
                      END
            FROM sequence s
            WHERE s.term_index < 12
        )
        SELECT *
        FROM sequence
    ) q
) s
WHERE d.recurrence_name = 'inventory_with_campaign_effect'
ON CONFLICT (recurrence_id, term_index)
DO UPDATE SET
    term_value = EXCLUDED.term_value,
    generated_at = CURRENT_TIMESTAMP;

-- ---------------------------------------------------------------------------
-- Validate stored terms against the recurrence rule
-- ---------------------------------------------------------------------------

WITH ordered_terms AS (
    SELECT
        g.recurrence_id,
        g.term_index,
        g.term_value,
        LAG(g.term_value, 1)
            OVER (
                PARTITION BY g.recurrence_id
                ORDER BY g.term_index
            ) AS previous_1,
        LAG(g.term_value, 2)
            OVER (
                PARTITION BY g.recurrence_id
                ORDER BY g.term_index
            ) AS previous_2
    FROM generated_term g
)
SELECT
    d.recurrence_name,
    o.term_index,
    o.term_value,
    o.previous_1 + o.previous_2
        + COALESCE(f.forcing_value, 0) AS expected_value,
    CASE
        WHEN o.term_value =
             o.previous_1 + o.previous_2
             + COALESCE(f.forcing_value, 0)
        THEN 'VALID'
        ELSE 'INVALID'
    END AS validation_status
FROM ordered_terms o
JOIN recurrence_definition d
    ON d.recurrence_id = o.recurrence_id
LEFT JOIN recurrence_forcing f
    ON f.recurrence_id = o.recurrence_id
   AND f.term_index = o.term_index
WHERE d.recurrence_name = 'inventory_with_campaign_effect'
  AND o.term_index >= 2
ORDER BY o.term_index;

-- ---------------------------------------------------------------------------
-- Homogeneous versus non-homogeneous comparison
-- ---------------------------------------------------------------------------

SELECT
    d.recurrence_name,
    d.recurrence_type,
    COUNT(f.term_index) AS forcing_rows,
    COALESCE(SUM(ABS(f.forcing_value)), 0) AS total_absolute_forcing
FROM recurrence_definition d
LEFT JOIN recurrence_forcing f
    ON f.recurrence_id = d.recurrence_id
GROUP BY
    d.recurrence_name,
    d.recurrence_type
ORDER BY
    d.recurrence_name;

-- ---------------------------------------------------------------------------
-- Detect missing forcing data for non-homogeneous definitions
-- ---------------------------------------------------------------------------

SELECT
    d.recurrence_name,
    n.term_index
FROM recurrence_definition d
CROSS JOIN generate_series(1, 12) AS n(term_index)
LEFT JOIN recurrence_forcing f
    ON f.recurrence_id = d.recurrence_id
   AND f.term_index = n.term_index
WHERE d.recurrence_type = 'NON_HOMOGENEOUS'
  AND f.recurrence_id IS NULL
ORDER BY
    d.recurrence_name,
    n.term_index;

-- ---------------------------------------------------------------------------
-- Transactional demonstration
-- ---------------------------------------------------------------------------

BEGIN;

INSERT INTO generated_term (
    recurrence_id,
    term_index,
    term_value
)
SELECT
    d.recurrence_id,
    13,
    999999
FROM recurrence_definition d
WHERE d.recurrence_name = 'inventory_with_campaign_effect';

-- The value is intentionally outside the expected recurrence sequence.
-- A validation query identifies it before the transaction is committed.
SELECT
    g.term_index,
    g.term_value
FROM generated_term g
JOIN recurrence_definition d
    ON d.recurrence_id = g.recurrence_id
WHERE d.recurrence_name = 'inventory_with_campaign_effect'
  AND g.term_index = 13;

ROLLBACK;

-- ---------------------------------------------------------------------------
-- View for operational inspection
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW recurrence_definition_summary AS
SELECT
    d.recurrence_id,
    d.recurrence_name,
    d.recurrence_type,
    d.recurrence_order,
    COUNT(DISTINCT c.lag) AS coefficient_count,
    COUNT(DISTINCT i.term_index) AS initial_term_count,
    COUNT(DISTINCT f.term_index) AS forcing_term_count
FROM recurrence_definition d
LEFT JOIN recurrence_coefficient c
    ON c.recurrence_id = d.recurrence_id
LEFT JOIN recurrence_initial_term i
    ON i.recurrence_id = d.recurrence_id
LEFT JOIN recurrence_forcing f
    ON f.recurrence_id = d.recurrence_id
GROUP BY
    d.recurrence_id,
    d.recurrence_name,
    d.recurrence_type,
    d.recurrence_order;

SELECT *
FROM recurrence_definition_summary
ORDER BY recurrence_name;

-- The database model deliberately keeps recurrence coefficients, initial
-- conditions, and forcing terms separate. This prevents a non-homogeneous
-- forcing term from being mistaken for a historical coefficient and makes
-- validation queries capable of checking the mathematical rule explicitly.
