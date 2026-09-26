"use strict";

/*
 * Logic in Computing
 * ==================
 *
 * Digital logic, predicates in programs, assertions, and verification.
 *
 * This file complements the Python implementation by emphasizing JavaScript
 * truthiness, short-circuit behavior, functional predicates, asynchronous
 * verification, immutable-style transformations, and application-level rules.
 *
 * Run with:
 *     node logic_in_computing.js
 */


// ============================================================================
// 1. BOOLEAN LOGIC AND DIGITAL GATES
// ============================================================================

const NOT = (value) => !value;
const AND = (left, right) => left && right;
const OR = (left, right) => left || right;
const XOR = (left, right) => left !== right;
const NAND = (left, right) => !(left && right);
const NOR = (left, right) => !(left || right);
const XNOR = (left, right) => left === right;

function implication(antecedent, consequent) {
    // P -> Q is false only when P is true and Q is false.
    return !antecedent || consequent;
}

function printTruthTable(name, operation) {
    console.log(`\n${name}`);
    console.log("A B | Result");
    console.log("----+-------");

    for (const a of [false, true]) {
        for (const b of [false, true]) {
            console.log(
                `${Number(a)} ${Number(b)} |   ${Number(operation(a, b))}`
            );
        }
    }
}

function demonstrateGates() {
    console.log("\n=== DIGITAL LOGIC GATES ===");

    printTruthTable("AND", AND);
    printTruthTable("OR", OR);
    printTruthTable("XOR", XOR);
    printTruthTable("NAND", NAND);
    printTruthTable("NOR", NOR);
    printTruthTable("XNOR", XNOR);

    console.log("\nNOT");
    for (const value of [false, true]) {
        console.log(`${Number(value)} -> ${Number(NOT(value))}`);
    }
}


// ============================================================================
// 2. BOOLEAN ALGEBRA
// ============================================================================

function assert(condition, message = "Assertion failed") {
    if (!condition) {
        throw new Error(message);
    }
}

function verifyBooleanLaws() {
    const values = [false, true];

    for (const p of values) {
        assert(AND(p, true) === p);
        assert(OR(p, false) === p);
        assert(AND(p, false) === false);
        assert(OR(p, true) === true);
        assert(AND(p, p) === p);
        assert(OR(p, p) === p);
        assert(AND(p, NOT(p)) === false);
        assert(OR(p, NOT(p)) === true);
        assert(NOT(NOT(p)) === p);
    }

    for (const p of values) {
        for (const q of values) {
            assert(
                NOT(AND(p, q)) === OR(NOT(p), NOT(q)),
                "De Morgan law 1 failed"
            );

            assert(
                NOT(OR(p, q)) === AND(NOT(p), NOT(q)),
                "De Morgan law 2 failed"
            );
        }
    }

    console.log("Boolean algebra laws verified.");
}


// ============================================================================
// 3. JAVASCRIPT TRUTHINESS
// ============================================================================

function demonstrateTruthiness() {
    console.log("\n=== JAVASCRIPT TRUTHINESS ===");

    /*
     * JavaScript conditions do not require an actual Boolean value.
     * Values such as 0, "", null, undefined, and NaN are falsy.
     * Objects and arrays are truthy, including empty arrays and objects.
     *
     * For security-sensitive or strict logical predicates, explicit Boolean
     * comparisons are often clearer than relying on implicit coercion.
     */

    const values = [
        false,
        true,
        0,
        1,
        "",
        "text",
        null,
        undefined,
        [],
        {},
        NaN
    ];

    for (const value of values) {
        console.log(
            `${String(value).padEnd(12)} -> Boolean(value) = ${Boolean(value)}`
        );
    }
}


// ============================================================================
// 4. PREDICATES
// ============================================================================

const isEven = (number) => number % 2 === 0;
const isPositive = (number) => number > 0;
const isAdult = (person) => person.age >= 18;

function canEnterLab(person) {
    /*
     * Predicate:
     *
     * valid age AND identity AND authorization
     */
    return (
        person.age >= 0 &&
        person.age <= 130 &&
        person.hasId === true &&
        person.authorized === true
    );
}

function demonstratePredicates() {
    console.log("\n=== PREDICATES ===");

    const numbers = [-2, 0, 3, 8, 11];

    for (const number of numbers) {
        console.log(
            `${number}: even=${isEven(number)}, positive=${isPositive(number)}`
        );
    }

    const people = [
        { age: 21, hasId: true, authorized: true },
        { age: 21, hasId: true, authorized: false },
        { age: 21, hasId: false, authorized: true },
        { age: -4, hasId: true, authorized: true }
    ];

    for (const person of people) {
        console.log(
            "Lab access:",
            canEnterLab(person)
        );
    }
}


