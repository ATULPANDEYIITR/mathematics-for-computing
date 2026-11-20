-- ============================================================
-- HYPOTHESIS TESTING MANAGEMENT SYSTEM
-- PostgreSQL 15+
--
-- Domain:
-- Statistical experiments, hypotheses, observations,
-- statistical evaluations, significance decisions,
-- multiple testing and audit history.
--
-- Statistical method:
-- One-sample Z-test with known population standard deviation.
--
-- Supports:
-- Null hypotheses
-- Alternative hypotheses
-- P-values
-- Significance levels
-- Confidence intervals
-- Bonferroni correction
-- Experiment lifecycle
-- Validation and reporting
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS hypothesis_testing;

SET search_path TO hypothesis_testing, public;

-- ============================================================
-- 1. DOMAIN TYPES
-- ============================================================

CREATE TYPE experiment_status AS ENUM (
    'DRAFT',
    'READY',
    'RUNNING',
    'COMPLETED',
    'FAILED',
    'ARCHIVED'
);

CREATE TYPE alternative_type AS ENUM (
    'TWO_SIDED',
    'GREATER',
    'LESS'
);

CREATE TYPE statistical_decision AS ENUM (
    'REJECT_NULL',
    'FAIL_TO_REJECT'
);

CREATE TYPE error_category AS ENUM (
    'NONE',
    'TYPE_I',
    'TYPE_II'
);

-- ============================================================
-- 2. EXPERIMENTS
-- ============================================================

CREATE TABLE experiments (
    experiment_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    experiment_code VARCHAR(60) NOT NULL UNIQUE,

    experiment_name VARCHAR(200) NOT NULL,

    description TEXT,

    owner_name VARCHAR(120) NOT NULL,

    status experiment_status NOT NULL DEFAULT 'DRAFT',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMPTZ,

    CONSTRAINT valid_experiment_code
        CHECK (experiment_code ~ '^[A-Z0-9_-]+$'),

    CONSTRAINT valid_experiment_name
        CHECK (length(trim(experiment_name)) > 0),

    CONSTRAINT valid_owner
        CHECK (length(trim(owner_name)) > 0),

    CONSTRAINT valid_completion_time
        CHECK (
            (status = 'COMPLETED' AND completed_at IS NOT NULL)
            OR
            (status <> 'COMPLETED' AND completed_at IS NULL)
        )
);

-- ============================================================
-- 3. HYPOTHESES
-- ============================================================

CREATE TABLE hypotheses (
    hypothesis_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id)
        ON DELETE RESTRICT,

    hypothesis_code VARCHAR(60) NOT NULL,

    null_mean NUMERIC(18,6) NOT NULL,

    alternative alternative_type NOT NULL,

    significance_level NUMERIC(8,6) NOT NULL DEFAULT 0.05,

    population_sigma NUMERIC(18,6) NOT NULL,

    hypothesis_description TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_hypothesis_code
        UNIQUE (experiment_id, hypothesis_code),

    CONSTRAINT valid_significance_level
        CHECK (
            significance_level > 0
            AND significance_level < 1
        ),

    CONSTRAINT positive_population_sigma
        CHECK (population_sigma > 0),

    CONSTRAINT valid_hypothesis_description
        CHECK (length(trim(hypothesis_description)) > 0)
);

-- ============================================================
-- 4. OBSERVATIONS
-- ============================================================

CREATE TABLE observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    hypothesis_id BIGINT NOT NULL
        REFERENCES hypotheses(hypothesis_id)
        ON DELETE CASCADE,

    observation_number INTEGER NOT NULL,

    observed_value NUMERIC(18,6) NOT NULL,

    observed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    source_reference VARCHAR(150),

    CONSTRAINT unique_observation_number
        UNIQUE (hypothesis_id, observation_number),

    CONSTRAINT positive_observation_number
        CHECK (observation_number > 0)
);

