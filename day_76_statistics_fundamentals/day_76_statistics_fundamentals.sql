/*
============================================================
STATISTICS FUNDAMENTALS
Population, Sample, Parameters, Statistics and Sampling
PostgreSQL 14+

Database capabilities:
- Population and sampling-frame management
- Stratified population organization
- Population parameters
- Sample selection and observations
- Simple random sampling
- Systematic sampling
- Stratified sample allocation
- Sample statistics
- Standard errors
- Confidence intervals
- Sample-size determination
- Sampling workflow and audit history
- Constraints, functions, procedures, views and triggers
============================================================
*/

BEGIN;

CREATE SCHEMA IF NOT EXISTS statistics_lab;

SET search_path TO statistics_lab, public;

-- =========================================================
-- 1. ENUMERATIONS
-- =========================================================

CREATE TYPE sampling_method AS ENUM (
    'SIMPLE_RANDOM',
    'SYSTEMATIC',
    'STRATIFIED'
);

CREATE TYPE sampling_status AS ENUM (
    'CREATED',
    'VALIDATED',
    'SELECTED',
    'ANALYZED',
    'FAILED'
);

-- =========================================================
-- 2. POPULATION AND SAMPLING FRAME
-- =========================================================

CREATE TABLE population (
    population_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    population_name VARCHAR(150) NOT NULL UNIQUE,

    description TEXT,

    population_type VARCHAR(50) NOT NULL,

    reference_date DATE NOT NULL DEFAULT CURRENT_DATE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT population_name_not_blank
        CHECK (length(trim(population_name)) > 0)
);

CREATE TABLE population_strata (
    stratum_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    population_id BIGINT NOT NULL
        REFERENCES population(population_id)
        ON DELETE CASCADE,

    stratum_name VARCHAR(100) NOT NULL,

    description TEXT,

    UNIQUE(population_id, stratum_name),

    UNIQUE(population_id, stratum_id)
);

CREATE TABLE population_units (
    unit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    population_id BIGINT NOT NULL
        REFERENCES population(population_id)
        ON DELETE CASCADE,

    external_id VARCHAR(100) NOT NULL,

    stratum_id BIGINT NOT NULL,

    cluster_id VARCHAR(100) NOT NULL,

    observed_value NUMERIC(18, 4) NOT NULL,

    is_eligible BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_population_unit
        UNIQUE(population_id, external_id),

    CONSTRAINT unit_value_finite_range
        CHECK (
            observed_value BETWEEN -999999999999
            AND 999999999999
        ),

    CONSTRAINT unit_cluster_not_blank
        CHECK (length(trim(cluster_id)) > 0),

    FOREIGN KEY(population_id, stratum_id)
        REFERENCES population_strata(population_id, stratum_id)
);

CREATE INDEX idx_population_units_population
    ON population_units(population_id);

CREATE INDEX idx_population_units_stratum
    ON population_units(population_id, stratum_id);

CREATE INDEX idx_population_units_cluster
    ON population_units(population_id, cluster_id);

CREATE INDEX idx_population_units_eligible
    ON population_units(population_id, unit_id)
    WHERE is_eligible = TRUE;

-- =========================================================
-- 3. SAMPLING PROJECTS
-- =========================================================

CREATE TABLE sampling_projects (
    project_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    population_id BIGINT NOT NULL
        REFERENCES population(population_id),

    project_name VARCHAR(150) NOT NULL,

    method sampling_method NOT NULL,

    requested_sample_size INTEGER NOT NULL,

    random_seed BIGINT NOT NULL DEFAULT 42,

    confidence_level NUMERIC(5, 4) NOT NULL DEFAULT 0.9500,

    status sampling_status NOT NULL DEFAULT 'CREATED',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMPTZ,

    CONSTRAINT valid_sample_size
        CHECK (requested_sample_size > 0),

    CONSTRAINT valid_confidence_level
        CHECK (confidence_level > 0 AND confidence_level < 1),

    CONSTRAINT unique_project_name
        UNIQUE(project_name)
);

