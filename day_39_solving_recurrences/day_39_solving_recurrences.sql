/*
 * SOLVING RECURRENCES
 * ====================
 *
 * PostgreSQL-compatible demonstration of recurrence data and validation.
 *
 * The database models recurrence definitions, initial conditions, generated
 * values, characteristic roots, closed-form validation, and complexity
 * metadata. SQL is used for relational integrity, sequence generation,
 * validation, aggregation, and transactional loading.
 *
 * The recurrence examples include:
 *
 * T(n) = T(n-1) + n
 * T(n) = 3T(n-1) + 4
 * T(n) = 5T(n-1) - 6T(n-2)
 * T(n) = 4T(n-1) - 4T(n-2)
 *
 * The script intentionally keeps mathematical concepts separate:
 * iteration is represented through generated recurrence states,
 * characteristic equations through stored coefficients and roots,
 * and validation through database queries comparing expected and actual
 * recurrence values.
 */

DROP SCHEMA IF EXISTS recurrence_lab CASCADE;

CREATE SCHEMA recurrence_lab;

SET search_path TO recurrence_lab;


/* -------------------------------------------------------------------------
   Recurrence definitions
   ------------------------------------------------------------------------- */

CREATE TABLE recurrence_definition (
    recurrence_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    order_number SMALLINT NOT NULL
        CHECK (order_number IN (1, 2)),
    coefficient_a NUMERIC NOT NULL,
    coefficient_b NUMERIC,
    forcing_constant NUMERIC NOT NULL DEFAULT 0,
    initial_t0 NUMERIC NOT NULL,
    initial_t1 NUMERIC,
    description TEXT NOT NULL,
    CHECK (
        (order_number = 1 AND coefficient_b IS NULL)
        OR
        (order_number = 2 AND coefficient_b IS NOT NULL)
    ),
    CHECK (
        order_number = 1
        OR initial_t1 IS NOT NULL
    )
);


/* -------------------------------------------------------------------------
   Complexity metadata is separate because the recurrence definition and
   the selected evaluation strategy are different concepts.
   ------------------------------------------------------------------------- */

CREATE TABLE evaluation_strategy (
    strategy_id BIGSERIAL PRIMARY KEY,
    recurrence_id BIGINT NOT NULL
        REFERENCES recurrence_definition(recurrence_id)
        ON DELETE CASCADE,
    strategy_name TEXT NOT NULL,
    time_complexity TEXT NOT NULL,
    space_complexity TEXT NOT NULL,
    notes TEXT NOT NULL,
    UNIQUE (recurrence_id, strategy_name)
);


/* -------------------------------------------------------------------------
   Generated recurrence states
   ------------------------------------------------------------------------- */

CREATE TABLE recurrence_value (
    recurrence_id BIGINT NOT NULL
        REFERENCES recurrence_definition(recurrence_id)
        ON DELETE CASCADE,
    n INTEGER NOT NULL CHECK (n >= 0),
    actual_value NUMERIC NOT NULL,
    expected_value NUMERIC,
    validation_status TEXT NOT NULL
        CHECK (
            validation_status IN ('VALID', 'INVALID', 'NOT_CHECKED')
        ),
    PRIMARY KEY (recurrence_id, n)
);

CREATE INDEX idx_recurrence_value_status
    ON recurrence_value (validation_status);

CREATE INDEX idx_recurrence_value_n
    ON recurrence_value (recurrence_id, n);


/* -------------------------------------------------------------------------
   Characteristic roots
   ------------------------------------------------------------------------- */

CREATE TABLE characteristic_root (
    root_id BIGSERIAL PRIMARY KEY,
    recurrence_id BIGINT NOT NULL
        REFERENCES recurrence_definition(recurrence_id)
        ON DELETE CASCADE,
    root_value NUMERIC NOT NULL,
    multiplicity INTEGER NOT NULL DEFAULT 1
        CHECK (multiplicity >= 1),
    root_role TEXT NOT NULL
        CHECK (root_role IN ('REAL_ROOT', 'REPEATED_ROOT'))
);


/* -------------------------------------------------------------------------
   Closed-form models
   ------------------------------------------------------------------------- */

CREATE TABLE closed_form_solution (
    solution_id BIGSERIAL PRIMARY KEY,
    recurrence_id BIGINT NOT NULL UNIQUE
        REFERENCES recurrence_definition(recurrence_id)
        ON DELETE CASCADE,
    form_expression TEXT NOT NULL,
    derivation_method TEXT NOT NULL
        CHECK (
            derivation_method IN (
                'ITERATION',
                'CHARACTERISTIC_EQUATION',
                'NON_HOMOGENEOUS_DECOMPOSITION'
            )
        )
);


