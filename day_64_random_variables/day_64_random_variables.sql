-- Random Variables: PostgreSQL Probability Laboratory
--
-- This script creates a relational model for discrete and continuous
-- random variables, stores distribution parameters and observations,
-- calculates PMFs, PDFs, CDFs, expectation and variance, and reports
-- empirical statistics.
--
-- The script recreates its dedicated schema. Existing objects and data
-- in random_variable_lab are removed when the script is executed.

DROP SCHEMA IF EXISTS random_variable_lab CASCADE;

CREATE SCHEMA random_variable_lab;

SET search_path TO random_variable_lab, public;

CREATE TYPE random_variable_kind AS ENUM (
    'DISCRETE',
    'CONTINUOUS'
);

CREATE TYPE continuous_family AS ENUM (
    'NORMAL',
    'UNIFORM'
);

-- ---------------------------------------------------------------------
-- 1. Distribution metadata
-- ---------------------------------------------------------------------

CREATE TABLE random_variables (
    distribution_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    variable_code VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    variable_kind random_variable_kind NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT variable_code_not_empty
        CHECK (length(trim(variable_code)) > 0),

    CONSTRAINT description_not_empty
        CHECK (length(trim(description)) > 0)
);

COMMENT ON TABLE random_variables IS
    'Metadata for discrete and continuous random variables.';

-- ---------------------------------------------------------------------
-- 2. Discrete probability mass functions
-- ---------------------------------------------------------------------

CREATE TABLE discrete_outcomes (
    distribution_id BIGINT NOT NULL
        REFERENCES random_variables(distribution_id)
        ON DELETE CASCADE,

    outcome NUMERIC(20, 8) NOT NULL,
    probability NUMERIC(20, 12) NOT NULL,

    PRIMARY KEY (distribution_id, outcome),

    CONSTRAINT probability_range
        CHECK (probability >= 0 AND probability <= 1)
);

COMMENT ON TABLE discrete_outcomes IS
    'Stores support values and their probability mass function values.';

-- Probability totals are checked at transaction commit so that a
-- complete PMF can be inserted using multiple rows in one transaction.

CREATE OR REPLACE FUNCTION validate_discrete_probability_total()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_distribution_id BIGINT;
    v_total NUMERIC;
    v_count BIGINT;
    v_old_distribution_id BIGINT;
BEGIN
    IF TG_OP = 'DELETE' THEN
        v_distribution_id := OLD.distribution_id;
    ELSE
        v_distribution_id := NEW.distribution_id;
    END IF;

    SELECT
        COALESCE(SUM(probability), 0),
        COUNT(*)
    INTO
        v_total,
        v_count
    FROM discrete_outcomes
    WHERE distribution_id = v_distribution_id;

    IF v_count = 0 OR ABS(v_total - 1.0) > 0.000000001 THEN
        RAISE EXCEPTION
            'Invalid PMF for distribution %. Row count: %, probability total: %',
            v_distribution_id,
            v_count,
            v_total;
    END IF;

    -- If an existing outcome is moved to another distribution,
    -- validate the original distribution as well.
    IF TG_OP = 'UPDATE'
       AND OLD.distribution_id <> NEW.distribution_id THEN

        v_old_distribution_id := OLD.distribution_id;

        SELECT
            COALESCE(SUM(probability), 0),
            COUNT(*)
        INTO
            v_total,
            v_count
        FROM discrete_outcomes
        WHERE distribution_id = v_old_distribution_id;

        IF v_count = 0 OR ABS(v_total - 1.0) > 0.000000001 THEN
            RAISE EXCEPTION
                'Update would invalidate original PMF for distribution %',
                v_old_distribution_id;
        END IF;
    END IF;

    RETURN NULL;
END;
$$;

CREATE CONSTRAINT TRIGGER discrete_probability_total_check
AFTER INSERT OR UPDATE OR DELETE
ON discrete_outcomes
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION validate_discrete_probability_total();

-- Verify that each discrete PMF belongs to a discrete variable.

CREATE OR REPLACE FUNCTION require_discrete_distribution()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_kind random_variable_kind;
BEGIN
    SELECT variable_kind
    INTO v_kind
    FROM random_variables
    WHERE distribution_id = NEW.distribution_id;

    IF v_kind IS DISTINCT FROM 'DISCRETE'::random_variable_kind THEN
        RAISE EXCEPTION
            'Distribution % is not a discrete random variable.',
            NEW.distribution_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER discrete_distribution_type_check
BEFORE INSERT OR UPDATE
ON discrete_outcomes
FOR EACH ROW
EXECUTE FUNCTION require_discrete_distribution();

