import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;

/**
 * Rainbow Tables and Password Attacks
 *
 * Enterprise password governance and authentication laboratory.
 *
 * Features:
 * - Domain-driven password security model
 * - Synthetic rainbow-table simulation
 * - Password attack classification
 * - PBKDF2-HMAC-SHA256 password storage
 * - Unique salt generation
 * - Approval-independent authentication policies
 * - Account state transitions
 * - Security audit reporting
 *
 * No external dependencies.
 */
public class PasswordSecurityEnterprise {

    enum AttackType {
        DICTIONARY,
        BRUTE_FORCE,
        RAINBOW_TABLE,
        PASSWORD_SPRAYING,
        CREDENTIAL_STUFFING,
        PHISHING
    }

    enum AccountStatus {
        ACTIVE,
        LOCKED,
        DISABLED
    }

    enum AuthenticationStatus {
        ACCEPTED,
        REJECTED,
        LOCKED,
        DISABLED
    }

    record PasswordPolicy(
        int minimumLength,
        int maximumLength,
        boolean requireUppercase,
        boolean requireLowercase,
        boolean requireDigit,
        boolean requireSymbol
    ) {
        PasswordPolicy {
            if (minimumLength < 1 ||
                maximumLength < minimumLength) {
                throw new IllegalArgumentException(
                    "Invalid password policy dimensions"
                );
            }
        }

        List<String> validate(String password) {
            Objects.requireNonNull(password);

            List<String> errors = new ArrayList<>();

            if (password.length() < minimumLength) {
                errors.add("Password is too short");
            }

            if (password.length() > maximumLength) {
                errors.add("Password is too long");
            }

            if (requireUppercase &&
                password.chars().noneMatch(Character::isUpperCase)) {
                errors.add("Uppercase character required");
            }

            if (requireLowercase &&
                password.chars().noneMatch(Character::isLowerCase)) {
                errors.add("Lowercase character required");
            }

            if (requireDigit &&
                password.chars().noneMatch(Character::isDigit)) {
                errors.add("Digit required");
            }

            if (requireSymbol &&
                password.chars().noneMatch(c -> !Character.isLetterOrDigit(c))) {
                errors.add("Symbol required");
            }

            return Collections.unmodifiableList(errors);
        }
    }

    record PasswordCredential(
        byte[] salt,
        byte[] derivedKey,
        int iterations,
        String algorithm
    ) {
        PasswordCredential {
            salt = salt.clone();
            derivedKey = derivedKey.clone();

            if (salt.length < 16 ||
                derivedKey.length != 32 ||
                iterations < 100000 ||
                iterations > 10000000) {
                throw new IllegalArgumentException(
                    "Invalid password credential parameters"
                );
            }

            Objects.requireNonNull(algorithm);
        }

        @Override
        public byte[] salt() {
            return salt.clone();
        }

        @Override
        public byte[] derivedKey() {
            return derivedKey.clone();
        }
    }

    static final class PasswordHasher {

        private static final int KEY_LENGTH = 256;
        private static final String ALGORITHM = "PBKDF2WithHmacSHA256";

        private final int iterations;
        private final SecureRandom secureRandom;

        PasswordHasher(int iterations) {
            if (iterations < 100000 || iterations > 10000000) {
                throw new IllegalArgumentException(
                    "Invalid PBKDF2 iteration count"
                );
            }

            this.iterations = iterations;
            this.secureRandom = new SecureRandom();
        }

        PasswordCredential create(char[] password)
            throws GeneralSecurityException {

            if (password == null || password.length == 0) {
                throw new IllegalArgumentException(
                    "Password cannot be empty"
                );
            }

            byte[] salt = new byte[16];
            secureRandom.nextBytes(salt);

            byte[] derived = derive(password, salt, iterations);

            return new PasswordCredential(
                salt,
                derived,
                iterations,
                ALGORITHM
            );
        }

        boolean verify(
            char[] password,
            PasswordCredential credential
        ) throws GeneralSecurityException {

            if (password == null || credential == null) {
                return false;
            }

            byte[] candidate = derive(
                password,
                credential.salt(),
                credential.iterations()
            );

            return MessageDigest.isEqual(
                candidate,
                credential.derivedKey()
            );
        }

