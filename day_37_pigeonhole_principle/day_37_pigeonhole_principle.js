/**
 * Pigeonhole Principle in Computing
 *
 * This Node.js program models the basic and generalized pigeonhole
 * principles through hash buckets, finite identifiers, duplicate detection,
 * load distribution, event-driven processing, and probabilistic experiments.
 *
 * The program uses JavaScript-specific mechanisms such as classes,
 * Map/Set, generators, Promises, async functions, and EventEmitter.
 */

"use strict";

const crypto = require("crypto");
const { EventEmitter } = require("events");

function minimumGuaranteedOccupancy(objects, containers) {
    if (!Number.isInteger(objects) || objects < 0) {
        throw new RangeError("objects must be a non-negative integer");
    }

    if (!Number.isInteger(containers) || containers <= 0) {
        throw new RangeError("containers must be a positive integer");
    }

    return objects === 0 ? 0 : Math.ceil(objects / containers);
}

function objectsRequiredForTarget(containers, targetOccupancy) {
    if (!Number.isInteger(containers) || containers <= 0) {
        throw new RangeError("containers must be positive");
    }

    if (!Number.isInteger(targetOccupancy) || targetOccupancy <= 0) {
        throw new RangeError("targetOccupancy must be positive");
    }

    return containers * (targetOccupancy - 1) + 1;
}

function assertBasicPrinciple(objects, containers) {
    if (objects > containers) {
        return {
            guaranteedCollision: true,
            reason: `${objects} objects exceed ${containers} containers`
        };
    }

    return {
        guaranteedCollision: false,
        reason: "A collision may occur, but it is not forced by counting alone"
    };
}

function countBuckets(assignments, bucketCount) {
    if (!Number.isInteger(bucketCount) || bucketCount <= 0) {
        throw new RangeError("bucketCount must be positive");
    }

    const counts = new Array(bucketCount).fill(0);

    for (const bucket of assignments) {
        if (!Number.isInteger(bucket) || bucket < 0 || bucket >= bucketCount) {
            throw new RangeError(`Invalid bucket: ${bucket}`);
        }

        counts[bucket] += 1;
    }

    return counts;
}

function hashToBucket(value, bucketCount) {
    if (bucketCount <= 0) {
        throw new RangeError("bucketCount must be positive");
    }

    const digest = crypto
        .createHash("sha256")
        .update(value, "utf8")
        .digest();

    const firstEightBytes = digest.readBigUInt64BE(0);

    return Number(firstEightBytes % BigInt(bucketCount));
}

function demonstrateHashCollisions() {
    console.log("\n=== Hash Bucket Collision Model ===");

    const keys = [
        "employee:1001",
        "employee:1002",
        "employee:1003",
        "employee:1004",
        "employee:1005",
        "employee:1006",
        "employee:1007",
        "employee:1008",
        "employee:1009",
        "employee:1010"
    ];

    const bucketCount = 4;

    const assignments = keys.map(key => hashToBucket(key, bucketCount));
    const counts = countBuckets(assignments, bucketCount);

    keys.forEach((key, index) => {
        console.log(`${key} -> bucket ${assignments[index]}`);
    });

    console.log("Bucket counts:", counts);

    console.log(
        "Guaranteed largest occupancy:",
        minimumGuaranteedOccupancy(keys.length, bucketCount)
    );
}

function demonstrateFiniteIdentifiers() {
    console.log("\n=== Finite Identifier Space ===");

    const alphabetSize = 10;
    const identifierLength = 3;
    const identifierCount = alphabetSize ** identifierLength;

    console.log(`Available three-digit identifiers: ${identifierCount}`);

    const requests = identifierCount + 1;

    console.log(
        `Requests required to force a duplicate: ${requests}`
    );
}

class BucketStore {
    constructor(bucketCount) {
        if (!Number.isInteger(bucketCount) || bucketCount <= 0) {
            throw new RangeError("bucketCount must be positive");
        }

        this.bucketCount = bucketCount;
        this.buckets = Array.from(
            { length: bucketCount },
            () => new Map()
        );
    }

    put(key, value) {
        const bucket = hashToBucket(key, this.bucketCount);

        this.buckets[bucket].set(key, value);

        return bucket;
    }

    get(key) {
        const bucket = hashToBucket(key, this.bucketCount);

        return this.buckets[bucket].get(key);
    }

    occupancy() {
        return this.buckets.map(bucket => bucket.size);
    }

    collisionBuckets() {
        return this.occupancy()
            .map((size, index) => ({ index, size }))
            .filter(entry => entry.size > 1);
    }
}

