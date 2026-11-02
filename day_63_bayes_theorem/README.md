# Bayesian Repository Governance

## Scope

This project models Bayes' theorem through a repository-governance workflow involving Pull Requests, code review, approvals, status checks, protected branches, and merge eligibility.

The central probability model is:

`P(Safe | E) = P(E | Safe)P(Safe) / [P(E | Safe)P(Safe) + P(E | Unsafe)P(Unsafe)]`

where:

- `P(Safe)` is the prior probability that a proposed merge is safe.
- `P(E | Safe)` is the likelihood of observing the available evidence when the merge is safe.
- `P(E | Unsafe)` is the likelihood of observing that evidence when the merge is unsafe.
- `P(Safe | E)` is the posterior probability after observing the evidence.

The repository workflow keeps four concepts separate:

| Area | Meaning in the model |
|---|---|
| Pull Request | Workflow object that proposes a set of changes from a source branch into a target branch |
| Code Review | Evaluation of the proposed changes through reviews, comments, discussions, and requested changes |
| Approvals | Explicit review decisions that satisfy or fail a required approval policy |
| Branch Protection | Repository-level enforcement applied to the target branch before merging |

The relationship is therefore:

`Repository → Branches → Commits → Pull Request → Reviews → Comments/Conversations → Status Checks → Branch Protection → Bayesian Evaluation → Merge Eligibility`

Bayes' theorem does not replace these controls. It provides a probabilistic evidence layer that evaluates the combined state.

## Bayesian Model

The implementations use multiple evidence observations.

| Evidence | Safe likelihood | Unsafe likelihood | Interpretation |
|---|---:|---:|---|
| Current-head approvals | 0.92 | 0.08 | Required reviewers approved the exact current commit |
| Required status checks | 0.97 | 0.03 | Required automated checks passed |
| No failed checks | 0.98 | 0.02 | No known automated failure is present |
| No pending checks | 0.94 | 0.06 | The automated evaluation is complete |
| Resolved conversations | 0.96 | 0.04 | Review discussions have been resolved |
| No requested changes | 0.95 | 0.05 | Current review state contains no active change request |

The likelihoods are deliberately explicit rather than hidden inside a single score. This makes the Bayesian calculation auditable.

The model treats evidence factors as conditionally independent. That is a simplifying assumption for this learning implementation. Real governance systems should estimate likelihoods from historical repository outcomes and should account for correlations between evidence sources.

### Prior Probability

The source implementations use a prior safe probability of `0.85` for the repository governance scenario.

A separate basic example uses:

- prior safe probability: `0.20`
- safe likelihood: `0.90`
- unsafe likelihood: `0.30`

The resulting posterior is approximately `0.4286`.

The example illustrates that strong evidence does not automatically imply a high posterior when the prior is low.

## Pull Request Lifecycle

A Pull Request represents a proposed change between two different branches.

The model distinguishes:

- source branch
- target branch
- commit sequence
- current head commit
- base commit
- Pull Request state
- merge strategy
- review state
- status-check state
- unresolved conversations

A typical lifecycle is:

`Draft → Open → Review → Checks → Eligibility Evaluation → Merged`

A Pull Request can also move from an open state to closed without being merged. Reopening is represented by returning to the open workflow state while retaining the relevant branch and commit history.

A new commit changes the effective review evidence. Approvals associated with an older commit do not automatically count as approvals for the new head.

This is important because the object being approved is not merely the branch name. The review decision is associated with a particular changeset.

## Source and Target Branches

The source branch contains the proposed changes.

The target branch receives those changes if the Pull Request is merged.

The implementations reject a Pull Request where source and target branches are identical.

The protected target branch determines which repository-level rules apply.

For example:

`feature/payment-validation → main`

The feature branch is the proposed-change side of the workflow. `main` is the governed integration target.

## Changesets and Commits

Commits form the concrete changeset behind a Pull Request.

The current head commit is especially important for approval semantics.

Suppose two reviewers approve commit `a101`. If a developer later adds commit `a102`, the earlier approvals are associated with `a101`, not `a102`.

The model therefore evaluates:

`review.commit_sha == pull_request.head_sha`

This prevents an approval from being treated as current after the reviewed code has changed.

