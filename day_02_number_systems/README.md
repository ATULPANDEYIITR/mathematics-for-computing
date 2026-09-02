# Number System

## Introduction

A number system is a method of representing numbers using a defined set of symbols and a specific base. Number systems are fundamental to mathematics, computer science, digital electronics, programming, computer architecture, networking, and data representation.

In everyday life, the decimal number system is normally used. Computers, on the other hand, work internally with binary values because their electronic components naturally operate using two distinguishable states. Octal and hexadecimal systems are also widely used because they provide convenient and compact ways of representing binary values.

Understanding number systems means understanding how numbers are represented, converted, stored, interpreted, and manipulated.

---

## What Is a Number System?

A number system defines:

* The symbols that can be used to represent numbers.
* The number of symbols available.
* The base or radix of the system.
* The positional value of each digit.
* How numbers are converted from one representation to another.
* How arithmetic operations are performed.
* How numbers are represented inside computer memory.

For example:

* Decimal uses base 10.
* Binary uses base 2.
* Octal uses base 8.
* Hexadecimal uses base 16.

The base determines how many different symbols are available and how the positional value of each digit changes.

---

## Base or Radix

The **base**, also called the **radix**, is the number of unique digits available in a number system, including zero.

### Common bases

| Number System | Base | Digits   |
| ------------- | ---: | -------- |
| Binary        |    2 | 0, 1     |
| Octal         |    8 | 0–7      |
| Decimal       |   10 | 0–9      |
| Hexadecimal   |   16 | 0–9, A–F |

A number system with base `b` uses digits ranging from `0` to `b - 1`.

For example, binary has base 2, so its only valid digits are `0` and `1`.

---

## Positional Number Systems

Most number systems used in computing are positional number systems.

In a positional system, the value of a digit depends on:

1. The digit itself.
2. Its position.
3. The base of the number system.

For example, in decimal:

`583`

means:

* 5 hundreds
* 8 tens
* 3 ones

Therefore:

`583 = 5 × 10² + 8 × 10¹ + 3 × 10⁰`

The same principle applies to binary, octal, hexadecimal, and other positional systems.

---

## General Positional Representation

A number represented in base `b` can be expressed as:

`(dₙdₙ₋₁...d₂d₁d₀)ᵦ`

Its decimal value is:

`dₙ × bⁿ + dₙ₋₁ × bⁿ⁻¹ + ... + d₂ × b² + d₁ × b¹ + d₀ × b⁰`

This positional formula is one of the most important ideas in number systems.

It explains why the same digit can have different values depending on its position and base.

---

# Decimal Number System

The decimal system is the standard number system used in everyday mathematics.

It uses:

`0, 1, 2, 3, 4, 5, 6, 7, 8, 9`

Its base is 10.

Each position represents a power of 10.

For example:

`472`

means:

`4 × 10² + 7 × 10¹ + 2 × 10⁰`

which equals:

`400 + 70 + 2 = 472`

Decimal is convenient for humans because people traditionally count using ten fingers, but computers do not naturally operate using decimal representation internally.

---

# Binary Number System

The binary number system has base 2.

It uses only:

`0` and `1`

Each binary digit is called a **bit**.

Binary is fundamental to computing because digital electronic systems can represent information using two distinguishable states.

These states can conceptually correspond to:

* Off and on
* Low and high
* False and true
* 0 and 1

Binary values are therefore used to represent data at the lowest levels of computer systems.

---

## Binary Place Values

Binary positions represent powers of 2.

Starting from the right:

| Position | Power | Value |
| -------- | ----: | ----: |
| 0        |    2⁰ |     1 |
| 1        |    2¹ |     2 |
| 2        |    2² |     4 |
| 3        |    2³ |     8 |
| 4        |    2⁴ |    16 |
| 5        |    2⁵ |    32 |
| 6        |    2⁶ |    64 |
| 7        |    2⁷ |   128 |

For example:

`1011₂`

means:

`1 × 2³ + 0 × 2² + 1 × 2¹ + 1 × 2⁰`

Therefore:

`8 + 0 + 2 + 1 = 11`

So:

`1011₂ = 11₁₀`

---

# Decimal to Binary Conversion

One common method for converting a decimal integer into binary is repeated division by 2.

The process is:

1. Divide the decimal number by 2.
2. Record the remainder.
3. Divide the quotient by 2 again.
4. Continue until the quotient becomes zero.
5. Read the remainders from bottom to top.

For example, converting 13 to binary produces:

`13₁₀ = 1101₂`

The method works because every binary position represents a power of 2.

---

# Binary to Decimal Conversion

To convert binary to decimal:

1. Identify the position of each bit.
2. Determine the corresponding power of 2.
3. Multiply each bit by its positional value.
4. Add the results.

For example:

`1101₂`

is:

