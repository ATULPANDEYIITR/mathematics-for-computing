"use strict";

/*
 * Graph connectivity with event-driven analysis.
 *
 * This Node.js program models changes to an undirected network, incrementally
 * invalidates cached analyses when topology changes, evaluates single-link
 * and single-vertex failures, and computes strongly connected components
 * in a directed service graph.
 *
 * Run with: node graph_connectivity.js
 */

const assert = require("node:assert/strict");

class GraphValidationError extends Error {}

class UndirectedNetwork {
  #adjacency = new Map();
  #edges = [];
  #version = 0;
  #cachedAnalysis = null;

  get version() {
    return this.#version;
  }

  get vertexCount() {
    return this.#adjacency.size;
  }

  get edgeCount() {
    return this.#edges.length;
  }

  addVertex(vertex) {
    if (typeof vertex !== "string" || vertex.trim() === "") {
      throw new GraphValidationError("Vertex names must be non-empty strings.");
    }

    if (!this.#adjacency.has(vertex)) {
      this.#adjacency.set(vertex, []);
      this.#invalidate();
    }
  }

  addEdge(left, right) {
    this.addVertex(left);
    this.addVertex(right);

    const edge = Object.freeze({
      id: this.#edges.length,
      left,
      right,
    });

    this.#edges.push(edge);
    this.#adjacency.get(left).push({ neighbor: right, edgeId: edge.id });
    this.#adjacency.get(right).push({ neighbor: left, edgeId: edge.id });
    this.#invalidate();

    return edge.id;
  }

  #invalidate() {
    this.#version += 1;
    this.#cachedAnalysis = null;
  }

  #assertKnownVertex(vertex) {
    if (!this.#adjacency.has(vertex)) {
      throw new GraphValidationError(`Unknown vertex: ${vertex}`);
    }
  }

  connectedComponents(excludedVertex = null) {
    if (excludedVertex !== null) {
      this.#assertKnownVertex(excludedVertex);
    }

    const visited = new Set();
    const components = [];

    for (const start of this.#adjacency.keys()) {
      if (start === excludedVertex || visited.has(start)) continue;

      const component = new Set();
      const queue = [start];
      let head = 0;
      visited.add(start);

      // A head index avoids the repeated array shifting caused by Array.shift.
      while (head < queue.length) {
        const current = queue[head++];
        component.add(current);

        for (const { neighbor } of this.#adjacency.get(current)) {
          if (neighbor === excludedVertex || visited.has(neighbor)) continue;
          visited.add(neighbor);
          queue.push(neighbor);
        }
      }

      components.push(component);
    }

    return components;
  }

  analyze() {
    if (this.#cachedAnalysis?.version === this.#version) {
      return this.#cachedAnalysis;
    }

    const discovery = new Map();
    const low = new Map();
    const parent = new Map();
    const parentEdge = new Map();
    const childCount = new Map();
    const bridges = [];
    const articulationPoints = new Set();
    let clock = 0;

    for (const root of this.#adjacency.keys()) {
      if (discovery.has(root)) continue;

      discovery.set(root, clock);
      low.set(root, clock++);
      parent.set(root, null);
      parentEdge.set(root, null);
      childCount.set(root, 0);

      const stack = [{ vertex: root, nextEdge: 0 }];

      while (stack.length > 0) {
        const frame = stack[stack.length - 1];
        const neighbors = this.#adjacency.get(frame.vertex);

        if (frame.nextEdge < neighbors.length) {
          const { neighbor, edgeId } = neighbors[frame.nextEdge++];

          if (edgeId === parentEdge.get(frame.vertex)) continue;

          if (!discovery.has(neighbor)) {
            parent.set(neighbor, frame.vertex);
            parentEdge.set(neighbor, edgeId);
            childCount.set(
              frame.vertex,
              (childCount.get(frame.vertex) ?? 0) + 1
            );
            childCount.set(neighbor, 0);
            discovery.set(neighbor, clock);
            low.set(neighbor, clock++);
            stack.push({ vertex: neighbor, nextEdge: 0 });
          } else {
            low.set(
              frame.vertex,
              Math.min(low.get(frame.vertex), discovery.get(neighbor))
            );
          }
        } else {
          stack.pop();
          const ancestor = parent.get(frame.vertex);

          if (ancestor === null) {
            if (childCount.get(frame.vertex) > 1) {
              articulationPoints.add(frame.vertex);
            }
            continue;
          }

          low.set(
            ancestor,
            Math.min(low.get(ancestor), low.get(frame.vertex))
          );

          if (low.get(frame.vertex) > discovery.get(ancestor)) {
            bridges.push(parentEdge.get(frame.vertex));
          }

          if (
            parent.get(ancestor) !== null &&
            low.get(frame.vertex) >= discovery.get(ancestor)
          ) {
            articulationPoints.add(ancestor);
          }
        }
      }
    }

    this.#cachedAnalysis = Object.freeze({
      version: this.#version,
      bridges: Object.freeze(bridges.map((id) => this.#edges[id])),
      articulationPoints: Object.freeze([...articulationPoints]),
      componentCount: this.connectedComponents().length,
      connected:
        this.#adjacency.size > 0 &&
        this.connectedComponents().length === 1,
    });

    return this.#cachedAnalysis;
  }

  simulateVertexFailure(vertex) {
    this.#assertKnownVertex(vertex);

    const before = this.connectedComponents().length;
    const after = this.connectedComponents(vertex).length;

    return Object.freeze({
      vertex,
      componentsBefore: before,
      componentsAfter: after,
      causesAdditionalFragmentation: after > before,
    });
  }

  simulateEdgeFailure(edgeId) {
    if (!Number.isInteger(edgeId) || !this.#edges[edgeId]) {
      throw new GraphValidationError(`Unknown edge ID: ${edgeId}`);
    }

    const before = this.connectedComponents().length;
    const reduced = new Map(
      [...this.#adjacency.keys()].map((vertex) => [vertex, []])
    );

    for (const edge of this.#edges) {
      if (edge.id === edgeId) continue;

      reduced.get(edge.left).push(edge.right);
      reduced.get(edge.right).push(edge.left);
    }

    const visited = new Set();
    let componentCount = 0;

    for (const start of reduced.keys()) {
      if (visited.has(start)) continue;

      componentCount += 1;
      const queue = [start];
      let head = 0;
      visited.add(start);

      while (head < queue.length) {
        const current = queue[head++];
        for (const neighbor of reduced.get(current)) {
          if (!visited.has(neighbor)) {
            visited.add(neighbor);
            queue.push(neighbor);
          }
        }
      }
    }

    return Object.freeze({
      edgeId,
      componentsBefore: before,
      componentsAfter: componentCount,
      disconnectsNetwork: componentCount > before,
    });
  }
}

