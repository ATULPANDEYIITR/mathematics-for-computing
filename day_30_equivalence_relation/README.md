# Equivalence Relations, Equivalence Classes, Partitions, and Quotient Structures

## Scope

An equivalence relation is a relation that divides a set into groups of elements that are indistinguishable with respect to a particular criterion. The three defining properties are reflexivity, symmetry, and transitivity.

For a set \(S\), an equivalence relation \(R\) satisfies:

- Reflexivity: \(xRx\) for every \(x \in S\).
- Symmetry: if \(xRy\), then \(yRx\).
- Transitivity: if \(xRy\) and \(yRz\), then \(xRz\).

These properties are not independent implementation details. Together they guarantee that every element belongs to exactly one equivalence class and that the collection of equivalence classes forms a partition of the original set.

This project treats four closely connected structures as distinct concepts:

- **Equivalence relations** define when two elements should be regarded as equivalent.
- **Equivalence classes** collect all elements equivalent to a selected element.
- **Partitions** describe the resulting disjoint grouping of an entire set.
- **Quotient structures** replace individual elements with their equivalence classes and support operations on those classes when those operations are well-defined.

The Python, JavaScript, and C++ implementations approach these ideas from different technical perspectives rather than reproducing the same program in three languages.

## Core Mathematical Structure

Let \(S\) be a set and let \(R\) be an equivalence relation on \(S\).

The equivalence class of \(x\) is

\[
[x] = \{y \in S \mid xRy\}.
\]

If \(xRy\), then

\[
[x] = [y].
\]

If \(x\) and \(y\) are not equivalent, then their classes are disjoint:

\[
[x] \cap [y] = \varnothing.
\]

Therefore the equivalence classes cover \(S\) without overlapping. The set of all classes is called the quotient set:

\[
S/R = \{[x] \mid x \in S\}.
\]

The notation is important. An element of \(S/R\) is not normally an individual representative such as `2`; it is an entire equivalence class such as \([2]\).

## Equivalence Relations

### Reflexivity

Reflexivity requires every element to be related to itself.

For modular congruence,

\[
x \equiv x \pmod n
\]

because \(n\) divides \(x-x=0\).

In the Python implementation, `is_reflexive()` evaluates the relation against every pair `(x, x)`. The C++ and JavaScript implementations use the same mathematical test but expose it through their respective class designs.

A relation that fails reflexivity cannot produce the standard equivalence-class partition.

### Symmetry

Symmetry means that the direction of the relationship does not matter:

\[
xRy \Rightarrow yRx.
\]

Congruence modulo \(n\) is symmetric because if \(n\mid(x-y)\), then \(n\mid(y-x)\).

The implementations explicitly check both directions. This prevents a directional relation such as strict ordering from being incorrectly treated as an equivalence relation.

### Transitivity

Transitivity connects chains of equivalence:

\[
xRy \land yRz \Rightarrow xRz.
\]

For congruence modulo \(n\), if

\[
x \equiv y \pmod n
\]

and

\[
y \equiv z \pmod n,
\]

then \(n\) divides both \(x-y\) and \(y-z\). Consequently it also divides

\[
(x-y)+(y-z)=x-z,
\]

so \(x \equiv z \pmod n\).

Transitivity is what prevents an element from being connected to two incompatible groups.

## A Concrete Equivalence Relation: Congruence Modulo \(n\)

The relation

\[
x \equiv y \pmod n
\]

means that \(x-y\) is divisible by \(n\).

For \(n=4\), integers fall into four classes:

\[
[0]_4,\ [1]_4,\ [2]_4,\ [3]_4.
\]

For example,

\[
[1]_4 = \{\ldots,-7,-3,1,5,9,13,\ldots\}.
\]

The integers in the class have different ordinary values but identical remainders after division by four.

The Python and JavaScript programs restrict the displayed domain so that the classes can be inspected directly. The C++ program performs the same finite verification and then uses the modulo construction as the basis for a quotient-algebra example.

## Equivalence Classes

An equivalence class contains every element related to a selected representative.

The term **representative** needs careful interpretation. If \(x \in [a]\), then \(x\) can represent the class \([a]\), but the class itself is the complete set of equivalent elements.

