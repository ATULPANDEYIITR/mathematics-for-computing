-- ============================================================
-- CORRELATION AND COVARIANCE ANALYSIS
-- PostgreSQL 15+
--
-- Relational statistical analysis system.
--
-- Features:
-- 1. Dataset and variable management
-- 2. Observation storage
-- 3. Data-quality validation
-- 4. Sample and population covariance
-- 5. Pearson correlation
-- 6. Pairwise covariance matrix
-- 7. Correlation matrix
-- 8. Dependence monitoring
-- 9. Missing-value handling
-- 10. Statistical reporting
-- 11. Transaction-safe analysis execution
--
-- Statistical convention:
-- Sample covariance uses denominator N - 1.
-- Population covariance uses denominator N.
-- Pearson correlation is based on paired observations.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS statistics_lab;

SET search_path TO statistics_lab, public;

-- ============================================================
-- 1. DOMAIN TYPES
-- ============================================================

CREATE TYPE missing_policy AS ENUM (
    'REJECT',
    'PAIRWISE',
    'LISTWISE'
);

CREATE TYPE analysis_status AS ENUM (
    'CREATED',
    'RUNNING',
    'COMPLETED',
    'FAILED'
);

CREATE TYPE correlation_category AS ENUM (
    'NEGLIGIBLE',
    'WEAK',
    'MODERATE',
    'STRONG',
    'VERY_STRONG'
);

-- ============================================================
-- 2. DATASET MANAGEMENT
-- ============================================================

CREATE TABLE datasets (
    dataset_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT valid_dataset_name
        CHECK (length(trim(dataset_name)) > 0)
);

CREATE TABLE variables (
    variable_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_id BIGINT NOT NULL
        REFERENCES datasets(dataset_id)
        ON DELETE CASCADE,

    variable_name VARCHAR(100) NOT NULL,
    measurement_unit VARCHAR(50),
    description TEXT,

    CONSTRAINT unique_dataset_variable
        UNIQUE(dataset_id, variable_name),

    CONSTRAINT valid_variable_name
        CHECK (length(trim(variable_name)) > 0)
);

-- ============================================================
-- 3. OBSERVATION STORAGE
--
-- Missing values are represented by NULL.
-- Zero is a valid observation and must not be treated as missing.
-- ============================================================

CREATE TABLE observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    variable_id BIGINT NOT NULL
        REFERENCES variables(variable_id)
        ON DELETE CASCADE,

    observation_number INTEGER NOT NULL,

    observation_value DOUBLE PRECISION,

    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_variable_observation
        UNIQUE(variable_id, observation_number),

    CONSTRAINT valid_observation_number
        CHECK (observation_number > 0),

    CONSTRAINT finite_observation
        CHECK (
            observation_value IS NULL
            OR (
                observation_value > '-Infinity'::DOUBLE PRECISION
                AND observation_value < 'Infinity'::DOUBLE PRECISION
            )
        )
);

CREATE INDEX idx_observations_variable
    ON observations(variable_id);

CREATE INDEX idx_observations_number
    ON observations(observation_number);

CREATE INDEX idx_observations_variable_number
    ON observations(variable_id, observation_number);

-- ============================================================
-- 4. ANALYSIS CONFIGURATION AND EXECUTION
-- ============================================================

CREATE TABLE analysis_runs (
    analysis_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dataset_id BIGINT NOT NULL
        REFERENCES datasets(dataset_id),

    policy missing_policy NOT NULL DEFAULT 'REJECT',

    use_sample_statistics BOOLEAN NOT NULL DEFAULT TRUE,

    correlation_threshold DOUBLE PRECISION NOT NULL DEFAULT 0.80,

    status analysis_status NOT NULL DEFAULT 'CREATED',

    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    error_message TEXT,

    created_by VARCHAR(100) NOT NULL,

    CONSTRAINT valid_correlation_threshold
        CHECK (
            correlation_threshold > 0
            AND correlation_threshold <= 1
        )
);

