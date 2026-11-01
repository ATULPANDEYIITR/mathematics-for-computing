'use strict';

/**
 * Rainbow Tables and Password Attacks
 * Event-driven defensive security laboratory.
 *
 * Uses synthetic credentials and a deliberately restricted keyspace.
 * No real authentication endpoints or credential databases are accessed.
 */

const crypto = require('node:crypto');
const { EventEmitter } = require('node:events');
const { promisify } = require('node:util');

const pbkdf2 = promisify(crypto.pbkdf2);

const AttackType = Object.freeze({
    DICTIONARY: 'DICTIONARY',
    BRUTE_FORCE: 'BRUTE_FORCE',
    RAINBOW_TABLE: 'RAINBOW_TABLE',
    PASSWORD_SPRAYING: 'PASSWORD_SPRAYING',
    CREDENTIAL_STUFFING: 'CREDENTIAL_STUFFING',
    PHISHING: 'PHISHING'
});

const AccountState = Object.freeze({
    ACTIVE: 'ACTIVE',
    LOCKED: 'LOCKED',
    DISABLED: 'DISABLED'
});

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = 'ValidationError';
    }
}

class SecurityPolicy {
    constructor({
        minimumLength = 14,
        maximumLength = 128,
        rejectCommon = true
    } = {}) {
        this.minimumLength = minimumLength;
        this.maximumLength = maximumLength;
        this.rejectCommon = rejectCommon;

        this.commonPasswords = new Set([
            'password',
            'password123',
            'admin123',
            'qwerty123',
            'welcome123'
        ]);
    }

    validate(password) {
        if (typeof password !== 'string') {
            throw new ValidationError('Password must be a string.');
        }

        const errors = [];

        if (password.length < this.minimumLength) {
            errors.push('Password is too short.');
        }

        if (password.length > this.maximumLength) {
            errors.push('Password is too long.');
        }

        if (!/[A-Z]/.test(password)) {
            errors.push('Uppercase character required.');
        }

        if (!/[a-z]/.test(password)) {
            errors.push('Lowercase character required.');
        }

        if (!/[0-9]/.test(password)) {
            errors.push('Digit required.');
        }

        if (!/[^a-zA-Z0-9]/.test(password)) {
            errors.push('Special character required.');
        }

        if (
            this.rejectCommon &&
            this.commonPasswords.has(password.toLowerCase())
        ) {
            errors.push('Common password prohibited.');
        }

        return {
            valid: errors.length === 0,
            errors
        };
    }
}

class PasswordHasher {
    constructor(iterations = 600000) {
        if (!Number.isInteger(iterations) || iterations < 100000) {
            throw new ValidationError('Unsafe iteration configuration.');
        }

        this.iterations = iterations;
        this.keyLength = 32;
        this.digest = 'sha256';
    }

    async hash(password) {
        if (typeof password !== 'string' || password.length === 0) {
            throw new ValidationError('Password cannot be empty.');
        }

        const salt = crypto.randomBytes(16);

        const derivedKey = await pbkdf2(
            password,
            salt,
            this.iterations,
            this.keyLength,
            this.digest
        );

        return Object.freeze({
            salt: salt.toString('hex'),
            hash: derivedKey.toString('hex'),
            iterations: this.iterations,
            algorithm: 'PBKDF2-HMAC-SHA256'
        });
    }

    async verify(password, record) {
        if (
            typeof password !== 'string' ||
            !record ||
            !/^[a-f0-9]{32}$/.test(record.salt) ||
            !/^[a-f0-9]{64}$/.test(record.hash)
        ) {
            return false;
        }

        if (
            !Number.isInteger(record.iterations) ||
            record.iterations < 100000 ||
            record.iterations > 10000000
        ) {
            return false;
        }

        const candidate = await pbkdf2(
            password,
            Buffer.from(record.salt, 'hex'),
            record.iterations,
            32,
            'sha256'
        );

        const expected = Buffer.from(record.hash, 'hex');

        return crypto.timingSafeEqual(candidate, expected);
    }
}

class SyntheticRainbowTable {
    constructor({
        alphabet = 'abcd',
        passwordLength = 3,
        chainLength = 8
    } = {}) {
        if (
            !alphabet ||
            new Set(alphabet).size !== alphabet.length ||
            !Number.isInteger(passwordLength) ||
            passwordLength < 1 ||
            passwordLength > 5 ||
            !Number.isInteger(chainLength) ||
            chainLength < 1 ||
            chainLength > 32
        ) {
            throw new ValidationError('Invalid synthetic table configuration.');
        }

        this.alphabet = alphabet;
        this.passwordLength = passwordLength;
        this.chainLength = chainLength;
        this.spaceSize = alphabet.length ** passwordLength;
        this.table = new Map();
    }