## Draft Pull Requests

A draft Pull Request represents work that is visible for collaboration but is not yet treated as a normal merge candidate.

The state model includes `draft`, `open`, `closed`, and `merged`.

The merge-eligibility services require the state to be `open`.

This prevents a draft or closed Pull Request from becoming eligible solely because its probability calculation happens to be favorable.

## Base-Branch Synchronization

The Pull Request records a base commit and a head commit.

When the target branch changes, the practical governance question is whether the Pull Request still represents a valid changeset against the current target state.

The model keeps the base and head identities explicit so synchronization can be evaluated independently from reviewer decisions.

A synchronization operation can change the effective changeset and therefore may require fresh review or status validation according to repository policy.

## Merge Strategies

Three strategies are represented:

- merge commit
- squash
- rebase

Branch protection can require linear history.

When linear history is required, the C++, Java, Python, JavaScript, and SQL models reject `merge_commit` for the protected target.

The choice is therefore a branch-governance rule, not a Bayesian likelihood.

## Code Review

Code review evaluates the proposed changes.

The model distinguishes review states:

- `commented`
- `changes_requested`
- `approved`
- `dismissed`

Review comments are separate from review decisions.

A comment can be resolved without being an approval. A reviewer can therefore participate in the discussion without satisfying the approval requirement.

The review workflow is:

`Review → Inline Discussion → Requested Changes or Approval → Conversation Resolution`

The Bayesian evidence model uses the resulting review state as evidence rather than treating every comment as an approval.

## Review Discussions

Open conversations represent review matters that have not been resolved.

A protected branch can require all conversations to be resolved before merging.

The model checks:

`open_conversations == 0`

A Pull Request with two valid approvals can still be blocked if a required conversation remains open.

This separates review quality from approval count.

## Requested Changes

A `changes_requested` review is different from an approval.

The implementations associate requested changes with the current head commit.

If a reviewer requests changes against the current head, the evidence model assigns a much lower safe likelihood to the absence of remediation.

A later commit can address the request. The review state and the new commit can then be evaluated again.

## Approvals

An approval is a specific review decision.

The repository policy specifies a required number of approvals.

For the main branch scenario:

`required approvals = 2`

The implementations count distinct reviewers whose approval references the current Pull Request head.

This avoids counting duplicate submissions by the same reviewer as multiple independent approvals.

Approval eligibility is therefore based on:

`distinct eligible reviewers × approved state × current head commit`

## Stale Approvals

A stale approval is an approval associated with a previous Pull Request head.

Example:

`a101 → approved by Alice and Bob`

Then:

`a102 → new commit`

The previous approvals do not satisfy a current-head approval requirement because they reference `a101`.

This behavior is demonstrated explicitly in the C++ and Java implementations and in the PostgreSQL transactional scenario.

The distinction is important for Bayesian reasoning because the evidence must correspond to the actual state being evaluated.

## Dismissed Approvals

A dismissed review is not counted as an approval.

The review-state enumeration explicitly separates `approved` from `dismissed`.

A repository can dismiss a review when the reviewed state is no longer considered valid. The subsequent eligibility calculation then uses the remaining current evidence.

## Reviewer Eligibility

The repository database stores members and roles.

The governance model treats reviewers as named participants rather than anonymous approval counters.

The PostgreSQL schema separates:

- repository membership
- reviewer identity
- review decision
- review commit
- branch protection

This structure permits eligibility rules to be expanded without mixing identity with probability calculations.

## Branch Protection

Branch protection is repository-level enforcement.

The protected `main` branch in the examples requires:

- two current-head approvals
- passing `unit-tests`
- passing `security-scan`
- resolved review conversations
- linear history
- no force push

Branch protection is not the same as code review.

Code review produces evaluation and decisions. Branch protection determines which conditions are mandatory before integration.

The Bayesian posterior is another condition in the modeled governance engine, not a replacement for mandatory controls.

## Required Status Checks

Status checks represent automated evidence.

Each check has one of three states:

- `pass`
- `fail`
- `pending`

The protected branch identifies required check names.

A required check that is absent, pending, or failed does not satisfy the policy.

The Bayesian layer also considers failed and pending checks as separate evidence because they carry different operational meanings.

