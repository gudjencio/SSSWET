"""Covariance-aware first-order uncertainty budgets for measured quantities."""
from __future__ import annotations

from math import isfinite, sqrt

MAX_COMPONENTS = 100


def _finite(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{label} must be finite")
    return float(value)


def _positive_semidefinite(matrix: list[list[float]], tolerance: float = 1e-10) -> bool:
    """Check PSD with an LDL' factorization that permits zero pivots."""
    size = len(matrix)
    lower = [[0.0] * size for _ in range(size)]
    diagonal = [0.0] * size
    for i in range(size):
        pivot = matrix[i][i] - sum(lower[i][k] ** 2 * diagonal[k] for k in range(i))
        if pivot < -tolerance:
            return False
        diagonal[i] = max(0.0, pivot)
        lower[i][i] = 1.0
        for j in range(i + 1, size):
            residual = matrix[j][i] - sum(lower[j][k] * lower[i][k] * diagonal[k] for k in range(i))
            if diagonal[i] > tolerance:
                lower[j][i] = residual / diagonal[i]
            elif abs(residual) > tolerance:
                return False
    return True


def propagate_linear(components: list[dict], correlation_matrix: list[list[float]] | None = None) -> dict:
    """Propagate standard uncertainties through y=sum(c_i*x_i), retaining covariance."""
    if not isinstance(components, list) or not 1 <= len(components) <= MAX_COMPONENTS:
        raise ValueError(f"components must contain 1 to {MAX_COMPONENTS} entries")
    names, sensitivities, uncertainties = [], [], []
    for item in components:
        if not isinstance(item, dict):
            raise ValueError("each component must be an object")
        name = item.get("name")
        if not isinstance(name, str) or not name.strip() or len(name) > 120 or name in names:
            raise ValueError("component names must be unique non-empty strings")
        names.append(name)
        sensitivities.append(_finite(item.get("sensitivity"), "sensitivity"))
        uncertainty = _finite(item.get("standard_uncertainty"), "standard_uncertainty")
        if uncertainty < 0:
            raise ValueError("standard_uncertainty cannot be negative")
        uncertainties.append(uncertainty)
    size = len(components)
    if correlation_matrix is None:
        correlation_matrix = [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]
    if not isinstance(correlation_matrix, list) or len(correlation_matrix) != size:
        raise ValueError("correlation_matrix must be square and match the component count")
    matrix = []
    for row in correlation_matrix:
        if not isinstance(row, list) or len(row) != size:
            raise ValueError("correlation_matrix must be square")
        matrix.append([_finite(value, "correlation") for value in row])
    for i in range(size):
        if abs(matrix[i][i] - 1.0) > 1e-9:
            raise ValueError("correlation matrix diagonal values must equal 1")
        for j in range(size):
            if abs(matrix[i][j]) > 1.0 + 1e-9 or abs(matrix[i][j] - matrix[j][i]) > 1e-9:
                raise ValueError("correlation matrix must be symmetric with values in [-1, 1]")
    if not _positive_semidefinite(matrix):
        raise ValueError("correlation matrix must be positive semidefinite")
    weighted = [sensitivities[i] * uncertainties[i] for i in range(size)]
    variance = sum(weighted[i] * matrix[i][j] * weighted[j] for i in range(size) for j in range(size))
    if variance < -1e-9:
        raise ValueError("computed variance is negative; check the covariance inputs")
    variance = max(0.0, variance)
    return {
        "method": "first_order_covariance_propagation",
        "component_count": size,
        "combined_standard_uncertainty": sqrt(variance),
        "expanded_uncertainty_k1_96": 1.96 * sqrt(variance),
        "worst_case_absolute_bound": sum(abs(weighted[i]) for i in range(size)),
        "variance": variance,
        "components": [
            {"name": names[i], "sensitivity": sensitivities[i], "standard_uncertainty": uncertainties[i], "weighted_uncertainty": weighted[i]}
            for i in range(size)
        ],
        "correlation_assumption": "user-supplied matrix" if any(abs(matrix[i][j]) > 1e-12 for i in range(size) for j in range(size) if i != j) else "independent components",
        "linearization_required": True,
        "scientific_validity_established": False,
    }
