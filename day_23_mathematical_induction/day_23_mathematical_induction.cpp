/*
 * MATHEMATICAL INDUCTION
 * ======================
 *
 * Industry-style C++ case study:
 *
 * A dependency-aware task planner whose correctness can be reasoned about
 * using mathematical induction.
 *
 * The program demonstrates:
 *
 * - Weak induction through one-step state transitions
 * - Strong induction through dependencies on arbitrary earlier states
 * - Base cases
 * - Recurrence-style computation
 * - Dynamic programming
 * - Graph-like dependency validation
 * - Topological ordering
 * - Cycle detection
 * - Input validation
 * - Error handling
 * - Complexity analysis
 * - Integer safety considerations
 *
 * Build:
 *
 *     g++ -std=c++17 -O2 -Wall -Wextra -pedantic induction_case_study.cpp -o induction_case_study
 *
 * Run:
 *
 *     ./induction_case_study
 */

#include <algorithm>
#include <cstdint>
#include <exception>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <queue>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>


// ---------------------------------------------------------------------------
// SECTION 1: BASIC DATA TYPES
// ---------------------------------------------------------------------------

struct Task {
    int id;
    std::string name;
    int duration;
    std::vector<int> dependencies;
};

struct ScheduleEntry {
    int taskId;
    int startTime;
    int finishTime;
};


// ---------------------------------------------------------------------------
// SECTION 2: UTILITY FUNCTIONS
// ---------------------------------------------------------------------------

void printSection(const std::string& title) {
    std::cout << "\n"
              << std::string(78, '=')
              << "\n"
              << title
              << "\n"
              << std::string(78, '=')
              << "\n";
}

void printSubsection(const std::string& title) {
    std::cout << "\n"
              << std::string(78, '-')
              << "\n"
              << title
              << "\n"
              << std::string(78, '-')
              << "\n";
}

void require(bool condition, const std::string& message) {
    if (!condition) {
        throw std::runtime_error(message);
    }
}


// ---------------------------------------------------------------------------
// SECTION 3: INTRODUCTION TO THE CASE STUDY
// ---------------------------------------------------------------------------

void explainInduction() {
    printSection("1. Mathematical induction and the case study");

    std::cout
        << "The central induction structure is:\n\n"
        << "  Base case:\n"
        << "      Establish P(n0).\n\n"
        << "  Inductive hypothesis:\n"
        << "      Assume P(k) for an arbitrary k in the domain.\n\n"
        << "  Inductive step:\n"
        << "      Establish P(k+1).\n\n"
        << "For strong induction, the hypothesis becomes:\n\n"
        << "      Assume P(j) for every n0 <= j <= k.\n\n"
        << "      Then establish P(k+1).\n\n"
        << "The case study models tasks whose completion depends on earlier tasks.\n"
        << "A valid schedule is built in dependency order.\n";
}


// ---------------------------------------------------------------------------
// SECTION 4: SIMPLE WEAK-INDUCTION EXAMPLE
// ---------------------------------------------------------------------------

std::int64_t arithmeticSum(std::int64_t n) {
    if (n < 0) {
        throw std::invalid_argument(
            "n must be non-negative."
        );
    }

    return n * (n + 1) / 2;
}

std::int64_t arithmeticSumLoop(std::int64_t n) {
    if (n < 0) {
        throw std::invalid_argument(
            "n must be non-negative."
        );
    }

    std::int64_t result = 0;

    for (std::int64_t value = 1; value <= n; ++value) {
        result += value;
    }

    return result;
}

void demonstrateWeakInduction() {
    printSection("2. Weak induction: arithmetic series");

    std::cout
        << "Claim:\n"
        << "    1 + 2 + ... + n = n(n+1)/2\n\n"
        << "Base case n=1:\n"
        << "    1 = 1(2)/2\n\n"
        << "Inductive hypothesis:\n"
        << "    Assume the formula holds for k.\n\n"
        << "Inductive step:\n"
        << "    S(k+1) = S(k) + (k+1)\n"
        << "           = k(k+1)/2 + (k+1)\n"
        << "           = (k+1)(k+2)/2.\n";

    for (std::int64_t n = 0; n <= 20; ++n) {
        require(
            arithmeticSum(n) == arithmeticSumLoop(n),
            "Arithmetic sum identity failed."
        );
    }

    std::cout << "Verified the identity for n=0 through n=20.\n";
}


