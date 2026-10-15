-- Graph Connectivity: PostgreSQL relational model and operational analysis.
-- The schema represents physical sites, undirected links, directed routes,
-- connected components, link failures, and service reachability.
--
-- Run this complete script in a dedicated PostgreSQL database.
-- The transaction rolls back at the end so the example leaves no persistent
-- demonstration data behind.

BEGIN;

DROP SCHEMA IF EXISTS graph_connectivity_lab CASCADE;
CREATE SCHEMA graph_connectivity_lab;
SET LOCAL search_path TO graph_connectivity_lab, public;

CREATE TABLE site (
    site_id       text PRIMARY KEY,
    site_name     text NOT NULL,
    site_type     text NOT NULL CHECK (
        site_type IN (
            'CONTROL_CENTER',
            'DATA_CENTER',
            'GATEWAY',
            'SENSOR'
        )
    ),
    region        text NOT NULL,
    commissioned  boolean NOT NULL DEFAULT true,
    created_at    timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(site_id)) > 0),
    CHECK (length(trim(site_name)) > 0)
);

-- An undirected link has one canonical endpoint order. The generated
-- endpoint columns prevent A--B and B--A from being stored as separate links.
CREATE TABLE network_link (
    link_id       bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    endpoint_a    text NOT NULL REFERENCES site(site_id) ON DELETE RESTRICT,
    endpoint_b    text NOT NULL REFERENCES site(site_id) ON DELETE RESTRICT,
    bandwidth_mbps integer NOT NULL CHECK (bandwidth_mbps > 0),
    operational   boolean NOT NULL DEFAULT true,
    CHECK (endpoint_a < endpoint_b),
    UNIQUE (endpoint_a, endpoint_b)
);

CREATE INDEX idx_network_link_endpoint_b
    ON network_link(endpoint_b);

CREATE INDEX idx_network_link_operational
    ON network_link(operational)
    WHERE operational;

CREATE TABLE directed_route (
    route_id      bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_site   text NOT NULL REFERENCES site(site_id) ON DELETE RESTRICT,
    target_site   text NOT NULL REFERENCES site(site_id) ON DELETE RESTRICT,
    route_kind    text NOT NULL CHECK (
        route_kind IN ('CONTROL', 'TELEMETRY', 'BACKUP')
    ),
    enabled       boolean NOT NULL DEFAULT true,
    CHECK (source_site <> target_site),
    UNIQUE (source_site, target_site, route_kind)
);

CREATE INDEX idx_directed_route_source
    ON directed_route(source_site)
    WHERE enabled;

CREATE TABLE service_requirement (
    service_id    text NOT NULL,
    required_site text NOT NULL REFERENCES site(site_id) ON DELETE RESTRICT,
    PRIMARY KEY (service_id, required_site),
    CHECK (length(trim(service_id)) > 0)
);

CREATE TABLE link_failure (
    failure_id    bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    link_id       bigint NOT NULL REFERENCES network_link(link_id)
                  ON DELETE RESTRICT,
    failure_reason text NOT NULL,
    started_at    timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    recovered_at timestamptz,
    CHECK (recovered_at IS NULL OR recovered_at >= started_at)
);

CREATE INDEX idx_active_link_failures
    ON link_failure(link_id)
    WHERE recovered_at IS NULL;

-- Current operational links exclude links with an active failure record.
CREATE VIEW operational_link AS
SELECT l.link_id, l.endpoint_a, l.endpoint_b, l.bandwidth_mbps
FROM network_link AS l
WHERE l.operational
  AND NOT EXISTS (
      SELECT 1
      FROM link_failure AS f
      WHERE f.link_id = l.link_id
        AND f.recovered_at IS NULL
  );

INSERT INTO site (site_id, site_name, site_type, region) VALUES
    ('CTRL', 'Regional Control', 'CONTROL_CENTER', 'North'),
    ('DC1', 'Primary Data Center', 'DATA_CENTER', 'North'),
    ('GW1', 'Field Gateway One', 'GATEWAY', 'North'),
    ('GW2', 'Field Gateway Two', 'GATEWAY', 'North'),
    ('SNS1', 'Water Sensor Station', 'SENSOR', 'North'),
    ('BACKUP', 'Backup Control Center', 'CONTROL_CENTER', 'Central'),
    ('ISLAND', 'Isolated Remote Station', 'SENSOR', 'South');

INSERT INTO network_link (
    endpoint_a, endpoint_b, bandwidth_mbps
) VALUES
    ('CTRL', 'DC1', 10000),
    ('CTRL', 'GW1', 1000),
    ('DC1', 'GW1', 1000),
    ('GW1', 'GW2', 500),
    ('GW2', 'SNS1', 250),
    ('BACKUP', 'SNS1', 100);

INSERT INTO directed_route (
    source_site, target_site, route_kind
) VALUES
    ('CTRL', 'DC1', 'CONTROL'),
    ('DC1', 'GW1', 'TELEMETRY'),
    ('GW1', 'GW2', 'TELEMETRY'),
    ('GW2', 'SNS1', 'TELEMETRY'),
    ('BACKUP', 'SNS1', 'BACKUP');

