"use strict";

/*
 * Equivalence Relations, Equivalence Classes, Partitions, and Quotient
 * Structures.
 *
 * This file uses JavaScript-specific features to model the mathematics:
 * - Map and Set for class construction
 * - classes for relation and quotient abstractions
 * - generators for lazy class traversal
 * - events for an incremental partition workflow
 * - immutable-style quotient values
 * - asynchronous validation to model a repository/service boundary
 *
 * Run with:
 *   node equivalence_relations.js
 */

class EquivalenceRelation {
    constructor(elements, relation, name = "R") {
        this.elements = [...new Set(elements)];
        this.relation = relation;
        this.name = name;
    }

    isReflexive() {
        return this.elements.every((x) => this.relation(x, x));
    }

    isSymmetric() {
        for (const x of this.elements) {
            for (const y of this.elements) {
                if (this.relation(x, y) && !this.relation(y, x)) {
                    return false;
                }
            }
        }
        return true;
    }

    isTransitive() {
        for (const x of this.elements) {
            for (const y of this.elements) {
                if (!this.relation(x, y)) {
                    continue;
                }

                for (const z of this.elements) {
                    if (this.relation(y, z) && !this.relation(x, z)) {
                        return false;
                    }
                }
            }
        }
        return true;
    }

    isEquivalence() {
        return (
            this.isReflexive() &&
            this.isSymmetric() &&
            this.isTransitive()
        );
    }

    equivalenceClass(element) {
        if (!this.elements.includes(element)) {
            throw new Error(`Element ${String(element)} is outside the domain.`);
        }

        return new Set(
            this.elements.filter((other) => this.relation(element, other))
        );
    }

    classes() {
        if (!this.isEquivalence()) {
            throw new Error(
                `${this.name} is not an equivalence relation; no valid partition exists.`
            );
        }

        const classes = [];
        const assigned = new Set();

        for (const element of this.elements) {
            if (assigned.has(element)) {
                continue;
            }

            const classSet = this.equivalenceClass(element);
            classes.push(classSet);

            for (const member of classSet) {
                assigned.add(member);
            }
        }

        return classes;
    }
}

function relationFromKey(elements, keyFunction, name = "R") {
    return new EquivalenceRelation(
        elements,
        (left, right) => keyFunction(left) === keyFunction(right),
        name
    );
}

function setToArray(set) {
    return [...set];
}

function formatClass(classSet) {
    return `{ ${setToArray(classSet).join(", ")} }`;
}

function printRelationReport(relation) {
    console.log(`\n=== ${relation.name} ===`);
    console.log(`Domain: ${JSON.stringify(relation.elements)}`);
    console.log(`Reflexive: ${relation.isReflexive()}`);
    console.log(`Symmetric: ${relation.isSymmetric()}`);
    console.log(`Transitive: ${relation.isTransitive()}`);
    console.log(`Equivalence relation: ${relation.isEquivalence()}`);

    if (relation.isEquivalence()) {
        console.log("Equivalence classes:");
        for (const classSet of relation.classes()) {
            console.log(`  ${formatClass(classSet)}`);
        }
    }
}

function demonstrateCongruence() {
    const domain = Array.from({ length: 17 }, (_, index) => index - 8);
    const modulus = 4;

    const congruence = new EquivalenceRelation(
        domain,
        (x, y) => (x - y) % modulus === 0,
        `congruence modulo ${modulus}`
    );

    printRelationReport(congruence);

    console.log("\nSpecific classes:");
    for (const representative of [-7, -2, 0, 1, 6]) {
        console.log(
            `[${representative}] = ${formatClass(
                congruence.equivalenceClass(representative)
            )}`
        );
    }
}

