"use strict";

/*
 * Graph Theory Fundamentals in JavaScript.
 *
 * This Node.js program explores dependency networks and communication
 * topologies using adjacency maps, edge lists, and adjacency matrices.
 * It also demonstrates traversal, event-driven graph updates, and
 * graph validation without third-party dependencies.
 */

class Graph {
  constructor({ directed = false, weighted = false } = {}) {
    this.directed = directed;
    this.weighted = weighted;
    this.adjacency = new Map();
    this.edgeCount = 0;
  }

  addVertex(vertex) {
    if (vertex === undefined || vertex === null) {
      throw new TypeError("A vertex cannot be null or undefined.");
    }

    if (!this.adjacency.has(vertex)) {
      this.adjacency.set(vertex, new Map());
    }

    return this;
  }

  requireVertex(vertex) {
    if (!this.adjacency.has(vertex)) {
      throw new Error(`Unknown vertex: ${String(vertex)}`);
    }
  }

  addEdge(source, target, weight = 1) {
    if (typeof weight !== "number" || !Number.isFinite(weight)) {
      throw new TypeError("Edge weights must be finite numbers.");
    }

    this.addVertex(source).addVertex(target);

    const outgoing = this.adjacency.get(source);
    const exists = outgoing.has(target);

    outgoing.set(target, weight);

    if (!this.directed && source !== target) {
      this.adjacency.get(target).set(source, weight);
    }

    if (!exists) {
      this.edgeCount += 1;
    }

    return this;
  }

  removeEdge(source, target) {
    this.requireVertex(source);
    this.requireVertex(target);

    if (!this.adjacency.get(source).has(target)) {
      return false;
    }

    this.adjacency.get(source).delete(target);

    if (!this.directed && source !== target) {
      this.adjacency.get(target).delete(source);
    }

    this.edgeCount -= 1;
    return true;
  }

  hasEdge(source, target) {
    this.requireVertex(source);
    this.requireVertex(target);
    return this.adjacency.get(source).has(target);
  }

  neighbors(vertex) {
    this.requireVertex(vertex);
    return [...this.adjacency.get(vertex).keys()];
  }

  inDegree(vertex) {
    this.requireVertex(vertex);

    if (!this.directed) {
      throw new Error("Use degree() for an undirected graph.");
    }

    let count = 0;

    for (const neighbors of this.adjacency.values()) {
      if (neighbors.has(vertex)) count += 1;
    }

    return count;
  }

  outDegree(vertex) {
    this.requireVertex(vertex);
    return this.adjacency.get(vertex).size;
  }

  degree(vertex) {
    this.requireVertex(vertex);

    if (this.directed) {
      throw new Error("Use inDegree() and outDegree() for directed graphs.");
    }

    let result = 0;

    for (const neighbor of this.adjacency.get(vertex).keys()) {
      result += neighbor === vertex ? 2 : 1;
    }

    return result;
  }

  edges() {
    const result = [];
    const position = new Map(
      [...this.adjacency.keys()].map((vertex, index) => [vertex, index])
    );

    for (const [source, neighbors] of this.adjacency) {
      for (const [target, weight] of neighbors) {
        if (this.directed || position.get(source) <= position.get(target)) {
          result.push({ source, target, weight });
        }
      }
    }

    return result;
  }

  toAdjacencyMatrix() {
    const vertices = [...this.adjacency.keys()];
    const indices = new Map(vertices.map((vertex, index) => [vertex, index]));

    // null represents no edge; zero remains a valid edge weight.
    const matrix = Array.from(
      { length: vertices.length },
      () => Array(vertices.length).fill(null)
    );

    for (const [source, neighbors] of this.adjacency) {
      for (const [target, weight] of neighbors) {
        matrix[indices.get(source)][indices.get(target)] = weight;
      }
    }

    return { vertices, matrix };
  }

  bfs(start) {
    this.requireVertex(start);

    const visited = new Set([start]);
    const queue = [start];
    const order = [];
    let head = 0;

    // Moving a head index avoids repeated Array.shift() reindexing.
    while (head < queue.length) {
      const vertex = queue[head++];
      order.push(vertex);

      for (const neighbor of this.adjacency.get(vertex).keys()) {
        if (!visited.has(neighbor)) {
          visited.add(neighbor);
          queue.push(neighbor);
        }
      }
    }

    return order;
  }

  dfs(start) {
    this.requireVertex(start);

    const visited = new Set();
    const stack = [start];
    const order = [];

    while (stack.length > 0) {
      const vertex = stack.pop();

      if (visited.has(vertex)) continue;

      visited.add(vertex);
      order.push(vertex);

      const neighbors = [...this.adjacency.get(vertex).keys()];

      for (let i = neighbors.length - 1; i >= 0; i--) {
        if (!visited.has(neighbors[i])) stack.push(neighbors[i]);
      }
    }

    return order;
  }

  shortestPath(source, target) {
    this.requireVertex(source);
    this.requireVertex(target);

    const parent = new Map([[source, null]]);
    const queue = [source];
    let head = 0;

    while (head < queue.length) {
      const vertex = queue[head++];

      if (vertex === target) break;

      for (const neighbor of this.adjacency.get(vertex).keys()) {
        if (!parent.has(neighbor)) {
          parent.set(neighbor, vertex);
          queue.push(neighbor);
        }
      }
    }

    if (!parent.has(target)) return null;

    const path = [];

    for (let current = target; current !== null; current = parent.get(current)) {
      path.push(current);
    }

    return path.reverse();
  }

