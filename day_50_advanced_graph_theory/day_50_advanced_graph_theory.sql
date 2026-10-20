DROP SCHEMA IF EXISTS advanced_graph_theory CASCADE;
CREATE SCHEMA advanced_graph_theory;
SET search_path TO advanced_graph_theory;

-- The relational model distinguishes graph structure from analytical results.
-- A graph can participate in isomorphism, minor, planarity, and extremal analyses
-- without conflating those mathematical concepts.

CREATE TABLE graph (
    graph_id BIGSERIAL PRIMARY KEY,
    graph_name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vertex (
    vertex_id BIGSERIAL PRIMARY KEY,
    graph_id BIGINT NOT NULL REFERENCES graph(graph_id) ON DELETE CASCADE,
    vertex_key TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (graph_id, vertex_key)
);

CREATE TABLE graph_edge (
    graph_edge_id BIGSERIAL PRIMARY KEY,
    graph_id BIGINT NOT NULL REFERENCES graph(graph_id) ON DELETE CASCADE,
    first_vertex_id BIGINT NOT NULL REFERENCES vertex(vertex_id) ON DELETE CASCADE,
    second_vertex_id BIGINT NOT NULL REFERENCES vertex(vertex_id) ON DELETE CASCADE,
    CHECK (first_vertex_id <> second_vertex_id),
    CHECK (first_vertex_id < second_vertex_id),
    UNIQUE (graph_id, first_vertex_id, second_vertex_id)
);

CREATE TABLE graph_analysis (
    analysis_id BIGSERIAL PRIMARY KEY,
    graph_id BIGINT NOT NULL REFERENCES graph(graph_id) ON DELETE CASCADE,
    analysis_type TEXT NOT NULL CHECK (
        analysis_type IN (
            'PLANARITY',
            'ISOMORPHISM',
            'MINOR',
            'EXTREMAL'
        )
    ),
    status TEXT NOT NULL CHECK (
        status IN (
            'CERTIFIED',
            'REJECTED',
            'EQUIVALENT',
            'NOT_EQUIVALENT',
            'UNDETERMINED'
        )
    ),
    explanation TEXT NOT NULL,
    analyzed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE isomorphism_mapping (
    analysis_id BIGINT NOT NULL REFERENCES graph_analysis(analysis_id)
        ON DELETE CASCADE,
    source_vertex_id BIGINT NOT NULL REFERENCES vertex(vertex_id)
        ON DELETE CASCADE,
    target_vertex_id BIGINT NOT NULL REFERENCES vertex(vertex_id)
        ON DELETE CASCADE,
    PRIMARY KEY (analysis_id, source_vertex_id),
    UNIQUE (analysis_id, target_vertex_id)
);

CREATE TABLE minor_operation (
    minor_operation_id BIGSERIAL PRIMARY KEY,
    source_graph_id BIGINT NOT NULL REFERENCES graph(graph_id)
        ON DELETE CASCADE,
    resulting_graph_id BIGINT NOT NULL REFERENCES graph(graph_id)
        ON DELETE CASCADE,
    operation_type TEXT NOT NULL CHECK (
        operation_type IN (
            'EDGE_CONTRACTION',
            'VERTEX_DELETION',
            'EDGE_DELETION'
        )
    ),
    first_vertex_id BIGINT REFERENCES vertex(vertex_id)
        ON DELETE SET NULL,
    second_vertex_id BIGINT REFERENCES vertex(vertex_id)
        ON DELETE SET NULL,
    CHECK (
        operation_type <> 'EDGE_CONTRACTION'
        OR (
            first_vertex_id IS NOT NULL
            AND second_vertex_id IS NOT NULL
            AND first_vertex_id <> second_vertex_id
        )
    )
);

CREATE TABLE extremal_bound (
    bound_id BIGSERIAL PRIMARY KEY,
    graph_family TEXT NOT NULL,
    vertex_count INTEGER NOT NULL CHECK (vertex_count >= 0),
    maximum_edges BIGINT NOT NULL CHECK (maximum_edges >= 0),
    theorem TEXT NOT NULL,
    UNIQUE (graph_family, vertex_count)
);

CREATE INDEX idx_vertex_graph
    ON vertex(graph_id);

CREATE INDEX idx_edge_graph
    ON graph_edge(graph_id);

CREATE INDEX idx_analysis_graph_type
    ON graph_analysis(graph_id, analysis_type);

CREATE OR REPLACE FUNCTION validate_edge_graph_membership()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM vertex
        WHERE vertex_id = NEW.first_vertex_id
          AND graph_id = NEW.graph_id
    ) THEN
        RAISE EXCEPTION
            'First vertex % does not belong to graph %',
            NEW.first_vertex_id,
            NEW.graph_id;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM vertex
        WHERE vertex_id = NEW.second_vertex_id
          AND graph_id = NEW.graph_id
    ) THEN
        RAISE EXCEPTION
            'Second vertex % does not belong to graph %',
            NEW.second_vertex_id,
            NEW.graph_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_edge_graph_membership
