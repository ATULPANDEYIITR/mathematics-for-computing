#include <algorithm>
#include <cassert>
#include <functional>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

/*
 * Quantifier Logic
 * =================
 *
 * Industry-style case study:
 *
 * A course-management and access-control validation engine uses first-order
 * quantifier patterns to validate users, courses, enrollments, permissions,
 * and relationships.
 *
 * The program demonstrates:
 *
 *   ∀x P(x)
 *   ∃x P(x)
 *   ∀x ∃y R(x,y)
 *   ∃y ∀x R(x,y)
 *   ¬∀x P(x) ≡ ∃x ¬P(x)
 *   ¬∃x P(x) ≡ ∀x ¬P(x)
 *
 * The implementation uses finite collections because unrestricted first-order
 * logic is not directly executable by ordinary C++ containers.
 *
 * C++17 is sufficient.
 */


// ============================================================================
// SECTION 1: OUTPUT HELPERS
// ============================================================================

void section(const std::string& title) {
    std::cout << "\n" << std::string(78, '=') << "\n";
    std::cout << title << "\n";
    std::cout << std::string(78, '=') << "\n";
}

void explain(const std::string& text) {
    std::cout << text << "\n";
}


// ============================================================================
// SECTION 2: GENERIC QUANTIFIER FUNCTIONS
// ============================================================================

template <typename Container, typename Predicate>
bool forall(const Container& domain, Predicate predicate) {
    /*
     * Universal quantification:
     *
     *     ∀x P(x)
     *
     * is true exactly when every domain element satisfies P.
     *
     * The function short-circuits on the first counterexample.
     */
    for (const auto& value : domain) {
        if (!predicate(value)) {
            return false;
        }
    }

    // Empty-domain universal quantification is true.
    return true;
}


template <typename Container, typename Predicate>
bool exists(const Container& domain, Predicate predicate) {
    /*
     * Existential quantification:
     *
     *     ∃x P(x)
     *
     * is true when at least one domain element satisfies P.
     *
     * The function short-circuits on the first witness.
     */
    for (const auto& value : domain) {
        if (predicate(value)) {
            return true;
        }
    }

    return false;
}


// ============================================================================
// SECTION 3: DOMAIN MODEL
// ============================================================================

struct Student {
    std::string name;
    int age;
};

struct Course {
    std::string code;
    std::string name;
};

struct User {
    std::string name;
};

struct Permission {
    std::string user;
    std::string resource;

    bool operator<(const Permission& other) const {
        return std::tie(user, resource) <
               std::tie(other.user, other.resource);
    }
};

struct Enrollment {
    std::string student;
    std::string course;

    bool operator<(const Enrollment& other) const {
        return std::tie(student, course) <
               std::tie(other.student, other.course);
    }
};

struct Result {
    std::string student;
    std::string course;
    bool passed;

    bool operator<(const Result& other) const {
        return std::tie(student, course) <
               std::tie(other.student, other.course);
    }
};


// ============================================================================
// SECTION 4: COURSE MANAGEMENT SYSTEM
// ============================================================================

class CourseManagementSystem {
private:
    std::vector<Student> students_;
    std::vector<Course> courses_;

    std::set<Enrollment> enrollments_;
    std::set<Result> results_;

public:
    CourseManagementSystem(
        std::vector<Student> students,
        std::vector<Course> courses
    )
        : students_(std::move(students)),
          courses_(std::move(courses)) {}

    const std::vector<Student>& students() const {
        return students_;
    }

    const std::vector<Course>& courses() const {
        return courses_;
    }

    bool isEnrolled(
        const std::string& student,
        const std::string& course
    ) const {
        return enrollments_.contains({student, course});
    }

    void enroll(
        const std::string& student,
        const std::string& course
    ) {
        if (!studentExists(student)) {
            throw std::invalid_argument(
                "Cannot enroll unknown student: " + student
            );
        }

        if (!courseExists(course)) {
            throw std::invalid_argument(
                "Cannot enroll in unknown course: " + course
            );
        }

        enrollments_.insert({student, course});
    }

    void recordResult(
        const std::string& student,
        const std::string& course,
        bool passed
    ) {
        if (!isEnrolled(student, course)) {
            throw std::invalid_argument(
                "A result cannot be recorded for a non-enrolled student."
            );
        }

        results_.insert({student, course, passed});
    }

