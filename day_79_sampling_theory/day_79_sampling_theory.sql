-- ============================================================
-- SAMPLING THEORY DATABASE
-- PostgreSQL 15+
--
-- Models:
-- Population frames
-- Sampling designs
-- Random and stratified selections
-- Sampling probabilities
-- Response and nonresponse
-- Sampling bias diagnostics
-- Sample-size planning
-- Statistical estimates
-- Audit history
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS sampling;

SET search_path TO sampling, public;

-- ------------------------------------------------------------
-- ENUM TYPES
-- ------------------------------------------------------------

CREATE TYPE sampling_method AS ENUM (
    'SIMPLE_RANDOM',
    'STRATIFIED',
    'SYSTEMATIC'
);

CREATE TYPE allocation_method AS ENUM (
    'PROPORTIONAL',
    'EQUAL',
    'OPTIMAL'
);

CREATE TYPE selection_status AS ENUM (
    'SELECTED',
    'CONTACTED',
    'RESPONDED',
    'NONRESPONSE',
    'EXCLUDED'
);

CREATE TYPE design_status AS ENUM (
    'DRAFT',
    'APPROVED',
    'RUNNING',
    'COMPLETED',
    'FAILED',
    'CANCELLED'
);

CREATE TYPE estimate_status AS ENUM (
    'VALID',
    'WARNING',
    'INVALID'
);

-- ------------------------------------------------------------
-- POPULATION FRAME
-- ------------------------------------------------------------

CREATE TABLE population (
    population_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    population_name VARCHAR(150) NOT NULL,
    description TEXT,
    source_name VARCHAR(150) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    snapshot_date DATE NOT NULL,
    is_closed BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT population_name_unique
        UNIQUE (population_name, snapshot_date)
);

CREATE TABLE population_unit (
    unit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    population_id BIGINT NOT NULL
        REFERENCES population(population_id) ON DELETE CASCADE,

    external_reference VARCHAR(100) NOT NULL,
    stratum_code VARCHAR(80) NOT NULL,
    age INTEGER,
    income NUMERIC(14,2),
    outcome NUMERIC(14,4),

    is_eligible BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT population_external_reference_unique
        UNIQUE (population_id, external_reference),

    CONSTRAINT valid_age
        CHECK (age IS NULL OR age BETWEEN 18 AND 100),

    CONSTRAINT valid_income
        CHECK (income IS NULL OR income >= 0),

    CONSTRAINT valid_outcome
        CHECK (
            outcome IS NULL OR
            outcome NOT IN (
                'NaN'::NUMERIC,
                'Infinity'::NUMERIC,
                '-Infinity'::NUMERIC
            )
        ),

    CONSTRAINT nonempty_stratum
        CHECK (LENGTH(TRIM(stratum_code)) > 0)
);

CREATE INDEX idx_population_unit_population
    ON population_unit(population_id);

CREATE INDEX idx_population_unit_stratum
    ON population_unit(population_id, stratum_code);

CREATE INDEX idx_population_unit_eligibility
    ON population_unit(population_id, is_eligible);

-- ------------------------------------------------------------
-- SAMPLING DESIGN
-- ------------------------------------------------------------

CREATE TABLE sampling_design (
    design_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    population_id BIGINT NOT NULL
        REFERENCES population(population_id),

    design_name VARCHAR(150) NOT NULL,
    method sampling_method NOT NULL,
    allocation allocation_method,

    requested_sample_size INTEGER NOT NULL,
    random_seed BIGINT NOT NULL,

    confidence_level NUMERIC(5,4) NOT NULL DEFAULT 0.95,
    margin_of_error NUMERIC(8,5) NOT NULL DEFAULT 0.05,
    expected_proportion NUMERIC(8,5) NOT NULL DEFAULT 0.50,

    status design_status NOT NULL DEFAULT 'DRAFT',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,

    CONSTRAINT valid_requested_sample_size
        CHECK (requested_sample_size > 0),

    CONSTRAINT valid_confidence_level
        CHECK (confidence_level > 0 AND confidence_level < 1),

    CONSTRAINT valid_margin
        CHECK (margin_of_error > 0 AND margin_of_error < 1),

    CONSTRAINT valid_expected_proportion
        CHECK (expected_proportion > 0 AND expected_proportion < 1),

    CONSTRAINT design_name_unique
        UNIQUE (population_id, design_name)
);

CREATE INDEX idx_design_population_status
    ON sampling_design(population_id, status);

-- ------------------------------------------------------------
-- STRATA
-- ------------------------------------------------------------

CREATE TABLE sampling_stratum (
    stratum_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    design_id BIGINT NOT NULL
        REFERENCES sampling_design(design_id) ON DELETE CASCADE,

    stratum_code VARCHAR(80) NOT NULL,
    population_count INTEGER NOT NULL,
    allocated_sample_size INTEGER NOT NULL DEFAULT 0,

    population_weight NUMERIC(12,8)
        GENERATED ALWAYS AS (
            allocated_sample_size::NUMERIC /
            NULLIF(population_count, 0)
        ) STORED,

    CONSTRAINT unique_design_stratum
        UNIQUE (design_id, stratum_code),

    CONSTRAINT valid_stratum_population
        CHECK (population_count > 0),

    CONSTRAINT valid_stratum_allocation
        CHECK (
            allocated_sample_size >= 0 AND
            allocated_sample_size <= population_count
        )
);

