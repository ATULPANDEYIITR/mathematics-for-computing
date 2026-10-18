-- PostgreSQL: Euler and Hamiltonian graph analysis.
-- The schema stores an undirected simple graph. A canonical endpoint order
-- prevents the same undirected edge from being inserted in reverse order.

DROP SCHEMA IF EXISTS graph_routes CASCADE;
CREATE SCHEMA graph_routes;
SET search_path = graph_routes, public;

CREATE TABLE graph (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE vertex (
    graph_id BIGINT NOT NULL REFERENCES graph(graph_id) ON DELETE CASCADE,
    vertex_id INTEGER NOT NULL,
    vertex_name TEXT NOT NULL,
    PRIMARY KEY (graph_id, vertex_id),
    UNIQUE (graph_id, vertex_name)
);

CREATE TABLE edge (
    graph_id BIGINT NOT NULL,
    edge_id INTEGER NOT NULL,
    endpoint_a INTEGER NOT NULL,
    endpoint_b INTEGER NOT NULL,
    PRIMARY KEY (graph_id, edge_id),
    FOREIGN KEY (graph_id, endpoint_a)
        REFERENCES vertex(graph_id, vertex_id) ON DELETE CASCADE,
    FOREIGN KEY (graph_id, endpoint_b)
        REFERENCES vertex(graph_id, vertex_id) ON DELETE CASCADE,
    CHECK (endpoint_a < endpoint_b),
    UNIQUE (graph_id, endpoint_a, endpoint_b)
);

CREATE INDEX edge_endpoint_b_idx
    ON edge (graph_id, endpoint_b);

CREATE TABLE route_analysis (
    analysis_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL REFERENCES graph(graph_id) ON DELETE CASCADE,
    route_type TEXT NOT NULL CHECK (
        route_type IN (
            'EULER_TRAIL',
            'EULER_CIRCUIT',
            'HAMILTONIAN_PATH',
            'HAMILTONIAN_CYCLE'
        )
    ),
    exists_flag BOOLEAN NOT NULL,
    route_vertices INTEGER[] NOT NULL DEFAULT '{}',
    analyzed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (
        cardinality(route_vertices) = 0
        OR array_position(route_vertices, NULL) IS NULL
    )
);

CREATE INDEX route_analysis_graph_type_idx
    ON route_analysis (graph_id, route_type, exists_flag);

INSERT INTO graph (graph_name, description) VALUES
    ('square', 'Four-vertex ring'),
    ('triangle_tail', 'Triangle with one pendant edge'),
    ('complete_k4', 'Complete graph on four vertices'),
    ('disconnected', 'Two disconnected components');

INSERT INTO vertex (graph_id, vertex_id, vertex_name)
SELECT g.graph_id, v.vertex_id, v.vertex_name
FROM graph g
JOIN (
    VALUES
        ('square', 1, 'A'),
        ('square', 2, 'B'),
        ('square', 3, 'C'),
        ('square', 4, 'D'),
        ('triangle_tail', 1, 'A'),
        ('triangle_tail', 2, 'B'),
        ('triangle_tail', 3, 'C'),
        ('triangle_tail', 4, 'D'),
        ('complete_k4', 1, 'A'),
        ('complete_k4', 2, 'B'),
        ('complete_k4', 3, 'C'),
        ('complete_k4', 4, 'D'),
        ('disconnected', 1, 'A'),
        ('disconnected', 2, 'B'),
        ('disconnected', 3, 'C'),
        ('disconnected', 4, 'D')
) AS v(graph_name, vertex_id, vertex_name)
    ON g.graph_name = v.graph_name;

INSERT INTO edge (graph_id, edge_id, endpoint_a, endpoint_b)
SELECT g.graph_id, e.edge_id, e.a, e.b
FROM graph g
JOIN (
    VALUES
        ('square', 1, 1, 2),
        ('square', 2, 2, 3),
        ('square', 3, 3, 4),
        ('square', 4, 1, 4),
        ('triangle_tail', 1, 1, 2),
        ('triangle_tail', 2, 2, 3),
        ('triangle_tail', 3, 1, 3),
        ('triangle_tail', 4, 3, 4),
        ('complete_k4', 1, 1, 2),
        ('complete_k4', 2, 1, 3),
        ('complete_k4', 3, 1, 4),
        ('complete_k4', 4, 2, 3),
        ('complete_k4', 5, 2, 4),
        ('complete_k4', 6, 3, 4),
        ('disconnected', 1, 1, 2),
        ('disconnected', 2, 3, 4)
) AS e(graph_name, edge_id, a, b)
    ON g.graph_name = e.graph_name;

-- Degree is a property of incident edges. The UNION ALL is important because
-- every undirected edge contributes one degree to each endpoint.
CREATE VIEW vertex_degree AS
SELECT v.graph_id, v.vertex_id, v.vertex_name,
       COUNT(i.endpoint) AS degree
FROM vertex v
LEFT JOIN (
    SELECT graph_id, endpoint_a AS endpoint FROM edge
    UNION ALL
    SELECT graph_id, endpoint_b AS endpoint FROM edge
) i
    ON i.graph_id = v.graph_id
   AND i.endpoint = v.vertex_id
GROUP BY v.graph_id, v.vertex_id, v.vertex_name;

-- Euler parity conditions are necessary and sufficient only when all
-- non-isolated vertices belong to one connected component.
-- Recursive reachability starts at every non-isolated vertex and follows edges.
WITH RECURSIVE reachability(graph_id, start_vertex, reached_vertex) AS (
    SELECT graph_id, vertex_id, vertex_id
    FROM vertex_degree
    WHERE degree > 0

    UNION

    SELECT r.graph_id, r.start_vertex,
           CASE
               WHEN e.endpoint_a = r.reached_vertex THEN e.endpoint_b
               ELSE e.endpoint_a
           END
    FROM reachability r
    JOIN edge e
      ON e.graph_id = r.graph_id
     AND (
         e.endpoint_a = r.reached_vertex
         OR e.endpoint_b = r.reached_vertex
     )
),
connectivity AS (
    SELECT g.graph_id,
           NOT EXISTS (
               SELECT 1
               FROM vertex_degree d
               WHERE d.graph_id = g.graph_id
                 AND d.degree > 0
                 AND NOT EXISTS (
                     SELECT 1
                     FROM reachability r
                     WHERE r.graph_id = d.graph_id
                       AND r.reached_vertex = d.vertex_id
                       AND r.start_vertex = (
                           SELECT MIN(d2.vertex_id)
                           FROM vertex_degree d2
                           WHERE d2.graph_id = d.graph_id
                             AND d2.degree > 0
                       )
                 )
           ) AS connected_nonisolated
    FROM graph g
),
parity AS (
    SELECT g.graph_id,
           COUNT(*) FILTER (WHERE d.degree % 2 = 1) AS odd_vertices,
           COUNT(d.vertex_id) AS total_vertices,
           COUNT(*) FILTER (WHERE d.degree > 0) AS active_vertices
    FROM graph g
    LEFT JOIN vertex_degree d ON d.graph_id = g.graph_id
    GROUP BY g.graph_id
)
SELECT g.graph_name,
       c.connected_nonisolated,
       p.total_vertices,
       p.active_vertices,
       p.odd_vertices,
       c.connected_nonisolated AND p.odd_vertices IN (0, 2)
           AS has_euler_trail,
       c.connected_nonisolated AND p.odd_vertices = 0
           AS has_euler_circuit
FROM graph g
JOIN connectivity c USING (graph_id)
JOIN parity p USING (graph_id)
ORDER BY g.graph_id;

-- Hamiltonian analysis is NP-complete in general. The following query stores
-- known candidate routes, then validates vertex coverage and adjacency.
-- A cycle is represented without repeating its first vertex at the end.

INSERT INTO route_analysis (graph_id, route_type, exists_flag, route_vertices)
SELECT graph_id, 'HAMILTONIAN_CYCLE', TRUE, ARRAY[1, 2, 3, 4]
FROM graph
WHERE graph_name = 'square';

INSERT INTO route_analysis (graph_id, route_type, exists_flag, route_vertices)
SELECT graph_id, 'HAMILTONIAN_PATH', TRUE, ARRAY[1, 2, 3, 4]
FROM graph
WHERE graph_name = 'triangle_tail';

-- Check each candidate route for correct length, unique vertices, membership,
-- and adjacency between consecutive vertices.
WITH candidates AS (
    SELECT ra.analysis_id, ra.graph_id, ra.route_type, ra.route_vertices,
           COUNT(DISTINCT x.vertex_id) AS distinct_count,
           COUNT(v.vertex_id) AS valid_vertex_count,
           cardinality(ra.route_vertices) AS route_length
    FROM route_analysis ra
    CROSS JOIN LATERAL unnest(ra.route_vertices) AS x(vertex_id)
    LEFT JOIN vertex v
      ON v.graph_id = ra.graph_id
     AND v.vertex_id = x.vertex_id
    GROUP BY ra.analysis_id, ra.graph_id, ra.route_type, ra.route_vertices
),
transitions AS (
    SELECT ra.analysis_id,
           bool_and(
               EXISTS (
                   SELECT 1
                   FROM edge e
                   WHERE e.graph_id = ra.graph_id
                     AND (
                         (e.endpoint_a = pair.from_vertex
                          AND e.endpoint_b = pair.to_vertex)
                         OR
                         (e.endpoint_a = pair.to_vertex
                          AND e.endpoint_b = pair.from_vertex)
                     )
               )
           ) AS all_transitions_exist
    FROM route_analysis ra
    CROSS JOIN LATERAL (
        SELECT ra.route_vertices[i] AS from_vertex,
               ra.route_vertices[i + 1] AS to_vertex
        FROM generate_subscripts(ra.route_vertices, 1) AS s(i)
        WHERE i < cardinality(ra.route_vertices)
    ) pair
    GROUP BY ra.analysis_id
)
SELECT g.graph_name,
       c.route_type,
       c.route_vertices,
       c.route_length = (SELECT COUNT(*) FROM vertex v
                         WHERE v.graph_id = c.graph_id)
           AND c.distinct_count = c.route_length
           AND c.valid_vertex_count = c.route_length
           AND COALESCE(t.all_transitions_exist, TRUE)
           AND (
               c.route_type <> 'HAMILTONIAN_CYCLE'
               OR EXISTS (
                   SELECT 1
                   FROM edge e
                   WHERE e.graph_id = c.graph_id
                     AND (
                         (e.endpoint_a = c.route_vertices[1]
                          AND e.endpoint_b = c.route_vertices[c.route_length])
                         OR
                         (e.endpoint_b = c.route_vertices[1]
                          AND e.endpoint_a = c.route_vertices[c.route_length])
                     )
               )
           ) AS candidate_is_valid
FROM candidates c
JOIN graph g USING (graph_id)
LEFT JOIN transitions t USING (analysis_id)
ORDER BY g.graph_name, c.route_type;

-- Integrity demonstration: a reverse-order duplicate violates endpoint_a <
-- endpoint_b or the unique edge constraint. Run separately to observe failure.
-- INSERT INTO edge (graph_id, edge_id, endpoint_a, endpoint_b)
-- SELECT graph_id, 99, 2, 1 FROM graph WHERE graph_name = 'square';

-- Record example findings atomically.
BEGIN;

INSERT INTO route_analysis (graph_id, route_type, exists_flag, route_vertices)
SELECT graph_id, 'EULER_CIRCUIT', TRUE, ARRAY[1, 2, 3, 4]
FROM graph
WHERE graph_name = 'square';

INSERT INTO route_analysis (graph_id, route_type, exists_flag, route_vertices)
SELECT graph_id, 'EULER_TRAIL', TRUE, ARRAY[1, 2, 4, 3, 1]
FROM graph
WHERE graph_name = 'triangle_tail';

COMMIT;

SELECT g.graph_name, a.route_type, a.exists_flag, a.route_vertices,
       a.analyzed_at
FROM route_analysis a
JOIN graph g USING (graph_id)
ORDER BY g.graph_name, a.route_type, a.analysis_id;