    bool passed(
        const std::string& student,
        const std::string& course
    ) const {
        auto iterator = results_.find({student, course, true});

        return iterator != results_.end();
    }

    bool studentExists(const std::string& name) const {
        return exists(
            students_,
            [&](const Student& student) {
                return student.name == name;
            }
        );
    }

    bool courseExists(const std::string& code) const {
        return exists(
            courses_,
            [&](const Course& course) {
                return course.code == code;
            }
        );
    }

    bool everyStudentEnrolledSomewhere() const {
        /*
         * Formula:
         *
         *     ∀s ∃c Enrolled(s,c)
         *
         * Each student may have a different course.
         */
        return forall(
            students_,
            [&](const Student& student) {
                return exists(
                    courses_,
                    [&](const Course& course) {
                        return isEnrolled(
                            student.name,
                            course.code
                        );
                    }
                );
            }
        );
    }

    bool everyStudentPassedAtLeastOneCourse() const {
        /*
         * Formula:
         *
         *     ∀s ∃c Passed(s,c)
         */
        return forall(
            students_,
            [&](const Student& student) {
                return exists(
                    courses_,
                    [&](const Course& course) {
                        return passed(
                            student.name,
                            course.code
                        );
                    }
                );
            }
        );
    }

    bool someCoursePassedByEveryStudent() const {
        /*
         * Formula:
         *
         *     ∃c ∀s Passed(s,c)
         *
         * One common course must work for every student.
         */
        return exists(
            courses_,
            [&](const Course& course) {
                return forall(
                    students_,
                    [&](const Student& student) {
                        return passed(
                            student.name,
                            course.code
                        );
                    }
                );
            }
        );
    }

    std::optional<Student> studentWhoPassedNothing() const {
        /*
         * This searches for a witness to:
         *
         *     ∃s ∀c ¬Passed(s,c)
         *
         * This is the logical negation of:
         *
         *     ∀s ∃c Passed(s,c)
         */
        for (const Student& student : students_) {
            bool passedSomething = exists(
                courses_,
                [&](const Course& course) {
                    return passed(
                        student.name,
                        course.code
                    );
                }
            );

            if (!passedSomething) {
                return student;
            }
        }

        return std::nullopt;
    }

    std::vector<std::string> studentsWithoutEnrollment() const {
        std::vector<std::string> result;

        for (const Student& student : students_) {
            bool enrolledSomewhere = exists(
                courses_,
                [&](const Course& course) {
                    return isEnrolled(
                        student.name,
                        course.code
                    );
                }
            );

            if (!enrolledSomewhere) {
                result.push_back(student.name);
            }
        }

        return result;
    }
};


// ============================================================================
// SECTION 5: ACCESS CONTROL SYSTEM
// ============================================================================

class AccessControlSystem {
private:
    std::vector<User> users_;
    std::vector<std::string> resources_;
    std::set<Permission> permissions_;

public:
    AccessControlSystem(
        std::vector<User> users,
        std::vector<std::string> resources
    )
        : users_(std::move(users)),
          resources_(std::move(resources)) {}

    void grant(
        const std::string& user,
        const std::string& resource
    ) {
        if (!userExists(user)) {
            throw std::invalid_argument(
                "Cannot grant permission to unknown user."
            );
        }

        if (!resourceExists(resource)) {
            throw std::invalid_argument(
                "Cannot grant access to unknown resource."
            );
        }

        permissions_.insert({user, resource});
    }

    bool userExists(const std::string& name) const {
        return exists(
            users_,
            [&](const User& user) {
                return user.name == name;
            }
        );
    }

    bool resourceExists(const std::string& resource) const {
        return std::find(
            resources_.begin(),
            resources_.end(),
            resource
        ) != resources_.end();
    }

    bool authorized(
        const std::string& user,
        const std::string& resource
    ) const {
        return permissions_.contains({user, resource});
    }

    bool everyUserHasSomePermission() const {
        /*
         * Formula:
         *
         *     ∀u ∃r Authorized(u,r)
         *
         * Each user may have a different authorized resource.
         */
        return forall(
            users_,
            [&](const User& user) {
                return exists(
                    resources_,
                    [&](const std::string& resource) {
                        return authorized(
                            user.name,
                            resource
                        );
                    }
                );
            }
        );
    }

