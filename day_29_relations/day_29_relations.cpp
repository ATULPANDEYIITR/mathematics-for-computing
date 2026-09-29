/*
 * Relations: Binary Relations and Relation Properties
 * ====================================================
 *
 * Complete C++17 case study:
 *
 * A prerequisite and authorization relationship engine for a small
 * enterprise learning platform.
 *
 * The program demonstrates:
 *   - ordered pairs
 *   - binary relations
 *   - reflexivity
 *   - irreflexivity
 *   - symmetry
 *   - antisymmetry
 *   - asymmetry
 *   - transitivity
 *   - relation composition
 *   - inverse relations
 *   - reflexive/symmetric/transitive closures
 *   - equivalence relations
 *   - partial orders
 *   - reachability
 *   - Warshall's algorithm
 *   - validation
 *   - complexity considerations
 *
 * Compile:
 *     g++ -std=c++17 -O2 relations.cpp -o relations
 *
 * Run:
 *     ./relations
 */

#include <algorithm>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

using namespace std;

using Pair = pair<string, string>;
using Relation = set<Pair>;
using Universe = set<string>;


// -----------------------------------------------------------------------------
// Utility functions
// -----------------------------------------------------------------------------

void printRelation(const Relation& relation) {
    cout << "{";

    bool first = true;

    for (const auto& [a, b] : relation) {
        if (!first) {
            cout << ", ";
        }

        cout << "(" << a << ", " << b << ")";
        first = false;
    }

    cout << "}";
}

void validateRelation(
    const Relation& relation,
    const Universe& domain,
    const Universe& codomain
) {
    for (const auto& [a, b] : relation) {
        if (!domain.contains(a) || !codomain.contains(b)) {
            throw invalid_argument(
                "Relation contains a pair outside domain x codomain."
            );
        }
    }
}

Relation cartesianProduct(
    const Universe& left,
    const Universe& right
) {
    Relation result;

    for (const auto& a : left) {
        for (const auto& b : right) {
            result.insert({a, b});
        }
    }

    return result;
}


// -----------------------------------------------------------------------------
// Relation properties
// -----------------------------------------------------------------------------

bool isReflexive(
    const Relation& relation,
    const Universe& universe
) {
    for (const auto& element : universe) {
        if (!relation.contains({element, element})) {
            return false;
        }
    }

    return true;
}

bool isIrreflexive(
    const Relation& relation,
    const Universe& universe
) {
    for (const auto& element : universe) {
        if (relation.contains({element, element})) {
            return false;
        }
    }

    return true;
}

bool isSymmetric(const Relation& relation) {
    for (const auto& [a, b] : relation) {
        if (!relation.contains({b, a})) {
            return false;
        }
    }

    return true;
}

bool isAntisymmetric(const Relation& relation) {
    for (const auto& [a, b] : relation) {
        if (a != b && relation.contains({b, a})) {
            return false;
        }
    }

    return true;
}

bool isAsymmetric(const Relation& relation) {
    for (const auto& [a, b] : relation) {
        if (relation.contains({b, a})) {
            return false;
        }
    }

    return true;
}

bool isTransitive(const Relation& relation) {
    /*
     * For every aRb and bRc, require aRc.
     *
     * This direct implementation examines pairs of pairs and is therefore
     * O(|R|^2) in the worst case.
     */
    for (const auto& [a, b] : relation) {
        for (const auto& [x, c] : relation) {
            if (b == x && !relation.contains({a, c})) {
                return false;
            }
        }
    }

    return true;
}

bool isConnected(
    const Relation& relation,
    const Universe& universe
) {
    for (const auto& a : universe) {
        for (const auto& b : universe) {
            if (
                a != b &&
                !relation.contains({a, b}) &&
                !relation.contains({b, a})
            ) {
                return false;
            }
        }
    }

    return true;
}


// -----------------------------------------------------------------------------
// Relation transformations
// -----------------------------------------------------------------------------

Relation inverseRelation(const Relation& relation) {
    Relation result;

    for (const auto& [a, b] : relation) {
        result.insert({b, a});
    }

    return result;
}

Relation composeRelations(
    const Relation& first,
    const Relation& second
) {
    /*
     * Computes second o first.
     *
     * If (a,b) belongs to first and (b,c) belongs to second,
     * then (a,c) belongs to the composition.
     */
    Relation result;

    for (const auto& [a, b] : first) {
        for (const auto& [x, c] : second) {
            if (b == x) {
                result.insert({a, c});
            }
        }
    }

    return result;
}