`1 × 2³ + 1 × 2² + 0 × 2¹ + 1 × 2⁰`

which equals:

`8 + 4 + 0 + 1 = 13`

Therefore:

`1101₂ = 13₁₀`

---

# Octal Number System

The octal number system has base 8.

It uses:

`0, 1, 2, 3, 4, 5, 6, 7`

The digits `8` and `9` are not valid octal digits.

Octal was historically useful in computing because binary numbers can be grouped efficiently into sets of three bits.

For example:

`101 110 011`

can be interpreted as three octal digits.

---

# Binary and Octal Relationship

Every octal digit corresponds to exactly three binary bits.

| Octal | Binary |
| ----: | ------ |
|     0 | 000    |
|     1 | 001    |
|     2 | 010    |
|     3 | 011    |
|     4 | 100    |
|     5 | 101    |
|     6 | 110    |
|     7 | 111    |

This relationship exists because:

`8 = 2³`

Therefore, three binary bits can represent exactly eight different values.

---

# Hexadecimal Number System

The hexadecimal number system has base 16.

It uses sixteen symbols:

`0–9` and `A–F`

The letters represent values greater than 9.

| Hexadecimal | Decimal |
| ----------- | ------: |
| 0           |       0 |
| 1           |       1 |
| 2           |       2 |
| 3           |       3 |
| 4           |       4 |
| 5           |       5 |
| 6           |       6 |
| 7           |       7 |
| 8           |       8 |
| 9           |       9 |
| A           |      10 |
| B           |      11 |
| C           |      12 |
| D           |      13 |
| E           |      14 |
| F           |      15 |

Hexadecimal is extremely useful in computing because:

`16 = 2⁴`

Therefore, every hexadecimal digit corresponds exactly to four binary bits.

---

# Binary and Hexadecimal Relationship

Each hexadecimal digit represents four binary bits.

| Hex | Binary |
| --- | ------ |
| 0   | 0000   |
| 1   | 0001   |
| 2   | 0010   |
| 3   | 0011   |
| 4   | 0100   |
| 5   | 0101   |
| 6   | 0110   |
| 7   | 0111   |
| 8   | 1000   |
| 9   | 1001   |
| A   | 1010   |
| B   | 1011   |
| C   | 1100   |
| D   | 1101   |
| E   | 1110   |
| F   | 1111   |

For example:

`10101111₂`

can be divided into:

`1010 1111`

which corresponds to:

`AF₁₆`

This makes hexadecimal a compact representation of binary data.

---

# Number System Prefixes

Programming languages commonly use prefixes to identify non-decimal numbers.

Typical representations include:

* Binary: `0b`
* Octal: `0o`
* Hexadecimal: `0x`

For example:

* `0b1010`
* `0o12`
* `0xA`

All three represent the decimal value 10.

The exact syntax can depend on the programming language, but these prefixes are widely recognized.

---

# Bits and Bytes

A **bit** is the smallest commonly used unit of digital information.

A bit can contain either:

`0`

or:

`1`

A **byte** normally contains 8 bits.

Therefore:

`1 byte = 8 bits`

An 8-bit value can represent:

`2⁸ = 256`

different combinations.

For unsigned values, those combinations represent:

`0 to 255`

---

# Powers of Two

Powers of two are extremely important in computer science because binary is based on powers of two.

Common values include:

| Power |                      Value |
| ----- | -------------------------: |
| 2⁰    |                          1 |
| 2¹    |                          2 |
| 2²    |                          4 |
| 2³    |                          8 |
| 2⁴    |                         16 |
| 2⁵    |                         32 |
| 2⁶    |                         64 |
| 2⁷    |                        128 |
| 2⁸    |                        256 |
| 2¹⁰   |                       1024 |
| 2¹⁶   |                      65536 |
| 2³²   |              4,294,967,296 |
| 2⁶⁴   | 18,446,744,073,709,551,616 |

Powers of two appear in memory sizes, integer ranges, addressing, bit operations, data structures, and computer architecture.

---

# Unsigned Integer Representation

An unsigned integer does not use a bit to represent a sign.

If `n` bits are available, the range is:

`0` to `2ⁿ - 1`

For example, with 8 bits:

`0` to `255`

With 16 bits:

`0` to `65,535`

With 32 bits:

`0` to `4,294,967,295`

The number of possible values is always:

`2ⁿ`

---

# Signed Integer Representation

Signed integers can represent both positive and negative numbers.

Modern computers commonly use **two's complement** representation for signed integers.

For an `n`-bit two's complement integer, the range is:

`-2ⁿ⁻¹` to `2ⁿ⁻¹ - 1`

For 8 bits:

`-128 to 127`

For 16 bits:

`-32,768 to 32,767`

The negative and positive ranges are not perfectly symmetrical because zero occupies one representation.

---