BEFORE INSERT OR UPDATE ON graph_edge
FOR EACH ROW
EXECUTE FUNCTION validate_edge_graph_membership();

CREATE OR REPLACE FUNCTION graph_vertex_count(p_graph_id BIGINT)
RETURNS BIGINT
LANGUAGE SQL
STABLE
AS $$
    SELECT COUNT(*)
    FROM vertex
    WHERE graph_id = p_graph_id;
$$;

CREATE OR REPLACE FUNCTION graph_edge_count(p_graph_id BIGINT)
RETURNS BIGINT
LANGUAGE SQL
STABLE
AS $$
    SELECT COUNT(*)
    FROM graph_edge
    WHERE graph_id = p_graph_id;
$$;

CREATE OR REPLACE FUNCTION planar_simple_edge_bound(p_vertex_count BIGINT)
RETURNS BIGINT
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT CASE
        WHEN p_vertex_count < 3
            THEN p_vertex_count * (p_vertex_count - 1) / 2
        ELSE 3 * p_vertex_count - 6
    END;
$$;

CREATE OR REPLACE FUNCTION planar_bipartite_edge_bound(p_vertex_count BIGINT)
RETURNS BIGINT
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT CASE
        WHEN p_vertex_count < 3
            THEN p_vertex_count * (p_vertex_count - 1) / 2
        ELSE 2 * p_vertex_count - 4
    END;
$$;

-- Demonstration graphs.
INSERT INTO graph (graph_name, description)
VALUES
    ('C5', 'Five-cycle'),
    ('K5', 'Complete graph on five vertices'),
    ('K3_3', 'Complete bipartite graph with partitions of size three'),
    ('K6', 'Complete graph on six vertices'),
    ('SUBDIVIDED_K3_3', 'K3,3 with one edge subdivided');

INSERT INTO vertex (graph_id, vertex_key)
SELECT g.graph_id, v.vertex_key
FROM graph g
CROSS JOIN LATERAL (
    SELECT generate_series(0, 4)::TEXT AS vertex_key
    WHERE g.graph_name IN ('C5', 'K5', 'K6')
    UNION ALL
    SELECT 'L' || generate_series(0, 2)::TEXT
    WHERE g.graph_name = 'K3_3'
    UNION ALL
    SELECT 'R' || generate_series(0, 2)::TEXT
    WHERE g.graph_name = 'K3_3'
    UNION ALL
    SELECT generate_series(0, 2)::TEXT
    WHERE g.graph_name = 'SUBDIVIDED_K3_3'
    UNION ALL
    SELECT 'R' || generate_series(0, 2)::TEXT
    WHERE g.graph_name = 'SUBDIVIDED_K3_3'
    UNION ALL
    SELECT 'X'
    WHERE g.graph_name = 'SUBDIVIDED_K3_3'
) AS v;

