-- ============================================================
-- REGRESSION MATHEMATICS
-- SIMPLE LINEAR REGRESSION, LEAST SQUARES AND RESIDUALS
--
-- PostgreSQL 14+
--
-- Relational workflow:
-- Dataset -> Observations -> Regression Model
--         -> Predictions -> Residuals -> Evaluation
--
-- OLS model:
-- y_hat = b0 + b1 * x
--
-- b1 = SUM((x - mean_x) * (y - mean_y))
--      / SUM((x - mean_x)^2)
--
-- b0 = mean_y - b1 * mean_x
--
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS regression_lab;

SET search_path TO regression_lab, public;

-- ------------------------------------------------------------
-- 1. DATASET MANAGEMENT
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS datasets (
    dataset_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dataset_name VARCHAR(150) NOT NULL UNIQUE,

    description TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    dataset_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    CONSTRAINT valid_dataset_status
        CHECK (
            dataset_status IN (
                'ACTIVE',
                'ARCHIVED'
            )
        )
);

-- ------------------------------------------------------------
-- 2. OBSERVATIONS
-- Each row represents one independent/dependent variable pair.
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dataset_id BIGINT NOT NULL
        REFERENCES datasets(dataset_id)
        ON DELETE CASCADE,

    observation_number INTEGER NOT NULL,

    x_value DOUBLE PRECISION NOT NULL,

    y_value DOUBLE PRECISION NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_observation_number
        CHECK (observation_number > 0),

    CONSTRAINT finite_x_value
        CHECK (
            x_value NOT IN (
                'Infinity'::DOUBLE PRECISION,
                '-Infinity'::DOUBLE PRECISION,
                'NaN'::DOUBLE PRECISION
            )
        ),

    CONSTRAINT finite_y_value
        CHECK (
            y_value NOT IN (
                'Infinity'::DOUBLE PRECISION,
                '-Infinity'::DOUBLE PRECISION,
                'NaN'::DOUBLE PRECISION
            )
        ),

    CONSTRAINT unique_dataset_observation
        UNIQUE (dataset_id, observation_number)
);

CREATE INDEX IF NOT EXISTS idx_observations_dataset
    ON observations(dataset_id);

CREATE INDEX IF NOT EXISTS idx_observations_dataset_x
    ON observations(dataset_id, x_value);

-- ------------------------------------------------------------
-- 3. MODEL REGISTRY
-- Stores immutable fitted model versions.
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS regression_models (
    model_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dataset_id BIGINT NOT NULL
        REFERENCES datasets(dataset_id),

    model_version INTEGER NOT NULL,

    intercept DOUBLE PRECISION NOT NULL,

    slope DOUBLE PRECISION NOT NULL,

    mean_x DOUBLE PRECISION NOT NULL,

    mean_y DOUBLE PRECISION NOT NULL,

    observation_count INTEGER NOT NULL,

    sse DOUBLE PRECISION NOT NULL,

    ssr DOUBLE PRECISION NOT NULL,

    sst DOUBLE PRECISION NOT NULL,

    r_squared DOUBLE PRECISION NOT NULL,

    rmse DOUBLE PRECISION NOT NULL,

    mae DOUBLE PRECISION NOT NULL,

    fitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_model_version
        UNIQUE(dataset_id, model_version),

    CONSTRAINT valid_model_version
        CHECK(model_version > 0),

    CONSTRAINT valid_observation_count
        CHECK(observation_count >= 3),

    CONSTRAINT finite_model_parameters
        CHECK (
            intercept NOT IN (
                'Infinity'::DOUBLE PRECISION,
                '-Infinity'::DOUBLE PRECISION,
                'NaN'::DOUBLE PRECISION
            )
            AND slope NOT IN (
                'Infinity'::DOUBLE PRECISION,
                '-Infinity'::DOUBLE PRECISION,
                'NaN'::DOUBLE PRECISION
            )
        ),

    CONSTRAINT valid_sse
        CHECK(sse >= 0 AND sse < 'Infinity'::DOUBLE PRECISION),

    CONSTRAINT valid_ssr
        CHECK(ssr >= 0 AND ssr < 'Infinity'::DOUBLE PRECISION),

    CONSTRAINT valid_sst
        CHECK(sst > 0 AND sst < 'Infinity'::DOUBLE PRECISION),

    CONSTRAINT valid_r_squared
        CHECK(r_squared BETWEEN 0 AND 1),

    CONSTRAINT valid_rmse
        CHECK(rmse >= 0 AND rmse < 'Infinity'::DOUBLE PRECISION),

    CONSTRAINT valid_mae
        CHECK(mae >= 0 AND mae < 'Infinity'::DOUBLE PRECISION)
);