# Sign-Magnitude Representation

In sign-magnitude representation, one bit is used for the sign and the remaining bits represent the magnitude.

Usually:

* `0` represents positive.
* `1` represents negative.

One limitation is that sign-magnitude has two representations of zero:

* Positive zero
* Negative zero

This is one reason it is not the standard representation for modern general-purpose signed integers.

---

# One's Complement

In one's complement representation, a negative number is obtained by inverting every bit of the positive number.

For example:

`00000101`

represents positive 5.

Inverting every bit produces:

`11111010`

which represents negative 5 under one's complement interpretation.

One's complement also has two representations of zero, which is an undesirable property for general integer arithmetic.

---

# Two's Complement

Two's complement is the standard representation commonly used for signed integers in modern computers.

To obtain the negative representation of a positive number:

1. Write the positive number in binary.
2. Invert every bit.
3. Add 1.

For example, using 8 bits:

Positive 5:

`00000101`

Invert the bits:

`11111010`

Add 1:

`11111011`

Therefore, `11111011` represents `-5` in 8-bit two's complement.

---

# Why Two's Complement Is Useful

Two's complement provides several important advantages:

* Only one representation of zero exists.
* Addition and subtraction can use the same underlying binary arithmetic.
* Hardware implementation becomes simpler.
* Signed and unsigned bit patterns can share the same physical storage.
* Negative values have a predictable mathematical interpretation.

This makes two's complement particularly suitable for computer hardware.

---

# Sign Extension

Sign extension occurs when a signed binary number is moved from a smaller width to a larger width.

The sign bit is copied into the newly added positions.

For example, a negative 8-bit two's complement value can be extended to 16 bits by filling the additional leftmost positions with `1`.

A positive value is extended by filling the additional positions with `0`.

Sign extension preserves the numerical value of a signed integer.

---

# Zero Extension

Zero extension is generally used with unsigned values.

When increasing the width of an unsigned binary number, zeros are added to the left.

For example:

`00001101`

can be extended to a larger width as:

`0000000000001101`

The numerical value remains unchanged.

---

# Integer Overflow

Overflow occurs when a calculation produces a value outside the range that can be represented using the available number of bits.

For example, an unsigned 8-bit integer can represent only:

`0 to 255`

If an operation attempts to produce a value greater than 255, the result cannot be represented directly within 8 bits.

Similarly, signed integers have their own limited ranges.

Overflow is an important concept in programming, embedded systems, computer architecture, and numerical computation.

---

# Wraparound

Unsigned arithmetic commonly exhibits wraparound behavior when values exceed the available range.

For an 8-bit unsigned value:

`255 + 1`

produces a bit pattern corresponding to:

`0`

because only eight bits are retained.

This behavior is closely related to modular arithmetic.

---

# Modular Arithmetic

Modular arithmetic considers numbers relative to a fixed modulus.

For an `n`-bit unsigned representation, arithmetic naturally corresponds to:

`mod 2ⁿ`

For 8-bit arithmetic:

`mod 256`

This explains why:

`255 + 1 = 0`

in an 8-bit unsigned context.

Modular arithmetic is important in:

* Computer arithmetic
* Cryptography
* Hash functions
* Random number generation
* Algorithms
* Digital systems

---

# Decimal Fractions

Number systems can represent fractional values as well as integers.

Decimal fractions use negative powers of the base.

For example:

`12.34`

can be interpreted as:

`1 × 10¹ + 2 × 10⁰ + 3 × 10⁻¹ + 4 × 10⁻²`

The same principle applies to binary fractions.

---

# Binary Fractions

Binary fractions use negative powers of 2.

For example:

`0.101₂`

means:

`1 × 2⁻¹ + 0 × 2⁻² + 1 × 2⁻³`

which equals:

`0.5 + 0 + 0.125`

Therefore:

`0.101₂ = 0.625₁₀`

---

# Decimal to Binary Fraction Conversion

To convert a decimal fraction to binary, repeatedly multiply the fractional part by 2.

At each step:

1. Multiply the fraction by 2.
2. Record the integer part.
3. Continue using the remaining fractional part.
4. The recorded bits form the binary fraction.

Some decimal fractions terminate in binary.

Others continue indefinitely.

---

# Repeating Binary Fractions

Not every decimal fraction can be represented exactly using a finite number of binary digits.

For example, the decimal value:

`0.1`

does not have a finite exact binary representation.

It becomes a repeating binary fraction.

This is one of the reasons floating-point calculations can sometimes produce results that appear surprising when decimal values are used in programming.

---

# Floating-Point Representation

Floating-point representation is used to represent numbers containing fractional values and numbers with very large or very small magnitudes.

A floating-point value can conceptually be described using:

* Sign
* Significant digits
* Exponent
* Base

Modern systems commonly use binary floating-point formats such as IEEE 754.

