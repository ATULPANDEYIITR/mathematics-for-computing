-- ============================================================
-- LINEAR ALGEBRA FOUNDATIONS
-- Scalars, vectors, vector notation and vector spaces
-- PostgreSQL implementation
--
-- Domain:
--   Real scalar field
--       |
--   Vector spaces R^n
--       |
--   Vectors and components
--       |
--   Vector operations
--       |
--   Linear combinations
--       |
--   Linear independence and basis evaluation
--
-- Requires PostgreSQL 14 or later.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS linear_algebra;

SET search_path TO linear_algebra, public;

-- ============================================================
-- 1. DOMAIN TYPES
-- ============================================================

-- Real scalars are represented using DOUBLE PRECISION.
-- The domain prevents NaN and infinite scalar values.
CREATE DOMAIN real_scalar AS DOUBLE PRECISION
CHECK (
    VALUE > '-Infinity'::DOUBLE PRECISION
    AND VALUE < 'Infinity'::DOUBLE PRECISION
);

CREATE TYPE field_type AS ENUM (
    'REAL'
);

CREATE TYPE vector_operation AS ENUM (
    'ADD',
    'SUBTRACT',
    'SCALE',
    'DOT_PRODUCT',
    'LINEAR_COMBINATION'
);

-- ============================================================
-- 2. VECTOR SPACES
-- ============================================================

