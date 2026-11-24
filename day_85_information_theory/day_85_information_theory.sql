-- ================================================================
-- INFORMATION THEORY DATABASE
-- PostgreSQL 15+
--
-- Models:
--   Probability experiments
--   Outcomes and observations
--   Empirical probability distributions
--   Self-information
--   Shannon entropy
--   Joint and conditional entropy
--   Mutual information
--   Cross-entropy
--   KL divergence
--   Entropy monitoring and reporting
--
-- Information units: bits
-- ================================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS information_theory;

SET search_path TO information_theory, public;

-- ------------------------------------------------
-- 1. DOMAIN TYPES
-- ------------------------------------------------

DO $$
BEGIN
    CREATE TYPE experiment_status AS ENUM (
        'draft',
        'collecting',
        'completed',
        'archived'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END
$$;

DO $$
BEGIN
    CREATE TYPE metric_type AS ENUM (
        'self_information',
        'entropy',
        'conditional_entropy',
        'mutual_information',
        'cross_entropy',
        'kl_divergence'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END
$$;

-- ------------------------------------------------
-- 2. EXPERIMENTS
-- ------------------------------------------------

CREATE TABLE IF NOT EXISTS experiments (
    experiment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    experiment_name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    status experiment_status NOT NULL DEFAULT 'draft',
    logarithm_base NUMERIC(12, 6) NOT NULL DEFAULT 2.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_logarithm_base
        CHECK (
            logarithm_base > 0
            AND logarithm_base <> 1
        )
);

-- ------------------------------------------------
-- 3. OUTCOME VOCABULARY
-- ------------------------------------------------

CREATE TABLE IF NOT EXISTS outcomes (
    outcome_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id)
        ON DELETE CASCADE,
    outcome_code VARCHAR(100) NOT NULL,
    outcome_description TEXT NOT NULL DEFAULT '',

    UNIQUE (experiment_id, outcome_code),
    UNIQUE (experiment_id, outcome_id)
);

-- ------------------------------------------------
-- 4. EMPIRICAL OBSERVATIONS
-- ------------------------------------------------

CREATE TABLE IF NOT EXISTS observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id)
        ON DELETE CASCADE,
    outcome_id BIGINT NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_reference VARCHAR(150),

    FOREIGN KEY (experiment_id, outcome_id)
        REFERENCES outcomes(experiment_id, outcome_id)
        ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_observations_experiment_time
    ON observations(experiment_id, observed_at DESC);

CREATE INDEX IF NOT EXISTS idx_observations_outcome
    ON observations(experiment_id, outcome_id);

-- ------------------------------------------------
-- 5. PROBABILITY DISTRIBUTIONS
-- ------------------------------------------------

CREATE TABLE IF NOT EXISTS probability_distributions (
    distribution_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id)
        ON DELETE CASCADE,
    distribution_name VARCHAR(150) NOT NULL,
    distribution_kind VARCHAR(20) NOT NULL
        CHECK (distribution_kind IN ('actual', 'predicted', 'empirical')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (experiment_id, distribution_name),
    UNIQUE (experiment_id, distribution_id)
);

CREATE TABLE IF NOT EXISTS distribution_probabilities (
    distribution_id BIGINT NOT NULL
        REFERENCES probability_distributions(distribution_id)
        ON DELETE CASCADE,
    outcome_id BIGINT NOT NULL
        REFERENCES outcomes(outcome_id)
        ON DELETE RESTRICT,
    probability NUMERIC(20, 15) NOT NULL,

    PRIMARY KEY (distribution_id, outcome_id),

    CONSTRAINT probability_range
        CHECK (probability >= 0 AND probability <= 1)
);

CREATE INDEX IF NOT EXISTS idx_distribution_probability
    ON distribution_probabilities(distribution_id, probability DESC);

-- ------------------------------------------------
-- 6. JOINT DISTRIBUTIONS
-- ------------------------------------------------

