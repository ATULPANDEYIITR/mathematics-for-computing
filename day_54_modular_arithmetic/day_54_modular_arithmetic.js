"use strict";

/**
 * Modular arithmetic engine for repository-independent number-theory tasks.
 * Run with Node.js 18 or later: node modular-arithmetic.js
 */

class ModularArithmeticError extends RangeError {}

function requireBigInt(value, name) {
  if (typeof value !== "bigint") {
    throw new TypeError(`${name} must be a BigInt.`);
  }
}

function validateModulus(modulus) {
  requireBigInt(modulus, "Modulus");
  if (modulus <= 0n) {
    throw new ModularArithmeticError("Modulus must be positive.");
  }
}

function normalize(value, modulus) {
  requireBigInt(value, "Value");
  validateModulus(modulus);
  return ((value % modulus) + modulus) % modulus;
}

function congruent(a, b, modulus) {
  requireBigInt(a, "a");
  requireBigInt(b, "b");
  validateModulus(modulus);
  return normalize(a - b, modulus) === 0n;
}

function addMod(a, b, modulus) {
  return normalize(normalize(a, modulus) + normalize(b, modulus), modulus);
}

function multiplyMod(a, b, modulus) {
  validateModulus(modulus);
  a = normalize(a, modulus);
  b = normalize(b, modulus);

  let result = 0n;

  // Repeated doubling limits the size of intermediate values.
  while (b > 0n) {
    if ((b & 1n) === 1n) {
      result = addMod(result, a, modulus);
    }
    a = addMod(a, a, modulus);
    b >>= 1n;
  }

  return result;
}

function extendedGcd(a, b) {
  let oldR = a;
  let r = b;
  let oldS = 1n;
  let s = 0n;
  let oldT = 0n;
  let t = 1n;

  while (r !== 0n) {
    const quotient = oldR / r;
    [oldR, r] = [r, oldR - quotient * r];
    [oldS, s] = [s, oldS - quotient * s];
    [oldT, t] = [t, oldT - quotient * t];
  }

  if (oldR < 0n) {
    return [-oldR, -oldS, -oldT];
  }
  return [oldR, oldS, oldT];
}

function inverseMod(value, modulus) {
  validateModulus(modulus);
  if (modulus === 1n) {
    throw new ModularArithmeticError(
      "The modulus must exceed one to compute a modular inverse."
    );
  }

  value = normalize(value, modulus);
  const [gcd, coefficient] = extendedGcd(value, modulus);

  if (gcd !== 1n) {
    throw new ModularArithmeticError(
      `Inverse does not exist: gcd(${value}, ${modulus}) = ${gcd}.`
    );
  }

  return normalize(coefficient, modulus);
}

function powerMod(base, exponent, modulus) {
  requireBigInt(base, "Base");
  requireBigInt(exponent, "Exponent");
  validateModulus(modulus);

  if (exponent < 0n) {
    base = inverseMod(base, modulus);
    exponent = -exponent;
  }

  base = normalize(base, modulus);
  let result = 1n % modulus;

  while (exponent > 0n) {
    if ((exponent & 1n) === 1n) {
      result = multiplyMod(result, base, modulus);
    }
    base = multiplyMod(base, base, modulus);
    exponent >>= 1n;
  }

  return result;
}

class Residue {
  #value;
  #modulus;

  constructor(value, modulus) {
    this.#value = normalize(value, modulus);
    this.#modulus = modulus;
    Object.freeze(this);
  }

  get value() {
    return this.#value;
  }

  get modulus() {
    return this.#modulus;
  }

