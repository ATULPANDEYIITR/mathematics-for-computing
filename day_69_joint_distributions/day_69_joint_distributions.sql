/*
 * JOINT DISTRIBUTIONS
 * PostgreSQL 14+
 *
 * Models:
 * 1. Joint probability mass functions.
 * 2. Marginal distributions.
 * 3. Conditional distributions.
 * 4. Expected values.
 * 5. Variances.
 * 6. Covariance.
 * 7. Correlation.
 * 8. Independence testing.
 * 9. Continuous bivariate normal density.
 *
 * Example domain:
 * Employee training level (X) and assessment outcome (Y).
 */

DROP SCHEMA IF EXISTS joint_statistics CASCADE;

CREATE SCHEMA joint_statistics;

SET search_path TO joint_statistics, public;

-- -----------------------------------------------------
-- 1. Domain definitions
-- -----------------------------------------------------

CREATE TABLE variables (
    variable_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    variable_name VARCHAR(100) NOT NULL UNIQUE,
    variable_type VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,

    CONSTRAINT valid_variable_type
        CHECK (variable_type IN ('DISCRETE', 'CONTINUOUS'))
);

CREATE TABLE joint_distributions (
    distribution_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    distribution_name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    distribution_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_distribution_type
        CHECK (distribution_type IN ('PMF', 'PDF'))
);

CREATE TABLE joint_distribution_variables (
    distribution_id BIGINT NOT NULL
        REFERENCES joint_distributions(distribution_id)
        ON DELETE CASCADE,

    variable_id BIGINT NOT NULL
        REFERENCES variables(variable_id),

    variable_position SMALLINT NOT NULL,

    PRIMARY KEY (distribution_id, variable_id),

    CONSTRAINT valid_variable_position
        CHECK (variable_position IN (1, 2)),

    UNIQUE (distribution_id, variable_position)
);

-- -----------------------------------------------------
-- 2. Discrete joint PMF
-- -----------------------------------------------------

CREATE TABLE joint_probability_atoms (
    atom_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    distribution_id BIGINT NOT NULL
        REFERENCES joint_distributions(distribution_id)
        ON DELETE CASCADE,

    x_value NUMERIC(18, 6) NOT NULL,
    y_value NUMERIC(18, 6) NOT NULL,

    probability NUMERIC(18, 12) NOT NULL,

    CONSTRAINT nonnegative_probability
        CHECK (
            probability >= 0
            AND probability <= 1
        ),

    UNIQUE (distribution_id, x_value, y_value)
);

CREATE INDEX idx_joint_atoms_distribution
    ON joint_probability_atoms(distribution_id);

CREATE INDEX idx_joint_atoms_x
    ON joint_probability_atoms(distribution_id, x_value);

CREATE INDEX idx_joint_atoms_y
    ON joint_probability_atoms(distribution_id, y_value);

-- -----------------------------------------------------
-- 3. Continuous bivariate normal parameters
-- -----------------------------------------------------

CREATE TABLE bivariate_normal_parameters (
    distribution_id BIGINT PRIMARY KEY
        REFERENCES joint_distributions(distribution_id)
        ON DELETE CASCADE,

    mean_x NUMERIC(18, 8) NOT NULL,
    mean_y NUMERIC(18, 8) NOT NULL,

    sigma_x NUMERIC(18, 8) NOT NULL,
    sigma_y NUMERIC(18, 8) NOT NULL,

    rho NUMERIC(18, 12) NOT NULL,

    CONSTRAINT positive_standard_deviations
        CHECK (sigma_x > 0 AND sigma_y > 0),

    CONSTRAINT valid_correlation
        CHECK (rho > -1 AND rho < 1)
);

-- -----------------------------------------------------
-- 4. Distribution validation function
-- -----------------------------------------------------