Floating-point representation provides a large range of values but does not guarantee exact representation of every decimal number.

---

# Precision and Range

Two important properties of numerical representation are:

### Range

Range describes the smallest and largest values that can be represented.

### Precision

Precision describes how accurately values can be represented.

Increasing the number of available bits can generally increase the amount of information that can be stored, but the relationship between precision and range depends on the representation format.

---

# Fixed-Width Representation

Computer systems frequently work with fixed-width integers.

Examples include:

* 8-bit integers
* 16-bit integers
* 32-bit integers
* 64-bit integers

The width determines how many different bit patterns are available.

For `n` bits:

`2ⁿ`

different patterns are possible.

The interpretation of those patterns depends on whether the data is treated as:

* Unsigned
* Signed
* Character data
* Floating-point data
* Flags
* Addresses
* Encoded information

The same physical bits can therefore have different meanings depending on context.

---

# Leading Zeros

Leading zeros do not change the mathematical value of an unsigned positional number.

For example:

`101`

and:

`00000101`

represent the same numerical value.

Leading zeros are important when working with fixed-width representations because they show the complete size of the representation.

---

# Radix Point

The decimal point in a decimal number is more generally called a **radix point**.

For decimal:

`123.45`

the radix point separates:

* Positive powers of 10
* Negative powers of 10

For binary:

`101.101₂`

the radix point separates:

* Integer binary digits
* Fractional binary digits

The same concept applies to any positional number system.

---

# General Base Conversion

Number systems can be converted between arbitrary bases.

One common strategy is:

`Source Base → Decimal → Target Base`

For example:

`Binary → Decimal → Hexadecimal`

Another efficient strategy can be used when two bases have a direct mathematical relationship.

Binary, octal, and hexadecimal are especially convenient because their bases are powers of two.

---

# Binary to Octal Conversion

Since:

`8 = 2³`

binary digits can be grouped into sets of three.

For example:

`110101₂`

can be grouped as:

`110 101`

The groups correspond to octal digits.

This method avoids converting through decimal.

---

# Binary to Hexadecimal Conversion

Since:

`16 = 2⁴`

binary digits can be grouped into sets of four.

For example:

`10111100₂`

becomes:

`1011 1100`

which corresponds to:

`BC₁₆`

This is one of the most useful practical number-system conversions in computing.

---

# Hexadecimal to Binary

Each hexadecimal digit can be replaced with its four-bit binary equivalent.

For example:

`A5₁₆`

becomes:

`1010 0101₂`

Hexadecimal therefore provides a compact way to display binary information.

---

# Octal to Binary

Each octal digit can be replaced with its three-bit binary equivalent.

For example:

`57₈`

becomes:

`101 111₂`

The direct relationship exists because:

`8 = 2³`

---

# Number Systems and Computer Memory

Computer memory stores information as binary patterns.

A memory location can contain a sequence of bits such as:

`10110110`

The same bit pattern can be interpreted differently depending on the data type.

It could represent:

* An unsigned integer
* A signed integer
* Part of a character encoding
* A bit mask
* A machine instruction
* Part of an address
* Part of a larger numerical value

Therefore, a number system describes representation, while the data type determines interpretation.

---

# Number Systems and Memory Addresses

Memory addresses are commonly displayed using hexadecimal notation.

Hexadecimal is convenient because it represents binary compactly.

A long binary address is difficult for humans to read:

`110101101010001011010110`

The same information can be expressed more compactly using hexadecimal.

This is why hexadecimal appears frequently in:

* Debuggers
* Assembly language
* Operating systems
* Computer architecture
* Memory inspection
* Low-level programming

---

# Endianness

Endianness describes the order in which multi-byte values are stored in memory.

The two common forms are:

* Big-endian
* Little-endian

Suppose a multi-byte number contains several bytes.

The bytes can be arranged differently in memory depending on the architecture.

Endianness does not change the mathematical value itself. It changes how the individual bytes of that value are arranged in memory.

This distinction is important when interpreting raw binary data.

---

# Bitwise Operations

Binary representation is directly connected to bitwise operations.

Common bitwise operations include:

* AND
* OR
* XOR
* NOT
* Left shift
* Right shift

These operations work directly on the individual bits of a value.

---

# Bitwise AND

AND produces `1` only when both corresponding bits are `1`.

| A | B | A AND B |
| - | - | ------- |
| 0 | 0 | 0       |
| 0 | 1 | 0       |
| 1 | 0 | 0       |
| 1 | 1 | 1       |

AND is commonly used for:

* Bit masking
* Checking flags
* Extracting specific bits
* Permission systems
* Low-level programming

---

# Bitwise OR

OR produces `1` when at least one corresponding bit is `1`.

