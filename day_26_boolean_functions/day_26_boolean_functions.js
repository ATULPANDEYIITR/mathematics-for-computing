/*
 * Boolean Functions: Truth Tables, Minterms, and Maxterms
 *
 * This self-contained JavaScript study file demonstrates:
 *   - Boolean operations
 *   - Boolean functions
 *   - Truth tables
 *   - Binary row indexing
 *   - Minterms
 *   - Maxterms
 *   - Canonical SOP and POS
 *   - Functional equivalence
 *   - De Morgan's laws
 *   - Don't-care conditions
 *   - Minterm adjacency
 *   - Quine-McCluskey-style combination
 *   - Validation
 *   - A practical control-system case study
 *
 * Runtime: modern Node.js
 * No external packages are required.
 */

"use strict";


// ============================================================
// 1. BASIC BOOLEAN OPERATIONS
// ============================================================

function booleanNot(value) {
    return !value;
}

function booleanAnd(left, right) {
    return left && right;
}

function booleanOr(left, right) {
    return left || right;
}

function booleanXor(left, right) {
    return left !== right;
}

function booleanXnor(left, right) {
    return left === right;
}

console.log("=".repeat(78));
console.log("BOOLEAN FUNCTIONS: TRUTH TABLES, MINTERMS, AND MAXTERMS");
console.log("=".repeat(78));

console.log("\n1. BASIC BOOLEAN OPERATIONS");

for (const a of [false, true]) {
    for (const b of [false, true]) {
        console.log(
            `A=${Number(a)} B=${Number(b)} | ` +
            `NOT A=${Number(booleanNot(a))} | ` +
            `A AND B=${Number(booleanAnd(a, b))} | ` +
            `A OR B=${Number(booleanOr(a, b))} | ` +
            `A XOR B=${Number(booleanXor(a, b))} | ` +
            `A XNOR B=${Number(booleanXnor(a, b))}`
        );
    }
}


// ============================================================
// 2. BOOLEAN FUNCTIONS
// ============================================================

function majorityFunction(a, b, c) {
    // At least two of the three inputs must be true.
    return (a && b) || (a && c) || (b && c);
}

function parityFunction(a, b, c) {
    // XOR is true when an odd number of inputs are true.
    return a !== b !== c;
}

console.log("\n2. BOOLEAN FUNCTIONS");

for (const inputs of generateInputCombinations(3)) {
    const [a, b, c] = inputs;

    console.log(
        `${inputs.join(" ")} | ` +
        `MAJORITY=${Number(majorityFunction(Boolean(a), Boolean(b), Boolean(c)))} | ` +
        `PARITY=${Number(parityFunction(Boolean(a), Boolean(b), Boolean(c)))}`
    );
}


// ============================================================
// 3. INPUT COMBINATION GENERATION
// ============================================================

function generateInputCombinations(variableCount) {
    if (!Number.isInteger(variableCount) || variableCount < 0) {
        throw new Error("Variable count must be a non-negative integer.");
    }

    const rowCount = 2 ** variableCount;
    const combinations = [];

    for (let index = 0; index < rowCount; index++) {
        const binary = index.toString(2).padStart(variableCount, "0");
        combinations.push(
            [...binary].map(bit => Number(bit))
        );
    }

    return combinations;
}


// ============================================================
// 4. TRUTH TABLE CLASS
// ============================================================

class TruthTable {
    constructor(variables, functionDefinition) {
        this.variables = [...variables];

        if (this.variables.length === 0) {
            throw new Error("At least one Boolean variable is required.");
        }

        if (typeof functionDefinition !== "function") {
            throw new Error("Function definition must be callable.");
        }

        this.rows = generateInputCombinations(this.variables.length);

        this.outputs = this.rows.map(inputs => {
            const booleanInputs = inputs.map(Boolean);
            return Number(Boolean(functionDefinition(...booleanInputs)));
        });
    }

    print(title = "Truth Table") {
        console.log(`\n${title}`);
        console.log("-".repeat(78));

        console.log(
            `${this.variables.join(" | ")} | F`
        );

        console.log("-".repeat(78));

        this.rows.forEach((inputs, index) => {
            console.log(
                `${inputs.join(" | ")} | ${this.outputs[index]}`
            );
        });
    }

    getRowCount() {
        return this.rows.length;
    }
}

const majorityTable = new TruthTable(
    ["A", "B", "C"],
    majorityFunction
);

majorityTable.print("Majority Function: F = AB + AC + BC");


// ============================================================
// 5. BINARY INDEXING
// ============================================================

