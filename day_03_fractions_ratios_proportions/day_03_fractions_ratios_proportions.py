"""
===============================================================================
FRACTIONS, RATIOS AND PROPORTIONS
===============================================================================

Topics covered:
    1. Fractions
    2. Numerator and denominator
    3. Proper, improper and mixed fractions
    4. Equivalent fractions
    5. Simplification
    6. Comparing fractions
    7. Fraction arithmetic
    8. Fractions and decimals
    9. Fractions and percentages
    10. Ratios
    11. Equivalent ratios
    12. Simplifying ratios
    13. Comparing ratios
    14. Part-to-part and part-to-whole ratios
    15. Proportions
    16. Direct proportion
    17. Inverse proportion
    18. Cross multiplication
    19. Scaling
    20. Scale factors
    21. Rates
    22. Unit rates
    23. Percentage calculations
    24. Percentage increase and decrease
    25. Discounts, profit and loss
    26. Taxes
    27. Compound percentage changes
    28. Real-world calculations
    29. Python's fractions.Fraction
    30. Floating-point precision
    31. Ratio and proportion algorithms
    32. Data analysis examples
    33. Excel-oriented concepts
    34. Advanced mathematical relationships
    35. Practical exercises

This file is intentionally educational.
Every major concept is explained before it is implemented.

===============================================================================
"""


# =============================================================================
# 1. BASIC MATHEMATICAL VOCABULARY
# =============================================================================

print("=" * 80)
print("FRACTIONS, RATIOS AND PROPORTIONS")
print("=" * 80)

"""
A FRACTION represents a part of a whole.

Example:

    3/5

The number above the line is the NUMERATOR.
The number below the line is the DENOMINATOR.

    numerator
       3
      ---
       5
    denominator

Meaning:

    3 out of 5 equal parts.

Important:
    The denominator cannot be zero.

Fractions are fundamental because percentages, ratios and proportions
are closely related to them.
"""


# =============================================================================
# 2. FRACTION BASICS
# =============================================================================

numerator = 3
denominator = 5

fraction_value = numerator / denominator

print("\nFraction:", f"{numerator}/{denominator}")
print("Decimal value:", fraction_value)


"""
Types of fractions:

1. Proper fraction
   Numerator < denominator

   Example:
       3/5

2. Improper fraction
   Numerator >= denominator

   Example:
       7/5

3. Mixed number
   Whole number + proper fraction

   Example:
       1 2/5

4. Unit fraction
   Numerator = 1

   Example:
       1/7
"""


proper_fraction = (3, 5)
improper_fraction = (7, 5)
unit_fraction = (1, 7)

print("\nProper fraction:", proper_fraction)
print("Improper fraction:", improper_fraction)
print("Unit fraction:", unit_fraction)


# =============================================================================
# 3. PYTHON'S Fraction CLASS
# =============================================================================

from fractions import Fraction

a = Fraction(3, 5)
b = Fraction(7, 10)

print("\nFraction objects:")
print("a =", a)
print("b =", b)

print("a + b =", a + b)
print("a - b =", a - b)
print("a * b =", a * b)
print("a / b =", a / b)


"""
Why use Fraction?

Normal Python division produces floating-point numbers:

    1 / 3 = 0.3333333333333333

This is an approximation.

Fraction stores the exact rational number:

    Fraction(1, 3)

This is particularly useful in:
    - financial calculations
    - measurement
    - mathematical education
    - exact probability
    - symbolic calculations
"""


exact_fraction = Fraction(1, 3)

print("\nExact fraction:", exact_fraction)
print("Decimal representation:", float(exact_fraction))


# =============================================================================
# 4. SIMPLIFYING FRACTIONS
# =============================================================================

"""
A fraction is simplified when numerator and denominator have no common
factor other than 1.

Example:

    8/12

The greatest common divisor is 4.

    8 / 4 = 2
    12 / 4 = 3

Therefore:

    8/12 = 2/3
"""

fraction = Fraction(8, 12)

print("\nOriginal fraction: 8/12")
print("Simplified fraction:", fraction)


# Manual simplification using GCD

from math import gcd

numerator = 8
denominator = 12

common_factor = gcd(numerator, denominator)

simplified_numerator = numerator // common_factor
simplified_denominator = denominator // common_factor

print(
    "Manual simplification:",
    f"{simplified_numerator}/{simplified_denominator}"
)


# =============================================================================
# 5. EQUIVALENT FRACTIONS
# =============================================================================

"""
Equivalent fractions have the same mathematical value.

Example:

    1/2 = 2/4 = 3/6 = 50/100

Multiplying numerator and denominator by the same non-zero number
does not change the value.
"""

base = Fraction(1, 2)

for multiplier in [2, 3, 4, 10]:
    equivalent = Fraction(
        base.numerator * multiplier,
        base.denominator * multiplier
    )
    print(f"Equivalent fraction: {equivalent}")


# =============================================================================
# 6. COMPARING FRACTIONS
# =============================================================================

fraction_1 = Fraction(3, 4)
fraction_2 = Fraction(5, 8)

print("\nComparing fractions:")
print(fraction_1, ">", fraction_2, ":", fraction_1 > fraction_2)
print(fraction_1, "<", fraction_2, ":", fraction_1 < fraction_2)
print(fraction_1, "==", fraction_2, ":", fraction_1 == fraction_2)


"""
Python can compare Fraction objects directly because Fraction represents
exact rational values.
"""


# =============================================================================
# 7. FRACTION TO DECIMAL
# =============================================================================

fraction = Fraction(3, 8)
decimal_value = float(fraction)

print("\nFraction:", fraction)
print("Decimal:", decimal_value)


"""
General conversion:

    fraction = numerator / denominator

Example:

    3/8 = 0.375
"""


# =============================================================================
# 8. DECIMAL TO FRACTION
# =============================================================================

from decimal import Decimal

decimal_number = Decimal("0.75")
fraction_from_decimal = Fraction(decimal_number)

print("\nDecimal:", decimal_number)
print("Fraction:", fraction_from_decimal)


"""
Important:

Use Decimal("0.75") instead of Decimal(0.75)
when exact decimal input is required.

Binary floating-point representation can introduce small errors.
"""


# =============================================================================
# 9. FRACTION TO PERCENTAGE
# =============================================================================

"""
To convert a fraction into a percentage:

    percentage = fraction * 100

Example:

    3/4 = 0.75

    0.75 * 100 = 75%

"""

