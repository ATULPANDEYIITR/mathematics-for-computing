#include <algorithm>
#include <cassert>
#include <cstdint>
#include <exception>
#include <iostream>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

using u64 = std::uint64_t;

u64 gcd_u64(u64 a, u64 b) {
    while (b != 0) {
        u64 remainder = a % b;
        a = b;
        b = remainder;
    }
    return a;
}

u64 mod_pow(u64 base, u64 exponent, u64 modulus) {
    if (modulus == 0) {
        throw std::invalid_argument("modulus must be non-zero");
    }

    u64 result = 1 % modulus;
    base %= modulus;

    while (exponent != 0) {
        if (exponent & 1ULL) {
            // For the educational parameter sizes used here, direct multiplication
            // is sufficient. Production cryptographic arithmetic needs overflow-safe
            // multiplication and side-channel considerations.
            result = (result * base) % modulus;
        }

        base = (base * base) % modulus;
        exponent >>= 1U;
    }

    return result;
}

bool is_prime(u64 n) {
    if (n < 2) return false;
    if (n == 2) return true;
    if (n % 2 == 0) return false;

    for (u64 divisor = 3; divisor <= n / divisor; divisor += 2) {
        if (n % divisor == 0) return false;
    }

    return true;
}

u64 euler_phi(u64 n) {
    if (n == 0) {
        throw std::invalid_argument("phi(0) is undefined");
    }

    u64 result = n;
    u64 value = n;

    if (value % 2 == 0) {
        result -= result / 2;
        while (value % 2 == 0) value /= 2;
    }

    for (u64 factor = 3; factor <= value / factor; factor += 2) {
        if (value % factor == 0) {
            result -= result / factor;
            while (value % factor == 0) value /= factor;
        }
    }

    if (value > 1) {
        result -= result / value;
    }

    return result;
}

struct ExtendedGcdResult {
    std::int64_t gcd;
    std::int64_t coefficient;
};

ExtendedGcdResult extended_gcd(std::int64_t a, std::int64_t b) {
    std::int64_t old_r = a;
    std::int64_t r = b;
    std::int64_t old_s = 1;
    std::int64_t s = 0;

    while (r != 0) {
        const std::int64_t quotient = old_r / r;

        const std::int64_t next_r = old_r - quotient * r;
        old_r = r;
        r = next_r;

        const std::int64_t next_s = old_s - quotient * s;
        old_s = s;
        s = next_s;
    }

    return {old_r, old_s};
}

u64 modular_inverse(u64 a, u64 modulus) {
    if (modulus <= 1) {
        throw std::invalid_argument("modulus must be greater than one");
    }

    const auto result = extended_gcd(
        static_cast<std::int64_t>(a % modulus),
        static_cast<std::int64_t>(modulus)
    );

    if (result.gcd != 1) {
        throw std::domain_error("modular inverse does not exist");
    }

    std::int64_t inverse = result.coefficient % static_cast<std::int64_t>(modulus);
    if (inverse < 0) {
        inverse += static_cast<std::int64_t>(modulus);
    }

    return static_cast<u64>(inverse);
}

struct PullRequestMathPolicy {
    u64 modulus;
    u64 exponent;
    bool coprime_required;

    bool evaluate(u64 value) const {
        if (modulus == 0) {
            throw std::invalid_argument("invalid modulus");
        }

        if (coprime_required && gcd_u64(value, modulus) != 1) {
            return false;
        }

        return mod_pow(value, exponent, modulus) == 1;
    }
};

struct RepositoryGovernance {
    std::string repository;
    std::vector<u64> prime_moduli;
    std::vector<u64> composite_moduli;

    bool validateFermat() const {
        for (u64 prime : prime_moduli) {
            if (!is_prime(prime)) return false;

            for (u64 a = 1; a < prime; ++a) {
                if (mod_pow(a, prime - 1, prime) != 1) {
                    return false;
                }
            }
        }

        return true;
    }

    bool validateEuler() const {
        for (u64 n : composite_moduli) {
            const u64 exponent = euler_phi(n);

            for (u64 a = 1; a <= n; ++a) {
                if (gcd_u64(a, n) == 1 &&
                    mod_pow(a, exponent, n) != 1) {
                    return false;
                }
            }
        }

        return true;
    }
};