// ============================================================================
// 5. QUANTIFIERS WITH ARRAY METHODS
// ============================================================================

function allSatisfy(values, predicate) {
    // Array.every corresponds conceptually to universal quantification.
    return values.every(predicate);
}

function anySatisfy(values, predicate) {
    // Array.some corresponds conceptually to existential quantification.
    return values.some(predicate);
}

function demonstrateQuantifiers() {
    console.log("\n=== QUANTIFIERS ===");

    const numbers = [2, 4, 6, 8];

    console.log(
        "All even:",
        allSatisfy(numbers, isEven)
    );

    console.log(
        "At least one positive:",
        anySatisfy([-5, -3, 2], isPositive)
    );

    console.log(
        "Every element in [] satisfies predicate:",
        allSatisfy([], isEven)
    );

    console.log(
        "Some element in [] satisfies predicate:",
        anySatisfy([], isEven)
    );
}


// ============================================================================
// 6. SHORT-CIRCUIT EVALUATION
// ============================================================================

function demonstrateShortCircuiting() {
    console.log("\n=== SHORT-CIRCUIT EVALUATION ===");

    let calls = 0;

    function expensiveCheck() {
        calls += 1;
        return true;
    }

    const first = false && expensiveCheck();
    const second = true || expensiveCheck();

    console.log("false && expensiveCheck():", first);
    console.log("true || expensiveCheck():", second);
    console.log("expensiveCheck calls:", calls);

    /*
     * The right-hand side was never evaluated.
     * This can improve performance but can also hide side effects.
     */
}


// ============================================================================
// 7. EXPRESSIONS AND OPERATOR PRECEDENCE
// ============================================================================

function demonstratePrecedence() {
    console.log("\n=== OPERATOR PRECEDENCE ===");

    const a = true;
    const b = false;
    const c = true;

    const grouped = (a && b) || c;
    const explicit = a && (b || c);

    console.log("(A AND B) OR C =", grouped);
    console.log("A AND (B OR C) =", explicit);

    /*
     * Parentheses make intended logic explicit and reduce maintenance errors.
     * Do not rely on a reader remembering every precedence rule.
     */
}


// ============================================================================
// 8. OBJECT-ORIENTED RULE ENGINE
// ============================================================================

class PredicateRule {
    constructor(name, predicate) {
        if (typeof name !== "string" || name.length === 0) {
            throw new TypeError("Rule name must be a non-empty string.");
        }

        if (typeof predicate !== "function") {
            throw new TypeError("Predicate must be a function.");
        }

        this.name = name;
        this.predicate = predicate;
    }

    evaluate(context) {
        return Boolean(this.predicate(context));
    }
}

class RuleEngine {
    constructor(rules) {
        if (!Array.isArray(rules)) {
            throw new TypeError("rules must be an array.");
        }

        this.rules = [...rules];
    }

    evaluate(context) {
        const results = {};

        for (const rule of this.rules) {
            results[rule.name] = rule.evaluate(context);
        }

        return results;
    }

    isAllowed(context) {
        const results = this.evaluate(context);
        return Object.values(results).every(Boolean);
    }
}

function demonstrateRuleEngine() {
    console.log("\n=== RULE ENGINE ===");

    const rules = [
        new PredicateRule(
            "identity verified",
            user => user.identityVerified === true
        ),
        new PredicateRule(
            "account active",
            user => user.accountActive === true
        ),
        new PredicateRule(
            "minimum age",
            user => user.age >= 18
        ),
        new PredicateRule(
            "security factor",
            user => (
                user.isAdmin === true ||
                user.hasMFA === true
            )
        )
    ];

    const engine = new RuleEngine(rules);

    const user = {
        age: 25,
        identityVerified: true,
        accountActive: true,
        isAdmin: false,
        hasMFA: true
    };

    console.log(engine.evaluate(user));
    console.log("Allowed:", engine.isAllowed(user));
}


// ============================================================================
// 9. DECISION TABLE
// ============================================================================