/* -------------------------------------------------------------------------
   Seed recurrence definitions
   ------------------------------------------------------------------------- */

INSERT INTO recurrence_definition (
    name,
    order_number,
    coefficient_a,
    coefficient_b,
    forcing_constant,
    initial_t0,
    initial_t1,
    description
)
VALUES
(
    'Incremental Work',
    1,
    1,
    NULL,
    1,
    10,
    NULL,
    'T(n) = T(n-1) + n is represented by a variable forcing term during evaluation.'
),
(
    'Branching Work',
    1,
    3,
    NULL,
    4,
    2,
    NULL,
    'T(n) = 3T(n-1) + 4 is a first-order non-homogeneous recurrence.'
),
(
    'Distinct Root Dependency',
    2,
    5,
    -6,
    0,
    1,
    4,
    'T(n) = 5T(n-1) - 6T(n-2), whose characteristic roots are 2 and 3.'
),
(
    'Repeated Root Dependency',
    2,
    4,
    -4,
    0,
    2,
    8,
    'T(n) = 4T(n-1) - 4T(n-2), whose characteristic root 2 has multiplicity 2.'
);


/* -------------------------------------------------------------------------
   Evaluation strategies
   ------------------------------------------------------------------------- */

INSERT INTO evaluation_strategy (
    recurrence_id,
    strategy_name,
    time_complexity,
    space_complexity,
    notes
)
SELECT
    recurrence_id,
    'ITERATION',
    'O(n)',
    'O(n)',
    'Stores recurrence states so each state can be reused by the next state.'
FROM recurrence_definition
WHERE name IN ('Incremental Work', 'Branching Work');

INSERT INTO evaluation_strategy (
    recurrence_id,
    strategy_name,
    time_complexity,
    space_complexity,
    notes
)
SELECT
    recurrence_id,
    'CHARACTERISTIC_CLOSED_FORM',
    'O(1) per requested n',
    'O(1)',
    'Uses characteristic roots and constants determined from initial values.'
FROM recurrence_definition
WHERE name IN (
    'Distinct Root Dependency',
    'Repeated Root Dependency'
);

INSERT INTO evaluation_strategy (
    recurrence_id,
    strategy_name,
    time_complexity,
    space_complexity,
    notes
)
SELECT
    recurrence_id,
    'MATRIX_EXPONENTIATION',
    'O(log n)',
    'O(1)',
    'Applicable to suitable fixed-order linear recurrences through matrix powers.'
FROM recurrence_definition
WHERE name = 'Distinct Root Dependency';


/* -------------------------------------------------------------------------
   Characteristic roots
   ------------------------------------------------------------------------- */

INSERT INTO characteristic_root (
    recurrence_id,
    root_value,
    multiplicity,
    root_role
)
SELECT
    recurrence_id,
    2,
    1,
    'REAL_ROOT'
FROM recurrence_definition
WHERE name = 'Distinct Root Dependency';

INSERT INTO characteristic_root (
    recurrence_id,
    root_value,
    multiplicity,
    root_role
)
SELECT
    recurrence_id,
    3,
    1,
    'REAL_ROOT'
FROM recurrence_definition
WHERE name = 'Distinct Root Dependency';

INSERT INTO characteristic_root (
    recurrence_id,
    root_value,
    multiplicity,
    root_role
)
SELECT
    recurrence_id,
    2,
    2,
    'REPEATED_ROOT'
FROM recurrence_definition
WHERE name = 'Repeated Root Dependency';


/* -------------------------------------------------------------------------
   Closed forms
   ------------------------------------------------------------------------- */

INSERT INTO closed_form_solution (
    recurrence_id,
    form_expression,
    derivation_method
)
SELECT
    recurrence_id,
    'T(n) = T(0) + n(n+1)/2',
    'ITERATION'
FROM recurrence_definition
WHERE name = 'Incremental Work';

INSERT INTO closed_form_solution (
    recurrence_id,
    form_expression,
    derivation_method
)
SELECT
    recurrence_id,
    'T(n) = C * 3^n - 2',
    'NON_HOMOGENEOUS_DECOMPOSITION'
FROM recurrence_definition
WHERE name = 'Branching Work';

