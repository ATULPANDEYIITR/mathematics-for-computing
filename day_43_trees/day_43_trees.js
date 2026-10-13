"use strict";

/*
 * Trees in JavaScript: rooted hierarchies, binary trees, tree properties,
 * and spanning trees for weighted networks.
 *
 * Run with Node.js 18 or later:
 * node trees.js
 */

class TreeError extends Error {
  constructor(message) {
    super(message);
    this.name = "TreeError";
  }
}

class RootedNode {
  constructor(value) {
    if (typeof value !== "string" || value.trim() === "") {
      throw new TreeError("A rooted-tree node needs a nonempty label.");
    }

    this.value = value;
    this.parent = null;
    this.children = [];
  }

  addChild(child) {
    if (!(child instanceof RootedNode)) {
      throw new TreeError("Child must be a RootedNode.");
    }
    if (child === this || child.parent !== null) {
      throw new TreeError("Self-links and multiple parents are forbidden.");
    }

    // Walking upward prevents an ancestor from being attached below itself.
    for (let ancestor = this; ancestor !== null; ancestor = ancestor.parent) {
      if (ancestor === child) {
        throw new TreeError("The attachment would create a cycle.");
      }
    }

    child.parent = this;
    this.children.push(child);
  }
}

function rootedMetrics(root) {
  if (!(root instanceof RootedNode)) {
    throw new TreeError("A rooted tree requires a RootedNode root.");
  }

  let nodes = 0;
  let leaves = 0;
  let height = 0;
  const seen = new Set();
  const stack = [[root, 0]];

  while (stack.length) {
    const [node, depth] = stack.pop();

    if (seen.has(node)) {
      throw new TreeError("Repeated node detected in rooted hierarchy.");
    }
    seen.add(node);
    nodes++;
    height = Math.max(height, depth);

    if (node.children.length === 0) leaves++;

    for (const child of node.children) {
      if (child.parent !== node) {
        throw new TreeError("Parent and child references disagree.");
      }
      stack.push([child, depth + 1]);
    }
  }

  return { nodes, edges: nodes - 1, leaves, height };
}

function rootedPreorder(root) {
  const result = [];
  const stack = [root];

  while (stack.length) {
    const node = stack.pop();
    result.push(node.value);

    // Reverse insertion order so the original child order is preserved.
    for (let i = node.children.length - 1; i >= 0; i--) {
      stack.push(node.children[i]);
    }
  }

  return result;
}

class BinaryNode {
  constructor(key, left = null, right = null) {
    if (!Number.isFinite(key)) {
      throw new TreeError("Binary-tree keys must be finite numbers.");
    }
    this.key = key;
    this.left = left;
    this.right = right;
  }
}

function inorder(root) {
  const result = [];
  const stack = [];
  let current = root;

  // An explicit stack avoids JavaScript call-stack overflow on a skewed tree.
  while (current !== null || stack.length) {
    while (current !== null) {
      stack.push(current);
      current = current.left;
    }

    current = stack.pop();
    result.push(current.key);
    current = current.right;
  }

  return result;
}

function levelOrder(root) {
  if (root === null) return [];

  const result = [];
  const queue = [root];
  let head = 0;

  // Advancing a head index avoids repeated Array.shift() reindexing.
  while (head < queue.length) {
    const node = queue[head++];
    result.push(node.key);

    if (node.left !== null) queue.push(node.left);
    if (node.right !== null) queue.push(node.right);
  }

  return result;
}

