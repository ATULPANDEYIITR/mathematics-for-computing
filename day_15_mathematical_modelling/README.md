# Mathematical modeling

## Introduction

Mathematical modeling is the process of translating a real-world or computing problem into a structured mathematical representation.

A computing problem may initially be expressed in natural language:

- determine how many products to manufacture
- estimate future demand
- find the shortest route
- calculate the cost of a transaction
- determine when a business reaches break-even
- allocate limited resources
- predict an outcome from historical observations
- simulate a queue
- evaluate investment alternatives

Mathematical modeling converts such descriptions into formal objects such as variables, parameters, equations, inequalities, functions, constraints, probability distributions, objective functions, and assumptions.

The essential transformation is:

`real problem → abstraction → mathematical representation → computational procedure → result → interpretation`

The mathematical model is not the real system itself. It is a simplified representation designed for a particular purpose.

The three implementations in this repository demonstrate this process from different programming perspectives:

- Python emphasizes mathematical experimentation, numerical methods, simulations, data-oriented modeling, and reusable analytical functions.
- JavaScript emphasizes executable application-oriented models, validation, asynchronous model evaluation, and algorithmic implementation.
- C++ develops a more structured industry-style production planning case study using classes, strong data organization, explicit validation, integer optimization, scenario analysis, and sensitivity analysis.

## Fundamental concepts

### Mathematical abstraction

Abstraction removes details that are not necessary for the particular question being answered.

Suppose a factory produces two products. A real factory contains employees, machines, suppliers, customers, inventories, transportation systems, maintenance schedules, contracts, taxes, and many other details.

A first mathematical model may represent only:

- product A quantity
- product B quantity
- labor consumption
- machine consumption
- available labor
- available machine capacity
- contribution profit
- demand limits

The purpose of abstraction is not to ignore reality arbitrarily. It is to retain the variables and relationships that materially affect the decision being modeled.

### Variables

A variable represents a quantity that can change or is unknown.

For example:

`x = number of units of product A`

`y = number of units of product B`

Variables can represent:

- quantities
- prices
- time
- distances
- probabilities
- inventory
- temperatures
- populations
- states of a system
- decisions

A variable may be continuous or discrete.

A continuous variable can take values such as `2.5`, `3.17`, or `10.001`.

A discrete variable can take only separated values. For example, the number of servers or completed products is normally an integer.

### Parameters

Parameters are values supplied to a model that characterize the environment or assumptions.

For a manufacturing model:

`selling price = 80`

`variable cost = 30`

`labor per unit = 2`

`machine time per unit = 3`

`labor capacity = 100`

These values may be fixed for one model run but can be changed during scenario analysis.

### Decision variables

A decision variable represents a quantity selected by a planning or optimization procedure.

In the production case study:

`x = production quantity of product A`

`y = production quantity of product B`

The optimization algorithm searches for values of `x` and `y` that satisfy the constraints while maximizing the objective.

### State variables

A state variable describes the condition of a system at a particular point in time.

An inventory model can be written as:

`I_t = I_(t-1) + P_t - D_t`

where:

- `I_t` is ending inventory at time `t`
- `I_(t-1)` is previous inventory
- `P_t` is production
- `D_t` is demand

State variables are especially important in dynamic systems and simulations.

## Expressions, equations, and inequalities

### Expressions

An expression computes a quantity.

For example:

`revenue = price × quantity`

or:

`profit = revenue - cost`

An expression does not necessarily assert that two quantities are equal.

### Equations

An equation states that two expressions have the same value.

For example:

`area = length × width`

or:

`profit = price × quantity - cost`

Equations can define relationships between variables.

### Inequalities

Inequalities express limits or conditions.

Examples include:

`2x + 3y ≤ 100`

`x ≥ 0`

`x ≤ maximum_demand`

Constraints are frequently represented using inequalities because real systems contain capacity limits.

## Functions

A function describes a relationship between inputs and outputs.

The general form is:

`y = f(x)`

For example:

`f(x) = x² + 2x + 1`

A business model may use:

`Revenue(q) = price × q`

A shipping model may be piecewise:

- one price for weights up to 1 kg
- another price for weights from 1 kg to 5 kg
- a different rule above 5 kg

Functions are fundamental because they allow a model to express how one quantity depends on another.

## Assumptions

Every practical mathematical model makes assumptions.

The production case study assumes:

- selling prices remain constant within a scenario
- variable costs remain constant per unit
- resource consumption is linear
- products are indivisible
- demand limits are known
- fixed costs do not depend on production quantity

These assumptions simplify the problem.

The quality of a model depends partly on whether its assumptions are appropriate for its intended use.

An assumption is not automatically a flaw. A simplified model can be highly useful if its simplifications do not materially distort the decision.

A model becomes unreliable when important relationships have been omitted or assumptions are applied outside their valid domain.

## Constraints

Constraints define the feasible region of the model.

For two products, suppose:

`x = units of product A`

`y = units of product B`

and the factory has two resources.

Labor:

`2x + 3y ≤ 100`

Machine capacity:

`3x + 2y ≤ 90`

Non-negativity:

`x ≥ 0`

`y ≥ 0`

Demand limits:

`x ≤ demand_A`

`y ≤ demand_B`

Only combinations satisfying all constraints are feasible.

The Python and JavaScript implementations enumerate feasible production plans. The C++ case study places the same logic inside a dedicated production planning class.

## Objective functions

An objective function specifies what the model is trying to optimize or evaluate.

For production planning:

`Profit(x,y) = contribution_A × x + contribution_B × y - fixed_cost`

If product A has price 80 and variable cost 30:

`contribution_A = 80 - 30 = 50`

If product B has price 100 and variable cost 40:

`contribution_B = 100 - 40 = 60`

The objective becomes:

`maximize 50x + 60y - fixed_cost`

Common objectives include:

- maximize profit
- minimize cost
- minimize delivery time
- maximize throughput
- minimize energy consumption
- maximize expected return
- minimize prediction error
- minimize resource usage

A model without an explicit objective can still describe a system, but an optimization model requires a clearly defined objective.

## Feasible and infeasible solutions

A feasible solution satisfies every constraint.

An infeasible solution violates at least one constraint.

For example:

`x = 10`

`y = 20`

might satisfy resource constraints, while a larger combination could exceed machine capacity.

The feasible region is therefore the set of all allowable solutions.

Optimization operates within this feasible region.

A common modeling mistake is to optimize an objective without checking feasibility. A mathematically attractive answer is useless if the system cannot actually implement it.

## Continuous versus discrete modeling

A mathematical equation can produce a fractional answer even when the real decision must be an integer.

Suppose:

`break_even = fixed_cost / (price - variable_cost)`

With:

`fixed_cost = 18000`

`price = 80`

`variable_cost = 35`

the result is:

`400 units`

If the result were `400.5`, the mathematical answer would still be valid as a continuous quantity, but an operation that requires complete units would need an integer rule such as rounding upward.

This distinction is important in:

- manufacturing
- staffing
- vehicle allocation
- server provisioning
- project selection
- facility location
- scheduling

## Linear and nonlinear models

A linear relationship has variables only to the first power and does not multiply decision variables together.

Example:

`y = 3x + 2`

A nonlinear relationship can contain:

- powers
- products of variables
- logarithms
- exponentials
- trigonometric functions
- other nonlinear transformations

Examples:

`y = x²`

`y = e^x`

`y = log(x)`

`y = xy`

Nonlinear models can represent reality more closely but may be computationally harder to solve.

The Python implementation demonstrates linear, quadratic, exponential, and logarithmic relationships.

## Dimensional consistency

Units provide an important modeling validation mechanism.

For:

`distance = speed × time`

the units are:

`km = (km/hour) × hour`

The hours cancel appropriately.

A model can contain mathematically valid arithmetic while being physically meaningless because of incompatible units.

Examples of common dimensional mistakes include:

- adding meters to kilograms
- multiplying a yearly quantity by an hourly rate without conversion
- confusing percentages with decimal rates
- mixing miles and kilometers
- mixing seconds and hours

Dimensional analysis is therefore both a mathematical and debugging technique.

## Break-even modeling

A basic profit model can be written as:

`Profit(q) = (price - variable_cost)q - fixed_cost`

At break-even:

`Profit(q) = 0`

Therefore:

`q = fixed_cost / (price - variable_cost)`

This equation demonstrates an important modeling principle: a natural-language business question can often be translated into an equation before any code is written.

The model also exposes a critical edge case.

If:

`price ≤ variable_cost`

then the contribution margin is zero or negative.

The ordinary positive break-even formula is no longer meaningful because every additional unit fails to recover fixed costs.

The implementations explicitly validate this condition.

## Probability and expected value