fraction = Fraction(3, 4)
percentage = float(fraction * 100)

print("\nFraction:", fraction)
print("Percentage:", percentage, "%")


# =============================================================================
# 10. PERCENTAGE TO FRACTION
# =============================================================================

"""
To convert a percentage into a fraction:

    percentage / 100

Example:

    25% = 25/100 = 1/4
"""

percentage = 25
fraction = Fraction(percentage, 100)

print("\nPercentage:", percentage, "%")
print("Fraction:", fraction)


# =============================================================================
# 11. DECIMAL TO PERCENTAGE
# =============================================================================

decimal_value = 0.625
percentage = decimal_value * 100

print("\nDecimal:", decimal_value)
print("Percentage:", percentage, "%")


# =============================================================================
# 12. PERCENTAGE TO DECIMAL
# =============================================================================

percentage = 62.5
decimal_value = percentage / 100

print("\nPercentage:", percentage, "%")
print("Decimal:", decimal_value)


# =============================================================================
# 13. RATIOS
# =============================================================================

"""
A RATIO compares two quantities.

Example:

    2 : 3

This means:

    For every 2 units of A, there are 3 units of B.

Ratios can represent:

    part : part
    part : whole
    quantity : quantity
    distance : time
    cost : quantity

Example:

    Boys : Girls = 2 : 3
"""


boys = 20
girls = 30

ratio = (boys, girls)

print("\nBoys:", boys)
print("Girls:", girls)
print("Ratio:", f"{boys}:{girls}")


# =============================================================================
# 14. SIMPLIFYING RATIOS
# =============================================================================

"""
To simplify:

    20 : 30

Find GCD:

    gcd(20, 30) = 10

Divide both by 10:

    2 : 3
"""

a = 20
b = 30

common = gcd(a, b)

simple_a = a // common
simple_b = b // common

print("\nOriginal ratio:", f"{a}:{b}")
print("Simplified ratio:", f"{simple_a}:{simple_b}")


# =============================================================================
# 15. EQUIVALENT RATIOS
# =============================================================================

"""
Equivalent ratios are created by multiplying or dividing both terms
by the same non-zero number.

Example:

    2 : 3
    4 : 6
    6 : 9
    20 : 30
"""

base_a = 2
base_b = 3

for multiplier in [1, 2, 3, 10]:
    print(
        f"{base_a * multiplier}:{base_b * multiplier}"
    )


# =============================================================================
# 16. PART-TO-PART VS PART-TO-WHOLE
# =============================================================================

"""
Suppose:

    Red balls = 2
    Blue balls = 3

Part-to-part ratio:

    Red : Blue = 2 : 3

Total:

    2 + 3 = 5

Red part-to-whole:

    2 : 5

Blue part-to-whole:

    3 : 5

This distinction is extremely important.
"""


red = 2
blue = 3
total = red + blue

print("\nRed : Blue =", f"{red}:{blue}")
print("Red : Total =", f"{red}:{total}")
print("Blue : Total =", f"{blue}:{total}")


# =============================================================================
# 17. RATIO AS A FRACTION
# =============================================================================

"""
A ratio:

    2 : 5

can be interpreted as:

    2/5

when calculating the proportion of the total represented by the first part.

Therefore:

    2/5 = 40%

"""


ratio_part = 2
ratio_total = 5

proportion = Fraction(ratio_part, ratio_total)
percentage = float(proportion * 100)

print("\nRatio:", f"{ratio_part}:{ratio_total}")
print("Proportion:", proportion)
print("Percentage:", percentage, "%")


# =============================================================================
# 18. PROPORTION
# =============================================================================

"""
A PROPORTION states that two ratios are equal.

Example:

    2/3 = 4/6

or:

    2 : 3 = 4 : 6

The two ratios represent the same relationship.
"""


left = Fraction(2, 3)
right = Fraction(4, 6)

print("\nProportion:")
print(left, "=", right)
print("Is proportional?", left == right)


# =============================================================================
# 19. CROSS MULTIPLICATION
# =============================================================================

"""
For:

    a/b = c/d

Cross multiplication gives:

    a*d = b*c

Example:

    2/3 = 4/6

Check:

    2 * 6 = 12
    3 * 4 = 12

Therefore the proportion is valid.
"""


a = 2
b = 3
c = 4
d = 6

print("\nCross multiplication:")
print("a*d =", a * d)
print("b*c =", b * c)
print("Valid proportion?", a * d == b * c)


# =============================================================================
# 20. SOLVING AN UNKNOWN USING PROPORTION
# =============================================================================

"""
Suppose:

    3/5 = x/20

Cross multiplication:

    3 * 20 = 5 * x

    60 = 5x

    x = 12
"""

a = 3
b = 5
d = 20

x = (a * d) / b

print("\nUnknown value in proportion:")
print("3/5 = x/20")
print("x =", x)


# =============================================================================
# 21. DIRECT PROPORTION
# =============================================================================

"""
Two quantities are directly proportional when:

    y ∝ x

This means:

    y = kx

where k is a constant.

Example:

If one notebook costs $20:

    1 notebook  = $20
    2 notebooks = $40
    3 notebooks = $60

Cost increases in the same proportion as quantity.
"""


price_per_item = 20

for quantity in [1, 2, 3, 5, 10]:
    cost = price_per_item * quantity
    print(f"{quantity} items -> {cost}")


# =============================================================================
# 22. FINDING THE CONSTANT OF PROPORTIONALITY
# =============================================================================

"""
For direct proportion:

    y = kx

Therefore:

    k = y/x

Example:

    x = 5
    y = 40

    k = 40/5 = 8

So:

    y = 8x
"""


x = 5
y = 40

k = y / x

print("\nConstant of proportionality:")
print("k =", k)
print("Equation: y =", k, "* x")


# =============================================================================
# 23. INVERSE PROPORTION
# =============================================================================

"""
Two quantities are inversely proportional when:

    y ∝ 1/x

Therefore:

    y = k/x

Example:

More workers can reduce the time required to complete a fixed task.

If:

    workers * time = constant

then:

    time = constant / workers
"""


constant = 120

for workers in [1, 2, 3, 4, 6, 8]:
    time = constant / workers
    print(f"{workers} workers -> {time} time units")


# =============================================================================
# 24. DIRECT VS INVERSE PROPORTION
# =============================================================================

