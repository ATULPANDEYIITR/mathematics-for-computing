/*
 * ENTROPY AND CROSS-ENTROPY ANALYTICS
 * PostgreSQL 15+
 *
 * Models:
 * 1. Probability distributions
 * 2. Events and probabilities
 * 3. Joint probability distributions
 * 4. Shannon entropy
 * 5. Cross-entropy
 * 6. KL divergence
 * 7. Conditional entropy
 * 8. Mutual information
 * 9. Classification predictions
 * 10. Evaluation policies and reports
 *
 * All logarithms are base 2.
 * All entropy values are measured in bits.
 */

BEGIN;

CREATE SCHEMA IF NOT EXISTS information_theory;

SET search_path TO information_theory, public;

-- =========================================================
-- 1. DOMAIN TABLES
-- =========================================================

CREATE TABLE IF NOT EXISTS probability_distribution (
    distribution_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    distribution_name VARCHAR(150) NOT NULL,

    distribution_type VARCHAR(30) NOT NULL
        CHECK (
            distribution_type IN (
                'ACTUAL',
                'PREDICTED',
                'REFERENCE',
                'JOINT'
            )
        ),

    description TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (distribution_name)
);

CREATE TABLE IF NOT EXISTS probability_event (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    distribution_id BIGINT NOT NULL
        REFERENCES probability_distribution(distribution_id)
        ON DELETE CASCADE,

    event_name VARCHAR(150) NOT NULL,

    probability DOUBLE PRECISION NOT NULL
        CHECK (
            probability >= 0
            AND probability <= 1
            AND probability <> 'Infinity'::DOUBLE PRECISION
            AND probability <> 'NaN'::DOUBLE PRECISION
        ),

    UNIQUE (distribution_id, event_name)
);

CREATE INDEX IF NOT EXISTS idx_probability_event_distribution
    ON probability_event(distribution_id);

CREATE TABLE IF NOT EXISTS joint_probability (
    joint_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    distribution_id BIGINT NOT NULL
        REFERENCES probability_distribution(distribution_id)
        ON DELETE CASCADE,

    x_event VARCHAR(150) NOT NULL,

    y_event VARCHAR(150) NOT NULL,

    probability DOUBLE PRECISION NOT NULL
        CHECK (
            probability >= 0
            AND probability <= 1
            AND probability <> 'Infinity'::DOUBLE PRECISION
            AND probability <> 'NaN'::DOUBLE PRECISION
        ),

    UNIQUE (distribution_id, x_event, y_event)
);

CREATE INDEX IF NOT EXISTS idx_joint_distribution
    ON joint_probability(distribution_id);

