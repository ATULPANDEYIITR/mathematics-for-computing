/*
 * Solving Recurrences
 * ====================
 *
 * Technical case study:
 * A recursive task scheduler estimates the cost of processing a dependency
 * tree. The scheduler uses recurrence relations to predict work before
 * execution and then validates those predictions against measured values.
 *
 * The program demonstrates:
 * - Iterative recurrence expansion
 * - First-order recurrence solutions
 * - Characteristic equations
 * - Distinct and repeated roots
 * - Non-homogeneous recurrences
 * - Matrix exponentiation
 * - Overflow-aware arithmetic
 * - Validation and complexity analysis
 *
 * C++17 or later.
 */

#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

using namespace std;


// ---------------------------------------------------------------------------
// Domain model
// ---------------------------------------------------------------------------

struct WorkEstimate {
    long long taskCount;
    long long estimatedOperations;
};

class RecurrenceModel {
public:
    virtual ~RecurrenceModel() = default;

    virtual long long next(
        size_t n,
        const vector<long long>& values
    ) const = 0;
};


// ---------------------------------------------------------------------------
// First-order additive workload:
//
// T(n) = T(n-1) + n
//
// This models a staged pipeline where each new stage introduces n units of
// additional processing.
// ---------------------------------------------------------------------------

class IncrementalWorkload final : public RecurrenceModel {
public:
    long long next(
        size_t n,
        const vector<long long>& values
    ) const override {
        if (values.empty()) {
            throw logic_error("A base value is required.");
        }

        if (n >= values.size() + 1) {
            throw logic_error("Recurrence state is inconsistent.");
        }

        return values[n - 1] + static_cast<long long>(n);
    }
};


// ---------------------------------------------------------------------------
// Evaluate a first-order recurrence iteratively.
// ---------------------------------------------------------------------------

vector<long long> generateSequence(
    long long initial,
    size_t count,
    const RecurrenceModel& model
) {
    if (count == 0) {
        return {};
    }

    vector<long long> values;
    values.reserve(count);
    values.push_back(initial);

    for (size_t n = 1; n < count; ++n) {
        const long long value = model.next(n, values);
        values.push_back(value);
    }

    return values;
}


// ---------------------------------------------------------------------------
// Closed form:
//
// T(n) = aT(n-1) + b
//
// a != 1:
//
// T(n) = a^n T(0) + b(a^n - 1)/(a - 1)
//
// a = 1:
//
// T(n) = T(0) + bn
// ---------------------------------------------------------------------------

long double firstOrderClosedForm(
    int n,
    long double a,
    long double b,
    long double initial
) {
    if (n < 0) {
        throw invalid_argument("n must be non-negative.");
    }

    if (a == 1.0L) {
        return initial + b * n;
    }

    const long double power = pow(a, n);
    return initial * power + b * (power - 1.0L) / (a - 1.0L);
}


// ---------------------------------------------------------------------------
// Characteristic equation:
//
// T(n) = pT(n-1) + qT(n-2)
//
// r^2 - pr - q = 0
//
// This structure returns the roots for real discriminants.
// ---------------------------------------------------------------------------

struct CharacteristicRoots {
    long double first;
    long double second;
};

CharacteristicRoots characteristicRoots(
    long double p,
    long double q
) {
    const long double discriminant = p * p + 4.0L * q;

    if (discriminant < 0.0L) {
        throw domain_error(
            "This case study expects real characteristic roots."
        );
    }

    const long double root = sqrt(discriminant);

    return {
        (p + root) / 2.0L,
        (p - root) / 2.0L
    };
}


// ---------------------------------------------------------------------------
// Distinct-root solution:
//
// T(n) = C1*r1^n + C2*r2^n
//
// Initial conditions:
//
// C1 + C2 = T(0)
// C1*r1 + C2*r2 = T(1)
// ---------------------------------------------------------------------------

struct DistinctRootSolution {
    long double c1;
    long double c2;
    long double r1;
    long double r2;