-- ------------------------------------------------------------
-- SELECTION RECORDS
-- ------------------------------------------------------------

CREATE TABLE sample_selection (
    selection_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    design_id BIGINT NOT NULL
        REFERENCES sampling_design(design_id) ON DELETE CASCADE,

    unit_id BIGINT NOT NULL
        REFERENCES population_unit(unit_id),

    stratum_id BIGINT
        REFERENCES sampling_stratum(stratum_id),

    inclusion_probability NUMERIC(16,12) NOT NULL,

    status selection_status NOT NULL DEFAULT 'SELECTED',

    selected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMPTZ,

    response_value NUMERIC(14,4),

    CONSTRAINT unique_selected_unit
        UNIQUE (design_id, unit_id),

    CONSTRAINT valid_inclusion_probability
        CHECK (
            inclusion_probability > 0 AND
            inclusion_probability <= 1
        ),

    CONSTRAINT response_timestamp_consistency
        CHECK (
            (status = 'RESPONDED' AND responded_at IS NOT NULL)
            OR
            (status <> 'RESPONDED' AND responded_at IS NULL)
        )
);

CREATE INDEX idx_selection_design_status
    ON sample_selection(design_id, status);

CREATE INDEX idx_selection_stratum
    ON sample_selection(stratum_id);

-- ------------------------------------------------------------
-- REVIEW AND QUALITY CONTROL
-- ------------------------------------------------------------

CREATE TABLE quality_check (
    check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    design_id BIGINT NOT NULL
        REFERENCES sampling_design(design_id) ON DELETE CASCADE,

    check_name VARCHAR(120) NOT NULL,
    passed BOOLEAN NOT NULL,
    measured_value NUMERIC(16,6),
    expected_value NUMERIC(16,6),
    details TEXT,

    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (design_id, check_name)
);

-- ------------------------------------------------------------
-- SAMPLE-SIZE PLANNING
-- ------------------------------------------------------------

CREATE TABLE sample_size_plan (
    plan_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    population_size BIGINT NOT NULL,
    confidence_z NUMERIC(10,5) NOT NULL DEFAULT 1.96,
    margin_of_error NUMERIC(10,6) NOT NULL DEFAULT 0.05,
    expected_proportion NUMERIC(10,6) NOT NULL DEFAULT 0.50,

    initial_sample_size INTEGER NOT NULL,
    adjusted_sample_size INTEGER NOT NULL,
    response_rate NUMERIC(8,6) NOT NULL DEFAULT 1.0,
    recruitment_target INTEGER NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (population_size > 0),
    CHECK (confidence_z > 0),
    CHECK (margin_of_error > 0 AND margin_of_error < 1),
    CHECK (expected_proportion > 0 AND expected_proportion < 1),
    CHECK (response_rate > 0 AND response_rate <= 1),
    CHECK (initial_sample_size > 0),
    CHECK (adjusted_sample_size > 0),
    CHECK (recruitment_target >= adjusted_sample_size)
);

-- ------------------------------------------------------------
-- STATISTICAL ESTIMATES
-- ------------------------------------------------------------

CREATE TABLE statistical_estimate (
    estimate_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    design_id BIGINT NOT NULL
        REFERENCES sampling_design(design_id) ON DELETE CASCADE,

    estimate_name VARCHAR(120) NOT NULL,
    population_size INTEGER NOT NULL,
    sample_size INTEGER NOT NULL,

    estimated_mean NUMERIC(16,6),
    sample_variance NUMERIC(16,6),
    standard_error NUMERIC(16,6),

    confidence_level NUMERIC(8,6),
    lower_bound NUMERIC(16,6),
    upper_bound NUMERIC(16,6),

    status estimate_status NOT NULL DEFAULT 'VALID',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (population_size > 0),
    CHECK (sample_size > 0 AND sample_size <= population_size),
    CHECK (sample_variance IS NULL OR sample_variance >= 0),
    CHECK (standard_error IS NULL OR standard_error >= 0)
);

-- ------------------------------------------------------------
-- AUDIT LOG
-- ------------------------------------------------------------

CREATE TABLE sampling_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    design_id BIGINT REFERENCES sampling_design(design_id),
    event_type VARCHAR(100) NOT NULL,
    event_details JSONB NOT NULL DEFAULT '{}'::JSONB,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_design_time
    ON sampling_audit(design_id, recorded_at DESC);

-- ------------------------------------------------------------
-- SAMPLE-SIZE FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_sample_size(
    p_population_size BIGINT,
    p_z NUMERIC DEFAULT 1.96,
    p_margin NUMERIC DEFAULT 0.05,
    p_proportion NUMERIC DEFAULT 0.50,
    p_response_rate NUMERIC DEFAULT 1.0
)
RETURNS TABLE (
    initial_size INTEGER,
    adjusted_size INTEGER,
    recruitment_size INTEGER
)
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_n0 NUMERIC;
    v_adjusted NUMERIC;
    v_initial INTEGER;
    v_final INTEGER;