function demonstratePartitionConstruction() {
    const universe = new Set(
        Array.from({ length: 12 }, (_, index) => index + 1)
    );

    const partition = [
        new Set([1, 4, 7, 10]),
        new Set([2, 5, 8, 11]),
        new Set([3, 6, 9, 12])
    ];

    const validation = validatePartition(universe, partition);

    console.log("\n=== Partition validation ===");
    console.log(validation);

    if (!validation.valid) {
        return;
    }

    const sameBlock = (x, y) =>
        partition.some((block) => block.has(x) && block.has(y));

    const inducedRelation = new EquivalenceRelation(
        [...universe],
        sameBlock,
        "relation induced by a partition"
    );

    console.log(
        `Induced relation is equivalence: ${inducedRelation.isEquivalence()}`
    );

    for (const [x, y] of [
        [1, 7],
        [1, 2],
        [5, 11],
        [9, 12]
    ]) {
        console.log(`${x} R ${y}: ${inducedRelation.relation(x, y)}`);
    }
}

function validatePartition(universe, blocks) {
    const normalized = blocks.map((block) => new Set(block));

    if (normalized.some((block) => block.size === 0)) {
        return {
            valid: false,
            reason: "A partition cannot contain an empty block."
        };
    }

    for (const block of normalized) {
        for (const element of block) {
            if (!universe.has(element)) {
                return {
                    valid: false,
                    reason: `Element ${String(element)} is outside the universe.`
                };
            }
        }
    }

    for (let i = 0; i < normalized.length; i += 1) {
        for (let j = i + 1; j < normalized.length; j += 1) {
            for (const element of normalized[i]) {
                if (normalized[j].has(element)) {
                    return {
                        valid: false,
                        reason: "Distinct blocks must be pairwise disjoint."
                    };
                }
            }
        }
    }

    const union = new Set();
    for (const block of normalized) {
        for (const element of block) {
            union.add(element);
        }
    }

    if (
        union.size !== universe.size ||
        [...universe].some((element) => !union.has(element))
    ) {
        return {
            valid: false,
            reason: "The blocks must cover the entire universe."
        };
    }

    return {
        valid: true,
        reason: "The blocks form a partition."
    };
}

class QuotientSet {
    constructor(relation) {
        if (!relation.isEquivalence()) {
            throw new Error("A quotient set requires an equivalence relation.");
        }

        this.relation = relation;
        this.blocks = relation.classes();
    }

    size() {
        return this.blocks.length;
    }

    *elements() {
        for (const block of this.blocks) {
            yield new Set(block);
        }
    }

    classOf(element) {
        return this.relation.equivalenceClass(element);
    }

    hasClassContaining(element) {
        return this.blocks.some((block) => block.has(element));
    }
}

function demonstrateQuotientSet() {
    const products = [
        { id: 1, name: "Laptop", category: "electronics" },
        { id: 2, name: "Monitor", category: "electronics" },
        { id: 3, name: "Desk", category: "furniture" },
        { id: 4, name: "Chair", category: "furniture" },
        { id: 5, name: "Python Book", category: "books" },
        { id: 6, name: "Database Book", category: "books" }
    ];

    const productById = new Map(
        products.map((product) => [product.id, product])
    );

    const relation = relationFromKey(
        products.map((product) => product.id),
        (id) => productById.get(id).category,
        "same product category"
    );

    const quotient = new QuotientSet(relation);

    console.log("\n=== Quotient of products by category ===");
    console.log(`Original set size: ${products.length}`);
    console.log(`Quotient set size: ${quotient.size()}`);

    for (const classSet of quotient.elements()) {
        const members = [...classSet].map(
            (id) => productById.get(id).name
        );
        const category = productById.get([...classSet][0]).category;

        console.log(`${category}: ${JSON.stringify(members)}`);
    }
}

class ResidueClass {
    constructor(value, modulus) {
        if (!Number.isInteger(modulus) || modulus <= 0) {
            throw new RangeError("The modulus must be a positive integer.");
        }

        this.modulus = modulus;
        this.value = ((value % modulus) + modulus) % modulus;

        Object.freeze(this);
    }