Uncertainty can be represented mathematically with probability.

If possible outcomes are `x_i` and probabilities are `p_i`, expected value is:

`E[X] = Σ x_i p_i`

with:

`Σ p_i = 1`

For outcomes:

`1000, 300, -500`

and probabilities:

`0.2, 0.5, 0.3`

the expected value is:

`1000(0.2) + 300(0.5) - 500(0.3)`

which equals:

`250`

Expected value is useful for comparing uncertain alternatives, but it does not describe the complete distribution of outcomes.

Two alternatives can have the same expected value but very different risks.

## Simulation

Some systems are too complicated to solve analytically or are more naturally represented as sequences of events.

Simulation uses a computational process to approximate system behavior.

The Python and JavaScript implementations estimate π with Monte Carlo simulation.

The mathematical reasoning is:

`P(point is inside quarter-circle) = π/4`

Therefore:

`π ≈ 4 × successes / total_samples`

As the number of samples increases, the estimate tends to become more stable, although random variation remains.

Simulation is useful for:

- queues
- financial uncertainty
- inventory
- network traffic
- reliability
- risk analysis
- logistics
- population models
- operational systems

Simulation does not eliminate assumptions. It executes the assumptions repeatedly under different simulated conditions.

## Numerical derivatives

The derivative represents a rate of change.

For:

`P(q) = -0.02q² + 40q - 5000`

the analytical derivative is:

`P'(q) = -0.04q + 40`

The implementations also demonstrate numerical differentiation using:

`f'(x) ≈ [f(x+h) - f(x-h)] / (2h)`

This is useful when a closed-form derivative is unavailable or when the function is represented only computationally.

Numerical methods introduce approximation error and can be sensitive to the choice of step size.

## Numerical root finding

Many computing problems require solving:

`f(x) = 0`

The bisection method finds a root when an interval contains a sign change.

The Python, JavaScript, and conceptual material use the equation:

`x² - 10 = 0`

The positive solution is:

`sqrt(10)`

Bisection repeatedly divides the interval and retains the half containing the root.

Its main advantage is robustness. Its disadvantage is that it can converge more slowly than methods such as Newton's method.

## Financial modeling

Discounted cash flow models translate future cash flows into present values.

A basic present value equation is:

`PV = Σ CF_t / (1+r)^t`

where:

- `CF_t` is the cash flow in period `t`
- `r` is the discount rate

Net present value adds the initial investment:

`NPV = initial_investment + PV(future_cash_flows)`

The Python and JavaScript implementations demonstrate this calculation.

Financial models require special care around:

- percentage versus decimal representation
- timing conventions
- negative cash flows
- discount-rate assumptions
- inflation
- taxes
- terminal value
- changing risk
- scenario uncertainty

A mathematically correct formula can still produce a poor decision if the input assumptions are inappropriate.

## Queueing models

A queueing system can be represented using arrival and service events.

For customer `i`:

`arrival_i = arrival_(i-1) + interarrival_i`

The service begins at:

`service_start_i = max(arrival_i, previous_service_end)`

Service ends at:

`service_end_i = service_start_i + service_time_i`

Waiting time is:

`waiting_i = service_start_i - arrival_i`

The Python and JavaScript implementations use this discrete-event representation.

Queue models can represent:

- customer service
- network requests
- call centers
- hospital systems
- database workloads
- CPU scheduling
- cloud services

The model can be extended to multiple servers, priority queues, stochastic arrivals, service distributions, abandonment, and finite capacity.

## Graph-based models

Many computing problems can be represented as graphs.

A graph consists of:

- vertices or nodes
- edges connecting nodes
- optional weights associated with edges

Weights may represent:

- distance
- cost
- time
- energy
- risk

The Python and JavaScript implementations use Dijkstra's algorithm to solve a shortest-path problem.

The mathematical objective is:

`minimize total path weight`

subject to the requirement that the path connects the starting node to the destination.

Dijkstra's algorithm requires non-negative edge weights.

Using it with negative edges violates its assumptions.

## Regression models

Regression converts observations into a mathematical relationship.

A simple linear regression model is:

`y = β_0 + β_1x`

where:

- `β_0` is the intercept
- `β_1` is the slope

The ordinary least-squares slope is:

`β_1 = Σ[(x_i-x̄)(y_i-ȳ)] / Σ[(x_i-x̄)²]`

and:

`β_0 = ȳ - β_1x̄`

