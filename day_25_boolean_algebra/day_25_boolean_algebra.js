/*
 * Boolean Algebra: Boolean Variables, Boolean Expressions, and Boolean Identities
 *
 * Self-contained JavaScript study implementation.
 *
 * Demonstrates:
 * - Boolean values and operators
 * - expressions and precedence
 * - truth tables
 * - Boolean identities
 * - De Morgan's laws
 * - XOR/XNOR
 * - NAND/NOR functional completeness
 * - expression trees
 * - symbolic simplification
 * - canonical minterms
 * - equivalence testing
 * - practical decision systems
 * - asynchronous evaluation
 * - performance considerations
 * - validation and testing
 *
 * Run with:
 *     node boolean_algebra.js
 */

"use strict";

// ============================================================================
// 1. FUNDAMENTAL BOOLEAN VALUES AND OPERATORS
// ============================================================================
//
// JavaScript has Boolean values:
//     true
//     false
//
// Logical operators:
//     !A       NOT
//     A && B   AND
//     A || B   OR
//
// Bitwise operators such as &, |, and ^ are different from logical Boolean
// operators. For single-bit integer values, they can model Boolean operations,
// but they should not be confused with JavaScript's logical operators.


function showFundamentalOperations() {
    console.log("\n" + "=".repeat(80));
    console.log("1. FUNDAMENTAL BOOLEAN OPERATIONS");
    console.log("=".repeat(80));

    for (const a of [false, true]) {
        console.log(`NOT ${Number(a)} = ${Number(!a)}`);
    }

    console.log("\nAND:");
    for (const a of [false, true]) {
        for (const b of [false, true]) {
            console.log(`${Number(a)} AND ${Number(b)} = ${Number(a && b)}`);
        }
    }

    console.log("\nOR:");
    for (const a of [false, true]) {
        for (const b of [false, true]) {
            console.log(`${Number(a)} OR ${Number(b)} = ${Number(a || b)}`);
        }
    }
}


// ============================================================================
// 2. BOOLEAN EXPRESSIONS
// ============================================================================

function booleanExpression(a, b, c) {
    // F = (A AND B) OR (NOT A AND C)
    return (a && b) || (!a && c);
}


function showTruthTable(variableNames, expression) {
    console.log("\n" + variableNames.map(name => name.padStart(3)).join(" ") + " | F");
    console.log("-".repeat(variableNames.length * 4 + 4));

    const combinations = 2 ** variableNames.length;

    for (let number = 0; number < combinations; number++) {
        const values = [];

        for (let bit = variableNames.length - 1; bit >= 0; bit--) {
            values.push(Boolean((number >> bit) & 1));
        }

        const result = Boolean(expression(...values));
        console.log(
            values.map(value => String(Number(value)).padStart(3)).join(" ") +
            ` | ${Number(result)}`
        );
    }
}


function expressionDemo() {
    console.log("\n" + "=".repeat(80));
    console.log("2. BOOLEAN EXPRESSION AND TRUTH TABLE");
    console.log("=".repeat(80));

    console.log("F = (A AND B) OR (NOT A AND C)");
    showTruthTable(["A", "B", "C"], booleanExpression);
}


// ============================================================================
// 3. PRECEDENCE
// ============================================================================
//
// JavaScript logical precedence includes:
//     !
//     &&
//     ||
//
// Therefore:
//     A || B && C
//
// is interpreted as:
//     A || (B && C)
//
// Parentheses are recommended for complex Boolean logic because they make
// intended grouping explicit.


function precedenceDemo() {
    console.log("\n" + "=".repeat(80));
    console.log("3. OPERATOR PRECEDENCE");
    console.log("=".repeat(80));

    const A = true;
    const B = false;
    const C = true;

    console.log("A || B && C       =", Number(A || B && C));
    console.log("A || (B && C)     =", Number(A || (B && C)));
    console.log("(A || B) && C     =", Number((A || B) && C));
}


// ============================================================================
// 4. BOOLEAN IDENTITIES
// ============================================================================