CREATE TABLE IF NOT EXISTS joint_distributions (
    joint_distribution_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id)
        ON DELETE CASCADE,
    joint_name VARCHAR(150) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS joint_probabilities (
    joint_distribution_id BIGINT NOT NULL
        REFERENCES joint_distributions(joint_distribution_id)
        ON DELETE CASCADE,
    x_value VARCHAR(100) NOT NULL,
    y_value VARCHAR(100) NOT NULL,
    probability NUMERIC(20, 15) NOT NULL
        CHECK (probability >= 0 AND probability <= 1),

    PRIMARY KEY (joint_distribution_id, x_value, y_value)
);

-- ------------------------------------------------
-- 7. INFORMATION METRICS
-- ------------------------------------------------

CREATE TABLE IF NOT EXISTS information_metrics (
    metric_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id)
        ON DELETE CASCADE,
    metric_name metric_type NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(20) NOT NULL DEFAULT 'bits',
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (
        metric_value >= 0
        OR metric_value = 'Infinity'::DOUBLE PRECISION
    )
);

CREATE INDEX IF NOT EXISTS idx_metrics_experiment_type
    ON information_metrics(experiment_id, metric_name, calculated_at DESC);

-- ------------------------------------------------
-- 8. DISTRIBUTION VALIDATION
-- ------------------------------------------------