// ---------------------------------------------------------------------------
// SECTION 5: STRONG INDUCTION CONCEPT
// ---------------------------------------------------------------------------

void demonstrateStrongInductionConcept() {
    printSection("3. Strong induction");

    std::cout
        << "Strong induction assumes all earlier propositions:\n\n"
        << "    P(n0), P(n0+1), ..., P(k)\n\n"
        << "The successor case may use any of these statements.\n\n"
        << "A natural example is prime factorization. A composite integer n\n"
        << "can be decomposed as n = ab where both a and b are smaller than n.\n"
        << "The proof therefore benefits from access to statements about all\n"
        << "smaller positive integers.\n";
}


// ---------------------------------------------------------------------------
// SECTION 6: PRIME FACTORIZATION
// ---------------------------------------------------------------------------

bool isPrime(int n) {
    if (n < 2) {
        return false;
    }

    if (n == 2) {
        return true;
    }

    if (n % 2 == 0) {
        return false;
    }

    for (int divisor = 3; divisor <= n / divisor; divisor += 2) {
        if (n % divisor == 0) {
            return false;
        }
    }

    return true;
}

std::vector<int> primeFactorization(int n) {
    if (n < 2) {
        throw std::invalid_argument(
            "Prime factorization requires n >= 2."
        );
    }

    if (isPrime(n)) {
        return {n};
    }

    for (int divisor = 2; divisor <= n / divisor; ++divisor) {
        if (n % divisor == 0) {
            std::vector<int> left = primeFactorization(divisor);
            std::vector<int> right = primeFactorization(n / divisor);

            left.insert(
                left.end(),
                right.begin(),
                right.end()
            );

            return left;
        }
    }

    return {n};
}

long long product(const std::vector<int>& values) {
    long long result = 1;

    for (int value : values) {
        result *= value;
    }

    return result;
}

void demonstratePrimeFactorization() {
    printSection("4. Strong induction case: prime factorization");

    const std::vector<int> examples = {
        2, 3, 4, 6, 12, 18, 60, 84, 97, 360
    };

    for (int number : examples) {
        const std::vector<int> factors =
            primeFactorization(number);

        std::cout << std::setw(4) << number << " = ";

        for (std::size_t index = 0; index < factors.size(); ++index) {
            if (index > 0) {
                std::cout << " * ";
            }

            std::cout << factors[index];
        }

        std::cout << "\n";

        require(
            product(factors) == number,
            "Prime factorization product is incorrect."
        );

        for (int factor : factors) {
            require(
                isPrime(factor),
                "Prime factorization produced a non-prime factor."
            );
        }
    }

    std::cout
        << "Every displayed factorization reconstructed the original number.\n";
}


// ---------------------------------------------------------------------------
// SECTION 7: TASK SCHEDULER
// ---------------------------------------------------------------------------

class TaskScheduler {
private:
    std::unordered_map<int, Task> tasks;

    void validateTaskId(int id) const {
        if (!tasks.contains(id)) {
            throw std::invalid_argument(
                "Unknown task ID: " + std::to_string(id)
            );
        }
    }

    void validateTask(const Task& task) const {
        if (task.id <= 0) {
            throw std::invalid_argument(
                "Task ID must be positive."
            );
        }

        if (task.name.empty()) {
            throw std::invalid_argument(
                "Task name cannot be empty."
            );
        }

        if (task.duration <= 0) {
            throw std::invalid_argument(
                "Task duration must be positive."
            );
        }

        for (int dependency : task.dependencies) {
            if (dependency == task.id) {
                throw std::invalid_argument(
                    "A task cannot depend directly on itself."
                );
            }
        }
    }

public:
    void addTask(
        int id,
        const std::string& name,
        int duration,
        const std::vector<int>& dependencies = {}
    ) {
        Task task{
            id,
            name,
            duration,
            dependencies
        };

        validateTask(task);

        if (tasks.contains(id)) {
            throw std::invalid_argument(
                "Duplicate task ID: " + std::to_string(id)
            );
        }

        tasks.emplace(id, std::move(task));
    }

