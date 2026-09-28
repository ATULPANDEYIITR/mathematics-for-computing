/*
 * Discrete Mathematical Structures: C++17 Case Study
 *
 * Scenario:
 *   A university computing platform manages users, roles, permissions,
 *   course prerequisites, and dependency workflows.
 *
 * Mathematical structures represented:
 *   - Sets
 *   - Relations
 *   - Functions
 *   - Equivalence classes
 *   - Partial orders
 *   - Directed graphs
 *   - Topological ordering
 *   - Boolean logic
 *   - Counting
 *   - State-transition relations
 *
 * Compile:
 *   g++ -std=c++17 -Wall -Wextra -pedantic discrete_structures.cpp -o discrete_structures
 *
 * Run:
 *   ./discrete_structures
 */

#include <algorithm>
#include <cassert>
#include <cstddef>
#include <exception>
#include <functional>
#include <iomanip>
#include <iostream>
#include <map>
#include <queue>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

// ============================================================================
// 1. BASIC MATHEMATICAL TYPES
// ============================================================================

template <typename T>
using Set = std::set<T>;

template <typename A, typename B>
using Relation = std::set<pair<A, B>>;

struct PermissionRequest {
    string user;
    string permission;
};


// ============================================================================
// 2. SET OPERATIONS
// ============================================================================

template <typename T>
Set<T> setUnion(const Set<T>& first, const Set<T>& second) {
    Set<T> result = first;
    result.insert(second.begin(), second.end());
    return result;
}

template <typename T>
Set<T> setIntersection(const Set<T>& first, const Set<T>& second) {
    Set<T> result;

    set_intersection(
        first.begin(),
        first.end(),
        second.begin(),
        second.end(),
        inserter(result, result.begin())
    );

    return result;
}

template <typename T>
Set<T> setDifference(const Set<T>& first, const Set<T>& second) {
    Set<T> result;

    set_difference(
        first.begin(),
        first.end(),
        second.begin(),
        second.end(),
        inserter(result, result.begin())
    );

    return result;
}

template <typename T>
bool isSubset(const Set<T>& subset, const Set<T>& superset) {
    for (const auto& value : subset) {
        if (!superset.count(value)) {
            return false;
        }
    }

    return true;
}

template <typename T>
void printSet(const Set<T>& values) {
    cout << "{";

    bool first = true;

    for (const auto& value : values) {
        if (!first) {
            cout << ", ";
        }

        cout << value;
        first = false;
    }

    cout << "}";
}


// ============================================================================
// 3. RELATION PROPERTIES
// ============================================================================

template <typename T>
bool isReflexive(
    const Set<T>& domain,
    const Relation<T, T>& relation
) {
    for (const auto& value : domain) {
        if (!relation.count({value, value})) {
            return false;
        }
    }

    return true;
}

template <typename T>
bool isSymmetric(
    const Relation<T, T>& relation
) {
    for (const auto& [first, second] : relation) {
        if (!relation.count({second, first})) {
            return false;
        }
    }

    return true;
}

template <typename T>
bool isAntisymmetric(
    const Relation<T, T>& relation
) {
    for (const auto& [first, second] : relation) {
        if (
            first != second &&
            relation.count({second, first})
        ) {
            return false;
        }
    }

    return true;
}

template <typename T>
bool isTransitive(
    const Relation<T, T>& relation
) {
    for (const auto& [first, middle] : relation) {
        for (const auto& [middle2, last] : relation) {
            if (
                middle == middle2 &&
                !relation.count({first, last})
            ) {
                return false;
            }
        }
    }

    return true;
}

template <typename T>
bool isPartialOrder(
    const Set<T>& domain,
    const Relation<T, T>& relation
) {
    return (
        isReflexive(domain, relation) &&
        isAntisymmetric(relation) &&
        isTransitive(relation)
    );
}


// ============================================================================
// 4. FUNCTION MODEL
// ============================================================================

template <typename Domain, typename Codomain>
class FiniteFunction {
private:
    map<Domain, Codomain> mapping;
    Set<Codomain> codomain;

public:
    FiniteFunction(
        map<Domain, Codomain> mappingValue,
        Set<Codomain> codomainValue
    )
        : mapping(std::move(mappingValue)),
          codomain(std::move(codomainValue)) {}

