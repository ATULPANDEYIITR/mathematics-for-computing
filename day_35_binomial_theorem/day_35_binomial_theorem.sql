DROP SCHEMA IF EXISTS binomial_theorem_lab CASCADE;

CREATE SCHEMA binomial_theorem_lab;

SET search_path TO binomial_theorem_lab;

-- PostgreSQL is used because numeric, generated data relationships,
-- constraints, CTEs, views, functions, and transactional behavior provide
-- a useful relational model for symbolic expansion experiments.

CREATE TYPE calculation_mode AS ENUM (
    'FINITE',
    'GENERALIZED'
);

CREATE TYPE request_state AS ENUM (
    'RECEIVED',
    'VALIDATED',
    'PROCESSED',
    'REJECTED'
);

CREATE TYPE validation_result AS ENUM (
    'PASSED',
    'FAILED'
);

CREATE TABLE expansion_requests (
    request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    expression_label TEXT NOT NULL,
    exponent INTEGER NOT NULL,
    constant_term NUMERIC(100, 30) NOT NULL,
    x_multiplier NUMERIC(100, 30) NOT NULL,
    mode calculation_mode NOT NULL,
    series_terms INTEGER,
    state request_state NOT NULL DEFAULT 'RECEIVED',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT exponent_non_negative
        CHECK (exponent >= 0),

    CONSTRAINT generalized_terms_valid
        CHECK (
            (mode = 'FINITE' AND series_terms IS NULL)
            OR
            (
                mode = 'GENERALIZED'
                AND series_terms BETWEEN 1 AND 10000
            )
        )
);

CREATE TABLE binomial_coefficients (
    n INTEGER NOT NULL,
    k INTEGER NOT NULL,
    coefficient NUMERIC(100, 0) NOT NULL,

    PRIMARY KEY (n, k),

    CONSTRAINT coefficient_domain
        CHECK (n >= 0 AND k >= 0 AND k <= n)
);

CREATE TABLE expansion_terms (
    term_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    request_id BIGINT NOT NULL
        REFERENCES expansion_requests(request_id)
        ON DELETE CASCADE,
    power INTEGER NOT NULL,
    binomial_coefficient NUMERIC(100, 0) NOT NULL,
    term_coefficient NUMERIC(100, 30) NOT NULL,

    CONSTRAINT power_non_negative
        CHECK (power >= 0),

    CONSTRAINT term_coefficient_not_null
        CHECK (term_coefficient IS NOT NULL),

    UNIQUE (request_id, power)
);

CREATE TABLE identity_checks (
    identity_check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    identity_name TEXT NOT NULL,
    n INTEGER NOT NULL,
    k INTEGER,
    left_value NUMERIC(100, 30) NOT NULL,
    right_value NUMERIC(100, 30) NOT NULL,
    result validation_result NOT NULL,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT identity_parameters_valid
        CHECK (n >= 0 AND (k IS NULL OR k >= 0))
);

CREATE TABLE generalized_series_terms (
    request_id BIGINT NOT NULL
        REFERENCES expansion_requests(request_id)
        ON DELETE CASCADE,
    power INTEGER NOT NULL,
    generalized_coefficient NUMERIC(100, 50) NOT NULL,

    PRIMARY KEY (request_id, power),

    CONSTRAINT generalized_power_valid
        CHECK (power >= 0)
);

CREATE INDEX idx_expansion_terms_request_power
    ON expansion_terms (request_id, power);

CREATE INDEX idx_requests_state_created
    ON expansion_requests (state, created_at);

CREATE INDEX idx_identity_checks_name_result
    ON identity_checks (identity_name, result);

