/*
===============================================================================
MULTIVARIATE STATISTICS
PostgreSQL implementation
===============================================================================

Implements:
1. Multiple linear regression with two predictors.
2. Sample covariance and correlation structures.
3. Multivariate normal density for two dimensions.
4. Mahalanobis distance.
5. Statistical anomaly classification.
6. Model evaluation and reporting.
7. Relational observation and model governance.

The regression implementation uses closed-form matrix algebra for
two predictors and an intercept.

Run using PostgreSQL 14 or later.
*/

BEGIN;

CREATE SCHEMA IF NOT EXISTS multivariate_stats;

SET search_path TO multivariate_stats, public;

-- ============================================================================
-- 1. DOMAIN MODEL
-- ============================================================================

CREATE TABLE IF NOT EXISTS datasets (
    dataset_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    CONSTRAINT valid_dataset_status
        CHECK (status IN ('ACTIVE', 'ARCHIVED'))
);

CREATE TABLE IF NOT EXISTS observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_id BIGINT NOT NULL
        REFERENCES datasets(dataset_id) ON DELETE CASCADE,

    advertising NUMERIC(14,4) NOT NULL,
    training_hours NUMERIC(14,4) NOT NULL,
    sales NUMERIC(14,4) NOT NULL,

    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_advertising
        CHECK (advertising >= 0),

    CONSTRAINT valid_training_hours
        CHECK (training_hours >= 0),

    CONSTRAINT finite_measurements
        CHECK (
            advertising NOT IN (
                'NaN'::NUMERIC,
                'Infinity'::NUMERIC,
                '-Infinity'::NUMERIC
            )
            AND training_hours NOT IN (
                'NaN'::NUMERIC,
                'Infinity'::NUMERIC,
                '-Infinity'::NUMERIC
            )
            AND sales NOT IN (
                'NaN'::NUMERIC,
                'Infinity'::NUMERIC,
                '-Infinity'::NUMERIC
            )
        )
);

CREATE INDEX IF NOT EXISTS idx_observations_dataset
    ON observations(dataset_id);

CREATE INDEX IF NOT EXISTS idx_observations_recorded
    ON observations(dataset_id, recorded_at DESC);

CREATE TABLE IF NOT EXISTS regression_models (
    model_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_id BIGINT NOT NULL
        REFERENCES datasets(dataset_id),

    intercept NUMERIC(18,8) NOT NULL,
    beta_advertising NUMERIC(18,8) NOT NULL,
    beta_training NUMERIC(18,8) NOT NULL,

    r_squared NUMERIC(18,10) NOT NULL,
    adjusted_r_squared NUMERIC(18,10) NOT NULL,
    rmse NUMERIC(18,10) NOT NULL,
    residual_variance NUMERIC(18,10) NOT NULL,

    training_count INTEGER NOT NULL,
    fitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_model_r_squared
        CHECK (r_squared BETWEEN -1000000 AND 1),

    CONSTRAINT valid_training_count
        CHECK (training_count > 3),

    CONSTRAINT valid_model_errors
        CHECK (rmse >= 0 AND residual_variance >= 0)
);

CREATE TABLE IF NOT EXISTS covariance_structures (
    covariance_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_id BIGINT NOT NULL
        REFERENCES datasets(dataset_id),

    variable_one VARCHAR(80) NOT NULL,
    variable_two VARCHAR(80) NOT NULL,

    covariance_value NUMERIC(20,10) NOT NULL,
    correlation_value NUMERIC(20,10) NOT NULL,

    calculated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_covariance_pair
        UNIQUE (
            dataset_id,
            variable_one,
            variable_two
        ),

    CONSTRAINT valid_correlation
        CHECK (correlation_value BETWEEN -1.000000001 AND 1.000000001)
);

CREATE TABLE IF NOT EXISTS distribution_profiles (
    profile_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    profile_name VARCHAR(120) NOT NULL UNIQUE,

    mean_one NUMERIC(18,8) NOT NULL,
    mean_two NUMERIC(18,8) NOT NULL,

    variance_one NUMERIC(18,8) NOT NULL,
    variance_two NUMERIC(18,8) NOT NULL,
    covariance_value NUMERIC(18,8) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_variances
        CHECK (variance_one > 0 AND variance_two > 0),

    CONSTRAINT positive_definite_covariance
        CHECK (
            variance_one * variance_two -
            covariance_value * covariance_value > 0
        )
);

