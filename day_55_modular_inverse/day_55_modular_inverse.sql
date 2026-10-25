-- Modular inverses and the extended Euclidean algorithm.
-- PostgreSQL 14+ is suitable for this script.

BEGIN;

DROP SCHEMA IF EXISTS modular_arithmetic CASCADE;
CREATE SCHEMA modular_arithmetic;
SET search_path TO modular_arithmetic, public;

CREATE TABLE modulus_registry (
    modulus_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    modulus NUMERIC(1000, 0) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    CHECK (modulus > 1),
    CHECK (modulus = trunc(modulus))
);

CREATE TABLE inverse_requests (
    request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    modulus_id BIGINT NOT NULL
        REFERENCES modulus_registry(modulus_id),
    input_value NUMERIC(1000, 0) NOT NULL,
    requested_by TEXT NOT NULL,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CHECK (requested_by <> '')
);

CREATE TABLE inverse_results (
    request_id BIGINT PRIMARY KEY
        REFERENCES inverse_requests(request_id) ON DELETE CASCADE,
    gcd_value NUMERIC(1000, 0) NOT NULL,
    bezout_x NUMERIC(1000, 0) NOT NULL,
    bezout_y NUMERIC(1000, 0) NOT NULL,
    inverse_value NUMERIC(1000, 0),
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CHECK (gcd_value >= 0),
    CHECK (
        (gcd_value = 1 AND inverse_value IS NOT NULL)
        OR
        (gcd_value <> 1 AND inverse_value IS NULL)
    )
);

CREATE INDEX inverse_requests_modulus_time_idx
    ON inverse_requests (modulus_id, requested_at DESC);

-- The iterative algorithm keeps the remainders and Bezout coefficients.
-- NUMERIC avoids fixed-width integer overflow in intermediate products.
CREATE OR REPLACE FUNCTION extended_gcd(
    p_a NUMERIC,
    p_b NUMERIC
)
RETURNS TABLE (
    gcd_value NUMERIC,
    bezout_x NUMERIC,
    bezout_y NUMERIC
)
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    old_r NUMERIC := abs(p_a);
    r NUMERIC := abs(p_b);
    old_s NUMERIC := 1;
    s NUMERIC := 0;
    old_t NUMERIC := 0;
    t NUMERIC := 1;
    quotient NUMERIC;
    temp NUMERIC;
BEGIN
    IF p_a <> trunc(p_a) OR p_b <> trunc(p_b) THEN
        RAISE EXCEPTION 'Extended GCD inputs must be integers';
    END IF;

    WHILE r <> 0 LOOP
        quotient := div(old_r, r);

        temp := old_r - quotient * r;
        old_r := r;
        r := temp;

        temp := old_s - quotient * s;
        old_s := s;
        s := temp;

        temp := old_t - quotient * t;
        old_t := t;
        t := temp;
    END LOOP;

    IF p_a < 0 THEN
        old_s := -old_s;
    END IF;

    IF p_b < 0 THEN
        old_t := -old_t;
    END IF;

    gcd_value := old_r;
    bezout_x := old_s;
    bezout_y := old_t;
    RETURN NEXT;
END;
$$;