    long double evaluate(int n) const {
        return c1 * pow(r1, n) + c2 * pow(r2, n);
    }
};

DistinctRootSolution solveDistinctRoots(
    long double r1,
    long double r2,
    long double initial0,
    long double initial1
) {
    if (fabsl(r1 - r2) < numeric_limits<long double>::epsilon()) {
        throw invalid_argument("Roots must be distinct.");
    }

    const long double c1 =
        (initial1 - initial0 * r2) / (r1 - r2);

    const long double c2 = initial0 - c1;

    return {c1, c2, r1, r2};
}


// ---------------------------------------------------------------------------
// Repeated root:
//
// Characteristic equation:
//
// (r-lambda)^2 = 0
//
// General solution:
//
// T(n) = (C1 + C2*n)lambda^n
// ---------------------------------------------------------------------------

long double repeatedRootSolution(
    int n,
    long double root,
    long double initial0,
    long double initial1
) {
    if (n < 0) {
        throw invalid_argument("n must be non-negative.");
    }

    if (root == 0.0L) {
        if (n == 0) {
            return initial0;
        }

        if (n == 1) {
            return initial1;
        }

        return 0.0L;
    }

    const long double c1 = initial0;
    const long double c2 = initial1 / root - c1;

    return (c1 + c2 * n) * pow(root, n);
}


// ---------------------------------------------------------------------------
// Matrix representation for Fibonacci-like recurrences.
//
// Matrix:
//
// [1 1]
// [1 0]
//
// Raised to n, it contains Fibonacci numbers. Binary exponentiation computes
// the power in O(log n) matrix multiplications.
// ---------------------------------------------------------------------------

struct Matrix {
    unsigned long long a00;
    unsigned long long a01;
    unsigned long long a10;
    unsigned long long a11;
};

Matrix multiply(const Matrix& x, const Matrix& y) {
    // This implementation intentionally uses unsigned long long. The caller
    // validates practical input sizes because unchecked integer overflow
    // would silently invalidate recurrence results.
    return {
        x.a00 * y.a00 + x.a01 * y.a10,
        x.a00 * y.a01 + x.a01 * y.a11,
        x.a10 * y.a00 + x.a11 * y.a10,
        x.a10 * y.a01 + x.a11 * y.a11
    };
}

Matrix matrixPower(Matrix base, unsigned int exponent) {
    Matrix result{1, 0, 0, 1};

    while (exponent > 0) {
        if (exponent & 1U) {
            result = multiply(result, base);
        }

        base = multiply(base, base);
        exponent >>= 1U;
    }

    return result;
}

unsigned long long fibonacciLogarithmic(unsigned int n) {
    if (n == 0) {
        return 0;
    }

    const Matrix result = matrixPower({1, 1, 1, 0}, n);
    return result.a01;
}


// ---------------------------------------------------------------------------
// Safe Fibonacci sequence generation.
//
// F(93) is the largest Fibonacci number that fits in unsigned long long.
// ---------------------------------------------------------------------------

vector<unsigned long long> fibonacciIterative(unsigned int count) {
    vector<unsigned long long> values;

    if (count == 0) {
        return values;
    }

    values.push_back(0);

    if (count == 1) {
        return values;
    }

    values.push_back(1);

    for (unsigned int n = 2; n < count; ++n) {
        const auto maximum = numeric_limits<unsigned long long>::max();

        if (values[n - 1] > maximum - values[n - 2]) {
            throw overflow_error(
                "Fibonacci value exceeds unsigned long long capacity."
            );
        }

        values.push_back(values[n - 1] + values[n - 2]);
    }

    return values;
}


// ---------------------------------------------------------------------------
// Recurrence validation
// ---------------------------------------------------------------------------

