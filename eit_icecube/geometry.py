"""Deterministic, dependency-free small 3D linear algebra."""
from __future__ import annotations
import math


def norm(a):
    return math.sqrt(sum(x * x for x in a))


def unit(a):
    length = norm(a)
    if not math.isfinite(length) or length < 1e-12:
        raise ValueError("Cannot normalize a zero/non-finite vector")
    return [float(x) / length for x in a]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def angle_deg(a, b):
    u, v = unit(a), unit(b)
    return math.degrees(math.acos(max(-1.0, min(1.0, dot(u, v)))))


def solve_3x3(a, b):
    """Gaussian elimination with pivoting, rejecting ill-conditioned geometry."""
    m = [list(map(float, a[i])) + [float(b[i])] for i in range(3)]
    scale = max(abs(m[i][j]) for i in range(3) for j in range(3))
    if not math.isfinite(scale) or scale == 0:
        raise ValueError("Singular sensor geometry")
    for col in range(3):
        pivot = max(range(col, 3), key=lambda k: abs(m[k][col]))
        if abs(m[pivot][col]) <= scale * 1e-11:
            raise ValueError("Ill-conditioned sensor geometry")
        m[col], m[pivot] = m[pivot], m[col]
        d = m[col][col]
        for j in range(col, 4):
            m[col][j] /= d
        for row in range(col + 1, 3):
            factor = m[row][col]
            for j in range(col, 4):
                m[row][j] -= factor * m[col][j]
    x = [0.0] * 3
    for i in range(2, -1, -1):
        x[i] = m[i][3] - sum(m[i][j] * x[j] for j in range(i + 1, 3))
    if not all(math.isfinite(v) for v in x):
        raise ValueError("Non-finite solution")
    return x


# Guardrail for the toy fit, NOT a validated detector/event-quality cut.
# kappa is computed for the centered, weighted 3D position Gram matrix.
MAX_GEOMETRY_CONDITION_NUMBER = 10_000.0


def symmetric_eigenvalues_3x3(a):
    """Three eigenvalues of a finite symmetric 3x3 matrix (Jacobi rotations).

    The routine scales by the largest coefficient first to avoid false
    overflow in its rotations. Results are rescaled to the input matrix units.
    No external linear algebra packages are required.
    """
    if len(a) != 3 or any(len(row) != 3 for row in a):
        raise ValueError("Expected a 3x3 geometry matrix")
    try:
        m = [[float(v) for v in row] for row in a]
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Non-numeric geometry matrix") from exc
    if not all(math.isfinite(v) for row in m for v in row):
        raise ValueError("Non-finite geometry matrix")
    scale = max(abs(v) for row in m for v in row)
    if scale == 0.0:
        raise ValueError("Singular sensor geometry")
    # The weighted centered Gram matrix is theoretically symmetric.
    # Use averaging to eliminate floating-point accumulation asymmetry.
    m = [[m[i][j] / scale for j in range(3)] for i in range(3)]
    for i in range(3):
        for j in range(i + 1, 3):
            x = 0.5 * (m[i][j] + m[j][i])
            m[i][j] = x
            m[j][i] = x
    for _ in range(40):
        p, r = max(((0, 1), (0, 2), (1, 2)), key=lambda pair: abs(m[pair[0]][pair[1]]))
        apq = m[p][r]
        if abs(apq) <= 1e-15:
            break
        app, aqq = m[p][p], m[r][r]
        tau = (aqq - app) / (2.0 * apq)
        t = math.copysign(1.0, tau) / (abs(tau) + math.hypot(1.0, tau))
        c = 1.0 / math.sqrt(1.0 + t*t)
        sn = t*c
        for k in range(3):
            if k not in (p, r):
                mkp, mkq = m[k][p], m[k][r]
                m[k][p] = m[p][k] = c * mkp - sn * mkq
                m[k][r] = m[r][k] = sn * mkp + c * mkq
        m[p][p] = app - t * apq
        m[r][r] = aqq + t * apq
        m[p][r] = m[r][p] = 0.0
    return sorted([m[0][0] * scale, m[1][1] * scale, m[2][2] * scale])


def geometry_condition_number(gram):
    """2-norm condition number of a positive 3D position Gram matrix.

    Infinite condition number means nonpositive/indistinguishable small
    eigenvalue. Upstream fail-closed handling must reject such geometry.
    """
    low, _, high = symmetric_eigenvalues_3x3(gram)
    if low <= 0.0 or not math.isfinite(high) or high <= 0:
        return math.inf
    return high / low


def require_well_conditioned_geometry(gram, *, max_condition=MAX_GEOMETRY_CONDITION_NUMBER):
    """Reject nearly degenerate weighted geometry before a timing fit.

    The 1e4 boundary is an explicit engineering heuristic for this synthetic
    benchmark, not an IceCube-approved or statistically calibrated limit.
    """
    if isinstance(max_condition, bool) or not isinstance(max_condition, (int, float)):
        raise ValueError("Invalid geometry condition limit")
    if not math.isfinite(max_condition) or max_condition < 1:
        raise ValueError("Invalid geometry condition limit")
    condition = geometry_condition_number(gram)
    if not math.isfinite(condition) or condition > max_condition:
        raise ValueError("Ill-conditioned sensor geometry (condition number exceeds toy safety limit)")
    return condition