    bool isInjective() const {
        Set<Codomain> image;

        for (const auto& [input, output] : mapping) {
            (void)input;

            if (!image.insert(output).second) {
                return false;
            }
        }

        return true;
    }

    bool isSurjective() const {
        Set<Codomain> image;

        for (const auto& [input, output] : mapping) {
            (void)input;
            image.insert(output);
        }

        return image == codomain;
    }

    bool isBijective() const {
        return isInjective() && isSurjective();
    }

    const Codomain& apply(const Domain& input) const {
        auto iterator = mapping.find(input);

        if (iterator == mapping.end()) {
            throw out_of_range("Input is outside the function domain.");
        }

        return iterator->second;
    }

    map<Codomain, Domain> inverse() const {
        if (!isBijective()) {
            throw logic_error(
                "An inverse function requires a bijection."
            );
        }

        map<Codomain, Domain> result;

        for (const auto& [input, output] : mapping) {
            result[output] = input;
        }

        return result;
    }
};


// ============================================================================
// 5. GRAPH STRUCTURE
// ============================================================================

class DirectedGraph {
private:
    map<string, Set<string>> adjacency;

public:
    void addVertex(const string& vertex) {
        adjacency.try_emplace(vertex);
    }

    void addEdge(
        const string& source,
        const string& target
    ) {
        addVertex(source);
        addVertex(target);
        adjacency[source].insert(target);
    }

    const map<string, Set<string>>& getAdjacency() const {
        return adjacency;
    }

    vector<string> topologicalSort() const {
        map<string, size_t> indegree;

        for (const auto& [vertex, neighbors] : adjacency) {
            (void)neighbors;
            indegree[vertex] = 0;
        }

        for (const auto& [vertex, neighbors] : adjacency) {
            (void)vertex;

            for (const auto& neighbor : neighbors) {
                ++indegree[neighbor];
            }
        }

        queue<string> ready;

        for (const auto& [vertex, degree] : indegree) {
            if (degree == 0) {
                ready.push(vertex);
            }
        }

        vector<string> order;

        while (!ready.empty()) {
            string current = ready.front();
            ready.pop();

            order.push_back(current);

            auto adjacencyIterator = adjacency.find(current);

            if (adjacencyIterator == adjacency.end()) {
                continue;
            }

            for (const auto& neighbor : adjacencyIterator->second) {
                --indegree[neighbor];

                if (indegree[neighbor] == 0) {
                    ready.push(neighbor);
                }
            }
        }

        if (order.size() != adjacency.size()) {
            throw logic_error(
                "Topological sorting failed because the graph contains a cycle."
            );
        }

        return order;
    }

    vector<string> breadthFirstSearch(
        const string& start
    ) const {
        if (!adjacency.count(start)) {
            throw out_of_range("BFS start vertex does not exist.");
        }

        queue<string> queue;
        Set<string> visited;
        vector<string> order;

        queue.push(start);
        visited.insert(start);

        while (!queue.empty()) {
            string current = queue.front();
            queue.pop();

            order.push_back(current);

            for (const auto& neighbor : adjacency.at(current)) {
                if (!visited.count(neighbor)) {
                    visited.insert(neighbor);
                    queue.push(neighbor);
                }
            }
        }

        return order;
    }
};


// ============================================================================
// 6. ROLE AND PERMISSION SYSTEM
// ============================================================================

class AuthorizationSystem {
private:
    Set<string> users;
    Set<string> roles;
    Set<string> permissions;

    map<string, Set<string>> rolePermissions;
    map<string, Set<string>> userRoles;

public:
    void addUser(const string& username) {
        users.insert(username);
    }

    void addRole(const string& role) {
        roles.insert(role);
    }

    void addPermission(const string& permission) {
        permissions.insert(permission);
    }

    void assignPermissionToRole(
        const string& role,
        const string& permission
    ) {
        if (!roles.count(role)) {
            throw invalid_argument("Unknown role.");
        }

        if (!permissions.count(permission)) {
            throw invalid_argument("Unknown permission.");
        }

        rolePermissions[role].insert(permission);
    }

    void assignRoleToUser(
        const string& username,
        const string& role
    ) {
        if (!users.count(username)) {
            throw invalid_argument("Unknown user.");
        }

        if (!roles.count(role)) {
            throw invalid_argument("Unknown role.");
        }

        userRoles[username].insert(role);
    }