bool validateSecondOrder(
    const vector<long long>& values,
    long long p,
    long long q,
    vector<string>& errors
) {
    errors.clear();

    if (values.size() < 2) {
        errors.push_back("At least two initial values are required.");
        return false;
    }

    for (size_t n = 2; n < values.size(); ++n) {
        const long long expected =
            p * values[n - 1] + q * values[n - 2];

        if (values[n] != expected) {
            errors.push_back(
                "Mismatch at n=" + to_string(n) +
                ": expected " + to_string(expected) +
                ", observed " + to_string(values[n])
            );
        }
    }

    return errors.empty();
}


// ---------------------------------------------------------------------------
// Case-study output
// ---------------------------------------------------------------------------

void printSequence(
    const string& title,
    const vector<long long>& values
) {
    cout << "\n" << title << "\n";
    cout << string(title.size(), '-') << "\n";

    for (size_t n = 0; n < values.size(); ++n) {
        cout << "T(" << n << ") = " << values[n] << "\n";
    }
}


// ---------------------------------------------------------------------------
// Main enterprise-style recurrence analysis
// ---------------------------------------------------------------------------

int main() {
    try {
        cout << "REPOSITORY BUILD-COST FORECASTING ENGINE\n";
        cout << "=========================================\n";

        /*
         * Scenario:
         *
         * A build pipeline has a staged processing workload. The first stage
         * costs 10 operations, and stage n adds n operations.
         *
         * T(n)=T(n-1)+n
         *
         * Iteration exposes a triangular-number closed form.
         */
        IncrementalWorkload workloadModel;

        const vector<long long> workload =
            generateSequence(10, 8, workloadModel);

        printSequence(
            "Iterative workload recurrence: T(n)=T(n-1)+n",
            workload
        );

        for (size_t n = 0; n < workload.size(); ++n) {
            const long double expected =
                10.0L +
                static_cast<long double>(n) *
                static_cast<long double>(n + 1) / 2.0L;

            if (fabsl(
                    static_cast<long double>(workload[n]) - expected
                ) > 1e-12L) {
                throw runtime_error(
                    "Iteration and closed form disagree."
                );
            }
        }

        cout << "\nIteration-derived closed form verified.\n";

        /*
         * A branching build dependency model:
         *
         * T(n)=3T(n-1)+2
         *
         * This is a first-order non-homogeneous recurrence. Its constant
         * particular solution is -1, so:
         *
         * T(n)=C*3^n-1
         */
        cout << "\nFirst-order non-homogeneous model\n";
        cout << "---------------------------------\n";

        constexpr int coefficient = 3;
        constexpr int forcing = 2;
        constexpr int initial = 4;

        for (int n = 0; n <= 6; ++n) {
            const long double closed =
                firstOrderClosedForm(
                    n,
                    coefficient,
                    forcing,
                    initial
                );

            cout << "T(" << n << ") = "
                 << fixed << setprecision(0)
                 << closed << "\n";
        }

        /*
         * Second-order dependency workload:
         *
         * T(n)=5T(n-1)-6T(n-2)
         *
         * Characteristic equation:
         *
         * r^2-5r+6=(r-2)(r-3)
         *
         * Hence:
         *
         * T(n)=C1*2^n+C2*3^n
         */
        cout << "\nCharacteristic-equation case study\n";
        cout << "----------------------------------\n";

        const auto roots = characteristicRoots(5.0L, -6.0L);

        cout << "Characteristic roots: "
             << roots.first << ", "
             << roots.second << "\n";

        const auto solution =
            solveDistinctRoots(
                roots.first,
                roots.second,
                1.0L,
                4.0L
            );

        cout << "C1 = " << solution.c1
             << ", C2 = " << solution.c2 << "\n";

        vector<long long> secondOrder{1, 4};

        for (int n = 2; n <= 8; ++n) {
            secondOrder.push_back(
                5 * secondOrder[n - 1] -
                6 * secondOrder[n - 2]
            );
        }

        printSequence(
            "Second-order recurrence generated from initial conditions",
            secondOrder
        );

        for (int n = 0; n <= 8; ++n) {
            const long double expected = solution.evaluate(n);

            if (fabsl(
                    static_cast<long double>(secondOrder[n]) -
                    expected
                ) > 1e-9L) {
                throw runtime_error(
                    "Characteristic-equation solution failed validation."
                );
            }
        }

        cout << "Characteristic solution validated.\n";

        /*
         * Repeated-root model:
         *
         * T(n)=4T(n-1)-4T(n-2)
         *
         * Characteristic equation:
         *
         * r^2-4r+4=(r-2)^2
         *
         * The solution requires:
         *
         * (C1+C2*n)2^n
         */
        cout << "\nRepeated-root case\n";
        cout << "------------------\n";

        vector<long long> repeated{2, 8};

        for (int n = 2; n <= 7; ++n) {
            repeated.push_back(
                4 * repeated[n - 1] -
                4 * repeated[n - 2]
            );
        }

        for (int n = 0; n < static_cast<int>(repeated.size()); ++n) {
            const long double expected =
                repeatedRootSolution(
                    n,
                    2.0L,
                    2.0L,
                    8.0L
                );

            if (fabsl(
                    static_cast<long double>(repeated[n]) -
                    expected
                ) > 1e-9L) {
                throw runtime_error(
                    "Repeated-root formula failed validation."
                );
            }

            cout << "T(" << n << ") = "
                 << repeated[n] << "\n";
        }

        /*
         * Recurrence validation is important in production systems because
         * a closed form may be mathematically correct while the implemented
         * recurrence transition contains an indexing error.
         */
        cout << "\nValidation engine\n";
        cout << "-----------------\n";

        vector<string> errors;

        const vector<long long> validFibonacci{
            0, 1, 1, 2, 3, 5, 8, 13
        };

        const bool valid =
            validateSecondOrder(
                validFibonacci,
                1,
                1,
                errors
            );

        cout << "Valid recurrence: "
             << boolalpha << valid << "\n";

        const vector<long long> invalidFibonacci{
            0, 1, 1, 2, 99, 5
        };

        const bool invalid =
            validateSecondOrder(
                invalidFibonacci,
                1,
                1,
                errors
            );

        cout << "Invalid recurrence accepted: "
             << invalid << "\n";

        if (invalid) {
            throw runtime_error(
                "Validation engine failed to reject bad data."
            );
        }

        for (const auto& error : errors) {
            cout << "Validation error: " << error << "\n";
        }

        /*
         * Fibonacci comparison:
         *
         * Iteration evaluates each state once: O(n).
         * Matrix exponentiation evaluates a matrix power by repeated
         * squaring: O(log n) matrix multiplications.
         */
        cout << "\nAlgorithmic comparison\n";
        cout << "----------------------\n";

        const auto fib = fibonacciIterative(20);

        cout << "F(19) by iteration: "
             << fib[19] << "\n";

        cout << "F(19) by matrix exponentiation: "
             << fibonacciLogarithmic(19) << "\n";

        if (fib[19] != fibonacciLogarithmic(19)) {
            throw runtime_error(
                "Fibonacci implementations disagree."
            );
        }

        cout << "Both recurrence evaluation methods agree.\n";

        cout << "\nComplexity characteristics\n";
        cout << "--------------------------\n";
        cout << "Direct first-order iteration: O(n) time, O(n) stored values.\n";
        cout << "Two-state iterative Fibonacci: O(n) time, O(1) working memory.\n";
        cout << "Memoized recursive Fibonacci: O(n) states and O(n) stack/cache.\n";
        cout << "Matrix exponentiation: O(log n) matrix multiplications.\n";
        cout << "Characteristic-form evaluation: O(1) arithmetic operations per n.\n";

        cout << "\nCase study completed successfully.\n";
        return 0;
    }
    catch (const exception& error) {
        cerr << "ERROR: " << error.what() << "\n";
        return 1;
    }
}