function verifyIdentity(name, left, right, variableCount) {
    const combinations = 2 ** variableCount;

    for (let number = 0; number < combinations; number++) {
        const values = [];

        for (let bit = variableCount - 1; bit >= 0; bit--) {
            values.push(Boolean((number >> bit) & 1));
        }

        if (Boolean(left(...values)) !== Boolean(right(...values))) {
            console.log(`FAILED: ${name} for inputs`, values);
            return false;
        }
    }

    console.log(`PASSED: ${name}`);
    return true;
}


function verifyBooleanIdentities() {
    console.log("\n" + "=".repeat(80));
    console.log("4. BOOLEAN IDENTITIES");
    console.log("=".repeat(80));

    const identities = [
        [
            "Identity: A OR 0 = A",
            a => a || false,
            a => a,
            1
        ],
        [
            "Identity: A AND 1 = A",
            a => a && true,
            a => a,
            1
        ],
        [
            "Dominance: A OR 1 = 1",
            a => a || true,
            () => true,
            1
        ],
        [
            "Dominance: A AND 0 = 0",
            a => a && false,
            () => false,
            1
        ],
        [
            "Idempotent: A OR A = A",
            a => a || a,
            a => a,
            1
        ],
        [
            "Idempotent: A AND A = A",
            a => a && a,
            a => a,
            1
        ],
        [
            "Complement: A OR NOT A = 1",
            a => a || !a,
            () => true,
            1
        ],
        [
            "Complement: A AND NOT A = 0",
            a => a && !a,
            () => false,
            1
        ],
        [
            "Involution: NOT NOT A = A",
            a => !!a,
            a => a,
            1
        ],
        [
            "Commutative OR",
            (a, b) => a || b,
            (a, b) => b || a,
            2
        ],
        [
            "Commutative AND",
            (a, b) => a && b,
            (a, b) => b && a,
            2
        ],
        [
            "Distributive AND over OR",
            (a, b, c) => a && (b || c),
            (a, b, c) => (a && b) || (a && c),
            3
        ],
        [
            "Distributive OR over AND",
            (a, b, c) => a || (b && c),
            (a, b, c) => (a || b) && (a || c),
            3
        ],
        [
            "Absorption A OR AB = A",
            (a, b) => a || (a && b),
            a => a,
            2
        ],
        [
            "Absorption A AND (A OR B) = A",
            (a, b) => a && (a || b),
            a => a,
            2
        ],
        [
            "De Morgan NOT(AB) = A' + B'",
            (a, b) => !(a && b),
            (a, b) => !a || !b,
            2
        ],
        [
            "De Morgan NOT(A+B) = A'B'",
            (a, b) => !(a || b),
            (a, b) => !a && !b,
            2
        ]
    ];

    for (const identity of identities) {
        verifyIdentity(...identity);
    }
}


// ============================================================================
// 5. XOR AND XNOR
// ============================================================================

function xor(a, b) {
    // Logical XOR is true exactly when the operands differ.
    return Boolean(a) !== Boolean(b);
}


function xnor(a, b) {
    return Boolean(a) === Boolean(b);
}


function xorDemo() {
    console.log("\n" + "=".repeat(80));
    console.log("5. XOR AND XNOR");
    console.log("=".repeat(80));

    console.log("A B | XOR XNOR");

    for (const a of [false, true]) {
        for (const b of [false, true]) {
            console.log(
                `${Number(a)} ${Number(b)} |  ${Number(xor(a, b))}    ${Number(xnor(a, b))}`
            );
        }
    }

    const xorExpanded = (a, b) => (!a && b) || (a && !b);

    console.log(
        "\nXOR expansion equivalent:",
        verifyIdentity(
            "A XOR B = A'B + AB'",
            xor,
            xorExpanded,
            2
        )
    );
}


// ============================================================================
// 6. NAND AND NOR
// ============================================================================

function nand(a, b) {
    return !(a && b);
}


function nor(a, b) {
    return !(a || b);
}


function notFromNand(a) {
    return nand(a, a);
}