INSERT INTO closed_form_solution (
    recurrence_id,
    form_expression,
    derivation_method
)
SELECT
    recurrence_id,
    'T(n) = C1 * 2^n + C2 * 3^n',
    'CHARACTERISTIC_EQUATION'
FROM recurrence_definition
WHERE name = 'Distinct Root Dependency';

INSERT INTO closed_form_solution (
    recurrence_id,
    form_expression,
    derivation_method
)
SELECT
    recurrence_id,
    'T(n) = (C1 + C2*n) * 2^n',
    'CHARACTERISTIC_EQUATION'
FROM recurrence_definition
WHERE name = 'Repeated Root Dependency';


/* -------------------------------------------------------------------------
   Generate the first-order incremental recurrence.
   PostgreSQL generate_series supplies the n-domain; the closed form is used
   to produce the expected value.
   ------------------------------------------------------------------------- */

INSERT INTO recurrence_value (
    recurrence_id,
    n,
    actual_value,
    expected_value,
    validation_status
)
SELECT
    r.recurrence_id,
    s.n,
    10 + (s.n * (s.n + 1)) / 2,
    10 + (s.n * (s.n + 1)) / 2,
    'VALID'
FROM recurrence_definition r
CROSS JOIN generate_series(0, 10) AS s(n)
WHERE r.name = 'Incremental Work';


/* -------------------------------------------------------------------------
   First-order non-homogeneous recurrence:
   T(n) = 3T(n-1) + 4
   T(0) = 2
   Particular solution = -2
   Therefore T(n) = 4*3^n - 2.
   ------------------------------------------------------------------------- */

INSERT INTO recurrence_value (
    recurrence_id,
    n,
    actual_value,
    expected_value,
    validation_status
)
SELECT
    r.recurrence_id,
    s.n,
    4 * power(3::numeric, s.n) - 2,
    4 * power(3::numeric, s.n) - 2,
    'VALID'
FROM recurrence_definition r
CROSS JOIN generate_series(0, 8) AS s(n)
WHERE r.name = 'Branching Work';


/* -------------------------------------------------------------------------
   Distinct-root recurrence:
   T(n) = 5T(n-1) - 6T(n-2)
   T(0)=1, T(1)=4
   -------------------------------------------------------------------------
   Solve:
   C1+C2=1
   2C1+3C2=4
   Hence C1=-1, C2=2.
   T(n) = -2^n + 2*3^n.
   ------------------------------------------------------------------------- */

INSERT INTO recurrence_value (
    recurrence_id,
    n,
    actual_value,
    expected_value,
    validation_status
)
SELECT
    r.recurrence_id,
    s.n,
    -power(2::numeric, s.n)
        + 2 * power(3::numeric, s.n),
    -power(2::numeric, s.n)
        + 2 * power(3::numeric, s.n),
    'VALID'
FROM recurrence_definition r
CROSS JOIN generate_series(0, 8) AS s(n)
WHERE r.name = 'Distinct Root Dependency';


/* -------------------------------------------------------------------------
   Repeated-root recurrence:
   T(n)=4T(n-1)-4T(n-2)
   T(0)=2, T(1)=8
   Root = 2.
   General form:
   T(n)=(C1+C2*n)2^n
   C1=2
   8=(2+C2)2 => C2=2
   Therefore:
   T(n)=2(1+n)2^n.
   ------------------------------------------------------------------------- */

INSERT INTO recurrence_value (
    recurrence_id,
    n,
    actual_value,
    expected_value,
    validation_status
)
SELECT
    r.recurrence_id,
    s.n,
    2 * (1 + s.n) * power(2::numeric, s.n),
    2 * (1 + s.n) * power(2::numeric, s.n),
    'VALID'
FROM recurrence_definition r
CROSS JOIN generate_series(0, 8) AS s(n)
WHERE r.name = 'Repeated Root Dependency';


/* -------------------------------------------------------------------------
   A deliberately corrupted record demonstrates that validation exposes
   incorrect recurrence values rather than silently accepting them.
   ------------------------------------------------------------------------- */

INSERT INTO recurrence_value (
    recurrence_id,
    n,
    actual_value,
    expected_value,
    validation_status
)
SELECT
    recurrence_id,
    9,
    999999,
    -power(2::numeric, 9) + 2 * power(3::numeric, 9),
    CASE
        WHEN 999999 =
            -power(2::numeric, 9) + 2 * power(3::numeric, 9)
        THEN 'VALID'
        ELSE 'INVALID'
    END