Relation relationPower(
    const Relation& relation,
    int exponent
) {
    if (exponent < 1) {
        throw invalid_argument(
            "Relation power must be a positive integer."
        );
    }

    Relation result = relation;

    for (int i = 1; i < exponent; ++i) {
        result = composeRelations(result, relation);
    }

    return result;
}


// -----------------------------------------------------------------------------
// Closures
// -----------------------------------------------------------------------------

Relation reflexiveClosure(
    const Relation& relation,
    const Universe& universe
) {
    Relation result = relation;

    for (const auto& element : universe) {
        result.insert({element, element});
    }

    return result;
}

Relation symmetricClosure(const Relation& relation) {
    Relation result = relation;

    for (const auto& [a, b] : relation) {
        result.insert({b, a});
    }

    return result;
}

Relation transitiveClosure(const Relation& relation) {
    /*
     * Repeatedly add (a,c) whenever (a,b) and (b,c) are present.
     *
     * This computes the smallest transitive relation containing R.
     */
    Relation closure = relation;

    bool changed = true;

    while (changed) {
        changed = false;
        Relation additions;

        for (const auto& [a, b] : closure) {
            for (const auto& [x, c] : closure) {
                if (b == x && !closure.contains({a, c})) {
                    additions.insert({a, c});
                }
            }
        }

        for (const auto& pair : additions) {
            if (!closure.contains(pair)) {
                closure.insert(pair);
                changed = true;
            }
        }
    }

    return closure;
}


// -----------------------------------------------------------------------------
// Warshall's algorithm
// -----------------------------------------------------------------------------

Relation warshallTransitiveClosure(
    const Relation& relation,
    const vector<string>& elements
) {
    const size_t n = elements.size();

    map<string, size_t> index;

    for (size_t i = 0; i < n; ++i) {
        index[elements[i]] = i;
    }

    vector<vector<bool>> reachable(
        n,
        vector<bool>(n, false)
    );

    for (const auto& [a, b] : relation) {
        reachable[index[a]][index[b]] = true;
    }

    /*
     * Warshall's recurrence:
     *
     * reachable[i][j] =
     *     reachable[i][j] OR
     *     (reachable[i][k] AND reachable[k][j])
     *
     * Time: O(n^3)
     * Space: O(n^2)
     */
    for (size_t k = 0; k < n; ++k) {
        for (size_t i = 0; i < n; ++i) {
            if (!reachable[i][k]) {
                continue;
            }

            for (size_t j = 0; j < n; ++j) {
                reachable[i][j] =
                    reachable[i][j] ||
                    reachable[k][j];
            }
        }
    }

    Relation result;

    for (size_t i = 0; i < n; ++i) {
        for (size_t j = 0; j < n; ++j) {
            if (reachable[i][j]) {
                result.insert({
                    elements[i],
                    elements[j]
                });
            }
        }
    }

    return result;
}


// -----------------------------------------------------------------------------
// Classifications
// -----------------------------------------------------------------------------

bool isEquivalenceRelation(
    const Relation& relation,
    const Universe& universe
) {
    return (
        isReflexive(relation, universe) &&
        isSymmetric(relation) &&
        isTransitive(relation)
    );
}

bool isPartialOrder(
    const Relation& relation,
    const Universe& universe
) {
    return (
        isReflexive(relation, universe) &&
        isAntisymmetric(relation) &&
        isTransitive(relation)
    );
}


// -----------------------------------------------------------------------------
// Equivalence classes
// -----------------------------------------------------------------------------

set<string> equivalenceClass(
    const Relation& relation,
    const string& element,
    const Universe& universe
) {
    if (!isEquivalenceRelation(relation, universe)) {
        throw invalid_argument(
            "Equivalence classes require an equivalence relation."
        );
    }

    set<string> result;

    for (const auto& other : universe) {
        if (relation.contains({element, other})) {
            result.insert(other);
        }
    }

    return result;
}

vector<set<string>> equivalenceClasses(
    const Relation& relation,
    const Universe& universe
) {
    if (!isEquivalenceRelation(relation, universe)) {
        throw invalid_argument(
            "Equivalence classes require an equivalence relation."
        );
    }

    set<string> remaining = universe;
    vector<set<string>> result;

    while (!remaining.empty()) {
        const string representative = *remaining.begin();

        set<string> currentClass =
            equivalenceClass(
                relation,
                representative,
                universe
            );

        result.push_back(currentClass);

        for (const auto& element : currentClass) {
            remaining.erase(element);
        }
    }

    return result;
}