    bool someResourceIsAvailableToEveryone() const {
        /*
         * Formula:
         *
         *     ∃r ∀u Authorized(u,r)
         *
         * A single shared resource must be authorized for everyone.
         */
        return exists(
            resources_,
            [&](const std::string& resource) {
                return forall(
                    users_,
                    [&](const User& user) {
                        return authorized(
                            user.name,
                            resource
                        );
                    }
                );
            }
        );
    }

    std::optional<User> userWithNoPermission() const {
        /*
         * Negation of:
         *
         *     ∀u ∃r Authorized(u,r)
         *
         * is:
         *
         *     ∃u ∀r ¬Authorized(u,r)
         */
        for (const User& user : users_) {
            bool hasPermission = exists(
                resources_,
                [&](const std::string& resource) {
                    return authorized(
                        user.name,
                        resource
                    );
                }
            );

            if (!hasPermission) {
                return user;
            }
        }

        return std::nullopt;
    }
};


// ============================================================================
// SECTION 6: BASIC LOGIC DEMONSTRATIONS
// ============================================================================

void demonstrateBasicQuantifiers() {
    section("1. Basic quantifier evaluation");

    std::vector<int> numbers{-3, -2, -1, 0, 1, 2, 3};

    std::cout
        << "∀x (x < 10): "
        << std::boolalpha
        << forall(numbers, [](int x) {
            return x < 10;
        })
        << "\n";

    std::cout
        << "∀x (x > 0): "
        << forall(numbers, [](int x) {
            return x > 0;
        })
        << "\n";

    std::cout
        << "∃x (x == 2): "
        << exists(numbers, [](int x) {
            return x == 2;
        })
        << "\n";

    std::cout
        << "∃x (x > 100): "
        << exists(numbers, [](int x) {
            return x > 100;
        })
        << "\n";
}


// ============================================================================
// SECTION 7: NEGATION RULES
// ============================================================================

void demonstrateNegation() {
    section("2. Negating quantified statements");

    std::vector<int> numbers{1, 2, 3, 4, 5};

    auto predicate = [](int x) {
        return x < 10;
    };

    bool universal = forall(numbers, predicate);
    bool negatedUniversal =
        !forall(numbers, predicate);

    bool equivalentForm =
        exists(numbers, [&](int x) {
            return !predicate(x);
        });

    std::cout << "∀x P(x): " << universal << "\n";
    std::cout << "¬∀x P(x): " << negatedUniversal << "\n";
    std::cout << "∃x ¬P(x): " << equivalentForm << "\n";

    assert(
        negatedUniversal == equivalentForm
    );

    auto secondPredicate = [](int x) {
        return x > 3;
    };

    bool negatedExistential =
        !exists(numbers, secondPredicate);

    bool equivalentUniversal =
        forall(numbers, [&](int x) {
            return !secondPredicate(x);
        });

    std::cout
        << "¬∃x Q(x): "
        << negatedExistential
        << "\n";

    std::cout
        << "∀x ¬Q(x): "
        << equivalentUniversal
        << "\n";

    assert(
        negatedExistential ==
        equivalentUniversal
    );

    explain(
        "\nThe implemented equivalences are:\n"
        "    ¬∀x P(x) ≡ ∃x ¬P(x)\n"
        "    ¬∃x P(x) ≡ ∀x ¬P(x)\n"
    );
}


// ============================================================================
// SECTION 8: QUANTIFIER ORDER
// ============================================================================

void demonstrateQuantifierOrder() {
    section("3. Quantifier order");

    std::vector<std::string> employees{
        "Alice",
        "Bob",
        "Carol"
    };

    std::vector<std::string> projects{
        "P1",
        "P2"
    };

    std::set<std::pair<std::string, std::string>> assignments{
        {"Alice", "P1"},
        {"Bob", "P2"},
        {"Carol", "P1"}
    };

    auto assigned = [&](const std::string& employee,
                        const std::string& project) {
        return assignments.contains(
            {employee, project}
        );
    };

    bool everyEmployeeHasAProject = forall(
        employees,
        [&](const std::string& employee) {
            return exists(
                projects,
                [&](const std::string& project) {
                    return assigned(
                        employee,
                        project
                    );
                }
            );
        }
    );

    bool oneProjectHasEveryEmployee = exists(
        projects,
        [&](const std::string& project) {
            return forall(
                employees,
                [&](const std::string& employee) {
                    return assigned(
                        employee,
                        project
                    );
                }
            );
        }
    );

    std::cout
        << "∀employee ∃project Assigned(employee, project): "
        << everyEmployeeHasAProject
        << "\n";

    std::cout
        << "∃project ∀employee Assigned(employee, project): "
        << oneProjectHasEveryEmployee
        << "\n";
}