function andFromNand(a, b) {
    const intermediate = nand(a, b);
    return nand(intermediate, intermediate);
}


function orFromNand(a, b) {
    return nand(nand(a, a), nand(b, b));
}


function functionalCompletenessDemo() {
    console.log("\n" + "=".repeat(80));
    console.log("6. FUNCTIONAL COMPLETENESS USING NAND");
    console.log("=".repeat(80));

    for (const a of [false, true]) {
        for (const b of [false, true]) {
            console.log(
                `A=${Number(a)} B=${Number(b)} | ` +
                `NAND=${Number(nand(a, b))} ` +
                `AND=${Number(andFromNand(a, b))} ` +
                `OR=${Number(orFromNand(a, b))}`
            );
        }
    }

    console.log("\nNOT from NAND:");
    for (const a of [false, true]) {
        console.log(
            `A=${Number(a)} -> ${Number(notFromNand(a))}`
        );
    }
}


// ============================================================================
// 7. HALF ADDER AND FULL ADDER
// ============================================================================

function halfAdder(a, b) {
    return {
        sum: xor(a, b),
        carry: a && b
    };
}


function fullAdder(a, b, carryIn) {
    const first = halfAdder(a, b);
    const second = halfAdder(first.sum, carryIn);

    return {
        sum: second.sum,
        carry: first.carry || second.carry
    };
}


function adderDemo() {
    console.log("\n" + "=".repeat(80));
    console.log("7. BOOLEAN ARITHMETIC: HALF ADDER AND FULL ADDER");
    console.log("=".repeat(80));

    console.log("\nHalf adder:");
    console.log("A B | Sum Carry");

    for (const a of [false, true]) {
        for (const b of [false, true]) {
            const result = halfAdder(a, b);

            console.log(
                `${Number(a)} ${Number(b)} |  ${Number(result.sum)}    ${Number(result.carry)}`
            );
        }
    }

    console.log("\nFull adder:");
    console.log("A B Cin | Sum Cout");

    for (const a of [false, true]) {
        for (const b of [false, true]) {
            for (const carryIn of [false, true]) {
                const result = fullAdder(a, b, carryIn);

                console.log(
                    `${Number(a)} ${Number(b)}  ${Number(carryIn)}  |  ` +
                    `${Number(result.sum)}    ${Number(result.carry)}`
                );
            }
        }
    }
}


// ============================================================================
// 8. CANONICAL MINTERMS
// ============================================================================

function minterm(index, variableCount) {
    const bits = index.toString(2).padStart(variableCount, "0");
    const variables = Array.from(
        { length: variableCount },
        (_, position) => String.fromCharCode(65 + position)
    );

    return variables
        .map((variable, position) => (
            bits[position] === "1" ? variable : variable + "'"
        ))
        .join("");
}


function maxterm(index, variableCount) {
    const bits = index.toString(2).padStart(variableCount, "0");
    const variables = Array.from(
        { length: variableCount },
        (_, position) => String.fromCharCode(65 + position)
    );

    return "(" + variables
        .map((variable, position) => (
            bits[position] === "1" ? variable + "'" : variable
        ))
        .join(" + ") + ")";
}


function canonicalFormDemo() {
    console.log("\n" + "=".repeat(80));
    console.log("8. CANONICAL SOP AND POS");
    console.log("=".repeat(80));

    const variableCount = 3;
    const minterms = [1, 3, 5, 7];
    const maxterms = [0, 2, 4, 6];

    console.log(
        "Canonical SOP:",
        minterms.map(index => minterm(index, variableCount)).join(" + ")
    );

    console.log(
        "Canonical POS:",
        maxterms.map(index => maxterm(index, variableCount)).join("")
    );

    console.log(`Sigma notation: F = Σm(${minterms.join(", ")})`);
    console.log(`Pi notation:    F = ΠM(${maxterms.join(", ")})`);
}


// ============================================================================
// 9. BOOLEAN EXPRESSION TREE
// ============================================================================

class BooleanNode {
    evaluate(environment) {
        throw new Error("evaluate() must be implemented by a subclass");
    }

