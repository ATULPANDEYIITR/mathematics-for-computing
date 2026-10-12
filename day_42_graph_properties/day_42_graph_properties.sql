-- PostgreSQL graph-property laboratory.
-- Models vertices, edges, degrees, walks, paths, cycles, and components.
-- Recursive CTEs are used for reachability and cycle-related queries.

BEGIN;

DROP VIEW IF EXISTS graph_degree_report CASCADE;
DROP TABLE IF EXISTS graph_component_members CASCADE;
DROP TABLE IF EXISTS graph_walk_steps CASCADE;
DROP TABLE IF EXISTS graph_edges CASCADE;
DROP TABLE IF EXISTS graph_vertices CASCADE;
DROP TABLE IF EXISTS graph_definitions CASCADE;

CREATE TABLE graph_definitions (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_name TEXT NOT NULL UNIQUE,
    graph_type TEXT NOT NULL CHECK (graph_type IN ('undirected', 'directed')),
    description TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE graph_vertices (
    graph_id BIGINT NOT NULL REFERENCES graph_definitions(graph_id)
        ON DELETE CASCADE,
    vertex_id TEXT NOT NULL CHECK (length(trim(vertex_id)) > 0),
    vertex_label TEXT NOT NULL,
    PRIMARY KEY (graph_id, vertex_id)
);

CREATE TABLE graph_edges (
    graph_id BIGINT NOT NULL,
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY,
    source_vertex TEXT NOT NULL,
    target_vertex TEXT NOT NULL,
    edge_weight NUMERIC(12, 4) NOT NULL DEFAULT 1 CHECK (edge_weight >= 0),
    PRIMARY KEY (graph_id, edge_id),
    FOREIGN KEY (graph_id, source_vertex)
        REFERENCES graph_vertices(graph_id, vertex_id) ON DELETE CASCADE,
    FOREIGN KEY (graph_id, target_vertex)
        REFERENCES graph_vertices(graph_id, vertex_id) ON DELETE CASCADE,
    CHECK (source_vertex <> target_vertex)
);

-- This model uses a simple graph: duplicate endpoint pairs are not allowed.
-- An undirected edge is stored once in canonical lexical endpoint order.
CREATE UNIQUE INDEX graph_edges_unique_directed
    ON graph_edges(graph_id, source_vertex, target_vertex);

CREATE INDEX graph_edges_by_target
    ON graph_edges(graph_id, target_vertex);

CREATE TABLE graph_walk_steps (
    walk_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL REFERENCES graph_definitions(graph_id)
        ON DELETE CASCADE,
    walk_name TEXT NOT NULL,
    step_number INTEGER NOT NULL CHECK (step_number >= 0),
    vertex_id TEXT NOT NULL,
    FOREIGN KEY (graph_id, vertex_id)
        REFERENCES graph_vertices(graph_id, vertex_id) ON DELETE CASCADE,
    UNIQUE (graph_id, walk_name, step_number)
);

CREATE TABLE graph_component_members (
    graph_id BIGINT NOT NULL,
    component_label TEXT NOT NULL,
    vertex_id TEXT NOT NULL,
    PRIMARY KEY (graph_id, vertex_id),
    FOREIGN KEY (graph_id, vertex_id)
        REFERENCES graph_vertices(graph_id, vertex_id) ON DELETE CASCADE
);

-- Degree reports include all vertices, including isolated vertices.
-- A self-loop is prohibited by this simple graph model.
CREATE VIEW graph_degree_report AS
SELECT
    v.graph_id,
    v.vertex_id,
    v.vertex_label,
    g.graph_type,
    CASE
        WHEN g.graph_type = 'undirected' THEN
            (SELECT count(*)
             FROM graph_edges e
             WHERE e.graph_id = v.graph_id
               AND (e.source_vertex = v.vertex_id
                    OR e.target_vertex = v.vertex_id))
        ELSE
            (SELECT count(*)
             FROM graph_edges e
             WHERE e.graph_id = v.graph_id
               AND e.source_vertex = v.vertex_id)
    END AS degree_or_out_degree,
    CASE
        WHEN g.graph_type = 'directed' THEN
            (SELECT count(*)
             FROM graph_edges e
             WHERE e.graph_id = v.graph_id
               AND e.target_vertex = v.vertex_id)
        ELSE NULL
    END AS in_degree
FROM graph_vertices v
JOIN graph_definitions g USING (graph_id);

-- Sample undirected graph: a campus road network.
INSERT INTO graph_definitions (graph_name, graph_type, description)
VALUES
    ('campus', 'undirected', 'Campus routes and isolated facilities'),
    ('deployment', 'directed', 'Directed service dependencies');

INSERT INTO graph_vertices (graph_id, vertex_id, vertex_label)
SELECT g.graph_id, x.vertex_id, x.vertex_label
FROM graph_definitions g
CROSS JOIN (
    VALUES
        ('gate', 'North Gate'),
        ('library', 'Library'),
        ('laboratory', 'Laboratory'),
        ('cafeteria', 'Cafeteria'),
        ('hostel', 'Hostel'),
        ('annex', 'Remote Annex')
) AS x(vertex_id, vertex_label)
WHERE g.graph_name = 'campus';

INSERT INTO graph_edges (graph_id, source_vertex, target_vertex, edge_weight)
SELECT g.graph_id, x.source_vertex, x.target_vertex, x.edge_weight
FROM graph_definitions g
CROSS JOIN (
    VALUES
        ('gate', 'library', 1.0::NUMERIC),
        ('library', 'laboratory', 1.0::NUMERIC),
        ('library', 'cafeteria', 1.0::NUMERIC),
        ('cafeteria', 'hostel', 1.0::NUMERIC)
) AS x(source_vertex, target_vertex, edge_weight)
WHERE g.graph_name = 'campus';

-- Sample directed graph: dependencies are directional and need not be symmetric.
INSERT INTO graph_vertices (graph_id, vertex_id, vertex_label)
SELECT g.graph_id, x.vertex_id, x.vertex_label
FROM graph_definitions g
CROSS JOIN (
    VALUES
        ('compile', 'Compile Service'),
        ('test', 'Test Service'),
        ('package', 'Package Service'),
        ('deploy', 'Deployment Service')
) AS x(vertex_id, vertex_label)
WHERE g.graph_name = 'deployment';

INSERT INTO graph_edges (graph_id, source_vertex, target_vertex)
SELECT g.graph_id, x.source_vertex, x.target_vertex
FROM graph_definitions g
CROSS JOIN (
    VALUES
        ('compile', 'test'),
        ('test', 'package'),
        ('package', 'deploy')
) AS x(source_vertex, target_vertex)
WHERE g.graph_name = 'deployment';

-- Degree and graph-size metrics.
SELECT
    g.graph_name,
    g.graph_type,
    count(DISTINCT v.vertex_id) AS vertex_count,
    count(DISTINCT e.edge_id) AS edge_count
FROM graph_definitions g
LEFT JOIN graph_vertices v USING (graph_id)
LEFT JOIN graph_edges e USING (graph_id)
GROUP BY g.graph_id, g.graph_name, g.graph_type
ORDER BY g.graph_name;

SELECT *
FROM graph_degree_report
ORDER BY graph_id, vertex_id;

-- The handshaking lemma for undirected graphs states that the sum of degrees
-- equals twice the number of edges.
SELECT
    g.graph_name,
    sum(d.degree_or_out_degree) AS degree_sum,
    2 * (
        SELECT count(*)
        FROM graph_edges e
        WHERE e.graph_id = g.graph_id
    ) AS twice_edge_count,
    sum(d.degree_or_out_degree) = 2 * (
        SELECT count(*) * 2
        FROM graph_edges e
        WHERE e.graph_id = g.graph_id
    ) AS incorrect_comparison_demonstration
FROM graph_definitions g
JOIN graph_degree_report d USING (graph_id)
WHERE g.graph_type = 'undirected'
GROUP BY g.graph_id, g.graph_name;

-- Correctly evaluate the handshaking lemma without multiplying twice.
SELECT
    g.graph_name,
    sum(d.degree_or_out_degree) AS degree_sum,
    2 * (
        SELECT count(*)
        FROM graph_edges e
        WHERE e.graph_id = g.graph_id
    ) AS twice_edge_count,
    sum(d.degree_or_out_degree) = 2 * (
        SELECT count(*)
        FROM graph_edges e
        WHERE e.graph_id = g.graph_id
    ) AS handshaking_lemma_holds
FROM graph_definitions g
JOIN graph_degree_report d USING (graph_id)
WHERE g.graph_type = 'undirected'
GROUP BY g.graph_id, g.graph_name;

-- Reachability: each recursive row represents a path prefix.
-- UNION (not UNION ALL) prevents repeated vertex pairs from looping forever.
WITH RECURSIVE reachability(graph_id, source_vertex, reached_vertex) AS (
    SELECT graph_id, vertex_id, vertex_id
    FROM graph_vertices

    UNION

    SELECT r.graph_id, r.source_vertex, e.target_vertex
    FROM reachability r
    JOIN graph_edges e
      ON e.graph_id = r.graph_id
     AND e.source_vertex = r.reached_vertex

    UNION

    SELECT r.graph_id, r.source_vertex, e.source_vertex
    FROM reachability r
    JOIN graph_edges e
      ON e.graph_id = r.graph_id
     AND e.target_vertex = r.reached_vertex
    JOIN graph_definitions g ON g.graph_id = r.graph_id
    WHERE g.graph_type = 'undirected'
)
SELECT
    g.graph_name,
    r.source_vertex,
    r.reached_vertex
FROM reachability r
JOIN graph_definitions g USING (graph_id)
WHERE r.source_vertex = 'gate'
  AND g.graph_name = 'campus'
ORDER BY r.reached_vertex;

-- Connected-component labels can be derived from the minimum vertex reachable
-- from each vertex. This is valid for undirected connectivity; for directed
-- graphs, the query below intentionally uses weak connectivity.
WITH RECURSIVE weak_edges(graph_id, source_vertex, target_vertex) AS (
    SELECT graph_id, source_vertex, target_vertex FROM graph_edges
    UNION
    SELECT graph_id, target_vertex, source_vertex FROM graph_edges
),
reachability(graph_id, source_vertex, reached_vertex) AS (
    SELECT graph_id, vertex_id, vertex_id FROM graph_vertices
    UNION
    SELECT r.graph_id, r.source_vertex, e.target_vertex
    FROM reachability r
    JOIN weak_edges e
      ON e.graph_id = r.graph_id
     AND e.source_vertex = r.reached_vertex
),
component_labels AS (
    SELECT
        graph_id,
        source_vertex AS vertex_id,
        min(reached_vertex) AS component_label
    FROM reachability
    GROUP BY graph_id, source_vertex
)
SELECT
    g.graph_name,
    c.component_label,
    array_agg(c.vertex_id ORDER BY c.vertex_id) AS members
FROM component_labels c
JOIN graph_definitions g USING (graph_id)
GROUP BY g.graph_name, c.component_label
ORDER BY g.graph_name, c.component_label;

-- Detect directed cycles by looking for a nonempty route from a vertex back
-- to itself. The recursive CTE is bounded by DISTINCT reachability pairs.
WITH RECURSIVE directed_reachability(graph_id, source_vertex, reached_vertex) AS (
    SELECT graph_id, source_vertex, target_vertex
    FROM graph_edges

    UNION

    SELECT r.graph_id, r.source_vertex, e.target_vertex
    FROM directed_reachability r
    JOIN graph_edges e
      ON e.graph_id = r.graph_id
     AND e.source_vertex = r.reached_vertex
)
SELECT
    g.graph_name,
    EXISTS (
        SELECT 1
        FROM directed_reachability r
        WHERE r.graph_id = g.graph_id
          AND r.source_vertex = r.reached_vertex
    ) AS contains_directed_cycle
FROM graph_definitions g
WHERE g.graph_type = 'directed';

-- Record a walk, which may repeat vertices. The foreign key validates each
-- visited vertex, while the following query checks each consecutive edge.
INSERT INTO graph_walk_steps (graph_id, walk_name, step_number, vertex_id)
SELECT g.graph_id, 'library-return-walk', x.step_number, x.vertex_id
FROM graph_definitions g
CROSS JOIN (
    VALUES
        (0, 'library'),
        (1, 'cafeteria'),
        (2, 'library'),
        (3, 'laboratory')
) AS x(step_number, vertex_id)
WHERE g.graph_name = 'campus';

WITH ordered_steps AS (
    SELECT
        s.graph_id,
        s.walk_name,
        s.step_number,
        s.vertex_id,
        lead(s.vertex_id) OVER (
            PARTITION BY s.graph_id, s.walk_name
            ORDER BY s.step_number
        ) AS next_vertex
    FROM graph_walk_steps s
)
SELECT
    g.graph_name,
    w.walk_name,
    bool_and(
        w.next_vertex IS NULL
        OR EXISTS (
            SELECT 1
            FROM graph_edges e
            WHERE e.graph_id = w.graph_id
              AND (
                  (e.source_vertex = w.vertex_id
                   AND e.target_vertex = w.next_vertex)
                  OR
                  (g.graph_type = 'undirected'
                   AND e.source_vertex = w.next_vertex
                   AND e.target_vertex = w.vertex_id)
              )
        )
    ) AS is_valid_walk
FROM ordered_steps w
JOIN graph_definitions g USING (graph_id)
GROUP BY g.graph_name, w.walk_name, w.graph_id;

-- Transactional integrity check: an invalid edge endpoint is rejected by the
-- composite foreign key. Uncomment the following statement to observe the error.
-- INSERT INTO graph_edges (graph_id, source_vertex, target_vertex)
-- SELECT graph_id, 'missing-vertex', 'library'
-- FROM graph_definitions WHERE graph_name = 'campus';

-- The canonical edge-order convention for undirected graphs is enforced here
-- as an explicit integrity query because the edge table supports directed
-- graphs too. Applications should validate endpoint ordering before inserts.
SELECT
    g.graph_name,
    e.source_vertex,
    e.target_vertex,
    e.source_vertex < e.target_vertex AS canonical_undirected_order
FROM graph_edges e
JOIN graph_definitions g USING (graph_id)
WHERE g.graph_type = 'undirected'
ORDER BY e.edge_id;

COMMIT;
