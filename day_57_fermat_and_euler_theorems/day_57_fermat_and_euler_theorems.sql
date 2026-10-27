DROP SCHEMA IF EXISTS number_theory CASCADE;
CREATE SCHEMA number_theory;

SET search_path = number_theory, public;

CREATE TABLE number_theory.number_sets (
    number_id BIGSERIAL PRIMARY KEY,
    value BIGINT NOT NULL CHECK (value > 0),
    category TEXT NOT NULL CHECK (
        category IN ('prime', 'composite', 'unit', 'general')
    ),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (value)
);

CREATE TABLE number_theory.theorem_evaluations (
    evaluation_id BIGSERIAL PRIMARY KEY,
    number_id BIGINT NOT NULL REFERENCES number_sets(number_id),
    base_value BIGINT NOT NULL,
    theorem TEXT NOT NULL CHECK (
        theorem IN ('fermat_little', 'euler')
    ),
    phi_value BIGINT NOT NULL CHECK (phi_value > 0),
    gcd_value BIGINT NOT NULL CHECK (gcd_value > 0),
    exponent BIGINT NOT NULL CHECK (exponent >= 0),
    modular_result BIGINT NOT NULL CHECK (modular_result >= 0),
    theorem_applicable BOOLEAN NOT NULL,
    theorem_holds BOOLEAN NOT NULL,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE number_theory.modular_inverses (
    inverse_id BIGSERIAL PRIMARY KEY,
    base_value BIGINT NOT NULL,
    modulus BIGINT NOT NULL CHECK (modulus > 1),
    inverse_value BIGINT,
    invertible BOOLEAN NOT NULL,
    UNIQUE (base_value, modulus),
    CHECK (
        inverse_value IS NULL
        OR (inverse_value >= 0 AND inverse_value < modulus)
    )
);

CREATE INDEX idx_theorem_evaluations_theorem_result
    ON theorem_evaluations (theorem, theorem_holds);

CREATE INDEX idx_theorem_evaluations_number
    ON theorem_evaluations (number_id);

CREATE OR REPLACE FUNCTION number_theory.gcd_bigint(
    a BIGINT,
    b BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    x BIGINT := ABS(a);
    y BIGINT := ABS(b);
    r BIGINT;
BEGIN
    WHILE y <> 0 LOOP
        r := x % y;
        x := y;
        y := r;
    END LOOP;

    RETURN x;
END;
$$;

CREATE OR REPLACE FUNCTION number_theory.mod_pow(
    base BIGINT,
    exponent BIGINT,
    modulus BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    b BIGINT := MOD(base, modulus);
    e BIGINT := exponent;
    result BIGINT := MOD(1, modulus);
BEGIN
    IF modulus <= 0 THEN
        RAISE EXCEPTION 'Modulus must be positive';
    END IF;

    IF exponent < 0 THEN
        RAISE EXCEPTION 'Exponent must be non-negative';
    END IF;

    WHILE e > 0 LOOP
        IF MOD(e, 2) = 1 THEN
            result := MOD(result * b, modulus);
        END IF;

        b := MOD(b * b, modulus);
        e := e / 2;
    END LOOP;

    RETURN result;
END;
$$;

CREATE OR REPLACE FUNCTION number_theory.is_prime(
    n BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    divisor BIGINT;
BEGIN
    IF n < 2 THEN
        RETURN FALSE;
    END IF;

    IF n = 2 THEN
        RETURN TRUE;
    END IF;

    IF MOD(n, 2) = 0 THEN
        RETURN FALSE;
    END IF;

    divisor := 3;

    WHILE divisor <= n / divisor LOOP
        IF MOD(n, divisor) = 0 THEN
            RETURN FALSE;
        END IF;

        divisor := divisor + 2;
    END LOOP;

    RETURN TRUE;
END;
$$;

CREATE OR REPLACE FUNCTION number_theory.euler_phi(
    n BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    result BIGINT := n;
    value BIGINT := n;
    factor BIGINT := 3;
BEGIN
    IF n <= 0 THEN
        RAISE EXCEPTION 'phi(n) requires n > 0';
    END IF;

    IF MOD(value, 2) = 0 THEN
        result := result - result / 2;

        WHILE MOD(value, 2) = 0 LOOP
            value := value / 2;
        END LOOP;
    END IF;

    WHILE factor <= value / factor LOOP
        IF MOD(value, factor) = 0 THEN
            result := result - result / factor;

            WHILE MOD(value, factor) = 0 LOOP
                value := value / factor;
            END LOOP;
        END IF;

        factor := factor + 2;
    END LOOP;

    IF value > 1 THEN
        result := result - result / value;
    END IF;

    RETURN result;
END;
$$;

CREATE OR REPLACE FUNCTION number_theory.modular_inverse(
    a BIGINT,
    modulus BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    old_r BIGINT := MOD(a, modulus);
    r BIGINT := modulus;
    old_s BIGINT := 1;
    s BIGINT := 0;
    quotient BIGINT;
    next_r BIGINT;
    next_s BIGINT;
BEGIN
    IF modulus <= 1 THEN
        RAISE EXCEPTION 'Modulus must be greater than 1';
    END IF;

    WHILE r <> 0 LOOP
        quotient := old_r / r;

        next_r := old_r - quotient * r;
        old_r := r;
        r := next_r;

        next_s := old_s - quotient * s;
        old_s := s;
        s := next_s;
    END LOOP;

    IF old_r <> 1 THEN
        RETURN NULL;
    END IF;

    RETURN MOD(old_s + modulus, modulus);
END;
$$;

CREATE OR REPLACE FUNCTION number_theory.evaluate_theorem(
    p_base BIGINT,
    p_modulus BIGINT,
    p_theorem TEXT
)
RETURNS TABLE (
    theorem TEXT,
    base_value BIGINT,
    modulus BIGINT,
    phi_value BIGINT,
    gcd_value BIGINT,
    exponent BIGINT,
    modular_result BIGINT,
    applicable BOOLEAN,
    holds BOOLEAN
)
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    g BIGINT;
    p BIGINT;
    result BIGINT;
BEGIN
    IF p_modulus <= 0 THEN
        RAISE EXCEPTION 'Modulus must be positive';
    END IF;

    IF p_theorem NOT IN ('fermat_little', 'euler') THEN
        RAISE EXCEPTION 'Unsupported theorem: %', p_theorem;
    END IF;

    g := number_theory.gcd_bigint(p_base, p_modulus);

    IF p_theorem = 'fermat_little' THEN
        IF NOT number_theory.is_prime(p_modulus) THEN
            RETURN QUERY
            SELECT
                p_theorem,
                p_base,
                p_modulus,
                number_theory.euler_phi(p_modulus),
                g,
                p_modulus - 1,
                NULL::BIGINT,
                FALSE,
                FALSE;
            RETURN;
        END IF;

        IF g <> 1 THEN
            RETURN QUERY
            SELECT
                p_theorem,
                p_base,
                p_modulus,
                number_theory.euler_phi(p_modulus),
                g,
                p_modulus - 1,
                number_theory.mod_pow(
                    p_base,
                    p_modulus - 1,
                    p_modulus
                ),
                FALSE,
                FALSE;
            RETURN;
        END IF;

        p := p_modulus - 1;
    ELSE
        IF g <> 1 THEN
            RETURN QUERY
            SELECT
                p_theorem,
                p_base,
                p_modulus,
                number_theory.euler_phi(p_modulus),
                g,
                number_theory.euler_phi(p_modulus),
                NULL::BIGINT,
                FALSE,
                FALSE;
            RETURN;
        END IF;

        p := number_theory.euler_phi(p_modulus);
    END IF;

    result := number_theory.mod_pow(
        p_base,
        p,
        p_modulus
    );

    RETURN QUERY
    SELECT
        p_theorem,
        p_base,
        p_modulus,
        number_theory.euler_phi(p_modulus),
        g,
        p,
        result,
        TRUE,
        result = 1;
END;
$$;

CREATE OR REPLACE VIEW number_theory.phi_report AS
SELECT
    number_id,
    value,
    category,
    number_theory.euler_phi(value) AS phi_value,
    value - number_theory.euler_phi(value) AS non_coprime_count
FROM number_theory.number_sets;

CREATE OR REPLACE VIEW number_theory.merge_eligibility_style_report AS
SELECT
    evaluation_id,
    theorem,
    base_value,
    phi_value,
    gcd_value,
    modular_result,
    theorem_applicable,
    theorem_holds,
    CASE
        WHEN NOT theorem_applicable THEN 'NOT_APPLICABLE'
        WHEN theorem_holds THEN 'VALID'
        ELSE 'FAILED'
    END AS evaluation_state,
    evaluated_at
FROM number_theory.theorem_evaluations;

CREATE OR REPLACE FUNCTION number_theory.validate_inverse()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.invertible THEN
        IF NEW.inverse_value IS NULL THEN
            RAISE EXCEPTION
                'Invertible record requires inverse_value';
        END IF;

        IF MOD(
            NEW.base_value * NEW.inverse_value,
            NEW.modulus
        ) <> 1 THEN
            RAISE EXCEPTION
                'Stored inverse does not satisfy a*x mod m = 1';
        END IF;
    ELSE
        IF NEW.inverse_value IS NOT NULL THEN
            RAISE EXCEPTION
                'Non-invertible record cannot store an inverse';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_inverse
BEFORE INSERT OR UPDATE ON number_theory.modular_inverses
FOR EACH ROW
EXECUTE FUNCTION number_theory.validate_inverse();

INSERT INTO number_theory.number_sets (value, category)
VALUES
    (2, 'prime'),
    (5, 'prime'),
    (7, 'prime'),
    (8, 'composite'),
    (9, 'composite'),
    (10, 'composite'),
    (12, 'composite'),
    (15, 'composite'),
    (36, 'composite');

INSERT INTO number_theory.modular_inverses
    (base_value, modulus, inverse_value, invertible)
VALUES
    (3, 10, 7, TRUE),
    (7, 40, 23, TRUE),
    (11, 26, 19, TRUE),
    (6, 15, NULL, FALSE);

INSERT INTO number_theory.theorem_evaluations (
    number_id,
    base_value,
    theorem,
    phi_value,
    gcd_value,
    exponent,
    modular_result,
    theorem_applicable,
    theorem_holds
)
SELECT
    ns.number_id,
    e.base_value,
    e.theorem,
    e.phi_value,
    e.gcd_value,
    e.exponent,
    e.modular_result,
    e.applicable,
    e.holds
FROM number_theory.number_sets ns
CROSS JOIN LATERAL number_theory.evaluate_theorem(
    3,
    ns.value,
    'euler'
) e
WHERE ns.value IN (5, 8, 9, 10, 12, 15);

SELECT
    value,
    phi_value
FROM number_theory.phi_report
ORDER BY value;

SELECT
    theorem,
    COUNT(*) AS evaluations,
    COUNT(*) FILTER (WHERE theorem_holds) AS successful,
    COUNT(*) FILTER (WHERE NOT theorem_applicable) AS not_applicable
FROM number_theory.theorem_evaluations
GROUP BY theorem
ORDER BY theorem;

SELECT *
FROM number_theory.evaluate_theorem(3, 7, 'fermat_little');

SELECT *
FROM number_theory.evaluate_theorem(5, 12, 'euler');

SELECT *
FROM number_theory.evaluate_theorem(6, 12, 'euler');

SELECT
    base_value,
    modulus,
    inverse_value,
    invertible
FROM number_theory.modular_inverses
ORDER BY modulus, base_value;

WITH coprime_values AS (
    SELECT
        ns.value AS modulus,
        candidate.value AS candidate,
        number_theory.gcd_bigint(candidate.value, ns.value) AS gcd_value
    FROM number_theory.number_sets ns
    CROSS JOIN LATERAL generate_series(
        1,
        ns.value
    ) AS candidate(value)
    WHERE ns.value IN (8, 12, 15)
)
SELECT
    modulus,
    COUNT(*) FILTER (WHERE gcd_value = 1) AS coprime_count,
    MAX(number_theory.euler_phi(modulus)) AS phi_value
FROM coprime_values
GROUP BY modulus
ORDER BY modulus;

BEGIN;

INSERT INTO number_theory.modular_inverses (
    base_value,
    modulus,
    inverse_value,
    invertible
)
VALUES (
    17,
    3120,
    number_theory.modular_inverse(17, 3120),
    TRUE
)
ON CONFLICT (base_value, modulus)
DO UPDATE SET
    inverse_value = EXCLUDED.inverse_value,
    invertible = EXCLUDED.invertible;

COMMIT;

SELECT
    17 AS public_exponent,
    3120 AS phi_value,
    number_theory.modular_inverse(17, 3120) AS private_exponent;

SELECT
    number_theory.mod_pow(65, 17, 3233) AS ciphertext,
    number_theory.mod_pow(
        number_theory.mod_pow(65, 17, 3233),
        2753,
        3233
    ) AS recovered_message;