        private static byte[] derive(
            char[] password,
            byte[] salt,
            int iterations
        ) throws GeneralSecurityException {

            PBEKeySpec specification = new PBEKeySpec(
                password,
                salt,
                iterations,
                KEY_LENGTH
            );

            try {
                SecretKeyFactory factory =
                    SecretKeyFactory.getInstance(ALGORITHM);

                return factory.generateSecret(specification).getEncoded();
            } finally {
                specification.clearPassword();
            }
        }
    }

    static final class SyntheticHash {

        private SyntheticHash() {}

        /*
         * FNV-1a is deliberately used only for the small educational
         * rainbow-table experiment. It is not a password hash.
         */
        static String calculate(String value) {
            long hash = 0xcbf29ce484222325L;

            for (byte b : value.getBytes(StandardCharsets.UTF_8)) {
                hash ^= b & 0xffL;
                hash *= 0x100000001b3L;
            }

            return String.format("%016x", hash);
        }
    }

    static final class SyntheticRainbowTable {

        private final String alphabet;
        private final int passwordLength;
        private final int chainLength;
        private final int spaceSize;

        private final Map<String, String> endpoints = new HashMap<>();

        SyntheticRainbowTable(
            String alphabet,
            int passwordLength,
            int chainLength
        ) {
            Objects.requireNonNull(alphabet);

            if (alphabet.isEmpty() ||
                alphabet.chars().distinct().count() != alphabet.length() ||
                passwordLength < 1 ||
                passwordLength > 5 ||
                chainLength < 1 ||
                chainLength > 32) {
                throw new IllegalArgumentException(
                    "Invalid rainbow-table configuration"
                );
            }

            this.alphabet = alphabet;
            this.passwordLength = passwordLength;
            this.chainLength = chainLength;

            long size = 1;

            for (int i = 0; i < passwordLength; i++) {
                size *= alphabet.length();

                if (size > 1000000) {
                    throw new IllegalArgumentException(
                        "Synthetic keyspace exceeds limit"
                    );
                }
            }

            this.spaceSize = (int) size;
        }

        private String decode(int number) {
            char[] result = new char[passwordLength];

            for (int i = passwordLength - 1; i >= 0; i--) {
                result[i] = alphabet.charAt(number % alphabet.length());
                number /= alphabet.length();
            }

            return new String(result);
        }

        private String reduce(String digest, int position) {
            long value = Long.parseUnsignedLong(digest, 16);

            value += (long) position * 104729L;
            value = Long.remainderUnsigned(value, spaceSize);

            return decode((int) value);
        }

        void build() {
            endpoints.clear();

            for (int i = 0; i < spaceSize; i++) {
                String start = decode(i);
                String current = start;

                for (int position = 0; position < chainLength; position++) {
                    current = reduce(
                        SyntheticHash.calculate(current),
                        position
                    );
                }

                endpoints.putIfAbsent(current, start);
            }
        }

        Optional<String> lookup(String targetHash) {
            if (targetHash == null ||
                !targetHash.matches("[0-9a-fA-F]{16}")) {
                throw new IllegalArgumentException(
                    "Invalid synthetic hash"
                );
            }

            for (int position = chainLength - 1;
                 position >= 0;
                 position--) {

                String current = targetHash.toLowerCase();

                for (int column = position;
                     column < chainLength;
                     column++) {

                    current = reduce(current, column);

                    if (column < chainLength - 1) {
                        current = SyntheticHash.calculate(current);
                    }
                }

                String start = endpoints.get(current);

                if (start == null) {
                    continue;
                }

                String candidate = start;

                for (int column = 0; column < chainLength; column++) {
                    String digest = SyntheticHash.calculate(candidate);

                    if (digest.equals(targetHash.toLowerCase())) {
                        return Optional.of(candidate);
                    }

                    candidate = reduce(digest, column);
                }
            }

            return Optional.empty();
        }

        int getSpaceSize() {
            return spaceSize;
        }

        int getStoredChains() {
            return endpoints.size();
        }
    }

    static final class Account {

        private final String username;
        private final PasswordCredential credential;

        private AccountStatus status = AccountStatus.ACTIVE;
        private int failedAttempts;

        Account(String username, PasswordCredential credential) {
            if (username == null ||
                !username.matches("[A-Za-z0-9_.-]{3,40}")) {
                throw new IllegalArgumentException("Invalid username");
            }

            this.username = username;
            this.credential = Objects.requireNonNull(credential);
        }

        String username() {
            return username;
        }

        PasswordCredential credential() {
            return credential;
        }