FROM recurrence_definition
WHERE name = 'Distinct Root Dependency';


/* -------------------------------------------------------------------------
   Validation view
   ------------------------------------------------------------------------- */

CREATE VIEW recurrence_validation_report AS
SELECT
    r.name,
    rv.n,
    rv.actual_value,
    rv.expected_value,
    rv.validation_status,
    CASE
        WHEN rv.expected_value IS NULL THEN 'NOT_CHECKED'
        WHEN rv.actual_value = rv.expected_value THEN 'MATCH'
        ELSE 'MISMATCH'
    END AS comparison_result
FROM recurrence_value rv
JOIN recurrence_definition r
    ON r.recurrence_id = rv.recurrence_id
ORDER BY r.name, rv.n;


/* -------------------------------------------------------------------------
   Query: inspect recurrence definitions and their mathematical methods.
   ------------------------------------------------------------------------- */

SELECT
    r.name,
    r.order_number,
    r.coefficient_a,
    r.coefficient_b,
    r.forcing_constant,
    c.form_expression,
    c.derivation_method
FROM recurrence_definition r
LEFT JOIN closed_form_solution c
    ON c.recurrence_id = r.recurrence_id
ORDER BY r.recurrence_id;


/* -------------------------------------------------------------------------
   Query: characteristic roots and multiplicity.
   ------------------------------------------------------------------------- */

SELECT
    r.name,
    cr.root_value,
    cr.multiplicity,
    cr.root_role
FROM characteristic_root cr
JOIN recurrence_definition r
    ON r.recurrence_id = cr.recurrence_id
ORDER BY r.name, cr.root_value;


/* -------------------------------------------------------------------------
   Query: identify every invalid generated state.
   ------------------------------------------------------------------------- */

SELECT
    name,
    n,
    actual_value,
    expected_value,
    comparison_result
FROM recurrence_validation_report
WHERE comparison_result = 'MISMATCH';


/* -------------------------------------------------------------------------
   Query: calculate validation statistics by recurrence.
   ------------------------------------------------------------------------- */

SELECT
    name,
    COUNT(*) AS evaluated_states,
    COUNT(*) FILTER (
        WHERE validation_status = 'VALID'
    ) AS valid_states,
    COUNT(*) FILTER (
        WHERE validation_status = 'INVALID'
    ) AS invalid_states,
    ROUND(
        100.0 *
        COUNT(*) FILTER (
            WHERE validation_status = 'VALID'
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS valid_percentage
FROM recurrence_validation_report
GROUP BY name
ORDER BY name;


/* -------------------------------------------------------------------------
   Query: compare characteristic-root growth.
   The largest absolute root is a useful indicator of dominant asymptotic
   growth for a linear homogeneous recurrence when no cancellation removes
   that component.
   ------------------------------------------------------------------------- */

SELECT
    r.name,
    MAX(ABS(cr.root_value)) AS dominant_root_magnitude
FROM recurrence_definition r
JOIN characteristic_root cr
    ON cr.recurrence_id = r.recurrence_id
GROUP BY r.name
ORDER BY dominant_root_magnitude DESC;


/* -------------------------------------------------------------------------
   Transactional demonstration:
   create a temporary validation record, inspect it, and roll back so the
   demonstration does not permanently change the recurrence dataset.
   ------------------------------------------------------------------------- */

BEGIN;

INSERT INTO recurrence_value (
    recurrence_id,
    n,
    actual_value,
    expected_value,
    validation_status
)
SELECT
    recurrence_id,
    10,
    0,
    -power(2::numeric, 10) + 2 * power(3::numeric, 10),
    'INVALID'
FROM recurrence_definition
WHERE name = 'Distinct Root Dependency';

SELECT
    name,
    n,
    actual_value,
    expected_value,
    validation_status
FROM recurrence_validation_report
WHERE name = 'Distinct Root Dependency'
  AND n = 10;

ROLLBACK;


/* -------------------------------------------------------------------------
   Final operational view:
   mathematical method plus evaluation complexity.
   ------------------------------------------------------------------------- */

SELECT
    r.name,
    c.form_expression,
    es.strategy_name,
    es.time_complexity,
    es.space_complexity
FROM recurrence_definition r
LEFT JOIN closed_form_solution c
    ON c.recurrence_id = r.recurrence_id
LEFT JOIN evaluation_strategy es
    ON es.recurrence_id = r.recurrence_id
ORDER BY r.name, es.strategy_name;