CREATE INDEX idx_analysis_dataset_status
    ON analysis_runs(dataset_id, status);

-- ============================================================
-- 5. PAIRWISE RESULTS
-- ============================================================

CREATE TABLE pair_statistics (
    pair_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    analysis_id BIGINT NOT NULL
        REFERENCES analysis_runs(analysis_id)
        ON DELETE CASCADE,

    first_variable_id BIGINT NOT NULL
        REFERENCES variables(variable_id),

    second_variable_id BIGINT NOT NULL
        REFERENCES variables(variable_id),

    observation_count INTEGER NOT NULL,

    covariance DOUBLE PRECISION NOT NULL,

    correlation DOUBLE PRECISION,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_analysis_pair
        UNIQUE (
            analysis_id,
            first_variable_id,
            second_variable_id
        ),

    CONSTRAINT distinct_variables
        CHECK (first_variable_id < second_variable_id),

    CONSTRAINT valid_pair_count
        CHECK (observation_count >= 2),

    CONSTRAINT valid_correlation
        CHECK (
            correlation IS NULL
            OR (
                correlation >= -1
                AND correlation <= 1
            )
        ),

    CONSTRAINT finite_covariance
        CHECK (
            covariance > '-Infinity'::DOUBLE PRECISION
            AND covariance < 'Infinity'::DOUBLE PRECISION
        )
);

CREATE INDEX idx_pair_statistics_analysis
    ON pair_statistics(analysis_id);

CREATE INDEX idx_pair_statistics_correlation
    ON pair_statistics(analysis_id, correlation);