-- ============================================================
-- 5. STATISTICAL TEST RESULTS
-- ============================================================

CREATE TABLE test_results (
    result_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    hypothesis_id BIGINT NOT NULL
        REFERENCES hypotheses(hypothesis_id)
        ON DELETE RESTRICT,

    sample_size INTEGER NOT NULL,

    sample_mean NUMERIC(18,8) NOT NULL,

    standard_error NUMERIC(18,8) NOT NULL,

    z_statistic NUMERIC(18,8) NOT NULL,

    p_value NUMERIC(18,12) NOT NULL,

    confidence_lower NUMERIC(18,8) NOT NULL,

    confidence_upper NUMERIC(18,8) NOT NULL,

    decision statistical_decision NOT NULL,

    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    execution_reference UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),

    CONSTRAINT valid_sample_size
        CHECK (sample_size >= 2),

    CONSTRAINT positive_standard_error
        CHECK (standard_error > 0),

    CONSTRAINT valid_p_value
        CHECK (p_value BETWEEN 0 AND 1),

    CONSTRAINT valid_confidence_interval
        CHECK (confidence_lower <= confidence_upper)
);

CREATE INDEX idx_observations_hypothesis
    ON observations(hypothesis_id);

CREATE INDEX idx_results_hypothesis_time
    ON test_results(hypothesis_id, evaluated_at DESC);

CREATE INDEX idx_experiments_status
    ON experiments(status);

CREATE INDEX idx_hypotheses_experiment
    ON hypotheses(experiment_id);

-- ============================================================
-- 6. AUDIT HISTORY
-- ============================================================

CREATE TABLE experiment_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    experiment_id BIGINT
        REFERENCES experiments(experiment_id)
        ON DELETE SET NULL,

    action VARCHAR(80) NOT NULL,

    details JSONB NOT NULL DEFAULT '{}'::jsonb,

    performed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 7. NORMAL DISTRIBUTION FUNCTIONS
-- ============================================================