    Set<string> effectivePermissions(
        const string& username
    ) const {
        if (!users.count(username)) {
            throw invalid_argument("Unknown user.");
        }

        Set<string> result;

        auto userIterator = userRoles.find(username);

        if (userIterator == userRoles.end()) {
            return result;
        }

        for (const auto& role : userIterator->second) {
            auto roleIterator = rolePermissions.find(role);

            if (roleIterator == rolePermissions.end()) {
                continue;
            }

            result = setUnion(
                result,
                roleIterator->second
            );
        }

        return result;
    }

    bool canPerform(
        const string& username,
        const string& permission
    ) const {
        if (!permissions.count(permission)) {
            return false;
        }

        Set<string> effective = effectivePermissions(username);
        return effective.count(permission) > 0;
    }
};


// ============================================================================
// 7. BOOLEAN LOGIC
// ============================================================================

bool implies(bool p, bool q) {
    // Material implication is equivalent to (!p OR q).
    return !p || q;
}

bool biconditional(bool p, bool q) {
    return p == q;
}

bool accessPolicy(
    bool authenticated,
    bool accountActive,
    bool permissionPresent
) {
    // Security rule:
    // authenticated AND active AND permitted.
    return (
        authenticated &&
        accountActive &&
        permissionPresent
    );
}


// ============================================================================
// 8. EQUIVALENCE CLASSES
// ============================================================================

Set<int> moduloClass(
    int representative,
    int modulus,
    const Set<int>& domain
) {
    if (modulus <= 0) {
        throw invalid_argument(
            "Modulus must be positive."
        );
    }

    Set<int> result;

    for (int value : domain) {
        if (
            ((value % modulus) + modulus) % modulus ==
            ((representative % modulus) + modulus) % modulus
        ) {
            result.insert(value);
        }
    }

    return result;
}


// ============================================================================
// 9. COUNTING FUNCTIONS
// ============================================================================

unsigned long long factorial(unsigned int n) {
    unsigned long long result = 1;

    for (unsigned int i = 2; i <= n; ++i) {
        if (
            result >
            numeric_limits<unsigned long long>::max() / i
        ) {
            throw overflow_error(
                "Factorial exceeds unsigned long long capacity."
            );
        }

        result *= i;
    }

    return result;
}

unsigned long long permutationCount(
    unsigned int n,
    unsigned int r
) {
    if (r > n) {
        throw invalid_argument(
            "Require 0 <= r <= n."
        );
    }

    unsigned long long result = 1;

    for (unsigned int i = 0; i < r; ++i) {
        result *= (n - i);
    }

    return result;
}

unsigned long long combinationCount(
    unsigned int n,
    unsigned int r
) {
    if (r > n) {
        throw invalid_argument(
            "Require 0 <= r <= n."
        );
    }

    unsigned int effectiveR = min(r, n - r);

    unsigned long long result = 1;

    for (unsigned int i = 1; i <= effectiveR; ++i) {
        result =
            result * (n - effectiveR + i) / i;
    }

    return result;
}


// ============================================================================
// 10. STATE-TRANSITION RELATION
// ============================================================================

enum class WorkflowState {
    Created,
    Queued,
    Processing,
    Completed,
    Failed,
    Cancelled
};

string stateName(WorkflowState state) {
    switch (state) {
        case WorkflowState::Created:
            return "created";
        case WorkflowState::Queued:
            return "queued";
        case WorkflowState::Processing:
            return "processing";
        case WorkflowState::Completed:
            return "completed";
        case WorkflowState::Failed:
            return "failed";
        case WorkflowState::Cancelled:
            return "cancelled";
    }

    throw logic_error("Unknown workflow state.");
}

class Workflow {
private:
    WorkflowState state = WorkflowState::Created;

    map<WorkflowState, Set<WorkflowState>> transitions = {
        {
            WorkflowState::Created,
            {
                WorkflowState::Queued,
                WorkflowState::Cancelled
            }
        },
        {
            WorkflowState::Queued,
            {
                WorkflowState::Processing,
                WorkflowState::Cancelled
            }
        },
        {
            WorkflowState::Processing,
            {
                WorkflowState::Completed,
                WorkflowState::Failed
            }
        },
        {
            WorkflowState::Failed,
            {
                WorkflowState::Queued
            }
        },
        {
            WorkflowState::Completed,
            {}
        },
        {
            WorkflowState::Cancelled,
            {}
        }
    };

public:
    WorkflowState currentState() const {
        return state;
    }