| A | B | A OR B |
| - | - | ------ |
| 0 | 0 | 0      |
| 0 | 1 | 1      |
| 1 | 0 | 1      |
| 1 | 1 | 1      |

OR is useful when setting selected bits.

---

# Bitwise XOR

XOR produces `1` when the two input bits are different.

| A | B | A XOR B |
| - | - | ------- |
| 0 | 0 | 0       |
| 0 | 1 | 1       |
| 1 | 0 | 1       |
| 1 | 1 | 0       |

XOR has important applications in:

* Cryptography
* Error detection
* Bit manipulation
* Algorithms
* Encoding techniques

---

# Bitwise NOT

NOT reverses every bit.

A `0` becomes `1`.

A `1` becomes `0`.

For fixed-width values, the width matters because the number of bits being inverted must be defined.

---

# Bit Shifting

Bit shifting moves bits to the left or right.

### Left shift

A left shift moves bits toward more significant positions.

For unsigned values, shifting left by one position is commonly equivalent to multiplying by 2 when no overflow occurs.

### Right shift

A right shift moves bits toward less significant positions.

For unsigned values, shifting right by one position is commonly equivalent to integer division by 2.

The exact behavior of right shifting signed values can depend on the programming language and representation.

---

# Bit Masks

A bit mask is a binary pattern used to select, modify, or inspect specific bits.

For example, a mask can be used to:

* Check whether a particular bit is set.
* Turn a bit on.
* Turn a bit off.
* Extract a group of bits.
* Store multiple Boolean flags in a single integer.

Bit masks are a practical application of binary number systems.

---

# Most Significant Bit and Least Significant Bit

The **Most Significant Bit**, or MSB, is the leftmost bit in a fixed-width binary representation.

The **Least Significant Bit**, or LSB, is the rightmost bit.

The LSB represents the smallest positional value.

For an unsigned binary number, the LSB represents:

`2⁰ = 1`

The MSB has the largest positional value within the chosen width.

In signed two's complement representation, the MSB also acts as the sign indicator.

---

# Bit Position

Each bit position corresponds to a power of two.

For example:

`10000000`

in an 8-bit unsigned representation has the MSB set.

Its value is:

`2⁷ = 128`

Changing a single bit can therefore change the numerical value significantly depending on its position.

---

# Number Systems and Boolean Logic

Binary numbers are closely related to Boolean logic.

Boolean logic deals with values such as:

* True
* False

These can be represented as:

* `1`
* `0`

This creates a direct connection between:

* Number systems
* Digital logic
* Logic gates
* Bitwise operations
* Computer processors

---

# Number Systems and Computer Architecture

At the hardware level, processors operate on binary data.

Number systems are involved in:

* Registers
* Arithmetic logic units
* Memory
* CPU instructions
* Addresses
* Data buses
* Bit operations
* Integer arithmetic

Understanding binary representation therefore helps explain how processors manipulate data.

---

# Number Systems in Networking

Number systems are also important in computer networking.

Binary and hexadecimal representations appear in:

* IP addresses
* Subnet masks
* Network masks
* MAC addresses
* Packet structures
* Protocol fields
* Bit flags

For example, an IPv4 address is normally displayed using decimal notation, but internally it consists of 32 binary bits.

---

# Number Systems in Cryptography

Cryptographic algorithms frequently operate on binary values and fixed-width integers.

Number systems are relevant to:

* Bitwise operations
* Modular arithmetic
* Integer representations
* Binary transformations
* Hash functions
* Encryption algorithms
* Key representation

Hexadecimal notation is also frequently used when displaying cryptographic values because it is much more compact than binary.

---

# Number Systems in Algorithms

Many algorithms depend on binary representation.

Examples include:

* Bit manipulation
* Binary search
* Bit counting
* Power-of-two calculations
* Binary trees
* Heap indexing
* Hashing
* Compression
* Encoding

Understanding number systems makes these algorithms easier to understand at a lower level.

---

# Binary Search and Number Representation

Binary search repeatedly divides a search space into smaller portions.

Although binary search is not directly a number-system conversion technique, its name reflects the concept of repeatedly dividing by two.

Understanding powers of two and binary representation helps explain why logarithmic behavior appears in many divide-and-conquer algorithms.

---

# Hamming Distance

Hamming distance measures the number of positions at which two equal-length binary strings differ.

For example:

`101101`

and:

`100001`

differ at specific bit positions.

The number of differing positions is their Hamming distance.

Hamming distance is used in:

* Error detection
* Error correction
* Information theory
* Coding theory
* Digital communication

---

# Gray Code

Gray code is a binary numeral system in which consecutive values differ by only one bit.

This property can be useful in systems where changing multiple bits simultaneously could cause unwanted transitional states.

Gray code has applications in:

* Digital electronics
* Position encoders
* Communication systems
* Hardware design

---

# Binary-Coded Decimal