function binaryIndex(inputs) {
    let index = 0;

    for (const bit of inputs) {
        if (bit !== 0 && bit !== 1) {
            throw new Error("Boolean vectors may contain only 0 and 1.");
        }

        index = (index << 1) | bit;
    }

    return index;
}

console.log("\n3. BINARY INPUT TO DECIMAL INDEX");

for (const inputs of [
    [0, 0, 0],
    [0, 1, 1],
    [1, 0, 1],
    [1, 1, 1]
]) {
    console.log(`${inputs.join("")} -> ${binaryIndex(inputs)}`);
}


// ============================================================
// 6. MINTERM REPRESENTATION
// ============================================================

function mintermExpression(variables, index) {
    const variableCount = variables.length;

    if (
        !Number.isInteger(index) ||
        index < 0 ||
        index >= 2 ** variableCount
    ) {
        throw new Error("Minterm index is outside the valid range.");
    }

    const binary = index
        .toString(2)
        .padStart(variableCount, "0");

    return variables
        .map((variable, position) => {
            // A 1 means the variable is uncomplemented.
            // A 0 means the variable is complemented.
            return binary[position] === "1"
                ? variable
                : `${variable}'`;
        })
        .join("");
}

console.log("\n4. THREE-VARIABLE MINTERMS");

for (let index = 0; index < 8; index++) {
    console.log(
        `m${index} = ${mintermExpression(["A", "B", "C"], index)}`
    );
}


// ============================================================
// 7. MAXTERM REPRESENTATION
// ============================================================

function maxtermExpression(variables, index) {
    const variableCount = variables.length;

    if (
        !Number.isInteger(index) ||
        index < 0 ||
        index >= 2 ** variableCount
    ) {
        throw new Error("Maxterm index is outside the valid range.");
    }

    const binary = index
        .toString(2)
        .padStart(variableCount, "0");

    const terms = variables.map((variable, position) => {
        /*
         * A 0 means the variable is uncomplemented.
         * A 1 means the variable is complemented.
         */
        return binary[position] === "0"
            ? variable
            : `${variable}'`;
    });

    return `(${terms.join(" + ")})`;
}

console.log("\n5. THREE-VARIABLE MAXTERMS");

for (let index = 0; index < 8; index++) {
    console.log(
        `M${index} = ${maxtermExpression(["A", "B", "C"], index)}`
    );
}


// ============================================================
// 8. EXTRACT MINTERMS AND MAXTERMS
// ============================================================

function extractMintermsAndMaxterms(table) {
    const minterms = [];
    const maxterms = [];

    table.rows.forEach((inputs, row) => {
        const index = binaryIndex(inputs);

        if (table.outputs[row] === 1) {
            minterms.push(index);
        } else {
            maxterms.push(index);
        }
    });

    return { minterms, maxterms };
}

const majorityRepresentation =
    extractMintermsAndMaxterms(majorityTable);

console.log("\n6. MAJORITY FUNCTION REPRESENTATION");
console.log(
    "Minterms:",
    majorityRepresentation.minterms
);
console.log(
    "Maxterms:",
    majorityRepresentation.maxterms
);


// ============================================================
// 9. CANONICAL SOP AND POS
// ============================================================

function canonicalSOP(variables, minterms) {
    const indices = [...new Set(minterms)];

    if (indices.length === 0) {
        return "0";
    }

    if (indices.length === 2 ** variables.length) {
        return "1";
    }

    return indices
        .sort((a, b) => a - b)
        .map(index => mintermExpression(variables, index))
        .join(" + ");
}

function canonicalPOS(variables, maxterms) {
    const indices = [...new Set(maxterms)];

    if (indices.length === 0) {
        return "1";
    }

    if (indices.length === 2 ** variables.length) {
        return "0";
    }

    return indices
        .sort((a, b) => a - b)
        .map(index => maxtermExpression(variables, index))
        .join("");
}

console.log(
    "Canonical SOP:",
    canonicalSOP(
        majorityTable.variables,
        majorityRepresentation.minterms
    )
);

console.log(
    "Canonical POS:",
    canonicalPOS(
        majorityTable.variables,
        majorityRepresentation.maxterms
    )
);


// ============================================================
// 10. EVALUATING CANONICAL FORMS
// ============================================================

function evaluateSOP(inputs, minterms) {
    const target = new Set(minterms);
    return target.has(binaryIndex(inputs)) ? 1 : 0;
}