// ============================================================================
// SECTION 9: EMPTY DOMAIN AND VACUOUS TRUTH
// ============================================================================

void demonstrateEmptyDomain() {
    section("4. Empty-domain behavior");

    std::vector<int> empty;

    bool universal = forall(
        empty,
        [](int x) {
            return x > 100;
        }
    );

    bool existential = exists(
        empty,
        [](int x) {
            return x > 100;
        }
    );

    std::cout
        << "∀x (x > 100) over empty domain: "
        << universal
        << "\n";

    std::cout
        << "∃x (x > 100) over empty domain: "
        << existential
        << "\n";

    assert(universal);
    assert(!existential);
}


// ============================================================================
// SECTION 10: FORMAL LOGIC AST
// ============================================================================

class Formula {
public:
    virtual ~Formula() = default;

    virtual bool evaluate(
        const std::map<std::string, int>& environment
    ) const = 0;
};


class Predicate : public Formula {
private:
    std::function<bool(int)> predicate_;
    std::string variable_;

public:
    Predicate(
        std::string variable,
        std::function<bool(int)> predicate
    )
        : predicate_(std::move(predicate)),
          variable_(std::move(variable)) {}

    bool evaluate(
        const std::map<std::string, int>& environment
    ) const override {
        auto iterator = environment.find(variable_);

        if (iterator == environment.end()) {
            throw std::runtime_error(
                "Free variable has no value."
            );
        }

        return predicate_(iterator->second);
    }
};


class NotFormula : public Formula {
private:
    const Formula& operand_;

public:
    explicit NotFormula(const Formula& operand)
        : operand_(operand) {}

    bool evaluate(
        const std::map<std::string, int>& environment
    ) const override {
        return !operand_.evaluate(environment);
    }
};


class AndFormula : public Formula {
private:
    const Formula& left_;
    const Formula& right_;

public:
    AndFormula(
        const Formula& left,
        const Formula& right
    )
        : left_(left),
          right_(right) {}

    bool evaluate(
        const std::map<std::string, int>& environment
    ) const override {
        return
            left_.evaluate(environment) &&
            right_.evaluate(environment);
    }
};


class OrFormula : public Formula {
private:
    const Formula& left_;
    const Formula& right_;

public:
    OrFormula(
        const Formula& left,
        const Formula& right
    )
        : left_(left),
          right_(right) {}

    bool evaluate(
        const std::map<std::string, int>& environment
    ) const override {
        return
            left_.evaluate(environment) ||
            right_.evaluate(environment);
    }
};


class ImpliesFormula : public Formula {
private:
    const Formula& antecedent_;
    const Formula& consequent_;

public:
    ImpliesFormula(
        const Formula& antecedent,
        const Formula& consequent
    )
        : antecedent_(antecedent),
          consequent_(consequent) {}

    bool evaluate(
        const std::map<std::string, int>& environment
    ) const override {
        return
            !antecedent_.evaluate(environment) ||
            consequent_.evaluate(environment);
    }
};


class ForAllFormula : public Formula {
private:
    std::string variable_;
    const std::vector<int>& domain_;
    const Formula& body_;

public:
    ForAllFormula(
        std::string variable,
        const std::vector<int>& domain,
        const Formula& body
    )
        : variable_(std::move(variable)),
          domain_(domain),
          body_(body) {}

    bool evaluate(
        const std::map<std::string, int>& environment
    ) const override {
        for (int value : domain_) {
            auto extended = environment;
            extended[variable_] = value;

            if (!body_.evaluate(extended)) {
                return false;
            }
        }

        return true;
    }
};


class ExistsFormula : public Formula {
private:
    std::string variable_;
    const std::vector<int>& domain_;
    const Formula& body_;

public:
    ExistsFormula(
        std::string variable,
        const std::vector<int>& domain,
        const Formula& body
    )
        : variable_(std::move(variable)),
          domain_(domain),
          body_(body) {}

    bool evaluate(
        const std::map<std::string, int>& environment
    ) const override {
        for (int value : domain_) {
            auto extended = environment;
            extended[variable_] = value;

            if (body_.evaluate(extended)) {
                return true;
            }
        }

        return false;
    }
};


