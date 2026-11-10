-- ============================================================================
-- LAW OF LARGE NUMBERS
-- PostgreSQL statistical experiment and convergence analysis database
--
-- Models:
--   1. Probability distributions and their theoretical moments.
--   2. Statistical experiments.
--   3. Independent Monte Carlo trials.
--   4. Sample means and squared deviations.
--   5. Weak Law of Large Numbers evaluation.
--   6. Strong Law of Large Numbers running observations.
--   7. Chebyshev probability bounds.
--   8. Statistical summaries and convergence reporting.
--
-- Compatible with PostgreSQL 14+.
-- ============================================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS probability;
SET search_path TO probability, public;

-- --------------------------------------------------------------------------
-- ENUM TYPES
-- --------------------------------------------------------------------------

CREATE TYPE distribution_type AS ENUM (
    'BERNOULLI',
    'UNIFORM',
    'NORMAL',
    'CONSTANT'
);

CREATE TYPE experiment_status AS ENUM (
    'CREATED',
    'RUNNING',
    'COMPLETED',
    'FAILED',
    'CANCELLED'
);

CREATE TYPE statistical_law AS ENUM (
    'WEAK',
    'STRONG'
);

CREATE TYPE trial_status AS ENUM (
    'VALID',
    'REJECTED'
);

-- --------------------------------------------------------------------------
-- DISTRIBUTIONS
-- --------------------------------------------------------------------------

CREATE TABLE distributions (
    distribution_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    distribution_name VARCHAR(120) NOT NULL UNIQUE,
    distribution_kind distribution_type NOT NULL,
    theoretical_mean DOUBLE PRECISION NOT NULL,
    theoretical_variance DOUBLE PRECISION NOT NULL,
    parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_distribution_mean
        CHECK (
            theoretical_mean NOT IN (
                'Infinity'::float8,
                '-Infinity'::float8,
                'NaN'::float8
            )
        ),

    CONSTRAINT valid_distribution_variance
        CHECK (
            theoretical_variance >= 0
            AND theoretical_variance NOT IN (
                'Infinity'::float8,
                'NaN'::float8
            )
        ),

    CONSTRAINT parameters_must_be_object
        CHECK (jsonb_typeof(parameters) = 'object')
);

INSERT INTO distributions (
    distribution_name,
    distribution_kind,
    theoretical_mean,
    theoretical_variance,
    parameters
)
VALUES
(
    'Bernoulli(0.5)',
    'BERNOULLI',
    0.5,
    0.25,
    '{"p": 0.5}'::jsonb
),
(
    'Uniform(0,1)',
    'UNIFORM',
    0.5,
    0.08333333333333333,
    '{"minimum": 0, "maximum": 1}'::jsonb
),
(
    'Normal(0,1)',
    'NORMAL',
    0,
    1,
    '{"mu": 0, "sigma": 1}'::jsonb
),
(
    'Constant(7)',
    'CONSTANT',
    7,
    0,
    '{"value": 7}'::jsonb
);

-- --------------------------------------------------------------------------
-- EXPERIMENTS
-- --------------------------------------------------------------------------

CREATE TABLE experiments (
    experiment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_name VARCHAR(180) NOT NULL,

    distribution_id BIGINT NOT NULL
        REFERENCES distributions(distribution_id),

    law statistical_law NOT NULL,

    status experiment_status NOT NULL DEFAULT 'CREATED',

    tolerance DOUBLE PRECISION NOT NULL DEFAULT 0.05,

    trial_count INTEGER NOT NULL DEFAULT 1000,

    random_seed BIGINT NOT NULL DEFAULT 42,

    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    failure_reason TEXT,

    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    CONSTRAINT valid_tolerance
        CHECK (
            tolerance > 0
            AND tolerance NOT IN (
                'Infinity'::float8,
                'NaN'::float8
            )
        ),

    CONSTRAINT valid_trial_count
        CHECK (trial_count > 0),

    CONSTRAINT valid_experiment_times
        CHECK (
            completed_at IS NULL
            OR started_at IS NULL
            OR completed_at >= started_at
        ),

    CONSTRAINT metadata_object
        CHECK (jsonb_typeof(metadata) = 'object')
);

