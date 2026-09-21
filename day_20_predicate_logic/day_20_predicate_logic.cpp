/*
 * Predicate Logic:
 * Predicates, Quantifiers, Universal Quantification,
 * and Existential Quantification
 *
 * C++17 case study:
 * Secure Enterprise Access Control
 *
 * The program models employees, training, authentication,
 * security clearance, resources, and logical authorization rules.
 *
 * It also contains reusable finite-domain implementations of
 * universal and existential quantification.
 */

#include <algorithm>
#include <cassert>
#include <functional>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <set>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

using namespace std;

// -----------------------------------------------------------------------------
// 1. Basic logical connectives
// -----------------------------------------------------------------------------

bool logical_not(bool value) {
    return !value;
}

bool logical_and(bool left, bool right) {
    return left && right;
}

bool logical_or(bool left, bool right) {
    return left || right;
}

bool logical_implies(bool antecedent, bool consequent) {
    // P -> Q is false only when P is true and Q is false.
    return !antecedent || consequent;
}

bool logical_iff(bool left, bool right) {
    return left == right;
}

// -----------------------------------------------------------------------------
// 2. Basic predicates
// -----------------------------------------------------------------------------

bool is_even(int number) {
    return number % 2 == 0;
}

bool is_positive(int number) {
    return number > 0;
}

bool is_prime(int number) {
    if (number < 2) {
        return false;
    }

    for (int divisor = 2; divisor * divisor <= number; ++divisor) {
        if (number % divisor == 0) {
            return false;
        }
    }

    return true;
}

bool less_than(int left, int right) {
    return left < right;
}

// -----------------------------------------------------------------------------
// 3. Finite-domain quantifiers
// -----------------------------------------------------------------------------

template <typename Container, typename Predicate>
bool forall(const Container& domain, Predicate predicate) {
    /*
     * Models:
     *
     *     ∀x P(x)
     *
     * over a finite domain.
     *
     * The function stops as soon as a counterexample is found.
     */
    for (const auto& item : domain) {
        if (!predicate(item)) {
            return false;
        }
    }

    return true;
}

template <typename Container, typename Predicate>
bool exists(const Container& domain, Predicate predicate) {
    /*
     * Models:
     *
     *     ∃x P(x)
     *
     * The function stops as soon as a witness is found.
     */
    for (const auto& item : domain) {
        if (predicate(item)) {
            return true;
        }
    }

    return false;
}

// -----------------------------------------------------------------------------
// 4. Witness and counterexample extraction
// -----------------------------------------------------------------------------

template <typename Container, typename Predicate>
optional<typename Container::value_type>
find_witness(const Container& domain, Predicate predicate) {
    for (const auto& item : domain) {
        if (predicate(item)) {
            return item;
        }
    }

    return nullopt;
}

template <typename Container, typename Predicate>
optional<typename Container::value_type>
find_counterexample(const Container& domain, Predicate predicate) {
    for (const auto& item : domain) {
        if (!predicate(item)) {
            return item;
        }
    }

    return nullopt;
}

// -----------------------------------------------------------------------------
// 5. Nested quantifiers
// -----------------------------------------------------------------------------

template <typename Container, typename Predicate>
bool forall_exists(
    const Container& outer_domain,
    const Container& inner_domain,
    Predicate predicate
) {
    /*
     * ∀x∃y P(x,y)
     */
    for (const auto& x : outer_domain) {
        bool found_y = false;

        for (const auto& y : inner_domain) {
            if (predicate(x, y)) {
                found_y = true;
                break;
            }
        }

        if (!found_y) {
            return false;
        }
    }

    return true;
}

template <typename Container, typename Predicate>
bool exists_forall(
    const Container& outer_domain,
    const Container& inner_domain,
    Predicate predicate
) {
    /*
     * ∃x∀y P(x,y)
     */
    for (const auto& x : outer_domain) {
        bool valid_for_all_y = true;

        for (const auto& y : inner_domain) {
            if (!predicate(x, y)) {
                valid_for_all_y = false;
                break;
            }
        }

        if (valid_for_all_y) {
            return true;
        }
    }

    return false;
}