    toString() {
        throw new Error("toString() must be implemented by a subclass");
    }
}


class VariableNode extends BooleanNode {
    constructor(name) {
        super();
        this.name = name;
    }

    evaluate(environment) {
        if (!Object.prototype.hasOwnProperty.call(environment, this.name)) {
            throw new Error(`Missing Boolean variable: ${this.name}`);
        }

        return Boolean(environment[this.name]);
    }

    toString() {
        return this.name;
    }
}


class ConstantNode extends BooleanNode {
    constructor(value) {
        super();
        this.value = Boolean(value);
    }

    evaluate() {
        return this.value;
    }

    toString() {
        return this.value ? "1" : "0";
    }
}


class NotNode extends BooleanNode {
    constructor(operand) {
        super();
        this.operand = operand;
    }

    evaluate(environment) {
        return !this.operand.evaluate(environment);
    }

    toString() {
        return `(NOT ${this.operand})`;
    }
}


class AndNode extends BooleanNode {
    constructor(left, right) {
        super();
        this.left = left;
        this.right = right;
    }

    evaluate(environment) {
        return this.left.evaluate(environment) &&
            this.right.evaluate(environment);
    }

    toString() {
        return `(${this.left} AND ${this.right})`;
    }
}


class OrNode extends BooleanNode {
    constructor(left, right) {
        super();
        this.left = left;
        this.right = right;
    }

    evaluate(environment) {
        return this.left.evaluate(environment) ||
            this.right.evaluate(environment);
    }

    toString() {
        return `(${this.left} OR ${this.right})`;
    }
}


function expressionTreeDemo() {
    console.log("\n" + "=".repeat(80));
    console.log("9. BOOLEAN EXPRESSION TREE");
    console.log("=".repeat(80));

    const A = new VariableNode("A");
    const B = new VariableNode("B");
    const C = new VariableNode("C");

    // F = AB + A'C
    const expression = new OrNode(
        new AndNode(A, B),
        new AndNode(new NotNode(A), C)
    );

    const environment = {
        A: true,
        B: false,
        C: true
    };

    console.log("Expression:", expression.toString());
    console.log("Environment:", environment);
    console.log("Result:", expression.evaluate(environment));
}


// ============================================================================
// 10. SYMBOLIC SIMPLIFICATION
// ============================================================================
//
// The simplifier applies selected identities:
//
//     A AND 1 = A
//     A AND 0 = 0
//     A OR 1 = 1
//     A OR 0 = A
//     A AND A = A
//     A OR A = A
//     A AND NOT A = 0
//     A OR NOT A = 1
//     NOT NOT A = A
//     A(A+B) = A
//     A+AB = A


function simplify(node) {
    if (
        node instanceof VariableNode ||
        node instanceof ConstantNode
    ) {
        return node;
    }

    if (node instanceof NotNode) {
        const operand = simplify(node.operand);

        if (operand instanceof ConstantNode) {
            return new ConstantNode(!operand.value);
        }

        if (operand instanceof NotNode) {
            return simplify(operand.operand);
        }

        return new NotNode(operand);
    }

    if (node instanceof AndNode) {
        const left = simplify(node.left);
        const right = simplify(node.right);

        if (left instanceof ConstantNode) {
            return left.value ? right : new ConstantNode(false);
        }

        if (right instanceof ConstantNode) {
            return right.value ? left : new ConstantNode(false);
        }

        if (left.toString() === right.toString()) {
            return left;
        }

        if (
            left instanceof NotNode &&
            left.operand.toString() === right.toString()
        ) {
            return new ConstantNode(false);
        }

        if (
            right instanceof NotNode &&
            right.operand.toString() === left.toString()
        ) {
            return new ConstantNode(false);
        }

        if (right instanceof OrNode) {
            if (
                right.left.toString() === left.toString() ||
                right.right.toString() === left.toString()
            ) {
                return left;
            }
        }

        if (left instanceof OrNode) {
            if (
                left.left.toString() === right.toString() ||
                left.right.toString() === right.toString()
            ) {
                return right;
            }
        }

        return new AndNode(left, right);
    }

    if (node instanceof OrNode) {
        const left = simplify(node.left);
        const right = simplify(node.right);

        if (left instanceof ConstantNode) {
            return left.value ? new ConstantNode(true) : right;
        }

        if (right instanceof ConstantNode) {
            return right.value ? new ConstantNode(true) : left;
        }

        if (left.toString() === right.toString()) {
            return left;
        }

        if (
            left instanceof NotNode &&
            left.operand.toString() === right.toString()
        ) {
            return new ConstantNode(true);
        }

        if (
            right instanceof NotNode &&
            right.operand.toString() === left.toString()
        ) {
            return new ConstantNode(true);
        }

        if (right instanceof AndNode) {
            if (
                right.left.toString() === left.toString() ||
                right.right.toString() === left.toString()
            ) {
                return left;
            }
        }

        if (left instanceof AndNode) {
            if (
                left.left.toString() === right.toString() ||
                left.right.toString() === right.toString()
            ) {
                return right;
            }
        }

        return new OrNode(left, right);
    }

    throw new Error(`Unsupported node: ${node.constructor.name}`);
}