    hash(value) {
        return crypto
            .createHash('sha256')
            .update(value, 'utf8')
            .digest('hex');
    }

    reduce(digest, position) {
        let number = (
            BigInt('0x' + digest.slice(0, 16)) +
            BigInt(position * 104729)
        ) % BigInt(this.spaceSize);

        const chars = [];

        for (let i = 0; i < this.passwordLength; i++) {
            chars.push(this.alphabet[Number(number % BigInt(this.alphabet.length))]);
            number /= BigInt(this.alphabet.length);
        }

        return chars.reverse().join('');
    }

    build() {
        this.table.clear();

        for (let index = 0; index < this.spaceSize; index++) {
            let number = index;
            const chars = [];

            for (let i = 0; i < this.passwordLength; i++) {
                chars.push(this.alphabet[number % this.alphabet.length]);
                number = Math.floor(number / this.alphabet.length);
            }

            const start = chars.reverse().join('');
            let current = start;

            for (let position = 0; position < this.chainLength; position++) {
                current = this.reduce(
                    this.hash(current),
                    position
                );
            }

            if (!this.table.has(current)) {
                this.table.set(current, start);
            }
        }
    }

    lookup(targetHash) {
        if (!/^[a-f0-9]{64}$/i.test(targetHash)) {
            throw new ValidationError('Invalid SHA-256 hash.');
        }

        for (
            let position = this.chainLength - 1;
            position >= 0;
            position--
        ) {
            let current = targetHash;

            for (
                let column = position;
                column < this.chainLength;
                column++
            ) {
                current = this.reduce(current, column);

                if (column < this.chainLength - 1) {
                    current = this.hash(current);
                }
            }

            const start = this.table.get(current);

            if (start === undefined) {
                continue;
            }

            let candidate = start;

            for (let column = 0; column < this.chainLength; column++) {
                const digest = this.hash(candidate);

                if (digest === targetHash.toLowerCase()) {
                    return candidate;
                }

                candidate = this.reduce(digest, column);
            }
        }

        return null;
    }
}

class SecurityEventBus extends EventEmitter {
    publish(eventName, payload) {
        this.emit(eventName, Object.freeze({
            timestamp: new Date().toISOString(),
            ...payload
        }));
    }
}

class Account {
    constructor(username, passwordRecord) {
        if (!/^[a-zA-Z0-9_.-]{3,40}$/.test(username)) {
            throw new ValidationError('Invalid username.');
        }

        this.username = username;
        this.passwordRecord = passwordRecord;
        this.state = AccountState.ACTIVE;
        this.failedAttempts = 0;
    }
}

class AuthenticationService {
    constructor({
        hasher = new PasswordHasher(),
        policy = new SecurityPolicy(),
        maxFailures = 5,
        eventBus = new SecurityEventBus()
    } = {}) {
        this.hasher = hasher;
        this.policy = policy;
        this.maxFailures = maxFailures;
        this.eventBus = eventBus;
        this.accounts = new Map();
    }

    async register(username, password) {
        if (this.accounts.has(username)) {
            throw new ValidationError('Account already exists.');
        }

        const validation = this.policy.validate(password);

        if (!validation.valid) {
            throw new ValidationError(validation.errors.join(' '));
        }

        const record = await this.hasher.hash(password);
        const account = new Account(username, record);

        this.accounts.set(username, account);

        this.eventBus.publish('account.registered', {
            username
        });

        return account;
    }

    async authenticate(username, password) {
        const account = this.accounts.get(username);

        if (!account || account.state !== AccountState.ACTIVE) {
            this.eventBus.publish('authentication.rejected', {
                username
            });

            return false;
        }

        const valid = await this.hasher.verify(
            password,
            account.passwordRecord
        );

        if (!valid) {
            account.failedAttempts++;

            if (account.failedAttempts >= this.maxFailures) {
                account.state = AccountState.LOCKED;

                this.eventBus.publish('account.locked', {
                    username
                });
            }

            this.eventBus.publish('authentication.failed', {
                username,
                failedAttempts: account.failedAttempts
            });

            return false;
        }

        account.failedAttempts = 0;

        this.eventBus.publish('authentication.succeeded', {
            username
        });

        return true;
    }
}

