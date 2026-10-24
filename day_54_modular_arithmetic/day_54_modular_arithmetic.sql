-- Modular arithmetic laboratory for PostgreSQL 14 or later.
-- Models congruences, residue classes, modular operations, and audited requests.

BEGIN;

CREATE SCHEMA IF NOT EXISTS modular_lab;
SET LOCAL search_path = modular_lab, public;

CREATE TABLE IF NOT EXISTS modulus_registry (
    modulus_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    modulus NUMERIC(1000, 0) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT positive_modulus CHECK (modulus > 0),
    CONSTRAINT modulus_size CHECK (length(modulus::TEXT) <= 1000)
);

CREATE TABLE IF NOT EXISTS arithmetic_requests (
    request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    operation TEXT NOT NULL,
    left_operand NUMERIC(1000, 0) NOT NULL,
    right_operand NUMERIC(1000, 0),
    exponent NUMERIC(1000, 0),
    modulus_id BIGINT NOT NULL REFERENCES modulus_registry(modulus_id),
    status TEXT NOT NULL DEFAULT 'pending',
    result NUMERIC(1000, 0),
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,

    CONSTRAINT allowed_operation CHECK (
        operation IN ('normalize', 'congruence', 'add', 'multiply',
                      'power', 'inverse')
    ),
    CONSTRAINT required_operands CHECK (
        (operation IN ('normalize', 'inverse')
            AND right_operand IS NULL AND exponent IS NULL)
        OR
        (operation IN ('congruence', 'add', 'multiply')
            AND right_operand IS NOT NULL AND exponent IS NULL)
        OR
        (operation = 'power'
            AND right_operand IS NULL AND exponent IS NOT NULL)
    ),
    CONSTRAINT valid_status CHECK (
        status IN ('pending', 'succeeded', 'failed')
    ),
    CONSTRAINT result_state CHECK (
        (status = 'pending' AND result IS NULL AND error_message IS NULL
            AND completed_at IS NULL)
        OR
        (status = 'succeeded' AND result IS NOT NULL
            AND error_message IS NULL AND completed_at IS NOT NULL)
        OR
        (status = 'failed' AND result IS NULL
            AND error_message IS NOT NULL AND completed_at IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS arithmetic_requests_recent_idx
    ON arithmetic_requests (created_at DESC);

CREATE INDEX IF NOT EXISTS arithmetic_requests_status_idx
    ON arithmetic_requests (status, operation);

CREATE OR REPLACE FUNCTION normalize_mod(
    p_value NUMERIC,
    p_modulus NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF p_modulus <= 0 OR trunc(p_modulus) <> p_modulus THEN
        RAISE EXCEPTION 'Modulus must be a positive integer'
            USING ERRCODE = '22023';
    END IF;

    IF trunc(p_value) <> p_value THEN
        RAISE EXCEPTION 'Operand must be an integer'
            USING ERRCODE = '22023';
    END IF;

    RETURN mod(mod(p_value, p_modulus) + p_modulus, p_modulus);
END;
$$;

CREATE OR REPLACE FUNCTION gcd_integer(
    p_a NUMERIC,
    p_b NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    a NUMERIC := abs(p_a);
    b NUMERIC := abs(p_b);
    remainder_value NUMERIC;
BEGIN
    IF trunc(a) <> a OR trunc(b) <> b THEN
        RAISE EXCEPTION 'GCD operands must be integers'
            USING ERRCODE = '22023';
    END IF;

    WHILE b <> 0 LOOP
        remainder_value := mod(a, b);
        a := b;
        b := remainder_value;
    END LOOP;

    RETURN a;
END;
$$;

CREATE OR REPLACE FUNCTION inverse_mod(
    p_value NUMERIC,
    p_modulus NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    old_r NUMERIC;
    r NUMERIC;
    old_s NUMERIC := 1;
    s NUMERIC := 0;
    quotient_value NUMERIC;
    next_r NUMERIC;
    next_s NUMERIC;
    normalized NUMERIC;
BEGIN
    IF p_modulus <= 1 OR trunc(p_modulus) <> p_modulus THEN
        RAISE EXCEPTION 'Inverse requires an integer modulus greater than one'
            USING ERRCODE = '22023';
    END IF;

    normalized := normalize_mod(p_value, p_modulus);
    old_r := normalized;
    r := p_modulus;

    WHILE r <> 0 LOOP
        quotient_value := trunc(old_r / r);
        next_r := old_r - quotient_value * r;
        old_r := r;
        r := next_r;

        next_s := old_s - quotient_value * s;
        old_s := s;
        s := next_s;
    END LOOP;

    IF old_r <> 1 THEN
        RAISE EXCEPTION 'Inverse does not exist: gcd(value, modulus) = %',
            old_r USING ERRCODE = '22023';
    END IF;

    RETURN normalize_mod(old_s, p_modulus);
END;
$$;

CREATE OR REPLACE FUNCTION power_mod(
    p_base NUMERIC,
    p_exponent NUMERIC,
    p_modulus NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    base_value NUMERIC;
    exponent_value NUMERIC := p_exponent;
    result_value NUMERIC;
BEGIN
    IF p_modulus <= 0 OR trunc(p_modulus) <> p_modulus THEN
        RAISE EXCEPTION 'Modulus must be a positive integer'
            USING ERRCODE = '22023';
    END IF;

    IF trunc(p_exponent) <> p_exponent THEN
        RAISE EXCEPTION 'Exponent must be an integer'
            USING ERRCODE = '22023';
    END IF;

    base_value := normalize_mod(p_base, p_modulus);

    IF exponent_value < 0 THEN
        base_value := inverse_mod(base_value, p_modulus);
        exponent_value := -exponent_value;
    END IF;

    result_value := normalize_mod(1, p_modulus);

    -- Binary exponentiation reduces after each multiplication.
    WHILE exponent_value > 0 LOOP
        IF mod(exponent_value, 2) = 1 THEN
            result_value := normalize_mod(
                result_value * base_value, p_modulus
            );
        END IF;

        base_value := normalize_mod(
            base_value * base_value, p_modulus
        );
        exponent_value := trunc(exponent_value / 2);
    END LOOP;

    RETURN result_value;
END;
$$;

CREATE OR REPLACE FUNCTION evaluate_request(p_request_id BIGINT)
RETURNS arithmetic_requests
LANGUAGE plpgsql
AS $$
DECLARE
    request_row arithmetic_requests%ROWTYPE;
    modulus_value NUMERIC;
    calculated_result NUMERIC;
BEGIN
    -- Lock the request so two workers cannot evaluate it simultaneously.
    SELECT *
    INTO request_row
    FROM arithmetic_requests
    WHERE request_id = p_request_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Request % does not exist', p_request_id
            USING ERRCODE = 'P0002';
    END IF;

    IF request_row.status <> 'pending' THEN
        RAISE EXCEPTION 'Request % has already been processed', p_request_id
            USING ERRCODE = '55000';
    END IF;

    SELECT modulus INTO modulus_value
    FROM modulus_registry
    WHERE modulus_id = request_row.modulus_id;

    BEGIN
        CASE request_row.operation
            WHEN 'normalize' THEN
                calculated_result := normalize_mod(
                    request_row.left_operand, modulus_value
                );

            WHEN 'congruence' THEN
                calculated_result := CASE
                    WHEN normalize_mod(request_row.left_operand, modulus_value)
                       = normalize_mod(request_row.right_operand, modulus_value)
                    THEN 1 ELSE 0 END;

            WHEN 'add' THEN
                calculated_result := normalize_mod(
                    request_row.left_operand + request_row.right_operand,
                    modulus_value
                );

            WHEN 'multiply' THEN
                calculated_result := normalize_mod(
                    normalize_mod(request_row.left_operand, modulus_value)
                    * normalize_mod(request_row.right_operand, modulus_value),
                    modulus_value
                );

            WHEN 'power' THEN
                calculated_result := power_mod(
                    request_row.left_operand,
                    request_row.exponent,
                    modulus_value
                );

            WHEN 'inverse' THEN
                calculated_result := inverse_mod(
                    request_row.left_operand, modulus_value
                );
        END CASE;

        UPDATE arithmetic_requests
        SET status = 'succeeded',
            result = calculated_result,
            error_message = NULL,
            completed_at = CURRENT_TIMESTAMP
        WHERE request_id = p_request_id
        RETURNING * INTO request_row;

    EXCEPTION WHEN OTHERS THEN
        -- Record expected domain failures without aborting the whole batch.
        UPDATE arithmetic_requests
        SET status = 'failed',
            result = NULL,
            error_message = SQLERRM,
            completed_at = CURRENT_TIMESTAMP
        WHERE request_id = p_request_id
        RETURNING * INTO request_row;
    END;

    RETURN request_row;
END;
$$;

CREATE OR REPLACE VIEW request_report AS
SELECT
    r.request_id,
    r.operation,
    r.left_operand,
    r.right_operand,
    r.exponent,
    m.modulus,
    r.status,
    r.result,
    r.error_message,
    r.created_at,
    r.completed_at
FROM arithmetic_requests AS r
JOIN modulus_registry AS m USING (modulus_id);

INSERT INTO modulus_registry (modulus, description)
VALUES
    (5, 'Small residue-class examples'),
    (7, 'Congruence and exponentiation examples'),
    (11, 'Invertible residue examples'),
    (17, 'General modular arithmetic examples'),
    (9, 'Composite modulus and inverse failure')
ON CONFLICT (modulus) DO NOTHING;

-- Each request has a well-defined operation and operand shape.
INSERT INTO arithmetic_requests
    (operation, left_operand, right_operand, exponent, modulus_id)
SELECT v.operation, v.left_operand, v.right_operand, v.exponent, m.modulus_id
FROM (VALUES
    ('normalize', -17::NUMERIC, NULL::NUMERIC, NULL::NUMERIC, 5::NUMERIC),
    ('congruence', 17::NUMERIC, 2::NUMERIC, NULL::NUMERIC, 5::NUMERIC),
    ('add', -7::NUMERIC, 12::NUMERIC, NULL::NUMERIC, 5::NUMERIC),
    ('multiply', 123456::NUMERIC, 789012::NUMERIC, NULL::NUMERIC, 97::NUMERIC),
    ('power', 3::NUMERIC, NULL::NUMERIC, 100::NUMERIC, 7::NUMERIC),
    ('power', 3::NUMERIC, NULL::NUMERIC, -1::NUMERIC, 11::NUMERIC),
    ('inverse', 5::NUMERIC, NULL::NUMERIC, NULL::NUMERIC, 17::NUMERIC),
    ('inverse', 6::NUMERIC, NULL::NUMERIC, NULL::NUMERIC, 9::NUMERIC)
) AS v(operation, left_operand, right_operand, exponent, modulus)
JOIN modulus_registry AS m ON m.modulus = v.modulus;

-- A savepoint lets the demonstration retain failed requests for inspection.
DO $$
DECLARE
    request_record RECORD;
BEGIN
    FOR request_record IN
        SELECT request_id
        FROM arithmetic_requests
        WHERE status = 'pending'
        ORDER BY request_id
    LOOP
        PERFORM evaluate_request(request_record.request_id);
    END LOOP;
END;
$$;

-- Retrieval: inspect individual operations and their outcomes.
SELECT * FROM request_report ORDER BY request_id;

-- Aggregation: compare successful and failed operation counts.
SELECT operation, status, count(*) AS request_count
FROM arithmetic_requests
GROUP BY operation, status
ORDER BY operation, status;

-- Evaluation: determine which operations succeeded and expose domain errors.
SELECT request_id, operation, modulus, result, error_message
FROM request_report
WHERE status IN ('succeeded', 'failed')
ORDER BY request_id;

-- Eligibility query: a negative exponent is valid only when an inverse exists.
SELECT
    request_id,
    left_operand,
    modulus,
    gcd_integer(
        normalize_mod(left_operand, modulus),
        modulus
    ) = 1 AS inverse_exists
FROM request_report
WHERE operation IN ('inverse', 'power')
  AND (operation = 'inverse' OR exponent < 0)
ORDER BY request_id;

COMMIT;
