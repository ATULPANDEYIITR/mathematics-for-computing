"use strict";

/**
 * Modular inverses and modular exponentiation using the extended
 * Euclidean algorithm. BigInt avoids integer precision loss.
 */

class ModularInverseError extends Error {
  constructor(message) {
    super(message);
    this.name = "ModularInverseError";
  }
}

function requireBigInt(value, name) {
  if (typeof value !== "bigint") {
    throw new ModularInverseError(`${name} must be a BigInt.`);
  }
}

function validateModulus(modulus) {
  requireBigInt(modulus, "Modulus");
  if (modulus <= 1n) {
    throw new ModularInverseError("Modulus must be greater than 1.");
  }
}

function extendedGcd(a, b) {
  requireBigInt(a, "a");
  requireBigInt(b, "b");

  let oldR = a < 0n ? -a : a;
  let r = b < 0n ? -b : b;
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

  if (a < 0n) oldS = -oldS;
  if (b < 0n) oldT = -oldT;

  return Object.freeze({ gcd: oldR, x: oldS, y: oldT });
}

function normalize(value, modulus) {
  const remainder = value % modulus;
  return remainder < 0n ? remainder + modulus : remainder;
}

function modularInverse(value, modulus) {
  requireBigInt(value, "Value");
  validateModulus(modulus);

  const result = extendedGcd(value, modulus);

  if (result.gcd !== 1n) {
    throw new ModularInverseError(
      `No inverse exists: gcd(${value}, ${modulus}) = ${result.gcd}.`
    );
  }

  return normalize(result.x, modulus);
}

function modularPower(base, exponent, modulus) {
  requireBigInt(base, "Base");
  requireBigInt(exponent, "Exponent");
  validateModulus(modulus);

  if (exponent < 0n) {
    base = modularInverse(base, modulus);
    exponent = -exponent;
  }

  let result = 1n;
  base = normalize(base, modulus);

  // Binary exponentiation takes O(log |exponent|) multiplications.
  while (exponent > 0n) {
    if (exponent % 2n === 1n) {
      result = (result * base) % modulus;
    }
    base = (base * base) % modulus;
    exponent /= 2n;
  }

  return result;
}

function inverseOrNull(value, modulus) {
  try {
    return modularInverse(value, modulus);
  } catch (error) {
    if (error instanceof ModularInverseError) return null;
    throw error;
  }
}

class InverseRegistry {
  constructor(modulus) {
    validateModulus(modulus);
    this.modulus = modulus;
    this.cache = new Map();
  }

  get(value) {
    requireBigInt(value, "Value");
    const key = normalize(value, this.modulus);

    if (!this.cache.has(key)) {
      this.cache.set(key, inverseOrNull(key, this.modulus));
    }

    return this.cache.get(key);
  }

  report(values) {
    if (!Array.isArray(values)) {
      throw new TypeError("Values must be an array.");
    }

    return values.map((value) => {
      const inverse = this.get(value);
      return Object.freeze({
        value,
        modulus: this.modulus,
        inverse,
        invertible: inverse !== null,
        verified:
          inverse !== null &&
          normalize(value * inverse, this.modulus) === 1n,
      });
    });
  }
}

function runTests() {
  const tests = [
    [3n, 11n, 4n],
    [10n, 17n, 12n],
    [-3n, 11n, 7n],
    [20n, 7n, 6n],
  ];

  for (const [value, modulus, expected] of tests) {
    if (modularInverse(value, modulus) !== expected) {
      throw new Error(`Inverse test failed for ${value} mod ${modulus}`);
    }
  }

  if (modularPower(3n, -2n, 11n) !== 5n) {
    throw new Error("Negative-exponent test failed.");
  }

  if (inverseOrNull(6n, 15n) !== null) {
    throw new Error("Non-invertible value test failed.");
  }

  const registry = new InverseRegistry(11n);
  const report = registry.report([3n, 4n, 6n, -3n]);
  if (report.some((item) => !item.verified)) {
    throw new Error("Registry verification failed.");
  }

  for (let modulus = 2n; modulus < 30n; modulus++) {
    for (let value = -30n; value <= 30n; value++) {
      const inverse = inverseOrNull(value, modulus);
      const result = extendedGcd(value, modulus);

      if (result.gcd === 1n) {
        if (inverse === null ||
            normalize(value * inverse, modulus) !== 1n) {
          throw new Error("Exhaustive inverse test failed.");
        }
      } else if (inverse !== null) {
        throw new Error("Invalid inverse was returned.");
      }
    }
  }

  console.log("All JavaScript tests passed.");
}

function main() {
  runTests();

  const registry = new InverseRegistry(17n);
  console.log("Inverse report modulo 17:");
  for (const item of registry.report([3n, 5n, 8n, 16n])) {
    console.log(
      `${item.value} -> ${item.inverse}; verified=${item.verified}`
    );
  }

  console.log(
    "3^(-2) mod 11 =",
    modularPower(3n, -2n, 11n).toString()
  );
}

main();
