-- Number Theory Algorithms: PostgreSQL implementation
-- The schema models modular computations, primality decisions,
-- factorization results, validation rules, and execution history.

DROP SCHEMA IF EXISTS number_theory CASCADE;
CREATE SCHEMA number_theory;

SET search_path = number_theory, public;

CREATE TYPE operation_state AS ENUM (
    'received',
    'validated',
    'executed',
    'rejected'
);

CREATE TYPE primality_state AS ENUM (
    'prime',
    'composite',
    'unknown'
);

CREATE TABLE algorithm_runs (
    run_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    operation       TEXT NOT NULL,
    state           operation_state NOT NULL DEFAULT 'received',
    input_value     NUMERIC,
    modulus         NUMERIC,
    exponent        NUMERIC,
    result_value    NUMERIC,
    error_message   TEXT,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at    TIMESTAMPTZ,
    CHECK (modulus IS NULL OR modulus > 0),
    CHECK (exponent IS NULL OR exponent >= 0)
);

CREATE TABLE prime_results (
    number_value    NUMERIC PRIMARY KEY,
    state           primality_state NOT NULL,
    tested_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    method          TEXT NOT NULL,
    CHECK (number_value >= 0)
);

CREATE TABLE prime_factors (
    number_value    NUMERIC NOT NULL,
    prime_factor    NUMERIC NOT NULL,
    exponent        INTEGER NOT NULL,
    PRIMARY KEY (number_value, prime_factor),
    CHECK (number_value > 0),
    CHECK (prime_factor > 1),
    CHECK (exponent > 0)
);

CREATE TABLE modular_requests (
    request_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    base_value      NUMERIC NOT NULL,
    exponent_value  NUMERIC NOT NULL,
    modulus_value   NUMERIC NOT NULL,
    state            operation_state NOT NULL DEFAULT 'received',
    result_value    NUMERIC,
    error_message   TEXT,
    requested_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at    TIMESTAMPTZ,
    CHECK (exponent_value >= 0),
    CHECK (modulus_value > 0)
);

CREATE INDEX idx_algorithm_runs_operation_state
    ON algorithm_runs (operation, state);

CREATE INDEX idx_prime_results_state
    ON prime_results (state);

CREATE INDEX idx_modular_requests_state
    ON modular_requests (state);

CREATE OR REPLACE FUNCTION validate_modular_request()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.modulus_value <= 0 THEN
        NEW.state := 'rejected';
        NEW.error_message := 'Modulus must be positive.';
        NEW.completed_at := CURRENT_TIMESTAMP;
    ELSIF NEW.exponent_value < 0 THEN
        NEW.state := 'rejected';
        NEW.error_message := 'Exponent must be non-negative.';
        NEW.completed_at := CURRENT_TIMESTAMP;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_modular_request
BEFORE INSERT OR UPDATE ON modular_requests
FOR EACH ROW
EXECUTE FUNCTION validate_modular_request();

