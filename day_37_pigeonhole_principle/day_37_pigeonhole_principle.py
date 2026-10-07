"""
Pigeonhole Principle: Basic, Generalized, and Computing Applications

This executable script develops the pigeonhole principle from its basic
form through generalized counting arguments and practical computing
applications.

The central idea is simple:

    If more objects are placed into fewer containers, at least one container
    receives more than one object.

Generalized form:

    If n objects are distributed among k containers, some container contains
    at least ceil(n / k) objects.

The examples deliberately use different computing scenarios so that the
principle is treated as a reasoning tool rather than as a single formula.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from math import ceil, comb
from typing import Callable, Iterable, Sequence
import hashlib
import random
import string


def banner(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


# ---------------------------------------------------------------------------
# Core mathematical operations
# ---------------------------------------------------------------------------

def minimum_guaranteed_collision(objects: int, containers: int) -> int:
    """
    Return the minimum occupancy that some container must have.

    By the generalized pigeonhole principle this is ceil(objects / containers).
    """
    if objects < 0:
        raise ValueError("objects cannot be negative")
    if containers <= 0:
        raise ValueError("containers must be positive")

    if objects == 0:
        return 0

    return ceil(objects / containers)


def objects_needed_for_at_least(
    containers: int,
    target_occupancy: int,
) -> int:
    """
    Return the minimum number of objects required to guarantee that some
    container contains at least target_occupancy objects.

    If every container had at most target_occupancy - 1 objects, there could
    be at most containers * (target_occupancy - 1) objects.

    Therefore one additional object forces the desired occupancy.
    """
    if containers <= 0:
        raise ValueError("containers must be positive")
    if target_occupancy <= 0:
        raise ValueError("target_occupancy must be positive")

    return containers * (target_occupancy - 1) + 1


def basic_pigeonhole(objects: int, containers: int) -> bool:
    """
    Basic principle: if objects > containers, a collision is guaranteed.
    """
    if objects < 0 or containers <= 0:
        raise ValueError("invalid object/container counts")

    return objects > containers


def demonstrate_basic_form() -> None:
    banner("Basic Pigeonhole Principle")

    # There are 13 students and 12 possible birth months.
    # Two students must therefore share a birth month.
    students = 13
    months = 12

    print(f"Students: {students}")
    print(f"Possible birth months: {months}")
    print(f"Guaranteed shared month: {basic_pigeonhole(students, months)}")

    # The result is guaranteed without knowing any student's actual month.
    print(
        "Reason: assigning 13 students to 12 months creates more objects "
        "than containers."
    )


# ---------------------------------------------------------------------------
# Generalized principle
# ---------------------------------------------------------------------------

def demonstrate_generalized_form() -> None:
    banner("Generalized Pigeonhole Principle")

    examples = [
        (100, 7),
        (1000, 31),
        (57, 8),
        (365, 12),
    ]

    for objects, containers in examples:
        guaranteed = minimum_guaranteed_collision(objects, containers)
        print(
            f"{objects} objects / {containers} containers -> "
            f"some container has at least {guaranteed}"
        )

    print(
        "\nFor 365 students distributed across 12 months, at least "
        f"{minimum_guaranteed_collision(365, 12)} students share a month."
    )


def demonstrate_threshold_form() -> None:
    banner("How Many Objects Guarantee a Target Occupancy?")

    cases = [
        (12, 2),
        (12, 3),
        (31, 4),
        (256, 5),
    ]

    for containers, target in cases:
        required = objects_needed_for_at_least(containers, target)
        print(
            f"{containers} containers, target occupancy {target}: "
            f"{required} objects guarantee the target."
        )


# ---------------------------------------------------------------------------
# Explicit distributions
# ---------------------------------------------------------------------------

def occupancy_table(assignments: Sequence[int], container_count: int) -> Counter:
    """Count how many objects occupy each container."""
    if container_count <= 0:
        raise ValueError("container_count must be positive")

    if any(value < 0 or value >= container_count for value in assignments):
        raise ValueError("assignment contains an invalid container index")

    counts = Counter(assignments)

    for container in range(container_count):
        counts.setdefault(container, 0)

    return counts


def demonstrate_explicit_distribution() -> None:
    banner("Checking an Explicit Distribution")

    assignments = [
        0, 2, 1, 3, 0, 2, 2, 1, 4, 3, 0, 2, 1, 2, 2
    ]

    counts = occupancy_table(assignments, 5)

    for container, count in sorted(counts.items()):
        print(f"Container {container}: {count} object(s)")

    maximum = max(counts.values())
    guaranteed = minimum_guaranteed_collision(len(assignments), 5)

    print(f"Actual maximum occupancy: {maximum}")
    print(f"Mathematically guaranteed minimum maximum: {guaranteed}")


# ---------------------------------------------------------------------------
# Computing application: hash collisions
# ---------------------------------------------------------------------------

def bucket_for_key(key: str, bucket_count: int) -> int:
    """
    Map an arbitrary key into one of bucket_count hash buckets.

    SHA-256 is used only to create a deterministic demonstration. The
    pigeonhole argument does not depend on the quality of the hash function.
    """
    if bucket_count <= 0:
        raise ValueError("bucket_count must be positive")

    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % bucket_count


def demonstrate_hash_buckets() -> None:
    banner("Computing Application: Hash Buckets")

    keys = [
        "alice@example.com",
        "bob@example.com",
        "carol@example.com",
        "dave@example.com",
        "eve@example.com",
        "frank@example.com",
        "grace@example.com",
        "heidi@example.com",
        "ivan@example.com",
        "judy@example.com",
    ]

    bucket_count = 4
    assignments = [
        bucket_for_key(key, bucket_count)
        for key in keys
    ]

    counts = occupancy_table(assignments, bucket_count)

    for key, bucket in zip(keys, assignments):
        print(f"{key:24} -> bucket {bucket}")

    print("\nBucket occupancy:")
    for bucket, count in sorted(counts.items()):
        print(f"bucket {bucket}: {count}")

    print(
        f"\nWith {len(keys)} keys and {bucket_count} buckets, "
        f"some bucket must contain at least "
        f"{minimum_guaranteed_collision(len(keys), bucket_count)} key(s)."
    )

    print(
        "The principle proves that collisions must eventually occur in any "
        "finite bucket space, regardless of how good the hash function is."
    )


# ---------------------------------------------------------------------------
# Computing application: finite identifiers
# ---------------------------------------------------------------------------

def demonstrate_identifier_space() -> None:
    banner("Computing Application: Finite Identifier Spaces")

    identifier_length = 3
    alphabet_size = 10
    identifier_space = alphabet_size ** identifier_length

    print(
        f"Three-digit decimal identifiers provide {identifier_space} "
        "possible values."
    )

    registrations = identifier_space + 1

    print(
        f"After {registrations} distinct registration requests, "
        "a duplicate identifier is unavoidable if identifiers are assigned "
        "only from this space."
    )

    required = objects_needed_for_at_least(
        identifier_space,
        2,
    )

    print(f"Generalized calculation gives: {required}")


# ---------------------------------------------------------------------------
# Computing application: birthdays
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Person:
    name: str
    birth_month: int


def find_shared_birth_month(
    people: Iterable[Person],
) -> dict[int, list[str]]:
    """
    Return only months containing more than one person.
    """
    groups: defaultdict[int, list[str]] = defaultdict(list)

    for person in people:
        if not 1 <= person.birth_month <= 12:
            raise ValueError(
                f"Invalid birth month for {person.name}: {person.birth_month}"
            )
        groups[person.birth_month].append(person.name)

    return {
        month: names
        for month, names in groups.items()
        if len(names) >= 2
    }


def demonstrate_birth_months() -> None:
    banner("Computing Application: Shared Birth Months")

    people = [
        Person("Asha", 3),
        Person("Rahul", 7),
        Person("Meera", 3),
        Person("Kabir", 11),
        Person("Neha", 7),
        Person("Vikram", 7),
        Person("Isha", 1),
        Person("Arjun", 12),
        Person("Riya", 5),
    ]

    shared = find_shared_birth_month(people)

    for month, names in sorted(shared.items()):
        print(f"Month {month}: {', '.join(names)}")


# ---------------------------------------------------------------------------
# Computing application: memory state spaces
# ---------------------------------------------------------------------------

def required_bits_for_states(state_count: int) -> int:
    """
    Return the number of bits needed to represent at least state_count
    distinct states.

    This is related to pigeonhole reasoning because b bits can represent
    exactly 2**b different bit patterns.
    """
    if state_count <= 0:
        raise ValueError("state_count must be positive")

    bits = 0
    states = 1

    while states < state_count:
        bits += 1
        states *= 2

    return bits


def demonstrate_bit_state_space() -> None:
    banner("Computing Application: Finite Bit Patterns")

    bit_width = 8
    possible_patterns = 2 ** bit_width

    print(f"{bit_width}-bit values: {possible_patterns} possible patterns")

    required_bits = required_bits_for_states(1000)

    print(
        f"At least {required_bits} bits are required to represent "
        "1000 distinct states."
    )

    print(
        "If a system needs more distinct states than its available bit "
        "patterns, two logical states must share a representation."
    )


# ---------------------------------------------------------------------------
# Computing application: modular arithmetic
# ---------------------------------------------------------------------------

def demonstrate_modular_collisions() -> None:
    banner("Computing Application: Modular Arithmetic")

    modulus = 7
    values = list(range(20))

    residues = [value % modulus for value in values]
    groups: defaultdict[int, list[int]] = defaultdict(list)

    for value, residue in zip(values, residues):
        groups[residue].append(value)

    for residue in sorted(groups):
        print(f"Residue {residue}: {groups[residue]}")

    guaranteed = minimum_guaranteed_collision(len(values), modulus)

    print(
        f"\nAmong {len(values)} integers and {modulus} possible residues, "
        f"some residue occurs at least {guaranteed} times."
    )


# ---------------------------------------------------------------------------
# Computing application: duplicate detection
# ---------------------------------------------------------------------------

def first_duplicate(values: Iterable[str]) -> tuple[str, int, int] | None:
    """
    Find the first repeated value and the two positions involved.

    A set provides average O(1) membership checks, giving O(n) expected
    time and O(n) additional space.
    """
    seen: dict[str, int] = {}

    for index, value in enumerate(values):
        if value in seen:
            return value, seen[value], index

        seen[value] = index

    return None


def demonstrate_duplicate_detection() -> None:
    banner("Computing Application: Duplicate Detection")

    identifiers = [
        "USR-1001",
        "USR-1002",
        "USR-1003",
        "USR-1004",
        "USR-1002",
        "USR-1005",
    ]

    result = first_duplicate(identifiers)

    if result is None:
        print("No duplicate identifier was found.")
    else:
        value, first_index, second_index = result
        print(
            f"Duplicate {value!r} occurred at positions "
            f"{first_index} and {second_index}."
        )


# ---------------------------------------------------------------------------
# A generalized occupancy engine
# ---------------------------------------------------------------------------

def guaranteed_overload(
    object_count: int,
    container_count: int,
) -> tuple[int, int]:
    """
    Return the guaranteed occupancy and the maximum occupancy possible
    without violating the guarantee.

    For n objects and k containers:

        maximum possible minimum occupancy = floor(n / k)
        guaranteed maximum occupancy = ceil(n / k)
    """
    if object_count < 0:
        raise ValueError("object_count cannot be negative")
    if container_count <= 0:
        raise ValueError("container_count must be positive")

    minimum_possible_maximum = ceil(object_count / container_count)
    average_floor = object_count // container_count

    return average_floor, minimum_possible_maximum


def demonstrate_bounds() -> None:
    banner("Lower Bounds from the Generalized Principle")

    cases = [
        (10, 3),
        (20, 6),
        (101, 10),
        (1001, 16),
    ]

    for objects, containers in cases:
        lower_average, guaranteed_maximum = guaranteed_overload(
            objects,
            containers,
        )

        print(
            f"{objects} objects across {containers} containers: "
            f"floor average={lower_average}, "
            f"guaranteed maximum occupancy={guaranteed_maximum}"
        )


# ---------------------------------------------------------------------------
# Adversarial simulation
# ---------------------------------------------------------------------------

def adversarial_distribution(
    object_count: int,
    container_count: int,
) -> list[int]:
    """
    Distribute objects as evenly as possible.

    This represents the adversarial strategy that tries to delay a large
    collision. Even this best-case balancing cannot beat the generalized
    pigeonhole lower bound.
    """
    if object_count < 0 or container_count <= 0:
        raise ValueError("invalid distribution parameters")

    counts = [0] * container_count

    for index in range(object_count):
        counts[index % container_count] += 1

    return counts


def demonstrate_adversarial_distribution() -> None:
    banner("Why the Bound Cannot Be Improved")

    objects = 23
    containers = 5

    counts = adversarial_distribution(objects, containers)

    print(f"Best balanced distribution of {objects} objects:")
    print(counts)

    print(
        f"Maximum occupancy is {max(counts)}, exactly matching the "
        f"guaranteed lower bound of "
        f"{minimum_guaranteed_collision(objects, containers)}."
    )


# ---------------------------------------------------------------------------
# Application: load balancing
# ---------------------------------------------------------------------------

def evaluate_server_loads(
    requests: Sequence[int],
    server_count: int,
) -> dict[str, float | int | list[int]]:
    """
    Model request assignment using round-robin distribution.

    The pigeonhole principle gives a deterministic lower bound on the
    largest server load when the request count exceeds the number of servers.
    """
    if server_count <= 0:
        raise ValueError("server_count must be positive")
    if any(request < 0 for request in requests):
        raise ValueError("request counts cannot be negative")

    loads = [0] * server_count

    for request_count in requests:
        for _ in range(request_count):
            target = min(range(server_count), key=loads.__getitem__)
            loads[target] += 1

    return {
        "total_requests": sum(requests),
        "server_count": server_count,
        "loads": loads,
        "largest_load": max(loads, default=0),
    }


def demonstrate_load_balancing() -> None:
    banner("Computing Application: Load Distribution")

    result = evaluate_server_loads([13, 8, 11, 6], 4)

    print(f"Total requests: {result['total_requests']}")
    print(f"Server loads: {result['loads']}")
    print(f"Largest load: {result['largest_load']}")

    guaranteed = minimum_guaranteed_collision(
        result["total_requests"],
        result["server_count"],
    )

    print(
        f"Pigeonhole lower bound on the largest load: {guaranteed}"
    )


# ---------------------------------------------------------------------------
# Application: cache key collision space
# ---------------------------------------------------------------------------

def simulate_truncated_hashes(
    keys: Sequence[str],
    bits: int,
) -> Counter[int]:
    """
    Simulate a deliberately small hash space.

    Truncating the hash to a small number of bits makes collisions easy to
    observe and illustrates why finite hash spaces cannot provide uniqueness.
    """
    if bits <= 0 or bits > 256:
        raise ValueError("bits must be between 1 and 256")

    bucket_count = 2 ** bits
    mask = bucket_count - 1
    counts: Counter[int] = Counter()

    for key in keys:
        digest = hashlib.sha256(key.encode("utf-8")).digest()
        integer = int.from_bytes(digest, "big")
        counts[integer & mask] += 1

    return counts


def demonstrate_truncated_hashes() -> None:
    banner("Computing Application: Truncated Hash Space")

    keys = [f"document-{index}" for index in range(100)]
    bits = 5

    counts = simulate_truncated_hashes(keys, bits)
    bucket_count = 2 ** bits

    collisions = {
        bucket: count
        for bucket, count in counts.items()
        if count > 1
    }

    print(f"Hash buckets: {bucket_count}")
    print(f"Keys: {len(keys)}")
    print(f"Buckets containing collisions: {len(collisions)}")

    print(
        f"Guaranteed occupancy somewhere: "
        f"{minimum_guaranteed_collision(len(keys), bucket_count)}"
    )

    for bucket, count in sorted(collisions.items()):
        print(f"bucket {bucket}: {count} keys")


# ---------------------------------------------------------------------------
# Application: finite categorical attributes
# ---------------------------------------------------------------------------

def categorical_signature(
    department: str,
    region: str,
    priority: str,
) -> tuple[str, str, str]:
    """
    Build a finite categorical signature.

    When the number of records exceeds the number of possible signatures,
    two records must have the same signature.
    """
    valid_departments = {"finance", "operations", "technology"}
    valid_regions = {"north", "south", "east", "west"}
    valid_priorities = {"low", "medium", "high"}

    if department not in valid_departments:
        raise ValueError("invalid department")
    if region not in valid_regions:
        raise ValueError("invalid region")
    if priority not in valid_priorities:
        raise ValueError("invalid priority")

    return department, region, priority


def demonstrate_categorical_signatures() -> None:
    banner("Computing Application: Finite Feature Signatures")

    departments = 3
    regions = 4
    priorities = 3
    signature_count = departments * regions * priorities

    record_count = signature_count + 1

    print(f"Possible signatures: {signature_count}")
    print(f"Records: {record_count}")
    print(
        "At least two records must share the complete "
        "(department, region, priority) signature."
    )

    sample = categorical_signature("technology", "north", "high")
    print(f"Example valid signature: {sample}")


# ---------------------------------------------------------------------------
# Random experiment: observation versus guarantee
# ---------------------------------------------------------------------------

def random_bucket_experiment(
    object_count: int,
    bucket_count: int,
    trials: int,
    seed: int = 42,
) -> tuple[int, float]:
    """
    Estimate how often a collision appears.

    The important distinction is that the pigeonhole principle gives a
    deterministic guarantee only once objects > buckets. Before that point,
    collisions may happen but are not forced.
    """
    if object_count < 0:
        raise ValueError("object_count cannot be negative")
    if bucket_count <= 0 or trials <= 0:
        raise ValueError("bucket_count and trials must be positive")

    generator = random.Random(seed)
    collision_trials = 0

    for _ in range(trials):
        buckets = [
            generator.randrange(bucket_count)
            for _ in range(object_count)
        ]

        if len(set(buckets)) < object_count:
            collision_trials += 1

    probability = collision_trials / trials
    return collision_trials, probability


def demonstrate_guarantee_vs_probability() -> None:
    banner("Guarantee Versus Probability")

    cases = [
        (10, 365),
        (23, 365),
        (366, 365),
    ]

    for people, days in cases:
        trials = 5000
        collisions, probability = random_bucket_experiment(
            people,
            days,
            trials,
        )

        print(
            f"{people} objects / {days} buckets -> "
            f"observed collision frequency {probability:.3f} "
            f"over {trials} trials"
        )

    print(
        "\nThe 366-object case is deterministic: a collision must occur "
        "because 366 > 365. The smaller cases are probabilistic."
    )


# ---------------------------------------------------------------------------
# Pigeonhole reasoning as a reusable verification function
# ---------------------------------------------------------------------------

def verify_claim(
    objects: int,
    containers: int,
    claimed_guarantee: int,
) -> bool:
    """
    Verify whether a claimed lower bound follows from the generalized
    pigeonhole principle.
    """
    actual = minimum_guaranteed_collision(objects, containers)
    return claimed_guarantee <= actual


def demonstrate_claim_verification() -> None:
    banner("Verifying Pigeonhole Claims")

    claims = [
        (101, 10, 10),
        (101, 10, 11),
        (100, 10, 11),
        (1000, 32, 32),
        (1000, 32, 31),
    ]

    for objects, containers, claim in claims:
        valid = verify_claim(objects, containers, claim)
        guaranteed = minimum_guaranteed_collision(objects, containers)

        print(
            f"{objects} objects, {containers} containers: "
            f"guaranteed={guaranteed}, claimed={claim}, valid={valid}"
        )


# ---------------------------------------------------------------------------
# Edge cases and failure handling
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    banner("Edge Cases and Validation")

    valid_cases = [
        (0, 5),
        (1, 1),
        (5, 5),
        (6, 5),
    ]

    for objects, containers in valid_cases:
        print(
            f"{objects} objects / {containers} containers -> "
            f"{minimum_guaranteed_collision(objects, containers)}"
        )

    invalid_cases = [
        (-1, 5),
        (10, 0),
        (10, -2),
    ]

    for objects, containers in invalid_cases:
        try:
            minimum_guaranteed_collision(objects, containers)
        except ValueError as exc:
            print(
                f"Rejected ({objects}, {containers}): {exc}"
            )


# ---------------------------------------------------------------------------
# Complexity analysis encoded as executable metadata
# ---------------------------------------------------------------------------

def complexity_reference() -> dict[str, str]:
    return {
        "direct_pigeonhole_calculation": "O(1) time, O(1) space",
        "explicit_bucket_counting": "O(n) time, O(k) space",
        "duplicate_detection_with_set": "O(n) expected time, O(n) space",
        "balanced_distribution": "O(n) time, O(k) space",
        "categorical_signature_space": "O(1) time when category sizes are known",
    }


def demonstrate_complexity() -> None:
    banner("Computational Complexity")

    for operation, complexity in complexity_reference().items():
        print(f"{operation}: {complexity}")


# ---------------------------------------------------------------------------
# Integrated case study
# ---------------------------------------------------------------------------

def run_repository_cache_case_study() -> None:
    """
    A computing-oriented case study.

    A service stores objects using a finite cache partition. The service may
    use hashing to choose a partition. The pigeonhole principle establishes
    a hard occupancy guarantee before any actual hashing takes place.
    """
    banner("Integrated Case Study: Distributed Cache Partitions")

    object_count = 10_000
    partition_count = 64

    guaranteed = minimum_guaranteed_collision(
        object_count,
        partition_count,
    )

    print(f"Objects: {object_count}")
    print(f"Cache partitions: {partition_count}")
    print(
        f"At least one partition must contain {guaranteed} objects "
        "under any assignment."
    )

    threshold = objects_needed_for_at_least(
        partition_count,
        200,
    )

    print(
        f"Objects required to guarantee a partition with at least "
        f"200 objects: {threshold}"
    )

    print(
        "Engineering implication: increasing the number of partitions "
        "changes the deterministic occupancy bound, but does not eliminate "
        "collisions while the identifier space remains finite."
    )


def main() -> None:
    demonstrate_basic_form()
    demonstrate_generalized_form()
    demonstrate_threshold_form()
    demonstrate_explicit_distribution()
    demonstrate_hash_buckets()
    demonstrate_identifier_space()
    demonstrate_birth_months()
    demonstrate_bit_state_space()
    demonstrate_modular_collisions()
    demonstrate_duplicate_detection()
    demonstrate_bounds()
    demonstrate_adversarial_distribution()
    demonstrate_load_balancing()
    demonstrate_truncated_hashes()
    demonstrate_categorical_signatures()
    demonstrate_guarantee_vs_probability()
    demonstrate_claim_verification()
    demonstrate_edge_cases()
    demonstrate_complexity()
    run_repository_cache_case_study()


if __name__ == "__main__":
    main()