function binaryProperties(root) {
  if (root === null) {
    return {
      nodes: 0,
      height: -1,
      leaves: 0,
      full: true,
      complete: true,
      perfect: true,
      balanced: true
    };
  }

  let nodes = 0;
  let leaves = 0;
  let full = true;
  let complete = true;
  let gapSeen = false;
  let balanced = true;
  const heights = new Map();
  const traversal = [[root, false]];

  // Postorder evaluation computes child heights before parent heights.
  while (traversal.length) {
    const [node, expanded] = traversal.pop();

    if (!expanded) {
      traversal.push([node, true]);
      if (node.right !== null) traversal.push([node.right, false]);
      if (node.left !== null) traversal.push([node.left, false]);
      continue;
    }

    nodes++;
    const leftHeight = node.left === null ? -1 : heights.get(node.left);
    const rightHeight = node.right === null ? -1 : heights.get(node.right);

    heights.set(node, 1 + Math.max(leftHeight, rightHeight));
    if (Math.abs(leftHeight - rightHeight) > 1) balanced = false;

    if (node.left === null && node.right === null) leaves++;
    if ((node.left === null) !== (node.right === null)) full = false;
  }

  // Completeness is a level-order property: no child may follow a missing slot.
  const queue = [root];
  let head = 0;

  while (head < queue.length) {
    const node = queue[head++];

    for (const child of [node.left, node.right]) {
      if (child === null) {
        gapSeen = true;
      } else {
        if (gapSeen) complete = false;
        queue.push(child);
      }
    }
  }

  const height = heights.get(root);
  const perfect = nodes === 2 ** (height + 1) - 1;

  return { nodes, height, leaves, full, complete, perfect, balanced };
}

class BinarySearchTree {
  constructor() {
    this.root = null;
    this.size = 0;
  }

  insert(key) {
    if (!Number.isFinite(key)) {
      throw new TreeError("BST keys must be finite numbers.");
    }

    if (this.root === null) {
      this.root = new BinaryNode(key);
      this.size++;
      return true;
    }

    let current = this.root;

    while (true) {
      if (key === current.key) return false;

      const side = key < current.key ? "left" : "right";
      if (current[side] === null) {
        current[side] = new BinaryNode(key);
        this.size++;
        return true;
      }
      current = current[side];
    }
  }

  has(key) {
    let current = this.root;

    while (current !== null) {
      if (key === current.key) return true;
      current = key < current.key ? current.left : current.right;
    }

    return false;
  }

  delete(key) {
    let parent = null;
    let current = this.root;

    while (current !== null && current.key !== key) {
      parent = current;
      current = key < current.key ? current.left : current.right;
    }

    if (current === null) return false;

    if (current.left !== null && current.right !== null) {
      let successorParent = current;
      let successor = current.right;

      while (successor.left !== null) {
        successorParent = successor;
        successor = successor.left;
      }

      current.key = successor.key;
      parent = successorParent;
      current = successor;
    }

    const replacement = current.left !== null ? current.left : current.right;

    if (parent === null) {
      this.root = replacement;
    } else if (parent.left === current) {
      parent.left = replacement;
    } else {
      parent.right = replacement;
    }

    this.size--;
    return true;
  }
}

class WeightedGraph {
  constructor(vertices) {
    if (!Array.isArray(vertices) || vertices.length === 0) {
      throw new TreeError("A graph needs at least one vertex.");
    }
    if (new Set(vertices).size !== vertices.length ||
        vertices.some(v => typeof v !== "string" || v.length === 0)) {
      throw new TreeError("Vertex labels must be unique nonempty strings.");
    }

    this.vertices = [...vertices];
    this.adjacency = new Map(vertices.map(v => [v, new Map()]));
    this.edges = [];
  }

  addEdge(first, second, weight) {
    if (!this.adjacency.has(first) || !this.adjacency.has(second)) {
      throw new TreeError("Edge endpoint is not in the graph.");
    }
    if (first === second) throw new TreeError("Self-loops are forbidden.");
    if (!Number.isFinite(weight)) throw new TreeError("Weight must be finite.");
    if (this.adjacency.get(first).has(second)) {
      throw new TreeError("Duplicate edges are not supported.");
    }

    this.adjacency.get(first).set(second, weight);
    this.adjacency.get(second).set(first, weight);
    this.edges.push({ first, second, weight });
  }

  hasCycle() {
    const visited = new Set();

    for (const start of this.vertices) {
      if (visited.has(start)) continue;

      const stack = [[start, null]];

      while (stack.length) {
        const [vertex, parent] = stack.pop();
        if (visited.has(vertex)) continue;
        visited.add(vertex);

        for (const neighbor of this.adjacency.get(vertex).keys()) {
          if (neighbor === parent) continue;
          if (visited.has(neighbor)) return true;
          stack.push([neighbor, vertex]);
        }
      }
    }

    return false;
  }

