# Fractions, Ratios and Proportions

## Overview

Fractions, ratios and proportions are fundamental mathematical concepts used to describe parts of a whole, compare quantities, establish relationships between quantities, scale values, calculate rates and express relative changes.

These concepts are closely connected:

- Fractions describe parts of a whole.
- Decimals provide another numerical representation of fractions.
- Percentages express quantities per hundred.
- Ratios compare quantities.
- Proportions state that two ratios are equivalent.
- Scaling changes quantities while preserving relationships.
- Rates compare quantities that usually have different units.

These concepts appear throughout mathematics, statistics, data analysis, finance, economics, engineering, science, business analytics, Excel and Python programming.

---

## 1. Fractions

A fraction represents a part of a whole.

A fraction has two primary components:

```text
    numerator
       3
      ---
       5
    denominator
````

For `3/5`:

* `3` is the numerator.
* `5` is the denominator.
* The denominator tells us how many equal parts the whole is divided into.
* The numerator tells us how many of those parts are being considered.

Therefore:

```text
3/5 = 3 parts out of 5 equal parts
```

The denominator cannot be zero because division by zero is undefined.

---

## 2. Types of fractions

### Proper fraction

A proper fraction has a numerator smaller than its denominator.

Examples:

```text
1/2
3/5
7/10
```

The value of a proper fraction is less than 1.

### Improper fraction

An improper fraction has a numerator greater than or equal to its denominator.

Examples:

```text
5/3
7/4
10/5
```

An improper fraction can be greater than or equal to 1.

### Mixed number

A mixed number contains a whole number and a proper fraction.

Example:

```text
2 1/3
```

This means:

```text
2 + 1/3
```

### Unit fraction

A unit fraction has numerator equal to 1.

Examples:

```text
1/2
1/5
1/10
1/100
```

---

## 3. Equivalent fractions

Equivalent fractions have the same mathematical value.

For example:

```text
1/2 = 2/4 = 3/6 = 4/8 = 50/100
```

Multiplying the numerator and denominator by the same non-zero number produces an equivalent fraction.

For example:

```text
1/2 × 2/2 = 2/4
```

The value does not change because:

```text
2/2 = 1
```

---

## 4. Simplifying fractions

A fraction is simplified by dividing the numerator and denominator by their greatest common divisor.

Example:

```text
8/12
```

The greatest common divisor of 8 and 12 is 4.

Therefore:

```text
8/4 = 2
12/4 = 3
```

So:

```text
8/12 = 2/3
```

In Python, the `Fraction` class automatically reduces fractions to their simplest form.

```python
from fractions import Fraction

value = Fraction(8, 12)

print(value)
```

Output:

```text
2/3
```

---

## 5. Fraction arithmetic

Fractions support the standard arithmetic operations.

For:

```text
a = 3/5
b = 7/10
```

we can calculate:

```text
a + b
a - b
a * b
a / b
```

Python can perform exact rational arithmetic using `Fraction`.

```python
from fractions import Fraction

a = Fraction(3, 5)
b = Fraction(7, 10)

print(a + b)
print(a - b)
print(a * b)
print(a / b)
```

This is preferable to floating-point arithmetic when exact rational representation is important.

---

## 6. Comparing fractions

Fractions can be compared mathematically.

For example:

```text
3/4 > 5/8
```

Python can perform this comparison directly when using `Fraction`.

```python
from fractions import Fraction

a = Fraction(3, 4)
b = Fraction(5, 8)

print(a > b)
```

Output:

```text
True
```

---

## 7. Fractions and decimals

A fraction can be converted into a decimal by dividing the numerator by the denominator.

For example:

```text
3/8 = 0.375
```

The general formula is:

```text
decimal = numerator / denominator
```

Python:

```python
numerator = 3
denominator = 8

decimal_value = numerator / denominator

print(decimal_value)
```

Output:

```text
0.375
```

---

## 8. Decimals and fractions

Decimals can also be converted to fractions.

Examples:

```text
0.5 = 1/2
0.25 = 1/4
0.75 = 3/4
0.125 = 1/8
```

Python can use `Fraction`:

```python
from fractions import Fraction
from decimal import Decimal

value = Decimal("0.75")

fraction = Fraction(value)