-- Standard normal cumulative distribution function.
CREATE OR REPLACE FUNCTION normal_cdf(
    p_z DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT 0.5 * (
        1.0 + erf(p_z / sqrt(2.0))
    );
$$;

CREATE OR REPLACE FUNCTION normal_survival(
    p_z DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT 0.5 * erfc(p_z / sqrt(2.0));
$$;

-- ============================================================
-- 8. P-VALUE CALCULATION
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_p_value(
    p_z DOUBLE PRECISION,
    p_alternative alternative_type
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    v_p DOUBLE PRECISION;
BEGIN
    CASE p_alternative

        WHEN 'TWO_SIDED' THEN
            v_p := erfc(abs(p_z) / sqrt(2.0));

        WHEN 'GREATER' THEN
            v_p := normal_survival(p_z);

        WHEN 'LESS' THEN
            v_p := normal_cdf(p_z);

        ELSE
            RAISE EXCEPTION 'Unsupported alternative hypothesis';
    END CASE;

    RETURN LEAST(1.0, GREATEST(0.0, v_p));
END;
$$;

-- ============================================================
-- 9. CRITICAL Z-VALUE
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_critical_z(
    p_alpha DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    v_low DOUBLE PRECISION := 0;
    v_high DOUBLE PRECISION := 10;
    v_mid DOUBLE PRECISION;
    v_target DOUBLE PRECISION;
    v_i INTEGER;
BEGIN
    IF p_alpha <= 0 OR p_alpha >= 1 THEN
        RAISE EXCEPTION 'Invalid significance level';
    END IF;

    v_target := p_alpha / 2.0;

    FOR v_i IN 1..100 LOOP
        v_mid := (v_low + v_high) / 2.0;

        IF normal_survival(v_mid) > v_target THEN
            v_low := v_mid;
        ELSE
            v_high := v_mid;
        END IF;
    END LOOP;

    RETURN (v_low + v_high) / 2.0;
END;
$$;

-- ============================================================
-- 10. OBSERVATION VALIDATION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_observation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_status experiment_status;
BEGIN
    SELECT e.status
    INTO v_status
    FROM hypotheses h
    JOIN experiments e
        ON e.experiment_id = h.experiment_id
    WHERE h.hypothesis_id = NEW.hypothesis_id
    FOR UPDATE OF e;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Hypothesis does not exist';
    END IF;

    IF v_status <> 'DRAFT' AND v_status <> 'READY' THEN
        RAISE EXCEPTION
            'Observations cannot be modified in experiment state %',
            v_status;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_observation
BEFORE INSERT OR UPDATE OR DELETE
ON observations
FOR EACH ROW
EXECUTE FUNCTION validate_observation();

-- ============================================================
-- 11. AUDIT TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION audit_experiment_change()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO experiment_audit (
        experiment_id,
        action,
        details
    )
    VALUES (
        NEW.experiment_id,
        'EXPERIMENT_UPDATED',
        jsonb_build_object(
            'old_status', OLD.status,
            'new_status', NEW.status
        )
    );

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_experiment_audit
AFTER UPDATE OF status
ON experiments
FOR EACH ROW
WHEN (OLD.status IS DISTINCT FROM NEW.status)
EXECUTE FUNCTION audit_experiment_change();

-- ============================================================
-- 12. STATISTICAL TEST EXECUTION
-- ============================================================

CREATE OR REPLACE FUNCTION execute_z_test(
    p_hypothesis_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_hypothesis hypotheses%ROWTYPE;
    v_sample_size INTEGER;
    v_sample_mean DOUBLE PRECISION;
    v_standard_error DOUBLE PRECISION;
    v_z DOUBLE PRECISION;
    v_p DOUBLE PRECISION;
    v_critical DOUBLE PRECISION;
    v_margin DOUBLE PRECISION;
    v_lower DOUBLE PRECISION;
    v_upper DOUBLE PRECISION;
    v_decision statistical_decision;
    v_result_id BIGINT;
BEGIN
    SELECT h.*
    INTO v_hypothesis
    FROM hypotheses h
    JOIN experiments e
        ON e.experiment_id = h.experiment_id
    WHERE h.hypothesis_id = p_hypothesis_id
      AND e.status = 'READY'
    FOR UPDATE OF e;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Hypothesis not found or experiment is not READY';
    END IF;

    SELECT
        COUNT(*)::INTEGER,
        AVG(observed_value)::DOUBLE PRECISION
    INTO
        v_sample_size,
        v_sample_mean
    FROM observations
    WHERE hypothesis_id = p_hypothesis_id;

    IF v_sample_size < 2 THEN
        RAISE EXCEPTION
            'At least two observations are required';
    END IF;

    v_standard_error :=
        v_hypothesis.population_sigma::DOUBLE PRECISION
        / sqrt(v_sample_size::DOUBLE PRECISION);

    v_z := (
        v_sample_mean - v_hypothesis.null_mean::DOUBLE PRECISION
    ) / v_standard_error;

    v_p := calculate_p_value(
        v_z,
        v_hypothesis.alternative
    );

    v_critical := calculate_critical_z(
        v_hypothesis.significance_level::DOUBLE PRECISION
    );

    v_margin := v_critical * v_standard_error;

    v_lower := v_sample_mean - v_margin;
    v_upper := v_sample_mean + v_margin;

    v_decision :=
        CASE
            WHEN v_p <= v_hypothesis.significance_level
                THEN 'REJECT_NULL'::statistical_decision
            ELSE 'FAIL_TO_REJECT'::statistical_decision
        END;

    INSERT INTO test_results (
        hypothesis_id,
        sample_size,
        sample_mean,
        standard_error,
        z_statistic,
        p_value,
        confidence_lower,
        confidence_upper,
        decision
    )
    VALUES (
        p_hypothesis_id,
        v_sample_size,
        v_sample_mean,
        v_standard_error,
        v_z,
        v_p,
        v_lower,
        v_upper,
        v_decision
    )
    RETURNING result_id INTO v_result_id;

    RETURN v_result_id;
END;
$$;

-- ============================================================
-- 13. EXPERIMENT PROCESSING PROCEDURE
-- ============================================================

CREATE OR REPLACE PROCEDURE process_experiment(
    p_experiment_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_hypothesis_id BIGINT;
BEGIN
    UPDATE experiments
    SET status = 'RUNNING'
    WHERE experiment_id = p_experiment_id
      AND status = 'READY';

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Experiment is not eligible for execution';
    END IF;

    FOR v_hypothesis_id IN
        SELECT hypothesis_id
        FROM hypotheses
        WHERE experiment_id = p_experiment_id
        ORDER BY hypothesis_id
    LOOP
        PERFORM execute_z_test(v_hypothesis_id);
    END LOOP;

    UPDATE experiments
    SET
        status = 'COMPLETED',
        completed_at = CURRENT_TIMESTAMP
    WHERE experiment_id = p_experiment_id;

EXCEPTION
    WHEN OTHERS THEN
        UPDATE experiments
        SET
            status = 'FAILED',
            completed_at = NULL
        WHERE experiment_id = p_experiment_id;

        RAISE;
END;
$$;

-- ============================================================
-- 14. EXPERIMENT READINESS VIEW
-- ============================================================

CREATE OR REPLACE VIEW experiment_readiness AS
SELECT
    e.experiment_id,
    e.experiment_code,
    e.experiment_name,
    e.status,
    COUNT(DISTINCT h.hypothesis_id) AS hypothesis_count,
    COUNT(o.observation_id) AS observation_count,
    CASE
        WHEN COUNT(DISTINCT h.hypothesis_id) = 0
            THEN FALSE
        WHEN COUNT(o.observation_id) = 0
            THEN FALSE
        WHEN BOOL_AND(
            COALESCE(obs.sample_count, 0) >= 2
        )
            THEN TRUE
        ELSE FALSE
    END AS ready_for_execution
FROM experiments e
LEFT JOIN hypotheses h
    ON h.experiment_id = e.experiment_id
LEFT JOIN observations o
    ON o.hypothesis_id = h.hypothesis_id
LEFT JOIN (
    SELECT
        hypothesis_id,
        COUNT(*) AS sample_count
    FROM observations
    GROUP BY hypothesis_id
) obs
    ON obs.hypothesis_id = h.hypothesis_id
GROUP BY
    e.experiment_id,
    e.experiment_code,
    e.experiment_name,
    e.status;

-- ============================================================
-- 15. RESULT REPORTING VIEW
-- ============================================================

CREATE OR REPLACE VIEW statistical_results_report AS
SELECT
    e.experiment_code,
    e.experiment_name,
    h.hypothesis_code,
    h.null_mean,
    h.alternative,
    h.significance_level,
    r.sample_size,
    r.sample_mean,
    r.z_statistic,
    r.p_value,
    r.confidence_lower,
    r.confidence_upper,
    r.decision,
    r.evaluated_at,
    CASE
        WHEN r.decision = 'REJECT_NULL'
            THEN 'Statistically significant'
        ELSE 'Not statistically significant'
    END AS interpretation
FROM test_results r
JOIN hypotheses h
    ON h.hypothesis_id = r.hypothesis_id
JOIN experiments e
    ON e.experiment_id = h.experiment_id;

-- ============================================================
-- 16. SAMPLE EXPERIMENTS
-- ============================================================

INSERT INTO experiments (
    experiment_code,
    experiment_name,
    description,
    owner_name
)
VALUES
(
    'QUALITY-001',
    'Manufacturing Output Evaluation',
    'Testing whether average production differs from target output.',
    'Quality Research Team'
),
(
    'MARKETING-001',
    'Marketing Conversion Evaluation',
    'Testing whether conversion rate differs from historical benchmark.',
    'Marketing Analytics Team'
),
(
    'FAILURE-001',
    'Insufficient Sample Evaluation',
    'Demonstrates a hypothesis with insufficient observations.',
    'Research Operations'
);

INSERT INTO hypotheses (
    experiment_id,
    hypothesis_code,
    null_mean,
    alternative,
    significance_level,
    population_sigma,
    hypothesis_description
)
SELECT
    experiment_id,
    'H1',
    100,
    'TWO_SIDED',
    0.05,
    8,
    'The average production output differs from 100 units.'
FROM experiments
WHERE experiment_code = 'QUALITY-001';

INSERT INTO hypotheses (
    experiment_id,
    hypothesis_code,
    null_mean,
    alternative,
    significance_level,
    population_sigma,
    hypothesis_description
)
SELECT
    experiment_id,
    'H1',
    5,
    'GREATER',
    0.01,
    2,
    'The average conversion-related measurement exceeds 5.'
FROM experiments
WHERE experiment_code = 'MARKETING-001';

INSERT INTO hypotheses (
    experiment_id,
    hypothesis_code,
    null_mean,
    alternative,
    significance_level,
    population_sigma,
    hypothesis_description
)
SELECT
    experiment_id,
    'H1',
    100,
    'TWO_SIDED',
    0.05,
    10,
    'The sample is intentionally insufficient.'
FROM experiments
WHERE experiment_code = 'FAILURE-001';

-- ============================================================
-- 17. SAMPLE OBSERVATIONS
-- ============================================================

INSERT INTO observations (
    hypothesis_id,
    observation_number,
    observed_value
)
SELECT
    h.hypothesis_id,
    sample.number,
    sample.value
FROM hypotheses h
JOIN experiments e
    ON e.experiment_id = h.experiment_id
CROSS JOIN (
    VALUES
        (1, 104.0),
        (2, 108.0),
        (3, 102.0),
        (4, 107.0),
        (5, 105.0),
        (6, 110.0),
        (7, 106.0),
        (8, 103.0),
        (9, 109.0),
        (10, 107.0),
        (11, 105.0),
        (12, 108.0),
        (13, 111.0),
        (14, 104.0),
        (15, 106.0),
        (16, 109.0),
        (17, 107.0),
        (18, 105.0),
        (19, 110.0),
        (20, 108.0)
) AS sample(number, value)
WHERE e.experiment_code = 'QUALITY-001'
  AND h.hypothesis_code = 'H1';

INSERT INTO observations (
    hypothesis_id,
    observation_number,
    observed_value
)
SELECT
    h.hypothesis_id,
    sample.number,
    sample.value
FROM hypotheses h
JOIN experiments e
    ON e.experiment_id = h.experiment_id
CROSS JOIN (
    VALUES
        (1, 8.1),
        (2, 8.5),
        (3, 8.3),
        (4, 8.8),
        (5, 9.0),
        (6, 8.7),
        (7, 8.4),
        (8, 8.9),
        (9, 9.1),
        (10, 8.6)
) AS sample(number, value)
WHERE e.experiment_code = 'MARKETING-001'
  AND h.hypothesis_code = 'H1';

INSERT INTO observations (
    hypothesis_id,
    observation_number,
    observed_value
)
SELECT
    h.hypothesis_id,
    1,
    105
FROM hypotheses h
JOIN experiments e
    ON e.experiment_id = h.experiment_id
WHERE e.experiment_code = 'FAILURE-001';

-- ============================================================
-- 18. MOVE EXPERIMENTS INTO READY STATE
-- ============================================================

UPDATE experiments e
SET status = 'READY'
WHERE EXISTS (
    SELECT 1
    FROM hypotheses h
    JOIN observations o
        ON o.hypothesis_id = h.hypothesis_id
    WHERE h.experiment_id = e.experiment_id
)
AND e.status = 'DRAFT';

-- ============================================================
-- 19. VALIDATION QUERIES
-- ============================================================

-- Experiments and their readiness.
SELECT *
FROM experiment_readiness
ORDER BY experiment_id;

-- Hypotheses without sufficient observations.
SELECT
    h.hypothesis_code,
    e.experiment_code,
    COUNT(o.observation_id) AS available_observations
FROM hypotheses h
JOIN experiments e
    ON e.experiment_id = h.experiment_id
LEFT JOIN observations o
    ON o.hypothesis_id = h.hypothesis_id
GROUP BY
    h.hypothesis_code,
    e.experiment_code
HAVING COUNT(o.observation_id) < 2;

-- ============================================================
-- 20. PROCESS VALID EXPERIMENTS
-- ============================================================

CALL process_experiment(
    (
        SELECT experiment_id
        FROM experiments
        WHERE experiment_code = 'QUALITY-001'
    )
);

CALL process_experiment(
    (
        SELECT experiment_id
        FROM experiments
        WHERE experiment_code = 'MARKETING-001'
    )
);

-- FAILURE-001 remains READY because it has insufficient data.
-- Its processing is intentionally excluded from this transaction.

-- ============================================================
-- 21. RETRIEVAL AND REPORTING
-- ============================================================

SELECT *
FROM statistical_results_report
ORDER BY experiment_code, hypothesis_code;

-- Aggregate significance results.
SELECT
    decision,
    COUNT(*) AS number_of_tests,
    ROUND(AVG(p_value), 8) AS average_p_value
FROM test_results
GROUP BY decision;

-- Significant versus non-significant hypotheses.
SELECT
    CASE
        WHEN r.p_value <= h.significance_level
            THEN 'SIGNIFICANT'
        ELSE 'NOT_SIGNIFICANT'
    END AS significance_status,
    COUNT(*) AS test_count
FROM test_results r
JOIN hypotheses h
    ON h.hypothesis_id = r.hypothesis_id
GROUP BY 1;

-- ============================================================
-- 22. BONFERRONI MULTIPLE-TESTING EVALUATION
-- ============================================================

WITH sample_p_values(test_number, p_value) AS (
    VALUES
        (1, 0.001::NUMERIC),
        (2, 0.018::NUMERIC),
        (3, 0.032::NUMERIC),
        (4, 0.120::NUMERIC),
        (5, 0.400::NUMERIC)
),
parameters AS (
    SELECT
        0.05::NUMERIC AS alpha,
        COUNT(*)::NUMERIC AS number_of_tests
    FROM sample_p_values
)
SELECT
    p.test_number,
    p.p_value AS original_p_value,
    LEAST(
        1.0,
        p.p_value * parameters.number_of_tests
    ) AS adjusted_p_value,
    parameters.alpha / parameters.number_of_tests
        AS adjusted_alpha,
    p.p_value <= (
        parameters.alpha / parameters.number_of_tests
    ) AS statistically_significant
FROM sample_p_values p
CROSS JOIN parameters
ORDER BY p.test_number;

-- ============================================================
-- 23. AUDIT REPORT
-- ============================================================

SELECT
    audit_id,
    experiment_id,
    action,
    details,
    performed_at
FROM experiment_audit
ORDER BY audit_id;

-- ============================================================
-- 24. TRANSACTION COMPLETION
-- ============================================================

COMMIT;

-- ============================================================
-- 25. OPERATIONAL NOTES
-- ============================================================

-- Use parameterized SQL statements in application code.
-- Restrict write permissions to authorized experiment operators.
-- Grant read-only access to reporting roles.
-- Keep observations immutable after experiment execution.
-- Record the test method, assumptions and software version
-- in production experiment metadata.
-- Avoid treating p-values as effect sizes or probabilities
-- that the null hypothesis is true.
-- The supplied implementation assumes independent observations
-- and a known population standard deviation.
-- A production deployment should separately implement
-- sample-based t-tests and multiplicity procedures when needed.