    void transitionTo(WorkflowState next) {
        if (!transitions[state].count(next)) {
            throw logic_error(
                "Invalid transition from " +
                stateName(state) +
                " to " +
                stateName(next)
            );
        }

        state = next;
    }
};


// ============================================================================
// 11. COURSE DEPENDENCY MODEL
// ============================================================================

class CourseCatalog {
private:
    Set<string> courses;
    Relation<string, string> prerequisites;

public:
    void addCourse(const string& course) {
        courses.insert(course);
    }

    void addPrerequisite(
        const string& prerequisite,
        const string& dependentCourse
    ) {
        if (!courses.count(prerequisite)) {
            throw invalid_argument(
                "Prerequisite course does not exist."
            );
        }

        if (!courses.count(dependentCourse)) {
            throw invalid_argument(
                "Dependent course does not exist."
            );
        }

        prerequisites.insert(
            {prerequisite, dependentCourse}
        );
    }

    vector<string> studyOrder() const {
        DirectedGraph graph;

        for (const auto& course : courses) {
            graph.addVertex(course);
        }

        for (const auto& [source, target] : prerequisites) {
            graph.addEdge(source, target);
        }

        return graph.topologicalSort();
    }

    bool containsCycle() const {
        try {
            (void)studyOrder();
            return false;
        } catch (const logic_error&) {
            return true;
        }
    }
};


// ============================================================================
// 12. PRINTING HELPERS
// ============================================================================

void printVector(
    const vector<string>& values
) {
    cout << "[";

    for (size_t index = 0; index < values.size(); ++index) {
        if (index > 0) {
            cout << ", ";
        }

        cout << values[index];
    }

    cout << "]";
}


// ============================================================================
// 13. MAIN CASE STUDY
// ============================================================================