void print_phi_table(const std::vector<u64>& values) {
    std::cout << "Euler phi values\n";
    for (u64 n : values) {
        std::cout << "phi(" << n << ") = " << euler_phi(n) << '\n';
    }
}

int main() {
    try {
        std::cout << "=== Euler Phi Function ===\n";
        print_phi_table({1, 2, 5, 8, 12, 36});

        std::cout << "\n=== Fermat's Little Theorem ===\n";
        for (u64 p : {5ULL, 7ULL, 11ULL, 13ULL}) {
            if (!is_prime(p)) {
                throw std::logic_error("prime test failed");
            }

            const u64 value = mod_pow(3, p - 1, p);
            std::cout << "3^(" << p - 1 << ") mod " << p
                      << " = " << value << '\n';
            assert(value == 1);
        }

        std::cout << "\n=== Euler's Theorem ===\n";
        for (const auto& [a, n] :
             std::vector<std::pair<u64, u64>>{{5, 8}, {5, 9}, {7, 12}, {11, 15}}) {
            const u64 divisor = gcd_u64(a, n);

            std::cout << "a=" << a
                      << ", n=" << n
                      << ", gcd=" << divisor;

            if (divisor == 1) {
                const u64 exponent = euler_phi(n);
                const u64 value = mod_pow(a, exponent, n);

                std::cout << ", phi(n)=" << exponent
                          << ", a^phi(n) mod n=" << value;
                assert(value == 1);
            } else {
                std::cout << ", Euler theorem not applicable";
            }

            std::cout << '\n';
        }

        std::cout << "\n=== Governance-Style Number-Theory Validation ===\n";
        RepositoryGovernance policy{
            "number-theory-demo",
            {2, 3, 5, 7, 11, 13},
            {8, 9, 10, 12, 15}
        };

        std::cout << "Repository: " << policy.repository << '\n';
        std::cout << "Fermat policy: "
                  << (policy.validateFermat() ? "PASS" : "FAIL") << '\n';
        std::cout << "Euler policy: "
                  << (policy.validateEuler() ? "PASS" : "FAIL") << '\n';

        std::cout << "\n=== Modular Inverse ===\n";
        for (const auto& [a, n] :
             std::vector<std::pair<u64, u64>>{{3, 10}, {7, 40}, {11, 26}}) {
            const u64 inverse = modular_inverse(a, n);
            std::cout << a << "^-1 mod " << n << " = " << inverse << '\n';
            assert((a * inverse) % n == 1);
        }

        std::cout << "\n=== RSA-Style Example ===\n";
        const u64 p = 61;
        const u64 q = 53;
        const u64 n = p * q;
        const u64 phi_n = (p - 1) * (q - 1);
        const u64 e = 17;
        const u64 d = modular_inverse(e, phi_n);
        const u64 message = 65;

        const u64 ciphertext = mod_pow(message, e, n);
        const u64 recovered = mod_pow(ciphertext, d, n);

        std::cout << "n = " << n << '\n';
        std::cout << "phi(n) = " << phi_n << '\n';
        std::cout << "e = " << e << '\n';
        std::cout << "d = " << d << '\n';
        std::cout << "ciphertext = " << ciphertext << '\n';
        std::cout << "recovered = " << recovered << '\n';

        assert(recovered == message);

        std::cout << "\n=== Failure Conditions ===\n";

        try {
            (void)modular_inverse(6, 15);
        } catch (const std::exception& error) {
            std::cout << "Non-invertible value rejected: "
                      << error.what() << '\n';
        }

        try {
            if (!is_prime(15)) {
                throw std::invalid_argument(
                    "Fermat's theorem requires a prime modulus"
                );
            }
        } catch (const std::exception& error) {
            std::cout << "Composite modulus rejected: "
                      << error.what() << '\n';
        }

        std::cout << "\nComplexity notes:\n";
        std::cout << "Binary modular exponentiation uses O(log exponent) "
                     "multiplications.\n";
        std::cout << "The trial-division primality test is O(sqrt(n)) in "
                     "the worst case.\n";
        std::cout << "Euler phi factorization is efficient for small "
                     "educational inputs but needs optimized factorization "
                     "for large integers.\n";

        std::cout << "\nSecurity note: textbook arithmetic is not a "
                     "production cryptographic implementation. Real systems "
                     "require safe modular multiplication, secure parameters, "
                     "constant-time techniques, padding, and vetted libraries.\n";
    } catch (const std::exception& error) {
        std::cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