-- --------------------------------------------------------------------------
-- SAMPLE SIZE CONFIGURATION
-- --------------------------------------------------------------------------

CREATE TABLE experiment_sample_sizes (
    sample_size_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id)
        ON DELETE CASCADE,

    sample_size INTEGER NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_sample_size
        CHECK (sample_size > 0),

    CONSTRAINT unique_experiment_sample_size
        UNIQUE (experiment_id, sample_size)
);

-- --------------------------------------------------------------------------
-- MONTE CARLO TRIALS
-- --------------------------------------------------------------------------

CREATE TABLE monte_carlo_trials (
    trial_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id)
        ON DELETE CASCADE,

    sample_size INTEGER NOT NULL,

    trial_number INTEGER NOT NULL,

    sample_mean DOUBLE PRECISION NOT NULL,

    absolute_error DOUBLE PRECISION NOT NULL,

    squared_error DOUBLE PRECISION NOT NULL,

    deviation_detected BOOLEAN NOT NULL,

    status trial_status NOT NULL DEFAULT 'VALID',

    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_sample_size
        CHECK (sample_size > 0),

    CONSTRAINT valid_trial_number
        CHECK (trial_number > 0),

    CONSTRAINT valid_sample_mean
        CHECK (
            sample_mean NOT IN (
                'Infinity'::float8,
                '-Infinity'::float8,
                'NaN'::float8
            )
        ),

    CONSTRAINT valid_absolute_error
        CHECK (
            absolute_error >= 0
            AND absolute_error NOT IN (
                'Infinity'::float8,
                'NaN'::float8
            )
        ),

    CONSTRAINT valid_squared_error
        CHECK (
            squared_error >= 0
            AND squared_error NOT IN (
                'Infinity'::float8,
                'NaN'::float8
            )
        ),

    CONSTRAINT unique_trial_execution
        UNIQUE (experiment_id, sample_size, trial_number)
);

-- --------------------------------------------------------------------------
-- STRONG LAW RUNNING OBSERVATIONS
-- --------------------------------------------------------------------------

CREATE TABLE running_observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id)
        ON DELETE CASCADE,

    observation_index BIGINT NOT NULL,

    observation_value DOUBLE PRECISION NOT NULL,

    running_sum DOUBLE PRECISION NOT NULL,

    running_mean DOUBLE PRECISION NOT NULL,

    absolute_error DOUBLE PRECISION NOT NULL,

    observed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_observation_index
        CHECK (observation_index > 0),

    CONSTRAINT unique_running_observation
        UNIQUE (experiment_id, observation_index),

    CONSTRAINT finite_observation_values
        CHECK (
            observation_value NOT IN (
                'Infinity'::float8,
                '-Infinity'::float8,
                'NaN'::float8
            )
            AND running_mean NOT IN (
                'Infinity'::float8,
                '-Infinity'::float8,
                'NaN'::float8
            )
            AND absolute_error >= 0
        )
);

-- --------------------------------------------------------------------------
-- PERFORMANCE INDEXES
-- --------------------------------------------------------------------------

CREATE INDEX idx_experiments_status
    ON experiments(status, created_at DESC);

CREATE INDEX idx_experiments_distribution
    ON experiments(distribution_id, law);

CREATE INDEX idx_trials_experiment_sample
    ON monte_carlo_trials(
        experiment_id,
        sample_size,
        trial_number
    );

CREATE INDEX idx_trials_deviation
    ON monte_carlo_trials(experiment_id, deviation_detected)
    WHERE status = 'VALID';

CREATE INDEX idx_running_observations_sequence
    ON running_observations(
        experiment_id,
        observation_index
    );

CREATE INDEX idx_experiment_metadata
    ON experiments USING GIN(metadata);

-- --------------------------------------------------------------------------
-- EXPERIMENT VALIDATION TRIGGER
-- --------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_experiment_trial()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_mean DOUBLE PRECISION;
    v_tolerance DOUBLE PRECISION;
    v_expected_error DOUBLE PRECISION;