function simplificationDemo() {
    console.log("\n" + "=".repeat(80));
    console.log("10. SYMBOLIC SIMPLIFICATION");
    console.log("=".repeat(80));

    const A = new VariableNode("A");
    const B = new VariableNode("B");

    const examples = [
        [
            "A AND 1",
            new AndNode(A, new ConstantNode(true))
        ],
        [
            "A OR 0",
            new OrNode(A, new ConstantNode(false))
        ],
        [
            "A AND A",
            new AndNode(A, A)
        ],
        [
            "A OR A",
            new OrNode(A, A)
        ],
        [
            "A AND NOT A",
            new AndNode(A, new NotNode(A))
        ],
        [
            "A OR NOT A",
            new OrNode(A, new NotNode(A))
        ],
        [
            "A AND (A OR B)",
            new AndNode(A, new OrNode(A, B))
        ],
        [
            "A OR (A AND B)",
            new OrNode(A, new AndNode(A, B))
        ],
        [
            "NOT NOT A",
            new NotNode(new NotNode(A))
        ]
    ];

    for (const [name, expression] of examples) {
        console.log(
            `${name.padEnd(24)} -> ${simplify(expression).toString()}`
        );
    }
}


// ============================================================================
// 11. LOGICAL EQUIVALENCE
// ============================================================================

function areEquivalent(variableCount, first, second) {
    const combinations = 2 ** variableCount;

    for (let number = 0; number < combinations; number++) {
        const values = [];

        for (let bit = variableCount - 1; bit >= 0; bit--) {
            values.push(Boolean((number >> bit) & 1));
        }

        if (Boolean(first(...values)) !== Boolean(second(...values))) {
            return false;
        }
    }

    return true;
}


function equivalenceDemo() {
    console.log("\n" + "=".repeat(80));
    console.log("11. LOGICAL EQUIVALENCE TESTING");
    console.log("=".repeat(80));

    const deMorganOne = (a, b) => !(a && b);
    const deMorganTwo = (a, b) => !a || !b;

    console.log(
        "NOT(A AND B) == NOT A OR NOT B:",
        areEquivalent(2, deMorganOne, deMorganTwo)
    );

    const absorptionOne = (a, b) => a || (a && b);
    const absorptionTwo = a => a;

    console.log(
        "A OR (A AND B) == A:",
        areEquivalent(2, absorptionOne, absorptionTwo)
    );
}


// ============================================================================
// 12. ACCESS CONTROL CASE
// ============================================================================
//
// Access = authenticated AND (admin OR owner) OR emergencyOverride
//
// This illustrates policy logic, but real authorization systems require
// explicit policy semantics, identity verification, auditing, logging, and
// secure defaults.


function accessGranted({
    authenticated,
    admin,
    owner,
    emergencyOverride
}) {
    return (
        (authenticated && (admin || owner)) ||
        emergencyOverride
    );
}