CREATE OR REPLACE FUNCTION validate_joint_pmf(
    p_distribution_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    probability_total NUMERIC;
    atom_count BIGINT;
BEGIN
    SELECT
        COALESCE(SUM(probability), 0),
        COUNT(*)
    INTO probability_total, atom_count
    FROM joint_probability_atoms
    WHERE distribution_id = p_distribution_id;

    IF atom_count = 0 THEN
        RAISE EXCEPTION
            'Joint PMF % contains no outcomes.',
            p_distribution_id;
    END IF;

    IF ABS(probability_total - 1.0) > 0.00000001 THEN
        RAISE EXCEPTION
            'Joint PMF % has probability total % instead of 1.',
            p_distribution_id,
            probability_total;
    END IF;

    RETURN TRUE;
END;
$$;

-- -----------------------------------------------------
-- 5. Marginal distributions
-- -----------------------------------------------------

CREATE OR REPLACE VIEW marginal_x AS
SELECT
    distribution_id,
    x_value,
    SUM(probability) AS marginal_probability
FROM joint_probability_atoms
GROUP BY distribution_id, x_value;

CREATE OR REPLACE VIEW marginal_y AS
SELECT
    distribution_id,
    y_value,
    SUM(probability) AS marginal_probability
FROM joint_probability_atoms
GROUP BY distribution_id, y_value;

-- -----------------------------------------------------
-- 6. Joint and marginal statistical measures
-- -----------------------------------------------------

CREATE OR REPLACE VIEW joint_distribution_metrics AS
WITH moments AS (
    SELECT
        distribution_id,

        SUM(x_value * probability) AS expected_x,
        SUM(y_value * probability) AS expected_y,

        SUM(
            x_value * x_value * probability
        ) AS expected_x_squared,

        SUM(
            y_value * y_value * probability
        ) AS expected_y_squared,

        SUM(
            x_value * y_value * probability
        ) AS expected_xy

    FROM joint_probability_atoms
    GROUP BY distribution_id
),
variances AS (
    SELECT
        distribution_id,
        expected_x,
        expected_y,

        expected_x_squared
            - expected_x * expected_x AS variance_x,

        expected_y_squared
            - expected_y * expected_y AS variance_y,

        expected_xy

    FROM moments
),
covariances AS (
    SELECT
        distribution_id,
        expected_x,
        expected_y,
        GREATEST(variance_x, 0) AS variance_x,
        GREATEST(variance_y, 0) AS variance_y,
        expected_xy,

        expected_xy
            - expected_x * expected_y AS covariance

    FROM variances
)
SELECT
    distribution_id,
    expected_x,
    expected_y,
    variance_x,
    variance_y,
    expected_xy,
    covariance,

    CASE
        WHEN variance_x = 0 OR variance_y = 0
        THEN NULL
        ELSE covariance /
            SQRT(variance_x * variance_y)
    END AS correlation

FROM covariances;

-- -----------------------------------------------------
-- 7. Independence evaluation
-- -----------------------------------------------------

CREATE OR REPLACE FUNCTION check_independence(
    p_distribution_id BIGINT,
    p_tolerance NUMERIC DEFAULT 0.00000001
)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
AS $$
    SELECT NOT EXISTS (
        SELECT 1
        FROM marginal_x mx
        CROSS JOIN marginal_y my

        WHERE mx.distribution_id = p_distribution_id
          AND my.distribution_id = p_distribution_id

          AND ABS(
              COALESCE(
                  (
                      SELECT atom.probability
                      FROM joint_probability_atoms atom
                      WHERE atom.distribution_id =
                            p_distribution_id
                        AND atom.x_value = mx.x_value
                        AND atom.y_value = my.y_value
                  ),
                  0
              )
              -
              (
                  mx.marginal_probability *
                  my.marginal_probability
              )
          ) > p_tolerance
    );
$$;

-- -----------------------------------------------------
-- 8. Conditional distribution
-- -----------------------------------------------------

CREATE OR REPLACE FUNCTION conditional_y_given_x(
    p_distribution_id BIGINT,
    p_x_value NUMERIC
)
RETURNS TABLE (
    y_value NUMERIC,
    conditional_probability NUMERIC
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    marginal_probability NUMERIC;
BEGIN
    SELECT mx.marginal_probability
    INTO marginal_probability
    FROM marginal_x mx
    WHERE mx.distribution_id = p_distribution_id
      AND mx.x_value = p_x_value;

    IF marginal_probability IS NULL
       OR marginal_probability = 0 THEN
        RAISE EXCEPTION
            'Conditional distribution undefined for X=%.',
            p_x_value;
    END IF;

    RETURN QUERY
    SELECT
        atom.y_value,
        SUM(atom.probability) / marginal_probability
    FROM joint_probability_atoms atom
    WHERE atom.distribution_id = p_distribution_id
      AND atom.x_value = p_x_value
    GROUP BY atom.y_value
    ORDER BY atom.y_value;
END;
$$;

CREATE OR REPLACE FUNCTION conditional_x_given_y(
    p_distribution_id BIGINT,
    p_y_value NUMERIC
)
RETURNS TABLE (
    x_value NUMERIC,
    conditional_probability NUMERIC
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    marginal_probability NUMERIC;
BEGIN
    SELECT my.marginal_probability
    INTO marginal_probability
    FROM marginal_y my
    WHERE my.distribution_id = p_distribution_id
      AND my.y_value = p_y_value;

    IF marginal_probability IS NULL
       OR marginal_probability = 0 THEN
        RAISE EXCEPTION
            'Conditional distribution undefined for Y=%.',
            p_y_value;
    END IF;

    RETURN QUERY
    SELECT
        atom.x_value,
        SUM(atom.probability) / marginal_probability
    FROM joint_probability_atoms atom
    WHERE atom.distribution_id = p_distribution_id
      AND atom.y_value = p_y_value
    GROUP BY atom.x_value
    ORDER BY atom.x_value;
END;
$$;

-- -----------------------------------------------------
-- 9. Bivariate normal PDF function
-- -----------------------------------------------------

CREATE OR REPLACE FUNCTION bivariate_normal_pdf(
    p_distribution_id BIGINT,
    p_x NUMERIC,
    p_y NUMERIC
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    parameters RECORD;

    zx DOUBLE PRECISION;
    zy DOUBLE PRECISION;

    exponent_value DOUBLE PRECISION;
    denominator DOUBLE PRECISION;
BEGIN
    IF p_x IS NULL OR p_y IS NULL THEN
        RAISE EXCEPTION 'PDF inputs cannot be NULL.';
    END IF;

    SELECT *
    INTO parameters
    FROM bivariate_normal_parameters
    WHERE distribution_id = p_distribution_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Bivariate normal parameters not found for %.',
            p_distribution_id;
    END IF;

    zx := (
        p_x - parameters.mean_x
    ) / parameters.sigma_x;

    zy := (
        p_y - parameters.mean_y
    ) / parameters.sigma_y;

    exponent_value := -(
        POWER(zx, 2)
        - 2 * parameters.rho * zx * zy
        + POWER(zy, 2)
    ) / (
        2 * (1 - POWER(parameters.rho, 2))
    );

    denominator :=
        2 * PI()
        * parameters.sigma_x
        * parameters.sigma_y
        * SQRT(1 - POWER(parameters.rho, 2));

    RETURN EXP(exponent_value) / denominator;
END;
$$;

-- -----------------------------------------------------
-- 10. Example distributions
-- -----------------------------------------------------

INSERT INTO variables (
    variable_name,
    variable_type,
    description
)
VALUES
(
    'Training Level',
    'DISCRETE',
    'Employee training level represented by integer categories.'
),
(
    'Assessment Result',
    'DISCRETE',
    'Assessment outcome represented by integer categories.'
),
(
    'Study Hours',
    'CONTINUOUS',
    'Continuous study duration.'
),
(
    'Assessment Score',
    'CONTINUOUS',
    'Continuous assessment score.'
);

INSERT INTO joint_distributions (
    distribution_name,
    description,
    distribution_type
)
VALUES
(
    'employee_training_assessment',
    'Joint PMF of employee training level and assessment result.',
    'PMF'
),
(
    'study_hours_assessment_score',
    'Bivariate normal model for study hours and assessment score.',
    'PDF'
);

INSERT INTO joint_distribution_variables (
    distribution_id,
    variable_id,
    variable_position
)
SELECT
    d.distribution_id,
    v.variable_id,
    CASE
        WHEN v.variable_name IN (
            'Training Level',
            'Study Hours'
        ) THEN 1
        ELSE 2
    END
FROM joint_distributions d
CROSS JOIN variables v
WHERE
    (
        d.distribution_name = 'employee_training_assessment'
        AND v.variable_name IN (
            'Training Level',
            'Assessment Result'
        )
    )
    OR
    (
        d.distribution_name = 'study_hours_assessment_score'
        AND v.variable_name IN (
            'Study Hours',
            'Assessment Score'
        )
    );

-- Valid discrete joint PMF.
INSERT INTO joint_probability_atoms (
    distribution_id,
    x_value,
    y_value,
    probability
)
SELECT
    d.distribution_id,
    sample.x_value,
    sample.y_value,
    sample.probability
FROM joint_distributions d
CROSS JOIN (
    VALUES
        (0::NUMERIC, 0::NUMERIC, 0.10::NUMERIC),
        (0::NUMERIC, 1::NUMERIC, 0.15::NUMERIC),
        (1::NUMERIC, 0::NUMERIC, 0.20::NUMERIC),
        (1::NUMERIC, 1::NUMERIC, 0.30::NUMERIC),
        (2::NUMERIC, 0::NUMERIC, 0.05::NUMERIC),
        (2::NUMERIC, 1::NUMERIC, 0.20::NUMERIC)
) AS sample(x_value, y_value, probability)
WHERE d.distribution_name =
    'employee_training_assessment';

-- Continuous distribution parameters.
INSERT INTO bivariate_normal_parameters (
    distribution_id,
    mean_x,
    mean_y,
    sigma_x,
    sigma_y,
    rho
)
SELECT
    distribution_id,
    70,
    75,
    10,
    12,
    0.65
FROM joint_distributions
WHERE distribution_name =
    'study_hours_assessment_score';

-- -----------------------------------------------------
-- 11. Validate the PMF
-- -----------------------------------------------------

SELECT validate_joint_pmf(distribution_id)
FROM joint_distributions
WHERE distribution_name =
    'employee_training_assessment';

-- -----------------------------------------------------
-- 12. Joint probability retrieval
-- -----------------------------------------------------

SELECT
    distribution_id,
    x_value,
    y_value,
    probability
FROM joint_probability_atoms
WHERE distribution_id = (
    SELECT distribution_id
    FROM joint_distributions
    WHERE distribution_name =
        'employee_training_assessment'
)
ORDER BY x_value, y_value;

-- -----------------------------------------------------
-- 13. Marginal probability reports
-- -----------------------------------------------------

SELECT *
FROM marginal_x
WHERE distribution_id = (
    SELECT distribution_id
    FROM joint_distributions
    WHERE distribution_name =
        'employee_training_assessment'
)
ORDER BY x_value;

SELECT *
FROM marginal_y
WHERE distribution_id = (
    SELECT distribution_id
    FROM joint_distributions
    WHERE distribution_name =
        'employee_training_assessment'
)
ORDER BY y_value;

-- -----------------------------------------------------
-- 14. Conditional probability reports
-- -----------------------------------------------------

SELECT *
FROM conditional_y_given_x(
    (
        SELECT distribution_id
        FROM joint_distributions
        WHERE distribution_name =
            'employee_training_assessment'
    ),
    1
);

SELECT *
FROM conditional_x_given_y(
    (
        SELECT distribution_id
        FROM joint_distributions
        WHERE distribution_name =
            'employee_training_assessment'
    ),
    1
);

-- -----------------------------------------------------
-- 15. Statistical aggregation
-- -----------------------------------------------------

SELECT
    expected_x,
    expected_y,
    variance_x,
    variance_y,
    expected_xy,
    covariance,
    correlation
FROM joint_distribution_metrics
WHERE distribution_id = (
    SELECT distribution_id
    FROM joint_distributions
    WHERE distribution_name =
        'employee_training_assessment'
);

-- -----------------------------------------------------
-- 16. Independence evaluation
-- -----------------------------------------------------

SELECT
    d.distribution_name,
    check_independence(d.distribution_id) AS is_independent
FROM joint_distributions d
WHERE d.distribution_type = 'PMF';

-- -----------------------------------------------------
-- 17. Continuous density evaluation
-- -----------------------------------------------------

SELECT bivariate_normal_pdf(
    (
        SELECT distribution_id
        FROM joint_distributions
        WHERE distribution_name =
            'study_hours_assessment_score'
    ),
    70,
    75
) AS joint_pdf_at_70_75;

-- -----------------------------------------------------
-- 18. Transaction demonstration
-- -----------------------------------------------------

BEGIN;

-- Create an independent test distribution.
INSERT INTO joint_distributions (
    distribution_name,
    description,
    distribution_type
)
VALUES (
    'independent_test_distribution',
    'Independent binary random variables.',
    'PMF'
);

INSERT INTO joint_probability_atoms (
    distribution_id,
    x_value,
    y_value,
    probability
)
SELECT
    distribution_id,
    sample.x_value,
    sample.y_value,
    sample.probability
FROM joint_distributions d
CROSS JOIN (
    VALUES
        (0::NUMERIC, 0::NUMERIC, 0.25::NUMERIC),
        (0::NUMERIC, 1::NUMERIC, 0.25::NUMERIC),
        (1::NUMERIC, 0::NUMERIC, 0.25::NUMERIC),
        (1::NUMERIC, 1::NUMERIC, 0.25::NUMERIC)
) AS sample(x_value, y_value, probability)
WHERE d.distribution_name =
    'independent_test_distribution';

SELECT validate_joint_pmf(distribution_id)
FROM joint_distributions
WHERE distribution_name =
    'independent_test_distribution';

SELECT
    d.distribution_name,
    check_independence(d.distribution_id) AS is_independent,
    m.covariance,
    m.correlation
FROM joint_distributions d
JOIN joint_distribution_metrics m
    ON m.distribution_id = d.distribution_id
WHERE d.distribution_name =
    'independent_test_distribution';

COMMIT;

-- -----------------------------------------------------
-- 19. Validation failure demonstration
-- -----------------------------------------------------

-- This intentionally demonstrates an invalid probability.
-- The constraint rejects the operation.

DO $$
BEGIN
    BEGIN
        INSERT INTO joint_probability_atoms (
            distribution_id,
            x_value,
            y_value,
            probability
        )
        SELECT
            distribution_id,
            99,
            99,
            1.5
        FROM joint_distributions
        WHERE distribution_name =
            'employee_training_assessment';

        RAISE EXCEPTION
            'Invalid probability unexpectedly accepted.';

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'Expected validation failure: probability exceeds 1.';
    END;
END;
$$;

-- -----------------------------------------------------
-- 20. Distribution reporting
-- -----------------------------------------------------

SELECT
    d.distribution_name,
    d.distribution_type,
    COUNT(a.atom_id) AS outcome_count,
    COALESCE(SUM(a.probability), 0) AS probability_total
FROM joint_distributions d
LEFT JOIN joint_probability_atoms a
    ON a.distribution_id = d.distribution_id
GROUP BY
    d.distribution_id,
    d.distribution_name,
    d.distribution_type
ORDER BY d.distribution_name;

-- -----------------------------------------------------
-- 21. Database integrity checks
-- -----------------------------------------------------

SELECT
    distribution_id,
    SUM(probability) AS probability_total,
    COUNT(*) AS outcome_count,
    BOOL_AND(probability >= 0 AND probability <= 1)
        AS valid_individual_probabilities
FROM joint_probability_atoms
GROUP BY distribution_id;

SELECT
    distribution_id,
    expected_x,
    expected_y,
    variance_x,
    variance_y,
    covariance,
    correlation
FROM joint_distribution_metrics
ORDER BY distribution_id;