CREATE OR REPLACE FUNCTION modular_power(
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
    v_result NUMERIC := 1;
    v_base   NUMERIC;
    v_exp    NUMERIC;
BEGIN
    IF p_modulus <= 0 THEN
        RAISE EXCEPTION 'Modulus must be positive';
    END IF;

    IF p_exponent < 0 OR trunc(p_exponent) <> p_exponent THEN
        RAISE EXCEPTION 'Exponent must be a non-negative integer';
    END IF;

    v_base := mod(p_base, p_modulus);
    v_exp := p_exponent;

    WHILE v_exp > 0 LOOP
        IF mod(v_exp, 2) = 1 THEN
            v_result := mod(v_result * v_base, p_modulus);
        END IF;

        v_base := mod(v_base * v_base, p_modulus);
        v_exp := trunc(v_exp / 2);
    END LOOP;

    RETURN v_result;
END;
$$;

CREATE OR REPLACE FUNCTION gcd_numeric(
    p_a NUMERIC,
    p_b NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    v_a NUMERIC := abs(p_a);
    v_b NUMERIC := abs(p_b);
    v_temp NUMERIC;
BEGIN
    WHILE v_b <> 0 LOOP
        v_temp := mod(v_a, v_b);
        v_a := v_b;
        v_b := v_temp;
    END LOOP;

    RETURN v_a;
END;
$$;

CREATE OR REPLACE FUNCTION is_prime_trial(
    p_number NUMERIC
)
RETURNS BOOLEAN
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    v_divisor NUMERIC;
BEGIN
    IF p_number < 2 OR trunc(p_number) <> p_number THEN
        RETURN FALSE;
    END IF;

    IF p_number IN (2, 3) THEN
        RETURN TRUE;
    END IF;

    IF mod(p_number, 2) = 0 THEN
        RETURN FALSE;
    END IF;

    v_divisor := 3;

    WHILE v_divisor * v_divisor <= p_number LOOP
        IF mod(p_number, v_divisor) = 0 THEN
            RETURN FALSE;
        END IF;

        v_divisor := v_divisor + 2;
    END LOOP;

    RETURN TRUE;
END;
$$;

CREATE OR REPLACE FUNCTION euler_totient(
    p_number NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    v_remaining NUMERIC := p_number;
    v_result NUMERIC := p_number;
    v_divisor NUMERIC := 2;
BEGIN
    IF p_number <= 0 OR trunc(p_number) <> p_number THEN
        RAISE EXCEPTION 'Totient requires a positive integer';
    END IF;

    WHILE v_divisor * v_divisor <= v_remaining LOOP
        IF mod(v_remaining, v_divisor) = 0 THEN
            v_result := v_result - trunc(v_result / v_divisor);

            WHILE mod(v_remaining, v_divisor) = 0 LOOP
                v_remaining := v_remaining / v_divisor;
            END LOOP;
        END IF;

        IF v_divisor = 2 THEN
            v_divisor := 3;
        ELSE
            v_divisor := v_divisor + 2;
        END IF;
    END LOOP;

    IF v_remaining > 1 THEN
        v_result := v_result - trunc(v_result / v_remaining);
    END IF;

    RETURN v_result;
END;
$$;

CREATE OR REPLACE FUNCTION record_modular_request_result(
    p_request_id BIGINT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_request modular_requests%ROWTYPE;
BEGIN
    SELECT *
    INTO v_request
    FROM modular_requests
    WHERE request_id = p_request_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Request % does not exist', p_request_id;
    END IF;

    IF v_request.state = 'rejected' THEN
        RETURN;
    END IF;

    UPDATE modular_requests
    SET state = 'validated'
    WHERE request_id = p_request_id;

    UPDATE modular_requests
    SET result_value = modular_power(
            v_request.base_value,
            v_request.exponent_value,
            v_request.modulus_value
        ),
        state = 'executed',
        completed_at = CURRENT_TIMESTAMP,
        error_message = NULL
    WHERE request_id = p_request_id;
END;
$$;

CREATE OR REPLACE VIEW modular_request_report AS
SELECT
    request_id,
    base_value,
    exponent_value,
    modulus_value,
    state,
    result_value,
    error_message,
    requested_at,
    completed_at,
    CASE
        WHEN state = 'executed' THEN
            'eligible for downstream use'
        WHEN state = 'rejected' THEN
            'requires correction'
        ELSE
            'processing'
    END AS workflow_status
FROM modular_requests;

-- Representative modular requests.
INSERT INTO modular_requests (
    base_value,
    exponent_value,
    modulus_value
)
VALUES
    (3, 100, 13),
    (7, 0, 26),
    (2, 63, 1000000007),
    (5, -1, 17);

-- Process valid requests transactionally.
BEGIN;

SELECT record_modular_request_result(1);
SELECT record_modular_request_result(2);
SELECT record_modular_request_result(3);
SELECT record_modular_request_result(4);

COMMIT;

-- Prime classification records.
INSERT INTO prime_results (number_value, state, method)
VALUES
    (2, 'prime', 'trial division'),
    (17, 'prime', 'trial division'),
    (97, 'prime', 'trial division'),
    (100, 'composite', 'trial division'),
    (104729, 'prime', 'trial division'),
    (1, 'composite', 'trial division');

-- Factorization for 360 = 2^3 * 3^2 * 5.
INSERT INTO prime_factors (
    number_value,
    prime_factor,
    exponent
)
VALUES
    (360, 2, 3),
    (360, 3, 2),
    (360, 5, 1);

-- Algorithm execution history.
INSERT INTO algorithm_runs (
    operation,
    state,
    input_value,
    modulus,
    exponent,
    result_value
)
VALUES
    (
        'fast_modular_exponentiation',
        'executed',
        3,
        13,
        100,
        modular_power(3, 100, 13)
    ),
    (
        'gcd',
        'executed',
        252,
        NULL,
        NULL,
        gcd_numeric(252, 105)
    ),
    (
        'euler_totient',
        'executed',
        36,
        NULL,
        NULL,
        euler_totient(36)
    );

-- Retrieval: completed modular computations.
SELECT
    request_id,
    base_value,
    exponent_value,
    modulus_value,
    result_value
FROM modular_requests
WHERE state = 'executed'
ORDER BY request_id;

-- Validation: confirm that all executed results are valid residues.
SELECT
    request_id,
    result_value,
    modulus_value,
    result_value >= 0
        AND result_value < modulus_value AS valid_residue
FROM modular_requests
WHERE state = 'executed';

-- Aggregation: number of requests by workflow state.
SELECT
    state,
    COUNT(*) AS request_count
FROM modular_requests
GROUP BY state
ORDER BY state;

-- Evaluation: prime results by classification.
SELECT
    state,
    COUNT(*) AS count
FROM prime_results
GROUP BY state
ORDER BY state;

-- Reporting: prime factorization representation.
SELECT
    number_value,
    string_agg(
        CASE
            WHEN exponent = 1
                THEN prime_factor::TEXT
            ELSE prime_factor::TEXT || '^' || exponent::TEXT
        END,
        ' * '
        ORDER BY prime_factor
    ) AS factorization
FROM prime_factors
GROUP BY number_value;

-- Workflow state report.
SELECT *
FROM modular_request_report
ORDER BY request_id;

-- Demonstrate arithmetic functions.
SELECT
    gcd_numeric(252, 105) AS gcd_value,
    modular_power(3, 100, 13) AS modular_power_value,
    euler_totient(36) AS totient_value;

-- Demonstrate a failure without changing persistent data.
DO $$
BEGIN
    BEGIN
        PERFORM modular_power(2, 10, 0);
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Rejected invalid modular operation: %', SQLERRM;
    END;
END;
$$;

-- Verify the known mathematical invariants.
DO $$
BEGIN
    IF modular_power(3, 100, 13) <> 9 THEN
        RAISE EXCEPTION 'Fast exponentiation invariant failed';
    END IF;

    IF gcd_numeric(252, 105) <> 21 THEN
        RAISE EXCEPTION 'GCD invariant failed';
    END IF;

    IF euler_totient(36) <> 12 THEN
        RAISE EXCEPTION 'Totient invariant failed';
    END IF;
END;
$$;