    add(other) {
        this.assertCompatible(other);
        return new ResidueClass(
            this.value + other.value,
            this.modulus
        );
    }

    multiply(other) {
        this.assertCompatible(other);
        return new ResidueClass(
            this.value * other.value,
            this.modulus
        );
    }

    equals(other) {
        return (
            other instanceof ResidueClass &&
            other.modulus === this.modulus &&
            other.value === this.value
        );
    }

    toString() {
        return `[${this.value}]_${this.modulus}`;
    }

    assertCompatible(other) {
        if (
            !(other instanceof ResidueClass) ||
            other.modulus !== this.modulus
        ) {
            throw new TypeError(
                "Residue classes must belong to the same quotient structure."
            );
        }
    }
}

function demonstrateWellDefinedOperations() {
    console.log("\n=== Well-defined operations in Z/5Z ===");

    const a = new ResidueClass(2, 5);
    const aPrime = new ResidueClass(7, 5);
    const b = new ResidueClass(3, 5);
    const bPrime = new ResidueClass(13, 5);

    console.log(`${a} equals ${aPrime}: ${a.equals(aPrime)}`);
    console.log(`${b} equals ${bPrime}: ${b.equals(bPrime)}`);

    const firstSum = a.add(b);
    const secondSum = aPrime.add(bPrime);

    const firstProduct = a.multiply(b);
    const secondProduct = aPrime.multiply(bPrime);

    console.log(`${a} + ${b} = ${firstSum}`);
    console.log(`${aPrime} + ${bPrime} = ${secondSum}`);
    console.log(`Addition is representative-independent: ${firstSum.equals(secondSum)}`);

    console.log(`${a} * ${b} = ${firstProduct}`);
    console.log(`${aPrime} * ${bPrime} = ${secondProduct}`);
    console.log(
        `Multiplication is representative-independent: ${firstProduct.equals(secondProduct)}`
    );
}

class IncrementalPartition {
    constructor(elements) {
        this.parent = new Map();
        this.rank = new Map();

        for (const element of elements) {
            this.parent.set(element, element);
            this.rank.set(element, 0);
        }
    }

    find(element) {
        if (!this.parent.has(element)) {
            throw new Error(`Unknown element: ${String(element)}`);
        }

        const parent = this.parent.get(element);

        if (parent !== element) {
            this.parent.set(element, this.find(parent));
        }

        return this.parent.get(element);
    }

    union(left, right) {
        const leftRoot = this.find(left);
        const rightRoot = this.find(right);

        if (leftRoot === rightRoot) {
            return false;
        }

        const leftRank = this.rank.get(leftRoot);
        const rightRank = this.rank.get(rightRoot);

        if (leftRank < rightRank) {
            this.parent.set(leftRoot, rightRoot);
        } else if (leftRank > rightRank) {
            this.parent.set(rightRoot, leftRoot);
        } else {
            this.parent.set(rightRoot, leftRoot);
            this.rank.set(leftRoot, leftRank + 1);
        }

        return true;
    }

    classes() {
        const groups = new Map();

        for (const element of this.parent.keys()) {
            const root = this.find(element);

            if (!groups.has(root)) {
                groups.set(root, new Set());
            }

            groups.get(root).add(element);
        }

        return groups;
    }
}

function demonstrateIncrementalPartition() {
    console.log("\n=== Incremental equivalence classes with union-find ===");

    const partition = new IncrementalPartition(
        Array.from({ length: 10 }, (_, index) => index + 1)
    );

    const relationships = [
        [1, 4],
        [4, 7],
        [2, 5],
        [5, 8],
        [3, 6],
        [6, 9],
        [9, 10]
    ];

    for (const [left, right] of relationships) {
        partition.union(left, right);
    }

    for (const [representative, members] of partition.classes()) {
        console.log(
            `Representative ${representative}: ${formatClass(members)}`
        );
    }

    console.log(
        `1 and 7 equivalent: ${partition.find(1) === partition.find(7)}`
    );
    console.log(
        `2 and 6 equivalent: ${partition.find(2) === partition.find(6)}`
    );
}