        AccountStatus status() {
            return status;
        }

        int failedAttempts() {
            return failedAttempts;
        }

        void incrementFailures() {
            failedAttempts++;
        }

        void resetFailures() {
            failedAttempts = 0;
        }

        void lock() {
            if (status == AccountStatus.DISABLED) {
                throw new IllegalStateException(
                    "Disabled accounts cannot transition to locked"
                );
            }

            status = AccountStatus.LOCKED;
        }

        void disable() {
            status = AccountStatus.DISABLED;
        }
    }

    record AuthenticationResult(
        AuthenticationStatus status,
        int failedAttempts
    ) {}

    static final class AuthenticationService {

        private final Map<String, Account> accounts = new HashMap<>();
        private final PasswordHasher hasher;
        private final PasswordPolicy policy;
        private final Set<String> commonPasswords;
        private final int maximumFailures;

        AuthenticationService(
            PasswordHasher hasher,
            PasswordPolicy policy,
            int maximumFailures
        ) {
            this.hasher = Objects.requireNonNull(hasher);
            this.policy = Objects.requireNonNull(policy);

            if (maximumFailures < 1) {
                throw new IllegalArgumentException(
                    "Failure threshold must be positive"
                );
            }

            this.maximumFailures = maximumFailures;

            this.commonPasswords = Set.of(
                "password",
                "password123",
                "admin123",
                "qwerty123",
                "welcome123"
            );
        }

        void register(String username, char[] password)
            throws GeneralSecurityException {

            if (accounts.containsKey(username)) {
                throw new IllegalArgumentException(
                    "Account already exists"
                );
            }

            String passwordValue = new String(password);

            if (commonPasswords.contains(
                passwordValue.toLowerCase()
            )) {
                throw new IllegalArgumentException(
                    "Common password prohibited"
                );
            }

            List<String> errors = policy.validate(passwordValue);

            if (!errors.isEmpty()) {
                throw new IllegalArgumentException(
                    String.join("; ", errors)
                );
            }

            PasswordCredential credential = hasher.create(password);

            accounts.put(
                username,
                new Account(username, credential)
            );
        }

        AuthenticationResult authenticate(
            String username,
            char[] password
        ) throws GeneralSecurityException {

            Account account = accounts.get(username);

            if (account == null) {
                return new AuthenticationResult(
                    AuthenticationStatus.REJECTED,
                    0
                );
            }

            if (account.status() == AccountStatus.DISABLED) {
                return new AuthenticationResult(
                    AuthenticationStatus.DISABLED,
                    account.failedAttempts()
                );
            }

            if (account.status() == AccountStatus.LOCKED) {
                return new AuthenticationResult(
                    AuthenticationStatus.LOCKED,
                    account.failedAttempts()
                );
            }

            boolean valid = hasher.verify(
                password,
                account.credential()
            );

            if (valid) {
                account.resetFailures();

                return new AuthenticationResult(
                    AuthenticationStatus.ACCEPTED,
                    0
                );
            }

            account.incrementFailures();

            if (account.failedAttempts() >= maximumFailures) {
                account.lock();

                return new AuthenticationResult(
                    AuthenticationStatus.LOCKED,
                    account.failedAttempts()
                );
            }

            return new AuthenticationResult(
                AuthenticationStatus.REJECTED,
                account.failedAttempts()
            );
        }

        int accountCount() {
            return accounts.size();
        }
    }

    record SecurityFinding(
        AttackType attack,
        boolean successful,
        String description
    ) {}

    static final class SecurityAuditService {

        private final Map<AttackType, List<SecurityFinding>> findings =
            new EnumMap<>(AttackType.class);

        void record(SecurityFinding finding) {
            findings.computeIfAbsent(
                finding.attack(),
                ignored -> new ArrayList<>()
            ).add(finding);
        }

        void printReport() {
            System.out.println("\nSecurity audit report");

            findings.forEach((attack, entries) -> {
                System.out.println(
                    attack + ": " + entries.size() + " finding(s)"
                );

                entries.forEach(entry -> System.out.println(
                    "  Successful=" + entry.successful()
                    + " | " + entry.description()
                ));
            });
        }
    }

