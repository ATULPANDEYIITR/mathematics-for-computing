#include <cstdint>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

using u64 = uint64_t;

class ModularArithmeticError : public runtime_error {
public:
    explicit ModularArithmeticError(const string& message)
        : runtime_error(message) {}
};

class ModularArithmetic {
public:
    static u64 normalize(int64_t value, u64 modulus) {
        validateModulus(modulus);

        // Avoid negating INT64_MIN, which is not representable as int64_t.
        if (value >= 0) {
            return static_cast<u64>(value) % modulus;
        }

        const u64 magnitude = static_cast<u64>(-(value + 1)) + 1;
        const u64 remainder = magnitude % modulus;
        return remainder == 0 ? 0 : modulus - remainder;
    }

    static bool congruent(int64_t a, int64_t b, u64 modulus) {
        validateModulus(modulus);
        return normalize(a, modulus) == normalize(b, modulus);
    }

    static u64 add(u64 a, u64 b, u64 modulus) {
        validateModulus(modulus);
        a %= modulus;
        b %= modulus;

        // This form avoids overflowing a + b for large unsigned values.
        return a >= modulus - b ? a - (modulus - b) : a + b;
    }

    static u64 multiply(u64 a, u64 b, u64 modulus) {
        validateModulus(modulus);
        a %= modulus;
        b %= modulus;
        u64 result = 0;

        // Portable multiplication using repeated doubling.
        while (b != 0) {
            if (b & 1ULL) {
                result = add(result, a, modulus);
            }
            a = add(a, a, modulus);
            b >>= 1;
        }
        return result;
    }

    static u64 power(u64 base, u64 exponent, u64 modulus) {
        validateModulus(modulus);
        base %= modulus;
        u64 result = 1 % modulus;

        while (exponent != 0) {
            if (exponent & 1ULL) {
                result = multiply(result, base, modulus);
            }
            base = multiply(base, base, modulus);
            exponent >>= 1;
        }
        return result;
    }

    static u64 gcd(u64 a, u64 b) {
        while (b != 0) {
            u64 remainder = a % b;
            a = b;
            b = remainder;
        }
        return a;
    }

    static u64 inverse(int64_t value, u64 modulus) {
        validateModulus(modulus);
        if (modulus == 1) {
            throw ModularArithmeticError(
                "Modular inverse requires a modulus greater than one."
            );
        }

        const u64 normalized = normalize(value, modulus);
        if (gcd(normalized, modulus) != 1) {
            throw ModularArithmeticError(
                "Modular inverse does not exist because gcd(value, modulus) != 1."
            );
        }

        // Use signed 128-bit intermediates to avoid coefficient overflow.
        __int128 oldR = normalized;
        __int128 r = modulus;
        __int128 oldS = 1;
        __int128 s = 0;

        while (r != 0) {
            const __int128 quotient = oldR / r;
            const __int128 nextR = oldR - quotient * r;
            oldR = r;
            r = nextR;

            const __int128 nextS = oldS - quotient * s;
            oldS = s;
            s = nextS;
        }

        __int128 answer = oldS % static_cast<__int128>(modulus);
        if (answer < 0) {
            answer += modulus;
        }
        return static_cast<u64>(answer);
    }

private:
    static void validateModulus(u64 modulus) {
        if (modulus == 0) {
            throw ModularArithmeticError("Modulus must be positive.");
        }
    }
};

struct ArithmeticCase {
    string name;
    int64_t left;
    int64_t right;
    u64 modulus;
};

void runTests() {
    if (ModularArithmetic::normalize(-17, 5) != 3)
        throw logic_error("Normalization failed.");
    if (!ModularArithmetic::congruent(17, 2, 5))
        throw logic_error("Congruence failed.");
    if (ModularArithmetic::add(4, 3, 5) != 2)
        throw logic_error("Addition failed.");
    if (ModularArithmetic::multiply(123, 456, 97) !=
        (123ULL * 456ULL) % 97ULL)
        throw logic_error("Multiplication failed.");
    if (ModularArithmetic::power(3, 100, 7) != 4)
        throw logic_error("Exponentiation failed.");
    if (ModularArithmetic::inverse(3, 11) != 4)
        throw logic_error("Inverse failed.");

    bool rejected = false;
    try {
        ModularArithmetic::inverse(6, 9);
    } catch (const ModularArithmeticError&) {
        rejected = true;
    }
    if (!rejected)
        throw logic_error("Invalid inverse was accepted.");

    cout << "All C++17 modular arithmetic tests passed.\n";
}

int main() {
    try {
        runTests();

        const vector<ArithmeticCase> cases = {
            {"negative normalization", -45, 0, 17},
            {"addition", 123, -45, 17},
            {"multiplication", 123456, 789012, 97},
            {"congruence", 102, 4, 7}
        };

        for (const auto& item : cases) {
            cout << item.name << ": ";
            if (item.name == "negative normalization") {
                cout << ModularArithmetic::normalize(
                    item.left, item.modulus
                );
            } else if (item.name == "addition") {
                cout << ModularArithmetic::add(
                    ModularArithmetic::normalize(item.left, item.modulus),
                    ModularArithmetic::normalize(item.right, item.modulus),
                    item.modulus
                );
            } else if (item.name == "multiplication") {
                cout << ModularArithmetic::multiply(
                    static_cast<u64>(item.left),
                    static_cast<u64>(item.right),
                    item.modulus
                );
            } else {
                cout << boolalpha << ModularArithmetic::congruent(
                    item.left, item.right, item.modulus
                );
            }
            cout << '\n';
        }

        cout << "3^100 mod 17 = "
             << ModularArithmetic::power(3, 100, 17) << '\n';
        cout << "5 inverse mod 17 = "
             << ModularArithmetic::inverse(5, 17) << '\n';

        // A real command-line service should reject malformed input before
        // constructing domain objects. This example reports domain failures.
        try {
            cout << ModularArithmetic::inverse(6, 9) << '\n';
        } catch (const ModularArithmeticError& error) {
            cerr << "Expected domain rejection: " << error.what() << '\n';
        }
    } catch (const exception& error) {
        cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
