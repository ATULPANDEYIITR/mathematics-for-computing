"use strict";

/*
 * Predicate Logic:
 * Predicates, Quantifiers, Universal Quantification,
 * and Existential Quantification
 *
 * This file demonstrates finite-domain predicate logic using JavaScript.
 * The implementation progresses from simple predicates to nested
 * quantifiers, logical equivalences, relations, rule systems, and a
 * small formula evaluator.
 */

// -----------------------------------------------------------------------------
// 1. Propositions and logical connectives
// -----------------------------------------------------------------------------

function logicalNot(value) {
    return !value;
}

function logicalAnd(left, right) {
    return left && right;
}

function logicalOr(left, right) {
    return left || right;
}

function logicalImplies(antecedent, consequent) {
    // P -> Q is equivalent to !P || Q.
    return !antecedent || consequent;
}

function logicalIff(left, right) {
    return left === right;
}

// -----------------------------------------------------------------------------
// 2. Predicates
// -----------------------------------------------------------------------------

function isEven(number) {
    return number % 2 === 0;
}

function isPositive(number) {
    return number > 0;
}

function isPrime(number) {
    if (number < 2) {
        return false;
    }

    for (let divisor = 2; divisor * divisor <= number; divisor += 1) {
        if (number % divisor === 0) {
            return false;
        }
    }

    return true;
}

function lessThan(left, right) {
    return left < right;
}

// A binary relation represented as a predicate.
function knows(personA, personB) {
    const relationships = new Set([
        "Alice|Bob",
        "Bob|Carol",
        "Carol|Alice"
    ]);

    return relationships.has(`${personA}|${personB}`);
}

// -----------------------------------------------------------------------------
// 3. Universal and existential quantification
// -----------------------------------------------------------------------------

function forall(domain, predicate) {
    /*
     * JavaScript Array.prototype.every() naturally models:
     *
     *     ∀x P(x)
     *
     * over a finite domain.
     *
     * It also short-circuits when it encounters a counterexample.
     */
    return domain.every(predicate);
}

function exists(domain, predicate) {
    /*
     * JavaScript Array.prototype.some() naturally models:
     *
     *     ∃x P(x)
     *
     * It short-circuits as soon as a witness is found.
     */
    return domain.some(predicate);
}

function findCounterexample(domain, predicate) {
    return domain.find((item) => !predicate(item));
}

function findWitness(domain, predicate) {
    return domain.find(predicate);
}

// -----------------------------------------------------------------------------
// 4. Nested quantifiers
// -----------------------------------------------------------------------------

function forallExists(outerDomain, innerDomain, predicate) {
    /*
     * ∀x ∃y P(x,y)
     *
     * For every x, at least one y must satisfy P.
     */
    return outerDomain.every((x) =>
        innerDomain.some((y) => predicate(x, y))
    );
}

function existsForall(outerDomain, innerDomain, predicate) {
    /*
     * ∃x ∀y P(x,y)
     *
     * There must be one x for which P(x,y) is true for every y.
     */
    return outerDomain.some((x) =>
        innerDomain.every((y) => predicate(x, y))
    );
}

// -----------------------------------------------------------------------------
// 5. Pair and triple evaluation
// -----------------------------------------------------------------------------

function forallPairs(domain, relation) {
    for (const first of domain) {
        for (const second of domain) {
            if (!relation(first, second)) {
                return false;
            }
        }
    }

    return true;
}

function existsPair(domain, relation) {
    for (const first of domain) {
        for (const second of domain) {
            if (relation(first, second)) {
                return true;
            }
        }
    }

    return false;
}

// -----------------------------------------------------------------------------
// 6. English-style examples
// -----------------------------------------------------------------------------

function demonstrateEnglishTranslation() {
    console.log("\n=== English-to-Predicate-Logic Translation ===");

    const people = ["Alice", "Bob", "Carol", "David"];

    const employed = new Set(["Alice", "Bob", "David"]);
    const qualified = new Set(["Alice", "Carol", "David"]);

    const isEmployed = (person) => employed.has(person);
    const isQualified = (person) => qualified.has(person);

    // "Everyone is employed."
    console.log(
        "Everyone is employed:",
        forall(people, isEmployed)
    );

    // "Someone is qualified."
    console.log(
        "Someone is qualified:",
        exists(people, isQualified)
    );

    // "Everyone who is qualified is employed."
    console.log(
        "Every qualified person is employed:",
        forall(
            people,
            (person) => logicalImplies(
                isQualified(person),
                isEmployed(person)
            )
        )
    );
}

// -----------------------------------------------------------------------------
// 7. Domain dependence and vacuous truth
// -----------------------------------------------------------------------------

