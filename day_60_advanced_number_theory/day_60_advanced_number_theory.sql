-- ============================================================================
-- ADVANCED NUMBER THEORY
-- Quadratic Residues, Discrete Logarithms and Computational Number Theory
-- PostgreSQL 15+
--
-- Relational computation model:
--   Prime registry
--       |
--   Integer factorizations
--       |
--   Quadratic residue evaluations
--       |
--   Modular square roots
--       |
--   Discrete logarithm jobs
--       |
--   Baby-step lookup records
--       |
--   Verified mathematical results
--
-- Algorithms implemented:
--   Modular exponentiation
--   Modular multiplication
--   Extended Euclidean algorithm
--   Modular inverse
--   Legendre symbol
--   Tonelli-Shanks
--   Baby-Step Giant-Step
--
-- The SQL implementation uses BSGS for discrete logarithms.
-- Pohlig-Hellman decomposition is implemented in the Python,
-- JavaScript, C++17 and Java 17 programs.
--
-- SECURITY:
-- This database is an educational computational environment.
-- It does not provide constant-time arithmetic or certified
-- cryptographic parameter generation.
-- ============================================================================

DROP SCHEMA IF EXISTS nt_lab CASCADE;

CREATE SCHEMA nt_lab;

SET search_path TO nt_lab, public;

-- ============================================================================
-- 1. PRIME MODULUS REGISTRY
-- ============================================================================

CREATE TABLE prime_moduli (
    p                   BIGINT PRIMARY KEY,
    verification_method VARCHAR(100) NOT NULL,
    verified_by         VARCHAR(100) NOT NULL,
    verified_at         TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT prime_modulus_positive
        CHECK (p > 1),

    CONSTRAINT verification_method_nonempty
        CHECK (length(trim(verification_method)) > 0),

    CONSTRAINT verified_by_nonempty
        CHECK (length(trim(verified_by)) > 0)
);

COMMENT ON TABLE prime_moduli IS
'Prime modulus registry. Registration represents an externally verified primality assertion.';

COMMENT ON COLUMN prime_moduli.verification_method IS
'Records the method used to establish primality.';

-- ============================================================================
-- 2. PRIME FACTORIZATION MODEL
-- ============================================================================

CREATE TABLE factorizations (
    number          BIGINT PRIMARY KEY,
    is_complete     BOOLEAN NOT NULL DEFAULT FALSE,
    recorded_at     TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT factorization_number_positive
        CHECK (number > 1)
);

CREATE TABLE prime_factor_powers (
    number          BIGINT NOT NULL,
    prime           BIGINT NOT NULL,
    exponent        INTEGER NOT NULL,

    PRIMARY KEY (number, prime),

    CONSTRAINT factorization_parent_fk
        FOREIGN KEY (number)
        REFERENCES factorizations(number)
        ON DELETE CASCADE,

    CONSTRAINT factor_prime_fk
        FOREIGN KEY (prime)
        REFERENCES prime_moduli(p),

    CONSTRAINT factor_exponent_positive
        CHECK (exponent > 0)
);

COMMENT ON TABLE factorizations IS
'Stores complete or incomplete prime factorizations of integers.';

COMMENT ON TABLE prime_factor_powers IS
'Stores the prime-power terms belonging to an integer factorization.';

CREATE OR REPLACE FUNCTION check_factorization_product()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_number       BIGINT;
    v_complete     BOOLEAN;
    v_product      NUMERIC := 1;
    v_factor       RECORD;
BEGIN
    IF TG_OP = 'DELETE' THEN
        v_number := OLD.number;
    ELSE
        v_number := NEW.number;
    END IF;

    SELECT is_complete
    INTO v_complete
    FROM factorizations
    WHERE number = v_number;

    IF NOT FOUND OR NOT v_complete THEN
        RETURN NULL;
    END IF;

    FOR v_factor IN
        SELECT prime, exponent
        FROM prime_factor_powers
        WHERE number = v_number
    LOOP
        v_product := v_product *
            power(v_factor.prime::NUMERIC, v_factor.exponent);
    END LOOP;

    IF v_product <> v_number::NUMERIC THEN
        RAISE EXCEPTION
            'Invalid factorization for %. Product is %.',
            v_number,
            v_product;
    END IF;

    RETURN NULL;