    void validateDependencies() const {
        for (const auto& [id, task] : tasks) {
            for (int dependency : task.dependencies) {
                validateTaskId(dependency);
            }
        }
    }

    std::vector<int> topologicalOrder() const {
        validateDependencies();

        std::unordered_map<int, int> indegree;
        std::unordered_map<int, std::vector<int>> outgoing;

        for (const auto& [id, task] : tasks) {
            indegree[id] = static_cast<int>(
                task.dependencies.size()
            );

            for (int dependency : task.dependencies) {
                outgoing[dependency].push_back(id);
            }
        }

        std::priority_queue<
            int,
            std::vector<int>,
            std::greater<int>
        > ready;

        for (const auto& [id, degree] : indegree) {
            if (degree == 0) {
                ready.push(id);
            }
        }

        std::vector<int> order;
        order.reserve(tasks.size());

        while (!ready.empty()) {
            const int current = ready.top();
            ready.pop();

            order.push_back(current);

            for (int dependent : outgoing[current]) {
                --indegree[dependent];

                if (indegree[dependent] == 0) {
                    ready.push(dependent);
                }
            }
        }

        if (order.size() != tasks.size()) {
            throw std::runtime_error(
                "Dependency graph contains a cycle."
            );
        }

        return order;
    }

    std::vector<ScheduleEntry> buildSchedule() const {
        const std::vector<int> order = topologicalOrder();

        std::unordered_map<int, int> finishTime;
        std::vector<ScheduleEntry> schedule;
        schedule.reserve(order.size());

        for (int id : order) {
            const Task& task = tasks.at(id);

            int startTime = 0;

            for (int dependency : task.dependencies) {
                startTime = std::max(
                    startTime,
                    finishTime.at(dependency)
                );
            }

            const int finish = startTime + task.duration;

            finishTime[id] = finish;

            schedule.push_back({
                id,
                startTime,
                finish
            });
        }

        return schedule;
    }

    const Task& getTask(int id) const {
        validateTaskId(id);
        return tasks.at(id);
    }

    std::size_t size() const {
        return tasks.size();
    }
};


// ---------------------------------------------------------------------------
// SECTION 8: CASE-STUDY DATA
// ---------------------------------------------------------------------------

TaskScheduler buildExampleScheduler() {
    TaskScheduler scheduler;

    /*
     * The dependencies create the following conceptual structure:
     *
     * Requirements
     *      |
     * Architecture
     *   /       \
     * Backend   Frontend
     *   |          |
     * Testing <----+
     *      |
     * Deployment
     *      |
     * Monitoring
     *
     * Some tasks depend on multiple earlier tasks.
     */
    scheduler.addTask(
        1,
        "Requirements analysis",
        3
    );

    scheduler.addTask(
        2,
        "System architecture",
        4,
        {1}
    );

    scheduler.addTask(
        3,
        "Backend implementation",
        6,
        {2}
    );

    scheduler.addTask(
        4,
        "Frontend implementation",
        5,
        {2}
    );

    scheduler.addTask(
        5,
        "Integration testing",
        4,
        {3, 4}
    );

    scheduler.addTask(
        6,
        "Deployment",
        2,
        {5}
    );

    scheduler.addTask(
        7,
        "Production monitoring",
        3,
        {6}
    );

    return scheduler;
}


// ---------------------------------------------------------------------------
// SECTION 9: DEPENDENCY VALIDATION
// ---------------------------------------------------------------------------

void demonstrateValidation(TaskScheduler& scheduler) {
    printSection("5. Task dependency validation");

    scheduler.validateDependencies();

    std::cout
        << "Task count: "
        << scheduler.size()
        << "\n";

    std::cout
        << "All referenced dependencies exist.\n";
}


// ---------------------------------------------------------------------------
// SECTION 10: TOPOLOGICAL ORDER
// ---------------------------------------------------------------------------

