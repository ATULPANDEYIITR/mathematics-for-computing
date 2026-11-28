-- ============================================================
-- VECTOR OPERATIONS DATABASE
-- PostgreSQL 14+
-- Operations: Addition, scalar multiplication, dot product,
-- L1 norm, L2 norm, infinity norm and cosine similarity.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS vector_lab;

SET search_path TO vector_lab, public;

-- ------------------------------------------------------------
-- 1. DOMAIN TABLES
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS vectors (
    vector_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vector_name VARCHAR(100) NOT NULL UNIQUE,
    dimension INTEGER NOT NULL CHECK (dimension > 0),
    components DOUBLE PRECISION[] NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT vector_components_dimension
        CHECK (
            array_ndims(components) = 1
            AND array_lower(components, 1) = 1
            AND cardinality(components) = dimension
        )
);

CREATE TABLE IF NOT EXISTS operation_types (
    operation_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    operation_code VARCHAR(40) NOT NULL UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vector_operations (
    operation_record_id BIGINT
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    operation_id SMALLINT NOT NULL
        REFERENCES operation_types(operation_id),

    first_vector_id BIGINT NOT NULL
        REFERENCES vectors(vector_id),

    second_vector_id BIGINT
        REFERENCES vectors(vector_id),

    scalar_value DOUBLE PRECISION,

    result_vector_id BIGINT
        REFERENCES vectors(vector_id),

    numeric_result DOUBLE PRECISION,

    execution_status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (
            execution_status IN (
                'PENDING', 'COMPLETED', 'FAILED'
            )
        ),

    error_message TEXT,

    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (
        (execution_status = 'COMPLETED' AND error_message IS NULL)
        OR
        (execution_status = 'FAILED' AND error_message IS NOT NULL)
        OR
        (execution_status = 'PENDING')
    )
);

CREATE TABLE IF NOT EXISTS operation_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    operation_record_id BIGINT NOT NULL
        REFERENCES vector_operations(operation_record_id),
    previous_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- 2. INDEXES
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_vectors_dimension
    ON vectors(dimension);

CREATE INDEX IF NOT EXISTS idx_operations_status
    ON vector_operations(execution_status, executed_at DESC);

CREATE INDEX IF NOT EXISTS idx_operations_first_vector
    ON vector_operations(first_vector_id);

CREATE INDEX IF NOT EXISTS idx_operations_second_vector
    ON vector_operations(second_vector_id);

-- ------------------------------------------------------------
-- 3. VALIDATION FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_vector(
    p_values DOUBLE PRECISION[]
)
RETURNS BOOLEAN
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    v_value DOUBLE PRECISION;
BEGIN
    IF array_ndims(p_values) IS DISTINCT FROM 1 THEN
        RETURN FALSE;
    END IF;

    IF array_lower(p_values, 1) IS DISTINCT FROM 1 THEN
        RETURN FALSE;
    END IF;

    IF cardinality(p_values) = 0 THEN
        RETURN FALSE;
    END IF;

    FOREACH v_value IN ARRAY p_values LOOP
        IF v_value IS NULL
           OR v_value = 'NaN'::DOUBLE PRECISION
           OR v_value = 'Infinity'::DOUBLE PRECISION
           OR v_value = '-Infinity'::DOUBLE PRECISION
        THEN
            RETURN FALSE;
        END IF;
    END LOOP;

    RETURN TRUE;
END;
$$;

-- ------------------------------------------------------------
-- 4. VECTOR REGISTRATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION register_vector(
    p_name VARCHAR,
    p_values DOUBLE PRECISION[]
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_id BIGINT;
BEGIN
    IF p_name IS NULL OR length(trim(p_name)) = 0 THEN
        RAISE EXCEPTION 'Vector name cannot be empty.';
    END IF;

    IF NOT validate_vector(p_values) THEN
        RAISE EXCEPTION 'Invalid vector components.';
    END IF;

    INSERT INTO vectors (
        vector_name,
        dimension,
        components
    )
    VALUES (
        p_name,
        cardinality(p_values),
        p_values
    )
    RETURNING vector_id INTO v_id;

    RETURN v_id;
END;
$$;

-- ------------------------------------------------------------
-- 5. ADDITION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION vector_add(
    p_first DOUBLE PRECISION[],
    p_second DOUBLE PRECISION[]
)
RETURNS DOUBLE PRECISION[]
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_result DOUBLE PRECISION[] := ARRAY[]::DOUBLE PRECISION[];
    i INTEGER;
BEGIN
    IF NOT validate_vector(p_first)
       OR NOT validate_vector(p_second)
    THEN
        RAISE EXCEPTION 'Invalid vector supplied to addition.';
    END IF;

    IF cardinality(p_first) <> cardinality(p_second) THEN
        RAISE EXCEPTION
            'Dimension mismatch: % != %',
            cardinality(p_first),
            cardinality(p_second);
    END IF;

    FOR i IN 1..cardinality(p_first) LOOP
        v_result := array_append(
            v_result,
            p_first[i] + p_second[i]
        );
    END LOOP;

    IF NOT validate_vector(v_result) THEN
        RAISE EXCEPTION 'Addition produced an invalid result.';
    END IF;

    RETURN v_result;
END;
$$;

-- ------------------------------------------------------------
-- 6. SCALAR MULTIPLICATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION vector_scale(
    p_values DOUBLE PRECISION[],
    p_scalar DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION[]
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_result DOUBLE PRECISION[] := ARRAY[]::DOUBLE PRECISION[];
    v_value DOUBLE PRECISION;
BEGIN
    IF NOT validate_vector(p_values) THEN
        RAISE EXCEPTION 'Invalid vector supplied to scaling.';
    END IF;

    IF p_scalar IS NULL
       OR p_scalar = 'NaN'::DOUBLE PRECISION
       OR p_scalar = 'Infinity'::DOUBLE PRECISION
       OR p_scalar = '-Infinity'::DOUBLE PRECISION
    THEN
        RAISE EXCEPTION 'Scalar must be finite.';
    END IF;

    FOREACH v_value IN ARRAY p_values LOOP
        v_result := array_append(
            v_result,
            v_value * p_scalar
        );
    END LOOP;

    IF NOT validate_vector(v_result) THEN
        RAISE EXCEPTION 'Scalar multiplication produced invalid output.';
    END IF;

    RETURN v_result;
END;
$$;

-- ------------------------------------------------------------
-- 7. DOT PRODUCT
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION vector_dot(
    p_first DOUBLE PRECISION[],
    p_second DOUBLE PRECISION[]
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_result DOUBLE PRECISION := 0;
    i INTEGER;
BEGIN
    IF NOT validate_vector(p_first)
       OR NOT validate_vector(p_second)
    THEN
        RAISE EXCEPTION 'Invalid vector supplied to dot product.';
    END IF;

    IF cardinality(p_first) <> cardinality(p_second) THEN
        RAISE EXCEPTION 'Dot product requires equal dimensions.';
    END IF;

    FOR i IN 1..cardinality(p_first) LOOP
        v_result := v_result + p_first[i] * p_second[i];
    END LOOP;

    IF v_result = 'NaN'::DOUBLE PRECISION
       OR v_result = 'Infinity'::DOUBLE PRECISION
       OR v_result = '-Infinity'::DOUBLE PRECISION
    THEN
        RAISE EXCEPTION 'Dot product overflowed.';
    END IF;

    RETURN v_result;
END;
$$;

-- ------------------------------------------------------------
-- 8. L1 NORM
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION vector_l1_norm(
    p_values DOUBLE PRECISION[]
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_result DOUBLE PRECISION := 0;
    v_value DOUBLE PRECISION;
BEGIN
    IF NOT validate_vector(p_values) THEN
        RAISE EXCEPTION 'Invalid vector supplied to L1 norm.';
    END IF;

    FOREACH v_value IN ARRAY p_values LOOP
        v_result := v_result + abs(v_value);
    END LOOP;

    IF NOT isfinite(v_result) THEN
        RAISE EXCEPTION 'L1 norm overflowed.';
    END IF;

    RETURN v_result;
END;
$$;

-- ------------------------------------------------------------
-- 9. L2 NORM
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION vector_l2_norm(
    p_values DOUBLE PRECISION[]
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_result DOUBLE PRECISION := 0;
    v_value DOUBLE PRECISION;
BEGIN
    IF NOT validate_vector(p_values) THEN
        RAISE EXCEPTION 'Invalid vector supplied to L2 norm.';
    END IF;

    -- Iterative hypot is more stable than directly summing squares.
    FOREACH v_value IN ARRAY p_values LOOP
        v_result := hypot(v_result, v_value);
    END LOOP;

    IF NOT isfinite(v_result) THEN
        RAISE EXCEPTION 'L2 norm overflowed.';
    END IF;

    RETURN v_result;
END;
$$;

-- ------------------------------------------------------------
-- 10. INFINITY NORM
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION vector_infinity_norm(
    p_values DOUBLE PRECISION[]
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_result DOUBLE PRECISION := 0;
    v_value DOUBLE PRECISION;
BEGIN
    IF NOT validate_vector(p_values) THEN
        RAISE EXCEPTION 'Invalid vector supplied to infinity norm.';
    END IF;

    FOREACH v_value IN ARRAY p_values LOOP
        v_result := greatest(v_result, abs(v_value));
    END LOOP;

    RETURN v_result;
END;
$$;

-- ------------------------------------------------------------
-- 11. NORMALIZATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION vector_normalize(
    p_values DOUBLE PRECISION[]
)
RETURNS DOUBLE PRECISION[]
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_magnitude DOUBLE PRECISION;
BEGIN
    v_magnitude := vector_l2_norm(p_values);

    IF v_magnitude = 0 THEN
        RAISE EXCEPTION 'Zero vector cannot be normalized.';
    END IF;

    RETURN vector_scale(p_values, 1.0 / v_magnitude);
END;
$$;

-- ------------------------------------------------------------
-- 12. COSINE SIMILARITY
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION vector_cosine_similarity(
    p_first DOUBLE PRECISION[],
    p_second DOUBLE PRECISION[]
)
RETURNS DOUBLE PRECISION
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_first_norm DOUBLE PRECISION;
    v_second_norm DOUBLE PRECISION;
    v_result DOUBLE PRECISION;
BEGIN
    IF cardinality(p_first) <> cardinality(p_second) THEN
        RAISE EXCEPTION 'Cosine similarity requires equal dimensions.';
    END IF;

    v_first_norm := vector_l2_norm(p_first);
    v_second_norm := vector_l2_norm(p_second);

    IF v_first_norm = 0 OR v_second_norm = 0 THEN
        RAISE EXCEPTION
            'Cosine similarity is undefined for zero vectors.';
    END IF;

    v_result := vector_dot(p_first, p_second)
                / v_first_norm
                / v_second_norm;

    RETURN greatest(-1.0, least(1.0, v_result));
END;
$$;

-- ------------------------------------------------------------
-- 13. OPERATION AUDIT TRIGGER
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION audit_operation_status()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO operation_audit (
            operation_record_id,
            previous_status,
            new_status
        )
        VALUES (
            NEW.operation_record_id,
            NULL,
            NEW.execution_status
        );

    ELSIF OLD.execution_status IS DISTINCT FROM NEW.execution_status THEN
        INSERT INTO operation_audit (
            operation_record_id,
            previous_status,
            new_status
        )
        VALUES (
            NEW.operation_record_id,
            OLD.execution_status,
            NEW.execution_status
        );
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_operation_audit
    ON vector_operations;

CREATE TRIGGER trg_operation_audit
AFTER INSERT OR UPDATE OF execution_status
ON vector_operations
FOR EACH ROW
EXECUTE FUNCTION audit_operation_status();

-- ------------------------------------------------------------
-- 14. OPERATION EXECUTION PROCEDURE
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE execute_vector_operation(
    p_operation VARCHAR,
    p_first_id BIGINT,
    p_second_id BIGINT DEFAULT NULL,
    p_scalar DOUBLE PRECISION DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_first DOUBLE PRECISION[];
    v_second DOUBLE PRECISION[];
    v_result_vector DOUBLE PRECISION[];
    v_result_numeric DOUBLE PRECISION;
    v_operation_id SMALLINT;
    v_record_id BIGINT;
BEGIN
    SELECT operation_id
    INTO v_operation_id
    FROM operation_types
    WHERE operation_code = p_operation;

    IF v_operation_id IS NULL THEN
        RAISE EXCEPTION 'Unknown operation: %', p_operation;
    END IF;

    SELECT components
    INTO STRICT v_first
    FROM vectors
    WHERE vector_id = p_first_id;

    IF p_operation IN (
        'addition', 'dot_product'
    ) THEN
        IF p_second_id IS NULL THEN
            RAISE EXCEPTION 'Second vector is required.';
        END IF;

        SELECT components
        INTO STRICT v_second
        FROM vectors
        WHERE vector_id = p_second_id;
    END IF;

    IF p_operation = 'addition' THEN
        v_result_vector := vector_add(v_first, v_second);

    ELSIF p_operation = 'scalar_multiplication' THEN
        v_result_vector := vector_scale(v_first, p_scalar);

    ELSIF p_operation = 'dot_product' THEN
        v_result_numeric := vector_dot(v_first, v_second);

    ELSIF p_operation = 'l1_norm' THEN
        v_result_numeric := vector_l1_norm(v_first);

    ELSIF p_operation = 'l2_norm' THEN
        v_result_numeric := vector_l2_norm(v_first);

    ELSIF p_operation = 'infinity_norm' THEN
        v_result_numeric := vector_infinity_norm(v_first);

    ELSIF p_operation = 'normalization' THEN
        v_result_vector := vector_normalize(v_first);

    ELSE
        RAISE EXCEPTION 'Unsupported operation.';
    END IF;

    INSERT INTO vector_operations (
        operation_id,
        first_vector_id,
        second_vector_id,
        scalar_value,
        execution_status
    )
    VALUES (
        v_operation_id,
        p_first_id,
        p_second_id,
        p_scalar,
        'PENDING'
    )
    RETURNING operation_record_id INTO v_record_id;

    IF v_result_vector IS NOT NULL THEN
        INSERT INTO vectors (
            vector_name,
            dimension,
            components
        )
        VALUES (
            'result_' || v_record_id,
            cardinality(v_result_vector),
            v_result_vector
        )
        RETURNING vector_id INTO v_result_numeric;

        UPDATE vector_operations
        SET result_vector_id = v_result_numeric::BIGINT,
            execution_status = 'COMPLETED'
        WHERE operation_record_id = v_record_id;
    ELSE
        UPDATE vector_operations
        SET numeric_result = v_result_numeric,
            execution_status = 'COMPLETED'
        WHERE operation_record_id = v_record_id;
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        -- Preserve failure details in a separate transaction boundary
        -- when the caller chooses to handle this procedure's exception.
        RAISE;
END;
$$;

-- ------------------------------------------------------------
-- 15. OPERATION CATALOG
-- ------------------------------------------------------------

INSERT INTO operation_types (operation_code, description)
VALUES
    ('addition', 'Element-wise addition of two vectors'),
    ('scalar_multiplication', 'Multiplication by a scalar'),
    ('dot_product', 'Sum of pairwise component products'),
    ('l1_norm', 'Sum of absolute component values'),
    ('l2_norm', 'Euclidean vector magnitude'),
    ('infinity_norm', 'Maximum absolute component'),
    ('normalization', 'Unit vector using Euclidean norm')
ON CONFLICT (operation_code) DO NOTHING;

-- ------------------------------------------------------------
-- 16. SAMPLE DATA
-- ------------------------------------------------------------

INSERT INTO vectors (
    vector_name,
    dimension,
    components
)
VALUES
    ('vector_u', 2, ARRAY[3.0, 4.0]::DOUBLE PRECISION[]),
    ('vector_v', 2, ARRAY[4.0, 3.0]::DOUBLE PRECISION[]),
    ('unit_x', 2, ARRAY[1.0, 0.0]::DOUBLE PRECISION[]),
    ('unit_y', 2, ARRAY[0.0, 1.0]::DOUBLE PRECISION[]),
    ('zero_vector', 2, ARRAY[0.0, 0.0]::DOUBLE PRECISION[]),
    ('high_dimension', 5, ARRAY[1.0, 2.0, 3.0, 4.0, 5.0]::DOUBLE PRECISION[])
ON CONFLICT (vector_name) DO NOTHING;

-- ------------------------------------------------------------
-- 17. RETRIEVAL QUERIES
-- ------------------------------------------------------------

SELECT
    vector_id,
    vector_name,
    dimension,
    components,
    created_at
FROM vectors
ORDER BY vector_id;

-- ------------------------------------------------------------
-- 18. ADDITION
-- ------------------------------------------------------------

SELECT vector_add(
    ARRAY[3.0, 4.0]::DOUBLE PRECISION[],
    ARRAY[4.0, 3.0]::DOUBLE PRECISION[]
) AS addition_result;

-- ------------------------------------------------------------
-- 19. SCALAR MULTIPLICATION
-- ------------------------------------------------------------

SELECT vector_scale(
    ARRAY[3.0, 4.0]::DOUBLE PRECISION[],
    3.0
) AS scaled_vector;

-- ------------------------------------------------------------
-- 20. DOT PRODUCT
-- ------------------------------------------------------------

SELECT vector_dot(
    ARRAY[3.0, 4.0]::DOUBLE PRECISION[],
    ARRAY[4.0, 3.0]::DOUBLE PRECISION[]
) AS dot_product;

-- ------------------------------------------------------------
-- 21. NORM REPORT
-- ------------------------------------------------------------

SELECT
    vector_name,
    components,
    vector_l1_norm(components) AS l1_norm,
    vector_l2_norm(components) AS l2_norm,
    vector_infinity_norm(components) AS infinity_norm
FROM vectors
ORDER BY vector_id;

-- ------------------------------------------------------------
-- 22. NORMALIZATION
-- ------------------------------------------------------------

SELECT
    vector_name,
    vector_normalize(components) AS normalized_components
FROM vectors
WHERE vector_name IN ('vector_u', 'vector_v');

-- ------------------------------------------------------------
-- 23. CTE-BASED VECTOR COMPARISON
-- ------------------------------------------------------------

WITH selected_vectors AS (
    SELECT
        vector_name,
        components
    FROM vectors
    WHERE vector_name IN ('vector_u', 'vector_v')
),
comparison AS (
    SELECT
        a.vector_name AS first_vector,
        b.vector_name AS second_vector,
        a.components AS first_components,
        b.components AS second_components
    FROM selected_vectors a
    CROSS JOIN selected_vectors b
    WHERE a.vector_name = 'vector_u'
      AND b.vector_name = 'vector_v'
)
SELECT
    first_vector,
    second_vector,
    vector_add(first_components, second_components) AS addition,
    vector_dot(first_components, second_components) AS dot_product,
    vector_l2_norm(
        vector_add(
            first_components,
            vector_scale(second_components, -1.0)
        )
    ) AS euclidean_distance,
    vector_cosine_similarity(
        first_components,
        second_components
    ) AS cosine_similarity
FROM comparison;

-- ------------------------------------------------------------
-- 24. AGGREGATION AND DIMENSION REPORT
-- ------------------------------------------------------------

SELECT
    dimension,
    COUNT(*) AS vector_count,
    AVG(vector_l2_norm(components)) AS average_l2_norm,
    MAX(vector_infinity_norm(components)) AS maximum_component_magnitude
FROM vectors
GROUP BY dimension
ORDER BY dimension;

-- ------------------------------------------------------------
-- 25. OPERATION WORKFLOW
-- ------------------------------------------------------------

-- Execute a dot product through the database service procedure.
CALL execute_vector_operation(
    'dot_product',
    (SELECT vector_id FROM vectors WHERE vector_name = 'vector_u'),
    (SELECT vector_id FROM vectors WHERE vector_name = 'vector_v')
);

-- Execute addition.
CALL execute_vector_operation(
    'addition',
    (SELECT vector_id FROM vectors WHERE vector_name = 'vector_u'),
    (SELECT vector_id FROM vectors WHERE vector_name = 'vector_v')
);

-- Execute scalar multiplication.
CALL execute_vector_operation(
    'scalar_multiplication',
    (SELECT vector_id FROM vectors WHERE vector_name = 'vector_u'),
    NULL,
    2.0
);

-- ------------------------------------------------------------
-- 26. EXECUTION REPORT
-- ------------------------------------------------------------

SELECT
    operation_record_id,
    operation_code,
    first_vector_id,
    second_vector_id,
    scalar_value,
    numeric_result,
    result_vector_id,
    execution_status,
    executed_at
FROM vector_operations operation
JOIN operation_types type
    ON type.operation_id = operation.operation_id
ORDER BY operation_record_id DESC;

-- ------------------------------------------------------------
-- 27. AUDIT REPORT
-- ------------------------------------------------------------

SELECT
    audit_id,
    operation_record_id,
    previous_status,
    new_status,
    changed_at
FROM operation_audit
ORDER BY audit_id;

-- ------------------------------------------------------------
-- 28. VALIDATION REPORT
-- ------------------------------------------------------------

SELECT
    vector_name,
    dimension,
    validate_vector(components) AS valid_vector,
    cardinality(components) = dimension AS dimension_consistent
FROM vectors
ORDER BY vector_id;

-- ------------------------------------------------------------
-- 29. ELIGIBILITY AND NUMERICAL EVALUATION
-- ------------------------------------------------------------

SELECT
    vector_name,
    CASE
        WHEN vector_l2_norm(components) = 0
            THEN 'NOT_NORMALIZABLE'
        WHEN validate_vector(components)
            THEN 'VALID_AND_NORMALIZABLE'
        ELSE 'INVALID'
    END AS normalization_eligibility
FROM vectors;

-- ------------------------------------------------------------
-- 30. TRANSACTION DEMONSTRATION
-- ------------------------------------------------------------

SAVEPOINT vector_transaction_test;

INSERT INTO vectors (
    vector_name,
    dimension,
    components
)
VALUES (
    'temporary_vector',
    3,
    ARRAY[7.0, 8.0, 9.0]::DOUBLE PRECISION[]
);

SELECT vector_l2_norm(components)
FROM vectors
WHERE vector_name = 'temporary_vector';

ROLLBACK TO SAVEPOINT vector_transaction_test;

RELEASE SAVEPOINT vector_transaction_test;

COMMIT;