class DirectedServiceGraph {
  #adjacency = new Map();

  addVertex(vertex) {
    if (typeof vertex !== "string" || vertex.trim() === "") {
      throw new GraphValidationError("Service names must be non-empty strings.");
    }
    if (!this.#adjacency.has(vertex)) this.#adjacency.set(vertex, []);
  }

  addDependency(source, target) {
    this.addVertex(source);
    this.addVertex(target);
    this.#adjacency.get(source).push(target);
  }

  stronglyConnectedComponents() {
    const index = new Map();
    const low = new Map();
    const activeStack = [];
    const onStack = new Set();
    const components = [];
    let clock = 0;

    for (const root of this.#adjacency.keys()) {
      if (index.has(root)) continue;

      index.set(root, clock);
      low.set(root, clock++);
      activeStack.push(root);
      onStack.add(root);

      const frames = [{ vertex: root, nextEdge: 0 }];

      while (frames.length > 0) {
        const frame = frames[frames.length - 1];
        const neighbors = this.#adjacency.get(frame.vertex);

        if (frame.nextEdge < neighbors.length) {
          const neighbor = neighbors[frame.nextEdge++];

          if (!index.has(neighbor)) {
            index.set(neighbor, clock);
            low.set(neighbor, clock++);
            activeStack.push(neighbor);
            onStack.add(neighbor);
            frames.push({ vertex: neighbor, nextEdge: 0 });
          } else if (onStack.has(neighbor)) {
            low.set(
              frame.vertex,
              Math.min(low.get(frame.vertex), index.get(neighbor))
            );
          }
        } else {
          frames.pop();

          if (frames.length > 0) {
            const parent = frames[frames.length - 1].vertex;
            low.set(parent, Math.min(low.get(parent), low.get(frame.vertex)));
          }

          if (low.get(frame.vertex) === index.get(frame.vertex)) {
            const component = [];

            while (true) {
              const member = activeStack.pop();
              onStack.delete(member);
              component.push(member);
              if (member === frame.vertex) break;
            }

            components.push(component.sort());
          }
        }
      }
    }

    return components;
  }

  condensationDag() {
    const components = this.stronglyConnectedComponents();
    const owner = new Map();

    components.forEach((component, componentId) => {
      component.forEach((vertex) => owner.set(vertex, componentId));
    });

    const edges = new Set();

    for (const [source, neighbors] of this.#adjacency) {
      for (const target of neighbors) {
        const from = owner.get(source);
        const to = owner.get(target);
        if (from !== to) edges.add(`${from}->${to}`);
      }
    }

    return { components, edges: [...edges].sort() };
  }
}

function printConnectivityReport(network) {
  const report = network.analyze();

  console.log({
    version: report.version,
    vertices: network.vertexCount,
    edges: network.edgeCount,
    connected: report.connected,
    components: report.componentCount,
    bridges: report.bridges.map(({ left, right, id }) => ({
      id,
      endpoints: `${left}-${right}`,
    })),
    articulationPoints: report.articulationPoints,
  });
}

function run() {
  console.log("=== Change-aware network analysis ===");

  const network = new UndirectedNetwork();
  for (const site of ["gateway", "switch-a", "switch-b", "database", "backup"]) {
    network.addVertex(site);
  }

  network.addEdge("gateway", "switch-a");
  network.addEdge("switch-a", "switch-b");
  network.addEdge("switch-b", "database");
  network.addEdge("switch-a", "backup");
  network.addEdge("backup", "switch-b");

  printConnectivityReport(network);

  const cached = network.analyze();
  assert.equal(network.analyze(), cached);

  console.log(
    "Database failure:",
    network.simulateVertexFailure("database")
  );

  console.log("Removing the gateway link:", network.simulateEdgeFailure(0));

  // A topology mutation increments the version and invalidates cached results.
  network.addEdge("gateway", "switch-b");
  assert.notEqual(network.analyze(), cached);
  printConnectivityReport(network);

  console.log("\n=== Directed dependency SCCs ===");

  const services = new DirectedServiceGraph();
  [
    ["api", "identity"],
    ["identity", "token-store"],
    ["token-store", "identity"],
    ["api", "events"],
    ["events", "consumer"],
    ["consumer", "events"],
    ["consumer", "warehouse"],
  ].forEach(([source, target]) => services.addDependency(source, target));

  console.log(services.condensationDag());

  assert.throws(
    () => network.simulateVertexFailure("missing"),
    GraphValidationError
  );

  assert.throws(
    () => network.simulateEdgeFailure(999),
    GraphValidationError
  );

  console.log("\nValidation checks passed.");
}

run();