void demonstrateTopologicalOrder(
    const TaskScheduler& scheduler
) {
    printSection("6. Dependency ordering");

    const std::vector<int> order =
        scheduler.topologicalOrder();

    std::cout << "Valid execution order:\n";

    for (std::size_t index = 0; index < order.size(); ++index) {
        const int taskId = order[index];

        std::cout
            << "  "
            << index + 1
            << ". "
            << scheduler.getTask(taskId).name
            << " [ID "
            << taskId
            << "]\n";
    }

    require(
        order.size() == scheduler.size(),
        "Topological order does not include every task."
    );
}


// ---------------------------------------------------------------------------
// SECTION 11: SCHEDULE GENERATION
// ---------------------------------------------------------------------------

void demonstrateSchedule(
    const TaskScheduler& scheduler
) {
    printSection("7. Complete schedule");

    const std::vector<ScheduleEntry> schedule =
        scheduler.buildSchedule();

    int projectFinish = 0;

    for (const ScheduleEntry& entry : schedule) {
        const Task& task =
            scheduler.getTask(entry.taskId);

        std::cout
            << std::left
            << std::setw(28)
            << task.name
            << " start="
            << std::setw(3)
            << entry.startTime
            << " finish="
            << std::setw(3)
            << entry.finishTime
            << "\n";

        projectFinish =
            std::max(projectFinish, entry.finishTime);
    }

    std::cout
        << "\nProject completion time: "
        << projectFinish
        << " time units.\n";
}


// ---------------------------------------------------------------------------
// SECTION 12: INDUCTION-STYLE CORRECTNESS ARGUMENT
// ---------------------------------------------------------------------------

void explainScheduleCorrectness() {
    printSection("8. Induction-style correctness argument");

    std::cout
        << "The scheduler can be reasoned about using strong induction over\n"
        << "the dependency order.\n\n"
        << "Base cases:\n"
        << "  Tasks with no dependencies can start at time zero.\n\n"
        << "Strong inductive hypothesis:\n"
        << "  Assume every dependency earlier in the topological order has a\n"
        << "  correct completion time.\n\n"
        << "Inductive step:\n"
        << "  For the next task, every dependency is already complete.\n"
        << "  Starting the task at the maximum dependency finish time prevents\n"
        << "  it from starting before any prerequisite is complete.\n\n"
        << "Conclusion:\n"
        << "  Every task receives a start time consistent with all dependencies.\n";
}


// ---------------------------------------------------------------------------
// SECTION 13: VERIFY SCHEDULE
// ---------------------------------------------------------------------------

void verifySchedule(
    const TaskScheduler& scheduler,
    const std::vector<ScheduleEntry>& schedule
) {
    std::unordered_map<int, ScheduleEntry> entries;

    for (const ScheduleEntry& entry : schedule) {
        entries[entry.taskId] = entry;
    }

    for (const ScheduleEntry& entry : schedule) {
        const Task& task =
            scheduler.getTask(entry.taskId);

        require(
            entry.finishTime - entry.startTime == task.duration,
            "Task duration does not match schedule."
        );

        for (int dependency : task.dependencies) {
            const ScheduleEntry& dependencyEntry =
                entries.at(dependency);

            require(
                dependencyEntry.finishTime <= entry.startTime,
                "Task begins before a dependency has finished."
            );
        }
    }
}

void demonstrateScheduleVerification(
    const TaskScheduler& scheduler
) {
    printSection("9. Automated schedule verification");

    const std::vector<ScheduleEntry> schedule =
        scheduler.buildSchedule();

    verifySchedule(scheduler, schedule);

    std::cout
        << "All task-duration and dependency constraints passed.\n";
}


// ---------------------------------------------------------------------------
// SECTION 14: CYCLE DETECTION EDGE CASE
// ---------------------------------------------------------------------------

void demonstrateCycleDetection() {
    printSection("10. Edge case: cyclic dependency");

    TaskScheduler cyclic;

    cyclic.addTask(
        1,
        "A",
        2,
        {3}
    );

    cyclic.addTask(
        2,
        "B",
        2,
        {1}
    );

    cyclic.addTask(
        3,
        "C",
        2,
        {2}
    );

    try {
        static_cast<void>(cyclic.topologicalOrder());

        throw std::runtime_error(
            "Expected cycle detection did not occur."
        );
    }
    catch (const std::runtime_error& error) {
        std::cout
            << "Expected failure detected: "
            << error.what()
            << "\n";
    }
}


