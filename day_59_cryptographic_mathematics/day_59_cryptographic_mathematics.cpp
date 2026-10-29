#include <algorithm>
#include <cstdint>
#include <exception>
#include <iostream>
#include <limits>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>

using u64 = std::uint64_t;
using u128 = unsigned __int128;

class RSAError : public std::runtime_error {
public:
    explicit RSAError(const std::string& message)
        : std::runtime_error(message) {}
};

u64 gcd_u64(u64 a, u64 b) {
    while (b != 0) {
        const u64 r = a % b;
        a = b;
        b = r;
    }
    return a;
}

/*
 * Extended Euclid over signed 64-bit integers.
 * The RSA demonstration uses moduli below 2^64, while multiplication in
 * modular arithmetic is performed through unsigned __int128.
 */
std::tuple<std::int64_t, std::int64_t, std::int64_t>
extended_gcd(std::int64_t a, std::int64_t b) {
    std::int64_t old_r = a, r = b;
    std::int64_t old_x = 1, x = 0;
    std::int64_t old_y = 0, y = 1;

    while (r != 0) {
        const std::int64_t q = old_r / r;

        const std::int64_t next_r = old_r - q * r;
        old_r = r;
        r = next_r;

        const std::int64_t next_x = old_x - q * x;
        old_x = x;
        x = next_x;

        const std::int64_t next_y = old_y - q * y;
        old_y = y;
        y = next_y;
    }

    return {old_r, old_x, old_y};
}

u64 mod_inverse(u64 a, u64 modulus) {
    if (modulus <= 1) {
        throw RSAError("Invalid modulus.");
    }

    auto [g, x, y] = extended_gcd(
        static_cast<std::int64_t>(a % modulus),
        static_cast<std::int64_t>(modulus)
    );

    if (g != 1) {
        throw RSAError("Modular inverse does not exist.");
    }

    const std::int64_t m = static_cast<std::int64_t>(modulus);
    x %= m;
    if (x < 0) x += m;

    return static_cast<u64>(x);
}

u64 mul_mod(u64 a, u64 b, u64 modulus) {
    return static_cast<u64>((static_cast<u128>(a) * b) % modulus);
}

u64 pow_mod(u64 base, u64 exponent, u64 modulus) {
    if (modulus == 0) {
        throw RSAError("Modulus cannot be zero.");
    }

    u64 result = 1 % modulus;
    base %= modulus;

    while (exponent != 0) {
        if (exponent & 1ULL) {
            result = mul_mod(result, base, modulus);
        }
        base = mul_mod(base, base, modulus);
        exponent >>= 1U;
    }

    return result;
}

bool is_probable_prime(u64 n, int rounds = 16) {
    if (n < 2) return false;

    constexpr u64 smallPrimes[] = {
        2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37
    };

    for (u64 p : smallPrimes) {
        if (n == p) return true;
        if (n % p == 0) return false;
    }

    u64 d = n - 1;
    int s = 0;

    while ((d & 1ULL) == 0) {
        d >>= 1U;
        ++s;
    }

    std::mt19937_64 rng(
        std::random_device{}()
    );

    for (int round = 0; round < rounds; ++round) {
        std::uniform_int_distribution<u64> distribution(2, n - 2);
        const u64 a = distribution(rng);

        u64 x = pow_mod(a, d, n);

        if (x == 1 || x == n - 1) continue;

        bool reachedMinusOne = false;

        for (int r = 1; r < s; ++r) {
            x = mul_mod(x, x, n);

            if (x == n - 1) {
                reachedMinusOne = true;
                break;
            }
        }

        if (!reachedMinusOne) return false;
    }

    return true;
}

u64 generate_prime(int bits) {
    if (bits < 8 || bits > 32) {
        throw RSAError(
            "This portable demonstration generates primes between 8 and 32 bits."
        );
    }

    std::random_device rd;
    std::mt19937_64 rng(rd());

    const u64 lower = 1ULL << (bits - 1);
    const u64 upper = (1ULL << bits) - 1;

    std::uniform_int_distribution<u64> distribution(lower, upper);

    while (true) {
        u64 candidate = distribution(rng);
        candidate |= 1ULL;

        if (is_probable_prime(candidate)) {
            return candidate;
        }
    }
}

enum class ReviewState {
    Draft,
    Open,
    ChangesRequested,
    Approved,
    Merged,
    Closed
};

struct StatusCheck {
    std::string name;
    bool required;
    bool passed;
};

struct Review {
    std::string reviewer;
    bool approval;
    bool dismissed;
    bool unresolvedConversation;
};

struct BranchProtection {
    bool requirePullRequest;
    bool requireApprovals;
    std::size_t requiredApprovalCount;
    bool requirePassingChecks;
    bool requireResolvedConversations;
    bool prohibitDirectPush;
    bool prohibitForcePush;
    bool requireLinearHistory;
};

struct PullRequest {
    int id;
    std::string sourceBranch;
    std::string targetBranch;
    ReviewState state;
    bool draft;
    bool hasMergeConflict;
    bool branchSynchronized;
    std::vector<Review> reviews;
    std::vector<StatusCheck> checks;
};

class GovernanceEngine {
public:
    static bool mergeEligible(
        const PullRequest& pr,
        const BranchProtection& policy
    ) {
        if (pr.state != ReviewState::Open &&
            pr.state != ReviewState::Approved) {
            return false;
        }

        if (pr.draft) return false;
        if (pr.hasMergeConflict) return false;
        if (!pr.branchSynchronized) return false;

        if (policy.requirePullRequest && pr.id <= 0) {
            return false;
        }

        if (policy.requireApprovals) {
            std::size_t approvals = 0;

            for (const auto& review : pr.reviews) {
                if (review.approval &&
                    !review.dismissed &&
                    !review.unresolvedConversation) {
                    ++approvals;
                }
            }

            if (approvals < policy.requiredApprovalCount) {
                return false;
            }
        }

        if (policy.requirePassingChecks) {
            for (const auto& check : pr.checks) {
                if (check.required && !check.passed) {
                    return false;
                }
            }
        }

        if (policy.requireResolvedConversations) {
            for (const auto& review : pr.reviews) {
                if (review.unresolvedConversation) {
                    return false;
                }
            }
        }

        return true;
    }
};