A failed check indicates known negative evidence.

A pending check indicates incomplete evidence.

## Direct Push Restrictions

Protected branches can prohibit direct pushes.

The model records this as:

`allow_direct_push = false`

The normal path is therefore:

`feature branch → Pull Request → review → checks → protected merge`

This makes the Pull Request the controlled workflow boundary.

## Force-Push Restrictions

The protected branch can prohibit force pushes.

The C++, Java, JavaScript, Python, and PostgreSQL representations explicitly include this policy.

A requested force push is treated as a governance violation when the branch policy prohibits it.

Force-push restrictions are independent of the Bayesian posterior.

A high posterior cannot override an explicit repository protection rule.

## Administrator and Bypass Behavior

Repository administrators may have privileges that differ from ordinary contributors depending on the hosting configuration.

The data model separates repository roles from branch policy so an external authorization layer can distinguish ordinary merge eligibility from privileged bypass authority.

The implementations do not silently grant an administrator a bypass.

A bypass should be an explicit governance action with an auditable actor, reason, and policy decision rather than an implicit side effect of probability.

## Python Implementation

The Python implementation uses dataclasses for domain records and enums for workflow states.

`BayesianRiskEngine` performs the posterior calculation.

`RepositoryGovernance` evaluates:

- Pull Request state
- branch existence
- current-head approvals
- required checks
- unresolved conversations
- requested changes
- linear-history restrictions
- Bayesian threshold

The script also writes a temporary JSON audit record.

The audit contains derived governance information rather than credentials or source code.

Assertions exercise invalid priors, invalid likelihoods, and the probability range.

The Python version is suited to simulation and policy experimentation because the domain objects remain lightweight and easy to modify.

## JavaScript Implementation

The JavaScript implementation uses Node.js standard-library features.

`Repository` extends `EventEmitter`, making Pull Request changes observable as events.

The workflow emits:

- `pull_request.opened`
- `pull_request.updated`

`Map` and `Set` are used for branch storage and reviewer identity deduplication.

The Bayesian policy is represented by `BayesianPolicy`.

The asynchronous audit operation uses `fs/promises` and creates a temporary audit file.

The implementation intentionally uses event-driven behavior rather than directly mirroring the Python object model.

## C++17 Implementation

The C++ program implements a repository-governance engine using STL containers.

`RepositoryGovernance` stores branches in a `std::map`.

Reviewer identities are deduplicated with `std::set`.

`std::vector` stores commits, reviews, and checks.

`std::any_of` and `std::all_of` express policy predicates over the collections.

The `BayesianEngine` calculates the posterior.

The implementation demonstrates a significant state transition:

`a101 approved → a102 added → previous approvals stale`

It then adds fresh approvals for `a102` and introduces an unresolved conversation to demonstrate that approval satisfaction and conversation resolution remain separate conditions.

Exceptions are used for invalid domain state and failed invariants.

## Java 17 Implementation

The Java implementation uses records for immutable value objects such as:

- `Commit`
- `Review`
- `StatusCheck`
- `Branch`
- `BranchProtection`
- `Evidence`
- `Evaluation`

`PullRequest` remains a mutable domain object because commits, reviews, and workflow state can change during the modeled lifecycle.

`ProbabilityPolicy` is an interface that separates Bayesian calculation from repository policy.

`BayesianPolicy` implements the posterior and threshold behavior.

`MergeEligibilityService` coordinates repository state, review state, status checks, branch protection, and Bayesian evidence.

Java streams are used for reviewer selection and status evaluation.

The design separates domain objects from the merge decision service, which makes the policy boundary explicit.

## PostgreSQL Implementation

The PostgreSQL implementation provides a relational governance model.

Core relationships include:

`repository → branch`

`repository → commit_record`

`pull_request → branches`

`pull_request → commits`

`pull_request → reviews`

`review → review_comment`

`pull_request → status_check`

`branch → branch_protection`

`branch_protection → required_status_check`

`pull_request → bayes_evidence`

The database uses:

- primary keys
- foreign keys
- unique constraints
- check constraints
- enum types
- indexes
- triggers
- functions
- views
- CTEs
- transactions

The `bayes_posterior` function implements the direct Bayesian update for a single evidence item.