For example, modulo five,

\[
[2] = [7] = [-3].
\]

The values `2`, `7`, and `-3` are representatives of the same class. They are not three different quotient elements.

This distinction matters when implementing quotient structures. A program that stores only one representative is using a representation of the class, not changing the mathematical definition of the class.

## Partitions

A partition of a set \(S\) is a collection of nonempty subsets satisfying two conditions:

- Every element of \(S\) belongs to a block.
- Distinct blocks are disjoint.

For example, a partition of

\[
S=\{1,2,3,4,5,6,7,8,9\}
\]

can be

\[
\{\{1,4,7\},\{2,5,8\},\{3,6,9\}\}.
\]

The Python `validate_partition()` function checks nonempty blocks, membership inside the universe, pairwise disjointness, and complete coverage.

The JavaScript implementation performs the same validation with `Set` objects. The C++ implementation uses `std::set`, allowing the universe and blocks to be compared directly.

A collection containing an overlapping block is not a partition. A collection that omits an element is also not a partition.

## From a Partition Back to an Equivalence Relation

The relationship between equivalence relations and partitions works in both directions.

Given a partition \(P\) of \(S\), define

\[
xRy
\]

when \(x\) and \(y\) belong to the same block of \(P\).

The resulting relation is automatically reflexive because every element occurs in a block. It is symmetric because membership in the same block has no direction. It is transitive because if \(x\) and \(y\) are in one block and \(y\) and \(z\) are in one block, the disjoint-block condition forces the relevant blocks to be the same.

The implementations explicitly construct such a relation from a partition.

This gives the fundamental correspondence:

\[
\text{equivalence relations on }S
\longleftrightarrow
\text{partitions of }S.
\]

The relation is the criterion for grouping, while the partition is the grouping produced by that criterion.

## Quotient Sets

The quotient set

\[
S/R
\]

contains the equivalence classes of \(R\).

For the integers modulo \(n\),

\[
\mathbb Z/n\mathbb Z
\]

contains \(n\) distinct residue classes:

\[
[0],[1],\ldots,[n-1].
\]

Although the original integer set is infinite, the quotient has only \(n\) elements.

This is a major purpose of quotient constructions: many distinct representations can be collapsed into a smaller structure while preserving the relationship that matters.

The Python implementation demonstrates this using product categories. Individual products are grouped by category, so the quotient contains logical category classes instead of individual product records.

The JavaScript implementation builds a `QuotientSet` object whose `blocks` property contains the classes produced by the underlying equivalence relation.

The C++ case study applies the same idea to customer records. Multiple records from CRM, billing, and support systems can correspond to one logical customer when they share the same normalized identity key.

## Quotient Structures Versus Quotient Sets

A quotient set only requires a valid equivalence relation.

A quotient **structure** requires more. If an operation is defined on representatives, that operation must give the same quotient result regardless of which representatives are selected.

For modular arithmetic,

\[
[a]+[b]=[a+b]
\]

and

\[
[a][b]=[ab].
\]

Suppose

\[
a\equiv a' \pmod n
\]

and

\[
b\equiv b' \pmod n.
\]

Then

\[
a+b\equiv a'+b' \pmod n
\]

and

\[
ab\equiv a'b' \pmod n.
\]

Therefore addition and multiplication do not depend on the chosen representatives.

This property is called **well-definedness**.

The `ResidueClass` implementation in C++ and the `ResidueClass` implementation in JavaScript normalize values to canonical residues while preserving the quotient interpretation. They also reject operations between different moduli because those values belong to different quotient structures.

## The Python Implementation

The Python program is designed as a finite mathematical laboratory for equivalence relations.

The `EquivalenceRelation` class stores a finite domain and a relation predicate. Its verification methods directly test reflexivity, symmetry, and transitivity. `equivalence_class()` calculates the class associated with a selected element, while `classes()` constructs the complete partition only after verifying that the relation is an equivalence relation.

The `relation_from_key()` helper demonstrates a useful general construction:

\[
xRy \iff f(x)=f(y).
\]

Equality of the key values automatically supplies an equivalence relation. The program uses this to group employee records by department and product records by category.