The Python and JavaScript implementations calculate these values directly.

Regression is useful for estimating relationships from data, but correlation does not automatically imply causation.

A regression model can also perform poorly when:

- the sample is biased
- important variables are omitted
- relationships are nonlinear
- observations are dependent
- the model extrapolates beyond observed data
- outliers dominate the fit

## Model validation

A mathematical model should be tested.

Validation can include:

- domain validation
- boundary tests
- mathematical invariants
- unit consistency
- expected-value tests
- numerical tolerance tests
- scenario testing
- comparison with historical observations
- sensitivity analysis
- error metrics

The Python and JavaScript programs include executable assertions.

The C++ case study uses assertions and explicit validation functions.

For predictive models, common error metrics include mean absolute error:

`MAE = (1/n) Σ |y_i - ŷ_i|`

and root mean squared error:

`RMSE = sqrt((1/n) Σ(y_i - ŷ_i)²)`

MAE is easier to interpret in the original units. RMSE penalizes larger errors more strongly.

## Sensitivity analysis

Sensitivity analysis investigates how the output changes when inputs change.

For:

`P(q,p,c,F) = (p-c)q - F`

the model is sensitive to:

- quantity `q`
- price `p`
- variable cost `c`
- fixed cost `F`

The Python, JavaScript, and C++ implementations change parameters and observe the resulting outputs.

Sensitivity analysis is especially important when model parameters are uncertain.

A recommendation that remains stable across reasonable parameter ranges is generally more robust than one that changes drastically after a small parameter change.

## Scenario analysis

Scenario analysis changes multiple assumptions together.

A typical set may include:

- pessimistic
- base
- optimistic

For example:

Pessimistic:

- lower demand
- lower prices
- higher costs

Base:

- expected demand
- expected prices
- expected costs

Optimistic:

- higher demand
- higher prices
- lower costs

Scenario analysis does not assign probabilities unless a probabilistic model is explicitly introduced. It is primarily a structured way to examine alternative assumptions.

## Model decomposition

Large models are easier to understand when decomposed into smaller relationships.

A production system may be represented as:

`demand model → capacity model → inventory model → cost model → profit model`

Each component can be implemented and tested separately.

The Python implementation demonstrates this architecture with separate functions for:

- demand
- capacity
- inventory
- profit

This approach reduces complexity and makes assumptions easier to inspect.

It also allows individual components to be replaced without rewriting the entire model.

## Python implementation

The Python program is designed as a mathematical study environment.

It demonstrates:

- variables and expressions
- equations
- business models
- assumptions
- constraints
- decision variables
- state variables
- integer optimization
- continuous versus discrete decisions
- functions
- piecewise functions
- linear and nonlinear relationships
- dimensional analysis
- probability
- expected value
- Monte Carlo simulation
- numerical differentiation
- bisection root finding
- financial modeling
- queueing
- graph algorithms
- regression
- model validation
- sensitivity analysis
- scenario analysis
- model decomposition
- input validation
- floating-point behavior
- computational complexity
- automated tests

Python is particularly suitable for mathematical modeling because its syntax is compact and its standard library contains useful numerical and data-processing functionality.

The implementation intentionally avoids unnecessary external dependencies so that the mathematical mechanisms remain visible.

## JavaScript implementation

The JavaScript program presents similar modeling concepts through application-oriented constructs.

Important JavaScript-specific features include:

- objects
- classes
- functions
- arrays
- error handling
- `Promise`
- `async` and `await`
- numerical computation
- explicit input validation

The asynchronous section demonstrates an important distinction between mathematical computation and application architecture.

The mathematical model may be synchronous, but the data required by an application can come from an asynchronous source.

For example:

`API request → parameters → model calculation → result`

The JavaScript implementation separates asynchronous orchestration from mathematical evaluation.

JavaScript is particularly relevant when mathematical models are integrated into:

- browser applications
- dashboards
- financial interfaces
- calculators
- planning tools
- web-based simulations
- interactive decision systems

## C++ production planning case study

The C++ program models a factory deciding how many units of two products to manufacture.

### Problem

The factory has:

- two products
- limited labor
- limited machine capacity
- product-specific demand limits
- fixed costs
- selling prices
- variable costs

The decision variables are:

`x = units of Product A`

`y = units of Product B`

### Product parameters

Product A:

- selling price = 80
- variable cost = 30
- labor requirement = 2 hours
- machine requirement = 3 hours
- maximum demand = 1000 units

