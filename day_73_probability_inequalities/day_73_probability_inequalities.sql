/*
    PROBABILITY INEQUALITIES
    Markov, Chebyshev, Jensen, and Chernoff Bounds

    PostgreSQL 14+
    Self-contained relational probability analysis system.

    The database stores finite discrete distributions, experiments,
    mathematical assumptions, calculated bounds, and evaluation results.
*/

BEGIN;

CREATE SCHEMA IF NOT EXISTS probability_lab;

SET search_path TO probability_lab, public;

-- ============================================================
-- 1. DOMAIN TYPES
-- ============================================================

CREATE TYPE inequality_type AS ENUM (
    'MARKOV',
    'CHEBYSHEV',
    'JENSEN',
    'CHERNOFF'
);

CREATE TYPE experiment_status AS ENUM (
    'DRAFT',
    'VALIDATED',
    'EVALUATED',
    'FAILED'
);

CREATE TYPE function_type AS ENUM (
    'SQUARE',
    'EXPONENTIAL',
    'ABSOLUTE'
);

-- ============================================================
-- 2. CORE TABLES
-- ============================================================

CREATE TABLE distributions (
    distribution_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    distribution_name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    is_normalized BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(distribution_name)) > 0)
);

CREATE TABLE outcomes (
    outcome_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    distribution_id BIGINT NOT NULL
        REFERENCES distributions(distribution_id)
        ON DELETE CASCADE,
    outcome_value DOUBLE PRECISION NOT NULL,
    probability DOUBLE PRECISION NOT NULL,
    UNIQUE (distribution_id, outcome_value),
    CHECK (
        probability >= 0
        AND probability <= 1
        AND probability < 'Infinity'::DOUBLE PRECISION
        AND probability = probability
    ),
    CHECK (
        outcome_value > '-Infinity'::DOUBLE PRECISION
        AND outcome_value < 'Infinity'::DOUBLE PRECISION
        AND outcome_value = outcome_value
    )
);

CREATE INDEX idx_outcomes_distribution
    ON outcomes(distribution_id);

CREATE INDEX idx_outcomes_value
    ON outcomes(distribution_id, outcome_value);

CREATE TABLE experiments (
    experiment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    distribution_id BIGINT NOT NULL
        REFERENCES distributions(distribution_id),
    experiment_name VARCHAR(150) NOT NULL UNIQUE,
    threshold DOUBLE PRECISION NOT NULL,
    deviation DOUBLE PRECISION NOT NULL,
    status experiment_status NOT NULL DEFAULT 'DRAFT',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(experiment_name)) > 0),
    CHECK (
        threshold > '-Infinity'::DOUBLE PRECISION
        AND threshold < 'Infinity'::DOUBLE PRECISION
    ),
    CHECK (
        deviation > 0
        AND deviation < 'Infinity'::DOUBLE PRECISION
    )
);

CREATE TABLE inequality_evaluations (
    evaluation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id)
        ON DELETE CASCADE,
    inequality inequality_type NOT NULL,
    calculated_bound DOUBLE PRECISION NOT NULL,
    exact_probability DOUBLE PRECISION,
    optimal_parameter DOUBLE PRECISION,
    assumption_valid BOOLEAN NOT NULL,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (experiment_id, inequality),
    CHECK (
        calculated_bound >= 0
        AND calculated_bound <= 1
        AND calculated_bound < 'Infinity'::DOUBLE PRECISION
        AND calculated_bound = calculated_bound
    ),
    CHECK (
        exact_probability IS NULL
        OR (
            exact_probability >= 0
            AND exact_probability <= 1
            AND exact_probability < 'Infinity'::DOUBLE PRECISION
            AND exact_probability = exact_probability
        )
    )
);

CREATE INDEX idx_evaluations_experiment
    ON inequality_evaluations(experiment_id, inequality);

