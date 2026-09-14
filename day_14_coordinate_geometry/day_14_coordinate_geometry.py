"""
Coordinate Geometry: From Fundamentals to Advanced Applications
=================================================================

A standalone study script covering:

1. Cartesian plane and coordinate systems
2. Points and quadrants
3. Distance and midpoint
4. Section formula
5. Slope and its geometric meaning
6. Equations of lines
7. Parallel and perpendicular lines
8. Intersections of lines
9. Collinearity
10. Area of triangles and polygons
11. Centroid and other special points
12. Coordinate transformations
13. Reflection
14. Circle equations
15. Tangent and normal concepts
16. Locus problems
17. Vector interpretation
18. Numerical stability and edge cases
19. Analytical geometry algorithms
20. Practical validation and testing

The script uses only Python's standard library.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Optional, Sequence


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

EPSILON = 1e-10


def almost_equal(a: float, b: float, tolerance: float = EPSILON) -> bool:
    """Return True when two numbers are approximately equal."""
    return math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance)


# ---------------------------------------------------------------------------
# 1. Fundamental coordinate concepts
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Point:
    """
    A point in the Cartesian plane.

    A point is represented by its x-coordinate and y-coordinate.
    """

    x: float
    y: float

    def __str__(self) -> str:
        return f"({self.x:g}, {self.y:g})"

    def distance_to(self, other: "Point") -> float:
        """Calculate Euclidean distance between two points."""
        return math.hypot(other.x - self.x, other.y - self.y)

    def midpoint(self, other: "Point") -> "Point":
        """Return the midpoint of the segment joining two points."""
        return Point(
            (self.x + other.x) / 2,
            (self.y + other.y) / 2,
        )

    def translate(self, dx: float, dy: float) -> "Point":
        """Move the point horizontally by dx and vertically by dy."""
        return Point(self.x + dx, self.y + dy)

    def reflect_x_axis(self) -> "Point":
        """Reflection across the x-axis: (x, y) -> (x, -y)."""
        return Point(self.x, -self.y)

    def reflect_y_axis(self) -> "Point":
        """Reflection across the y-axis: (x, y) -> (-x, y)."""
        return Point(-self.x, self.y)

    def reflect_origin(self) -> "Point":
        """Reflection through the origin: (x, y) -> (-x, -y)."""
        return Point(-self.x, -self.y)

    def reflect_line_y_equals_x(self) -> "Point":
        """Reflection across y = x: (x, y) -> (y, x)."""
        return Point(self.y, self.x)

    def reflect_line_y_equals_minus_x(self) -> "Point":
        """Reflection across y = -x: (x, y) -> (-y, -x)."""
        return Point(-self.y, -self.x)


def identify_quadrant(point: Point) -> str:
    """
    Identify the location of a point.

    Points on an axis are not inside any quadrant.
    The origin is a special case.
    """
    if almost_equal(point.x, 0) and almost_equal(point.y, 0):
        return "Origin"

    if almost_equal(point.x, 0):
        return "Positive y-axis" if point.y > 0 else "Negative y-axis"

    if almost_equal(point.y, 0):
        return "Positive x-axis" if point.x > 0 else "Negative x-axis"

    if point.x > 0 and point.y > 0:
        return "Quadrant I"

    if point.x < 0 and point.y > 0:
        return "Quadrant II"

    if point.x < 0 and point.y < 0:
        return "Quadrant III"

    return "Quadrant IV"


# ---------------------------------------------------------------------------
# 2. Distance, midpoint, and internal division
# ---------------------------------------------------------------------------

def distance_formula(p1: Point, p2: Point) -> float:
    """
    Distance formula:

        d = sqrt((x2 - x1)^2 + (y2 - y1)^2)
    """
    return math.hypot(p2.x - p1.x, p2.y - p1.y)


def midpoint_formula(p1: Point, p2: Point) -> Point:
    """
    Midpoint formula:

        M = ((x1 + x2)/2, (y1 + y2)/2)
    """
    return Point(
        (p1.x + p2.x) / 2,
        (p1.y + p2.y) / 2,
    )


def section_formula_internal(
    p1: Point,
    p2: Point,
    m: float,
    n: float,
) -> Point:
    """
    Internal section formula.

    If P divides AB internally in the ratio m:n, where
    AP:PB = m:n, then:

        P = ((n*x1 + m*x2)/(m+n),
             (n*y1 + m*y2)/(m+n))
    """
    if m <= 0 or n <= 0:
        raise ValueError("Internal division requires positive ratio values.")

    denominator = m + n

    return Point(
        (n * p1.x + m * p2.x) / denominator,
        (n * p1.y + m * p2.y) / denominator,
    )


def section_formula_external(
    p1: Point,
    p2: Point,
    m: float,
    n: float,
) -> Point:
    """
    External section formula.

    For external division in ratio m:n:

        P = ((m*x2 - n*x1)/(m-n),
             (m*y2 - n*y1)/(m-n))

    The ratio must not have m == n because that would require
    division by zero.
    """
    if m <= 0 or n <= 0:
        raise ValueError("External division requires positive ratio values.")

    if almost_equal(m, n):
        raise ValueError(
            "External division with equal ratio components has no finite point."
        )

    denominator = m - n

    return Point(
        (m * p2.x - n * p1.x) / denominator,
        (m * p2.y - n * p1.y) / denominator,
    )


# ---------------------------------------------------------------------------
# 3. Slope
# ---------------------------------------------------------------------------

def slope(p1: Point, p2: Point) -> Optional[float]:
    """
    Calculate slope:

        m = (y2 - y1) / (x2 - x1)

    A vertical line has undefined/infinite slope, represented here by None.
    """
    dx = p2.x - p1.x
    dy = p2.y - p1.y

    if almost_equal(dx, 0):
        return None

    return dy / dx


def slope_type(p1: Point, p2: Point) -> str:
    """Classify a line segment according to its slope."""
    if almost_equal(p1.x, p2.x):
        return "Vertical"

    if almost_equal(p1.y, p2.y):
        return "Horizontal"

    value = slope(p1, p2)

    if value is not None and value > 0:
        return "Positive slope"

    return "Negative slope"


def angle_of_inclination(p1: Point, p2: Point) -> float:
    """
    Calculate the angle of inclination in degrees.

    The angle is normalized to [0, 180).
    """
    dx = p2.x - p1.x
    dy = p2.y - p1.y

    if almost_equal(dx, 0):
        return 90.0

    angle = math.degrees(math.atan2(dy, dx))

    if angle < 0:
        angle += 180.0

    return angle


def slope_from_angle(degrees: float) -> float:
    """
    Since m = tan(theta), calculate slope from an angle.

    A 90-degree inclination has undefined slope.
    """
    radians = math.radians(degrees)
    cosine = math.cos(radians)

    if almost_equal(cosine, 0):
        raise ValueError("Slope is undefined for a 90-degree inclination.")

    return math.tan(radians)


# ---------------------------------------------------------------------------
# 4. General line representation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Line:
    """
    General equation of a line:

        ax + by + c = 0

    The coefficients are not required to be normalized.
    """

    a: float
    b: float
    c: float

    def __post_init__(self) -> None:
        if almost_equal(self.a, 0) and almost_equal(self.b, 0):
            raise ValueError("A valid line cannot have both a and b equal to zero.")

    def __str__(self) -> str:
        return (
            f"{self.a:g}x + {self.b:g}y + {self.c:g} = 0"
        )

    @classmethod
    def from_points(cls, p1: Point, p2: Point) -> "Line":
        """Construct a line passing through two distinct points."""
        if almost_equal(p1.x, p2.x) and almost_equal(p1.y, p2.y):
            raise ValueError("Two distinct points are required.")

        # Determinant-based construction:
        #
        # (y1 - y2)x + (x2 - x1)y + (x1*y2 - x2*y1) = 0
        return cls(
            p1.y - p2.y,
            p2.x - p1.x,
            p1.x * p2.y - p2.x * p1.y,
        )

    @classmethod
    def from_slope_point(
        cls,
        slope_value: Optional[float],
        point: Point,
    ) -> "Line":
        """
        Construct a line through a point.

        For a finite slope m:

            y - y1 = m(x - x1)

        For a vertical line:

            x = x1
        """
        if slope_value is None:
            return cls(1, 0, -point.x)

        # Rearrange y - y1 = m(x - x1):
        # mx - y + (y1 - mx1) = 0
        return cls(
            slope_value,
            -1,
            point.y - slope_value * point.x,
        )

    @classmethod
    def from_slope_intercept(
        cls,
        slope_value: Optional[float],
        intercept: float,
    ) -> "Line":
        """
        Construct y = mx + b.

        For vertical lines, the intercept represents x = intercept.
        """
        if slope_value is None:
            return cls(1, 0, -intercept)

        return cls(
            slope_value,
            -1,
            intercept,
        )

    def evaluate(self, point: Point) -> float:
        """Evaluate ax + by + c at a point."""
        return self.a * point.x + self.b * point.y + self.c

    def contains(self, point: Point) -> bool:
        """Check whether a point lies on the line."""
        return almost_equal(self.evaluate(point), 0)

    def is_vertical(self) -> bool:
        return almost_equal(self.b, 0)

    def is_horizontal(self) -> bool:
        return almost_equal(self.a, 0)

    def get_slope(self) -> Optional[float]:
        """
        For ax + by + c = 0:

            y = -(a/b)x - c/b

        Therefore slope = -a/b.
        """
        if self.is_vertical():
            return None

        return -self.a / self.b

    def y_intercept(self) -> Optional[float]:
        """Return y-intercept when it exists."""
        if self.is_vertical():
            return None

        return -self.c / self.b

    def x_intercept(self) -> Optional[float]:
        """Return x-intercept when it exists."""
        if almost_equal(self.a, 0):
            return None

        return -self.c / self.a

    def normalized(self) -> "Line":
        """
        Normalize coefficients so sqrt(a^2 + b^2) = 1.

        The sign is made consistent by making the first significant
        coefficient positive.
        """
        norm = math.hypot(self.a, self.b)

        a = self.a / norm
        b = self.b / norm
        c = self.c / norm

        if a < -EPSILON or (almost_equal(a, 0) and b < 0):
            a, b, c = -a, -b, -c

        return Line(a, b, c)

    def distance_to_point(self, point: Point) -> float:
        """
        Perpendicular distance from point (x0, y0) to:

            ax + by + c = 0

        Formula:

            |ax0 + by0 + c| / sqrt(a^2 + b^2)
        """
        numerator = abs(self.evaluate(point))
        denominator = math.hypot(self.a, self.b)

        return numerator / denominator

    def parallel_through(self, point: Point) -> "Line":
        """
        Construct a line parallel to this line through a given point.

        Parallel lines have proportional direction vectors and identical
        normal vectors up to scaling.
        """
        new_c = -(self.a * point.x + self.b * point.y)
        return Line(self.a, self.b, new_c)

    def perpendicular_through(self, point: Point) -> "Line":
        """
        Construct a perpendicular line through a point.

        If this line has normal vector (a, b), a perpendicular line can
        use direction vector (a, b), giving normal vector (-b, a).
        """
        new_a = -self.b
        new_b = self.a
        new_c = -(new_a * point.x + new_b * point.y)
        return Line(new_a, new_b, new_c)


# ---------------------------------------------------------------------------
# 5. Line relationships
# ---------------------------------------------------------------------------

def are_parallel(line1: Line, line2: Line) -> bool:
    """
    Two lines are parallel when:

        a1*b2 - a2*b1 = 0
    """
    determinant = line1.a * line2.b - line2.a * line1.b
    return almost_equal(determinant, 0)


def are_same_line(line1: Line, line2: Line) -> bool:
    """
    Check whether two general-form lines represent the same geometric line.

    The coefficient vectors (a,b,c) must be proportional.
    """
    cross_ab = line1.a * line2.b - line2.a * line1.b
    cross_ac = line1.a * line2.c - line2.a * line1.c
    cross_bc = line1.b * line2.c - line2.b * line1.c

    return (
        almost_equal(cross_ab, 0)
        and almost_equal(cross_ac, 0)
        and almost_equal(cross_bc, 0)
    )


def are_perpendicular(line1: Line, line2: Line) -> bool:
    """
    For general form, the normal vectors are (a1,b1) and (a2,b2).

    Lines are perpendicular when their direction vectors are perpendicular.
    Equivalent condition:

        a1*a2 + b1*b2 = 0
    """
    return almost_equal(
        line1.a * line2.a + line1.b * line2.b,
        0,
    )


# ---------------------------------------------------------------------------
# 6. Line intersection
# ---------------------------------------------------------------------------

def line_intersection(
    line1: Line,
    line2: Line,
) -> Optional[Point]:
    """
    Find the intersection of two lines.

    Solves:

        a1*x + b1*y = -c1
        a2*x + b2*y = -c2

    Returns:
        Point for a unique intersection.
        None for parallel or coincident lines.

    The caller can distinguish the latter cases with are_same_line().
    """
    determinant = line1.a * line2.b - line2.a * line1.b

    if almost_equal(determinant, 0):
        return None

    x = (
        line1.b * line2.c
        - line2.b * line1.c
    ) / determinant

    y = (
        line2.a * line1.c
        - line1.a * line2.c
    ) / determinant

    return Point(x, y)


# ---------------------------------------------------------------------------
# 7. Point-to-line projection and reflection
# ---------------------------------------------------------------------------

def foot_of_perpendicular(point: Point, line: Line) -> Point:
    """
    Find the perpendicular projection of a point onto a line.

    Let:

        d = ax0 + by0 + c
        s = a^2 + b^2

    Then:

        H = (x0 - ad/s, y0 - bd/s)
    """
    value = line.evaluate(point)
    denominator = line.a**2 + line.b**2

    return Point(
        point.x - line.a * value / denominator,
        point.y - line.b * value / denominator,
    )


def reflect_point_across_line(point: Point, line: Line) -> Point:
    """
    Reflect a point across ax + by + c = 0.

    The reflected point is:

        P' = P - 2d/(a^2+b^2) * (a,b)
    """
    value = line.evaluate(point)
    denominator = line.a**2 + line.b**2

    factor = 2 * value / denominator

    return Point(
        point.x - factor * line.a,
        point.y - factor * line.b,
    )


# ---------------------------------------------------------------------------
# 8. Collinearity
# ---------------------------------------------------------------------------

def twice_triangle_area_signed(
    p1: Point,
    p2: Point,
    p3: Point,
) -> float:
    """
    Twice the signed area of triangle ABC.

    Determinant form:

        x1(y2-y3) + x2(y3-y1) + x3(y1-y2)

    Zero means the three points are collinear.
    """
    return (
        p1.x * (p2.y - p3.y)
        + p2.x * (p3.y - p1.y)
        + p3.x * (p1.y - p2.y)
    )


def are_collinear(
    p1: Point,
    p2: Point,
    p3: Point,
) -> bool:
    """Check collinearity using the determinant condition."""
    return almost_equal(
        twice_triangle_area_signed(p1, p2, p3),
        0,
    )


# ---------------------------------------------------------------------------
# 9. Area calculations
# ---------------------------------------------------------------------------

def triangle_area(
    p1: Point,
    p2: Point,
    p3: Point,
) -> float:
    """Return the non-negative area of a triangle."""
    return abs(twice_triangle_area_signed(p1, p2, p3)) / 2


def polygon_area(vertices: Sequence[Point]) -> float:
    """
    Calculate polygon area using the shoelace formula.

    For vertices ordered around a simple polygon:

        Area = 1/2 |sum(x_i*y_(i+1) - y_i*x_(i+1))|
    """
    if len(vertices) < 3:
        raise ValueError("A polygon requires at least three vertices.")

    total = 0.0

    for current, next_point in zip(
        vertices,
        vertices[1:] + vertices[:1],
    ):
        total += current.x * next_point.y
        total -= current.y * next_point.x

    return abs(total) / 2


def polygon_signed_area(vertices: Sequence[Point]) -> float:
    """Return signed polygon area; sign indicates vertex orientation."""
    if len(vertices) < 3:
        raise ValueError("A polygon requires at least three vertices.")

    total = 0.0

    for current, next_point in zip(
        vertices,
        vertices[1:] + vertices[:1],
    ):
        total += (
            current.x * next_point.y
            - current.y * next_point.x
        )

    return total / 2


def polygon_orientation(vertices: Sequence[Point]) -> str:
    """Determine clockwise or counterclockwise vertex ordering."""
    area = polygon_signed_area(vertices)

    if almost_equal(area, 0):
        return "Degenerate"

    return "Counterclockwise" if area > 0 else "Clockwise"


# ---------------------------------------------------------------------------
# 10. Triangle centers
# ---------------------------------------------------------------------------

def triangle_centroid(
    p1: Point,
    p2: Point,
    p3: Point,
) -> Point:
    """
    Centroid formula:

        G = ((x1+x2+x3)/3, (y1+y2+y3)/3)
    """
    return Point(
        (p1.x + p2.x + p3.x) / 3,
        (p1.y + p2.y + p3.y) / 3,
    )


def perpendicular_bisector(
    p1: Point,
    p2: Point,
) -> Line:
    """
    Construct the perpendicular bisector of a segment.

    It passes through the midpoint and is perpendicular to AB.
    """
    midpoint = p1.midpoint(p2)
    original = Line.from_points(p1, p2)

    return original.perpendicular_through(midpoint)


def circumcenter(
    p1: Point,
    p2: Point,
    p3: Point,
) -> Point:
    """
    Calculate the circumcenter as the intersection of two
    perpendicular bisectors.
    """
    if are_collinear(p1, p2, p3):
        raise ValueError("A non-collinear triangle is required.")

    bisector1 = perpendicular_bisector(p1, p2)
    bisector2 = perpendicular_bisector(p1, p3)

    center = line_intersection(bisector1, bisector2)

    if center is None:
        raise ArithmeticError("Circumcenter could not be determined.")

    return center


# ---------------------------------------------------------------------------
# 11. Circles
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Circle:
    """
    Circle represented by center and radius.

    Standard equation:

        (x-h)^2 + (y-k)^2 = r^2
    """

    center: Point
    radius: float

    def __post_init__(self) -> None:
        if self.radius < 0:
            raise ValueError("Circle radius cannot be negative.")

    def contains(self, point: Point) -> bool:
        """Check whether a point lies on the circumference."""
        return almost_equal(
            self.center.distance_to(point),
            self.radius,
        )

    def distance_from_center(self, point: Point) -> float:
        return self.center.distance_to(point)

    def circumference(self) -> float:
        return 2 * math.pi * self.radius

    def area(self) -> float:
        return math.pi * self.radius**2

    def equation_coefficients(self) -> tuple[float, float, float]:
        """
        Expand:

            (x-h)^2 + (y-k)^2 = r^2

        into:

            x^2 + y^2 + Dx + Ey + F = 0

        where:

            D = -2h
            E = -2k
            F = h^2 + k^2 - r^2
        """
        h = self.center.x
        k = self.center.y

        return (
            -2 * h,
            -2 * k,
            h**2 + k**2 - self.radius**2,
        )


def circle_from_three_points(
    p1: Point,
    p2: Point,
    p3: Point,
) -> Circle:
    """Construct the unique circle through three non-collinear points."""
    center = circumcenter(p1, p2, p3)
    return Circle(center, center.distance_to(p1))


def line_circle_intersections(
    line: Line,
    circle: Circle,
) -> list[Point]:
    """
    Find intersections between a line and circle.

    The method projects the circle center onto the line and compares
    the perpendicular distance with the radius.

    Cases:
        distance > radius: no intersection
        distance = radius: tangent
        distance < radius: two intersections
    """
    foot = foot_of_perpendicular(circle.center, line)
    distance = circle.center.distance_to(foot)

    if distance > circle.radius + EPSILON:
        return []

    if almost_equal(distance, circle.radius):
        return [foot]

    # Unit direction vector along the line.
    direction_x = line.b
    direction_y = -line.a

    direction_length = math.hypot(direction_x, direction_y)

    direction_x /= direction_length
    direction_y /= direction_length

    half_chord = math.sqrt(
        max(circle.radius**2 - distance**2, 0)
    )

    return [
        Point(
            foot.x + direction_x * half_chord,
            foot.y + direction_y * half_chord,
        ),
        Point(
            foot.x - direction_x * half_chord,
            foot.y - direction_y * half_chord,
        ),
    ]


# ---------------------------------------------------------------------------
# 12. Locus and geometric conditions
# ---------------------------------------------------------------------------

def equal_distance_locus_line(
    p1: Point,
    p2: Point,
) -> Line:
    """
    The locus of points equidistant from two fixed points is their
    perpendicular bisector.
    """
    if almost_equal(p1.x, p2.x) and almost_equal(p1.y, p2.y):
        raise ValueError(
            "Two distinct fixed points are required."
        )

    return perpendicular_bisector(p1, p2)


def points_at_fixed_distance(
    center: Point,
    radius: float,
    angles_degrees: Iterable[float],
) -> list[Point]:
    """
    Sample points from the locus:

        (x-h)^2 + (y-k)^2 = r^2
    """
    if radius < 0:
        raise ValueError("Radius must be non-negative.")

    points = []

    for angle in angles_degrees:
        theta = math.radians(angle)

        points.append(
            Point(
                center.x + radius * math.cos(theta),
                center.y + radius * math.sin(theta),
            )
        )

    return points


# ---------------------------------------------------------------------------
# 13. Vector interpretation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Vector:
    """A two-dimensional vector."""

    x: float
    y: float

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector") -> "Vector":
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector":
        return Vector(self.x * scalar, self.y * scalar)

    def magnitude(self) -> float:
        return math.hypot(self.x, self.y)

    def dot(self, other: "Vector") -> float:
        """Dot product: ax*bx + ay*by."""
        return self.x * other.x + self.y * other.y

    def cross_z(self, other: "Vector") -> float:
        """
        Two-dimensional cross product represented by its z-component:

            ax*by - ay*bx

        This is useful for orientation and intersection tests.
        """
        return self.x * other.y - self.y * other.x

    def normalized(self) -> "Vector":
        """Return a unit vector in the same direction."""
        magnitude = self.magnitude()

        if almost_equal(magnitude, 0):
            raise ValueError("Zero vector cannot be normalized.")

        return Vector(
            self.x / magnitude,
            self.y / magnitude,
        )


def vector_between(p1: Point, p2: Point) -> Vector:
    """Return vector from p1 to p2."""
    return Vector(
        p2.x - p1.x,
        p2.y - p1.y,
    )


def angle_between_vectors(
    v1: Vector,
    v2: Vector,
) -> float:
    """
    Calculate the smaller angle between two vectors.

        cos(theta) = (u dot v) / (|u||v|)
    """
    denominator = v1.magnitude() * v2.magnitude()

    if almost_equal(denominator, 0):
        raise ValueError(
            "Angle involving a zero vector is undefined."
        )

    cosine = v1.dot(v2) / denominator

    # Floating-point calculations can produce values such as
    # 1.0000000000000002, so clamp before acos.
    cosine = max(-1.0, min(1.0, cosine))

    return math.degrees(math.acos(cosine))


# ---------------------------------------------------------------------------
# 14. Segment and orientation algorithms
# ---------------------------------------------------------------------------

def orientation(
    p: Point,
    q: Point,
    r: Point,
) -> int:
    """
    Determine orientation of ordered points p, q, r.

    Returns:
        1  -> counterclockwise
        -1 -> clockwise
        0  -> collinear
    """
    cross = twice_triangle_area_signed(p, q, r)

    if almost_equal(cross, 0):
        return 0

    return 1 if cross > 0 else -1


def point_on_segment(
    point: Point,
    start: Point,
    end: Point,
) -> bool:
    """Check whether a point lies on the closed line segment."""
    if orientation(start, point, end) != 0:
        return False

    return (
        min(start.x, end.x) - EPSILON <= point.x <= max(start.x, end.x) + EPSILON
        and
        min(start.y, end.y) - EPSILON <= point.y <= max(start.y, end.y) + EPSILON
    )


def segments_intersect(
    p1: Point,
    p2: Point,
    q1: Point,
    q2: Point,
) -> bool:
    """
    Robust segment-intersection test.

    It handles:
    - proper crossings
    - endpoint touching
    - collinear overlap
    """
    o1 = orientation(p1, p2, q1)
    o2 = orientation(p1, p2, q2)
    o3 = orientation(q1, q2, p1)
    o4 = orientation(q1, q2, p2)

    if o1 != o2 and o3 != o4:
        return True

    if o1 == 0 and point_on_segment(q1, p1, p2):
        return True

    if o2 == 0 and point_on_segment(q2, p1, p2):
        return True

    if o3 == 0 and point_on_segment(p1, q1, q2):
        return True

    if o4 == 0 and point_on_segment(p2, q1, q2):
        return True

    return False


# ---------------------------------------------------------------------------
# 15. Distance between two parallel lines
# ---------------------------------------------------------------------------

def distance_between_parallel_lines(
    line1: Line,
    line2: Line,
) -> float:
    """
    Distance between parallel lines.

    First normalize both equations to a common coefficient scale.

    For:

        ax + by + c1 = 0
        ax + by + c2 = 0

    distance = |c1-c2| / sqrt(a^2+b^2)
    """
    if not are_parallel(line1, line2):
        raise ValueError("The lines must be parallel.")

    normalized1 = line1.normalized()
    normalized2 = line2.normalized()

    # Account for potentially opposite signs after normalization.
    if (
        almost_equal(normalized1.a, -normalized2.a)
        and almost_equal(normalized1.b, -normalized2.b)
    ):
        c2 = -normalized2.c
    else:
        c2 = normalized2.c

    return abs(normalized1.c - c2)


# ---------------------------------------------------------------------------
# 16. Coordinate transformations
# ---------------------------------------------------------------------------

def rotate_point(
    point: Point,
    angle_degrees: float,
    center: Point = Point(0, 0),
) -> Point:
    """
    Rotate a point counterclockwise around a center.

    For rotation around origin:

        x' = x cos(theta) - y sin(theta)
        y' = x sin(theta) + y cos(theta)

    Translation before and after rotation extends the same formula
    to arbitrary centers.
    """
    theta = math.radians(angle_degrees)

    translated_x = point.x - center.x
    translated_y = point.y - center.y

    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)

    rotated_x = (
        translated_x * cos_theta
        - translated_y * sin_theta
    )

    rotated_y = (
        translated_x * sin_theta
        + translated_y * cos_theta
    )

    return Point(
        rotated_x + center.x,
        rotated_y + center.y,
    )


def scale_point(
    point: Point,
    scale_x: float,
    scale_y: float,
    center: Point = Point(0, 0),
) -> Point:
    """Scale a point relative to a chosen center."""
    return Point(
        center.x + (point.x - center.x) * scale_x,
        center.y + (point.y - center.y) * scale_y,
    )


# ---------------------------------------------------------------------------
# 17. Three-dimensional-style affine transformation matrix for 2D points
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Matrix3x3:
    """
    Homogeneous 2D transformation matrix.

    A point (x,y) is represented as:

        [x]
        [y]
        [1]

    Translation, rotation, scaling, and composition can therefore
    be represented using matrix multiplication.
    """

    values: tuple[
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
    ]

    def multiply(self, other: "Matrix3x3") -> "Matrix3x3":
        """Multiply two 3x3 matrices."""
        result = []

        for i in range(3):
            row = []

            for j in range(3):
                value = sum(
                    self.values[i][k] * other.values[k][j]
                    for k in range(3)
                )
                row.append(value)

            result.append(tuple(row))

        return Matrix3x3(tuple(result))  # type: ignore[arg-type]

    def transform_point(self, point: Point) -> Point:
        """Apply the homogeneous transformation to a Cartesian point."""
        x = point.x
        y = point.y

        transformed_x = (
            self.values[0][0] * x
            + self.values[0][1] * y
            + self.values[0][2]
        )

        transformed_y = (
            self.values[1][0] * x
            + self.values[1][1] * y
            + self.values[1][2]
        )

        w = (
            self.values[2][0] * x
            + self.values[2][1] * y
            + self.values[2][2]
        )

        if almost_equal(w, 0):
            raise ValueError(
                "Transformation produced a point at infinity."
            )

        return Point(
            transformed_x / w,
            transformed_y / w,
        )

    @staticmethod
    def identity() -> "Matrix3x3":
        return Matrix3x3(
            (
                (1, 0, 0),
                (0, 1, 0),
                (0, 0, 1),
            )
        )

    @staticmethod
    def translation(dx: float, dy: float) -> "Matrix3x3":
        return Matrix3x3(
            (
                (1, 0, dx),
                (0, 1, dy),
                (0, 0, 1),
            )
        )

    @staticmethod
    def scaling(sx: float, sy: float) -> "Matrix3x3":
        return Matrix3x3(
            (
                (sx, 0, 0),
                (0, sy, 0),
                (0, 0, 1),
            )
        )

    @staticmethod
    def rotation(angle_degrees: float) -> "Matrix3x3":
        theta = math.radians(angle_degrees)
        c = math.cos(theta)
        s = math.sin(theta)

        return Matrix3x3(
            (
                (c, -s, 0),
                (s, c, 0),
                (0, 0, 1),
            )
        )


# ---------------------------------------------------------------------------
# 18. Coordinate geometry utility algorithms
# ---------------------------------------------------------------------------

def bounding_box(points: Sequence[Point]) -> tuple[float, float, float, float]:
    """Return min_x, min_y, max_x, max_y."""
    if not points:
        raise ValueError("At least one point is required.")

    xs = [point.x for point in points]
    ys = [point.y for point in points]

    return min(xs), min(ys), max(xs), max(ys)


def nearest_point(
    reference: Point,
    points: Sequence[Point],
) -> Point:
    """Find the closest point to a reference point."""
    if not points:
        raise ValueError("At least one candidate point is required.")

    return min(
        points,
        key=lambda point: reference.distance_to(point),
    )


def farthest_pair(
    points: Sequence[Point],
) -> tuple[Point, Point, float]:
    """
    Brute-force farthest pair.

    Complexity:
        O(n^2)

    This is intentionally simple and useful for teaching. More advanced
    computational geometry can improve this for large point sets.
    """
    if len(points) < 2:
        raise ValueError("At least two points are required.")

    best_pair = (points[0], points[1])
    best_distance = points[0].distance_to(points[1])

    for p1, p2 in combinations(points, 2):
        current_distance = p1.distance_to(p2)

        if current_distance > best_distance:
            best_pair = (p1, p2)
            best_distance = current_distance

    return best_pair[0], best_pair[1], best_distance


# ---------------------------------------------------------------------------
# 19. Triangle classification
# ---------------------------------------------------------------------------

def triangle_side_lengths(
    p1: Point,
    p2: Point,
    p3: Point,
) -> tuple[float, float, float]:
    """Return the three side lengths."""
    return (
        p1.distance_to(p2),
        p2.distance_to(p3),
        p3.distance_to(p1),
    )


def classify_triangle(
    p1: Point,
    p2: Point,
    p3: Point,
) -> str:
    """
    Classify a triangle by side and angle properties.

    The squared-side method avoids unnecessary square roots for
    angle classification.
    """
    sides = triangle_side_lengths(p1, p2, p3)
    squared = sorted(side**2 for side in sides)

    if almost_equal(squared[0], 0):
        return "Degenerate"

    if almost_equal(squared[0] + squared[1], squared[2]):
        angle_type = "right"
    elif squared[0] + squared[1] > squared[2]:
        angle_type = "acute"
    else:
        angle_type = "obtuse"

    if (
        almost_equal(sides[0], sides[1])
        and almost_equal(sides[1], sides[2])
    ):
        side_type = "equilateral"
    elif (
        almost_equal(sides[0], sides[1])
        or almost_equal(sides[1], sides[2])
        or almost_equal(sides[0], sides[2])
    ):
        side_type = "isosceles"
    else:
        side_type = "scalene"

    return f"{side_type}, {angle_type}"


# ---------------------------------------------------------------------------
# 20. Solving equations from two points
# ---------------------------------------------------------------------------

def point_on_line_from_parameter(
    p1: Point,
    p2: Point,
    t: float,
) -> Point:
    """
    Parametric representation of a line:

        P(t) = P1 + t(P2-P1)

    t = 0 gives P1.
    t = 1 gives P2.
    0 < t < 1 gives points on the segment.
    Other values extend the line.
    """
    return Point(
        p1.x + t * (p2.x - p1.x),
        p1.y + t * (p2.y - p1.y),
    )


def line_parameter_for_point(
    point: Point,
    p1: Point,
    p2: Point,
) -> Optional[float]:
    """
    Find t such that:

        point = p1 + t(p2-p1)

    Returns None when the point does not lie on the line.
    """
    if not Line.from_points(p1, p2).contains(point):
        return None

    dx = p2.x - p1.x
    dy = p2.y - p1.y

    if abs(dx) >= abs(dy) and not almost_equal(dx, 0):
        return (point.x - p1.x) / dx

    if not almost_equal(dy, 0):
        return (point.y - p1.y) / dy

    return None


# ---------------------------------------------------------------------------
# 21. Distance from point to segment
# ---------------------------------------------------------------------------

def distance_point_to_segment(
    point: Point,
    start: Point,
    end: Point,
) -> float:
    """
    Minimum distance between a point and a finite segment.

    Projection parameter:

        t = ((P-A) dot (B-A)) / |B-A|^2

    Clamp t to [0,1] because a segment is finite.
    """
    segment = vector_between(start, end)

    denominator = segment.dot(segment)

    if almost_equal(denominator, 0):
        return point.distance_to(start)

    point_vector = vector_between(start, point)

    t = point_vector.dot(segment) / denominator
    t = max(0.0, min(1.0, t))

    projection = point_on_line_from_parameter(
        start,
        end,
        t,
    )

    return point.distance_to(projection)


# ---------------------------------------------------------------------------
# 22. Demonstration sections
# ---------------------------------------------------------------------------

def demonstrate_cartesian_plane() -> None:
    print("\n" + "=" * 72)
    print("1. CARTESIAN PLANE")
    print("=" * 72)

    points = [
        Point(3, 4),
        Point(-3, 4),
        Point(-3, -4),
        Point(3, -4),
        Point(0, 0),
        Point(0, 5),
        Point(-5, 0),
    ]

    for point in points:
        print(f"{point:>12} -> {identify_quadrant(point)}")


def demonstrate_distance_and_midpoint() -> None:
    print("\n" + "=" * 72)
    print("2. DISTANCE AND MIDPOINT")
    print("=" * 72)

    a = Point(2, 3)
    b = Point(8, 11)

    print(f"A = {a}")
    print(f"B = {b}")
    print(f"Distance AB = {distance_formula(a, b):.6f}")
    print(f"Midpoint AB = {midpoint_formula(a, b)}")

    internal = section_formula_internal(a, b, 2, 3)
    external = section_formula_external(a, b, 3, 2)

    print(f"Internal division 2:3 = {internal}")
    print(f"External division 3:2 = {external}")


def demonstrate_slope() -> None:
    print("\n" + "=" * 72)
    print("3. SLOPE")
    print("=" * 72)

    examples = [
        (Point(1, 2), Point(5, 10)),
        (Point(1, 5), Point(6, 5)),
        (Point(3, 1), Point(3, 9)),
        (Point(2, 7), Point(6, 3)),
    ]

    for p1, p2 in examples:
        print(
            f"{p1} -> {p2}: "
            f"slope={slope(p1, p2)}, "
            f"type={slope_type(p1, p2)}, "
            f"inclination={angle_of_inclination(p1, p2):.2f}°"
        )


def demonstrate_lines() -> None:
    print("\n" + "=" * 72)
    print("4. EQUATIONS OF LINES")
    print("=" * 72)

    p1 = Point(2, 3)
    p2 = Point(6, 11)

    line = Line.from_points(p1, p2)

    print(f"Line through {p1} and {p2}: {line}")
    print(f"Slope: {line.get_slope()}")
    print(f"x-intercept: {line.x_intercept()}")
    print(f"y-intercept: {line.y_intercept()}")

    test_points = [
        Point(4, 7),
        Point(0, -1),
        Point(10, 15),
    ]

    for point in test_points:
        print(
            f"{point} on line? "
            f"{line.contains(point)}; "
            f"distance={line.distance_to_point(point):.6f}"
        )


def demonstrate_parallel_perpendicular() -> None:
    print("\n" + "=" * 72)
    print("5. PARALLEL AND PERPENDICULAR LINES")
    print("=" * 72)

    base = Line.from_points(Point(0, 0), Point(4, 2))
    parallel = base.parallel_through(Point(0, 5))
    perpendicular = base.perpendicular_through(Point(0, 5))

    print(f"Base line:          {base}")
    print(f"Parallel line:      {parallel}")
    print(f"Perpendicular line: {perpendicular}")

    print(f"Base || parallel: {are_parallel(base, parallel)}")
    print(f"Base ⟂ perpendicular: {are_perpendicular(base, perpendicular)}")
    print(
        "Distance between parallel lines: "
        f"{distance_between_parallel_lines(base, parallel):.6f}"
    )


def demonstrate_intersections() -> None:
    print("\n" + "=" * 72)
    print("6. LINE INTERSECTIONS")
    print("=" * 72)

    line1 = Line.from_points(Point(0, 0), Point(4, 4))
    line2 = Line.from_points(Point(0, 4), Point(4, 0))

    intersection = line_intersection(line1, line2)

    print(f"Line 1: {line1}")
    print(f"Line 2: {line2}")
    print(f"Intersection: {intersection}")

    parallel1 = Line.from_slope_intercept(2, 1)
    parallel2 = Line.from_slope_intercept(2, -4)

    print(f"Parallel lines: {parallel1} and {parallel2}")
    print(f"Intersection: {line_intersection(parallel1, parallel2)}")


def demonstrate_collinearity_and_area() -> None:
    print("\n" + "=" * 72)
    print("7. COLLINEARITY AND AREA")
    print("=" * 72)

    a = Point(0, 0)
    b = Point(4, 4)
    c = Point(8, 8)
    d = Point(4, 0)

    print(f"A, B, C collinear? {are_collinear(a, b, c)}")
    print(f"A, B, D collinear? {are_collinear(a, b, d)}")
    print(f"Triangle ABD area: {triangle_area(a, b, d)}")

    polygon = [
        Point(0, 0),
        Point(4, 0),
        Point(5, 3),
        Point(2, 5),
        Point(-1, 3),
    ]

    print(f"Polygon area: {polygon_area(polygon)}")
    print(f"Polygon orientation: {polygon_orientation(polygon)}")


def demonstrate_triangle_centers() -> None:
    print("\n" + "=" * 72)
    print("8. TRIANGLE CENTERS")
    print("=" * 72)

    a = Point(0, 0)
    b = Point(4, 0)
    c = Point(0, 3)

    centroid = triangle_centroid(a, b, c)
    center = circumcenter(a, b, c)

    print(f"Triangle: {a}, {b}, {c}")
    print(f"Centroid: {centroid}")
    print(f"Circumcenter: {center}")
    print(f"Triangle classification: {classify_triangle(a, b, c)}")


def demonstrate_circles() -> None:
    print("\n" + "=" * 72)
    print("9. CIRCLES")
    print("=" * 72)

    circle = Circle(Point(2, 3), 5)

    print(f"Center: {circle.center}")
    print(f"Radius: {circle.radius}")
    print(f"Area: {circle.area():.6f}")
    print(f"Circumference: {circle.circumference():.6f}")
    print(f"Expanded coefficients: {circle.equation_coefficients()}")

    line = Line.from_slope_intercept(0, 3)
    intersections = line_circle_intersections(line, circle)

    print(f"Line: {line}")
    print(f"Line-circle intersections: {intersections}")

    p1 = Point(0, 1)
    p2 = Point(2, 3)
    p3 = Point(4, 1)

    circle2 = circle_from_three_points(p1, p2, p3)

    print(
        f"Circle through {p1}, {p2}, {p3}: "
        f"center={circle2.center}, radius={circle2.radius:.6f}"
    )


def demonstrate_projection_and_reflection() -> None:
    print("\n" + "=" * 72)
    print("10. PROJECTION AND REFLECTION")
    print("=" * 72)

    point = Point(5, 4)
    line = Line.from_slope_intercept(1, 0)

    foot = foot_of_perpendicular(point, line)
    reflected = reflect_point_across_line(point, line)

    print(f"Point: {point}")
    print(f"Line: {line}")
    print(f"Perpendicular foot: {foot}")
    print(f"Reflected point: {reflected}")
    print(
        "Distances from original and reflection to line: "
        f"{line.distance_to_point(point):.6f}, "
        f"{line.distance_to_point(reflected):.6f}"
    )


def demonstrate_vectors() -> None:
    print("\n" + "=" * 72)
    print("11. VECTOR INTERPRETATION")
    print("=" * 72)

    a = Point(1, 2)
    b = Point(5, 5)

    vector = vector_between(a, b)
    other = Vector(3, -4)

    print(f"Vector AB = {vector}")
    print(f"|AB| = {vector.magnitude():.6f}")
    print(f"Dot product = {vector.dot(other)}")
    print(f"Cross product z-component = {vector.cross_z(other)}")
    print(
        f"Angle between vectors = "
        f"{angle_between_vectors(vector, other):.6f}°"
    )


def demonstrate_segments() -> None:
    print("\n" + "=" * 72)
    print("12. SEGMENT GEOMETRY")
    print("=" * 72)

    a = Point(0, 0)
    b = Point(5, 5)
    c = Point(0, 5)
    d = Point(5, 0)

    print(f"Segments AB and CD intersect? {segments_intersect(a, b, c, d)}")

    point = Point(2, 3)

    print(
        f"Distance from {point} to segment AB: "
        f"{distance_point_to_segment(point, a, b):.6f}"
    )


def demonstrate_transformations() -> None:
    print("\n" + "=" * 72)
    print("13. COORDINATE TRANSFORMATIONS")
    print("=" * 72)

    point = Point(3, 1)

    print(f"Original: {point}")
    print(f"Rotated 90°: {rotate_point(point, 90)}")
    print(f"Scaled by (2,3): {scale_point(point, 2, 3)}")
    print(f"Translated by (5,-2): {point.translate(5, -2)}")
    print(f"Reflection over x-axis: {point.reflect_x_axis()}")
    print(f"Reflection over y-axis: {point.reflect_y_axis()}")
    print(f"Reflection over origin: {point.reflect_origin()}")
    print(f"Reflection over y=x: {point.reflect_line_y_equals_x()}")

    # Matrix composition demonstrates that transformations can be combined.
    translation = Matrix3x3.translation(5, 2)
    rotation = Matrix3x3.rotation(90)

    combined = translation.multiply(rotation)

    transformed = combined.transform_point(point)

    print(f"Matrix-composed transformation: {transformed}")


def demonstrate_locus() -> None:
    print("\n" + "=" * 72)
    print("14. LOCUS")
    print("=" * 72)

    fixed_a = Point(0, 0)
    fixed_b = Point(4, 0)

    locus = equal_distance_locus_line(fixed_a, fixed_b)

    print(
        f"Locus of points equidistant from {fixed_a} and {fixed_b}: "
        f"{locus}"
    )

    candidates = [
        Point(2, 0),
        Point(2, 5),
        Point(2, -5),
        Point(3, 4),
    ]

    for point in candidates:
        print(
            f"{point}: "
            f"distance to A={point.distance_to(fixed_a):.6f}, "
            f"distance to B={point.distance_to(fixed_b):.6f}, "
            f"on locus={locus.contains(point)}"
        )


def demonstrate_point_sets() -> None:
    print("\n" + "=" * 72)
    print("15. POINT-SET OPERATIONS")
    print("=" * 72)

    points = [
        Point(-2, 4),
        Point(8, 1),
        Point(3, 7),
        Point(0, -3),
        Point(5, 2),
    ]

    print(f"Bounding box: {bounding_box(points)}")

    reference = Point(1, 1)
    print(
        f"Nearest to {reference}: "
        f"{nearest_point(reference, points)}"
    )

    p1, p2, distance = farthest_pair(points)

    print(
        f"Farthest pair: {p1} and {p2}, "
        f"distance={distance:.6f}"
    )


# ---------------------------------------------------------------------------
# 23. Edge cases and numerical behavior
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    print("\n" + "=" * 72)
    print("16. EDGE CASES")
    print("=" * 72)

    vertical_p1 = Point(5, 1)
    vertical_p2 = Point(5, 9)

    print(
        "Vertical slope:",
        slope(vertical_p1, vertical_p2),
        "(None represents undefined slope)",
    )

    horizontal_p1 = Point(1, 7)
    horizontal_p2 = Point(9, 7)

    print(
        "Horizontal slope:",
        slope(horizontal_p1, horizontal_p2),
    )

    duplicate = Point(3, 3)

    try:
        Line.from_points(duplicate, duplicate)
    except ValueError as error:
        print(f"Duplicate-point line error: {error}")

    try:
        Vector(0, 0).normalized()
    except ValueError as error:
        print(f"Zero-vector normalization error: {error}")

    try:
        Circle(Point(0, 0), -2)
    except ValueError as error:
        print(f"Negative-radius error: {error}")


# ---------------------------------------------------------------------------
# 24. Verification and testing
# ---------------------------------------------------------------------------

def run_assertion_tests() -> None:
    """
    Small educational test suite.

    Assertions validate the mathematical implementations without requiring
    an external testing package.
    """
    a = Point(0, 0)
    b = Point(3, 4)

    assert almost_equal(distance_formula(a, b), 5)
    assert midpoint_formula(a, b) == Point(1.5, 2)

    assert almost_equal(slope(Point(0, 0), Point(2, 4)), 2)
    assert slope(Point(2, 0), Point(2, 5)) is None

    line = Line.from_points(Point(0, 0), Point(2, 2))

    assert line.contains(Point(5, 5))
    assert not line.contains(Point(5, 4))

    perpendicular = line.perpendicular_through(Point(0, 5))

    assert are_perpendicular(line, perpendicular)

    parallel = line.parallel_through(Point(0, 5))

    assert are_parallel(line, parallel)

    intersection = line_intersection(
        Line.from_points(Point(0, 0), Point(4, 4)),
        Line.from_points(Point(0, 4), Point(4, 0)),
    )

    assert intersection is not None
    assert almost_equal(intersection.x, 2)
    assert almost_equal(intersection.y, 2)

    assert are_collinear(
        Point(0, 0),
        Point(2, 2),
        Point(5, 5),
    )

    assert not are_collinear(
        Point(0, 0),
        Point(2, 2),
        Point(5, 4),
    )

    assert almost_equal(
        triangle_area(
            Point(0, 0),
            Point(4, 0),
            Point(0, 3),
        ),
        6,
    )

    polygon = [
        Point(0, 0),
        Point(4, 0),
        Point(4, 3),
        Point(0, 3),
    ]

    assert almost_equal(polygon_area(polygon), 12)

    centroid = triangle_centroid(
        Point(0, 0),
        Point(6, 0),
        Point(0, 6),
    )

    assert centroid == Point(2, 2)

    circle = Circle(Point(0, 0), 5)

    assert circle.contains(Point(3, 4))
    assert not circle.contains(Point(1, 1))

    reflected = reflect_point_across_line(
        Point(3, 1),
        Line.from_slope_intercept(1, 0),
    )

    assert almost_equal(reflected.x, 1)
    assert almost_equal(reflected.y, 3)

    assert segments_intersect(
        Point(0, 0),
        Point(4, 4),
        Point(0, 4),
        Point(4, 0),
    )

    assert not segments_intersect(
        Point(0, 0),
        Point(1, 1),
        Point(2, 2),
        Point(3, 3),
    )

    rotated = rotate_point(Point(1, 0), 90)

    assert almost_equal(rotated.x, 0)
    assert almost_equal(rotated.y, 1)

    print("\nAll assertion tests passed.")


# ---------------------------------------------------------------------------
# 25. Worked problem set
# ---------------------------------------------------------------------------

def worked_coordinate_geometry_problems() -> None:
    print("\n" + "=" * 72)
    print("17. WORKED COORDINATE GEOMETRY PROBLEMS")
    print("=" * 72)

    # Problem 1:
    # Find the equation of the line through (2, -1) and (6, 7).
    p1 = Point(2, -1)
    p2 = Point(6, 7)

    line = Line.from_points(p1, p2)

    print("\nProblem 1")
    print("Points:", p1, p2)
    print("Line:", line)
    print("Slope:", line.get_slope())

    # Problem 2:
    # Find a line perpendicular to the previous line through (3, 4).
    p = Point(3, 4)
    perpendicular = line.perpendicular_through(p)

    print("\nProblem 2")
    print("Required line:", perpendicular)
    print("Perpendicular:", are_perpendicular(line, perpendicular))

    # Problem 3:
    # Find the intersection of the two lines.
    line_a = Line.from_slope_intercept(2, -3)
    line_b = Line.from_slope_intercept(-1, 6)

    intersection = line_intersection(line_a, line_b)

    print("\nProblem 3")
    print("Line A:", line_a)
    print("Line B:", line_b)
    print("Intersection:", intersection)

    # Problem 4:
    # Find the area of a polygon.
    polygon = [
        Point(1, 1),
        Point(5, 1),
        Point(6, 4),
        Point(3, 6),
        Point(0, 4),
    ]

    print("\nProblem 4")
    print("Polygon:", polygon)
    print("Area:", polygon_area(polygon))

    # Problem 5:
    # Determine the point where the perpendicular from P meets the line.
    target = Point(7, 2)
    base_line = Line.from_slope_intercept(0.5, -1)

    foot = foot_of_perpendicular(target, base_line)

    print("\nProblem 5")
    print("Point:", target)
    print("Line:", base_line)
    print("Perpendicular foot:", foot)
    print(
        "Distance:",
        f"{target.distance_to(foot):.6f}",
    )

    # Problem 6:
    # Determine whether two finite segments intersect.
    s1_start = Point(1, 1)
    s1_end = Point(7, 5)
    s2_start = Point(1, 5)
    s2_end = Point(7, 1)

    print("\nProblem 6")
    print(
        "Segments intersect:",
        segments_intersect(
            s1_start,
            s1_end,
            s2_start,
            s2_end,
        ),
    )


# ---------------------------------------------------------------------------
# 26. Interactive calculator
# ---------------------------------------------------------------------------

def read_float(prompt: str) -> float:
    """Safely read a floating-point number from standard input."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid number.")