function demonstrateBucketStore() {
    console.log("\n=== Hash Table Storage Model ===");

    const store = new BucketStore(5);

    const records = [
        ["customer:1", "Asha"],
        ["customer:2", "Rahul"],
        ["customer:3", "Meera"],
        ["customer:4", "Kabir"],
        ["customer:5", "Neha"],
        ["customer:6", "Vikram"],
        ["customer:7", "Isha"],
        ["customer:8", "Arjun"]
    ];

    for (const [key, value] of records) {
        store.put(key, value);
    }

    console.log("Occupancy:", store.occupancy());
    console.log("Collision buckets:", store.collisionBuckets());
    console.log("Lookup customer:4:", store.get("customer:4"));
}

function findDuplicate(values) {
    const seen = new Set();

    for (let index = 0; index < values.length; index += 1) {
        const value = values[index];

        if (seen.has(value)) {
            return {
                value,
                index
            };
        }

        seen.add(value);
    }

    return null;
}

function demonstrateDuplicateDetection() {
    console.log("\n=== Duplicate Detection ===");

    const identifiers = [
        "REQ-100",
        "REQ-101",
        "REQ-102",
        "REQ-103",
        "REQ-101"
    ];

    const duplicate = findDuplicate(identifiers);

    if (duplicate) {
        console.log(
            `Duplicate ${duplicate.value} detected at index ${duplicate.index}`
        );
    }
}

function generateBalancedDistribution(objects, containers) {
    if (objects < 0 || containers <= 0) {
        throw new RangeError("Invalid distribution parameters");
    }

    const counts = new Array(containers).fill(0);

    for (let index = 0; index < objects; index += 1) {
        counts[index % containers] += 1;
    }

    return counts;
}

function demonstrateGeneralizedPrinciple() {
    console.log("\n=== Generalized Pigeonhole Principle ===");

    const objects = 23;
    const containers = 5;

    const distribution = generateBalancedDistribution(
        objects,
        containers
    );

    console.log("Most balanced distribution:", distribution);

    console.log(
        "Forced occupancy:",
        minimumGuaranteedOccupancy(objects, containers)
    );

    console.log(
        "Objects needed for a bucket of size 7:",
        objectsRequiredForTarget(containers, 7)
    );
}

class RequestRouter extends EventEmitter {
    constructor(serverCount) {
        super();

        if (!Number.isInteger(serverCount) || serverCount <= 0) {
            throw new RangeError("serverCount must be positive");
        }

        this.serverCount = serverCount;
        this.loads = new Array(serverCount).fill(0);

        this.on("requestAssigned", event => {
            console.log(
                `Request ${event.requestId} assigned to server ${event.server}`
            );
        });
    }

    route(requestId) {
        const server = this.loads.indexOf(Math.min(...this.loads));

        this.loads[server] += 1;

        this.emit("requestAssigned", {
            requestId,
            server,
            currentLoad: this.loads[server]
        });

        return server;
    }
}

function demonstrateEventDrivenLoadBalancing() {
    console.log("\n=== Event-Driven Load Distribution ===");

    const router = new RequestRouter(3);

    for (let request = 1; request <= 10; request += 1) {
        router.route(`R-${request}`);
    }

    console.log("Final server loads:", router.loads);

    console.log(
        "Pigeonhole lower bound:",
        minimumGuaranteedOccupancy(10, 3)
    );
}

function categoricalSignature(department, region, priority) {
    const departments = new Set([
        "finance",
        "operations",
        "technology"
    ]);

    const regions = new Set([
        "north",
        "south",
        "east",
        "west"
    ]);

    const priorities = new Set([
        "low",
        "medium",
        "high"
    ]);

    if (!departments.has(department)) {
        throw new Error("Unknown department");
    }

    if (!regions.has(region)) {
        throw new Error("Unknown region");
    }

    if (!priorities.has(priority)) {
        throw new Error("Unknown priority");
    }

    return `${department}|${region}|${priority}`;
}

function demonstrateFiniteCategoricalSpace() {
    console.log("\n=== Finite Categorical Signature Space ===");

    const signatureCount = 3 * 4 * 3;
    const recordsNeeded = signatureCount + 1;

    console.log("Possible signatures:", signatureCount);
    console.log("Records needed for a guaranteed duplicate:", recordsNeeded);

    console.log(
        "Valid signature:",
        categoricalSignature("technology", "north", "high")
    );
}

async function processBatchAsync(items, bucketCount) {
    const assignments = [];

    for (const item of items) {
        // Promise.resolve creates an asynchronous boundary without requiring
        // an external dependency or a network connection.
        await Promise.resolve();

        assignments.push({
            item,
            bucket: hashToBucket(item, bucketCount)
        });
    }

    return assignments;
}