INSERT INTO service_requirement (service_id, required_site) VALUES
    ('water-telemetry', 'GW1'),
    ('water-telemetry', 'GW2'),
    ('water-telemetry', 'SNS1');

-- A recursive traversal computes reachability from a designated root.
-- UNION, rather than UNION ALL, deduplicates visited sites and terminates
-- even when the operational graph contains cycles.
CREATE FUNCTION reachable_sites(start_site text)
RETURNS TABLE(site_id text)
LANGUAGE sql
STABLE
AS $function$
    WITH RECURSIVE reachable(site_id) AS (
        SELECT s.site_id
        FROM site AS s
        WHERE s.site_id = start_site
          AND s.commissioned

        UNION

        SELECT CASE
                   WHEN l.endpoint_a = r.site_id THEN l.endpoint_b
                   ELSE l.endpoint_a
               END
        FROM reachable AS r
        JOIN operational_link AS l
          ON l.endpoint_a = r.site_id
          OR l.endpoint_b = r.site_id
        JOIN site AS destination
          ON destination.site_id = CASE
               WHEN l.endpoint_a = r.site_id THEN l.endpoint_b
               ELSE l.endpoint_a
          END
        WHERE destination.commissioned
    )
    SELECT reachable.site_id
    FROM reachable;
$function$;

-- Return a per-service reachability report from the designated control site.
CREATE VIEW service_reachability AS
SELECT
    requirement.service_id,
    requirement.required_site,
    reachable.site_id IS NOT NULL AS reachable_from_control
FROM service_requirement AS requirement
LEFT JOIN reachable_sites('CTRL') AS reachable
    ON reachable.site_id = requirement.required_site;

-- Operational reachability for the baseline topology.
SELECT site_id
FROM reachable_sites('CTRL')
ORDER BY site_id;

SELECT
    service_id,
    count(*) AS required_site_count,
    count(*) FILTER (WHERE reachable_from_control) AS reachable_site_count,
    bool_and(reachable_from_control) AS service_fully_reachable
FROM service_reachability
GROUP BY service_id
ORDER BY service_id;

-- Demonstrate failure recording without deleting the underlying link.
INSERT INTO link_failure (link_id, failure_reason)
SELECT link_id, 'Simulated cable interruption'
FROM network_link
WHERE endpoint_a = 'GW1'
  AND endpoint_b = 'GW2';

SELECT
    endpoint_a,
    endpoint_b,
    bandwidth_mbps
FROM operational_link
ORDER BY endpoint_a, endpoint_b;

SELECT
    service_id,
    required_site,
    reachable_from_control
FROM service_reachability
ORDER BY service_id, required_site;

-- A recovered failure is historical evidence, not an active outage.
UPDATE link_failure
SET recovered_at = CURRENT_TIMESTAMP
WHERE failure_reason = 'Simulated cable interruption'
  AND recovered_at IS NULL;

SELECT
    endpoint_a,
    endpoint_b,
    bandwidth_mbps
FROM operational_link
WHERE endpoint_a = 'GW1'
  AND endpoint_b = 'GW2';

-- A cycle-free connectivity check is not enough to assess resilience.
-- This query counts active operational degree, identifying sites with
-- only one operational neighbor. Such sites have a single-link dependency.
WITH degrees AS (
    SELECT s.site_id, count(n.link_id) AS operational_degree
    FROM site AS s
    LEFT JOIN (
        SELECT endpoint_a AS site_id, link_id
        FROM operational_link
        UNION ALL
        SELECT endpoint_b AS site_id, link_id
        FROM operational_link
    ) AS n ON n.site_id = s.site_id
    GROUP BY s.site_id
)
SELECT site_id, operational_degree
FROM degrees
WHERE operational_degree <= 1
ORDER BY site_id;

-- Integrity enforcement examples are kept inside exception subtransactions.
-- Invalid self-links violate endpoint ordering and are rejected.
DO $block$
BEGIN
    BEGIN
        INSERT INTO network_link (
            endpoint_a, endpoint_b, bandwidth_mbps
        ) VALUES ('CTRL', 'CTRL', 100);
        RAISE EXCEPTION 'Expected self-link validation to fail';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Self-link rejected by CHECK constraint';
    END;

    BEGIN
        INSERT INTO network_link (
            endpoint_a, endpoint_b, bandwidth_mbps
        ) VALUES ('GW1', 'CTRL', 100);
        RAISE EXCEPTION 'Expected non-canonical link order to fail';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Non-canonical endpoint order rejected';
    END;

    BEGIN
        INSERT INTO network_link (
            endpoint_a, endpoint_b, bandwidth_mbps
        ) VALUES ('CTRL', 'NOT-A-SITE', 100);
        RAISE EXCEPTION 'Expected foreign-key validation to fail';
    EXCEPTION
        WHEN foreign_key_violation THEN
            RAISE NOTICE 'Unknown site rejected by foreign key';
    END;
END;
$block$;

-- Recursive reachability is a snapshot query, not a continuously maintained
-- connectivity index. For large, frequently changing graphs, consider
-- maintained component labels or an application-side DSU for insertion-only
-- workloads. DSU does not directly support arbitrary edge deletions.
ROLLBACK;