Product B:

- selling price = 100
- variable cost = 40
- labor requirement = 3 hours
- machine requirement = 2 hours
- maximum demand = 1000 units

Factory resources:

- labor capacity = 100 hours
- machine capacity = 90 hours
- fixed cost = 18000

### Objective

Product A contribution margin:

`80 - 30 = 50`

Product B contribution margin:

`100 - 40 = 60`

Therefore:

`maximize 50x + 60y - 18000`

### Constraints

Labor:

`2x + 3y ≤ 100`

Machine:

`3x + 2y ≤ 90`

Demand:

`0 ≤ x ≤ 1000`

`0 ≤ y ≤ 1000`

Integer requirement:

`x,y ∈ Z`

### Architecture

The C++ implementation uses a `Product` structure to represent product parameters.

`ProductionPlan` represents a candidate decision.

`ProductionPlanningModel` contains:

- parameters
- validation
- feasibility checking
- resource calculations
- objective calculation
- optimization
- scenario analysis
- sensitivity analysis
- reporting

This separates model definition from the execution logic.

### Feasibility

The `isFeasible` method checks:

- non-negative quantities
- demand limits
- labor capacity
- machine capacity

This prevents the objective function from being interpreted for an invalid production plan.

### Optimization

The case study uses exhaustive integer enumeration.

The algorithm examines possible combinations of product quantities and retains the feasible combination with the highest objective value.

For two bounded integer variables, the worst-case search complexity is approximately:

`O(D_A × D_B)`

where `D_A` and `D_B` are the respective search limits.

This approach is transparent and appropriate for the small case study.

It becomes unsuitable when the number of variables or candidate values grows significantly.

## Computational complexity and the curse of dimensionality

Suppose a model contains `n` decision variables and every variable has `k` possible values.

An exhaustive search can require:

`k^n`

combinations.

For ten possible values:

- 1 variable → 10 combinations
- 2 variables → 100 combinations
- 3 variables → 1000 combinations
- 5 variables → 100000 combinations
- 8 variables → 100000000 combinations

This exponential growth is known as combinatorial explosion.

It motivates the use of:

- linear programming
- integer programming
- dynamic programming
- branch and bound
- convex optimization
- gradient-based optimization
- constraint programming
- heuristic search
- approximation algorithms
- decomposition methods

The appropriate method depends on the structure of the mathematical model.

## Optimization distinctions

### Mathematical optimization versus simulation

Optimization asks:

`What decision produces the best objective value under the constraints?`

Simulation asks:

`What might happen when the system evolves under specified assumptions?`

They can be combined.

For example:

`optimization → choose staffing level`

followed by:

`simulation → estimate waiting times under uncertainty`

### Deterministic versus stochastic models

A deterministic model produces the same result when its inputs are unchanged.

A stochastic model incorporates randomness or probability.

Example deterministic:

`revenue = price × quantity`

Example stochastic:

`demand ~ probability distribution`

Stochastic models are useful when uncertainty is fundamental to the system.

### Static versus dynamic models

A static model represents a system at one point or aggregated period.

A dynamic model represents change over time.

Inventory:

`I_t = I_(t-1) + production_t - demand_t`

is dynamic because the current state depends on a previous state.

### Descriptive versus prescriptive models

A descriptive model represents what happens.

A predictive model estimates what may happen.

A prescriptive model determines what should be done according to a defined objective and constraints.

Production optimization is prescriptive.

## Edge cases

Mathematical models must explicitly address boundary conditions.

Important examples include:

### Division by zero

Percentage change is:

`((new-old)/old) × 100`

When `old = 0`, the ordinary formula is undefined.

The Python implementation raises an exception rather than silently returning an arbitrary result.

### Negative quantities

Physical quantities such as production, weight, and positive price inputs generally require non-negative domains.

The implementations validate these conditions.

### Zero contribution margin

If:

`price = variable_cost`

then each unit contributes zero toward fixed costs.

If:

`price < variable_cost`

each additional unit increases operating loss before fixed costs.

### Empty datasets

Statistical calculations require enough observations.

The regression and error-metric functions explicitly reject invalid input lengths.

### Identical predictor values

Linear regression requires variation in the independent variable.

If every `x` value is identical, the denominator of the slope equation becomes zero.

### Invalid probability distributions

A probability distribution must satisfy:

`0 ≤ p_i ≤ 1`

and:

`Σp_i = 1`

### Floating-point equality

Computer arithmetic uses finite-precision representations.

Therefore:

`0.1 + 0.2`

may not compare exactly equal to:

`0.3`

The implementations use tolerance-based comparison where appropriate.

## Floating-point considerations

Mathematical notation assumes exact arithmetic in many contexts.

Computers generally use finite-precision numeric representations.

This can introduce:

- rounding error
- cancellation
- overflow
- underflow
- loss of significance

Numerical comparisons should often use a tolerance rather than exact equality.

A tolerance should be chosen according to the scale and sensitivity of the model.

Using an arbitrarily large tolerance can hide real errors. Using an excessively small tolerance can cause valid numerical results to fail comparisons.

## Security considerations

Mathematical modeling systems often receive data from external sources.

Input should be validated before it enters the model.

Validation should consider:

- numeric type
- finite values
- minimum and maximum bounds
- domain restrictions
- unit consistency
- logical relationships
- missing values

The Python and JavaScript implementations deliberately avoid evaluating arbitrary user-provided mathematical strings as executable code.

Using unrestricted expression evaluation can create a code-execution vulnerability.

A production calculator or modeling application should parse mathematical expressions with a restricted grammar and explicitly permitted operations rather than executing arbitrary source code.

External model inputs should also be protected against:

- malformed data
- unexpected extreme values
- injection attacks
- denial-of-service inputs
- integer overflow
- floating-point overflow
- unauthorized model modification

## Implementation considerations

A production mathematical modeling system should separate several concerns.

### Data layer

Responsible for:

- input acquisition
- storage
- serialization
- validation
- unit metadata

### Model layer

Responsible for:

- variables
- equations
- constraints
- objective functions
- transformations

### Solver layer

Responsible for:

- optimization
- numerical methods
- simulation
- root finding
- search

### Validation layer

Responsible for:

- domain checks
- invariants
- numerical tolerances
- test cases
- model verification

### Presentation layer

Responsible for:

- reports
- charts
- dashboards
- user interaction

This separation reduces the risk of mixing business logic with presentation or input-processing logic.

## Common modeling mistakes

### Starting with code instead of the problem

Writing code before identifying the variables and relationships often produces an implementation without a clear mathematical structure.

A better process is:

`problem → variables → assumptions → equations → constraints → objective → algorithm → code`

### Undefined variables

Every important variable should have a precise meaning.

Bad:

`x = value`

Better:

`x = number of Product A units produced during the planning period`

### Hidden assumptions

A model can appear precise while depending on undocumented assumptions.

Assumptions should be written explicitly.

### Ignoring constraints

An unconstrained optimization result may be mathematically optimal but physically impossible.

### Mixing units

Always establish consistent units before combining quantities.

### Ignoring domains

Functions such as:

`log(x)`

require:

`x > 0`

Square roots require appropriate domains when real-valued outputs are expected.

### Treating approximate results as exact

Numerical algorithms produce approximations.

The implementation should preserve appropriate tolerances and communicate numerical precision honestly.

### Overfitting a model

A model with too much complexity can fit historical observations while performing poorly on new data.

### Extrapolating without justification

A regression model fitted to one range of inputs should not automatically be assumed valid far outside that range.

### Confusing model output with reality

A computed result is conditional on:

- the equations
- parameters
- assumptions
- constraints
- data
- algorithm

The output should therefore be interpreted in that context.

## Best practices

A strong mathematical model should have:

- clearly defined variables
- explicit parameters
- documented assumptions
- mathematically consistent units
- explicit constraints
- a clearly stated objective when optimization is involved
- defined variable domains
- deterministic behavior when reproducibility is required
- validation of external inputs
- boundary and edge-case tests
- sensitivity analysis
- scenario analysis where uncertainty matters
- numerical tolerance handling
- complexity analysis
- separation between model logic and application infrastructure

Model code should use meaningful names.

For example:

`laborCapacity`

is preferable to:

`a`

unless the short symbol is specifically required to match a mathematical derivation.

At the same time, the code can document the mathematical symbol:

`x = Product A quantity`

This maintains correspondence between equations and implementation.

## Relationship between mathematics and algorithms

A mathematical model describes the problem.

An algorithm determines how the computer obtains or approximates the desired result.

For example:

Mathematical problem:

`maximize 50x + 60y`

subject to:

`2x + 3y ≤ 100`

`3x + 2y ≤ 90`