// ---------------------------------------------------------------------------
// SECTION 15: MISSING DEPENDENCY EDGE CASE
// ---------------------------------------------------------------------------

void demonstrateMissingDependency() {
    printSection("11. Edge case: missing dependency");

    TaskScheduler invalid;

    invalid.addTask(
        1,
        "Task with missing prerequisite",
        2,
        {99}
    );

    try {
        static_cast<void>(invalid.topologicalOrder());

        throw std::runtime_error(
            "Expected missing-dependency failure did not occur."
        );
    }
    catch (const std::invalid_argument& error) {
        std::cout
            << "Expected failure detected: "
            << error.what()
            << "\n";
    }
}


// ---------------------------------------------------------------------------
// SECTION 16: INVALID TASK EDGE CASE
// ---------------------------------------------------------------------------

void demonstrateInvalidTask() {
    printSection("12. Edge case: invalid task duration");

    TaskScheduler scheduler;

    try {
        scheduler.addTask(
            1,
            "Invalid task",
            0
        );

        throw std::runtime_error(
            "Expected invalid-duration failure did not occur."
        );
    }
    catch (const std::invalid_argument& error) {
        std::cout
            << "Expected failure detected: "
            << error.what()
            << "\n";
    }
}


// ---------------------------------------------------------------------------
// SECTION 17: WEAK INDUCTION IN THE SCHEDULER
// ---------------------------------------------------------------------------

void explainWeakInductionInScheduler() {
    printSection("13. Where weak induction appears");

    std::cout
        << "A one-step recurrence can be viewed as weak induction.\n\n"
        << "Suppose a system state satisfies an invariant after processing\n"
        << "the first k tasks. If processing task k+1 preserves the invariant,\n"
        << "then the invariant holds after k+1 tasks.\n\n"
        << "The hypothesis concerns only the immediately preceding state.\n"
        << "This mirrors ordinary induction.\n";
}


// ---------------------------------------------------------------------------
// SECTION 18: STRONG INDUCTION IN THE SCHEDULER
// ---------------------------------------------------------------------------

void explainStrongInductionInScheduler() {
    printSection("14. Where strong induction appears");

    std::cout
        << "A task may depend on several earlier tasks rather than only the\n"
        << "immediately preceding task.\n\n"
        << "For example, integration testing depends on both backend and\n"
        << "frontend implementation.\n\n"
        << "A strong-induction proof can assume correctness for every earlier\n"
        << "dependency and then prove correctness for the current task.\n";
}


// ---------------------------------------------------------------------------
// SECTION 19: COMPLEXITY
// ---------------------------------------------------------------------------

void explainComplexity() {
    printSection("15. Complexity analysis");

    std::cout
        << "Let V be the number of tasks and E the number of dependency edges.\n\n"
        << "Dependency validation:\n"
        << "  O(V + E) after the task collection has been constructed.\n\n"
        << "Topological sorting with the priority queue:\n"
        << "  O((V + E) log V) in the general case.\n\n"
        << "Schedule construction:\n"
        << "  O(V + E), because each task and dependency is processed.\n\n"
        << "Memory:\n"
        << "  O(V + E) for task and graph-related structures.\n\n"
        << "The proof of correctness and the complexity analysis answer different\n"
        << "questions. Induction establishes a logical property; complexity\n"
        << "describes resource consumption.\n";
}


// ---------------------------------------------------------------------------
// SECTION 20: PROOF VERSUS TESTING
// ---------------------------------------------------------------------------

void explainProofVersusTesting() {
    printSection("16. Proof versus finite testing");

    std::cout
        << "The program can test many finite instances, but testing does not\n"
        << "replace a mathematical proof over an infinite domain.\n\n"
        << "For example, checking the first million integers can establish that\n"
        << "no counterexample was found in those million cases. It cannot by\n"
        << "itself establish truth for every larger integer.\n\n"
        << "Induction establishes a general base case plus a general propagation\n"
        << "rule. That is what gives the mathematical proof its universal scope.\n";
}


