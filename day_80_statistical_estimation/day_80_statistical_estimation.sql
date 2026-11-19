-- ============================================================
-- STATISTICAL ESTIMATION DATABASE
-- PostgreSQL 14+
--
-- Domain:
--   Datasets
--   Observations
--   Estimation requests
--   Point estimates
--   Confidence intervals
--   Estimator definitions
--   Estimator evaluation
--   Statistical reporting
--
-- Statistical methods:
--   Arithmetic mean
--   Unbiased sample variance
--   Maximum likelihood variance
--   Sample proportion
--   Exponential distribution MLE
--   Normal confidence interval
--   Student's t confidence interval
--   Wilson confidence interval
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS statistical;

SET search_path TO statistical, public;

-- ------------------------------------------------------------
-- 1. ENUMERATIONS
-- ------------------------------------------------------------

CREATE TYPE dataset_status AS ENUM (
    'DRAFT',
    'VALIDATED',
    'ACTIVE',
    'ARCHIVED'
);

CREATE TYPE estimation_status AS ENUM (
    'PENDING',
    'RUNNING',
    'COMPLETED',
    'REJECTED',
    'FAILED'
);

CREATE TYPE estimator_method AS ENUM (
    'ARITHMETIC_MEAN',
    'UNBIASED_VARIANCE',
    'MLE_VARIANCE',
    'SAMPLE_PROPORTION',
    'EXPONENTIAL_MLE'
);

CREATE TYPE interval_method AS ENUM (
    'NORMAL',
    'STUDENT_T',
    'WILSON',
    'BOOTSTRAP'
);

CREATE TYPE parameter_type AS ENUM (
    'MEAN',
    'VARIANCE',
    'PROPORTION',
    'EXPONENTIAL_RATE'
);

-- ------------------------------------------------------------
-- 2. ESTIMATOR DEFINITIONS
-- ------------------------------------------------------------

CREATE TABLE estimator_definitions (
    estimator_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    estimator_code VARCHAR(60) NOT NULL UNIQUE,
    estimator_name VARCHAR(150) NOT NULL,
    parameter parameter_type NOT NULL,
    method estimator_method NOT NULL,
    description TEXT NOT NULL,
    requires_minimum_two BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO estimator_definitions (
    estimator_code,
    estimator_name,
    parameter,
    method,
    description,
    requires_minimum_two
)
VALUES
(
    'MEAN_001',
    'Arithmetic Sample Mean',
    'MEAN',
    'ARITHMETIC_MEAN',
    'Estimates the population mean using the arithmetic sample mean.',
    FALSE
),
(
    'VAR_001',
    'Unbiased Sample Variance',
    'VARIANCE',
    'UNBIASED_VARIANCE',
    'Uses the Bessel-corrected sample variance.',
    TRUE
),
(
    'VAR_002',
    'Maximum Likelihood Variance',
    'VARIANCE',
    'MLE_VARIANCE',
    'Uses the maximum likelihood variance estimator with denominator n.',
    FALSE
),
(
    'PROP_001',
    'Sample Proportion',
    'PROPORTION',
    'SAMPLE_PROPORTION',
    'Estimates a Bernoulli population proportion.',
    FALSE
),
(
    'EXP_001',
    'Exponential Rate MLE',
    'EXPONENTIAL_RATE',
    'EXPONENTIAL_MLE',
    'Estimates the exponential distribution rate using reciprocal sample mean.',
    FALSE
);

-- ------------------------------------------------------------
-- 3. DATASETS
-- ------------------------------------------------------------

CREATE TABLE datasets (
    dataset_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_name VARCHAR(150) NOT NULL,
    description TEXT,
    variable_name VARCHAR(100) NOT NULL,
    variable_unit VARCHAR(50),
    data_type VARCHAR(20) NOT NULL
        CHECK (data_type IN ('CONTINUOUS', 'BINARY')),
    status dataset_status NOT NULL DEFAULT 'DRAFT',
    true_parameter NUMERIC(18, 8),
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    validated_at TIMESTAMPTZ,

    CHECK (
        true_parameter IS NULL
        OR true_parameter::TEXT <> 'NaN'
    )
);

CREATE TABLE observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_id BIGINT NOT NULL
        REFERENCES datasets(dataset_id) ON DELETE CASCADE,
    observation_index INTEGER NOT NULL CHECK (observation_index > 0),
    observed_value NUMERIC(20, 8) NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (dataset_id, observation_index),

    CHECK (
        observed_value::TEXT NOT IN ('NaN', 'Infinity', '-Infinity')
    )
);

CREATE INDEX idx_observations_dataset
    ON observations(dataset_id, observation_index);

CREATE INDEX idx_datasets_status
    ON datasets(status);

-- ------------------------------------------------------------
-- 4. ESTIMATION REQUESTS
-- ------------------------------------------------------------

CREATE TABLE estimation_requests (
    request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    request_code VARCHAR(80) NOT NULL UNIQUE,
    dataset_id BIGINT NOT NULL
        REFERENCES datasets(dataset_id),
    estimator_id BIGINT NOT NULL
        REFERENCES estimator_definitions(estimator_id),
    status estimation_status NOT NULL DEFAULT 'PENDING',
    confidence_level NUMERIC(6, 5) NOT NULL DEFAULT 0.95,
    requested_by VARCHAR(100) NOT NULL,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    failure_reason TEXT,

    CHECK (
        confidence_level > 0
        AND confidence_level < 1
    ),

    CHECK (
        completed_at IS NULL
        OR started_at IS NOT NULL
    )
);

CREATE INDEX idx_requests_status
    ON estimation_requests(status, requested_at DESC);

CREATE INDEX idx_requests_dataset
    ON estimation_requests(dataset_id);

-- ------------------------------------------------------------
-- 5. POINT ESTIMATES
-- ------------------------------------------------------------

