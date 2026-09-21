"use strict";

/*
 * Quantifier Logic
 * =================
 *
 * This self-contained JavaScript program demonstrates:
 *
 * - Universal quantification
 * - Existential quantification
 * - Nested quantifiers
 * - Quantifier order
 * - Negation of quantified statements
 * - Natural-language translation
 * - Scope and variable binding
 * - Witnesses and counterexamples
 * - Vacuous truth
 * - Relations over finite domains
 * - Database-style reasoning
 * - Logical equivalence testing
 * - Practical specification patterns
 * - Performance considerations
 *
 * JavaScript does not provide native first-order quantifier syntax.
 * This program therefore models finite-domain quantifiers using functions,
 * arrays, sets, objects, and executable predicates.
 */


// ============================================================================
// SECTION 1: DISPLAY HELPERS
// ============================================================================

function section(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function subsection(title) {
    console.log("\n" + "-".repeat(78));
    console.log(title);
    console.log("-".repeat(78));
}

function explain(text) {
    console.log(text.trim());
}


// ============================================================================
// SECTION 2: BASIC QUANTIFIERS
// ============================================================================

function forall(domain, predicate) {
    // Array.every() naturally implements universal quantification:
    // ∀x P(x) is true exactly when every domain element satisfies P.
    return domain.every(predicate);
}

function exists(domain, predicate) {
    // Array.some() naturally implements existential quantification:
    // ∃x P(x) is true when at least one domain element satisfies P.
    return domain.some(predicate);
}

function demoBasicQuantifiers() {
    section("1. Universal and existential quantifiers");

    const numbers = [-2, -1, 0, 1, 2, 3];

    console.log("Domain:", numbers);
    console.log("∀x (x < 10):", forall(numbers, x => x < 10));
    console.log("∀x (x > 0):", forall(numbers, x => x > 0));
    console.log("∃x (x === 3):", exists(numbers, x => x === 3));
    console.log("∃x (x > 100):", exists(numbers, x => x > 100));

    explain(`
Universal quantification requires every domain object to satisfy a predicate.

Existential quantification requires at least one domain object to satisfy it.

The finite JavaScript equivalents are:

    domain.every(predicate)
    domain.some(predicate)

Both methods short-circuit. every() stops after finding a false result,
while some() stops after finding a true result.
`);
}


// ============================================================================
// SECTION 3: RESTRICTED UNIVERSAL STATEMENTS
// ============================================================================

function demoRestrictedUniversal() {
    section("2. Restricted universal statements");

    const people = [
        { name: "Alice", student: true, age: 20 },
        { name: "Bob", student: false, age: 30 },
        { name: "Carol", student: true, age: 22 },
        { name: "David", student: true, age: 17 }
    ];

    // "Every student is an adult":
    //
    // ∀x (Student(x) → Adult(x))
    //
    // In JavaScript, implication P → Q can be written as !P || Q.
    const everyStudentIsAdult = forall(
        people,
        person => !person.student || person.age >= 18
    );

    console.log("Every student is an adult:", everyStudentIsAdult);

    // "Some student is an adult":
    //
    // ∃x (Student(x) ∧ Adult(x))
    const someStudentIsAdult = exists(
        people,
        person => person.student && person.age >= 18
    );

    console.log("Some student is an adult:", someStudentIsAdult);

    explain(`
The distinction between implication and conjunction is important.

"Every student is an adult" means:

    ∀x (Student(x) → Adult(x))

It does not require non-students to be adults.

"Some student is an adult" means:

    ∃x (Student(x) ∧ Adult(x))

The same object must satisfy both conditions.
`);
}


// ============================================================================
// SECTION 4: TRANSLATING NATURAL LANGUAGE
// ============================================================================

function demoTranslation() {
    section("3. Natural-language translation");

    const translations = [
        {
            sentence: "Every programmer knows Python.",
            logic: "∀x (Programmer(x) → Knows(x, Python))"
        },
        {
            sentence: "Some programmer knows Python.",
            logic: "∃x (Programmer(x) ∧ Knows(x, Python))"
        },
        {
            sentence: "No programmer knows Python.",
            logic: "∀x (Programmer(x) → ¬Knows(x, Python))"
        },
        {
            sentence: "Some programmer does not know Python.",
            logic: "∃x (Programmer(x) ∧ ¬Knows(x, Python))"
        },
        {
            sentence: "Every student knows some language.",
            logic: "∀x (Student(x) → ∃y (Language(y) ∧ Knows(x,y)))"
        },
        {
            sentence: "There is a language known by every student.",
            logic: "∃y (Language(y) ∧ ∀x (Student(x) → Knows(x,y)))"
        }
    ];

    for (const item of translations) {
        console.log(`\n${item.sentence}`);
        console.log(`  ${item.logic}`);
    }
}


// ============================================================================
// SECTION 5: NESTED QUANTIFIERS
// ============================================================================

function demoNestedQuantifiers() {
    section("4. Nested quantifiers");

    const students = ["Alice", "Bob", "Carol"];
    const subjects = ["Math", "Physics", "Programming"];

    const passed = new Set([
        "Alice|Math",
        "Alice|Programming",
        "Bob|Physics",
        "Carol|Math",
        "Carol|Physics",
        "Carol|Programming"
    ]);

    const passedCourse = (student, subject) =>
        passed.has(`${student}|${subject}`);

    // ∀student ∃subject Passed(student, subject)
    const everyStudentPassedSomeSubject = forall(
        students,
        student => exists(
            subjects,
            subject => passedCourse(student, subject)
        )
    );

    // ∃subject ∀student Passed(student, subject)
    const someSubjectPassedByEveryone = exists(
        subjects,
        subject => forall(
            students,
            student => passedCourse(student, subject)
        )
    );

    console.log(
        "∀student ∃subject Passed(student, subject):",
        everyStudentPassedSomeSubject
    );

    console.log(
        "∃subject ∀student Passed(student, subject):",
        someSubjectPassedByEveryone
    );

    explain(`
These formulas are not generally equivalent.

∀x ∃y R(x,y)
means each x may have its own y.

∃y ∀x R(x,y)
requires one y that works for every x.

The order therefore represents dependency.
`);
}


// ============================================================================
// SECTION 6: QUANTIFIER NEGATION
// ============================================================================

function negateForall(domain, predicate) {
    // ¬∀x P(x) ≡ ∃x ¬P(x)
    return exists(domain, item => !predicate(item));
}

function negateExists(domain, predicate) {
    // ¬∃x P(x) ≡ ∀x ¬P(x)
    return forall(domain, item => !predicate(item));
}

function demoNegation() {
    section("5. Negating quantified statements");

    const numbers = [1, 2, 3, 4, 5];

    const allLessThanTen = forall(numbers, x => x < 10);
    const notAllLessThanTen = negateForall(numbers, x => x < 10);

    const someGreaterThanThree = exists(numbers, x => x > 3);
    const noneGreaterThanThree = negateExists(numbers, x => x > 3);

    console.log("∀x (x < 10):", allLessThanTen);
    console.log("¬∀x (x < 10):", notAllLessThanTen);
    console.log("∃x (x > 3):", someGreaterThanThree);
    console.log("¬∃x (x > 3):", noneGreaterThanThree);

    explain(`
The two fundamental quantifier-negation rules are:

    ¬∀x P(x) ≡ ∃x ¬P(x)
    ¬∃x P(x) ≡ ∀x ¬P(x)

For nested quantifiers, apply the rule repeatedly.

Example:

    ¬∀x ∃y R(x,y)

becomes:

    ∃x ∀y ¬R(x,y)
`);
}


// ============================================================================
// SECTION 7: NATURAL-LANGUAGE NEGATION
// ============================================================================

function demoNaturalLanguageNegation() {
    section("6. Negating natural-language statements");

    const examples = [
        {
            original: "Every student passed.",
            formula: "∀x (Student(x) → Passed(x))",
            negation: "∃x (Student(x) ∧ ¬Passed(x))"
        },
        {
            original: "Some student passed.",
            formula: "∃x (Student(x) ∧ Passed(x))",
            negation: "∀x (Student(x) → ¬Passed(x))"
        },
        {
            original: "Every student knows some language.",
            formula: "∀x (Student(x) → ∃y (Language(y) ∧ Knows(x,y)))",
            negation: "∃x (Student(x) ∧ ∀y (Language(y) → ¬Knows(x,y)))"
        }
    ];

    for (const example of examples) {
        console.log(`\nOriginal: ${example.original}`);
        console.log(`Formula:  ${example.formula}`);
        console.log(`Negation: ${example.negation}`);
    }
}


// ============================================================================
// SECTION 8: QUANTIFIER ORDER
// ============================================================================

function demoQuantifierOrder() {
    section("7. Quantifier order and dependency");

    const employees = ["Alice", "Bob", "Carol"];
    const projects = ["P1", "P2"];

    const assignments = new Set([
        "Alice|P1",
        "Bob|P2",
        "Carol|P1"
    ]);

    const assigned = (employee, project) =>
        assignments.has(`${employee}|${project}`);

    const eachEmployeeHasSomeProject = forall(
        employees,
        employee => exists(
            projects,
            project => assigned(employee, project)
        )
    );

    const oneProjectHasEveryone = exists(
        projects,
        project => forall(
            employees,
            employee => assigned(employee, project)
        )
    );

    console.log(
        "∀employee ∃project Assigned(employee, project):",
        eachEmployeeHasSomeProject
    );

    console.log(
        "∃project ∀employee Assigned(employee, project):",
        oneProjectHasEveryone
    );
}


// ============================================================================
// SECTION 9: VACUOUS TRUTH
// ============================================================================

function demoVacuousTruth() {
    section("8. Vacuous truth");

    const emptyDomain = [];

    console.log(
        "∀x P(x) over empty domain:",
        forall(emptyDomain, x => x > 0)
    );

    console.log(
        "∃x P(x) over empty domain:",
        exists(emptyDomain, x => x > 0)
    );

    explain(`
For a standard finite-domain implementation:

    ∀x P(x)

is true over an empty domain because there is no counterexample.

    ∃x P(x)

is false because there is no witness.

This behavior is called vacuous truth for universal statements.
`);
}


// ============================================================================
// SECTION 10: WITNESSES AND COUNTEREXAMPLES
// ============================================================================

function findWitness(domain, predicate) {
    for (const item of domain) {
        if (predicate(item)) {
            return item;
        }
    }

    return undefined;
}

function findCounterexample(domain, predicate) {
    for (const item of domain) {
        if (!predicate(item)) {
            return item;
        }
    }

    return undefined;
}

function demoWitnesses() {
    section("9. Witnesses and counterexamples");

    const values = [2, 4, 6, 7, 8];

    const witness = findWitness(values, x => x % 2 === 0);
    const counterexample = findCounterexample(values, x => x % 2 === 0);

    console.log("Witness for ∃x Even(x):", witness);
    console.log("Counterexample to ∀x Even(x):", counterexample);

    explain(`
A witness proves an existential statement over a finite domain.

A counterexample disproves a universal statement.

These concepts are particularly useful for testing specifications because a
single violating input can disprove a universal requirement.
`);
}


// ============================================================================
// SECTION 11: RELATIONAL QUANTIFICATION
// ============================================================================

function demoRelations() {
    section("10. Binary predicates and relationships");

    const people = ["Alice", "Bob", "Carol", "David"];

    const knows = new Set([
        "Alice|Bob",
        "Alice|Carol",
        "Bob|Carol",
        "Carol|Alice",
        "David|Alice"
    ]);

    const knowsPerson = (person, other) =>
        knows.has(`${person}|${other}`);

    const everyoneKnowsSomeoneElse = forall(
        people,
        person => exists(
            people,
            other => person !== other && knowsPerson(person, other)
        )
    );

    const someoneIsKnownByEveryone = exists(
        people,
        target => forall(
            people,
            person => person === target || knowsPerson(person, target)
        )
    );

    console.log(
        "Everyone knows someone else:",
        everyoneKnowsSomeoneElse
    );

    console.log(
        "Someone is known by everyone:",
        someoneIsKnownByEveryone
    );
}


// ============================================================================
// SECTION 12: SMALL FORMULA OBJECT MODEL
// ============================================================================

class Formula {
    evaluate(environment = {}) {
        throw new Error("Formula.evaluate() must be implemented.");
    }
}

class Predicate extends Formula {
    constructor(name, evaluator, variables) {
        super();
        this.name = name;
        this.evaluator = evaluator;
        this.variables = variables;
    }

    evaluate(environment = {}) {
        const values = this.variables.map(variable => environment[variable]);
        return Boolean(this.evaluator(...values));
    }
}

class Not extends Formula {
    constructor(operand) {
        super();
        this.operand = operand;
    }

    evaluate(environment = {}) {
        return !this.operand.evaluate(environment);
    }
}

class And extends Formula {
    constructor(left, right) {
        super();
        this.left = left;
        this.right = right;
    }

    evaluate(environment = {}) {
        return (
            this.left.evaluate(environment) &&
            this.right.evaluate(environment)
        );
    }
}

class Or extends Formula {
    constructor(left, right) {
        super();
        this.left = left;
        this.right = right;
    }

    evaluate(environment = {}) {
        return (
            this.left.evaluate(environment) ||
            this.right.evaluate(environment)
        );
    }
}

class Implies extends Formula {
    constructor(antecedent, consequent) {
        super();
        this.antecedent = antecedent;
        this.consequent = consequent;
    }

    evaluate(environment = {}) {
        return (
            !this.antecedent.evaluate(environment) ||
            this.consequent.evaluate(environment)
        );
    }
}

class ForAll extends Formula {
    constructor(variable, domain, body) {
        super();
        this.variable = variable;
        this.domain = domain;
        this.body = body;
    }

    evaluate(environment = {}) {
        for (const value of this.domain) {
            const extendedEnvironment = {
                ...environment,
                [this.variable]: value
            };

            if (!this.body.evaluate(extendedEnvironment)) {
                return false;
            }
        }

        return true;
    }
}

class Exists extends Formula {
    constructor(variable, domain, body) {
        super();
        this.variable = variable;
        this.domain = domain;
        this.body = body;
    }

    evaluate(environment = {}) {
        for (const value of this.domain) {
            const extendedEnvironment = {
                ...environment,
                [this.variable]: value
            };

            if (this.body.evaluate(extendedEnvironment)) {
                return true;
            }
        }

        return false;
    }
}

function demoFormulaObjects() {
    section("11. Formula objects and semantic evaluation");

    const domain = [1, 2, 3, 4, 5];

    const positive = new Predicate(
        "Positive",
        x => x > 0,
        ["x"]
    );

    const lessThanTen = new Predicate(
        "LessThanTen",
        x => x < 10,
        ["x"]
    );

    const formula = new ForAll(
        "x",
        domain,
        new And(positive, lessThanTen)
    );

    console.log(
        "Formula: ∀x (Positive(x) ∧ LessThanTen(x))"
    );

    console.log(
        "Evaluation:",
        formula.evaluate()
    );

    explain(`
This object model separates formula structure from evaluation.

A larger logic engine could add parsing, symbolic substitution, formula
normalization, proof rules, unification, or satisfiability procedures.
`);
}


// ============================================================================
// SECTION 13: DATABASE-STYLE QUERIES
// ============================================================================

function demoDatabaseQueries() {
    section("12. Database-style quantified queries");

    const customers = ["Alice", "Bob", "Carol"];
    const products = ["Laptop", "Phone", "Tablet"];

    const purchases = new Set([
        "Alice|Laptop",
        "Alice|Phone",
        "Bob|Phone",
        "Carol|Tablet",
        "Carol|Phone"
    ]);

    const purchased = (customer, product) =>
        purchases.has(`${customer}|${product}`);

    const customersWithPurchase = customers.filter(
        customer => exists(
            products,
            product => purchased(customer, product)
        )
    );

    const customersWhoBoughtEverything = customers.filter(
        customer => forall(
            products,
            product => purchased(customer, product)
        )
    );

    const productsBoughtByEveryone = products.filter(
        product => forall(
            customers,
            customer => purchased(customer, product)
        )
    );

    console.log(
        "Customers with at least one purchase:",
        customersWithPurchase
    );

    console.log(
        "Customers who bought every product:",
        customersWhoBoughtEverything
    );

    console.log(
        "Products bought by every customer:",
        productsBoughtByEveryone
    );

    explain(`
The patterns correspond closely to database queries.

EXISTS corresponds naturally to existential filtering.

A universal condition can often be represented by every(), while a negated
universal can be represented through some().

This is also why NOT EXISTS is a common technique in relational querying.
`);
}


// ============================================================================
// SECTION 14: ADVANCED NEGATION
// ============================================================================

function nestedAuthorizationFormula(users, resources, authorized) {
    // ∀u ∃r Authorized(u,r)
    return forall(
        users,
        user => exists(
            resources,
            resource => authorized.has(`${user}|${resource}`)
        )
    );
}

function directNegationOfNestedAuthorization(
    users,
    resources,
    authorized
) {
    // Negation:
    //
    // ¬∀u ∃r Authorized(u,r)
    //
    // ≡ ∃u ∀r ¬Authorized(u,r)
    return exists(
        users,
        user => forall(
            resources,
            resource => !authorized.has(`${user}|${resource}`)
        )
    );
}

function demoNestedNegation() {
    section("13. Negating nested quantifiers");

    const users = ["Alice", "Bob", "Carol"];
    const resources = ["Database", "Server"];

    const authorized = new Set([
        "Alice|Database",
        "Bob|Server"
    ]);

    const original = nestedAuthorizationFormula(
        users,
        resources,
        authorized
    );

    const directNegation = directNegationOfNestedAuthorization(
        users,
        resources,
        authorized
    );

    console.log("Original formula:", original);
    console.log("Direct transformed negation:", directNegation);
    console.log("JavaScript !original:", !original);

    if (directNegation !== !original) {
        throw new Error(
            "Nested quantifier negation implementation is inconsistent."
        );
    }
}


// ============================================================================
// SECTION 15: LOGICAL EQUIVALENCE TESTING
// ============================================================================

function formulasAgree(domain, first, second) {
    return first(domain) === second(domain);
}

function demoEquivalenceTesting() {
    section("14. Testing quantifier equivalences");

    const domains = [
        [],
        [0],
        [1, 2, 3],
        [-2, -1, 0, 1, 2]
    ];

    const predicates = [
        x => x > 0,
        x => x % 2 === 0,
        x => x === 42
    ];

    for (const domain of domains) {
        for (const predicate of predicates) {
            const left = !forall(domain, predicate);
            const right = exists(domain, x => !predicate(x));

            if (left !== right) {
                throw new Error(
                    "Quantifier-negation equivalence failed."
                );
            }
        }
    }

    console.log(
        "All finite-domain tests for ¬∀P ≡ ∃¬P passed."
    );

    explain(`
Finite-domain testing can detect counterexamples to claimed equivalences.

It does not prove equivalence for all possible domains, but it is an effective
debugging technique for an implementation.
`);
}


// ============================================================================
// SECTION 16: PERFORMANCE
// ============================================================================

function quantifiedPairSearch(outerDomain, innerDomain, relation) {
    /*
     * Evaluates:
     *
     *     ∀x ∃y R(x,y)
     *
     * Worst-case complexity is O(n*m), where n and m are domain sizes.
     * Short-circuiting can reduce actual work.
     */
    for (const x of outerDomain) {
        let found = false;

        for (const y of innerDomain) {
            if (relation(x, y)) {
                found = true;
                break;
            }
        }

        if (!found) {
            return false;
        }
    }

    return true;
}

function demoPerformance() {
    section("15. Performance considerations");

    const users = Array.from({ length: 100 }, (_, index) => index + 1);
    const resources = Array.from({ length: 100 }, (_, index) => index + 1);

    const result = quantifiedPairSearch(
        users,
        resources,
        (user, resource) => user === resource
    );

    console.log(
        "∀user ∃resource resource === user:",
        result
    );

    explain(`
Nested quantifiers can create multiplicative work.

A direct evaluation of:

    ∀x ∃y R(x,y)

may inspect O(|X| × |Y|) pairs.

A Set or Map can provide indexing when the relation is stored explicitly.
That can substantially improve practical performance.
`);
}


// ============================================================================
// SECTION 17: PRACTICAL SECURITY SPECIFICATION
// ============================================================================

function demoSecuritySpecification() {
    section("16. Security policy specification");

    const users = ["Alice", "Bob", "Carol"];
    const resources = ["database", "server", "reports"];

    const permissions = new Set([
        "Alice|database",
        "Alice|reports",
        "Bob|reports",
        "Carol|database",
        "Carol|server"
    ]);

    const approvedPermissions = permissions;

    // Requirement:
    //
    // ∀u ∃r HasPermission(u,r)
    const everyUserHasPermission = forall(
        users,
        user => exists(
            resources,
            resource => approvedPermissions.has(
                `${user}|${resource}`
            )
        )
    );

    // Requirement:
    //
    // ∀u∀r Access(u,r) → Authorized(u,r)
    //
    // For this finite model, each recorded access is checked against policy.
    const accesses = [
        ["Alice", "database"],
        ["Bob", "reports"]
    ];

    const allRecordedAccessesAuthorized = accesses.every(
        ([user, resource]) =>
            approvedPermissions.has(`${user}|${resource}`)
    );

    console.log(
        "Every user has at least one permission:",
        everyUserHasPermission
    );

    console.log(
        "Every recorded access is authorized:",
        allRecordedAccessesAuthorized
    );

    explain(`
A logical security specification must be precise about what it guarantees.

"Every user has at least one permission" does not imply that users are
restricted to authorized resources.

A separate property is needed for authorization safety.

Formal specifications are useful only when implementation checks enforce the
properties they state.
`);
}


// ============================================================================
// SECTION 18: EDGE CASES
// ============================================================================

function demoEdgeCases() {
    section("17. Edge cases");

    const empty = [];
    const singleton = [5];

    console.log(
        "∀x(x === 5), empty domain:",
        forall(empty, x => x === 5)
    );

    console.log(
        "∃x(x === 5), empty domain:",
        exists(empty, x => x === 5)
    );

    console.log(
        "∀x(x === 5), singleton domain:",
        forall(singleton, x => x === 5)
    );

    console.log(
        "∃x(x === 5), singleton domain:",
        exists(singleton, x => x === 5)
    );

    explain(`
Important implementation edge cases include:

- Empty arrays.
- Singleton arrays.
- Predicates that always return true.
- Predicates that always return false.
- Duplicate values.
- Nested quantifiers over empty inner domains.
- Missing relation pairs.
- Relations containing every possible pair.
`);
}


// ============================================================================
// SECTION 19: PRACTICAL COURSE CASE STUDY
// ============================================================================

function demoCourseCaseStudy() {
    section("18. Course-management case study");

    const students = ["Alice", "Bob", "Carol", "David"];
    const courses = ["Math", "Physics", "Programming"];

    const enrollments = new Set([
        "Alice|Math",
        "Alice|Programming",
        "Bob|Physics",
        "Carol|Math",
        "Carol|Physics",
        "Carol|Programming",
        "David|Programming"
    ]);

    const passed = new Set([
        "Alice|Math",
        "Alice|Programming",
        "Bob|Physics",
        "Carol|Math",
        "Carol|Physics"
    ]);

    const enrolled = (student, course) =>
        enrollments.has(`${student}|${course}`);

    const passedCourse = (student, course) =>
        passed.has(`${student}|${course}`);

    // ∀s ∃c Enrolled(s,c)
    const everyoneIsEnrolled = forall(
        students,
        student => exists(
            courses,
            course => enrolled(student, course)
        )
    );

    // ∀s ∃c Passed(s,c)
    const everyonePassedAtLeastOne = forall(
        students,
        student => exists(
            courses,
            course => passedCourse(student, course)
        )
    );

    // ∃c ∀s Passed(s,c)
    const oneCoursePassedByEveryone = exists(
        courses,
        course => forall(
            students,
            student => passedCourse(student, course)
        )
    );

    const studentWithoutPass = findWitness(
        students,
        student => !exists(
            courses,
            course => passedCourse(student, course)
        )
    );

    console.log("Everyone is enrolled:", everyoneIsEnrolled);
    console.log(
        "Everyone passed at least one course:",
        everyonePassedAtLeastOne
    );
    console.log(
        "One course was passed by everyone:",
        oneCoursePassedByEveryone
    );
    console.log(
        "Student with no passed course:",
        studentWithoutPass
    );

    explain(`
The same quantified formulas can be used as executable validation rules.

The negation of:

    ∀s ∃c Passed(s,c)

is:

    ∃s ∀c ¬Passed(s,c)

The program can therefore locate the violating student directly.
`);
}


// ============================================================================
// SECTION 20: TESTS
// ============================================================================

function runTests() {
    section("19. Executable tests");

    const domains = [
        [],
        [0],
        [1, 2, 3],
        [-2, -1, 0, 1, 2]
    ];

    const predicates = [
        x => x > 0,
        x => x % 2 === 0,
        x => x === 42
    ];

    for (const domain of domains) {
        for (const predicate of predicates) {
            console.assert(
                !forall(domain, predicate) ===
                exists(domain, x => !predicate(x)),
                "Failed ¬∀P ≡ ∃¬P test"
            );

            console.assert(
                !exists(domain, predicate) ===
                forall(domain, x => !predicate(x)),
                "Failed ¬∃P ≡ ∀¬P test"
            );
        }
    }

    console.log("All automated tests completed successfully.");
}


// ============================================================================
// MAIN
// ============================================================================

function main() {
    section("Quantifier Logic: JavaScript Study Program");

    demoBasicQuantifiers();
    demoRestrictedUniversal();
    demoTranslation();
    demoNestedQuantifiers();
    demoNegation();
    demoNaturalLanguageNegation();
    demoQuantifierOrder();
    demoVacuousTruth();
    demoWitnesses();
    demoRelations();
    demoFormulaObjects();
    demoDatabaseQueries();
    demoNestedNegation();
    demoEquivalenceTesting();
    demoPerformance();
    demoSecuritySpecification();
    demoEdgeCases();
    demoCourseCaseStudy();
    runTests();

    section("Program complete");
    console.log(
        "Quantifier logic demonstrations completed successfully."
    );
}

main();