CREATE INDEX idx_sampling_projects_status
    ON sampling_projects(status, created_at DESC);

-- =========================================================
-- 4. SELECTED SAMPLE UNITS
-- =========================================================

CREATE TABLE sample_units (
    sample_unit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    project_id BIGINT NOT NULL
        REFERENCES sampling_projects(project_id)
        ON DELETE CASCADE,

    population_unit_id BIGINT NOT NULL
        REFERENCES population_units(unit_id),

    inclusion_probability NUMERIC(12, 10),

    selection_order INTEGER NOT NULL,

    selected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(project_id, population_unit_id),

    UNIQUE(project_id, selection_order),

    CHECK (
        inclusion_probability IS NULL
        OR inclusion_probability > 0
        AND inclusion_probability <= 1
    ),

    CHECK (selection_order > 0)
);

CREATE INDEX idx_sample_units_project
    ON sample_units(project_id);

-- =========================================================
-- 5. SAMPLE STATISTICAL RESULTS
-- =========================================================

CREATE TABLE sample_analysis (
    analysis_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    project_id BIGINT NOT NULL UNIQUE
        REFERENCES sampling_projects(project_id)
        ON DELETE CASCADE,

    sample_size INTEGER NOT NULL,

    sample_mean NUMERIC(18, 6) NOT NULL,

    sample_variance NUMERIC(18, 6) NOT NULL,

    sample_standard_deviation NUMERIC(18, 6) NOT NULL,

    standard_error NUMERIC(18, 6),

    confidence_lower NUMERIC(18, 6),

    confidence_upper NUMERIC(18, 6),

    analyzed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (sample_size > 0),

    CHECK (sample_variance >= 0),

    CHECK (sample_standard_deviation >= 0),

    CHECK (
        standard_error IS NULL OR standard_error >= 0
    ),

    CHECK (
        confidence_lower IS NULL
        OR confidence_upper IS NULL
        OR confidence_lower <= confidence_upper
    )
);

-- =========================================================
-- 6. WORKFLOW AUDIT
-- =========================================================

CREATE TABLE sampling_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    project_id BIGINT NOT NULL
        REFERENCES sampling_projects(project_id)
        ON DELETE CASCADE,

    previous_status sampling_status,

    new_status sampling_status NOT NULL,

    event_description TEXT NOT NULL,

    event_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sampling_audit_project
    ON sampling_audit(project_id, event_time DESC);

-- =========================================================
-- 7. POPULATION VALIDATION
-- =========================================================

CREATE FUNCTION validate_population()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_population_size BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_population_size
    FROM population_units
    WHERE population_id = NEW.population_id
      AND is_eligible = TRUE;

    IF v_population_size = 0 THEN
        RAISE EXCEPTION
            'Population % has no eligible units.',
            NEW.population_id;
    END IF;

    RETURN NEW;
END;
$$;

-- =========================================================
-- 8. SAMPLE INTEGRITY TRIGGER
-- =========================================================

CREATE FUNCTION validate_sample_unit()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_project_population BIGINT;
    v_unit_population BIGINT;
    v_eligible BOOLEAN;
BEGIN
    SELECT population_id
    INTO v_project_population
    FROM sampling_projects
    WHERE project_id = NEW.project_id;

    SELECT population_id, is_eligible
    INTO v_unit_population, v_eligible
    FROM population_units
    WHERE unit_id = NEW.population_unit_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Population unit does not exist.';
    END IF;

    IF v_project_population <> v_unit_population THEN
        RAISE EXCEPTION
            'Sample unit belongs to another population.';
    END IF;

    IF NOT v_eligible THEN
        RAISE EXCEPTION
            'Ineligible population units cannot be sampled.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_sample_unit
BEFORE INSERT OR UPDATE ON sample_units
FOR EACH ROW
EXECUTE FUNCTION validate_sample_unit();

-- =========================================================
-- 9. PROJECT STATE TRANSITION AUDIT
-- =========================================================