void demonstrateFormulaTree() {
    section("5. Executable formula tree");

    std::vector<int> domain{1, 2, 3, 4, 5};

    Predicate positive(
        "x",
        [](int x) {
            return x > 0;
        }
    );

    Predicate lessThanTen(
        "x",
        [](int x) {
            return x < 10;
        }
    );

    AndFormula both(
        positive,
        lessThanTen
    );

    ForAllFormula formula(
        "x",
        domain,
        both
    );

    std::map<std::string, int> environment;

    std::cout
        << "Formula: ∀x (Positive(x) ∧ LessThanTen(x))\n";

    std::cout
        << "Result: "
        << formula.evaluate(environment)
        << "\n";
}


// ============================================================================
// SECTION 11: COURSE CASE STUDY
// ============================================================================

void demonstrateCourseCaseStudy() {
    section("6. Course-management case study");

    CourseManagementSystem system(
        {
            {"Alice", 20},
            {"Bob", 21},
            {"Carol", 22},
            {"David", 23}
        },
        {
            {"MATH101", "Mathematics"},
            {"PHY101", "Physics"},
            {"CS101", "Programming"}
        }
    );

    system.enroll("Alice", "MATH101");
    system.enroll("Alice", "CS101");

    system.enroll("Bob", "PHY101");

    system.enroll("Carol", "MATH101");
    system.enroll("Carol", "PHY101");
    system.enroll("Carol", "CS101");

    system.enroll("David", "CS101");

    system.recordResult(
        "Alice",
        "MATH101",
        true
    );

    system.recordResult(
        "Alice",
        "CS101",
        true
    );

    system.recordResult(
        "Bob",
        "PHY101",
        true
    );

    system.recordResult(
        "Carol",
        "MATH101",
        true
    );

    system.recordResult(
        "Carol",
        "PHY101",
        true
    );

    system.recordResult(
        "Carol",
        "CS101",
        false
    );

    system.recordResult(
        "David",
        "CS101",
        false
    );

    std::cout
        << "∀student ∃course Enrolled(student, course): "
        << system.everyStudentEnrolledSomewhere()
        << "\n";

    std::cout
        << "∀student ∃course Passed(student, course): "
        << system.everyStudentPassedAtLeastOneCourse()
        << "\n";

    std::cout
        << "∃course ∀student Passed(student, course): "
        << system.someCoursePassedByEveryStudent()
        << "\n";

    auto studentWithoutPass =
        system.studentWhoPassedNothing();

    if (studentWithoutPass.has_value()) {
        std::cout
            << "Witness for ∃student ∀course ¬Passed(student, course): "
            << studentWithoutPass->name
            << "\n";
    } else {
        std::cout
            << "No student was found who failed every course.\n";
    }

    explain(
        "\nThe case study converts quantified requirements into executable "
        "validation rules.\n"
        "\nThe formula:\n"
        "    ∀s ∃c Passed(s,c)\n"
        "\nmeans every student has at least one course they passed.\n"
        "\nIts negation is:\n"
        "    ∃s ∀c ¬Passed(s,c)\n"
        "\nwhich identifies a student who passed no course.\n"
    );
}


// ============================================================================
// SECTION 12: ACCESS CONTROL CASE STUDY
// ============================================================================

void demonstrateAccessControlCaseStudy() {
    section("7. Access-control case study");

    AccessControlSystem accessControl(
        {
            {"Alice"},
            {"Bob"},
            {"Carol"}
        },
        {
            "database",
            "server",
            "reports"
        }
    );

    accessControl.grant(
        "Alice",
        "database"
    );

    accessControl.grant(
        "Alice",
        "reports"
    );

    accessControl.grant(
        "Bob",
        "reports"
    );

    accessControl.grant(
        "Carol",
        "database"
    );

    accessControl.grant(
        "Carol",
        "server"
    );

    std::cout
        << "∀user ∃resource Authorized(user, resource): "
        << accessControl.everyUserHasSomePermission()
        << "\n";

    std::cout
        << "∃resource ∀user Authorized(user, resource): "
        << accessControl.someResourceIsAvailableToEveryone()
        << "\n";

    auto userWithoutPermission =
        accessControl.userWithNoPermission();

    if (userWithoutPermission.has_value()) {
        std::cout
            << "User with no permission: "
            << userWithoutPermission->name
            << "\n";
    } else {
        std::cout
            << "Every user has at least one permission.\n";
    }

    explain(
        "\nSecurity interpretation:\n"
        "\n"
        "    ∀u ∃r Authorized(u,r)\n"
        "\n"
        "does not mean every user has access to every resource. It only says "
        "that each user has at least one authorized resource.\n"
    );
}


