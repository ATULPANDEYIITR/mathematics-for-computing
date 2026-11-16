-- ============================================================
-- DESCRIPTIVE STATISTICS MANAGEMENT SYSTEM
-- PostgreSQL 15+
--
-- Statistical measures:
-- Mean, median, mode, variance, standard deviation,
-- quantiles, percentiles, interquartile range and outliers.
--
-- Includes:
-- Dataset management
-- Observation validation
-- Data-quality policies
-- Relational integrity
-- Statistical aggregation
-- Stored functions
-- Stored procedures
-- Triggers
-- Views
-- Transactions
-- Analytical reporting
-- ============================================================

BEGIN;

DROP SCHEMA IF EXISTS descriptive_stats CASCADE;

CREATE SCHEMA descriptive_stats;

SET search_path TO descriptive_stats, public;

-- ============================================================
-- 1. ENUM TYPES
-- ============================================================

CREATE TYPE dataset_status AS ENUM (
    'DRAFT',
    'ACTIVE',
    'ARCHIVED'
);

CREATE TYPE quality_status AS ENUM (
    'ACCEPTED',
    'REJECTED',
    'WARNING'
);

-- ============================================================
-- 2. DATASET MANAGEMENT
-- ============================================================

CREATE TABLE datasets (
    dataset_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dataset_name VARCHAR(150) NOT NULL UNIQUE,

    description TEXT,

    metric_unit VARCHAR(50) NOT NULL DEFAULT 'unit',

    status dataset_status NOT NULL DEFAULT 'DRAFT',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT dataset_name_not_empty
        CHECK (LENGTH(TRIM(dataset_name)) > 0)
);

-- ============================================================
-- 3. OBSERVATIONS
-- ============================================================

CREATE TABLE observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dataset_id BIGINT NOT NULL
        REFERENCES datasets(dataset_id)
        ON DELETE CASCADE,

    observation_value NUMERIC(20, 6) NOT NULL,

    category VARCHAR(100),

    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    source_reference VARCHAR(150),

    CONSTRAINT observation_value_finite
        CHECK (
            observation_value NOT IN (
                'NaN'::NUMERIC,
                'Infinity'::NUMERIC,
                '-Infinity'::NUMERIC
            )
        )
);

CREATE INDEX idx_observations_dataset
    ON observations(dataset_id);

CREATE INDEX idx_observations_value
    ON observations(dataset_id, observation_value);

CREATE INDEX idx_observations_recorded_at
    ON observations(recorded_at DESC);

-- ============================================================
-- 4. QUALITY POLICIES
-- ============================================================

CREATE TABLE quality_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dataset_id BIGINT NOT NULL UNIQUE
        REFERENCES datasets(dataset_id)
        ON DELETE CASCADE,

    minimum_observations INTEGER NOT NULL DEFAULT 2,

    minimum_allowed NUMERIC(20, 6),

    maximum_allowed NUMERIC(20, 6),

    outlier_multiplier NUMERIC(5, 2) NOT NULL DEFAULT 1.5,

    require_nonnegative BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (minimum_observations >= 1),

    CHECK (outlier_multiplier >= 0),

    CHECK (
        minimum_allowed IS NULL
        OR maximum_allowed IS NULL
        OR minimum_allowed <= maximum_allowed
    )
);

-- ============================================================
-- 5. ANALYSIS EXECUTIONS
-- ============================================================

CREATE TABLE analysis_runs (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dataset_id BIGINT NOT NULL
        REFERENCES datasets(dataset_id),

    quality quality_status NOT NULL,

    observation_count INTEGER NOT NULL DEFAULT 0,

    rejection_count INTEGER NOT NULL DEFAULT 0,

    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (observation_count >= 0),

    CHECK (rejection_count >= 0)
);