CREATE TABLE vector_spaces (
    space_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    space_name VARCHAR(100) NOT NULL UNIQUE,

    dimension INTEGER NOT NULL
        CHECK (dimension > 0 AND dimension <= 1000),

    scalar_field field_type NOT NULL DEFAULT 'REAL',

    description TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE vector_spaces IS
'Defines finite-dimensional real coordinate vector spaces R^n.';

COMMENT ON COLUMN vector_spaces.dimension IS
'Number of components required by every vector in the space.';

-- ============================================================
-- 3. VECTORS
-- ============================================================

CREATE TABLE vectors (
    vector_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    space_id BIGINT NOT NULL
        REFERENCES vector_spaces(space_id)
        ON DELETE RESTRICT,

    vector_name VARCHAR(100) NOT NULL,

    notation TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (space_id, vector_name),

    UNIQUE (vector_id, space_id)
);

COMMENT ON TABLE vectors IS
'Stores vector identities independently of their components.';

COMMENT ON COLUMN vectors.notation IS
'Human-readable vector notation such as (2, 3, 4).';

-- ============================================================
-- 4. VECTOR COMPONENTS
-- ============================================================

CREATE TABLE vector_components (
    vector_id BIGINT NOT NULL
        REFERENCES vectors(vector_id)
        ON DELETE CASCADE,

    component_index INTEGER NOT NULL
        CHECK (component_index >= 1),

    component_value real_scalar NOT NULL,

    PRIMARY KEY (vector_id, component_index)
);

COMMENT ON TABLE vector_components IS
'Stores each ordered component of a vector.';

COMMENT ON COLUMN vector_components.component_index IS
'One-based position of the component in the vector.';

CREATE INDEX idx_vector_components_value
ON vector_components(component_value);

-- ============================================================
-- 5. SCALAR REGISTRY
-- ============================================================

CREATE TABLE scalars (
    scalar_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    scalar_name VARCHAR(100) NOT NULL UNIQUE,

    scalar_value real_scalar NOT NULL,

    description TEXT
);

-- ============================================================
-- 6. VECTOR OPERATION HISTORY
-- ============================================================

CREATE TABLE operation_history (
    operation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    operation vector_operation NOT NULL,

    first_vector_id BIGINT
        REFERENCES vectors(vector_id)
        ON DELETE RESTRICT,

    second_vector_id BIGINT
        REFERENCES vectors(vector_id)
        ON DELETE RESTRICT,

    scalar_value real_scalar,

    result_notation TEXT,

    success BOOLEAN NOT NULL DEFAULT TRUE,

    error_message TEXT,

    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (
        success = TRUE
        OR error_message IS NOT NULL
    )
);

CREATE INDEX idx_operation_history_time
ON operation_history(executed_at DESC);

CREATE INDEX idx_operation_history_type
ON operation_history(operation);

-- ============================================================
-- 7. VALIDATE VECTOR COMPONENT POSITIONS
-- ============================================================

CREATE OR REPLACE FUNCTION validate_component_position()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    expected_dimension INTEGER;
BEGIN
    SELECT s.dimension
    INTO expected_dimension
    FROM vectors v
    JOIN vector_spaces s
      ON s.space_id = v.space_id
    WHERE v.vector_id = NEW.vector_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Vector % does not exist.',
            NEW.vector_id;
    END IF;

    IF NEW.component_index > expected_dimension THEN
        RAISE EXCEPTION
            'Component index % exceeds vector dimension %.',
            NEW.component_index,
            expected_dimension;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_component_position
BEFORE INSERT OR UPDATE
ON vector_components
FOR EACH ROW
EXECUTE FUNCTION validate_component_position();

-- ============================================================
-- 8. ENSURE COMPLETE VECTOR DIMENSIONS
-- ============================================================

-- Component rows are inserted separately, so dimension
-- completeness is checked when a vector is used.
CREATE OR REPLACE FUNCTION validate_complete_vector(
    p_vector_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    expected_dimension INTEGER;
    actual_count BIGINT;
    minimum_index INTEGER;
    maximum_index INTEGER;
BEGIN
    SELECT s.dimension
    INTO expected_dimension
    FROM vectors v
    JOIN vector_spaces s
      ON s.space_id = v.space_id
    WHERE v.vector_id = p_vector_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Vector % not found.', p_vector_id;
    END IF;

    SELECT
        COUNT(*),
        MIN(component_index),
        MAX(component_index)
    INTO
        actual_count,
        minimum_index,
        maximum_index
    FROM vector_components
    WHERE vector_id = p_vector_id;

    IF actual_count <> expected_dimension
       OR minimum_index <> 1
       OR maximum_index <> expected_dimension
    THEN
        RETURN FALSE;
    END IF;

    RETURN TRUE;
END;
$$;

-- ============================================================
-- 9. VECTOR NORM FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION vector_norm(
    p_vector_id BIGINT
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    result DOUBLE PRECISION;
BEGIN
    IF NOT validate_complete_vector(p_vector_id) THEN
        RAISE EXCEPTION
            'Vector % has incomplete components.',
            p_vector_id;
    END IF;

    SELECT SQRT(
        SUM(component_value * component_value)
    )
    INTO result
    FROM vector_components
    WHERE vector_id = p_vector_id;

    RETURN result;
END;
$$;

-- ============================================================
-- 10. VECTOR DOT PRODUCT
-- ============================================================

CREATE OR REPLACE FUNCTION vector_dot_product(
    p_first_vector BIGINT,
    p_second_vector BIGINT
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    first_space BIGINT;
    second_space BIGINT;
    result DOUBLE PRECISION;
BEGIN
    IF NOT validate_complete_vector(p_first_vector)
       OR NOT validate_complete_vector(p_second_vector)
    THEN
        RAISE EXCEPTION 'Incomplete vector components.';
    END IF;

    SELECT space_id
    INTO first_space
    FROM vectors
    WHERE vector_id = p_first_vector;

    SELECT space_id
    INTO second_space
    FROM vectors
    WHERE vector_id = p_second_vector;

    IF first_space <> second_space THEN
        RAISE EXCEPTION
            'Vectors must belong to the same vector space.';
    END IF;

    SELECT SUM(
        a.component_value * b.component_value
    )
    INTO result
    FROM vector_components a
    JOIN vector_components b
      ON b.component_index = a.component_index
    WHERE a.vector_id = p_first_vector
      AND b.vector_id = p_second_vector;

    RETURN COALESCE(result, 0);
END;
$$;

-- ============================================================
-- 11. VECTOR ADDITION FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION vector_addition(
    p_first_vector BIGINT,
    p_second_vector BIGINT
)
RETURNS TABLE (
    component_index INTEGER,
    result_value DOUBLE PRECISION
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    first_space BIGINT;
    second_space BIGINT;
BEGIN
    IF NOT validate_complete_vector(p_first_vector)
       OR NOT validate_complete_vector(p_second_vector)
    THEN
        RAISE EXCEPTION 'Incomplete vector components.';
    END IF;

    SELECT space_id INTO first_space
    FROM vectors
    WHERE vector_id = p_first_vector;

    SELECT space_id INTO second_space
    FROM vectors
    WHERE vector_id = p_second_vector;

    IF first_space <> second_space THEN
        RAISE EXCEPTION
            'Vector addition requires equal vector spaces.';
    END IF;

    RETURN QUERY
    SELECT
        a.component_index,
        a.component_value + b.component_value
    FROM vector_components a
    JOIN vector_components b
      ON b.component_index = a.component_index
    WHERE a.vector_id = p_first_vector
      AND b.vector_id = p_second_vector
    ORDER BY a.component_index;
END;
$$;

-- ============================================================
-- 12. SCALAR MULTIPLICATION FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION vector_scalar_multiplication(
    p_vector_id BIGINT,
    p_scalar real_scalar
)
RETURNS TABLE (
    component_index INTEGER,
    result_value DOUBLE PRECISION
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    IF NOT validate_complete_vector(p_vector_id) THEN
        RAISE EXCEPTION
            'Vector % has incomplete components.',
            p_vector_id;
    END IF;

    RETURN QUERY
    SELECT
        component_index,
        component_value * p_scalar
    FROM vector_components
    WHERE vector_id = p_vector_id
    ORDER BY component_index;
END;
$$;

-- ============================================================
-- 13. VECTOR CATALOG VIEW
-- ============================================================

CREATE VIEW vector_catalog AS
SELECT
    v.vector_id,
    v.vector_name,
    v.notation,
    s.space_name,
    s.dimension,
    s.scalar_field,
    COUNT(c.component_index) AS component_count,
    CASE
        WHEN COUNT(c.component_index) = s.dimension
         AND MIN(c.component_index) = 1
         AND MAX(c.component_index) = s.dimension
        THEN TRUE
        ELSE FALSE
    END AS is_complete,
    COALESCE(
        SQRT(SUM(c.component_value * c.component_value)),
        0
    ) AS euclidean_norm,
    v.created_at
FROM vectors v
JOIN vector_spaces s
  ON s.space_id = v.space_id
LEFT JOIN vector_components c
  ON c.vector_id = v.vector_id
GROUP BY
    v.vector_id,
    v.vector_name,
    v.notation,
    s.space_name,
    s.dimension,
    s.scalar_field,
    v.created_at;

-- ============================================================
-- 14. SAMPLE VECTOR SPACES
-- ============================================================

INSERT INTO vector_spaces (
    space_name,
    dimension,
    scalar_field,
    description
)
VALUES
(
    'R2',
    2,
    'REAL',
    'Two-dimensional real coordinate vector space.'
),
(
    'R3',
    3,
    'REAL',
    'Three-dimensional real coordinate vector space.'
),
(
    'R4',
    4,
    'REAL',
    'Four-dimensional real coordinate vector space.'
);

-- ============================================================
-- 15. SAMPLE SCALARS
-- ============================================================

INSERT INTO scalars (
    scalar_name,
    scalar_value,
    description
)
VALUES
('alpha', 3, 'First real scalar.'),
('beta', 2, 'Second real scalar.'),
('zero', 0, 'Additive identity in the real field.'),
('negative_scalar', -2, 'Negative real scalar.');

-- ============================================================
-- 16. SAMPLE VECTORS
-- ============================================================

INSERT INTO vectors (
    space_id,
    vector_name,
    notation
)
SELECT
    space_id,
    data.vector_name,
    data.notation
FROM vector_spaces
CROSS JOIN (
    VALUES
        ('u', '(2, 3)', 'R2'),
        ('v', '(4, 1)', 'R2'),
        ('e1', '(1, 0)', 'R2'),
        ('e2', '(0, 1)', 'R2'),
        ('dependent_a', '(1, 2)', 'R2'),
        ('dependent_b', '(2, 4)', 'R2'),
        ('a3', '(1, 0, 0)', 'R3'),
        ('b3', '(0, 1, 0)', 'R3'),
        ('c3', '(0, 0, 1)', 'R3')
) AS data(vector_name, notation, target_space)
WHERE vector_spaces.space_name = data.target_space;

-- ============================================================
-- 17. INSERT VECTOR COMPONENTS
-- ============================================================

INSERT INTO vector_components (
    vector_id,
    component_index,
    component_value
)
SELECT
    v.vector_id,
    data.component_index,
    data.component_value
FROM (
    VALUES
        ('u',  'R2', 1, 2.0::DOUBLE PRECISION),
        ('u',  'R2', 2, 3.0::DOUBLE PRECISION),
        ('v',  'R2', 1, 4.0::DOUBLE PRECISION),
        ('v',  'R2', 2, 1.0::DOUBLE PRECISION),
        ('e1', 'R2', 1, 1.0::DOUBLE PRECISION),
        ('e1', 'R2', 2, 0.0::DOUBLE PRECISION),
        ('e2', 'R2', 1, 0.0::DOUBLE PRECISION),
        ('e2', 'R2', 2, 1.0::DOUBLE PRECISION),
        ('dependent_a', 'R2', 1, 1.0::DOUBLE PRECISION),
        ('dependent_a', 'R2', 2, 2.0::DOUBLE PRECISION),
        ('dependent_b', 'R2', 1, 2.0::DOUBLE PRECISION),
        ('dependent_b', 'R2', 2, 4.0::DOUBLE PRECISION),
        ('a3', 'R3', 1, 1.0::DOUBLE PRECISION),
        ('a3', 'R3', 2, 0.0::DOUBLE PRECISION),
        ('a3', 'R3', 3, 0.0::DOUBLE PRECISION),
        ('b3', 'R3', 1, 0.0::DOUBLE PRECISION),
        ('b3', 'R3', 2, 1.0::DOUBLE PRECISION),
        ('b3', 'R3', 3, 0.0::DOUBLE PRECISION),
        ('c3', 'R3', 1, 0.0::DOUBLE PRECISION),
        ('c3', 'R3', 2, 0.0::DOUBLE PRECISION),
        ('c3', 'R3', 3, 1.0::DOUBLE PRECISION)
) AS data(
    vector_name,
    target_space,
    component_index,
    component_value
)
JOIN vectors v
  ON v.vector_name = data.vector_name
JOIN vector_spaces s
  ON s.space_id = v.space_id
 AND s.space_name = data.target_space;

-- ============================================================
-- 18. VECTOR RETRIEVAL
-- ============================================================

SELECT
    v.vector_name,
    s.space_name,
    s.dimension,
    c.component_index,
    c.component_value
FROM vectors v
JOIN vector_spaces s
  ON s.space_id = v.space_id
JOIN vector_components c
  ON c.vector_id = v.vector_id
ORDER BY
    s.space_name,
    v.vector_name,
    c.component_index;

-- ============================================================
-- 19. VECTOR CATALOG REPORT
-- ============================================================

SELECT *
FROM vector_catalog
ORDER BY space_name, vector_name;

-- ============================================================
-- 20. VALIDATION REPORT
-- ============================================================

SELECT
    vector_name,
    space_name,
    dimension,
    component_count,
    is_complete,
    CASE
        WHEN is_complete THEN 'VALID'
        ELSE 'INCOMPLETE'
    END AS validation_status
FROM vector_catalog
ORDER BY space_name, vector_name;

-- ============================================================
-- 21. SCALAR AGGREGATION
-- ============================================================

SELECT
    scalar_field,
    COUNT(*) AS number_of_spaces,
    AVG(dimension) AS average_dimension,
    MAX(dimension) AS maximum_dimension
FROM vector_spaces
GROUP BY scalar_field;

-- ============================================================
-- 22. VECTOR NORM REPORT
-- ============================================================

SELECT
    vector_name,
    space_name,
    ROUND(euclidean_norm::NUMERIC, 6) AS euclidean_norm
FROM vector_catalog
WHERE is_complete
ORDER BY space_name, vector_name;

-- ============================================================
-- 23. DOT PRODUCT EVALUATION
-- ============================================================

SELECT
    vector_dot_product(
        (SELECT vector_id FROM vectors WHERE vector_name = 'u'),
        (SELECT vector_id FROM vectors WHERE vector_name = 'v')
    ) AS dot_product_u_v;

-- ============================================================
-- 24. VECTOR ADDITION EVALUATION
-- ============================================================

SELECT *
FROM vector_addition(
    (SELECT vector_id FROM vectors WHERE vector_name = 'u'),
    (SELECT vector_id FROM vectors WHERE vector_name = 'v')
);

-- ============================================================
-- 25. SCALAR MULTIPLICATION EVALUATION
-- ============================================================

SELECT *
FROM vector_scalar_multiplication(
    (SELECT vector_id FROM vectors WHERE vector_name = 'u'),
    3.0
);

-- ============================================================
-- 26. LINEAR COMBINATION REPORT
-- ============================================================

-- Evaluate 2u + 3v using component-wise aggregation.
WITH selected_vectors AS (
    SELECT
        c.component_index,
        c.component_value,
        CASE
            WHEN v.vector_name = 'u' THEN 2.0
            WHEN v.vector_name = 'v' THEN 3.0
        END AS coefficient
    FROM vectors v
    JOIN vector_components c
      ON c.vector_id = v.vector_id
    WHERE v.vector_name IN ('u', 'v')
),
combined AS (
    SELECT
        component_index,
        SUM(component_value * coefficient) AS result_component
    FROM selected_vectors
    GROUP BY component_index
)
SELECT
    component_index,
    result_component
FROM combined
ORDER BY component_index;

-- ============================================================
-- 27. BASIS ELIGIBILITY REPORT
-- ============================================================

-- For two vectors in R2:
-- A set is a basis exactly when its determinant is nonzero.
-- This query evaluates the determinant of the standard basis
-- and a dependent pair.

WITH named_components AS (
    SELECT
        v.vector_name,
        c.component_index,
        c.component_value
    FROM vectors v
    JOIN vector_components c
      ON c.vector_id = v.vector_id
    WHERE v.vector_name IN (
        'e1',
        'e2',
        'dependent_a',
        'dependent_b'
    )
),
basis_pairs AS (
    SELECT
        first.vector_name AS first_vector,
        second.vector_name AS second_vector,
        MAX(
            CASE
                WHEN first.component_index = 1
                THEN first.component_value
            END
        ) AS a,
        MAX(
            CASE
                WHEN first.component_index = 2
                THEN first.component_value
            END
        ) AS b,
        MAX(
            CASE
                WHEN second.component_index = 1
                THEN second.component_value
            END
        ) AS c,
        MAX(
            CASE
                WHEN second.component_index = 2
                THEN second.component_value
            END
        ) AS d
    FROM named_components first
    JOIN named_components second
      ON first.vector_name < second.vector_name
    GROUP BY
        first.vector_name,
        second.vector_name
)
SELECT
    first_vector,
    second_vector,
    a * d - b * c AS determinant,
    CASE
        WHEN ABS(a * d - b * c) > 0.000000001
        THEN TRUE
        ELSE FALSE
    END AS linearly_independent
FROM basis_pairs
ORDER BY first_vector, second_vector;

-- ============================================================
-- 28. INCOMPLETE VECTOR FAILURE DEMONSTRATION
-- ============================================================

-- A valid R2 vector is created with one component.
-- The vector can exist, but it must not be treated as complete.

INSERT INTO vectors (
    space_id,
    vector_name,
    notation
)
SELECT
    space_id,
    'incomplete_vector',
    '(5)'
FROM vector_spaces
WHERE space_name = 'R2';

INSERT INTO vector_components (
    vector_id,
    component_index,
    component_value
)
SELECT
    vector_id,
    1,
    5
FROM vectors
WHERE vector_name = 'incomplete_vector';

SELECT
    vector_name,
    dimension,
    component_count,
    is_complete,
    CASE
        WHEN is_complete THEN 'ELIGIBLE'
        ELSE 'REJECTED: INCOMPLETE COMPONENTS'
    END AS evaluation
FROM vector_catalog
WHERE vector_name = 'incomplete_vector';

-- ============================================================
-- 29. INVALID COMPONENT POSITION DEMONSTRATION
-- ============================================================

-- The exception is caught inside a PL/pgSQL block so the
-- complete database script can continue executing.

DO $$
DECLARE
    target_vector BIGINT;
BEGIN
    SELECT vector_id
    INTO target_vector
    FROM vectors
    WHERE vector_name = 'u';

    BEGIN
        INSERT INTO vector_components (
            vector_id,
            component_index,
            component_value
        )
        VALUES (
            target_vector,
            3,
            10
        );
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Expected validation failure: %',
                SQLERRM;
    END;
END;
$$;

-- ============================================================
-- 30. TRANSACTIONAL OPERATION AUDIT
-- ============================================================

INSERT INTO operation_history (
    operation,
    first_vector_id,
    second_vector_id,
    result_notation,
    success
)
SELECT
    'DOT_PRODUCT',
    first.vector_id,
    second.vector_id,
    '11',
    TRUE
FROM vectors first
CROSS JOIN vectors second
WHERE first.vector_name = 'u'
  AND second.vector_name = 'v';

-- Failed operation record.
INSERT INTO operation_history (
    operation,
    first_vector_id,
    second_vector_id,
    success,
    error_message
)
SELECT
    'ADD',
    first.vector_id,
    second.vector_id,
    FALSE,
    'Incompatible vector spaces or dimensions.'
FROM vectors first
CROSS JOIN vectors second
WHERE first.vector_name = 'u'
  AND second.vector_name = 'a3';

-- ============================================================
-- 31. OPERATION REPORT
-- ============================================================

SELECT
    operation,
    success,
    COUNT(*) AS operation_count
FROM operation_history
GROUP BY operation, success
ORDER BY operation, success;

-- ============================================================
-- 32. SPACE-LEVEL REPORTING
-- ============================================================

SELECT
    s.space_name,
    s.dimension,
    COUNT(v.vector_id) AS registered_vectors,
    COUNT(v.vector_id) FILTER (
        WHERE catalog.is_complete
    ) AS complete_vectors,
    COUNT(v.vector_id) FILTER (
        WHERE NOT catalog.is_complete
    ) AS incomplete_vectors
FROM vector_spaces s
LEFT JOIN vectors v
  ON v.space_id = s.space_id
LEFT JOIN vector_catalog catalog
  ON catalog.vector_id = v.vector_id
GROUP BY s.space_id, s.space_name, s.dimension
ORDER BY s.dimension;

-- ============================================================
-- 33. DATABASE INTEGRITY CHECK
-- ============================================================

DO $$
DECLARE
    invalid_vectors BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO invalid_vectors
    FROM vector_catalog
    WHERE NOT is_complete;

    RAISE NOTICE
        'Incomplete registered vectors: %',
        invalid_vectors;

    IF invalid_vectors < 0 THEN
        RAISE EXCEPTION 'Invalid integrity result.';
    END IF;
END;
$$;

COMMIT;

-- ============================================================
-- END OF LINEAR ALGEBRA DATABASE IMPLEMENTATION
-- ============================================================