INSERT INTO vertex (graph_id, vertex_key)
SELECT graph_id, vertex_key
FROM (
    SELECT graph_id, '5' AS vertex_key
    FROM graph
    WHERE graph_name = 'K6'
) AS extra;

-- C5 edges.
INSERT INTO graph_edge (graph_id, first_vertex_id, second_vertex_id)
SELECT g.graph_id, LEAST(v1.vertex_id, v2.vertex_id),
       GREATEST(v1.vertex_id, v2.vertex_id)
FROM graph g
JOIN vertex v1 ON v1.graph_id = g.graph_id
JOIN vertex v2 ON v2.graph_id = g.graph_id
WHERE g.graph_name = 'C5'
  AND (
      (v1.vertex_key = '0' AND v2.vertex_key = '1') OR
      (v1.vertex_key = '1' AND v2.vertex_key = '2') OR
      (v1.vertex_key = '2' AND v2.vertex_key = '3') OR
      (v1.vertex_key = '3' AND v2.vertex_key = '4') OR
      (v1.vertex_key = '0' AND v2.vertex_key = '4')
  );

-- K5 and K6 are generated from every unordered pair.
INSERT INTO graph_edge (graph_id, first_vertex_id, second_vertex_id)
SELECT g.graph_id, v1.vertex_id, v2.vertex_id
FROM graph g
JOIN vertex v1 ON v1.graph_id = g.graph_id
JOIN vertex v2
  ON v2.graph_id = g.graph_id
 AND v1.vertex_id < v2.vertex_id
WHERE g.graph_name IN ('K5', 'K6');

-- K3,3.
INSERT INTO graph_edge (graph_id, first_vertex_id, second_vertex_id)
SELECT g.graph_id, l.vertex_id, r.vertex_id
FROM graph g
JOIN vertex l
  ON l.graph_id = g.graph_id
 AND l.vertex_key LIKE 'L%'
JOIN vertex r
  ON r.graph_id = g.graph_id
 AND r.vertex_key LIKE 'R%'
WHERE g.graph_name = 'K3_3';

-- Subdivided K3,3:
-- retain all K3,3 edges except L0-R0 and replace it with L0-X and X-R0.
INSERT INTO graph_edge (graph_id, first_vertex_id, second_vertex_id)
SELECT g.graph_id,
       LEAST(l.vertex_id, r.vertex_id),
       GREATEST(l.vertex_id, r.vertex_id)
FROM graph g
JOIN vertex l
  ON l.graph_id = g.graph_id
 AND l.vertex_key LIKE 'L%'
JOIN vertex r
  ON r.graph_id = g.graph_id
 AND r.vertex_key LIKE 'R%'
WHERE g.graph_name = 'SUBDIVIDED_K3_3'
  AND NOT (l.vertex_key = 'L0' AND r.vertex_key = 'R0');

INSERT INTO graph_edge (graph_id, first_vertex_id, second_vertex_id)
SELECT g.graph_id,
       LEAST(l.vertex_id, x.vertex_id),
       GREATEST(l.vertex_id, x.vertex_id)
FROM graph g
JOIN vertex l
  ON l.graph_id = g.graph_id
 AND l.vertex_key = 'L0'
JOIN vertex x
  ON x.graph_id = g.graph_id
 AND x.vertex_key = 'X'
WHERE g.graph_name = 'SUBDIVIDED_K3_3';

INSERT INTO graph_edge (graph_id, first_vertex_id, second_vertex_id)
SELECT g.graph_id,
       LEAST(x.vertex_id, r.vertex_id),
       GREATEST(x.vertex_id, r.vertex_id)
FROM graph g
JOIN vertex x
  ON x.graph_id = g.graph_id
 AND x.vertex_key = 'X'
JOIN vertex r
  ON r.graph_id = g.graph_id
 AND r.vertex_key = 'R0'
WHERE g.graph_name = 'SUBDIVIDED_K3_3';

