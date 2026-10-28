#include <algorithm>
#include <cstdint>
#include <exception>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

class NumberTheoryError : public std::runtime_error {
public:
    explicit NumberTheoryError(const std::string& message)
        : std::runtime_error(message) {}
};

struct ExtendedGcdResult {
    std::int64_t gcd;
    std::int64_t x;
    std::int64_t y;
};

struct MergeRequest {
    std::uint64_t id;
    std::uint64_t base;
    std::uint64_t exponent;
    std::uint64_t modulus;
};

struct MergeDecision {
    bool eligible;
    std::string reason;
};

std::uint64_t gcd(std::uint64_t a, std::uint64_t b) {
    while (b != 0) {
        const std::uint64_t remainder = a % b;
        a = b;
        b = remainder;
    }
    return a;
}

ExtendedGcdResult extendedGcd(std::int64_t a, std::int64_t b) {
    std::int64_t oldR = a;
    std::int64_t r = b;
    std::int64_t oldX = 1;
    std::int64_t x = 0;
    std::int64_t oldY = 0;
    std::int64_t y = 1;

    while (r != 0) {
        const std::int64_t quotient = oldR / r;

        const std::int64_t nextR = oldR - quotient * r;
        oldR = r;
        r = nextR;

        const std::int64_t nextX = oldX - quotient * x;
        oldX = x;
        x = nextX;

        const std::int64_t nextY = oldY - quotient * y;
        oldY = y;
        y = nextY;
    }

    if (oldR < 0) {
        return {-oldR, -oldX, -oldY};
    }

    return {oldR, oldX, oldY};
}

/*
 * Multiplication uses __int128 to avoid intermediate overflow for
 * uint64_t operands before reducing modulo the modulus.
 */
std::uint64_t multiplyMod(
    std::uint64_t a,
    std::uint64_t b,
    std::uint64_t modulus
) {
    if (modulus == 0) {
        throw NumberTheoryError("Modulus must be positive.");
    }

    const unsigned __int128 product =
        static_cast<unsigned __int128>(a) *
        static_cast<unsigned __int128>(b);

    return static_cast<std::uint64_t>(product % modulus);
}

std::uint64_t modPow(
    std::uint64_t base,
    std::uint64_t exponent,
    std::uint64_t modulus
) {
    if (modulus == 0) {
        throw NumberTheoryError("Modulus must be positive.");
    }

    std::uint64_t result = 1 % modulus;
    base %= modulus;

    while (exponent != 0) {
        if (exponent & 1ULL) {
            result = multiplyMod(result, base, modulus);
        }

        base = multiplyMod(base, base, modulus);
        exponent >>= 1U;
    }

    return result;
}

bool isPrimeTrial(std::uint64_t n) {
    if (n < 2) {
        return false;
    }

    if (n == 2 || n == 3) {
        return true;
    }

    if (n % 2 == 0) {
        return false;
    }

    for (std::uint64_t divisor = 3;
         divisor <= n / divisor;
         divisor += 2) {
        if (n % divisor == 0) {
            return false;
        }
    }

    return true;
}

std::uint64_t randomBelow(
    std::uint64_t upper,
    std::mt19937_64& generator
) {
    if (upper == 0) {
        throw NumberTheoryError("Random upper bound cannot be zero.");
    }

    std::uniform_int_distribution<std::uint64_t> distribution(0, upper - 1);
    return distribution(generator);
}

/*
 * Miller-Rabin with a fixed witness set is deterministic for uint64_t.
 * This avoids probabilistic behavior for the program's supported range.
 */
bool isPrimeMillerRabin(std::uint64_t n) {
    if (n < 2) {
        return false;
    }

    for (std::uint64_t p : {
        2ULL, 3ULL, 5ULL, 7ULL, 11ULL, 13ULL,
        17ULL, 19ULL, 23ULL, 29ULL, 31ULL, 37ULL
    }) {
        if (n == p) {
            return true;
        }

        if (n % p == 0) {
            return false;
        }
    }

    std::uint64_t d = n - 1;
    unsigned int s = 0;

    while ((d & 1ULL) == 0) {
        d >>= 1U;
        ++s;
    }

    /*
     * This witness set is sufficient for deterministic Miller-Rabin
     * testing over the full unsigned 64-bit integer range.
     */
    const std::uint64_t witnesses[] = {
        2ULL, 325ULL, 9375ULL, 28178ULL,
        450775ULL, 9780504ULL, 1795265022ULL
    };

    for (std::uint64_t witness : witnesses) {
        const std::uint64_t a = witness % n;

        if (a == 0) {
            continue;
        }

        std::uint64_t x = modPow(a, d, n);

        if (x == 1 || x == n - 1) {
            continue;
        }

        bool passed = false;

        for (unsigned int r = 1; r < s; ++r) {
            x = multiplyMod(x, x, n);

            if (x == n - 1) {
                passed = true;
                break;
            }
        }

        if (!passed) {
            return false;
        }
    }

    return true;
}

std::uint64_t modularInverse(
    std::int64_t value,
    std::int64_t modulus
) {
    if (modulus <= 0) {
        throw NumberTheoryError("Modulus must be positive.");
    }

    const auto result = extendedGcd(value, modulus);

    if (result.gcd != 1) {
        throw NumberTheoryError("Modular inverse does not exist.");
    }

    const std::int64_t normalized =
        ((result.x % modulus) + modulus) % modulus;

    return static_cast<std::uint64_t>(normalized);
}