struct RSAKeyPair {
    u64 p;
    u64 q;
    u64 n;
    u64 phi;
    u64 e;
    u64 d;

    void validate() const {
        if (p * q != n) {
            throw RSAError("Invalid RSA modulus.");
        }

        if (gcd_u64(e, phi) != 1) {
            throw RSAError("e is not coprime with phi(n).");
        }

        if (mul_mod(e, d, phi) != 1) {
            throw RSAError("d is not the inverse of e modulo phi(n).");
        }
    }
};

RSAKeyPair generate_key_pair() {
    constexpr u64 e = 65537;

    while (true) {
        const u64 p = generate_prime(16);
        const u64 q = generate_prime(16);

        if (p == q) continue;

        const u64 n = p * q;
        const u64 phi = (p - 1) * (q - 1);

        if (gcd_u64(e, phi) != 1) continue;

        const u64 d = mod_inverse(e, phi);

        RSAKeyPair keys{p, q, n, phi, e, d};
        keys.validate();
        return keys;
    }
}

u64 rsa_encrypt(u64 message, const RSAKeyPair& key) {
    if (message >= key.n) {
        throw RSAError("Message must be smaller than n.");
    }

    return pow_mod(message, key.e, key.n);
}

u64 rsa_decrypt(u64 ciphertext, const RSAKeyPair& key) {
    if (ciphertext >= key.n) {
        throw RSAError("Ciphertext must be smaller than n.");
    }

    return pow_mod(ciphertext, key.d, key.n);
}

u64 rsa_decrypt_crt(u64 ciphertext, const RSAKeyPair& key) {
    if (ciphertext >= key.n) {
        throw RSAError("Ciphertext must be smaller than n.");
    }

    const u64 dp = key.d % (key.p - 1);
    const u64 dq = key.d % (key.q - 1);

    const u64 mp = pow_mod(ciphertext, dp, key.p);
    const u64 mq = pow_mod(ciphertext, dq, key.q);

    const u64 qInverse = mod_inverse(key.q, key.p);
    const u64 difference = (mp + key.p - mq) % key.p;
    const u64 h = mul_mod(difference, qInverse, key.p);

    return mq + h * key.q;
}

void validateArithmetic() {
    if (pow_mod(7, 560, 561) != 1) {
        throw RSAError("Modular exponentiation test failed.");
    }

    if (mod_inverse(17, 3120) != 2753) {
        throw RSAError("Modular inverse test failed.");
    }

    if (!is_probable_prime(101) || is_probable_prime(121)) {
        throw RSAError("Primality test failed.");
    }
}

void demonstrateGovernance() {
    BranchProtection policy{
        true,
        true,
        2,
        true,
        true,
        true,
        true,
        true
    };

    PullRequest pr{
        42,
        "feature/rsa-policy",
        "main",
        ReviewState::Open,
        false,
        false,
        true,
        {
            {"reviewer-a", true, false, false},
            {"reviewer-b", true, false, false}
        },
        {
            {"unit-tests", true, true},
            {"security-scan", true, true},
            {"documentation", false, false}
        }
    };

    const bool eligible = GovernanceEngine::mergeEligible(pr, policy);

    std::cout << "\nRepository governance case study\n";
    std::cout << "Pull Request #" << pr.id << '\n';
    std::cout << "Merge eligible: " << std::boolalpha << eligible << '\n';

    // A stale branch blocks merging even when the review decisions are valid.
    pr.branchSynchronized = false;
    std::cout << "After branch becomes stale: "
              << GovernanceEngine::mergeEligible(pr, policy) << '\n';
}

int main() {
    try {
        validateArithmetic();

        const RSAKeyPair keys = generate_key_pair();

        std::cout << "RSA mathematical case study\n";
        std::cout << "p   = " << keys.p << '\n';
        std::cout << "q   = " << keys.q << '\n';
        std::cout << "n   = " << keys.n << '\n';
        std::cout << "phi = " << keys.phi << '\n';
        std::cout << "e   = " << keys.e << '\n';
        std::cout << "d   = " << keys.d << '\n';

        const u64 message = 12345;
        const u64 ciphertext = rsa_encrypt(message, keys);
        const u64 recovered = rsa_decrypt(ciphertext, keys);
        const u64 crtRecovered = rsa_decrypt_crt(ciphertext, keys);

        if (recovered != message || crtRecovered != message) {
            throw RSAError("RSA round-trip failed.");
        }

        std::cout << "\nRSA operation\n";
        std::cout << "message    = " << message << '\n';
        std::cout << "ciphertext = " << ciphertext << '\n';
        std::cout << "decrypted  = " << recovered << '\n';
        std::cout << "CRT        = " << crtRecovered << '\n';

        try {
            rsa_encrypt(keys.n, keys);
        } catch (const RSAError& error) {
            std::cout << "Expected validation failure: "
                      << error.what() << '\n';
        }

        demonstrateGovernance();

        /*
         * The program deliberately uses small demonstration primes.
         * Production RSA requires cryptographically strong random generation,
         * substantially larger moduli, secure padding, side-channel defenses,
         * and a well-reviewed cryptographic implementation.
         */
    } catch (const std::exception& error) {
        std::cerr << "Execution failed: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