int main() {
    try {
        cout << "DISCRETE MATHEMATICAL STRUCTURES CASE STUDY\n";
        cout << string(78, '=') << "\n";

        // --------------------------------------------------------------------
        // Sets
        // --------------------------------------------------------------------

        cout << "\n1. SET OPERATIONS\n";

        Set<int> first = {1, 2, 3, 4};
        Set<int> second = {3, 4, 5, 6};

        cout << "A = ";
        printSet(first);

        cout << "\nB = ";
        printSet(second);

        cout << "\nA union B = ";
        printSet(setUnion(first, second));

        cout << "\nA intersection B = ";
        printSet(setIntersection(first, second));

        cout << "\nA - B = ";
        printSet(setDifference(first, second));

        cout << "\n{1,2} subset A = "
             << boolalpha
             << isSubset(Set<int>{1, 2}, first)
             << "\n";

        // --------------------------------------------------------------------
        // Relation properties
        // --------------------------------------------------------------------

        cout << "\n2. PARTIAL ORDER RELATION\n";

        Set<int> numbers = {1, 2, 3};

        Relation<int, int> lessEqual = {
            {1, 1},
            {1, 2},
            {1, 3},
            {2, 2},
            {2, 3},
            {3, 3}
        };

        cout << "Reflexive: "
             << isReflexive(numbers, lessEqual)
             << "\n";

        cout << "Symmetric: "
             << isSymmetric(lessEqual)
             << "\n";

        cout << "Antisymmetric: "
             << isAntisymmetric(lessEqual)
             << "\n";

        cout << "Transitive: "
             << isTransitive(lessEqual)
             << "\n";

        cout << "Partial order: "
             << isPartialOrder(numbers, lessEqual)
             << "\n";

        assert(isPartialOrder(numbers, lessEqual));

        // --------------------------------------------------------------------
        // Equivalence relation
        // --------------------------------------------------------------------

        cout << "\n3. EQUIVALENCE CLASSES MODULO 3\n";

        Set<int> moduloDomain = {
            0, 1, 2, 3, 4, 5, 6, 7
        };

        for (int representative : {0, 1, 2}) {
            cout << "["
                 << representative
                 << "] = ";

            printSet(
                moduloClass(
                    representative,
                    3,
                    moduloDomain
                )
            );

            cout << "\n";
        }

        // --------------------------------------------------------------------
        // Function
        // --------------------------------------------------------------------

        cout << "\n4. FINITE FUNCTION\n";

        FiniteFunction<string, int> function(
            {
                {"A", 10},
                {"B", 20},
                {"C", 30}
            },
            {10, 20, 30}
        );

        cout << "Injective: "
             << function.isInjective()
             << "\n";

        cout << "Surjective: "
             << function.isSurjective()
             << "\n";

        cout << "Bijective: "
             << function.isBijective()
             << "\n";

        cout << "f(B) = "
             << function.apply("B")
             << "\n";

        map<int, string> inverse = function.inverse();

        cout << "f^-1(20) = "
             << inverse.at(20)
             << "\n";

        assert(function.isBijective());

        // --------------------------------------------------------------------
        // Boolean logic
        // --------------------------------------------------------------------

        cout << "\n5. PROPOSITIONAL LOGIC\n";

        for (bool p : {false, true}) {
            for (bool q : {false, true}) {
                cout << "p=" << p
                     << ", q=" << q
                     << ", p->q=" << implies(p, q)
                     << ", p<->q=" << biconditional(p, q)
                     << "\n";
            }
        }

        // De Morgan's law is verified for all four assignments.
        for (bool p : {false, true}) {
            for (bool q : {false, true}) {
                bool left = !(p && q);
                bool right = (!p || !q);

                assert(left == right);
            }
        }

        cout << "De Morgan's law verified.\n";

        // --------------------------------------------------------------------
        // Authorization system
        // --------------------------------------------------------------------

        cout << "\n6. AUTHORIZATION SYSTEM\n";

        AuthorizationSystem authorization;

        authorization.addUser("alice");
        authorization.addUser("bob");
        authorization.addUser("carol");

        authorization.addRole("viewer");
        authorization.addRole("editor");
        authorization.addRole("admin");

        authorization.addPermission("read");
        authorization.addPermission("write");
        authorization.addPermission("delete");

        authorization.assignPermissionToRole(
            "viewer",
            "read"
        );

        authorization.assignPermissionToRole(
            "editor",
            "read"
        );

        authorization.assignPermissionToRole(
            "editor",
            "write"
        );

        authorization.assignPermissionToRole(
            "admin",
            "read"
        );

        authorization.assignPermissionToRole(
            "admin",
            "write"
        );

        authorization.assignPermissionToRole(
            "admin",
            "delete"
        );

        authorization.assignRoleToUser(
            "alice",
            "admin"
        );

        authorization.assignRoleToUser(
            "bob",
            "editor"
        );

        authorization.assignRoleToUser(
            "carol",
            "viewer"
        );

        cout << "alice delete = "
             << authorization.canPerform(
                    "alice",
                    "delete"
                )
             << "\n";

        cout << "bob write = "
             << authorization.canPerform(
                    "bob",
                    "write"
                )
             << "\n";

        cout << "carol write = "
             << authorization.canPerform(
                    "carol",
                    "write"
                )
             << "\n";

        assert(
            authorization.canPerform(
                "alice",
                "delete"
            )
        );

        assert(
            !authorization.canPerform(
                "carol",
                "write"
            )
        );

        // --------------------------------------------------------------------
        // Course dependency partial order
        // --------------------------------------------------------------------

        cout << "\n7. COURSE DEPENDENCY SYSTEM\n";

        CourseCatalog catalog;

        for (const string& course : {
            "Sets",
            "Relations",
            "Logic",
            "Algorithms",
            "Databases"
        }) {
            catalog.addCourse(course);
        }

        catalog.addPrerequisite(
            "Sets",
            "Relations"
        );

        catalog.addPrerequisite(
            "Relations",
            "Databases"
        );

        catalog.addPrerequisite(
            "Logic",
            "Algorithms"
        );

        catalog.addPrerequisite(
            "Algorithms",
            "Databases"
        );

        vector<string> order = catalog.studyOrder();

        cout << "Valid course dependency order: ";
        printVector(order);
        cout << "\n";

        assert(!catalog.containsCycle());

        // Failure case: introducing a directed cycle makes a topological
        // ordering impossible.
        CourseCatalog cyclicCatalog;

        for (const string& course : {
            "A",
            "B",
            "C"
        }) {
            cyclicCatalog.addCourse(course);
        }

        cyclicCatalog.addPrerequisite("A", "B");
        cyclicCatalog.addPrerequisite("B", "C");
        cyclicCatalog.addPrerequisite("C", "A");

        cout << "Cycle detected: "
             << cyclicCatalog.containsCycle()
             << "\n";

        assert(cyclicCatalog.containsCycle());

        // --------------------------------------------------------------------
        // State transition relation
        // --------------------------------------------------------------------

        cout << "\n8. WORKFLOW STATE MACHINE\n";

        Workflow workflow;

        cout << "Initial state: "
             << stateName(workflow.currentState())
             << "\n";

        workflow.transitionTo(WorkflowState::Queued);

        cout << "After queue: "
             << stateName(workflow.currentState())
             << "\n";

        workflow.transitionTo(WorkflowState::Processing);

        cout << "After processing: "
             << stateName(workflow.currentState())
             << "\n";

        workflow.transitionTo(WorkflowState::Completed);

        cout << "Final state: "
             << stateName(workflow.currentState())
             << "\n";

        try {
            workflow.transitionTo(
                WorkflowState::Processing
            );
        } catch (const logic_error& error) {
            cout << "Expected invalid transition: "
                 << error.what()
                 << "\n";
        }

        // --------------------------------------------------------------------
        // Counting
        // --------------------------------------------------------------------

        cout << "\n9. COUNTING\n";

        cout << "5! = "
             << factorial(5)
             << "\n";

        cout << "P(5,2) = "
             << permutationCount(5, 2)
             << "\n";

        cout << "C(5,2) = "
             << combinationCount(5, 2)
             << "\n";

        assert(factorial(5) == 120);
        assert(permutationCount(5, 2) == 20);
        assert(combinationCount(5, 2) == 10);

        // --------------------------------------------------------------------
        // Security-oriented logical rule
        // --------------------------------------------------------------------

        cout << "\n10. SECURITY POLICY LOGIC\n";

        struct SecurityCase {
            bool authenticated;
            bool active;
            bool permitted;
        };

        vector<SecurityCase> securityCases = {
            {false, false, false},
            {true, false, true},
            {true, true, false},
            {true, true, true}
        };

        for (const auto& test : securityCases) {
            cout
                << "authenticated="
                << test.authenticated
                << ", active="
                << test.active
                << ", permission="
                << test.permitted
                << " -> access="
                << accessPolicy(
                    test.authenticated,
                    test.active,
                    test.permitted
                )
                << "\n";
        }

        // --------------------------------------------------------------------
        // Performance and design notes
        // --------------------------------------------------------------------

        cout << "\n11. COMPLEXITY CONSIDERATIONS\n";

        cout << "std::set lookup: O(log n)\n";
        cout << "Adjacency-list BFS: O(V + E)\n";
        cout << "Topological sorting: O(V + E)\n";
        cout << "Power-set generation: O(2^n)\n";
        cout << "Truth-table enumeration: O(2^n)\n";
        cout << "Finite map lookup: O(log n) with std::map\n";

        // --------------------------------------------------------------------
        // Edge cases
        // --------------------------------------------------------------------

        cout << "\n12. EDGE CASES\n";

        try {
            FiniteFunction<string, int> invalidFunction(
                {
                    {"A", 1},
                    {"B", 1}
                },
                {1}
            );

            invalidFunction.inverse();

            // This line should never execute.
            cerr << "Unexpected inverse success.\n";
            return 1;
        } catch (const logic_error& error) {
            cout << "Non-bijection inverse rejected: "
                 << error.what()
                 << "\n";
        }

        try {
            combinationCount(2, 5);
            cerr << "Unexpected invalid combination success.\n";
            return 1;
        } catch (const invalid_argument& error) {
            cout << "Invalid combination rejected: "
                 << error.what()
                 << "\n";
        }

        // --------------------------------------------------------------------
        // Final verification
        // --------------------------------------------------------------------

        cout << "\n13. FORMAL ASSERTIONS\n";

        assert(
            setIntersection(
                Set<int>{1, 2, 3},
                Set<int>{2, 3, 4}
            ) ==
            Set<int>{2, 3}
        );

        assert(
            isSubset(
                Set<int>{1, 2},
                Set<int>{1, 2, 3}
            )
        );

        assert(
            implies(false, false)
        );

        assert(
            biconditional(true, true)
        );

        cout << "All case-study assertions passed.\n";
        cout << "\nCase study completed successfully.\n";

    } catch (const exception& error) {
        cerr << "Fatal error: "
             << error.what()
             << "\n";

        return 1;
    }

    return 0;
}