function accessControlDemo() {
    console.log("\n" + "=".repeat(80));
    console.log("12. ACCESS CONTROL LOGIC");
    console.log("=".repeat(80));

    const scenarios = [
        {
            authenticated: false,
            admin: false,
            owner: false,
            emergencyOverride: false
        },
        {
            authenticated: true,
            admin: false,
            owner: true,
            emergencyOverride: false
        },
        {
            authenticated: true,
            admin: true,
            owner: false,
            emergencyOverride: false
        },
        {
            authenticated: true,
            admin: false,
            owner: false,
            emergencyOverride: false
        },
        {
            authenticated: false,
            admin: false,
            owner: false,
            emergencyOverride: true
        }
    ];

    for (const scenario of scenarios) {
        console.log(
            scenario,
            "=> access:",
            accessGranted(scenario)
        );
    }
}


// ============================================================================
// 13. VALIDATION
// ============================================================================

function requireBoolean(value, name) {
    if (typeof value !== "boolean") {
        throw new TypeError(
            `${name} must be a Boolean; received ${typeof value}`
        );
    }

    return value;
}


function safeAnd(a, b) {
    requireBoolean(a, "a");
    requireBoolean(b, "b");
    return a && b;
}


function validationDemo() {
    console.log("\n" + "=".repeat(80));
    console.log("13. VALIDATION AND FAILURE HANDLING");
    console.log("=".repeat(80));

    console.log("safeAnd(true, false) =", safeAnd(true, false));

    try {
        safeAnd(true, 1);
    } catch (error) {
        console.log("Caught expected error:", error.message);
    }
}


// ============================================================================
// 14. JAVASCRIPT TRUTHINESS VERSUS BOOLEAN ALGEBRA
// ============================================================================
//
// JavaScript is not restricted to Boolean values in conditional expressions.
// Values such as 0, "", null, undefined, and NaN are falsy.
//
// Boolean algebra itself contains only 0 and 1.
// Therefore, Boolean algebra models should normalize inputs when exact Boolean
// semantics are required.


function truthinessDemo() {
    console.log("\n" + "=".repeat(80));
    console.log("14. JAVASCRIPT TRUTHINESS");
    console.log("=".repeat(80));

    const values = [
        false,
        true,
        0,
        1,
        "",
        "Boolean",
        null,
        undefined,
        [],
        [1]
    ];

    for (const value of values) {
        console.log(
            String(value).padEnd(12),
            "=> Boolean(value) =",
            Boolean(value)
        );
    }

    console.log(
        "\nFor Boolean algebra, explicitly normalize external values with Boolean()."
    );
}


// ============================================================================
// 15. ASYNCHRONOUS BOOLEAN EVALUATION
// ============================================================================
//
// JavaScript is event-driven and frequently evaluates conditions after
// asynchronous operations such as network requests.
//
// The example below models asynchronous policy inputs without external
// dependencies.


function getSecuritySignal(name, value, delayMilliseconds) {
    return new Promise(resolve => {
        setTimeout(() => {
            resolve({
                name,
                value: Boolean(value)
            });
        }, delayMilliseconds);
    });
}


async function asynchronousPolicyDemo() {
    console.log("\n" + "=".repeat(80));
    console.log("15. ASYNCHRONOUS BOOLEAN POLICY EVALUATION");
    console.log("=".repeat(80));

    const [authenticated, admin, owner] = await Promise.all([
        getSecuritySignal("authenticated", true, 10),
        getSecuritySignal("admin", false, 20),
        getSecuritySignal("owner", true, 15)
    ]);

    const access = (
        authenticated.value &&
        (admin.value || owner.value)
    );

    console.log("Signals:", {
        authenticated,
        admin,
        owner
    });

    console.log("Access:", access);
}


// ============================================================================
// 16. BIT-PARALLEL BOOLEAN OPERATIONS
// ============================================================================
//
// JavaScript bitwise operations operate on signed 32-bit integer values.
// They can be useful when multiple Boolean flags are packed into bits.
//
// This is not the same as ordinary logical && and ||.