"""
DIRECT:

    y = kx

As x increases:
    y increases.

INVERSE:

    y = k/x

As x increases:
    y decreases.

Examples:

Direct:
    quantity and total cost
    distance and time at constant speed

Inverse:
    workers and completion time
    speed and travel time for fixed distance
"""


# =============================================================================
# 25. SCALING
# =============================================================================

"""
Scaling means increasing or decreasing a quantity while maintaining
the same proportions.

If the scale factor is k:

    new value = old value * k

Example:

Original dimensions:

    width = 10
    height = 5

Scale factor = 2

New dimensions:

    width = 20
    height = 10
"""


width = 10
height = 5
scale_factor = 2

new_width = width * scale_factor
new_height = height * scale_factor

print("\nScaling:")
print("Original:", width, height)
print("Scale factor:", scale_factor)
print("New:", new_width, new_height)


# =============================================================================
# 26. SCALE FACTOR
# =============================================================================

"""
Scale factor:

    scale factor = new value / original value

Example:

    Original = 10
    New = 25

    Scale factor = 25/10 = 2.5
"""


original = 10
new = 25

scale_factor = new / original

print("\nScale factor:", scale_factor)


# =============================================================================
# 27. SCALE DRAWING EXAMPLE
# =============================================================================

"""
Suppose a map uses:

    1 cm = 5 km

A measured distance of 7 cm represents:

    7 * 5 = 35 km
"""

map_distance_cm = 7
km_per_cm = 5

real_distance_km = map_distance_cm * km_per_cm

print("\nMap scaling:")
print("Map distance:", map_distance_cm, "cm")
print("Real distance:", real_distance_km, "km")


# =============================================================================
# 28. RATES
# =============================================================================

"""
A RATE compares quantities with different units.

Examples:

    60 km/hour
    ₹100/kg
    5 pages/minute
    80 words/minute

A rate often has the form:

    quantity / unit

"""


distance = 120
time = 2

speed = distance / time

print("\nRate:")
print("Distance:", distance, "km")
print("Time:", time, "hours")
print("Speed:", speed, "km/hour")


# =============================================================================
# 29. UNIT RATE
# =============================================================================

"""
A unit rate expresses the quantity for exactly one unit.

Example:

    ₹240 for 6 kg

Unit price:

    240/6 = ₹40 per kg
"""


total_cost = 240
quantity = 6

unit_price = total_cost / quantity

print("\nUnit rate:")
print("Total cost:", total_cost)
print("Quantity:", quantity)
print("Unit price:", unit_price)


# =============================================================================
# 30. COMPARING RATES
# =============================================================================

"""
Suppose:

    Product A:
        ₹300 / 5 kg = ₹60/kg

    Product B:
        ₹420 / 7 kg = ₹60/kg

Both have the same unit rate.
"""


products = {
    "A": {"cost": 300, "quantity": 5},
    "B": {"cost": 420, "quantity": 7},
}

for name, data in products.items():
    unit_rate = data["cost"] / data["quantity"]
    print(
        f"Product {name}: "
        f"{unit_rate:.2f} per unit"
    )


# =============================================================================
# 31. PERCENTAGE BASICS
# =============================================================================

"""
Percentage literally means "per hundred".

    x% = x/100

Examples:

    50% = 50/100 = 1/2
    25% = 25/100 = 1/4
    10% = 10/100 = 1/10
"""


percentages = [10, 25, 50, 75, 100]

for p in percentages:
    print(f"{p}% = {Fraction(p, 100)}")


# =============================================================================
# 32. FINDING A PERCENTAGE OF A NUMBER
# =============================================================================

"""
To find p% of x:

    result = (p/100) * x

Example:

    20% of 500

    = 0.20 * 500
    = 100
"""


p = 20
number = 500

result = (p / 100) * number

print("\nPercentage of number:")
print(f"{p}% of {number} =", result)


# =============================================================================
# 33. FINDING WHAT PERCENTAGE ONE NUMBER IS OF ANOTHER
# =============================================================================

"""
Formula:

    percentage = (part / whole) * 100

Example:

    30 out of 120

    = (30/120) * 100
    = 25%
"""


part = 30
whole = 120

percentage = (part / whole) * 100

print("\nPercentage relationship:")
print(f"{part} is {percentage}% of {whole}")


# =============================================================================
# 34. PERCENTAGE INCREASE
# =============================================================================

"""
Percentage increase:

    increase = new - original

    percentage increase =
        ((new - original) / original) * 100

Example:

    Original = 100
    New = 120

    Increase = 20

    Percentage increase = 20%
"""


original = 100
new = 120

increase = new - original
percentage_increase = increase / original * 100

print("\nPercentage increase:", percentage_increase, "%")


# =============================================================================
# 35. PERCENTAGE DECREASE
# =============================================================================

"""
Percentage decrease:

    decrease = original - new

    percentage decrease =
        ((original - new) / original) * 100
"""


original = 500
new = 425

decrease = original - new
percentage_decrease = decrease / original * 100

print("\nPercentage decrease:", percentage_decrease, "%")


# =============================================================================
# 36. APPLYING A PERCENTAGE INCREASE
# =============================================================================

"""
New value after increase:

    new = original * (1 + percentage/100)

Example:

    ₹1,000 increased by 15%

    = 1000 * 1.15
    = 1150
"""


original = 1000
increase_percent = 15

new_value = original * (1 + increase_percent / 100)

print("\nValue after increase:", new_value)


# =============================================================================
# 37. APPLYING A PERCENTAGE DECREASE
# =============================================================================

"""
New value after decrease:

    new = original * (1 - percentage/100)

Example:

    ₹1,000 decreased by 15%

    = 1000 * 0.85
    = 850
"""


original = 1000
decrease_percent = 15

new_value = original * (1 - decrease_percent / 100)

print("\nValue after decrease:", new_value)


# =============================================================================
# 38. DISCOUNT
# =============================================================================

"""
Discount amount:

    discount = original_price * discount_rate

Selling price:

    selling_price = original_price - discount

Example:

    Price = ₹2,000
    Discount = 20%

    Discount = ₹400
    Final price = ₹1,600
"""


price = 2000
discount_percent = 20

discount = price * discount_percent / 100
final_price = price - discount

print("\nDiscount calculation:")
print("Original price:", price)
print("Discount:", discount)
print("Final price:", final_price)


# =============================================================================
# 39. TAX
# =============================================================================

"""
Tax:

    tax = price * tax_rate

Total:

    total = price + tax
"""