-- Extremal values for common graph families.
INSERT INTO extremal_bound (
    graph_family,
    vertex_count,
    maximum_edges,
    theorem
)
SELECT
    'SIMPLE_GRAPH',
    n,
    n * (n - 1) / 2,
    'A simple graph has at most n(n-1)/2 edges.'
FROM generate_series(3, 10) AS n;

INSERT INTO extremal_bound (
    graph_family,
    vertex_count,
    maximum_edges,
    theorem
)
SELECT
    'PLANAR_SIMPLE_GRAPH',
    n,
    3 * n - 6,
    'A simple planar graph with n >= 3 has at most 3n-6 edges.'
FROM generate_series(3, 10) AS n;

INSERT INTO extremal_bound (
    graph_family,
    vertex_count,
    maximum_edges,
    theorem
)
SELECT
    'BIPARTITE_PLANAR_GRAPH',
    n,
    2 * n - 4,
    'A simple bipartite planar graph with n >= 3 has at most 2n-4 edges.'
FROM generate_series(3, 10) AS n;

-- Graph metrics view supports extremal analysis without modifying graph data.
CREATE OR REPLACE VIEW graph_metrics AS
SELECT
    g.graph_id,
    g.graph_name,
    COUNT(DISTINCT v.vertex_id) AS vertex_count,
    COUNT(DISTINCT e.graph_edge_id) AS edge_count,
    CASE
        WHEN COUNT(DISTINCT v.vertex_id) < 3 THEN
            COUNT(DISTINCT v.vertex_id)
            * (COUNT(DISTINCT v.vertex_id) - 1) / 2
        ELSE
            3 * COUNT(DISTINCT v.vertex_id) - 6
    END AS planar_edge_bound
FROM graph g
LEFT JOIN vertex v
    ON v.graph_id = g.graph_id
LEFT JOIN graph_edge e
    ON e.graph_id = g.graph_id
GROUP BY g.graph_id, g.graph_name;

-- Fast retrieval of graph density relative to the planar Euler bound.
SELECT
    graph_name,
    vertex_count,
    edge_count,
    planar_edge_bound,
    edge_count <= planar_edge_bound AS passes_planar_edge_bound
FROM graph_metrics
ORDER BY graph_name;

-- Degree distribution is a useful invariant for rejecting non-isomorphic graphs.
WITH degree_data AS (
    SELECT
        g.graph_name,
        v.vertex_id,
        COUNT(e.graph_edge_id) AS degree
    FROM graph g
    JOIN vertex v
      ON v.graph_id = g.graph_id
    LEFT JOIN graph_edge e
      ON e.graph_id = g.graph_id
     AND (e.first_vertex_id = v.vertex_id
          OR e.second_vertex_id = v.vertex_id)
    GROUP BY g.graph_name, v.vertex_id
)
SELECT
    graph_name,
    ARRAY_AGG(degree ORDER BY degree DESC) AS degree_sequence
FROM degree_data
GROUP BY graph_name
ORDER BY graph_name;

-- Detect triangles. This is a direct relational expression of a K3 subgraph.
SELECT
    g.graph_name,
    COUNT(*) AS triangle_instances
FROM graph g
JOIN graph_edge e1 ON e1.graph_id = g.graph_id
JOIN graph_edge e2
  ON e2.graph_id = g.graph_id
JOIN graph_edge e3
  ON e3.graph_id = g.graph_id
WHERE e1.first_vertex_id < e2.first_vertex_id
  AND e2.first_vertex_id < e3.first_vertex_id
  AND EXISTS (
      SELECT 1
      FROM vertex a
      JOIN vertex b ON b.vertex_id = e1.second_vertex_id
      JOIN vertex c ON c.vertex_id = e2.second_vertex_id
      WHERE a.vertex_id = e1.first_vertex_id
        AND EXISTS (
            SELECT 1
            FROM graph_edge closing
            WHERE closing.graph_id = g.graph_id
              AND (
                  (
                      closing.first_vertex_id = LEAST(a.vertex_id, c.vertex_id)
                      AND closing.second_vertex_id = GREATEST(a.vertex_id, c.vertex_id)
                  )
              )
        )
  )