-- ---------------------------------------------------------------------
-- 3. Continuous distribution parameters
-- ---------------------------------------------------------------------

CREATE TABLE continuous_parameters (
    distribution_id BIGINT PRIMARY KEY
        REFERENCES random_variables(distribution_id)
        ON DELETE CASCADE,

    family continuous_family NOT NULL,

    -- NORMAL:
    -- parameter_one = mean
    -- parameter_two = standard deviation
    --
    -- UNIFORM:
    -- parameter_one = lower bound
    -- parameter_two = upper bound

    parameter_one DOUBLE PRECISION NOT NULL,
    parameter_two DOUBLE PRECISION NOT NULL,

    CONSTRAINT parameters_must_be_finite
        CHECK (
            parameter_one > '-Infinity'::DOUBLE PRECISION
            AND parameter_one < 'Infinity'::DOUBLE PRECISION
            AND parameter_two > '-Infinity'::DOUBLE PRECISION
            AND parameter_two < 'Infinity'::DOUBLE PRECISION
        ),

    CONSTRAINT family_parameter_rules
        CHECK (
            (
                family = 'NORMAL'
                AND parameter_two > 0
            )
            OR
            (
                family = 'UNIFORM'
                AND parameter_one < parameter_two
            )
        )
);

COMMENT ON TABLE continuous_parameters IS
    'Parameters for normal and continuous uniform distributions.';

CREATE OR REPLACE FUNCTION require_continuous_distribution()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_kind random_variable_kind;
BEGIN
    SELECT variable_kind
    INTO v_kind
    FROM random_variables
    WHERE distribution_id = NEW.distribution_id;

    IF v_kind IS DISTINCT FROM 'CONTINUOUS'::random_variable_kind THEN
        RAISE EXCEPTION
            'Distribution % is not a continuous random variable.',
            NEW.distribution_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER continuous_distribution_type_check
BEFORE INSERT OR UPDATE
ON continuous_parameters
FOR EACH ROW
EXECUTE FUNCTION require_continuous_distribution();

-- ---------------------------------------------------------------------
-- 4. Observations from random-variable samples
-- ---------------------------------------------------------------------

CREATE TABLE observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    distribution_id BIGINT NOT NULL
        REFERENCES random_variables(distribution_id)
        ON DELETE CASCADE,

    sample_number BIGINT NOT NULL,
    observed_value NUMERIC(20, 8) NOT NULL,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT sample_number_positive
        CHECK (sample_number > 0),

    CONSTRAINT one_observation_per_sample
        UNIQUE (distribution_id, sample_number)
);

COMMENT ON TABLE observations IS
    'Observed sample values generated or collected for a distribution.';

CREATE INDEX observations_distribution_time_idx
    ON observations(distribution_id, captured_at DESC);

CREATE INDEX observations_distribution_value_idx
    ON observations(distribution_id, observed_value);

CREATE OR REPLACE FUNCTION validate_observation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_kind random_variable_kind;
    v_matches BOOLEAN;
BEGIN
    SELECT variable_kind
    INTO v_kind
    FROM random_variables
    WHERE distribution_id = NEW.distribution_id;

    IF v_kind IS NULL THEN
        RAISE EXCEPTION
            'Unknown distribution ID: %',
            NEW.distribution_id;
    END IF;

    IF v_kind = 'DISCRETE' THEN
        SELECT EXISTS (
            SELECT 1
            FROM discrete_outcomes
            WHERE distribution_id = NEW.distribution_id
              AND outcome = NEW.observed_value
        )
        INTO v_matches;

        IF NOT v_matches THEN
            RAISE EXCEPTION
                'Observed value % is not in the discrete support of distribution %',
                NEW.observed_value,
                NEW.distribution_id;
        END IF;
    ELSE
        IF NOT EXISTS (
            SELECT 1
            FROM continuous_parameters
            WHERE distribution_id = NEW.distribution_id
        ) THEN
            RAISE EXCEPTION
                'Continuous distribution % has no parameters.',
                NEW.distribution_id;
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER observation_integrity_check
BEFORE INSERT OR UPDATE
ON observations
FOR EACH ROW
EXECUTE FUNCTION validate_observation();

-- ---------------------------------------------------------------------
-- 5. PMF and discrete CDF
-- ---------------------------------------------------------------------