// -----------------------------------------------------------------------------
// Matrix representation
// -----------------------------------------------------------------------------

void printMatrix(
    const Relation& relation,
    const vector<string>& elements
) {
    cout << setw(16) << "";

    for (const auto& element : elements) {
        cout << setw(5) << element;
    }

    cout << "\n";

    for (const auto& row : elements) {
        cout << setw(16) << row;

        for (const auto& column : elements) {
            cout << setw(5)
                 << (relation.contains({row, column}) ? 1 : 0);
        }

        cout << "\n";
    }
}


// -----------------------------------------------------------------------------
// Counterexamples
// -----------------------------------------------------------------------------

string reflexivityCounterexample(
    const Relation& relation,
    const Universe& universe
) {
    for (const auto& element : universe) {
        if (!relation.contains({element, element})) {
            return "(" + element + ", " + element + ")";
        }
    }

    return "none";
}

string symmetryCounterexample(
    const Relation& relation
) {
    for (const auto& [a, b] : relation) {
        if (!relation.contains({b, a})) {
            return "(" + a + ", " + b + ")";
        }
    }

    return "none";
}

string antisymmetryCounterexample(
    const Relation& relation
) {
    for (const auto& [a, b] : relation) {
        if (a != b && relation.contains({b, a})) {
            return "(" + a + ", " + b + ")";
        }
    }

    return "none";
}

string transitivityCounterexample(
    const Relation& relation
) {
    for (const auto& [a, b] : relation) {
        for (const auto& [x, c] : relation) {
            if (b == x && !relation.contains({a, c})) {
                return "(" + a + ", " + b + ", " + c + ")";
            }
        }
    }

    return "none";
}


// -----------------------------------------------------------------------------
// Property report
// -----------------------------------------------------------------------------

void printProperties(
    const string& name,
    const Relation& relation,
    const Universe& universe
) {
    cout << "\n" << name << "\n";
    cout << string(name.size(), '-') << "\n";

    cout << "Relation: ";
    printRelation(relation);
    cout << "\n";

    cout << boolalpha;
    cout << "Reflexive:     "
         << isReflexive(relation, universe) << "\n";
    cout << "Irreflexive:   "
         << isIrreflexive(relation, universe) << "\n";
    cout << "Symmetric:     "
         << isSymmetric(relation) << "\n";
    cout << "Antisymmetric: "
         << isAntisymmetric(relation) << "\n";
    cout << "Asymmetric:    "
         << isAsymmetric(relation) << "\n";
    cout << "Transitive:    "
         << isTransitive(relation) << "\n";
    cout << "Connected:     "
         << isConnected(relation, universe) << "\n";
}


// -----------------------------------------------------------------------------
// Industry-style case study
// -----------------------------------------------------------------------------

class LearningPlatform {
private:
    Universe users;
    Universe courses;

    /*
     * enrolled:
     *     User -> Course
     *
     * prerequisites:
     *     Course -> Course
     *
     * authorized:
     *     User -> Resource
     *
     * The different relations intentionally demonstrate that a binary
     * relation does not have to be a relation from a set to itself.
     */
    Relation enrolled;
    Relation prerequisites;
    Relation authorized;

public:
    void addUser(const string& user) {
        users.insert(user);
    }

    void addCourse(const string& course) {
        courses.insert(course);
    }

    void enroll(
        const string& user,
        const string& course
    ) {
        if (!users.contains(user)) {
            throw invalid_argument("Unknown user: " + user);
        }

        if (!courses.contains(course)) {
            throw invalid_argument("Unknown course: " + course);
        }

        enrolled.insert({user, course});
    }

    void addPrerequisite(
        const string& prerequisite,
        const string& course
    ) {
        if (!courses.contains(prerequisite) ||
            !courses.contains(course)) {
            throw invalid_argument(
                "Prerequisite references an unknown course."
            );
        }

        if (prerequisite == course) {
            throw invalid_argument(
                "A course cannot directly require itself."
            );
        }

        prerequisites.insert({
            prerequisite,
            course
        });
    }