CREATE TABLE IF NOT EXISTS evaluation_policy (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    policy_name VARCHAR(120) NOT NULL UNIQUE,

    maximum_cross_entropy DOUBLE PRECISION NOT NULL
        CHECK (
            maximum_cross_entropy > 0
            AND maximum_cross_entropy <>
                'Infinity'::DOUBLE PRECISION
            AND maximum_cross_entropy <>
                'NaN'::DOUBLE PRECISION
        ),

    require_finite_loss BOOLEAN NOT NULL DEFAULT TRUE,

    allow_zero_predicted_probability BOOLEAN
        NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS entropy_evaluation (
    evaluation_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    actual_distribution_id BIGINT NOT NULL
        REFERENCES probability_distribution(distribution_id),

    predicted_distribution_id BIGINT NOT NULL
        REFERENCES probability_distribution(distribution_id),

    policy_id BIGINT NOT NULL
        REFERENCES evaluation_policy(policy_id),

    shannon_entropy DOUBLE PRECISION,

    cross_entropy DOUBLE PRECISION,

    kl_divergence DOUBLE PRECISION,

    evaluation_status VARCHAR(30) NOT NULL DEFAULT 'PENDING'
        CHECK (
            evaluation_status IN (
                'PENDING',
                'VALID',
                'INFINITE_LOSS',
                'POLICY_REJECTED',
                'INVALID'
            )
        ),

    evaluated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_evaluation_status
    ON entropy_evaluation(evaluation_status);

CREATE INDEX IF NOT EXISTS idx_evaluation_created
    ON entropy_evaluation(evaluated_at DESC);

-- =========================================================
-- 2. DISTRIBUTION VALIDATION
-- =========================================================

CREATE OR REPLACE FUNCTION validate_distribution(
    p_distribution_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_count BIGINT;
    v_total DOUBLE PRECISION;
BEGIN
    SELECT
        COUNT(*),
        COALESCE(SUM(probability), 0)
    INTO v_count, v_total
    FROM probability_event
    WHERE distribution_id = p_distribution_id;

    IF v_count = 0 THEN
        RETURN FALSE;
    END IF;

    RETURN ABS(v_total - 1.0) <= 0.0000000001;
END;
$$;

CREATE OR REPLACE FUNCTION validate_joint_distribution(
    p_distribution_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_count BIGINT;
    v_total DOUBLE PRECISION;
BEGIN
    SELECT
        COUNT(*),
        COALESCE(SUM(probability), 0)
    INTO v_count, v_total
    FROM joint_probability
    WHERE distribution_id = p_distribution_id;

    IF v_count = 0 THEN
        RETURN FALSE;
    END IF;

    RETURN ABS(v_total - 1.0) <= 0.0000000001;
END;
$$;

-- =========================================================
-- 3. SHANNON ENTROPY
-- =========================================================

CREATE OR REPLACE FUNCTION calculate_entropy(
    p_distribution_id BIGINT
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_result DOUBLE PRECISION;
BEGIN
    IF NOT validate_distribution(p_distribution_id) THEN
        RAISE EXCEPTION
            'Invalid or incomplete distribution: %',
            p_distribution_id;
    END IF;

    SELECT COALESCE(
        -SUM(
            CASE
                WHEN probability > 0
                THEN probability * LOG(2, probability)
                ELSE 0
            END
        ),
        0
    )
    INTO v_result
    FROM probability_event
    WHERE distribution_id = p_distribution_id;

    RETURN v_result;
END;
$$;

-- =========================================================
-- 4. CROSS-ENTROPY
-- =========================================================

CREATE OR REPLACE FUNCTION calculate_cross_entropy(
    p_actual_id BIGINT,
    p_predicted_id BIGINT
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_actual_count BIGINT;
    v_predicted_count BIGINT;
    v_missing BIGINT;
    v_result DOUBLE PRECISION;
BEGIN
    IF NOT validate_distribution(p_actual_id)
       OR NOT validate_distribution(p_predicted_id) THEN
        RAISE EXCEPTION 'Invalid input distribution.';
    END IF;

    SELECT COUNT(*)
    INTO v_actual_count
    FROM probability_event
    WHERE distribution_id = p_actual_id;

    SELECT COUNT(*)
    INTO v_predicted_count
    FROM probability_event
    WHERE distribution_id = p_predicted_id;

    IF v_actual_count <> v_predicted_count THEN
        RAISE EXCEPTION
            'Distribution dimensions do not match.';
    END IF;

    SELECT COUNT(*)
    INTO v_missing
    FROM probability_event a
    LEFT JOIN probability_event q
        ON q.distribution_id = p_predicted_id
        AND q.event_name = a.event_name
    WHERE a.distribution_id = p_actual_id
      AND q.event_id IS NULL;

    IF v_missing > 0 THEN
        RAISE EXCEPTION
            'Distribution event sets do not match.';
    END IF;

    SELECT CASE
        WHEN BOOL_OR(
            a.probability > 0
            AND q.probability = 0
        )
        THEN 'Infinity'::DOUBLE PRECISION
        ELSE -SUM(
            CASE
                WHEN a.probability > 0
                THEN a.probability * LOG(2, q.probability)
                ELSE 0
            END
        )
    END
    INTO v_result
    FROM probability_event a
    JOIN probability_event q
        ON q.event_name = a.event_name
    WHERE a.distribution_id = p_actual_id
      AND q.distribution_id = p_predicted_id;

    RETURN v_result;
END;
$$;

-- =========================================================
-- 5. KL DIVERGENCE
-- =========================================================

CREATE OR REPLACE FUNCTION calculate_kl_divergence(
    p_actual_id BIGINT,
    p_predicted_id BIGINT
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_cross_entropy DOUBLE PRECISION;
    v_entropy DOUBLE PRECISION;
BEGIN
    v_cross_entropy := calculate_cross_entropy(
        p_actual_id,
        p_predicted_id
    );

    v_entropy := calculate_entropy(p_actual_id);

    IF v_cross_entropy = 'Infinity'::DOUBLE PRECISION THEN
        RETURN v_cross_entropy;
    END IF;

    RETURN GREATEST(
        0,
        v_cross_entropy - v_entropy
    );
END;
$$;

-- =========================================================
-- 6. JOINT DISTRIBUTION METRICS
-- =========================================================

CREATE OR REPLACE FUNCTION calculate_joint_entropy(
    p_distribution_id BIGINT
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_result DOUBLE PRECISION;
BEGIN
    IF NOT validate_joint_distribution(p_distribution_id) THEN
        RAISE EXCEPTION
            'Invalid joint distribution: %',
            p_distribution_id;
    END IF;

    SELECT -SUM(
        CASE
            WHEN probability > 0
            THEN probability * LOG(2, probability)
            ELSE 0
        END
    )
    INTO v_result
    FROM joint_probability
    WHERE distribution_id = p_distribution_id;

    RETURN v_result;
END;
$$;

CREATE OR REPLACE FUNCTION calculate_mutual_information(
    p_distribution_id BIGINT
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
    IF NOT validate_joint_distribution(p_distribution_id) THEN
        RAISE EXCEPTION 'Invalid joint distribution.';
    END IF;

    WITH marginals AS (
        SELECT
            x_event,
            y_event,
            SUM(probability) AS probability
        FROM joint_probability
        WHERE distribution_id = p_distribution_id
        GROUP BY x_event, y_event
    ),
    mx AS (
        SELECT
            x_event,
            SUM(probability) AS probability
        FROM marginals
        GROUP BY x_event
    ),
    my AS (
        SELECT
            y_event,
            SUM(probability) AS probability
        FROM marginals
        GROUP BY y_event
    )
    SELECT
        -COALESCE(
            (SELECT SUM(
                CASE WHEN probability > 0
                    THEN probability * LOG(2, probability)
                    ELSE 0 END
            ) FROM mx), 0
        ),
        -COALESCE(
            (SELECT SUM(
                CASE WHEN probability > 0
                    THEN probability * LOG(2, probability)
                    ELSE 0 END
            ) FROM my), 0
        ),
        calculate_joint_entropy(p_distribution_id)
    INTO v_hx, v_hy, v_hxy;

    RETURN GREATEST(0, v_hx + v_hy - v_hxy);
END;
$$;

-- =========================================================
-- 7. CONDITIONAL ENTROPY
-- =========================================================

CREATE OR REPLACE FUNCTION calculate_conditional_entropy(
    p_distribution_id BIGINT
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_hxy DOUBLE PRECISION;
    v_hx DOUBLE PRECISION;
BEGIN
    IF NOT validate_joint_distribution(p_distribution_id) THEN
        RAISE EXCEPTION 'Invalid joint distribution.';
    END IF;

    v_hxy := calculate_joint_entropy(p_distribution_id);

    WITH marginal AS (
        SELECT
            x_event,
            SUM(probability) AS probability
        FROM joint_probability
        WHERE distribution_id = p_distribution_id
        GROUP BY x_event
    )
    SELECT -SUM(
        CASE
            WHEN probability > 0
            THEN probability * LOG(2, probability)
            ELSE 0
        END
    )
    INTO v_hx
    FROM marginal;

    RETURN GREATEST(0, v_hxy - v_hx);
END;
$$;

-- =========================================================
-- 8. EVALUATION WORKFLOW
-- =========================================================

CREATE OR REPLACE PROCEDURE evaluate_distribution_pair(
    p_actual_id BIGINT,
    p_predicted_id BIGINT,
    p_policy_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_entropy DOUBLE PRECISION;
    v_cross_entropy DOUBLE PRECISION;
    v_kl DOUBLE PRECISION;
    v_maximum DOUBLE PRECISION;
    v_require_finite BOOLEAN;
    v_allow_zero BOOLEAN;
    v_status VARCHAR(30);
BEGIN
    SELECT
        maximum_cross_entropy,
        require_finite_loss,
        allow_zero_predicted_probability
    INTO
        v_maximum,
        v_require_finite,
        v_allow_zero
    FROM evaluation_policy
    WHERE policy_id = p_policy_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Evaluation policy not found.';
    END IF;

    v_entropy := calculate_entropy(p_actual_id);

    v_cross_entropy := calculate_cross_entropy(
        p_actual_id,
        p_predicted_id
    );

    v_kl := calculate_kl_divergence(
        p_actual_id,
        p_predicted_id
    );

    IF v_cross_entropy = 'Infinity'::DOUBLE PRECISION THEN
        IF NOT v_allow_zero THEN
            v_status := 'INFINITE_LOSS';
        ELSE
            v_status := 'VALID';
        END IF;
    ELSIF v_cross_entropy > v_maximum THEN
        v_status := 'POLICY_REJECTED';
    ELSE
        v_status := 'VALID';
    END IF;

    IF v_require_finite
       AND v_cross_entropy = 'Infinity'::DOUBLE PRECISION THEN
        v_status := 'INFINITE_LOSS';
    END IF;

    INSERT INTO entropy_evaluation (
        actual_distribution_id,
        predicted_distribution_id,
        policy_id,
        shannon_entropy,
        cross_entropy,
        kl_divergence,
        evaluation_status,
        evaluated_at
    )
    VALUES (
        p_actual_id,
        p_predicted_id,
        p_policy_id,
        v_entropy,
        v_cross_entropy,
        v_kl,
        v_status,
        CURRENT_TIMESTAMP
    );
END;
$$;

-- =========================================================
-- 9. REPORTING VIEWS
-- =========================================================

CREATE OR REPLACE VIEW distribution_summary AS
SELECT
    d.distribution_id,
    d.distribution_name,
    d.distribution_type,
    COUNT(e.event_id) AS event_count,
    COALESCE(SUM(e.probability), 0) AS probability_total,
    CASE
        WHEN COUNT(e.event_id) = 0 THEN FALSE
        ELSE ABS(SUM(e.probability) - 1.0) <= 0.0000000001
    END AS is_valid
FROM probability_distribution d
LEFT JOIN probability_event e
    ON e.distribution_id = d.distribution_id
GROUP BY
    d.distribution_id,
    d.distribution_name,
    d.distribution_type;

CREATE OR REPLACE VIEW evaluation_report AS
SELECT
    e.evaluation_id,
    a.distribution_name AS actual_distribution,
    p.distribution_name AS predicted_distribution,
    ep.policy_name,
    e.shannon_entropy,
    e.cross_entropy,
    e.kl_divergence,
    e.evaluation_status,
    e.evaluated_at
FROM entropy_evaluation e
JOIN probability_distribution a
    ON a.distribution_id = e.actual_distribution_id
JOIN probability_distribution p
    ON p.distribution_id = e.predicted_distribution_id
JOIN evaluation_policy ep
    ON ep.policy_id = e.policy_id;

-- =========================================================
-- 10. SAMPLE DATA
-- =========================================================

INSERT INTO probability_distribution (
    distribution_name,
    distribution_type,
    description
)
VALUES
(
    'observed_classes',
    'ACTUAL',
    'Observed classification outcomes'
),
(
    'model_predictions',
    'PREDICTED',
    'Predicted classification probabilities'
),
(
    'perfect_predictions',
    'PREDICTED',
    'Prediction identical to observed distribution'
),
(
    'zero_probability_predictions',
    'PREDICTED',
    'Prediction with zero probability for an observed event'
),
(
    'dependent_variables',
    'JOINT',
    'Joint probability distribution of X and Y'
)
ON CONFLICT (distribution_name) DO NOTHING;

INSERT INTO probability_event (
    distribution_id,
    event_name,
    probability
)
SELECT d.distribution_id, x.event_name, x.probability
FROM probability_distribution d
CROSS JOIN (
    VALUES
        ('class_A', 0.50::DOUBLE PRECISION),
        ('class_B', 0.30::DOUBLE PRECISION),
        ('class_C', 0.20::DOUBLE PRECISION)
) AS x(event_name, probability)
WHERE d.distribution_name = 'observed_classes'
ON CONFLICT (distribution_id, event_name)
DO UPDATE SET probability = EXCLUDED.probability;

INSERT INTO probability_event (
    distribution_id,
    event_name,
    probability
)
SELECT d.distribution_id, x.event_name, x.probability
FROM probability_distribution d
CROSS JOIN (
    VALUES
        ('class_A', 0.40::DOUBLE PRECISION),
        ('class_B', 0.40::DOUBLE PRECISION),
        ('class_C', 0.20::DOUBLE PRECISION)
) AS x(event_name, probability)
WHERE d.distribution_name = 'model_predictions'
ON CONFLICT (distribution_id, event_name)
DO UPDATE SET probability = EXCLUDED.probability;

INSERT INTO probability_event (
    distribution_id,
    event_name,
    probability
)
SELECT d.distribution_id, x.event_name, x.probability
FROM probability_distribution d
CROSS JOIN (
    VALUES
        ('class_A', 0.50::DOUBLE PRECISION),
        ('class_B', 0.30::DOUBLE PRECISION),
        ('class_C', 0.20::DOUBLE PRECISION)
) AS x(event_name, probability)
WHERE d.distribution_name = 'perfect_predictions'
ON CONFLICT (distribution_id, event_name)
DO UPDATE SET probability = EXCLUDED.probability;

INSERT INTO probability_event (
    distribution_id,
    event_name,
    probability
)
SELECT d.distribution_id, x.event_name, x.probability
FROM probability_distribution d
CROSS JOIN (
    VALUES
        ('class_A', 1.00::DOUBLE PRECISION),
        ('class_B', 0.00::DOUBLE PRECISION),
        ('class_C', 0.00::DOUBLE PRECISION)
) AS x(event_name, probability)
WHERE d.distribution_name = 'zero_probability_predictions'
ON CONFLICT (distribution_id, event_name)
DO UPDATE SET probability = EXCLUDED.probability;

INSERT INTO joint_probability (
    distribution_id,
    x_event,
    y_event,
    probability
)
SELECT
    d.distribution_id,
    x.x_event,
    x.y_event,
    x.probability
FROM probability_distribution d
CROSS JOIN (
    VALUES
        ('X0', 'Y0', 0.40::DOUBLE PRECISION),
        ('X0', 'Y1', 0.10::DOUBLE PRECISION),
        ('X1', 'Y0', 0.10::DOUBLE PRECISION),
        ('X1', 'Y1', 0.40::DOUBLE PRECISION)
) AS x(x_event, y_event, probability)
WHERE d.distribution_name = 'dependent_variables'
ON CONFLICT (distribution_id, x_event, y_event)
DO UPDATE SET probability = EXCLUDED.probability;

INSERT INTO evaluation_policy (
    policy_name,
    maximum_cross_entropy,
    require_finite_loss,
    allow_zero_predicted_probability
)
VALUES
(
    'standard_policy',
    100.0,
    TRUE,
    FALSE
),
(
    'strict_policy',
    2.0,
    TRUE,
    FALSE
)
ON CONFLICT (policy_name) DO NOTHING;

-- =========================================================
-- 11. DISTRIBUTION RETRIEVAL
-- =========================================================

SELECT *
FROM distribution_summary
ORDER BY distribution_id;

-- =========================================================
-- 12. SHANNON ENTROPY REPORT
-- =========================================================

SELECT
    d.distribution_name,
    calculate_entropy(d.distribution_id) AS entropy_bits
FROM probability_distribution d
WHERE d.distribution_type IN ('ACTUAL', 'PREDICTED')
AND EXISTS (
    SELECT 1
    FROM probability_event e
    WHERE e.distribution_id = d.distribution_id
);

-- =========================================================
-- 13. CROSS-ENTROPY AND KL REPORT
-- =========================================================

SELECT
    calculate_entropy(a.distribution_id) AS entropy_bits,
    calculate_cross_entropy(
        a.distribution_id,
        p.distribution_id
    ) AS cross_entropy_bits,
    calculate_kl_divergence(
        a.distribution_id,
        p.distribution_id
    ) AS kl_divergence_bits
FROM probability_distribution a
JOIN probability_distribution p
    ON p.distribution_name = 'model_predictions'
WHERE a.distribution_name = 'observed_classes';

-- =========================================================
-- 14. JOINT DISTRIBUTION ANALYSIS
-- =========================================================

SELECT
    calculate_joint_entropy(d.distribution_id)
        AS joint_entropy_bits,

    calculate_conditional_entropy(d.distribution_id)
        AS conditional_entropy_bits,

    calculate_mutual_information(d.distribution_id)
        AS mutual_information_bits

FROM probability_distribution d
WHERE d.distribution_name = 'dependent_variables';

-- =========================================================
-- 15. AGGREGATION AND ELIGIBILITY
-- =========================================================

SELECT
    evaluation_status,
    COUNT(*) AS evaluation_count,
    AVG(shannon_entropy) AS average_entropy,
    AVG(cross_entropy) AS average_cross_entropy,
    AVG(kl_divergence) AS average_kl_divergence
FROM entropy_evaluation
GROUP BY evaluation_status;

-- =========================================================
-- 16. TRANSACTIONAL EVALUATION
-- =========================================================

DO $$
DECLARE
    v_actual BIGINT;
    v_predicted BIGINT;
    v_policy BIGINT;
BEGIN
    SELECT distribution_id
    INTO STRICT v_actual
    FROM probability_distribution
    WHERE distribution_name = 'observed_classes';

    SELECT distribution_id
    INTO STRICT v_predicted
    FROM probability_distribution
    WHERE distribution_name = 'model_predictions';

    SELECT policy_id
    INTO STRICT v_policy
    FROM evaluation_policy
    WHERE policy_name = 'standard_policy';

    CALL evaluate_distribution_pair(
        v_actual,
        v_predicted,
        v_policy
    );
END;
$$;

-- =========================================================
-- 17. ZERO-PROBABILITY FAILURE CASE
-- =========================================================

DO $$
DECLARE
    v_actual BIGINT;
    v_predicted BIGINT;
    v_policy BIGINT;
BEGIN
    SELECT distribution_id
    INTO STRICT v_actual
    FROM probability_distribution
    WHERE distribution_name = 'observed_classes';

    SELECT distribution_id
    INTO STRICT v_predicted
    FROM probability_distribution
    WHERE distribution_name = 'zero_probability_predictions';

    SELECT policy_id
    INTO STRICT v_policy
    FROM evaluation_policy
    WHERE policy_name = 'standard_policy';

    CALL evaluate_distribution_pair(
        v_actual,
        v_predicted,
        v_policy
    );
END;
$$;

-- =========================================================
-- 18. FINAL EVALUATION REPORT
-- =========================================================

SELECT *
FROM evaluation_report
ORDER BY evaluation_id;

COMMIT;