function evaluatePOS(inputs, maxterms) {
    const target = new Set(maxterms);

    // A POS evaluates to zero at its listed maxterm rows.
    return target.has(binaryIndex(inputs)) ? 0 : 1;
}

console.log("\n7. VERIFY CANONICAL FORMS");

majorityTable.rows.forEach((inputs, row) => {
    const sop = evaluateSOP(
        inputs,
        majorityRepresentation.minterms
    );

    const pos = evaluatePOS(
        inputs,
        majorityRepresentation.maxterms
    );

    const original = majorityTable.outputs[row];

    if (sop !== original || pos !== original) {
        throw new Error(
            `Canonical representation failed for row ${row}.`
        );
    }
});

console.log("SOP verification: PASS");
console.log("POS verification: PASS");


// ============================================================
// 11. DE MORGAN'S LAWS
// ============================================================

console.log("\n8. DE MORGAN'S LAWS");

for (const a of [false, true]) {
    for (const b of [false, true]) {
        const firstLeft = !(a && b);
        const firstRight = (!a) || (!b);

        const secondLeft = !(a || b);
        const secondRight = (!a) && (!b);

        console.assert(
            firstLeft === firstRight,
            "First De Morgan law failed."
        );

        console.assert(
            secondLeft === secondRight,
            "Second De Morgan law failed."
        );
    }
}

console.log("NOT(A AND B) = NOT A OR NOT B");
console.log("NOT(A OR B) = NOT A AND NOT B");


// ============================================================
// 12. FUNCTIONAL EQUIVALENCE
// ============================================================

function functionsAreEquivalent(
    variableCount,
    firstFunction,
    secondFunction
) {
    for (const inputs of generateInputCombinations(variableCount)) {
        const first = Number(
            Boolean(firstFunction(...inputs.map(Boolean)))
        );

        const second = Number(
            Boolean(secondFunction(...inputs.map(Boolean)))
        );

        if (first !== second) {
            return false;
        }
    }

    return true;
}

const expressionA = (a, b, c) =>
    (a && b) || (a && c) || (b && c);

const expressionB = (a, b, c) =>
    (a && (b || c)) || (b && c);

console.log("\n9. FUNCTIONAL EQUIVALENCE");

console.log(
    "AB + AC + BC == A(B+C) + BC:",
    functionsAreEquivalent(
        3,
        expressionA,
        expressionB
    )
);


// ============================================================
// 13. DON'T-CARE CONDITIONS
// ============================================================

class BooleanSpecification {
    constructor(variableCount, onSet, offSet, dontCareSet) {
        this.variableCount = variableCount;
        this.onSet = new Set(onSet);
        this.offSet = new Set(offSet);
        this.dontCareSet = new Set(dontCareSet);

        this.validate();
    }

    validate() {
        const maximum = 2 ** this.variableCount - 1;

        const validateRange = (set, name) => {
            for (const index of set) {
                if (
                    !Number.isInteger(index) ||
                    index < 0 ||
                    index > maximum
                ) {
                    throw new Error(
                        `${name} contains invalid index ${index}.`
                    );
                }
            }
        };

        validateRange(this.onSet, "ON-set");
        validateRange(this.offSet, "OFF-set");
        validateRange(this.dontCareSet, "Don't-care set");

        for (const index of this.onSet) {
            if (this.offSet.has(index)) {
                throw new Error("ON-set and OFF-set overlap.");
            }

            if (this.dontCareSet.has(index)) {
                throw new Error("ON-set and don't-care set overlap.");
            }
        }

        for (const index of this.offSet) {
            if (this.dontCareSet.has(index)) {
                throw new Error(
                    "OFF-set and don't-care set overlap."
                );
            }
        }
    }
}

const specification = new BooleanSpecification(
    3,
    [1, 3, 5],
    [0, 2, 7],
    [4, 6]
);

console.log("\n10. DON'T-CARE SPECIFICATION");
console.log("ON-set:", [...specification.onSet].sort((a, b) => a - b));
console.log("OFF-set:", [...specification.offSet].sort((a, b) => a - b));
console.log(
    "Don't-care:",
    [...specification.dontCareSet].sort((a, b) => a - b)
);


// ============================================================
// 14. HAMMING DISTANCE AND ADJACENCY
// ============================================================

function hammingDistance(left, right, variableCount) {
    const leftBits = left
        .toString(2)
        .padStart(variableCount, "0");

    const rightBits = right
        .toString(2)
        .padStart(variableCount, "0");

    let differenceCount = 0;

    for (let i = 0; i < variableCount; i++) {
        if (leftBits[i] !== rightBits[i]) {
            differenceCount++;
        }
    }

    return differenceCount;
}