function shippingCost({ orderTotal, isMember, expedited }) {
    if (!Number.isFinite(orderTotal) || orderTotal < 0) {
        throw new RangeError("Order total must be a non-negative finite number.");
    }

    if (expedited === true) {
        return 15;
    }

    if (isMember === true && orderTotal >= 100) {
        return 0;
    }

    return 7.5;
}

function demonstrateDecisionTable() {
    console.log("\n=== DECISION TABLE ===");

    const cases = [
        { orderTotal: 120, isMember: true, expedited: false },
        { orderTotal: 80, isMember: true, expedited: false },
        { orderTotal: 120, isMember: false, expedited: false },
        { orderTotal: 120, isMember: true, expedited: true }
    ];

    for (const order of cases) {
        console.log(order, "=>", shippingCost(order));
    }
}


// ============================================================================
// 10. FUNCTIONAL LOGIC COMPOSITION
// ============================================================================

function allOf(...predicates) {
    return value => predicates.every(predicate => predicate(value));
}

function anyOf(...predicates) {
    return value => predicates.some(predicate => predicate(value));
}

function not(predicate) {
    return value => !predicate(value);
}

function demonstrateFunctionalComposition() {
    console.log("\n=== FUNCTIONAL PREDICATE COMPOSITION ===");

    const adult = person => person.age >= 18;
    const verified = person => person.verified;
    const blocked = person => person.blocked;

    const canUseService = allOf(
        adult,
        verified,
        not(blocked)
    );

    const people = [
        { age: 25, verified: true, blocked: false },
        { age: 17, verified: true, blocked: false },
        { age: 25, verified: false, blocked: false },
        { age: 25, verified: true, blocked: true }
    ];

    for (const person of people) {
        console.log(
            person,
            "=>",
            canUseService(person)
        );
    }

    const privileged = anyOf(
        person => person.isAdmin === true,
        person => person.isManager === true
    );

    console.log(
        "Privileged:",
        privileged({ isAdmin: false, isManager: true })
    );
}


// ============================================================================
// 11. ASSERTIONS AND CONTRACTS
// ============================================================================

function assertNumber(value, name) {
    if (typeof value !== "number" || !Number.isFinite(value)) {
        throw new TypeError(`${name} must be a finite number.`);
    }
}

function transferMoney(balance, amount) {
    /*
     * Preconditions are checked explicitly because JavaScript does not have
     * native language-level design-by-contract syntax.
     */
    assertNumber(balance, "balance");
    assertNumber(amount, "amount");

    if (balance < 0) {
        throw new RangeError("Balance cannot be negative.");
    }

    if (amount <= 0) {
        throw new RangeError("Amount must be positive.");
    }

    if (amount > balance) {
        throw new RangeError("Insufficient balance.");
    }

    const newBalance = balance - amount;

    // Postcondition:
    assert(newBalance >= 0, "Balance invariant was violated.");

    return newBalance;
}

function demonstrateContracts() {
    console.log("\n=== ASSERTIONS AND CONTRACTS ===");

    console.log(
        "Balance after transfer:",
        transferMoney(500, 125)
    );

    try {
        transferMoney(100, 200);
    } catch (error) {
        console.log("Expected error:", error.message);
    }
}


// ============================================================================
// 12. ASYNCHRONOUS VERIFICATION
// ============================================================================

function verifyAsync(operation, inputs) {
    /*
     * Promise-based verification models a situation where a predicate or
     * verification operation may depend on asynchronous work.
     */
    return Promise.all(
        inputs.map(async input => ({
            input,
            result: Boolean(await operation(input))
        }))
    );
}

async function demonstrateAsyncVerification() {
    console.log("\n=== ASYNCHRONOUS VERIFICATION ===");

    const results = await verifyAsync(
        async number => number % 2 === 0,
        [2, 3, 4, 5, 6]
    );

    console.table(results);

    const allPassed = results.every(item => item.result === true);
    console.log("All inputs passed:", allPassed);
}


// ============================================================================
// 13. EXHAUSTIVE BOOLEAN VERIFICATION
// ============================================================================

function booleanCombinations(inputCount) {
    const combinations = [];
    const total = 2 ** inputCount;

    for (let mask = 0; mask < total; mask += 1) {
        const inputs = [];

        for (let bit = inputCount - 1; bit >= 0; bit -= 1) {
            inputs.push(Boolean((mask >> bit) & 1));
        }

        combinations.push(inputs);
    }

    return combinations;
}