def interactive_two_point_calculator() -> None:
    """
    Optional interactive demonstration.

    The function is kept separate so the main educational demonstrations
    remain deterministic and automated.
    """
    print("\n" + "=" * 72)
    print("18. INTERACTIVE TWO-POINT CALCULATOR")
    print("=" * 72)

    print("Enter coordinates for two points.")

    p1 = Point(
        read_float("x1: "),
        read_float("y1: "),
    )

    p2 = Point(
        read_float("x2: "),
        read_float("y2: "),
    )

    print("\nResults")
    print(f"Point 1: {p1}")
    print(f"Point 2: {p2}")
    print(f"Distance: {distance_formula(p1, p2):.10g}")
    print(f"Midpoint: {midpoint_formula(p1, p2)}")
    print(f"Slope: {slope(p1, p2)}")
    print(f"Line type: {slope_type(p1, p2)}")
    print(
        f"Angle of inclination: "
        f"{angle_of_inclination(p1, p2):.6f}°"
    )


# ---------------------------------------------------------------------------
# 27. Production-oriented considerations
# ---------------------------------------------------------------------------

def demonstrate_numerical_stability() -> None:
    print("\n" + "=" * 72)
    print("19. NUMERICAL STABILITY")
    print("=" * 72)

    # Floating-point arithmetic is approximate.
    # Direct equality can be misleading:
    value = 0.1 + 0.2

    print("0.1 + 0.2 =", value)
    print("Direct equality with 0.3:", value == 0.3)
    print(
        "Approximate equality with math.isclose:",
        math.isclose(value, 0.3),
    )

    # This matters in geometry because coordinates often come from
    # trigonometric functions, transformations, or measurements.
    rotated = rotate_point(Point(1, 0), 90)

    print("Rotation of (1,0) by 90°:", rotated)
    print(
        "x approximately zero:",
        almost_equal(rotated.x, 0),
    )
    print(
        "y approximately one:",
        almost_equal(rotated.y, 1),
    )


# ---------------------------------------------------------------------------
# 28. Main program
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Run the complete coordinate geometry lesson.

    Every section is deterministic except the optional interactive
    calculator, which is intentionally not invoked automatically.
    """
    print("=" * 72)
    print("COORDINATE GEOMETRY: COMPLETE PYTHON STUDY SCRIPT")
    print("=" * 72)

    demonstrate_cartesian_plane()
    demonstrate_distance_and_midpoint()
    demonstrate_slope()
    demonstrate_lines()
    demonstrate_parallel_perpendicular()
    demonstrate_intersections()
    demonstrate_collinearity_and_area()
    demonstrate_triangle_centers()
    demonstrate_circles()
    demonstrate_projection_and_reflection()
    demonstrate_vectors()
    demonstrate_segments()
    demonstrate_transformations()
    demonstrate_locus()
    demonstrate_point_sets()
    demonstrate_edge_cases()
    run_assertion_tests()
    worked_coordinate_geometry_problems()
    demonstrate_numerical_stability()

    print("\n" + "=" * 72)
    print("END OF COORDINATE GEOMETRY STUDY SCRIPT")
    print("=" * 72)


if __name__ == "__main__":
    main()