function adjacentMinterms(index, variableCount) {
    const result = [];

    for (let candidate = 0; candidate < 2 ** variableCount; candidate++) {
        if (
            candidate !== index &&
            hammingDistance(
                index,
                candidate,
                variableCount
            ) === 1
        ) {
            result.push(candidate);
        }
    }

    return result;
}

console.log("\n11. MINTERM ADJACENCY");

for (let index = 0; index < 8; index++) {
    console.log(
        `m${index}:`,
        adjacentMinterms(index, 3)
    );
}


// ============================================================
// 15. QUINE-MCCLUSKEY-STYLE IMPLICANTS
// ============================================================

class Implicant {
    constructor(pattern, coveredMinterms) {
        this.pattern = pattern;
        this.coveredMinterms = new Set(coveredMinterms);
    }

    combine(other) {
        if (this.pattern.length !== other.pattern.length) {
            return null;
        }

        const differences = [];

        for (let i = 0; i < this.pattern.length; i++) {
            const left = this.pattern[i];
            const right = other.pattern[i];

            if (left !== right) {
                if (left === "-" || right === "-") {
                    return null;
                }

                differences.push(i);
            }
        }

        if (differences.length !== 1) {
            return null;
        }

        const position = differences[0];

        const combinedPattern =
            this.pattern.slice(0, position) +
            "-" +
            this.pattern.slice(position + 1);

        return new Implicant(
            combinedPattern,
            [
                ...this.coveredMinterms,
                ...other.coveredMinterms
            ]
        );
    }
}

function createInitialImplicants(minterms, variableCount) {
    return [...new Set(minterms)].map(index =>
        new Implicant(
            index
                .toString(2)
                .padStart(variableCount, "0"),
            [index]
        )
    );
}

function oneStepCombine(implicants) {
    const combinedByPattern = new Map();
    const combinedIndices = new Set();

    for (let i = 0; i < implicants.length; i++) {
        for (let j = i + 1; j < implicants.length; j++) {
            const result = implicants[i].combine(implicants[j]);

            if (result !== null) {
                combinedByPattern.set(
                    result.pattern,
                    result
                );

                combinedIndices.add(i);
                combinedIndices.add(j);
            }
        }
    }

    const leftovers = implicants.filter(
        (_, index) => !combinedIndices.has(index)
    );

    return {
        combined: [...combinedByPattern.values()],
        leftovers
    };
}

console.log("\n12. QUINE-MCCLUSKEY-STYLE COMBINATION");

const initialImplicants = createInitialImplicants(
    [1, 3, 5, 7],
    3
);

const combinationResult = oneStepCombine(
    initialImplicants
);

for (const implicant of combinationResult.combined) {
    console.log(
        `${implicant.pattern} covers ` +
        `[${[...implicant.coveredMinterms].sort((a, b) => a - b)}]`
    );
}


// ============================================================
// 16. PRACTICAL CONTROL SYSTEM
// ============================================================

/*
 * Three-input activation controller:
 *
 * D = door closed
 * A = authorization valid
 * E = emergency override
 *
 * S = DA + E
 *
 * This demonstrates how a Boolean function can encode a simple
 * real-world decision rule.
 */

function safetyController(
    doorClosed,
    authorized,
    emergencyOverride
) {
    return (
        (doorClosed && authorized) ||
        emergencyOverride
    );
}

const safetyTable = new TruthTable(
    ["D", "A", "E"],
    safetyController
);

safetyTable.print("Safety Controller: S = DA + E");

const safetyRepresentation =
    extractMintermsAndMaxterms(safetyTable);

console.log(
    "\n13. SAFETY CONTROLLER CANONICAL REPRESENTATION"
);

console.log(
    `S = Σm(${safetyRepresentation.minterms.join(",")})`
);

console.log(
    `S = ΠM(${safetyRepresentation.maxterms.join(",")})`
);

console.log(
    "SOP:",
    canonicalSOP(
        ["D", "A", "E"],
        safetyRepresentation.minterms
    )
);

console.log(
    "POS:",
    canonicalPOS(
        ["D", "A", "E"],
        safetyRepresentation.maxterms
    )
);


// ============================================================
// 17. EDGE CASES
// ============================================================

console.log("\n14. EDGE CASES");

const constantZero = new TruthTable(
    ["A", "B"],
    () => false
);

const constantOne = new TruthTable(
    ["A", "B"],
    () => true
);

const zeroRepresentation =
    extractMintermsAndMaxterms(constantZero);