  isConnected() {
    const visited = new Set();
    const stack = [this.vertices[0]];

    while (stack.length) {
      const vertex = stack.pop();
      if (visited.has(vertex)) continue;
      visited.add(vertex);

      for (const neighbor of this.adjacency.get(vertex).keys()) {
        if (!visited.has(neighbor)) stack.push(neighbor);
      }
    }

    return visited.size === this.vertices.length;
  }

  isTree() {
    return this.edges.length === this.vertices.length - 1 &&
      this.isConnected();
  }

  kruskal() {
    const parent = new Map(this.vertices.map(v => [v, v]));
    const rank = new Map(this.vertices.map(v => [v, 0]));

    function find(vertex) {
      if (parent.get(vertex) !== vertex) {
        parent.set(vertex, find(parent.get(vertex)));
      }
      return parent.get(vertex);
    }

    function union(a, b) {
      let rootA = find(a);
      let rootB = find(b);
      if (rootA === rootB) return false;

      if (rank.get(rootA) < rank.get(rootB)) {
        [rootA, rootB] = [rootB, rootA];
      }

      parent.set(rootB, rootA);
      if (rank.get(rootA) === rank.get(rootB)) {
        rank.set(rootA, rank.get(rootA) + 1);
      }
      return true;
    }

    const chosen = [];
    let totalWeight = 0;

    for (const edge of [...this.edges].sort(
      (a, b) => a.weight - b.weight ||
        a.first.localeCompare(b.first) ||
        a.second.localeCompare(b.second)
    )) {
      if (union(edge.first, edge.second)) {
        chosen.push(edge);
        totalWeight += edge.weight;
      }
    }

    if (chosen.length !== this.vertices.length - 1) {
      throw new TreeError("No spanning tree exists for a disconnected graph.");
    }

    return { edges: chosen, totalWeight };
  }
}

function buildDeploymentHierarchy() {
  const root = new RootedNode("Production");
  const regionA = new RootedNode("Region-A");
  const regionB = new RootedNode("Region-B");

  root.addChild(regionA);
  root.addChild(regionB);
  regionA.addChild(new RootedNode("API-Service"));
  regionA.addChild(new RootedNode("Worker-Service"));
  regionB.addChild(new RootedNode("Database-Service"));

  return root;
}

function runTests() {
  const bst = new BinarySearchTree();
  for (const key of [8, 4, 12, 2, 6, 10, 14]) {
    if (!bst.insert(key)) throw new Error("Unexpected duplicate key.");
  }

  console.assert(inorder(bst.root).join(",") === "2,4,6,8,10,12,14");
  console.assert(bst.delete(4));
  console.assert(!bst.has(4));
  console.assert(binaryProperties(null).height === -1);

  const graph = new WeightedGraph(["A", "B", "C"]);
  graph.addEdge("A", "B", 3);
  graph.addEdge("B", "C", 1);
  graph.addEdge("A", "C", 5);

  const mst = graph.kruskal();
  console.assert(mst.edges.length === 2);
  console.assert(mst.totalWeight === 4);

  console.log("JavaScript tree tests passed.");
}

function main() {
  console.log("ROOTED TREE");
  const hierarchy = buildDeploymentHierarchy();
  console.log("Preorder:", rootedPreorder(hierarchy));
  console.log("Metrics:", rootedMetrics(hierarchy));

  console.log("\nBINARY TREE");
  const binaryRoot = new BinaryNode(
    20,
    new BinaryNode(10, new BinaryNode(5), new BinaryNode(15)),
    new BinaryNode(30, new BinaryNode(25), new BinaryNode(35))
  );
  console.log("Inorder:", inorder(binaryRoot));
  console.log("Level order:", levelOrder(binaryRoot));
  console.log("Properties:", binaryProperties(binaryRoot));

  console.log("\nSPANNING TREE");
  const network = new WeightedGraph(["api", "cache", "database", "worker"]);
  network.addEdge("api", "cache", 3);
  network.addEdge("api", "database", 8);
  network.addEdge("cache", "database", 2);
  network.addEdge("cache", "worker", 4);
  network.addEdge("database", "worker", 5);

  console.log("Original graph contains cycle:", network.hasCycle());
  console.log("Original graph is a tree:", network.isTree());
  console.log("Minimum spanning tree:", network.kruskal());

  runTests();
}

main();