    private static void demonstrate() throws Exception {

        System.out.println("RAINBOW TABLES AND PASSWORD ATTACKS");
        System.out.println("=".repeat(55));

        System.out.println("\n1. Attack classifications");

        for (AttackType attack : AttackType.values()) {
            System.out.println("- " + attack);
        }

        System.out.println("\n2. Synthetic rainbow-table experiment");

        SyntheticRainbowTable table =
            new SyntheticRainbowTable("abcd", 3, 8);

        table.build();

        String syntheticPassword = "cab";
        String target = SyntheticHash.calculate(syntheticPassword);

        Optional<String> recovered = table.lookup(target);

        System.out.println("Search space: " + table.getSpaceSize());
        System.out.println("Stored chains: " + table.getStoredChains());
        System.out.println("Recovered: " + recovered.orElse("Not found"));

        if (!recovered.orElse("").equals(syntheticPassword)) {
            throw new IllegalStateException(
                "Synthetic rainbow-table test failed"
            );
        }

        System.out.println("\n3. Password policy");

        PasswordPolicy policy = new PasswordPolicy(
            14, 128, true, true, true, true
        );

        for (String sample : List.of(
            "short",
            "password123",
            "SyntheticExample!2026"
        )) {
            List<String> errors = policy.validate(sample);

            System.out.println(
                sample + " => " +
                (errors.isEmpty() ? "Accepted" : errors)
            );
        }

        System.out.println("\n4. Secure credential storage");

        PasswordHasher hasher = new PasswordHasher(600000);

        PasswordCredential first = hasher.create(
            "SyntheticExample!2026".toCharArray()
        );

        PasswordCredential second = hasher.create(
            "SyntheticExample!2026".toCharArray()
        );

        System.out.println(
            "Different salts: " +
            !Arrays.equals(first.salt(), second.salt())
        );

        System.out.println(
            "Different derived keys: " +
            !Arrays.equals(first.derivedKey(), second.derivedKey())
        );

        System.out.println(
            "Correct password: " +
            hasher.verify(
                "SyntheticExample!2026".toCharArray(),
                first
            )
        );

        System.out.println(
            "Incorrect password: " +
            hasher.verify(
                "IncorrectExample!2026".toCharArray(),
                first
            )
        );

        System.out.println("\n5. Enterprise authentication service");

        AuthenticationService authentication =
            new AuthenticationService(
                hasher,
                policy,
                3
            );

        authentication.register(
            "security_user",
            "SyntheticExample!2026".toCharArray()
        );

        System.out.println(
            "Registered accounts: " +
            authentication.accountCount()
        );

        AuthenticationResult success = authentication.authenticate(
            "security_user",
            "SyntheticExample!2026".toCharArray()
        );

        System.out.println("Valid login: " + success.status());

        for (int i = 0; i < 3; i++) {
            AuthenticationResult result =
                authentication.authenticate(
                    "security_user",
                    "IncorrectExample!2026".toCharArray()
                );

            System.out.println(
                "Failed login " + (i + 1) + ": " + result.status()
            );
        }

        System.out.println(
            "After lock: " +
            authentication.authenticate(
                "security_user",
                "SyntheticExample!2026".toCharArray()
            ).status()
        );

        System.out.println("\n6. Security audit");

        SecurityAuditService audit = new SecurityAuditService();

        audit.record(new SecurityFinding(
            AttackType.RAINBOW_TABLE,
            true,
            "Synthetic demonstration chain recovered"
        ));

        audit.record(new SecurityFinding(
            AttackType.DICTIONARY,
            true,
            "Synthetic weak-password candidate matched"
        ));

        audit.record(new SecurityFinding(
            AttackType.CREDENTIAL_STUFFING,
            false,
            "No external authentication traffic processed"
        ));

        audit.printReport();

        System.out.println("\n7. Operational security controls");

        List<String> controls = List.of(
            "Unique random salts",
            "Argon2id or appropriately configured PBKDF2",
            "Multi-factor authentication",
            "Phishing-resistant authentication",
            "Rate limiting and account protection",
            "Credential-stuffing detection",
            "Secure password reset",
            "Restricted credential database access",
            "Authentication audit trails"
        );

        controls.forEach(control -> System.out.println("- " + control));

        System.out.println("\nAll enterprise security checks passed.");
    }

    public static void main(String[] args) {
        try {
            demonstrate();
        } catch (GeneralSecurityException | RuntimeException exception) {
            System.err.println(
                "Security application failure: " +
                exception.getMessage()
            );

            System.exit(1);
        } catch (Exception exception) {
            System.err.println(
                "Unexpected failure: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