-- ============================================================
-- 6. STORED DATA VALIDATION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_observation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    policy_record quality_policies%ROWTYPE;
BEGIN
    SELECT *
    INTO policy_record
    FROM quality_policies
    WHERE dataset_id = NEW.dataset_id;

    IF FOUND THEN

        IF policy_record.minimum_allowed IS NOT NULL
           AND NEW.observation_value < policy_record.minimum_allowed
        THEN
            RAISE EXCEPTION
                'Observation % is below permitted minimum %',
                NEW.observation_value,
                policy_record.minimum_allowed;
        END IF;

        IF policy_record.maximum_allowed IS NOT NULL
           AND NEW.observation_value > policy_record.maximum_allowed
        THEN
            RAISE EXCEPTION
                'Observation % exceeds permitted maximum %',
                NEW.observation_value,
                policy_record.maximum_allowed;
        END IF;

        IF policy_record.require_nonnegative
           AND NEW.observation_value < 0
        THEN
            RAISE EXCEPTION
                'Negative observations are prohibited.';
        END IF;

    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_observation
BEFORE INSERT OR UPDATE ON observations
FOR EACH ROW
EXECUTE FUNCTION validate_observation();

-- ============================================================
-- 7. FREQUENCY DISTRIBUTION VIEW
-- ============================================================

CREATE OR REPLACE VIEW frequency_distribution AS
SELECT
    dataset_id,
    observation_value,
    COUNT(*) AS frequency
FROM observations
GROUP BY dataset_id, observation_value;

-- ============================================================
-- 8. BASIC STATISTICAL SUMMARY VIEW
-- ============================================================

CREATE OR REPLACE VIEW descriptive_summary AS
SELECT
    d.dataset_id,
    d.dataset_name,
    d.metric_unit,

    COUNT(o.observation_id) AS observation_count,

    MIN(o.observation_value) AS minimum_value,

    MAX(o.observation_value) AS maximum_value,

    MAX(o.observation_value)
        - MIN(o.observation_value) AS data_range,

    AVG(o.observation_value) AS arithmetic_mean,

    VAR_POP(o.observation_value) AS population_variance,

    VAR_SAMP(o.observation_value) AS sample_variance,

    STDDEV_POP(o.observation_value)
        AS population_standard_deviation,

    STDDEV_SAMP(o.observation_value)
        AS sample_standard_deviation,

    PERCENTILE_CONT(0.50)
        WITHIN GROUP (ORDER BY o.observation_value)
        AS median

FROM datasets d

LEFT JOIN observations o
    ON o.dataset_id = d.dataset_id

GROUP BY
    d.dataset_id,
    d.dataset_name,
    d.metric_unit;