std::map<std::uint64_t, unsigned int> factorize(std::uint64_t n) {
    if (n == 0) {
        throw NumberTheoryError("Cannot factorize zero.");
    }

    std::map<std::uint64_t, unsigned int> factors;

    while (n % 2 == 0 && n > 1) {
        ++factors[2];
        n /= 2;
    }

    for (std::uint64_t divisor = 3;
         divisor <= n / divisor;
         divisor += 2) {
        while (n % divisor == 0) {
            ++factors[divisor];
            n /= divisor;
        }
    }

    if (n > 1) {
        ++factors[n];
    }

    return factors;
}

std::uint64_t eulerTotient(std::uint64_t n) {
    if (n == 0) {
        throw NumberTheoryError("Totient is undefined for zero.");
    }

    const auto factors = factorize(n);
    std::uint64_t result = n;

    for (const auto& [prime, exponent] : factors) {
        static_cast<void>(exponent);
        result -= result / prime;
    }

    return result;
}

MergeDecision evaluateRequest(const MergeRequest& request) {
    if (request.modulus == 0) {
        return {false, "The modulus must be positive."};
    }

    if (request.modulus == 1) {
        return {true, "Modulo 1 is valid and produces residue 0."};
    }

    const auto result =
        modPow(request.base, request.exponent, request.modulus);

    if (result >= request.modulus) {
        return {false, "Internal modular reduction invariant failed."};
    }

    return {
        true,
        "Validated modular exponentiation: result = " +
            std::to_string(result)
    };
}

void printFactorization(const std::map<std::uint64_t, unsigned int>& factors) {
    bool first = true;

    for (const auto& [prime, exponent] : factors) {
        if (!first) {
            std::cout << " * ";
        }

        std::cout << prime;

        if (exponent > 1) {
            std::cout << "^" << exponent;
        }

        first = false;
    }

    if (first) {
        std::cout << "1";
    }

    std::cout << '\n';
}

int main() {
    try {
        std::cout << "NUMBER THEORY ALGORITHMS\n";
        std::cout << std::string(70, '=') << '\n';

        std::cout << "\n1. Euclidean algorithm\n";
        std::cout << "gcd(252, 105) = " << gcd(252, 105) << '\n';

        std::cout << "\n2. Extended Euclidean algorithm\n";
        const auto eg = extendedGcd(240, 46);
        std::cout
            << "gcd=" << eg.gcd
            << ", x=" << eg.x
            << ", y=" << eg.y << '\n';

        if (240 * eg.x + 46 * eg.y != eg.gcd) {
            throw NumberTheoryError("Extended GCD invariant failed.");
        }

        std::cout << "\n3. Fast modular exponentiation\n";
        const auto power = modPow(3, 100, 13);
        std::cout << "3^100 mod 13 = " << power << '\n';

        if (power != 9) {
            throw NumberTheoryError("Unexpected modular exponentiation result.");
        }

        std::cout << "\n4. Deterministic 64-bit primality testing\n";

        for (const auto value : {
            1ULL, 2ULL, 17ULL, 97ULL, 100ULL, 104729ULL
        }) {
            std::cout
                << value
                << " -> "
                << (isPrimeMillerRabin(value) ? "prime" : "composite")
                << '\n';
        }

        std::cout << "\n5. Prime factorization\n";
        std::cout << "360 = ";
        printFactorization(factorize(360));

        std::cout << "\n6. Euler's totient\n";
        std::cout << "phi(36) = " << eulerTotient(36) << '\n';

        if (eulerTotient(36) != 12) {
            throw NumberTheoryError("Totient validation failed.");
        }

        std::cout << "\n7. Modular inverse\n";
        const auto inverse = modularInverse(7, 26);
        std::cout << "7^-1 mod 26 = " << inverse << '\n';

        if ((7 * inverse) % 26 != 1) {
            throw NumberTheoryError("Modular inverse validation failed.");
        }

        std::cout << "\n8. Governance-style computational request validation\n";

        const std::vector<MergeRequest> requests = {
            {1001, 3, 100, 13},
            {1002, 7, 0, 26},
            {1003, 2, 63, 0},
            {1004, 123456789ULL, 987654321ULL, 1000000007ULL}
        };

        for (const auto& request : requests) {
            const auto decision = evaluateRequest(request);

            std::cout
                << "Request " << request.id
                << ": "
                << (decision.eligible ? "accepted" : "rejected")
                << " - "
                << decision.reason
                << '\n';
        }

        std::cout << "\n9. Failure conditions\n";

        try {
            modularInverse(6, 15);
            throw NumberTheoryError(
                "An invalid modular inverse was incorrectly accepted."
            );
        } catch (const NumberTheoryError& error) {
            std::cout << "Rejected as expected: " << error.what() << '\n';
        }

        try {
            modPow(2, 10, 0);
            throw NumberTheoryError(
                "An invalid modulus was incorrectly accepted."
            );
        } catch (const NumberTheoryError& error) {
            std::cout << "Rejected as expected: " << error.what() << '\n';
        }

        std::cout << "\nAll checks completed successfully.\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }
}
