#include <algorithm>
#include <array>
#include <cstdint>
#include <exception>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

/*
 * Rainbow Tables and Password Attacks
 *
 * Repository-independent password governance engine.
 *
 * Demonstrates:
 * - Attack classification
 * - Synthetic rainbow-table behavior
 * - Password hash records and salt isolation
 * - Password policy evaluation
 * - Account authentication states
 * - Failure thresholds
 * - Security audit decisions
 *
 * Synthetic hashing uses a deterministic educational digest.
 * It is NOT cryptographically secure and must never store real passwords.
 */

enum class AttackType {
    Dictionary,
    BruteForce,
    RainbowTable,
    PasswordSpraying,
    CredentialStuffing,
    Phishing
};

enum class AccountStatus {
    Active,
    Locked,
    Disabled
};

enum class Decision {
    Accepted,
    Rejected,
    Locked,
    Disabled
};

string toString(AttackType attack) {
    switch (attack) {
        case AttackType::Dictionary: return "Dictionary";
        case AttackType::BruteForce: return "Brute force";
        case AttackType::RainbowTable: return "Rainbow table";
        case AttackType::PasswordSpraying: return "Password spraying";
        case AttackType::CredentialStuffing: return "Credential stuffing";
        case AttackType::Phishing: return "Phishing";
    }

    throw logic_error("Unknown attack type");
}

string toString(Decision decision) {
    switch (decision) {
        case Decision::Accepted: return "Accepted";
        case Decision::Rejected: return "Rejected";
        case Decision::Locked: return "Locked";
        case Decision::Disabled: return "Disabled";
    }

    throw logic_error("Unknown decision");
}

struct PasswordPolicy {
    size_t minimumLength = 14;
    size_t maximumLength = 128;
    bool requireUppercase = true;
    bool requireLowercase = true;
    bool requireDigit = true;
    bool requireSymbol = true;

    vector<string> validate(const string& password) const {
        vector<string> errors;

        if (password.size() < minimumLength) {
            errors.push_back("Password is too short");
        }

        if (password.size() > maximumLength) {
            errors.push_back("Password is too long");
        }

        bool upper = false;
        bool lower = false;
        bool digit = false;
        bool symbol = false;

        for (unsigned char c : password) {
            if (c >= 'A' && c <= 'Z') upper = true;
            else if (c >= 'a' && c <= 'z') lower = true;
            else if (c >= '0' && c <= '9') digit = true;
            else symbol = true;
        }

        if (requireUppercase && !upper)
            errors.push_back("Uppercase character required");

        if (requireLowercase && !lower)
            errors.push_back("Lowercase character required");

        if (requireDigit && !digit)
            errors.push_back("Digit required");

        if (requireSymbol && !symbol)
            errors.push_back("Symbol required");

        return errors;
    }
};

/*
 * FNV-1a is used solely as a deterministic synthetic hash
 * for demonstrating table construction and lookup.
 */
class SyntheticHash {
public:
    static string calculate(const string& input) {
        uint64_t hash = 14695981039346656037ULL;

        for (unsigned char c : input) {
            hash ^= c;
            hash *= 1099511628211ULL;
        }

        stringstream stream;
        stream << hex << setw(16) << setfill('0') << hash;

        return stream.str();
    }
};

class SyntheticRainbowTable {
private:
    string alphabet;
    size_t passwordLength;
    size_t chainLength;
    size_t spaceSize;

    unordered_map<string, string> endpoints;

    size_t integerPower(size_t base, size_t exponent) const {
        size_t result = 1;

        for (size_t i = 0; i < exponent; ++i) {
            if (result > 1000000 / base) {
                throw invalid_argument("Search space too large");
            }

            result *= base;
        }

        return result;
    }

    string decode(size_t number) const {
        string result(passwordLength, alphabet[0]);

        for (size_t i = 0; i < passwordLength; ++i) {
            result[passwordLength - i - 1] =
                alphabet[number % alphabet.size()];

            number /= alphabet.size();
        }

        return result;
    }

    string reduce(const string& digest, size_t position) const {
        uint64_t number = stoull(digest, nullptr, 16);

        number += static_cast<uint64_t>(position) * 104729ULL;
        number %= spaceSize;

        return decode(static_cast<size_t>(number));
    }

public:
    SyntheticRainbowTable(
        string alphabetValue = "abcd",
        size_t passwordLengthValue = 3,
        size_t chainLengthValue = 8
    )
        : alphabet(move(alphabetValue)),
          passwordLength(passwordLengthValue),
          chainLength(chainLengthValue) {

        if (alphabet.empty() ||
            set<char>(alphabet.begin(), alphabet.end()).size()
                != alphabet.size()) {
            throw invalid_argument("Alphabet must contain unique characters");
        }

        if (passwordLength == 0 ||
            passwordLength > 5 ||
            chainLength == 0 ||
            chainLength > 32) {
            throw invalid_argument("Invalid table dimensions");
        }

        spaceSize = integerPower(alphabet.size(), passwordLength);
    }