function verifyEquivalent(first, second, inputCount) {
    const failures = [];

    for (const inputs of booleanCombinations(inputCount)) {
        const actual = Boolean(first(...inputs));
        const expected = Boolean(second(...inputs));

        if (actual !== expected) {
            failures.push({
                inputs,
                actual,
                expected
            });
        }
    }

    return failures;
}

function demonstrateEquivalenceVerification() {
    console.log("\n=== EXHAUSTIVE EQUIVALENCE VERIFICATION ===");

    const failures = verifyEquivalent(
        (a, b) => !(a && b),
        (a, b) => !a || !b,
        2
    );

    console.log(
        "De Morgan equivalence:",
        failures.length === 0 ? "PASS" : "FAIL"
    );

    const incorrectFailures = verifyEquivalent(
        XOR,
        OR,
        2
    );

    console.log(
        "XOR versus OR equivalence:",
        incorrectFailures.length === 0 ? "PASS" : "FAIL"
    );

    if (incorrectFailures.length > 0) {
        console.log(
            "Counterexample:",
            incorrectFailures[0]
        );
    }
}


// ============================================================================
// 14. TRUTH TABLE GENERATION FOR ARBITRARY EXPRESSIONS
// ============================================================================

function truthTable(variableNames, expression) {
    return booleanCombinations(variableNames.length).map(inputs => {
        const environment = Object.fromEntries(
            variableNames.map((name, index) => [name, inputs[index]])
        );

        return {
            ...environment,
            result: Boolean(expression(environment))
        };
    });
}

function demonstrateExpressionTable() {
    console.log("\n=== EXPRESSION TRUTH TABLE ===");

    const table = truthTable(
        ["A", "B", "C"],
        ({ A, B, C }) => (A && B) || (!A && C)
    );

    console.table(table);
}


// ============================================================================
// 15. SECURITY-SENSITIVE LOGIC
// ============================================================================

function authorizeTransaction(transaction) {
    /*
     * Example:
     *
     * positive amount
     * AND verified identity
     * AND mature account
     * AND safe location
     * AND (trusted device OR low amount)
     *
     * Security decisions should be centralized, auditable, tested, and
     * validated against the intended policy rather than scattered through
     * unrelated application code.
     */
    const amountValid =
        Number.isFinite(transaction.amount) &&
        transaction.amount > 0;

    const matureAccount =
        transaction.accountAgeDays >= 30;

    const identityVerified =
        transaction.identityVerified === true;

    const safeLocation =
        transaction.suspiciousLocation !== true;

    const acceptableDeviceOrAmount =
        transaction.trustedDevice === true ||
        transaction.amount <= 1000;

    return (
        amountValid &&
        matureAccount &&
        identityVerified &&
        safeLocation &&
        acceptableDeviceOrAmount
    );
}

function explainTransaction(transaction) {
    return {
        amountValid:
            Number.isFinite(transaction.amount) &&
            transaction.amount > 0,

        matureAccount:
            transaction.accountAgeDays >= 30,

        identityVerified:
            transaction.identityVerified === true,

        safeLocation:
            transaction.suspiciousLocation !== true,

        acceptableDeviceOrAmount:
            transaction.trustedDevice === true ||
            transaction.amount <= 1000
    };
}

function demonstrateSecurityLogic() {
    console.log("\n=== SECURITY DECISION LOGIC ===");

    const transaction = {
        amount: 750,
        accountAgeDays: 180,
        identityVerified: true,
        suspiciousLocation: false,
        trustedDevice: false
    };

    console.log(explainTransaction(transaction));
    console.log("Authorized:", authorizeTransaction(transaction));
}


// ============================================================================
// 16. EDGE CASES
// ============================================================================

function demonstrateEdgeCases() {
    console.log("\n=== EDGE CASES ===");

    console.log("[] === true:", [] === true);
    console.log("Boolean([]):", Boolean([]));

    console.log("null == undefined:", null == undefined);
    console.log("null === undefined:", null === undefined);

    /*
     * Strict equality (===) avoids many implicit-conversion surprises.
     */
    console.log('"5" === 5:', "5" === 5);
    console.log('"5" == 5:', "5" == 5);

    /*
     * NaN is not equal to itself. Number.isNaN is the appropriate explicit
     * check for a NaN value.
     */
    console.log("NaN === NaN:", NaN === NaN);
    console.log("Number.isNaN(NaN):", Number.isNaN(NaN));
}


// ============================================================================
// 17. PROPERTY-STYLE TESTING
// ============================================================================