price = 1000
tax_percent = 18

tax = price * tax_percent / 100
total = price + tax

print("\nTax calculation:")
print("Price:", price)
print("Tax:", tax)
print("Total:", total)


# =============================================================================
# 40. PROFIT AND LOSS
# =============================================================================

"""
Profit:

    profit = selling_price - cost_price

Profit percentage:

    profit% = profit / cost_price * 100

Loss:

    loss = cost_price - selling_price

Loss percentage:

    loss% = loss / cost_price * 100
"""


cost_price = 800
selling_price = 1000

profit = selling_price - cost_price
profit_percent = profit / cost_price * 100

print("\nProfit:")
print("Profit:", profit)
print("Profit percentage:", profit_percent, "%")


# =============================================================================
# 41. COMPOUND PERCENTAGE CHANGE
# =============================================================================

"""
Two consecutive percentage changes must NOT simply be added.

Example:

    Increase by 20%
    Then decrease by 20%

Start:

    100

After +20%:

    120

After -20%:

    96

Final value = 96

Not 100.

This is because the second percentage is applied to the new base.
"""


value = 100

value *= 1.20
value *= 0.80

print("\nCompound percentage change:")
print("Final value:", value)


# =============================================================================
# 42. GENERAL COMPOUND CHANGE
# =============================================================================

"""
For multiple percentage changes:

    final =
        initial
        * (1 + r1)
        * (1 + r2)
        * ...

where:
    increase = positive rate
    decrease = negative rate
"""


initial = 1000
changes = [10, 20, -15]

final = initial

for change in changes:
    final *= (1 + change / 100)

print("\nMultiple percentage changes:")
print("Initial:", initial)
print("Final:", final)


# =============================================================================
# 43. REVERSE PERCENTAGE CALCULATION
# =============================================================================

"""
Suppose a price after a 20% discount is ₹800.

We want the original price.

We know:

    final = original * 0.80

Therefore:

    original = final / 0.80

"""


final_price = 800
discount_percent = 20

original_price = final_price / (1 - discount_percent / 100)

print("\nReverse percentage:")
print("Original price:", original_price)


# =============================================================================
# 44. SOLVING A PROPORTIONAL ALLOCATION
# =============================================================================

"""
Suppose ₹10,000 is divided in the ratio:

    2 : 3 : 5

Total ratio units:

    2 + 3 + 5 = 10

One unit:

    10,000 / 10 = 1,000

Shares:

    2 units = 2,000
    3 units = 3,000
    5 units = 5,000
"""


total_money = 10000
ratio = [2, 3, 5]

ratio_sum = sum(ratio)

shares = [
    total_money * part / ratio_sum
    for part in ratio
]

print("\nRatio allocation:")
print("Total:", total_money)
print("Ratio:", ratio)
print("Shares:", shares)


# =============================================================================
# 45. GENERAL RATIO ALLOCATION FUNCTION
# =============================================================================

def allocate_by_ratio(total, ratios):
    """
    Divide total according to a ratio.

    Example:
        allocate_by_ratio(100, [1, 2, 3])

    Returns:
        [16.666..., 33.333..., 50.0]
    """

    if total < 0:
        raise ValueError("Total cannot be negative.")

    if not ratios:
        raise ValueError("Ratios cannot be empty.")

    if any(r < 0 for r in ratios):
        raise ValueError("Ratios cannot contain negative values.")

    ratio_sum = sum(ratios)

    if ratio_sum == 0:
        raise ValueError("Sum of ratios must be greater than zero.")

    return [
        total * ratio / ratio_sum
        for ratio in ratios
    ]


print("\nRatio allocation function:")
print(allocate_by_ratio(10000, [2, 3, 5]))


# =============================================================================
# 46. FINDING A MISSING RATIO TERM
# =============================================================================

"""
Suppose:

    4 : 7 = 20 : x

Using cross multiplication:

    4x = 7 * 20

    x = 35
"""


def solve_ratio(a, b, c):
    """
    Solve:

        a/b = c/x

    for x.
    """

    if a == 0:
        raise ValueError("a cannot be zero.")

    return (b * c) / a


x = solve_ratio(4, 7, 20)

print("\nMissing ratio term:")
print("x =", x)


# =============================================================================
# 47. RATE CONVERSION
# =============================================================================

"""
Rates can be converted when units are changed.

Example:

    60 km/hour

To convert to km/minute:

    60 / 60 = 1 km/minute

To convert to meters/second:

    60 km/hour
    = 60,000 meters / 3,600 seconds
    = 16.666... m/s
"""


speed_kmh = 60

speed_mps = speed_kmh * 1000 / 3600

print("\nRate conversion:")
print(speed_kmh, "km/h =", speed_mps, "m/s")


# =============================================================================
# 48. UNIT PRICE COMPARISON
# =============================================================================

def unit_price(total_price, quantity):
    """
    Calculate price per unit.
    """

    if quantity <= 0:
        raise ValueError("Quantity must be positive.")

    return total_price / quantity


items = [
    ("A", 250, 5),
    ("B", 360, 8),
    ("C", 500, 10),
]

print("\nUnit price comparison:")

for name, price, quantity in items:
    rate = unit_price(price, quantity)
    print(name, "=", round(rate, 2), "per unit")


# =============================================================================
# 49. SPEED, DISTANCE AND TIME
# =============================================================================

"""
Core relationship:

    speed = distance / time

Therefore:

    distance = speed * time

    time = distance / speed
"""


def calculate_speed(distance, time):
    if time <= 0:
        raise ValueError("Time must be positive.")
    return distance / time


def calculate_distance(speed, time):
    if speed < 0 or time < 0:
        raise ValueError("Speed and time cannot be negative.")
    return speed * time


def calculate_time(distance, speed):
    if speed <= 0:
        raise ValueError("Speed must be positive.")
    return distance / speed


print("\nSpeed-distance-time:")
print("Speed:", calculate_speed(150, 3))
print("Distance:", calculate_distance(50, 3))
print("Time:", calculate_time(150, 50))


# =============================================================================
# 50. RECIPE SCALING
# =============================================================================

"""
A recipe is an excellent example of proportional scaling.

Suppose a recipe serves 4 people and requires:

    Flour = 300 g
    Sugar = 100 g
    Milk = 200 ml

For 10 people:

    scale factor = 10/4 = 2.5

Every ingredient is multiplied by 2.5.
"""