The partition validation logic checks the mathematical definition rather than merely trusting input. This is important in software systems where partition data may arrive from a file, database, or external service.

The program also includes a disjoint-set union implementation. This provides a different computational perspective: instead of repeatedly scanning every pair of elements, equivalence classes can be maintained incrementally as relationships are discovered.

The final quotient-map example demonstrates

\[
q:\mathbb Z\rightarrow\mathbb Z/3\mathbb Z
\]

where each integer is mapped to its residue class.

## The JavaScript Implementation

The JavaScript program focuses on object-oriented and event-driven representations of the same mathematical structures.

`EquivalenceRelation` provides relation verification and class construction. JavaScript `Set` is appropriate for representing classes because a class is a collection in which duplicate membership has no meaning.

`QuotientSet` treats equivalence classes as the elements of a new mathematical structure. Its `elements()` generator demonstrates lazy iteration over quotient elements rather than materializing another transformed array each time the quotient is inspected.

The `ResidueClass` class provides an explicit representation of an element of \(\mathbb Z/n\mathbb Z\). Its constructor normalizes negative values, so values such as `-3` and `2` represent the same residue modulo five.

The event-driven portion uses `RelationEventStream` and `IncrementalPartition`. New equivalences can be emitted as events, and the disjoint-set structure updates the current partition. This is useful as a software model for systems where relationships arrive incrementally.

The asynchronous validation function illustrates that mathematical validation can occur at an application boundary without changing the underlying mathematical definition.

## The C++ Case Study

The C++ program models a repository-like data integration problem in which multiple systems contain records representing the same logical customer.

Each `CustomerRecord` contains a source system, an external identifier, and a normalized identity key. Records with the same normalized key form one equivalence class.

The `IdentityQuotient` class constructs a quotient representation using a `std::map` from identity keys to sets of record identifiers. This makes the distinction between physical records and logical identities explicit.

The scenario illustrates why quotient structures are useful in systems engineering. The original set contains multiple representations, while the quotient identifies which distinctions can be safely ignored under the chosen equivalence criterion.

The criterion must still be justified by the application. If two records merely share a weak or unreliable attribute, treating them as equivalent can collapse distinct entities incorrectly. The mathematical structure can prove consistency of the chosen relation, but it cannot determine whether the domain-specific criterion is appropriate.

## Incremental Equivalence Classes

The C++ and JavaScript implementations include disjoint-set union, also called union-find.

The structure maintains a collection of disjoint sets and supports two fundamental operations:

- `find(x)` identifies the current representative of the class containing `x`.
- `union(x, y)` merges the classes containing `x` and `y`.

Path compression changes parent pointers during `find`, shortening future lookup paths. Union by rank prevents unnecessary growth of the internal trees.

For \(m\) operations on \(n\) elements, the standard amortized complexity is commonly expressed using the inverse Ackermann function:

\[
O(m\alpha(n)).
\]

For practical input sizes, this is extremely close to linear behavior.

Union-find is appropriate when equivalence relationships are discovered through merge events. It is not a general replacement for a relation predicate when the application needs arbitrary pairwise relation queries based on rich rules.

## Common Failure Modes

A relation defined by strict ordering, such as

\[
x<y,
\]

is not an equivalence relation. It is not reflexive because \(x<x\) is false, and it is not symmetric.

The relation “has different parity” is also not an equivalence relation. If \(x\) is even, then \(x\) is not related to itself under that definition, so reflexivity fails.

A proposed partition can fail because a block is empty, two blocks overlap, an element belongs to no block, or a block contains an element outside the declared universe.

A quotient operation can fail to be well-defined even when the underlying equivalence relation is valid. An operation defined on representatives must respect the equivalence relation before it can safely be transferred to quotient classes.

These failure modes are different. Relation validation checks the properties of \(R\), partition validation checks the structure of the blocks, and well-definedness checks whether an operation survives the identification of equivalent elements.

## Common Implementation Mistakes

### Confusing a Representative with a Class

Storing `2` as a convenient representative of \([2]\) modulo five does not mean that the quotient element mathematically equals the integer `2`.