CREATE INDEX IF NOT EXISTS idx_models_dataset_version
    ON regression_models(dataset_id, model_version DESC);

-- ------------------------------------------------------------
-- 4. PREDICTIONS AND RESIDUALS
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS model_residuals (
    residual_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    model_id BIGINT NOT NULL
        REFERENCES regression_models(model_id)
        ON DELETE CASCADE,

    observation_id BIGINT NOT NULL
        REFERENCES observations(observation_id)
        ON DELETE CASCADE,

    fitted_value DOUBLE PRECISION NOT NULL,

    residual_value DOUBLE PRECISION NOT NULL,

    squared_residual DOUBLE PRECISION NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_model_observation
        UNIQUE(model_id, observation_id),

    CONSTRAINT valid_residual_square
        CHECK (
            squared_residual >= 0
            AND squared_residual < 'Infinity'::DOUBLE PRECISION
        )
);

CREATE INDEX IF NOT EXISTS idx_residuals_model
    ON model_residuals(model_id);

-- ------------------------------------------------------------
-- 5. OBSERVATION VALIDATION FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_observation_count(
    p_dataset_id BIGINT
)
RETURNS TABLE (
    observation_count BIGINT,
    distinct_x_count BIGINT,
    distinct_y_count BIGINT,
    is_eligible BOOLEAN,
    validation_message TEXT
)
LANGUAGE SQL
STABLE
AS $$
    SELECT
        COUNT(*) AS observation_count,
        COUNT(DISTINCT x_value) AS distinct_x_count,
        COUNT(DISTINCT y_value) AS distinct_y_count,

        (
            COUNT(*) >= 3
            AND COUNT(DISTINCT x_value) >= 2
            AND COUNT(DISTINCT y_value) >= 2
        ) AS is_eligible,

        CASE
            WHEN COUNT(*) < 3
                THEN 'Insufficient observations'

            WHEN COUNT(DISTINCT x_value) < 2
                THEN 'Independent variable has zero variance'

            WHEN COUNT(DISTINCT y_value) < 2
                THEN 'Dependent variable has zero variance'

            ELSE 'Dataset eligible for regression'
        END AS validation_message

    FROM observations
    WHERE dataset_id = p_dataset_id;
$$;