Algorithm:

- enumerate candidate values
- reject infeasible values
- evaluate objective
- retain the best feasible solution

The same mathematical model could be solved by a different algorithm.

Possible alternatives include:

- linear programming
- integer programming
- branch and bound
- dynamic programming
- specialized optimization methods

The mathematical model and computational algorithm are related but distinct.

## Relationship between model accuracy and computational cost

More detail does not automatically mean a better model.

A highly detailed model may require:

- more parameters
- more data
- more computation
- more validation
- more maintenance

A simpler model may be preferable if it answers the decision question adequately.

The practical goal is not maximum mathematical complexity. It is an appropriate representation of the system for the intended decision or analysis.

## Real-world applications

Mathematical modeling is used throughout computing and industry.

### Finance

Models can represent:

- cash flows
- loan amortization
- portfolio allocation
- risk
- valuation
- interest
- scenario analysis

### Operations

Models can represent:

- production planning
- staffing
- inventory
- transportation
- scheduling
- warehouse capacity

### Software engineering

Models can represent:

- system capacity
- latency
- throughput
- reliability
- resource utilization
- queueing behavior

### Networking

Models can represent:

- shortest paths
- packet traffic
- bandwidth allocation
- congestion
- reliability

### Machine learning

Models can represent:

- prediction functions
- loss functions
- probability distributions
- optimization objectives
- parameter estimation

### Data analytics

Models can represent:

- trends
- relationships
- forecasts
- statistical uncertainty
- error distributions

### Engineering

Models can represent:

- physical systems
- energy
- forces
- material constraints
- control systems
- resource consumption

## Comparison of the three implementations

| Aspect | Python | JavaScript | C++ |
|---|---|---|---|
| Mathematical experimentation | Strong | Strong | Strong |
| Concise numerical code | Strong | Strong | Moderate |
| Simulation | Strong | Strong | Strong |
| Data-oriented analysis | Strong | Strong | Strong |
| Browser integration | Limited without additional infrastructure | Strong | Limited |
| Asynchronous application behavior | Available but different ecosystem | Strong | Available through explicit mechanisms |
| Low-level control | Limited compared with C++ | Limited | Strong |
| Performance-sensitive modeling | Good | Good | Strong |
| Explicit system architecture | Strong | Strong | Strong |
| Educational mathematical prototyping | Strong | Strong | Strong |
| Industry-style systems implementation | Strong | Strong | Strong |

The languages are not interchangeable in every context.

Python is often convenient for rapid mathematical experimentation.

JavaScript is useful when mathematical models are part of interactive web applications.

C++ provides strong control over memory, execution characteristics, data structures, and performance, making it suitable for computationally intensive systems.

## Conceptual modeling checklist

Before implementing a mathematical model, identify:

### Problem

What real-world or computing question needs to be answered?

### Purpose

Is the model intended to describe, predict, simulate, optimize, or support a decision?

### Variables

What quantities can change?

### Parameters

Which values describe the environment?

### Assumptions

What simplifications are being made?

### Relationships

How do the variables influence each other?

### Constraints

What combinations are impossible or unacceptable?

### Objective

What should be minimized, maximized, estimated, or measured?

### Domain

What values are mathematically and physically valid?

### Data

Where do parameter values come from?

### Algorithm

How will the mathematical problem be solved?

### Validation

How will correctness be tested?

### Sensitivity

How much does the result change when uncertain inputs change?

### Interpretation

What does the mathematical result mean in the real system?

## Implementation mapping

The Python program provides executable demonstrations of the mathematical concepts and emphasizes numerical experimentation.

The JavaScript program provides executable application-style demonstrations and includes asynchronous model execution to show how mathematical computation can fit into event-driven software.

The C++ program converts a complete production-planning problem into an explicit software model. Its architecture demonstrates how mathematical concepts can become domain objects, validation rules, objective functions, feasibility checks, optimization procedures, scenario calculations, and reports.

The central correspondence is:

`mathematical variable → program variable or object property`

`mathematical equation → function or method`

`mathematical constraint → validation or feasibility function`

`objective function → objective method`

`mathematical algorithm → program algorithm`

`assumption → documented model parameter or rule`

`mathematical result → computational output`

`model uncertainty → scenario and sensitivity analysis`

This correspondence is what makes mathematical modeling useful in computing. A problem is first reduced to a formal representation, and that representation is then implemented as an executable computational system.
