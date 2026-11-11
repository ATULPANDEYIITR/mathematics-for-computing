/*
 * CENTRAL LIMIT THEOREM
 * Sampling Distributions and Approximation Techniques
 *
 * PostgreSQL 15+
 *
 * Models:
 * - Statistical experiments
 * - Population distributions
 * - Sampling configurations
 * - Repeated random samples
 * - Individual observations
 * - Sample-mean distributions
 * - Standard errors
 * - Normal approximation
 * - Confidence intervals
 * - Bootstrap estimates
 * - Simulation validation
 * - Statistical reporting
 *
 * Run as a database role with schema creation privileges.
 */

BEGIN;

CREATE SCHEMA IF NOT EXISTS clt;

SET search_path TO clt, public;

-- ------------------------------------------------------------
-- 1. Domain types
-- ------------------------------------------------------------

CREATE TYPE distribution_type AS ENUM (
    'BERNOULLI',
    'EXPONENTIAL',
    'UNIFORM',
    'SKEWED'
);

CREATE TYPE sampling_method AS ENUM (
    'WITH_REPLACEMENT',
    'WITHOUT_REPLACEMENT'
);

CREATE TYPE experiment_status AS ENUM (
    'CREATED',
    'RUNNING',
    'COMPLETED',
    'FAILED'
);

-- ------------------------------------------------------------
-- 2. Experiment metadata
-- ------------------------------------------------------------

CREATE TABLE experiment (
    experiment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_name VARCHAR(150) NOT NULL UNIQUE,

    distribution distribution_type NOT NULL,

    population_size INTEGER NOT NULL
        CHECK (population_size >= 2),

    population_mean NUMERIC(20, 8) NOT NULL,

    population_variance NUMERIC(20, 8) NOT NULL
        CHECK (population_variance >= 0),

    population_sd NUMERIC(20, 8)
        GENERATED ALWAYS AS (
            SQRT(population_variance)
        ) STORED,

    sampling_method sampling_method NOT NULL
        DEFAULT 'WITH_REPLACEMENT',

    sample_size INTEGER NOT NULL
        CHECK (sample_size > 0),

    repetitions INTEGER NOT NULL
        CHECK (repetitions >= 2),

    random_seed BIGINT NOT NULL DEFAULT 42,

    confidence_level NUMERIC(5, 4) NOT NULL
        DEFAULT 0.9500
        CHECK (
            confidence_level > 0
            AND confidence_level < 1
        ),

    status experiment_status NOT NULL DEFAULT 'CREATED',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMPTZ,

    CHECK (
        sampling_method <> 'WITHOUT_REPLACEMENT'
        OR sample_size <= population_size
    ),

    CHECK (
        population_variance <> 0
        OR population_mean IS NOT NULL
    )
);

-- ------------------------------------------------------------
-- 3. Experiment execution
-- ------------------------------------------------------------

CREATE TABLE sampling_run (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_id BIGINT NOT NULL
        REFERENCES experiment(experiment_id)
        ON DELETE CASCADE,

    run_number INTEGER NOT NULL CHECK (run_number > 0),

    sample_size INTEGER NOT NULL CHECK (sample_size > 0),

    observed_count INTEGER NOT NULL DEFAULT 0
        CHECK (observed_count >= 0),

    sample_mean NUMERIC(20, 8),

    sample_variance NUMERIC(20, 8),

    sample_standard_error NUMERIC(20, 8),

    lower_confidence_limit NUMERIC(20, 8),

    upper_confidence_limit NUMERIC(20, 8),

    completed BOOLEAN NOT NULL DEFAULT FALSE,

    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMPTZ,

    UNIQUE (experiment_id, run_number),

    CHECK (
        lower_confidence_limit IS NULL
        OR upper_confidence_limit IS NULL
        OR lower_confidence_limit <= upper_confidence_limit
    )
);

-- ------------------------------------------------------------
-- 4. Individual observations
-- ------------------------------------------------------------

