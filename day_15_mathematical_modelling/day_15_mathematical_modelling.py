"""
Mathematical Modeling
=====================

A comprehensive, executable study file for translating computing problems into
mathematical expressions, variables, constraints, and assumptions.

The examples progress from elementary algebra to optimization, simulation,
probability, resource allocation, numerical methods, sensitivity analysis,
validation, and a complete software-oriented modeling workflow.

Run:
    python mathematical_modeling.py

The program uses only the Python standard library.
"""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass
from itertools import product
from typing import Callable, Iterable


# ============================================================================
# 1. FOUNDATIONS
# ============================================================================

def section(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def subsection(title: str) -> None:
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


def demonstrate_variables_and_expressions() -> None:
    subsection("Variables, constants, expressions, and equations")

    # A variable represents an unknown or changing quantity.
    # A constant represents a fixed quantity in the current model.
    hourly_rate = 25
    hours_worked = 8
    overtime_hours = 2
    overtime_multiplier = 1.5

    # Mathematical expression:
    # income = normal_hours * rate + overtime_hours * rate * multiplier
    income = (
        hours_worked * hourly_rate
        + overtime_hours * hourly_rate * overtime_multiplier
    )

    print(f"Hourly rate: {hourly_rate}")
    print(f"Hours worked: {hours_worked}")
    print(f"Overtime hours: {overtime_hours}")
    print(f"Income: {income}")

    # An equation expresses a relationship that should hold.
    # For a rectangular area:
    # area = length * width
    length = 12
    width = 5
    area = length * width
    print(f"Rectangle area: {area}")

    # A function is a reusable mathematical mapping:
    # f(x) = x^2 + 2x + 1
    def polynomial(x: float) -> float:
        return x * x + 2 * x + 1

    print(f"f(3) = {polynomial(3)}")


# ============================================================================
# 2. TRANSLATING WORD PROBLEMS INTO MATHEMATICS
# ============================================================================

def translate_business_problem() -> None:
    subsection("Translating a business problem into a mathematical model")

    """
    Problem:
        A company sells a product for price p.
        The variable cost per unit is c.
        Fixed costs are F.
        Units sold are q.

    Revenue:
        R(q) = p * q

    Variable cost:
        VC(q) = c * q

    Total cost:
        C(q) = F + c * q

    Profit:
        P(q) = R(q) - C(q)
             = p*q - F - c*q
             = (p-c)*q - F

    Break-even quantity:
        P(q) = 0
        q = F / (p-c)

    The model is useful because it converts a narrative problem into
    equations that can be evaluated, optimized, and tested.
    """

    price = 80.0
    variable_cost = 35.0
    fixed_cost = 18000.0

    def revenue(quantity: float) -> float:
        return price * quantity

    def total_cost(quantity: float) -> float:
        return fixed_cost + variable_cost * quantity

    def profit(quantity: float) -> float:
        return revenue(quantity) - total_cost(quantity)

    contribution_margin = price - variable_cost
    break_even_quantity = fixed_cost / contribution_margin

    print(f"Contribution margin per unit: {contribution_margin:.2f}")
    print(f"Break-even quantity: {break_even_quantity:.2f}")

    for quantity in [0, 100, 250, 500, 1000]:
        print(
            f"q={quantity:4d}, "
            f"revenue={revenue(quantity):9.2f}, "
            f"cost={total_cost(quantity):9.2f}, "
            f"profit={profit(quantity):9.2f}"
        )


# ============================================================================
# 3. ASSUMPTIONS
# ============================================================================

@dataclass(frozen=True)
class SalesModel:
    price: float
    variable_cost: float
    fixed_cost: float
    maximum_demand: float

    def validate(self) -> None:
        if self.price < 0:
            raise ValueError("Price cannot be negative.")
        if self.variable_cost < 0:
            raise ValueError("Variable cost cannot be negative.")
        if self.fixed_cost < 0:
            raise ValueError("Fixed cost cannot be negative.")
        if self.maximum_demand < 0:
            raise ValueError("Maximum demand cannot be negative.")
        if self.price <= self.variable_cost:
            raise ValueError(
                "The selling price must exceed variable cost for positive "
                "unit contribution."
            )

    def profit(self, quantity: float) -> float:
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        if quantity > self.maximum_demand:
            raise ValueError("Quantity exceeds modeled demand.")
        return (
            self.price * quantity
            - self.fixed_cost
            - self.variable_cost * quantity
        )


def demonstrate_assumptions() -> None:
    subsection("Assumptions and model boundaries")

    """
    Every mathematical model simplifies reality.

    Example assumptions:
        1. Selling price is constant.
        2. Variable cost per unit is constant.
        3. Fixed cost does not depend on quantity.
        4. Demand has an upper bound.
        5. Fractional units are mathematically allowed.

    These assumptions make the model tractable. They also determine when
    the model should not be trusted.

    A model should explicitly state its domain and validity conditions.
    """

    model = SalesModel(
        price=80,
        variable_cost=35,
        fixed_cost=18_000,
        maximum_demand=2_000,
    )
    model.validate()

    print(f"Profit at 500 units: {model.profit(500):.2f}")

    try:
        model.profit(2_500)
    except ValueError as error:
        print(f"Expected validation failure: {error}")


# ============================================================================
# 4. VARIABLES, PARAMETERS, DECISION VARIABLES, STATE VARIABLES
# ============================================================================

def demonstrate_model_variable_types() -> None:
    subsection("Parameters, decision variables, and state variables")

    """
    Parameters:
        Values supplied to the model, such as unit cost.

    Decision variables:
        Values selected by an optimization or planning algorithm.

    State variables:
        Values describing the current state of a dynamic system.

    Example inventory model:

        I_t = I_(t-1) + production_t - demand_t

    where:
        I_t       = inventory at time t
        production_t = production decision at time t
        demand_t  = external demand
    """

    initial_inventory = 100
    production = [50, 70, 40]
    demand = [80, 60, 100]

    inventory = initial_inventory

    for period, (produced, consumed) in enumerate(
        zip(production, demand), start=1
    ):
        inventory = inventory + produced - consumed
        print(
            f"period={period}, production={produced}, "
            f"demand={consumed}, ending_inventory={inventory}"
        )


# ============================================================================
# 5. CONSTRAINTS
# ============================================================================

def feasible_production_plans() -> list[tuple[int, int]]:
    """
    Two products are manufactured.

    Variables:
        x = units of product A
        y = units of product B

    Constraints:
        2x + y <= 100       labor/resource constraint
        x + 3y <= 90        machine/resource constraint
        x >= 0
        y >= 0

    Integer quantities are required.
    """
    feasible = []

    for x in range(101):
        for y in range(91):
            if 2 * x + y <= 100 and x + 3 * y <= 90:
                feasible.append((x, y))

    return feasible


def demonstrate_constraints() -> None:
    subsection("Constraints and feasible regions")

    feasible = feasible_production_plans()
    print(f"Number of feasible integer plans: {len(feasible)}")

    for plan in feasible[:10]:
        x, y = plan
        print(
            f"x={x:2d}, y={y:2d}, "
            f"resource_1={2*x+y:3d}, resource_2={x+3*y:3d}"
        )

    invalid_plan = (40, 30)
    x, y = invalid_plan
    print(
        f"Plan {invalid_plan} satisfies resource 1: "
        f"{2*x+y <= 100}"
    )
    print(
        f"Plan {invalid_plan} satisfies resource 2: "
        f"{x+3*y <= 90}"
    )


# ============================================================================
# 6. OBJECTIVE FUNCTIONS AND OPTIMIZATION
# ============================================================================

@dataclass(frozen=True)
class ProductionProblem:
    profit_a: float
    profit_b: float
    labor_a: float
    labor_b: float
    machine_a: float
    machine_b: float
    labor_capacity: float
    machine_capacity: float

    def is_feasible(self, x: int, y: int) -> bool:
        return (
            x >= 0
            and y >= 0
            and self.labor_a * x + self.labor_b * y <= self.labor_capacity
            and self.machine_a * x + self.machine_b * y
            <= self.machine_capacity
        )

    def objective(self, x: int, y: int) -> float:
        return self.profit_a * x + self.profit_b * y


def brute_force_integer_optimization(problem: ProductionProblem) -> tuple[int, int, float]:
    best_plan = (0, 0)
    best_value = float("-inf")

    maximum_x = int(problem.labor_capacity / problem.labor_a)
    maximum_y = int(problem.labor_capacity / problem.labor_b)

    for x in range(maximum_x + 1):
        for y in range(maximum_y + 1):
            if problem.is_feasible(x, y):
                value = problem.objective(x, y)
                if value > best_value:
                    best_plan = (x, y)
                    best_value = value

    return best_plan[0], best_plan[1], best_value


def demonstrate_optimization() -> None:
    subsection("Objective functions and optimization")

    problem = ProductionProblem(
        profit_a=50,
        profit_b=70,
        labor_a=2,
        labor_b=3,
        machine_a=3,
        machine_b=2,
        labor_capacity=100,
        machine_capacity=90,
    )

    x, y, profit = brute_force_integer_optimization(problem)

    print(f"Optimal integer plan: A={x}, B={y}")
    print(f"Maximum modeled profit: {profit:.2f}")

    print(
        "Resource usage:",
        f"labor={problem.labor_a*x + problem.labor_b*y}",
        f"machine={problem.machine_a*x + problem.machine_b*y}",
    )


# ============================================================================
# 7. CONTINUOUS VS DISCRETE MODELS
# ============================================================================

def continuous_break_even(
    fixed_cost: float,
    unit_price: float,
    unit_cost: float,
) -> float:
    if unit_price <= unit_cost:
        raise ValueError("Break-even is undefined for non-positive margin.")
    return fixed_cost / (unit_price - unit_cost)


def demonstrate_continuous_discrete_models() -> None:
    subsection("Continuous and discrete variables")

    """
    Continuous variable:
        x may take values such as 10.2 or 10.25.

    Discrete variable:
        x may only take values from a defined set.

    Example:
        The mathematical break-even quantity can be 400.5 units.
        A factory cannot normally sell half a finished product, so the
        operational quantity may need to be ceil(400.5) = 401.
    """

    continuous_quantity = continuous_break_even(20_000, 100, 50)
    operational_quantity = math.ceil(continuous_quantity)

    print(f"Continuous break-even: {continuous_quantity:.2f}")
    print(f"Minimum whole-unit quantity: {operational_quantity}")


# ============================================================================
# 8. FUNCTIONS AS MATHEMATICAL MAPPINGS
# ============================================================================

def demonstrate_functions() -> None:
    subsection("Functions and functional relationships")

    """
    A mathematical function maps an input to an output.

        y = f(x)

    Example:
        temperature conversion

        C = (F - 32) * 5 / 9
    """

    def fahrenheit_to_celsius(fahrenheit: float) -> float:
        return (fahrenheit - 32) * 5 / 9

    for temperature in [32, 68, 98.6, 212]:
        print(
            f"{temperature:6.1f} F -> "
            f"{fahrenheit_to_celsius(temperature):6.2f} C"
        )

    # A piecewise model can represent different rules in different ranges.
    def shipping_cost(weight_kg: float) -> float:
        if weight_kg < 0:
            raise ValueError("Weight cannot be negative.")
        if weight_kg <= 1:
            return 5
        if weight_kg <= 5:
            return 8
        return 8 + 2 * math.ceil(weight_kg - 5)

    for weight in [0.5, 1, 3, 5, 6.2]:
        print(f"weight={weight:.1f} kg -> cost={shipping_cost(weight):.2f}")


# ============================================================================
# 9. LINEAR AND NONLINEAR MODELS
# ============================================================================

def demonstrate_linear_nonlinear_models() -> None:
    subsection("Linear and nonlinear mathematical relationships")

    x_values = [0, 1, 2, 3, 4]

    linear = [3 * x + 2 for x in x_values]
    quadratic = [x * x + 2 * x + 1 for x in x_values]
    exponential = [2 ** x for x in x_values]
    logarithmic = [math.log2(x + 1) for x in x_values]

    print("x          linear       quadratic     exponential    logarithmic")
    for x, a, b, c, d in zip(
        x_values, linear, quadratic, exponential, logarithmic
    ):
        print(f"{x:<10}{a:<13.2f}{b:<14.2f}{c:<15.2f}{d:<.2f}")


# ============================================================================
# 10. DIMENSIONAL ANALYSIS
# ============================================================================

def demonstrate_units() -> None:
    subsection("Units and dimensional consistency")

    """
    Mathematical expressions should preserve compatible units.

    If:
        distance = speed * time

    then:
        km = (km/hour) * hour

    A common modeling mistake is combining quantities with incompatible
    dimensions.
    """

    speed_km_per_hour = 60
    time_hours = 2.5
    distance_km = speed_km_per_hour * time_hours

    print(f"Distance: {distance_km:.2f} km")

    # Converting units before applying a formula avoids hidden mistakes.
    speed_m_per_second = speed_km_per_hour * 1000 / 3600
    time_seconds = time_hours * 3600
    distance_meters = speed_m_per_second * time_seconds

    print(f"Equivalent distance: {distance_meters:.2f} m")


# ============================================================================
# 11. PROBABILITY AND EXPECTED VALUE
# ============================================================================

def expected_value(outcomes: Iterable[float], probabilities: Iterable[float]) -> float:
    outcomes = list(outcomes)
    probabilities = list(probabilities)

    if len(outcomes) != len(probabilities):
        raise ValueError("Outcome and probability counts must match.")

    if any(p < 0 for p in probabilities):
        raise ValueError("Probabilities cannot be negative.")

    total_probability = sum(probabilities)
    if not math.isclose(total_probability, 1.0, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError("Probabilities must sum to 1.")

    return sum(x * p for x, p in zip(outcomes, probabilities))


def demonstrate_expected_value() -> None:
    subsection("Probabilistic mathematical models")

    outcomes = [1000, 300, -500]
    probabilities = [0.2, 0.5, 0.3]

    value = expected_value(outcomes, probabilities)

    print(f"Expected value: {value:.2f}")


# ============================================================================
# 12. MONTE CARLO SIMULATION
# ============================================================================

def monte_carlo_pi(number_of_samples: int, seed: int = 42) -> float:
    """
    Estimate pi using random points in a unit square.

    Probability interpretation:

        P(point lies inside quarter-circle)
            = area of quarter-circle / area of square
            = (pi / 4) / 1
            = pi / 4

    Therefore:

        pi ≈ 4 * successes / samples
    """
    if number_of_samples <= 0:
        raise ValueError("Sample count must be positive.")

    generator = random.Random(seed)
    inside = 0

    for _ in range(number_of_samples):
        x = generator.random()
        y = generator.random()

        if x * x + y * y <= 1:
            inside += 1

    return 4 * inside / number_of_samples


def demonstrate_monte_carlo() -> None:
    subsection("Simulation as a mathematical approximation")

    for samples in [100, 1_000, 10_000, 100_000]:
        estimate = monte_carlo_pi(samples)
        error = abs(estimate - math.pi)
        print(
            f"samples={samples:6d}, "
            f"estimate={estimate:.8f}, "
            f"absolute_error={error:.8f}"
        )


# ============================================================================
# 13. DIFFERENTIAL CHANGE AND SENSITIVITY
# ============================================================================

def numerical_derivative(
    function: Callable[[float], float],
    x: float,
    step: float = 1e-5,
) -> float:
    """
    Central-difference approximation:

        f'(x) ≈ [f(x+h) - f(x-h)] / (2h)

    Smaller h is not always better because floating-point rounding can
    become significant.
    """
    if step <= 0:
        raise ValueError("Step must be positive.")

    return (function(x + step) - function(x - step)) / (2 * step)


def demonstrate_sensitivity() -> None:
    subsection("Sensitivity analysis and derivatives")

    """
    Suppose profit depends on quantity:

        P(q) = -0.02q^2 + 40q - 5000

    The derivative:

        P'(q) = -0.04q + 40

    indicates how rapidly profit changes with quantity.
    """

    def profit(quantity: float) -> float:
        return -0.02 * quantity**2 + 40 * quantity - 5000

    for quantity in [100, 500, 1000]:
        slope = numerical_derivative(profit, quantity)
        print(
            f"q={quantity:4d}, profit={profit(quantity):10.2f}, "
            f"approximate marginal profit={slope:8.2f}"
        )


# ============================================================================
# 14. NUMERICAL ROOT FINDING
# ============================================================================

def bisection(
    function: Callable[[float], float],
    low: float,
    high: float,
    tolerance: float = 1e-10,
    maximum_iterations: int = 200,
) -> float:
    """
    Bisection solves f(x)=0 when f(low) and f(high) have opposite signs.

    It is slower than some advanced methods but is robust when the
    assumptions are satisfied.
    """
    if low >= high:
        raise ValueError("Lower bound must be less than upper bound.")

    f_low = function(low)
    f_high = function(high)

    if f_low == 0:
        return low
    if f_high == 0:
        return high

    if f_low * f_high > 0:
        raise ValueError("The interval does not bracket a root.")

    for _ in range(maximum_iterations):
        middle = (low + high) / 2
        f_middle = function(middle)

        if abs(f_middle) <= tolerance or abs(high - low) <= tolerance:
            return middle

        if f_low * f_middle <= 0:
            high = middle
            f_high = f_middle
        else:
            low = middle
            f_low = f_middle

    return (low + high) / 2


def demonstrate_root_finding() -> None:
    subsection("Solving equations numerically")

    # Solve x^2 - 10 = 0, whose positive root is sqrt(10).
    root = bisection(lambda x: x * x - 10, 0, 10)
    print(f"Numerical root: {root:.12f}")
    print(f"Reference value: {math.sqrt(10):.12f}")


# ============================================================================
# 15. DISCOUNTED CASH FLOW MODEL
# ============================================================================

def present_value(
    cash_flows: list[float],
    discount_rate: float,
) -> float:
    """
    Present value model:

        PV = Σ CF_t / (1+r)^t

    where:
        CF_t = cash flow at time t
        r    = discount rate
    """
    if discount_rate <= -1:
        raise ValueError("Discount rate must be greater than -100%.")

    return sum(
        cash_flow / ((1 + discount_rate) ** period)
        for period, cash_flow in enumerate(cash_flows, start=1)
    )


def demonstrate_financial_model() -> None:
    subsection("Financial mathematical model")

    initial_investment = -100_000
    future_cash_flows = [30_000, 35_000, 40_000, 45_000]
    discount_rate = 0.10

    pv = present_value(future_cash_flows, discount_rate)
    npv = initial_investment + pv

    print(f"Present value of future cash flows: {pv:,.2f}")
    print(f"NPV: {npv:,.2f}")


# ============================================================================
# 16. QUEUEING MODEL
# ============================================================================

@dataclass
class QueueObservation:
    arrival_time: float
    service_start: float
    service_end: float

    @property
    def waiting_time(self) -> float:
        return self.service_start - self.arrival_time

    @property
    def time_in_system(self) -> float:
        return self.service_end - self.arrival_time


def simulate_single_server_queue(
    interarrival_times: list[float],
    service_times: list[float],
) -> list[QueueObservation]:
    """
    Basic deterministic queue model.

    For customer i:

        arrival_i = arrival_(i-1) + interarrival_i

        service_start_i =
            max(arrival_i, service_end_(i-1))

        service_end_i =
            service_start_i + service_time_i

    This is a discrete-event model.
    """
    if len(interarrival_times) != len(service_times):
        raise ValueError("Input sequences must have equal length.")

    observations = []
    current_arrival = 0.0
    previous_service_end = 0.0

    for interarrival, service in zip(interarrival_times, service_times):
        if interarrival < 0 or service < 0:
            raise ValueError("Times cannot be negative.")

        current_arrival += interarrival
        service_start = max(current_arrival, previous_service_end)
        service_end = service_start + service

        observations.append(
            QueueObservation(
                arrival_time=current_arrival,
                service_start=service_start,
                service_end=service_end,
            )
        )

        previous_service_end = service_end

    return observations


def demonstrate_queueing_model() -> None:
    subsection("Queueing and event-based modeling")

    arrivals = [0, 2, 1, 1.5, 3]
    services = [2.5, 3, 1, 4, 2]

    observations = simulate_single_server_queue(arrivals, services)

    for index, observation in enumerate(observations, start=1):
        print(
            f"customer={index}, "
            f"arrival={observation.arrival_time:.1f}, "
            f"start={observation.service_start:.1f}, "
            f"end={observation.service_end:.1f}, "
            f"wait={observation.waiting_time:.1f}"
        )


# ============================================================================
# 17. GRAPH MODEL
# ============================================================================

def shortest_path_dijkstra(
    graph: dict[str, list[tuple[str, float]]],
    start: str,
) -> dict[str, float]:
    """
    Dijkstra's algorithm models shortest-path optimization.

    Mathematical interpretation:

        distance(v) = minimum accumulated edge weight
                      from start to v

    The edge weights can represent time, cost, distance, energy, or another
    measurable quantity.
    """
    import heapq

    distances = {node: float("inf") for node in graph}
    distances[start] = 0.0

    queue: list[tuple[float, str]] = [(0.0, start)]

    while queue:
        current_distance, current_node = heapq.heappop(queue)

        if current_distance > distances[current_node]:
            continue

        for neighbor, weight in graph[current_node]:
            if weight < 0:
                raise ValueError("Dijkstra requires non-negative weights.")

            candidate = current_distance + weight

            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                heapq.heappush(queue, (candidate, neighbor))

    return distances


def demonstrate_graph_model() -> None:
    subsection("Graph-based mathematical models")

    graph = {
        "A": [("B", 4), ("C", 2)],
        "B": [("C", 1), ("D", 5)],
        "C": [("B", 1), ("D", 8), ("E", 10)],
        "D": [("E", 2)],
        "E": [],
    }

    distances = shortest_path_dijkstra(graph, "A")

    for node, distance in distances.items():
        print(f"Shortest cost A -> {node}: {distance}")


# ============================================================================
# 18. REGRESSION MODEL
# ============================================================================

@dataclass(frozen=True)
class LinearRegressionModel:
    slope: float
    intercept: float

    def predict(self, x: float) -> float:
        return self.slope * x + self.intercept


def fit_simple_linear_regression(
    x_values: list[float],
    y_values: list[float],
) -> LinearRegressionModel:
    """
    Ordinary least squares for:

        y = beta_0 + beta_1*x

    The estimated slope is:

        beta_1 = Σ[(x_i-x_bar)(y_i-y_bar)] / Σ[(x_i-x_bar)^2]

    The intercept is:

        beta_0 = y_bar - beta_1*x_bar
    """
    if len(x_values) != len(y_values):
        raise ValueError("x and y must have equal lengths.")
    if len(x_values) < 2:
        raise ValueError("At least two observations are required.")

    x_bar = statistics.mean(x_values)
    y_bar = statistics.mean(y_values)

    numerator = sum(
        (x - x_bar) * (y - y_bar)
        for x, y in zip(x_values, y_values)
    )

    denominator = sum(
        (x - x_bar) ** 2
        for x in x_values
    )

    if denominator == 0:
        raise ValueError("Predictor values must not all be identical.")

    slope = numerator / denominator
    intercept = y_bar - slope * x_bar

    return LinearRegressionModel(slope, intercept)


def demonstrate_regression() -> None:
    subsection("Data-driven mathematical modeling")

    advertising_spend = [1, 2, 3, 4, 5, 6]
    sales = [12, 18, 25, 29, 38, 43]

    model = fit_simple_linear_regression(advertising_spend, sales)

    print(f"Slope: {model.slope:.4f}")
    print(f"Intercept: {model.intercept:.4f}")

    for spend in [2.5, 7]:
        print(
            f"Predicted sales for spend={spend}: "
            f"{model.predict(spend):.2f}"
        )


# ============================================================================
# 19. MODEL VALIDATION
# ============================================================================

def mean_absolute_error(
    actual: list[float],
    predicted: list[float],
) -> float:
    if len(actual) != len(predicted):
        raise ValueError("Input lengths must match.")
    if not actual:
        raise ValueError("At least one observation is required.")

    return statistics.mean(
        abs(a - p) for a, p in zip(actual, predicted)
    )


def root_mean_squared_error(
    actual: list[float],
    predicted: list[float],
) -> float:
    if len(actual) != len(predicted):
        raise ValueError("Input lengths must match.")
    if not actual:
        raise ValueError("At least one observation is required.")

    return math.sqrt(
        statistics.mean(
            (a - p) ** 2 for a, p in zip(actual, predicted)
        )
    )


def demonstrate_validation() -> None:
    subsection("Model validation and error measurement")

    actual = [10, 20, 30, 40]
    predicted = [11, 18, 31, 37]

    print(f"MAE: {mean_absolute_error(actual, predicted):.4f}")
    print(f"RMSE: {root_mean_squared_error(actual, predicted):.4f}")


# ============================================================================
# 20. SENSITIVITY ANALYSIS
# ============================================================================

def demonstrate_parameter_sensitivity() -> None:
    subsection("Parameter sensitivity")

    """
    A model can be structurally correct but highly sensitive to uncertain
    inputs.

    For profit:

        P(q, p, c, F) = (p-c)q - F

    Changing price p, cost c, or fixed cost F changes the output.
    """

    quantity = 1_000
    price_values = [70, 80, 90]
    cost_values = [30, 35, 40]

    print("Profit sensitivity:")
    for price, cost in product(price_values, cost_values):
        profit = (price - cost) * quantity - 18_000
        print(
            f"price={price}, variable_cost={cost}, "
            f"profit={profit:,.2f}"
        )


# ============================================================================
# 21. SCENARIO ANALYSIS
# ============================================================================

def demonstrate_scenarios() -> None:
    subsection("Scenario analysis")

    scenarios = {
        "pessimistic": {"demand": 600, "price": 70, "cost": 40},
        "base": {"demand": 1_000, "price": 80, "cost": 35},
        "optimistic": {"demand": 1_400, "price": 90, "cost": 30},
    }

    fixed_cost = 18_000

    for name, assumptions in scenarios.items():
        demand = assumptions["demand"]
        price = assumptions["price"]
        cost = assumptions["cost"]

        revenue = demand * price
        total_cost = fixed_cost + demand * cost
        profit = revenue - total_cost

        print(
            f"{name:12s}: demand={demand:4d}, "
            f"revenue={revenue:10.2f}, "
            f"cost={total_cost:10.2f}, "
            f"profit={profit:10.2f}"
        )


# ============================================================================
# 22. DIMENSIONAL AND LOGICAL EDGE CASES
# ============================================================================

def safe_percentage_change(
    old_value: float,
    new_value: float,
) -> float:
    """
    Percentage change:

        ((new - old) / old) * 100

    If old_value is zero, the ordinary percentage-change formula is
    undefined. Returning infinity would hide the mathematical issue, so
    this function raises an explicit exception.
    """
    if old_value == 0:
        raise ZeroDivisionError(
            "Percentage change is undefined when the baseline is zero."
        )

    return ((new_value - old_value) / old_value) * 100


def demonstrate_edge_cases() -> None:
    subsection("Edge cases and exceptions")

    test_cases = [
        (100, 120),
        (100, 80),
        (-100, -120),
        (0, 100),
    ]

    for old_value, new_value in test_cases:
        try:
            change = safe_percentage_change(old_value, new_value)
            print(
                f"{old_value:6.1f} -> {new_value:6.1f}: "
                f"{change:8.2f}%"
            )
        except ZeroDivisionError as error:
            print(f"{old_value:6.1f} -> {new_value:6.1f}: {error}")


# ============================================================================
# 23. FLOATING-POINT MODELING
# ============================================================================

def demonstrate_numerical_precision() -> None:
    subsection("Numerical precision and floating-point limitations")

    """
    Binary floating-point cannot exactly represent many decimal fractions.

    Therefore:
        0.1 + 0.2

    is not necessarily represented as exactly 0.3.

    Mathematical models implemented on computers must distinguish:
        mathematical equality
    from:
        machine-level floating-point equality.
    """

    result = 0.1 + 0.2

    print(f"0.1 + 0.2 = {result!r}")
    print(f"Direct equality with 0.3: {result == 0.3}")
    print(
        "Tolerance-based equality:",
        math.isclose(result, 0.3, rel_tol=1e-12, abs_tol=1e-12),
    )


# ============================================================================
# 24. OPTIMIZATION WITH MULTIPLE CONSTRAINTS
# ============================================================================

@dataclass(frozen=True)
class InvestmentOption:
    name: str
    expected_return: float
    minimum_allocation: float
    maximum_allocation: float


def optimize_investment_grid(
    options: list[InvestmentOption],
    budget: float,
    step: float,
) -> tuple[dict[str, float], float]:
    """
    Educational grid-search optimization.

    The objective is:

        maximize Σ allocation_i * return_i

    subject to:

        Σ allocation_i <= budget
        min_i <= allocation_i <= max_i

    This is intentionally implemented without an optimization package to
    expose the modeling mechanics. For large continuous problems, this
    brute-force approach becomes computationally impractical.
    """
    if budget < 0:
        raise ValueError("Budget cannot be negative.")
    if step <= 0:
        raise ValueError("Step must be positive.")

    best_allocation: dict[str, float] = {}
    best_return = float("-inf")

    possible_allocations: list[list[float]] = []

    for option in options:
        values = []
        current = option.minimum_allocation

        while current <= option.maximum_allocation + 1e-12:
            values.append(round(current, 10))
            current += step

        possible_allocations.append(values)

    for combination in product(*possible_allocations):
        total_allocation = sum(combination)

        if total_allocation > budget + 1e-12:
            continue

        total_return = sum(
            allocation * option.expected_return
            for allocation, option in zip(combination, options)
        )

        if total_return > best_return:
            best_return = total_return
            best_allocation = {
                option.name: allocation
                for option, allocation in zip(options, combination)
            }

    if not best_allocation:
        raise ValueError("No feasible allocation exists.")

    return best_allocation, best_return


def demonstrate_multi_constraint_optimization() -> None:
    subsection("Multi-variable optimization")

    options = [
        InvestmentOption("A", 0.08, 0, 600),
        InvestmentOption("B", 0.12, 0, 700),
        InvestmentOption("C", 0.15, 0, 500),
    ]

    allocation, expected_return = optimize_investment_grid(
        options,
        budget=1_000,
        step=100,
    )

    print("Allocation:", allocation)
    print(f"Expected return: {expected_return:.2f}")


# ============================================================================
# 25. MODEL DECOMPOSITION
# ============================================================================

def demonstrate_decomposition() -> None:
    subsection("Decomposing a large problem into smaller mathematical models")

    """
    A production system can be decomposed into:

        demand model
            ↓
        capacity model
            ↓
        inventory model
            ↓
        cost model
            ↓
        profit model

    Each function below represents one layer.
    """

    def demand(price: float) -> float:
        return max(0.0, 2_000 - 15 * price)

    def production_capacity(workers: int) -> float:
        return workers * 80

    def inventory_after_period(
        opening_inventory: float,
        production: float,
        sales: float,
    ) -> float:
        return opening_inventory + production - sales

    def profit(
        units_sold: float,
        price: float,
        unit_cost: float,
        fixed_cost: float,
    ) -> float:
        return units_sold * (price - unit_cost) - fixed_cost

    price = 75
    workers = 12
    opening_inventory = 200

    expected_demand = demand(price)
    capacity = production_capacity(workers)
    production = min(expected_demand, capacity)

    ending_inventory = inventory_after_period(
        opening_inventory,
        production,
        expected_demand,
    )

    modeled_profit = profit(
        units_sold=expected_demand,
        price=price,
        unit_cost=30,
        fixed_cost=20_000,
    )

    print(f"Demand: {expected_demand:.2f}")
    print(f"Production capacity: {capacity:.2f}")
    print(f"Production: {production:.2f}")
    print(f"Ending inventory: {ending_inventory:.2f}")
    print(f"Profit: {modeled_profit:.2f}")


# ============================================================================
# 26. MODEL GOVERNANCE AND VALIDATION RULES
# ============================================================================

def validate_probability_distribution(
    probabilities: list[float],
) -> None:
    if not probabilities:
        raise ValueError("Probability distribution cannot be empty.")

    if any(not math.isfinite(p) for p in probabilities):
        raise ValueError("Probabilities must be finite.")

    if any(p < 0 or p > 1 for p in probabilities):
        raise ValueError("Every probability must be between 0 and 1.")

    if not math.isclose(sum(probabilities), 1.0, abs_tol=1e-9):
        raise ValueError("Probabilities must sum to 1.")


def demonstrate_model_validation_rules() -> None:
    subsection("Formal validation rules")

    valid = [0.2, 0.3, 0.5]
    validate_probability_distribution(valid)
    print("Valid probability distribution accepted.")

    invalid = [0.2, 0.4, 0.5]
    try:
        validate_probability_distribution(invalid)
    except ValueError as error:
        print(f"Invalid distribution rejected: {error}")


# ============================================================================
# 27. COMPLETE MODELING WORKFLOW
# ============================================================================

@dataclass
class ModelingWorkflow:
    """
    A structured representation of a modeling workflow.

    The workflow mirrors a common analytical process:

        real problem
            -> abstraction
            -> variables
            -> assumptions
            -> equations
            -> constraints
            -> objective
            -> computation
            -> validation
            -> interpretation
    """

    problem_statement: str
    variables: dict[str, str]
    assumptions: list[str]
    constraints: list[str]
    objective: str

    def describe(self) -> None:
        print("\nProblem:")
        print(self.problem_statement)

        print("\nVariables:")
        for name, meaning in self.variables.items():
            print(f"  {name}: {meaning}")

        print("\nAssumptions:")
        for assumption in self.assumptions:
            print(f"  - {assumption}")

        print("\nConstraints:")
        for constraint in self.constraints:
            print(f"  - {constraint}")

        print("\nObjective:")
        print(f"  {self.objective}")


def demonstrate_complete_workflow() -> None:
    subsection("Complete mathematical-modeling workflow")

    workflow = ModelingWorkflow(
        problem_statement=(
            "Determine the number of two products to manufacture "
            "to maximize contribution profit."
        ),
        variables={
            "x": "units of product A",
            "y": "units of product B",
        },
        assumptions=[
            "Unit contribution margins are known and constant.",
            "Resource consumption per unit is constant.",
            "Products are indivisible.",
            "Demand limits are ignored in this simplified model.",
        ],
        constraints=[
            "2x + 3y <= 100 labor units",
            "3x + 2y <= 90 machine units",
            "x >= 0",
            "y >= 0",
            "x and y are integers",
        ],
        objective="maximize 50x + 70y",
    )

    workflow.describe()

    problem = ProductionProblem(
        profit_a=50,
        profit_b=70,
        labor_a=2,
        labor_b=3,
        machine_a=3,
        machine_b=2,
        labor_capacity=100,
        machine_capacity=90,
    )

    x, y, objective = brute_force_integer_optimization(problem)

    print("\nComputed solution:")
    print(f"  x = {x}")
    print(f"  y = {y}")
    print(f"  objective = {objective}")


# ============================================================================
# 28. SECURITY AND ROBUSTNESS CONSIDERATIONS
# ============================================================================

def demonstrate_safe_model_input() -> None:
    subsection("Safe input handling")

    """
    Mathematical modeling systems often receive values from users,
    spreadsheets, APIs, or databases.

    Never assume external values are valid.

    Validate:
        - type
        - finite numeric status
        - domain
        - units
        - bounds
        - logical relationships

    This example avoids eval() for mathematical input. Evaluating arbitrary
    user-provided strings as Python code is a serious security risk.
    """

    def validate_positive_finite(value: float, name: str) -> float:
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite.")
        if value <= 0:
            raise ValueError(f"{name} must be positive.")
        return value

    values = [100.0, float("inf"), -5.0]

    for value in values:
        try:
            checked = validate_positive_finite(value, "price")
            print(f"Accepted price: {checked}")
        except ValueError as error:
            print(f"Rejected value {value!r}: {error}")


# ============================================================================
# 29. PERFORMANCE CONSIDERATIONS
# ============================================================================

def benchmark_search_space_size() -> None:
    subsection("Performance and computational complexity")

    """
    Brute-force search over n variables with k possible values each has
    approximately:

        O(k^n)

    combinations.

    This exponential growth is why mathematical optimization often uses:
        - linear programming
        - integer programming
        - dynamic programming
        - branch and bound
        - convex optimization
        - heuristics
        - approximation algorithms
        - decomposition methods

    The code below demonstrates how quickly a Cartesian search space grows.
    """

    for variables in range(1, 9):
        combinations = 10 ** variables
        print(
            f"variables={variables}, "
            f"10 choices each -> {combinations:,} combinations"
        )


# ============================================================================
# 30. TESTING MATHEMATICAL MODELS
# ============================================================================

def run_assertion_tests() -> None:
    subsection("Automated tests for mathematical models")

    model = SalesModel(
        price=80,
        variable_cost=35,
        fixed_cost=18_000,
        maximum_demand=2_000,
    )

    assert model.profit(0) == -18_000
    assert math.isclose(model.profit(1), -17_955)
    assert continuous_break_even(18_000, 80, 35) == 400

    assert math.isclose(
        numerical_derivative(lambda x: x * x, 5),
        10,
        abs_tol=1e-4,
    )

    root = bisection(lambda x: x * x - 25, 0, 10)
    assert math.isclose(root, 5, abs_tol=1e-8)

    assert math.isclose(
        expected_value([0, 100], [0.75, 0.25]),
        25,
    )

    print("All model assertions passed.")


# ============================================================================
# 31. INTERPRETATION OF A MODEL
# ============================================================================

def demonstrate_interpretation() -> None:
    subsection("Mathematical output versus business interpretation")

    """
    A numerical answer is not automatically a decision.

    Example:
        Model output:
            optimal production = 300 units

    Interpretation requires asking:
        - Is demand actually available?
        - Can the organization produce the quantity?
        - Are the cost assumptions realistic?
        - Is the objective function appropriate?
        - Are there regulatory constraints?
        - How sensitive is the answer to uncertain parameters?

    Modeling separates computation from judgment.
    """

    production = 300
    unit_profit = 45

    print(f"Modeled production: {production} units")
    print(f"Modeled contribution: {production * unit_profit:,.2f}")
    print(
        "Interpretation requires checking whether the assumptions and "
        "constraints remain valid outside the mathematical model."
    )


# ============================================================================
# 32. MAIN STUDY PROGRAM
# ============================================================================

def main() -> None:
    section("MATHEMATICAL MODELING: FROM COMPUTING PROBLEMS TO MATHEMATICS")

    demonstrate_variables_and_expressions()
    translate_business_problem()
    demonstrate_assumptions()
    demonstrate_model_variable_types()
    demonstrate_constraints()
    demonstrate_optimization()
    demonstrate_continuous_discrete_models()
    demonstrate_functions()
    demonstrate_linear_nonlinear_models()
    demonstrate_units()
    demonstrate_expected_value()
    demonstrate_monte_carlo()
    demonstrate_sensitivity()
    demonstrate_root_finding()
    demonstrate_financial_model()
    demonstrate_queueing_model()
    demonstrate_graph_model()
    demonstrate_regression()
    demonstrate_validation()
    demonstrate_parameter_sensitivity()
    demonstrate_scenarios()
    demonstrate_edge_cases()
    demonstrate_numerical_precision()
    demonstrate_multi_constraint_optimization()
    demonstrate_decomposition()
    demonstrate_model_validation_rules()
    demonstrate_complete_workflow()
    demonstrate_safe_model_input()
    benchmark_search_space_size()
    run_assertion_tests()
    demonstrate_interpretation()

    section("END OF STUDY PROGRAM")
    print(
        "The examples demonstrate how a real-world computing problem can be "
        "abstracted into variables, parameters, assumptions, equations, "
        "constraints, objectives, algorithms, simulations, and validation."
    )


if __name__ == "__main__":
    main()