function verifyProperty(values, property, name) {
    const failures = [];

    for (const value of values) {
        if (!property(value)) {
            failures.push(value);
        }
    }

    return {
        name,
        passed: failures.length === 0,
        failures
    };
}

function demonstratePropertyTesting() {
    console.log("\n=== PROPERTY-STYLE TESTING ===");

    const values = Array.from({ length: 100 }, (_, index) => index);

    const result = verifyProperty(
        values,
        number => (
            number + 1 > number ||
            number === Number.MAX_SAFE_INTEGER
        ),
        "Monotonic increment over test range"
    );

    console.log(result);
}


// ============================================================================
// 18. PERFORMANCE CONSIDERATIONS
// ============================================================================

function performanceExample(iterations = 100000) {
    let count = 0;

    for (let index = 0; index < iterations; index += 1) {
        if (index % 2 === 0 && index % 3 === 0) {
            count += 1;
        }
    }

    return count;
}

function demonstratePerformance() {
    console.log("\n=== PERFORMANCE ===");

    console.log(
        "Matches:",
        performanceExample()
    );

    console.log("Single Boolean operation: approximately O(1)");
    console.log("Scanning n records: O(n) in the worst case");
    console.log("Truth table for n Boolean variables: O(2^n)");
}


// ============================================================================
// 19. CAPSTONE VERIFICATION
// ============================================================================

function runVerificationSuite() {
    console.log("\n=== CAPSTONE VERIFICATION SUITE ===");

    const tests = [
        {
            name: "AND",
            check: () => verifyEquivalent(
                AND,
                (a, b) => a && b,
                2
            ).length === 0
        },
        {
            name: "OR",
            check: () => verifyEquivalent(
                OR,
                (a, b) => a || b,
                2
            ).length === 0
        },
        {
            name: "XOR",
            check: () => verifyEquivalent(
                XOR,
                (a, b) => a !== b,
                2
            ).length === 0
        },
        {
            name: "NAND",
            check: () => verifyEquivalent(
                NAND,
                (a, b) => !(a && b),
                2
            ).length === 0
        },
        {
            name: "NOR",
            check: () => verifyEquivalent(
                NOR,
                (a, b) => !(a || b),
                2
            ).length === 0
        },
        {
            name: "XNOR",
            check: () => verifyEquivalent(
                XNOR,
                (a, b) => a === b,
                2
            ).length === 0
        },
        {
            name: "Implication",
            check: () => verifyEquivalent(
                implication,
                (p, q) => !p || q,
                2
            ).length === 0
        },
        {
            name: "De Morgan 1",
            check: () => verifyEquivalent(
                (a, b) => !(a && b),
                (a, b) => !a || !b,
                2
            ).length === 0
        },
        {
            name: "De Morgan 2",
            check: () => verifyEquivalent(
                (a, b) => !(a || b),
                (a, b) => !a && !b,
                2
            ).length === 0
        }
    ];

    let failures = 0;

    for (const test of tests) {
        try {
            if (test.check()) {
                console.log(`[PASS] ${test.name}`);
            } else {
                console.log(`[FAIL] ${test.name}`);
                failures += 1;
            }
        } catch (error) {
            console.log(`[ERROR] ${test.name}: ${error.message}`);
            failures += 1;
        }
    }

    console.log(`Tests: ${tests.length}`);
    console.log(`Failures: ${failures}`);

    assert(failures === 0, "Verification suite failed.");
}


// ============================================================================
// 20. MAIN
// ============================================================================

async function main() {
    console.log("=".repeat(78));
    console.log("LOGIC IN COMPUTING");
    console.log("Digital Logic | Predicates | Assertions | Verification");
    console.log("=".repeat(78));

    demonstrateGates();
    verifyBooleanLaws();
    demonstrateTruthiness();
    demonstratePredicates();
    demonstrateQuantifiers();
    demonstrateShortCircuiting();
    demonstratePrecedence();
    demonstrateRuleEngine();
    demonstrateDecisionTable();
    demonstrateFunctionalComposition();
    demonstrateContracts();
    await demonstrateAsyncVerification();
    demonstrateEquivalenceVerification();
    demonstrateExpressionTable();
    demonstrateSecurityLogic();
    demonstrateEdgeCases();
    demonstratePropertyTesting();
    demonstratePerformance();
    runVerificationSuite();

    console.log("\nJavaScript logic study completed successfully.");
}


main().catch(error => {
    console.error("Program failed:", error);
    process.exitCode = 1;
});