print(fraction)
```

Output:

```text
3/4
```

Using `Decimal("0.75")` rather than `Decimal(0.75)` helps avoid introducing binary floating-point representation issues into the Decimal value.

---

## 9. Percentages

Percentage means "per hundred".

Therefore:

```text
x% = x/100
```

Examples:

```text
10% = 10/100 = 1/10
25% = 25/100 = 1/4
50% = 50/100 = 1/2
75% = 75/100 = 3/4
100% = 100/100 = 1
```

Percentages are therefore closely related to fractions.

---

## 10. Fraction to percentage

To convert a fraction into a percentage:

```text
percentage = fraction × 100
```

Example:

```text
3/4 = 0.75

0.75 × 100 = 75%
```

Therefore:

```text
3/4 = 75%
```

Python:

```python
from fractions import Fraction

value = Fraction(3, 4)

percentage = value * 100

print(percentage)
```

---

## 11. Percentage to fraction

To convert a percentage into a fraction:

```text
percentage / 100
```

Example:

```text
25% = 25/100 = 1/4
```

Python:

```python
from fractions import Fraction

value = Fraction(25, 100)

print(value)
```

Output:

```text
1/4
```

---

## 12. Decimal to percentage

Multiply the decimal by 100.

```text
0.625 × 100 = 62.5%
```

Python:

```python
decimal_value = 0.625

percentage = decimal_value * 100

print(percentage)
```

Output:

```text
62.5
```

---

## 13. Percentage to decimal

Divide the percentage by 100.

```text
62.5% = 62.5/100 = 0.625
```

Python:

```python
percentage = 62.5

decimal_value = percentage / 100

print(decimal_value)
```

---

## 14. Finding a percentage of a number

To calculate `p%` of a number:

```text
result = p/100 × number
```

Example:

```text
20% of 500

= 20/100 × 500

= 100
```

Python:

```python
percentage = 20
number = 500

result = percentage / 100 * number

print(result)
```

---

## 15. Finding what percentage one number is of another

The formula is:

```text
percentage = part / whole × 100
```

Example:

```text
30 out of 120

= 30/120 × 100

= 25%
```

Python:

```python
part = 30
whole = 120

percentage = part / whole * 100

print(percentage)
```

---

## 16. Percentage increase

Percentage increase measures how much a value increased relative to its original value.

Formula:

```text
percentage increase =
(new value - original value) / original value × 100
```

Example:

```text
Original = 100
New = 120

Increase = 20

Percentage increase = 20/100 × 100
                   = 20%
```

Python:

```python
original = 100
new = 120

percentage_increase = (new - original) / original * 100

print(percentage_increase)
```

---

## 17. Percentage decrease

Percentage decrease is:

```text
percentage decrease =
(original value - new value) / original value × 100
```

Example:

```text
Original = 500
New = 425

Decrease = 75

Percentage decrease =
75/500 × 100
= 15%
```

---

## 18. Applying a percentage increase

To increase a value by a percentage:

```text
new value = original × (1 + percentage/100)
```

Example:

```text
₹1,000 increased by 15%

= 1000 × 1.15
= ₹1,150
```

Python:

```python
original = 1000
increase = 15

new_value = original * (1 + increase / 100)

print(new_value)
```

---

## 19. Applying a percentage decrease

To decrease a value:

```text
new value = original × (1 - percentage/100)
```

Example:

```text
₹1,000 decreased by 15%

= 1000 × 0.85
= ₹850
```

---

## 20. Percentage points vs percentage change

This distinction is extremely important in analytics.

Suppose a rate changes from:

```text
40% → 50%
```

The change in percentage points is:

```text
50% - 40% = 10 percentage points
```

But the relative percentage increase is:

```text
(50 - 40) / 40 × 100
= 25%
```

Therefore:

```text
10 percentage points
```

and

```text
25% relative increase
```

are two different concepts.

---

## 21. Base effect

Percentages always depend on a base.

A ₹100 increase means:

```text
100% increase on ₹100
10% increase on ₹1,000
1% increase on ₹10,000
```

Therefore, whenever a percentage is calculated, ask:

> Percentage of what base?

This is one of the most important habits in quantitative reasoning.

---

## 22. Compound percentage changes

Multiple percentage changes must be applied sequentially.

Suppose a value increases by 20% and then decreases by 20%.

Start:

```text
100
```

After 20% increase:

```text
100 × 1.20 = 120
```

After 20% decrease:

```text
120 × 0.80 = 96
```

Final value:

```text
96
```

It does not return to 100.

This happens because the second 20% is calculated using 120 as the base.

For multiple percentage changes:

```text
Final =
Initial × (1 + r1) × (1 + r2) × ...
```

where increases are positive and decreases are negative.

---

## 23. Reverse percentage calculations

Suppose an item costs ₹800 after a 20% discount.

The final price is:

```text
Original × 0.80 = 800
```

Therefore:

```text
Original = 800 / 0.80
         = ₹1,000
