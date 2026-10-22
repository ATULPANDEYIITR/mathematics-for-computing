-- Euclidean Algorithm relational case study
-- PostgreSQL 14+.
--
-- The model stores arithmetic jobs, input operands, Bézout certificates,
-- modular-inverse requests, and linear Diophantine evaluations.
-- PostgreSQL NUMERIC is used so the database does not impose an
-- unnecessary 64-bit integer limit on mathematical coefficients.

DROP VIEW IF EXISTS arithmetic_job_report;
DROP VIEW IF EXISTS bezout_certificate_report;
DROP FUNCTION IF EXISTS solve_linear_diophantine(BIGINT, BIGINT, NUMERIC);
DROP FUNCTION IF EXISTS calculate_extended_gcd(BIGINT, BIGINT);
DROP FUNCTION IF EXISTS normalize_mod(NUMERIC, NUMERIC);
DROP FUNCTION IF EXISTS touch_updated_at();
DROP TABLE IF EXISTS diophantine_requests CASCADE;
DROP TABLE IF EXISTS modular_inverse_requests CASCADE;
DROP TABLE IF EXISTS bezout_certificates CASCADE;
DROP TABLE IF EXISTS arithmetic_jobs CASCADE;

CREATE TABLE arithmetic_jobs (
    job_id BIGSERIAL PRIMARY KEY,
    job_type TEXT NOT NULL
        CHECK (job_type IN (
            'GCD',
            'EXTENDED_GCD',
            'MODULAR_INVERSE',
            'DIOPHANTINE'
        )),
    status TEXT NOT NULL DEFAULT 'PENDING'
        CHECK (status IN (
            'PENDING',
            'SUCCEEDED',
            'REJECTED'
        )),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bezout_certificates (
    certificate_id BIGSERIAL PRIMARY KEY,
    job_id BIGINT NOT NULL UNIQUE
        REFERENCES arithmetic_jobs(job_id)
        ON DELETE CASCADE,
    operand_a BIGINT NOT NULL,
    operand_b BIGINT NOT NULL,
    gcd_value BIGINT NOT NULL
        CHECK (gcd_value >= 0),
    coefficient_x NUMERIC NOT NULL,
    coefficient_y NUMERIC NOT NULL,
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT bezout_identity_holds
        CHECK (
            operand_a::NUMERIC * coefficient_x +
            operand_b::NUMERIC * coefficient_y =
            gcd_value::NUMERIC
        )
);

CREATE TABLE modular_inverse_requests (
    request_id BIGSERIAL PRIMARY KEY,
    job_id BIGINT NOT NULL UNIQUE
        REFERENCES arithmetic_jobs(job_id)
        ON DELETE CASCADE,
    value NUMERIC NOT NULL,
    modulus NUMERIC NOT NULL
        CHECK (modulus > 1),
    gcd_value NUMERIC,
    inverse_value NUMERIC,
    is_invertible BOOLEAN NOT NULL DEFAULT FALSE,
    failure_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT inverse_consistency
        CHECK (
            (
                is_invertible = TRUE
                AND gcd_value = 1
                AND inverse_value IS NOT NULL
                AND MOD(value * inverse_value, modulus) = 1
            )
            OR
            (
                is_invertible = FALSE
                AND inverse_value IS NULL
            )
        )
);

CREATE TABLE diophantine_requests (
    request_id BIGSERIAL PRIMARY KEY,
    job_id BIGINT NOT NULL UNIQUE
        REFERENCES arithmetic_jobs(job_id)
        ON DELETE CASCADE,
    coefficient_a NUMERIC NOT NULL,
    coefficient_b NUMERIC NOT NULL,
    target_c NUMERIC NOT NULL,
    gcd_value NUMERIC,
    solution_x NUMERIC,
    solution_y NUMERIC,
    solvable BOOLEAN NOT NULL DEFAULT FALSE,
    failure_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT equation_consistency
        CHECK (
            (
                solvable = TRUE
                AND solution_x IS NOT NULL
                AND solution_y IS NOT NULL
                AND gcd_value IS NOT NULL
                AND coefficient_a * solution_x +
                    coefficient_b * solution_y = target_c
            )
            OR
            (
                solvable = FALSE
                AND solution_x IS NULL
                AND solution_y IS NULL
            )
        )
);

CREATE INDEX idx_arithmetic_jobs_type_status
    ON arithmetic_jobs (job_type, status);

CREATE INDEX idx_certificates_operands
    ON bezout_certificates (operand_a, operand_b);

CREATE INDEX idx_inverse_modulus
    ON modular_inverse_requests (modulus);

CREATE INDEX idx_diophantine_solvable
    ON diophantine_requests (solvable);

CREATE OR REPLACE FUNCTION touch_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_arithmetic_jobs_updated_at
BEFORE UPDATE ON arithmetic_jobs
FOR EACH ROW
EXECUTE FUNCTION touch_updated_at();


CREATE OR REPLACE FUNCTION calculate_extended_gcd(
    input_a BIGINT,
    input_b BIGINT
)
RETURNS TABLE (
    gcd_value BIGINT,
    coefficient_x NUMERIC,
    coefficient_y NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    old_r NUMERIC := ABS(input_a);
    r NUMERIC := ABS(input_b);

    old_s NUMERIC := 1;
    s NUMERIC := 0;

    old_t NUMERIC := 0;
    t NUMERIC := 1;

    quotient NUMERIC;
    next_r NUMERIC;
    next_s NUMERIC;
    next_t NUMERIC;
BEGIN
    /*
     * The remainder recurrence is the Euclidean algorithm.
     * The s/t sequences propagate the Bézout coefficients.
     */
    WHILE r <> 0 LOOP
        quotient := TRUNC(old_r / r);

        next_r := old_r - quotient * r;
        next_s := old_s - quotient * s;
        next_t := old_t - quotient * t;

        old_r := r;
        r := next_r;

        old_s := s;
        s := next_s;

        old_t := t;
        t := next_t;
    END LOOP;

    IF input_a < 0 THEN
        old_s := -old_s;
    END IF;

    IF input_b < 0 THEN
        old_t := -old_t;
    END IF;

    gcd_value := old_r::BIGINT;
    coefficient_x := old_s;
    coefficient_y := old_t;

    RETURN NEXT;
END;
$$;


CREATE OR REPLACE FUNCTION normalize_mod(
    input_value NUMERIC,
    input_modulus NUMERIC
)
RETURNS NUMERIC
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT MOD(MOD(input_value, input_modulus) + input_modulus,
               input_modulus);
$$;


CREATE OR REPLACE FUNCTION solve_linear_diophantine(
    input_a BIGINT,
    input_b BIGINT,
    input_c NUMERIC
)
RETURNS TABLE (
    solvable BOOLEAN,
    gcd_value NUMERIC,
    solution_x NUMERIC,
    solution_y NUMERIC,
    failure_reason TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    certificate RECORD;
    multiplier NUMERIC;
BEGIN
    IF input_a = 0 AND input_b = 0 THEN
        IF input_c = 0 THEN
            solvable := TRUE;
            gcd_value := 0;
            solution_x := 0;
            solution_y := 0;
            failure_reason := NULL;
        ELSE
            solvable := FALSE;
            gcd_value := 0;
            solution_x := NULL;
            solution_y := NULL;
            failure_reason := 'Both coefficients are zero';
        END IF;

        RETURN NEXT;
        RETURN;
    END IF;

    SELECT *
    INTO certificate
    FROM calculate_extended_gcd(input_a, input_b);

    gcd_value := certificate.gcd_value;

    IF MOD(input_c, gcd_value) <> 0 THEN
        solvable := FALSE;
        solution_x := NULL;
        solution_y := NULL;
        failure_reason :=
            'gcd(a,b) does not divide c';

        RETURN NEXT;
        RETURN;
    END IF;

    multiplier := input_c / gcd_value;

    solvable := TRUE;
    solution_x :=
        certificate.coefficient_x * multiplier;
    solution_y :=
        certificate.coefficient_y * multiplier;
    failure_reason := NULL;

    RETURN NEXT;
END;
$$;


-- Successful GCD and extended-GCD job.
INSERT INTO arithmetic_jobs (job_type, status)
VALUES ('EXTENDED_GCD', 'PENDING');

WITH certificate AS (
    SELECT *
    FROM calculate_extended_gcd(1071, 462)
)
INSERT INTO bezout_certificates (
    job_id,
    operand_a,
    operand_b,
    gcd_value,
    coefficient_x,
    coefficient_y,
    verified
)
SELECT
    1,
    1071,
    462,
    gcd_value,
    coefficient_x,
    coefficient_y,
    (
        1071::NUMERIC * coefficient_x +
        462::NUMERIC * coefficient_y =
        gcd_value::NUMERIC
    )
FROM certificate;

UPDATE arithmetic_jobs
SET status = 'SUCCEEDED'
WHERE job_id = 1
  AND EXISTS (
      SELECT 1
      FROM bezout_certificates
      WHERE job_id = 1
        AND verified = TRUE
  );


-- Successful modular inverse.
INSERT INTO arithmetic_jobs (job_type, status)
VALUES ('MODULAR_INVERSE', 'PENDING');

WITH certificate AS (
    SELECT *
    FROM calculate_extended_gcd(17, 3120)
)
INSERT INTO modular_inverse_requests (
    job_id,
    value,
    modulus,
    gcd_value,
    inverse_value,
    is_invertible
)
SELECT
    2,
    17,
    3120,
    gcd_value,
    normalize_mod(coefficient_x, 3120),
    gcd_value = 1
FROM certificate;

UPDATE arithmetic_jobs
SET status = 'SUCCEEDED'
WHERE job_id = 2
  AND EXISTS (
      SELECT 1
      FROM modular_inverse_requests
      WHERE job_id = 2
        AND is_invertible = TRUE
  );


-- Failed modular inverse because 6 and 15 are not coprime.
INSERT INTO arithmetic_jobs (job_type, status)
VALUES ('MODULAR_INVERSE', 'PENDING');

WITH certificate AS (
    SELECT *
    FROM calculate_extended_gcd(6, 15)
)
INSERT INTO modular_inverse_requests (
    job_id,
    value,
    modulus,
    gcd_value,
    inverse_value,
    is_invertible,
    failure_reason
)
SELECT
    3,
    6,
    15,
    gcd_value,
    NULL,
    FALSE,
    'gcd(value, modulus) is not 1'
FROM certificate;

UPDATE arithmetic_jobs
SET status = 'REJECTED'
WHERE job_id = 3;


-- Solvable linear Diophantine equation.
INSERT INTO arithmetic_jobs (job_type, status)
VALUES ('DIOPHANTINE', 'PENDING');

INSERT INTO diophantine_requests (
    job_id,
    coefficient_a,
    coefficient_b,
    target_c,
    gcd_value,
    solution_x,
    solution_y,
    solvable
)
SELECT
    4,
    35,
    15,
    10,
    gcd_value,
    solution_x,
    solution_y,
    solvable
FROM solve_linear_diophantine(35, 15, 10);

UPDATE arithmetic_jobs
SET status = 'SUCCEEDED'
WHERE job_id = 4
  AND EXISTS (
      SELECT 1
      FROM diophantine_requests
      WHERE job_id = 4
        AND solvable = TRUE
  );


-- Unsolvable equation because gcd(6,10)=2 does not divide 7.
INSERT INTO arithmetic_jobs (job_type, status)
VALUES ('DIOPHANTINE', 'PENDING');

INSERT INTO diophantine_requests (
    job_id,
    coefficient_a,
    coefficient_b,
    target_c,
    gcd_value,
    solution_x,
    solution_y,
    solvable,
    failure_reason
)
SELECT
    5,
    6,
    10,
    7,
    gcd_value,
    solution_x,
    solution_y,
    solvable,
    failure_reason
FROM solve_linear_diophantine(6, 10, 7);

UPDATE arithmetic_jobs
SET status = 'REJECTED'
WHERE job_id = 5;


CREATE OR REPLACE VIEW bezout_certificate_report AS
SELECT
    c.certificate_id,
    c.job_id,
    c.operand_a,
    c.operand_b,
    c.gcd_value,
    c.coefficient_x,
    c.coefficient_y,
    c.operand_a::NUMERIC * c.coefficient_x +
        c.operand_b::NUMERIC * c.coefficient_y
        AS reconstructed_gcd,
    c.verified,
    j.status,
    j.created_at
FROM bezout_certificates c
JOIN arithmetic_jobs j
    ON j.job_id = c.job_id;


CREATE OR REPLACE VIEW arithmetic_job_report AS
SELECT
    j.job_id,
    j.job_type,
    j.status,
    j.created_at,
    CASE
        WHEN j.job_type = 'EXTENDED_GCD'
            THEN c.gcd_value::NUMERIC
        WHEN j.job_type = 'MODULAR_INVERSE'
            THEN m.gcd_value
        WHEN j.job_type = 'DIOPHANTINE'
            THEN d.gcd_value
        ELSE NULL
    END AS gcd_value,
    m.inverse_value,
    d.solution_x,
    d.solution_y,
    m.failure_reason AS inverse_failure_reason,
    d.failure_reason AS diophantine_failure_reason
FROM arithmetic_jobs j
LEFT JOIN bezout_certificates c
    ON c.job_id = j.job_id
LEFT JOIN modular_inverse_requests m
    ON m.job_id = j.job_id
LEFT JOIN diophantine_requests d
    ON d.job_id = j.job_id;


-- Certificate validation.
SELECT
    operand_a,
    operand_b,
    gcd_value,
    coefficient_x,
    coefficient_y,
    reconstructed_gcd,
    verified
FROM bezout_certificate_report
ORDER BY certificate_id;


-- Retrieve modular inverse and verify the congruence.
SELECT
    value,
    modulus,
    gcd_value,
    inverse_value,
    MOD(value * inverse_value, modulus) AS verification_remainder,
    is_invertible
FROM modular_inverse_requests
ORDER BY request_id;


-- Retrieve successful and failed Diophantine cases.
SELECT
    coefficient_a,
    coefficient_b,
    target_c,
    gcd_value,
    solution_x,
    solution_y,
    solvable,
    failure_reason
FROM diophantine_requests
ORDER BY request_id;


-- Aggregated operational report.
SELECT
    job_type,
    status,
    COUNT(*) AS job_count
FROM arithmetic_jobs
GROUP BY job_type, status
ORDER BY job_type, status;


-- CTE showing the Euclidean remainder chain for 1071 and 462.
WITH RECURSIVE euclidean_steps(a, b, step_number) AS (
    SELECT
        1071::BIGINT,
        462::BIGINT,
        0

    UNION ALL

    SELECT
        b,
        MOD(a, b),
        step_number + 1
    FROM euclidean_steps
    WHERE b <> 0
)
SELECT
    step_number,
    a,
    b,
    CASE
        WHEN b <> 0 THEN TRUNC(a::NUMERIC / b)
        ELSE NULL
    END AS quotient,
    CASE
        WHEN b <> 0 THEN MOD(a, b)
        ELSE NULL
    END AS remainder
FROM euclidean_steps
ORDER BY step_number;


-- Transactional demonstration.
-- The savepoint makes the invalid request reversible while preserving
-- the surrounding transaction.
BEGIN;

INSERT INTO arithmetic_jobs (job_type, status)
VALUES ('MODULAR_INVERSE', 'PENDING');

SAVEPOINT before_invalid_inverse;

INSERT INTO modular_inverse_requests (
    job_id,
    value,
    modulus,
    gcd_value,
    inverse_value,
    is_invertible,
    failure_reason
)
VALUES (
    currval('arithmetic_jobs_job_id_seq'),
    12,
    18,
    6,
    NULL,
    FALSE,
    'gcd(value, modulus) is not 1'
);

ROLLBACK TO SAVEPOINT before_invalid_inverse;

-- The failed calculation can now be recorded explicitly.
INSERT INTO modular_inverse_requests (
    job_id,
    value,
    modulus,
    gcd_value,
    inverse_value,
    is_invertible,
    failure_reason
)
VALUES (
    currval('arithmetic_jobs_job_id_seq'),
    12,
    18,
    6,
    NULL,
    FALSE,
    'gcd(value, modulus) is not 1'
);

UPDATE arithmetic_jobs
SET status = 'REJECTED'
WHERE job_id = currval('arithmetic_jobs_job_id_seq');

COMMIT;


-- Final report after transactional processing.
SELECT
    job_id,
    job_type,
    status,
    gcd_value,
    inverse_value,
    solution_x,
    solution_y
FROM arithmetic_job_report
ORDER BY job_id;