CREATE TABLE IF NOT EXISTS distribution_evaluations (
    evaluation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    profile_id BIGINT NOT NULL
        REFERENCES distribution_profiles(profile_id),

    observation_one NUMERIC(18,8) NOT NULL,
    observation_two NUMERIC(18,8) NOT NULL,

    mahalanobis_distance NUMERIC(18,10) NOT NULL,
    probability_density NUMERIC(24,16) NOT NULL,

    classification VARCHAR(20) NOT NULL,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_classification
        CHECK (classification IN ('NORMAL', 'ANOMALY')),

    CONSTRAINT nonnegative_distance
        CHECK (mahalanobis_distance >= 0),

    CONSTRAINT nonnegative_density
        CHECK (probability_density >= 0)
);

CREATE INDEX IF NOT EXISTS idx_evaluations_profile
    ON distribution_evaluations(profile_id, evaluated_at DESC);

-- ============================================================================
-- 2. SAMPLE DATA
-- ============================================================================

INSERT INTO datasets(dataset_name, description)
VALUES (
    'sales_performance',
    'Sales observations with advertising and training predictors.'
)
ON CONFLICT (dataset_name) DO NOTHING;

INSERT INTO observations (
    dataset_id,
    advertising,
    training_hours,
    sales
)
SELECT
    d.dataset_id,
    v.advertising,
    v.training_hours,
    v.sales
FROM datasets d
CROSS JOIN (
    VALUES
        (10, 2, 40),
        (12, 3, 44),
        (14, 4, 49),
        (16, 3, 50),
        (18, 5, 57),
        (20, 6, 63),
        (22, 5, 65),
        (24, 7, 72),
        (26, 8, 78),
        (28, 7, 80),
        (30, 9, 87),
        (32, 10, 94)
) AS v(advertising, training_hours, sales)
WHERE d.dataset_name = 'sales_performance'
AND NOT EXISTS (
    SELECT 1
    FROM observations o
    WHERE o.dataset_id = d.dataset_id
);

INSERT INTO distribution_profiles (
    profile_name,
    mean_one,
    mean_two,
    variance_one,
    variance_two,
    covariance_value
)
VALUES (
    'business_performance_profile',
    50,
    60,
    100,
    144,
    30
)
ON CONFLICT (profile_name) DO NOTHING;

-- ============================================================================
-- 3. DESCRIPTIVE STATISTICS
-- ============================================================================

CREATE OR REPLACE VIEW descriptive_statistics AS
SELECT
    d.dataset_id,
    d.dataset_name,
    COUNT(o.observation_id) AS observation_count,

    AVG(o.advertising) AS mean_advertising,
    AVG(o.training_hours) AS mean_training_hours,
    AVG(o.sales) AS mean_sales,

    VAR_SAMP(o.advertising) AS variance_advertising,
    VAR_SAMP(o.training_hours) AS variance_training_hours,
    VAR_SAMP(o.sales) AS variance_sales,

    STDDEV_SAMP(o.advertising) AS sd_advertising,
    STDDEV_SAMP(o.training_hours) AS sd_training_hours,
    STDDEV_SAMP(o.sales) AS sd_sales,

    MIN(o.sales) AS minimum_sales,
    MAX(o.sales) AS maximum_sales

FROM datasets d
LEFT JOIN observations o
    ON o.dataset_id = d.dataset_id

GROUP BY d.dataset_id, d.dataset_name;

-- ============================================================================
-- 4. COVARIANCE AND CORRELATION STRUCTURE
-- ============================================================================

CREATE OR REPLACE VIEW predictor_covariance AS
SELECT
    dataset_id,
    COVAR_SAMP(advertising, training_hours)
        AS advertising_training_covariance,

    CORR(advertising, training_hours)
        AS advertising_training_correlation,

    COVAR_SAMP(advertising, sales)
        AS advertising_sales_covariance,

    CORR(advertising, sales)
        AS advertising_sales_correlation,

    COVAR_SAMP(training_hours, sales)
        AS training_sales_covariance,

    CORR(training_hours, sales)
        AS training_sales_correlation

FROM observations
GROUP BY dataset_id;