const oneRepresentation =
    extractMintermsAndMaxterms(constantOne);

console.log(
    "Constant 0 minterms:",
    zeroRepresentation.minterms
);

console.log(
    "Constant 0 maxterms:",
    zeroRepresentation.maxterms
);

console.log(
    "Constant 1 minterms:",
    oneRepresentation.minterms
);

console.log(
    "Constant 1 maxterms:",
    oneRepresentation.maxterms
);

console.assert(
    canonicalSOP(
        ["A", "B"],
        zeroRepresentation.minterms
    ) === "0"
);

console.assert(
    canonicalPOS(
        ["A", "B"],
        zeroRepresentation.maxterms
    ) === "0"
);

console.assert(
    canonicalSOP(
        ["A", "B"],
        oneRepresentation.minterms
    ) === "1"
);

console.assert(
    canonicalPOS(
        ["A", "B"],
        oneRepresentation.maxterms
    ) === "1"
);


// ============================================================
// 18. ERROR HANDLING
// ============================================================

console.log("\n15. ERROR HANDLING");

try {
    binaryIndex([1, 0, 2]);
} catch (error) {
    console.log("Caught invalid input:", error.message);
}

try {
    mintermExpression(["A", "B"], 4);
} catch (error) {
    console.log("Caught invalid minterm:", error.message);
}

try {
    new BooleanSpecification(
        2,
        [1],
        [1],
        []
    );
} catch (error) {
    console.log(
        "Caught overlapping specification:",
        error.message
    );
}


// ============================================================
// 19. COMPLEXITY
// ============================================================

function booleanSpaceSize(variableCount) {
    const rows = 2 ** variableCount;
    const functionCount = 2 ** rows;

    return {
        rows,
        functionCount
    };
}

console.log("\n16. BOOLEAN FUNCTION SPACE");

for (let variableCount = 1; variableCount <= 5; variableCount++) {
    const { rows, functionCount } =
        booleanSpaceSize(variableCount);

    console.log(
        `n=${variableCount}: ` +
        `rows=${rows.toLocaleString()}, ` +
        `possible functions=${functionCount.toLocaleString()}`
    );
}


// ============================================================
// 20. ASYNCHRONOUS VALIDATION EXAMPLE
// ============================================================

/*
 * JavaScript is particularly useful when Boolean decisions are part of
 * event-driven applications. This Promise-based validator simulates an
 * asynchronous policy check without requiring a network service.
 */

function asynchronousPolicyCheck(input) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (
                typeof input !== "object" ||
                input === null
            ) {
                reject(
                    new Error("Input must be an object.")
                );
                return;
            }

            const {
                doorClosed,
                authorized,
                emergencyOverride
            } = input;

            const result = safetyController(
                Boolean(doorClosed),
                Boolean(authorized),
                Boolean(emergencyOverride)
            );

            resolve(result);
        }, 10);
    });
}

async function demonstrateAsyncPolicyCheck() {
    const request = {
        doorClosed: true,
        authorized: true,
        emergencyOverride: false
    };

    const result =
        await asynchronousPolicyCheck(request);

    console.log(
        "\n17. ASYNCHRONOUS BOOLEAN POLICY RESULT:",
        result
    );
}


// ============================================================
// 21. COMPLETE SELF-TEST
// ============================================================

function selfTest() {
    const table = new TruthTable(
        ["A", "B", "C"],
        (a, b, c) => (a && b) || !c
    );

    const representation =
        extractMintermsAndMaxterms(table);

    table.rows.forEach((inputs, row) => {
        const sop = evaluateSOP(
            inputs,
            representation.minterms
        );

        const pos = evaluatePOS(
            inputs,
            representation.maxterms
        );

        if (
            sop !== table.outputs[row] ||
            pos !== table.outputs[row]
        ) {
            throw new Error(
                `Self-test failed at row ${row}.`
            );
        }
    });

    if (
        !functionsAreEquivalent(
            3,
            majorityFunction,
            expressionB
        )
    ) {
        throw new Error(
            "Majority equivalence test failed."
        );
    }

    console.log("\n18. SELF-TEST: PASS");
}

selfTest();


// ============================================================
// 22. PROGRAM ENTRY FOR ASYNCHRONOUS DEMONSTRATION
// ============================================================

demonstrateAsyncPolicyCheck()
    .then(() => {
        console.log("\nBoolean-function study execution completed.");
    })
    .catch(error => {
        console.error(
            "Asynchronous demonstration failed:",
            error.message
        );
        process.exitCode = 1;
    });