CREATE TABLE point_estimates (
    estimate_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    request_id BIGINT NOT NULL UNIQUE
        REFERENCES estimation_requests(request_id)
        ON DELETE CASCADE,
    parameter parameter_type NOT NULL,
    estimate_value NUMERIC(24, 12) NOT NULL,
    sample_size INTEGER NOT NULL CHECK (sample_size > 0),
    sample_variance NUMERIC(24, 12),
    standard_error NUMERIC(24, 12),
    estimator_bias NUMERIC(24, 12),
    estimator_variance NUMERIC(24, 12),
    mean_squared_error NUMERIC(24, 12),
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (
        estimate_value::TEXT NOT IN (
            'NaN', 'Infinity', '-Infinity'
        )
    ),

    CHECK (
        parameter <> 'PROPORTION'
        OR estimate_value BETWEEN 0 AND 1
    ),

    CHECK (
        sample_variance IS NULL OR sample_variance >= 0
    ),

    CHECK (
        standard_error IS NULL OR standard_error >= 0
    )
);

CREATE INDEX idx_estimates_parameter
    ON point_estimates(parameter, calculated_at DESC);

-- ------------------------------------------------------------
-- 6. CONFIDENCE INTERVALS
-- ------------------------------------------------------------

CREATE TABLE confidence_intervals (
    interval_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    estimate_id BIGINT NOT NULL
        REFERENCES point_estimates(estimate_id)
        ON DELETE CASCADE,
    method interval_method NOT NULL,
    lower_bound NUMERIC(24, 12) NOT NULL,
    upper_bound NUMERIC(24, 12) NOT NULL,
    confidence_level NUMERIC(6, 5) NOT NULL,
    interval_width NUMERIC(24, 12)
        GENERATED ALWAYS AS (upper_bound - lower_bound) STORED,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (lower_bound <= upper_bound),

    CHECK (
        confidence_level > 0
        AND confidence_level < 1
    ),

    CHECK (
        method <> 'WILSON'
        OR (
            lower_bound >= 0
            AND upper_bound <= 1
        )
    )
);

CREATE INDEX idx_intervals_estimate
    ON confidence_intervals(estimate_id, method);

-- ------------------------------------------------------------
-- 7. ESTIMATOR EVALUATION
-- ------------------------------------------------------------

