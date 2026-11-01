#!/usr/bin/env python3
"""
Rainbow Tables and Password Attacks
Defensive password-security laboratory.

Demonstrates:
- Password attack classifications
- Synthetic rainbow-table construction and lookup
- Hash collisions and chain limitations
- Salt effectiveness against precomputation
- PBKDF2 password storage
- Password policy validation
- Offline password-audit simulation
- Security testing and reporting

Only synthetic demonstration credentials are processed.
No network authentication or real credential databases are accessed.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import string
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class AttackType(Enum):
    DICTIONARY = "Dictionary attack"
    BRUTE_FORCE = "Brute-force attack"
    RAINBOW_TABLE = "Rainbow-table attack"
    PASSWORD_SPRAYING = "Password spraying"
    CREDENTIAL_STUFFING = "Credential stuffing"
    PHISHING = "Phishing"


class PasswordStatus(Enum):
    ACCEPTED = "accepted"
    TOO_SHORT = "too_short"
    TOO_LONG = "too_long"
    COMMON = "common"
    REPEATED = "repeated"


@dataclass(frozen=True)
class SecurityPolicy:
    minimum_length: int = 14
    maximum_length: int = 128
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digit: bool = True
    require_symbol: bool = True

    def validate(self, password: str) -> tuple[bool, list[str]]:
        errors = []

        if len(password) < self.minimum_length:
            errors.append("Password is too short.")

        if len(password) > self.maximum_length:
            errors.append("Password exceeds maximum length.")

        if self.require_uppercase and not any(c.isupper() for c in password):
            errors.append("An uppercase character is required.")

        if self.require_lowercase and not any(c.islower() for c in password):
            errors.append("A lowercase character is required.")

        if self.require_digit and not any(c.isdigit() for c in password):
            errors.append("A digit is required.")

        if self.require_symbol and not any(
            not c.isalnum() for c in password
        ):
            errors.append("A non-alphanumeric character is required.")

        return not errors, errors


@dataclass
class AuditResult:
    attack_type: AttackType
    tested_candidates: int
    recovered: bool
    matched_value: Optional[str] = None
    explanation: str = ""


@dataclass
class PasswordRecord:
    username: str
    salt: bytes
    password_hash: bytes
    iterations: int


class PasswordHasher:
    """PBKDF2-HMAC-SHA256 password storage demonstration."""

    def __init__(self, iterations: int = 600_000):
        if iterations < 100_000:
            raise ValueError("Iteration count is below the security minimum.")
        self.iterations = iterations

    def create(self, username: str, password: str) -> PasswordRecord:
        if not username.strip():
            raise ValueError("Username cannot be empty.")

        salt = secrets.token_bytes(16)

        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            self.iterations,
            dklen=32
        )

        return PasswordRecord(
            username=username,
            salt=salt,
            password_hash=digest,
            iterations=self.iterations
        )

    @staticmethod
    def verify(password: str, record: PasswordRecord) -> bool:
        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            record.salt,
            record.iterations,
            dklen=32
        )

        return hmac.compare_digest(candidate, record.password_hash)


class SyntheticRainbowTable:
    """
    Educational rainbow table over a deliberately tiny keyspace.

    Each chain position uses a different deterministic reduction
    function. The implementation is not intended for real passwords.
    """

    def __init__(
        self,
        alphabet: str = "abcd",
        password_length: int = 3,
        chain_length: int = 8
    ):
        if not alphabet or len(set(alphabet)) != len(alphabet):
            raise ValueError("Alphabet must contain unique characters.")

        if password_length < 1 or chain_length < 1:
            raise ValueError("Lengths must be positive.")

        self.alphabet = alphabet
        self.password_length = password_length
        self.chain_length = chain_length
        self.table: dict[str, str] = {}

        self.space_size = len(alphabet) ** password_length

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(
            password.encode("utf-8")
        ).hexdigest()

    def reduce_hash(self, digest: str, position: int) -> str:
        """
        Map a digest into the finite demonstration password space.
        Position-dependent reduction differentiates chain columns.
        """
        number = (
            int(digest[:16], 16) + position * 104729
        ) % self.space_size

        chars = []

        for _ in range(self.password_length):
            chars.append(self.alphabet[number % len(self.alphabet)])
            number //= len(self.alphabet)

        return "".join(reversed(chars))

    def build(self) -> None:
        self.table.clear()

        # Store chain endpoints and their starting passwords.
        for number in range(self.space_size):
            value = number
            chars = []

            for _ in range(self.password_length):
                chars.append(self.alphabet[value % len(self.alphabet)])
                value //= len(self.alphabet)

            start = "".join(reversed(chars))
            current = start

            for position in range(self.chain_length):
                digest = self.hash_password(current)
                current = self.reduce_hash(digest, position)

            endpoint = current
            self.table.setdefault(endpoint, start)

    def lookup(self, target_hash: str) -> Optional[str]:
        if len(target_hash) != 64:
            raise ValueError("Expected a SHA-256 hexadecimal digest.")

        try:
            bytes.fromhex(target_hash)
        except ValueError as exc:
            raise ValueError("Invalid hexadecimal hash.") from exc

        # Reconstruct possible chain suffixes from each column.
        for position in range(self.chain_length - 1, -1, -1):
            current = target_hash

            for column in range(position, self.chain_length):
                current = self.reduce_hash(current, column)

                if column < self.chain_length - 1:
                    current = self.hash_password(current)

            start = self.table.get(current)

            if start is None:
                continue

            # Regenerate the chain to verify the actual target.
            candidate = start

            for column in range(self.chain_length):
                digest = self.hash_password(candidate)

                if hmac.compare_digest(digest, target_hash):
                    return candidate

                candidate = self.reduce_hash(digest, column)

        return None


class PasswordSecurityLab:
    def __init__(self):
        self.policy = SecurityPolicy()
        self.hasher = PasswordHasher()
        self.records: dict[str, PasswordRecord] = {}
        self.audit_history: list[AuditResult] = []
        self.common_passwords = {
            "password", "password123", "admin123",
            "qwerty123", "welcome123"
        }

    def register(self, username: str, password: str) -> None:
        if username in self.records:
            raise ValueError("Username already exists.")

        if password.lower() in self.common_passwords:
            raise ValueError("Common passwords are not permitted.")

        valid, errors = self.policy.validate(password)

        if not valid:
            raise ValueError("; ".join(errors))

        self.records[username] = self.hasher.create(
            username, password
        )

    def authenticate(self, username: str, password: str) -> bool:
        record = self.records.get(username)

        if record is None:
            return False

        return self.hasher.verify(password, record)

    def simulate_dictionary_audit(
        self,
        target_hash: str,
        candidates: list[str]
    ) -> AuditResult:
        """Test a small synthetic candidate list against a synthetic hash."""
        tested = 0

        for candidate in candidates:
            tested += 1

            digest = hashlib.sha256(
                candidate.encode("utf-8")
            ).hexdigest()

            if hmac.compare_digest(digest, target_hash):
                result = AuditResult(
                    AttackType.DICTIONARY,
                    tested,
                    True,
                    candidate,
                    "Synthetic weak-password match."
                )
                self.audit_history.append(result)
                return result

        result = AuditResult(
            AttackType.DICTIONARY,
            tested,
            False,
            explanation="No candidate matched."
        )

        self.audit_history.append(result)
        return result

    def attack_explanation(self) -> dict[str, str]:
        return {
            AttackType.DICTIONARY.value:
                "Tests previously selected candidate passwords.",
            AttackType.BRUTE_FORCE.value:
                "Searches a defined password search space.",
            AttackType.RAINBOW_TABLE.value:
                "Uses precomputed hash chains to reduce repeated computation.",
            AttackType.PASSWORD_SPRAYING.value:
                "Attempts a small set of passwords across multiple accounts.",
            AttackType.CREDENTIAL_STUFFING.value:
                "Reuses exposed username-password combinations.",
            AttackType.PHISHING.value:
                "Uses deception to obtain authentication secrets."
        }


def demonstrate() -> None:
    print("=" * 65)
    print("RAINBOW TABLES AND PASSWORD SECURITY LAB")
    print("=" * 65)

    lab = PasswordSecurityLab()

    print("\n1. Password attack classifications")

    for attack, explanation in lab.attack_explanation().items():
        print(f"{attack}: {explanation}")

    print("\n2. Synthetic rainbow-table experiment")

    rainbow = SyntheticRainbowTable(
        alphabet="abcd",
        password_length=3,
        chain_length=8
    )

    rainbow.build()

    synthetic_password = "cab"
    target = rainbow.hash_password(synthetic_password)

    recovered = rainbow.lookup(target)

    print(f"Search-space size: {rainbow.space_size}")
    print(f"Stored chains: {len(rainbow.table)}")
    print(f"Target SHA-256: {target}")
    print(f"Recovered value: {recovered}")

    assert recovered == synthetic_password

    print("\n3. Hash collisions and table limitations")

    print("Chain merging can reduce effective table coverage.")
    print("Truncation and reduction mappings can create collisions.")
    print("A rainbow table does not guarantee recovery of every password.")

    print("\n4. Unsalted hash dictionary audit")

    weak_password = "password123"

    weak_hash = hashlib.sha256(
        weak_password.encode("utf-8")
    ).hexdigest()

    candidates = [
        "admin",
        "welcome",
        "password123",
        "letmein"
    ]

    audit = lab.simulate_dictionary_audit(
        weak_hash, candidates
    )

    print(f"Attack: {audit.attack_type.value}")
    print(f"Candidates tested: {audit.tested_candidates}")
    print(f"Recovered: {audit.recovered}")
    print(f"Match: {audit.matched_value}")

    print("\n5. Salt effectiveness")

    first = lab.hasher.create("alice", "SyntheticExample!2026")
    second = lab.hasher.create("bob", "SyntheticExample!2026")

    print(f"Same password: True")
    print(f"Different salts: {first.salt != second.salt}")
    print(f"Different hashes: {first.password_hash != second.password_hash}")

    assert first.salt != second.salt
    assert first.password_hash != second.password_hash

    print("\n6. Secure password registration")

    try:
        lab.register("alice", "SyntheticExample!2026")
        print("Registration successful.")
    except ValueError as exc:
        print(f"Registration rejected: {exc}")

    print(
        "Authentication:",
        lab.authenticate("alice", "SyntheticExample!2026")
    )

    print(
        "Incorrect password:",
        lab.authenticate("alice", "IncorrectPassword!2026")
    )

    print("\n7. Input validation")

    for sample in ("short", "password123", "ValidExample!2026"):
        valid, errors = lab.policy.validate(sample)
        print(f"{sample}: valid={valid}, errors={errors}")

    print("\n8. Security controls")

    controls = [
        "Unique random salts for every password",
        "Memory-hard password hashing such as Argon2id",
        "PBKDF2 or scrypt when appropriate",
        "MFA and phishing-resistant authentication",
        "Rate limiting and progressive authentication delays",
        "Credential-stuffing detection",
        "Secure password-reset procedures",
        "Protected password-hash storage",
        "Audit logging without recording passwords",
        "Compromised-password screening"
    ]

    for control in controls:
        print(f"- {control}")

    print("\nAll synthetic security assertions passed.")


if __name__ == "__main__":
    demonstrate()