```

The reverse formula is:

```text
original = final / (1 - discount/100)
```

This technique is useful when the final value and percentage change are known but the original value is unknown.

---

## 24. Ratios

A ratio compares two or more quantities.

Example:

```text
2 : 3
```

This means that for every 2 units of the first quantity, there are 3 units of the second quantity.

Ratios can represent:

```text
part : part
part : whole
quantity : quantity
distance : time
cost : quantity
```

---

## 25. Part-to-part ratio

Suppose:

```text
Red balls = 2
Blue balls = 3
```

The part-to-part ratio is:

```text
Red : Blue = 2 : 3
```

The ratio compares red objects directly with blue objects.

---

## 26. Part-to-whole ratio

The total number of balls is:

```text
2 + 3 = 5
```

Therefore:

```text
Red : Total = 2 : 5

Blue : Total = 3 : 5
```

This distinction is important.

`2:3` is a part-to-part ratio.

`2:5` is the red part-to-whole relationship.

---

## 27. Simplifying ratios

Ratios can be simplified using the greatest common divisor.

Example:

```text
20 : 30
```

The GCD is 10.

Divide both terms by 10:

```text
20/10 : 30/10

= 2 : 3
```

Python:

```python
from math import gcd

a = 20
b = 30

common = gcd(a, b)

