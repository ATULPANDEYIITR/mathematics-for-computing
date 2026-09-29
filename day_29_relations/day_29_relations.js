/*
 * Relations: Binary Relations and Relation Properties
 * ====================================================
 *
 * A self-contained JavaScript study program covering:
 *
 * - Ordered pairs and Cartesian products
 * - Binary relations
 * - Domain and range
 * - Relation representations
 * - Reflexive, irreflexive, symmetric, antisymmetric, asymmetric,
 *   and transitive relations
 * - Equivalence relations
 * - Partial orders
 * - Inverse relations
 * - Composition
 * - Relation powers
 * - Reflexive, symmetric, and transitive closures
 * - Warshall's algorithm
 * - Practical applications
 * - Validation, edge cases, and performance
 *
 * Run with:
 *     node relations.js
 */

"use strict";

// -----------------------------------------------------------------------------
// 1. Cartesian products and relation construction
// -----------------------------------------------------------------------------

function cartesianProduct(left, right) {
    const result = [];

    for (const a of left) {
        for (const b of right) {
            result.push([a, b]);
        }
    }

    return result;
}

function pairKey(a, b) {
    // JSON encoding prevents collisions for many ordinary JavaScript values.
    return JSON.stringify([a, b]);
}

function relationFromPairs(pairs) {
    const relation = new Map();

    for (const [a, b] of pairs) {
        if (!Array.isArray([a, b])) {
            throw new TypeError("A relation pair must contain two elements.");
        }

        relation.set(pairKey(a, b), [a, b]);
    }

    return relation;
}

function relationPairs(relation) {
    return [...relation.values()];
}

function hasPair(relation, a, b) {
    return relation.has(pairKey(a, b));
}

function validateRelation(relation, domain, codomain) {
    const domainSet = new Set(domain);
    const codomainSet = new Set(codomain);

    for (const [a, b] of relationPairs(relation)) {
        if (!domainSet.has(a) || !codomainSet.has(b)) {
            throw new Error(
                `Invalid pair (${String(a)}, ${String(b)}): ` +
                "outside domain x codomain."
            );
        }
    }

    return true;
}

function relationDomain(relation) {
    return new Set(relationPairs(relation).map(([a]) => a));
}

function relationRange(relation) {
    return new Set(relationPairs(relation).map(([, b]) => b));
}


// -----------------------------------------------------------------------------
// 2. Core properties
// -----------------------------------------------------------------------------

function isReflexive(relation, universe) {
    return universe.every(element => hasPair(relation, element, element));
}

function isIrreflexive(relation, universe) {
    return universe.every(element => !hasPair(relation, element, element));
}

function isSymmetric(relation) {
    for (const [a, b] of relationPairs(relation)) {
        if (!hasPair(relation, b, a)) {
            return false;
        }
    }

    return true;
}

function isAntisymmetric(relation) {
    for (const [a, b] of relationPairs(relation)) {
        if (a !== b && hasPair(relation, b, a)) {
            return false;
        }
    }

    return true;
}

function isAsymmetric(relation) {
    for (const [a, b] of relationPairs(relation)) {
        if (hasPair(relation, b, a)) {
            return false;
        }
    }

    return true;
}

function isTransitive(relation) {
    const pairs = relationPairs(relation);

    for (const [a, b] of pairs) {
        for (const [x, c] of pairs) {
            if (Object.is(b, x) && !hasPair(relation, a, c)) {
                return false;
            }
        }
    }

    return true;
}

function isConnected(relation, universe) {
    for (const a of universe) {
        for (const b of universe) {
            if (
                a !== b &&
                !hasPair(relation, a, b) &&
                !hasPair(relation, b, a)
            ) {
                return false;
            }
        }
    }

    return true;
}