CREATE OR REPLACE FUNCTION probability_mass_function(
    p_distribution_id BIGINT,
    p_x NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_kind random_variable_kind;
    v_result NUMERIC;
BEGIN
    SELECT variable_kind
    INTO v_kind
    FROM random_variables
    WHERE distribution_id = p_distribution_id;

    IF v_kind IS NULL THEN
        RAISE EXCEPTION
            'Unknown distribution ID: %',
            p_distribution_id;
    END IF;

    IF v_kind <> 'DISCRETE' THEN
        RAISE EXCEPTION
            'PMF is only defined for discrete variables.';
    END IF;

    SELECT COALESCE(MAX(probability), 0)
    INTO v_result
    FROM discrete_outcomes
    WHERE distribution_id = p_distribution_id
      AND outcome = p_x;

    RETURN v_result;
END;
$$;

CREATE OR REPLACE FUNCTION discrete_cdf(
    p_distribution_id BIGINT,
    p_x NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_kind random_variable_kind;
    v_result NUMERIC;
BEGIN
    SELECT variable_kind
    INTO v_kind
    FROM random_variables
    WHERE distribution_id = p_distribution_id;

    IF v_kind IS NULL THEN
        RAISE EXCEPTION
            'Unknown distribution ID: %',
            p_distribution_id;
    END IF;

    IF v_kind <> 'DISCRETE' THEN
        RAISE EXCEPTION
            'Discrete CDF function requires a discrete variable.';
    END IF;

    SELECT COALESCE(SUM(probability), 0)
    INTO v_result
    FROM discrete_outcomes
    WHERE distribution_id = p_distribution_id
      AND outcome <= p_x;

    RETURN LEAST(1.0, GREATEST(0.0, v_result));
END;
$$;

-- ---------------------------------------------------------------------
-- 6. Continuous PDF functions
-- ---------------------------------------------------------------------

CREATE OR REPLACE FUNCTION normal_pdf(
    p_distribution_id BIGINT,
    p_x DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_family continuous_family;
    v_mean DOUBLE PRECISION;
    v_sd DOUBLE PRECISION;
    v_z DOUBLE PRECISION;
BEGIN
    SELECT family, parameter_one, parameter_two
    INTO v_family, v_mean, v_sd
    FROM continuous_parameters
    WHERE distribution_id = p_distribution_id;

    IF NOT FOUND OR v_family <> 'NORMAL' THEN
        RAISE EXCEPTION
            'Distribution % is not configured as normal.',
            p_distribution_id;
    END IF;

    IF p_x IS NULL OR p_x = 'NaN'::DOUBLE PRECISION THEN
        RAISE EXCEPTION 'PDF input cannot be NULL or NaN.';
    END IF;

    IF p_x IN (
        'Infinity'::DOUBLE PRECISION,
        '-Infinity'::DOUBLE PRECISION
    ) THEN
        RETURN 0.0;
    END IF;

    v_z := (p_x - v_mean) / v_sd;

    RETURN
        EXP(-0.5 * v_z * v_z)
        / (v_sd * SQRT(2.0 * PI()));
END;
$$;

CREATE OR REPLACE FUNCTION uniform_pdf(
    p_distribution_id BIGINT,
    p_x DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_family continuous_family;
    v_lower DOUBLE PRECISION;
    v_upper DOUBLE PRECISION;
BEGIN
    SELECT family, parameter_one, parameter_two
    INTO v_family, v_lower, v_upper
    FROM continuous_parameters
    WHERE distribution_id = p_distribution_id;

    IF NOT FOUND OR v_family <> 'UNIFORM' THEN
        RAISE EXCEPTION
            'Distribution % is not configured as uniform.',
            p_distribution_id;
    END IF;

    IF p_x IS NULL OR p_x = 'NaN'::DOUBLE PRECISION THEN
        RAISE EXCEPTION 'PDF input cannot be NULL or NaN.';
    END IF;

    IF p_x >= v_lower AND p_x <= v_upper THEN
        RETURN 1.0 / (v_upper - v_lower);
    END IF;

    RETURN 0.0;
END;
$$;

-- ---------------------------------------------------------------------
-- 7. Continuous CDF functions
-- ---------------------------------------------------------------------

CREATE OR REPLACE FUNCTION normal_cdf(
    p_distribution_id BIGINT,
    p_x DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_family continuous_family;
    v_mean DOUBLE PRECISION;
    v_sd DOUBLE PRECISION;
    v_z DOUBLE PRECISION;
    v_t DOUBLE PRECISION;
    v_density DOUBLE PRECISION;
    v_polynomial DOUBLE PRECISION;
BEGIN
    SELECT family, parameter_one, parameter_two
    INTO v_family, v_mean, v_sd
    FROM continuous_parameters
    WHERE distribution_id = p_distribution_id;

    IF NOT FOUND OR v_family <> 'NORMAL' THEN
        RAISE EXCEPTION
            'Distribution % is not configured as normal.',
            p_distribution_id;
    END IF;

    IF p_x IS NULL OR p_x = 'NaN'::DOUBLE PRECISION THEN
        RAISE EXCEPTION 'CDF input cannot be NULL or NaN.';
    END IF;

    IF p_x = 'Infinity'::DOUBLE PRECISION THEN
        RETURN 1.0;
    END IF;

    IF p_x = '-Infinity'::DOUBLE PRECISION THEN
        RETURN 0.0;
    END IF;

    v_z := (p_x - v_mean) / v_sd;

    -- Abramowitz-Stegun normal CDF approximation.
    -- Maximum absolute error is approximately 8e-8.
    v_t := 1.0 / (1.0 + 0.2316419 * ABS(v_z));

    v_density :=
        0.3989422804014327 * EXP(-0.5 * v_z * v_z);

    v_polynomial :=
        v_t * (
            0.319381530
            + v_t * (
                -0.356563782
                + v_t * (
                    1.781477937
                    + v_t * (
                        -1.821255978
                        + v_t * 1.330274429
                    )
                )
            )
        );

    IF v_z >= 0 THEN
        RETURN 1.0 - v_density * v_polynomial;
    END IF;

    RETURN v_density * v_polynomial;
END;
$$;

CREATE OR REPLACE FUNCTION uniform_cdf(
    p_distribution_id BIGINT,
    p_x DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_family continuous_family;
    v_lower DOUBLE PRECISION;
    v_upper DOUBLE PRECISION;
BEGIN
    SELECT family, parameter_one, parameter_two
    INTO v_family, v_lower, v_upper
    FROM continuous_parameters
    WHERE distribution_id = p_distribution_id;

    IF NOT FOUND OR v_family <> 'UNIFORM' THEN
        RAISE EXCEPTION
            'Distribution % is not configured as uniform.',
            p_distribution_id;
    END IF;

    IF p_x IS NULL OR p_x = 'NaN'::DOUBLE PRECISION THEN
        RAISE EXCEPTION 'CDF input cannot be NULL or NaN.';
    END IF;

    IF p_x <= v_lower THEN
        RETURN 0.0;
    END IF;

    IF p_x >= v_upper THEN
        RETURN 1.0;
    END IF;

    RETURN (p_x - v_lower) / (v_upper - v_lower);
END;
$$;

-- ---------------------------------------------------------------------
-- 8. Generic PDF and CDF dispatch functions
-- ---------------------------------------------------------------------

CREATE OR REPLACE FUNCTION probability_density_function(
    p_distribution_id BIGINT,
    p_x DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_family continuous_family;
    v_kind random_variable_kind;
BEGIN
    SELECT variable_kind
    INTO v_kind
    FROM random_variables
    WHERE distribution_id = p_distribution_id;

    IF v_kind IS NULL THEN
        RAISE EXCEPTION
            'Unknown distribution ID: %',
            p_distribution_id;
    END IF;

    IF v_kind <> 'CONTINUOUS' THEN
        RAISE EXCEPTION
            'PDF is only defined for continuous variables.';
    END IF;

    SELECT family
    INTO v_family
    FROM continuous_parameters
    WHERE distribution_id = p_distribution_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Continuous parameters are missing for distribution %.',
            p_distribution_id;
    END IF;

    IF v_family = 'NORMAL' THEN
        RETURN normal_pdf(p_distribution_id, p_x);
    END IF;

    RETURN uniform_pdf(p_distribution_id, p_x);
END;
$$;

CREATE OR REPLACE FUNCTION cumulative_distribution_function(
    p_distribution_id BIGINT,
    p_x DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_kind random_variable_kind;
    v_family continuous_family;
BEGIN
    SELECT variable_kind
    INTO v_kind
    FROM random_variables
    WHERE distribution_id = p_distribution_id;

    IF v_kind IS NULL THEN
        RAISE EXCEPTION
            'Unknown distribution ID: %',
            p_distribution_id;
    END IF;

    IF v_kind = 'DISCRETE' THEN
        RETURN discrete_cdf(
            p_distribution_id,
            p_x::NUMERIC
        )::DOUBLE PRECISION;
    END IF;

    SELECT family
    INTO v_family
    FROM continuous_parameters
    WHERE distribution_id = p_distribution_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Continuous distribution parameters are missing.';
    END IF;

    IF v_family = 'NORMAL' THEN
        RETURN normal_cdf(p_distribution_id, p_x);
    END IF;

    RETURN uniform_cdf(p_distribution_id, p_x);
END;
$$;

-- ---------------------------------------------------------------------
-- 9. Expectation and variance
-- ---------------------------------------------------------------------

CREATE OR REPLACE FUNCTION expected_value(
    p_distribution_id BIGINT
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_kind random_variable_kind;
    v_family continuous_family;
    v_result DOUBLE PRECISION;
BEGIN
    SELECT variable_kind
    INTO v_kind
    FROM random_variables
    WHERE distribution_id = p_distribution_id;

    IF v_kind IS NULL THEN
        RAISE EXCEPTION
            'Unknown distribution ID: %',
            p_distribution_id;
    END IF;

    IF v_kind = 'DISCRETE' THEN
        SELECT SUM(outcome * probability)
        INTO v_result
        FROM discrete_outcomes
        WHERE distribution_id = p_distribution_id;

        RETURN COALESCE(v_result, 0.0);
    END IF;

    SELECT
        family,
        CASE
            WHEN family = 'NORMAL' THEN parameter_one
            ELSE (parameter_one + parameter_two) / 2.0
        END
    INTO v_family, v_result
    FROM continuous_parameters
    WHERE distribution_id = p_distribution_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Continuous parameters not found.';
    END IF;

    RETURN v_result;
END;
$$;

CREATE OR REPLACE FUNCTION theoretical_variance(
    p_distribution_id BIGINT
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_kind random_variable_kind;
    v_family continuous_family;
    v_result DOUBLE PRECISION;
BEGIN
    SELECT variable_kind
    INTO v_kind
    FROM random_variables
    WHERE distribution_id = p_distribution_id;

    IF v_kind IS NULL THEN
        RAISE EXCEPTION
            'Unknown distribution ID: %',
            p_distribution_id;
    END IF;

    IF v_kind = 'DISCRETE' THEN
        SELECT
            SUM(
                probability
                * POWER(
                    outcome - expected_value(p_distribution_id),
                    2
                )
            )
        INTO v_result
        FROM discrete_outcomes
        WHERE distribution_id = p_distribution_id;

        RETURN COALESCE(v_result, 0.0);
    END IF;

    SELECT
        family,
        CASE
            WHEN family = 'NORMAL' THEN POWER(parameter_two, 2)
            ELSE POWER(parameter_two - parameter_one, 2) / 12.0
        END
    INTO v_family, v_result
    FROM continuous_parameters
    WHERE distribution_id = p_distribution_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Continuous parameters not found.';
    END IF;

    RETURN v_result;
END;
$$;

-- ---------------------------------------------------------------------
-- 10. Discrete random sampling
-- ---------------------------------------------------------------------

CREATE OR REPLACE FUNCTION draw_discrete(
    p_distribution_id BIGINT
)
RETURNS NUMERIC
LANGUAGE plpgsql
VOLATILE
AS $$
DECLARE
    v_kind random_variable_kind;
    v_draw DOUBLE PRECISION;
    v_result NUMERIC;
BEGIN
    SELECT variable_kind
    INTO v_kind
    FROM random_variables
    WHERE distribution_id = p_distribution_id;

    IF v_kind IS DISTINCT FROM 'DISCRETE'::random_variable_kind THEN
        RAISE EXCEPTION
            'Sampling function requires a discrete distribution.';
    END IF;

    -- Store the draw once so every row is compared against the same value.
    v_draw := random();

    SELECT outcome
    INTO v_result
    FROM (
        SELECT
            outcome,
            SUM(probability) OVER (
                ORDER BY outcome
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS cumulative_probability
        FROM discrete_outcomes
        WHERE distribution_id = p_distribution_id
    ) distribution
    WHERE cumulative_probability >= v_draw
    ORDER BY outcome
    LIMIT 1;

    IF v_result IS NULL THEN
        RAISE EXCEPTION
            'Unable to sample from distribution %.',
            p_distribution_id;
    END IF;

    RETURN v_result;
END;
$$;

-- ---------------------------------------------------------------------
-- 11. Controlled observation recording
-- ---------------------------------------------------------------------

CREATE OR REPLACE PROCEDURE record_observation(
    p_distribution_id BIGINT,
    p_sample_number BIGINT,
    p_value NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_sample_number <= 0 THEN
        RAISE EXCEPTION
            'Sample number must be positive.';
    END IF;

    IF p_value IS NULL THEN
        RAISE EXCEPTION
            'Observation value cannot be NULL.';
    END IF;

    INSERT INTO observations (
        distribution_id,
        sample_number,
        observed_value
    )
    VALUES (
        p_distribution_id,
        p_sample_number,
        p_value
    )
    ON CONFLICT (distribution_id, sample_number)
    DO UPDATE SET
        observed_value = EXCLUDED.observed_value,
        captured_at = CURRENT_TIMESTAMP;
END;
$$;

-- ---------------------------------------------------------------------
-- 12. Reporting views
-- ---------------------------------------------------------------------

CREATE OR REPLACE VIEW distribution_catalog AS
SELECT
    rv.distribution_id,
    rv.variable_code,
    rv.description,
    rv.variable_kind,
    cp.family AS continuous_family,
    cp.parameter_one,
    cp.parameter_two,
    expected_value(rv.distribution_id) AS theoretical_mean,
    theoretical_variance(rv.distribution_id) AS theoretical_variance,
    rv.created_at
FROM random_variables rv
LEFT JOIN continuous_parameters cp
    ON cp.distribution_id = rv.distribution_id;

CREATE OR REPLACE VIEW observation_statistics AS
SELECT
    rv.distribution_id,
    rv.variable_code,
    rv.variable_kind,
    COUNT(o.observation_id) AS observation_count,
    AVG(o.observed_value) AS empirical_mean,
    VAR_SAMP(o.observed_value) AS empirical_sample_variance,
    STDDEV_SAMP(o.observed_value) AS empirical_sample_standard_deviation,
    MIN(o.observed_value) AS minimum_observed_value,
    MAX(o.observed_value) AS maximum_observed_value,
    MAX(o.captured_at) AS latest_observation_time
FROM random_variables rv
LEFT JOIN observations o
    ON o.distribution_id = rv.distribution_id
GROUP BY
    rv.distribution_id,
    rv.variable_code,
    rv.variable_kind;

-- ---------------------------------------------------------------------
-- 13. Sample distributions
-- ---------------------------------------------------------------------

BEGIN;

INSERT INTO random_variables (
    variable_code,
    description,
    variable_kind
)
VALUES
(
    'failed_requests',
    'Number of failed requests among four independent requests.',
    'DISCRETE'
),
(
    'api_latency_ms',
    'API response time in milliseconds, modeled by a normal distribution.',
    'CONTINUOUS'
),
(
    'sensor_error',
    'Sensor measurement error with a bounded uniform distribution.',
    'CONTINUOUS'
);

INSERT INTO discrete_outcomes (
    distribution_id,
    outcome,
    probability
)
SELECT
    rv.distribution_id,
    values.outcome,
    values.probability
FROM random_variables rv
CROSS JOIN (
    VALUES
        (0::NUMERIC, 0.6561::NUMERIC),
        (1::NUMERIC, 0.2916::NUMERIC),
        (2::NUMERIC, 0.0486::NUMERIC),
        (3::NUMERIC, 0.0036::NUMERIC),
        (4::NUMERIC, 0.0001::NUMERIC)
) AS values(outcome, probability)
WHERE rv.variable_code = 'failed_requests';

INSERT INTO continuous_parameters (
    distribution_id,
    family,
    parameter_one,
    parameter_two
)
SELECT
    rv.distribution_id,
    'NORMAL',
    120.0,
    25.0
FROM random_variables rv
WHERE rv.variable_code = 'api_latency_ms';

INSERT INTO continuous_parameters (
    distribution_id,
    family,
    parameter_one,
    parameter_two
)
SELECT
    rv.distribution_id,
    'UNIFORM',
    -2.0,
    2.0
FROM random_variables rv
WHERE rv.variable_code = 'sensor_error';

-- Record representative observations.
-- Discrete values must belong to the defined support.
CALL record_observation(
    (SELECT distribution_id FROM random_variables
     WHERE variable_code = 'failed_requests'),
    1,
    0
);

CALL record_observation(
    (SELECT distribution_id FROM random_variables
     WHERE variable_code = 'failed_requests'),
    2,
    1
);

CALL record_observation(
    (SELECT distribution_id FROM random_variables
     WHERE variable_code = 'failed_requests'),
    3,
    2
);

CALL record_observation(
    (SELECT distribution_id FROM random_variables
     WHERE variable_code = 'failed_requests'),
    4,
    0
);

CALL record_observation(
    (SELECT distribution_id FROM random_variables
     WHERE variable_code = 'failed_requests'),
    5,
    1
);

CALL record_observation(
    (SELECT distribution_id FROM random_variables
     WHERE variable_code = 'api_latency_ms'),
    1,
    105.0
);

CALL record_observation(
    (SELECT distribution_id FROM random_variables
     WHERE variable_code = 'api_latency_ms'),
    2,
    122.0
);

CALL record_observation(
    (SELECT distribution_id FROM random_variables
     WHERE variable_code = 'api_latency_ms'),
    3,
    180.0
);

CALL record_observation(
    (SELECT distribution_id FROM random_variables
     WHERE variable_code = 'api_latency_ms'),
    4,
    95.0
);

CALL record_observation(
    (SELECT distribution_id FROM random_variables
     WHERE variable_code = 'api_latency_ms'),
    5,
    145.0
);

CALL record_observation(
    (SELECT distribution_id FROM random_variables
     WHERE variable_code = 'sensor_error'),
    1,
    -1.25
);

CALL record_observation(
    (SELECT distribution_id FROM random_variables
     WHERE variable_code = 'sensor_error'),
    2,
    0.20
);

CALL record_observation(
    (SELECT distribution_id FROM random_variables
     WHERE variable_code = 'sensor_error'),
    3,
    1.70
);

COMMIT;

-- ---------------------------------------------------------------------
-- 14. Retrieval: distribution metadata and theoretical properties
-- ---------------------------------------------------------------------

SELECT
    variable_code,
    variable_kind,
    continuous_family,
    parameter_one,
    parameter_two,
    theoretical_mean,
    theoretical_variance
FROM distribution_catalog
ORDER BY variable_code;

-- ---------------------------------------------------------------------
-- 15. Retrieval: discrete PMF
-- ---------------------------------------------------------------------

SELECT
    rv.variable_code,
    d.outcome,
    d.probability AS probability_mass
FROM random_variables rv
JOIN discrete_outcomes d
    ON d.distribution_id = rv.distribution_id
WHERE rv.variable_code = 'failed_requests'
ORDER BY d.outcome;

-- ---------------------------------------------------------------------
-- 16. Evaluation: PMF and discrete CDF
-- ---------------------------------------------------------------------

SELECT
    rv.variable_code,
    probability_mass_function(rv.distribution_id, 2) AS probability_x_equals_2,
    discrete_cdf(rv.distribution_id, 2) AS probability_x_at_most_2
FROM random_variables rv
WHERE rv.variable_code = 'failed_requests';

-- ---------------------------------------------------------------------
-- 17. Evaluation: normal PDF and CDF
-- ---------------------------------------------------------------------

SELECT
    rv.variable_code,
    probability_density_function(
        rv.distribution_id,
        150.0
    ) AS density_at_150_ms,
    cumulative_distribution_function(
        rv.distribution_id,
        150.0
    ) AS probability_at_most_150_ms,
    1.0 - cumulative_distribution_function(
        rv.distribution_id,
        180.0
    ) AS probability_above_180_ms
FROM random_variables rv
WHERE rv.variable_code = 'api_latency_ms';

-- ---------------------------------------------------------------------
-- 18. Evaluation: uniform PDF and CDF
-- ---------------------------------------------------------------------

SELECT
    rv.variable_code,
    probability_density_function(
        rv.distribution_id,
        0.0
    ) AS density_at_zero,
    cumulative_distribution_function(
        rv.distribution_id,
        1.0
    ) AS probability_at_most_one,
    cumulative_distribution_function(
        rv.distribution_id,
        1.0
    ) - cumulative_distribution_function(
        rv.distribution_id,
        -1.0
    ) AS probability_between_minus_one_and_one
FROM random_variables rv
WHERE rv.variable_code = 'sensor_error';

-- ---------------------------------------------------------------------
-- 19. Validation: PMF probability totals
-- ---------------------------------------------------------------------

SELECT
    rv.variable_code,
    COUNT(d.outcome) AS support_size,
    SUM(d.probability) AS total_probability,
    CASE
        WHEN COUNT(d.outcome) > 0
         AND ABS(SUM(d.probability) - 1.0) <= 0.000000001
        THEN 'VALID'
        ELSE 'INVALID'
    END AS pmf_validation
FROM random_variables rv
LEFT JOIN discrete_outcomes d
    ON d.distribution_id = rv.distribution_id
WHERE rv.variable_kind = 'DISCRETE'
GROUP BY rv.distribution_id, rv.variable_code;

-- ---------------------------------------------------------------------
-- 20. Aggregation: empirical observations
-- ---------------------------------------------------------------------

SELECT
    variable_code,
    variable_kind,
    observation_count,
    ROUND(empirical_mean::NUMERIC, 4) AS empirical_mean,
    ROUND(empirical_sample_variance::NUMERIC, 4)
        AS empirical_sample_variance,
    ROUND(empirical_sample_standard_deviation::NUMERIC, 4)
        AS empirical_sample_standard_deviation,
    minimum_observed_value,
    maximum_observed_value
FROM observation_statistics
ORDER BY variable_code;

-- ---------------------------------------------------------------------
-- 21. Retrieval: recorded observation history
-- ---------------------------------------------------------------------

SELECT
    rv.variable_code,
    o.sample_number,
    o.observed_value,
    o.captured_at
FROM observations o
JOIN random_variables rv
    ON rv.distribution_id = o.distribution_id
ORDER BY rv.variable_code, o.sample_number;

-- ---------------------------------------------------------------------
-- 22. Workflow evaluation: upper-tail probability and policy eligibility
-- ---------------------------------------------------------------------

WITH policy AS (
    SELECT
        'failed_requests'::VARCHAR AS variable_code,
        1.0::DOUBLE PRECISION AS threshold,
        0.06::DOUBLE PRECISION AS maximum_allowed_probability
),
evaluated AS (
    SELECT
        rv.distribution_id,
        rv.variable_code,
        p.threshold,
        p.maximum_allowed_probability,
        1.0 - cumulative_distribution_function(
            rv.distribution_id,
            p.threshold
        ) AS upper_tail_probability
    FROM random_variables rv
    JOIN policy p
        ON p.variable_code = rv.variable_code
)
SELECT
    variable_code,
    threshold,
    upper_tail_probability,
    maximum_allowed_probability,
    CASE
        WHEN upper_tail_probability <= maximum_allowed_probability
            THEN 'ELIGIBLE'
        ELSE 'NOT_ELIGIBLE'
    END AS policy_decision
FROM evaluated;

-- ---------------------------------------------------------------------
-- 23. Aggregation with a CTE: observed failure-count distribution
-- ---------------------------------------------------------------------

WITH observed_counts AS (
    SELECT
        distribution_id,
        observed_value,
        COUNT(*) AS frequency
    FROM observations
    WHERE distribution_id = (
        SELECT distribution_id
        FROM random_variables
        WHERE variable_code = 'failed_requests'
    )
    GROUP BY distribution_id, observed_value
),
total_observations AS (
    SELECT SUM(frequency) AS total
    FROM observed_counts
)
SELECT
    observed_counts.observed_value AS failure_count,
    observed_counts.frequency,
    ROUND(
        observed_counts.frequency::NUMERIC /
        NULLIF(total_observations.total, 0),
        4
    ) AS empirical_probability
FROM observed_counts
CROSS JOIN total_observations
ORDER BY observed_counts.observed_value;

-- ---------------------------------------------------------------------
-- 24. Workflow processing: generate a discrete observation
-- ---------------------------------------------------------------------

SELECT
    rv.variable_code,
    draw_discrete(rv.distribution_id) AS simulated_failure_count
FROM random_variables rv
WHERE rv.variable_code = 'failed_requests';

-- ---------------------------------------------------------------------
-- 25. Demonstrate a failed transaction safely
-- ---------------------------------------------------------------------

-- The trigger rejects this observation because 9 is not in the
-- support {0, 1, 2, 3, 4}. The savepoint allows the script to continue.

BEGIN;

SAVEPOINT invalid_observation_test;

DO $$
DECLARE
    v_distribution_id BIGINT;
BEGIN
    SELECT distribution_id
    INTO v_distribution_id
    FROM random_variables
    WHERE variable_code = 'failed_requests';

    BEGIN
        INSERT INTO observations (
            distribution_id,
            sample_number,
            observed_value
        )
        VALUES (
            v_distribution_id,
            999,
            9
        );

        RAISE EXCEPTION
            'Validation failed: an unsupported discrete value was accepted.';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Expected validation failure: %',
                SQLERRM;
    END;
END;
$$;

ROLLBACK TO SAVEPOINT invalid_observation_test;
RELEASE SAVEPOINT invalid_observation_test;
COMMIT;

-- ---------------------------------------------------------------------
-- 26. Final integrity report
-- ---------------------------------------------------------------------

SELECT
    rv.variable_code,
    rv.variable_kind,
    COUNT(o.observation_id) AS observation_count,
    CASE
        WHEN rv.variable_kind = 'DISCRETE'
             AND EXISTS (
                 SELECT 1
                 FROM discrete_outcomes d
                 WHERE d.distribution_id = rv.distribution_id
             )
            THEN 'SUPPORT_CONFIGURED'
        WHEN rv.variable_kind = 'CONTINUOUS'
             AND EXISTS (
                 SELECT 1
                 FROM continuous_parameters cp
                 WHERE cp.distribution_id = rv.distribution_id
             )
            THEN 'PARAMETERS_CONFIGURED'
        ELSE 'CONFIGURATION_MISSING'
    END AS configuration_status
FROM random_variables rv
LEFT JOIN observations o
    ON o.distribution_id = rv.distribution_id
GROUP BY
    rv.distribution_id,
    rv.variable_code,
    rv.variable_kind
ORDER BY rv.variable_code;