CREATE TABLE sample_observation (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    run_id BIGINT NOT NULL
        REFERENCES sampling_run(run_id)
        ON DELETE CASCADE,

    observation_number INTEGER NOT NULL
        CHECK (observation_number > 0),

    observed_value NUMERIC(20, 8) NOT NULL,

    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (run_id, observation_number)
);

-- ------------------------------------------------------------
-- 5. Sampling-distribution summary
-- ------------------------------------------------------------

CREATE TABLE sampling_distribution_summary (
    summary_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    experiment_id BIGINT NOT NULL
        REFERENCES experiment(experiment_id)
        ON DELETE CASCADE,

    sample_size INTEGER NOT NULL,

    number_of_runs INTEGER NOT NULL,

    empirical_mean NUMERIC(20, 8) NOT NULL,

    empirical_variance NUMERIC(20, 8) NOT NULL,

    empirical_standard_deviation NUMERIC(20, 8) NOT NULL,

    theoretical_standard_error NUMERIC(20, 8) NOT NULL,

    relative_se_error NUMERIC(20, 8),

    ks_distance NUMERIC(20, 8),

    confidence_interval_coverage NUMERIC(10, 8),

    calculated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (experiment_id, sample_size),

    CHECK (number_of_runs >= 2),
    CHECK (empirical_variance >= 0),
    CHECK (empirical_standard_deviation >= 0),
    CHECK (theoretical_standard_error >= 0),
    CHECK (
        confidence_interval_coverage IS NULL
        OR confidence_interval_coverage BETWEEN 0 AND 1
    )
);

-- ------------------------------------------------------------
-- 6. Indexes
-- ------------------------------------------------------------

CREATE INDEX idx_experiment_status
    ON experiment(status, created_at DESC);

CREATE INDEX idx_sampling_run_experiment
    ON sampling_run(experiment_id, run_number);

CREATE INDEX idx_observation_run
    ON sample_observation(run_id, observation_number);

CREATE INDEX idx_observation_value
    ON sample_observation(observed_value);

CREATE INDEX idx_summary_experiment
    ON sampling_distribution_summary(
        experiment_id,
        sample_size
    );