function propertyReport(relation, universe) {
    return {
        reflexive: isReflexive(relation, universe),
        irreflexive: isIrreflexive(relation, universe),
        symmetric: isSymmetric(relation),
        antisymmetric: isAntisymmetric(relation),
        asymmetric: isAsymmetric(relation),
        transitive: isTransitive(relation),
        connected: isConnected(relation, universe)
    };
}


// -----------------------------------------------------------------------------
// 3. Relation transformations
// -----------------------------------------------------------------------------

function inverseRelation(relation) {
    const result = new Map();

    for (const [a, b] of relationPairs(relation)) {
        result.set(pairKey(b, a), [b, a]);
    }

    return result;
}

function composeRelations(first, second) {
    /*
     * Returns second o first.
     *
     * If a R1 b and b R2 c, then a (R2 o R1) c.
     */
    const result = new Map();
    const secondPairs = relationPairs(second);

    for (const [a, b] of relationPairs(first)) {
        for (const [x, c] of secondPairs) {
            if (Object.is(b, x)) {
                result.set(pairKey(a, c), [a, c]);
            }
        }
    }

    return result;
}

function relationPower(relation, exponent) {
    if (!Number.isInteger(exponent) || exponent < 1) {
        throw new RangeError("Relation powers require a positive integer.");
    }

    let result = new Map(relation);

    for (let i = 1; i < exponent; i++) {
        result = composeRelations(result, relation);
    }

    return result;
}


// -----------------------------------------------------------------------------
// 4. Closures
// -----------------------------------------------------------------------------

function reflexiveClosure(relation, universe) {
    const result = new Map(relation);

    for (const element of universe) {
        result.set(pairKey(element, element), [element, element]);
    }

    return result;
}

function symmetricClosure(relation) {
    const result = new Map(relation);

    for (const [a, b] of relationPairs(relation)) {
        result.set(pairKey(b, a), [b, a]);
    }

    return result;
}

function transitiveClosure(relation) {
    /*
     * Repeatedly add (a,c) whenever (a,b) and (b,c) exist.
     * For finite relations this terminates at the smallest transitive
     * relation containing the original relation.
     */
    const closure = new Map(relation);

    let changed = true;

    while (changed) {
        changed = false;

        const currentPairs = relationPairs(closure);
        const additions = [];

        for (const [a, b] of currentPairs) {
            for (const [x, c] of currentPairs) {
                if (Object.is(b, x) && !hasPair(closure, a, c)) {
                    additions.push([a, c]);
                }
            }
        }

        for (const [a, c] of additions) {
            const key = pairKey(a, c);

            if (!closure.has(key)) {
                closure.set(key, [a, c]);
                changed = true;
            }
        }
    }

    return closure;
}

function warshallTransitiveClosure(relation, elements) {
    /*
     * Warshall's algorithm:
     *
     * reachable[i][j] becomes true when a path exists from i to j.
     *
     * Time: O(n^3)
     * Space: O(n^2)
     */
    const n = elements.length;
    const index = new Map(
        elements.map((element, i) => [element, i])
    );

    const reachable = Array.from(
        { length: n },
        () => Array(n).fill(false)
    );

    for (const [a, b] of relationPairs(relation)) {
        reachable[index.get(a)][index.get(b)] = true;
    }

    for (let k = 0; k < n; k++) {
        for (let i = 0; i < n; i++) {
            if (!reachable[i][k]) {
                continue;
            }

            for (let j = 0; j < n; j++) {
                reachable[i][j] =
                    reachable[i][j] ||
                    reachable[k][j];
            }
        }
    }

    const result = new Map();

    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
            if (reachable[i][j]) {
                result.set(
                    pairKey(elements[i], elements[j]),
                    [elements[i], elements[j]]
                );
            }
        }
    }

    return result;
}


// -----------------------------------------------------------------------------
// 5. Mathematical classifications
// -----------------------------------------------------------------------------

function isEquivalenceRelation(relation, universe) {
    return (
        isReflexive(relation, universe) &&
        isSymmetric(relation) &&
        isTransitive(relation)
    );
}