// ---------------------------------------------------------------------------
// SECTION 21: MULTIPLE BASE CASES
// ---------------------------------------------------------------------------

long long fibonacci(int n) {
    if (n < 0) {
        throw std::invalid_argument(
            "n must be non-negative."
        );
    }

    if (n == 0) {
        return 0;
    }

    if (n == 1) {
        return 1;
    }

    long long previous = 0;
    long long current = 1;

    for (int index = 2; index <= n; ++index) {
        const long long next =
            previous + current;

        previous = current;
        current = next;
    }

    return current;
}

void demonstrateMultipleBaseCases() {
    printSection("17. Multiple base cases");

    std::cout
        << "The Fibonacci recurrence is:\n"
        << "    F(n) = F(n-1) + F(n-2)\n\n"
        << "with:\n"
        << "    F(0) = 0\n"
        << "    F(1) = 1\n\n"
        << "Two initial cases are required for the recurrence.\n";

    const std::vector<long long> expected = {
        0, 1, 1, 2, 3, 5, 8, 13, 21, 34
    };

    for (int n = 0;
         n < static_cast<int>(expected.size());
         ++n) {

        require(
            fibonacci(n) == expected[n],
            "Fibonacci verification failed."
        );
    }

    std::cout
        << "Fibonacci base cases and recurrence verified.\n";
}


// ---------------------------------------------------------------------------
// SECTION 22: DIVISIBILITY
// ---------------------------------------------------------------------------

bool divides(long long divisor, long long value) {
    if (divisor == 0) {
        throw std::invalid_argument(
            "Divisor cannot be zero."
        );
    }

    return value % divisor == 0;
}

void demonstrateDivisibility() {
    printSection("18. Induction and divisibility");

    std::cout
        << "Claim:\n"
        << "    3 divides n^3-n for every integer n.\n\n"
        << "Inductive step:\n"
        << "    (k+1)^3-(k+1)\n"
        << "      = (k^3-k) + 3k^2 + 3k.\n\n"
        << "The first term is divisible by 3 by the hypothesis, and the other\n"
        << "terms are explicit multiples of 3.\n";

    for (int n = 1; n <= 50; ++n) {
        require(
            divides(3, static_cast<long long>(n) * n * n - n),
            "Divisibility identity failed."
        );
    }

    std::cout
        << "Divisibility identity verified for n=1 through n=50.\n";
}


// ---------------------------------------------------------------------------
// SECTION 23: INEQUALITY
// ---------------------------------------------------------------------------

void demonstrateInequality() {
    printSection("19. Induction and inequalities");

    std::cout
        << "Claim:\n"
        << "    2^n >= n+1 for n >= 0.\n\n"
        << "Base:\n"
        << "    2^0 = 1 >= 1.\n\n"
        << "Inductive step:\n"
        << "    2^(k+1) = 2*2^k\n"
        << "             >= 2(k+1)\n"
        << "             >= k+2.\n";
    
    for (int n = 0; n <= 30; ++n) {
        const long long power = 1LL << n;

        require(
            power >= static_cast<long long>(n) + 1,
            "Exponential inequality failed."
        );
    }

    std::cout
        << "Inequality verified for the selected exact integer range.\n";
}


// ---------------------------------------------------------------------------
// SECTION 24: STRUCTURAL INDUCTION
// ---------------------------------------------------------------------------

struct Expression {
    enum class Type {
        Number,
        Add
    };

    Type type;

    int value = 0;

    std::unique_ptr<Expression> left;
    std::unique_ptr<Expression> right;

    static std::unique_ptr<Expression> number(int value) {
        auto expression =
            std::make_unique<Expression>();

        expression->type = Type::Number;
        expression->value = value;

        return expression;
    }

    static std::unique_ptr<Expression> add(
        std::unique_ptr<Expression> left,
        std::unique_ptr<Expression> right
    ) {
        auto expression =
            std::make_unique<Expression>();

        expression->type = Type::Add;
        expression->left = std::move(left);
        expression->right = std::move(right);

        return expression;
    }
};