CREATE FUNCTION audit_sampling_status()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status IS DISTINCT FROM OLD.status THEN

        INSERT INTO sampling_audit (
            project_id,
            previous_status,
            new_status,
            event_description
        )
        VALUES (
            NEW.project_id,
            OLD.status,
            NEW.status,
            'Sampling workflow status changed'
        );

    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_audit_sampling_status
AFTER UPDATE OF status ON sampling_projects
FOR EACH ROW
EXECUTE FUNCTION audit_sampling_status();

-- =========================================================
-- 10. POPULATION PARAMETERS FUNCTION
-- =========================================================

CREATE FUNCTION calculate_population_parameters(
    p_population_id BIGINT
)
RETURNS TABLE (
    population_size BIGINT,
    population_mean NUMERIC,
    population_variance NUMERIC,
    population_std NUMERIC,
    population_total NUMERIC
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT,
        AVG(observed_value),
        VAR_POP(observed_value),
        STDDEV_POP(observed_value),
        SUM(observed_value)
    FROM population_units
    WHERE population_id = p_population_id
      AND is_eligible = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Population not found.';
    END IF;
END;
$$;

-- =========================================================
-- 11. SAMPLE STATISTICS FUNCTION
-- =========================================================

CREATE FUNCTION calculate_sample_statistics(
    p_project_id BIGINT
)
RETURNS TABLE (
    sample_size BIGINT,
    sample_mean NUMERIC,
    sample_variance NUMERIC,
    sample_std NUMERIC,
    sample_min NUMERIC,
    sample_max NUMERIC
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT,
        AVG(pu.observed_value),
        VAR_SAMP(pu.observed_value),
        STDDEV_SAMP(pu.observed_value),
        MIN(pu.observed_value),
        MAX(pu.observed_value)
    FROM sample_units su
    JOIN population_units pu
        ON pu.unit_id = su.population_unit_id
    WHERE su.project_id = p_project_id;
END;
$$;

-- =========================================================
-- 12. SAMPLE STANDARD ERROR
-- =========================================================

CREATE FUNCTION calculate_standard_error(
    p_project_id BIGINT
)
RETURNS NUMERIC
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_n BIGINT;
    v_N BIGINT;
    v_std NUMERIC;
BEGIN
    SELECT
        COUNT(*),
        MAX(sp.requested_sample_size)
    INTO v_n, v_N
    FROM sample_units su
    JOIN sampling_projects sp
        ON sp.project_id = su.project_id
    WHERE su.project_id = p_project_id;

    IF v_n < 2 THEN
        RAISE EXCEPTION
            'At least two sampled units are required.';
    END IF;

    SELECT
        STDDEV_SAMP(pu.observed_value)
    INTO v_std
    FROM sample_units su
    JOIN population_units pu
        ON pu.unit_id = su.population_unit_id
    WHERE su.project_id = p_project_id;

    RETURN v_std / SQRT(v_n::NUMERIC);
END;
$$;

-- =========================================================
-- 13. SAMPLE SELECTION PROCEDURE
-- =========================================================

CREATE PROCEDURE select_simple_random_sample(
    p_project_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_population_id BIGINT;
    v_requested INTEGER;
    v_seed BIGINT;
    v_population_size BIGINT;
BEGIN
    SELECT population_id, requested_sample_size, random_seed
    INTO v_population_id, v_requested, v_seed
    FROM sampling_projects
    WHERE project_id = p_project_id
      AND method = 'SIMPLE_RANDOM'
      AND status IN ('CREATED', 'VALIDATED');

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Project is missing, invalid or already processed.';
    END IF;

    SELECT COUNT(*)
    INTO v_population_size
    FROM population_units
    WHERE population_id = v_population_id
      AND is_eligible = TRUE;

    IF v_requested > v_population_size THEN
        RAISE EXCEPTION
            'Requested sample exceeds eligible population.';
    END IF;

    -- Seed is session-local. This provides reproducibility within
    -- the PostgreSQL random-number implementation.
    PERFORM setseed(
        ((v_seed % 1000000)::DOUBLE PRECISION) / 1000000.0
    );

    INSERT INTO sample_units (
        project_id,
        population_unit_id,
        selection_order,
        inclusion_probability
    )
    SELECT
        p_project_id,
        selected.unit_id,
        ROW_NUMBER() OVER (ORDER BY selected.random_order)::INTEGER,
        v_requested::NUMERIC / v_population_size
    FROM (
        SELECT
            unit_id,
            RANDOM() AS random_order
        FROM population_units
        WHERE population_id = v_population_id
          AND is_eligible = TRUE
        ORDER BY random_order
        LIMIT v_requested
    ) selected;

    UPDATE sampling_projects
    SET status = 'SELECTED'
    WHERE project_id = p_project_id;
END;
$$;

-- =========================================================
-- 14. SYSTEMATIC SAMPLING PROCEDURE
-- =========================================================

CREATE PROCEDURE select_systematic_sample(
    p_project_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_population_id BIGINT;
    v_requested INTEGER;
    v_population_size BIGINT;
    v_interval NUMERIC;
    v_start NUMERIC;
BEGIN
    SELECT population_id, requested_sample_size
    INTO v_population_id, v_requested
    FROM sampling_projects
    WHERE project_id = p_project_id
      AND method = 'SYSTEMATIC'
      AND status IN ('CREATED', 'VALIDATED');

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Invalid systematic sampling project.';
    END IF;

    SELECT COUNT(*)
    INTO v_population_size
    FROM population_units
    WHERE population_id = v_population_id
      AND is_eligible = TRUE;

    IF v_requested > v_population_size THEN
        RAISE EXCEPTION 'Sample size exceeds population.';
    END IF;

    v_interval := v_population_size::NUMERIC / v_requested;

    v_start := 1 + RANDOM() * v_interval;

    WITH ordered_units AS (
        SELECT
            unit_id,
            ROW_NUMBER() OVER (ORDER BY unit_id) AS rn
        FROM population_units
        WHERE population_id = v_population_id
          AND is_eligible = TRUE
    ),
    selected AS (
        SELECT
            unit_id,
            FLOOR(
                v_start + (g.i - 1) * v_interval
            ) AS position
        FROM GENERATE_SERIES(1, v_requested) AS g(i)
    )
    INSERT INTO sample_units (
        project_id,
        population_unit_id,
        selection_order,
        inclusion_probability
    )
    SELECT
        p_project_id,
        ou.unit_id,
        ROW_NUMBER() OVER (ORDER BY s.position)::INTEGER,
        v_requested::NUMERIC / v_population_size
    FROM selected s
    JOIN ordered_units ou
        ON ou.rn = LEAST(s.position, v_population_size);

    UPDATE sampling_projects
    SET status = 'SELECTED'
    WHERE project_id = p_project_id;
END;
$$;

-- =========================================================
-- 15. STRATIFIED SAMPLE ALLOCATION
-- =========================================================

CREATE PROCEDURE select_stratified_sample(
    p_project_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_population_id BIGINT;
    v_requested INTEGER;
    v_population_size BIGINT;
    v_strata_count INTEGER;
BEGIN
    SELECT population_id, requested_sample_size
    INTO v_population_id, v_requested
    FROM sampling_projects
    WHERE project_id = p_project_id
      AND method = 'STRATIFIED'
      AND status IN ('CREATED', 'VALIDATED');

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Invalid stratified sampling project.';
    END IF;

    SELECT COUNT(*)
    INTO v_population_size
    FROM population_units
    WHERE population_id = v_population_id
      AND is_eligible = TRUE;

    SELECT COUNT(DISTINCT stratum_id)
    INTO v_strata_count
    FROM population_units
    WHERE population_id = v_population_id
      AND is_eligible = TRUE;

    IF v_requested > v_population_size
       OR v_requested < v_strata_count THEN
        RAISE EXCEPTION
            'Sample size must cover every stratum and not exceed N.';
    END IF;

    WITH stratum_sizes AS (
        SELECT
            stratum_id,
            COUNT(*)::INTEGER AS stratum_size,
            (v_requested::NUMERIC * COUNT(*)
                / v_population_size) AS exact_allocation
        FROM population_units
        WHERE population_id = v_population_id
          AND is_eligible = TRUE
        GROUP BY stratum_id
    ),
    initial_allocation AS (
        SELECT
            stratum_id,
            stratum_size,
            FLOOR(exact_allocation)::INTEGER AS base_count,
            exact_allocation - FLOOR(exact_allocation) AS remainder
        FROM stratum_sizes
    ),
    ranked_allocation AS (
        SELECT
            *,
            SUM(base_count) OVER () AS allocated,
            ROW_NUMBER() OVER (
                ORDER BY remainder DESC, stratum_id
            ) AS remainder_rank
        FROM initial_allocation
    ),
    final_allocation AS (
        SELECT
            stratum_id,
            LEAST(
                stratum_size,
                base_count +
                CASE
                    WHEN remainder_rank <=
                        v_requested - allocated
                    THEN 1
                    ELSE 0
                END
            ) AS sample_count
        FROM ranked_allocation
    ),
    ranked_units AS (
        SELECT
            pu.unit_id,
            pu.stratum_id,
            ROW_NUMBER() OVER (
                PARTITION BY pu.stratum_id
                ORDER BY RANDOM()
            ) AS row_number_in_stratum
        FROM population_units pu
        WHERE pu.population_id = v_population_id
          AND pu.is_eligible = TRUE
    )
    INSERT INTO sample_units (
        project_id,
        population_unit_id,
        selection_order,
        inclusion_probability
    )
    SELECT
        p_project_id,
        ru.unit_id,
        ROW_NUMBER() OVER (
            ORDER BY ru.stratum_id, ru.row_number_in_stratum
        )::INTEGER,
        fa.sample_count::NUMERIC /
            NULLIF(ss.stratum_size, 0)
    FROM ranked_units ru
    JOIN final_allocation fa
        ON fa.stratum_id = ru.stratum_id
    JOIN stratum_sizes ss
        ON ss.stratum_id = ru.stratum_id
    WHERE ru.row_number_in_stratum <= fa.sample_count;

    IF (
        SELECT COUNT(*)
        FROM sample_units
        WHERE project_id = p_project_id
    ) <> v_requested THEN
        RAISE EXCEPTION
            'Stratified allocation did not produce requested sample size.';
    END IF;

    UPDATE sampling_projects
    SET status = 'SELECTED'
    WHERE project_id = p_project_id;
END;
$$;

-- =========================================================
-- 16. ANALYSIS PROCEDURE
-- =========================================================

CREATE PROCEDURE analyze_sample(
    p_project_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_n BIGINT;
    v_N BIGINT;
    v_mean NUMERIC;
    v_variance NUMERIC;
    v_std NUMERIC;
    v_se NUMERIC;
    v_z NUMERIC;
    v_confidence NUMERIC;
    v_margin NUMERIC;
BEGIN
    SELECT
        sp.confidence_level,
        COUNT(su.sample_unit_id),
        COUNT(pu.unit_id)
    INTO
        v_confidence,
        v_n,
        v_N
    FROM sampling_projects sp
    LEFT JOIN sample_units su
        ON su.project_id = sp.project_id
    LEFT JOIN population_units pu
        ON pu.unit_id = su.population_unit_id
    WHERE sp.project_id = p_project_id
      AND sp.status = 'SELECTED'
    GROUP BY sp.confidence_level;

    IF NOT FOUND OR v_n < 2 THEN
        RAISE EXCEPTION
            'Selected sample requires at least two observations.';
    END IF;

    SELECT
        AVG(pu.observed_value),
        VAR_SAMP(pu.observed_value),
        STDDEV_SAMP(pu.observed_value)
    INTO v_mean, v_variance, v_std
    FROM sample_units su
    JOIN population_units pu
        ON pu.unit_id = su.population_unit_id
    WHERE su.project_id = p_project_id;

    v_se := v_std / SQRT(v_n::NUMERIC);

    IF v_n < v_N THEN
        v_se := v_se * SQRT(
            (v_N - v_n)::NUMERIC / (v_N - 1)
        );
    END IF;

    v_z := CASE v_confidence
        WHEN 0.90 THEN 1.645
        WHEN 0.95 THEN 1.960
        WHEN 0.99 THEN 2.576
        ELSE 1.960
    END;

    v_margin := v_z * v_se;

    INSERT INTO sample_analysis (
        project_id,
        sample_size,
        sample_mean,
        sample_variance,
        sample_standard_deviation,
        standard_error,
        confidence_lower,
        confidence_upper
    )
    VALUES (
        p_project_id,
        v_n,
        v_mean,
        v_variance,
        v_std,
        v_se,
        v_mean - v_margin,
        v_mean + v_margin
    )
    ON CONFLICT (project_id)
    DO UPDATE SET
        sample_size = EXCLUDED.sample_size,
        sample_mean = EXCLUDED.sample_mean,
        sample_variance = EXCLUDED.sample_variance,
        sample_standard_deviation =
            EXCLUDED.sample_standard_deviation,
        standard_error = EXCLUDED.standard_error,
        confidence_lower = EXCLUDED.confidence_lower,
        confidence_upper = EXCLUDED.confidence_upper,
        analyzed_at = CURRENT_TIMESTAMP;

    UPDATE sampling_projects
    SET
        status = 'ANALYZED',
        completed_at = CURRENT_TIMESTAMP
    WHERE project_id = p_project_id;
END;
$$;

-- =========================================================
-- 17. SAMPLE-SIZE DETERMINATION
-- =========================================================

CREATE FUNCTION required_sample_size(
    p_population_std NUMERIC,
    p_margin NUMERIC,
    p_z NUMERIC,
    p_population_size INTEGER
)
RETURNS INTEGER
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_n0 NUMERIC;
    v_adjusted NUMERIC;
BEGIN
    IF p_population_std < 0
       OR p_margin <= 0
       OR p_z <= 0
       OR p_population_size <= 0 THEN
        RAISE EXCEPTION 'Invalid sample-size parameters.';
    END IF;

    IF p_population_std = 0 THEN
        RETURN 1;
    END IF;

    v_n0 := POWER(
        p_z * p_population_std / p_margin,
        2
    );

    IF v_n0 >= p_population_size THEN
        RETURN p_population_size;
    END IF;

    v_adjusted := v_n0 / (
        1 + (v_n0 - 1) / p_population_size
    );

    RETURN CEIL(v_adjusted)::INTEGER;
END;
$$;

-- =========================================================
-- 18. REPORTING VIEWS
-- =========================================================

CREATE VIEW population_summary AS
SELECT
    p.population_id,
    p.population_name,
    COUNT(pu.unit_id) AS eligible_population_size,
    AVG(pu.observed_value) AS population_mean,
    VAR_POP(pu.observed_value) AS population_variance,
    STDDEV_POP(pu.observed_value) AS population_std,
    MIN(pu.observed_value) AS minimum_value,
    MAX(pu.observed_value) AS maximum_value
FROM population p
LEFT JOIN population_units pu
    ON pu.population_id = p.population_id
   AND pu.is_eligible = TRUE
GROUP BY p.population_id, p.population_name;

CREATE VIEW sampling_project_report AS
SELECT
    sp.project_id,
    sp.project_name,
    p.population_name,
    sp.method,
    sp.status,
    sp.requested_sample_size,
    COUNT(su.sample_unit_id) AS actual_sample_size,
    sa.sample_mean,
    sa.sample_variance,
    sa.standard_error,
    sa.confidence_lower,
    sa.confidence_upper
FROM sampling_projects sp
JOIN population p
    ON p.population_id = sp.population_id
LEFT JOIN sample_units su
    ON su.project_id = sp.project_id
LEFT JOIN sample_analysis sa
    ON sa.project_id = sp.project_id
GROUP BY
    sp.project_id,
    sp.project_name,
    p.population_name,
    sp.method,
    sp.status,
    sp.requested_sample_size,
    sa.sample_mean,
    sa.sample_variance,
    sa.standard_error,
    sa.confidence_lower,
    sa.confidence_upper;

-- =========================================================
-- 19. SAMPLE ELIGIBILITY QUERY
-- =========================================================

CREATE VIEW sampling_eligibility AS
SELECT
    sp.project_id,
    sp.project_name,
    COUNT(pu.unit_id) AS eligible_units,
    sp.requested_sample_size,
    CASE
        WHEN COUNT(pu.unit_id) >= sp.requested_sample_size
        THEN TRUE
        ELSE FALSE
    END AS population_sufficient,
    CASE
        WHEN sp.method = 'STRATIFIED'
         AND COUNT(DISTINCT pu.stratum_id) >
             sp.requested_sample_size
        THEN FALSE
        ELSE TRUE
    END AS strata_covered
FROM sampling_projects sp
JOIN population_units pu
    ON pu.population_id = sp.population_id
   AND pu.is_eligible = TRUE
GROUP BY
    sp.project_id,
    sp.project_name,
    sp.requested_sample_size,
    sp.method;

-- =========================================================
-- 20. SAMPLE DATA
-- =========================================================

INSERT INTO population (
    population_name,
    description,
    population_type
)
VALUES (
    'University Student Performance 2026',
    'Student examination scores across three departments.',
    'STUDENT'
);

INSERT INTO population_strata (
    population_id,
    stratum_name,
    description
)
SELECT
    population_id,
    department,
    'Academic department sampling stratum'
FROM population
CROSS JOIN (
    VALUES
        ('Technology'),
        ('Mathematics'),
        ('Physics')
) AS departments(department)
WHERE population_name = 'University Student Performance 2026';

INSERT INTO population_units (
    population_id,
    external_id,
    stratum_id,
    cluster_id,
    observed_value,
    is_eligible
)
SELECT
    p.population_id,
    'STU-' || s.department_index || '-' ||
        LPAD(g.student_number::TEXT, 3, '0'),
    ps.stratum_id,
    'CLASS-' || CEIL(g.student_number / 10.0)::INTEGER,
    50
        + (s.department_index - 1) * 10
        + g.student_number * 0.8
        + (g.student_number % 5) * 2,
    TRUE
FROM population p
CROSS JOIN (
    VALUES
        ('Technology', 1),
        ('Mathematics', 2),
        ('Physics', 3)
) AS s(department, department_index)
JOIN population_strata ps
    ON ps.population_id = p.population_id
   AND ps.stratum_name = s.department
CROSS JOIN GENERATE_SERIES(1, 30) AS g(student_number)
WHERE p.population_name = 'University Student Performance 2026';

-- Demonstrate an ineligible record.
UPDATE population_units
SET is_eligible = FALSE
WHERE external_id = 'STU-3-030';

-- =========================================================
-- 21. CREATE SAMPLING PROJECTS
-- =========================================================

INSERT INTO sampling_projects (
    population_id,
    project_name,
    method,
    requested_sample_size,
    random_seed,
    confidence_level
)
SELECT
    population_id,
    project_name,
    method::sampling_method,
    20,
    42,
    0.95
FROM population
CROSS JOIN (
    VALUES
        ('Simple Random Study', 'SIMPLE_RANDOM'),
        ('Systematic Study', 'SYSTEMATIC'),
        ('Stratified Study', 'STRATIFIED')
) AS projects(project_name, method)
WHERE population_name = 'University Student Performance 2026';

-- =========================================================
-- 22. TRANSACTIONAL WORKFLOW PROCESSING
-- =========================================================

DO $$
DECLARE
    v_project RECORD;
BEGIN
    FOR v_project IN
        SELECT project_id, method
        FROM sampling_projects
        ORDER BY project_id
    LOOP

        UPDATE sampling_projects
        SET status = 'VALIDATED'
        WHERE project_id = v_project.project_id
          AND status = 'CREATED';

        CASE v_project.method

            WHEN 'SIMPLE_RANDOM' THEN
                CALL select_simple_random_sample(
                    v_project.project_id
                );

            WHEN 'SYSTEMATIC' THEN
                CALL select_systematic_sample(
                    v_project.project_id
                );

            WHEN 'STRATIFIED' THEN
                CALL select_stratified_sample(
                    v_project.project_id
                );

        END CASE;

        CALL analyze_sample(v_project.project_id);

    END LOOP;
END;
$$;

-- =========================================================
-- 23. RETRIEVAL QUERIES
-- =========================================================

-- Population parameters.
SELECT *
FROM population_summary;

-- Detailed sampling reports.
SELECT *
FROM sampling_project_report
ORDER BY project_id;

-- Selected sample observations.
SELECT
    sp.project_name,
    pu.external_id,
    ps.stratum_name,
    pu.observed_value,
    su.selection_order,
    su.inclusion_probability
FROM sample_units su
JOIN sampling_projects sp
    ON sp.project_id = su.project_id
JOIN population_units pu
    ON pu.unit_id = su.population_unit_id
JOIN population_strata ps
    ON ps.stratum_id = pu.stratum_id
ORDER BY sp.project_id, su.selection_order;

-- =========================================================
-- 24. STRATIFIED POPULATION AGGREGATION
-- =========================================================

SELECT
    ps.stratum_name,
    COUNT(*) AS population_count,
    AVG(pu.observed_value) AS stratum_mean,
    VAR_POP(pu.observed_value) AS stratum_variance,
    STDDEV_POP(pu.observed_value) AS stratum_std
FROM population_units pu
JOIN population_strata ps
    ON ps.stratum_id = pu.stratum_id
WHERE pu.is_eligible = TRUE
GROUP BY ps.stratum_name
ORDER BY ps.stratum_name;

-- =========================================================
-- 25. CTE-BASED SAMPLING VALIDATION
-- =========================================================

WITH project_counts AS (
    SELECT
        sp.project_id,
        sp.project_name,
        sp.requested_sample_size,
        COUNT(su.sample_unit_id) AS actual_sample_size
    FROM sampling_projects sp
    LEFT JOIN sample_units su
        ON su.project_id = sp.project_id
    GROUP BY
        sp.project_id,
        sp.project_name,
        sp.requested_sample_size
)
SELECT
    *,
    actual_sample_size = requested_sample_size AS size_valid,
    actual_sample_size <= requested_sample_size AS size_within_limit
FROM project_counts;

-- =========================================================
-- 26. SAMPLE SIZE CALCULATION
-- =========================================================

SELECT required_sample_size(
    15,
    3,
    1.96,
    89
) AS required_sample_size;

-- =========================================================
-- 27. WORKFLOW AND FAILURE REPORTING
-- =========================================================

SELECT
    project_name,
    status,
    requested_sample_size,
    actual_sample_size,
    CASE
        WHEN actual_sample_size = requested_sample_size
        THEN 'VALID'
        ELSE 'INVALID'
    END AS sample_validation
FROM sampling_project_report;

SELECT
    sp.project_name,
    sa.previous_status,
    sa.new_status,
    sa.event_description,
    sa.event_time
FROM sampling_audit sa
JOIN sampling_projects sp
    ON sp.project_id = sa.project_id
ORDER BY sa.event_time;

-- =========================================================
-- 28. FINAL DATABASE INTEGRITY CHECK
-- =========================================================

DO $$
DECLARE
    v_invalid_projects INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_invalid_projects
    FROM sampling_project_report
    WHERE actual_sample_size <> requested_sample_size
       OR status <> 'ANALYZED';

    IF v_invalid_projects > 0 THEN
        RAISE WARNING
            '% sampling projects require investigation.',
            v_invalid_projects;
    ELSE
        RAISE NOTICE
            'All sampling projects passed integrity checks.';
    END IF;
END;
$$;

COMMIT;