-- ------------------------------------------------------------
-- 6. ORDINARY LEAST SQUARES FITTING FUNCTION
--
-- Calculates the model directly from relational observations.
-- A new model version is stored for every successful fit.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION fit_linear_regression(
    p_dataset_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_count BIGINT;

    v_mean_x DOUBLE PRECISION;
    v_mean_y DOUBLE PRECISION;

    v_sxx DOUBLE PRECISION;
    v_sxy DOUBLE PRECISION;

    v_slope DOUBLE PRECISION;
    v_intercept DOUBLE PRECISION;

    v_sse DOUBLE PRECISION;
    v_ssr DOUBLE PRECISION;
    v_sst DOUBLE PRECISION;

    v_r_squared DOUBLE PRECISION;
    v_rmse DOUBLE PRECISION;
    v_mae DOUBLE PRECISION;

    v_model_version INTEGER;
    v_model_id BIGINT;

BEGIN

    -- Prevent fitting archived datasets.
    PERFORM 1
    FROM datasets
    WHERE dataset_id = p_dataset_id
      AND dataset_status = 'ACTIVE'
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Dataset % does not exist or is archived.',
            p_dataset_id;
    END IF;

    SELECT
        COUNT(*),
        AVG(x_value),
        AVG(y_value),

        SUM(
            POWER(x_value - AVG(x_value) OVER (), 2)
        )

    INTO
        v_count,
        v_mean_x,
        v_mean_y,
        v_sxx

    FROM observations
    WHERE dataset_id = p_dataset_id;

    IF v_count < 3 THEN
        RAISE EXCEPTION
            'At least three observations are required.';
    END IF;

    -- Calculate centered sums.
    SELECT
        SUM(POWER(x_value - v_mean_x, 2)),
        SUM(
            (x_value - v_mean_x) *
            (y_value - v_mean_y)
        ),
        SUM(POWER(y_value - v_mean_y, 2))

    INTO
        v_sxx,
        v_sxy,
        v_sst

    FROM observations
    WHERE dataset_id = p_dataset_id;

    IF v_sxx IS NULL OR v_sxx <= 0 THEN
        RAISE EXCEPTION
            'Independent variable has zero variance.';
    END IF;

    IF v_sst IS NULL OR v_sst <= 0 THEN
        RAISE EXCEPTION
            'Dependent variable has zero variance.';
    END IF;

    v_slope := v_sxy / v_sxx;

    v_intercept := v_mean_y - v_slope * v_mean_x;

    IF NOT (
        isfinite(v_slope)
        AND isfinite(v_intercept)
    ) THEN
        RAISE EXCEPTION
            'Invalid regression coefficients.';
    END IF;

    -- Calculate residual-based metrics.
    SELECT
        SUM(
            POWER(
                y_value -
                (v_intercept + v_slope * x_value),
                2
            )
        ),

        SUM(
            POWER(
                (v_intercept + v_slope * x_value)
                - v_mean_y,
                2
            )
        ),

        AVG(
            ABS(
                y_value -
                (v_intercept + v_slope * x_value)
            )
        )

    INTO
        v_sse,
        v_ssr,
        v_mae

    FROM observations
    WHERE dataset_id = p_dataset_id;

    v_r_squared := 1.0 - v_sse / v_sst;

    v_rmse := SQRT(v_sse / v_count);

    v_r_squared := GREATEST(
        0.0,
        LEAST(1.0, v_r_squared)
    );

    -- Validate OLS decomposition.
    IF ABS(v_sst - v_sse - v_ssr) >
       1e-8 * GREATEST(1.0, v_sst) THEN

        RAISE EXCEPTION
            'Sum of squares decomposition failed.';
    END IF;

    SELECT COALESCE(MAX(model_version), 0) + 1
    INTO v_model_version
    FROM regression_models
    WHERE dataset_id = p_dataset_id;

    INSERT INTO regression_models (
        dataset_id,
        model_version,
        intercept,
        slope,
        mean_x,
        mean_y,
        observation_count,
        sse,
        ssr,
        sst,
        r_squared,
        rmse,
        mae
    )
    VALUES (
        p_dataset_id,
        v_model_version,
        v_intercept,
        v_slope,
        v_mean_x,
        v_mean_y,
        v_count,
        v_sse,
        v_ssr,
        v_sst,
        v_r_squared,
        v_rmse,
        v_mae
    )
    RETURNING model_id INTO v_model_id;

    -- Persist fitted values and residuals.
    INSERT INTO model_residuals (
        model_id,
        observation_id,
        fitted_value,
        residual_value,
        squared_residual
    )
    SELECT
        v_model_id,
        observation_id,

        v_intercept + v_slope * x_value,

        y_value -
        (v_intercept + v_slope * x_value),

        POWER(
            y_value -
            (v_intercept + v_slope * x_value),
            2
        )

    FROM observations
    WHERE dataset_id = p_dataset_id;

    RETURN v_model_id;

END;
$$;

-- ------------------------------------------------------------
-- 7. PREDICTION FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION predict_linear(
    p_model_id BIGINT,
    p_x DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_prediction DOUBLE PRECISION;
BEGIN

    IF NOT isfinite(p_x) THEN
        RAISE EXCEPTION
            'Prediction input must be finite.';
    END IF;

    SELECT
        intercept + slope * p_x
    INTO v_prediction
    FROM regression_models
    WHERE model_id = p_model_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Regression model % does not exist.',
            p_model_id;
    END IF;

    IF NOT isfinite(v_prediction) THEN
        RAISE EXCEPTION
            'Prediction exceeded numeric limits.';
    END IF;

    RETURN v_prediction;

END;
$$;

-- ------------------------------------------------------------
-- 8. RESIDUAL REPORTING VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW residual_analysis AS
SELECT
    m.model_id,
    m.dataset_id,
    m.model_version,

    o.observation_number,
    o.x_value,
    o.y_value,

    r.fitted_value,
    r.residual_value,
    r.squared_residual,

    ABS(r.residual_value) AS absolute_residual

FROM regression_models m

JOIN model_residuals r
    ON r.model_id = m.model_id

JOIN observations o
    ON o.observation_id = r.observation_id;

-- ------------------------------------------------------------
-- 9. MODEL PERFORMANCE REPORTING VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW regression_performance AS
SELECT
    m.model_id,
    d.dataset_name,
    m.model_version,
    m.observation_count,

    m.slope,
    m.intercept,

    m.sse,
    m.ssr,
    m.sst,

    m.r_squared,
    m.rmse,
    m.mae,

    m.fitted_at

FROM regression_models m

JOIN datasets d
    ON d.dataset_id = m.dataset_id;

-- ------------------------------------------------------------
-- 10. RESIDUAL AGGREGATION VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW residual_summary AS
SELECT
    model_id,

    COUNT(*) AS observation_count,

    AVG(residual_value) AS mean_residual,

    MIN(residual_value) AS minimum_residual,

    MAX(residual_value) AS maximum_residual,

    AVG(absolute_residual) AS mean_absolute_residual,

    SQRT(AVG(squared_residual)) AS residual_rmse,

    SUM(squared_residual) AS total_squared_error

FROM residual_analysis

GROUP BY model_id;

-- ------------------------------------------------------------
-- 11. SAMPLE DATASETS
-- ------------------------------------------------------------

INSERT INTO datasets (
    dataset_name,
    description
)
VALUES
(
    'STUDY_HOURS',
    'Relationship between study hours and examination scores.'
),
(
    'CONSTANT_X_TEST',
    'Invalid dataset used to test zero independent-variable variance.'
)
ON CONFLICT (dataset_name) DO NOTHING;

-- Main regression dataset.
INSERT INTO observations (
    dataset_id,
    observation_number,
    x_value,
    y_value
)
SELECT
    d.dataset_id,
    v.observation_number,
    v.x_value,
    v.y_value

FROM datasets d

CROSS JOIN (
    VALUES
        (1, 1.0, 2.1),
        (2, 2.0, 3.9),
        (3, 3.0, 6.2),
        (4, 4.0, 7.8),
        (5, 5.0, 10.1),
        (6, 6.0, 11.9),
        (7, 7.0, 14.2),
        (8, 8.0, 15.8)
) AS v(observation_number, x_value, y_value)

WHERE d.dataset_name = 'STUDY_HOURS'

ON CONFLICT (dataset_id, observation_number) DO NOTHING;

-- Invalid dataset with constant X.
INSERT INTO observations (
    dataset_id,
    observation_number,
    x_value,
    y_value
)
SELECT
    d.dataset_id,
    v.observation_number,
    5.0,
    v.y_value

FROM datasets d

CROSS JOIN (
    VALUES
        (1, 2.0),
        (2, 4.0),
        (3, 6.0)
) AS v(observation_number, y_value)

WHERE d.dataset_name = 'CONSTANT_X_TEST'

ON CONFLICT (dataset_id, observation_number) DO NOTHING;

-- ------------------------------------------------------------
-- 12. FIT THE VALID MODEL
-- ------------------------------------------------------------

DO $$
DECLARE
    v_dataset_id BIGINT;
    v_model_id BIGINT;
BEGIN

    SELECT dataset_id
    INTO v_dataset_id
    FROM regression_lab.datasets
    WHERE dataset_name = 'STUDY_HOURS';

    v_model_id :=
        regression_lab.fit_linear_regression(v_dataset_id);

    RAISE NOTICE
        'Regression model created with ID: %',
        v_model_id;

END;
$$;

-- ------------------------------------------------------------
-- 13. DATA RETRIEVAL
-- ------------------------------------------------------------

SELECT
    d.dataset_name,
    o.observation_number,
    o.x_value,
    o.y_value

FROM datasets d

JOIN observations o
    ON o.dataset_id = d.dataset_id

WHERE d.dataset_name = 'STUDY_HOURS'

ORDER BY o.observation_number;

-- ------------------------------------------------------------
-- 14. DATASET ELIGIBILITY
-- ------------------------------------------------------------

SELECT
    d.dataset_name,
    v.*

FROM datasets d

CROSS JOIN LATERAL
    validate_observation_count(d.dataset_id) v

ORDER BY d.dataset_name;

-- ------------------------------------------------------------
-- 15. REGRESSION MODEL PERFORMANCE
-- ------------------------------------------------------------

SELECT *
FROM regression_performance
ORDER BY model_id;

-- ------------------------------------------------------------
-- 16. OBSERVATION-LEVEL RESIDUAL REPORT
-- ------------------------------------------------------------

SELECT
    model_id,
    observation_number,
    x_value,
    y_value,
    fitted_value,
    residual_value,
    squared_residual

FROM residual_analysis

ORDER BY model_id, observation_number;

-- ------------------------------------------------------------
-- 17. RESIDUAL AGGREGATION
-- ------------------------------------------------------------

SELECT *
FROM residual_summary
ORDER BY model_id;

-- ------------------------------------------------------------
-- 18. PREDICTION
-- ------------------------------------------------------------

SELECT
    m.model_id,
    v.x_value,

    predict_linear(
        m.model_id,
        v.x_value
    ) AS predicted_y

FROM regression_models m

CROSS JOIN (
    VALUES
        (6.0::DOUBLE PRECISION),
        (7.0::DOUBLE PRECISION),
        (8.0::DOUBLE PRECISION),
        (10.0::DOUBLE PRECISION)
) AS v(x_value)

ORDER BY m.model_id, v.x_value;

-- ------------------------------------------------------------
-- 19. RESIDUAL QUALITY CHECK
-- OLS with an intercept should have approximately zero
-- sum of residuals, subject to floating-point precision.
-- ------------------------------------------------------------

SELECT
    model_id,

    SUM(residual_value) AS residual_sum,

    AVG(residual_value) AS residual_mean,

    CASE
        WHEN ABS(SUM(residual_value)) < 1e-8
            THEN 'PASS'
        ELSE 'CHECK'
    END AS residual_validation

FROM residual_analysis

GROUP BY model_id;

-- ------------------------------------------------------------
-- 20. MODEL VERSION HISTORY
-- ------------------------------------------------------------

SELECT
    dataset_id,
    model_version,
    slope,
    intercept,
    r_squared,
    rmse,
    fitted_at

FROM regression_models

ORDER BY dataset_id, model_version;

-- ------------------------------------------------------------
-- 21. TRANSACTIONAL FAILURE HANDLING
-- A failed model fit does not leave a partially stored model.
-- ------------------------------------------------------------

DO $$
DECLARE
    v_invalid_dataset BIGINT;
BEGIN

    SELECT dataset_id
    INTO v_invalid_dataset

    FROM regression_lab.datasets

    WHERE dataset_name = 'CONSTANT_X_TEST';

    BEGIN

        PERFORM regression_lab.fit_linear_regression(
            v_invalid_dataset
        );

        RAISE EXCEPTION
            'Invalid dataset unexpectedly passed validation.';

    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Expected regression failure: %',
                SQLERRM;
    END;

END;
$$;

COMMIT;