function demonstrateDomains() {
    console.log("\n=== Domains and Vacuous Truth ===");

    const positiveNumbers = [2, 4, 6, 8];
    const mixedNumbers = [-2, -1, 0, 1, 2];
    const emptyDomain = [];

    console.log(
        "∀x Positive(x) over positive numbers:",
        forall(positiveNumbers, isPositive)
    );

    console.log(
        "∀x Positive(x) over mixed numbers:",
        forall(mixedNumbers, isPositive)
    );

    // Universal statements over an empty finite domain are true.
    console.log(
        "∀x Prime(x) over empty domain:",
        forall(emptyDomain, isPrime)
    );

    // Existential statements over an empty domain are false.
    console.log(
        "∃x Prime(x) over empty domain:",
        exists(emptyDomain, isPrime)
    );
}

// -----------------------------------------------------------------------------
// 8. Negating quantifiers
// -----------------------------------------------------------------------------

function demonstrateQuantifierNegation() {
    console.log("\n=== Negating Quantifiers ===");

    const domain = [1, 2, 3, 4];

    const notForAll = logicalNot(
        forall(domain, isEven)
    );

    const existsNot = exists(
        domain,
        (number) => logicalNot(isEven(number))
    );

    console.log("¬∀x Even(x):", notForAll);
    console.log("∃x ¬Even(x):", existsNot);
    console.log("Equivalent:", notForAll === existsNot);

    const notExists = logicalNot(
        exists(domain, isEven)
    );

    const forallNot = forall(
        domain,
        (number) => logicalNot(isEven(number))
    );

    console.log("¬∃x Even(x):", notExists);
    console.log("∀x ¬Even(x):", forallNot);
    console.log("Equivalent:", notExists === forallNot);
}

// -----------------------------------------------------------------------------
// 9. Quantifier order
// -----------------------------------------------------------------------------

function demonstrateQuantifierOrder() {
    console.log("\n=== Quantifier Order ===");

    const numbers = [1, 2, 3, 4];

    const forallExistsResult = forallExists(
        numbers,
        numbers,
        (x, y) => x <= y
    );

    const existsForallResult = existsForall(
        numbers,
        numbers,
        (x, y) => x <= y
    );

    console.log(
        "∀x∃y (x <= y):",
        forallExistsResult
    );

    console.log(
        "∃x∀y (x <= y):",
        existsForallResult
    );

    console.log(
        "The different results demonstrate that quantifier order matters."
    );
}

// -----------------------------------------------------------------------------
// 10. Witnesses and counterexamples
// -----------------------------------------------------------------------------

function demonstrateEvidence() {
    console.log("\n=== Witnesses and Counterexamples ===");

    const domain = [1, 3, 5, 8, 10];

    const witness = findWitness(domain, isEven);
    const counterexample = findCounterexample(domain, isEven);

    console.log("Witness for ∃x Even(x):", witness);
    console.log("Counterexample to ∀x Even(x):", counterexample);
}

// -----------------------------------------------------------------------------
// 11. Relations and relation properties
// -----------------------------------------------------------------------------

function isReflexive(domain, relation) {
    return domain.every((item) => relation(item, item));
}

function isSymmetric(domain, relation) {
    for (const x of domain) {
        for (const y of domain) {
            if (relation(x, y) && !relation(y, x)) {
                return false;
            }
        }
    }

    return true;
}

function isTransitive(domain, relation) {
    for (const x of domain) {
        for (const y of domain) {
            for (const z of domain) {
                if (
                    relation(x, y) &&
                    relation(y, z) &&
                    !relation(x, z)
                ) {
                    return false;
                }
            }
        }
    }

    return true;
}

function demonstrateRelations() {
    console.log("\n=== Relations ===");

    const domain = [1, 2, 3];

    const equality = (x, y) => x === y;

    console.log(
        "Equality is reflexive:",
        isReflexive(domain, equality)
    );

    console.log(
        "Equality is symmetric:",
        isSymmetric(domain, equality)
    );

    console.log(
        "Equality is transitive:",
        isTransitive(domain, equality)
    );

    console.log(
        "∃x∃y (x < y):",
        existsPair(domain, lessThan)
    );

    console.log(
        "∀x∀y (x < y):",
        forallPairs(domain, lessThan)
    );
}

// -----------------------------------------------------------------------------
// 12. Formula objects
// -----------------------------------------------------------------------------

class Formula {
    evaluate(_assignment) {
        throw new Error("Formula.evaluate must be implemented.");
    }
}

class PredicateFormula extends Formula {
    constructor(name, predicate, variables) {
        super();
        this.name = name;
        this.predicate = predicate;
        this.variables = variables;
    }

    evaluate(assignment) {
        const argumentsForPredicate = this.variables.map(
            (variable) => assignment[variable]
        );

        return Boolean(
            this.predicate(...argumentsForPredicate)
        );
    }
}

class NotFormula extends Formula {
    constructor(formula) {
        super();
        this.formula = formula;
    }

