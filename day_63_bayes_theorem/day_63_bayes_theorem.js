'use strict';

const fs = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');
const EventEmitter = require('node:events');

const PullRequestState = Object.freeze({
    DRAFT: 'draft',
    OPEN: 'open',
    CLOSED: 'closed',
    MERGED: 'merged'
});

const ReviewState = Object.freeze({
    COMMENTED: 'commented',
    CHANGES_REQUESTED: 'changes_requested',
    APPROVED: 'approved',
    DISMISSED: 'dismissed'
});

const CheckState = Object.freeze({
    PASS: 'pass',
    FAIL: 'fail',
    PENDING: 'pending'
});

const MergeStrategy = Object.freeze({
    MERGE_COMMIT: 'merge_commit',
    SQUASH: 'squash',
    REBASE: 'rebase'
});

class ValidationError extends Error {}

class BayesianPolicy {
    constructor(priorSafe = 0.85, threshold = 0.90) {
        if (!(priorSafe > 0 && priorSafe < 1)) {
            throw new ValidationError('Prior probability must be between zero and one.');
        }
        if (!(threshold > 0 && threshold < 1)) {
            throw new ValidationError('Decision threshold must be between zero and one.');
        }
        this.priorSafe = priorSafe;
        this.threshold = threshold;
    }

    posterior(evidence) {
        let safe = this.priorSafe;
        let unsafe = 1 - this.priorSafe;

        for (const item of evidence) {
            if (!(item.safe > 0 && item.safe <= 1) ||
                !(item.unsafe > 0 && item.unsafe <= 1)) {
                throw new ValidationError(`Invalid likelihood for ${item.name}.`);
            }
            safe *= item.safe;
            unsafe *= item.unsafe;
        }

        return safe / (safe + unsafe);
    }
}

class Repository extends EventEmitter {
    constructor(name) {
        super();
        if (!name || !/^[A-Za-z0-9_.-]+$/.test(name)) {
            throw new ValidationError('Repository name contains invalid characters.');
        }

        this.name = name;
        this.branches = new Map();
        this.pullRequests = new Map();
    }

    addBranch(branch) {
        if (this.branches.has(branch.name)) {
            throw new ValidationError(`Branch ${branch.name} already exists.`);
        }
        this.branches.set(branch.name, branch);
    }

    openPullRequest(pr) {
        if (pr.source === pr.target) {
            throw new ValidationError('Source and target branches must differ.');
        }
        if (!this.branches.has(pr.source) || !this.branches.has(pr.target)) {
            throw new ValidationError('Both Pull Request branches must exist.');
        }

        this.pullRequests.set(pr.number, pr);
        this.emit('pull_request.opened', pr);
    }

    updatePullRequest(number, update) {
        const pr = this.pullRequests.get(number);
        if (!pr) {
            throw new ValidationError(`Pull Request #${number} does not exist.`);
        }

        Object.assign(pr, update);
        this.emit('pull_request.updated', pr);
    }
}

class MergeEligibilityService {
    constructor(repository, policy) {
        this.repository = repository;
        this.policy = policy;
    }

    evidenceFor(pr, branch) {
        const currentApprovers = new Set(
            pr.reviews
                .filter(r =>
                    r.state === ReviewState.APPROVED &&
                    r.commitSha === pr.headSha
                )
                .map(r => r.reviewer)
        );

        const changesRequested = pr.reviews.some(r =>
            r.state === ReviewState.CHANGES_REQUESTED &&
            r.commitSha === pr.headSha
        );

        const failedChecks = pr.checks.some(c => c.state === CheckState.FAIL);
        const pendingChecks = pr.checks.some(c => c.state === CheckState.PENDING);

        const allRequiredChecksPassed =
            [...branch.protection.requiredChecks].every(required =>
                pr.checks.some(c =>
                    c.name === required &&
                    c.state === CheckState.PASS
                )
            );

        return [
            {
                name: 'current-head-approval',
                safe: currentApprovers.size >= branch.protection.requiredApprovals ? 0.92 : 0.20,
                unsafe: currentApprovers.size >= branch.protection.requiredApprovals ? 0.08 : 0.80
            },
            {
                name: 'required-status-checks',
                safe: allRequiredChecksPassed ? 0.97 : 0.15,
                unsafe: allRequiredChecksPassed ? 0.03 : 0.85
            },
            {
                name: 'failed-status-check',
                safe: failedChecks ? 0.05 : 0.98,
                unsafe: failedChecks ? 0.95 : 0.02
            },
            {
                name: 'pending-status-check',
                safe: pendingChecks ? 0.35 : 0.94,
                unsafe: pendingChecks ? 0.65 : 0.06
            },
            {
                name: 'resolved-conversations',
                safe: pr.openConversations === 0 ? 0.96 : 0.30,
                unsafe: pr.openConversations === 0 ? 0.04 : 0.70
            },
            {
                name: 'requested-changes',
                safe: changesRequested ? 0.10 : 0.95,
                unsafe: changesRequested ? 0.90 : 0.05
            }
        ];
    }