// -----------------------------------------------------------------------------
// 6. Employee model
// -----------------------------------------------------------------------------

struct Employee {
    int employee_id;
    string name;
    string department;
    int age;
    bool active;
    bool trained;
    int security_clearance;
};

bool is_adult(const Employee& employee) {
    return employee.age >= 18;
}

bool is_active(const Employee& employee) {
    return employee.active;
}

bool is_trained(const Employee& employee) {
    return employee.trained;
}

bool has_sufficient_clearance(const Employee& employee) {
    return employee.security_clearance >= 2;
}

// -----------------------------------------------------------------------------
// 7. Access request model
// -----------------------------------------------------------------------------

struct AccessRequest {
    string user;
    string role;
    string resource;
    bool authenticated;
    bool active;
};

// -----------------------------------------------------------------------------
// 8. Authorization predicates
// -----------------------------------------------------------------------------

bool is_admin(const AccessRequest& request) {
    return request.role == "admin";
}

bool is_authenticated(const AccessRequest& request) {
    return request.authenticated;
}

bool request_is_active(const AccessRequest& request) {
    return request.active;
}

bool can_access_database(const AccessRequest& request) {
    /*
     * Simplified logical rule:
     *
     * Authenticated(x)
     * ∧ Active(x)
     * ∧ Admin(x)
     * -> AccessGranted(x)
     *
     * In an actual security system, this simplified predicate would not
     * be sufficient by itself.
     */
    return logical_and(
        logical_and(
            is_authenticated(request),
            request_is_active(request)
        ),
        is_admin(request)
    );
}

// -----------------------------------------------------------------------------
// 9. Secure-area predicate
// -----------------------------------------------------------------------------

bool can_enter_secure_area(const Employee& employee) {
    /*
     * Formal structure:
     *
     * Adult(x)
     * ∧ Active(x)
     * ∧ Trained(x)
     * ∧ ClearanceAtLeast2(x)
     *
     * -> CanEnterSecureArea(x)
     */
    return (
        is_adult(employee) &&
        is_active(employee) &&
        is_trained(employee) &&
        has_sufficient_clearance(employee)
    );
}

// -----------------------------------------------------------------------------
// 10. Policy statements
// -----------------------------------------------------------------------------

bool every_employee_is_adult(
    const vector<Employee>& employees
) {
    return forall(employees, is_adult);
}

bool at_least_one_employee_can_enter(
    const vector<Employee>& employees
) {
    return exists(
        employees,
        can_enter_secure_area
    );
}

bool every_trained_employee_is_active(
    const vector<Employee>& employees
) {
    return forall(
        employees,
        [](const Employee& employee) {
            return logical_implies(
                is_trained(employee),
                is_active(employee)
            );
        }
    );
}

bool every_cleared_employee_is_trained(
    const vector<Employee>& employees
) {
    return forall(
        employees,
        [](const Employee& employee) {
            return logical_implies(
                has_sufficient_clearance(employee),
                is_trained(employee)
            );
        }
    );
}

// -----------------------------------------------------------------------------
// 11. Reporting functions
// -----------------------------------------------------------------------------

void print_employee(const Employee& employee) {
    cout
        << "ID=" << employee.employee_id
        << ", Name=" << employee.name
        << ", Department=" << employee.department
        << ", Age=" << employee.age
        << ", Active=" << boolalpha << employee.active
        << ", Trained=" << employee.trained
        << ", Clearance=" << employee.security_clearance
        << '\n';
}

void report_secure_area_access(
    const vector<Employee>& employees
) {
    cout << "\nSecure-area eligibility:\n";

    for (const auto& employee : employees) {
        cout
            << "  "
            << employee.name
            << ": "
            << boolalpha
            << can_enter_secure_area(employee)
            << '\n';
    }
}