  #check(other) {
    if (!(other instanceof Residue)) {
      throw new TypeError("Expected a Residue.");
    }
    if (this.#modulus !== other.#modulus) {
      throw new ModularArithmeticError("Moduli must match.");
    }
  }

  add(other) {
    this.#check(other);
    return new Residue(
      addMod(this.#value, other.#value, this.#modulus),
      this.#modulus
    );
  }

  multiply(other) {
    this.#check(other);
    return new Residue(
      multiplyMod(this.#value, other.#value, this.#modulus),
      this.#modulus
    );
  }

  power(exponent) {
    return new Residue(
      powerMod(this.#value, exponent, this.#modulus),
      this.#modulus
    );
  }

  toString() {
    return `${this.#value} (mod ${this.#modulus})`;
  }
}

/**
 * Event-driven evaluator. Each request is validated and recorded with a
 * monotonically increasing sequence number. Failed requests remain observable.
 */
class ArithmeticService {
  #sequence = 0;
  #listeners = new Map();

  on(eventName, listener) {
    if (typeof listener !== "function") {
      throw new TypeError("Listener must be a function.");
    }
    if (!this.#listeners.has(eventName)) {
      this.#listeners.set(eventName, new Set());
    }
    this.#listeners.get(eventName).add(listener);

    return () => this.#listeners.get(eventName)?.delete(listener);
  }

  #emit(eventName, event) {
    for (const listener of this.#listeners.get(eventName) ?? []) {
      try {
        listener(Object.freeze({ ...event }));
      } catch (error) {
        // Observer failures must not change the arithmetic result.
        process.stderr.write(`Observer error: ${error.message}\n`);
      }
    }
  }

  evaluate(operation, operands) {
    const sequence = ++this.#sequence;

    try {
      const { a, b, modulus, exponent } = operands;
      validateModulus(modulus);

      let result;
      switch (operation) {
        case "normalize":
          result = normalize(a, modulus);
          break;
        case "congruent":
          result = congruent(a, b, modulus);
          break;
        case "add":
          result = addMod(a, b, modulus);
          break;
        case "multiply":
          result = multiplyMod(a, b, modulus);
          break;
        case "power":
          result = powerMod(a, exponent, modulus);
          break;
        case "inverse":
          result = inverseMod(a, modulus);
          break;
        default:
          throw new ModularArithmeticError(
            `Unsupported operation: ${operation}`
          );
      }

      const event = { sequence, operation, success: true, result };
      this.#emit("completed", event);
      return event;
    } catch (error) {
      const event = {
        sequence,
        operation,
        success: false,
        error: error.message
      };
      this.#emit("failed", event);
      return event;
    }
  }
}

function runTests() {
  const mod = 97n;
  if (normalize(-1n, 5n) !== 4n) throw new Error("Normalization failed.");
  if (!congruent(17n, 2n, 5n)) throw new Error("Congruence failed.");
  if (addMod(-7n, 12n, 5n) !== 0n) throw new Error("Addition failed.");
  if (multiplyMod(123n, 456n, mod) !== (123n * 456n) % mod) {
    throw new Error("Multiplication failed.");
  }
  if (powerMod(3n, 100n, 7n) !== 4n) throw new Error("Power failed.");
  if (inverseMod(3n, 11n) !== 4n) throw new Error("Inverse failed.");

  let rejected = false;
  try {
    inverseMod(6n, 9n);
  } catch (error) {
    rejected = error instanceof ModularArithmeticError;
  }
  if (!rejected) throw new Error("Non-invertible value was accepted.");

  const service = new ArithmeticService();
  const observed = [];
  service.on("completed", event => observed.push(event.sequence));
  service.evaluate("add", { a: 2n, b: 3n, modulus: 7n });
  service.evaluate("invalid", { a: 1n, modulus: 7n });
  if (observed.length !== 1) throw new Error("Event handling failed.");

  console.log("All JavaScript modular arithmetic tests passed.");
}

function main() {
  runTests();

  const service = new ArithmeticService();
  service.on("completed", event => {
    console.log(`[${event.sequence}] ${event.operation}: ${event.result}`);
  });
  service.on("failed", event => {
    console.error(`[${event.sequence}] ${event.operation}: ${event.error}`);
  });

  service.evaluate("add", {
    a: 123n,
    b: -45n,
    modulus: 17n
  });
  service.evaluate("multiply", {
    a: 123456n,
    b: 789012n,
    modulus: 97n
  });
  service.evaluate("power", {
    a: 3n,
    exponent: 100n,
    modulus: 17n
  });
  service.evaluate("inverse", {
    a: 5n,
    modulus: 17n
  });
  service.evaluate("inverse", {
    a: 6n,
    modulus: 9n
  });

  const residue = new Residue(-2n, 7n);
  console.log(`Residue: ${residue}`);
  console.log(`Residue product: ${residue.multiply(new Residue(3n, 7n))}`);
}

main();
