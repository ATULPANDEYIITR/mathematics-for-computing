-- ============================================================
-- INFORMATION-THEORETIC MEASURES
-- Mutual Information, Conditional Entropy, Information Gain
--
-- PostgreSQL 14+
--
-- Implements:
-- 1. Categorical datasets and feature observations
-- 2. Probability distributions and frequencies
-- 3. Shannon entropy
-- 4. Conditional entropy
-- 5. Joint entropy
-- 6. Mutual information
-- 7. Conditional mutual information
-- 8. Information gain
-- 9. Normalized mutual information
-- 10. Feature selection and ranking
-- 11. Dataset validation and integrity constraints
-- 12. Aggregated reporting
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS information_theory;

SET search_path TO information_theory, public;

-- ------------------------------------------------------------
-- 1. DOMAIN TYPES
-- ------------------------------------------------------------

CREATE TYPE dataset_status AS ENUM (
    'DRAFT',
    'VALIDATED',
    'ANALYZED',
    'ARCHIVED'
);

CREATE TYPE measure_type AS ENUM (
    'ENTROPY',
    'CONDITIONAL_ENTROPY',
    'JOINT_ENTROPY',
    'MUTUAL_INFORMATION',
    'CONDITIONAL_MUTUAL_INFORMATION',
    'INFORMATION_GAIN',
    'NORMALIZED_MUTUAL_INFORMATION'
);

-- ------------------------------------------------------------
-- 2. DATASET
-- ------------------------------------------------------------

CREATE TABLE datasets (
    dataset_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dataset_name VARCHAR(150) NOT NULL UNIQUE,

    description TEXT,

    target_name VARCHAR(100) NOT NULL,

    observation_count INTEGER NOT NULL DEFAULT 0,

    status dataset_status NOT NULL DEFAULT 'DRAFT',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_dataset_name
        CHECK (length(trim(dataset_name)) > 0),

    CONSTRAINT valid_target_name
        CHECK (length(trim(target_name)) > 0),

    CONSTRAINT valid_observation_count
        CHECK (observation_count >= 0)
);

-- ------------------------------------------------------------
-- 3. FEATURES
-- ------------------------------------------------------------

CREATE TABLE features (
    feature_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dataset_id BIGINT NOT NULL
        REFERENCES datasets(dataset_id)
        ON DELETE CASCADE,

    feature_name VARCHAR(100) NOT NULL,

    feature_description TEXT,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_dataset_feature
        UNIQUE (dataset_id, feature_name),

    CONSTRAINT valid_feature_name
        CHECK (length(trim(feature_name)) > 0)
);

-- ------------------------------------------------------------
-- 4. OBSERVATIONS
--
-- Each row represents one observation for one feature.
-- observation_id connects feature values belonging to
-- the same original sample.
--
-- Target values are stored separately from feature values
-- to preserve the distinction between predictors and labels.
-- ------------------------------------------------------------

CREATE TABLE observations (
    observation_id BIGINT NOT NULL,

    dataset_id BIGINT NOT NULL
        REFERENCES datasets(dataset_id)
        ON DELETE CASCADE,

    target_value VARCHAR(200) NOT NULL,

    PRIMARY KEY (dataset_id, observation_id),

    CONSTRAINT valid_target_value
        CHECK (length(target_value) > 0)
);

CREATE TABLE feature_observations (
    dataset_id BIGINT NOT NULL,

    observation_id BIGINT NOT NULL,

    feature_id BIGINT NOT NULL
        REFERENCES features(feature_id)
        ON DELETE CASCADE,

    feature_value VARCHAR(200) NOT NULL,

    PRIMARY KEY (
        dataset_id,
        observation_id,
        feature_id
    ),

    FOREIGN KEY (
        dataset_id,
        observation_id
    )
    REFERENCES observations (
        dataset_id,
        observation_id
    )
    ON DELETE CASCADE,

    CONSTRAINT valid_feature_value
        CHECK (length(feature_value) > 0)
);

-- ------------------------------------------------------------
-- 5. INFORMATION MEASUREMENT RESULTS
-- ------------------------------------------------------------

