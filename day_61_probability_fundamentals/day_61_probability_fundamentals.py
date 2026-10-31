from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import comb
from random import Random
from typing import Callable, Iterable, Sequence


class ProbabilityError(ValueError):
    """Raised when a probability model violates its mathematical rules."""


@dataclass(frozen=True)
class SampleSpace:
    outcomes: frozenset
    probabilities: dict[object, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.outcomes:
            raise ProbabilityError("A sample space must contain at least one outcome.")

        if set(self.probabilities) != set(self.outcomes):
            raise ProbabilityError(
                "A probability must be supplied for every outcome, and only valid outcomes."
            )

        if any(p < 0 or p > 1 for p in self.probabilities.values()):
            raise ProbabilityError("Every outcome probability must be between 0 and 1.")

        total = sum(self.probabilities.values())
        if abs(total - 1.0) > 1e-12:
            raise ProbabilityError(
                f"Outcome probabilities must sum to 1. Current total: {total}"
            )

    def probability(self, event: Iterable) -> float:
        event_set = set(event)
        if not event_set.issubset(self.outcomes):
            invalid = event_set - self.outcomes
            raise ProbabilityError(f"Event contains invalid outcomes: {invalid}")
        return sum(self.probabilities[x] for x in event_set)


@dataclass(frozen=True)
class Event:
    name: str
    outcomes: frozenset

    def contains(self, outcome: object) -> bool:
        return outcome in self.outcomes


class Coin:
    def __init__(self, p_heads: float = 0.5) -> None:
        if not 0 <= p_heads <= 1:
            raise ProbabilityError("p_heads must be between 0 and 1.")
        self.p_heads = p_heads

    def flip(self, rng: Random) -> str:
        return "H" if rng.random() < self.p_heads else "T"


class Die:
    def __init__(self, sides: int = 6) -> None:
        if sides < 2:
            raise ProbabilityError("A die needs at least two sides.")
        self.sides = sides

    def roll(self, rng: Random) -> int:
        return rng.randint(1, self.sides)


def make_fair_die_space(sides: int = 6) -> SampleSpace:
    if sides < 2:
        raise ProbabilityError("A die needs at least two sides.")
    outcomes = frozenset(range(1, sides + 1))
    p = 1.0 / sides
    return SampleSpace(outcomes, {x: p for x in outcomes})


def complement(space: SampleSpace, event: Event) -> Event:
    return Event(f"not({event.name})", frozenset(space.outcomes - event.outcomes))


def union(space: SampleSpace, a: Event, b: Event) -> Event:
    if not a.outcomes.issubset(space.outcomes) or not b.outcomes.issubset(space.outcomes):
        raise ProbabilityError("Both events must belong to the sample space.")
    return Event(f"{a.name} union {b.name}", a.outcomes | b.outcomes)


def intersection(space: SampleSpace, a: Event, b: Event) -> Event:
    if not a.outcomes.issubset(space.outcomes) or not b.outcomes.issubset(space.outcomes):
        raise ProbabilityError("Both events must belong to the sample space.")
    return Event(f"{a.name} intersection {b.name}", a.outcomes & b.outcomes)


def conditional_probability(
    space: SampleSpace,
    event: Event,
    condition: Event,
) -> float:
    denominator = space.probability(condition.outcomes)
    if denominator == 0:
        raise ProbabilityError("Conditional probability is undefined for a zero-probability condition.")

    numerator = space.probability(intersection(space, event, condition).outcomes)
    return numerator / denominator


def estimate_probability(
    experiment: Callable[[Random], object],
    event_test: Callable[[object], bool],
    trials: int,
    seed: int = 42,
) -> float:
    if trials <= 0:
        raise ValueError("trials must be positive.")

    rng = Random(seed)
    successes = sum(event_test(experiment(rng)) for _ in range(trials))
    return successes / trials


def binomial_probability(n: int, k: int, p: float) -> float:
    if n < 0 or not 0 <= k <= n:
        raise ValueError("Require n >= 0 and 0 <= k <= n.")
    if not 0 <= p <= 1:
        raise ProbabilityError("p must be between 0 and 1.")
    return comb(n, k) * p**k * (1 - p) ** (n - k)


def run_assertions() -> None:
    # Axiom checks for a fair six-sided die.
    space = make_fair_die_space()
    sure = Event("sure", frozenset(range(1, 7)))
    impossible = Event("impossible", frozenset())
    even = Event("even", frozenset({2, 4, 6}))
    greater_than_four = Event("greater_than_four", frozenset({5, 6}))

    assert abs(space.probability(sure.outcomes) - 1.0) < 1e-12
    assert abs(space.probability(impossible.outcomes)) < 1e-12
    assert abs(space.probability(even.outcomes) - 0.5) < 1e-12
    assert abs(space.probability(greater_than_four.outcomes) - 1 / 3) < 1e-12

    not_even = complement(space, even)
    assert abs(space.probability(not_even.outcomes) - 0.5) < 1e-12

    both = intersection(space, even, greater_than_four)
    either = union(space, even, greater_than_four)

    assert both.outcomes == frozenset({6})
    assert either.outcomes == frozenset({2, 4, 5, 6})

    p_b_given_a = conditional_probability(space, greater_than_four, even)
    assert abs(p_b_given_a - 1 / 3) < 1e-12

    # Addition rule: P(A U B) = P(A) + P(B) - P(A intersection B).
    lhs = space.probability(either.outcomes)
    rhs = (
        space.probability(even.outcomes)
        + space.probability(greater_than_four.outcomes)
        - space.probability(both.outcomes)
    )
    assert abs(lhs - rhs) < 1e-12

    # A deliberately invalid model must fail validation.
    try:
        SampleSpace(
            frozenset({"A", "B"}),
            {"A": 0.7, "B": 0.7},
        )
    except ProbabilityError:
        pass
    else:
        raise AssertionError("Invalid probability distribution was accepted.")


def main() -> None:
    run_assertions()

    print("=== Probability Fundamentals ===")
    print("Sample space: fair six-sided die")

    space = make_fair_die_space()
    events = {
        "even": Event("even", frozenset({2, 4, 6})),
        "prime": Event("prime", frozenset({2, 3, 5})),
        "greater_than_3": Event("greater_than_3", frozenset({4, 5, 6})),
    }

    for name, event in events.items():
        print(f"P({name}) = {space.probability(event.outcomes):.4f}")

    even = events["even"]
    prime = events["prime"]

    print(
        "P(even and prime) = "
        f"{space.probability(intersection(space, even, prime).outcomes):.4f}"
    )
    print(
        "P(even or prime) = "
        f"{space.probability(union(space, even, prime).outcomes):.4f}"
    )
    print(
        "P(prime | even) = "
        f"{conditional_probability(space, prime, even):.4f}"
    )

    coin = Coin(0.6)
    estimated_heads = estimate_probability(
        coin.flip,
        lambda result: result == "H",
        trials=100_000,
        seed=2026,
    )
    print(f"\nEstimated P(heads) for biased coin = {estimated_heads:.4f}")
    print("Theoretical P(heads) = 0.6000")

    die = Die()
    estimated_six = estimate_probability(
        die.roll,
        lambda result: result == 6,
        trials=100_000,
        seed=2026,
    )
    print(f"\nEstimated P(rolling 6) = {estimated_six:.4f}")
    print("Theoretical P(rolling 6) = 0.1667")

    print("\nBinomial experiment: exactly 3 heads in 5 fair coin flips")
    theoretical = binomial_probability(5, 3, 0.5)
    print(f"Theoretical probability = {theoretical:.4f}")

    estimated = estimate_probability(
        lambda rng: sum(Coin(0.5).flip(rng) == "H" for _ in range(5)),
        lambda count: count == 3,
        trials=100_000,
        seed=2026,
    )
    print(f"Simulation estimate      = {estimated:.4f}")

    print("\nValidation and edge-case checks passed.")


if __name__ == "__main__":
    main()