    evaluate(assignment) {
        return !this.formula.evaluate(assignment);
    }
}

class AndFormula extends Formula {
    constructor(left, right) {
        super();
        this.left = left;
        this.right = right;
    }

    evaluate(assignment) {
        return (
            this.left.evaluate(assignment) &&
            this.right.evaluate(assignment)
        );
    }
}

class OrFormula extends Formula {
    constructor(left, right) {
        super();
        this.left = left;
        this.right = right;
    }

    evaluate(assignment) {
        return (
            this.left.evaluate(assignment) ||
            this.right.evaluate(assignment)
        );
    }
}

class ImpliesFormula extends Formula {
    constructor(left, right) {
        super();
        this.left = left;
        this.right = right;
    }

    evaluate(assignment) {
        return logicalImplies(
            this.left.evaluate(assignment),
            this.right.evaluate(assignment)
        );
    }
}

class UniversalFormula extends Formula {
    constructor(variable, domain, body) {
        super();
        this.variable = variable;
        this.domain = domain;
        this.body = body;
    }

    evaluate(assignment) {
        for (const value of this.domain) {
            const extendedAssignment = {
                ...assignment,
                [this.variable]: value
            };

            if (!this.body.evaluate(extendedAssignment)) {
                return false;
            }
        }

        return true;
    }
}

class ExistentialFormula extends Formula {
    constructor(variable, domain, body) {
        super();
        this.variable = variable;
        this.domain = domain;
        this.body = body;
    }

    evaluate(assignment) {
        for (const value of this.domain) {
            const extendedAssignment = {
                ...assignment,
                [this.variable]: value
            };

            if (this.body.evaluate(extendedAssignment)) {
                return true;
            }
        }

        return false;
    }
}

function demonstrateFormulaObjects() {
    console.log("\n=== Formula Objects ===");

    const domain = [1, 2, 3, 4, 5];

    const evenX = new PredicateFormula(
        "Even",
        isEven,
        ["x"]
    );

    const positiveX = new PredicateFormula(
        "Positive",
        isPositive,
        ["x"]
    );

    const formula = new UniversalFormula(
        "x",
        domain,
        new ImpliesFormula(
            evenX,
            positiveX
        )
    );

    console.log(
        "∀x (Even(x) -> Positive(x)):",
        formula.evaluate({})
    );
}

// -----------------------------------------------------------------------------
// 13. Practical authorization case study
// -----------------------------------------------------------------------------

class AccessRequest {
    constructor(
        user,
        role,
        resource,
        authenticated,
        active
    ) {
        this.user = user;
        this.role = role;
        this.resource = resource;
        this.authenticated = authenticated;
        this.active = active;
    }
}

function canAccess(request) {
    /*
     * Simplified rule:
     *
     * Authenticated(x) AND Active(x) AND Admin(x)
     * -> AccessGranted(x)
     */
    return (
        request.authenticated &&
        request.active &&
        request.role === "admin"
    );
}

function demonstrateAuthorization() {
    console.log("\n=== Authorization Case Study ===");

    const requests = [
        new AccessRequest(
            "Alice",
            "admin",
            "database",
            true,
            true
        ),
        new AccessRequest(
            "Bob",
            "user",
            "database",
            true,
            true
        ),
        new AccessRequest(
            "Carol",
            "admin",
            "database",
            true,
            false
        )
    ];

    for (const request of requests) {
        console.log(
            request.user,
            "access granted:",
            canAccess(request)
        );
    }
}

// -----------------------------------------------------------------------------
// 14. Employee model
// -----------------------------------------------------------------------------

class Employee {
    constructor(
        employeeId,
        name,
        department,
        age,
        active,
        trained,
        securityClearance
    ) {
        this.employeeId = employeeId;
        this.name = name;
        this.department = department;
        this.age = age;
        this.active = active;
        this.trained = trained;
        this.securityClearance = securityClearance;
    }
}

function isAdult(employee) {
    return employee.age >= 18;
}

function canEnterSecureArea(employee) {
    return (
        employee.active &&
        employee.trained &&
        employee.securityClearance >= 2 &&
        isAdult(employee)
    );
}

function demonstrateEmployeeCaseStudy() {
    console.log("\n=== Employee Predicate Logic Case Study ===");

    const employees = [
        new Employee(
            101,
            "Alice",
            "Security",
            31,
            true,
            true,
            3
        ),
        new Employee(
            102,
            "Bob",
            "Finance",
            29,
            true,
            false,
            1
        ),
        new Employee(
            103,
            "Carol",
            "Engineering",
            17,
            false,
            true,
            2
        ),
        new Employee(
            104,
            "David",
            "Security",
            44,
            true,
            true,
            2
        )
    ];

    console.log(
        "∀x Adult(x):",
        forall(employees, isAdult)
    );

    console.log(
        "∃x CanEnterSecureArea(x):",
        exists(employees, canEnterSecureArea)
    );

    const violatingEmployee = employees.find(
        (employee) =>
            employee.trained &&
            !employee.active
    );

    console.log(
        "Counterexample to ∀x(Trained(x) -> Active(x)):",
        violatingEmployee
            ? violatingEmployee.name
            : null
    );
}