CREATE OR REPLACE FUNCTION modular_inverse(
    p_value NUMERIC,
    p_modulus NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    result RECORD;
BEGIN
    IF p_value <> trunc(p_value) THEN
        RAISE EXCEPTION 'Value must be an integer';
    END IF;

    IF p_modulus <> trunc(p_modulus) OR p_modulus <= 1 THEN
        RAISE EXCEPTION 'Modulus must be an integer greater than 1';
    END IF;

    SELECT * INTO result
    FROM extended_gcd(p_value, p_modulus);

    IF result.gcd_value <> 1 THEN
        RETURN NULL;
    END IF;

    -- PostgreSQL mod() returns a nonnegative residue for positive modulus.
    RETURN mod(result.bezout_x, p_modulus);
END;
$$;

CREATE OR REPLACE FUNCTION modular_power(
    p_base NUMERIC,
    p_exponent BIGINT,
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
    result NUMERIC := 1;
BEGIN
    IF p_base <> trunc(p_base) THEN
        RAISE EXCEPTION 'Base must be an integer';
    END IF;

    IF p_modulus <> trunc(p_modulus) OR p_modulus <= 1 THEN
        RAISE EXCEPTION 'Modulus must be an integer greater than 1';
    END IF;

    base_value := mod(p_base, p_modulus);

    IF exponent_value < 0 THEN
        base_value := modular_inverse(base_value, p_modulus);

        IF base_value IS NULL THEN
            RAISE EXCEPTION
                'Negative exponent requires an invertible base';
        END IF;

        exponent_value := -exponent_value;
    END IF;

    WHILE exponent_value > 0 LOOP
        IF mod(exponent_value, 2) = 1 THEN
            result := mod(result * base_value, p_modulus);
        END IF;

        base_value := mod(base_value * base_value, p_modulus);
        exponent_value := floor(exponent_value / 2);
    END LOOP;

    RETURN result;
END;
$$;

-- Store the mathematical result and its Bezout certificate atomically.
CREATE OR REPLACE FUNCTION evaluate_inverse_request()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    m NUMERIC;
    result RECORD;
    inverse NUMERIC;
BEGIN
    SELECT modulus INTO STRICT m
    FROM modulus_registry
    WHERE modulus_id = NEW.modulus_id;

    SELECT * INTO STRICT result
    FROM extended_gcd(NEW.input_value, m);

    inverse := CASE
        WHEN result.gcd_value = 1
        THEN mod(result.bezout_x, m)
        ELSE NULL
    END;

    INSERT INTO inverse_results (
        request_id,
        gcd_value,
        bezout_x,
        bezout_y,
        inverse_value
    )
    VALUES (
        NEW.request_id,
        result.gcd_value,
        result.bezout_x,
        result.bezout_y,
        inverse
    );

    RETURN NEW;
END;
$$;

CREATE TRIGGER inverse_request_after_insert
AFTER INSERT ON inverse_requests
FOR EACH ROW
EXECUTE FUNCTION evaluate_inverse_request();

-- This view independently checks the Bezout identity and inverse equation.
CREATE VIEW inverse_verification AS
SELECT
    req.request_id,
    req.input_value,
    reg.modulus,
    res.gcd_value,
    res.bezout_x,
    res.bezout_y,
    res.inverse_value,
    req.requested_by,
    req.requested_at,
    (
        req.input_value * res.bezout_x
        + reg.modulus * res.bezout_y
        = res.gcd_value
    ) AS bezout_identity_valid,
    (
        res.inverse_value IS NOT NULL
        AND mod(req.input_value * res.inverse_value, reg.modulus) = 1
    ) AS inverse_verified
FROM inverse_requests AS req
JOIN modulus_registry AS reg USING (modulus_id)
JOIN inverse_results AS res USING (request_id);

INSERT INTO modulus_registry (modulus, description)
VALUES
    (11, 'Small demonstration modulus'),
    (17, 'Prime modulus'),
    (15, 'Composite modulus with non-units'),
    (26, 'Composite modulus');

-- Each request receives an inverse result through the trigger.
INSERT INTO inverse_requests (
    modulus_id, input_value, requested_by
)
SELECT modulus_id, input_value, requested_by
FROM (
    VALUES
        (11::NUMERIC, 3::NUMERIC, 'alice'),
        (17::NUMERIC, 10::NUMERIC, 'bob'),
        (11::NUMERIC, -3::NUMERIC, 'carol'),
        (15::NUMERIC, 6::NUMERIC, 'dave'),
        (26::NUMERIC, 7::NUMERIC, 'erin'),
        (17::NUMERIC, 0::NUMERIC, 'frank')
) AS sample(modulus, input_value, requested_by)
JOIN modulus_registry USING (modulus);

-- Retrieval: include successful and unsuccessful inverse requests.
SELECT
    request_id,
    input_value,
    modulus,
    gcd_value,
    inverse_value,
    bezout_identity_valid,
    inverse_verified
FROM inverse_verification
ORDER BY request_id;

-- Aggregate: show invertibility rates for each modulus.
SELECT
    modulus,
    count(*) AS total_requests,
    count(*) FILTER (WHERE inverse_value IS NOT NULL) AS invertible_requests,
    count(*) FILTER (WHERE inverse_value IS NULL) AS noninvertible_requests
FROM inverse_verification
GROUP BY modulus
ORDER BY modulus;

-- Negative exponent uses the modular inverse before exponentiation.
SELECT
    modular_inverse(3, 11) AS inverse_3_mod_11,
    modular_power(3, -2, 11) AS three_to_negative_two_mod_11,
    modular_power(2, 10, 17) AS two_to_ten_mod_17;

-- Validate a Bezout certificate for gcd(30, 18) = 6.
SELECT
    g.gcd_value,
    g.bezout_x,
    g.bezout_y,
    30 * g.bezout_x + 18 * g.bezout_y AS reconstructed_value
FROM extended_gcd(30, 18) AS g;

-- Demonstrate transactional rollback: the failed insert leaves no request.
DO $$
DECLARE
    selected_modulus_id BIGINT;
    failed_request_id BIGINT;
BEGIN
    SELECT modulus_id INTO STRICT selected_modulus_id
    FROM modulus_registry
    WHERE modulus = 11;

    BEGIN
        INSERT INTO inverse_requests (
            modulus_id, input_value, requested_by
        )
        VALUES (selected_modulus_id, 3, 'rollback-test')
        RETURNING request_id INTO failed_request_id;

        -- The request and trigger-created result are rolled back together.
        RAISE EXCEPTION 'Intentional rollback demonstration';
    EXCEPTION
        WHEN raise_exception THEN
            RAISE NOTICE 'Request and result rolled back atomically';
    END;
END;
$$;

SELECT count(*) AS rollback_test_rows
FROM inverse_requests
WHERE requested_by = 'rollback-test';

COMMIT;