    void authorize(
        const string& user,
        const string& resource
    ) {
        if (!users.contains(user)) {
            throw invalid_argument("Unknown user: " + user);
        }

        authorized.insert({user, resource});
    }

    bool isEnrolled(
        const string& user,
        const string& course
    ) const {
        return enrolled.contains({user, course});
    }

    bool hasDirectPrerequisite(
        const string& prerequisite,
        const string& course
    ) const {
        return prerequisites.contains({
            prerequisite,
            course
        });
    }

    Relation allPrerequisites() const {
        /*
         * The transitive closure converts direct prerequisites into
         * all direct and indirect prerequisite relationships.
         */
        return transitiveClosure(prerequisites);
    }

    bool hasPrerequisite(
        const string& prerequisite,
        const string& course
    ) const {
        const Relation closure = allPrerequisites();

        return closure.contains({
            prerequisite,
            course
        });
    }

    bool hasAccess(
        const string& user,
        const string& resource
    ) const {
        return authorized.contains({
            user,
            resource
        });
    }

    void printSystem() const {
        cout << "\nUsers: ";

        for (const auto& user : users) {
            cout << user << " ";
        }

        cout << "\nCourses: ";

        for (const auto& course : courses) {
            cout << course << " ";
        }

        cout << "\nEnrollment relation: ";
        printRelation(enrolled);

        cout << "\nPrerequisite relation: ";
        printRelation(prerequisites);

        cout << "\nAuthorization relation: ";
        printRelation(authorized);

        cout << "\n";
    }

    const Relation& getPrerequisites() const {
        return prerequisites;
    }

    const Universe& getCourses() const {
        return courses;
    }
};


// -----------------------------------------------------------------------------
// Main
// -----------------------------------------------------------------------------