// -----------------------------------------------------------------------------
// 15. Logical equivalence tests
// -----------------------------------------------------------------------------

function verifyLogicalLaws() {
    console.log("\n=== Logical Law Tests ===");

    const domain = [-5, -2, -1, 0, 1, 2, 4];

    const doubleNegation = forall(
        domain,
        (x) => logicalNot(logicalNot(isEven(x))) === isEven(x)
    );

    const implicationEquivalence = forall(
        domain,
        (x) => {
            const first = logicalImplies(
                isEven(x),
                isPositive(x)
            );

            const second =
                logicalNot(isEven(x)) ||
                isPositive(x);

            return first === second;
        }
    );

    const quantifierNegation = (
        logicalNot(forall(domain, isEven))
        === exists(
            domain,
            (x) => logicalNot(isEven(x))
        )
    );

    console.log(
        "Double negation:",
        doubleNegation
    );

    console.log(
        "Implication equivalence:",
        implicationEquivalence
    );

    console.log(
        "¬∀x P(x) == ∃x ¬P(x):",
        quantifierNegation
    );

    if (
        !doubleNegation ||
        !implicationEquivalence ||
        !quantifierNegation
    ) {
        throw new Error(
            "One or more logical equivalence tests failed."
        );
    }
}

// -----------------------------------------------------------------------------
// 16. Complexity demonstration
// -----------------------------------------------------------------------------

function unaryChecks(domainSize) {
    return domainSize;
}

function binaryChecks(domainSize) {
    return domainSize ** 2;
}

function ternaryChecks(domainSize) {
    return domainSize ** 3;
}

function demonstrateComplexity() {
    console.log("\n=== Complexity ===");

    const n = 100;

    console.log("Unary quantification checks:", unaryChecks(n));
    console.log("Binary nested checks:", binaryChecks(n));
    console.log("Ternary nested checks:", ternaryChecks(n));

    console.log(
        "Direct evaluation of k nested quantifiers can require O(n^k) checks."
    );
}

// -----------------------------------------------------------------------------
// 17. Common mistakes
// -----------------------------------------------------------------------------

function demonstrateCommonMistakes() {
    console.log("\n=== Common Mistakes ===");

    const domain = [1, 2, 3, 4];

    console.log(
        "∀x Even(x):",
        forall(domain, isEven)
    );

    console.log(
        "∃x Even(x):",
        exists(domain, isEven)
    );

    const incorrectNegation = forall(
        domain,
        (x) => !isEven(x)
    );

    const correctNegation = exists(
        domain,
        (x) => !isEven(x)
    );

    console.log(
        "Incorrect attempt at ¬∀x Even(x):",
        incorrectNegation
    );

    console.log(
        "Correct ∃x ¬Even(x):",
        correctNegation
    );

    const first = forallExists(
        domain,
        domain,
        (x, y) => x <= y
    );

    const second = existsForall(
        domain,
        domain,
        (x, y) => x <= y
    );

    console.log("∀x∃y (x <= y):", first);
    console.log("∃x∀y (x <= y):", second);
}

// -----------------------------------------------------------------------------
// 18. Main
// -----------------------------------------------------------------------------

function main() {
    console.log("=".repeat(72));
    console.log("PREDICATE LOGIC STUDY PROGRAM");
    console.log("=".repeat(72));

    console.log("\n=== Basic Predicates ===");
    console.log("Even(4):", isEven(4));
    console.log("Even(5):", isEven(5));
    console.log("Prime(7):", isPrime(7));
    console.log("Prime(8):", isPrime(8));
    console.log("LessThan(3, 8):", lessThan(3, 8));
    console.log("Knows(Alice, Bob):", knows("Alice", "Bob"));
    console.log("Knows(Alice, Carol):", knows("Alice", "Carol"));

    demonstrateEnglishTranslation();
    demonstrateDomains();
    demonstrateQuantifierNegation();
    demonstrateQuantifierOrder();
    demonstrateEvidence();
    demonstrateRelations();
    demonstrateFormulaObjects();
    demonstrateAuthorization();
    demonstrateEmployeeCaseStudy();
    verifyLogicalLaws();
    demonstrateComplexity();
    demonstrateCommonMistakes();

    console.log("\n" + "=".repeat(72));
    console.log("All JavaScript predicate-logic demonstrations completed.");
    console.log("=".repeat(72));
}

main();
