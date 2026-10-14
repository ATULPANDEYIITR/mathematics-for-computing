"use strict";

/*
 * Graph Traversal Mathematics in JavaScript
 *
 * Demonstrates BFS, DFS, reachability, shortest paths, traversal trees,
 * event-driven traversal, directed-cycle detection, and graph invariants.
 *
 * Run with Node.js:
 *     node graph_traversal.js
 */

class GraphError extends Error {
  constructor(message) {
    super(message);
    this.name = "GraphError";
  }
}

class Graph {
  #adjacency = new Map();

  constructor({ directed = false } = {}) {
    this.directed = directed;
  }

  addVertex(vertex) {
    if (vertex === null || vertex === undefined) {
      throw new GraphError("Vertices cannot be null or undefined.");
    }

    if (!this.#adjacency.has(vertex)) {
      this.#adjacency.set(vertex, new Set());
    }

    return this;
  }

  addEdge(source, target) {
    this.addVertex(source);
    this.addVertex(target);

    this.#adjacency.get(source).add(target);

    if (!this.directed) {
      this.#adjacency.get(target).add(source);
    }

    return this;
  }

  hasVertex(vertex) {
    return this.#adjacency.has(vertex);
  }

  vertices() {
    return [...this.#adjacency.keys()];
  }

  neighbors(vertex) {
    this.#requireVertex(vertex);
    return [...this.#adjacency.get(vertex)];
  }

  edgeCount() {
    const total = [...this.#adjacency.values()]
      .reduce((sum, neighbors) => sum + neighbors.size, 0);

    return this.directed ? total : total / 2;
  }

  #requireVertex(vertex) {
    if (!this.#adjacency.has(vertex)) {
      throw new GraphError(`Unknown vertex: ${String(vertex)}`);
    }
  }

  bfs(start, onVisit = () => {}) {
    this.#requireVertex(start);

    const visited = new Set([start]);
    const queue = [start];
    const order = [];

    // A head index avoids the repeated array shifting caused by Array.shift().
    let head = 0;

    while (head < queue.length) {
      const current = queue[head++];
      order.push(current);
      onVisit(current);

      for (const neighbor of this.#adjacency.get(current)) {
        if (!visited.has(neighbor)) {
          // Discovery happens before enqueueing, so each vertex is queued once.
          visited.add(neighbor);
          queue.push(neighbor);
        }
      }
    }

    return order;
  }

  bfsTree(start) {
    this.#requireVertex(start);

    const parent = new Map([[start, null]]);
    const distance = new Map([[start, 0]]);
    const order = [];
    const queue = [start];
    let head = 0;

    while (head < queue.length) {
      const current = queue[head++];
      order.push(current);

      for (const neighbor of this.#adjacency.get(current)) {
        if (!parent.has(neighbor)) {
          parent.set(neighbor, current);
          distance.set(neighbor, distance.get(current) + 1);
          queue.push(neighbor);
        }
      }
    }

    return { order, parent, distance };
  }

  dfs(start) {
    this.#requireVertex(start);

    const visited = new Set();
    const order = [];
    const stack = [start];

    while (stack.length > 0) {
      const current = stack.pop();

      if (visited.has(current)) {
        continue;
      }

      visited.add(current);
      order.push(current);

      const neighbors = [...this.#adjacency.get(current)];

      // Reverse pushing preserves the adjacency order when popping.
      for (let index = neighbors.length - 1; index >= 0; index--) {
        if (!visited.has(neighbors[index])) {
          stack.push(neighbors[index]);
        }
      }
    }

    return order;
  }

  reachable(source, target) {
    this.#requireVertex(source);
    this.#requireVertex(target);

    if (Object.is(source, target)) {
      return true;
    }

    const visited = new Set([source]);
    const queue = [source];
    let head = 0;

    while (head < queue.length) {
      const current = queue[head++];

      for (const neighbor of this.#adjacency.get(current)) {
        if (Object.is(neighbor, target)) {
          return true;
        }

        if (!visited.has(neighbor)) {
          visited.add(neighbor);
          queue.push(neighbor);
        }
      }
    }

    return false;
  }

  shortestPath(source, target) {
    this.#requireVertex(source);
    this.#requireVertex(target);

    const parent = new Map([[source, null]]);
    const queue = [source];
    let head = 0;

    while (head < queue.length) {
      const current = queue[head++];

      if (Object.is(current, target)) {
        const path = [];
        let cursor = target;

        while (cursor !== null) {
          path.push(cursor);
          cursor = parent.get(cursor);
        }

        return path.reverse();
      }

      for (const neighbor of this.#adjacency.get(current)) {
        if (!parent.has(neighbor)) {
          parent.set(neighbor, current);
          queue.push(neighbor);
        }
      }
    }

    return null;
  }

  hasDirectedCycle() {
    if (!this.directed) {
      throw new GraphError("Directed-cycle detection needs a directed graph.");
    }

    const color = new Map(
      this.vertices().map((vertex) => [vertex, 0])
    );

    const visit = (vertex) => {
      color.set(vertex, 1);

      for (const neighbor of this.#adjacency.get(vertex)) {
        if (color.get(neighbor) === 1) {
          return true;
        }

        if (color.get(neighbor) === 0 && visit(neighbor)) {
          return true;
        }
      }

      color.set(vertex, 2);
      return false;
    };

    for (const vertex of this.vertices()) {
      if (color.get(vertex) === 0 && visit(vertex)) {
        return true;
      }
    }

    return false;
  }

  stronglyConnectedComponents() {
    if (!this.directed) {
      throw new GraphError("Strongly connected components require a directed graph.");
    }

    // Kosaraju's algorithm: finish-order DFS, then DFS on the transposed graph.
    const visited = new Set();
    const finishOrder = [];

    const finishDfs = (vertex) => {
      visited.add(vertex);

      for (const neighbor of this.#adjacency.get(vertex)) {
        if (!visited.has(neighbor)) {
          finishDfs(neighbor);
        }
      }

      finishOrder.push(vertex);
    };

    for (const vertex of this.vertices()) {
      if (!visited.has(vertex)) {
        finishDfs(vertex);
      }
    }

    const transpose = new Graph({ directed: true });

    for (const vertex of this.vertices()) {
      transpose.addVertex(vertex);
    }

    for (const [source, neighbors] of this.#adjacency) {
      for (const target of neighbors) {
        transpose.addEdge(target, source);
      }
    }

    visited.clear();
    const components = [];

    const collect = (vertex, component) => {
      visited.add(vertex);
      component.push(vertex);

      for (const neighbor of transpose.#adjacency.get(vertex)) {
        if (!visited.has(neighbor)) {
          collect(neighbor, component);
        }
      }
    };

    while (finishOrder.length > 0) {
      const vertex = finishOrder.pop();

      if (!visited.has(vertex)) {
        const component = [];
        collect(vertex, component);
        components.push(component);
      }
    }

    return components;
  }
}

class TraversalEventLog {
  constructor() {
    this.events = [];
  }

  record(type, vertex, details = {}) {
    this.events.push(
      Object.freeze({
        sequence: this.events.length,
        type,
        vertex,
        ...details
      })
    );
  }

  getEvents() {
    return this.events.map((event) => ({ ...event }));
  }
}

async function* breadthFirstEvents(graph, start) {
  if (!graph.hasVertex(start)) {
    throw new GraphError(`Unknown vertex: ${String(start)}`);
  }

  const visited = new Set([start]);
  const queue = [start];
  const distance = new Map([[start, 0]]);
  let head = 0;

  while (head < queue.length) {
    const current = queue[head++];

    yield {
      type: "visit",
      vertex: current,
      distance: distance.get(current)
    };

    for (const neighbor of graph.neighbors(current)) {
      if (!visited.has(neighbor)) {
        visited.add(neighbor);
        distance.set(neighbor, distance.get(current) + 1);
        queue.push(neighbor);

        yield {
          type: "discover",
          vertex: neighbor,
          parent: current,
          distance: distance.get(neighbor)
        };
      }
    }
  }
}

async function runEventDrivenTraversal(graph, start) {
  const log = new TraversalEventLog();

  // The asynchronous iterator allows consumers to process events incrementally.
  for await (const event of breadthFirstEvents(graph, start)) {
    log.record(event.type, event.vertex, {
      parent: event.parent ?? null,
      distance: event.distance
    });
  }

  return log;
}

function validateBfsTree(graph, start, tree) {
  if (!tree.parent.has(start) || tree.parent.get(start) !== null) {
    return false;
  }

  if (tree.distance.get(start) !== 0) {
    return false;
  }

  if (tree.parent.size !== tree.distance.size) {
    return false;
  }

  for (const [vertex, parent] of tree.parent) {
    if (vertex === start) {
      continue;
    }

    if (parent === null || !tree.parent.has(parent)) {
      return false;
    }

    if (!graph.neighbors(parent).includes(vertex)) {
      return false;
    }

    if (tree.distance.get(vertex) !== tree.distance.get(parent) + 1) {
      return false;
    }
  }

  return true;
}

async function main() {
  const graph = new Graph();

  for (const vertex of ["gateway", "api", "worker", "database", "cache", "archive"]) {
    graph.addVertex(vertex);
  }

  graph
    .addEdge("gateway", "api")
    .addEdge("gateway", "worker")
    .addEdge("api", "database")
    .addEdge("worker", "database")
    .addEdge("worker", "cache");

  console.log("Undirected service-connectivity graph");
  console.log("Vertices:", graph.vertices());
  console.log("Edges:", graph.edgeCount());
  console.log("BFS:", graph.bfs("gateway"));
  console.log("DFS:", graph.dfs("gateway"));
  console.log("Reachable gateway -> cache:", graph.reachable("gateway", "cache"));
  console.log("Reachable gateway -> archive:", graph.reachable("gateway", "archive"));
  console.log("Shortest path:", graph.shortestPath("gateway", "database"));

  const tree = graph.bfsTree("gateway");

  console.log("BFS parent map:", Object.fromEntries(tree.parent));
  console.log("BFS distance map:", Object.fromEntries(tree.distance));
  console.log("Tree invariant validation:", validateBfsTree(graph, "gateway", tree));

  const eventLog = await runEventDrivenTraversal(graph, "gateway");
  console.log("Traversal event count:", eventLog.getEvents().length);
  console.log("Traversal events:", eventLog.getEvents());

  const dependencies = new Graph({ directed: true });
  dependencies
    .addEdge("compile", "unit-test")
    .addEdge("unit-test", "integration-test")
    .addEdge("integration-test", "release")
    .addEdge("compile", "static-analysis");

  console.log("Dependency cycle:", dependencies.hasDirectedCycle());

  dependencies.addEdge("release", "compile");
  console.log("Cycle after invalid dependency:", dependencies.hasDirectedCycle());

  const directedNetwork = new Graph({ directed: true });
  directedNetwork
    .addEdge("A", "B")
    .addEdge("B", "A")
    .addEdge("B", "C")
    .addEdge("C", "D")
    .addEdge("D", "C")
    .addVertex("E");

  console.log(
    "Strongly connected components:",
    directedNetwork.stronglyConnectedComponents()
  );

  try {
    graph.bfs("missing");
  } catch (error) {
    console.log("Invalid start handled:", error.message);
  }
}

main().catch((error) => {
  console.error("Traversal failed:", error);
  process.exitCode = 1;
});