    void build() {
        endpoints.clear();

        for (size_t i = 0; i < spaceSize; ++i) {
            string start = decode(i);
            string current = start;

            for (size_t position = 0; position < chainLength; ++position) {
                current = reduce(
                    SyntheticHash::calculate(current),
                    position
                );
            }

            endpoints.emplace(current, start);
        }
    }

    optional<string> lookup(const string& targetHash) const {
        if (targetHash.size() != 16) {
            throw invalid_argument("Invalid synthetic hash length");
        }

        for (char c : targetHash) {
            if (!isxdigit(static_cast<unsigned char>(c))) {
                throw invalid_argument("Invalid hexadecimal hash");
            }
        }

        for (int position = static_cast<int>(chainLength) - 1;
             position >= 0;
             --position) {

            string current = targetHash;

            for (size_t column = static_cast<size_t>(position);
                 column < chainLength;
                 ++column) {

                current = reduce(current, column);

                if (column < chainLength - 1) {
                    current = SyntheticHash::calculate(current);
                }
            }

            auto found = endpoints.find(current);

            if (found == endpoints.end()) {
                continue;
            }

            string candidate = found->second;

            for (size_t column = 0; column < chainLength; ++column) {
                string digest = SyntheticHash::calculate(candidate);

                if (digest == targetHash) {
                    return candidate;
                }

                candidate = reduce(digest, column);
            }
        }

        return nullopt;
    }

    size_t getSpaceSize() const {
        return spaceSize;
    }

    size_t getStoredChains() const {
        return endpoints.size();
    }
};

struct PasswordRecord {
    string username;
    string syntheticSalt;
    string syntheticDigest;
};

/*
 * This class intentionally does not implement production password
 * storage. Production systems must use a vetted Argon2id, scrypt,
 * or PBKDF2 implementation with cryptographically random salts.
 */
class DemonstrationCredentialStore {
private:
    unordered_map<string, PasswordRecord> records;
    PasswordPolicy policy;

    unordered_set<string> commonPasswords = {
        "password",
        "password123",
        "admin123",
        "qwerty123",
        "welcome123"
    };

    static string digest(const string& salt, const string& password) {
        return SyntheticHash::calculate(salt + password);
    }

public:
    bool registerAccount(
        const string& username,
        const string& password,
        const string& salt
    ) {
        if (username.empty() || username.size() > 40) {
            throw invalid_argument("Invalid username");
        }

        if (records.count(username)) {
            throw invalid_argument("Duplicate username");
        }

        if (commonPasswords.count(password)) {
            throw invalid_argument("Common password rejected");
        }

        if (!policy.validate(password).empty()) {
            throw invalid_argument("Password policy violation");
        }

        if (salt.empty()) {
            throw invalid_argument("Salt cannot be empty");
        }

        PasswordRecord record{
            username,
            salt,
            digest(salt, password)
        };

        records.emplace(username, move(record));
        return true;
    }

    bool authenticate(
        const string& username,
        const string& password
    ) const {
        auto found = records.find(username);

        if (found == records.end()) {
            return false;
        }

        const string candidate = digest(
            found->second.syntheticSalt,
            password
        );

        return candidate == found->second.syntheticDigest;
    }

    size_t size() const {
        return records.size();
    }
};

struct AuthenticationResult {
    Decision decision;
    size_t failedAttempts;
};

class Account {
private:
    string username;
    AccountStatus status = AccountStatus::Active;
    size_t failedAttempts = 0;
    size_t maximumFailures;

public:
    Account(string usernameValue, size_t maximumFailuresValue)
        : username(move(usernameValue)),
          maximumFailures(maximumFailuresValue) {

        if (username.empty() || maximumFailures == 0) {
            throw invalid_argument("Invalid account configuration");
        }
    }

    AuthenticationResult authenticate(bool validPassword) {
        if (status == AccountStatus::Disabled) {
            return {Decision::Disabled, failedAttempts};
        }

        if (status == AccountStatus::Locked) {
            return {Decision::Locked, failedAttempts};
        }

        if (validPassword) {
            failedAttempts = 0;
            return {Decision::Accepted, failedAttempts};
        }

        ++failedAttempts;

        if (failedAttempts >= maximumFailures) {
            status = AccountStatus::Locked;
            return {Decision::Locked, failedAttempts};
        }

        return {Decision::Rejected, failedAttempts};
    }

