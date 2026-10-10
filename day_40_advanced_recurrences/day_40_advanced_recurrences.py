#!/usr/bin/env python3
"""Advanced recurrence analysis, recursion trees, and the Master Theorem.

Run with:
    python advanced_recurrences.py

The program uses exact integer arithmetic for recurrence costs and
Fractions for logarithmic exponents where possible. It distinguishes
recurrence models from asymptotic bounds and validates the assumptions
required by each analytical method.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from math import ceil, floor, isclose, log2, log
from typing import Callable, Iterable


@dataclass(frozen=True)
class Recurrence:
    """Represent T(n) = a*T(n/b) + f(n), with a regular subproblem size."""

    name: str
    a: int
    b: int
    combine_cost: Callable[[int], int]
    base_cost: int = 1
    description: str = ""

    def __post_init__(self) -> None:
        if self.a < 1:
            raise ValueError("The number of recursive calls must be positive.")
        if self.b <= 1:
            raise ValueError("The shrink factor must be greater than one.")
        if self.base_cost < 0:
            raise ValueError("Base cost cannot be negative.")

    def validate_size(self, n: int) -> None:
        if n < 1:
            raise ValueError("Problem size must be positive.")

    def cost(self, n: int) -> int:
        """Evaluate an integer recurrence with ceiling-sized subproblems.

        This is an executable cost model, not an assertion that all
        asymptotic recurrences use exactly this rounding convention.
        """
        self.validate_size(n)

        @lru_cache(maxsize=None)
        def evaluate(size: int) -> int:
            if size <= 1:
                return self.base_cost
            child_size = ceil(size / self.b)
            return (
                self.a * evaluate(child_size)
                + self.combine_cost(size)
            )

        return evaluate(n)

    def tree_levels(self, n: int) -> list[dict[str, int]]:
        """Build an aggregate recursion-tree model for power-of-b sizes."""
        self.validate_size(n)
        levels: list[dict[str, int]] = []
        nodes = 1
        size = n
        depth = 0

        while size > 1:
            levels.append(
                {
                    "depth": depth,
                    "nodes": nodes,
                    "subproblem_size": size,
                    "level_combine_cost": nodes * self.combine_cost(size),
                }
            )
            nodes *= self.a
            size = max(1, size // self.b)
            depth += 1

        levels.append(
            {
                "depth": depth,
                "nodes": nodes,
                "subproblem_size": 1,
                "level_combine_cost": nodes * self.base_cost,
            }
        )
        return levels


def polynomial_cost(power: int, coefficient: int = 1) -> Callable[[int], int]:
    """Return f(n) = coefficient*n**power."""
    if power < 0:
        raise ValueError("This demonstration expects a nonnegative power.")
    if coefficient < 0:
        raise ValueError("Combine cost must be nonnegative.")
    return lambda n: coefficient * n**power


def logarithmic_cost(coefficient: int = 1) -> Callable[[int], int]:
    """Return an integer approximation of coefficient*log2(n)."""
    if coefficient < 0:
        raise ValueError("Combine cost must be nonnegative.")
    return lambda n: coefficient * max(1, n.bit_length() - 1)


def master_theorem(a: int, b: int, polynomial_power: float) -> str:
    """Classify T(n)=a*T(n/b)+Theta(n**power) under Master Theorem.

    This handles the basic polynomial f(n) cases, not logarithmic
    factors or arbitrary oscillating functions.
    """
    if a < 1 or b <= 1:
        raise ValueError("Require a >= 1 and b > 1.")
    if polynomial_power < 0:
        raise ValueError("Polynomial power must be nonnegative.")

    critical_power = log(a, b)
    tolerance = 1e-10

    if polynomial_power < critical_power - tolerance:
        return (
            f"Case 1: Theta(n^{critical_power:.6g}); "
            "recursive leaves dominate."
        )

    if isclose(
        polynomial_power,
        critical_power,
        rel_tol=tolerance,
        abs_tol=tolerance,
    ):
        return (
            f"Case 2: Theta(n^{critical_power:.6g} log n); "
            "each level contributes the same asymptotic order."
        )

    return (
        f"Case 3 candidate: Theta(n^{polynomial_power:.6g}); "
        "the nonrecursive work dominates if the regularity condition holds."
    )


def extended_master_theorem(
    a: int,
    b: int,
    polynomial_power: float,
    log_power: float,
) -> str:
    """Classify f(n)=Theta(n^p log^k n) in standard extended cases.

    For the critical exponent p=log_b(a), the logarithmic multiplier
    adds one power of log n. For