END;
$$;

-- Deferred validation allows factorization and factor rows
-- to be inserted within one transaction.
CREATE CONSTRAINT TRIGGER factorization_product_parent_check
AFTER INSERT OR UPDATE ON factorizations
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION check_factorization_product();

CREATE CONSTRAINT TRIGGER factorization_product_child_check
AFTER INSERT OR UPDATE OR DELETE ON prime_factor_powers
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION check_factorization_product();

-- ============================================================================
-- 3. MODULAR ARITHMETIC
-- ============================================================================

CREATE OR REPLACE FUNCTION mod_multiply(
    p_a BIGINT,
    p_b BIGINT,
    p_modulus BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    v_result NUMERIC;
BEGIN
    IF p_modulus <= 1 THEN
        RAISE EXCEPTION 'Modulus must exceed one.';
    END IF;

    -- NUMERIC prevents overflow in a*b for BIGINT operands.
    v_result := mod(
        p_a::NUMERIC * p_b::NUMERIC,
        p_modulus::NUMERIC
    );

    RETURN v_result::BIGINT;
END;
$$;


CREATE OR REPLACE FUNCTION mod_pow(
    p_base BIGINT,
    p_exponent BIGINT,
    p_modulus BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    v_result NUMERIC := 1;
    v_base NUMERIC;
    v_exponent BIGINT;
    v_modulus NUMERIC;
BEGIN
    IF p_modulus <= 1 THEN
        RAISE EXCEPTION 'Modulus must exceed one.';
    END IF;

    IF p_exponent < 0 THEN
        RAISE EXCEPTION 'Exponent cannot be negative.';
    END IF;

    v_modulus := p_modulus::NUMERIC;

    v_base := mod(
        p_base::NUMERIC,
        v_modulus
    );

    v_exponent := p_exponent;

    v_result := mod(1, v_modulus);

    -- Binary exponentiation: O(log exponent).
    WHILE v_exponent > 0 LOOP

        IF v_exponent % 2 = 1 THEN
            v_result := mod(
                v_result * v_base,
                v_modulus
            );
        END IF;

        v_base := mod(
            v_base * v_base,
            v_modulus
        );

        v_exponent := v_exponent / 2;
    END LOOP;

    RETURN v_result::BIGINT;
END;
$$;


CREATE OR REPLACE FUNCTION modular_inverse(
    p_value BIGINT,
    p_modulus BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    v_old_r NUMERIC;
    v_r NUMERIC;
    v_old_s NUMERIC := 1;
    v_s NUMERIC := 0;
    v_quotient NUMERIC;
    v_temp NUMERIC;
BEGIN
    IF p_modulus <= 1 THEN
        RAISE EXCEPTION 'Modulus must exceed one.';
    END IF;

    v_old_r := mod(
        p_value::NUMERIC,
        p_modulus::NUMERIC
    );

    v_r := p_modulus::NUMERIC;

    -- Extended Euclidean algorithm.
    WHILE v_r <> 0 LOOP
        v_quotient := trunc(v_old_r / v_r);

        v_temp := v_old_r - v_quotient * v_r;
        v_old_r := v_r;
        v_r := v_temp;

        v_temp := v_old_s - v_quotient * v_s;
        v_old_s := v_s;
        v_s := v_temp;
    END LOOP;

    IF v_old_r <> 1 THEN
        RAISE EXCEPTION
            'Inverse does not exist: gcd(%, %) = %.',
            p_value,
            p_modulus,
            v_old_r;
    END IF;

    RETURN mod(
        v_old_s,
        p_modulus::NUMERIC
    )::BIGINT;
END;
$$;


-- ============================================================================
-- 4. LEGENDRE SYMBOL AND QUADRATIC RESIDUE ANALYSIS
-- ============================================================================

CREATE OR REPLACE FUNCTION legendre_symbol(
    p_value BIGINT,
    p_prime BIGINT
)
RETURNS SMALLINT
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_result BIGINT;
BEGIN
    IF p_prime <= 2 THEN
        RAISE EXCEPTION
            'Legendre symbol requires an odd prime.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM prime_moduli
        WHERE p = p_prime
    ) THEN
        RAISE EXCEPTION
            'Prime modulus % is not registered.',
            p_prime;
    END IF;

    IF mod(p_value, p_prime) = 0 THEN
        RETURN 0;
    END IF;

    v_result := mod_pow(
        p_value,
        (p_prime - 1) / 2,
        p_prime
    );

    IF v_result = 1 THEN
        RETURN 1;
    END IF;

    IF v_result = p_prime - 1 THEN
        RETURN -1;
    END IF;

    RAISE EXCEPTION
        'Unexpected Euler criterion result.';
END;
$$;


CREATE TABLE quadratic_residue_checks (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    prime_modulus   BIGINT NOT NULL REFERENCES prime_moduli(p),
    input_value     BIGINT NOT NULL,
    symbol          SMALLINT NOT NULL,
    checked_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_legendre_symbol
        CHECK (symbol IN (-1, 0, 1)),

    UNIQUE (id, prime_modulus)
);

COMMENT ON TABLE quadratic_residue_checks IS
'Stores evaluated quadratic-character classifications.';

CREATE OR REPLACE FUNCTION validate_residue_symbol()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.symbol := legendre_symbol(
        NEW.input_value,
        NEW.prime_modulus
    );

    RETURN NEW;
END;
$$;

CREATE TRIGGER residue_symbol_integrity
BEFORE INSERT OR UPDATE OF
    input_value,
    prime_modulus,
    symbol
ON quadratic_residue_checks
FOR EACH ROW
EXECUTE FUNCTION validate_residue_symbol();


-- ============================================================================
-- 5. TONELLI-SHANKS MODULAR SQUARE ROOTS
-- ============================================================================

CREATE OR REPLACE FUNCTION sqrt_mod_prime(
    p_value BIGINT,
    p_prime BIGINT
)
RETURNS BIGINT[]
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_a BIGINT;
    v_q BIGINT;
    v_s INTEGER := 0;
    v_z BIGINT := 2;
    v_c BIGINT;
    v_x BIGINT;
    v_t BIGINT;
    v_m INTEGER;
    v_i INTEGER;
    v_b BIGINT;
    v_b_squared BIGINT;
BEGIN
    IF p_prime = 2 THEN
        RETURN ARRAY[mod(p_value, 2)];
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM prime_moduli
        WHERE p = p_prime
    ) THEN
        RAISE EXCEPTION
            'Prime modulus is not registered.';
    END IF;

    v_a := mod(
        mod(p_value, p_prime) + p_prime,
        p_prime
    );

    IF v_a = 0 THEN
        RETURN ARRAY[0::BIGINT];
    END IF;

    IF legendre_symbol(v_a, p_prime) <> 1 THEN
        RETURN ARRAY[]::BIGINT[];
    END IF;

    -- Simplified branch when p = 3 mod 4.
    IF p_prime % 4 = 3 THEN
        v_x := mod_pow(
            v_a,
            (p_prime + 1) / 4,
            p_prime
        );

        RETURN ARRAY[
            LEAST(v_x, p_prime - v_x),
            GREATEST(v_x, p_prime - v_x)
        ]::BIGINT[];
    END IF;

    -- Decompose p-1 = q * 2^s.
    v_q := p_prime - 1;

    WHILE v_q % 2 = 0 LOOP
        v_q := v_q / 2;
        v_s := v_s + 1;
    END LOOP;

    -- Find a quadratic nonresidue.
    WHILE legendre_symbol(v_z, p_prime) <> -1 LOOP
        v_z := v_z + 1;
    END LOOP;

    v_c := mod_pow(v_z, v_q, p_prime);
    v_x := mod_pow(v_a, (v_q + 1) / 2, p_prime);
    v_t := mod_pow(v_a, v_q, p_prime);
    v_m := v_s;

    WHILE v_t <> 1 LOOP
        v_i := 1;

        v_b := mod_pow(v_t, 2, p_prime);

        WHILE v_i < v_m AND v_b <> 1 LOOP
            v_b := mod_pow(v_b, 2, p_prime);
            v_i := v_i + 1;
        END LOOP;

        IF v_i = v_m THEN
            RAISE EXCEPTION
                'Tonelli-Shanks invariant failed.';
        END IF;

        v_b := mod_pow(
            v_c,
            (1::BIGINT << (v_m - v_i - 1)),
            p_prime
        );

        v_x := mod_multiply(v_x, v_b, p_prime);

        v_b_squared := mod_pow(v_b, 2, p_prime);

        v_t := mod_multiply(
            v_t,
            v_b_squared,
            p_prime
        );

        v_c := v_b_squared;
        v_m := v_i;
    END LOOP;

    IF mod_pow(v_x, 2, p_prime) <> v_a THEN
        RAISE EXCEPTION
            'Computed modular square root failed verification.';
    END IF;

    RETURN ARRAY[
        LEAST(v_x, p_prime - v_x),
        GREATEST(v_x, p_prime - v_x)
    ]::BIGINT[];
END;
$$;


CREATE TABLE modular_roots (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    residue_check_id BIGINT NOT NULL,
    prime_modulus   BIGINT NOT NULL,
    root_value      BIGINT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT root_residue_fk
        FOREIGN KEY (residue_check_id, prime_modulus)
        REFERENCES quadratic_residue_checks(id, prime_modulus)
        ON DELETE CASCADE,

    CONSTRAINT root_nonnegative
        CHECK (root_value >= 0),

    CONSTRAINT unique_root_per_check
        UNIQUE (residue_check_id, root_value)
);

CREATE OR REPLACE FUNCTION validate_modular_root()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_input BIGINT;
BEGIN
    SELECT input_value
    INTO v_input
    FROM quadratic_residue_checks
    WHERE id = NEW.residue_check_id
      AND prime_modulus = NEW.prime_modulus;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Quadratic residue check does not exist.';
    END IF;

    IF NEW.root_value >= NEW.prime_modulus THEN
        RAISE EXCEPTION 'Root must be in the canonical residue range.';
    END IF;

    IF mod_pow(
        NEW.root_value,
        2,
        NEW.prime_modulus
    ) <> mod(
        mod(v_input, NEW.prime_modulus) +
        NEW.prime_modulus,
        NEW.prime_modulus
    ) THEN
        RAISE EXCEPTION
            'Root % does not satisfy the modular equation.',
            NEW.root_value;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER modular_root_integrity
BEFORE INSERT OR UPDATE ON modular_roots
FOR EACH ROW
EXECUTE FUNCTION validate_modular_root();


CREATE OR REPLACE FUNCTION record_quadratic_residue(
    p_value BIGINT,
    p_prime BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_check_id BIGINT;
    v_roots BIGINT[];
    v_root BIGINT;
BEGIN
    INSERT INTO quadratic_residue_checks (
        prime_modulus,
        input_value,
        symbol
    )
    VALUES (
        p_prime,
        p_value,
        0
    )
    RETURNING id INTO v_check_id;

    v_roots := sqrt_mod_prime(p_value, p_prime);

    FOREACH v_root IN ARRAY v_roots LOOP
        INSERT INTO modular_roots (
            residue_check_id,
            prime_modulus,
            root_value
        )
        VALUES (
            v_check_id,
            p_prime,
            v_root
        );
    END LOOP;

    RETURN v_check_id;
END;
$$;


-- ============================================================================
-- 6. DISCRETE LOGARITHM JOBS
-- ============================================================================

CREATE TABLE discrete_log_jobs (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    prime_modulus       BIGINT NOT NULL REFERENCES prime_moduli(p),
    base_value          BIGINT NOT NULL,
    target_value        BIGINT NOT NULL,
    group_order         BIGINT NOT NULL,
    requested_by        VARCHAR(100) NOT NULL,

    status              VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    algorithm           VARCHAR(50) NOT NULL DEFAULT 'BABY_STEP_GIANT_STEP',

    result_exponent     BIGINT,
    error_message       TEXT,

    max_baby_steps      BIGINT NOT NULL DEFAULT 100000,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at        TIMESTAMPTZ,

    CONSTRAINT valid_group_order
        CHECK (group_order > 1),

    CONSTRAINT base_in_field
        CHECK (
            base_value >= 0
            AND base_value < prime_modulus
        ),

    CONSTRAINT target_in_field
        CHECK (
            target_value >= 0
            AND target_value < prime_modulus
        ),

    CONSTRAINT valid_baby_step_limit
        CHECK (max_baby_steps > 0),

    CONSTRAINT valid_dlog_status
        CHECK (
            status IN (
                'PENDING',
                'RUNNING',
                'SOLVED',
                'NO_SOLUTION',
                'FAILED'
            )
        ),

    CONSTRAINT valid_dlog_result
        CHECK (
            result_exponent IS NULL
            OR (
                result_exponent >= 0
                AND result_exponent < group_order
            )
        ),

    CONSTRAINT completed_job_has_result
        CHECK (
            status <> 'SOLVED'
            OR (
                result_exponent IS NOT NULL
                AND completed_at IS NOT NULL
            )
        ),

    CONSTRAINT non_solution_has_no_result
        CHECK (
            status <> 'NO_SOLUTION'
            OR result_exponent IS NULL
        )
);

COMMENT ON TABLE discrete_log_jobs IS
'Tracks the lifecycle and mathematical outcome of discrete logarithm computations.';

CREATE TABLE dlog_baby_steps (
    job_id          BIGINT NOT NULL
        REFERENCES discrete_log_jobs(id)
        ON DELETE CASCADE,

    residue_value   BIGINT NOT NULL,
    exponent_value  BIGINT NOT NULL,

    PRIMARY KEY (job_id, residue_value),

    CONSTRAINT baby_exponent_nonnegative
        CHECK (exponent_value >= 0)
);

-- Primary key provides indexed baby-step lookup by job and residue.

CREATE INDEX idx_dlog_job_queue
ON discrete_log_jobs(status, created_at)
WHERE status IN ('PENDING', 'RUNNING');

CREATE INDEX idx_residue_modulus_time
ON quadratic_residue_checks(prime_modulus, checked_at DESC);


-- ============================================================================
-- 7. DISCRETE LOGARITHM ELIGIBILITY VIEW
-- ============================================================================

CREATE OR REPLACE VIEW v_dlog_eligibility AS
SELECT
    j.id,
    j.prime_modulus,
    j.base_value,
    j.target_value,
    j.group_order,
    j.status,

    ceil(sqrt(j.group_order::NUMERIC))::BIGINT
        AS required_baby_steps,

    j.max_baby_steps,

    (
        j.status = 'PENDING'
        AND j.base_value <> 0
        AND ceil(sqrt(j.group_order::NUMERIC))
            <= j.max_baby_steps
        AND EXISTS (
            SELECT 1
            FROM factorizations f
            WHERE f.number = j.group_order
              AND f.is_complete
        )
    ) AS passes_initial_capacity_checks,

    mod_pow(
        j.target_value,
        j.group_order,
        j.prime_modulus
    ) = 1 AS target_is_in_declared_subgroup

FROM discrete_log_jobs j;


-- ============================================================================
-- 8. BABY-STEP GIANT-STEP PROCESSING PROCEDURE
-- ============================================================================

CREATE OR REPLACE PROCEDURE solve_discrete_log_job(
    p_job_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_job RECORD;

    v_factor RECORD;

    v_prime BIGINT;
    v_order BIGINT;
    v_base BIGINT;
    v_target BIGINT;

    v_baby_limit BIGINT;
    v_m BIGINT;

    v_j BIGINT := 0;
    v_i BIGINT := 0;

    v_value BIGINT;
    v_inverse_factor BIGINT;
    v_gamma BIGINT;

    v_baby_exponent BIGINT;
    v_candidate NUMERIC;

    v_found BOOLEAN := FALSE;
BEGIN
    SELECT *
    INTO v_job
    FROM discrete_log_jobs
    WHERE id = p_job_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Discrete logarithm job % does not exist.',
            p_job_id;
    END IF;

    IF v_job.status <> 'PENDING' THEN
        RAISE EXCEPTION
            'Job % cannot be executed from state %.',
            p_job_id,
            v_job.status;
    END IF;

    UPDATE discrete_log_jobs
    SET status = 'RUNNING'
    WHERE id = p_job_id;

    -- Internal exception block keeps failure reporting atomic:
    -- failed computation writes a terminal FAILED state.
    BEGIN
        SELECT p INTO v_prime
        FROM prime_moduli
        WHERE p = v_job.prime_modulus;

        v_order := v_job.group_order;
        v_base := v_job.base_value;
        v_target := v_job.target_value;
        v_baby_limit := v_job.max_baby_steps;

        IF v_base = 0 THEN
            RAISE EXCEPTION
                'Discrete logarithm base cannot be zero.';
        END IF;

        IF v_order > v_prime - 1 THEN
            RAISE EXCEPTION
                'Declared subgroup order exceeds field group order.';
        END IF;

        -- A complete factorization of the declared group order
        -- is necessary to verify that the base has exact order.
        IF NOT EXISTS (
            SELECT 1
            FROM factorizations
            WHERE number = v_order
              AND is_complete
        ) THEN
            RAISE EXCEPTION
                'A complete group-order factorization is required.';
        END IF;

        -- Verify the prime factor product.
        IF (
            SELECT COALESCE(
                product(
                    power(prime::NUMERIC, exponent)
                ),
                1
            )
            FROM prime_factor_powers
            WHERE number = v_order
        ) <> v_order::NUMERIC THEN
            RAISE EXCEPTION
                'Group-order factorization is inconsistent.';
        END IF;

        IF mod_pow(v_base, v_order, v_prime) <> 1 THEN
            RAISE EXCEPTION
                'Base does not satisfy the declared group order.';
        END IF;

        FOR v_factor IN
            SELECT prime
            FROM prime_factor_powers
            WHERE number = v_order
        LOOP
            IF mod_pow(
                v_base,
                v_order / v_factor.prime,
                v_prime
            ) = 1 THEN
                RAISE EXCEPTION
                    'Declared group order is not exact.';
            END IF;
        END LOOP;

        -- The target must belong to the subgroup generated by base.
        IF mod_pow(v_target, v_order, v_prime) <> 1 THEN
            UPDATE discrete_log_jobs
            SET
                status = 'NO_SOLUTION',
                result_exponent = NULL,
                completed_at = CURRENT_TIMESTAMP
            WHERE id = p_job_id;

            RETURN;
        END IF;

        v_m := ceil(sqrt(v_order::NUMERIC))::BIGINT;

        IF v_m > v_baby_limit THEN
            RAISE EXCEPTION
                'Required baby-step count % exceeds limit %.',
                v_m,
                v_baby_limit;
        END IF;

        DELETE FROM dlog_baby_steps
        WHERE job_id = p_job_id;

        -- Baby steps: base^j, for 0 <= j < m.
        v_value := 1;
        v_j := 0;

        WHILE v_j < v_m LOOP
            INSERT INTO dlog_baby_steps (
                job_id,
                residue_value,
                exponent_value
            )
            VALUES (
                p_job_id,
                v_value,
                v_j
            )
            ON CONFLICT (job_id, residue_value) DO NOTHING;

            v_value := mod_multiply(
                v_value,
                v_base,
                v_prime
            );

            v_j := v_j + 1;
        END LOOP;

        -- base^(-m) is the giant-step multiplier.
        v_inverse_factor := modular_inverse(
            mod_pow(v_base, v_m, v_prime),
            v_prime
        );

        v_gamma := v_target;
        v_i := 0;

        WHILE v_i <= ceil(v_order::NUMERIC / v_m) LOOP

            SELECT exponent_value
            INTO v_baby_exponent
            FROM dlog_baby_steps
            WHERE job_id = p_job_id
              AND residue_value = v_gamma;

            IF FOUND THEN
                v_candidate :=
                    v_i::NUMERIC * v_m +
                    v_baby_exponent;

                IF (
                    v_candidate < v_order
                    AND mod_pow(
                        v_base,
                        v_candidate::BIGINT,
                        v_prime
                    ) = v_target
                ) THEN
                    UPDATE discrete_log_jobs
                    SET
                        status = 'SOLVED',
                        result_exponent = v_candidate::BIGINT,
                        completed_at = CURRENT_TIMESTAMP
                    WHERE id = p_job_id;

                    v_found := TRUE;
                    EXIT;
                END IF;
            END IF;

            v_gamma := mod_multiply(
                v_gamma,
                v_inverse_factor,
                v_prime
            );

            v_i := v_i + 1;
        END LOOP;

        IF NOT v_found THEN
            UPDATE discrete_log_jobs
            SET
                status = 'NO_SOLUTION',
                result_exponent = NULL,
                completed_at = CURRENT_TIMESTAMP
            WHERE id = p_job_id;
        END IF;

    EXCEPTION WHEN OTHERS THEN

        UPDATE discrete_log_jobs
        SET
            status = 'FAILED',
            result_exponent = NULL,
            error_message = left(SQLERRM, 2000),
            completed_at = CURRENT_TIMESTAMP
        WHERE id = p_job_id;

    END;
END;
$$;


-- ============================================================================
-- 9. REPORTING VIEWS
-- ============================================================================

CREATE OR REPLACE VIEW v_quadratic_residue_report AS
SELECT
    q.id,
    q.prime_modulus,
    q.input_value,
    q.symbol,

    CASE q.symbol
        WHEN -1 THEN 'QUADRATIC_NONRESIDUE'
        WHEN 0 THEN 'ZERO'
        WHEN 1 THEN 'QUADRATIC_RESIDUE'
    END AS classification,

    COALESCE(
        array_agg(r.root_value ORDER BY r.root_value)
            FILTER (WHERE r.id IS NOT NULL),
        ARRAY[]::BIGINT[]
    ) AS square_roots,

    q.checked_at

FROM quadratic_residue_checks q

LEFT JOIN modular_roots r
    ON r.residue_check_id = q.id

GROUP BY
    q.id,
    q.prime_modulus,
    q.input_value,
    q.symbol,
    q.checked_at;


CREATE OR REPLACE VIEW v_dlog_results AS
SELECT
    j.id,
    j.prime_modulus,
    j.base_value,
    j.target_value,
    j.group_order,
    j.algorithm,
    j.status,
    j.result_exponent,
    j.requested_by,
    j.error_message,
    j.created_at,
    j.completed_at

FROM discrete_log_jobs j;


CREATE OR REPLACE VIEW v_number_theory_activity AS
SELECT
    'QUADRATIC_RESIDUE' AS operation,
    COUNT(*) AS total_records,
    COUNT(*) FILTER (WHERE symbol = 1) AS successful_residues,
    COUNT(*) FILTER (WHERE symbol = -1) AS nonresidues,
    COUNT(*) FILTER (WHERE symbol = 0) AS zero_values
FROM quadratic_residue_checks

UNION ALL

SELECT
    'DISCRETE_LOGARITHM',
    COUNT(*),
    COUNT(*) FILTER (WHERE status = 'SOLVED'),
    COUNT(*) FILTER (WHERE status = 'NO_SOLUTION'),
    COUNT(*) FILTER (WHERE status = 'FAILED')
FROM discrete_log_jobs;


-- ============================================================================
-- 10. SAMPLE DATA AND INTEGRITY TESTS
-- ============================================================================

BEGIN;

-- The registry trusts the recorded verification process.
-- Registration does not itself prove primality.
INSERT INTO prime_moduli (
    p,
    verification_method,
    verified_by
)
VALUES
    (2, 'Deterministic small-prime verification', 'number_theory_lab'),
    (509, 'Miller-Rabin and independent verification', 'number_theory_lab'),
    (1019, 'Miller-Rabin and trial verification', 'number_theory_lab');


-- 1018 = 2 * 509.
INSERT INTO factorizations (
    number,
    is_complete
)
VALUES
    (1018, FALSE);

INSERT INTO prime_factor_powers (
    number,
    prime,
    exponent
)
VALUES
    (1018, 2, 1),
    (1018, 509, 1);

UPDATE factorizations
SET is_complete = TRUE
WHERE number = 1018;


-- Quadratic residue:
-- 56^2 mod 1019 = 79.
SELECT record_quadratic_residue(
    79,
    1019
) AS residue_check_id;

-- Since 2 is a quadratic nonresidue modulo 1019,
-- its modular square-root result has no rows.
SELECT record_quadratic_residue(
    2,
    1019
) AS nonresidue_check_id;

-- The zero case has one distinct root.
SELECT record_quadratic_residue(
    0,
    1019
) AS zero_check_id;


-- Create a solvable discrete logarithm.
-- 2^137 mod 1019 is calculated within the database.
DO $$
DECLARE
    v_job_id BIGINT;
    v_target BIGINT;
BEGIN
    v_target := mod_pow(2, 137, 1019);

    INSERT INTO discrete_log_jobs (
        prime_modulus,
        base_value,
        target_value,
        group_order,
        requested_by,
        max_baby_steps
    )
    VALUES (
        1019,
        2,
        v_target,
        1018,
        'research_engineer',
        100
    )
    RETURNING id INTO v_job_id;

    CALL solve_discrete_log_job(v_job_id);
END;
$$;


-- Create an unsolvable case.
-- Zero does not belong to the multiplicative group.
DO $$
DECLARE
    v_job_id BIGINT;
BEGIN
    INSERT INTO discrete_log_jobs (
        prime_modulus,
        base_value,
        target_value,
        group_order,
        requested_by,
        max_baby_steps
    )
    VALUES (
        1019,
        2,
        0,
        1018,
        'validation_service',
        100
    )
    RETURNING id INTO v_job_id;

    CALL solve_discrete_log_job(v_job_id);
END;
$$;


-- ============================================================================
-- 11. OPERATIONAL QUERIES
-- ============================================================================

-- Prime modulus registry.
SELECT
    p,
    verification_method,
    verified_by,
    verified_at
FROM prime_moduli
ORDER BY p;


-- Prime factorization retrieval.
SELECT
    f.number,
    f.is_complete,
    pf.prime,
    pf.exponent
FROM factorizations f
JOIN prime_factor_powers pf
    ON pf.number = f.number
ORDER BY f.number, pf.prime;


-- Verify quadratic residue classifications and roots.
SELECT
    id,
    prime_modulus,
    input_value,
    symbol,
    classification,
    square_roots
FROM v_quadratic_residue_report
ORDER BY id;


-- Check arithmetic operations directly.
SELECT
    mod_pow(2, 137, 1019) AS public_value,
    legendre_symbol(79, 1019) AS residue_character,
    modular_inverse(3, 11) AS inverse_mod_11,
    sqrt_mod_prime(79, 1019) AS modular_roots;


-- Retrieve discrete logarithm job status.
SELECT *
FROM v_dlog_results
ORDER BY id;


-- Determine initial eligibility and memory requirements.
SELECT
    id,
    status,
    required_baby_steps,
    max_baby_steps,
    passes_initial_capacity_checks,
    target_is_in_declared_subgroup
FROM v_dlog_eligibility
ORDER BY id;


-- Aggregate computational activity.
SELECT
    operation,
    total_records,
    successful_residues,
    nonresidues,
    zero_values
FROM v_number_theory_activity
ORDER BY operation;


-- Inspect baby-step table size.
SELECT
    job_id,
    COUNT(*) AS stored_baby_steps,
    MIN(exponent_value) AS minimum_exponent,
    MAX(exponent_value) AS maximum_exponent
FROM dlog_baby_steps
GROUP BY job_id
ORDER BY job_id;


-- Validate the recovered discrete logarithm.
SELECT
    id,
    result_exponent,
    mod_pow(base_value, result_exponent, prime_modulus)
        AS reconstructed_target,
    target_value,
    (
        mod_pow(base_value, result_exponent, prime_modulus)
        = target_value
    ) AS verification_passed
FROM discrete_log_jobs
WHERE status = 'SOLVED';


COMMIT;


-- ============================================================================
-- 12. FAILURE-CASE DEMONSTRATIONS
-- ============================================================================
--
-- The following statements are intentionally commented because
-- executing them should raise constraint or mathematical errors.
--
-- Non-invertible number:
-- SELECT modular_inverse(6, 15);
--
-- Invalid Legendre modulus:
-- SELECT legendre_symbol(5, 15);
--
-- Unregistered prime:
-- SELECT legendre_symbol(5, 103);
--
-- Invalid modular root:
-- INSERT INTO modular_roots
-- (residue_check_id, prime_modulus, root_value)
-- VALUES (1, 1019, 5);
--
-- Invalid incomplete factorization:
-- An incomplete factorization is rejected when marked complete
-- if the product of its registered prime powers is incorrect.
--
-- Re-executing a completed job:
-- CALL solve_discrete_log_job(1);
--
-- These checks preserve mathematical and workflow integrity.
-- ============================================================================