Binary-Coded Decimal, or BCD, represents each decimal digit separately using binary.

For example, decimal digits are encoded individually rather than converting the complete decimal number directly into binary.

BCD is useful in situations where exact decimal digit representation is important.

It differs from ordinary binary representation because the entire decimal number is not treated as one binary integer.

---

# ASCII and Numeric Representation

Character encodings assign numerical values to characters.

ASCII is one well-known character encoding system.

For example, characters such as letters, digits, and punctuation correspond to numerical codes.

This demonstrates an important concept:

> A bit pattern does not have an inherent meaning by itself.

Its meaning depends on the representation and interpretation being used.

---

# Hexadecimal as Human-Friendly Binary

Binary is excellent for machines but can be difficult for humans to read.

Hexadecimal provides a shorter representation.

Every hexadecimal digit represents four bits.

Therefore, a long binary sequence can be reduced significantly without losing information.

This is why hexadecimal is common in:

* Programming
* Debugging
* Memory addresses
* Machine code
* Cryptography
* Color codes
* Network analysis

---

# Color Representation

Digital colors are often represented using hexadecimal notation.

A common RGB color representation uses three components:

* Red
* Green
* Blue

Each component can be represented using two hexadecimal digits.

This results in a six-digit hexadecimal representation.

For example:

`#FF0000`

represents maximum red with zero green and zero blue in the standard RGB interpretation.

This is another practical example of hexadecimal being used as a compact representation of binary data.

---

# Mathematical Base Versus Storage Format

A number system describes how a value is written.

A storage format describes how information is actually stored.

These concepts should not be confused.

For example, the same numerical value can be written as:

`10₁₀`

`1010₂`

`12₈`

`A₁₆`

The mathematical value is the same.

Only the representation changes.

Similarly, displaying a number in hexadecimal does not necessarily mean that the computer stores a special "hexadecimal number." The underlying bits are what are physically stored.

---

# Information Capacity

The number of possible combinations increases exponentially with the number of bits.

With:

* 1 bit → 2 combinations
* 2 bits → 4 combinations
* 3 bits → 8 combinations
* 4 bits → 16 combinations
* 8 bits → 256 combinations
* 16 bits → 65,536 combinations
* 32 bits → 4,294,967,296 combinations

The general formula is:

`Number of combinations = 2ⁿ`

where `n` is the number of bits.

---

# Number of Bits Required

The number of bits required to represent a positive integer depends on its magnitude.

For a positive integer `N`, the minimum number of bits required can be determined using:

`floor(log₂(N)) + 1`

for `N > 0`.

For example, 8 requires four bits because:

`8 = 1000₂`

The number 7 requires three bits:

`7 = 111₂`

This relationship between logarithms and binary representation is important in algorithm analysis and computer science.

---

# Binary Prefixes and Memory Units

Computer systems use several units related to powers of two.

Common binary quantities include:

* 1 KiB = 1024 bytes
* 1 MiB = 1024 KiB
* 1 GiB = 1024 MiB
* 1 TiB = 1024 GiB

The `KiB`, `MiB`, `GiB`, and `TiB` terminology specifically refers to binary-based quantities.

Decimal units such as KB, MB, and GB are also used, and their exact definitions depend on the context.

---

# Carrying in Different Bases

Arithmetic rules depend on the base.

In decimal, a carry occurs after reaching 10.

In binary, a carry occurs after reaching 2.

For example:

`1 + 1 = 10₂`

The result contains a zero in the current position and carries one into the next position.

The same principle applies to every positional number system.

---

# Binary Addition

Binary addition follows a small set of rules:

| A | B | Result |
| - | - | ------ |
| 0 | 0 | 0      |
| 0 | 1 | 1      |
| 1 | 0 | 1      |
| 1 | 1 | 10     |

When adding multiple binary digits, carries are propagated to the next position.

Binary addition is the foundation of integer arithmetic inside digital computers.

---

# Binary Subtraction

Binary subtraction follows principles similar to decimal subtraction but uses only two digits.

When a smaller bit must be subtracted from a larger required value, borrowing occurs from a higher position.

Binary subtraction is closely connected to two's complement arithmetic in computer systems.

---

# Binary Multiplication

Binary multiplication is simpler than decimal multiplication because the multiplier contains only:

`0` and `1`

Multiplication by:

* `0` produces zero.
* `1` preserves the value.

Bit shifting can also be used to efficiently multiply binary integers by powers of two.

---

# Binary Division

Binary division follows principles similar to long division in decimal.

It can be understood through repeated comparison, subtraction, and shifting.

Division by powers of two can often be implemented efficiently using right shifts for appropriate unsigned integer operations.

---

# Signed Versus Unsigned Interpretation

The same binary bit pattern can represent different values depending on interpretation.

For example, in 8 bits:

`11111111`

as unsigned means:

`255`

The same bit pattern under two's complement signed interpretation means:

`-1`

Therefore, understanding the data type is essential when interpreting binary data.

---

# Integer Representation and Programming

Programming languages provide different integer types and representations.

Common integer widths include:

* 8-bit
* 16-bit
* 32-bit
* 64-bit

The actual behavior depends on the programming language and implementation.

Some languages provide fixed-width integer types directly, while others provide integer types with different rules.

Understanding the underlying number system helps explain:

* Integer ranges
* Overflow
* Bitwise operations
* Memory usage
* Type conversion
* Signedness

---

# Number Systems in Python

Python provides built-in support for working with different number systems.

Numbers can be represented using:

* Decimal notation
* Binary notation
* Octal notation
* Hexadecimal notation

Python also provides facilities for converting between bases.

Python integers have arbitrary precision, meaning that Python integers can grow beyond the fixed-width limits commonly associated with languages using fixed-size integer types.

This is an important distinction between mathematical integers in Python and fixed-width machine integers.

---

# Arbitrary Precision

In many programming languages, an integer type has a fixed number of bits.

For example, a 32-bit integer has a fixed range.

Python integers are different because their size can grow as required, subject to available memory.

This means Python can represent very large integers without ordinary fixed-width integer overflow in the same way as a typical 32-bit or 64-bit integer.

---

# Number Representation and Precision

Integers are generally easier to represent exactly than floating-point fractions.

A finite binary integer can be represented exactly as long as sufficient storage is available.

Many decimal fractions cannot be represented exactly in binary floating-point.

This distinction is important when performing numerical calculations.

---

# Exact Integer Arithmetic

Integer arithmetic can be exact when the representation supports the required values.

For example, an integer such as:

`100`

has an exact binary representation.

The challenge arises when the value exceeds the available range or when fractional values are introduced using limited-precision representations.

---

# Representation of Zero

Zero has special importance in number systems.

In ordinary positional notation, zero has one mathematical value.

Some historical signed representations, such as sign-magnitude and one's complement, can produce two different bit patterns representing zero.

Two's complement avoids this problem by using a single representation for zero.

---

# Base and Number of Digits

The base determines how many symbols are available.

For example:

* Base 2 → 2 symbols
* Base 8 → 8 symbols
* Base 10 → 10 symbols
* Base 16 → 16 symbols

Increasing the base allows a number to be represented using fewer digits.

This is why hexadecimal representations are shorter than binary representations of the same value.

---

# Binary Grouping

Binary values can be grouped for easier human interpretation.

Groups of:

* 3 bits correspond naturally to octal digits.
* 4 bits correspond naturally to hexadecimal digits.
* 8 bits correspond to a byte.

Grouping does not change the value.

It simply provides a more convenient way of reading the same bit pattern.

---

# Leading Zeros and Fixed Width

Leading zeros become important when discussing fixed-width data.

For example, the value 5 can be written as:

`101`

or as an 8-bit value:

`00000101`

Both represent 5, but the second representation explicitly shows that the value occupies eight bit positions.

Fixed-width representations are important in:

* CPU registers
* Memory
* Network protocols
* Binary files
* Cryptography
* Embedded systems

---

# Negative Numbers

Negative numbers require a representation scheme because binary digits themselves only contain zero and one.

Common historical and modern approaches include:

* Sign-magnitude
* One's complement
* Two's complement

Two's complement is the most important representation to understand for modern signed integer systems.

---

# Overflow in Signed Numbers

Signed integers have limited ranges.

For an `n`-bit two's complement integer:

`Minimum = -2ⁿ⁻¹`

`Maximum = 2ⁿ⁻¹ - 1`

For 8 bits:

`-128 to 127`

If an operation exceeds this range, signed overflow can occur.

The exact behavior of signed overflow depends on the programming language and execution environment.

---

# Number Systems and Digital Electronics

Digital circuits fundamentally work with binary states.

Logic gates operate on binary inputs and produce binary outputs.

Common logic gates include:

* AND
* OR
* NOT
* XOR
* NAND
* NOR
* XNOR

These operations form the foundation of digital computing.

Number systems therefore connect mathematical notation with physical computer hardware.

---

# Number Systems and Computer Storage

Data stored in a computer ultimately consists of bits.

Those bits can represent:

* Numbers
* Characters
* Instructions
* Images
* Audio
* Video
* Addresses
* Metadata
* Flags

The interpretation depends on the format being used.

This is why understanding number systems is fundamental to understanding data representation.

---

# Common Mistakes

Several mistakes frequently occur when working with number systems.

### Using invalid digits

A binary number cannot contain digits other than `0` and `1`.

An octal number cannot contain `8` or `9`.

A hexadecimal number can contain `0–9` and `A–F`.

### Forgetting positional values

A digit's value depends on its position.