def scale_recipe(recipe, original_servings, new_servings):
    """
    Scale recipe quantities proportionally.
    """

    if original_servings <= 0:
        raise ValueError("Original servings must be positive.")

    if new_servings <= 0:
        raise ValueError("New servings must be positive.")

    factor = new_servings / original_servings

    return {
        ingredient: quantity * factor
        for ingredient, quantity in recipe.items()
    }


recipe = {
    "flour_g": 300,
    "sugar_g": 100,
    "milk_ml": 200,
}

scaled_recipe = scale_recipe(recipe, 4, 10)

print("\nScaled recipe:")
print(scaled_recipe)


# =============================================================================
# 51. MAP SCALE
# =============================================================================

def real_distance_from_map(map_distance, scale):
    """
    Example:
        scale = 5 km/cm

        map_distance = 10 cm

        real distance = 50 km
    """

    return map_distance * scale


print("\nMap distance:")
print(real_distance_from_map(10, 5), "km")


# =============================================================================
# 52. DATA ANALYSIS WITH PERCENTAGES
# =============================================================================

"""
Percentages are heavily used in data analysis.

Suppose an organization has:

    Completed = 720
    Pending = 180

Total:

    900

Completion percentage:

    720 / 900 * 100 = 80%
"""


completed = 720
pending = 180
total = completed + pending

completion_percentage = completed / total * 100
pending_percentage = pending / total * 100

print("\nData analysis:")
print("Completion:", completion_percentage, "%")
print("Pending:", pending_percentage, "%")


# =============================================================================
# 53. PERCENTAGE CHANGE FUNCTION
# =============================================================================

def percentage_change(original, new):
    """
    Calculate percentage change from original to new.

    Positive result = increase.
    Negative result = decrease.
    """

    if original == 0:
        raise ValueError(
            "Percentage change from zero is undefined."
        )

    return (new - original) / original * 100


print("\nPercentage change:")
print(percentage_change(500, 575), "%")
print(percentage_change(500, 425), "%")


# =============================================================================
# 54. PERCENTAGE OF TOTAL FUNCTION
# =============================================================================

def percentage_of_total(part, total):
    """
    Calculate what percentage 'part' represents of 'total'.
    """

    if total == 0:
        raise ValueError("Total cannot be zero.")

    return part / total * 100


print("\nPercentage of total:")
print(percentage_of_total(35, 140), "%")


# =============================================================================
# 55. CONVERTING BETWEEN COMMON REPRESENTATIONS
# =============================================================================

def fraction_to_decimal(numerator, denominator):
    if denominator == 0:
        raise ValueError("Denominator cannot be zero.")
    return numerator / denominator


def fraction_to_percentage(numerator, denominator):
    return fraction_to_decimal(numerator, denominator) * 100


def percentage_to_decimal(percentage):
    return percentage / 100


def percentage_to_fraction(percentage):
    return Fraction(percentage, 100)


print("\nRepresentation conversions:")

print(
    "3/8 -> decimal:",
    fraction_to_decimal(3, 8)
)

print(
    "3/8 -> percentage:",
    fraction_to_percentage(3, 8), "%"
)

print(
    "62.5% -> decimal:",
    percentage_to_decimal(62.5)
)

print(
    "62.5% -> fraction:",
    percentage_to_fraction(62.5)
)


# =============================================================================
# 56. FLOATING-POINT PRECISION
# =============================================================================

"""
A major advanced topic is numerical precision.

Computers generally represent floating-point numbers using binary
floating-point arithmetic.

Some decimal numbers cannot be represented exactly in binary.

Therefore:

    0.1 + 0.2

may produce:

    0.30000000000000004

instead of exactly 0.3.
"""

floating_result = 0.1 + 0.2

print("\nFloating-point example:")
print("0.1 + 0.2 =", floating_result)
print("Equals 0.3?", floating_result == 0.3)


# Better comparison

import math

print(
    "Approximately equal?",
    math.isclose(floating_result, 0.3)
)


# =============================================================================
# 57. DECIMAL FOR FINANCIAL CALCULATIONS
# =============================================================================

"""
For decimal-sensitive applications such as money, Decimal is often
preferable to binary floating point.
"""

from decimal import Decimal

price = Decimal("19.99")
tax_rate = Decimal("0.18")

tax = price * tax_rate
total = price + tax

print("\nDecimal calculation:")
print("Price:", price)
print("Tax:", tax)
print("Total:", total)


# =============================================================================
# 58. FRACTION VS FLOAT VS DECIMAL
# =============================================================================

"""
FLOAT:
    Fast approximate representation.

DECIMAL:
    Decimal arithmetic with controllable precision.

FRACTION:
    Exact rational arithmetic.

Example:

    1/3

Fraction:
    exactly represents 1/3.

Float:
    approximate representation.

Decimal:
    can represent a decimal approximation depending on context.
"""

fraction_value = Fraction(1, 3)
float_value = 1 / 3
decimal_value = Decimal("1") / Decimal("3")

print("\nNumerical representations:")
print("Fraction:", fraction_value)
print("Float:", float_value)
print("Decimal:", decimal_value)


# =============================================================================
# 59. RATIO NORMALIZATION
# =============================================================================

"""
Normalization converts values into proportions that sum to 1.

Example:

    Values = [2, 3, 5]

Total = 10

Normalized:

    [0.2, 0.3, 0.5]

These can also be interpreted as:

    [20%, 30%, 50%]
"""


def normalize(values):
    total = sum(values)

    if total == 0:
        raise ValueError("Cannot normalize values with zero sum.")

    return [value / total for value in values]


values = [2, 3, 5]
normalized = normalize(values)

print("\nNormalized values:")
print(normalized)
print("As percentages:")
print([value * 100 for value in normalized])


# =============================================================================
# 60. WEIGHTED AVERAGE
# =============================================================================

"""
Weighted averages are closely related to proportions.

Formula:

    weighted average =
        sum(value * weight) / sum(weights)

Example:

    Exam = 80, weight = 60%
    Project = 90, weight = 40%

Weighted score:

    80 * 0.60 + 90 * 0.40
    = 84
"""


def weighted_average(values, weights):
    if len(values) != len(weights):
        raise ValueError(
            "Values and weights must have the same length."
        )

    weight_sum = sum(weights)

    if weight_sum == 0:
        raise ValueError("Sum of weights cannot be zero.")

    return sum(
        value * weight
        for value, weight in zip(values, weights)
    ) / weight_sum