The governance report uses logarithmic likelihood aggregation:

`log P(E | Safe) = Σ log P(Ei | Safe)`

This is preferable to multiplying many small probabilities directly because logarithmic accumulation reduces numerical underflow as the number of evidence items grows.

The final posterior is recovered from the accumulated safe and unsafe weights.

## Database Integrity

The `validate_pull_request_commit` trigger ensures that a Pull Request and its commits belong to the same repository.

This prevents cross-repository commit associations.

The `refresh_head_commit` trigger updates the Pull Request head when its ordered commit set changes.

The schema therefore stores both:

- the ordered changeset
- the current head identity

This supports stale-approval detection.

## Query Model

The PostgreSQL views and queries cover:

- Pull Request retrieval
- current approval counting
- required status-check validation
- Bayesian posterior calculation
- failure analysis
- conversation state
- merge eligibility
- transactional workflow updates
- stale approval detection

The `pull_request_governance_report` view combines deterministic policy gates with the Bayesian probability gate.

A Pull Request is merge-eligible only when all mandatory conditions and the probability threshold are satisfied.

## Deterministic Gates and Probabilistic Evidence

The model deliberately distinguishes hard constraints from probabilistic evidence.

Hard constraints include:

- Pull Request must be open
- target branch must exist
- required approvals must be present
- required checks must pass
- required conversations must be resolved
- prohibited merge strategies must not be used
- prohibited force pushes must not be requested

The Bayesian posterior evaluates the accumulated evidence.

This produces:

`Merge Eligibility = Hard Policy Gates AND Bayesian Probability Gate`

A high posterior cannot make a failed mandatory security check acceptable.

A successful status check does not by itself create a reviewer approval.

This separation prevents unrelated governance concepts from collapsing into one score.

## Complexity and Performance

The in-memory implementations generally inspect the reviews and checks associated with one Pull Request.

For `R` reviews and `C` status checks, a straightforward evaluation is approximately `O(R + C)`.

Reviewer deduplication uses set-based storage.

The PostgreSQL schema adds indexes on common governance paths:

- target branch and Pull Request state
- Pull Request, commit, and review state
- Pull Request and status-check state
- Pull Request commit sequence

The Bayesian SQL calculation aggregates evidence using logarithms.

For a Pull Request with `E` evidence records, the evidence aggregation is approximately `O(E)` before relational filtering and grouping.

## Security Considerations

The examples intentionally avoid credentials, access tokens, passwords, and private source-code contents.

Governance decisions should be auditable.

Important production controls include:

- authenticated reviewer identity
- authorization before accepting reviews
- protected status-check definitions
- immutable audit records
- protection against reviewer self-approval where required
- explicit administrator bypass records
- secure webhook verification
- protection against replayed events
- least-privilege database access
- transaction boundaries around state changes

Bayesian probabilities should not be treated as security guarantees.

They are evidence-based decision signals. Mandatory controls should remain deterministic where the risk policy requires them.

## Edge Cases

The implementations explicitly address:

| Edge case | Result |
|---|---|
| Invalid prior | Validation failure |
| Invalid likelihood | Validation failure |
| Empty commit set | Pull Request cannot be evaluated as mergeable |
| Same source and target branch | Invalid Pull Request |
| Missing target branch | Merge blocked |
| Closed Pull Request | Merge blocked |
| Draft Pull Request | Merge blocked |
| Failed required check | Merge blocked |
| Pending required check | Merge blocked |
| Insufficient approvals | Merge blocked |
| Stale approvals | Not counted for the new head |
| Open conversation | Merge blocked when policy requires resolution |
| Requested changes | Negative review evidence |
| Merge commit under linear-history policy | Merge blocked |
| Force push under protected policy | Merge blocked |
| Low posterior | Bayesian gate fails |

## Educational Structure

The implementations progress from direct probability calculation to a complete repository decision model.

The central learning path is:

`Prior Probability`
→ `Likelihood`
→ `Evidence`
→ `Posterior Probability`
→ `Policy Threshold`
→ `Repository Governance`
→ `Merge Eligibility`

The repository domain provides a concrete setting in which posterior probability has a defined operational role while Pull Requests, code review, approvals, and branch protection retain their separate meanings.