async function demonstrateAsyncProcessing() {
    console.log("\n=== Asynchronous Batch Processing ===");

    const items = Array.from(
        { length: 12 },
        (_, index) => `job-${index + 1}`
    );

    const assignments = await processBatchAsync(items, 4);
    const counts = countBuckets(
        assignments.map(entry => entry.bucket),
        4
    );

    console.log("Assignments:", assignments);
    console.log("Occupancy:", counts);
    console.log(
        "Guaranteed occupancy:",
        minimumGuaranteedOccupancy(items.length, 4)
    );
}

function randomCollisionExperiment(
    objects,
    containers,
    trials,
    seed = 123456789
) {
    if (
        !Number.isInteger(objects) ||
        objects < 0 ||
        !Number.isInteger(containers) ||
        containers <= 0 ||
        !Number.isInteger(trials) ||
        trials <= 0
    ) {
        throw new RangeError("Invalid experiment parameters");
    }

    let state = seed >>> 0;

    function randomInteger(maxExclusive) {
        state = (1664525 * state + 1013904223) >>> 0;

        return Math.floor(
            (state / 0x100000000) * maxExclusive
        );
    }

    let collisionTrials = 0;

    for (let trial = 0; trial < trials; trial += 1) {
        const seen = new Set();

        for (let object = 0; object < objects; object += 1) {
            seen.add(randomInteger(containers));
        }

        if (seen.size < objects) {
            collisionTrials += 1;
        }
    }

    return collisionTrials / trials;
}

function demonstrateProbabilityVsGuarantee() {
    console.log("\n=== Probability Versus Deterministic Guarantee ===");

    const cases = [
        [10, 365],
        [23, 365],
        [366, 365]
    ];

    for (const [objects, containers] of cases) {
        const frequency = randomCollisionExperiment(
            objects,
            containers,
            3000
        );

        console.log(
            `${objects} objects / ${containers} containers -> ` +
            `observed collision frequency ${frequency.toFixed(3)}`
        );
    }

    console.log(
        "At 366 objects and 365 containers, the collision is mathematically "
        + "guaranteed, regardless of the random experiment."
    );
}

function demonstrateMemoryStateSpace() {
    console.log("\n=== Bit Pattern State Space ===");

    const bitWidth = 8;
    const states = 2 ** bitWidth;

    console.log(
        `${bitWidth}-bit representation has ${states} distinct patterns.`
    );

    const requestedStates = 300;

    let bits = 0;
    let capacity = 1;

    while (capacity < requestedStates) {
        capacity *= 2;
        bits += 1;
    }

    console.log(
        `${requestedStates} states require at least ${bits} bits.`
    );

    console.log(
        "A representation with fewer possible patterns than required "
        + "cannot assign a unique pattern to every logical state."
    );
}

function demonstrateModularArithmetic() {
    console.log("\n=== Modular Arithmetic ===");

    const modulus = 7;
    const values = Array.from({ length: 20 }, (_, index) => index);

    const groups = new Map();

    for (const value of values) {
        const residue = value % modulus;

        if (!groups.has(residue)) {
            groups.set(residue, []);
        }

        groups.get(residue).push(value);
    }

    for (const [residue, group] of groups.entries()) {
        console.log(`Residue ${residue}:`, group);
    }

    console.log(
        "Guaranteed repeated residue count:",
        minimumGuaranteedOccupancy(values.length, modulus)
    );
}

function* generateIdentifiers(alphabet, length) {
    if (length < 0) {
        throw new RangeError("length cannot be negative");
    }

    if (length === 0) {
        yield "";
        return;
    }

    for (const character of alphabet) {
        for (const suffix of generateIdentifiers(alphabet, length - 1)) {
            yield character + suffix;
        }
    }
}

function demonstrateFiniteIdentifierGenerator() {
    console.log("\n=== Finite Identifier Generator ===");

    const alphabet = "012";
    const length = 3;

    const identifiers = [...generateIdentifiers(alphabet, length)];

    console.log("Identifier space size:", identifiers.length);
    console.log("Identifiers:", identifiers.join(", "));

    console.log(
        "One more assigned object than the identifier space forces "
        + "a duplicate identifier."
    );
}

function main() {
    console.log("PIGEONHOLE PRINCIPLE: COMPUTING APPLICATIONS");

    const basic = assertBasicPrinciple(13, 12);

    console.log("\n=== Basic Principle ===");
    console.log(basic);

    demonstrateHashCollisions();
    demonstrateFiniteIdentifiers();
    demonstrateBucketStore();
    demonstrateGeneralizedPrinciple();
    demonstrateDuplicateDetection();
    demonstrateEventDrivenLoadBalancing();
    demonstrateFiniteCategoricalSpace();
    demonstrateMemoryStateSpace();
    demonstrateModularArithmetic();
    demonstrateFiniteIdentifierGenerator();

    demonstrateProbabilityVsGuarantee();

    // Async work is deliberately awaited so that all output is deterministic
    // in ordering and the Node.js process does not exit early.
    return demonstrateAsyncProcessing();
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
