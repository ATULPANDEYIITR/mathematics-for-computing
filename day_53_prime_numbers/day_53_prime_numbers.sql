DROP SCHEMA IF EXISTS prime_lab CASCADE;
CREATE SCHEMA prime_lab;
SET search_path = prime_lab;

-- The schema stores integers and their factorizations separately so that
-- prime identity, exponent counts, and distribution observations remain
-- relationally queryable.

CREATE TABLE prime_numbers (
    value bigint PRIMARY KEY,
    CONSTRAINT prime_value_positive CHECK (value >= 2)
);

CREATE TABLE factorizations (
    number_value bigint PRIMARY KEY
        REFERENCES prime_numbers(value) ON DELETE CASCADE,
    verified boolean NOT NULL DEFAULT false
);

CREATE TABLE factor_components (
    number_value bigint NOT NULL
        REFERENCES factorizations(number_value) ON DELETE CASCADE,
    prime_value bigint NOT NULL
        REFERENCES prime_numbers(value),
    exponent integer NOT NULL,
    PRIMARY KEY (number_value, prime_value),
    CONSTRAINT positive_exponent CHECK (exponent > 0)
);

CREATE TABLE prime_distribution_runs (
    run_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    upper_bound bigint NOT NULL,
    prime_count bigint NOT NULL,
    empirical_density numeric(20,12) NOT NULL,
    logarithmic_estimate numeric(20,12) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT valid_upper_bound CHECK (upper_bound >= 2),
    CONSTRAINT valid_prime_count CHECK (prime_count >= 0)
);

CREATE TABLE prime_gaps (
    run_id bigint NOT NULL
        REFERENCES prime_distribution_runs(run_id) ON DELETE CASCADE,
    lower_prime bigint NOT NULL,
    upper_prime bigint NOT NULL,
    gap bigint GENERATED ALWAYS AS (upper_prime - lower_prime) STORED,
    PRIMARY KEY (run_id, lower_prime, upper_prime),
    CONSTRAINT ordered_primes CHECK (upper_prime > lower_prime),
    CONSTRAINT positive_gap CHECK (upper_prime - lower_prime > 0)
);

CREATE INDEX idx_factor_components_prime
    ON factor_components (prime_value);

CREATE INDEX idx_prime_gaps_gap
    ON prime_gaps (gap DESC);

CREATE OR REPLACE FUNCTION is_prime(candidate bigint)
RETURNS boolean
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    divisor bigint;
BEGIN
    IF candidate < 2 THEN
        RETURN false;
    END IF;

    IF candidate = 2 THEN
        RETURN true;
    END IF;

    IF candidate % 2 = 0 THEN
        RETURN false;
    END IF;

    divisor := 3;

    WHILE divisor <= candidate / divisor LOOP
        IF candidate % divisor = 0 THEN
            RETURN false;
        END IF;

        divisor := divisor + 2;
    END LOOP;

    RETURN true;
END;
$$;

ALTER TABLE prime_numbers
    ADD CONSTRAINT prime_numbers_must_be_prime
    CHECK (is_prime(value));

CREATE OR REPLACE FUNCTION factorize_number(target bigint)
RETURNS TABLE (
    prime_value bigint,
    exponent integer
)
LANGUAGE plpgsql
AS $$
DECLARE
    remaining bigint := target;
    divisor bigint;
    current_exponent integer;
BEGIN
    IF target < 2 THEN
        RAISE EXCEPTION 'Factorization requires a value >= 2';
    END IF;

    WHILE remaining % 2 = 0 LOOP
        current_exponent := COALESCE(current_exponent, 0) + 1;
        remaining := remaining / 2;
    END LOOP;

    IF current_exponent IS NOT NULL THEN
        prime_value := 2;
        exponent := current_exponent;
        RETURN NEXT;
    END IF;

    divisor := 3;

    WHILE divisor <= remaining / divisor LOOP
        current_exponent := 0;

        WHILE remaining % divisor = 0 LOOP
            current_exponent := current_exponent + 1;
            remaining := remaining / divisor;
        END LOOP;

        IF current_exponent > 0 THEN
            prime_value := divisor;
            exponent := current_exponent;
            RETURN NEXT;
        END IF;

        divisor := divisor + 2;
    END LOOP;

    IF remaining > 1 THEN
        prime_value := remaining;
        exponent := 1;
        RETURN NEXT;
    END IF;
END;
$$;

CREATE OR REPLACE FUNCTION validate_factorization(target bigint)
RETURNS boolean
LANGUAGE plpgsql
AS $$
DECLARE
    reconstructed numeric := 1;
    component record;
BEGIN
    IF target < 2 THEN
        RETURN false;
    END IF;

    FOR component IN
        SELECT prime_value, exponent
        FROM factor_components
        WHERE number_value = target
    LOOP
        IF NOT is_prime(component.prime_value)
           OR component.exponent <= 0 THEN
            RETURN false;
        END IF;

        reconstructed :=
            reconstructed *
            power(component.prime_value::numeric, component.exponent);
    END LOOP;

    RETURN reconstructed = target;
END;
$$;

CREATE OR REPLACE FUNCTION verify_factorization_trigger()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE factorizations
    SET verified = validate_factorization(NEW.number_value)
    WHERE number_value = NEW.number_value;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_verify_factorization
AFTER INSERT OR UPDATE OR DELETE ON factor_components
FOR EACH ROW
EXECUTE FUNCTION verify_factorization_trigger();