### Reading binary digits in the wrong direction

Binary-to-decimal conversion starts with the rightmost digit at position zero.

### Confusing representation with value

`1010₂`, `12₈`, `10₁₀`, and `A₁₆` represent the same mathematical value.

### Ignoring fixed width

Signed and unsigned interpretations depend heavily on the number of bits available.

### Confusing decimal and binary memory units

KB and KiB are not necessarily the same quantity.

---

# Important Number-System Relationships

Several relationships are particularly useful:

`2³ = 8`

Therefore:

`3 binary bits = 1 octal digit`

And:

`2⁴ = 16`

Therefore:

`4 binary bits = 1 hexadecimal digit`

Also:

`2⁸ = 256`

Therefore:

`8 bits = 256 possible bit patterns`

These relationships make binary, octal, and hexadecimal conversions especially efficient.

---

# General Base Arithmetic

The rules of positional arithmetic remain consistent across different bases.

In base 10, digits roll over after 9.

In base 2, digits roll over after 1.

In base 8, digits roll over after 7.

In base 16, digits roll over after F.

The principle is the same:

> When a digit reaches the base, it resets to zero and carries one to the next position.

---

# Non-Positional Number Systems

Not every number system is positional.

Roman numerals are an example of a system that does not operate in the same positional manner as binary or decimal.

Modern computing relies heavily on positional systems because they provide efficient mathematical representation and arithmetic.

---

# Fundamental Terminology

Important terminology includes:

* **Bit**: A binary digit containing 0 or 1.
* **Byte**: Normally 8 bits.
* **Base**: The number of symbols used in a positional number system.
* **Radix**: Another name for base.
* **Digit**: A symbol used to represent a value.
* **MSB**: Most Significant Bit.
* **LSB**: Least Significant Bit.
* **Overflow**: A result exceeding the available representation range.
* **Unsigned**: A representation containing only non-negative values.
* **Signed**: A representation capable of representing negative and positive values.
* **Two's complement**: A standard signed integer representation.
* **Hexadecimal**: Base-16 representation.
* **Octal**: Base-8 representation.
* **Binary**: Base-2 representation.
* **Decimal**: Base-10 representation.
* **Radix point**: The separator between integer and fractional portions.

---

# Core Formulas

### Positional representation

For base `b`:

`Value = Σ(dᵢ × bⁱ)`

### Unsigned n-bit range

`0 to 2ⁿ - 1`

### Number of possible n-bit patterns

`2ⁿ`

### Two's complement n-bit range

`-2ⁿ⁻¹ to 2ⁿ⁻¹ - 1`

### Minimum bits for a positive integer

`floor(log₂(N)) + 1`

for `N > 0`.

---

# Conceptual Distinctions

Several concepts should not be confused.

### Number versus representation

A number is a mathematical value.

A representation is a way of writing or storing that value.

### Binary versus bit pattern

Binary is a number system.

A bit pattern is a sequence of bits that may be interpreted in many ways.

### Hexadecimal versus storage

Hexadecimal is primarily a notation.

It does not mean that computers physically store values as hexadecimal digits.

### Signed versus unsigned

Signedness determines how a binary pattern is interpreted.

### Integer versus floating point

Integers represent whole numbers.

Floating-point formats represent a much wider range of values, including fractions, using a different representation scheme.

---

# Practical Importance of Number Systems

Number systems are not merely theoretical mathematical concepts.

They are directly involved in:

* Programming
* Data structures
* Algorithms
* Computer architecture
* Operating systems
* Digital electronics
* Networking
* Cryptography
* Cybersecurity
* Databases
* Embedded systems
* Memory management
* File formats
* Machine learning systems
* Graphics
* Digital communication

A strong understanding of number systems makes many lower-level computer concepts easier to understand.

---

# Complete Representation Analysis

When examining a number, it is useful to ask:

1. What base is being used?
2. What digits are valid in that base?
3. What does each position represent?
4. Is the value signed or unsigned?
5. How many bits are available?
6. Is the representation fixed-width?
7. Is the value an integer or a fraction?
8. Is the value being stored or merely displayed?
9. Could overflow occur?
10. Does the bit pattern have another possible interpretation?

These questions provide a systematic way to analyze numerical representations.

---

# Number Systems as a Foundation of Computing

At a high level, number systems provide the connection between mathematical values and computer representation.

Humans commonly work with decimal numbers.

Computers operate fundamentally using binary states.

Octal and hexadecimal provide compact ways for humans to work with binary information.

Signed representations explain how negative numbers can be stored.

Two's complement explains modern signed integer representation.

Bitwise operations explain how individual binary positions can be manipulated.

Floating-point representation explains how computers handle fractional values and extremely large or small magnitudes.

Together, these concepts form the foundation for understanding how numerical information is represented and processed inside computing systems.