score = weighted_average(
    [80, 90],
    [0.60, 0.40]
)

print("\nWeighted average:", score)


# =============================================================================
# 61. PROBABILITY CONNECTION
# =============================================================================

"""
Probability is often represented as a fraction.

If 3 outcomes are favorable out of 10 equally likely outcomes:

    P(event) = 3/10

Percentage:

    30%
"""


favorable = 3
possible = 10

probability = Fraction(favorable, possible)

print("\nProbability:")
print("Fraction:", probability)
print("Decimal:", float(probability))
print("Percentage:", float(probability * 100), "%")


# =============================================================================
# 62. POPULATION PROPORTION
# =============================================================================

population = 1_000_000
group = 275_000

proportion = Fraction(group, population)

print("\nPopulation proportion:")
print("Fraction:", proportion)
print("Percentage:", float(proportion * 100), "%")


# =============================================================================
# 63. SAMPLING PROPORTION
# =============================================================================

"""
Suppose a survey has:

    420 respondents
    168 selected option A

Sample proportion:

    168 / 420 = 0.4

Percentage:

    40%
"""


respondents = 420
option_a = 168

sample_proportion = option_a / respondents

print("\nSample proportion:")
print("Proportion:", sample_proportion)
print("Percentage:", sample_proportion * 100, "%")


# =============================================================================
# 64. RATE OF CHANGE
# =============================================================================

"""
Rate of change:

    change in y / change in x

This is a foundational idea in mathematics, statistics and machine learning.

Example:

    Revenue increases from ₹100,000 to ₹130,000
    over 3 months.

Average rate of change:

    30,000 / 3 = ₹10,000 per month
"""


initial_revenue = 100000
final_revenue = 130000
months = 3

revenue_change = final_revenue - initial_revenue
rate_of_change = revenue_change / months

print("\nRate of change:")
print("₹", rate_of_change, "per month")


# =============================================================================
# 65. COMPOUND ANNUAL GROWTH RATE (CAGR)
# =============================================================================

"""
CAGR is an advanced percentage-growth concept.

Formula:

    CAGR =
        (Ending Value / Beginning Value)^(1/n) - 1

where n = number of periods.

Example:

    Beginning = 100
    Ending = 150
    Periods = 5
"""


def cagr(beginning, ending, periods):
    if beginning <= 0 or ending <= 0:
        raise ValueError(
            "Beginning and ending values must be positive."
        )

    if periods <= 0:
        raise ValueError("Periods must be positive.")

    return (ending / beginning) ** (1 / periods) - 1


growth = cagr(100, 150, 5)

print("\nCAGR:")
print(growth * 100, "%")


# =============================================================================
# 66. MIXTURE RATIO
# =============================================================================

"""
Suppose a solution requires:

    Chemical A : Chemical B = 2 : 3

For a total of 50 liters:

    A = 2/(2+3) * 50 = 20 L
    B = 3/(2+3) * 50 = 30 L
"""


total_volume = 50
ratio_a = 2
ratio_b = 3

a_volume = total_volume * ratio_a / (ratio_a + ratio_b)
b_volume = total_volume * ratio_b / (ratio_a + ratio_b)

print("\nMixture ratio:")
print("A:", a_volume)
print("B:", b_volume)


# =============================================================================
# 67. SCALE FACTORS IN TWO DIMENSIONS
# =============================================================================

"""
If length is scaled by k:

    new length = k * old length

For a two-dimensional object:

    area scales by k²

For a three-dimensional object:

    volume scales by k³

This is extremely important.

Example:

Scale factor = 2

Length:
    2 times

Area:
    4 times

Volume:
    8 times
"""


k = 2

length_factor = k
area_factor = k ** 2
volume_factor = k ** 3

print("\nGeometric scaling:")
print("Length factor:", length_factor)
print("Area factor:", area_factor)
print("Volume factor:", volume_factor)


# =============================================================================
# 68. DIMENSIONAL ANALYSIS
# =============================================================================

"""
Dimensional analysis checks whether units make sense.

Example:

    distance / time = speed

    km / hour = km/hour

Example:

    ₹ / kg = ₹ per kg

When multiplying:

    ₹/kg * kg = ₹

This is useful for detecting calculation errors.
"""


price_per_kg = 80
mass_kg = 5

total_cost = price_per_kg * mass_kg

print("\nDimensional analysis:")
print("₹/kg * kg = ₹")
print("Total cost:", total_cost)


# =============================================================================
# 69. EXCEL CONNECTIONS
# =============================================================================

"""
The same concepts can be implemented in Excel.

Suppose:

    A2 = Original value
    B2 = New value

Percentage change:

    =(B2-A2)/A2

Percentage of total:

    =A2/B2*100

Percentage increase:

    =A2*(1+B2)

Percentage decrease:

    =A2*(1-B2)

Ratio:

    =A2/B2

Unit rate:

    =A2/B2

Direct proportion:

    =A2*B2

The mathematical principles remain the same regardless of the tool.
"""


# =============================================================================
# 70. PYTHON + EXCEL THINKING
# =============================================================================

"""
A data analyst should think in terms of relationships:

    numerator
    denominator
    part
    whole
    rate
    base
    scale factor
    proportion
    percentage

Python automates calculations.

Excel makes the same calculations accessible through formulas,
tables and spreadsheets.
"""


# =============================================================================
# 71. PRACTICAL BUSINESS EXAMPLE
# =============================================================================

"""
Suppose an organization has monthly sales:

    January   = ₹500,000
    February  = ₹575,000
    March     = ₹690,000

We can calculate:

    month-over-month growth
    total sales
    average sales
    growth percentage
"""


sales = {
    "January": 500000,
    "February": 575000,
    "March": 690000,
}

months = list(sales.keys())

print("\nBusiness sales analysis:")

for i in range(1, len(months)):
    previous = sales[months[i - 1]]
    current = sales[months[i]]

    change = percentage_change(previous, current)

    print(
        months[i - 1],
        "->",
        months[i],
        ":",
        round(change, 2),
        "%"
    )


# =============================================================================
# 72. PRACTICAL INVENTORY EXAMPLE
# =============================================================================

"""
Inventory:

    Total items = 5,000
    Sold = 3,750
    Remaining = 1,250

Sold percentage:

    3,750 / 5,000 * 100 = 75%

Remaining:

    25%
"""