GROUP BY g.graph_name;

-- Transactional recording of analytical results.
BEGIN;

INSERT INTO graph_analysis (
    graph_id,
    analysis_type,
    status,
    explanation
)
SELECT
    graph_id,
    'PLANARITY',
    CASE
        WHEN edge_count > planar_edge_bound THEN 'REJECTED'
        ELSE 'UNDETERMINED'
    END,
    CASE
        WHEN edge_count > planar_edge_bound
            THEN 'Edge count exceeds the necessary planar upper bound.'
        ELSE
            'Edge count satisfies the necessary planar upper bound; '
            || 'this does not prove planarity.'
    END
FROM graph_metrics
WHERE graph_name IN ('C5', 'K5', 'K3_3', 'SUBDIVIDED_K3_3');

COMMIT;

-- A CTE evaluates the extremal position of each stored graph.
WITH graph_position AS (
    SELECT
        gm.graph_name,
        gm.vertex_count,
        gm.edge_count,
        gm.planar_edge_bound,
        CASE
            WHEN gm.edge_count > gm.planar_edge_bound
                THEN 'ABOVE_PLANAR_BOUND'
            WHEN gm.edge_count = gm.planar_edge_bound
                THEN 'AT_PLANAR_BOUND'
            ELSE
                'BELOW_PLANAR_BOUND'
        END AS extremal_position
    FROM graph_metrics gm
)
SELECT *
FROM graph_position
ORDER BY vertex_count, graph_name;

-- A minor relationship can be recorded without pretending that an edge
-- contraction is the same mathematical operation as arbitrary subgraph
-- selection. This example records a contraction from K6 to a derived graph.
INSERT INTO graph (
    graph_name,
    description
)
VALUES (
    'K6_CONTRACTED_01',
    'Derived graph after contracting one K6 edge'
);

INSERT INTO vertex (graph_id, vertex_key)
SELECT g2.graph_id, 'merged_0_1'
FROM graph g2
WHERE g2.graph_name = 'K6_CONTRACTED_01';

INSERT INTO vertex (graph_id, vertex_key)
SELECT g2.graph_id, v.vertex_key
FROM graph g2
JOIN graph g1
  ON g1.graph_name = 'K6'
JOIN vertex v
  ON v.graph_id = g1.graph_id
WHERE g2.graph_name = 'K6_CONTRACTED_01'
  AND v.vertex_key NOT IN ('0', '1');

INSERT INTO minor_operation (
    source_graph_id,
    resulting_graph_id,
    operation_type,
    first_vertex_id,
    second_vertex_id
)
SELECT
    source.graph_id,
    result.graph_id,
    'EDGE_CONTRACTION',
    v0.vertex_id,
    v1.vertex_id
FROM graph source
JOIN graph result
  ON result.graph_name = 'K6_CONTRACTED_01'
JOIN vertex v0
  ON v0.graph_id = source.graph_id
 AND v0.vertex_key = '0'
JOIN vertex v1
  ON v1.graph_id = source.graph_id
 AND v1.vertex_key = '1'
WHERE source.graph_name = 'K6';

-- Final integrity report.
SELECT
    g.graph_name,
    COUNT(DISTINCT v.vertex_id) AS vertices,
    COUNT(DISTINCT e.graph_edge_id) AS edges,
    COUNT(DISTINCT a.analysis_id) AS recorded_analyses
FROM graph g
LEFT JOIN vertex v
    ON v.graph_id = g.graph_id
LEFT JOIN graph_edge e
    ON e.graph_id = g.graph_id
LEFT JOIN graph_analysis a
    ON a.graph_id = g.graph_id
GROUP BY g.graph_id, g.graph_name
ORDER BY g.graph_name;