CREATE TABLE estimator_evaluations (
    evaluation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_id BIGINT NOT NULL REFERENCES datasets(dataset_id),
    estimator_id BIGINT NOT NULL
        REFERENCES estimator_definitions(estimator_id),
    true_parameter NUMERIC(24, 12) NOT NULL,
    average_estimate NUMERIC(24, 12) NOT NULL,
    bias NUMERIC(24, 12) NOT NULL,
    estimator_variance NUMERIC(24, 12) NOT NULL
        CHECK (estimator_variance >= 0),
    mse NUMERIC(24, 12) NOT NULL CHECK (mse >= 0),
    repetitions INTEGER NOT NULL CHECK (repetitions >= 2),
    sample_size INTEGER NOT NULL CHECK (sample_size >= 1),
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- 8. DATASET VALIDATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_dataset(
    p_dataset_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_type VARCHAR(20);
    v_count BIGINT;
    v_invalid BIGINT;
BEGIN
    SELECT data_type
    INTO v_type
    FROM datasets
    WHERE dataset_id = p_dataset_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Dataset % does not exist.', p_dataset_id;
    END IF;

    SELECT COUNT(*)
    INTO v_count
    FROM observations
    WHERE dataset_id = p_dataset_id;

    IF v_count = 0 THEN
        RAISE EXCEPTION 'Dataset must contain observations.';
    END IF;

    IF v_type = 'BINARY' THEN
        SELECT COUNT(*)
        INTO v_invalid
        FROM observations
        WHERE dataset_id = p_dataset_id
          AND observed_value NOT IN (0, 1);

        IF v_invalid > 0 THEN
            RAISE EXCEPTION
                'Binary dataset contains % invalid observations.',
                v_invalid;
        END IF;
    END IF;

    UPDATE datasets
    SET status = 'VALIDATED',
        validated_at = CURRENT_TIMESTAMP
    WHERE dataset_id = p_dataset_id;

    RETURN TRUE;
END;
$$;

-- Prevent changes to validated or active datasets.
CREATE OR REPLACE FUNCTION enforce_observation_dataset_state()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_status dataset_status;
BEGIN
    SELECT status
    INTO v_status
    FROM datasets
    WHERE dataset_id = COALESCE(NEW.dataset_id, OLD.dataset_id)
    FOR UPDATE;

    IF v_status IN ('VALIDATED', 'ACTIVE', 'ARCHIVED') THEN
        RAISE EXCEPTION
            'Observations cannot be changed in dataset state %.',
            v_status;
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$;

CREATE TRIGGER trg_observation_state
BEFORE INSERT OR UPDATE OR DELETE
ON observations
FOR EACH ROW
EXECUTE FUNCTION enforce_observation_dataset_state();

-- ------------------------------------------------------------
-- 9. ACTIVATE VALIDATED DATASET
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE activate_dataset(
    p_dataset_id BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE datasets
    SET status = 'ACTIVE'
    WHERE dataset_id = p_dataset_id
      AND status = 'VALIDATED';

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Only validated datasets can be activated.';
    END IF;
END;
$$;

-- ------------------------------------------------------------
-- 10. SAMPLE STATISTICS FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_sample_statistics(
    p_dataset_id BIGINT
)
RETURNS TABLE (
    sample_size BIGINT,
    sample_mean NUMERIC,
    sample_variance NUMERIC,
    mle_variance NUMERIC,
    sample_standard_deviation NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM datasets
        WHERE dataset_id = p_dataset_id
          AND status = 'ACTIVE'
    ) THEN
        RAISE EXCEPTION 'Dataset must be active.';
    END IF;

    RETURN QUERY
    SELECT
        COUNT(*),
        AVG(o.observed_value),
        CASE
            WHEN COUNT(*) >= 2
            THEN VAR_SAMP(o.observed_value)
            ELSE NULL
        END,
        VAR_POP(o.observed_value),
        CASE
            WHEN COUNT(*) >= 2
            THEN STDDEV_SAMP(o.observed_value)
            ELSE NULL
        END
    FROM observations o
    WHERE o.dataset_id = p_dataset_id;
END;
$$;

-- ------------------------------------------------------------
-- 11. POINT ESTIMATION FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_point_estimate(
    p_dataset_id BIGINT,
    p_method estimator_method
)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    v_data_type VARCHAR(20);
    v_count BIGINT;
    v_mean NUMERIC;
    v_result NUMERIC;
BEGIN
    SELECT data_type
    INTO v_data_type
    FROM datasets
    WHERE dataset_id = p_dataset_id
      AND status = 'ACTIVE';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Dataset is not active or does not exist.';
    END IF;

    SELECT
        COUNT(*),
        AVG(observed_value)
    INTO v_count, v_mean
    FROM observations
    WHERE dataset_id = p_dataset_id;

    IF v_count = 0 THEN
        RAISE EXCEPTION 'No observations available.';
    END IF;

    CASE p_method

        WHEN 'ARITHMETIC_MEAN' THEN
            v_result := v_mean;

        WHEN 'UNBIASED_VARIANCE' THEN
            IF v_count < 2 THEN
                RAISE EXCEPTION
                    'Unbiased variance requires at least two observations.';
            END IF;

            SELECT VAR_SAMP(observed_value)
            INTO v_result
            FROM observations
            WHERE dataset_id = p_dataset_id;

        WHEN 'MLE_VARIANCE' THEN
            SELECT VAR_POP(observed_value)
            INTO v_result
            FROM observations
            WHERE dataset_id = p_dataset_id;

        WHEN 'SAMPLE_PROPORTION' THEN
            IF v_data_type <> 'BINARY' THEN
                RAISE EXCEPTION
                    'Proportion estimator requires a binary dataset.';
            END IF;

            SELECT AVG(observed_value)
            INTO v_result
            FROM observations
            WHERE dataset_id = p_dataset_id;

        WHEN 'EXPONENTIAL_MLE' THEN
            IF EXISTS (
                SELECT 1
                FROM observations
                WHERE dataset_id = p_dataset_id
                  AND observed_value < 0
            ) THEN
                RAISE EXCEPTION
                    'Exponential observations cannot be negative.';
            END IF;

            IF v_mean <= 0 THEN
                RAISE EXCEPTION
                    'Exponential rate MLE is undefined.';
            END IF;

            v_result := 1 / v_mean;

        ELSE
            RAISE EXCEPTION 'Unsupported estimation method.';
    END CASE;

    RETURN v_result;
END;
$$;

-- ------------------------------------------------------------
-- 12. NORMAL QUANTILE FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION normal_quantile(
    p_probability DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    a DOUBLE PRECISION[] := ARRAY[
        -39.69683028665376,
        220.9460984245205,
        -275.9285104469687,
        138.3577518672690,
        -30.66479806614716,
        2.506628277459239
    ];

    b DOUBLE PRECISION[] := ARRAY[
        -54.47609879822406,
        161.5858368580409,
        -155.6989798598866,
        66.80131188771972,
        -13.28068155288572
    ];

    c DOUBLE PRECISION[] := ARRAY[
        -0.007784894002430293,
        -0.3223964580411365,
        -2.400758277161838,
        -2.549732539343734,
        4.374664141464968,
        2.938163982698783
    ];

    d DOUBLE PRECISION[] := ARRAY[
        0.007784695709041462,
        0.3224671290700398,
        2.445134137142996,
        3.754408661907416
    ];

    v_q DOUBLE PRECISION;
    v_r DOUBLE PRECISION;
    v_num DOUBLE PRECISION;
    v_den DOUBLE PRECISION;
    i INTEGER;
BEGIN
    IF p_probability <= 0 OR p_probability >= 1 THEN
        RAISE EXCEPTION 'Probability must be between zero and one.';
    END IF;

    IF p_probability < 0.02425
       OR p_probability > 0.97575 THEN

        v_q := SQRT(
            -2 * LN(
                CASE
                    WHEN p_probability < 0.5
                    THEN p_probability
                    ELSE 1 - p_probability
                END
            )
        );

        v_num := 0;
        v_den := 1;

        FOR i IN 1..6 LOOP
            v_num := v_num + c[i] * POWER(v_q, 5 - (i - 1));
        END LOOP;

        FOR i IN 1..4 LOOP
            v_den := v_den + d[i] * POWER(v_q, 3 - (i - 1));
        END LOOP;

        RETURN CASE
            WHEN p_probability < 0.5
            THEN v_num / v_den
            ELSE -v_num / v_den
        END;
    END IF;

    v_q := p_probability - 0.5;
    v_r := v_q * v_q;

    v_num := 0;
    v_den := 1;

    FOR i IN 1..6 LOOP
        v_num := v_num
            + a[i] * v_q * POWER(v_r, 2 - (i - 1));
    END LOOP;

    FOR i IN 1..5 LOOP
        v_den := v_den
            + b[i] * POWER(v_r, 2 - (i - 1));
    END LOOP;

    RETURN v_num / v_den;
END;
$$;

-- ------------------------------------------------------------
-- 13. STUDENT T QUANTILE FUNCTION
--
-- Uses the normal approximation for high degrees of freedom.
-- For finite degrees of freedom, the beta-based CDF is
-- inverted using bisection.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION student_t_quantile(
    p_probability DOUBLE PRECISION,
    p_degrees INTEGER
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
AS $$
DECLARE
    v_lower DOUBLE PRECISION := 0;
    v_upper DOUBLE PRECISION := 1;
    v_middle DOUBLE PRECISION;
    v_x DOUBLE PRECISION;
    v_beta DOUBLE PRECISION;
    v_cdf DOUBLE PRECISION;
    v_a DOUBLE PRECISION;
    v_b DOUBLE PRECISION;
    v_bt DOUBLE PRECISION;
    v_c DOUBLE PRECISION;
    v_d DOUBLE PRECISION;
    v_h DOUBLE PRECISION;
    v_aa DOUBLE PRECISION;
    v_delta DOUBLE PRECISION;
    v_qab DOUBLE PRECISION;
    v_qap DOUBLE PRECISION;
    v_qam DOUBLE PRECISION;
    v_m INTEGER;
    v_m2 INTEGER;
    v_iteration INTEGER;
    v_epsilon DOUBLE PRECISION := 3e-14;
    v_tiny DOUBLE PRECISION := 1e-300;
BEGIN
    IF p_degrees < 1 OR p_probability <= 0
       OR p_probability >= 1 THEN
        RAISE EXCEPTION 'Invalid Student t parameters.';
    END IF;

    IF p_probability = 0.5 THEN
        RETURN 0;
    END IF;

    IF p_probability < 0.5 THEN
        RETURN -student_t_quantile(
            1 - p_probability,
            p_degrees
        );
    END IF;

    -- Incomplete beta calculation is performed inside
    -- the quantile inversion to avoid external extensions.

    WHILE TRUE LOOP
        v_x := p_degrees::DOUBLE PRECISION
            / (p_degrees + v_upper * v_upper);

        v_a := p_degrees / 2.0;
        v_b := 0.5;

        v_bt := EXP(
            LGAMMA(v_a + v_b)
            - LGAMMA(v_a)
            - LGAMMA(v_b)
            + v_a * LN(v_x)
            + v_b * LN(1 - v_x)
        );

        v_qab := v_a + v_b;
        v_qap := v_a + 1;
        v_qam := v_a - 1;

        v_c := 1;
        v_d := 1 - v_qab * v_x / v_qap;

        IF ABS(v_d) < v_tiny THEN
            v_d := v_tiny;
        END IF;

        v_d := 1 / v_d;
        v_h := v_d;

        FOR v_m IN 1..300 LOOP
            v_m2 := 2 * v_m;

            v_aa := v_m * (v_b - v_m) * v_x
                / ((v_qam + v_m2) * (v_a + v_m2));

            v_d := 1 + v_aa * v_d;
            IF ABS(v_d) < v_tiny THEN v_d := v_tiny; END IF;

            v_c := 1 + v_aa / v_c;
            IF ABS(v_c) < v_tiny THEN v_c := v_tiny; END IF;

            v_d := 1 / v_d;
            v_h := v_h * v_d * v_c;

            v_aa := -(v_a + v_m) * (v_qab + v_m) * v_x
                / ((v_a + v_m2) * (v_qap + v_m2));

            v_d := 1 + v_aa * v_d;
            IF ABS(v_d) < v_tiny THEN v_d := v_tiny; END IF;

            v_c := 1 + v_aa / v_c;
            IF ABS(v_c) < v_tiny THEN v_c := v_tiny; END IF;

            v_d := 1 / v_d;

            v_delta := v_d * v_c;
            v_h := v_h * v_delta;

            EXIT WHEN ABS(v_delta - 1) < v_epsilon;
        END LOOP;

        IF v_x < (v_a + 1) / (v_a + v_b + 2) THEN
            v_beta := v_bt * v_h / v_a;
        ELSE
            -- Evaluate the complementary beta fraction.
            v_a := 0.5;
            v_b := p_degrees / 2.0;
            v_x := 1 - (
                p_degrees::DOUBLE PRECISION
                / (p_degrees + v_upper * v_upper)
            );

            v_bt := EXP(
                LGAMMA(v_a + v_b)
                - LGAMMA(v_a)
                - LGAMMA(v_b)
                + v_a * LN(v_x)
                + v_b * LN(1 - v_x)
            );

            v_qab := v_a + v_b;
            v_qap := v_a + 1;
            v_qam := v_a - 1;

            v_c := 1;
            v_d := 1 - v_qab * v_x / v_qap;

            IF ABS(v_d) < v_tiny THEN v_d := v_tiny; END IF;

            v_d := 1 / v_d;
            v_h := v_d;

            FOR v_m IN 1..300 LOOP
                v_m2 := 2 * v_m;

                v_aa := v_m * (v_b - v_m) * v_x
                    / ((v_qam + v_m2) * (v_a + v_m2));

                v_d := 1 + v_aa * v_d;
                IF ABS(v_d) < v_tiny THEN v_d := v_tiny; END IF;

                v_c := 1 + v_aa / v_c;
                IF ABS(v_c) < v_tiny THEN v_c := v_tiny; END IF;

                v_d := 1 / v_d;
                v_h := v_h * v_d * v_c;

                v_aa := -(v_a + v_m) * (v_qab + v_m) * v_x
                    / ((v_a + v_m2) * (v_qap + v_m2));

                v_d := 1 + v_aa * v_d;
                IF ABS(v_d) < v_tiny THEN v_d := v_tiny; END IF;

                v_c := 1 + v_aa / v_c;
                IF ABS(v_c) < v_tiny THEN v_c := v_tiny; END IF;

                v_d := 1 / v_d;
                v_delta := v_d * v_c;
                v_h := v_h * v_delta;

                EXIT WHEN ABS(v_delta - 1) < v_epsilon;
            END LOOP;

            v_beta := 1 - v_bt * v_h / v_a;
        END IF;

        v_cdf := 1 - v_beta / 2;

        EXIT WHEN v_cdf >= p_probability;

        v_upper := v_upper * 2;

        IF v_upper > 1e12 THEN
            RAISE EXCEPTION 'Unable to bracket t quantile.';
        END IF;
    END LOOP;

    FOR v_iteration IN 1..120 LOOP
        v_middle := (v_lower + v_upper) / 2;

        v_x := p_degrees::DOUBLE PRECISION
            / (p_degrees + v_middle * v_middle);

        v_a := p_degrees / 2.0;
        v_b := 0.5;

        v_bt := EXP(
            LGAMMA(v_a + v_b)
            - LGAMMA(v_a)
            - LGAMMA(v_b)
            + v_a * LN(v_x)
            + v_b * LN(1 - v_x)
        );

        v_qab := v_a + v_b;
        v_qap := v_a + 1;
        v_qam := v_a - 1;

        v_c := 1;
        v_d := 1 - v_qab * v_x / v_qap;

        IF ABS(v_d) < v_tiny THEN v_d := v_tiny; END IF;

        v_d := 1 / v_d;
        v_h := v_d;

        FOR v_m IN 1..300 LOOP
            v_m2 := 2 * v_m;

            v_aa := v_m * (v_b - v_m) * v_x
                / ((v_qam + v_m2) * (v_a + v_m2));

            v_d := 1 + v_aa * v_d;
            IF ABS(v_d) < v_tiny THEN v_d := v_tiny; END IF;

            v_c := 1 + v_aa / v_c;
            IF ABS(v_c) < v_tiny THEN v_c := v_tiny; END IF;

            v_d := 1 / v_d;
            v_h := v_h * v_d * v_c;

            v_aa := -(v_a + v_m) * (v_qab + v_m) * v_x
                / ((v_a + v_m2) * (v_qap + v_m2));

            v_d := 1 + v_aa * v_d;
            IF ABS(v_d) < v_tiny THEN v_d := v_tiny; END IF;

            v_c := 1 + v_aa / v_c;
            IF ABS(v_c) < v_tiny THEN v_c := v_tiny; END IF;

            v_d := 1 / v_d;
            v_delta := v_d * v_c;
            v_h := v_h * v_delta;

            EXIT WHEN ABS(v_delta - 1) < v_epsilon;
        END LOOP;

        IF v_x < (v_a + 1) / (v_a + v_b + 2) THEN
            v_beta := v_bt * v_h / v_a;
        ELSE
            v_a := 0.5;
            v_b := p_degrees / 2.0;
            v_x := 1 - (
                p_degrees::DOUBLE PRECISION
                / (p_degrees + v_middle * v_middle)
            );

            v_bt := EXP(
                LGAMMA(v_a + v_b)
                - LGAMMA(v_a)
                - LGAMMA(v_b)
                + v_a * LN(v_x)
                + v_b * LN(1 - v_x)
            );

            v_qab := v_a + v_b;
            v_qap := v_a + 1;
            v_qam := v_a - 1;

            v_c := 1;
            v_d := 1 - v_qab * v_x / v_qap;

            IF ABS(v_d) < v_tiny THEN v_d := v_tiny; END IF;

            v_d := 1 / v_d;
            v_h := v_d;

            FOR v_m IN 1..300 LOOP
                v_m2 := 2 * v_m;

                v_aa := v_m * (v_b - v_m) * v_x
                    / ((v_qam + v_m2) * (v_a + v_m2));

                v_d := 1 + v_aa * v_d;
                IF ABS(v_d) < v_tiny THEN v_d := v_tiny; END IF;

                v_c := 1 + v_aa / v_c;
                IF ABS(v_c) < v_tiny THEN v_c := v_tiny; END IF;

                v_d := 1 / v_d;
                v_h := v_h * v_d * v_c;

                v_aa := -(v_a + v_m) * (v_qab + v_m) * v_x
                    / ((v_a + v_m2) * (v_qap + v_m2));

                v_d := 1 + v_aa * v_d;
                IF ABS(v_d) < v_tiny THEN v_d := v_tiny; END IF;

                v_c := 1 + v_aa / v_c;
                IF ABS(v_c) < v_tiny THEN v_c := v_tiny; END IF;

                v_d := 1 / v_d;
                v_delta := v_d * v_c;
                v_h := v_h * v_delta;

                EXIT WHEN ABS(v_delta - 1) < v_epsilon;
            END LOOP;

            v_beta := 1 - v_bt * v_h / v_a;
        END IF;

        v_cdf := 1 - v_beta / 2;

        IF v_cdf < p_probability THEN
            v_lower := v_middle;
        ELSE
            v_upper := v_middle;
        END IF;
    END LOOP;

    RETURN (v_lower + v_upper) / 2;
END;
$$;

-- ------------------------------------------------------------
-- 14. CONFIDENCE INTERVAL CALCULATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_mean_interval(
    p_dataset_id BIGINT,
    p_confidence NUMERIC DEFAULT 0.95,
    p_method interval_method DEFAULT 'STUDENT_T'
)
RETURNS TABLE (
    estimated_mean NUMERIC,
    lower_bound NUMERIC,
    upper_bound NUMERIC,
    standard_error NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_n INTEGER;
    v_mean NUMERIC;
    v_sd NUMERIC;
    v_critical DOUBLE PRECISION;
    v_margin NUMERIC;
BEGIN
    IF p_confidence <= 0 OR p_confidence >= 1 THEN
        RAISE EXCEPTION 'Invalid confidence level.';
    END IF;

    IF p_method NOT IN ('STUDENT_T', 'NORMAL') THEN
        RAISE EXCEPTION 'Invalid mean interval method.';
    END IF;

    SELECT
        COUNT(*)::INTEGER,
        AVG(observed_value),
        STDDEV_SAMP(observed_value)
    INTO v_n, v_mean, v_sd
    FROM observations
    WHERE dataset_id = p_dataset_id;

    IF v_n < 2 THEN
        RAISE EXCEPTION 'At least two observations are required.';
    END IF;

    IF p_method = 'STUDENT_T' THEN
        v_critical := student_t_quantile(
            (1 + p_confidence)::DOUBLE PRECISION / 2,
            v_n - 1
        );
    ELSE
        v_critical := normal_quantile(
            (1 + p_confidence)::DOUBLE PRECISION / 2
        );
    END IF;

    standard_error := v_sd / SQRT(v_n);

    v_margin := v_critical * standard_error;

    estimated_mean := v_mean;
    lower_bound := v_mean - v_margin;
    upper_bound := v_mean + v_margin;

    RETURN NEXT;
END;
$$;

-- ------------------------------------------------------------
-- 15. WILSON PROPORTION INTERVAL
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_wilson_interval(
    p_dataset_id BIGINT,
    p_confidence NUMERIC DEFAULT 0.95
)
RETURNS TABLE (
    estimated_proportion NUMERIC,
    lower_bound NUMERIC,
    upper_bound NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_n NUMERIC;
    v_p NUMERIC;
    v_z NUMERIC;
    v_z2 NUMERIC;
    v_denominator NUMERIC;
    v_center NUMERIC;
    v_margin NUMERIC;
BEGIN
    IF p_confidence <= 0 OR p_confidence >= 1 THEN
        RAISE EXCEPTION 'Invalid confidence level.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM datasets
        WHERE dataset_id = p_dataset_id
          AND data_type = 'BINARY'
    ) THEN
        RAISE EXCEPTION 'Wilson interval requires a binary dataset.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM observations
        WHERE dataset_id = p_dataset_id
          AND observed_value NOT IN (0, 1)
    ) THEN
        RAISE EXCEPTION 'Invalid binary observations.';
    END IF;

    SELECT
        COUNT(*),
        AVG(observed_value)
    INTO v_n, v_p
    FROM observations
    WHERE dataset_id = p_dataset_id;

    IF v_n = 0 THEN
        RAISE EXCEPTION 'Dataset has no observations.';
    END IF;

    v_z := normal_quantile(
        (1 + p_confidence)::DOUBLE PRECISION / 2
    );

    v_z2 := v_z * v_z;

    v_denominator := 1 + v_z2 / v_n;

    v_center := (
        v_p + v_z2 / (2 * v_n)
    ) / v_denominator;

    v_margin := v_z * SQRT(
        v_p * (1 - v_p) / v_n
        + v_z2 / (4 * v_n * v_n)
    ) / v_denominator;

    estimated_proportion := v_p;

    lower_bound := GREATEST(0, v_center - v_margin);
    upper_bound := LEAST(1, v_center + v_margin);

    RETURN NEXT;
END;
$$;

-- ------------------------------------------------------------
-- 16. REQUEST PROCESSING
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE process_estimation_request(
    p_request_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_dataset_id BIGINT;
    v_estimator_id BIGINT;
    v_method estimator_method;
    v_parameter parameter_type;
    v_confidence NUMERIC;
    v_estimate NUMERIC;
    v_count INTEGER;
    v_variance NUMERIC;
    v_standard_error NUMERIC;
    v_estimate_id BIGINT;
    v_interval RECORD;
BEGIN
    SELECT
        r.dataset_id,
        r.estimator_id,
        e.method,
        e.parameter,
        r.confidence_level
    INTO
        v_dataset_id,
        v_estimator_id,
        v_method,
        v_parameter,
        v_confidence
    FROM estimation_requests r
    JOIN estimator_definitions e
      ON e.estimator_id = r.estimator_id
    WHERE r.request_id = p_request_id
      AND r.status = 'PENDING'
      AND e.is_active = TRUE
    FOR UPDATE OF r;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Request does not exist, is not pending, or estimator is inactive.';
    END IF;

    UPDATE estimation_requests
    SET status = 'RUNNING',
        started_at = CURRENT_TIMESTAMP
    WHERE request_id = p_request_id;

    IF NOT EXISTS (
        SELECT 1
        FROM datasets
        WHERE dataset_id = v_dataset_id
          AND status = 'ACTIVE'
    ) THEN
        RAISE EXCEPTION 'Dataset is not active.';
    END IF;

    SELECT COUNT(*)::INTEGER
    INTO v_count
    FROM observations
    WHERE dataset_id = v_dataset_id;

    IF v_count = 0 THEN
        RAISE EXCEPTION 'No observations available.';
    END IF;

    v_estimate := calculate_point_estimate(
        v_dataset_id,
        v_method
    );

    IF v_count >= 2 THEN
        SELECT
            VAR_SAMP(observed_value),
            STDDEV_SAMP(observed_value) / SQRT(v_count)
        INTO v_variance, v_standard_error
        FROM observations
        WHERE dataset_id = v_dataset_id;
    END IF;

    INSERT INTO point_estimates (
        request_id,
        parameter,
        estimate_value,
        sample_size,
        sample_variance,
        standard_error
    )
    VALUES (
        p_request_id,
        v_parameter,
        v_estimate,
        v_count,
        v_variance,
        v_standard_error
    )
    RETURNING estimate_id INTO v_estimate_id;

    IF v_parameter = 'MEAN' AND v_count >= 2 THEN

        SELECT *
        INTO v_interval
        FROM calculate_mean_interval(
            v_dataset_id,
            v_confidence,
            'STUDENT_T'
        );

        INSERT INTO confidence_intervals (
            estimate_id,
            method,
            lower_bound,
            upper_bound,
            confidence_level
        )
        VALUES (
            v_estimate_id,
            'STUDENT_T',
            v_interval.lower_bound,
            v_interval.upper_bound,
            v_confidence
        );

    ELSIF v_parameter = 'PROPORTION' THEN

        SELECT *
        INTO v_interval
        FROM calculate_wilson_interval(
            v_dataset_id,
            v_confidence
        );

        INSERT INTO confidence_intervals (
            estimate_id,
            method,
            lower_bound,
            upper_bound,
            confidence_level
        )
        VALUES (
            v_estimate_id,
            'WILSON',
            v_interval.lower_bound,
            v_interval.upper_bound,
            v_confidence
        );

    END IF;

    UPDATE estimation_requests
    SET status = 'COMPLETED',
        completed_at = CURRENT_TIMESTAMP
    WHERE request_id = p_request_id;
END;
$$;

-- ------------------------------------------------------------
-- 17. REQUEST FAILURE HANDLING
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE reject_estimation_request(
    p_request_id BIGINT,
    p_reason TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_reason IS NULL OR LENGTH(TRIM(p_reason)) = 0 THEN
        RAISE EXCEPTION 'Failure reason is required.';
    END IF;

    UPDATE estimation_requests
    SET status = 'REJECTED',
        failure_reason = p_reason,
        completed_at = CURRENT_TIMESTAMP
    WHERE request_id = p_request_id
      AND status IN ('PENDING', 'RUNNING');

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Request cannot be rejected in its current state.';
    END IF;
END;
$$;

-- ------------------------------------------------------------
-- 18. REPORTING VIEWS
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW estimation_report AS
SELECT
    r.request_code,
    d.dataset_name,
    d.variable_name,
    e.estimator_name,
    pe.parameter,
    pe.estimate_value,
    pe.sample_size,
    pe.standard_error,
    ci.method AS interval_method,
    ci.lower_bound,
    ci.upper_bound,
    ci.interval_width,
    ci.confidence_level,
    r.status,
    r.requested_by,
    r.completed_at
FROM estimation_requests r
JOIN datasets d
    ON d.dataset_id = r.dataset_id
JOIN estimator_definitions e
    ON e.estimator_id = r.estimator_id
LEFT JOIN point_estimates pe
    ON pe.request_id = r.request_id
LEFT JOIN confidence_intervals ci
    ON ci.estimate_id = pe.estimate_id;

CREATE OR REPLACE VIEW dataset_summary AS
SELECT
    d.dataset_id,
    d.dataset_name,
    d.data_type,
    d.status,
    COUNT(o.observation_id) AS observation_count,
    AVG(o.observed_value) AS sample_mean,
    VAR_SAMP(o.observed_value) AS unbiased_variance,
    VAR_POP(o.observed_value) AS mle_variance,
    STDDEV_SAMP(o.observed_value) AS sample_standard_deviation
FROM datasets d
LEFT JOIN observations o
    ON o.dataset_id = d.dataset_id
GROUP BY
    d.dataset_id,
    d.dataset_name,
    d.data_type,
    d.status;

-- ------------------------------------------------------------
-- 19. SAMPLE DATA
-- ------------------------------------------------------------

INSERT INTO datasets (
    dataset_name,
    description,
    variable_name,
    variable_unit,
    data_type,
    created_by,
    true_parameter
)
VALUES
(
    'Employee Productivity Sample',
    'Continuous observations representing productivity scores.',
    'productivity_score',
    'points',
    'CONTINUOUS',
    'research_analyst',
    50.0
),
(
    'Customer Conversion Sample',
    'Binary observations representing successful conversions.',
    'converted',
    'binary',
    'BINARY',
    'marketing_analyst',
    0.60
),
(
    'Exponential Waiting Time Sample',
    'Non-negative waiting-time observations.',
    'waiting_time',
    'minutes',
    'CONTINUOUS',
    'operations_analyst',
    NULL
);

INSERT INTO observations (
    dataset_id,
    observation_index,
    observed_value
)
SELECT
    1,
    value_index,
    observation_value
FROM (
    VALUES
        (1, 48.2),
        (2, 51.1),
        (3, 49.5),
        (4, 52.3),
        (5, 47.8),
        (6, 50.6),
        (7, 53.0),
        (8, 49.9),
        (9, 51.7),
        (10, 48.9),
        (11, 52.1),
        (12, 50.3)
) AS sample(value_index, observation_value);

INSERT INTO observations (
    dataset_id,
    observation_index,
    observed_value
)
SELECT
    2,
    value_index,
    observation_value
FROM (
    VALUES
        (1, 1),
        (2, 1),
        (3, 0),
        (4, 1),
        (5, 0),
        (6, 1),
        (7, 1),
        (8, 0),
        (9, 1),
        (10, 1),
        (11, 0),
        (12, 1),
        (13, 0),
        (14, 1),
        (15, 1),
        (16, 1),
        (17, 0),
        (18, 1),
        (19, 0),
        (20, 1)
) AS sample(value_index, observation_value);

INSERT INTO observations (
    dataset_id,
    observation_index,
    observed_value
)
SELECT
    3,
    value_index,
    observation_value
FROM (
    VALUES
        (1, 1.2),
        (2, 0.8),
        (3, 2.1),
        (4, 1.5),
        (5, 0.9),
        (6, 1.7)
) AS sample(value_index, observation_value);

-- ------------------------------------------------------------
-- 20. VALIDATE AND ACTIVATE DATASETS
-- ------------------------------------------------------------

SELECT validate_dataset(1);
SELECT validate_dataset(2);
SELECT validate_dataset(3);

CALL activate_dataset(1);
CALL activate_dataset(2);
CALL activate_dataset(3);

-- ------------------------------------------------------------
-- 21. CREATE ESTIMATION REQUESTS
-- ------------------------------------------------------------

INSERT INTO estimation_requests (
    request_code,
    dataset_id,
    estimator_id,
    confidence_level,
    requested_by
)
SELECT
    'REQ-MEAN-001',
    1,
    estimator_id,
    0.95,
    'research_analyst'
FROM estimator_definitions
WHERE estimator_code = 'MEAN_001';

INSERT INTO estimation_requests (
    request_code,
    dataset_id,
    estimator_id,
    confidence_level,
    requested_by
)
SELECT
    'REQ-VAR-001',
    1,
    estimator_id,
    0.95,
    'research_analyst'
FROM estimator_definitions
WHERE estimator_code = 'VAR_001';

INSERT INTO estimation_requests (
    request_code,
    dataset_id,
    estimator_id,
    confidence_level,
    requested_by
)
SELECT
    'REQ-PROP-001',
    2,
    estimator_id,
    0.95,
    'marketing_analyst'
FROM estimator_definitions
WHERE estimator_code = 'PROP_001';

INSERT INTO estimation_requests (
    request_code,
    dataset_id,
    estimator_id,
    confidence_level,
    requested_by
)
SELECT
    'REQ-EXP-001',
    3,
    estimator_id,
    0.95,
    'operations_analyst'
FROM estimator_definitions
WHERE estimator_code = 'EXP_001';

-- ------------------------------------------------------------
-- 22. PROCESS REQUESTS
-- ------------------------------------------------------------

CALL process_estimation_request(
    (SELECT request_id
     FROM estimation_requests
     WHERE request_code = 'REQ-MEAN-001')
);

CALL process_estimation_request(
    (SELECT request_id
     FROM estimation_requests
     WHERE request_code = 'REQ-VAR-001')
);

CALL process_estimation_request(
    (SELECT request_id
     FROM estimation_requests
     WHERE request_code = 'REQ-PROP-001')
);

CALL process_estimation_request(
    (SELECT request_id
     FROM estimation_requests
     WHERE request_code = 'REQ-EXP-001')
);

-- ------------------------------------------------------------
-- 23. RETRIEVAL QUERIES
-- ------------------------------------------------------------

SELECT *
FROM dataset_summary
ORDER BY dataset_id;

SELECT *
FROM estimation_report
ORDER BY request_code, interval_method;

SELECT *
FROM observations
WHERE dataset_id = 1
ORDER BY observation_index;

-- ------------------------------------------------------------
-- 24. VALIDATION QUERIES
-- ------------------------------------------------------------

SELECT
    dataset_id,
    dataset_name,
    data_type,
    observation_count,
    CASE
        WHEN observation_count = 0 THEN 'EMPTY'
        WHEN data_type = 'BINARY'
             AND (
                 sample_mean < 0 OR sample_mean > 1
             )
            THEN 'INVALID_PROPORTION'
        ELSE 'VALID'
    END AS validation_result
FROM dataset_summary;

-- ------------------------------------------------------------
-- 25. AGGREGATION AND ESTIMATOR COMPARISON
-- ------------------------------------------------------------

SELECT
    d.dataset_name,
    COUNT(o.observation_id) AS n,
    AVG(o.observed_value) AS arithmetic_mean,
    VAR_SAMP(o.observed_value) AS unbiased_variance,
    VAR_POP(o.observed_value) AS mle_variance,
    STDDEV_SAMP(o.observed_value) AS sample_standard_deviation
FROM datasets d
JOIN observations o
    ON o.dataset_id = d.dataset_id
WHERE d.dataset_id = 1
GROUP BY d.dataset_name;

-- ------------------------------------------------------------
-- 26. ESTIMATOR ELIGIBILITY
-- ------------------------------------------------------------

SELECT
    d.dataset_name,
    e.estimator_code,
    e.estimator_name,
    CASE
        WHEN d.status <> 'ACTIVE'
            THEN 'INELIGIBLE_DATASET_STATE'
        WHEN NOT e.is_active
            THEN 'INACTIVE_ESTIMATOR'
        WHEN e.requires_minimum_two
             AND counts.n < 2
            THEN 'INSUFFICIENT_SAMPLE_SIZE'
        WHEN e.method = 'SAMPLE_PROPORTION'
             AND d.data_type <> 'BINARY'
            THEN 'INVALID_DATA_TYPE'
        ELSE 'ELIGIBLE'
    END AS eligibility
FROM datasets d
CROSS JOIN estimator_definitions e
CROSS JOIN LATERAL (
    SELECT COUNT(*) AS n
    FROM observations o
    WHERE o.dataset_id = d.dataset_id
) counts
ORDER BY d.dataset_id, e.estimator_id;

-- ------------------------------------------------------------
-- 27. ESTIMATOR PERFORMANCE REPORT
-- ------------------------------------------------------------

SELECT
    estimator_name,
    parameter,
    AVG(bias) AS average_bias,
    AVG(estimator_variance) AS average_variance,
    AVG(mse) AS average_mse,
    SUM(repetitions) AS total_repetitions
FROM estimator_evaluations ev
JOIN estimator_definitions ed
    ON ed.estimator_id = ev.estimator_id
GROUP BY estimator_name, parameter
ORDER BY average_mse;

-- ------------------------------------------------------------
-- 28. TRANSACTIONAL FAILURE DEMONSTRATION
--
-- A failed operation is rolled back without changing
-- previously committed estimation records.
-- ------------------------------------------------------------

SAVEPOINT estimation_validation_point;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM estimation_requests
        WHERE request_code = 'REQ-MEAN-001'
          AND status <> 'COMPLETED'
    ) THEN
        RAISE EXCEPTION 'Mean estimation has not completed.';
    END IF;
END;
$$;

RELEASE SAVEPOINT estimation_validation_point;

COMMIT;

-- ------------------------------------------------------------
-- 29. OPERATIONAL QUERIES
-- ------------------------------------------------------------

-- Completed estimation requests.
SELECT
    request_code,
    status,
    requested_by,
    requested_at,
    completed_at
FROM estimation_requests
WHERE status = 'COMPLETED'
ORDER BY completed_at DESC;

-- Requests that require investigation.
SELECT
    request_code,
    status,
    failure_reason,
    requested_at
FROM estimation_requests
WHERE status IN ('FAILED', 'REJECTED');

-- Confidence interval precision comparison.
SELECT
    d.dataset_name,
    ci.method,
    ci.confidence_level,
    ci.interval_width
FROM confidence_intervals ci
JOIN point_estimates pe
    ON pe.estimate_id = ci.estimate_id
JOIN estimation_requests r
    ON r.request_id = pe.request_id
JOIN datasets d
    ON d.dataset_id = r.dataset_id
ORDER BY d.dataset_name, ci.interval_width;

-- ============================================================
-- END OF STATISTICAL ESTIMATION DATABASE
-- ============================================================