CREATE OR REPLACE FUNCTION refresh_covariance_structure(
    p_dataset_id BIGINT
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    inserted_count INTEGER;
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM datasets
        WHERE dataset_id = p_dataset_id
    ) THEN
        RAISE EXCEPTION 'Dataset % does not exist', p_dataset_id;
    END IF;

    DELETE FROM covariance_structures
    WHERE dataset_id = p_dataset_id;

    INSERT INTO covariance_structures (
        dataset_id,
        variable_one,
        variable_two,
        covariance_value,
        correlation_value
    )
    SELECT
        p_dataset_id,
        'advertising',
        'training_hours',
        COVAR_SAMP(advertising, training_hours),
        CORR(advertising, training_hours)
    FROM observations
    WHERE dataset_id = p_dataset_id
    HAVING COUNT(*) >= 2

    UNION ALL

    SELECT
        p_dataset_id,
        'advertising',
        'sales',
        COVAR_SAMP(advertising, sales),
        CORR(advertising, sales)
    FROM observations
    WHERE dataset_id = p_dataset_id
    HAVING COUNT(*) >= 2

    UNION ALL

    SELECT
        p_dataset_id,
        'training_hours',
        'sales',
        COVAR_SAMP(training_hours, sales),
        CORR(training_hours, sales)
    FROM observations
    WHERE dataset_id = p_dataset_id
    HAVING COUNT(*) >= 2;

    GET DIAGNOSTICS inserted_count = ROW_COUNT;

    RETURN inserted_count;
END;
$$;

-- ============================================================================
-- 5. MULTIPLE LINEAR REGRESSION
-- ============================================================================

/*
Model:

sales = beta_0 + beta_1 * advertising
              + beta_2 * training_hours + error

Normal equations:

(X'X) beta = X'y

The implementation solves the resulting three-parameter system
using explicit Gaussian elimination with partial pivoting.
*/

CREATE OR REPLACE FUNCTION fit_multiple_regression(
    p_dataset_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    n DOUBLE PRECISION;

    sx DOUBLE PRECISION;
    sz DOUBLE PRECISION;
    sy DOUBLE PRECISION;

    sxx DOUBLE PRECISION;
    szz DOUBLE PRECISION;
    sxz DOUBLE PRECISION;

    sxy DOUBLE PRECISION;
    szy DOUBLE PRECISION;
    syy DOUBLE PRECISION;

    m DOUBLE PRECISION[3][4];

    pivot_row INTEGER;
    row_index INTEGER;
    col_index INTEGER;

    pivot_value DOUBLE PRECISION;
    factor DOUBLE PRECISION;

    b0 DOUBLE PRECISION;
    b1 DOUBLE PRECISION;
    b2 DOUBLE PRECISION;

    ss_res DOUBLE PRECISION;
    ss_total DOUBLE PRECISION;

    r2 DOUBLE PRECISION;
    adjusted_r2 DOUBLE PRECISION;
    rmse_value DOUBLE PRECISION;
    residual_var DOUBLE PRECISION;

    new_model_id BIGINT;

BEGIN
    SELECT
        COUNT(*)::DOUBLE PRECISION,
        SUM(advertising),
        SUM(training_hours),
        SUM(sales),

        SUM(advertising * advertising),
        SUM(training_hours * training_hours),
        SUM(advertising * training_hours),

        SUM(advertising * sales),
        SUM(training_hours * sales),
        SUM(sales * sales)

    INTO
        n, sx, sz, sy,
        sxx, szz, sxz,
        sxy, szy, syy

    FROM observations
    WHERE dataset_id = p_dataset_id;

    IF n IS NULL OR n <= 3 THEN
        RAISE EXCEPTION
            'At least four observations are required';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM datasets
        WHERE dataset_id = p_dataset_id
        AND status <> 'ACTIVE'
    ) THEN
        RAISE EXCEPTION 'Archived datasets cannot be fitted';
    END IF;

    /*
       Construct the augmented normal-equation matrix.

       [ n    sx    sz | sy  ]
       [ sx   sxx   sxz| sxy ]
       [ sz   sxz   szz| szy ]
    */

    m[1][1] := n;
    m[1][2] := sx;
    m[1][3] := sz;
    m[1][4] := sy;

    m[2][1] := sx;
    m[2][2] := sxx;
    m[2][3] := sxz;
    m[2][4] := sxy;

    m[3][1] := sz;
    m[3][2] := sxz;
    m[3][3] := szz;
    m[3][4] := szy;

    -- Gaussian elimination with partial pivoting.

    FOR col_index IN 1..3 LOOP

        pivot_row := col_index;

        FOR row_index IN col_index..3 LOOP
            IF ABS(m[row_index][col_index]) >
               ABS(m[pivot_row][col_index]) THEN
                pivot_row := row_index;
            END IF;
        END LOOP;

        IF ABS(m[pivot_row][col_index]) < 1e-12 THEN
            RAISE EXCEPTION
                'Singular or numerically unstable design matrix';
        END IF;

        IF pivot_row <> col_index THEN
            FOR row_index IN 1..4 LOOP
                factor := m[col_index][row_index];
                m[col_index][row_index] :=
                    m[pivot_row][row_index];
                m[pivot_row][row_index] := factor;
            END LOOP;
        END IF;

        pivot_value := m[col_index][col_index];

        FOR row_index IN col_index..4 LOOP
            m[col_index][row_index] :=
                m[col_index][row_index] / pivot_value;
        END LOOP;

        FOR row_index IN 1..3 LOOP
            IF row_index <> col_index THEN
                factor := m[row_index][col_index];

                FOR col_index IN col_index..4 LOOP
                    m[row_index][col_index] :=
                        m[row_index][col_index] -
                        factor * m[pivot_row][col_index];
                END LOOP;
            END IF;
        END LOOP;

    END LOOP;

    b0 := m[1][4];
    b1 := m[2][4];
    b2 := m[3][4];

    -- Calculate residual and total sums of squares.

    SELECT
        SUM(
            POWER(
                sales - (
                    b0 +
                    b1 * advertising +
                    b2 * training_hours
                ),
                2
            )
        ),
        SUM(POWER(sales - sy / n, 2))

    INTO ss_res, ss_total

    FROM observations
    WHERE dataset_id = p_dataset_id;

    IF ss_total IS NULL OR ss_total <= 0 THEN
        RAISE EXCEPTION
            'R-squared is undefined for constant target';
    END IF;

    r2 := 1 - ss_res / ss_total;

    adjusted_r2 :=
        1 - (1 - r2) * (n - 1) / (n - 3);

    rmse_value := SQRT(ss_res / n);

    residual_var := ss_res / (n - 3);

    INSERT INTO regression_models (
        dataset_id,
        intercept,
        beta_advertising,
        beta_training,
        r_squared,
        adjusted_r_squared,
        rmse,
        residual_variance,
        training_count
    )
    VALUES (
        p_dataset_id,
        b0,
        b1,
        b2,
        r2,
        adjusted_r2,
        rmse_value,
        residual_var,
        n::INTEGER
    )
    RETURNING model_id INTO new_model_id;

    RETURN new_model_id;