CREATE TABLE analysis_results (
    result_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dataset_id BIGINT NOT NULL
        REFERENCES datasets(dataset_id)
        ON DELETE CASCADE,

    feature_id BIGINT
        REFERENCES features(feature_id)
        ON DELETE CASCADE,

    measure measure_type NOT NULL,

    value DOUBLE PRECISION NOT NULL,

    unit VARCHAR(30) NOT NULL DEFAULT 'bits',

    analyzed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_measurement
        CHECK (
            value >= -0.000000000001
            AND value < 'Infinity'::DOUBLE PRECISION
            AND value > '-Infinity'::DOUBLE PRECISION
        )
);

-- ------------------------------------------------------------
-- 6. INDEXES
-- ------------------------------------------------------------

CREATE INDEX idx_features_dataset
    ON features(dataset_id);

CREATE INDEX idx_observations_target
    ON observations(dataset_id, target_value);

CREATE INDEX idx_feature_values
    ON feature_observations(
        dataset_id,
        feature_id,
        feature_value
    );

CREATE INDEX idx_analysis_results
    ON analysis_results(
        dataset_id,
        measure,
        analyzed_at DESC
    );

CREATE INDEX idx_active_features
    ON features(dataset_id, feature_name)
    WHERE is_active = TRUE;

-- ------------------------------------------------------------
-- 7. DISTRIBUTION FUNCTION
--
-- Calculates Shannon entropy using grouped frequencies.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_entropy(
    p_values TEXT[]
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    total_count DOUBLE PRECISION;
    result_value DOUBLE PRECISION;
BEGIN
    IF p_values IS NULL OR cardinality(p_values) = 0 THEN
        RAISE EXCEPTION 'Entropy input cannot be empty.';
    END IF;

    IF array_position(p_values, NULL) IS NOT NULL THEN
        RAISE EXCEPTION 'Null observations are not supported.';
    END IF;

    SELECT
        -SUM(
            frequency * LN(frequency)
        ) / LN(2.0)
    INTO result_value
    FROM (
        SELECT
            COUNT(*)::DOUBLE PRECISION /
            cardinality(p_values)::DOUBLE PRECISION AS frequency
        FROM unnest(p_values) AS item
        GROUP BY item
    ) probabilities;

    RETURN GREATEST(COALESCE(result_value, 0), 0);
END;
$$;

-- ------------------------------------------------------------
-- 8. CONDITIONAL ENTROPY
--
-- H(Y|X) = SUM_x P(x) H(Y|X=x)
--
-- Both arrays must have identical lengths.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_conditional_entropy(
    p_target TEXT[],
    p_condition TEXT[]
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    result_value DOUBLE PRECISION;
BEGIN
    IF
        p_target IS NULL
        OR p_condition IS NULL
        OR cardinality(p_target) = 0
        OR cardinality(p_target) <> cardinality(p_condition)
    THEN
        RAISE EXCEPTION
            'Conditional entropy requires equally sized non-empty arrays.';
    END IF;

    IF
        array_position(p_target, NULL) IS NOT NULL
        OR array_position(p_condition, NULL) IS NOT NULL
    THEN
        RAISE EXCEPTION 'Null observations are not supported.';
    END IF;

    WITH grouped AS (
        SELECT
            x,
            COUNT(*)::DOUBLE PRECISION AS group_size,
            ARRAY_AGG(y) AS target_values
        FROM unnest(p_target, p_condition) AS source(y, x)
        GROUP BY x
    )
    SELECT
        SUM(
            group_size / cardinality(p_target)::DOUBLE PRECISION
            * calculate_entropy(target_values)
        )
    INTO result_value
    FROM grouped;

    RETURN GREATEST(COALESCE(result_value, 0), 0);
END;
$$;

-- ------------------------------------------------------------
-- 9. MUTUAL INFORMATION
--
-- I(X;Y) = H(Y) - H(Y|X)
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_mutual_information(
    p_x TEXT[],
    p_y TEXT[]
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    IF
        p_x IS NULL
        OR p_y IS NULL
        OR cardinality(p_x) <> cardinality(p_y)
        OR cardinality(p_x) = 0
    THEN
        RAISE EXCEPTION
            'Mutual information requires equally sized non-empty arrays.';
    END IF;

    RETURN GREATEST(
        0,
        calculate_entropy(p_y)
        - calculate_conditional_entropy(p_y, p_x)
    );
END;
$$;

-- ------------------------------------------------------------
-- 10. INFORMATION GAIN
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_information_gain(
    p_target TEXT[],
    p_feature TEXT[]
)
RETURNS DOUBLE PRECISION
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT calculate_mutual_information(
        p_feature,
        p_target
    );
$$;

-- ------------------------------------------------------------
-- 11. JOINT ENTROPY
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_joint_entropy(
    p_x TEXT[],
    p_y TEXT[]
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    result_value DOUBLE PRECISION;
BEGIN
    IF
        p_x IS NULL
        OR p_y IS NULL
        OR cardinality(p_x) = 0
        OR cardinality(p_x) <> cardinality(p_y)
    THEN
        RAISE EXCEPTION 'Invalid joint entropy inputs.';
    END IF;

    WITH joint_values AS (
        SELECT
            x,
            y,
            COUNT(*)::DOUBLE PRECISION /
            cardinality(p_x)::DOUBLE PRECISION AS probability
        FROM unnest(p_x, p_y) AS source(x, y)
        GROUP BY x, y
    )
    SELECT
        -SUM(probability * LN(probability)) / LN(2.0)
    INTO result_value
    FROM joint_values;

    RETURN GREATEST(COALESCE(result_value, 0), 0);
END;
$$;

-- ------------------------------------------------------------
-- 12. CONDITIONAL MUTUAL INFORMATION
--
-- I(X;Y|Z) = H(Y|Z) - H(Y|X,Z)
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_conditional_mutual_information(
    p_x TEXT[],
    p_y TEXT[],
    p_z TEXT[]
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    first_term DOUBLE PRECISION;
    second_term DOUBLE PRECISION;
    total_count INTEGER;
    y_values TEXT[];
    xz_values TEXT[];
BEGIN
    IF
        p_x IS NULL
        OR p_y IS NULL
        OR p_z IS NULL
        OR cardinality(p_x) = 0
        OR cardinality(p_x) <> cardinality(p_y)
        OR cardinality(p_x) <> cardinality(p_z)
    THEN
        RAISE EXCEPTION
            'Conditional mutual information requires three equally sized arrays.';
    END IF;

    IF
        array_position(p_x, NULL) IS NOT NULL
        OR array_position(p_y, NULL) IS NOT NULL
        OR array_position(p_z, NULL) IS NOT NULL
    THEN
        RAISE EXCEPTION 'Null observations are not supported.';
    END IF;

    total_count := cardinality(p_x);

    first_term :=
        calculate_conditional_entropy(p_y, p_z);

    -- Length prefixes make compound categorical keys unambiguous.
    SELECT
        ARRAY_AGG(y),
        ARRAY_AGG(
            LENGTH(x)::TEXT || ':' || x ||
            LENGTH(z)::TEXT || ':' || z
        )
    INTO y_values, xz_values
    FROM unnest(p_x, p_y, p_z) AS source(x, y, z);

    second_term :=
        calculate_conditional_entropy(
            y_values,
            xz_values
        );

    RETURN GREATEST(0, first_term - second_term);
END;
$$;

-- ------------------------------------------------------------
-- 13. NORMALIZED MUTUAL INFORMATION
--
-- NMI = 2 * I(X;Y) / (H(X)+H(Y))
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_normalized_mi(
    p_x TEXT[],
    p_y TEXT[]
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    denominator DOUBLE PRECISION;
BEGIN
    denominator :=
        calculate_entropy(p_x) +
        calculate_entropy(p_y);

    IF denominator <= 0.000000000001 THEN
        RETURN 1.0;
    END IF;

    RETURN LEAST(
        1.0,
        2.0 * calculate_mutual_information(p_x, p_y)
        / denominator
    );
END;
$$;

-- ------------------------------------------------------------
-- 14. OBSERVATION COUNT MAINTENANCE
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION refresh_dataset_count()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    affected_dataset BIGINT;
BEGIN
    affected_dataset :=
        COALESCE(NEW.dataset_id, OLD.dataset_id);

    UPDATE datasets
    SET
        observation_count = (
            SELECT COUNT(*)::INTEGER
            FROM observations
            WHERE dataset_id = affected_dataset
        ),
        updated_at = CURRENT_TIMESTAMP
    WHERE dataset_id = affected_dataset;

    RETURN COALESCE(NEW, OLD);
END;
$$;

CREATE TRIGGER trg_refresh_dataset_count
AFTER INSERT OR UPDATE OR DELETE
ON observations
FOR EACH ROW
EXECUTE FUNCTION refresh_dataset_count();

-- ------------------------------------------------------------
-- 15. DATASET INTEGRITY VALIDATION
--
-- Every observation must contain exactly one value for
-- every active feature before the dataset is validated.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_dataset(
    p_dataset_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    observation_total BIGINT;
    active_feature_total BIGINT;
    invalid_observation_total BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO observation_total
    FROM observations
    WHERE dataset_id = p_dataset_id;

    SELECT COUNT(*)
    INTO active_feature_total
    FROM features
    WHERE dataset_id = p_dataset_id
      AND is_active = TRUE;

    IF observation_total = 0 THEN
        RAISE EXCEPTION
            'Dataset % contains no observations.',
            p_dataset_id;
    END IF;

    IF active_feature_total = 0 THEN
        RAISE EXCEPTION
            'Dataset % has no active features.',
            p_dataset_id;
    END IF;

    SELECT COUNT(*)
    INTO invalid_observation_total
    FROM observations o
    WHERE o.dataset_id = p_dataset_id
      AND (
          SELECT COUNT(*)
          FROM feature_observations fo
          JOIN features f
            ON f.feature_id = fo.feature_id
          WHERE fo.dataset_id = o.dataset_id
            AND fo.observation_id = o.observation_id
            AND f.is_active = TRUE
      ) <> active_feature_total;

    IF invalid_observation_total > 0 THEN
        RAISE EXCEPTION
            'Dataset % contains % incomplete observations.',
            p_dataset_id,
            invalid_observation_total;
    END IF;

    UPDATE datasets
    SET
        status = 'VALIDATED',
        updated_at = CURRENT_TIMESTAMP
    WHERE dataset_id = p_dataset_id
      AND status <> 'ARCHIVED';

    RETURN TRUE;
END;
$$;

-- ------------------------------------------------------------
-- 16. FEATURE EVALUATION
--
-- Uses actual observation records rather than independently
-- aggregated feature distributions.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION evaluate_feature(
    p_dataset_id BIGINT,
    p_feature_id BIGINT
)
RETURNS TABLE (
    feature_name TEXT,
    target_entropy DOUBLE PRECISION,
    conditional_entropy DOUBLE PRECISION,
    mutual_information DOUBLE PRECISION,
    information_gain DOUBLE PRECISION,
    normalized_mutual_information DOUBLE PRECISION
)
LANGUAGE plpgsql
AS $$
DECLARE
    target_values TEXT[];
    feature_values TEXT[];
    feature_label TEXT;
    h_target DOUBLE PRECISION;
    h_conditional DOUBLE PRECISION;
    mi DOUBLE PRECISION;
BEGIN
    IF NOT validate_dataset(p_dataset_id) THEN
        RAISE EXCEPTION 'Dataset validation failed.';
    END IF;

    SELECT f.feature_name
    INTO feature_label
    FROM features f
    WHERE f.feature_id = p_feature_id
      AND f.dataset_id = p_dataset_id
      AND f.is_active = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Feature % is not active in dataset %.',
            p_feature_id,
            p_dataset_id;
    END IF;

    SELECT
        ARRAY_AGG(o.target_value ORDER BY o.observation_id),
        ARRAY_AGG(fo.feature_value ORDER BY o.observation_id)
    INTO
        target_values,
        feature_values
    FROM observations o
    JOIN feature_observations fo
      ON fo.dataset_id = o.dataset_id
     AND fo.observation_id = o.observation_id
    WHERE o.dataset_id = p_dataset_id
      AND fo.feature_id = p_feature_id;

    h_target := calculate_entropy(target_values);

    h_conditional :=
        calculate_conditional_entropy(
            target_values,
            feature_values
        );

    mi := calculate_mutual_information(
        feature_values,
        target_values
    );

    RETURN QUERY
    SELECT
        feature_label,
        h_target,
        h_conditional,
        mi,
        GREATEST(0, h_target - h_conditional),
        calculate_normalized_mi(
            feature_values,
            target_values
        );
END;
$$;

-- ------------------------------------------------------------
-- 17. FEATURE RANKING VIEW
--
-- Each feature is evaluated independently against the target.
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW feature_information_report AS
SELECT
    d.dataset_id,
    d.dataset_name,
    f.feature_id,
    f.feature_name,
    r.target_entropy,
    r.conditional_entropy,
    r.mutual_information,
    r.information_gain,
    r.normalized_mutual_information,
    DENSE_RANK() OVER (
        PARTITION BY d.dataset_id
        ORDER BY r.information_gain DESC
    ) AS feature_rank
FROM datasets d
JOIN features f
  ON f.dataset_id = d.dataset_id
 AND f.is_active = TRUE
CROSS JOIN LATERAL evaluate_feature(
    d.dataset_id,
    f.feature_id
) r
WHERE d.status <> 'ARCHIVED';

-- ------------------------------------------------------------
-- 18. STORE FEATURE RESULTS
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE store_feature_analysis(
    p_dataset_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    feature_record RECORD;
BEGIN
    PERFORM validate_dataset(p_dataset_id);

    DELETE FROM analysis_results
    WHERE dataset_id = p_dataset_id
      AND measure IN (
          'ENTROPY',
          'CONDITIONAL_ENTROPY',
          'MUTUAL_INFORMATION',
          'INFORMATION_GAIN',
          'NORMALIZED_MUTUAL_INFORMATION'
      );

    FOR feature_record IN
        SELECT *
        FROM feature_information_report
        WHERE dataset_id = p_dataset_id
    LOOP
        INSERT INTO analysis_results (
            dataset_id,
            feature_id,
            measure,
            value
        )
        VALUES
        (
            p_dataset_id,
            feature_record.feature_id,
            'ENTROPY',
            feature_record.target_entropy
        ),
        (
            p_dataset_id,
            feature_record.feature_id,
            'CONDITIONAL_ENTROPY',
            feature_record.conditional_entropy
        ),
        (
            p_dataset_id,
            feature_record.feature_id,
            'MUTUAL_INFORMATION',
            feature_record.mutual_information
        ),
        (
            p_dataset_id,
            feature_record.feature_id,
            'INFORMATION_GAIN',
            feature_record.information_gain
        ),
        (
            p_dataset_id,
            feature_record.feature_id,
            'NORMALIZED_MUTUAL_INFORMATION',
            feature_record.normalized_mutual_information
        );
    END LOOP;

    UPDATE datasets
    SET
        status = 'ANALYZED',
        updated_at = CURRENT_TIMESTAMP
    WHERE dataset_id = p_dataset_id;
END;
$$;

-- ------------------------------------------------------------
-- 19. SAMPLE DATASET
-- ------------------------------------------------------------

INSERT INTO datasets (
    dataset_name,
    description,
    target_name
)
VALUES (
    'Weather Classification',
    'Categorical weather observations for information gain analysis.',
    'Play'
);

INSERT INTO features (
    dataset_id,
    feature_name,
    feature_description
)
SELECT
    dataset_id,
    feature_name,
    description
FROM datasets
CROSS JOIN (
    VALUES
        ('Outlook', 'Weather outlook category'),
        ('Temperature', 'Temperature category'),
        ('Humidity', 'Humidity category'),
        ('Wind', 'Wind condition')
) AS feature_data(feature_name, description)
WHERE dataset_name = 'Weather Classification';

-- ------------------------------------------------------------
-- 20. OBSERVATIONS
-- ------------------------------------------------------------

INSERT INTO observations (
    observation_id,
    dataset_id,
    target_value
)
SELECT
    source.observation_id,
    d.dataset_id,
    source.target_value
FROM datasets d
CROSS JOIN (
    VALUES
        (1, 'No'),
        (2, 'No'),
        (3, 'Yes'),
        (4, 'Yes'),
        (5, 'Yes'),
        (6, 'No'),
        (7, 'Yes'),
        (8, 'No'),
        (9, 'Yes'),
        (10, 'Yes'),
        (11, 'Yes'),
        (12, 'Yes'),
        (13, 'Yes'),
        (14, 'No')
) AS source(observation_id, target_value)
WHERE d.dataset_name = 'Weather Classification';

-- ------------------------------------------------------------
-- 21. FEATURE VALUES
-- ------------------------------------------------------------

INSERT INTO feature_observations (
    dataset_id,
    observation_id,
    feature_id,
    feature_value
)
SELECT
    d.dataset_id,
    source.observation_id,
    f.feature_id,
    source.feature_value
FROM datasets d
JOIN (
    VALUES
        (1, 'Outlook', 'Sunny'),
        (2, 'Outlook', 'Sunny'),
        (3, 'Outlook', 'Overcast'),
        (4, 'Outlook', 'Rain'),
        (5, 'Outlook', 'Rain'),
        (6, 'Outlook', 'Rain'),
        (7, 'Outlook', 'Overcast'),
        (8, 'Outlook', 'Sunny'),
        (9, 'Outlook', 'Sunny'),
        (10, 'Outlook', 'Rain'),
        (11, 'Outlook', 'Sunny'),
        (12, 'Outlook', 'Overcast'),
        (13, 'Outlook', 'Overcast'),
        (14, 'Outlook', 'Rain'),

        (1, 'Temperature', 'Hot'),
        (2, 'Temperature', 'Hot'),
        (3, 'Temperature', 'Hot'),
        (4, 'Temperature', 'Mild'),
        (5, 'Temperature', 'Cool'),
        (6, 'Temperature', 'Cool'),
        (7, 'Temperature', 'Cool'),
        (8, 'Temperature', 'Mild'),
        (9, 'Temperature', 'Cool'),
        (10, 'Temperature', 'Mild'),
        (11, 'Temperature', 'Mild'),
        (12, 'Temperature', 'Mild'),
        (13, 'Temperature', 'Hot'),
        (14, 'Temperature', 'Mild'),

        (1, 'Humidity', 'High'),
        (2, 'Humidity', 'High'),
        (3, 'Humidity', 'High'),
        (4, 'Humidity', 'High'),
        (5, 'Humidity', 'Normal'),
        (6, 'Humidity', 'Normal'),
        (7, 'Humidity', 'Normal'),
        (8, 'Humidity', 'High'),
        (9, 'Humidity', 'Normal'),
        (10, 'Humidity', 'Normal'),
        (11, 'Humidity', 'Normal'),
        (12, 'Humidity', 'High'),
        (13, 'Humidity', 'Normal'),
        (14, 'Humidity', 'High'),

        (1, 'Wind', 'Weak'),
        (2, 'Wind', 'Strong'),
        (3, 'Wind', 'Weak'),
        (4, 'Wind', 'Weak'),
        (5, 'Wind', 'Weak'),
        (6, 'Wind', 'Strong'),
        (7, 'Wind', 'Strong'),
        (8, 'Wind', 'Weak'),
        (9, 'Wind', 'Weak'),
        (10, 'Wind', 'Weak'),
        (11, 'Wind', 'Strong'),
        (12, 'Wind', 'Strong'),
        (13, 'Wind', 'Weak'),
        (14, 'Wind', 'Strong')
) AS source(observation_id, feature_name, feature_value)
  ON TRUE
JOIN features f
  ON f.dataset_id = d.dataset_id
 AND f.feature_name = source.feature_name
WHERE d.dataset_name = 'Weather Classification';

-- ------------------------------------------------------------
-- 22. MATHEMATICAL VALIDATION QUERIES
-- ------------------------------------------------------------

-- Entropy of a fair binary distribution = 1 bit.
SELECT calculate_entropy(
    ARRAY['H', 'T', 'H', 'T']::TEXT[]
) AS fair_coin_entropy;

-- Entropy of a constant distribution = 0 bits.
SELECT calculate_entropy(
    ARRAY['A', 'A', 'A', 'A']::TEXT[]
) AS constant_entropy;

-- Perfect dependence: MI = 1 bit.
SELECT calculate_mutual_information(
    ARRAY['0', '0', '1', '1']::TEXT[],
    ARRAY['0', '0', '1', '1']::TEXT[]
) AS perfect_mutual_information;

-- Independence: MI = 0 bits.
SELECT calculate_mutual_information(
    ARRAY['0', '0', '1', '1']::TEXT[],
    ARRAY['0', '1', '0', '1']::TEXT[]
) AS independent_mutual_information;

-- Conditional entropy of a perfectly predictable target = 0.
SELECT calculate_conditional_entropy(
    ARRAY['0', '0', '1', '1']::TEXT[],
    ARRAY['0', '0', '1', '1']::TEXT[]
) AS predictable_conditional_entropy;

-- Joint entropy of identical fair binary variables = 1 bit.
SELECT calculate_joint_entropy(
    ARRAY['0', '0', '1', '1']::TEXT[],
    ARRAY['0', '0', '1', '1']::TEXT[]
) AS joint_entropy;

-- Conditional mutual information.
SELECT calculate_conditional_mutual_information(
    ARRAY['A', 'A', 'B', 'B']::TEXT[],
    ARRAY['X', 'Y', 'X', 'Y']::TEXT[],
    ARRAY['Z', 'Z', 'W', 'W']::TEXT[]
) AS conditional_mi;

-- ------------------------------------------------------------
-- 23. FEATURE EVALUATION AND RANKING
-- ------------------------------------------------------------

SELECT
    dataset_name,
    feature_name,
    ROUND(target_entropy::NUMERIC, 5) AS target_entropy,
    ROUND(conditional_entropy::NUMERIC, 5)
        AS conditional_entropy,
    ROUND(mutual_information::NUMERIC, 5)
        AS mutual_information,
    ROUND(information_gain::NUMERIC, 5)
        AS information_gain,
    ROUND(normalized_mutual_information::NUMERIC, 5)
        AS normalized_mutual_information,
    feature_rank
FROM feature_information_report
WHERE dataset_name = 'Weather Classification'
ORDER BY feature_rank, feature_name;

-- ------------------------------------------------------------
-- 24. FEATURE SELECTION
--
-- Features with at least 0.05 bits of information gain.
-- ------------------------------------------------------------

SELECT
    feature_name,
    information_gain,
    feature_rank
FROM feature_information_report
WHERE dataset_name = 'Weather Classification'
  AND information_gain >= 0.05
ORDER BY information_gain DESC;

-- ------------------------------------------------------------
-- 25. DISTRIBUTION REPORT
-- ------------------------------------------------------------

SELECT
    f.feature_name,
    fo.feature_value,
    COUNT(*) AS frequency,
    ROUND(
        COUNT(*)::NUMERIC /
        SUM(COUNT(*)) OVER (
            PARTITION BY f.feature_id
        ),
        5
    ) AS probability
FROM feature_observations fo
JOIN features f
  ON f.feature_id = fo.feature_id
WHERE f.dataset_id = (
    SELECT dataset_id
    FROM datasets
    WHERE dataset_name = 'Weather Classification'
)
GROUP BY
    f.feature_id,
    f.feature_name,
    fo.feature_value
ORDER BY
    f.feature_name,
    frequency DESC;

-- ------------------------------------------------------------
-- 26. AGGREGATED RESULT STORAGE
-- ------------------------------------------------------------

CALL store_feature_analysis(
    (
        SELECT dataset_id
        FROM datasets
        WHERE dataset_name = 'Weather Classification'
    )
);

-- ------------------------------------------------------------
-- 27. STORED ANALYSIS REPORT
-- ------------------------------------------------------------

SELECT
    d.dataset_name,
    f.feature_name,
    ar.measure,
    ROUND(ar.value::NUMERIC, 5) AS measurement,
    ar.unit,
    ar.analyzed_at
FROM analysis_results ar
JOIN datasets d
  ON d.dataset_id = ar.dataset_id
LEFT JOIN features f
  ON f.feature_id = ar.feature_id
WHERE d.dataset_name = 'Weather Classification'
ORDER BY
    f.feature_name,
    ar.measure;

-- ------------------------------------------------------------
-- 28. DATA QUALITY REPORT
-- ------------------------------------------------------------

SELECT
    d.dataset_name,
    d.observation_count,
    COUNT(DISTINCT f.feature_id)
        FILTER (WHERE f.is_active) AS active_features,
    COUNT(fo.feature_value) AS recorded_feature_values,
    d.status
FROM datasets d
LEFT JOIN features f
  ON f.dataset_id = d.dataset_id
LEFT JOIN feature_observations fo
  ON fo.dataset_id = d.dataset_id
 AND fo.feature_id = f.feature_id
GROUP BY
    d.dataset_id,
    d.dataset_name,
    d.observation_count,
    d.status;

-- ------------------------------------------------------------
-- 29. TRANSACTIONAL INTEGRITY
--
-- All schema creation, sample insertion, validation,
-- analysis, and reporting setup are committed together.
-- Any SQL error before COMMIT leaves the transaction
-- available for rollback by the database client.
-- ------------------------------------------------------------

COMMIT;
