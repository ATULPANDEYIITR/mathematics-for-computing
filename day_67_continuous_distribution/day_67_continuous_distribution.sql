/*
===============================================================================
CONTINUOUS DISTRIBUTIONS
Uniform, Exponential, and Normal Distributions
PostgreSQL 14+

Database workflow:
- Distribution parameter registration
- Parameter validation
- PDF, CDF and quantile calculations
- Simulation observation storage
- Statistical aggregation
- Probability evaluation
- Distribution monitoring
- Analytical reporting

All calculations use double precision.
===============================================================================
*/

BEGIN;

CREATE SCHEMA IF NOT EXISTS continuous_stats;

SET search_path TO continuous_stats, public;


/* ============================================================================
   1. DOMAIN TYPES AND DISTRIBUTION REGISTRY
   ============================================================================ */

DO $$
BEGIN
    CREATE TYPE distribution_type AS ENUM (
        'UNIFORM',
        'EXPONENTIAL',
        'NORMAL'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END;
$$;

DO $$
BEGIN
    CREATE TYPE simulation_status AS ENUM (
        'CREATED',
        'RUNNING',
        'COMPLETED',
        'FAILED'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END;
$$;

CREATE TABLE IF NOT EXISTS distribution_registry (
    distribution_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    distribution_name VARCHAR(100) NOT NULL,

    distribution_type distribution_type NOT NULL,

    parameter_one DOUBLE PRECISION NOT NULL,

    parameter_two DOUBLE PRECISION,

    description TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_distribution_name UNIQUE (distribution_name),

    CONSTRAINT chk_parameter_one_finite
        CHECK (
            parameter_one NOT IN (
                'Infinity'::DOUBLE PRECISION,
                '-Infinity'::DOUBLE PRECISION,
                'NaN'::DOUBLE PRECISION
            )
        ),

    CONSTRAINT chk_parameter_two_finite
        CHECK (
            parameter_two IS NULL
            OR parameter_two NOT IN (
                'Infinity'::DOUBLE PRECISION,
                '-Infinity'::DOUBLE PRECISION,
                'NaN'::DOUBLE PRECISION
            )
        ),

    CONSTRAINT chk_distribution_parameters
        CHECK (
            (
                distribution_type = 'UNIFORM'
                AND parameter_two IS NOT NULL
                AND parameter_one < parameter_two
            )
            OR
            (
                distribution_type = 'EXPONENTIAL'
                AND parameter_one > 0
                AND parameter_two IS NULL
            )
            OR
            (
                distribution_type = 'NORMAL'
                AND parameter_two > 0
            )
        )
);


/* ============================================================================
   2. SIMULATION AND OBSERVATION TABLES
   ============================================================================ */

CREATE TABLE IF NOT EXISTS simulation_runs (
    simulation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    distribution_id BIGINT NOT NULL
        REFERENCES distribution_registry(distribution_id),

    simulation_name VARCHAR(150) NOT NULL,

    status simulation_status NOT NULL DEFAULT 'CREATED',

    random_seed BIGINT NOT NULL,

    requested_sample_count INTEGER NOT NULL,

    interval_lower DOUBLE PRECISION NOT NULL,

    interval_upper DOUBLE PRECISION NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    started_at TIMESTAMPTZ,

    completed_at TIMESTAMPTZ,

    failure_reason TEXT,

    CONSTRAINT chk_sample_count
        CHECK (requested_sample_count > 0),

    CONSTRAINT chk_interval
        CHECK (
            interval_lower NOT IN (
                'Infinity'::DOUBLE PRECISION,
                '-Infinity'::DOUBLE PRECISION,
                'NaN'::DOUBLE PRECISION
            )
            AND interval_upper NOT IN (
                'Infinity'::DOUBLE PRECISION,
                '-Infinity'::DOUBLE PRECISION,
                'NaN'::DOUBLE PRECISION
            )
            AND interval_lower <= interval_upper
        ),

    CONSTRAINT chk_simulation_dates
        CHECK (
            completed_at IS NULL
            OR started_at IS NULL
            OR completed_at >= started_at
        ),

    CONSTRAINT chk_failure_state
        CHECK (
            status <> 'FAILED'
            OR failure_reason IS NOT NULL
        )
);

CREATE TABLE IF NOT EXISTS observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    simulation_id BIGINT NOT NULL
        REFERENCES simulation_runs(simulation_id)
        ON DELETE CASCADE,

    observation_number INTEGER NOT NULL,

    observed_value DOUBLE PRECISION NOT NULL,

    observed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_simulation_observation
        UNIQUE (simulation_id, observation_number),

    CONSTRAINT chk_observation_number
        CHECK (observation_number > 0),

    CONSTRAINT chk_observation_finite
        CHECK (
            observed_value NOT IN (
                'Infinity'::DOUBLE PRECISION,
                '-Infinity'::DOUBLE PRECISION,
                'NaN'::DOUBLE PRECISION
            )
        )
);

CREATE INDEX IF NOT EXISTS idx_simulation_distribution_status
    ON simulation_runs(distribution_id, status);

CREATE INDEX IF NOT EXISTS idx_observations_simulation_value
    ON observations(simulation_id, observed_value);

CREATE INDEX IF NOT EXISTS idx_observations_simulation_number
    ON observations(simulation_id, observation_number);


/* ============================================================================
   3. DISTRIBUTION REGISTRATION
   ============================================================================ */

INSERT INTO distribution_registry (
    distribution_name,
    distribution_type,
    parameter_one,
    parameter_two,
    description
)
VALUES
(
    'Uniform_0_100',
    'UNIFORM',
    0,
    100,
    'Uniform processing-duration model between zero and one hundred.'
),
(
    'Exponential_Rate_0_2',
    'EXPONENTIAL',
    0.2,
    NULL,
    'Exponential waiting-time model with rate 0.2.'
),
(
    'Normal_Mean_50_SD_10',
    'NORMAL',
    50,
    10,
    'Normal measurement model with mean fifty and standard deviation ten.'
)
ON CONFLICT (distribution_name) DO NOTHING;


/* ============================================================================
   4. PDF FUNCTIONS
   ============================================================================ */

CREATE OR REPLACE FUNCTION uniform_pdf(
    p_x DOUBLE PRECISION,
    p_a DOUBLE PRECISION,
    p_b DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF p_a >= p_b THEN
        RAISE EXCEPTION 'Uniform distribution requires a < b.';
    END IF;

    IF p_x < p_a OR p_x > p_b THEN
        RETURN 0;
    END IF;

    RETURN 1.0 / (p_b - p_a);
END;
$$;


CREATE OR REPLACE FUNCTION exponential_pdf(
    p_x DOUBLE PRECISION,
    p_rate DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF p_rate <= 0 THEN
        RAISE EXCEPTION 'Exponential rate must be positive.';
    END IF;

    IF p_x < 0 THEN
        RETURN 0;
    END IF;

    RETURN p_rate * EXP(-p_rate * p_x);
END;
$$;


CREATE OR REPLACE FUNCTION normal_pdf(
    p_x DOUBLE PRECISION,
    p_mean DOUBLE PRECISION,
    p_sd DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    v_z DOUBLE PRECISION;
BEGIN
    IF p_sd <= 0 THEN
        RAISE EXCEPTION 'Normal standard deviation must be positive.';
    END IF;

    v_z := (p_x - p_mean) / p_sd;

    RETURN EXP(-0.5 * v_z * v_z)
        / (p_sd * SQRT(2.0 * PI()));
END;
$$;


/* ============================================================================
   5. CDF FUNCTIONS
   ============================================================================ */

CREATE OR REPLACE FUNCTION uniform_cdf(
    p_x DOUBLE PRECISION,
    p_a DOUBLE PRECISION,
    p_b DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF p_a >= p_b THEN
        RAISE EXCEPTION 'Uniform distribution requires a < b.';
    END IF;

    IF p_x < p_a THEN
        RETURN 0;
    ELSIF p_x >= p_b THEN
        RETURN 1;
    END IF;

    RETURN (p_x - p_a) / (p_b - p_a);
END;
$$;


CREATE OR REPLACE FUNCTION exponential_cdf(
    p_x DOUBLE PRECISION,
    p_rate DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF p_rate <= 0 THEN
        RAISE EXCEPTION 'Exponential rate must be positive.';
    END IF;

    IF p_x <= 0 THEN
        RETURN 0;
    END IF;

    RETURN 1.0 - EXP(-p_rate * p_x);
END;
$$;


/*
 * PostgreSQL does not provide a built-in erf function.
 * This approximation is used to calculate the normal CDF.
 */

CREATE OR REPLACE FUNCTION error_function(
    p_x DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    v_sign DOUBLE PRECISION;
    v_x DOUBLE PRECISION;
    v_t DOUBLE PRECISION;
    v_poly DOUBLE PRECISION;
BEGIN
    v_sign := CASE WHEN p_x < 0 THEN -1 ELSE 1 END;
    v_x := ABS(p_x);

    v_t := 1.0 / (1.0 + 0.3275911 * v_x);

    v_poly :=
        (((((1.061405429 * v_t - 1.453152027) * v_t)
        + 1.421413741) * v_t - 0.284496736) * v_t
        + 0.254829592) * v_t;

    RETURN v_sign * (
        1.0 - v_poly * EXP(-v_x * v_x)
    );
END;
$$;


CREATE OR REPLACE FUNCTION normal_cdf(
    p_x DOUBLE PRECISION,
    p_mean DOUBLE PRECISION,
    p_sd DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    v_z DOUBLE PRECISION;
BEGIN
    IF p_sd <= 0 THEN
        RAISE EXCEPTION 'Normal standard deviation must be positive.';
    END IF;

    v_z := (p_x - p_mean) / p_sd;

    RETURN 0.5 * (
        1.0 + error_function(v_z / SQRT(2.0))
    );
END;
$$;


/* ============================================================================
   6. QUANTILE FUNCTIONS
   ============================================================================ */

CREATE OR REPLACE FUNCTION uniform_quantile(
    p_probability DOUBLE PRECISION,
    p_a DOUBLE PRECISION,
    p_b DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF p_a >= p_b THEN
        RAISE EXCEPTION 'Uniform distribution requires a < b.';
    END IF;

    IF p_probability < 0 OR p_probability > 1 THEN
        RAISE EXCEPTION 'Probability must be in [0, 1].';
    END IF;

    RETURN p_a + p_probability * (p_b - p_a);
END;
$$;


CREATE OR REPLACE FUNCTION exponential_quantile(
    p_probability DOUBLE PRECISION,
    p_rate DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF p_rate <= 0 THEN
        RAISE EXCEPTION 'Rate must be positive.';
    END IF;

    IF p_probability < 0 OR p_probability > 1 THEN
        RAISE EXCEPTION 'Probability must be in [0, 1].';
    END IF;

    IF p_probability = 1 THEN
        RETURN 'Infinity'::DOUBLE PRECISION;
    END IF;

    RETURN -LN(1.0 - p_probability) / p_rate;
END;
$$;


/*
 * Inverse normal CDF using bisection.
 * The search interval is deliberately broad for common applications.
 * Probabilities at zero and one have infinite quantiles.
 */

CREATE OR REPLACE FUNCTION normal_quantile(
    p_probability DOUBLE PRECISION,
    p_mean DOUBLE PRECISION,
    p_sd DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    v_low DOUBLE PRECISION;
    v_high DOUBLE PRECISION;
    v_mid DOUBLE PRECISION;
    v_result DOUBLE PRECISION;
    v_iteration INTEGER;
BEGIN
    IF p_sd <= 0 THEN
        RAISE EXCEPTION 'Standard deviation must be positive.';
    END IF;

    IF p_probability < 0 OR p_probability > 1 THEN
        RAISE EXCEPTION 'Probability must be in [0, 1].';
    END IF;

    IF p_probability = 0 THEN
        RETURN '-Infinity'::DOUBLE PRECISION;
    ELSIF p_probability = 1 THEN
        RETURN 'Infinity'::DOUBLE PRECISION;
    END IF;

    IF p_probability = 0.5 THEN
        RETURN p_mean;
    END IF;

    /*
     * A standardized interval of [-40, 40] covers probabilities
     * representable with useful precision in double precision.
     */
    v_low := -40;
    v_high := 40;

    FOR v_iteration IN 1..200 LOOP
        v_mid := (v_low + v_high) / 2.0;

        v_result := normal_cdf(v_mid, 0, 1);

        IF v_result < p_probability THEN
            v_low := v_mid;
        ELSE
            v_high := v_mid;
        END IF;
    END LOOP;

    RETURN p_mean + p_sd * ((v_low + v_high) / 2.0);
END;
$$;


/* ============================================================================
   7. UNIFIED DISTRIBUTION FUNCTIONS
   ============================================================================ */

CREATE OR REPLACE FUNCTION distribution_pdf(
    p_distribution_id BIGINT,
    p_x DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_distribution distribution_registry%ROWTYPE;
BEGIN
    SELECT *
    INTO STRICT v_distribution
    FROM distribution_registry
    WHERE distribution_id = p_distribution_id;

    CASE v_distribution.distribution_type

        WHEN 'UNIFORM' THEN
            RETURN uniform_pdf(
                p_x,
                v_distribution.parameter_one,
                v_distribution.parameter_two
            );

        WHEN 'EXPONENTIAL' THEN
            RETURN exponential_pdf(
                p_x,
                v_distribution.parameter_one
            );

        WHEN 'NORMAL' THEN
            RETURN normal_pdf(
                p_x,
                v_distribution.parameter_one,
                v_distribution.parameter_two
            );
    END CASE;

    RAISE EXCEPTION 'Unsupported distribution.';
END;
$$;


CREATE OR REPLACE FUNCTION distribution_cdf(
    p_distribution_id BIGINT,
    p_x DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_distribution distribution_registry%ROWTYPE;
BEGIN
    SELECT *
    INTO STRICT v_distribution
    FROM distribution_registry
    WHERE distribution_id = p_distribution_id;

    CASE v_distribution.distribution_type

        WHEN 'UNIFORM' THEN
            RETURN uniform_cdf(
                p_x,
                v_distribution.parameter_one,
                v_distribution.parameter_two
            );

        WHEN 'EXPONENTIAL' THEN
            RETURN exponential_cdf(
                p_x,
                v_distribution.parameter_one
            );

        WHEN 'NORMAL' THEN
            RETURN normal_cdf(
                p_x,
                v_distribution.parameter_one,
                v_distribution.parameter_two
            );
    END CASE;

    RAISE EXCEPTION 'Unsupported distribution.';
END;
$$;


CREATE OR REPLACE FUNCTION distribution_quantile(
    p_distribution_id BIGINT,
    p_probability DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_distribution distribution_registry%ROWTYPE;
BEGIN
    SELECT *
    INTO STRICT v_distribution
    FROM distribution_registry
    WHERE distribution_id = p_distribution_id;

    CASE v_distribution.distribution_type

        WHEN 'UNIFORM' THEN
            RETURN uniform_quantile(
                p_probability,
                v_distribution.parameter_one,
                v_distribution.parameter_two
            );

        WHEN 'EXPONENTIAL' THEN
            RETURN exponential_quantile(
                p_probability,
                v_distribution.parameter_one
            );

        WHEN 'NORMAL' THEN
            RETURN normal_quantile(
                p_probability,
                v_distribution.parameter_one,
                v_distribution.parameter_two
            );
    END CASE;

    RAISE EXCEPTION 'Unsupported distribution.';
END;
$$;


/* ============================================================================
   8. SIMULATION STATE VALIDATION
   ============================================================================ */

CREATE OR REPLACE FUNCTION validate_simulation_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN

        IF OLD.status = 'COMPLETED' AND NEW.status <> 'COMPLETED' THEN
            RAISE EXCEPTION
                'Completed simulations cannot be reopened or modified.';
        END IF;

        IF OLD.status = 'FAILED' AND NEW.status <> 'FAILED' THEN
            RAISE EXCEPTION
                'Failed simulations cannot be restarted directly.';
        END IF;

        IF OLD.status = 'CREATED'
           AND NEW.status NOT IN ('CREATED', 'RUNNING', 'FAILED') THEN

            RAISE EXCEPTION 'Invalid CREATED state transition.';
        END IF;

        IF OLD.status = 'RUNNING'
           AND NEW.status NOT IN ('RUNNING', 'COMPLETED', 'FAILED') THEN

            RAISE EXCEPTION 'Invalid RUNNING state transition.';
        END IF;

    END IF;

    IF NEW.status = 'RUNNING' AND NEW.started_at IS NULL THEN
        NEW.started_at := CURRENT_TIMESTAMP;
    END IF;

    IF NEW.status = 'COMPLETED' THEN
        IF NEW.completed_at IS NULL THEN
            NEW.completed_at := CURRENT_TIMESTAMP;
        END IF;

        NEW.failure_reason := NULL;
    END IF;

    IF NEW.status = 'FAILED' AND NEW.failure_reason IS NULL THEN
        RAISE EXCEPTION
            'Failure reason is required for failed simulations.';
    END IF;

    RETURN NEW;
END;
$$;


DROP TRIGGER IF EXISTS trg_simulation_transition
ON simulation_runs;

CREATE TRIGGER trg_simulation_transition
BEFORE UPDATE ON simulation_runs
FOR EACH ROW
EXECUTE FUNCTION validate_simulation_transition();


/* ============================================================================
   9. OBSERVATION INSERTION PROTECTION
   ============================================================================ */

CREATE OR REPLACE FUNCTION validate_observation_insert()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_status simulation_status;
    v_expected INTEGER;
BEGIN
    SELECT status, requested_sample_count
    INTO STRICT v_status, v_expected
    FROM simulation_runs
    WHERE simulation_id = NEW.simulation_id
    FOR UPDATE;

    IF v_status <> 'RUNNING' THEN
        RAISE EXCEPTION
            'Observations can only be added to running simulations.';
    END IF;

    IF NEW.observation_number > v_expected THEN
        RAISE EXCEPTION
            'Observation exceeds requested sample count.';
    END IF;

    RETURN NEW;
END;
$$;


DROP TRIGGER IF EXISTS trg_observation_insert
ON observations;

CREATE TRIGGER trg_observation_insert
BEFORE INSERT ON observations
FOR EACH ROW
EXECUTE FUNCTION validate_observation_insert();


/* ============================================================================
   10. SIMULATION WORKFLOW PROCEDURES
   ============================================================================ */

CREATE OR REPLACE PROCEDURE start_simulation(
    p_simulation_id BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE simulation_runs
    SET status = 'RUNNING'
    WHERE simulation_id = p_simulation_id
      AND status = 'CREATED';

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Simulation does not exist or cannot be started.';
    END IF;
END;
$$;


CREATE OR REPLACE PROCEDURE complete_simulation(
    p_simulation_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_expected INTEGER;
    v_actual BIGINT;
BEGIN
    SELECT requested_sample_count
    INTO STRICT v_expected
    FROM simulation_runs
    WHERE simulation_id = p_simulation_id
      AND status = 'RUNNING'
    FOR UPDATE;

    SELECT COUNT(*)
    INTO v_actual
    FROM observations
    WHERE simulation_id = p_simulation_id;

    IF v_actual <> v_expected THEN
        RAISE EXCEPTION
            'Expected % observations but received %.',
            v_expected,
            v_actual;
    END IF;

    UPDATE simulation_runs
    SET status = 'COMPLETED'
    WHERE simulation_id = p_simulation_id;
END;
$$;


CREATE OR REPLACE PROCEDURE fail_simulation(
    p_simulation_id BIGINT,
    p_reason TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NULLIF(BTRIM(p_reason), '') IS NULL THEN
        RAISE EXCEPTION 'Failure reason cannot be empty.';
    END IF;

    UPDATE simulation_runs
    SET
        status = 'FAILED',
        failure_reason = p_reason
    WHERE simulation_id = p_simulation_id
      AND status IN ('CREATED', 'RUNNING');

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Simulation cannot be moved to FAILED state.';
    END IF;
END;
$$;


/* ============================================================================
   11. SIMULATION CREATION
   ============================================================================ */

INSERT INTO simulation_runs (
    distribution_id,
    simulation_name,
    random_seed,
    requested_sample_count,
    interval_lower,
    interval_upper
)
SELECT
    distribution_id,
    'Uniform_Processing_Duration',
    42,
    1000,
    20,
    80
FROM distribution_registry
WHERE distribution_name = 'Uniform_0_100'
ON CONFLICT DO NOTHING;


INSERT INTO simulation_runs (
    distribution_id,
    simulation_name,
    random_seed,
    requested_sample_count,
    interval_lower,
    interval_upper
)
SELECT
    distribution_id,
    'Exponential_Service_Waiting_Time',
    42,
    1000,
    1,
    5
FROM distribution_registry
WHERE distribution_name = 'Exponential_Rate_0_2';


INSERT INTO simulation_runs (
    distribution_id,
    simulation_name,
    random_seed,
    requested_sample_count,
    interval_lower,
    interval_upper
)
SELECT
    distribution_id,
    'Normal_Measurement_Variation',
    42,
    1000,
    40,
    60
FROM distribution_registry
WHERE distribution_name = 'Normal_Mean_50_SD_10';


/* ============================================================================
   12. RANDOM SAMPLE GENERATION
   ============================================================================ */

/*
 * PostgreSQL random() returns pseudo-random values in [0, 1).
 * These SQL simulations are illustrative and are not cryptographic.
 *
 * The SQL normal sampler uses the Box-Muller transformation.
 */

CREATE OR REPLACE FUNCTION generate_uniform_sample(
    p_a DOUBLE PRECISION,
    p_b DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
VOLATILE
AS $$
BEGIN
    IF p_a >= p_b THEN
        RAISE EXCEPTION 'Require a < b.';
    END IF;

    RETURN p_a + random() * (p_b - p_a);
END;
$$;


CREATE OR REPLACE FUNCTION generate_exponential_sample(
    p_rate DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
VOLATILE
AS $$
DECLARE
    v_u DOUBLE PRECISION;
BEGIN
    IF p_rate <= 0 THEN
        RAISE EXCEPTION 'Rate must be positive.';
    END IF;

    v_u := random();

    RETURN -LN(1.0 - v_u) / p_rate;
END;
$$;


CREATE OR REPLACE FUNCTION generate_normal_sample(
    p_mean DOUBLE PRECISION,
    p_sd DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
VOLATILE
AS $$
DECLARE
    v_u1 DOUBLE PRECISION;
    v_u2 DOUBLE PRECISION;
    v_z DOUBLE PRECISION;
BEGIN
    IF p_sd <= 0 THEN
        RAISE EXCEPTION 'Standard deviation must be positive.';
    END IF;

    v_u1 := random();

    WHILE v_u1 <= 0 LOOP
        v_u1 := random();
    END LOOP;

    v_u2 := random();

    v_z := SQRT(-2.0 * LN(v_u1))
        * COS(2.0 * PI() * v_u2);

    RETURN p_mean + p_sd * v_z;
END;
$$;


/* ============================================================================
   13. EXECUTE THREE SIMULATIONS
   ============================================================================ */

DO $$
DECLARE
    v_run RECORD;
    v_value DOUBLE PRECISION;
    v_i INTEGER;
BEGIN
    FOR v_run IN
        SELECT
            sr.simulation_id,
            sr.requested_sample_count,
            dr.distribution_type,
            dr.parameter_one,
            dr.parameter_two
        FROM simulation_runs sr
        JOIN distribution_registry dr
            USING (distribution_id)
        WHERE sr.status = 'CREATED'
        ORDER BY sr.simulation_id
    LOOP

        UPDATE simulation_runs
        SET status = 'RUNNING'
        WHERE simulation_id = v_run.simulation_id;

        FOR v_i IN 1..v_run.requested_sample_count LOOP

            CASE v_run.distribution_type

                WHEN 'UNIFORM' THEN
                    v_value := generate_uniform_sample(
                        v_run.parameter_one,
                        v_run.parameter_two
                    );

                WHEN 'EXPONENTIAL' THEN
                    v_value := generate_exponential_sample(
                        v_run.parameter_one
                    );

                WHEN 'NORMAL' THEN
                    v_value := generate_normal_sample(
                        v_run.parameter_one,
                        v_run.parameter_two
                    );

            END CASE;

            INSERT INTO observations (
                simulation_id,
                observation_number,
                observed_value
            )
            VALUES (
                v_run.simulation_id,
                v_i,
                v_value
            );

        END LOOP;

        CALL complete_simulation(v_run.simulation_id);

    END LOOP;
END;
$$;


/* ============================================================================
   14. SAMPLE VALIDATION CASES
   ============================================================================ */

/*
 * A failed simulation records a meaningful failure state.
 * It is kept separate from completed statistical simulations.
 */

INSERT INTO simulation_runs (
    distribution_id,
    simulation_name,
    random_seed,
    requested_sample_count,
    interval_lower,
    interval_upper
)
SELECT
    distribution_id,
    'Rejected_Operational_Run',
    99,
    100,
    0,
    10
FROM distribution_registry
WHERE distribution_name = 'Uniform_0_100';


/*
 * This run intentionally fails and demonstrates state validation.
 */
DO $$
DECLARE
    v_id BIGINT;
BEGIN
    SELECT simulation_id
    INTO v_id
    FROM simulation_runs
    WHERE simulation_name = 'Rejected_Operational_Run';

    UPDATE simulation_runs
    SET
        status = 'FAILED',
        failure_reason = 'Insufficient input observations.'
    WHERE simulation_id = v_id;
END;
$$;


/* ============================================================================
   15. THEORETICAL DISTRIBUTION VIEW
   ============================================================================ */

CREATE OR REPLACE VIEW distribution_parameters AS
SELECT
    distribution_id,
    distribution_name,
    distribution_type,
    parameter_one,
    parameter_two,

    CASE distribution_type
        WHEN 'UNIFORM' THEN
            (parameter_one + parameter_two) / 2.0

        WHEN 'EXPONENTIAL' THEN
            1.0 / parameter_one

        WHEN 'NORMAL' THEN
            parameter_one
    END AS theoretical_mean,

    CASE distribution_type
        WHEN 'UNIFORM' THEN
            POWER(parameter_two - parameter_one, 2) / 12.0

        WHEN 'EXPONENTIAL' THEN
            1.0 / POWER(parameter_one, 2)

        WHEN 'NORMAL' THEN
            POWER(parameter_two, 2)
    END AS theoretical_variance

FROM distribution_registry;


/* ============================================================================
   16. OBSERVATION STATISTICS VIEW
   ============================================================================ */

CREATE OR REPLACE VIEW simulation_statistics AS
SELECT
    sr.simulation_id,
    sr.simulation_name,
    sr.status,
    dr.distribution_name,
    dr.distribution_type,

    COUNT(o.observation_id) AS observation_count,

    AVG(o.observed_value) AS empirical_mean,

    VAR_SAMP(o.observed_value) AS empirical_variance,

    STDDEV_SAMP(o.observed_value) AS empirical_standard_deviation,

    MIN(o.observed_value) AS minimum_value,

    MAX(o.observed_value) AS maximum_value,

    PERCENTILE_CONT(0.5)
        WITHIN GROUP (ORDER BY o.observed_value)
        AS median_value,

    PERCENTILE_CONT(0.95)
        WITHIN GROUP (ORDER BY o.observed_value)
        AS ninety_fifth_percentile

FROM simulation_runs sr

JOIN distribution_registry dr
    USING (distribution_id)

LEFT JOIN observations o
    USING (simulation_id)

GROUP BY
    sr.simulation_id,
    sr.simulation_name,
    sr.status,
    dr.distribution_name,
    dr.distribution_type;


/* ============================================================================
   17. INTERVAL PROBABILITY REPORT
   ============================================================================ */

CREATE OR REPLACE VIEW interval_probability_report AS
SELECT
    sr.simulation_id,
    sr.simulation_name,
    dr.distribution_type,

    sr.interval_lower,
    sr.interval_upper,

    distribution_cdf(
        sr.distribution_id,
        sr.interval_upper
    )
    -
    distribution_cdf(
        sr.distribution_id,
        sr.interval_lower
    ) AS theoretical_probability,

    COUNT(o.observation_id) FILTER (
        WHERE o.observed_value >= sr.interval_lower
          AND o.observed_value <= sr.interval_upper
    )::DOUBLE PRECISION
    /
    NULLIF(COUNT(o.observation_id), 0)
    AS empirical_probability,

    COUNT(o.observation_id) AS total_observations

FROM simulation_runs sr

JOIN distribution_registry dr
    USING (distribution_id)

LEFT JOIN observations o
    USING (simulation_id)

WHERE sr.status = 'COMPLETED'

GROUP BY
    sr.simulation_id,
    sr.simulation_name,
    sr.distribution_type,
    sr.interval_lower,
    sr.interval_upper,
    dr.distribution_type;


/* ============================================================================
   18. EMPIRICAL CDF EVALUATION
   ============================================================================ */

CREATE OR REPLACE FUNCTION empirical_cdf(
    p_simulation_id BIGINT,
    p_x DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_total BIGINT;
    v_below BIGINT;
BEGIN
    SELECT
        COUNT(*),
        COUNT(*) FILTER (
            WHERE observed_value <= p_x
        )
    INTO v_total, v_below
    FROM observations
    WHERE simulation_id = p_simulation_id;

    IF v_total = 0 THEN
        RAISE EXCEPTION
            'No observations exist for simulation %.',
            p_simulation_id;
    END IF;

    RETURN v_below::DOUBLE PRECISION / v_total;
END;
$$;


/* ============================================================================
   19. EMPIRICAL DISTRIBUTION DISTANCE
   ============================================================================ */

CREATE OR REPLACE FUNCTION empirical_ks_distance(
    p_simulation_id BIGINT
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_distribution_id BIGINT;
    v_total BIGINT;
    v_distance DOUBLE PRECISION;
BEGIN
    SELECT distribution_id
    INTO STRICT v_distribution_id
    FROM simulation_runs
    WHERE simulation_id = p_simulation_id
      AND status = 'COMPLETED';

    SELECT COUNT(*)
    INTO v_total
    FROM observations
    WHERE simulation_id = p_simulation_id;

    IF v_total = 0 THEN
        RAISE EXCEPTION 'No observations available.';
    END IF;

    WITH ordered AS (
        SELECT
            o.observed_value,

            ROW_NUMBER() OVER (
                ORDER BY o.observed_value, o.observation_id
            ) AS position

        FROM observations o

        WHERE o.simulation_id = p_simulation_id
    ),

    distances AS (
        SELECT
            ABS(
                position::DOUBLE PRECISION / v_total
                -
                distribution_cdf(
                    v_distribution_id,
                    observed_value
                )
            ) AS upper_distance,

            ABS(
                (position - 1)::DOUBLE PRECISION / v_total
                -
                distribution_cdf(
                    v_distribution_id,
                    observed_value
                )
            ) AS lower_distance

        FROM ordered
    )

    SELECT MAX(
        GREATEST(upper_distance, lower_distance)
    )
    INTO v_distance
    FROM distances;

    RETURN v_distance;
END;
$$;


/* ============================================================================
   20. QUANTILE COMPARISON REPORT
   ============================================================================ */

CREATE OR REPLACE VIEW distribution_quantile_report AS
SELECT
    d.distribution_id,
    d.distribution_name,
    p.probability,

    distribution_quantile(
        d.distribution_id,
        p.probability
    ) AS theoretical_quantile

FROM distribution_registry d

CROSS JOIN (
    VALUES
        (0.05::DOUBLE PRECISION),
        (0.25::DOUBLE PRECISION),
        (0.50::DOUBLE PRECISION),
        (0.75::DOUBLE PRECISION),
        (0.95::DOUBLE PRECISION)
) AS p(probability);


/* ============================================================================
   21. MONITORING AND ELIGIBILITY VIEW
   ============================================================================ */

CREATE OR REPLACE VIEW simulation_quality_report AS
SELECT
    sr.simulation_id,
    sr.simulation_name,
    sr.status,

    sr.requested_sample_count,

    COALESCE(ss.observation_count, 0) AS actual_sample_count,

    CASE
        WHEN sr.status <> 'COMPLETED'
            THEN 'NOT_EVALUATED'

        WHEN ss.observation_count <> sr.requested_sample_count
            THEN 'INVALID_SAMPLE_COUNT'

        WHEN ss.empirical_mean IS NULL
            THEN 'NO_STATISTICAL_DATA'

        ELSE 'VALIDATED'
    END AS quality_status,

    CASE
        WHEN sr.status = 'COMPLETED'
         AND ss.observation_count = sr.requested_sample_count
        THEN TRUE
        ELSE FALSE
    END AS eligible_for_reporting

FROM simulation_runs sr

LEFT JOIN simulation_statistics ss
    USING (simulation_id);


/* ============================================================================
   22. RETRIEVAL QUERIES
   ============================================================================ */

-- Distribution registry.
SELECT *
FROM distribution_parameters
ORDER BY distribution_id;

-- Simulation lifecycle.
SELECT
    simulation_id,
    simulation_name,
    status,
    requested_sample_count,
    created_at,
    started_at,
    completed_at,
    failure_reason
FROM simulation_runs
ORDER BY simulation_id;

-- Statistical descriptions.
SELECT *
FROM simulation_statistics
ORDER BY simulation_id;

-- Probability comparison.
SELECT *
FROM interval_probability_report
ORDER BY simulation_id;

-- Quality validation.
SELECT *
FROM simulation_quality_report
ORDER BY simulation_id;


/* ============================================================================
   23. PDF AND CDF EVALUATION
   ============================================================================ */

SELECT
    distribution_name,
    distribution_type,

    distribution_pdf(distribution_id, 50) AS pdf_at_50,

    distribution_cdf(distribution_id, 50) AS cdf_at_50

FROM distribution_registry
ORDER BY distribution_id;


/* ============================================================================
   24. QUANTILE EVALUATION
   ============================================================================ */

SELECT
    distribution_name,
    probability,
    theoretical_quantile
FROM distribution_quantile_report
ORDER BY distribution_id, probability;


/* ============================================================================
   25. EMPIRICAL CDF AND KS REPORTING
   ============================================================================ */

SELECT
    sr.simulation_id,
    sr.simulation_name,

    empirical_cdf(
        sr.simulation_id,
        50
    ) AS empirical_cdf_at_50,

    distribution_cdf(
        sr.distribution_id,
        50
    ) AS theoretical_cdf_at_50,

    empirical_ks_distance(
        sr.simulation_id
    ) AS ks_distance

FROM simulation_runs sr

WHERE sr.status = 'COMPLETED'
ORDER BY sr.simulation_id;


/* ============================================================================
   26. DISTRIBUTION-SPECIFIC ANALYSIS
   ============================================================================ */

-- Uniform distribution:
-- Every equal-width interval has the same probability.

SELECT
    uniform_pdf(50, 0, 100) AS density_at_50,

    uniform_cdf(50, 0, 100) AS cumulative_probability,

    uniform_quantile(0.95, 0, 100) AS ninety_fifth_percentile;


-- Exponential distribution:
-- Constant hazard rate and memoryless survival.

SELECT
    exponential_pdf(5, 0.2) AS density_at_5,

    exponential_cdf(5, 0.2) AS cumulative_probability,

    exponential_quantile(0.95, 0.2) AS ninety_fifth_percentile,

    EXP(-0.2 * 5) AS survival_probability;


-- Normal distribution:
-- Symmetric measurement variation.

SELECT
    normal_pdf(50, 50, 10) AS density_at_mean,

    normal_cdf(60, 50, 10) AS probability_below_60,

    normal_quantile(0.975, 50, 10) AS ninety_seventh_point_fifth_percentile;


/* ============================================================================
   27. TRANSACTIONAL FAILURE HANDLING
   ============================================================================ */

/*
 * A failed operation inside a PostgreSQL transaction rolls back its
 * associated changes. The following block demonstrates a savepoint.
 */

SAVEPOINT analysis_checkpoint;

SELECT
    simulation_name,
    empirical_mean,
    empirical_variance
FROM simulation_statistics
WHERE status = 'COMPLETED';

RELEASE SAVEPOINT analysis_checkpoint;


/* ============================================================================
   28. OPERATIONAL INDEX AND STORAGE NOTES
   ============================================================================ */

/*
 * Existing indexes support:
 *
 * 1. Simulation lookup by distribution and lifecycle state.
 * 2. Observation retrieval by simulation.
 * 3. Observation ordering and range filtering.
 * 4. Uniqueness of observation sequence numbers.
 *
 * For large production observation tables:
 * - Consider partitioning observations by simulation or time.
 * - Analyze query plans before adding more indexes.
 * - Batch inserts instead of inserting individual rows.
 * - Restrict observation updates after simulation completion.
 * - Use database roles to restrict direct writes.
 * - Keep statistical aggregates in materialized views when
 *   reporting volume justifies their maintenance cost.
 */


/* ============================================================================
   29. FINAL DATA INTEGRITY CHECKS
   ============================================================================ */

DO $$
DECLARE
    v_invalid_count BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid_count
    FROM simulation_runs sr
    LEFT JOIN observations o
        USING (simulation_id)
    WHERE sr.status = 'COMPLETED'
    GROUP BY sr.simulation_id, sr.requested_sample_count
    HAVING COUNT(o.observation_id) <> sr.requested_sample_count;

    IF v_invalid_count IS NOT NULL THEN
        RAISE EXCEPTION
            'Completed simulation sample-count integrity failure.';
    END IF;
END;
$$;

COMMIT;