BEGIN
    SELECT
        d.theoretical_mean,
        e.tolerance
    INTO
        v_mean,
        v_tolerance
    FROM experiments e
    JOIN distributions d
      ON d.distribution_id = e.distribution_id
    WHERE e.experiment_id = NEW.experiment_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Experiment % does not exist',
            NEW.experiment_id;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM experiment_sample_sizes s
        WHERE s.experiment_id = NEW.experiment_id
          AND s.sample_size = NEW.sample_size
    ) THEN
        RAISE EXCEPTION
            'Sample size % is not configured for experiment %',
            NEW.sample_size,
            NEW.experiment_id;
    END IF;

    v_expected_error := abs(NEW.sample_mean - v_mean);

    IF abs(NEW.absolute_error - v_expected_error) > 1e-8 THEN
        RAISE EXCEPTION
            'Absolute error does not match the sample mean';
    END IF;

    IF abs(
        NEW.squared_error -
        (v_expected_error * v_expected_error)
    ) > 1e-8 THEN
        RAISE EXCEPTION
            'Squared error does not match absolute error';
    END IF;

    IF NEW.deviation_detected <>
        (v_expected_error >= v_tolerance) THEN
        RAISE EXCEPTION
            'Deviation flag does not match experiment tolerance';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_experiment_trial
BEFORE INSERT OR UPDATE ON monte_carlo_trials
FOR EACH ROW
EXECUTE FUNCTION validate_experiment_trial();

-- --------------------------------------------------------------------------
-- RUNNING OBSERVATION VALIDATION
-- --------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_running_observation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_mean DOUBLE PRECISION;
    v_previous_index BIGINT;
BEGIN
    SELECT d.theoretical_mean
    INTO v_mean
    FROM experiments e
    JOIN distributions d
      ON d.distribution_id = e.distribution_id
    WHERE e.experiment_id = NEW.experiment_id
      AND e.law = 'STRONG';

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Strong-law experiment % does not exist',
            NEW.experiment_id;
    END IF;

    IF abs(
        NEW.running_mean -
        NEW.running_sum / NEW.observation_index
    ) > 1e-8 THEN
        RAISE EXCEPTION
            'Running mean is inconsistent with running sum';
    END IF;

    IF abs(
        NEW.absolute_error -
        abs(NEW.running_mean - v_mean)
    ) > 1e-8 THEN
        RAISE EXCEPTION
            'Running error is inconsistent';
    END IF;

    SELECT max(observation_index)
    INTO v_previous_index
    FROM running_observations
    WHERE experiment_id = NEW.experiment_id;

    IF v_previous_index IS NOT NULL
       AND NEW.observation_index <= v_previous_index THEN
        RAISE EXCEPTION
            'Observation index must increase monotonically';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_running_observation
BEFORE INSERT OR UPDATE ON running_observations
FOR EACH ROW
EXECUTE FUNCTION validate_running_observation();

-- --------------------------------------------------------------------------
-- EXPERIMENT STATE TRANSITION VALIDATION
-- --------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_experiment_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status <> OLD.status THEN
        IF NOT (
            (OLD.status = 'CREATED'
                AND NEW.status IN ('RUNNING', 'CANCELLED'))
            OR
            (OLD.status = 'RUNNING'
                AND NEW.status IN ('COMPLETED', 'FAILED', 'CANCELLED'))
        ) THEN
            RAISE EXCEPTION
                'Invalid experiment transition: % -> %',
                OLD.status,
                NEW.status;
        END IF;
    END IF;

    IF NEW.status = 'RUNNING'
       AND NEW.started_at IS NULL THEN
        NEW.started_at := CURRENT_TIMESTAMP;
    END IF;

    IF NEW.status IN ('COMPLETED', 'FAILED', 'CANCELLED')
       AND NEW.completed_at IS NULL THEN
        NEW.completed_at := CURRENT_TIMESTAMP;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_experiment_state_transition