CREATE TABLE convex_functions (
    function_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    function_name VARCHAR(100) NOT NULL UNIQUE,
    implementation function_type NOT NULL,
    is_convex BOOLEAN NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE jensen_evaluations (
    jensen_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    experiment_id BIGINT NOT NULL
        REFERENCES experiments(experiment_id)
        ON DELETE CASCADE,
    function_id BIGINT NOT NULL
        REFERENCES convex_functions(function_id),
    function_at_mean DOUBLE PRECISION NOT NULL,
    mean_of_function DOUBLE PRECISION NOT NULL,
    inequality_holds BOOLEAN NOT NULL,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 3. DISTRIBUTION VALIDATION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_distribution(
    p_distribution_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_count BIGINT;
    v_total DOUBLE PRECISION;
BEGIN
    SELECT COUNT(*), COALESCE(SUM(probability), 0)
    INTO v_count, v_total
    FROM outcomes
    WHERE distribution_id = p_distribution_id;

    IF v_count = 0 THEN
        RAISE EXCEPTION 'Distribution % has no outcomes',
            p_distribution_id;
    END IF;

    IF abs(v_total - 1.0) > 1e-10 THEN
        RAISE EXCEPTION
            'Distribution probabilities must sum to one. Actual: %',
            v_total;
    END IF;

    UPDATE distributions
    SET is_normalized = TRUE
    WHERE distribution_id = p_distribution_id;

    RETURN TRUE;
END;
$$;

CREATE OR REPLACE FUNCTION invalidate_distribution()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE distributions
    SET is_normalized = FALSE
    WHERE distribution_id = COALESCE(
        NEW.distribution_id,
        OLD.distribution_id
    );

    RETURN COALESCE(NEW, OLD);
END;
$$;

CREATE TRIGGER trg_invalidate_distribution
AFTER INSERT OR UPDATE OR DELETE ON outcomes
FOR EACH ROW
EXECUTE FUNCTION invalidate_distribution();

-- ============================================================
-- 4. MOMENT CALCULATIONS
-- ============================================================

CREATE OR REPLACE FUNCTION distribution_mean(
    p_distribution_id BIGINT
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_mean DOUBLE PRECISION;
BEGIN
    SELECT SUM(outcome_value * probability)
    INTO v_mean
    FROM outcomes
    WHERE distribution_id = p_distribution_id;

    IF v_mean IS NULL THEN
        RAISE EXCEPTION 'Distribution does not exist or is empty';
    END IF;

    RETURN v_mean;
END;
$$;

CREATE OR REPLACE FUNCTION distribution_variance(
    p_distribution_id BIGINT
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_mean DOUBLE PRECISION;
    v_variance DOUBLE PRECISION;
BEGIN
    v_mean := distribution_mean(p_distribution_id);

    SELECT SUM(
        probability * POWER(outcome_value - v_mean, 2)
    )
    INTO v_variance
    FROM outcomes
    WHERE distribution_id = p_distribution_id;

    RETURN v_variance;
END;
$$;

CREATE OR REPLACE FUNCTION distribution_expectation(
    p_distribution_id BIGINT,
    p_function function_type
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_result DOUBLE PRECISION;
BEGIN
    SELECT SUM(
        probability *
        CASE p_function
            WHEN 'SQUARE' THEN POWER(outcome_value, 2)
            WHEN 'EXPONENTIAL' THEN EXP(outcome_value)
            WHEN 'ABSOLUTE' THEN ABS(outcome_value)
        END
    )
    INTO v_result
    FROM outcomes
    WHERE distribution_id = p_distribution_id;

    IF v_result IS NULL OR v_result = 'Infinity'::DOUBLE PRECISION THEN
        RAISE EXCEPTION 'Invalid expectation calculation';
    END IF;

    RETURN v_result;
END;
$$;

CREATE OR REPLACE FUNCTION exact_upper_probability(
    p_distribution_id BIGINT,
    p_threshold DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE SQL
STABLE
AS $$
    SELECT COALESCE(SUM(probability), 0)
    FROM outcomes
    WHERE distribution_id = p_distribution_id
      AND outcome_value >= p_threshold;
$$;

CREATE OR REPLACE FUNCTION exact_deviation_probability(
    p_distribution_id BIGINT,
    p_deviation DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_mean DOUBLE PRECISION;
    v_result DOUBLE PRECISION;
BEGIN
    IF p_deviation <= 0 THEN
        RAISE EXCEPTION 'Deviation must be positive';
    END IF;

    v_mean := distribution_mean(p_distribution_id);

    SELECT COALESCE(SUM(probability), 0)
    INTO v_result
    FROM outcomes
    WHERE distribution_id = p_distribution_id
      AND ABS(outcome_value - v_mean) >= p_deviation;

    RETURN v_result;
END;
$$;

-- ============================================================
-- 5. MARKOV INEQUALITY
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_markov(
    p_distribution_id BIGINT,
    p_threshold DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_mean DOUBLE PRECISION;
    v_minimum DOUBLE PRECISION;
BEGIN
    IF p_threshold <= 0
       OR p_threshold = 'Infinity'::DOUBLE PRECISION THEN
        RAISE EXCEPTION 'Markov threshold must be positive and finite';
    END IF;

    SELECT MIN(outcome_value)
    INTO v_minimum
    FROM outcomes
    WHERE distribution_id = p_distribution_id;

    IF v_minimum IS NULL OR v_minimum < 0 THEN
        RAISE EXCEPTION
            'Markov inequality requires a nonnegative variable';
    END IF;

    v_mean := distribution_mean(p_distribution_id);

    RETURN LEAST(1.0, v_mean / p_threshold);
END;
$$;

-- ============================================================
-- 6. CHEBYSHEV INEQUALITY
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_chebyshev(
    p_distribution_id BIGINT,
    p_deviation DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    IF p_deviation <= 0
       OR p_deviation = 'Infinity'::DOUBLE PRECISION THEN
        RAISE EXCEPTION 'Deviation must be positive and finite';
    END IF;

    RETURN LEAST(
        1.0,
        distribution_variance(p_distribution_id)
        / POWER(p_deviation, 2)
    );
END;
$$;

-- ============================================================
-- 7. JENSEN INEQUALITY
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_jensen(
    p_distribution_id BIGINT,
    p_function function_type
)
RETURNS TABLE (
    function_at_mean DOUBLE PRECISION,
    mean_of_function DOUBLE PRECISION,
    inequality_holds BOOLEAN
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_mean DOUBLE PRECISION;
    v_left DOUBLE PRECISION;
    v_right DOUBLE PRECISION;
BEGIN
    v_mean := distribution_mean(p_distribution_id);

    IF p_function = 'SQUARE' THEN
        v_left := POWER(v_mean, 2);
    ELSIF p_function = 'EXPONENTIAL' THEN
        v_left := EXP(v_mean);
    ELSIF p_function = 'ABSOLUTE' THEN
        v_left := ABS(v_mean);
    END IF;

    v_right := distribution_expectation(
        p_distribution_id,
        p_function
    );

    function_at_mean := v_left;
    mean_of_function := v_right;
    inequality_holds := v_left <= v_right + 1e-10;

    RETURN NEXT;
END;
$$;

-- ============================================================
-- 8. CHERNOFF INEQUALITY
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_chernoff(
    p_distribution_id BIGINT,
    p_threshold DOUBLE PRECISION,
    p_lambda_max DOUBLE PRECISION DEFAULT 20.0,
    p_steps INTEGER DEFAULT 2000
)
RETURNS TABLE (
    probability_bound DOUBLE PRECISION,
    optimal_lambda DOUBLE PRECISION
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_lambda DOUBLE PRECISION;
    v_log_mgf DOUBLE PRECISION;
    v_exponent DOUBLE PRECISION;
    v_bound DOUBLE PRECISION;
    v_best_bound DOUBLE PRECISION := 1.0;
    v_best_lambda DOUBLE PRECISION := 0.0;
BEGIN
    IF p_lambda_max <= 0
       OR p_lambda_max = 'Infinity'::DOUBLE PRECISION
       OR p_steps <= 0
       OR p_threshold = 'Infinity'::DOUBLE PRECISION
       OR p_threshold = '-Infinity'::DOUBLE PRECISION THEN
        RAISE EXCEPTION 'Invalid Chernoff parameters';
    END IF;

    FOR i IN 0..p_steps LOOP
        v_lambda := p_lambda_max * i / p_steps;

        -- MGF is evaluated in log space for numerical stability.
        SELECT MAX(
            LN(probability) + v_lambda * outcome_value
        )
        INTO v_log_mgf
        FROM outcomes
        WHERE distribution_id = p_distribution_id
          AND probability > 0;

        IF v_log_mgf IS NULL THEN
            RAISE EXCEPTION 'Distribution is empty';
        END IF;

        SELECT v_log_mgf + LN(SUM(
            EXP(
                LN(probability) +
                v_lambda * outcome_value -
                v_log_mgf
            )
        ))
        INTO v_log_mgf
        FROM outcomes
        WHERE distribution_id = p_distribution_id
          AND probability > 0;

        v_exponent := v_log_mgf - v_lambda * p_threshold;

        IF v_exponent < -745 THEN
            v_bound := 0;
        ELSE
            v_bound := LEAST(1.0, EXP(v_exponent));
        END IF;

        IF v_bound < v_best_bound THEN
            v_best_bound := v_bound;
            v_best_lambda := v_lambda;
        END IF;
    END LOOP;

    probability_bound := v_best_bound;
    optimal_lambda := v_best_lambda;

    RETURN NEXT;
END;
$$;

-- ============================================================
-- 9. EVALUATION WORKFLOW
-- ============================================================

CREATE OR REPLACE PROCEDURE evaluate_experiment(
    p_experiment_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_experiment experiments%ROWTYPE;
    v_markov DOUBLE PRECISION;
    v_chebyshev DOUBLE PRECISION;
    v_chernoff DOUBLE PRECISION;
    v_lambda DOUBLE PRECISION;
    v_minimum DOUBLE PRECISION;
BEGIN
    SELECT *
    INTO v_experiment
    FROM experiments
    WHERE experiment_id = p_experiment_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Experiment not found';
    END IF;

    BEGIN
        IF NOT validate_distribution(
            v_experiment.distribution_id
        ) THEN
            RAISE EXCEPTION 'Distribution validation failed';
        END IF;

        UPDATE experiments
        SET status = 'VALIDATED'
        WHERE experiment_id = p_experiment_id;

        v_chebyshev := calculate_chebyshev(
            v_experiment.distribution_id,
            v_experiment.deviation
        );

        INSERT INTO inequality_evaluations (
            experiment_id,
            inequality,
            calculated_bound,
            exact_probability,
            assumption_valid
        )
        VALUES (
            p_experiment_id,
            'CHEBYSHEV',
            v_chebyshev,
            exact_deviation_probability(
                v_experiment.distribution_id,
                v_experiment.deviation
            ),
            TRUE
        )
        ON CONFLICT (experiment_id, inequality)
        DO UPDATE SET
            calculated_bound = EXCLUDED.calculated_bound,
            exact_probability = EXCLUDED.exact_probability,
            assumption_valid = EXCLUDED.assumption_valid,
            evaluated_at = CURRENT_TIMESTAMP;

        SELECT MIN(outcome_value)
        INTO v_minimum
        FROM outcomes
        WHERE distribution_id = v_experiment.distribution_id;

        IF v_minimum >= 0 THEN
            v_markov := calculate_markov(
                v_experiment.distribution_id,
                v_experiment.threshold
            );

            INSERT INTO inequality_evaluations (
                experiment_id,
                inequality,
                calculated_bound,
                exact_probability,
                assumption_valid
            )
            VALUES (
                p_experiment_id,
                'MARKOV',
                v_markov,
                exact_upper_probability(
                    v_experiment.distribution_id,
                    v_experiment.threshold
                ),
                TRUE
            )
            ON CONFLICT (experiment_id, inequality)
            DO UPDATE SET
                calculated_bound = EXCLUDED.calculated_bound,
                exact_probability = EXCLUDED.exact_probability,
                assumption_valid = TRUE,
                evaluated_at = CURRENT_TIMESTAMP;
        END IF;

        SELECT probability_bound, optimal_lambda
        INTO v_chernoff, v_lambda
        FROM calculate_chernoff(
            v_experiment.distribution_id,
            v_experiment.threshold
        );

        INSERT INTO inequality_evaluations (
            experiment_id,
            inequality,
            calculated_bound,
            exact_probability,
            optimal_parameter,
            assumption_valid
        )
        VALUES (
            p_experiment_id,
            'CHERNOFF',
            v_chernoff,
            exact_upper_probability(
                v_experiment.distribution_id,
                v_experiment.threshold
            ),
            v_lambda,
            TRUE
        )
        ON CONFLICT (experiment_id, inequality)
        DO UPDATE SET
            calculated_bound = EXCLUDED.calculated_bound,
            exact_probability = EXCLUDED.exact_probability,
            optimal_parameter = EXCLUDED.optimal_parameter,
            assumption_valid = TRUE,
            evaluated_at = CURRENT_TIMESTAMP;

        UPDATE experiments
        SET status = 'EVALUATED'
        WHERE experiment_id = p_experiment_id;

    EXCEPTION WHEN OTHERS THEN
        UPDATE experiments
        SET status = 'FAILED'
        WHERE experiment_id = p_experiment_id;

        RAISE;
    END;
END;
$$;

-- ============================================================
-- 10. REPORTING VIEWS
-- ============================================================

CREATE OR REPLACE VIEW distribution_statistics AS
SELECT
    d.distribution_id,
    d.distribution_name,
    COUNT(o.outcome_id) AS outcome_count,
    SUM(o.probability) AS total_probability,
    SUM(o.outcome_value * o.probability) AS expected_value,
    SUM(
        o.probability *
        POWER(
            o.outcome_value -
            (
                SELECT SUM(o2.outcome_value * o2.probability)
                FROM outcomes o2
                WHERE o2.distribution_id = d.distribution_id
            ),
            2
        )
    ) AS variance
FROM distributions d
LEFT JOIN outcomes o
    ON o.distribution_id = d.distribution_id
GROUP BY d.distribution_id, d.distribution_name;

CREATE OR REPLACE VIEW evaluation_report AS
SELECT
    e.experiment_id,
    e.experiment_name,
    d.distribution_name,
    e.threshold,
    e.deviation,
    e.status,
    r.inequality,
    r.calculated_bound,
    r.exact_probability,
    r.optimal_parameter,
    r.assumption_valid,
    CASE
        WHEN r.exact_probability IS NULL THEN NULL
        ELSE r.exact_probability <= r.calculated_bound + 1e-10
    END AS bound_validated
FROM experiments e
JOIN distributions d
    ON d.distribution_id = e.distribution_id
LEFT JOIN inequality_evaluations r
    ON r.experiment_id = e.experiment_id;

-- ============================================================
-- 11. SAMPLE DISTRIBUTIONS
-- ============================================================

INSERT INTO distributions (
    distribution_name,
    description
)
VALUES
(
    'operational-risk',
    'Discrete operational incident count distribution.'
),
(
    'binomial-failures',
    'Number of failures in thirty independent Bernoulli trials.'
),
(
    'centered-measurement',
    'A symmetric random variable containing negative and positive values.'
);

INSERT INTO outcomes (
    distribution_id,
    outcome_value,
    probability
)
SELECT
    d.distribution_id,
    sample.value,
    sample.probability
FROM distributions d
CROSS JOIN (
    VALUES
        (0.0, 0.05),
        (1.0, 0.10),
        (2.0, 0.20),
        (3.0, 0.30),
        (4.0, 0.20),
        (5.0, 0.15)
) AS sample(value, probability)
WHERE d.distribution_name = 'operational-risk';

-- Exact binomial probabilities for n = 30, p = 0.5.
WITH RECURSIVE binomial(k, probability) AS (
    SELECT
        0,
        POWER(0.5::DOUBLE PRECISION, 30)

    UNION ALL

    SELECT
        k + 1,
        probability * (31 - k)::DOUBLE PRECISION
            / (k + 1)::DOUBLE PRECISION
    FROM binomial
    WHERE k < 30
)
INSERT INTO outcomes (
    distribution_id,
    outcome_value,
    probability
)
SELECT
    d.distribution_id,
    b.k,
    b.probability
FROM distributions d
CROSS JOIN binomial b
WHERE d.distribution_name = 'binomial-failures';

INSERT INTO outcomes (
    distribution_id,
    outcome_value,
    probability
)
SELECT
    d.distribution_id,
    sample.value,
    sample.probability
FROM distributions d
CROSS JOIN (
    VALUES
        (-2.0, 0.25),
        (0.0, 0.50),
        (2.0, 0.25)
) AS sample(value, probability)
WHERE d.distribution_name = 'centered-measurement';

INSERT INTO convex_functions (
    function_name,
    implementation,
    is_convex,
    description
)
VALUES
(
    'Square',
    'SQUARE',
    TRUE,
    'Convex quadratic function f(x) = x^2.'
),
(
    'Exponential',
    'EXPONENTIAL',
    TRUE,
    'Convex exponential function f(x) = exp(x).'
),
(
    'Absolute',
    'ABSOLUTE',
    TRUE,
    'Convex absolute value function f(x) = |x|.'
);

-- ============================================================
-- 12. VALIDATE DISTRIBUTIONS
-- ============================================================

SELECT validate_distribution(distribution_id)
FROM distributions;

-- ============================================================
-- 13. REGISTER EXPERIMENTS
-- ============================================================

INSERT INTO experiments (
    distribution_id,
    experiment_name,
    threshold,
    deviation
)
SELECT
    distribution_id,
    'Operational risk threshold analysis',
    4.0,
    2.0
FROM distributions
WHERE distribution_name = 'operational-risk';

INSERT INTO experiments (
    distribution_id,
    experiment_name,
    threshold,
    deviation
)
SELECT
    distribution_id,
    'Binomial failure threshold analysis',
    20.0,
    5.0
FROM distributions
WHERE distribution_name = 'binomial-failures';

INSERT INTO experiments (
    distribution_id,
    experiment_name,
    threshold,
    deviation
)
SELECT
    distribution_id,
    'Centered measurement analysis',
    2.0,
    1.0
FROM distributions
WHERE distribution_name = 'centered-measurement';

-- ============================================================
-- 14. EXECUTE EVALUATIONS
-- ============================================================

CALL evaluate_experiment(
    (
        SELECT experiment_id
        FROM experiments
        WHERE experiment_name =
            'Operational risk threshold analysis'
    )
);

CALL evaluate_experiment(
    (
        SELECT experiment_id
        FROM experiments
        WHERE experiment_name =
            'Binomial failure threshold analysis'
    )
);

CALL evaluate_experiment(
    (
        SELECT experiment_id
        FROM experiments
        WHERE experiment_name =
            'Centered measurement analysis'
    )
);

-- ============================================================
-- 15. JENSEN EVALUATION WORKFLOW
-- ============================================================

INSERT INTO jensen_evaluations (
    experiment_id,
    function_id,
    function_at_mean,
    mean_of_function,
    inequality_holds
)
SELECT
    e.experiment_id,
    f.function_id,
    j.function_at_mean,
    j.mean_of_function,
    j.inequality_holds
FROM experiments e
JOIN distributions d
    ON d.distribution_id = e.distribution_id
CROSS JOIN convex_functions f
CROSS JOIN LATERAL calculate_jensen(
    e.distribution_id,
    f.implementation
) j
WHERE f.is_convex = TRUE
  AND f.implementation IN ('SQUARE', 'EXPONENTIAL', 'ABSOLUTE');

-- ============================================================
-- 16. RETRIEVAL AND REPORTING QUERIES
-- ============================================================

-- Distribution-level statistics.
SELECT *
FROM distribution_statistics
ORDER BY distribution_id;

-- Full inequality evaluation report.
SELECT *
FROM evaluation_report
ORDER BY experiment_id, inequality;

-- Exact probability compared with each bound.
SELECT
    experiment_name,
    inequality,
    calculated_bound,
    exact_probability,
    calculated_bound - exact_probability AS safety_gap,
    bound_validated
FROM evaluation_report
WHERE exact_probability IS NOT NULL
ORDER BY experiment_name, inequality;

-- Aggregated evaluation performance.
SELECT
    inequality,
    COUNT(*) AS evaluation_count,
    AVG(calculated_bound) AS average_bound,
    AVG(exact_probability) AS average_exact_probability,
    MIN(calculated_bound) AS minimum_bound,
    MAX(calculated_bound) AS maximum_bound
FROM inequality_evaluations
GROUP BY inequality
ORDER BY inequality;

-- Jensen inequality validation.
SELECT
    e.experiment_name,
    f.function_name,
    j.function_at_mean,
    j.mean_of_function,
    j.inequality_holds
FROM jensen_evaluations j
JOIN experiments e
    ON e.experiment_id = j.experiment_id
JOIN convex_functions f
    ON f.function_id = j.function_id
ORDER BY e.experiment_name, f.function_name;

-- ============================================================
-- 17. CTE-BASED ELIGIBILITY AND FAILURE REPORT
-- ============================================================

WITH evaluated AS (
    SELECT
        e.experiment_id,
        e.experiment_name,
        e.status,
        COUNT(r.evaluation_id) AS evaluation_count,
        BOOL_AND(
            CASE
                WHEN r.evaluation_id IS NULL THEN FALSE
                ELSE r.assumption_valid
            END
        ) AS assumptions_valid
    FROM experiments e
    LEFT JOIN inequality_evaluations r
        ON r.experiment_id = e.experiment_id
    GROUP BY
        e.experiment_id,
        e.experiment_name,
        e.status
)
SELECT
    experiment_name,
    status,
    evaluation_count,
    assumptions_valid,
    CASE
        WHEN status = 'EVALUATED'
             AND evaluation_count >= 2
             AND assumptions_valid
        THEN 'ELIGIBLE'
        ELSE 'REQUIRES_REVIEW'
    END AS evaluation_status
FROM evaluated
ORDER BY experiment_id;

-- ============================================================
-- 18. FAILURE CASE: MARKOV ON A NEGATIVE-VALUED VARIABLE
-- ============================================================

DO $$
DECLARE
    v_distribution_id BIGINT;
BEGIN
    SELECT distribution_id
    INTO v_distribution_id
    FROM distributions
    WHERE distribution_name = 'centered-measurement';

    BEGIN
        PERFORM calculate_markov(v_distribution_id, 2.0);
        RAISE EXCEPTION
            'Expected Markov validation failure did not occur';
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM NOT LIKE
                'Markov inequality requires a nonnegative variable%' THEN
                RAISE;
            END IF;

            RAISE NOTICE
                'Expected validation failure: %', SQLERRM;
    END;
END;
$$;

-- ============================================================
-- 19. TRANSACTION AND DATA-INTEGRITY DEMONSTRATION
-- ============================================================

SAVEPOINT integrity_check;

DO $$
BEGIN
    BEGIN
        INSERT INTO outcomes (
            distribution_id,
            outcome_value,
            probability
        )
        VALUES (
            (
                SELECT distribution_id
                FROM distributions
                WHERE distribution_name = 'operational-risk'
            ),
            99.0,
            1.5
        );

        RAISE EXCEPTION
            'Invalid probability unexpectedly accepted';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'Invalid probability correctly rejected.';
    END;
END;
$$;

ROLLBACK TO SAVEPOINT integrity_check;

COMMIT;