function isPartialOrder(relation, universe) {
    return (
        isReflexive(relation, universe) &&
        isAntisymmetric(relation) &&
        isTransitive(relation)
    );
}

function equivalenceClass(relation, element, universe) {
    if (!isEquivalenceRelation(relation, universe)) {
        throw new Error(
            "Equivalence classes require an equivalence relation."
        );
    }

    return universe.filter(
        other => hasPair(relation, element, other)
    );
}

function equivalenceClasses(relation, universe) {
    if (!isEquivalenceRelation(relation, universe)) {
        throw new Error(
            "Equivalence classes require an equivalence relation."
        );
    }

    const remaining = new Set(universe);
    const classes = [];

    while (remaining.size > 0) {
        const representative = remaining.values().next().value;
        const currentClass = equivalenceClass(
            relation,
            representative,
            universe
        );

        classes.push(currentClass);

        for (const element of currentClass) {
            remaining.delete(element);
        }
    }

    return classes;
}


// -----------------------------------------------------------------------------
// 6. Relations defined by rules
// -----------------------------------------------------------------------------

function relationByRule(universe, predicate) {
    const result = new Map();

    for (const a of universe) {
        for (const b of universe) {
            if (predicate(a, b)) {
                result.set(pairKey(a, b), [a, b]);
            }
        }
    }

    return result;
}

function lessThanRelation(universe) {
    return relationByRule(universe, (a, b) => a < b);
}

function lessEqualRelation(universe) {
    return relationByRule(universe, (a, b) => a <= b);
}

function dividesRelation(universe) {
    return relationByRule(
        universe,
        (a, b) => b % a === 0
    );
}

function congruentModuloRelation(universe, modulus) {
    if (!Number.isInteger(modulus) || modulus <= 0) {
        throw new RangeError("Modulus must be a positive integer.");
    }

    return relationByRule(
        universe,
        (a, b) => ((a - b) % modulus + modulus) % modulus === 0
    );
}


// -----------------------------------------------------------------------------
// 7. Counterexamples
// -----------------------------------------------------------------------------

function reflexivityCounterexample(relation, universe) {
    for (const element of universe) {
        if (!hasPair(relation, element, element)) {
            return [element, element];
        }
    }

    return null;
}

function symmetryCounterexample(relation) {
    for (const [a, b] of relationPairs(relation)) {
        if (!hasPair(relation, b, a)) {
            return [a, b];
        }
    }

    return null;
}

function antisymmetryCounterexample(relation) {
    for (const [a, b] of relationPairs(relation)) {
        if (a !== b && hasPair(relation, b, a)) {
            return [a, b];
        }
    }

    return null;
}

function transitivityCounterexample(relation) {
    const pairs = relationPairs(relation);

    for (const [a, b] of pairs) {
        for (const [x, c] of pairs) {
            if (Object.is(b, x) && !hasPair(relation, a, c)) {
                return [a, b, c];
            }
        }
    }

    return null;
}


// -----------------------------------------------------------------------------
// 8. Matrix representation
// -----------------------------------------------------------------------------

function relationMatrix(relation, elements) {
    return elements.map(
        a => elements.map(
            b => hasPair(relation, a, b) ? 1 : 0
        )
    );
}

function printMatrix(relation, elements) {
    console.log(
        "     " +
        elements.map(element => String(element).padStart(4)).join(" ")
    );

    console.log(
        "     " +
        "-".repeat(elements.length * 5)
    );

    const matrix = relationMatrix(relation, elements);

    matrix.forEach((row, index) => {
        console.log(
            String(elements[index]).padStart(4) +
            " | " +
            row.map(value => String(value).padStart(4)).join(" ")
        );
    });
}


// -----------------------------------------------------------------------------
// 9. Demonstration
// -----------------------------------------------------------------------------