The representation is a programming choice. The mathematical object remains the equivalence class.

### Constructing Classes Before Validating the Relation

For an arbitrary relation, the set of elements related to a selected element does not necessarily behave like an equivalence class. Without reflexivity, symmetry, and transitivity, the resulting groups can overlap or fail to cover the domain.

The Python, JavaScript, and C++ implementations therefore validate the relation before treating its classes as a partition.

### Ignoring Canonicalization

Canonical representatives are convenient because equivalent objects can then share a stable stored form.

For residue classes modulo five, values can be normalized to the range

\[
0,\ldots,4.
\]

Canonicalization is useful for storage and comparison, but it should not be confused with the mathematical definition of the quotient.

### Defining Operations Without Checking Well-Definedness

Suppose a quotient identifies several representatives as one element. An operation cannot automatically be copied from representatives to quotient elements.

For a definition such as

\[
[a]\star[b]=[a\star b],
\]

the result must remain unchanged if \(a\) is replaced by an equivalent representative or \(b\) is replaced by an equivalent representative.

This is why modular addition and multiplication work naturally on residue classes.

## Computational Complexity

Direct verification of an arbitrary finite relation can be expensive.

If a domain contains \(n\) elements, checking reflexivity requires up to \(n\) relation evaluations. Checking symmetry may require \(O(n^2)\) evaluations. A straightforward transitivity check can require \(O(n^3)\) evaluations.

This cubic behavior appears in the teaching implementations because it makes the mathematical definition explicit.

Production systems usually exploit additional structure. A relation represented by a key function can construct classes using hashing or ordered maps. Disjoint-set union can maintain dynamically merged equivalence classes without repeatedly checking all triples.

The appropriate representation therefore depends on whether the application begins with:

- an arbitrary relation predicate,
- an explicit partition,
- a classification key,
- or a stream of pairwise equivalence declarations.

## Practical Applications

Equivalence relations appear whenever a system intentionally ignores some distinctions.

Examples include:

- Congruence modulo \(n\), where integers with the same remainder are identified.
- Employee grouping by department, where employee identity is retained inside a class but department membership determines equivalence.
- Product grouping by category, where individual products are collapsed into category-level quotient elements.
- Customer identity resolution, where records from different systems are grouped under a common normalized identity key.
- Graph connectivity, where vertices connected through undirected paths form connected components. The connectivity relation is an equivalence relation on the vertex set.
- String normalization, when a carefully defined normalization rule determines that different representations should be treated as equivalent.
- State minimization, where states are grouped when they are indistinguishable under the relevant behavioral criterion.

In each application, the key question is not simply whether grouping is convenient. The equivalence criterion must actually satisfy the properties required by the intended model.

## Security and Data Integrity Considerations

An equivalence relation can be mathematically correct and still encode an unsafe application rule.

For identity resolution, an overly broad key can incorrectly merge distinct users. Once records are placed in the same equivalence class, downstream systems may treat them as one entity.

Normalization rules should therefore be explicit and deterministic. Case folding, whitespace handling, Unicode normalization, identifier parsing, and missing values can all affect the equivalence criterion.

Input validation is especially important when partition data is accepted from outside the application. Overlapping blocks, missing elements, and malformed identifiers should not silently produce a quotient structure.

Canonical representations should also be validated before they become persistent identifiers. A quotient implementation should not assume that a convenient representative is authoritative merely because it is easy to store.

## Design Relationship Between the Four Structures

The complete workflow can be expressed as:

`set + relation -> equivalence classes -> partition -> quotient set`

A relation supplies the rule.

The classes are the groups induced by that rule.

The partition is the complete family of those groups.

The quotient set treats each group as a single mathematical element.

When an operation respects the equivalence relation, the quotient can inherit that operation and become a richer quotient structure such as a quotient group, quotient ring, or related algebraic construction.

The central distinction is therefore:

\[
\boxed{
\text{relation defines identification}
\rightarrow
\text{classes record identification}
\rightarrow
\text{partition organizes identification}
\rightarrow
\text{quotient performs computation after identification}
}
\]

The implementations deliberately preserve these distinctions rather than using the four terms as interchangeable labels.