int main() {
    try {
        cout << string(78, '=') << "\n";
        cout << "BINARY RELATIONS: C++ TECHNICAL CASE STUDY\n";
        cout << string(78, '=') << "\n";

        // ---------------------------------------------------------------------
        // 1. Cartesian product
        // ---------------------------------------------------------------------

        cout << "\n1. CARTESIAN PRODUCT\n";
        cout << "--------------------\n";

        Universe A = {"1", "2", "3"};
        Universe B = {"x", "y"};

        Relation AxB = cartesianProduct(A, B);

        cout << "A x B = ";
        printRelation(AxB);
        cout << "\n";

        // ---------------------------------------------------------------------
        // 2. A general binary relation
        // ---------------------------------------------------------------------

        cout << "\n2. GENERAL BINARY RELATION\n";
        cout << "--------------------------\n";

        Universe small = {"1", "2", "3"};

        Relation R = {
            {"1", "1"},
            {"1", "2"},
            {"2", "2"},
            {"2", "3"},
            {"3", "3"}
        };

        validateRelation(R, small, small);

        printProperties(
            "Relation R",
            R,
            small
        );

        // ---------------------------------------------------------------------
        // 3. Matrix representation
        // ---------------------------------------------------------------------

        cout << "\n3. RELATION MATRIX\n";
        cout << "------------------\n";

        vector<string> matrixElements(
            small.begin(),
            small.end()
        );

        printMatrix(R, matrixElements);

        // ---------------------------------------------------------------------
        // 4. Property counterexamples
        // ---------------------------------------------------------------------

        cout << "\n4. COUNTEREXAMPLES\n";
        cout << "-----------------\n";

        cout << "Reflexivity counterexample: "
             << reflexivityCounterexample(R, small)
             << "\n";

        cout << "Symmetry counterexample: "
             << symmetryCounterexample(R)
             << "\n";

        cout << "Antisymmetry counterexample: "
             << antisymmetryCounterexample(R)
             << "\n";

        cout << "Transitivity counterexample: "
             << transitivityCounterexample(R)
             << "\n";

        // ---------------------------------------------------------------------
        // 5. Identity relation
        // ---------------------------------------------------------------------

        cout << "\n5. IDENTITY RELATION\n";
        cout << "--------------------\n";

        Relation identity;

        for (const auto& element : small) {
            identity.insert({
                element,
                element
            });
        }

        printProperties(
            "Identity",
            identity,
            small
        );

        // ---------------------------------------------------------------------
        // 6. Strict and non-strict ordering
        // ---------------------------------------------------------------------

        cout << "\n6. ORDER RELATIONS\n";
        cout << "------------------\n";

        Relation lessThan = {
            {"1", "2"},
            {"1", "3"},
            {"2", "3"}
        };

        Relation lessEqual = {
            {"1", "1"},
            {"1", "2"},
            {"1", "3"},
            {"2", "2"},
            {"2", "3"},
            {"3", "3"}
        };

        printProperties(
            "Strict less-than relation",
            lessThan,
            small
        );

        printProperties(
            "Less-than-or-equal relation",
            lessEqual,
            small
        );

        // ---------------------------------------------------------------------
        // 7. Equivalence relation
        // ---------------------------------------------------------------------

        cout << "\n7. EQUIVALENCE RELATION\n";
        cout << "-----------------------\n";

        Universe residues = {
            "0", "1", "2", "3", "4", "5", "6", "7"
        };

        Relation moduloThree;

        for (const auto& aString : residues) {
            int a = stoi(aString);

            for (const auto& bString : residues) {
                int b = stoi(bString);

                if ((a - b) % 3 == 0) {
                    moduloThree.insert({
                        aString,
                        bString
                    });
                }
            }
        }

        printProperties(
            "Congruence modulo 3",
            moduloThree,
            residues
        );

        cout << "Is equivalence relation: "
             << boolalpha
             << isEquivalenceRelation(
                    moduloThree,
                    residues
                )
             << "\n";

        const auto classes =
            equivalenceClasses(
                moduloThree,
                residues
            );

        cout << "Equivalence classes:\n";

        for (const auto& currentClass : classes) {
            cout << "  {";

            bool first = true;

            for (const auto& element : currentClass) {
                if (!first) {
                    cout << ", ";
                }

                cout << element;
                first = false;
            }

            cout << "}\n";
        }

        // ---------------------------------------------------------------------
        // 8. Partial order through divisibility
        // ---------------------------------------------------------------------

        cout << "\n8. PARTIAL ORDER: DIVISIBILITY\n";
        cout << "------------------------------\n";

        Universe numbers = {
            "1", "2", "3", "4", "6", "12"
        };

        Relation divides;

        for (const auto& aString : numbers) {
            int a = stoi(aString);

            for (const auto& bString : numbers) {
                int b = stoi(bString);

                if (b % a == 0) {
                    divides.insert({
                        aString,
                        bString
                    });
                }
            }
        }

        printProperties(
            "Divisibility",
            divides,
            numbers
        );

        cout << "Partial order: "
             << isPartialOrder(divides, numbers)
             << "\n";

        cout << "Connected/total: "
             << isConnected(divides, numbers)
             << "\n";

        // ---------------------------------------------------------------------
        // 9. Inverse and composition
        // ---------------------------------------------------------------------

        cout << "\n9. INVERSE AND COMPOSITION\n";
        cout << "--------------------------\n";

        Relation employeeSkills = {
            {"Alice", "Python"},
            {"Bob", "C++"},
            {"Carol", "Python"}
        };

        Relation skillCategories = {
            {"Python", "Programming"},
            {"C++", "Programming"}
        };

        cout << "Employee -> Skill: ";
        printRelation(employeeSkills);
        cout << "\n";

        cout << "Skill -> Category: ";
        printRelation(skillCategories);
        cout << "\n";

        Relation employeeCategories =
            composeRelations(
                employeeSkills,
                skillCategories
            );

        cout << "Employee -> Category: ";
        printRelation(employeeCategories);
        cout << "\n";

        cout << "Inverse Employee -> Skill relation: ";
        printRelation(
            inverseRelation(employeeSkills)
        );
        cout << "\n";

        // ---------------------------------------------------------------------
        // 10. Relation powers
        // ---------------------------------------------------------------------

        cout << "\n10. RELATION POWERS\n";
        cout << "-------------------\n";

        Relation graph = {
            {"A", "B"},
            {"B", "C"},
            {"C", "D"}
        };

        cout << "R: ";
        printRelation(graph);
        cout << "\n";

        cout << "R^2: ";
        printRelation(
            relationPower(graph, 2)
        );
        cout << "\n";

        cout << "R^3: ";
        printRelation(
            relationPower(graph, 3)
        );
        cout << "\n";

        // ---------------------------------------------------------------------
        // 11. Closures
        // ---------------------------------------------------------------------

        cout << "\n11. RELATION CLOSURES\n";
        cout << "--------------------\n";

        Relation incomplete = {
            {"1", "2"},
            {"2", "3"}
        };

        cout << "Original: ";
        printRelation(incomplete);
        cout << "\n";

        cout << "Reflexive closure: ";
        printRelation(
            reflexiveClosure(
                incomplete,
                small
            )
        );
        cout << "\n";

        cout << "Symmetric closure: ";
        printRelation(
            symmetricClosure(incomplete)
        );
        cout << "\n";

        Relation closure =
            transitiveClosure(incomplete);

        cout << "Transitive closure: ";
        printRelation(closure);
        cout << "\n";

        // ---------------------------------------------------------------------
        // 12. Warshall verification
        // ---------------------------------------------------------------------

        cout << "\n12. WARSHALL'S ALGORITHM\n";
        cout << "-----------------------\n";

        Relation warshall =
            warshallTransitiveClosure(
                incomplete,
                matrixElements
            );

        cout << "Repeated-composition closure: ";
        printRelation(closure);
        cout << "\n";

        cout << "Warshall closure: ";
        printRelation(warshall);
        cout << "\n";

        cout << "Results agree: "
             << (closure == warshall)
             << "\n";

        // ---------------------------------------------------------------------
        // 13. Industry-style learning-platform model
        // ---------------------------------------------------------------------

        cout << "\n13. INDUSTRY-STYLE CASE STUDY\n";
        cout << "-----------------------------\n";

        LearningPlatform platform;

        platform.addUser("Alice");
        platform.addUser("Bob");
        platform.addUser("Carol");

        platform.addCourse("Programming");
        platform.addCourse("Data Structures");
        platform.addCourse("Algorithms");
        platform.addCourse("Machine Learning");

        platform.enroll(
            "Alice",
            "Programming"
        );

        platform.enroll(
            "Alice",
            "Data Structures"
        );

        platform.enroll(
            "Bob",
            "Programming"
        );

        platform.enroll(
            "Carol",
            "Algorithms"
        );

        platform.addPrerequisite(
            "Programming",
            "Data Structures"
        );

        platform.addPrerequisite(
            "Data Structures",
            "Algorithms"
        );

        platform.addPrerequisite(
            "Algorithms",
            "Machine Learning"
        );

        platform.authorize(
            "Alice",
            "Course Dashboard"
        );

        platform.authorize(
            "Bob",
            "Course Dashboard"
        );

        platform.authorize(
            "Alice",
            "Analytics"
        );

        platform.printSystem();

        cout << "\nDirect prerequisite checks:\n";

        cout << "Programming -> Data Structures: "
             << platform.hasDirectPrerequisite(
                    "Programming",
                    "Data Structures"
                )
             << "\n";

        cout << "Programming -> Algorithms: "
             << platform.hasDirectPrerequisite(
                    "Programming",
                    "Algorithms"
                )
             << "\n";

        cout << "\nTransitive prerequisite checks:\n";

        cout << "Programming -> Algorithms: "
             << platform.hasPrerequisite(
                    "Programming",
                    "Algorithms"
                )
             << "\n";

        cout << "Programming -> Machine Learning: "
             << platform.hasPrerequisite(
                    "Programming",
                    "Machine Learning"
                )
             << "\n";

        cout << "Data Structures -> Machine Learning: "
             << platform.hasPrerequisite(
                    "Data Structures",
                    "Machine Learning"
                )
             << "\n";

        cout << "\nAuthorization checks:\n";

        cout << "Alice -> Analytics: "
             << platform.hasAccess(
                    "Alice",
                    "Analytics"
                )
             << "\n";

        cout << "Bob -> Analytics: "
             << platform.hasAccess(
                    "Bob",
                    "Analytics"
                )
             << "\n";

        // ---------------------------------------------------------------------
        // 14. Cycle detection through self-reachability
        // ---------------------------------------------------------------------

        cout << "\n14. CYCLE AND SELF-REACHABILITY CHECK\n";
        cout << "--------------------------------------\n";

        Relation acyclicPrerequisites = {
            {"Programming", "Data Structures"},
            {"Data Structures", "Algorithms"},
            {"Algorithms", "Machine Learning"}
        };

        Universe courseUniverse = {
            "Programming",
            "Data Structures",
            "Algorithms",
            "Machine Learning"
        };

        Relation prerequisiteClosure =
            transitiveClosure(
                acyclicPrerequisites
            );

        bool hasCycle = false;

        for (const auto& course : courseUniverse) {
            if (prerequisiteClosure.contains({
                    course,
                    course
                })) {
                hasCycle = true;
                break;
            }
        }

        /*
         * A non-empty path from a node back to itself indicates a cycle.
         * The direct prerequisite relation deliberately excludes self-edges.
         */
        cout << "Cycle detected: "
             << hasCycle
             << "\n";

        // ---------------------------------------------------------------------
        // 15. Failure handling
        // ---------------------------------------------------------------------

        cout << "\n15. VALIDATION AND FAILURE HANDLING\n";
        cout << "-----------------------------------\n";

        try {
            platform.enroll(
                "Unknown User",
                "Programming"
            );
        } catch (const exception& error) {
            cout << "Caught invalid enrollment: "
                 << error.what()
                 << "\n";
        }

        try {
            platform.addPrerequisite(
                "Machine Learning",
                "Machine Learning"
            );
        } catch (const exception& error) {
            cout << "Caught self-prerequisite: "
                 << error.what()
                 << "\n";
        }

        // ---------------------------------------------------------------------
        // 16. Mathematical assertions
        // ---------------------------------------------------------------------

        cout << "\n16. EXECUTABLE ASSERTIONS\n";
        cout << "-------------------------\n";

        if (!isReflexive(identity, small)) {
            throw runtime_error(
                "Identity relation should be reflexive."
            );
        }

        if (!isSymmetric(identity)) {
            throw runtime_error(
                "Identity relation should be symmetric."
            );
        }

        if (!isAntisymmetric(identity)) {
            throw runtime_error(
                "Identity relation should be antisymmetric."
            );
        }

        if (!isTransitive(identity)) {
            throw runtime_error(
                "Identity relation should be transitive."
            );
        }

        if (!isIrreflexive(lessThan, small)) {
            throw runtime_error(
                "Less-than should be irreflexive."
            );
        }

        if (!isAsymmetric(lessThan)) {
            throw runtime_error(
                "Less-than should be asymmetric."
            );
        }

        if (!isTransitive(lessThan)) {
            throw runtime_error(
                "Less-than should be transitive."
            );
        }

        if (!isPartialOrder(lessEqual, small)) {
            throw runtime_error(
                "Less-than-or-equal should be a partial order."
            );
        }

        if (!isEquivalenceRelation(
                moduloThree,
                residues
            )) {
            throw runtime_error(
                "Modulo congruence should be an equivalence relation."
            );
        }

        cout << "All mathematical assertions passed.\n";

        // ---------------------------------------------------------------------
        // 17. Complexity
        // ---------------------------------------------------------------------

        cout << "\n17. PERFORMANCE CONSIDERATIONS\n";
        cout << "------------------------------\n";

        cout << "A relation on n elements can contain at most n^2 pairs.\n";
        cout << "Reflexivity check: O(n).\n";
        cout << "Symmetry check: O(|R|) using set lookup.\n";
        cout << "Antisymmetry check: O(|R|) using set lookup.\n";
        cout << "Naive transitivity check: O(|R|^2).\n";
        cout << "Warshall transitive closure: O(n^3) time, O(n^2) space.\n";
        cout << "std::set provides logarithmic lookup, so practical constants "
                "also depend on the representation.\n";

        // ---------------------------------------------------------------------
        // 18. Design and security considerations
        // ---------------------------------------------------------------------

        cout << "\n18. DESIGN AND SECURITY CONSIDERATIONS\n";
        cout << "--------------------------------------\n";

        cout << "1. Validate relation endpoints before storing pairs.\n";
        cout << "2. Keep domain/codomain definitions explicit.\n";
        cout << "3. Treat authorization relations as security-sensitive data.\n";
        cout << "4. Use transitive closure carefully because indirect permissions "
                "or dependencies may become visible.\n";
        cout << "5. Prefer sparse representations when the relation contains "
                "far fewer than n^2 pairs.\n";
        cout << "6. Use matrix algorithms when dense reachability queries justify "
                "the O(n^2) memory cost.\n";

        cout << "\n" << string(78, '=') << "\n";
        cout << "END OF C++ RELATION CASE STUDY\n";
        cout << string(78, '=') << "\n";

    } catch (const exception& error) {
        cerr << "\nFatal error: "
             << error.what()
             << "\n";

        return 1;
    }

    return 0;
}