total_inventory = 5000
sold = 3750
remaining = total_inventory - sold

sold_percent = percentage_of_total(sold, total_inventory)
remaining_percent = percentage_of_total(
    remaining,
    total_inventory
)

print("\nInventory analysis:")
print("Sold:", sold_percent, "%")
print("Remaining:", remaining_percent, "%")


# =============================================================================
# 73. PRACTICAL WORKFORCE EXAMPLE
# =============================================================================

"""
Suppose a team has:

    Developers = 12
    Analysts = 8
    Managers = 5

Total = 25

Developer proportion:

    12/25 = 48%

Analyst proportion:

    8/25 = 32%

Manager proportion:

    5/25 = 20%
"""


workforce = {
    "Developers": 12,
    "Analysts": 8,
    "Managers": 5,
}

total_workers = sum(workforce.values())

print("\nWorkforce proportions:")

for role, count in workforce.items():
    percentage = percentage_of_total(
        count,
        total_workers
    )

    print(
        role,
        ":",
        round(percentage, 2),
        "%"
    )


# =============================================================================
# 74. PRACTICAL CONVERSION PIPELINE
# =============================================================================

"""
A common mathematical conversion chain is:

    Fraction
        ↓
    Decimal
        ↓
    Percentage

Example:

    3/5
    ↓
    0.6
    ↓
    60%
"""


fraction = Fraction(3, 5)
decimal = float(fraction)
percentage = decimal * 100

print("\nConversion pipeline:")
print("Fraction:", fraction)
print("Decimal:", decimal)
print("Percentage:", percentage, "%")


# =============================================================================
# 75. ADVANCED: RATIO AS A VECTOR
# =============================================================================

"""
A ratio [2, 3, 5] can be viewed as a vector of weights.

Normalize:

    [2/10, 3/10, 5/10]

This gives:

    [0.2, 0.3, 0.5]

Such normalized proportions appear in:

    - probability
    - machine learning
    - portfolio allocation
    - resource allocation
    - statistics
    - data science
"""


ratio_vector = [2, 3, 5]
proportion_vector = normalize(ratio_vector)

print("\nRatio vector:")
print(ratio_vector)

print("Proportion vector:")
print(proportion_vector)


# =============================================================================
# 76. ADVANCED: PERCENTAGE POINTS VS PERCENTAGE CHANGE
# =============================================================================

"""
This distinction is extremely important.

Suppose a rate changes:

    40% -> 50%

Percentage-point increase:

    50% - 40% = 10 percentage points

Percentage increase:

    (50 - 40) / 40 * 100
    = 25%

Therefore:

    +10 percentage points
    is equivalent to
    +25% relative increase.

These are NOT the same thing.
"""


old_rate = 40
new_rate = 50

percentage_points = new_rate - old_rate
relative_change = percentage_change(old_rate, new_rate)

print("\nPercentage points vs percentage change:")
print("Percentage-point change:", percentage_points)
print("Relative percentage change:", relative_change, "%")


# =============================================================================
# 77. ADVANCED: BASE EFFECT
# =============================================================================

"""
Percentage calculations depend on the base.

An increase of ₹100 means:

    100% increase if base = ₹100
    10% increase if base = ₹1,000
    1% increase if base = ₹10,000

Therefore always ask:

    "Percentage of WHAT?"
"""


increase = 100

for base in [100, 1000, 10000]:
    percent = increase / base * 100

    print(
        f"Increase ₹{increase} on base ₹{base}: "
        f"{percent}%"
    )


# =============================================================================
# 78. ADVANCED: ERROR PERCENTAGE
# =============================================================================

"""
Percentage error:

    |measured - actual| / actual * 100

Example:

    Actual = 100
    Measured = 97

Error:

    3%

"""


def percentage_error(actual, measured):
    if actual == 0:
        raise ValueError("Actual value cannot be zero.")

    return abs(measured - actual) / abs(actual) * 100


error = percentage_error(100, 97)

print("\nPercentage error:", error, "%")


# =============================================================================
# 79. ADVANCED: RELATIVE ERROR
# =============================================================================

"""
Relative error:

    absolute error / actual value

Percentage error:

    relative error * 100
"""


actual = 200
measured = 194

absolute_error = abs(measured - actual)
relative_error = absolute_error / actual

print("\nError analysis:")
print("Absolute error:", absolute_error)
print("Relative error:", relative_error)
print("Percentage error:", relative_error * 100, "%")


# =============================================================================
# 80. ADVANCED: PROPORTIONAL REASONING
# =============================================================================

"""
Suppose:

    4 machines produce 800 units per hour.

If production is directly proportional to machines:

    1 machine = 200 units/hour

Then:

    10 machines = 2,000 units/hour
"""


machines = 4
production = 800

production_per_machine = production / machines

new_machines = 10
new_production = production_per_machine * new_machines

print("\nProportional production:")
print("Production per machine:", production_per_machine)
print("Production with 10 machines:", new_production)


# =============================================================================
# 81. ADVANCED: INVERSE PROPORTION REASONING
# =============================================================================

"""
Suppose:

    5 workers require 12 hours.

Assuming fixed workload:

    workers * hours = constant

Constant:

    5 * 12 = 60

For 10 workers:

    hours = 60 / 10 = 6
"""


workers_1 = 5
hours_1 = 12

constant = workers_1 * hours_1

workers_2 = 10
hours_2 = constant / workers_2

print("\nInverse proportion:")
print("New time:", hours_2, "hours")


# =============================================================================
# 82. ADVANCED: PERCENTAGE COMPOSITION
# =============================================================================

"""
Percentage composition:

    component / total * 100

Example:

    Carbon = 20 g
    Oxygen = 30 g
    Hydrogen = 50 g

Total = 100 g

Percentages:

    Carbon = 20%
    Oxygen = 30%
    Hydrogen = 50%
"""


composition = {
    "Carbon": 20,
    "Oxygen": 30,
    "Hydrogen": 50,
}

composition_total = sum(composition.values())

print("\nComposition:")

for component, mass in composition.items():
    percent = mass / composition_total * 100
    print(component, "=", percent, "%")


# =============================================================================
# 83. ADVANCED: REVERSE RATIO ALLOCATION
# =============================================================================

"""
Sometimes the known total and ratio are available, but the individual
components need to be reconstructed.

Example:

    Total = 240
    Ratio = 3 : 5

Total ratio units:

    8

Each unit:

    240 / 8 = 30

Components:

    90 and 150
"""