class RelationEventStream {
    constructor() {
        this.listeners = new Map();
    }

    on(eventName, listener) {
        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, new Set());
        }

        this.listeners.get(eventName).add(listener);

        return () => {
            this.listeners.get(eventName)?.delete(listener);
        };
    }

    emit(eventName, payload) {
        const listeners = this.listeners.get(eventName) ?? [];

        for (const listener of listeners) {
            listener(payload);
        }
    }
}

function demonstrateEventDrivenPartition() {
    console.log("\n=== Event-driven equivalence updates ===");

    const events = new RelationEventStream();
    const partition = new IncrementalPartition(["A", "B", "C", "D"]);

    events.on("equivalent", ({ left, right }) => {
        partition.union(left, right);
        console.log(
            `Merged ${left} and ${right}; class = ${formatClass(
                [...partition.classes().values()].find(
                    (members) =>
                        members.has(left) && members.has(right)
                )
            )}`
        );
    });

    events.emit("equivalent", { left: "A", right: "B" });
    events.emit("equivalent", { left: "C", right: "D" });
    events.emit("equivalent", { left: "B", right: "C" });

    console.log("Final partition:");
    for (const members of partition.classes().values()) {
        console.log(`  ${formatClass(members)}`);
    }
}

async function asynchronousPartitionValidation() {
    /*
     * The Promise represents a boundary where partition data could come from
     * a database, API, or user interface. Mathematical validation still
     * occurs before the structure is accepted.
     */
    const universe = new Set(["red", "green", "blue", "yellow"]);

    const proposedPartition = [
        new Set(["red", "green"]),
        new Set(["blue"]),
        new Set(["yellow"])
    ];

    const result = await Promise.resolve(
        validatePartition(universe, proposedPartition)
    );

    console.log("\n=== Asynchronous validation boundary ===");
    console.log(result);

    if (!result.valid) {
        throw new Error(result.reason);
    }
}

function demonstrateNonEquivalence() {
    console.log("\n=== Relations that are not equivalence relations ===");

    const domain = [1, 2, 3];

    const lessThan = new EquivalenceRelation(
        domain,
        (x, y) => x < y,
        "strict less-than"
    );

    const differentParity = new EquivalenceRelation(
        domain,
        (x, y) => x % 2 !== y % 2,
        "different parity"
    );

    printRelationReport(lessThan);
    printRelationReport(differentParity);
}

async function main() {
    console.log(
        "EQUIVALENCE RELATIONS, EQUIVALENCE CLASSES, PARTITIONS, AND QUOTIENT STRUCTURES"
    );
    console.log("=".repeat(82));

    demonstrateCongruence();
    demonstratePartitionConstruction();
    demonstrateQuotientSet();
    demonstrateWellDefinedOperations();
    demonstrateIncrementalPartition();
    demonstrateEventDrivenPartition();
    demonstrateNonEquivalence();
    await asynchronousPartitionValidation();

    console.log("\n=== Verification ===");

    const moduloThree = new EquivalenceRelation(
        Array.from({ length: 10 }, (_, index) => index),
        (x, y) => (x - y) % 3 === 0,
        "modulo 3"
    );

    if (!moduloThree.isEquivalence()) {
        throw new Error("Modulo-3 relation failed equivalence verification.");
    }

    if (moduloThree.classes().length !== 3) {
        throw new Error("Modulo-3 quotient should contain three classes.");
    }

    const quotient = new QuotientSet(moduloThree);

    if (!quotient.hasClassContaining(8)) {
        throw new Error("Quotient lost the class containing 8.");
    }

    console.log("All equivalence-relation checks passed.");
}

main().catch((error) => {
    console.error(`Execution failed: ${error.message}`);
    process.exitCode = 1;
});