CREATE OR REPLACE FUNCTION populate_factorization(target bigint)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    component record;
BEGIN
    IF target < 2 THEN
        RAISE EXCEPTION 'Target must be >= 2';
    END IF;

    INSERT INTO prime_numbers(value)
    SELECT target
    WHERE is_prime(target)
    ON CONFLICT DO NOTHING;

    INSERT INTO factorizations(number_value)
    VALUES (target)
    ON CONFLICT DO NOTHING;

    FOR component IN
        SELECT *
        FROM factorize_number(target)
    LOOP
        INSERT INTO prime_numbers(value)
        VALUES (component.prime_value)
        ON CONFLICT DO NOTHING;

        INSERT INTO factor_components(
            number_value,
            prime_value,
            exponent
        )
        VALUES (
            target,
            component.prime_value,
            component.exponent
        )
        ON CONFLICT (number_value, prime_value)
        DO UPDATE SET exponent = EXCLUDED.exponent;
    END LOOP;

    UPDATE factorizations
    SET verified = validate_factorization(target)
    WHERE number_value = target;
END;
$$;

-- Seed primes required by the sample factorization and distribution data.
INSERT INTO prime_numbers(value)
SELECT value
FROM generate_series(2, 200) AS values(value)
WHERE is_prime(value)
ON CONFLICT DO NOTHING;

-- Build exact factorization records for realistic composite values.
SELECT populate_factorization(84);
SELECT populate_factorization(360);
SELECT populate_factorization(9973);
SELECT populate_factorization(1000000);

-- A distribution run is generated transactionally. The temporary table
-- keeps the derived prime sequence available while gaps are calculated.
BEGIN;

CREATE TEMP TABLE current_distribution AS
SELECT value
FROM prime_numbers
WHERE value <= 100;

INSERT INTO prime_distribution_runs(
    upper_bound,
    prime_count,
    empirical_density,
    logarithmic_estimate
)
SELECT
    100,
    COUNT(*),
    COUNT(*)::numeric / 100,
    1 / ln(100::numeric)
FROM current_distribution;

WITH ordered AS (
    SELECT
        value,
        lag(value) OVER (ORDER BY value) AS previous_value
    FROM current_distribution
)
INSERT INTO prime_gaps(
    run_id,
    lower_prime,
    upper_prime
)
SELECT
    (SELECT max(run_id) FROM prime_distribution_runs),
    previous_value,
    value
FROM ordered
WHERE previous_value IS NOT NULL;

COMMIT;

-- Query factorization components and reconstruct the mathematical form.
SELECT
    f.number_value,
    string_agg(
        CASE
            WHEN c.exponent = 1
                THEN c.prime_value::text
            ELSE c.prime_value::text || '^' || c.exponent::text
        END,
        ' × ' ORDER BY c.prime_value
    ) AS factorization,
    f.verified
FROM factorizations AS f
JOIN factor_components AS c
    ON c.number_value = f.number_value
GROUP BY f.number_value, f.verified
ORDER BY f.number_value;

-- Validate every stored factor component against the primality function.
SELECT
    number_value,
    prime_value,
    exponent,
    is_prime(prime_value) AS factor_is_prime,
    validate_factorization(number_value) AS factorization_is_valid
FROM factor_components
ORDER BY number_value, prime_value;

-- Prime-counting function for the populated demonstration domain.
SELECT
    upper_bound,
    prime_count,
    empirical_density,
    logarithmic_estimate,
    prime_count::numeric /
        NULLIF(upper_bound / ln(upper_bound), 0) AS ratio_to_pnt_count_estimate
FROM prime_distribution_runs
ORDER BY upper_bound;

-- Distribution query: largest observed prime gaps.
SELECT
    run_id,
    lower_prime,
    upper_prime,
    gap
FROM prime_gaps
ORDER BY gap DESC, lower_prime
LIMIT 10;

-- CTE-based report of consecutive-prime gaps and their frequency.
WITH gap_frequency AS (
    SELECT
        gap,
        COUNT(*) AS occurrences
    FROM prime_gaps
    GROUP BY gap
),
ranked AS (
    SELECT
        gap,
        occurrences,
        dense_rank() OVER (
            ORDER BY occurrences DESC, gap
        ) AS frequency_rank
    FROM gap_frequency
)
SELECT
    gap,
    occurrences,
    frequency_rank
FROM ranked
ORDER BY frequency_rank, gap;

-- Demonstrate a failed transaction: an invalid exponent is rejected by
-- the database constraint, so no invalid component becomes persistent.
BEGIN;

DO $$
BEGIN
    BEGIN
        INSERT INTO factor_components(
            number_value,
            prime_value,
            exponent
        )
        VALUES (360, 5, 0);
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Invalid exponent rejected by CHECK constraint';
    END;
END;
$$;

ROLLBACK;

-- Demonstrate a direct integrity query for prime-number storage.
SELECT
    value,
    is_prime(value) AS verified_prime
FROM prime_numbers
WHERE value IN (2, 3, 5, 7, 11, 84, 360)
ORDER BY value;

-- The following CTE identifies prime pairs separated by the maximum
-- observed gap in the demonstration run.
WITH maximum_gap AS (
    SELECT max(gap) AS gap
    FROM prime_gaps
),
gap_pairs AS (
    SELECT
        lower_prime,
        upper_prime,
        gap
    FROM prime_gaps
)
SELECT
    lower_prime,
    upper_prime,
    gap
FROM gap_pairs
WHERE gap = (SELECT gap FROM maximum_gap)
ORDER BY lower_prime;
