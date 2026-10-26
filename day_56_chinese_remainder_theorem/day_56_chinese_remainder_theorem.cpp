#include <algorithm>
#include <cstdint>
#include <exception>
#include <iostream>
#include <numeric>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

using int64 = std::int64_t;
using int128 = __int128_t;

enum class MergeStatus {
    Success,
    Inconsistent
};

struct Congruence {
    int64 remainder;
    int64 modulus;

    Congruence(int64 r, int64 m) : remainder(r), modulus(m) {
        if (modulus <= 1) {
            throw std::invalid_argument("Modulus must be greater than 1.");
        }
        remainder %= modulus;
        if (remainder < 0) {
            remainder += modulus;
        }
    }
};

struct CRTResult {
    int64 remainder;
    int64 modulus;

    bool contains(int64 value) const {
        return ((value % modulus) + modulus) % modulus == remainder;
    }
};

struct EGCD {
    int64 gcd;
    int64 x;
    int64 y;
};

EGCD extendedGcd(int64 a, int64 b) {
    int64 oldR = std::llabs(a);
    int64 r = std::llabs(b);
    int64 oldS = 1;
    int64 s = 0;
    int64 oldT = 0;
    int64 t = 1;

    while (r != 0) {
        const int64 q = oldR / r;
        const int64 nextR = oldR - q * r;
        oldR = r;
        r = nextR;

        const int64 nextS = oldS - q * s;
        oldS = s;
        s = nextS;

        const int64 nextT = oldT - q * t;
        oldT = t;
        t = nextT;
    }

    if (a < 0) oldS = -oldS;
    if (b < 0) oldT = -oldT;

    return {oldR, oldS, oldT};
}

int64 modInverse(int64 a, int64 modulus) {
    const EGCD result = extendedGcd(a, modulus);
    if (result.gcd != 1) {
        throw std::domain_error("Modular inverse does not exist.");
    }

    int64 inverse = result.x % modulus;
    if (inverse < 0) inverse += modulus;
    return inverse;
}

bool pairwiseCoprime(const std::vector<Congruence>& system) {
    for (std::size_t i = 0; i < system.size(); ++i) {
        for (std::size_t j = i + 1; j < system.size(); ++j) {
            if (std::gcd(system[i].modulus, system[j].modulus) != 1) {
                return false;
            }
        }
    }
    return true;
}

int64 checkedToInt64(int128 value) {
    if (value > static_cast<int128>(INT64_MAX) ||
        value < static_cast<int128>(INT64_MIN)) {
        throw std::overflow_error("Result exceeds int64 range.");
    }
    return static_cast<int64>(value);
}

CRTResult solveCoprimeCRT(const std::vector<Congruence>& system) {
    if (system.empty()) {
        throw std::invalid_argument("CRT system cannot be empty.");
    }

    if (!pairwiseCoprime(system)) {
        throw std::invalid_argument(
            "Direct CRT construction requires pairwise-coprime moduli."
        );
    }

    int128 product = 1;
    for (const auto& c : system) {
        product *= c.modulus;
    }

    if (product > static_cast<int128>(INT64_MAX)) {
        throw std::overflow_error("Combined modulus exceeds int64 range.");
    }

    const int64 modulus = static_cast<int64>(product);
    int128 value = 0;

    for (const auto& c : system) {
        const int64 partial = modulus / c.modulus;
        const int64 inverse = modInverse(partial % c.modulus, c.modulus);

        value += static_cast<int128>(c.remainder) *
                 partial *
                 inverse;
    }

    int64 normalized = static_cast<int64>(value % modulus);
    if (normalized < 0) normalized += modulus;

    return {normalized, modulus};
}

std::optional<CRTResult> mergeCongruences(
    const Congruence& a,
    const Congruence& b
) {
    const int64 g = std::gcd(a.modulus, b.modulus);
    const int64 difference = b.remainder - a.remainder;

    if (difference % g != 0) {
        return std::nullopt;
    }

    const int64 reducedA = a.modulus / g;
    const int64 reducedB = b.modulus / g;
    const int64 rhs = difference / g;

    const int64 inverse = modInverse(
        ((reducedA % reducedB) + reducedB) % reducedB,
        reducedB
    );

    int64 k = static_cast<int64>(
        (static_cast<int128>(rhs) * inverse) % reducedB
    );
    if (k < 0) k += reducedB;

    const int128 combinedModulus128 =
        static_cast<int128>(a.modulus) * reducedB;

    if (combinedModulus128 > static_cast<int128>(INT64_MAX)) {
        throw std::overflow_error("LCM exceeds int64 range.");
    }

    const int64 combinedModulus = static_cast<int64>(combinedModulus128);

    int64 value = static_cast<int64>(
        (static_cast<int128>(a.remainder) +
         static_cast<int128>(a.modulus) * k) %
        combinedModulus
    );

    if (value < 0) value += combinedModulus;

    return CRTResult{value, combinedModulus};
}