function bitMaskDemo() {
    console.log("\n" + "=".repeat(80));
    console.log("16. BIT-MASK BOOLEAN REPRESENTATION");
    console.log("=".repeat(80));

    const READ = 1 << 0;
    const WRITE = 1 << 1;
    const EXECUTE = 1 << 2;

    let permissions = READ | WRITE;

    console.log("Permissions mask:", permissions);
    console.log("Has READ:", Boolean(permissions & READ));
    console.log("Has WRITE:", Boolean(permissions & WRITE));
    console.log("Has EXECUTE:", Boolean(permissions & EXECUTE));

    permissions |= EXECUTE;

    console.log("After adding EXECUTE:", permissions);

    permissions &= ~WRITE;

    console.log("After removing WRITE:", permissions);
}


// ============================================================================
// 17. TEST SUITE
// ============================================================================

function assertEqual(actual, expected, description) {
    if (actual !== expected) {
        throw new Error(
            `${description}: expected ${expected}, received ${actual}`
        );
    }
}


function runTests() {
    console.log("\n" + "=".repeat(80));
    console.log("17. SELF-TESTS");
    console.log("=".repeat(80));

    assertEqual(nand(false, false), true, "NAND 0,0");
    assertEqual(nand(true, true), false, "NAND 1,1");

    assertEqual(nor(false, false), true, "NOR 0,0");
    assertEqual(nor(true, false), false, "NOR 1,0");

    assertEqual(halfAdder(false, false).sum, false, "Half adder sum");
    assertEqual(halfAdder(true, false).sum, true, "Half adder sum");
    assertEqual(halfAdder(true, true).carry, true, "Half adder carry");

    const fullAdderResult = fullAdder(true, true, true);

    assertEqual(fullAdderResult.sum, true, "Full adder sum");
    assertEqual(fullAdderResult.carry, true, "Full adder carry");

    assertEqual(
        areEquivalent(
            2,
            (a, b) => !(a && b),
            (a, b) => !a || !b
        ),
        true,
        "De Morgan equivalence"
    );

    assertEqual(
        accessGranted({
            authenticated: true,
            admin: true,
            owner: false,
            emergencyOverride: false
        }),
        true,
        "Admin access"
    );

    assertEqual(
        accessGranted({
            authenticated: true,
            admin: false,
            owner: false,
            emergencyOverride: false
        }),
        false,
        "Unauthorized access"
    );

    console.log("All JavaScript tests passed.");
}


// ============================================================================
// 18. PERFORMANCE GROWTH
// ============================================================================

function performanceDemo() {
    console.log("\n" + "=".repeat(80));
    console.log("18. TRUTH-TABLE PERFORMANCE GROWTH");
    console.log("=".repeat(80));

    for (let variableCount = 1; variableCount <= 12; variableCount++) {
        console.log(
            `${String(variableCount).padStart(2)} variables -> ` +
            `${String(2 ** variableCount).padStart(5)} combinations`
        );
    }

    console.log(
        "\nExhaustive equivalence testing is exponential in the number of variables."
    );
}


// ============================================================================
// 19. MAIN
// ============================================================================

async function main() {
    console.log("=".repeat(80));
    console.log("BOOLEAN ALGEBRA: JAVASCRIPT EXECUTABLE STUDY");
    console.log("=".repeat(80));

    showFundamentalOperations();
    expressionDemo();
    precedenceDemo();
    verifyBooleanIdentities();
    xorDemo();
    functionalCompletenessDemo();
    adderDemo();
    canonicalFormDemo();
    expressionTreeDemo();
    simplificationDemo();
    equivalenceDemo();
    accessControlDemo();
    validationDemo();
    truthinessDemo();
    await asynchronousPolicyDemo();
    bitMaskDemo();
    performanceDemo();
    runTests();

    console.log("\n" + "=".repeat(80));
    console.log("END OF JAVASCRIPT BOOLEAN ALGEBRA STUDY");
    console.log("=".repeat(80));
}


main().catch(error => {
    console.error("Program failed:", error);
    process.exitCode = 1;
});