allocation = allocate_by_ratio(240, [3, 5])

print("\nReverse ratio allocation:")
print(allocation)


# =============================================================================
# 84. MATHEMATICAL SUMMARY FUNCTIONS
# =============================================================================

def fraction_to_all(
    numerator,
    denominator
):
    """
    Return fraction, decimal and percentage representations.
    """

    if denominator == 0:
        raise ValueError("Denominator cannot be zero.")

    fraction = Fraction(numerator, denominator)
    decimal = float(fraction)
    percentage = decimal * 100

    return {
        "fraction": fraction,
        "decimal": decimal,
        "percentage": percentage,
    }


print("\nComplete fraction representation:")
print(fraction_to_all(7, 20))


# =============================================================================
# 85. GENERAL RATIO ANALYSIS
# =============================================================================

def analyze_ratio(a, b):
    """
    Analyze a ratio a:b.

    Returns:
        simplified ratio
        proportion of a
        proportion of b
        percentage share of a
        percentage share of b
    """

    if a < 0 or b < 0:
        raise ValueError("Ratio terms cannot be negative.")

    total = a + b

    if total == 0:
        raise ValueError("Ratio cannot be 0:0.")

    common = gcd(a, b)

    return {
        "original_ratio": f"{a}:{b}",
        "simplified_ratio": f"{a // common}:{b // common}",
        "a_proportion": a / total,
        "b_proportion": b / total,
        "a_percentage": a / total * 100,
        "b_percentage": b / total * 100,
    }


print("\nRatio analysis:")
print(analyze_ratio(20, 30))


# =============================================================================
# 86. COMMON MISTAKES
# =============================================================================

"""
COMMON MISTAKE 1:
Confusing part-to-part with part-to-whole.

2 : 3 does NOT mean 2/3 of the total.

If there are 2 red and 3 blue objects:

    Red : Blue = 2 : 3

but:

    Red : Total = 2 : 5


COMMON MISTAKE 2:
Adding percentage changes.

+20% followed by -20% does not return to the original value.


COMMON MISTAKE 3:
Using the wrong base.

Percentage increase must use the ORIGINAL value as the denominator.


COMMON MISTAKE 4:
Assuming all ratios are percentages.

A ratio such as 2:3 is not automatically 2%:3%.


COMMON MISTAKE 5:
Ignoring units.

    60 km/hour

is not the same as:

    60 km/minute


COMMON MISTAKE 6:
Using floating point when exact rational arithmetic is needed.

Use Fraction when exact fractions matter.


COMMON MISTAKE 7:
Dividing by zero.

A denominator, total or base cannot be zero when the formula requires division.
"""


# =============================================================================
# 87. QUICK REFERENCE
# =============================================================================

print("\n" + "=" * 80)
print("QUICK REFERENCE")
print("=" * 80)

print("""
FRACTION:
    numerator / denominator

DECIMAL:
    fraction -> numerator / denominator

PERCENTAGE:
    fraction * 100

PERCENTAGE OF A NUMBER:
    percentage/100 * number

PERCENTAGE CHANGE:
    (new - old) / old * 100

RATIO:
    a:b

SIMPLIFY RATIO:
    divide both terms by GCD

PROPORTION:
    a/b = c/d

CROSS MULTIPLICATION:
    a*d = b*c

DIRECT PROPORTION:
    y = kx

INVERSE PROPORTION:
    y = k/x

SCALE:
    new = old * scale_factor

SCALE FACTOR:
    new / old

RATE:
    quantity / time or quantity / another unit

UNIT RATE:
    total quantity / number of units

DISCOUNT:
    price * discount%

TAX:
    price * tax%

PROFIT:
    selling price - cost price

PROFIT %:
    profit / cost price * 100

LOSS:
    cost price - selling price

LOSS %:
    loss / cost price * 100

CAGR:
    (ending / beginning)^(1/n) - 1

AREA SCALING:
    k²

VOLUME SCALING:
    k³
""")


# =============================================================================
# 88. MINI PRACTICE PROBLEMS
# =============================================================================

"""
Practice these independently.

1. Simplify 24/36.
2. Convert 3/8 to a decimal.
3. Convert 7/20 to a percentage.
4. Convert 45% to a fraction.
5. Simplify 45:60.
6. If 3/5 = x/25, find x.
7. Divide 1,000 in the ratio 2:3.
8. Find 25% of 640.
9. A price increases from 800 to 920. Find percentage increase.
10. A price decreases from 1,500 to 1,200. Find percentage decrease.
11. A product costs ₹240 for 6 kg. Find unit price.
12. A car travels 300 km in 5 hours. Find speed.
13. Scale a recipe from 4 people to 12 people.
14. A quantity increases by 10% and then by 20%. Find total increase.
15. A value increases by 25% and then decreases by 25%. Is it back to
    the original value?
16. 8 workers finish a task in 15 hours. Assuming inverse proportion,
    how long will 12 workers take?
17. A map scale is 1 cm = 10 km. What does 7.5 cm represent?
18. A company's revenue rises from ₹2 million to ₹2.6 million. Find
    percentage growth.
19. Convert 72 km/h to m/s.
20. Explain the difference between percentage points and percentage change.
"""


# =============================================================================
# 89. FINAL LEARNING CHECKLIST
# =============================================================================

topics_mastered = [
    "Fractions",
    "Equivalent fractions",
    "Fraction simplification",
    "Fraction arithmetic",
    "Decimals",
    "Percentages",
    "Percentage change",
    "Ratios",
    "Ratio simplification",
    "Ratio allocation",
    "Proportions",
    "Cross multiplication",
    "Direct proportion",
    "Inverse proportion",
    "Scaling",
    "Scale factors",
    "Rates",
    "Unit rates",
    "Discounts",
    "Taxes",
    "Profit and loss",
    "Compound percentage changes",
    "Floating-point precision",
    "Fraction vs Decimal vs Float",
    "Weighted averages",
    "Normalization",
    "CAGR",
    "Dimensional analysis",
    "Percentage points",
    "Base effects",
    "Error percentages",
    "Python implementation",
    "Excel-oriented formulas",
]

print("\nTopics covered:")

for number, topic in enumerate(topics_mastered, start=1):
    print(f"{number:02d}. {topic}")


print("\n" + "=" * 80)
print("END OF FRACTIONS, RATIOS AND PROPORTIONS GUIDE")
print("=" * 80)