class PasswordAudit {
    constructor() {
        this.results = [];
    }

    dictionaryAudit(targetHash, candidates) {
        if (!/^[a-f0-9]{64}$/i.test(targetHash)) {
            throw new ValidationError('Invalid target hash.');
        }

        if (!Array.isArray(candidates) || candidates.length > 1000) {
            throw new ValidationError('Invalid audit candidate collection.');
        }

        let tested = 0;

        for (const candidate of candidates) {
            if (typeof candidate !== 'string') {
                continue;
            }

            tested++;

            const digest = crypto
                .createHash('sha256')
                .update(candidate, 'utf8')
                .digest('hex');

            if (digest === targetHash.toLowerCase()) {
                const result = Object.freeze({
                    attack: AttackType.DICTIONARY,
                    tested,
                    recovered: true
                });

                this.results.push(result);
                return result;
            }
        }

        const result = Object.freeze({
            attack: AttackType.DICTIONARY,
            tested,
            recovered: false
        });

        this.results.push(result);
        return result;
    }

    report() {
        return {
            totalAudits: this.results.length,
            successfulAudits: this.results.filter(
                result => result.recovered
            ).length,
            results: [...this.results]
        };
    }
}

async function main() {
    const events = new SecurityEventBus();

    events.on('account.registered', event => {
        console.log('Account registered:', event.username);
    });

    events.on('account.locked', event => {
        console.log('Security alert: account locked:', event.username);
    });

    events.on('authentication.failed', event => {
        console.log(
            'Failed authentication:',
            event.username,
            event.failedAttempts
        );
    });

    console.log('\n1. Synthetic rainbow-table experiment');

    const rainbow = new SyntheticRainbowTable();
    rainbow.build();

    const syntheticPassword = 'cab';
    const targetHash = rainbow.hash(syntheticPassword);
    const recovered = rainbow.lookup(targetHash);

    console.log({
        searchSpace: rainbow.spaceSize,
        storedChains: rainbow.table.size,
        recovered
    });

    if (recovered !== syntheticPassword) {
        throw new Error('Rainbow-table verification failed.');
    }

    console.log('\n2. Dictionary audit');

    const audit = new PasswordAudit();

    const weakHash = crypto
        .createHash('sha256')
        .update('password123')
        .digest('hex');

    const result = audit.dictionaryAudit(
        weakHash,
        ['admin', 'welcome', 'password123', 'letmein']
    );

    console.log(result);

    console.log('\n3. Password hashing and salt isolation');

    const hasher = new PasswordHasher();

    const first = await hasher.hash('SyntheticExample!2026');
    const second = await hasher.hash('SyntheticExample!2026');

    console.log({
        samePassword: true,
        differentSalts: first.salt !== second.salt,
        differentHashes: first.hash !== second.hash,
        verification: await hasher.verify(
            'SyntheticExample!2026',
            first
        )
    });

    console.log('\n4. Account authentication workflow');

    const authentication = new AuthenticationService({
        hasher,
        eventBus: events,
        maxFailures: 3
    });

    await authentication.register(
        'security_user',
        'SyntheticExample!2026'
    );

    console.log(
        'Valid login:',
        await authentication.authenticate(
            'security_user',
            'SyntheticExample!2026'
        )
    );

    for (let i = 0; i < 3; i++) {
        await authentication.authenticate(
            'security_user',
            'IncorrectExample!2026'
        );
    }

    console.log(
        'Locked account login:',
        await authentication.authenticate(
            'security_user',
            'SyntheticExample!2026'
        )
    );

    console.log('\n5. Audit report');

    console.log(JSON.stringify(audit.report(), null, 2));

    console.log('\n6. Defensive controls');

    const controls = [
        'Unique cryptographically random salts',
        'Argon2id or appropriately configured PBKDF2',
        'Multi-factor authentication',
        'Authentication rate limiting',
        'Account compromise detection',
        'Password reset token expiration',
        'Secure session management',
        'Protected credential storage',
        'Phishing-resistant authentication',
        'Security event monitoring'
    ];

    controls.forEach(control => console.log('-', control));

    console.log('\nAll security laboratory checks completed.');
}

main().catch(error => {
    console.error('Laboratory failure:', error.message);
    process.exitCode = 1;
});