void report_authorization(
    const vector<AccessRequest>& requests
) {
    cout << "\nDatabase authorization:\n";

    for (const auto& request : requests) {
        cout
            << "  "
            << request.user
            << " -> "
            << request.resource
            << ": "
            << boolalpha
            << can_access_database(request)
            << '\n';
    }
}

// -----------------------------------------------------------------------------
// 12. Relation properties
// -----------------------------------------------------------------------------

template <typename Container, typename Relation>
bool is_reflexive(
    const Container& domain,
    Relation relation
) {
    for (const auto& x : domain) {
        if (!relation(x, x)) {
            return false;
        }
    }

    return true;
}

template <typename Container, typename Relation>
bool is_symmetric(
    const Container& domain,
    Relation relation
) {
    for (const auto& x : domain) {
        for (const auto& y : domain) {
            if (relation(x, y) && !relation(y, x)) {
                return false;
            }
        }
    }

    return true;
}

template <typename Container, typename Relation>
bool is_transitive(
    const Container& domain,
    Relation relation
) {
    for (const auto& x : domain) {
        for (const auto& y : domain) {
            for (const auto& z : domain) {
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

// -----------------------------------------------------------------------------
// 13. Demonstrate basic predicates
// -----------------------------------------------------------------------------

void demonstrate_basic_predicates() {
    cout << "\n=== Basic Predicates ===\n";

    cout << "Even(4): " << boolalpha << is_even(4) << '\n';
    cout << "Even(5): " << is_even(5) << '\n';
    cout << "Positive(-2): " << is_positive(-2) << '\n';
    cout << "Prime(7): " << is_prime(7) << '\n';
    cout << "Prime(8): " << is_prime(8) << '\n';
    cout << "LessThan(3, 8): " << less_than(3, 8) << '\n';
}

// -----------------------------------------------------------------------------
// 14. Demonstrate basic quantifiers
// -----------------------------------------------------------------------------

void demonstrate_basic_quantifiers() {
    cout << "\n=== Basic Quantifiers ===\n";

    vector<int> numbers{2, 4, 6, 8};

    cout
        << "∀x Even(x): "
        << forall(numbers, is_even)
        << '\n';

    cout
        << "∃x Prime(x): "
        << exists(numbers, is_prime)
        << '\n';

    vector<int> mixed_numbers{1, 2, 3, 4, 5};

    cout
        << "∀x Even(x) over mixed numbers: "
        << forall(mixed_numbers, is_even)
        << '\n';

    cout
        << "∃x Even(x) over mixed numbers: "
        << exists(mixed_numbers, is_even)
        << '\n';
}

// -----------------------------------------------------------------------------
// 15. Domain and vacuous truth
// -----------------------------------------------------------------------------

void demonstrate_domain_and_vacuous_truth() {
    cout << "\n=== Domain and Vacuous Truth ===\n";

    vector<int> empty_domain;

    cout
        << "∀x Prime(x) over empty domain: "
        << forall(empty_domain, is_prime)
        << '\n';

    cout
        << "∃x Prime(x) over empty domain: "
        << exists(empty_domain, is_prime)
        << '\n';

    /*
     * The empty-domain result follows directly from the definitions:
     *
     * ∀x P(x) is false only if a counterexample exists.
     * An empty domain contains no counterexample.
     *
     * ∃x P(x) requires at least one witness.
     * An empty domain contains no witness.
     */
}

// -----------------------------------------------------------------------------
// 16. Negation of quantified statements
// -----------------------------------------------------------------------------

void demonstrate_quantifier_negation() {
    cout << "\n=== Quantifier Negation ===\n";

    vector<int> domain{1, 2, 3, 4};

    bool not_forall = !forall(domain, is_even);

    bool exists_not = exists(
        domain,
        [](int number) {
            return !is_even(number);
        }
    );

    cout
        << "¬∀x Even(x): "
        << not_forall
        << '\n';

    cout
        << "∃x ¬Even(x): "
        << exists_not
        << '\n';

    cout
        << "Equivalent: "
        << (not_forall == exists_not)
        << '\n';

    bool not_exists = !exists(domain, is_even);

    bool forall_not = forall(
        domain,
        [](int number) {
            return !is_even(number);
        }
    );

    cout
        << "¬∃x Even(x): "
        << not_exists
        << '\n';

    cout
        << "∀x ¬Even(x): "
        << forall_not
        << '\n';
}

// -----------------------------------------------------------------------------
// 17. Quantifier order
// -----------------------------------------------------------------------------

void demonstrate_quantifier_order() {
    cout << "\n=== Quantifier Order ===\n";

    vector<int> domain{1, 2, 3, 4};

    bool first = forall_exists(
        domain,
        domain,
        [](int x, int y) {
            return x <= y;
        }
    );

    bool second = exists_forall(
        domain,
        domain,
        [](int x, int y) {
            return x <= y;
        }
    );

    cout
        << "∀x∃y (x <= y): "
        << first
        << '\n';

    cout
        << "∃x∀y (x <= y): "
        << second
        << '\n';

    /*
     * These formulas cannot generally be treated as interchangeable.
     * The first allows the witness y to depend on x.
     * The second requires one single x that works for every y.
     */
}

// -----------------------------------------------------------------------------
// 18. Evidence extraction
// -----------------------------------------------------------------------------

void demonstrate_evidence() {
    cout << "\n=== Witnesses and Counterexamples ===\n";

    vector<int> domain{1, 3, 5, 8, 10};

    auto witness = find_witness(domain, is_even);
    auto counterexample = find_counterexample(domain, is_even);

    cout << "Witness for ∃x Even(x): ";

    if (witness.has_value()) {
        cout << witness.value();
    } else {
        cout << "none";
    }

    cout << '\n';

    cout << "Counterexample to ∀x Even(x): ";

    if (counterexample.has_value()) {
        cout << counterexample.value();
    } else {
        cout << "none";
    }

    cout << '\n';
}

// -----------------------------------------------------------------------------
// 19. Complexity discussion through counting
// -----------------------------------------------------------------------------

long long unary_quantifier_checks(long long n) {
    return n;
}

long long binary_quantifier_checks(long long n) {
    return n * n;
}

long long ternary_quantifier_checks(long long n) {
    return n * n * n;
}

void demonstrate_complexity() {
    cout << "\n=== Complexity ===\n";

    const long long n = 100;

    cout
        << "Unary checks: "
        << unary_quantifier_checks(n)
        << '\n';

    cout
        << "Binary nested checks: "
        << binary_quantifier_checks(n)
        << '\n';

    cout
        << "Ternary nested checks: "
        << ternary_quantifier_checks(n)
        << '\n';

    /*
     * Direct finite-model evaluation of k nested quantifiers can grow
     * approximately as O(n^k), where n is the domain size.
     *
     * Short-circuit evaluation can reduce the practical number of checks,
     * but it does not change the worst-case asymptotic structure.
     */
}

// -----------------------------------------------------------------------------
// 20. Security case study
// -----------------------------------------------------------------------------

void run_security_case_study() {
    cout << "\n";
    cout << "============================================================\n";
    cout << "SECURITY ACCESS-CONTROL CASE STUDY\n";
    cout << "============================================================\n";

    vector<Employee> employees{
        {
            101,
            "Alice",
            "Security",
            31,
            true,
            true,
            3
        },
        {
            102,
            "Bob",
            "Finance",
            29,
            true,
            false,
            1
        },
        {
            103,
            "Carol",
            "Engineering",
            17,
            false,
            true,
            2
        },
        {
            104,
            "David",
            "Security",
            44,
            true,
            true,
            2
        }
    };

    cout << "\nEmployees:\n";

    for (const auto& employee : employees) {
        print_employee(employee);
    }

    cout
        << "\n∀x Adult(x): "
        << every_employee_is_adult(employees)
        << '\n';

    cout
        << "∃x CanEnterSecureArea(x): "
        << at_least_one_employee_can_enter(employees)
        << '\n';

    cout
        << "∀x (Trained(x) -> Active(x)): "
        << every_trained_employee_is_active(employees)
        << '\n';

    cout
        << "∀x (Clearance(x) -> Trained(x)): "
        << every_cleared_employee_is_trained(employees)
        << '\n';

    report_secure_area_access(employees);

    /*
     * Extract a counterexample to:
     *
     *     ∀x (Trained(x) -> Active(x))
     *
     * A violation has:
     *
     *     Trained(x) == true
     *     Active(x) == false
     */
    auto violating_employee = find_if(
        employees.begin(),
        employees.end(),
        [](const Employee& employee) {
            return employee.trained && !employee.active;
        }
    );

    if (violating_employee != employees.end()) {
        cout
            << "\nCounterexample to trained -> active: "
            << violating_employee->name
            << '\n';
    } else {
        cout
            << "\nNo counterexample found.\n";
    }

    vector<AccessRequest> requests{
        {
            "Alice",
            "admin",
            "database",
            true,
            true
        },
        {
            "Bob",
            "user",
            "database",
            true,
            true
        },
        {
            "Carol",
            "admin",
            "database",
            true,
            false
        },
        {
            "David",
            "admin",
            "database",
            false,
            true
        }
    };

    report_authorization(requests);

    /*
     * Security limitation:
     *
     * Predicate logic can express policy conditions, but a real access
     * control system also needs authentication, secure credential handling,
     * authorization enforcement, auditing, revocation, identity lifecycle
     * management, failure handling, and protection against implementation
     * vulnerabilities.
     */
}

// -----------------------------------------------------------------------------
// 21. Relation properties
// -----------------------------------------------------------------------------

void demonstrate_relation_properties() {
    cout << "\n=== Relation Properties ===\n";

    vector<int> domain{1, 2, 3};

    auto equality = [](int x, int y) {
        return x == y;
    };

    cout
        << "Equality reflexive: "
        << is_reflexive(domain, equality)
        << '\n';

    cout
        << "Equality symmetric: "
        << is_symmetric(domain, equality)
        << '\n';

    cout
        << "Equality transitive: "
        << is_transitive(domain, equality)
        << '\n';
}

// -----------------------------------------------------------------------------
// 22. Assertions for logical laws
// -----------------------------------------------------------------------------

void run_assertions() {
    vector<int> domain{1, 2, 3, 4, 5};

    assert(exists(domain, is_even));
    assert(exists(domain, is_prime));
    assert(!forall(domain, is_even));

    const bool not_forall = !forall(domain, is_even);

    const bool exists_not = exists(
        domain,
        [](int value) {
            return !is_even(value);
        }
    );

    assert(not_forall == exists_not);

    const bool not_exists = !exists(domain, is_even);

    const bool forall_not = forall(
        domain,
        [](int value) {
            return !is_even(value);
        }
    );

    assert(not_exists == forall_not);

    assert(logical_implies(true, true));
    assert(logical_implies(false, true));
    assert(logical_implies(false, false));
    assert(!logical_implies(true, false));

    assert(logical_iff(true, true));
    assert(logical_iff(false, false));
    assert(!logical_iff(true, false));
}

// -----------------------------------------------------------------------------
// 23. Main
// -----------------------------------------------------------------------------

int main() {
    cout << "============================================================\n";
    cout << "PREDICATE LOGIC STUDY PROGRAM\n";
    cout << "============================================================\n";

    demonstrate_basic_predicates();
    demonstrate_basic_quantifiers();
    demonstrate_domain_and_vacuous_truth();
    demonstrate_quantifier_negation();
    demonstrate_quantifier_order();
    demonstrate_evidence();
    demonstrate_complexity();
    demonstrate_relation_properties();
    run_security_case_study();
    run_assertions();

    cout << "\n============================================================\n";
    cout << "All C++ predicate-logic demonstrations completed.\n";
    cout << "============================================================\n";

    return 0;
}