-- The recurrence
--   C(n,k) = C(n,k-1) * (n-k+1) / k
-- is represented directly as a PostgreSQL function.
CREATE OR REPLACE FUNCTION calculate_binomial_coefficient(
    p_n INTEGER,
    p_k INTEGER
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    effective_k INTEGER;
    current_value NUMERIC := 1;
    i INTEGER;
BEGIN
    IF p_n < 0 OR p_k < 0 THEN
        RAISE EXCEPTION 'n and k must be non-negative';
    END IF;

    IF p_k > p_n THEN
        RETURN 0;
    END IF;

    effective_k := LEAST(p_k, p_n - p_k);

    FOR i IN 1..effective_k LOOP
        current_value :=
            current_value
            * (p_n - effective_k + i)
            / i;
    END LOOP;

    RETURN current_value;
END;
$$;

-- Generate the coefficient table for commonly used finite expansions.
INSERT INTO binomial_coefficients (n, k, coefficient)
SELECT
    n,
    k,
    calculate_binomial_coefficient(n, k)
FROM generate_series(0, 30) AS n
CROSS JOIN LATERAL generate_series(0, n) AS k;

-- Register realistic expansion requests.
INSERT INTO expansion_requests (
    expression_label,
    exponent,
    constant_term,
    x_multiplier,
    mode,
    series_terms,
    state
)
VALUES
    ('(1 + x)^5', 5, 1, 1, 'FINITE', NULL, 'RECEIVED'),
    ('(2 + 3x)^4', 4, 2, 3, 'FINITE', NULL, 'RECEIVED'),
    ('(1 + x)^10 coefficient analysis', 10, 1, 1, 'FINITE', NULL, 'RECEIVED'),
    ('(1 + x)^1/2 generalized series', 0, 1, 0.25, 'GENERALIZED', 20, 'RECEIVED');

-- Finite expansion terms.
INSERT INTO expansion_terms (
    request_id,
    power,
    binomial_coefficient,
    term_coefficient
)
SELECT
    r.request_id,
    k.k,
    calculate_binomial_coefficient(r.exponent, k.k),
    calculate_binomial_coefficient(r.exponent, k.k)
        * POWER(r.constant_term, r.exponent - k.k)
        * POWER(r.x_multiplier, k.k)
FROM expansion_requests AS r
CROSS JOIN LATERAL generate_series(0, r.exponent) AS k(k)
WHERE r.mode = 'FINITE';

-- Transition requests whose finite terms were generated successfully.
UPDATE expansion_requests AS r
SET state = 'VALIDATED'
WHERE r.mode = 'FINITE'
  AND EXISTS (
      SELECT 1
      FROM expansion_terms AS t
      WHERE t.request_id = r.request_id
  );

UPDATE expansion_requests AS r
SET state = 'PROCESSED'
WHERE r.state = 'VALIDATED'
  AND r.mode = 'FINITE';

-- ---------------------------------------------------------------------------
-- Coefficient extraction
-- ---------------------------------------------------------------------------

-- The coefficient of x^k in (a + bx)^n is:
--   C(n,k) * a^(n-k) * b^k
SELECT
    calculate_binomial_coefficient(10, 4) AS binomial_coefficient,
    calculate_binomial_coefficient(10, 4)
        * POWER(1::NUMERIC, 6)
        * POWER(1::NUMERIC, 4) AS coefficient_of_x4;

SELECT
    calculate_binomial_coefficient(7, 3) AS binomial_coefficient,
    calculate_binomial_coefficient(7, 3)
        * POWER(2::NUMERIC, 4)
        * POWER(5::NUMERIC, 3) AS coefficient_of_x3;

-- ---------------------------------------------------------------------------
-- Expansion reconstruction
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW finite_expansion_report AS
SELECT
    r.request_id,
    r.expression_label,
    r.exponent,
    r.constant_term,
    r.x_multiplier,
    t.power,
    t.binomial_coefficient,
    t.term_coefficient
FROM expansion_requests AS r
JOIN expansion_terms AS t
    ON t.request_id = r.request_id
WHERE r.mode = 'FINITE';

SELECT *
FROM finite_expansion_report
ORDER BY request_id, power;

-- ---------------------------------------------------------------------------
-- Pascal identity
-- ---------------------------------------------------------------------------

INSERT INTO identity_checks (
    identity_name,
    n,
    k,
    left_value,
    right_value,
    result
)
SELECT
    'Pascal identity',
    12,
    5,
    calculate_binomial_coefficient(12, 5),
    calculate_binomial_coefficient(11, 4)
        + calculate_binomial_coefficient(11, 5),
    CASE
        WHEN calculate_binomial_coefficient(12, 5)
             =
             calculate_binomial_coefficient(11, 4)
             + calculate_binomial_coefficient(11, 5)
        THEN 'PASSED'::validation_result
        ELSE 'FAILED'::validation_result
    END;

-- ---------------------------------------------------------------------------
-- Symmetry identity
-- ---------------------------------------------------------------------------

INSERT INTO identity_checks (
    identity_name,
    n,
    k,
    left_value,
    right_value,
    result
)
SELECT
    'Symmetry identity',
    12,
    5,
    calculate_binomial_coefficient(12, 5),
    calculate_binomial_coefficient(12, 7),
    CASE
        WHEN calculate_binomial_coefficient(12, 5)
             = calculate_binomial_coefficient(12, 7)
        THEN 'PASSED'::validation_result
        ELSE 'FAILED'::validation_result
    END;

-- ---------------------------------------------------------------------------
-- Hockey-stick identity
-- ---------------------------------------------------------------------------

WITH values AS (
    SELECT
        SUM(
            calculate_binomial_coefficient(n, 5)
        ) AS left_value
    FROM generate_series(5, 12) AS n
)
INSERT INTO identity_checks (
    identity_name,
    n,
    k,
    left_value,
    right_value,
    result
)
SELECT
    'Hockey-stick identity',
    12,
    5,
    values.left_value,
    calculate_binomial_coefficient(13, 6),
    CASE
        WHEN values.left_value
             = calculate_binomial_coefficient(13, 6)
        THEN 'PASSED'::validation_result
        ELSE 'FAILED'::validation_result
    END
FROM values;

-- ---------------------------------------------------------------------------
-- Vandermonde identity
-- ---------------------------------------------------------------------------

WITH convolution AS (
    SELECT
        SUM(
            calculate_binomial_coefficient(8, k)
            * calculate_binomial_coefficient(7, 6 - k)
        ) AS left_value
    FROM generate_series(0, 6) AS k
    WHERE k <= 8
      AND 6 - k BETWEEN 0 AND 7
)
INSERT INTO identity_checks (
    identity_name,
    n,
    k,
    left_value,
    right_value,
    result
)
SELECT
    'Vandermonde identity',
    15,
    6,
    convolution.left_value,
    calculate_binomial_coefficient(15, 6),
    CASE
        WHEN convolution.left_value
             = calculate_binomial_coefficient(15, 6)
        THEN 'PASSED'::validation_result
        ELSE 'FAILED'::validation_result
    END
FROM convolution;

SELECT
    identity_name,
    n,
    k,
    result,
    left_value,
    right_value
FROM identity_checks
ORDER BY identity_check_id;

-- ---------------------------------------------------------------------------
-- Coefficient-sum identity
-- ---------------------------------------------------------------------------

-- Evaluating (1+x)^n at x=1 gives:
--   sum C(n,k) = 2^n
SELECT
    12 AS n,
    SUM(coefficient) AS coefficient_sum,
    POWER(2::NUMERIC, 12) AS expected_sum,
    SUM(coefficient) = POWER(2::NUMERIC, 12) AS identity_holds
FROM binomial_coefficients
WHERE n = 12;

-- Evaluating at x=-1 gives:
--   sum (-1)^k C(n,k) = 0 for n > 0
SELECT
    12 AS n,
    SUM(
        CASE
            WHEN k % 2 = 0 THEN coefficient
            ELSE -coefficient
        END
    ) AS alternating_sum
FROM binomial_coefficients
WHERE n = 12;

-- ---------------------------------------------------------------------------
-- Combinatorial application
-- ---------------------------------------------------------------------------

-- Choosing exactly five positions for ones among twelve positions:
-- C(12,5).
SELECT
    calculate_binomial_coefficient(12, 5)
        AS binary_strings_with_exactly_five_ones;

-- ---------------------------------------------------------------------------
-- Binomial probability
-- ---------------------------------------------------------------------------

-- P(X=k) = C(n,k) p^k (1-p)^(n-k)
WITH parameters AS (
    SELECT
        10::INTEGER AS n,
        6::INTEGER AS k,
        0.40::NUMERIC AS p
)
SELECT
    n,
    k,
    p,
    calculate_binomial_coefficient(n, k)
        * POWER(p, k)
        * POWER(1 - p, n - k)
        AS probability
FROM parameters;

-- The entire distribution should sum to 1.
WITH parameters AS (
    SELECT
        10::INTEGER AS n,
        0.40::NUMERIC AS p
),
distribution AS (
    SELECT
        k,
        calculate_binomial_coefficient(
            parameters.n,
            k
        )
        * POWER(parameters.p, k)
        * POWER(1 - parameters.p, parameters.n - k)
        AS probability
    FROM parameters
    CROSS JOIN LATERAL generate_series(0, parameters.n) AS k
)
SELECT
    SUM(probability) AS total_probability,
    ABS(SUM(probability) - 1) < 0.000000000001
        AS distribution_is_normalized
FROM distribution;

-- ---------------------------------------------------------------------------
-- Generalized binomial coefficients
-- ---------------------------------------------------------------------------

-- For alpha = 1/2:
-- C(alpha,k) =
-- alpha(alpha-1)...(alpha-k+1) / k!
--
-- PostgreSQL NUMERIC is used because the generalized coefficients are
-- rational/decimal values rather than arbitrary-size integer coefficients.
CREATE OR REPLACE FUNCTION generalized_binomial_coefficient(
    p_alpha NUMERIC,
    p_k INTEGER
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    result NUMERIC := 1;
    i INTEGER;
BEGIN
    IF p_k < 0 THEN
        RAISE EXCEPTION 'k must be non-negative';
    END IF;

    IF p_k = 0 THEN
        RETURN 1;
    END IF;

    FOR i IN 0..p_k - 1 LOOP
        result :=
            result
            * (p_alpha - i)
            / (i + 1);
    END LOOP;

    RETURN result;
END;
$$;

INSERT INTO generalized_series_terms (
    request_id,
    power,
    generalized_coefficient
)
SELECT
    r.request_id,
    k.k,
    generalized_binomial_coefficient(0.5, k.k)
FROM expansion_requests AS r
CROSS JOIN LATERAL generate_series(
    0,
    COALESCE(r.series_terms, 0) - 1
) AS k(k)
WHERE r.mode = 'GENERALIZED';

-- Generalized expansion of (1+x)^(1/2) evaluated at x=0.25.
WITH series AS (
    SELECT
        SUM(
            generalized_coefficient
            * POWER(0.25::NUMERIC, power)
        ) AS approximation
    FROM generalized_series_terms
    WHERE request_id = (
        SELECT request_id
        FROM expansion_requests
        WHERE mode = 'GENERALIZED'
        ORDER BY request_id
        LIMIT 1
    )
)
SELECT
    approximation,
    SQRT(1.25::NUMERIC) AS reference_value,
    approximation - SQRT(1.25::NUMERIC) AS approximation_error
FROM series;

-- ---------------------------------------------------------------------------
-- Transactional integrity example
-- ---------------------------------------------------------------------------

BEGIN;

INSERT INTO expansion_requests (
    expression_label,
    exponent,
    constant_term,
    x_multiplier,
    mode,
    series_terms,
    state
)
VALUES (
    '(3 + 2x)^3 transactional request',
    3,
    3,
    2,
    'FINITE',
    NULL,
    'RECEIVED'
);

WITH request AS (
    SELECT request_id, exponent, constant_term, x_multiplier
    FROM expansion_requests
    WHERE expression_label = '(3 + 2x)^3 transactional request'
)
INSERT INTO expansion_terms (
    request_id,
    power,
    binomial_coefficient,
    term_coefficient
)
SELECT
    request.request_id,
    k.k,
    calculate_binomial_coefficient(request.exponent, k.k),
    calculate_binomial_coefficient(request.exponent, k.k)
        * POWER(request.constant_term, request.exponent - k.k)
        * POWER(request.x_multiplier, k.k)
FROM request
CROSS JOIN LATERAL generate_series(0, request.exponent) AS k(k);

UPDATE expansion_requests
SET state = 'PROCESSED'
WHERE expression_label = '(3 + 2x)^3 transactional request';

COMMIT;

SELECT
    r.expression_label,
    r.state,
    COUNT(t.term_id) AS generated_terms
FROM expansion_requests AS r
LEFT JOIN expansion_terms AS t
    ON t.request_id = r.request_id
WHERE r.expression_label = '(3 + 2x)^3 transactional request'
GROUP BY r.expression_label, r.state;

-- ---------------------------------------------------------------------------
-- Invalid-state exposure
-- ---------------------------------------------------------------------------

-- This query identifies any finite request whose term count does not equal
-- exponent + 1. A correct finite expansion must contain exactly one term for
-- each power from 0 through n.
SELECT
    r.request_id,
    r.expression_label,
    r.exponent,
    COUNT(t.term_id) AS actual_term_count,
    r.exponent + 1 AS expected_term_count
FROM expansion_requests AS r
LEFT JOIN expansion_terms AS t
    ON t.request_id = r.request_id
WHERE r.mode = 'FINITE'
GROUP BY
    r.request_id,
    r.expression_label,
    r.exponent
HAVING COUNT(t.term_id) <> r.exponent + 1;

-- ---------------------------------------------------------------------------
-- Performance-oriented query
-- ---------------------------------------------------------------------------

-- The composite index on (request_id, power) supports ordered retrieval of
-- terms belonging to one expansion without scanning unrelated requests.
EXPLAIN
SELECT
    power,
    term_coefficient
FROM expansion_terms
WHERE request_id = 2
ORDER BY power;

-- ---------------------------------------------------------------------------
-- Governance-style final report
-- ---------------------------------------------------------------------------

SELECT
    r.request_id,
    r.expression_label,
    r.mode,
    r.state,
    COUNT(t.term_id) AS finite_term_count
FROM expansion_requests AS r
LEFT JOIN expansion_terms AS t
    ON t.request_id = r.request_id
GROUP BY
    r.request_id,
    r.expression_label,
    r.mode,
    r.state
ORDER BY r.request_id;