// ============================================================================
// SECTION 13: QUANTIFIER NEGATION TESTS
// ============================================================================

void runQuantifierTests() {
    section("8. Automated logical tests");

    std::vector<std::vector<int>> domains{
        {},
        {0},
        {1, 2, 3},
        {-2, -1, 0, 1, 2}
    };

    std::vector<std::function<bool(int)>> predicates{
        [](int x) {
            return x > 0;
        },
        [](int x) {
            return x % 2 == 0;
        },
        [](int x) {
            return x == 42;
        }
    };

    for (const auto& domain : domains) {
        for (const auto& predicate : predicates) {
            bool leftUniversal =
                !forall(domain, predicate);

            bool rightUniversal =
                exists(
                    domain,
                    [&](int x) {
                        return !predicate(x);
                    }
                );

            assert(
                leftUniversal == rightUniversal
            );

            bool leftExistential =
                !exists(domain, predicate);

            bool rightExistential =
                forall(
                    domain,
                    [&](int x) {
                        return !predicate(x);
                    }
                );

            assert(
                leftExistential == rightExistential
            );
        }
    }

    std::cout
        << "All quantifier-negation tests passed.\n";
}


// ============================================================================
// SECTION 14: PERFORMANCE CONSIDERATIONS
// ============================================================================

bool everyItemHasRelatedItem(
    const std::vector<int>& outerDomain,
    const std::vector<int>& innerDomain,
    const std::function<bool(int, int)>& relation
) {
    /*
     * Evaluates:
     *
     *     ∀x ∃y R(x,y)
     *
     * Worst-case complexity:
     *
     *     O(|X| * |Y|)
     *
     * Short-circuiting can reduce actual work.
     */
    for (int x : outerDomain) {
        bool found = false;

        for (int y : innerDomain) {
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


void demonstratePerformance() {
    section("9. Performance considerations");

    std::vector<int> users(100);
    std::vector<int> resources(100);

    for (int i = 0; i < 100; ++i) {
        users[i] = i + 1;
        resources[i] = i + 1;
    }

    bool result = everyItemHasRelatedItem(
        users,
        resources,
        [](int user, int resource) {
            return user == resource;
        }
    );

    std::cout
        << "∀user ∃resource user == resource: "
        << result
        << "\n";

    explain(
        "\nA direct nested scan may require O(n*m) relation checks. "
        "When a relation is stored as a set, map, or indexed database "
        "structure, membership testing can be much faster in practice.\n"
    );
}


// ============================================================================
// SECTION 15: ERROR HANDLING
// ============================================================================

void demonstrateValidationErrors() {
    section("10. Validation and failure conditions");

    CourseManagementSystem system(
        {
            {"Alice", 20}
        },
        {
            {"CS101", "Programming"}
        }
    );

    try {
        system.enroll(
            "UnknownStudent",
            "CS101"
        );
    } catch (const std::invalid_argument& error) {
        std::cout
            << "Caught validation error: "
            << error.what()
            << "\n";
    }

    try {
        system.enroll(
            "Alice",
            "UNKNOWN"
        );
    } catch (const std::invalid_argument& error) {
        std::cout
            << "Caught validation error: "
            << error.what()
            << "\n";
    }

    try {
        system.recordResult(
            "Alice",
            "CS101",
            true
        );
    } catch (const std::invalid_argument& error) {
        std::cout
            << "Caught validation error: "
            << error.what()
            << "\n";
    }
}


// ============================================================================
// SECTION 16: MAIN
// ============================================================================

int main() {
    std::cout
        << std::boolalpha;

    section(
        "Quantifier Logic: C++17 Technical Case Study"
    );

    demonstrateBasicQuantifiers();
    demonstrateNegation();
    demonstrateQuantifierOrder();
    demonstrateEmptyDomain();
    demonstrateFormulaTree();
    demonstrateCourseCaseStudy();
    demonstrateAccessControlCaseStudy();
    runQuantifierTests();
    demonstratePerformance();
    demonstrateValidationErrors();

    section("Case study complete");

    std::cout
        << "The program demonstrated quantified logic through "
        << "finite-domain algorithms, formula objects, course validation, "
        << "access-control rules, testing, error handling, and complexity "
        << "considerations.\n";

    return 0;
}