BEGIN
    IF p_population_size <= 0 THEN
        RAISE EXCEPTION 'Population size must be positive';
    END IF;

    IF p_z <= 0 OR p_margin <= 0 OR p_margin >= 1 THEN
        RAISE EXCEPTION 'Invalid confidence or margin parameters';
    END IF;

    IF p_proportion <= 0 OR p_proportion >= 1 THEN
        RAISE EXCEPTION 'Proportion must be between 0 and 1';
    END IF;

    IF p_response_rate <= 0 OR p_response_rate > 1 THEN
        RAISE EXCEPTION 'Response rate must be in (0,1]';
    END IF;

    v_n0 :=
        (p_z * p_z * p_proportion * (1 - p_proportion))
        / (p_margin * p_margin);

    v_initial := CEIL(v_n0);

    IF p_population_size = 1 THEN
        v_final := 1;
    ELSE
        v_adjusted :=
            v_n0 /
            (
                1 +
                (v_n0 - 1) / p_population_size
            );

        v_final := LEAST(
            p_population_size,
            CEIL(v_adjusted)::INTEGER
        );
    END IF;

    RETURN QUERY
    SELECT
        v_initial,
        v_final,
        CEIL(v_final / p_response_rate)::INTEGER;
END;
$$;

-- ------------------------------------------------------------
-- CREATE STRATA FROM A POPULATION FRAME
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE populate_strata(
    p_design_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_population_id BIGINT;
BEGIN
    SELECT population_id
    INTO v_population_id
    FROM sampling_design
    WHERE design_id = p_design_id
      AND status = 'DRAFT';

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Design does not exist or is not in DRAFT status';
    END IF;

    INSERT INTO sampling_stratum (
        design_id,
        stratum_code,
        population_count
    )
    SELECT
        p_design_id,
        pu.stratum_code,
        COUNT(*)::INTEGER
    FROM population_unit pu
    WHERE pu.population_id = v_population_id
      AND pu.is_eligible = TRUE
    GROUP BY pu.stratum_code
    ON CONFLICT (design_id, stratum_code)
    DO UPDATE SET
        population_count = EXCLUDED.population_count;

END;
$$;

-- ------------------------------------------------------------
-- ALLOCATION FUNCTION
-- Largest-remainder proportional allocation.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION allocate_strata(
    p_design_id BIGINT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_requested INTEGER;
    v_total BIGINT;
    v_strata INTEGER;
    v_allocated INTEGER;
    v_difference INTEGER;
    v_name VARCHAR(80);
BEGIN
    SELECT
        requested_sample_size
    INTO v_requested
    FROM sampling_design
    WHERE design_id = p_design_id
      AND status = 'DRAFT';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Design must be in DRAFT status';
    END IF;

    SELECT
        SUM(population_count),
        COUNT(*)
    INTO v_total, v_strata
    FROM sampling_stratum
    WHERE design_id = p_design_id;

    IF v_total IS NULL OR v_total = 0 THEN
        RAISE EXCEPTION 'No eligible strata exist';
    END IF;

    IF v_requested > v_total THEN
        RAISE EXCEPTION 'Sample exceeds eligible population';
    END IF;

    IF v_requested < v_strata THEN
        RAISE EXCEPTION
            'Sample must represent every non-empty stratum';
    END IF;

    UPDATE sampling_stratum
    SET allocated_sample_size = GREATEST(
        1,
        FLOOR(
            v_requested::NUMERIC *
            population_count / v_total
        )::INTEGER
    )
    WHERE design_id = p_design_id;

    SELECT SUM(allocated_sample_size)
    INTO v_allocated
    FROM sampling_stratum
    WHERE design_id = p_design_id;

    v_difference := v_requested - v_allocated;

    WHILE v_difference > 0 LOOP
        SELECT stratum_code
        INTO v_name
        FROM sampling_stratum
        WHERE design_id = p_design_id
          AND allocated_sample_size < population_count
        ORDER BY
            (
                v_requested::NUMERIC *
                population_count / v_total
                -
                FLOOR(
                    v_requested::NUMERIC *
                    population_count / v_total
                )
            ) DESC,
            stratum_code
        LIMIT 1;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'No remaining allocation capacity';
        END IF;

        UPDATE sampling_stratum
        SET allocated_sample_size =
            allocated_sample_size + 1
        WHERE design_id = p_design_id
          AND stratum_code = v_name;

        v_difference := v_difference - 1;
    END LOOP;

    WHILE v_difference < 0 LOOP
        SELECT stratum_code
        INTO v_name
        FROM sampling_stratum
        WHERE design_id = p_design_id
          AND allocated_sample_size > 1
        ORDER BY
            (
                v_requested::NUMERIC *
                population_count / v_total
                -
                FLOOR(
                    v_requested::NUMERIC *
                    population_count / v_total
                )
            ) ASC,
            stratum_code DESC
        LIMIT 1;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Cannot reduce stratum allocation';
        END IF;

        UPDATE sampling_stratum
        SET allocated_sample_size =
            allocated_sample_size - 1
        WHERE design_id = p_design_id
          AND stratum_code = v_name;

        v_difference := v_difference + 1;
    END LOOP;

    INSERT INTO sampling_audit (
        design_id,
        event_type,
        event_details
    )
    VALUES (
        p_design_id,
        'STRATA_ALLOCATED',
        jsonb_build_object(
            'requested_sample_size', v_requested,
            'population_size', v_total
        )
    );
END;
$$;

-- ------------------------------------------------------------
-- RANDOM SELECTION PROCEDURE
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE execute_random_sampling(
    p_design_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_population_id BIGINT;
    v_requested INTEGER;
    v_status design_status;
BEGIN
    SELECT
        d.population_id,
        d.requested_sample_size,
        d.status
    INTO
        v_population_id,
        v_requested,
        v_status
    FROM sampling_design d
    WHERE d.design_id = p_design_id
    FOR UPDATE;

    IF NOT FOUND OR v_status <> 'DRAFT' THEN
        RAISE EXCEPTION 'Design is missing or not in DRAFT status';
    END IF;

    IF (
        SELECT COUNT(*)
        FROM population_unit
        WHERE population_id = v_population_id
          AND is_eligible = TRUE
    ) < v_requested THEN
        RAISE EXCEPTION 'Insufficient eligible population';
    END IF;

    UPDATE sampling_design
    SET status = 'RUNNING'
    WHERE design_id = p_design_id;

    INSERT INTO sample_selection (
        design_id,
        unit_id,
        inclusion_probability
    )
    SELECT
        p_design_id,
        selected.unit_id,
        v_requested::NUMERIC /
        (
            SELECT COUNT(*)::NUMERIC
            FROM population_unit
            WHERE population_id = v_population_id
              AND is_eligible = TRUE
        )
    FROM (
        SELECT unit_id
        FROM population_unit
        WHERE population_id = v_population_id
          AND is_eligible = TRUE
        ORDER BY md5(
            unit_id::TEXT ||
            (
                SELECT random_seed::TEXT
                FROM sampling_design
                WHERE design_id = p_design_id
            )
        )
        LIMIT v_requested
    ) selected;

    UPDATE sampling_design
    SET
        status = 'COMPLETED',
        completed_at = CURRENT_TIMESTAMP
    WHERE design_id = p_design_id;

    INSERT INTO sampling_audit (
        design_id,
        event_type,
        event_details
    )
    VALUES (
        p_design_id,
        'RANDOM_SAMPLE_COMPLETED',
        jsonb_build_object(
            'sample_size', v_requested
        )
    );

EXCEPTION WHEN OTHERS THEN
    UPDATE sampling_design
    SET status = 'FAILED'
    WHERE design_id = p_design_id
      AND status = 'RUNNING';

    RAISE;
END;
$$;

-- ------------------------------------------------------------
-- STRATIFIED RANDOM SELECTION PROCEDURE
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE execute_stratified_sampling(
    p_design_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_population_id BIGINT;
    v_requested INTEGER;
    v_status design_status;
BEGIN
    SELECT
        population_id,
        requested_sample_size,
        status
    INTO
        v_population_id,
        v_requested,
        v_status
    FROM sampling_design
    WHERE design_id = p_design_id
    FOR UPDATE;

    IF NOT FOUND OR v_status <> 'DRAFT' THEN
        RAISE EXCEPTION 'Design is missing or not in DRAFT status';
    END IF;

    CALL populate_strata(p_design_id);
    PERFORM allocate_strata(p_design_id);

    UPDATE sampling_design
    SET status = 'RUNNING'
    WHERE design_id = p_design_id;

    INSERT INTO sample_selection (
        design_id,
        unit_id,
        stratum_id,
        inclusion_probability
    )
    SELECT
        p_design_id,
        selected.unit_id,
        selected.stratum_id,
        selected.allocated_sample_size::NUMERIC /
        selected.population_count
    FROM (
        SELECT
            pu.unit_id,
            ss.stratum_id,
            ss.population_count,
            ss.allocated_sample_size,
            ROW_NUMBER() OVER (
                PARTITION BY ss.stratum_id
                ORDER BY md5(
                    pu.unit_id::TEXT ||
                    (
                        SELECT random_seed::TEXT
                        FROM sampling_design
                        WHERE design_id = p_design_id
                    )
                )
            ) AS row_number
        FROM population_unit pu
        JOIN sampling_stratum ss
          ON ss.design_id = p_design_id
         AND ss.stratum_code = pu.stratum_code
        WHERE pu.population_id = v_population_id
          AND pu.is_eligible = TRUE
    ) selected
    WHERE selected.row_number <=
        selected.allocated_sample_size;

    UPDATE sampling_design
    SET
        status = 'COMPLETED',
        completed_at = CURRENT_TIMESTAMP
    WHERE design_id = p_design_id;

    INSERT INTO sampling_audit (
        design_id,
        event_type,
        event_details
    )
    VALUES (
        p_design_id,
        'STRATIFIED_SAMPLE_COMPLETED',
        jsonb_build_object(
            'sample_size', v_requested
        )
    );

EXCEPTION WHEN OTHERS THEN
    UPDATE sampling_design
    SET status = 'FAILED'
    WHERE design_id = p_design_id
      AND status = 'RUNNING';

    RAISE;
END;
$$;

-- ------------------------------------------------------------
-- RESPONSE VALIDATION TRIGGER
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_sample_response()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status = 'RESPONDED' THEN
        IF NEW.response_value IS NULL THEN
            RAISE EXCEPTION
                'Responded observations require a response value';
        END IF;

        IF NEW.responded_at IS NULL THEN
            NEW.responded_at := CURRENT_TIMESTAMP;
        END IF;
    ELSE
        NEW.responded_at := NULL;
        NEW.response_value := NULL;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_sample_response
BEFORE INSERT OR UPDATE
ON sample_selection
FOR EACH ROW
EXECUTE FUNCTION validate_sample_response();

-- ------------------------------------------------------------
-- IMMUTABLE POPULATION SNAPSHOT CONTROL
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION protect_closed_population()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_closed BOOLEAN;
    v_population_id BIGINT;
BEGIN
    v_population_id := COALESCE(NEW.population_id, OLD.population_id);

    SELECT is_closed
    INTO v_closed
    FROM population
    WHERE population_id = v_population_id;

    IF v_closed THEN
        RAISE EXCEPTION
            'Closed population snapshots cannot be modified';
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$;

CREATE TRIGGER trg_protect_population_units
BEFORE INSERT OR UPDATE OR DELETE
ON population_unit
FOR EACH ROW
EXECUTE FUNCTION protect_closed_population();

-- ------------------------------------------------------------
-- DESIGN VALIDATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_sampling_design()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_population_size BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO v_population_size
    FROM population_unit
    WHERE population_id = NEW.population_id
      AND is_eligible = TRUE;

    IF NEW.requested_sample_size > v_population_size THEN
        RAISE EXCEPTION
            'Requested sample exceeds eligible population';
    END IF;

    IF v_population_size = 0 THEN
        RAISE EXCEPTION 'Population contains no eligible units';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_sampling_design
BEFORE INSERT OR UPDATE OF requested_sample_size, population_id
ON sampling_design
FOR EACH ROW
EXECUTE FUNCTION validate_sampling_design();

-- ------------------------------------------------------------
-- VIEWS
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW v_population_summary AS
SELECT
    p.population_id,
    p.population_name,
    p.snapshot_date,
    COUNT(pu.unit_id) AS total_units,
    COUNT(pu.unit_id) FILTER (
        WHERE pu.is_eligible
    ) AS eligible_units,
    COUNT(DISTINCT pu.stratum_code) AS number_of_strata
FROM population p
LEFT JOIN population_unit pu
    ON pu.population_id = p.population_id
GROUP BY
    p.population_id,
    p.population_name,
    p.snapshot_date;

CREATE OR REPLACE VIEW v_sample_summary AS
SELECT
    d.design_id,
    d.design_name,
    d.method,
    d.status,
    d.requested_sample_size,
    COUNT(s.selection_id) AS selected_count,
    COUNT(s.selection_id) FILTER (
        WHERE s.status = 'RESPONDED'
    ) AS responded_count,
    COUNT(s.selection_id) FILTER (
        WHERE s.status = 'NONRESPONSE'
    ) AS nonresponse_count,
    CASE
        WHEN COUNT(s.selection_id) = 0 THEN NULL
        ELSE
            COUNT(s.selection_id) FILTER (
                WHERE s.status = 'RESPONDED'
            )::NUMERIC /
            COUNT(s.selection_id)
    END AS observed_response_rate
FROM sampling_design d
LEFT JOIN sample_selection s
    ON s.design_id = d.design_id
GROUP BY
    d.design_id,
    d.design_name,
    d.method,
    d.status,
    d.requested_sample_size;

CREATE OR REPLACE VIEW v_stratum_representation AS
WITH population_counts AS (
    SELECT
        d.design_id,
        pu.stratum_code,
        COUNT(*) AS population_count
    FROM sampling_design d
    JOIN population_unit pu
      ON pu.population_id = d.population_id
    WHERE pu.is_eligible
    GROUP BY d.design_id, pu.stratum_code
),
sample_counts AS (
    SELECT
        design_id,
        stratum_id,
        COUNT(*) AS sample_count
    FROM sample_selection
    GROUP BY design_id, stratum_id
)
SELECT
    ss.design_id,
    ss.stratum_code,
    pc.population_count,
    COALESCE(sc.sample_count, 0) AS sample_count,
    pc.population_count::NUMERIC /
        NULLIF(SUM(pc.population_count) OVER (
            PARTITION BY ss.design_id
        ), 0) AS population_share,
    COALESCE(sc.sample_count, 0)::NUMERIC /
        NULLIF(SUM(COALESCE(sc.sample_count, 0)) OVER (
            PARTITION BY ss.design_id
        ), 0) AS sample_share
FROM sampling_stratum ss
JOIN population_counts pc
    ON pc.design_id = ss.design_id
   AND pc.stratum_code = ss.stratum_code
LEFT JOIN sample_counts sc
    ON sc.design_id = ss.design_id
   AND sc.stratum_id = ss.stratum_id;

-- ------------------------------------------------------------
-- ESTIMATE CALCULATION FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_sample_estimate(
    p_design_id BIGINT,
    p_confidence_z NUMERIC DEFAULT 1.96
)
RETURNS TABLE (
    sample_count BIGINT,
    estimated_mean NUMERIC,
    sample_variance NUMERIC,
    standard_error NUMERIC,
    lower_bound NUMERIC,
    upper_bound NUMERIC
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_population_size BIGINT;
    v_sample_size BIGINT;
    v_mean NUMERIC;
    v_variance NUMERIC;
    v_se NUMERIC;
    v_fpc NUMERIC;
    v_margin NUMERIC;
BEGIN
    SELECT
        COUNT(*),
        AVG(response_value),
        VAR_SAMP(response_value)
    INTO
        v_sample_size,
        v_mean,
        v_variance
    FROM sample_selection
    WHERE design_id = p_design_id
      AND status = 'RESPONDED'
      AND response_value IS NOT NULL;

    SELECT COUNT(*)
    INTO v_population_size
    FROM population_unit pu
    JOIN sampling_design d
      ON d.population_id = pu.population_id
    WHERE d.design_id = p_design_id
      AND pu.is_eligible;

    IF v_sample_size < 2 THEN
        RAISE EXCEPTION
            'At least two responses are required for variance estimation';
    END IF;

    IF v_population_size <= 1 THEN
        v_fpc := 1;
    ELSE
        v_fpc := SQRT(
            GREATEST(
                0,
                (v_population_size - v_sample_size)::NUMERIC /
                (v_population_size - 1)
            )
        );
    END IF;

    v_se := SQRT(v_variance / v_sample_size) * v_fpc;
    v_margin := p_confidence_z * v_se;

    RETURN QUERY
    SELECT
        v_sample_size,
        v_mean,
        v_variance,
        v_se,
        v_mean - v_margin,
        v_mean + v_margin;
END;
$$;

-- ------------------------------------------------------------
-- SAMPLE-SIZE PLANNING DATA
-- ------------------------------------------------------------

INSERT INTO sample_size_plan (
    population_size,
    confidence_z,
    margin_of_error,
    expected_proportion,
    initial_sample_size,
    adjusted_sample_size,
    response_rate,
    recruitment_target
)
SELECT
    1000,
    1.96,
    0.05,
    0.50,
    result.initial_size,
    result.adjusted_size,
    0.85,
    result.recruitment_size
FROM calculate_sample_size(
    1000,
    1.96,
    0.05,
    0.50,
    0.85
) result;

-- ------------------------------------------------------------
-- SAMPLE POPULATION
-- ------------------------------------------------------------

INSERT INTO population (
    population_name,
    description,
    source_name,
    snapshot_date
)
VALUES (
    'Enterprise Workforce 2026',
    'Synthetic employee population for sampling analysis.',
    'Internal Workforce Register',
    DATE '2026-11-01'
);

INSERT INTO population_unit (
    population_id,
    external_reference,
    stratum_code,
    age,
    income,
    outcome
)
SELECT
    1,
    'EMP-' || LPAD(i::TEXT, 5, '0'),
    CASE
        WHEN i <= 400 THEN 'ENGINEERING'
        WHEN i <= 600 THEN 'FINANCE'
        WHEN i <= 850 THEN 'OPERATIONS'
        ELSE 'RESEARCH'
    END,
    21 + (i % 45),
    ROUND(
        (25000 + (i % 100) * 1500)::NUMERIC,
        2
    ),
    ROUND(
        (
            40 +
            (i % 30) * 0.8 +
            (i % 11) * 1.2
        )::NUMERIC,
        4
    )
FROM generate_series(1, 1000) AS series(i);

-- ------------------------------------------------------------
-- CREATE SAMPLING DESIGNS
-- ------------------------------------------------------------

INSERT INTO sampling_design (
    population_id,
    design_name,
    method,
    requested_sample_size,
    random_seed
)
VALUES
    (1, 'Random Sample 100', 'SIMPLE_RANDOM', 100, 17),
    (1, 'Stratified Sample 100', 'STRATIFIED', 100, 17),
    (1, 'Systematic Design 100', 'SYSTEMATIC', 100, 17);

-- ------------------------------------------------------------
-- EXECUTE WORKFLOWS
-- ------------------------------------------------------------

CALL execute_random_sampling(1);

CALL execute_stratified_sampling(2);

-- ------------------------------------------------------------
-- SYSTEMATIC SAMPLING
-- Randomized start with equal intervals.
-- ------------------------------------------------------------

DO $$
DECLARE
    v_population_id BIGINT;
    v_n INTEGER;
    v_N BIGINT;
    v_start NUMERIC;
BEGIN
    SELECT population_id, requested_sample_size
    INTO v_population_id, v_n
    FROM sampling_design
    WHERE design_id = 3
      AND status = 'DRAFT'
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Systematic design is unavailable';
    END IF;

    SELECT COUNT(*)
    INTO v_N
    FROM population_unit
    WHERE population_id = v_population_id
      AND is_eligible;

    IF v_n > v_N THEN
        RAISE EXCEPTION 'Sample exceeds population';
    END IF;

    v_start := random() * (v_N::NUMERIC / v_n);

    UPDATE sampling_design
    SET status = 'RUNNING'
    WHERE design_id = 3;

    INSERT INTO sample_selection (
        design_id,
        unit_id,
        inclusion_probability
    )
    SELECT
        3,
        selected.unit_id,
        v_n::NUMERIC / v_N
    FROM (
        SELECT
            unit_id,
            ROW_NUMBER() OVER (
                ORDER BY unit_id
            ) AS sequence_number
        FROM population_unit
        WHERE population_id = v_population_id
          AND is_eligible
    ) selected
    WHERE selected.sequence_number IN (
        SELECT
            LEAST(
                v_N,
                FLOOR(
                    v_start + (series.i - 1) *
                    (v_N::NUMERIC / v_n)
                )::BIGINT + 1
            )
        FROM generate_series(1, v_n) AS series(i)
    );

    UPDATE sampling_design
    SET
        status = 'COMPLETED',
        completed_at = CURRENT_TIMESTAMP
    WHERE design_id = 3;

    INSERT INTO sampling_audit (
        design_id,
        event_type,
        event_details
    )
    VALUES (
        3,
        'SYSTEMATIC_SAMPLE_COMPLETED',
        jsonb_build_object(
            'sample_size', v_n,
            'population_size', v_N
        )
    );
END;
$$;

-- ------------------------------------------------------------
-- SIMULATE RESPONSES
-- ------------------------------------------------------------

UPDATE sample_selection
SET
    status = 'RESPONDED',
    response_value = pu.outcome,
    responded_at = CURRENT_TIMESTAMP
FROM population_unit pu
WHERE sample_selection.unit_id = pu.unit_id
  AND sample_selection.design_id IN (1, 2, 3)
  AND sample_selection.selection_id % 10 <> 0;

-- Simulated nonresponse.
UPDATE sample_selection
SET status = 'NONRESPONSE'
WHERE design_id = 1
  AND selection_id % 10 = 0;

-- ------------------------------------------------------------
-- STATISTICAL QUALITY CHECKS
-- ------------------------------------------------------------

INSERT INTO quality_check (
    design_id,
    check_name,
    passed,
    measured_value,
    expected_value,
    details
)
SELECT
    d.design_id,
    'SAMPLE_SIZE_MATCH',
    COUNT(s.selection_id) = d.requested_sample_size,
    COUNT(s.selection_id),
    d.requested_sample_size,
    'Actual selected count compared with requested sample size.'
FROM sampling_design d
LEFT JOIN sample_selection s
    ON s.design_id = d.design_id
GROUP BY d.design_id, d.requested_sample_size
ON CONFLICT (design_id, check_name)
DO UPDATE SET
    passed = EXCLUDED.passed,
    measured_value = EXCLUDED.measured_value,
    expected_value = EXCLUDED.expected_value,
    details = EXCLUDED.details;

INSERT INTO quality_check (
    design_id,
    check_name,
    passed,
    measured_value,
    expected_value,
    details
)
SELECT
    design_id,
    'MINIMUM_RESPONSE_COUNT',
    COUNT(*) FILTER (
        WHERE status = 'RESPONDED'
    ) >= 2,
    COUNT(*) FILTER (
        WHERE status = 'RESPONDED'
    ),
    2,
    'At least two responses are required for variance estimation.'
FROM sample_selection
GROUP BY design_id
ON CONFLICT (design_id, check_name)
DO UPDATE SET
    passed = EXCLUDED.passed,
    measured_value = EXCLUDED.measured_value,
    expected_value = EXCLUDED.expected_value,
    details = EXCLUDED.details;

-- ------------------------------------------------------------
-- STORE ESTIMATES
-- ------------------------------------------------------------

INSERT INTO statistical_estimate (
    design_id,
    estimate_name,
    population_size,
    sample_size,
    estimated_mean,
    sample_variance,
    standard_error,
    confidence_level,
    lower_bound,
    upper_bound,
    status
)
SELECT
    d.design_id,
    'Employee outcome mean',
    COUNT(DISTINCT pu.unit_id)::INTEGER,
    COUNT(s.selection_id) FILTER (
        WHERE s.status = 'RESPONDED'
    )::INTEGER,
    result.estimated_mean,
    result.sample_variance,
    result.standard_error,
    0.95,
    result.lower_bound,
    result.upper_bound,
    CASE
        WHEN result.sample_count >= 2 THEN 'VALID'::estimate_status
        ELSE 'INVALID'::estimate_status
    END
FROM sampling_design d
JOIN population_unit pu
    ON pu.population_id = d.population_id
LEFT JOIN sample_selection s
    ON s.design_id = d.design_id
LEFT JOIN LATERAL calculate_sample_estimate(
    d.design_id,
    1.96
) result ON TRUE
WHERE d.design_id IN (1, 2, 3)
GROUP BY
    d.design_id,
    result.estimated_mean,
    result.sample_variance,
    result.standard_error,
    result.lower_bound,
    result.upper_bound,
    result.sample_count;

-- ------------------------------------------------------------
-- REPORTING QUERIES
-- ------------------------------------------------------------

-- 1. Population characteristics.
SELECT *
FROM v_population_summary
ORDER BY population_id;

-- 2. Sampling workflow status.
SELECT *
FROM v_sample_summary
ORDER BY design_id;

-- 3. Sample allocation by stratum.
SELECT
    design_id,
    stratum_code,
    population_count,
    allocated_sample_size,
    ROUND(
        population_count::NUMERIC /
        SUM(population_count) OVER (
            PARTITION BY design_id
        ),
        4
    ) AS population_share
FROM sampling_stratum
ORDER BY design_id, stratum_code;

-- 4. Sample representation differences.
SELECT
    design_id,
    stratum_code,
    ROUND(population_share, 4) AS population_share,
    ROUND(sample_share, 4) AS sample_share,
    ROUND(sample_share - population_share, 4)
        AS representation_gap
FROM v_stratum_representation
ORDER BY design_id, stratum_code;

-- 5. Response and nonresponse analysis.
SELECT
    design_id,
    status,
    COUNT(*) AS observations
FROM sample_selection
GROUP BY design_id, status
ORDER BY design_id, status;

-- 6. Weighted inverse-probability estimate.
SELECT
    design_id,
    SUM(response_value / inclusion_probability)
        / SUM(1 / inclusion_probability)
        AS weighted_mean
FROM sample_selection
WHERE status = 'RESPONDED'
GROUP BY design_id
ORDER BY design_id;

-- 7. Design quality evaluation.
SELECT
    d.design_name,
    qc.check_name,
    qc.passed,
    qc.measured_value,
    qc.expected_value,
    qc.details
FROM quality_check qc
JOIN sampling_design d
    ON d.design_id = qc.design_id
ORDER BY d.design_id, qc.check_name;

-- 8. Statistical estimates.
SELECT *
FROM statistical_estimate
ORDER BY design_id;

-- 9. Sampling audit.
SELECT
    design_id,
    event_type,
    event_details,
    recorded_at
FROM sampling_audit
ORDER BY recorded_at DESC;

-- 10. Eligibility determination.
SELECT
    d.design_id,
    d.design_name,
    d.requested_sample_size,
    COUNT(pu.unit_id) AS eligible_population,
    COUNT(pu.unit_id) >= d.requested_sample_size
        AS eligible_for_sampling
FROM sampling_design d
JOIN population_unit pu
    ON pu.population_id = d.population_id
   AND pu.is_eligible
GROUP BY
    d.design_id,
    d.design_name,
    d.requested_sample_size
ORDER BY d.design_id;

-- ------------------------------------------------------------
-- FAILURE CASES
-- These queries intentionally demonstrate constraint enforcement.
-- Run individually with error handling if testing interactively.
-- ------------------------------------------------------------

-- Invalid sample size:
-- INSERT INTO sampling_design (
--     population_id, design_name, method,
--     requested_sample_size, random_seed
-- )
-- VALUES (1, 'Invalid Design', 'SIMPLE_RANDOM', 0, 1);

-- Invalid probability:
-- INSERT INTO sample_selection (
--     design_id, unit_id, inclusion_probability
-- )
-- VALUES (1, 1, 1.5);

-- Invalid age:
-- INSERT INTO population_unit (
--     population_id, external_reference,
--     stratum_code, age
-- )
-- VALUES (1, 'INVALID-AGE', 'ENGINEERING', 150);

-- ------------------------------------------------------------
-- TRANSACTION EXAMPLE
-- Rollback preserves the existing design.
-- ------------------------------------------------------------

SAVEPOINT sampling_test;

UPDATE sampling_design
SET status = 'CANCELLED'
WHERE design_id = 3;

ROLLBACK TO SAVEPOINT sampling_test;

RELEASE SAVEPOINT sampling_test;

-- ------------------------------------------------------------
-- DATABASE ACCESS CONTROL
-- ------------------------------------------------------------

-- For deployment, create a restricted application role separately.
-- The application should receive only the permissions it requires.
--
-- Example:
-- CREATE ROLE sampling_reader NOLOGIN;
-- GRANT USAGE ON SCHEMA sampling TO sampling_reader;
-- GRANT SELECT ON ALL TABLES IN SCHEMA sampling TO sampling_reader;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA sampling
--     GRANT SELECT ON TABLES TO sampling_reader;

COMMIT;