CRTResult solveGeneralCRT(const std::vector<Congruence>& system) {
    if (system.empty()) {
        throw std::invalid_argument("CRT system cannot be empty.");
    }

    CRTResult current{system.front().remainder, system.front().modulus};

    for (std::size_t i = 1; i < system.size(); ++i) {
        const auto merged = mergeCongruences(
            Congruence(current.remainder, current.modulus),
            system[i]
        );

        if (!merged) {
            throw std::domain_error("CRT system is inconsistent.");
        }

        current = *merged;
    }

    return current;
}

int64 modularPower(int64 base, int64 exponent, int64 modulus) {
    if (modulus <= 1 || exponent < 0) {
        throw std::invalid_argument("Invalid modular exponentiation input.");
    }

    int64 result = 1 % modulus;
    base %= modulus;

    while (exponent > 0) {
        if (exponent & 1LL) {
            result = static_cast<int64>(
                (static_cast<int128>(result) * base) % modulus
            );
        }

        base = static_cast<int64>(
            (static_cast<int128>(base) * base) % modulus
        );
        exponent >>= 1;
    }

    return result;
}

bool verify(
    const CRTResult& result,
    const std::vector<Congruence>& system
) {
    return std::all_of(
        system.begin(),
        system.end(),
        [&](const Congruence& c) {
            return result.contains(c.remainder);
        }
    );
}

class MergeEligibilityEngine {
public:
    struct PullRequest {
        std::string id;
        std::string baseBranch;
        bool conflicts;
        bool draft;
        bool requiredChecksPassed;
        int requiredApprovals;
        int validApprovals;
    };

    static bool eligible(const PullRequest& pr) {
        return !pr.draft &&
               !pr.conflicts &&
               pr.requiredChecksPassed &&
               pr.validApprovals >= pr.requiredApprovals;
    }
};

int main() {
    try {
        const std::vector<Congruence> system{
            {2, 3},
            {3, 5},
            {2, 7}
        };

        const CRTResult result = solveCoprimeCRT(system);

        std::cout << "Coprime CRT\n";
        std::cout << "x = " << result.remainder
                  << " (mod " << result.modulus << ")\n";
        std::cout << "Verification: "
                  << (verify(result, system) ? "passed" : "failed")
                  << "\n\n";

        const std::vector<Congruence> compatible{
            {2, 6},
            {8, 9}
        };

        const CRTResult generalized = solveGeneralCRT(compatible);

        std::cout << "Generalized CRT\n";
        std::cout << "x = " << generalized.remainder
                  << " (mod " << generalized.modulus << ")\n\n";

        try {
            solveGeneralCRT({
                {1, 4},
                {2, 6}
            });
        } catch (const std::exception& ex) {
            std::cout << "Expected inconsistency: "
                      << ex.what() << "\n\n";
        }

        const int64 p = 61;
        const int64 q = 53;
        const int64 privateExponent = 2753;
        const int64 ciphertext = 2790;

        const int64 mP = modularPower(
            ciphertext,
            privateExponent % (p - 1),
            p
        );

        const int64 mQ = modularPower(
            ciphertext,
            privateExponent % (q - 1),
            q
        );

        const CRTResult recombined = solveCoprimeCRT({
            Congruence(mP, p),
            Congruence(mQ, q)
        });

        const int64 direct = modularPower(
            ciphertext,
            privateExponent,
            p * q
        );

        if (recombined.remainder != direct) {
            throw std::runtime_error("CRT recombination verification failed.");
        }

        std::cout << "RSA-style CRT recombination\n";
        std::cout << "direct = " << direct << "\n";
        std::cout << "CRT    = " << recombined.remainder << "\n\n";

        MergeEligibilityEngine::PullRequest pr{
            "PR-1042",
            "main",
            false,
            false,
            true,
            2,
            2
        };

        std::cout << "Governance example\n";
        std::cout << pr.id << " merge eligible: "
                  << (MergeEligibilityEngine::eligible(pr) ? "yes" : "no")
                  << "\n";

    } catch (const std::exception& ex) {
        std::cerr << "Fatal error: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