-- ============================================================
-- 9. QUANTILE AND PERCENTILE FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_quantile(
    p_dataset_id BIGINT,
    p_probability DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    result_value DOUBLE PRECISION;
BEGIN
    IF p_probability < 0 OR p_probability > 1 THEN
        RAISE EXCEPTION
            'Probability must be between 0 and 1.';
    END IF;

    SELECT PERCENTILE_CONT(p_probability)
           WITHIN GROUP (
               ORDER BY observation_value::DOUBLE PRECISION
           )
    INTO result_value
    FROM observations
    WHERE dataset_id = p_dataset_id;

    RETURN result_value;
END;
$$;

-- ============================================================
-- 10. MODE FUNCTION
-- Returns all modes when multiple values share maximum
-- frequency. NULL means that no repeated value exists.
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_modes(
    p_dataset_id BIGINT
)
RETURNS TABLE (
    mode_value NUMERIC,
    mode_frequency BIGINT
)
LANGUAGE sql
STABLE
AS $$
    WITH frequencies AS (
        SELECT
            observation_value,
            COUNT(*) AS frequency
        FROM observations
        WHERE dataset_id = p_dataset_id
        GROUP BY observation_value
    ),
    maximum_frequency AS (
        SELECT MAX(frequency) AS maximum
        FROM frequencies
    )
    SELECT
        f.observation_value,
        f.frequency
    FROM frequencies f
    CROSS JOIN maximum_frequency m
    WHERE f.frequency = m.maximum
      AND m.maximum > 1
    ORDER BY f.observation_value;
$$;

-- ============================================================
-- 11. COMPREHENSIVE REPORT FUNCTION
-- Uses PostgreSQL ordered-set aggregates.
-- ============================================================

CREATE OR REPLACE FUNCTION generate_statistics_report(
    p_dataset_id BIGINT
)
RETURNS TABLE (
    total_observations BIGINT,
    arithmetic_mean NUMERIC,
    median NUMERIC,
    q1 NUMERIC,
    q3 NUMERIC,
    interquartile_range NUMERIC,
    population_variance NUMERIC,
    sample_variance NUMERIC,
    population_stddev NUMERIC,
    sample_stddev NUMERIC,
    percentile_90 NUMERIC,
    percentile_95 NUMERIC
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        COUNT(*)::BIGINT,

        AVG(observation_value),

        PERCENTILE_CONT(0.50)
            WITHIN GROUP (ORDER BY observation_value)::NUMERIC,

        PERCENTILE_CONT(0.25)
            WITHIN GROUP (ORDER BY observation_value)::NUMERIC,

        PERCENTILE_CONT(0.75)
            WITHIN GROUP (ORDER BY observation_value)::NUMERIC,

        (
            PERCENTILE_CONT(0.75)
                WITHIN GROUP (ORDER BY observation_value)
            -
            PERCENTILE_CONT(0.25)
                WITHIN GROUP (ORDER BY observation_value)
        )::NUMERIC,

        VAR_POP(observation_value),

        VAR_SAMP(observation_value),

        STDDEV_POP(observation_value),

        STDDEV_SAMP(observation_value),

        PERCENTILE_CONT(0.90)
            WITHIN GROUP (ORDER BY observation_value)::NUMERIC,

        PERCENTILE_CONT(0.95)
            WITHIN GROUP (ORDER BY observation_value)::NUMERIC

    FROM observations
    WHERE dataset_id = p_dataset_id;
$$;

-- ============================================================
-- 12. OUTLIER DETECTION VIEW
-- Uses the standard 1.5 * IQR rule.
-- ============================================================

CREATE OR REPLACE VIEW statistical_outliers AS
WITH quartile_values AS (
    SELECT
        dataset_id,

        PERCENTILE_CONT(0.25)
            WITHIN GROUP (ORDER BY observation_value) AS q1,

        PERCENTILE_CONT(0.75)
            WITHIN GROUP (ORDER BY observation_value) AS q3

    FROM observations
    GROUP BY dataset_id
),
boundaries AS (
    SELECT
        dataset_id,
        q1,
        q3,
        q1 - 1.5 * (q3 - q1) AS lower_bound,
        q3 + 1.5 * (q3 - q1) AS upper_bound
    FROM quartile_values
)
SELECT
    o.observation_id,
    o.dataset_id,
    o.observation_value,
    b.lower_bound,
    b.upper_bound
FROM observations o
JOIN boundaries b
    ON b.dataset_id = o.dataset_id
WHERE o.observation_value < b.lower_bound
   OR o.observation_value > b.upper_bound;

-- ============================================================
-- 13. ANALYSIS EXECUTION PROCEDURE
-- Checks policy requirements and records execution status.
-- ============================================================

CREATE OR REPLACE PROCEDURE execute_analysis(
    p_dataset_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    policy_record quality_policies%ROWTYPE;
    total_count INTEGER;
    rejected_count INTEGER;
    final_status quality_status;
BEGIN
    PERFORM 1
    FROM datasets
    WHERE dataset_id = p_dataset_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Dataset % does not exist.',
            p_dataset_id;
    END IF;

    SELECT *
    INTO policy_record
    FROM quality_policies
    WHERE dataset_id = p_dataset_id;

    SELECT COUNT(*)
    INTO total_count
    FROM observations
    WHERE dataset_id = p_dataset_id;

    rejected_count := 0;

    IF NOT FOUND THEN
        rejected_count := 0;
    END IF;

    IF policy_record.dataset_id IS NULL THEN
        final_status := 'WARNING';

    ELSIF total_count < policy_record.minimum_observations THEN
        final_status := 'WARNING';

    ELSE
        final_status := 'ACCEPTED';
    END IF;

    INSERT INTO analysis_runs (
        dataset_id,
        quality,
        observation_count,
        rejection_count
    )
    VALUES (
        p_dataset_id,
        final_status,
        total_count,
        rejected_count
    );
END;
$$;

-- ============================================================
-- 14. SAMPLE DATASETS
-- ============================================================

INSERT INTO datasets (
    dataset_name,
    description,
    metric_unit,
    status
)
VALUES
(
    'Employee Performance',
    'Employee performance measurements.',
    'score',
    'ACTIVE'
),
(
    'Server Response Time',
    'Production server response measurements.',
    'milliseconds',
    'ACTIVE'
),
(
    'Customer Satisfaction',
    'Customer satisfaction ratings.',
    'rating',
    'ACTIVE'
),
(
    'Identical Measurements',
    'Dataset containing repeated identical observations.',
    'unit',
    'ACTIVE'
);

-- ============================================================
-- 15. QUALITY POLICIES
-- ============================================================

INSERT INTO quality_policies (
    dataset_id,
    minimum_observations,
    minimum_allowed,
    maximum_allowed,
    outlier_multiplier,
    require_nonnegative
)
SELECT
    dataset_id,
    2,
    0,
    100000,
    1.5,
    TRUE
FROM datasets;

-- ============================================================
-- 16. SAMPLE OBSERVATIONS
-- ============================================================

INSERT INTO observations (
    dataset_id,
    observation_value,
    category
)
SELECT
    d.dataset_id,
    v.value,
    'Operations'
FROM datasets d
CROSS JOIN (
    VALUES
        (12::NUMERIC),
        (15),
        (18),
        (20),
        (15),
        (22),
        (25),
        (18),
        (30),
        (35),
        (18),
        (40),
        (45),
        (50),
        (55),
        (60)
) AS v(value)
WHERE d.dataset_name = 'Employee Performance';

INSERT INTO observations (
    dataset_id,
    observation_value,
    category
)
SELECT
    d.dataset_id,
    v.value,
    'Production'
FROM datasets d
CROSS JOIN (
    VALUES
        (100::NUMERIC),
        (110),
        (115),
        (120),
        (125),
        (130),
        (140),
        (150),
        (155),
        (160),
        (180),
        (200),
        (220),
        (250),
        (300),
        (900)
) AS v(value)
WHERE d.dataset_name = 'Server Response Time';

INSERT INTO observations (
    dataset_id,
    observation_value,
    category
)
SELECT
    d.dataset_id,
    v.value,
    'Survey'
FROM datasets d
CROSS JOIN (
    VALUES
        (2::NUMERIC),
        (3),
        (3),
        (4),
        (4),
        (4),
        (5),
        (5),
        (5),
        (5)
) AS v(value)
WHERE d.dataset_name = 'Customer Satisfaction';

INSERT INTO observations (
    dataset_id,
    observation_value,
    category
)
SELECT
    d.dataset_id,
    5,
    'Repeated'
FROM datasets d
CROSS JOIN generate_series(1, 5)
WHERE d.dataset_name = 'Identical Measurements';

-- ============================================================
-- 17. TRANSACTIONAL FAILURE EXAMPLE
-- Invalid values are rejected by the trigger.
-- The exception is handled inside a subtransaction.
-- ============================================================

DO $$
DECLARE
    target_id BIGINT;
BEGIN
    SELECT dataset_id
    INTO target_id
    FROM descriptive_stats.datasets
    WHERE dataset_name = 'Employee Performance';

    BEGIN
        INSERT INTO descriptive_stats.observations (
            dataset_id,
            observation_value,
            category
        )
        VALUES (
            target_id,
            -100,
            'Invalid test'
        );

    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE
            'Expected data validation failure: %',
            SQLERRM;
    END;
END;
$$;

-- ============================================================
-- 18. BASIC RETRIEVAL
-- ============================================================

SELECT *
FROM descriptive_stats.descriptive_summary
ORDER BY dataset_id;

-- ============================================================
-- 19. FREQUENCY DISTRIBUTION
-- ============================================================

SELECT
    d.dataset_name,
    f.observation_value,
    f.frequency
FROM descriptive_stats.frequency_distribution f
JOIN descriptive_stats.datasets d
    ON d.dataset_id = f.dataset_id
ORDER BY
    d.dataset_name,
    f.observation_value;

-- ============================================================
-- 20. MODE ANALYSIS
-- ============================================================

SELECT
    d.dataset_name,
    m.mode_value,
    m.mode_frequency
FROM descriptive_stats.datasets d
CROSS JOIN LATERAL
    descriptive_stats.calculate_modes(d.dataset_id) m
ORDER BY d.dataset_name, m.mode_value;

-- ============================================================
-- 21. QUANTILE ANALYSIS
-- ============================================================

SELECT
    dataset_name,

    descriptive_stats.calculate_quantile(
        dataset_id,
        0.10
    ) AS p10,

    descriptive_stats.calculate_quantile(
        dataset_id,
        0.25
    ) AS q1,

    descriptive_stats.calculate_quantile(
        dataset_id,
        0.50
    ) AS median,

    descriptive_stats.calculate_quantile(
        dataset_id,
        0.75
    ) AS q3,

    descriptive_stats.calculate_quantile(
        dataset_id,
        0.90
    ) AS p90,

    descriptive_stats.calculate_quantile(
        dataset_id,
        0.95
    ) AS p95

FROM descriptive_stats.datasets
ORDER BY dataset_id;

-- ============================================================
-- 22. COMPREHENSIVE STATISTICAL REPORT
-- ============================================================

SELECT
    d.dataset_name,
    r.*
FROM descriptive_stats.datasets d
CROSS JOIN LATERAL
    descriptive_stats.generate_statistics_report(
        d.dataset_id
    ) r
ORDER BY d.dataset_name;

-- ============================================================
-- 23. OUTLIER ANALYSIS
-- ============================================================

SELECT
    d.dataset_name,
    o.observation_id,
    o.observation_value,
    o.lower_bound,
    o.upper_bound
FROM descriptive_stats.statistical_outliers o
JOIN descriptive_stats.datasets d
    ON d.dataset_id = o.dataset_id
ORDER BY
    d.dataset_name,
    o.observation_value DESC;

-- ============================================================
-- 24. GROUPED STATISTICAL ANALYSIS
-- ============================================================

SELECT
    d.dataset_name,
    o.category,
    COUNT(*) AS observation_count,
    AVG(o.observation_value) AS mean,
    VAR_POP(o.observation_value) AS variance,
    STDDEV_POP(o.observation_value) AS standard_deviation,
    MIN(o.observation_value) AS minimum,
    MAX(o.observation_value) AS maximum
FROM descriptive_stats.observations o
JOIN descriptive_stats.datasets d
    ON d.dataset_id = o.dataset_id
GROUP BY
    d.dataset_name,
    o.category
ORDER BY
    d.dataset_name,
    o.category;

-- ============================================================
-- 25. WORKFLOW EXECUTION
-- ============================================================

DO $$
DECLARE
    dataset_record RECORD;
BEGIN
    FOR dataset_record IN
        SELECT dataset_id
        FROM descriptive_stats.datasets
        ORDER BY dataset_id
    LOOP
        CALL descriptive_stats.execute_analysis(
            dataset_record.dataset_id
        );
    END LOOP;
END;
$$;

-- ============================================================
-- 26. ANALYSIS HISTORY
-- ============================================================

SELECT
    r.run_id,
    d.dataset_name,
    r.quality,
    r.observation_count,
    r.rejection_count,
    r.executed_at
FROM descriptive_stats.analysis_runs r
JOIN descriptive_stats.datasets d
    ON d.dataset_id = r.dataset_id
ORDER BY r.executed_at DESC;

-- ============================================================
-- 27. DATA QUALITY REPORT
-- ============================================================

SELECT
    d.dataset_name,
    COUNT(o.observation_id) AS available_observations,
    p.minimum_observations,
    CASE
        WHEN COUNT(o.observation_id) < p.minimum_observations
            THEN 'INSUFFICIENT DATA'
        ELSE 'READY FOR ANALYSIS'
    END AS eligibility
FROM descriptive_stats.datasets d
JOIN descriptive_stats.quality_policies p
    ON p.dataset_id = d.dataset_id
LEFT JOIN descriptive_stats.observations o
    ON o.dataset_id = d.dataset_id
GROUP BY
    d.dataset_id,
    d.dataset_name,
    p.minimum_observations
ORDER BY d.dataset_name;

COMMIT;

-- ============================================================
-- END OF DESCRIPTIVE STATISTICS SYSTEM
-- ============================================================