function printProperties(name, relation, universe) {
    console.log(`\n${name}`);
    console.log("-".repeat(name.length));

    console.log(
        "Relation:",
        relationPairs(relation)
    );

    const report = propertyReport(relation, universe);

    for (const [property, value] of Object.entries(report)) {
        console.log(
            `${property.padStart(14)}: ${value}`
        );
    }
}

function main() {
    console.log("=".repeat(78));
    console.log("BINARY RELATIONS AND RELATION PROPERTIES");
    console.log("=".repeat(78));

    // -------------------------------------------------------------------------
    // Ordered pairs and Cartesian products
    // -------------------------------------------------------------------------

    console.log("\n1. ORDERED PAIRS AND CARTESIAN PRODUCTS");
    console.log("---------------------------------------");

    const A = [1, 2, 3];
    const B = ["x", "y"];

    const AxB = cartesianProduct(A, B);

    console.log("A =", A);
    console.log("B =", B);
    console.log("A x B =", AxB);
    console.log("(1, 'x') belongs to A x B:", AxB.some(
        ([a, b]) => a === 1 && b === "x"
    ));

    console.log(
        "(1, 2) === (2, 1):",
        JSON.stringify([1, 2]) === JSON.stringify([2, 1])
    );

    // -------------------------------------------------------------------------
    // Binary relation
    // -------------------------------------------------------------------------

    console.log("\n2. BINARY RELATION");
    console.log("------------------");

    const universe = [1, 2, 3];

    const R = relationFromPairs([
        [1, 1],
        [1, 2],
        [2, 2],
        [2, 3],
        [3, 3]
    ]);

    validateRelation(R, universe, universe);

    console.log("Universe =", universe);
    console.log("R =", relationPairs(R));
    console.log(
        "Domain(R) =",
        [...relationDomain(R)]
    );
    console.log(
        "Range(R) =",
        [...relationRange(R)]
    );

    // -------------------------------------------------------------------------
    // Matrix representation
    // -------------------------------------------------------------------------

    console.log("\n3. MATRIX REPRESENTATION");
    console.log("-------------------------");

    printMatrix(R, universe);

    // -------------------------------------------------------------------------
    // Property classification
    // -------------------------------------------------------------------------

    console.log("\n4. PROPERTY CLASSIFICATION");
    console.log("---------------------------");

    printProperties("Example R", R, universe);

    console.log(
        "\nTransitivity counterexample:",
        transitivityCounterexample(R)
    );

    // -------------------------------------------------------------------------
    // Standard relations
    // -------------------------------------------------------------------------

    console.log("\n5. STANDARD MATHEMATICAL RELATIONS");
    console.log("----------------------------------");

    const lessThan = lessThanRelation(universe);
    const lessEqual = lessEqualRelation(universe);

    printProperties("< relation", lessThan, universe);
    printProperties("<= relation", lessEqual, universe);

    const divisibilityUniverse = [1, 2, 3, 4, 6, 12];
    const divides = dividesRelation(divisibilityUniverse);

    printProperties(
        "Divisibility relation",
        divides,
        divisibilityUniverse
    );

    console.log(
        "\nDivisibility is a partial order:",
        isPartialOrder(divides, divisibilityUniverse)
    );

    console.log(
        "Divisibility is connected:",
        isConnected(divides, divisibilityUniverse)
    );

    // -------------------------------------------------------------------------
    // Equivalence relation
    // -------------------------------------------------------------------------

    console.log("\n6. EQUIVALENCE RELATION");
    console.log("-----------------------");

    const moduloUniverse = [0, 1, 2, 3, 4, 5, 6, 7];
    const moduloThree = congruentModuloRelation(
        moduloUniverse,
        3
    );

    printProperties(
        "Congruence modulo 3",
        moduloThree,
        moduloUniverse
    );

    console.log(
        "Is equivalence relation:",
        isEquivalenceRelation(moduloThree, moduloUniverse)
    );

    console.log(
        "Equivalence classes:",
        equivalenceClasses(moduloThree, moduloUniverse)
    );

    // -------------------------------------------------------------------------
    // Inverse and composition
    // -------------------------------------------------------------------------

    console.log("\n7. INVERSE RELATION");
    console.log("-------------------");

    const directed = relationFromPairs([
        ["A", "B"],
        ["B", "C"],
        ["C", "A"]
    ]);

    console.log("R =", relationPairs(directed));
    console.log(
        "R^-1 =",
        relationPairs(inverseRelation(directed))
    );

    console.log("\n8. RELATION COMPOSITION");
    console.log("-----------------------");

    const skills = relationFromPairs([
        ["Alice", "Python"],
        ["Bob", "C++"],
        ["Carol", "Python"]
    ]);

    const skillCategories = relationFromPairs([
        ["Python", "Programming"],
        ["C++", "Programming"]
    ]);

    console.log(
        "R1 =",
        relationPairs(skills)
    );

    console.log(
        "R2 =",
        relationPairs(skillCategories)
    );

    console.log(
        "R2 o R1 =",
        relationPairs(
            composeRelations(skills, skillCategories)
        )
    );

    // -------------------------------------------------------------------------
    // Powers and paths
    // -------------------------------------------------------------------------

    console.log("\n9. RELATION POWERS");
    console.log("------------------");

    const graph = relationFromPairs([
        ["A", "B"],
        ["B", "C"],
        ["C", "D"]
    ]);

    console.log("R =", relationPairs(graph));
    console.log("R^2 =", relationPairs(
        relationPower(graph, 2)
    ));
    console.log("R^3 =", relationPairs(
        relationPower(graph, 3)
    ));

    // -------------------------------------------------------------------------
    // Closures
    // -------------------------------------------------------------------------

    console.log("\n10. CLOSURES");
    console.log("------------");

    const incomplete = relationFromPairs([
        [1, 2],
        [2, 3]
    ]);

    console.log(
        "Original:",
        relationPairs(incomplete)
    );

    console.log(
        "Reflexive closure:",
        relationPairs(
            reflexiveClosure(incomplete, universe)
        )
    );

    console.log(
        "Symmetric closure:",
        relationPairs(
            symmetricClosure(incomplete)
        )
    );

    console.log(
        "Transitive closure:",
        relationPairs(
            transitiveClosure(incomplete)
        )
    );

    // -------------------------------------------------------------------------
    // Warshall's algorithm
    // -------------------------------------------------------------------------

    console.log("\n11. WARSHALL'S ALGORITHM");
    console.log("-----------------------");

    const repeatedClosure = transitiveClosure(incomplete);

    const warshallClosure = warshallTransitiveClosure(
        incomplete,
        universe
    );

    const repeatedKeys = new Set(
        relationPairs(repeatedClosure).map(
            ([a, b]) => pairKey(a, b)
        )
    );

    const warshallKeys = new Set(
        relationPairs(warshallClosure).map(
            ([a, b]) => pairKey(a, b)
        )
    );

    console.log(
        "Repeated closure:",
        relationPairs(repeatedClosure)
    );

    console.log(
        "Warshall closure:",
        relationPairs(warshallClosure)
    );

    console.log(
        "Both methods agree:",
        repeatedKeys.size === warshallKeys.size &&
        [...repeatedKeys].every(key => warshallKeys.has(key))
    );

    // -------------------------------------------------------------------------
    // Edge cases
    // -------------------------------------------------------------------------

    console.log("\n12. EDGE CASES");
    console.log("--------------");

    const emptyRelation = new Map();

    console.log(
        "Empty relation reflexive on [1,2,3]:",
        isReflexive(emptyRelation, universe)
    );

    console.log(
        "Empty relation symmetric:",
        isSymmetric(emptyRelation)
    );

    console.log(
        "Empty relation antisymmetric:",
        isAntisymmetric(emptyRelation)
    );

    console.log(
        "Empty relation transitive:",
        isTransitive(emptyRelation)
    );

    const identity = relationFromPairs(
        universe.map(x => [x, x])
    );

    printProperties(
        "Identity relation",
        identity,
        universe
    );

    // -------------------------------------------------------------------------
    // Practical application: authorization
    // -------------------------------------------------------------------------

    console.log("\n13. PRACTICAL APPLICATION: ACCESS CONTROL");
    console.log("------------------------------------------");

    const users = ["Alice", "Bob", "Carol"];
    const resources = [
        "Database",
        "Reports",
        "Dashboard"
    ];

    const access = relationFromPairs([
        ["Alice", "Database"],
        ["Alice", "Reports"],
        ["Bob", "Reports"],
        ["Carol", "Dashboard"]
    ]);

    validateRelation(access, users, resources);

    console.log("Users:", users);
    console.log("Resources:", resources);
    console.log("Access relation:", relationPairs(access));

    console.log(
        "Alice -> Database:",
        hasPair(access, "Alice", "Database")
    );

    console.log(
        "Bob -> Dashboard:",
        hasPair(access, "Bob", "Dashboard")
    );

    // -------------------------------------------------------------------------
    // Practical application: prerequisite graph
    // -------------------------------------------------------------------------

    console.log("\n14. PRACTICAL APPLICATION: PREREQUISITES");
    console.log("-----------------------------------------");

    const prerequisites = relationFromPairs([
        ["Programming", "Data Structures"],
        ["Data Structures", "Algorithms"],
        ["Algorithms", "Machine Learning"]
    ]);

    const dependencyClosure = transitiveClosure(prerequisites);

    console.log(
        "Direct dependencies:",
        relationPairs(prerequisites)
    );

    console.log(
        "Transitive dependencies:",
        relationPairs(dependencyClosure)
    );

    // -------------------------------------------------------------------------
    // Assertions
    // -------------------------------------------------------------------------

    console.log("\n15. EXECUTABLE MATHEMATICAL ASSERTIONS");
    console.log("---------------------------------------");

    console.assert(
        isReflexive(identity, universe),
        "Identity should be reflexive."
    );

    console.assert(
        isSymmetric(identity),
        "Identity should be symmetric."
    );

    console.assert(
        isAntisymmetric(identity),
        "Identity should be antisymmetric."
    );

    console.assert(
        isTransitive(identity),
        "Identity should be transitive."
    );

    console.assert(
        isIrreflexive(lessThan, universe),
        "< should be irreflexive."
    );

    console.assert(
        isAsymmetric(lessThan),
        "< should be asymmetric."
    );

    console.assert(
        isTransitive(lessThan),
        "< should be transitive."
    );

    console.assert(
        isPartialOrder(lessEqual, universe),
        "<= should be a partial order."
    );

    console.assert(
        isEquivalenceRelation(moduloThree, moduloUniverse),
        "Congruence modulo 3 should be an equivalence relation."
    );

    console.log("All assertions passed.");

    // -------------------------------------------------------------------------
    // Performance notes
    // -------------------------------------------------------------------------

    console.log("\n16. PERFORMANCE CONSIDERATIONS");
    console.log("------------------------------");

    console.log(
        "A relation on n elements can contain up to n^2 ordered pairs."
    );

    console.log(
        "Reflexivity checking is O(n) with efficient membership."
    );

    console.log(
        "Symmetry and antisymmetry checking are O(|R|) on average."
    );

    console.log(
        "The straightforward transitivity implementation can be O(|R|^2)."
    );

    console.log(
        "Warshall's algorithm uses O(n^3) time and O(n^2) space."
    );

    console.log("\n" + "=".repeat(78));
    console.log("END OF RELATION STUDY");
    console.log("=".repeat(78));
}

main();