print(a // common, b // common)
```

---

## 28. Equivalent ratios

Equivalent ratios preserve the same relationship.

For example:

```text
2 : 3
4 : 6
6 : 9
20 : 30
```

All represent the same ratio.

Both terms are multiplied by the same factor.

---

## 29. Ratio as a fraction

A ratio:

```text
2 : 5
```

can be interpreted as:

```text
2/5
```

when determining what proportion the first quantity represents of the total.

Therefore:

```text
2/5 = 0.4 = 40%
```

The ratio itself is `2:5`, while the corresponding proportion of the total is `2/5`.

---

## 30. Proportions

A proportion states that two ratios are equal.

Example:

```text
2/3 = 4/6
```

or:

```text
2 : 3 = 4 : 6
```

Because:

```text
2 × 6 = 12
3 × 4 = 12
```

the proportion is valid.

---

## 31. Cross multiplication

For:

```text
a/b = c/d
```

cross multiplication gives:

```text
a × d = b × c
```

This is useful for testing proportions and solving unknown values.

Example:

```text
3/5 = x/20
```

Cross multiplication:

```text
3 × 20 = 5 × x

60 = 5x

x = 12
```

---

## 32. Direct proportion

Two quantities are directly proportional when one increases or decreases in the same proportional relationship as the other.

Mathematically:

```text
y ∝ x
```

or:

```text
y = kx
```

where `k` is the constant of proportionality.

Example:

If one notebook costs ₹20:

```text
1 notebook = ₹20
2 notebooks = ₹40
3 notebooks = ₹60
5 notebooks = ₹100
```

The cost is directly proportional to the number of notebooks.

---

## 33. Constant of proportionality

For direct proportion:

```text
y = kx
```

Therefore:

```text
k = y/x
```

Example:

```text
x = 5
y = 40

k = 40/5
  = 8
```

Therefore:

```text
y = 8x
```

---

## 34. Inverse proportion

Two quantities are inversely proportional when one increases while the other decreases in such a way that their product remains constant.

Mathematically:

```text
y ∝ 1/x
```

or:

```text
y = k/x
```

Example:

If a fixed task requires:

```text
1 worker → 120 hours
2 workers → 60 hours
3 workers → 40 hours
4 workers → 30 hours
```

then:

```text
workers × time = constant
```

This is inverse proportionality.

---

## 35. Direct vs inverse proportion

### Direct proportion

```text
y = kx
```

As `x` increases, `y` increases.

Examples:

* Quantity and total cost at fixed unit price
* Distance and time at constant speed
* Production and number of identical machines under ideal assumptions

### Inverse proportion

```text
y = k/x
```

As `x` increases, `y` decreases.

Examples:

* Number of workers and completion time for a fixed workload
* Speed and travel time for a fixed distance

---

## 36. Scaling

Scaling means changing the size or quantity while preserving proportional relationships.

If the scale factor is `k`:

```text
new value = original value × k
```

Example:

```text
Original width = 10
Original height = 5
Scale factor = 2
```

New dimensions:

```text
Width = 20
Height = 10
```

The shape remains proportional.

---

## 37. Scale factor

The scale factor is:

```text
scale factor = new value / original value
```

Example:

```text
Original = 10
New = 25

Scale factor = 25/10
             = 2.5
```

A scale factor greater than 1 enlarges the quantity.

A scale factor between 0 and 1 reduces it.

---

## 38. Geometric scaling

Scaling has a particularly important effect on area and volume.

If the linear scale factor is `k`:

```text
Length scales by:
k

Area scales by:
k²

Volume scales by:
k³
```

For example, if the scale factor is 2:

```text
Length = 2×
Area = 4×
Volume = 8×
```

This is important in engineering, architecture, physics, computer graphics and scientific modeling.

---

## 39. Recipe scaling

Recipes are practical examples of proportional scaling.

Suppose a recipe for 4 people requires:

```text
Flour = 300 g
Sugar = 100 g
Milk = 200 ml
```

To prepare it for 10 people:

```text
Scale factor = 10/4
             = 2.5
```

Therefore:

```text
Flour = 300 × 2.5 = 750 g
Sugar = 100 × 2.5 = 250 g
Milk = 200 × 2.5 = 500 ml
```

---

## 40. Map scaling

Suppose:

```text
1 cm on map = 5 km in reality
```

Then:

```text
7 cm = 7 × 5
     = 35 km
```

Scale relationships are used in:

* Maps
* Architecture
* Engineering drawings
* CAD
* Geographic information systems
* Models
* Data visualization

---

## 41. Rates

A rate compares quantities that often have different units.

Examples:

```text
60 km/hour
₹80/kg
5 pages/minute
100 words/minute
₹500/day
```

The general idea is:

```text
rate = quantity / another quantity
```

---

## 42. Unit rates

A unit rate expresses the quantity corresponding to one unit.

Suppose:

```text
₹240 for 6 kg
```

Unit price:

```text
₹240 / 6 kg
= ₹40/kg
```

Unit rates allow fair comparison between products with different package sizes.

---

## 43. Comparing unit rates

Suppose:

```text
Product A:
₹300 for 5 kg

Product B:
₹420 for 7 kg
```

Unit rates:

```text
A = ₹300/5 = ₹60/kg

B = ₹420/7 = ₹60/kg
```

Both products have the same unit price.

This technique is frequently used in shopping, procurement, inventory analysis and business analytics.

---

## 44. Speed, distance and time

These three quantities are connected by:

```text
speed = distance / time
```

Therefore:

```text
distance = speed × time

time = distance / speed
```

Example:

```text
Distance = 150 km
Time = 3 hours

Speed = 150/3
      = 50 km/hour
```

---

## 45. Unit conversion

Rates often require unit conversion.

For example:

```text
60 km/hour
```

To convert to meters per second:

```text
60 km = 60,000 m
1 hour = 3,600 seconds
```

Therefore:

```text
60,000 / 3,600
= 16.6667 m/s
```

The conversion factor is:

```text
1 km/h = 5/18 m/s
```

---

## 46. Dimensional analysis

Dimensional analysis verifies that units are mathematically consistent.

Examples:

```text
distance / time = speed

km / hour = km/hour
```

Another example:

```text
₹/kg × kg = ₹
```

Dimensional analysis is useful for detecting incorrect formulas and unit mismatches.

---

## 47. Discount

A discount is a percentage reduction from the original price.

Formula:

```text
discount amount =
original price × discount percentage / 100
```

Final price:

```text
final price =
original price - discount amount
```

Example:

```text
Original price = ₹2,000
Discount = 20%

Discount = ₹400
Final price = ₹1,600
```

---

## 48. Tax

Tax can be calculated as:

```text
tax = price × tax rate / 100
```

Total price:

```text
total = price + tax
```

Example:

```text
Price = ₹1,000
Tax = 18%

Tax = ₹180
Total = ₹1,180
```

---

## 49. Profit and loss

Profit:

```text
profit = selling price - cost price
```

Profit percentage:

```text
profit percentage =
profit / cost price × 100
```

Loss:

```text
loss = cost price - selling price
```

Loss percentage:

```text
loss percentage =
loss / cost price × 100
```

The cost price is generally the base when calculating profit or loss percentage.

---

## 50. Ratio allocation

Suppose ₹10,000 must be divided in the ratio:

```text
2 : 3 : 5
```

Total ratio units:

```text
2 + 3 + 5 = 10
```

Value of one ratio unit:

```text
10,000 / 10 = 1,000
```

Therefore:

```text
2 units = ₹2,000
3 units = ₹3,000
5 units = ₹5,000
```

General formula:

```text
share = total × individual ratio / sum of ratios
```

Python:

```python
def allocate_by_ratio(total, ratios):
    ratio_sum = sum(ratios)

    return [
        total * ratio / ratio_sum
        for ratio in ratios
    ]
```

---

## 51. Ratio normalization

A ratio can be converted into proportions that sum to 1.

For:

```text
2 : 3 : 5
```

Total:

```text
10
```

Normalized values:

```text
2/10 = 0.2
3/10 = 0.3
5/10 = 0.5
```

Therefore:

```text
[0.2, 0.3, 0.5]
```

As percentages:

```text
[20%, 30%, 50%]
```

Normalization is widely used in:

* Statistics
* Probability
* Machine learning
* Portfolio allocation
* Resource allocation
* Data science

---

## 52. Weighted averages

Weighted averages are closely connected to proportions.

Formula:

```text
weighted average =
sum(value × weight) / sum(weights)
```

Example:

```text
Exam score = 80
Exam weight = 60%

Project score = 90
Project weight = 40%
```

Weighted score:

```text
80 × 0.60 + 90 × 0.40
= 48 + 36
= 84
```

Python:

```python
values = [80, 90]
weights = [0.60, 0.40]

weighted_average = (
    sum(value * weight for value, weight in zip(values, weights))
    / sum(weights)
)

print(weighted_average)
```

---

## 53. Probability connection

Probability is frequently represented as a fraction.

If there are 3 favorable outcomes among 10 equally likely outcomes:

```text
P(event) = 3/10
```

Decimal:

```text
0.3
```

Percentage:

```text
30%
```

Therefore:

```text
3/10 = 0.3 = 30%
```

Fractions, decimals and percentages are different representations of the same numerical relationship.

---

## 54. Population proportions

Suppose a population contains:

```text
1,000,000 people
```

and a group contains:

```text
275,000 people
```

The proportion is:

```text
275,000 / 1,000,000
= 0.275
```

Percentage:

```text
27.5%
```

This type of calculation is common in:

* Demographics
* Surveys
* Census analysis
* Statistics
* Market research

---

## 55. Sample proportions

Suppose:

```text
Survey respondents = 420
Selected option A = 168
```

Sample proportion:

```text
168 / 420
= 0.4
```

Percentage:

```text
40%
```

Sample proportions are fundamental in statistical analysis.

---

## 56. Rate of change

Rate of change measures how quickly one quantity changes relative to another.

A basic formula is:

```text
rate of change =
change in y / change in x
```

Example:

Revenue increases from ₹100,000 to ₹130,000 over 3 months.

Revenue change:

```text
₹130,000 - ₹100,000
= ₹30,000
```

Average rate of change:

```text
₹30,000 / 3
= ₹10,000 per month
```

---

## 57. CAGR

Compound Annual Growth Rate, or CAGR, measures the constant annualized growth rate that connects a beginning value to an ending value over a specified number of periods.

Formula:

```text
CAGR =
(Ending Value / Beginning Value)^(1/n) - 1
```

where `n` is the number of periods.

Example:

```text
Beginning value = 100
Ending value = 150
Periods = 5
```

Python:

```python
cagr = (150 / 100) ** (1 / 5) - 1

print(cagr * 100)
```

CAGR is widely used in:

* Business analysis
* Investment analysis
* Revenue analysis
* Market analysis
* Financial modeling

---

## 58. Floating-point precision

One advanced programming issue is floating-point precision.

For example:

```python
print(0.1 + 0.2)
```

may produce:

```text
0.30000000000000004
```

instead of:

```text
0.3
```

This occurs because binary floating-point representation cannot exactly represent many decimal fractions.

Therefore:

```python
0.1 + 0.2 == 0.3
```

can evaluate to:

```text
False
```

For approximate comparisons, Python provides:

```python
import math

math.isclose(0.1 + 0.2, 0.3)
```

---

## 59. Float vs Decimal vs Fraction

### Float

Best suited for:

* General numerical calculations
* Scientific calculations where small approximation errors are acceptable
* High-performance numerical work

Float is an approximation.

### Decimal

Useful when decimal representation and controlled precision matter.

Common applications include:

* Financial calculations
* Monetary values
* Accounting

Example:

```python
from decimal import Decimal

price = Decimal("19.99")
```

### Fraction

Useful when exact rational arithmetic is required.

Example:

```python
from fractions import Fraction

value = Fraction(1, 3)
```

Conceptually:

```text
Float   → approximate binary floating-point
Decimal → decimal arithmetic
Fraction → exact rational arithmetic
```

---

## 60. Percentage error

Percentage error measures the size of an error relative to the actual value.

Formula:

```text
percentage error =
|measured - actual| / |actual| × 100
```

Example:

```text
Actual = 100
Measured = 97

Absolute error = 3

Percentage error =
3/100 × 100
= 3%
```

This is useful in:

* Scientific measurement
* Engineering
* Experimental analysis
* Data quality assessment

---

## 61. Absolute and relative error

Absolute error:

```text
|measured - actual|
```

Relative error:

```text
absolute error / actual
```

Percentage error:

```text
relative error × 100
```

These concepts help quantify how far an observed value is from a reference value.

---

## 62. Percentage composition

Percentage composition describes how much each component contributes to the total.

Suppose:

```text
Carbon = 20 g
Oxygen = 30 g
Hydrogen = 50 g
```

Total:

```text
100 g
```

Therefore:

```text
Carbon = 20%
Oxygen = 30%
Hydrogen = 50%
```

Formula:

```text
component percentage =
component / total × 100
```

---

## 63. Base-aware percentage reasoning

A percentage is meaningless without a base.

For example:

```text
₹100 increase on ₹100 = 100%
₹100 increase on ₹1,000 = 10%
₹100 increase on ₹10,000 = 1%
```

Therefore, whenever interpreting percentages in reports, dashboards or business discussions, identify the denominator or base.

This is especially important when comparing percentages across different populations or time periods.

---

## 64. Python implementation

Python can automate virtually all fraction, ratio, proportion and percentage calculations.

Important Python tools include:

```python
from fractions import Fraction
from decimal import Decimal
from math import gcd
```

Useful Python operations include:

```python
Fraction(3, 4)

float(Fraction(3, 4))

gcd(20, 30)

Decimal("19.99")
```

Python functions can turn mathematical formulas into reusable components.

Example:

```python
def percentage_change(original, new):
    if original == 0:
        raise ValueError("Original value cannot be zero.")

    return (new - original) / original * 100
```

---

## 65. Excel connection

The same mathematical principles can be implemented in Excel.

Suppose:

```text
A2 = Original value
B2 = New value
```

Percentage change:

```excel
=(B2-A2)/A2
```

Percentage of total:

```excel
=A2/B2*100
```

Percentage increase:

```excel
=A2*(1+B2)
```

Percentage decrease:

```excel
=A2*(1-B2)
```

Ratio:

```excel
=A2/B2
```

Unit rate:

```excel
=A2/B2
```

The underlying mathematics is the same whether the calculation is performed manually, in Excel or in Python.

---

## 66. Python vs Excel

### Python

Python is particularly useful when:

* Calculations need to be automated.
* Thousands or millions of records must be processed.
* Mathematical logic needs to be reusable.
* Data pipelines are required.
* Calculations need to integrate with databases or APIs.
* Statistical or machine-learning workflows are involved.

### Excel

Excel is particularly useful when:

* Calculations need to be visually inspected.
* Users need an interactive spreadsheet.
* Small-to-medium datasets are being analyzed.
* Business users need to modify assumptions easily.
* Tables and formulas need to be presented directly.

Both tools rely on the same mathematical concepts.

---

## 67. Business applications

Fractions, ratios, percentages and proportions appear throughout business.

Examples include:

### Sales

```text
Growth percentage
Conversion rate
Revenue share
Market share
```

### Finance

```text
Profit margin
Loss percentage
Interest rates
Portfolio allocation
Return percentage
```

### Marketing

```text
Click-through rate
Conversion rate
Customer acquisition rate
Campaign performance
```

### Operations

```text
Production rate
Defect rate
Resource allocation
Capacity utilization
```

### Procurement

```text
Unit price
Cost per kilogram
Cost per item
Discount percentage
Tax calculation
```

---

## 68. Data analytics applications

These concepts are essential in analytics.

Common metrics include:

```text
Percentage of total
Percentage change
Growth rate
Conversion rate
Error rate
Completion rate
Utilization rate
Proportion
Ratio
Unit rate
```

For example:

```text
Completed tasks = 720
Total tasks = 900

Completion rate =
720 / 900 × 100
= 80%
```

---

## 69. Common mistakes

### Mistake 1: Confusing part-to-part and part-to-whole ratios

If:

```text
Red = 2
Blue = 3
```

then:

```text
Red : Blue = 2 : 3
```

but:

```text
Red : Total = 2 : 5
```

These are different relationships.

### Mistake 2: Adding percentage changes

A 20% increase followed by a 20% decrease does not return to the original value.

### Mistake 3: Using the wrong base

Percentage increase generally uses the original value as the denominator.

### Mistake 4: Ignoring units

```text
60 km/hour
```

is not equivalent to:

```text
60 km/minute
```

### Mistake 5: Treating every ratio as a percentage

A ratio:

```text
2 : 3
```

is not automatically:

```text
2% : 3%
```

### Mistake 6: Dividing by zero

A denominator, base or total cannot be zero where division is required.

### Mistake 7: Ignoring floating-point limitations

Exact mathematical relationships may not always be represented exactly using binary floating-point numbers.

---

## 70. Important formulas

### Fraction

```text
Fraction = numerator / denominator
```

### Decimal

```text
Decimal = numerator / denominator
```

### Percentage

```text
Percentage = fraction × 100
```

### Percentage of a number

```text
Result = percentage/100 × number
```

### Percentage change

```text
Percentage change =
(new - old) / old × 100
```

### Percentage increase

```text
(new - original) / original × 100
```

### Percentage decrease

```text
(original - new) / original × 100
```

### Ratio simplification

```text
Divide both terms by GCD
```

### Proportion

```text
a/b = c/d
```

### Cross multiplication

```text
a × d = b × c
```

### Direct proportion

```text
y = kx
```

### Inverse proportion

```text
y = k/x
```

### Scale factor

```text
new / original
```

### Scaling

```text
new = original × scale factor
```

### Unit rate

```text
total quantity / number of units
```

### Profit

```text
selling price - cost price
```

### Profit percentage

```text
profit / cost price × 100
```

### Loss

```text
cost price - selling price
```

### Loss percentage

```text
loss / cost price × 100
```

### CAGR

```text
(ending / beginning)^(1/n) - 1
```

### Weighted average

```text
sum(value × weight) / sum(weights)
```

### Percentage error

```text
|measured - actual| / |actual| × 100
```

### Area scaling

```text
k²
```

### Volume scaling

```text
k³
```

---

## 71. Mental model

The most useful way to understand these concepts is to think in terms of relationships.

```text
                    WHOLE
                      |
             +--------+--------+
             |                 |
            PART             PART
             |
          FRACTION
             |
          DECIMAL
             |
        PERCENTAGE
```

Ratios compare quantities:

```text
A : B
```

Proportions establish equivalent relationships:

```text
A/B = C/D
```

Scaling preserves relationships:

```text
new = old × scale factor
```

Rates compare quantities with units:

```text
quantity / unit
```

This creates a connected mathematical framework rather than a collection of unrelated formulas.

---

## 72. End-to-end example

Suppose a company has:

```text
Developers = 12
Analysts = 8
Managers = 5
```

Total workforce:

```text
12 + 8 + 5 = 25
```

Developer proportion:

```text
12/25 = 0.48
```

Developer percentage:

```text
48%
```

Analyst proportion:

```text
8/25 = 0.32
```

Analyst percentage:

```text
32%
```

Manager proportion:

```text
5/25 = 0.20
```

Manager percentage:

```text
20%
```

The same information can therefore be represented as:

```text
Ratio:
12 : 8 : 5

Fractions:
12/25, 8/25, 5/25

Decimals:
0.48, 0.32, 0.20

Percentages:
48%, 32%, 20%
```

This demonstrates how fractions, ratios, decimals and percentages are different representations of related quantitative relationships.

---

## 73. What I learned

After studying this topic, I learned how to:

* Understand the numerator and denominator of a fraction.
* Distinguish proper, improper, mixed and unit fractions.
* Simplify fractions using the greatest common divisor.
* Identify and construct equivalent fractions.
* Perform arithmetic operations with fractions.
* Compare fractions.
* Convert fractions to decimals.
* Convert decimals to fractions.
* Convert fractions to percentages.
* Convert percentages to fractions.
* Convert decimals to percentages.
* Convert percentages to decimals.
* Calculate a percentage of a number.
* Calculate what percentage one number represents of another.
* Calculate percentage increases and decreases.
* Apply percentage increases and decreases.
* Reverse percentage calculations.
* Understand discounts and taxes.
* Calculate profit and loss percentages.
* Understand compound percentage changes.
* Understand the importance of the percentage base.
* Distinguish percentage points from percentage change.
* Understand ratios as comparisons between quantities.
* Distinguish part-to-part ratios from part-to-whole ratios.
* Simplify ratios.
* Generate equivalent ratios.
* Convert ratio relationships into proportions.
* Understand proportions.
* Use cross multiplication.
* Solve unknown values in proportions.
* Understand direct proportionality.
* Calculate the constant of proportionality.
* Understand inverse proportionality.
* Distinguish direct and inverse relationships.
* Apply scale factors.
* Scale quantities proportionally.
* Understand geometric scaling.
* Scale recipes and measurements.
* Work with map scales.
* Understand rates.
* Calculate unit rates.
* Compare unit prices.
* Calculate speed, distance and time.
* Perform unit conversions.
* Apply dimensional analysis.
* Allocate resources according to ratios.
* Normalize ratios into proportions.
* Calculate weighted averages.
* Understand probability as a proportion.
* Calculate population and sample proportions.
* Calculate rates of change.
* Understand CAGR.
* Calculate percentage errors.
* Distinguish absolute error from relative error.
* Understand floating-point precision.
* Understand the difference between `float`, `Decimal` and `Fraction` in Python.
* Use Python's `fractions.Fraction` for exact rational arithmetic.
* Use Python's `decimal.Decimal` for decimal-sensitive calculations.
* Use Python's `math.gcd()` to simplify ratios and fractions.
* Build reusable Python functions for mathematical calculations.
* Translate mathematical formulas into Python code.
* Translate mathematical formulas into Excel formulas.
* Apply fractions, ratios, percentages, proportions and rates to business problems.
* Apply proportional reasoning to data analysis.
* Recognize common mathematical mistakes involving percentages, ratios and bases.

---

## 74. Key takeaways

The central ideas can be summarized as:

```text
Fraction
    ↓
Part / Whole

Decimal
    ↓
Fraction represented in decimal notation

Percentage
    ↓
Part / Whole × 100

Ratio
    ↓
Comparison between quantities

Proportion
    ↓
Equality between two ratios

Scale
    ↓
Multiply by a scale factor

Rate
    ↓
Comparison between quantities with units
```

The most important formulas to remember are:

```text
fraction = numerator / denominator

percentage = part / whole × 100

percentage change =
(new - old) / old × 100

ratio = a : b

proportion =
a/b = c/d

cross multiplication =
a × d = b × c

direct proportion =
y = kx

inverse proportion =
y = k/x

scale factor =
new / original

unit rate =
total / number of units

profit =
selling price - cost price

loss =
cost price - selling price

weighted average =
sum(value × weight) / sum(weights)

percentage error =
|measured - actual| / |actual| × 100

CAGR =
(ending / beginning)^(1/n) - 1
```

---

## 75. Final perspective

Fractions, ratios and proportions are not isolated school-level mathematical topics. They form a foundation for quantitative reasoning.

They appear in:

* Mathematics
* Statistics
* Probability
* Data analysis
* Finance
* Economics
* Business intelligence
* Engineering
* Science
* Machine learning
* Programming
* Excel
* Python
* Financial modeling
* Operational analysis
* Resource allocation

Understanding these concepts means being able to move comfortably between different representations of the same relationship:

```text
Fraction
    ↕
Decimal
    ↕
Percentage
```

while also understanding:

```text
Ratio
    ↓
Proportion
    ↓
Scaling
    ↓
Rate
    ↓
Quantitative reasoning
```

The ultimate skill is not simply memorizing formulas. It is identifying the relationship between quantities, selecting the correct mathematical representation, choosing the correct base or denominator, maintaining consistent units and then implementing the calculation accurately using tools such as Python or Excel.

```
```