    evaluate(pr) {
        const reasons = [];

        if (pr.state !== PullRequestState.OPEN) {
            reasons.push('Pull Request is not open.');
            return this.result(false, 0, reasons);
        }

        const target = this.repository.branches.get(pr.target);
        if (!target) {
            reasons.push('Target branch does not exist.');
            return this.result(false, 0, reasons);
        }

        if (pr.commits.length === 0) {
            reasons.push('Pull Request has no commits.');
            return this.result(false, 0, reasons);
        }

        const protection = target.protection;

        if (target.protected) {
            const approvers = new Set(
                pr.reviews
                    .filter(r =>
                        r.state === ReviewState.APPROVED &&
                        r.commitSha === pr.headSha
                    )
                    .map(r => r.reviewer)
            );

            if (approvers.size < protection.requiredApprovals) {
                reasons.push(
                    `Requires ${protection.requiredApprovals} current-head approval(s); found ${approvers.size}.`
                );
            }

            for (const required of protection.requiredChecks) {
                const check = pr.checks.find(c => c.name === required);
                if (!check || check.state !== CheckState.PASS) {
                    reasons.push(`Required check '${required}' has not passed.`);
                }
            }

            if (protection.requireConversationResolution && pr.openConversations > 0) {
                reasons.push('Open review conversations remain.');
            }

            if (protection.requireLinearHistory &&
                pr.mergeStrategy === MergeStrategy.MERGE_COMMIT) {
                reasons.push('Merge commits are prohibited by branch policy.');
            }

            if (!protection.allowForcePush && pr.forcePushRequested) {
                reasons.push('Force push is prohibited on the protected branch.');
            }
        }

        const posterior = this.policy.posterior(this.evidenceFor(pr, target));

        if (posterior < this.policy.threshold) {
            reasons.push(
                `Bayesian posterior ${posterior.toFixed(4)} is below ` +
                `${this.policy.threshold.toFixed(2)}.`
            );
        }

        return this.result(reasons.length === 0, posterior, reasons);
    }

    result(eligible, posterior, reasons) {
        return { eligible, posterior, reasons };
    }
}

async function persistAudit(pr, result) {
    const directory = await fs.mkdtemp(path.join(os.tmpdir(), 'bayes-review-'));
    const file = path.join(directory, 'audit.json');

    const audit = {
        pullRequest: pr.number,
        source: pr.source,
        target: pr.target,
        headCommit: pr.headSha,
        mergeEligible: result.eligible,
        posteriorMergeSafety: Number(result.posterior.toFixed(6)),
        blockingReasons: result.reasons
    };

    await fs.writeFile(file, JSON.stringify(audit, null, 2), 'utf8');
    return file;
}

async function main() {
    const repository = new Repository('payments-service');

    repository.addBranch({
        name: 'main',
        protected: true,
        protection: {
            requiredApprovals: 2,
            requiredChecks: new Set(['unit-tests', 'security-scan']),
            requireConversationResolution: true,
            requireLinearHistory: true,
            allowForcePush: false
        }
    });

    repository.addBranch({
        name: 'feature/payment-validation',
        protected: false
    });

    repository.on('pull_request.opened', pr => {
        console.log(`Event: Pull Request #${pr.number} opened`);
    });

    repository.on('pull_request.updated', pr => {
        console.log(`Event: Pull Request #${pr.number} updated`);
    });

    const pullRequest = {
        number: 42,
        source: 'feature/payment-validation',
        target: 'main',
        state: PullRequestState.OPEN,
        commits: [
            { sha: 'a100', message: 'Add payment validation' },
            { sha: 'a101', message: 'Fix boundary validation' }
        ],
        reviews: [
            {
                reviewer: 'alice',
                state: ReviewState.APPROVED,
                commitSha: 'a101'
            },
            {
                reviewer: 'bob',
                state: ReviewState.APPROVED,
                commitSha: 'a101'
            }
        ],
        checks: [
            { name: 'unit-tests', state: CheckState.PASS },
            { name: 'security-scan', state: CheckState.PASS },
            { name: 'integration-tests', state: CheckState.PASS }
        ],
        openConversations: 0,
        forcePushRequested: false,
        mergeStrategy: MergeStrategy.SQUASH,

        get headSha() {
            return this.commits.at(-1).sha;
        }
    };

    repository.openPullRequest(pullRequest);

    const service = new MergeEligibilityService(
        repository,
        new BayesianPolicy(0.85, 0.90)
    );

    let result = service.evaluate(pullRequest);

    console.log(`Posterior merge safety: ${result.posterior.toFixed(4)}`);
    console.log(`Merge eligible: ${result.eligible}`);

    if (result.reasons.length > 0) {
        console.log('Blocking conditions:');
        for (const reason of result.reasons) {
            console.log(`- ${reason}`);
        }
    }

    await repository.updatePullRequest(42, {
        openConversations: 1
    });

    result = service.evaluate(pullRequest);
    console.log(`After opening a conversation: ${result.eligible}`);

    pullRequest.openConversations = 0;

    const auditFile = await persistAudit(pullRequest, service.evaluate(pullRequest));
    const stored = JSON.parse(await fs.readFile(auditFile, 'utf8'));

    if (stored.pullRequest !== 42) {
        throw new Error('Audit validation failed.');
    }

    console.log(`Audit persisted to: ${auditFile}`);

    const basicPrior = 0.20;
    const safeLikelihood = 0.90;
    const unsafeLikelihood = 0.30;
    const posterior =
        (safeLikelihood * basicPrior) /
        ((safeLikelihood * basicPrior) +
         (unsafeLikelihood * (1 - basicPrior)));

    console.log(`Basic Bayes posterior: ${posterior.toFixed(4)}`);
}

main().catch(error => {
    console.error(`Failure: ${error.message}`);
    process.exitCode = 1;
});