  describe() {
    console.log(
      `${this.directed ? "Directed" : "Undirected"} graph: ` +
      `${this.adjacency.size} vertices, ${this.edgeCount} edges`
    );

    for (const [vertex, neighbors] of this.adjacency) {
      console.log(
        `  ${String(vertex)}: ` +
        JSON.stringify([...neighbors].map(([to, weight]) => ({ to, weight })))
      );
    }
  }
}

class GraphChangeEmitter {
  constructor(graph) {
    this.graph = graph;
    this.listeners = new Map();
  }

  on(eventName, callback) {
    if (typeof callback !== "function") {
      throw new TypeError("Event listener must be a function.");
    }

    if (!this.listeners.has(eventName)) this.listeners.set(eventName, new Set());
    this.listeners.get(eventName).add(callback);

    // Return an unsubscribe function to prevent listener leaks.
    return () => this.listeners.get(eventName)?.delete(callback);
  }

  emit(eventName, payload) {
    for (const listener of this.listeners.get(eventName) ?? []) {
      listener(payload);
    }
  }

  connect(source, target, weight = 1) {
    const existed = this.graph.hasEdge(source, target);
    this.graph.addEdge(source, target, weight);

    this.emit(existed ? "edgeUpdated" : "edgeAdded", {
      source,
      target,
      weight
    });
  }

  disconnect(source, target) {
    if (this.graph.removeEdge(source, target)) {
      this.emit("edgeRemoved", { source, target });
    }
  }
}

function demonstrateNetworkTopology() {
  console.log("\n=== Network topology ===");

  const network = new Graph({ directed: false, weighted: true });

  network
    .addVertex("Backup node")
    .addEdge("Gateway", "Core switch", 2)
    .addEdge("Core switch", "Application server", 1)
    .addEdge("Core switch", "Database server", 3)
    .addEdge("Gateway", "Remote office", 8);

  network.describe();

  console.log("BFS:", network.bfs("Gateway"));
  console.log("DFS:", network.dfs("Gateway"));
  console.log(
    "Minimum-hop route:",
    network.shortestPath("Gateway", "Database server")
  );

  const representation = network.toAdjacencyMatrix();
  console.log("Matrix vertices:", representation.vertices);
  console.log("Matrix:", representation.matrix);
}

function demonstrateDependencyDirection() {
  console.log("\n=== Directed build dependencies ===");

  const dependencies = new Graph({ directed: true });

  dependencies
    .addEdge("Schema", "API")
    .addEdge("API", "Frontend")
    .addEdge("API", "Integration tests");

  console.log("Downstream from Schema:", dependencies.bfs("Schema"));
  console.log("Schema in-degree:", dependencies.inDegree("Schema"));
  console.log("API out-degree:", dependencies.outDegree("API"));
  console.log(
    "Can Frontend reach Schema?",
    dependencies.bfs("Frontend").includes("Schema")
  );
}

function demonstrateEventDrivenChanges() {
  console.log("\n=== Event-driven topology changes ===");

  const graph = new Graph();
  graph.addVertex("Primary");

  const events = new GraphChangeEmitter(graph);

  const unsubscribe = events.on("edgeAdded", ({ source, target }) => {
    console.log(`Topology updated: ${source} now connects to ${target}`);
  });

  events.on("edgeRemoved", ({ source, target }) => {
    console.log(`Topology removed: ${source} no longer connects to ${target}`);
  });

  events.connect("Primary", "Replica");
  events.connect("Primary", "Replica");
  events.disconnect("Primary", "Replica");

  unsubscribe();
}

function runTests() {
  const graph = new Graph();

  graph.addEdge("A", "B").addEdge("B", "C");
  graph.addVertex("D");

  console.assert(graph.edgeCount === 2, "Undirected edge count");
  console.assert(graph.degree("B") === 2, "Middle vertex degree");
  console.assert(graph.bfs("A").join(",") === "A,B,C", "BFS order");
  console.assert(
    graph.shortestPath("A", "C").join(",") === "A,B,C",
    "Shortest path"
  );
  console.assert(graph.shortestPath("A", "D") === null, "Disconnected path");

  const directed = new Graph({ directed: true });
  directed.addEdge("X", "Y");

  console.assert(directed.inDegree("Y") === 1, "Directed in-degree");
  console.assert(directed.outDegree("X") === 1, "Directed out-degree");
  console.assert(!directed.hasEdge("Y", "X"), "Direction must be preserved");

  const zeroWeight = new Graph({ weighted: true });
  zeroWeight.addEdge("A", "B", 0);
  console.assert(zeroWeight.hasEdge("A", "B"), "Zero-weight edge exists");

  try {
    graph.bfs("Missing");
    throw new Error("Unknown vertices should be rejected.");
  } catch (error) {
    console.log("Validation test:", error.message);
  }

  console.log("Graph assertions completed.");
}

function main() {
  demonstrateNetworkTopology();
  demonstrateDependencyDirection();
  demonstrateEventDrivenChanges();
  runTests();
}

main();