END;
$$;

-- ============================================================================
-- 6. PREDICTION AND MODEL EVALUATION
-- ============================================================================

CREATE OR REPLACE VIEW regression_model_report AS
SELECT
    m.model_id,
    d.dataset_name,
    m.intercept,
    m.beta_advertising,
    m.beta_training,
    m.r_squared,
    m.adjusted_r_squared,
    m.rmse,
    m.residual_variance,
    m.training_count,
    m.fitted_at

FROM regression_models m
JOIN datasets d
    ON d.dataset_id = m.dataset_id;

CREATE OR REPLACE FUNCTION predict_sales(
    p_model_id BIGINT,
    p_advertising NUMERIC,
    p_training_hours NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    result NUMERIC;
BEGIN
    IF p_advertising < 0 OR p_training_hours < 0 THEN
        RAISE EXCEPTION 'Predictor values cannot be negative';
    END IF;

    SELECT
        intercept +
        beta_advertising * p_advertising +
        beta_training * p_training_hours

    INTO result

    FROM regression_models
    WHERE model_id = p_model_id;

    IF result IS NULL THEN
        RAISE EXCEPTION 'Model % does not exist', p_model_id;
    END IF;

    RETURN result;
END;
$$;

CREATE OR REPLACE VIEW regression_residual_report AS
SELECT
    m.model_id,
    o.observation_id,
    o.sales AS actual_sales,

    m.intercept +
    m.beta_advertising * o.advertising +
    m.beta_training * o.training_hours AS predicted_sales,

    o.sales -
    (
        m.intercept +
        m.beta_advertising * o.advertising +
        m.beta_training * o.training_hours
    ) AS residual

FROM regression_models m
JOIN observations o
    ON o.dataset_id = m.dataset_id;

-- ============================================================================
-- 7. MULTIVARIATE NORMAL DISTRIBUTION
-- ============================================================================

/*
For a two-dimensional multivariate normal distribution:

Sigma = [ variance_one   covariance ]
        [ covariance     variance_two ]

Determinant:

|Sigma| = variance_one * variance_two - covariance^2

Mahalanobis squared distance:

D² = (x1-mu1)^2 * variance_two / determinant
   + (x2-mu2)^2 * variance_one / determinant
   - 2 * covariance * (x1-mu1) * (x2-mu2) / determinant

Density:

f(x) = exp(-D²/2) / (2*pi*sqrt(|Sigma|))
*/

CREATE OR REPLACE FUNCTION mahalanobis_distance_2d(
    p_x1 NUMERIC,
    p_x2 NUMERIC,
    p_mean1 NUMERIC,
    p_mean2 NUMERIC,
    p_variance1 NUMERIC,
    p_variance2 NUMERIC,
    p_covariance NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    determinant NUMERIC;
    d1 NUMERIC;
    d2 NUMERIC;
    distance_squared NUMERIC;
BEGIN
    determinant :=
        p_variance1 * p_variance2 -
        POWER(p_covariance, 2);

    IF determinant <= 0 THEN
        RAISE EXCEPTION
            'Covariance matrix must be positive definite';
    END IF;

    d1 := p_x1 - p_mean1;
    d2 := p_x2 - p_mean2;

    distance_squared := (
        p_variance2 * POWER(d1, 2)
        + p_variance1 * POWER(d2, 2)
        - 2 * p_covariance * d1 * d2
    ) / determinant;

    IF distance_squared < -1e-10 THEN
        RAISE EXCEPTION 'Invalid Mahalanobis distance';
    END IF;

    RETURN SQRT(GREATEST(distance_squared, 0));
END;
$$;

CREATE OR REPLACE FUNCTION multivariate_normal_density_2d(
    p_x1 NUMERIC,
    p_x2 NUMERIC,
    p_mean1 NUMERIC,
    p_mean2 NUMERIC,
    p_variance1 NUMERIC,
    p_variance2 NUMERIC,
    p_covariance NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    determinant NUMERIC;
    distance NUMERIC;
BEGIN
    determinant :=
        p_variance1 * p_variance2 -
        POWER(p_covariance, 2);

    IF determinant <= 0 THEN
        RAISE EXCEPTION
            'Covariance matrix must be positive definite';
    END IF;

    distance := mahalanobis_distance_2d(
        p_x1,
        p_x2,
        p_mean1,
        p_mean2,
        p_variance1,
        p_variance2,
        p_covariance
    );

    RETURN EXP(-0.5 * POWER(distance, 2)) /
        (2 * PI() * SQRT(determinant));
END;
$$;

-- ============================================================================
-- 8. DISTRIBUTION EVALUATION AND ANOMALY CLASSIFICATION
-- ============================================================================

CREATE OR REPLACE FUNCTION evaluate_observation(
    p_profile_id BIGINT,
    p_observation_one NUMERIC,
    p_observation_two NUMERIC,
    p_threshold NUMERIC DEFAULT 3.0
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    profile distribution_profiles%ROWTYPE;

    distance NUMERIC;
    density NUMERIC;

    classification_value VARCHAR(20);
    new_id BIGINT;
BEGIN
    IF p_threshold <= 0 THEN
        RAISE EXCEPTION 'Threshold must be positive';
    END IF;

    SELECT *
    INTO profile
    FROM distribution_profiles
    WHERE profile_id = p_profile_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Distribution profile not found';
    END IF;

    distance := mahalanobis_distance_2d(
        p_observation_one,
        p_observation_two,
        profile.mean_one,
        profile.mean_two,
        profile.variance_one,
        profile.variance_two,
        profile.covariance_value
    );

    density := multivariate_normal_density_2d(
        p_observation_one,
        p_observation_two,
        profile.mean_one,
        profile.mean_two,
        profile.variance_one,
        profile.variance_two,
        profile.covariance_value
    );

    classification_value :=
        CASE
            WHEN distance > p_threshold THEN 'ANOMALY'
            ELSE 'NORMAL'
        END;

    INSERT INTO distribution_evaluations (
        profile_id,
        observation_one,
        observation_two,
        mahalanobis_distance,
        probability_density,
        classification
    )
    VALUES (
        p_profile_id,
        p_observation_one,
        p_observation_two,
        distance,
        density,
        classification_value
    )
    RETURNING evaluation_id INTO new_id;

    RETURN new_id;
END;
$$;

-- ============================================================================
-- 9. STATISTICAL REPORTING
-- ============================================================================

CREATE OR REPLACE VIEW anomaly_summary AS
SELECT
    p.profile_name,
    COUNT(e.evaluation_id) AS total_evaluations,

    COUNT(*) FILTER (
        WHERE e.classification = 'NORMAL'
    ) AS normal_observations,

    COUNT(*) FILTER (
        WHERE e.classification = 'ANOMALY'
    ) AS anomalies,

    AVG(e.mahalanobis_distance) AS average_distance,
    MAX(e.mahalanobis_distance) AS maximum_distance,

    AVG(e.probability_density) AS average_density

FROM distribution_profiles p
LEFT JOIN distribution_evaluations e
    ON e.profile_id = p.profile_id

GROUP BY p.profile_id, p.profile_name;

-- ============================================================================
-- 10. EXECUTE THE ANALYTICAL WORKFLOW
-- ============================================================================

DO $$
DECLARE
    dataset_key BIGINT;
    model_key BIGINT;
    profile_key BIGINT;
    evaluation_key BIGINT;
BEGIN
    SELECT dataset_id
    INTO dataset_key
    FROM datasets
    WHERE dataset_name = 'sales_performance';

    PERFORM refresh_covariance_structure(dataset_key);

    model_key := fit_multiple_regression(dataset_key);

    RAISE NOTICE 'Regression model created: %', model_key;

    RAISE NOTICE 'Predicted sales: %',
        predict_sales(model_key, 25, 6);

    SELECT profile_id
    INTO profile_key
    FROM distribution_profiles
    WHERE profile_name = 'business_performance_profile';

    evaluation_key := evaluate_observation(
        profile_key,
        55,
        65,
        2.5
    );

    RAISE NOTICE 'Distribution evaluation created: %',
        evaluation_key;

    -- Deliberately extreme observation for anomaly demonstration.
    evaluation_key := evaluate_observation(
        profile_key,
        90,
        120,
        2.5
    );

    RAISE NOTICE 'Anomaly evaluation created: %',
        evaluation_key;
END;
$$;

-- ============================================================================
-- 11. VALIDATION QUERIES
-- ============================================================================

-- Descriptive statistics.
SELECT *
FROM descriptive_statistics;

-- Predictor covariance and correlation.
SELECT *
FROM predictor_covariance;

-- Persisted covariance structures.
SELECT *
FROM covariance_structures
ORDER BY covariance_id;

-- Regression coefficients and model performance.
SELECT *
FROM regression_model_report
ORDER BY model_id;

-- Actual and predicted observations.
SELECT *
FROM regression_residual_report
ORDER BY model_id, observation_id;

-- Prediction using a fitted model.
SELECT
    model_id,
    predict_sales(model_id, 25, 6) AS predicted_sales
FROM regression_models;

-- Distribution evaluation.
SELECT *
FROM distribution_evaluations
ORDER BY evaluation_id;

-- Normal and anomalous observations.
SELECT *
FROM anomaly_summary;

-- ============================================================================
-- 12. TRANSACTION AND FAILURE VALIDATION
-- ============================================================================

/*
The following transaction demonstrates rollback when a statistical
operation violates a positive-definiteness requirement.
*/

DO $$
BEGIN
    BEGIN
        PERFORM mahalanobis_distance_2d(
            10, 20,
            0, 0,
            1, 1,
            2
        );

        RAISE EXCEPTION
            'Expected positive-definiteness validation failure';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Invalid covariance rejected: %',
                SQLERRM;
    END;
END;
$$;

-- ============================================================================
-- 13. PERFORMANCE AND OPERATIONAL NOTES
-- ============================================================================

/*
1. Dataset indexes support filtering by dataset and observation time.
2. Aggregation views compute covariance and correlation at dataset level.
3. Regression fitting uses sufficient statistics rather than repeatedly
   materializing the complete design matrix.
4. The regression implementation is limited to two predictors.
5. The multivariate normal implementation is limited to two dimensions.
6. Larger models should use a numerically stable QR or SVD implementation.
7. Covariance matrices estimated from limited observations may be singular.
8. Statistical anomaly thresholds require calibration to the distribution
   and operational false-positive requirements.
9. Prediction outside the training feature range is extrapolation.
10. Database permissions should restrict modification of fitted models
    and distribution profiles in production.
*/

COMMIT;
