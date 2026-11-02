from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json
import math
import tempfile


class PullRequestState(Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"


class ReviewState(Enum):
    COMMENTED = "commented"
    CHANGES_REQUESTED = "changes_requested"
    APPROVED = "approved"
    DISMISSED = "dismissed"


class CheckState(Enum):
    PASS = "pass"
    FAIL = "fail"
    PENDING = "pending"


class MergeStrategy(Enum):
    MERGE_COMMIT = "merge_commit"
    SQUASH = "squash"
    REBASE = "rebase"


@dataclass(frozen=True)
class Commit:
    sha: str
    message: str


@dataclass
class Review:
    reviewer: str
    state: ReviewState
    commit_sha: str
    comments: int = 0
    resolved_comments: int = 0

    @property
    def unresolved_comments(self) -> int:
        return max(0, self.comments - self.resolved_comments)


@dataclass
class StatusCheck:
    name: str
    state: CheckState


@dataclass
class BranchProtection:
    required_approvals: int = 2
    required_checks: Set[str] = field(default_factory=set)
    require_conversation_resolution: bool = True
    require_linear_history: bool = False
    allow_force_push: bool = False
    allow_direct_push: bool = False


@dataclass
class Branch:
    name: str
    protected: bool = False
    protection: BranchProtection | None = None


@dataclass
class PullRequest:
    number: int
    source: str
    target: str
    state: PullRequestState
    commits: List[Commit]
    reviews: List[Review]
    checks: List[StatusCheck]
    conversations_open: int = 0
    merge_strategy: MergeStrategy = MergeStrategy.SQUASH
    base_sha: str = ""

    @property
    def head_sha(self) -> str:
        if not self.commits:
            raise ValueError("A pull request must contain at least one commit.")
        return self.commits[-1].sha


@dataclass
class BayesEvidence:
    name: str
    likelihood_if_merge_safe: float
    likelihood_if_merge_unsafe: float

    def validate(self) -> None:
        if not 0 < self.likelihood_if_merge_safe <= 1:
            raise ValueError(f"Invalid safe likelihood for {self.name}")
        if not 0 < self.likelihood_if_merge_unsafe <= 1:
            raise ValueError(f"Invalid unsafe likelihood for {self.name}")


class BayesianRiskEngine:
    """
    P(Safe | evidence) =
        P(evidence | Safe) P(Safe)
        ----------------------------------------------
        P(evidence | Safe)P(Safe) +
        P(evidence | Unsafe)P(Unsafe)

    The evidence factors are treated as conditionally independent for this
    educational model. Production systems should calibrate these probabilities
    from historical repository outcomes rather than using arbitrary values.
    """

    def __init__(self, prior_safe: float = 0.85):
        if not 0 < prior_safe < 1:
            raise ValueError("The prior must be strictly between zero and one.")
        self.prior_safe = prior_safe

    def posterior(self, evidence: List[BayesEvidence]) -> float:
        safe = self.prior_safe
        unsafe = 1.0 - self.prior_safe

        for item in evidence:
            item.validate()
            safe *= item.likelihood_if_merge_safe
            unsafe *= item.likelihood_if_merge_unsafe

        denominator = safe + unsafe
        return safe / denominator if denominator else 0.0

    def posterior_odds(self, evidence: List[BayesEvidence]) -> float:
        probability = self.posterior(evidence)
        return probability / (1.0 - probability)


class RepositoryGovernance:
    def __init__(self, branches: Dict[str, Branch], bayes: BayesianRiskEngine):
        self.branches = branches
        self.bayes = bayes

    @staticmethod
    def _evidence(pr: PullRequest, branch: Branch) -> List[BayesEvidence]:
        approvals = {
            review.reviewer
            for review in pr.reviews
            if review.state == ReviewState.APPROVED
            and review.commit_sha == pr.head_sha
        }

        failed_checks = {
            check.name for check in pr.checks if check.state == CheckState.FAIL
        }
        pending_checks = {
            check.name for check in pr.checks if check.state == CheckState.PENDING
        }

        evidence: List[BayesEvidence] = []

        evidence.append(
            BayesEvidence(
                "current-head-approval",
                0.92 if approvals else 0.20,
                0.08 if approvals else 0.80,
            )
        )

        if branch.protection and branch.protection.required_checks:
            all_passed = all(
                any(c.name == required and c.state == CheckState.PASS for c in pr.checks)
                for required in branch.protection.required_checks
            )
            evidence.append(
                BayesEvidence(
                    "required-status-checks",
                    0.97 if all_passed else 0.15,
                    0.03 if all_passed else 0.85,
                )
            )

        evidence.append(
            BayesEvidence(
                "failed-checks",
                0.98 if not failed_checks else 0.05,
                0.02 if not failed_checks else 0.95,
            )
        )

        evidence.append(
            BayesEvidence(
                "pending-checks",
                0.94 if not pending_checks else 0.35,
                0.06 if not pending_checks else 0.65,
            )
        )

        evidence.append(
            BayesEvidence(
                "resolved-conversations",
                0.96 if pr.conversations_open == 0 else 0.30,
                0.04 if pr.conversations_open == 0 else 0.70,
            )
        )

        changes_requested = any(
            r.state == ReviewState.CHANGES_REQUESTED and r.commit_sha == pr.head_sha
            for r in pr.reviews
        )
        evidence.append(
            BayesEvidence(
                "requested-changes",
                0.95 if not changes_requested else 0.10,
                0.05 if not changes_requested else 0.90,
            )
        )

        return evidence

    def evaluate(self, pr: PullRequest) -> Tuple[bool, float, List[str]]:
        reasons: List[str] = []

        if pr.state != PullRequestState.OPEN:
            reasons.append("Pull Request is not open.")
            return False, 0.0, reasons

        if pr.source == pr.target:
            reasons.append("Source and target branches must differ.")
            return False, 0.0, reasons

        if pr.number <= 0:
            reasons.append("Pull Request number must be positive.")
            return False, 0.0, reasons

        branch = self.branches.get(pr.target)
        if branch is None:
            reasons.append("Target branch does not exist.")
            return False, 0.0, reasons

        if not pr.commits:
            reasons.append("Pull Request has no commits.")
            return False, 0.0, reasons

        if branch.protected and branch.protection:
            protection = branch.protection

            if not protection.allow_direct_push and pr.source == branch.name:
                reasons.append("Direct pushes to the protected branch are prohibited.")

            approvals = {
                r.reviewer
                for r in pr.reviews
                if r.state == ReviewState.APPROVED
                and r.commit_sha == pr.head_sha
            }

            if len(approvals) < protection.required_approvals:
                reasons.append(
                    f"Requires {protection.required_approvals} current-head approval(s); "
                    f"found {len(approvals)}."
                )

            for required in protection.required_checks:
                matching = [c for c in pr.checks if c.name == required]
                if not matching or matching[-1].state != CheckState.PASS:
                    reasons.append(f"Required check '{required}' has not passed.")

            if protection.require_conversation_resolution and pr.conversations_open:
                reasons.append("All review conversations must be resolved.")

            if protection.require_linear_history and pr.merge_strategy == MergeStrategy.MERGE_COMMIT:
                reasons.append("Merge commits are prohibited by linear-history policy.")

        posterior = self.bayes.posterior(self._evidence(pr, branch))
        threshold = 0.90

        if posterior < threshold:
            reasons.append(
                f"Bayesian merge-safety posterior {posterior:.4f} is below {threshold:.2f}."
            )

        eligible = not reasons
        return eligible, posterior, reasons


def demonstrate_bayes() -> None:
    prior = 0.20
    likelihood_safe = 0.90
    likelihood_unsafe = 0.30

    numerator = likelihood_safe * prior
    denominator = numerator + likelihood_unsafe * (1 - prior)
    posterior = numerator / denominator

    print("Bayes theorem example")
    print(f"Prior probability:       {prior:.4f}")
    print(f"Safe likelihood:         {likelihood_safe:.4f}")
    print(f"Unsafe likelihood:       {likelihood_unsafe:.4f}")
    print(f"Posterior probability:   {posterior:.4f}")
    print()


def build_repository_scenario() -> Tuple[RepositoryGovernance, PullRequest]:
    protection = BranchProtection(
        required_approvals=2,
        required_checks={"unit-tests", "security-scan"},
        require_conversation_resolution=True,
        require_linear_history=True,
        allow_force_push=False,
        allow_direct_push=False,
    )

    branches = {
        "main": Branch("main", protected=True, protection=protection),
        "feature/payment-validation": Branch("feature/payment-validation"),
    }

    pr = PullRequest(
        number=42,
        source="feature/payment-validation",
        target="main",
        state=PullRequestState.OPEN,
        commits=[
            Commit("a100", "Add payment validation"),
            Commit("a101", "Fix boundary validation"),
        ],
        reviews=[
            Review("reviewer-alice", ReviewState.APPROVED, "a101"),
            Review("reviewer-bob", ReviewState.APPROVED, "a101"),
            Review("reviewer-carol", ReviewState.COMMENTED, "a101", comments=2, resolved_comments=2),
        ],
        checks=[
            StatusCheck("unit-tests", CheckState.PASS),
            StatusCheck("security-scan", CheckState.PASS),
            StatusCheck("integration-tests", CheckState.PASS),
        ],
        conversations_open=0,
        merge_strategy=MergeStrategy.SQUASH,
        base_sha="m500",
    )

    return RepositoryGovernance(branches, BayesianRiskEngine(0.85)), pr


def test_edge_cases() -> None:
    engine = BayesianRiskEngine(0.5)

    evidence = [
        BayesEvidence("positive", 0.8, 0.2),
        BayesEvidence("negative", 0.3, 0.7),
    ]
    posterior = engine.posterior(evidence)
    assert 0 < posterior < 1

    try:
        BayesianRiskEngine(1.0)
        raise AssertionError("Invalid prior was accepted.")
    except ValueError:
        pass

    try:
        engine.posterior([BayesEvidence("bad", 1.2, 0.2)])
        raise AssertionError("Invalid likelihood was accepted.")
    except ValueError:
        pass


def save_audit_record(path: Path, pr: PullRequest, eligible: bool, posterior: float, reasons: List[str]) -> None:
    record = {
        "pull_request": pr.number,
        "source": pr.source,
        "target": pr.target,
        "head_commit": pr.head_sha,
        "eligible": eligible,
        "posterior_merge_safety": round(posterior, 6),
        "reasons": reasons,
    }

    # The file contains only derived governance data, avoiding credentials,
    # tokens, or source-code contents.
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")


def main() -> None:
    demonstrate_bayes()

    governance, pr = build_repository_scenario()
    eligible, posterior, reasons = governance.evaluate(pr)

    print(f"Pull Request #{pr.number}")
    print(f"Head commit:             {pr.head_sha}")
    print(f"Merge-safety posterior:  {posterior:.4f}")
    print(f"Merge eligible:          {eligible}")

    if reasons:
        print("Blocking conditions:")
        for reason in reasons:
            print(f"  - {reason}")
    else:
        print("All repository governance conditions are satisfied.")

    test_edge_cases()

    with tempfile.TemporaryDirectory() as directory:
        audit_path = Path(directory) / "merge_audit.json"
        save_audit_record(audit_path, pr, eligible, posterior, reasons)
        assert json.loads(audit_path.read_text(encoding="utf-8"))["pull_request"] == 42

    print("Validation tests: passed")


if __name__ == "__main__":
    main()