BEFORE UPDATE ON experiments
FOR EACH ROW
EXECUTE FUNCTION validate_experiment_transition();

-- --------------------------------------------------------------------------
-- CHEBYSHEV BOUND FUNCTION
-- --------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION chebyshev_probability_bound(
    p_variance DOUBLE PRECISION,
    p_sample_size INTEGER,
    p_epsilon DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF p_variance < 0
       OR p_sample_size <= 0
       OR p_epsilon <= 0 THEN
        RAISE EXCEPTION 'Invalid Chebyshev parameters';
    END IF;

    RETURN LEAST(
        1.0,
        p_variance /
        (p_sample_size * p_epsilon * p_epsilon)
    );
END;
$$;

-- --------------------------------------------------------------------------
-- CREATE EXPERIMENT PROCEDURE
-- --------------------------------------------------------------------------

CREATE OR REPLACE PROCEDURE create_experiment(
    p_name VARCHAR,
    p_distribution_id BIGINT,
    p_law statistical_law,
    p_tolerance DOUBLE PRECISION,
    p_trials INTEGER,
    p_sample_sizes INTEGER[],
    INOUT p_experiment_id BIGINT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_size INTEGER;
BEGIN
    IF p_name IS NULL OR length(trim(p_name)) = 0 THEN
        RAISE EXCEPTION 'Experiment name cannot be empty';
    END IF;

    IF p_tolerance <= 0
       OR p_tolerance IN (
           'Infinity'::float8,
           'NaN'::float8
       ) THEN
        RAISE EXCEPTION 'Invalid tolerance';
    END IF;

    IF p_trials <= 0 THEN
        RAISE EXCEPTION 'Trial count must be positive';
    END IF;

    IF cardinality(p_sample_sizes) = 0 THEN
        RAISE EXCEPTION 'At least one sample size is required';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM unnest(p_sample_sizes) AS s(value)
        WHERE value <= 0
    ) THEN
        RAISE EXCEPTION 'Sample sizes must be positive';
    END IF;

    IF (
        SELECT count(DISTINCT value)
        FROM unnest(p_sample_sizes) AS s(value)
    ) <> cardinality(p_sample_sizes) THEN
        RAISE EXCEPTION 'Sample sizes must be unique';
    END IF;

    INSERT INTO experiments (
        experiment_name,
        distribution_id,
        law,
        tolerance,
        trial_count
    )
    VALUES (
        p_name,
        p_distribution_id,
        p_law,
        p_tolerance,
        p_trials
    )
    RETURNING experiment_id INTO p_experiment_id;

    FOREACH v_size IN ARRAY p_sample_sizes LOOP
        INSERT INTO experiment_sample_sizes (
            experiment_id,
            sample_size
        )
        VALUES (
            p_experiment_id,
            v_size
        );
    END LOOP;
END;
$$;

-- --------------------------------------------------------------------------
-- WEAK LAW REPORTING VIEW
-- --------------------------------------------------------------------------

CREATE OR REPLACE VIEW weak_law_summary AS
SELECT
    e.experiment_id,
    e.experiment_name,
    d.distribution_name,
    d.theoretical_mean,
    d.theoretical_variance,
    e.tolerance,
    t.sample_size,
    count(*) AS valid_trials,

    avg(t.sample_mean) AS average_sample_mean,

    avg(t.absolute_error) AS mean_absolute_error,

    avg(t.squared_error) AS empirical_mean_squared_error,

    avg(t.deviation_detected::INTEGER::DOUBLE PRECISION)
        AS observed_deviation_probability,

    chebyshev_probability_bound(
        d.theoretical_variance,
        t.sample_size,
        e.tolerance
    ) AS chebyshev_upper_bound

FROM experiments e
JOIN distributions d
  ON d.distribution_id = e.distribution_id
JOIN monte_carlo_trials t
  ON t.experiment_id = e.experiment_id

WHERE e.law = 'WEAK'
  AND t.status = 'VALID'

GROUP BY
    e.experiment_id,
    e.experiment_name,
    d.distribution_name,
    d.theoretical_mean,
    d.theoretical_variance,
    e.tolerance,
    t.sample_size;

-- --------------------------------------------------------------------------
-- STRONG LAW REPORTING VIEW
-- --------------------------------------------------------------------------

CREATE OR REPLACE VIEW strong_law_summary AS
SELECT
    e.experiment_id,
    e.experiment_name,
    d.distribution_name,
    r.observation_index,
    r.observation_value,
    r.running_mean,
    d.theoretical_mean,
    r.absolute_error
FROM experiments e
JOIN distributions d
  ON d.distribution_id = e.distribution_id
JOIN running_observations r
  ON r.experiment_id = e.experiment_id
WHERE e.law = 'STRONG';

-- --------------------------------------------------------------------------
-- SAMPLE DATA: WEAK LAW EXPERIMENT
-- --------------------------------------------------------------------------

DO $$
DECLARE
    v_distribution BIGINT;
    v_experiment BIGINT;
BEGIN
    SELECT distribution_id
    INTO v_distribution
    FROM distributions
    WHERE distribution_name = 'Bernoulli(0.5)';

    CALL create_experiment(
        'Bernoulli WLLN demonstration',
        v_distribution,
        'WEAK',
        0.05,
        5,
        ARRAY[10, 100, 1000],
        v_experiment
    );

    UPDATE experiments
    SET status = 'RUNNING'
    WHERE experiment_id = v_experiment;

    -- Each row represents an independent Monte Carlo experiment.
    -- These deterministic values are chosen to demonstrate decreasing error.

    INSERT INTO monte_carlo_trials (
        experiment_id,
        sample_size,
        trial_number,
        sample_mean,
        absolute_error,
        squared_error,
        deviation_detected
    )
    VALUES
    (v_experiment, 10, 1, 0.50, 0.00, 0.0000, FALSE),
    (v_experiment, 10, 2, 0.60, 0.10, 0.0100, TRUE),
    (v_experiment, 10, 3, 0.40, 0.10, 0.0100, TRUE),
    (v_experiment, 10, 4, 0.50, 0.00, 0.0000, FALSE),
    (v_experiment, 10, 5, 0.50, 0.00, 0.0000, FALSE),

    (v_experiment, 100, 1, 0.50, 0.00, 0.0000, FALSE),
    (v_experiment, 100, 2, 0.52, 0.02, 0.0004, FALSE),
    (v_experiment, 100, 3, 0.49, 0.01, 0.0001, FALSE),
    (v_experiment, 100, 4, 0.51, 0.01, 0.0001, FALSE),
    (v_experiment, 100, 5, 0.50, 0.00, 0.0000, FALSE),

    (v_experiment, 1000, 1, 0.500, 0.000, 0.000000, FALSE),
    (v_experiment, 1000, 2, 0.503, 0.003, 0.000009, FALSE),
    (v_experiment, 1000, 3, 0.498, 0.002, 0.000004, FALSE),
    (v_experiment, 1000, 4, 0.501, 0.001, 0.000001, FALSE),
    (v_experiment, 1000, 5, 0.500, 0.000, 0.000000, FALSE);

    UPDATE experiments
    SET status = 'COMPLETED'
    WHERE experiment_id = v_experiment;
END;
$$;

-- --------------------------------------------------------------------------
-- SAMPLE DATA: STRONG LAW EXPERIMENT
-- --------------------------------------------------------------------------

DO $$
DECLARE
    v_distribution BIGINT;
    v_experiment BIGINT;
    v_mean DOUBLE PRECISION := 0.5;
    v_running_sum DOUBLE PRECISION := 0;
    v_value DOUBLE PRECISION;
    v_n INTEGER;
BEGIN
    SELECT distribution_id
    INTO v_distribution
    FROM distributions
    WHERE distribution_name = 'Bernoulli(0.5)';

    CALL create_experiment(
        'Bernoulli SLLN running sequence',
        v_distribution,
        'STRONG',
        0.05,
        1,
        ARRAY[1, 2, 5, 10, 50, 100],
        v_experiment
    );

    UPDATE experiments
    SET status = 'RUNNING'
    WHERE experiment_id = v_experiment;

    -- A deterministic illustrative sequence of Bernoulli observations.
    FOR v_n IN 1..100 LOOP
        v_value := CASE
            WHEN v_n % 2 = 0 THEN 1.0
            ELSE 0.0
        END;

        v_running_sum := v_running_sum + v_value;

        IF v_n IN (1, 2, 5, 10, 50, 100) THEN
            INSERT INTO running_observations (
                experiment_id,
                observation_index,
                observation_value,
                running_sum,
                running_mean,
                absolute_error
            )
            VALUES (
                v_experiment,
                v_n,
                v_value,
                v_running_sum,
                v_running_sum / v_n,
                abs(v_running_sum / v_n - v_mean)
            );
        END IF;
    END LOOP;

    UPDATE experiments
    SET status = 'COMPLETED'
    WHERE experiment_id = v_experiment;
END;
$$;

-- --------------------------------------------------------------------------
-- RETRIEVAL: AVAILABLE DISTRIBUTIONS
-- --------------------------------------------------------------------------

SELECT
    distribution_name,
    distribution_kind,
    theoretical_mean,
    theoretical_variance,
    parameters
FROM distributions
ORDER BY distribution_id;

-- --------------------------------------------------------------------------
-- RETRIEVAL: EXPERIMENT HISTORY
-- --------------------------------------------------------------------------

SELECT
    experiment_id,
    experiment_name,
    law,
    status,
    trial_count,
    tolerance,
    started_at,
    completed_at
FROM experiments
ORDER BY created_at;

-- --------------------------------------------------------------------------
-- WLLN EVALUATION
-- --------------------------------------------------------------------------

SELECT
    experiment_name,
    distribution_name,
    sample_size,
    valid_trials,
    round(average_sample_mean::NUMERIC, 6) AS average_mean,
    round(mean_absolute_error::NUMERIC, 6) AS mae,
    round(empirical_mean_squared_error::NUMERIC, 8) AS mse,
    round(observed_deviation_probability::NUMERIC, 6)
        AS observed_probability,
    round(chebyshev_upper_bound::NUMERIC, 6)
        AS theoretical_upper_bound
FROM weak_law_summary
ORDER BY experiment_id, sample_size;

-- --------------------------------------------------------------------------
-- SLLN CONVERGENCE REPORT
-- --------------------------------------------------------------------------

SELECT
    experiment_name,
    observation_index,
    round(running_mean::NUMERIC, 6) AS running_mean,
    round(theoretical_mean::NUMERIC, 6) AS population_mean,
    round(absolute_error::NUMERIC, 6) AS absolute_error
FROM strong_law_summary
ORDER BY experiment_id, observation_index;

-- --------------------------------------------------------------------------
-- AGGREGATION: SAMPLE SIZE AND ERROR RELATIONSHIP
-- --------------------------------------------------------------------------

SELECT
    sample_size,
    count(*) AS experiment_count,
    avg(absolute_error) AS average_absolute_error,
    sqrt(avg(squared_error)) AS root_mean_squared_error,
    max(absolute_error) AS maximum_absolute_error
FROM monte_carlo_trials
WHERE status = 'VALID'
GROUP BY sample_size
ORDER BY sample_size;

-- --------------------------------------------------------------------------
-- CTE: EMPIRICAL VERSUS THEORETICAL PROBABILITY
-- --------------------------------------------------------------------------

WITH probability_comparison AS (
    SELECT
        experiment_id,
        experiment_name,
        sample_size,
        observed_deviation_probability,
        chebyshev_upper_bound
    FROM weak_law_summary
),
evaluation AS (
    SELECT
        *,
        observed_deviation_probability
            <= chebyshev_upper_bound AS bound_satisfied
    FROM probability_comparison
)
SELECT
    experiment_name,
    sample_size,
    observed_deviation_probability,
    chebyshev_upper_bound,
    bound_satisfied
FROM evaluation
ORDER BY experiment_id, sample_size;

-- --------------------------------------------------------------------------
-- VALIDATION: SAMPLE COUNT CONSISTENCY
-- --------------------------------------------------------------------------

SELECT
    e.experiment_id,
    e.experiment_name,
    s.sample_size,
    e.trial_count AS expected_trials,
    count(t.trial_id) AS recorded_trials,
    count(t.trial_id) = e.trial_count AS trial_count_valid
FROM experiments e
JOIN experiment_sample_sizes s
  ON s.experiment_id = e.experiment_id
LEFT JOIN monte_carlo_trials t
  ON t.experiment_id = e.experiment_id
 AND t.sample_size = s.sample_size
WHERE e.law = 'WEAK'
GROUP BY
    e.experiment_id,
    e.experiment_name,
    s.sample_size,
    e.trial_count
ORDER BY e.experiment_id, s.sample_size;

-- --------------------------------------------------------------------------
-- ELIGIBILITY: CAN THE EXPERIMENT BE MARKED COMPLETED?
-- --------------------------------------------------------------------------

SELECT
    e.experiment_id,
    e.experiment_name,
    e.status,
    CASE
        WHEN e.status <> 'RUNNING'
            THEN FALSE
        WHEN e.law = 'WEAK'
             AND NOT EXISTS (
                 SELECT 1
                 FROM experiment_sample_sizes s
                 WHERE s.experiment_id = e.experiment_id
                   AND (
                       SELECT count(*)
                       FROM monte_carlo_trials t
                       WHERE t.experiment_id = e.experiment_id
                         AND t.sample_size = s.sample_size
                         AND t.status = 'VALID'
                   ) < e.trial_count
             )
            THEN TRUE
        WHEN e.law = 'STRONG'
             AND EXISTS (
                 SELECT 1
                 FROM running_observations r
                 WHERE r.experiment_id = e.experiment_id
             )
            THEN TRUE
        ELSE FALSE
    END AS completion_eligible
FROM experiments e
ORDER BY e.experiment_id;

-- --------------------------------------------------------------------------
-- FAILURE CASE: INVALID CHEBYSHEV PARAMETERS
-- --------------------------------------------------------------------------

DO $$
BEGIN
    BEGIN
        PERFORM chebyshev_probability_bound(0.25, 0, 0.05);
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Invalid sample size correctly rejected: %',
            SQLERRM;
    END;
END;
$$;

-- --------------------------------------------------------------------------
-- FAILURE CASE: INVALID STATE TRANSITION
-- --------------------------------------------------------------------------

DO $$
DECLARE
    v_id BIGINT;
BEGIN
    SELECT experiment_id
    INTO v_id
    FROM experiments
    ORDER BY experiment_id
    LIMIT 1;

    BEGIN
        UPDATE experiments
        SET status = 'RUNNING'
        WHERE experiment_id = v_id;

    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Invalid transition correctly rejected: %',
            SQLERRM;
    END;
END;
$$;

-- --------------------------------------------------------------------------
-- TRANSACTION DEMONSTRATION
-- --------------------------------------------------------------------------

SAVEPOINT statistical_checkpoint;

-- A rejected sample cannot silently corrupt an existing experiment.
DO $$
DECLARE
    v_id BIGINT;
BEGIN
    SELECT experiment_id
    INTO v_id
    FROM experiments
    WHERE law = 'WEAK'
    ORDER BY experiment_id
    LIMIT 1;

    BEGIN
        INSERT INTO monte_carlo_trials (
            experiment_id,
            sample_size,
            trial_number,
            sample_mean,
            absolute_error,
            squared_error,
            deviation_detected
        )
        VALUES (
            v_id,
            10,
            999,
            0.90,
            0.01,
            0.0001,
            FALSE
        );
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Invalid statistical record rejected: %',
            SQLERRM;
    END;
END;
$$;

RELEASE SAVEPOINT statistical_checkpoint;

COMMIT;

-- ============================================================================
-- END OF SCRIPT
-- ============================================================================