    void disable() {
        status = AccountStatus::Disabled;
    }

    const string& getUsername() const {
        return username;
    }
};

struct SecurityFinding {
    AttackType attack;
    bool successful;
    size_t candidatesTested;
    string description;
};

class GovernanceEngine {
private:
    vector<SecurityFinding> findings;

public:
    void record(SecurityFinding finding) {
        findings.push_back(move(finding));
    }

    void report() const {
        cout << "\nSecurity audit report\n";

        for (const auto& finding : findings) {
            cout << toString(finding.attack)
                 << " | Successful: "
                 << boolalpha << finding.successful
                 << " | Tested: "
                 << finding.candidatesTested
                 << " | " << finding.description
                 << '\n';
        }
    }
};

void demonstrate() {
    cout << "RAINBOW TABLES AND PASSWORD SECURITY\n";
    cout << string(55, '=') << '\n';

    cout << "\n1. Attack classification\n";

    vector<AttackType> attacks = {
        AttackType::Dictionary,
        AttackType::BruteForce,
        AttackType::RainbowTable,
        AttackType::PasswordSpraying,
        AttackType::CredentialStuffing,
        AttackType::Phishing
    };

    for (auto attack : attacks) {
        cout << "- " << toString(attack) << '\n';
    }

    cout << "\n2. Synthetic rainbow-table experiment\n";

    SyntheticRainbowTable table;
    table.build();

    const string password = "cab";
    const string target = SyntheticHash::calculate(password);

    auto recovered = table.lookup(target);

    cout << "Search space: " << table.getSpaceSize() << '\n';
    cout << "Stored chains: " << table.getStoredChains() << '\n';
    cout << "Synthetic target: " << target << '\n';

    if (!recovered || *recovered != password) {
        throw runtime_error("Synthetic table verification failed");
    }

    cout << "Recovered value: " << *recovered << '\n';

    cout << "\n3. Password policy validation\n";

    PasswordPolicy policy;

    vector<string> samples = {
        "short",
        "password123",
        "SyntheticExample!2026"
    };

    for (const auto& sample : samples) {
        auto errors = policy.validate(sample);

        cout << sample << ": "
             << (errors.empty() ? "Accepted" : "Rejected")
             << '\n';

        for (const auto& error : errors) {
            cout << "  " << error << '\n';
        }
    }

    cout << "\n4. Synthetic credential storage\n";

    DemonstrationCredentialStore store;

    store.registerAccount(
        "security_user",
        "SyntheticExample!2026",
        "unique-synthetic-salt-001"
    );

    cout << "Stored accounts: " << store.size() << '\n';

    cout << "Valid authentication: "
         << boolalpha
         << store.authenticate(
                "security_user",
                "SyntheticExample!2026"
            )
         << '\n';

    cout << "Invalid authentication: "
         << store.authenticate(
                "security_user",
                "IncorrectExample!2026"
            )
         << '\n';

    cout << "\n5. Authentication state transitions\n";

    Account account("analyst", 3);

    vector<bool> attempts = {
        false, false, false, true
    };

    for (bool valid : attempts) {
        auto result = account.authenticate(valid);

        cout << toString(result.decision)
             << " | Failed attempts: "
             << result.failedAttempts
             << '\n';
    }

    cout << "\n6. Security audit findings\n";

    GovernanceEngine engine;

    engine.record({
        AttackType::Dictionary,
        true,
        3,
        "Synthetic weak-password candidate matched"
    });

    engine.record({
        AttackType::RainbowTable,
        true,
        table.getStoredChains(),
        "Synthetic precomputed chain lookup"
    });

    engine.record({
        AttackType::CredentialStuffing,
        false,
        0,
        "No external authentication attempts performed"
    });

    engine.report();

    cout << "\n7. Production security requirements\n";

    vector<string> controls = {
        "Use Argon2id or appropriately configured PBKDF2",
        "Generate a unique cryptographically random salt per account",
        "Use MFA and phishing-resistant authentication",
        "Apply rate limiting and risk-based controls",
        "Detect credential stuffing and password spraying",
        "Protect password hashes with restricted access",
        "Use constant-time comparison for credential verification",
        "Monitor authentication failures",
        "Secure account recovery and session invalidation"
    };

    for (const auto& control : controls) {
        cout << "- " << control << '\n';
    }

    cout << "\nAll synthetic security checks passed.\n";
}

int main() {
    try {
        demonstrate();
        return 0;
    } catch (const exception& error) {
        cerr << "Security laboratory error: "
             << error.what() << '\n';

        return 1;
    }
}