-- ------------------------------------------------------------
-- 7. Standard normal CDF
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION normal_cdf(
    p_z DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE SQL
IMMUTABLE
STRICT
PARALLEL SAFE
AS $$
    SELECT 0.5 * ERFC(-p_z / SQRT(2.0));
$$;

-- ------------------------------------------------------------
-- 8. Theoretical standard error
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION theoretical_standard_error(
    p_population_sd NUMERIC,
    p_population_size INTEGER,
    p_sample_size INTEGER,
    p_method sampling_method
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    v_result NUMERIC;
BEGIN
    IF p_population_size < 2 OR p_sample_size < 1 THEN
        RAISE EXCEPTION 'Invalid population or sample size.';
    END IF;

    IF p_method = 'WITHOUT_REPLACEMENT'
       AND p_sample_size > p_population_size THEN
        RAISE EXCEPTION 'Sample exceeds finite population.';
    END IF;

    v_result :=
        p_population_sd / SQRT(p_sample_size::NUMERIC);

    IF p_method = 'WITHOUT_REPLACEMENT' THEN
        v_result := v_result * SQRT(
            (p_population_size - p_sample_size)::NUMERIC /
            (p_population_size - 1)
        );
    END IF;

    RETURN v_result;
END;
$$;

-- ------------------------------------------------------------
-- 9. Sample integrity trigger
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_sample_observation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_sample_size INTEGER;
    v_completed BOOLEAN;
    v_existing_count INTEGER;
BEGIN
    SELECT sample_size, completed
    INTO v_sample_size, v_completed
    FROM sampling_run
    WHERE run_id = NEW.run_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Sampling run does not exist.';
    END IF;

    IF v_completed THEN
        RAISE EXCEPTION 'Completed runs cannot accept observations.';
    END IF;

    IF NEW.observation_number > v_sample_size THEN
        RAISE EXCEPTION 'Observation exceeds configured sample size.';
    END IF;

    SELECT COUNT(*)
    INTO v_existing_count
    FROM sample_observation
    WHERE run_id = NEW.run_id
      AND observation_number <> NEW.observation_number;

    IF v_existing_count >= v_sample_size THEN
        RAISE EXCEPTION 'Sample capacity exceeded.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_sample_observation
BEFORE INSERT ON sample_observation
FOR EACH ROW
EXECUTE FUNCTION validate_sample_observation();

-- ------------------------------------------------------------
-- 10. Calculate sample statistics
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE finalize_sampling_run(
    p_run_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_experiment experiment%ROWTYPE;
    v_run sampling_run%ROWTYPE;
    v_count INTEGER;
    v_mean NUMERIC;
    v_variance NUMERIC;
    v_se NUMERIC;
    v_z NUMERIC := 1.959963984540054;
    v_margin NUMERIC;
BEGIN
    SELECT *
    INTO v_run
    FROM sampling_run
    WHERE run_id = p_run_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Sampling run not found.';
    END IF;

    IF v_run.completed THEN
        RAISE EXCEPTION 'Sampling run already finalized.';
    END IF;

    SELECT *
    INTO v_experiment
    FROM experiment
    WHERE experiment_id = v_run.experiment_id;

    SELECT
        COUNT(*),
        AVG(observed_value),
        VAR_SAMP(observed_value)
    INTO
        v_count,
        v_mean,
        v_variance
    FROM sample_observation
    WHERE run_id = p_run_id;

    IF v_count <> v_run.sample_size THEN
        RAISE EXCEPTION
            'Incomplete sample: expected %, received %.',
            v_run.sample_size,
            v_count;
    END IF;

    v_se := SQRT(
        COALESCE(v_variance, 0) / v_count
    );

    IF v_experiment.sampling_method = 'WITHOUT_REPLACEMENT' THEN
        v_se := v_se * SQRT(
            (v_experiment.population_size - v_count)::NUMERIC /
            (v_experiment.population_size - 1)
        );
    END IF;

    v_margin := v_z * v_se;

    UPDATE sampling_run
    SET
        observed_count = v_count,
        sample_mean = v_mean,
        sample_variance = COALESCE(v_variance, 0),
        sample_standard_error = v_se,
        lower_confidence_limit = v_mean - v_margin,
        upper_confidence_limit = v_mean + v_margin,
        completed = TRUE,
        completed_at = CURRENT_TIMESTAMP
    WHERE run_id = p_run_id;
END;
$$;

-- ------------------------------------------------------------
-- 11. Sampling distribution aggregation
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE calculate_sampling_summary(
    p_experiment_id BIGINT,
    p_sample_size INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_experiment experiment%ROWTYPE;
    v_count INTEGER;
    v_mean NUMERIC;
    v_variance NUMERIC;
    v_empirical_sd NUMERIC;
    v_theoretical_se NUMERIC;
    v_relative_error NUMERIC;
BEGIN
    SELECT *
    INTO v_experiment
    FROM experiment
    WHERE experiment_id = p_experiment_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Experiment not found.';
    END IF;

    SELECT
        COUNT(*),
        AVG(sample_mean),
        VAR_SAMP(sample_mean)
    INTO
        v_count,
        v_mean,
        v_variance
    FROM sampling_run
    WHERE experiment_id = p_experiment_id
      AND sample_size = p_sample_size
      AND completed = TRUE;

    IF v_count < 2 THEN
        RAISE EXCEPTION
            'At least two completed runs are required.';
    END IF;

    v_variance := COALESCE(v_variance, 0);
    v_empirical_sd := SQRT(v_variance);

    v_theoretical_se := theoretical_standard_error(
        v_experiment.population_sd,
        v_experiment.population_size,
        p_sample_size,
        v_experiment.sampling_method
    );

    v_relative_error := CASE
        WHEN v_theoretical_se = 0 THEN 0
        ELSE ABS(v_empirical_sd - v_theoretical_se)
             / v_theoretical_se
    END;

    INSERT INTO sampling_distribution_summary (
        experiment_id,
        sample_size,
        number_of_runs,
        empirical_mean,
        empirical_variance,
        empirical_standard_deviation,
        theoretical_standard_error,
        relative_se_error
    )
    VALUES (
        p_experiment_id,
        p_sample_size,
        v_count,
        v_mean,
        v_variance,
        v_empirical_sd,
        v_theoretical_se,
        v_relative_error
    )
    ON CONFLICT (experiment_id, sample_size)
    DO UPDATE SET
        number_of_runs = EXCLUDED.number_of_runs,
        empirical_mean = EXCLUDED.empirical_mean,
        empirical_variance = EXCLUDED.empirical_variance,
        empirical_standard_deviation =
            EXCLUDED.empirical_standard_deviation,
        theoretical_standard_error =
            EXCLUDED.theoretical_standard_error,
        relative_se_error = EXCLUDED.relative_se_error,
        calculated_at = CURRENT_TIMESTAMP;
END;
$$;

-- ------------------------------------------------------------
-- 12. Eligibility and normal approximation evaluation
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION evaluate_clt_eligibility(
    p_experiment_id BIGINT,
    p_sample_size INTEGER
)
RETURNS TABLE (
    sample_size INTEGER,
    population_sd NUMERIC,
    theoretical_se NUMERIC,
    normal_approximation_applicable BOOLEAN,
    evaluation_note TEXT
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_experiment experiment%ROWTYPE;
    v_eligibility BOOLEAN;
BEGIN
    SELECT *
    INTO v_experiment
    FROM experiment
    WHERE experiment_id = p_experiment_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Experiment not found.';
    END IF;

    IF p_sample_size < 1 THEN
        RAISE EXCEPTION 'Sample size must be positive.';
    END IF;

    IF v_experiment.sampling_method = 'WITHOUT_REPLACEMENT'
       AND p_sample_size > v_experiment.population_size THEN
        RAISE EXCEPTION 'Sample exceeds population.';
    END IF;

    /*
     * This is a practical screening rule, not a mathematical
     * guarantee. Skewed and heavy-tailed populations may need
     * larger sample sizes.
     */
    v_eligibility := p_sample_size >= 30;

    RETURN QUERY
    SELECT
        p_sample_size,
        v_experiment.population_sd,
        theoretical_standard_error(
            v_experiment.population_sd,
            v_experiment.population_size,
            p_sample_size,
            v_experiment.sampling_method
        ),
        v_eligibility,
        CASE
            WHEN v_experiment.population_variance = 0
                THEN 'Degenerate population; CLT approximation unnecessary.'
            WHEN v_eligibility
                THEN 'Practical screening threshold met; verify empirically.'
            ELSE
                'Small sample; inspect population shape and approximation error.'
        END;
END;
$$;

-- ------------------------------------------------------------
-- 13. Views
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW completed_sampling_runs AS
SELECT
    e.experiment_id,
    e.experiment_name,
    e.distribution,
    e.population_mean,
    e.population_sd,
    e.sampling_method,
    r.run_id,
    r.sample_size,
    r.observed_count,
    r.sample_mean,
    r.sample_standard_error,
    r.lower_confidence_limit,
    r.upper_confidence_limit,
    CASE
        WHEN r.lower_confidence_limit <= e.population_mean
         AND r.upper_confidence_limit >= e.population_mean
        THEN TRUE
        ELSE FALSE
    END AS interval_covers_population_mean
FROM experiment e
JOIN sampling_run r
    ON r.experiment_id = e.experiment_id
WHERE r.completed = TRUE;

CREATE OR REPLACE VIEW clt_performance_report AS
SELECT
    e.experiment_name,
    e.distribution,
    s.sample_size,
    s.number_of_runs,
    e.population_mean,
    s.empirical_mean,
    s.empirical_standard_deviation,
    s.theoretical_standard_error,
    s.relative_se_error,
    s.ks_distance,
    s.confidence_interval_coverage
FROM experiment e
JOIN sampling_distribution_summary s
    ON s.experiment_id = e.experiment_id;

-- ------------------------------------------------------------
-- 14. Sample experiments
-- ------------------------------------------------------------

INSERT INTO experiment (
    experiment_name,
    distribution,
    population_size,
    population_mean,
    population_variance,
    sampling_method,
    sample_size,
    repetitions,
    random_seed
)
VALUES
(
    'Bernoulli_30_Percent',
    'BERNOULLI',
    10000,
    0.30000000,
    0.21000000,
    'WITH_REPLACEMENT',
    30,
    5000,
    42
),
(
    'Exponential_Population',
    'EXPONENTIAL',
    10000,
    1.00000000,
    1.00000000,
    'WITH_REPLACEMENT',
    50,
    5000,
    43
),
(
    'Uniform_Population',
    'UNIFORM',
    10000,
    50.00000000,
    833.33333333,
    'WITH_REPLACEMENT',
    100,
    5000,
    44
),
(
    'Finite_Population',
    'UNIFORM',
    100,
    50.50000000,
    833.25000000,
    'WITHOUT_REPLACEMENT',
    10,
    1000,
    45
);

-- ------------------------------------------------------------
-- 15. Sample observations and runs
-- ------------------------------------------------------------

INSERT INTO sampling_run (
    experiment_id,
    run_number,
    sample_size
)
SELECT experiment_id, 1, sample_size
FROM experiment
WHERE experiment_name = 'Bernoulli_30_Percent';

INSERT INTO sampling_run (
    experiment_id,
    run_number,
    sample_size
)
SELECT experiment_id, 2, sample_size
FROM experiment
WHERE experiment_name = 'Bernoulli_30_Percent';

INSERT INTO sampling_run (
    experiment_id,
    run_number,
    sample_size
)
SELECT experiment_id, 1, sample_size
FROM experiment
WHERE experiment_name = 'Exponential_Population';

INSERT INTO sampling_run (
    experiment_id,
    run_number,
    sample_size
)
SELECT experiment_id, 1, sample_size
FROM experiment
WHERE experiment_name = 'Uniform_Population';

INSERT INTO sampling_run (
    experiment_id,
    run_number,
    sample_size
)
SELECT experiment_id, 1, sample_size
FROM experiment
WHERE experiment_name = 'Finite_Population';

-- Bernoulli sample: 3 successes from 10 observations.
INSERT INTO sample_observation (
    run_id,
    observation_number,
    observed_value
)
SELECT
    r.run_id,
    v.observation_number,
    v.observed_value
FROM sampling_run r
CROSS JOIN (
    VALUES
        (1, 0.0::NUMERIC),
        (2, 0.0::NUMERIC),
        (3, 1.0::NUMERIC),
        (4, 0.0::NUMERIC),
        (5, 1.0::NUMERIC),
        (6, 0.0::NUMERIC),
        (7, 1.0::NUMERIC),
        (8, 0.0::NUMERIC),
        (9, 0.0::NUMERIC),
        (10, 0.0::NUMERIC)
) AS v(observation_number, observed_value)
WHERE r.run_number = 1
  AND r.experiment_id = (
      SELECT experiment_id
      FROM experiment
      WHERE experiment_name = 'Bernoulli_30_Percent'
  );

-- Second Bernoulli sample: 4 successes.
INSERT INTO sample_observation (
    run_id,
    observation_number,
    observed_value
)
SELECT
    r.run_id,
    v.observation_number,
    v.observed_value
FROM sampling_run r
CROSS JOIN (
    VALUES
        (1, 1.0::NUMERIC),
        (2, 0.0::NUMERIC),
        (3, 0.0::NUMERIC),
        (4, 1.0::NUMERIC),
        (5, 0.0::NUMERIC),
        (6, 0.0::NUMERIC),
        (7, 1.0::NUMERIC),
        (8, 0.0::NUMERIC),
        (9, 1.0::NUMERIC),
        (10, 0.0::NUMERIC)
) AS v(observation_number, observed_value)
WHERE r.run_number = 2
  AND r.experiment_id = (
      SELECT experiment_id
      FROM experiment
      WHERE experiment_name = 'Bernoulli_30_Percent'
  );

-- Exponential sample.
INSERT INTO sample_observation (
    run_id,
    observation_number,
    observed_value
)
SELECT
    r.run_id,
    v.observation_number,
    v.observed_value
FROM sampling_run r
CROSS JOIN (
    VALUES
        (1, 0.25::NUMERIC),
        (2, 0.40::NUMERIC),
        (3, 0.55::NUMERIC),
        (4, 0.65::NUMERIC),
        (5, 0.75::NUMERIC),
        (6, 0.85::NUMERIC),
        (7, 0.95::NUMERIC),
        (8, 1.10::NUMERIC),
        (9, 1.30::NUMERIC),
        (10, 1.45::NUMERIC),
        (11, 1.60::NUMERIC),
        (12, 1.90::NUMERIC),
        (13, 2.10::NUMERIC),
        (14, 2.50::NUMERIC),
        (15, 3.00::NUMERIC)
) AS v(observation_number, observed_value)
WHERE r.experiment_id = (
    SELECT experiment_id
    FROM experiment
    WHERE experiment_name = 'Exponential_Population'
);

-- Uniform sample.
INSERT INTO sample_observation (
    run_id,
    observation_number,
    observed_value
)
SELECT
    r.run_id,
    v.observation_number,
    v.observed_value
FROM sampling_run r
CROSS JOIN (
    VALUES
        (1, 10.0::NUMERIC),
        (2, 20.0::NUMERIC),
        (3, 30.0::NUMERIC),
        (4, 40.0::NUMERIC),
        (5, 50.0::NUMERIC),
        (6, 60.0::NUMERIC),
        (7, 70.0::NUMERIC),
        (8, 80.0::NUMERIC),
        (9, 90.0::NUMERIC),
        (10, 100.0::NUMERIC)
) AS v(observation_number, observed_value)
WHERE r.experiment_id = (
    SELECT experiment_id
    FROM experiment
    WHERE experiment_name = 'Uniform_Population'
);

-- Finite population sample.
INSERT INTO sample_observation (
    run_id,
    observation_number,
    observed_value
)
SELECT
    r.run_id,
    v.observation_number,
    v.observed_value
FROM sampling_run r
CROSS JOIN (
    VALUES
        (1, 10.0::NUMERIC),
        (2, 20.0::NUMERIC),
        (3, 30.0::NUMERIC),
        (4, 40.0::NUMERIC),
        (5, 50.0::NUMERIC),
        (6, 60.0::NUMERIC),
        (7, 70.0::NUMERIC),
        (8, 80.0::NUMERIC),
        (9, 90.0::NUMERIC),
        (10, 100.0::NUMERIC)
) AS v(observation_number, observed_value)
WHERE r.experiment_id = (
    SELECT experiment_id
    FROM experiment
    WHERE experiment_name = 'Finite_Population'
);

-- ------------------------------------------------------------
-- 16. Finalize complete samples
-- ------------------------------------------------------------

DO $$
DECLARE
    v_run RECORD;
BEGIN
    FOR v_run IN
        SELECT run_id
        FROM sampling_run
    LOOP
        CALL finalize_sampling_run(v_run.run_id);
    END LOOP;
END;
$$;

-- ------------------------------------------------------------
-- 17. Generate sampling-distribution summaries
-- ------------------------------------------------------------

CALL calculate_sampling_summary(
    (
        SELECT experiment_id
        FROM experiment
        WHERE experiment_name = 'Bernoulli_30_Percent'
    ),
    30
);

-- ------------------------------------------------------------
-- 18. Retrieval queries
-- ------------------------------------------------------------

SELECT *
FROM experiment
ORDER BY created_at DESC;

SELECT *
FROM completed_sampling_runs
ORDER BY experiment_name, run_number;

-- ------------------------------------------------------------
-- 19. Validation queries
-- ------------------------------------------------------------

SELECT
    e.experiment_name,
    r.run_id,
    r.sample_size,
    r.observed_count,
    r.completed,
    CASE
        WHEN r.observed_count = r.sample_size THEN 'VALID'
        ELSE 'INCOMPLETE'
    END AS sample_validation
FROM experiment e
JOIN sampling_run r
    ON r.experiment_id = e.experiment_id;

-- ------------------------------------------------------------
-- 20. Aggregation queries
-- ------------------------------------------------------------

SELECT
    experiment_name,
    distribution,
    sample_size,
    repetitions,
    population_mean,
    population_sd
FROM experiment
ORDER BY experiment_name;

SELECT
    experiment_name,
    COUNT(*) AS completed_runs,
    AVG(sample_mean) AS average_sample_mean,
    STDDEV_SAMP(sample_mean) AS sampling_distribution_sd
FROM experiment e
JOIN sampling_run r
    ON r.experiment_id = e.experiment_id
WHERE r.completed
GROUP BY experiment_name;

-- ------------------------------------------------------------
-- 21. Confidence interval evaluation
-- ------------------------------------------------------------

SELECT
    experiment_name,
    COUNT(*) AS evaluated_intervals,
    COUNT(*) FILTER (
        WHERE interval_covers_population_mean
    ) AS covered_intervals,
    ROUND(
        AVG(interval_covers_population_mean::INTEGER)::NUMERIC,
        4
    ) AS observed_coverage
FROM completed_sampling_runs
GROUP BY experiment_name;

-- ------------------------------------------------------------
-- 22. Approximation eligibility
-- ------------------------------------------------------------

SELECT *
FROM evaluate_clt_eligibility(
    (
        SELECT experiment_id
        FROM experiment
        WHERE experiment_name = 'Exponential_Population'
    ),
    50
);

-- ------------------------------------------------------------
-- 23. Normal probability calculations
-- ------------------------------------------------------------

SELECT
    normal_cdf(0.0) AS probability_below_mean,
    normal_cdf(1.96) AS probability_below_196,
    normal_cdf(-1.96) AS probability_below_negative_196;

-- ------------------------------------------------------------
-- 24. Reporting
-- ------------------------------------------------------------

SELECT *
FROM clt_performance_report
ORDER BY experiment_name, sample_size;

-- ------------------------------------------------------------
-- 25. Sample-level diagnostic report
-- ------------------------------------------------------------

WITH sample_diagnostics AS (
    SELECT
        e.experiment_name,
        r.sample_size,
        r.sample_mean,
        r.sample_standard_error,
        e.population_mean,
        e.population_sd,
        r.lower_confidence_limit,
        r.upper_confidence_limit,
        ABS(r.sample_mean - e.population_mean) AS absolute_error
    FROM experiment e
    JOIN sampling_run r
        ON r.experiment_id = e.experiment_id
    WHERE r.completed = TRUE
)
SELECT
    experiment_name,
    sample_size,
    sample_mean,
    population_mean,
    absolute_error,
    sample_standard_error,
    lower_confidence_limit,
    upper_confidence_limit
FROM sample_diagnostics
ORDER BY absolute_error DESC;

-- ------------------------------------------------------------
-- 26. Transactional experiment status update
-- ------------------------------------------------------------

UPDATE experiment
SET
    status = 'COMPLETED',
    completed_at = CURRENT_TIMESTAMP
WHERE experiment_id IN (
    SELECT DISTINCT experiment_id
    FROM sampling_run
    WHERE completed = TRUE
);

COMMIT;

 * Important operational considerations:
 *
 * 1. Population parameters are declared experiment metadata.
 *    They are not inferred from sample observations.
 *
 * 2. Monte Carlo sampling and persistence are separate operations.
 *    This SQL script records representative observations rather
 *    than claiming to execute thousands of simulations.
 *
 * 3. The trigger serializes inserts for a run using a row lock.
 *    This protects sample-capacity validation under concurrent writes.
 *
 * 4. The sample variance uses VAR_SAMP, while population variance
 *    uses the denominator N.
 *
 * 5. Confidence interval coverage is calculated from completed runs.
 *
 * 6. The 30-observation rule is a practical heuristic, not a guarantee.
 *
 * 7. For large simulations, aggregate observations before inserting
 *    summary records to reduce database storage and index overhead.