-- ============================================================
-- 6. STATISTICAL FUNCTIONS
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_mean(
    p_values DOUBLE PRECISION[]
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_mean DOUBLE PRECISION;
BEGIN
    SELECT AVG(value)
    INTO v_mean
    FROM unnest(p_values) AS value
    WHERE value IS NOT NULL;

    IF v_mean IS NULL THEN
        RAISE EXCEPTION 'Mean requires at least one observation.';
    END IF;

    RETURN v_mean;
END;
$$;

CREATE OR REPLACE FUNCTION calculate_variance(
    p_values DOUBLE PRECISION[],
    p_sample BOOLEAN DEFAULT TRUE
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_count INTEGER;
    v_mean DOUBLE PRECISION;
    v_variance DOUBLE PRECISION;
BEGIN
    SELECT
        COUNT(value),
        AVG(value)
    INTO v_count, v_mean
    FROM unnest(p_values) AS value
    WHERE value IS NOT NULL;

    IF v_count < CASE WHEN p_sample THEN 2 ELSE 1 END THEN
        RAISE EXCEPTION 'Insufficient observations for variance.';
    END IF;

    IF p_sample THEN
        SELECT VAR_SAMP(value)
        INTO v_variance
        FROM unnest(p_values) AS value
        WHERE value IS NOT NULL;
    ELSE
        SELECT VAR_POP(value)
        INTO v_variance
        FROM unnest(p_values) AS value
        WHERE value IS NOT NULL;
    END IF;

    RETURN v_variance;
END;
$$;

CREATE OR REPLACE FUNCTION calculate_covariance(
    p_x DOUBLE PRECISION[],
    p_y DOUBLE PRECISION[],
    p_sample BOOLEAN DEFAULT TRUE
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_count INTEGER;
    v_covariance DOUBLE PRECISION;
BEGIN
    IF cardinality(p_x) <> cardinality(p_y) THEN
        RAISE EXCEPTION 'Array lengths must match.';
    END IF;

    SELECT COUNT(*)
    INTO v_count
    FROM generate_subscripts(p_x, 1) AS i
    WHERE p_x[i] IS NOT NULL
      AND p_y[i] IS NOT NULL;

    IF v_count < CASE WHEN p_sample THEN 2 ELSE 1 END THEN
        RAISE EXCEPTION 'Insufficient paired observations.';
    END IF;

    IF p_sample THEN
        SELECT COVAR_SAMP(p_x[i], p_y[i])
        INTO v_covariance
        FROM generate_subscripts(p_x, 1) AS i;
    ELSE
        SELECT COVAR_POP(p_x[i], p_y[i])
        INTO v_covariance
        FROM generate_subscripts(p_x, 1) AS i;
    END IF;

    RETURN v_covariance;
END;
$$;

CREATE OR REPLACE FUNCTION calculate_pearson(
    p_x DOUBLE PRECISION[],
    p_y DOUBLE PRECISION[]
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_count INTEGER;
    v_correlation DOUBLE PRECISION;
BEGIN
    IF cardinality(p_x) <> cardinality(p_y) THEN
        RAISE EXCEPTION 'Array lengths must match.';
    END IF;

    SELECT
        COUNT(*),
        CORR(p_x[i], p_y[i])
    INTO v_count, v_correlation
    FROM generate_subscripts(p_x, 1) AS i
    WHERE p_x[i] IS NOT NULL
      AND p_y[i] IS NOT NULL;

    IF v_count < 2 THEN
        RAISE EXCEPTION 'Pearson correlation requires two paired observations.';
    END IF;

    IF v_correlation IS NULL THEN
        RAISE EXCEPTION 'Correlation undefined for constant variables.';
    END IF;

    RETURN GREATEST(-1.0, LEAST(1.0, v_correlation));
END;
$$;

CREATE OR REPLACE FUNCTION classify_correlation(
    p_correlation DOUBLE PRECISION
)
RETURNS correlation_category
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_magnitude DOUBLE PRECISION;
BEGIN
    IF p_correlation IS NULL
       OR p_correlation < -1
       OR p_correlation > 1 THEN
        RAISE EXCEPTION 'Invalid correlation value.';
    END IF;

    v_magnitude := ABS(p_correlation);

    RETURN CASE
        WHEN v_magnitude >= 0.90 THEN 'VERY_STRONG'
        WHEN v_magnitude >= 0.70 THEN 'STRONG'
        WHEN v_magnitude >= 0.40 THEN 'MODERATE'
        WHEN v_magnitude >= 0.20 THEN 'WEAK'
        ELSE 'NEGLIGIBLE'
    END::correlation_category;
END;
$$;

-- ============================================================
-- 7. DATA-QUALITY VALIDATION FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_dataset(
    p_dataset_id BIGINT
)
RETURNS TABLE (
    variable_name VARCHAR,
    observation_count BIGINT,
    missing_count BIGINT,
    valid_count BIGINT,
    is_valid BOOLEAN
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM datasets
        WHERE dataset_id = p_dataset_id
    ) THEN
        RAISE EXCEPTION 'Dataset does not exist.';
    END IF;

    RETURN QUERY
    SELECT
        v.variable_name::VARCHAR,
        COUNT(o.observation_id),
        COUNT(*) FILTER (
            WHERE o.observation_value IS NULL
        ),
        COUNT(o.observation_value),
        COUNT(o.observation_id) >= 2
    FROM variables v
    LEFT JOIN observations o
        ON o.variable_id = v.variable_id
    WHERE v.dataset_id = p_dataset_id
    GROUP BY v.variable_id, v.variable_name
    ORDER BY v.variable_name;
END;
$$;

-- ============================================================
-- 8. PAIRWISE ANALYSIS PROCEDURE
--
-- LISTWISE:
-- A row is retained only when all dataset variables are present.
--
-- PAIRWISE:
-- Each variable pair uses its own complete observations.
--
-- REJECT:
-- Any missing observation prevents execution.
-- ============================================================

CREATE OR REPLACE PROCEDURE run_correlation_analysis(
    p_analysis_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_run analysis_runs%ROWTYPE;
    v_variable_count INTEGER;
    v_missing_count BIGINT;
    v_sample_count INTEGER;
    v_x DOUBLE PRECISION[];
    v_y DOUBLE PRECISION[];
    v_covariance DOUBLE PRECISION;
    v_correlation DOUBLE PRECISION;
    v_count INTEGER;
    v_first BIGINT;
    v_second BIGINT;
    v_i INTEGER;
    v_j INTEGER;
BEGIN
    SELECT *
    INTO v_run
    FROM analysis_runs
    WHERE analysis_id = p_analysis_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Analysis run does not exist.';
    END IF;

    IF v_run.status = 'RUNNING' THEN
        RAISE EXCEPTION 'Analysis is already running.';
    END IF;

    IF v_run.status = 'COMPLETED' THEN
        RAISE EXCEPTION 'Completed analysis cannot be rerun.';
    END IF;

    UPDATE analysis_runs
    SET
        status = 'RUNNING',
        started_at = CURRENT_TIMESTAMP,
        completed_at = NULL,
        error_message = NULL
    WHERE analysis_id = p_analysis_id;

    DELETE FROM pair_statistics
    WHERE analysis_id = p_analysis_id;

    SELECT COUNT(*)
    INTO v_variable_count
    FROM variables
    WHERE dataset_id = v_run.dataset_id;

    IF v_variable_count < 2 THEN
        RAISE EXCEPTION 'At least two variables are required.';
    END IF;

    SELECT COUNT(*)
    INTO v_missing_count
    FROM observations o
    JOIN variables v
        ON v.variable_id = o.variable_id
    WHERE v.dataset_id = v_run.dataset_id
      AND o.observation_value IS NULL;

    IF v_run.policy = 'REJECT' AND v_missing_count > 0 THEN
        RAISE EXCEPTION
            'Missing values found. REJECT policy prevents analysis.';
    END IF;

    -- All variables must share an observation index range.
    SELECT MIN(observation_number)
    INTO v_sample_count
    FROM observations o
    JOIN variables v
        ON v.variable_id = o.variable_id
    WHERE v.dataset_id = v_run.dataset_id;

    FOR v_i IN
        SELECT variable_id
        FROM variables
        WHERE dataset_id = v_run.dataset_id
        ORDER BY variable_id
    LOOP
        FOR v_j IN
            SELECT variable_id
            FROM variables
            WHERE dataset_id = v_run.dataset_id
              AND variable_id > v_i
            ORDER BY variable_id
        LOOP
            v_first := v_i;
            v_second := v_j;

            IF v_run.policy = 'LISTWISE' THEN

                SELECT
                    ARRAY_AGG(first_obs.observation_value
                              ORDER BY first_obs.observation_number),
                    ARRAY_AGG(second_obs.observation_value
                              ORDER BY second_obs.observation_number)
                INTO v_x, v_y
                FROM observations first_obs
                JOIN observations second_obs
                    ON second_obs.observation_number =
                       first_obs.observation_number
                WHERE first_obs.variable_id = v_first
                  AND second_obs.variable_id = v_second
                  AND first_obs.observation_value IS NOT NULL
                  AND second_obs.observation_value IS NOT NULL
                  AND NOT EXISTS (
                      SELECT 1
                      FROM variables all_variables
                      LEFT JOIN observations other_obs
                        ON other_obs.variable_id =
                           all_variables.variable_id
                       AND other_obs.observation_number =
                           first_obs.observation_number
                      WHERE all_variables.dataset_id =
                            v_run.dataset_id
                        AND other_obs.observation_value IS NULL
                  );

            ELSE

                SELECT
                    ARRAY_AGG(first_obs.observation_value
                              ORDER BY first_obs.observation_number),
                    ARRAY_AGG(second_obs.observation_value
                              ORDER BY second_obs.observation_number)
                INTO v_x, v_y
                FROM observations first_obs
                JOIN observations second_obs
                    ON second_obs.observation_number =
                       first_obs.observation_number
                WHERE first_obs.variable_id = v_first
                  AND second_obs.variable_id = v_second
                  AND first_obs.observation_value IS NOT NULL
                  AND second_obs.observation_value IS NOT NULL;

            END IF;

            v_count := COALESCE(cardinality(v_x), 0);

            IF v_count < 2 THEN
                RAISE EXCEPTION
                    'Insufficient paired observations for variables % and %.',
                    v_first,
                    v_second;
            END IF;

            v_covariance := calculate_covariance(
                v_x,
                v_y,
                v_run.use_sample_statistics
            );

            v_correlation := calculate_pearson(v_x, v_y);

            INSERT INTO pair_statistics (
                analysis_id,
                first_variable_id,
                second_variable_id,
                observation_count,
                covariance,
                correlation
            )
            VALUES (
                p_analysis_id,
                v_first,
                v_second,
                v_count,
                v_covariance,
                v_correlation
            );

        END LOOP;
    END LOOP;

    UPDATE analysis_runs
    SET
        status = 'COMPLETED',
        completed_at = CURRENT_TIMESTAMP
    WHERE analysis_id = p_analysis_id;

EXCEPTION
    WHEN OTHERS THEN
        UPDATE analysis_runs
        SET
            status = 'FAILED',
            completed_at = CURRENT_TIMESTAMP,
            error_message = SQLERRM
        WHERE analysis_id = p_analysis_id;

        RAISE;
END;
$$;

-- ============================================================
-- 9. REPORTING VIEWS
-- ============================================================

CREATE OR REPLACE VIEW variable_descriptive_statistics AS
SELECT
    d.dataset_id,
    d.dataset_name,
    v.variable_id,
    v.variable_name,
    COUNT(o.observation_id) AS total_rows,
    COUNT(o.observation_value) AS valid_observations,
    COUNT(o.observation_id) -
        COUNT(o.observation_value) AS missing_observations,
    AVG(o.observation_value) AS mean_value,
    VAR_SAMP(o.observation_value) AS sample_variance,
    VAR_POP(o.observation_value) AS population_variance,
    STDDEV_SAMP(o.observation_value) AS sample_standard_deviation,
    MIN(o.observation_value) AS minimum_value,
    MAX(o.observation_value) AS maximum_value
FROM datasets d
JOIN variables v
    ON v.dataset_id = d.dataset_id
LEFT JOIN observations o
    ON o.variable_id = v.variable_id
GROUP BY
    d.dataset_id,
    d.dataset_name,
    v.variable_id,
    v.variable_name;

CREATE OR REPLACE VIEW correlation_report AS
SELECT
    a.analysis_id,
    d.dataset_name,
    first_variable.variable_name AS first_variable,
    second_variable.variable_name AS second_variable,
    p.observation_count,
    p.covariance,
    p.correlation,
    CASE
        WHEN p.correlation IS NULL THEN NULL
        ELSE classify_correlation(p.correlation)
    END AS correlation_strength,
    CASE
        WHEN p.correlation > 0 THEN 'POSITIVE'
        WHEN p.correlation < 0 THEN 'NEGATIVE'
        ELSE 'ZERO'
    END AS relationship_direction
FROM pair_statistics p
JOIN analysis_runs a
    ON a.analysis_id = p.analysis_id
JOIN datasets d
    ON d.dataset_id = a.dataset_id
JOIN variables first_variable
    ON first_variable.variable_id = p.first_variable_id
JOIN variables second_variable
    ON second_variable.variable_id = p.second_variable_id;

-- ============================================================
-- 10. COVARIANCE AND CORRELATION MATRIX RETRIEVAL
-- ============================================================

CREATE OR REPLACE FUNCTION get_statistical_matrix(
    p_analysis_id BIGINT,
    p_matrix_type TEXT DEFAULT 'CORRELATION'
)
RETURNS TABLE (
    row_variable TEXT,
    column_variable TEXT,
    matrix_value DOUBLE PRECISION
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_type TEXT := UPPER(p_matrix_type);
BEGIN
    IF v_type NOT IN ('CORRELATION', 'COVARIANCE') THEN
        RAISE EXCEPTION
            'Matrix type must be CORRELATION or COVARIANCE.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM analysis_runs
        WHERE analysis_id = p_analysis_id
          AND status = 'COMPLETED'
    ) THEN
        RAISE EXCEPTION
            'Only completed analyses can be queried.';
    END IF;

    RETURN QUERY
    SELECT
        first_variable.variable_name::TEXT,
        second_variable.variable_name::TEXT,
        CASE
            WHEN v_type = 'CORRELATION' THEN
                CASE
                    WHEN first_variable.variable_id =
                         second_variable.variable_id
                    THEN 1.0
                    ELSE p.correlation
                END
            ELSE
                CASE
                    WHEN first_variable.variable_id =
                         second_variable.variable_id
                    THEN (
                        SELECT
                            CASE
                                WHEN a.use_sample_statistics
                                THEN VAR_SAMP(o.observation_value)
                                ELSE VAR_POP(o.observation_value)
                            END
                        FROM observations o
                        WHERE o.variable_id =
                              first_variable.variable_id
                    )
                    ELSE p.covariance
                END
        END
    FROM analysis_runs a
    JOIN variables first_variable
        ON first_variable.dataset_id = a.dataset_id
    JOIN variables second_variable
        ON second_variable.dataset_id = a.dataset_id
    LEFT JOIN pair_statistics p
        ON p.analysis_id = a.analysis_id
       AND p.first_variable_id = LEAST(
           first_variable.variable_id,
           second_variable.variable_id
       )
       AND p.second_variable_id = GREATEST(
           first_variable.variable_id,
           second_variable.variable_id
       )
    WHERE a.analysis_id = p_analysis_id
    ORDER BY
        first_variable.variable_name,
        second_variable.variable_name;
END;
$$;

-- ============================================================
-- 11. SAMPLE DATASET
-- ============================================================

INSERT INTO datasets (
    dataset_name,
    description,
    created_by
)
VALUES (
    'Investment Portfolio Analysis',
    'Six-period investment observations for dependence analysis.',
    'research_analyst'
);

INSERT INTO variables (
    dataset_id,
    variable_name,
    measurement_unit,
    description
)
SELECT
    dataset_id,
    variable_name,
    'index_points',
    description
FROM datasets
CROSS JOIN (
    VALUES
        ('Equity_A', 'First equity asset'),
        ('Equity_B', 'Second equity asset'),
        ('Bonds', 'Fixed-income asset'),
        ('Gold', 'Gold market index'),
        ('Market_Index', 'Broad market index')
) AS v(variable_name, description)
WHERE dataset_name = 'Investment Portfolio Analysis';

-- Six aligned observations per variable.

INSERT INTO observations (
    variable_id,
    observation_number,
    observation_value
)
SELECT
    v.variable_id,
    sample.observation_number,
    sample.observation_value
FROM variables v
JOIN datasets d
    ON d.dataset_id = v.dataset_id
JOIN LATERAL (
    SELECT *
    FROM (
        VALUES
            ('Equity_A', 1, 10.0),
            ('Equity_A', 2, 12.0),
            ('Equity_A', 3, 14.0),
            ('Equity_A', 4, 16.0),
            ('Equity_A', 5, 18.0),
            ('Equity_A', 6, 20.0),

            ('Equity_B', 1, 8.0),
            ('Equity_B', 2, 10.0),
            ('Equity_B', 3, 12.0),
            ('Equity_B', 4, 14.0),
            ('Equity_B', 5, 16.0),
            ('Equity_B', 6, 18.0),

            ('Bonds', 1, 20.0),
            ('Bonds', 2, 19.0),
            ('Bonds', 3, 21.0),
            ('Bonds', 4, 18.0),
            ('Bonds', 5, 22.0),
            ('Bonds', 6, 17.0),

            ('Gold', 1, 15.0),
            ('Gold', 2, 17.0),
            ('Gold', 3, 14.0),
            ('Gold', 4, 18.0),
            ('Gold', 5, 13.0),
            ('Gold', 6, 19.0),

            ('Market_Index', 1, 11.0),
            ('Market_Index', 2, 13.0),
            ('Market_Index', 3, 15.0),
            ('Market_Index', 4, 17.0),
            ('Market_Index', 5, 19.0),
            ('Market_Index', 6, 21.0)
    ) AS values_table(
        variable_name,
        observation_number,
        observation_value
    )
) AS sample
    ON sample.variable_name = v.variable_name
WHERE d.dataset_name = 'Investment Portfolio Analysis';

-- ============================================================
-- 12. MISSING-DATA EXAMPLE
-- ============================================================

INSERT INTO datasets (
    dataset_name,
    description,
    created_by
)
VALUES (
    'Missing Observation Example',
    'Dataset demonstrating pairwise missing-value handling.',
    'research_analyst'
);

INSERT INTO variables (
    dataset_id,
    variable_name
)
SELECT dataset_id, variable_name
FROM datasets
CROSS JOIN (
    VALUES ('Variable_A'), ('Variable_B')
) AS v(variable_name)
WHERE dataset_name = 'Missing Observation Example';

INSERT INTO observations (
    variable_id,
    observation_number,
    observation_value
)
SELECT
    v.variable_id,
    sample.observation_number,
    sample.observation_value
FROM variables v
JOIN datasets d
    ON d.dataset_id = v.dataset_id
JOIN LATERAL (
    SELECT *
    FROM (
        VALUES
            ('Variable_A', 1, 1.0::DOUBLE PRECISION),
            ('Variable_A', 2, 2.0::DOUBLE PRECISION),
            ('Variable_A', 3, NULL::DOUBLE PRECISION),
            ('Variable_A', 4, 4.0::DOUBLE PRECISION),
            ('Variable_A', 5, 5.0::DOUBLE PRECISION),

            ('Variable_B', 1, 2.0::DOUBLE PRECISION),
            ('Variable_B', 2, 4.0::DOUBLE PRECISION),
            ('Variable_B', 3, 6.0::DOUBLE PRECISION),
            ('Variable_B', 4, NULL::DOUBLE PRECISION),
            ('Variable_B', 5, 10.0::DOUBLE PRECISION)
    ) AS values_table(
        variable_name,
        observation_number,
        observation_value
    )
) AS sample
    ON sample.variable_name = v.variable_name
WHERE d.dataset_name = 'Missing Observation Example';

-- ============================================================
-- 13. ANALYSIS EXECUTION
-- ============================================================

INSERT INTO analysis_runs (
    dataset_id,
    policy,
    use_sample_statistics,
    correlation_threshold,
    created_by
)
SELECT
    dataset_id,
    'REJECT',
    TRUE,
    0.80,
    'research_analyst'
FROM datasets
WHERE dataset_name = 'Investment Portfolio Analysis';

CALL run_correlation_analysis(
    (
        SELECT analysis_id
        FROM analysis_runs
        JOIN datasets USING (dataset_id)
        WHERE dataset_name = 'Investment Portfolio Analysis'
        ORDER BY analysis_id DESC
        LIMIT 1
    )
);

INSERT INTO analysis_runs (
    dataset_id,
    policy,
    use_sample_statistics,
    correlation_threshold,
    created_by
)
SELECT
    dataset_id,
    'PAIRWISE',
    TRUE,
    0.80,
    'research_analyst'
FROM datasets
WHERE dataset_name = 'Missing Observation Example';

CALL run_correlation_analysis(
    (
        SELECT analysis_id
        FROM analysis_runs
        JOIN datasets USING (dataset_id)
        WHERE dataset_name = 'Missing Observation Example'
        ORDER BY analysis_id DESC
        LIMIT 1
    )
);

-- ============================================================
-- 14. RETRIEVAL QUERIES
-- ============================================================

-- Dataset inventory.
SELECT
    dataset_id,
    dataset_name,
    created_by,
    created_at,
    is_active
FROM datasets
ORDER BY dataset_id;

-- Variable inventory.
SELECT
    d.dataset_name,
    v.variable_name,
    v.measurement_unit
FROM variables v
JOIN datasets d USING (dataset_id)
ORDER BY d.dataset_name, v.variable_name;

-- Individual observations.
SELECT
    d.dataset_name,
    v.variable_name,
    o.observation_number,
    o.observation_value
FROM observations o
JOIN variables v USING (variable_id)
JOIN datasets d USING (dataset_id)
WHERE d.dataset_name = 'Investment Portfolio Analysis'
ORDER BY v.variable_name, o.observation_number;

-- ============================================================
-- 15. VALIDATION QUERIES
-- ============================================================

SELECT *
FROM validate_dataset(
    (
        SELECT dataset_id
        FROM datasets
        WHERE dataset_name = 'Investment Portfolio Analysis'
    )
);

SELECT *
FROM validate_dataset(
    (
        SELECT dataset_id
        FROM datasets
        WHERE dataset_name = 'Missing Observation Example'
    )
);

-- ============================================================
-- 16. DESCRIPTIVE STATISTICS
-- ============================================================

SELECT
    dataset_name,
    variable_name,
    total_rows,
    valid_observations,
    missing_observations,
    ROUND(mean_value::NUMERIC, 4) AS mean_value,
    ROUND(sample_variance::NUMERIC, 4) AS sample_variance,
    ROUND(population_variance::NUMERIC, 4) AS population_variance,
    ROUND(
        sample_standard_deviation::NUMERIC,
        4
    ) AS standard_deviation,
    minimum_value,
    maximum_value
FROM variable_descriptive_statistics
ORDER BY dataset_name, variable_name;

-- ============================================================
-- 17. CORRELATION REPORTING
-- ============================================================

SELECT
    analysis_id,
    dataset_name,
    first_variable,
    second_variable,
    observation_count,
    ROUND(covariance::NUMERIC, 4) AS covariance,
    ROUND(correlation::NUMERIC, 4) AS pearson_correlation,
    correlation_strength,
    relationship_direction
FROM correlation_report
ORDER BY analysis_id, ABS(correlation) DESC;

-- ============================================================
-- 18. MATRIX RETRIEVAL
-- ============================================================

SELECT *
FROM get_statistical_matrix(
    (
        SELECT analysis_id
        FROM analysis_runs
        JOIN datasets USING (dataset_id)
        WHERE dataset_name = 'Investment Portfolio Analysis'
        ORDER BY analysis_id DESC
        LIMIT 1
    ),
    'CORRELATION'
);

SELECT *
FROM get_statistical_matrix(
    (
        SELECT analysis_id
        FROM analysis_runs
        JOIN datasets USING (dataset_id)
        WHERE dataset_name = 'Investment Portfolio Analysis'
        ORDER BY analysis_id DESC
        LIMIT 1
    ),
    'COVARIANCE'
);

-- ============================================================
-- 19. HIGH-CORRELATION DEPENDENCE MONITORING
-- ============================================================

SELECT
    dataset_name,
    first_variable,
    second_variable,
    correlation,
    correlation_strength,
    relationship_direction
FROM correlation_report
WHERE ABS(correlation) >= 0.80
ORDER BY ABS(correlation) DESC;

-- ============================================================
-- 20. AGGREGATION AND ANALYSIS HEALTH
-- ============================================================

SELECT
    a.analysis_id,
    d.dataset_name,
    a.policy,
    a.status,
    COUNT(p.pair_id) AS analyzed_pairs,
    AVG(p.correlation) AS average_correlation,
    MAX(ABS(p.correlation)) AS maximum_absolute_correlation,
    a.started_at,
    a.completed_at
FROM analysis_runs a
JOIN datasets d USING (dataset_id)
LEFT JOIN pair_statistics p USING (analysis_id)
GROUP BY
    a.analysis_id,
    d.dataset_name,
    a.policy,
    a.status,
    a.started_at,
    a.completed_at
ORDER BY a.analysis_id;

-- ============================================================
-- 21. TRANSACTION AND INTEGRITY CHECK
-- ============================================================

-- All sample inserts, analysis runs and reports are part of
-- this transaction. Any unhandled failure rolls back the script.
-- A failed analysis is recorded as FAILED before its exception
-- is propagated.

COMMIT;