int countExpressionNodes(const Expression& expression) {
    if (expression.type == Expression::Type::Number) {
        return 1;
    }

    return 1
        + countExpressionNodes(*expression.left)
        + countExpressionNodes(*expression.right);
}

void demonstrateStructuralInduction() {
    printSection("20. Structural induction");

    std::cout
        << "Structural induction applies induction to recursively constructed\n"
        << "objects.\n\n"
        << "For an expression grammar containing numbers and addition:\n\n"
        << "    Expression ::= Number\n"
        << "                | Expression + Expression\n\n"
        << "A structural property can be proved by handling the Number base\n"
        << "constructor and the recursive Add constructor.\n";

    auto expression =
        Expression::add(
            Expression::add(
                Expression::number(1),
                Expression::number(2)
            ),
            Expression::number(3)
        );

    require(
        countExpressionNodes(*expression) == 5,
        "Expression node count is incorrect."
    );

    std::cout
        << "Structural expression contains 5 nodes.\n";
}


// ---------------------------------------------------------------------------
// SECTION 25: PROOF DESIGN CHECKLIST
// ---------------------------------------------------------------------------

void printProofChecklist() {
    printSection("21. Proof-design checklist");

    const std::vector<std::string> checklist = {
        "State P(n) precisely.",
        "State the domain.",
        "Identify the first required value.",
        "Verify the base case or base cases.",
        "Choose weak or strong induction deliberately.",
        "State the inductive hypothesis precisely.",
        "Treat the induction variable as arbitrary.",
        "Do not assume the target statement.",
        "Use only justified assumptions.",
        "Establish the successor case.",
        "State the conclusion over the entire domain."
    };

    for (std::size_t index = 0;
         index < checklist.size();
         ++index) {

        std::cout
            << std::setw(2)
            << index + 1
            << ". "
            << checklist[index]
            << "\n";
    }
}


// ---------------------------------------------------------------------------
// SECTION 26: SOFTWARE ENGINEERING CONSIDERATIONS
// ---------------------------------------------------------------------------

void explainEngineeringConsiderations() {
    printSection("22. Engineering considerations");

    std::cout
        << "A mathematical proof may establish that an algorithm is correct\n"
        << "under its assumptions. Production software must also account for:\n\n"
        << "  - Invalid input\n"
        << "  - Missing dependencies\n"
        << "  - Cyclic dependencies\n"
        << "  - Integer overflow\n"
        << "  - Resource limits\n"
        << "  - Memory consumption\n"
        << "  - Exception handling\n"
        << "  - Deterministic behavior\n"
        << "  - Testing and observability\n\n"
        << "C++ requires particular care with integer overflow and object lifetime.\n"
        << "The standard library containers used here manage most ordinary memory\n"
        << "ownership concerns through RAII and value semantics.\n";
}


// ---------------------------------------------------------------------------
// SECTION 27: MAIN
// ---------------------------------------------------------------------------

int main() {
    try {
        explainInduction();

        demonstrateWeakInduction();

        demonstrateStrongInductionConcept();

        demonstratePrimeFactorization();

        TaskScheduler scheduler =
            buildExampleScheduler();

        demonstrateValidation(scheduler);

        demonstrateTopologicalOrder(scheduler);

        demonstrateSchedule(scheduler);

        explainScheduleCorrectness();

        demonstrateScheduleVerification(scheduler);

        demonstrateCycleDetection();

        demonstrateMissingDependency();

        demonstrateInvalidTask();

        explainWeakInductionInScheduler();

        explainStrongInductionInScheduler();

        explainComplexity();

        explainProofVersusTesting();

        demonstrateMultipleBaseCases();

        demonstrateDivisibility();

        demonstrateInequality();

        demonstrateStructuralInduction();

        printProofChecklist();

        explainEngineeringConsiderations();

        printSection("23. Case study verification complete");

        std::cout
            << "All mathematical examples and scheduler checks passed.\n"
            << "The program completed without an unexpected failure.\n";

        return 0;
    }
    catch (const std::exception& error) {
        std::cerr
            << "ERROR: "
            << error.what()
            << "\n";

        return 1;
    }
}