CREATE OR REPLACE FUNCTION validate_distribution(
    p_distribution_id BIGINT,
    p_tolerance DOUBLE PRECISION DEFAULT 0.000000001
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_total NUMERIC;
    v_count BIGINT;
BEGIN
    IF p_tolerance <= 0 OR NOT isfinite(p_tolerance) THEN
        RAISE EXCEPTION 'Tolerance must be positive and finite';
    END IF;

    SELECT
        COALESCE(SUM(probability), 0),
        COUNT(*)
    INTO v_total, v_count
    FROM distribution_probabilities
    WHERE distribution_id = p_distribution_id;

    IF v_count = 0 THEN
        RETURN FALSE;
    END IF;

    RETURN ABS(v_total - 1.0) <= p_tolerance;
END;
$$;

-- ------------------------------------------------
-- 9. SELF-INFORMATION
-- ------------------------------------------------

CREATE OR REPLACE FUNCTION self_information(
    p_probability DOUBLE PRECISION,
    p_base DOUBLE PRECISION DEFAULT 2.0
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF p_probability < 0 OR p_probability > 1 THEN
        RAISE EXCEPTION 'Probability must be between 0 and 1';
    END IF;

    IF p_base <= 0 OR p_base = 1
       OR NOT isfinite(p_base) THEN
        RAISE EXCEPTION 'Invalid logarithm base';
    END IF;

    IF p_probability = 0 THEN
        RETURN 'Infinity'::DOUBLE PRECISION;
    END IF;

    RETURN -LN(p_probability) / LN(p_base);
END;
$$;

-- ------------------------------------------------
-- 10. SHANNON ENTROPY
-- ------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_entropy(
    p_distribution_id BIGINT,
    p_base DOUBLE PRECISION DEFAULT 2.0
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_total NUMERIC;
    v_count BIGINT;
    v_result DOUBLE PRECISION;
BEGIN
    IF p_base <= 0 OR p_base = 1
       OR NOT isfinite(p_base) THEN
        RAISE EXCEPTION 'Invalid logarithm base';
    END IF;

    SELECT SUM(probability), COUNT(*)
    INTO v_total, v_count
    FROM distribution_probabilities
    WHERE distribution_id = p_distribution_id;

    IF v_count = 0 OR ABS(v_total - 1.0) > 0.000000001 THEN
        RAISE EXCEPTION 'Invalid probability distribution';
    END IF;

    SELECT COALESCE(
        SUM(
            CASE
                WHEN probability > 0 THEN
                    -probability *
                    LN(probability) / LN(p_base)
                ELSE 0
            END
        ),
        0
    )
    INTO v_result
    FROM distribution_probabilities
    WHERE distribution_id = p_distribution_id;

    RETURN v_result;
END;
$$;

-- ------------------------------------------------
-- 11. MAXIMUM ENTROPY
-- ------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_maximum_entropy(
    p_outcome_count BIGINT,
    p_base DOUBLE PRECISION DEFAULT 2.0
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF p_outcome_count < 1 THEN
        RAISE EXCEPTION 'Outcome count must be positive';
    END IF;

    IF p_base <= 0 OR p_base = 1
       OR NOT isfinite(p_base) THEN
        RAISE EXCEPTION 'Invalid logarithm base';
    END IF;

    RETURN LN(p_outcome_count::DOUBLE PRECISION) / LN(p_base);
END;
$$;

-- ------------------------------------------------
-- 12. EMPIRICAL PROBABILITY ESTIMATION
-- ------------------------------------------------

CREATE OR REPLACE PROCEDURE build_empirical_distribution(
    p_experiment_id BIGINT,
    p_distribution_name VARCHAR(150)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_distribution_id BIGINT;
    v_total BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_total
    FROM observations
    WHERE experiment_id = p_experiment_id;

    IF v_total = 0 THEN
        RAISE EXCEPTION 'No observations available';
    END IF;

    INSERT INTO probability_distributions (
        experiment_id,
        distribution_name,
        distribution_kind
    )
    VALUES (
        p_experiment_id,
        p_distribution_name,
        'empirical'
    )
    RETURNING distribution_id INTO v_distribution_id;

    INSERT INTO distribution_probabilities (
        distribution_id,
        outcome_id,
        probability
    )
    SELECT
        v_distribution_id,
        outcome_id,
        COUNT(*)::NUMERIC / v_total
    FROM observations
    WHERE experiment_id = p_experiment_id
    GROUP BY outcome_id;

    IF NOT validate_distribution(v_distribution_id) THEN
        RAISE EXCEPTION 'Generated empirical distribution is invalid';
    END IF;
END;
$$;

-- ------------------------------------------------
-- 13. DISTRIBUTION COMPARISON
-- ------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_cross_entropy(
    p_actual_id BIGINT,
    p_predicted_id BIGINT
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_result DOUBLE PRECISION;
    v_actual_count BIGINT;
    v_predicted_count BIGINT;
    v_mismatch BIGINT;
BEGIN
    IF NOT validate_distribution(p_actual_id)
       OR NOT validate_distribution(p_predicted_id) THEN
        RAISE EXCEPTION 'Both distributions must be valid';
    END IF;

    SELECT COUNT(*) INTO v_actual_count
    FROM distribution_probabilities
    WHERE distribution_id = p_actual_id;

    SELECT COUNT(*) INTO v_predicted_count
    FROM distribution_probabilities
    WHERE distribution_id = p_predicted_id;

    SELECT COUNT(*)
    INTO v_mismatch
    FROM distribution_probabilities a
    FULL JOIN distribution_probabilities b
        ON a.outcome_id = b.outcome_id
        AND b.distribution_id = p_predicted_id
    WHERE a.distribution_id = p_actual_id
      AND (
          a.outcome_id IS NULL
          OR b.outcome_id IS NULL
      );

    IF v_actual_count <> v_predicted_count OR v_mismatch > 0 THEN
        RAISE EXCEPTION 'Distribution outcome sets do not match';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM distribution_probabilities a
        JOIN distribution_probabilities b
          ON b.outcome_id = a.outcome_id
        WHERE a.distribution_id = p_actual_id
          AND b.distribution_id = p_predicted_id
          AND a.probability > 0
          AND b.probability = 0
    ) THEN
        RETURN 'Infinity'::DOUBLE PRECISION;
    END IF;

    SELECT COALESCE(
        -SUM(
            CASE
                WHEN a.probability > 0 THEN
                    a.probability * LN(b.probability) / LN(2.0)
                ELSE 0
            END
        ),
        0
    )
    INTO v_result
    FROM distribution_probabilities a
    JOIN distribution_probabilities b
      ON b.outcome_id = a.outcome_id
    WHERE a.distribution_id = p_actual_id
      AND b.distribution_id = p_predicted_id;

    RETURN v_result;
END;
$$;

CREATE OR REPLACE FUNCTION calculate_kl_divergence(
    p_actual_id BIGINT,
    p_predicted_id BIGINT
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN GREATEST(
        0,
        calculate_cross_entropy(p_actual_id, p_predicted_id)
        - calculate_entropy(p_actual_id)
    );
END;
$$;

-- ------------------------------------------------
-- 14. JOINT ENTROPY
-- ------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_joint_entropy(
    p_joint_id BIGINT
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_total NUMERIC;
    v_count BIGINT;
    v_result DOUBLE PRECISION;
BEGIN
    SELECT SUM(probability), COUNT(*)
    INTO v_total, v_count
    FROM joint_probabilities
    WHERE joint_distribution_id = p_joint_id;

    IF v_count = 0 OR ABS(v_total - 1.0) > 0.000000001 THEN
        RAISE EXCEPTION 'Invalid joint distribution';
    END IF;

    SELECT SUM(
        CASE
            WHEN probability > 0 THEN
                -probability * LN(probability) / LN(2.0)
            ELSE 0
        END
    )
    INTO v_result
    FROM joint_probabilities
    WHERE joint_distribution_id = p_joint_id;

    RETURN COALESCE(v_result, 0);
END;
$$;

-- ------------------------------------------------
-- 15. JOINT MARGINALS AND CONDITIONAL ENTROPY
-- ------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_conditional_entropy(
    p_joint_id BIGINT,
    p_target VARCHAR(1) DEFAULT 'x'
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_total NUMERIC;
    v_count BIGINT;
    v_result DOUBLE PRECISION;
BEGIN
    IF p_target NOT IN ('x', 'y') THEN
        RAISE EXCEPTION 'Target must be x or y';
    END IF;

    SELECT SUM(probability), COUNT(*)
    INTO v_total, v_count
    FROM joint_probabilities
    WHERE joint_distribution_id = p_joint_id;

    IF v_count = 0 OR ABS(v_total - 1.0) > 0.000000001 THEN
        RAISE EXCEPTION 'Invalid joint distribution';
    END IF;

    IF p_target = 'x' THEN
        WITH marginal AS (
            SELECT y_value AS condition_value,
                   SUM(probability) AS group_probability
            FROM joint_probabilities
            WHERE joint_distribution_id = p_joint_id
            GROUP BY y_value
        ),
        conditional AS (
            SELECT
                j.y_value,
                j.x_value,
                j.probability / m.group_probability AS cp
            FROM joint_probabilities j
            JOIN marginal m
              ON m.condition_value = j.y_value
            WHERE j.joint_distribution_id = p_joint_id
        )
        SELECT SUM(
            m.group_probability *
            COALESCE(
                (
                    SELECT -SUM(
                        CASE WHEN c.cp > 0
                        THEN c.cp * LN(c.cp) / LN(2.0)
                        ELSE 0 END
                    )
                    FROM conditional c
                    WHERE c.y_value = m.condition_value
                ),
                0
            )
        )
        INTO v_result
        FROM marginal m;

    ELSE
        WITH marginal AS (
            SELECT x_value AS condition_value,
                   SUM(probability) AS group_probability
            FROM joint_probabilities
            WHERE joint_distribution_id = p_joint_id
            GROUP BY x_value
        ),
        conditional AS (
            SELECT
                j.x_value,
                j.y_value,
                j.probability / m.group_probability AS cp
            FROM joint_probabilities j
            JOIN marginal m
              ON m.condition_value = j.x_value
            WHERE j.joint_distribution_id = p_joint_id
        )
        SELECT SUM(
            m.group_probability *
            COALESCE(
                (
                    SELECT -SUM(
                        CASE WHEN c.cp > 0
                        THEN c.cp * LN(c.cp) / LN(2.0)
                        ELSE 0 END
                    )
                    FROM conditional c
                    WHERE c.x_value = m.condition_value
                ),
                0
            )
        )
        INTO v_result
        FROM marginal m;
    END IF;

    RETURN COALESCE(v_result, 0);
END;
$$;

CREATE OR REPLACE FUNCTION calculate_mutual_information(
    p_joint_id BIGINT
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_hx DOUBLE PRECISION;
    v_hy DOUBLE PRECISION;
    v_hxy DOUBLE PRECISION;
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM joint_probabilities
        WHERE joint_distribution_id = p_joint_id
    ) THEN
        RAISE EXCEPTION 'Joint distribution not found';
    END IF;

    WITH x_marginal AS (
        SELECT x_value, SUM(probability) AS p
        FROM joint_probabilities
        WHERE joint_distribution_id = p_joint_id
        GROUP BY x_value
    )
    SELECT -SUM(
        CASE WHEN p > 0 THEN p * LN(p) / LN(2.0) ELSE 0 END
    )
    INTO v_hx
    FROM x_marginal;

    WITH y_marginal AS (
        SELECT y_value, SUM(probability) AS p
        FROM joint_probabilities
        WHERE joint_distribution_id = p_joint_id
        GROUP BY y_value
    )
    SELECT -SUM(
        CASE WHEN p > 0 THEN p * LN(p) / LN(2.0) ELSE 0 END
    )
    INTO v_hy
    FROM y_marginal;

    v_hxy := calculate_joint_entropy(p_joint_id);

    RETURN GREATEST(0, v_hx + v_hy - v_hxy);
END;
$$;

-- ------------------------------------------------
-- 16. ENTROPY REPORTING VIEW
-- ------------------------------------------------

CREATE OR REPLACE VIEW distribution_entropy_report AS
SELECT
    d.experiment_id,
    e.experiment_name,
    d.distribution_id,
    d.distribution_name,
    d.distribution_kind,
    COUNT(p.outcome_id) AS outcome_count,
    SUM(p.probability) AS probability_total,
    CASE
        WHEN ABS(SUM(p.probability) - 1.0) <= 0.000000001
        THEN -SUM(
            CASE
                WHEN p.probability > 0
                THEN p.probability * LN(p.probability) / LN(2.0)
                ELSE 0
            END
        )
        ELSE NULL
    END AS entropy_bits
FROM probability_distributions d
JOIN experiments e
    ON e.experiment_id = d.experiment_id
LEFT JOIN distribution_probabilities p
    ON p.distribution_id = d.distribution_id
GROUP BY
    d.experiment_id,
    e.experiment_name,
    d.distribution_id,
    d.distribution_name,
    d.distribution_kind;

-- ------------------------------------------------
-- 17. JOINT INFORMATION REPORTING VIEW
-- ------------------------------------------------

CREATE OR REPLACE VIEW joint_entropy_report AS
SELECT
    j.joint_distribution_id,
    j.joint_name,
    COUNT(*) AS joint_outcome_count,
    SUM(jp.probability) AS probability_total,
    CASE
        WHEN ABS(SUM(jp.probability) - 1.0) <= 0.000000001
        THEN -SUM(
            CASE
                WHEN jp.probability > 0
                THEN jp.probability * LN(jp.probability) / LN(2.0)
                ELSE 0
            END
        )
        ELSE NULL
    END AS joint_entropy_bits
FROM joint_distributions j
JOIN joint_probabilities jp
    ON jp.joint_distribution_id = j.joint_distribution_id
GROUP BY j.joint_distribution_id, j.joint_name;

-- ------------------------------------------------
-- 18. SAMPLE EXPERIMENTS
-- ------------------------------------------------

INSERT INTO experiments (
    experiment_name,
    description,
    status
)
VALUES
(
    'Communication Source A',
    'Four-symbol discrete information source.',
    'completed'
),
(
    'Weather Dependence',
    'Joint probability model for weather and temperature.',
    'completed'
),
(
    'Prediction Evaluation',
    'Comparison of actual and predicted probabilities.',
    'completed'
),
(
    'Empirical Observation Stream',
    'Frequency-based probability estimation.',
    'collecting'
)
ON CONFLICT (experiment_name) DO NOTHING;

-- ------------------------------------------------
-- 19. SAMPLE OUTCOMES
-- ------------------------------------------------

INSERT INTO outcomes (
    experiment_id,
    outcome_code,
    outcome_description
)
SELECT e.experiment_id, v.code, v.description
FROM experiments e
CROSS JOIN (
    VALUES
        ('A', 'Source symbol A'),
        ('B', 'Source symbol B'),
        ('C', 'Source symbol C'),
        ('D', 'Source symbol D')
) AS v(code, description)
WHERE e.experiment_name = 'Communication Source A'
ON CONFLICT (experiment_id, outcome_code) DO NOTHING;

INSERT INTO outcomes (
    experiment_id,
    outcome_code,
    outcome_description
)
SELECT e.experiment_id, v.code, v.description
FROM experiments e
CROSS JOIN (
    VALUES
        ('A', 'Outcome A'),
        ('B', 'Outcome B'),
        ('C', 'Outcome C')
) AS v(code, description)
WHERE e.experiment_name = 'Prediction Evaluation'
ON CONFLICT (experiment_id, outcome_code) DO NOTHING;

INSERT INTO outcomes (
    experiment_id,
    outcome_code,
    outcome_description
)
SELECT e.experiment_id, v.code, v.description
FROM experiments e
CROSS JOIN (
    VALUES
        ('success', 'Successful event'),
        ('failure', 'Failed event')
) AS v(code, description)
WHERE e.experiment_name = 'Empirical Observation Stream'
ON CONFLICT (experiment_id, outcome_code) DO NOTHING;

-- ------------------------------------------------
-- 20. SAMPLE PROBABILITY DISTRIBUTIONS
-- ------------------------------------------------

INSERT INTO probability_distributions (
    experiment_id,
    distribution_name,
    distribution_kind
)
SELECT
    experiment_id,
    'source_probabilities',
    'actual'
FROM experiments
WHERE experiment_name = 'Communication Source A'
ON CONFLICT DO NOTHING;

INSERT INTO distribution_probabilities (
    distribution_id,
    outcome_id,
    probability
)
SELECT
    d.distribution_id,
    o.outcome_id,
    v.probability
FROM probability_distributions d
JOIN experiments e
    ON e.experiment_id = d.experiment_id
JOIN outcomes o
    ON o.experiment_id = e.experiment_id
JOIN (
    VALUES
        ('A', 0.50::NUMERIC),
        ('B', 0.25::NUMERIC),
        ('C', 0.125::NUMERIC),
        ('D', 0.125::NUMERIC)
) AS v(code, probability)
    ON v.code = o.outcome_code
WHERE e.experiment_name = 'Communication Source A'
  AND d.distribution_name = 'source_probabilities'
ON CONFLICT DO NOTHING;

INSERT INTO probability_distributions (
    experiment_id,
    distribution_name,
    distribution_kind
)
SELECT experiment_id, 'actual_probabilities', 'actual'
FROM experiments
WHERE experiment_name = 'Prediction Evaluation'
ON CONFLICT DO NOTHING;

INSERT INTO probability_distributions (
    experiment_id,
    distribution_name,
    distribution_kind
)
SELECT experiment_id, 'predicted_probabilities', 'predicted'
FROM experiments
WHERE experiment_name = 'Prediction Evaluation'
ON CONFLICT DO NOTHING;

INSERT INTO distribution_probabilities (
    distribution_id,
    outcome_id,
    probability
)
SELECT
    d.distribution_id,
    o.outcome_id,
    v.probability
FROM probability_distributions d
JOIN experiments e
    ON e.experiment_id = d.experiment_id
JOIN outcomes o
    ON o.experiment_id = e.experiment_id
JOIN (
    VALUES
        ('A', 'actual_probabilities', 0.50::NUMERIC),
        ('B', 'actual_probabilities', 0.30::NUMERIC),
        ('C', 'actual_probabilities', 0.20::NUMERIC),
        ('A', 'predicted_probabilities', 0.40::NUMERIC),
        ('B', 'predicted_probabilities', 0.40::NUMERIC),
        ('C', 'predicted_probabilities', 0.20::NUMERIC)
) AS v(code, distribution_name, probability)
    ON v.code = o.outcome_code
   AND v.distribution_name = d.distribution_name
WHERE e.experiment_name = 'Prediction Evaluation'
ON CONFLICT DO NOTHING;

-- ------------------------------------------------
-- 21. JOINT PROBABILITY SAMPLE
-- ------------------------------------------------

INSERT INTO joint_distributions (
    experiment_id,
    joint_name
)
SELECT experiment_id, 'weather_temperature'
FROM experiments
WHERE experiment_name = 'Weather Dependence'
ON CONFLICT (joint_name) DO NOTHING;

INSERT INTO joint_probabilities (
    joint_distribution_id,
    x_value,
    y_value,
    probability
)
SELECT
    j.joint_distribution_id,
    v.x_value,
    v.y_value,
    v.probability
FROM joint_distributions j
CROSS JOIN (
    VALUES
        ('Sunny', 'Hot', 0.30::NUMERIC),
        ('Sunny', 'Cold', 0.20::NUMERIC),
        ('Rainy', 'Hot', 0.10::NUMERIC),
        ('Rainy', 'Cold', 0.40::NUMERIC)
) AS v(x_value, y_value, probability)
WHERE j.joint_name = 'weather_temperature'
ON CONFLICT DO NOTHING;

-- ------------------------------------------------
-- 22. EMPIRICAL OBSERVATION SAMPLE
-- ------------------------------------------------

INSERT INTO observations (
    experiment_id,
    outcome_id,
    source_reference
)
SELECT
    e.experiment_id,
    o.outcome_id,
    'sample-stream'
FROM experiments e
JOIN outcomes o
    ON o.experiment_id = e.experiment_id
JOIN (
    VALUES
        ('success', 4),
        ('failure', 2)
) AS v(code, frequency)
    ON v.code = o.outcome_code
CROSS JOIN LATERAL generate_series(1, v.frequency)
WHERE e.experiment_name = 'Empirical Observation Stream'
  AND NOT EXISTS (
      SELECT 1
      FROM observations existing
      WHERE existing.experiment_id = e.experiment_id
        AND existing.source_reference = 'sample-stream'
  );

-- ------------------------------------------------
-- 23. QUERY: SELF-INFORMATION
-- ------------------------------------------------

SELECT
    o.outcome_code,
    p.probability,
    self_information(
        p.probability::DOUBLE PRECISION
    ) AS self_information_bits
FROM distribution_probabilities p
JOIN probability_distributions d
    ON d.distribution_id = p.distribution_id
JOIN outcomes o
    ON o.outcome_id = p.outcome_id
WHERE d.distribution_name = 'source_probabilities'
ORDER BY o.outcome_code;

-- ------------------------------------------------
-- 24. QUERY: ENTROPY AND UNCERTAINTY
-- ------------------------------------------------

SELECT
    distribution_name,
    outcome_count,
    probability_total,
    entropy_bits,
    calculate_maximum_entropy(outcome_count) AS maximum_entropy_bits,
    calculate_maximum_entropy(outcome_count) - entropy_bits
        AS uncertainty_gap_bits,
    CASE
        WHEN outcome_count > 1
        THEN entropy_bits /
             calculate_maximum_entropy(outcome_count)
        ELSE 0
    END AS normalized_entropy
FROM distribution_entropy_report
WHERE entropy_bits IS NOT NULL
ORDER BY experiment_id, distribution_name;

-- ------------------------------------------------
-- 25. QUERY: CONDITIONAL ENTROPY AND MUTUAL INFORMATION
-- ------------------------------------------------

SELECT
    j.joint_name,
    calculate_joint_entropy(j.joint_distribution_id)
        AS joint_entropy_bits,
    calculate_conditional_entropy(j.joint_distribution_id, 'x')
        AS hx_given_y_bits,
    calculate_conditional_entropy(j.joint_distribution_id, 'y')
        AS hy_given_x_bits,
    calculate_mutual_information(j.joint_distribution_id)
        AS mutual_information_bits
FROM joint_distributions j;

-- ------------------------------------------------
-- 26. QUERY: CROSS-ENTROPY AND KL DIVERGENCE
-- ------------------------------------------------

SELECT
    e.experiment_name,
    calculate_entropy(a.distribution_id) AS actual_entropy_bits,
    calculate_cross_entropy(
        a.distribution_id,
        p.distribution_id
    ) AS cross_entropy_bits,
    calculate_kl_divergence(
        a.distribution_id,
        p.distribution_id
    ) AS kl_divergence_bits
FROM probability_distributions a
JOIN experiments e
    ON e.experiment_id = a.experiment_id
JOIN probability_distributions p
    ON p.experiment_id = a.experiment_id
WHERE a.distribution_name = 'actual_probabilities'
  AND p.distribution_name = 'predicted_probabilities';

-- ------------------------------------------------
-- 27. QUERY: DISTRIBUTION VALIDATION
-- ------------------------------------------------

SELECT
    distribution_name,
    validate_distribution(distribution_id) AS is_valid
FROM probability_distributions
ORDER BY distribution_id;

-- ------------------------------------------------
-- 28. QUERY: EMPIRICAL DISTRIBUTION GENERATION
-- ------------------------------------------------

CALL build_empirical_distribution(
    (
        SELECT experiment_id
        FROM experiments
        WHERE experiment_name = 'Empirical Observation Stream'
    ),
    'generated_empirical_distribution'
);

-- ------------------------------------------------
-- 29. QUERY: OBSERVATION FREQUENCY REPORT
-- ------------------------------------------------

SELECT
    e.experiment_name,
    o.outcome_code,
    COUNT(ob.observation_id) AS observation_count,
    COUNT(ob.observation_id)::DOUBLE PRECISION /
        NULLIF(
            SUM(COUNT(ob.observation_id)) OVER (
                PARTITION BY e.experiment_id
            ),
            0
        ) AS empirical_probability
FROM experiments e
JOIN outcomes o
    ON o.experiment_id = e.experiment_id
LEFT JOIN observations ob
    ON ob.outcome_id = o.outcome_id
WHERE e.experiment_name = 'Empirical Observation Stream'
GROUP BY
    e.experiment_id,
    e.experiment_name,
    o.outcome_code
ORDER BY o.outcome_code;

-- ------------------------------------------------
-- 30. QUERY: INFORMATION METRIC STORAGE
-- ------------------------------------------------

INSERT INTO information_metrics (
    experiment_id,
    metric_name,
    metric_value,
    unit
)
SELECT
    e.experiment_id,
    'entropy',
    calculate_entropy(d.distribution_id),
    'bits'
FROM experiments e
JOIN probability_distributions d
    ON d.experiment_id = e.experiment_id
WHERE d.distribution_name = 'source_probabilities'
ON CONFLICT DO NOTHING;

-- ------------------------------------------------
-- 31. QUERY: STORED METRIC REPORT
-- ------------------------------------------------

SELECT
    e.experiment_name,
    m.metric_name,
    m.metric_value,
    m.unit,
    m.calculated_at
FROM information_metrics m
JOIN experiments e
    ON e.experiment_id = m.experiment_id
ORDER BY m.calculated_at DESC;

-- ------------------------------------------------
-- 32. TRANSACTIONAL VALIDATION EXAMPLE
-- ------------------------------------------------

SAVEPOINT information_validation;

DO $$
DECLARE
    v_id BIGINT;
BEGIN
    SELECT distribution_id
    INTO v_id
    FROM probability_distributions
    WHERE distribution_name = 'source_probabilities';

    IF NOT validate_distribution(v_id) THEN
        RAISE EXCEPTION 'Source distribution failed validation';
    END IF;

    RAISE NOTICE 'Source distribution successfully validated';
END;
$$;

RELEASE SAVEPOINT information_validation;

-- ------------------------------------------------
-- 33. FAILURE HANDLING EXAMPLE
-- ------------------------------------------------

DO $$
BEGIN
    BEGIN
        PERFORM self_information(1.5);
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Invalid probability correctly rejected: %',
                SQLERRM;
    END;
END;
$$;

-- ------------------------------------------------
-- 34. DATA INTEGRITY AND OPERATIONAL QUERIES
-- ------------------------------------------------

SELECT
    e.experiment_name,
    e.status,
    COUNT(DISTINCT o.outcome_id) AS defined_outcomes,
    COUNT(DISTINCT ob.observation_id) AS observations,
    COUNT(DISTINCT d.distribution_id) AS distributions
FROM experiments e
LEFT JOIN outcomes o
    ON o.experiment_id = e.experiment_id
LEFT JOIN observations ob
    ON ob.experiment_id = e.experiment_id
LEFT JOIN probability_distributions d
    ON d.experiment_id = e.experiment_id
GROUP BY e.experiment_id, e.experiment_name, e.status
ORDER BY e.experiment_name;

COMMIT;

-- ================================================================
-- END OF INFORMATION THEORY DATABASE
-- ================================================================
