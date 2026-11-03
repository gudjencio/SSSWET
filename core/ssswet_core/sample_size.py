"""Transparent sample-size planning for a mean estimate; not a substitute for study design."""
from __future__ import annotations
import math
from statistics import NormalDist

def estimate_mean(*, standard_deviation: float, margin_of_error: float, confidence: float = 0.95) -> dict:
    values = (standard_deviation, margin_of_error, confidence)
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise ValueError("inputs must be finite numbers")
    if standard_deviation <= 0 or margin_of_error <= 0 or not 0 < confidence < 1:
        raise ValueError("standard_deviation and margin_of_error must be positive; confidence must be between 0 and 1")
    z = NormalDist().inv_cdf((1 + confidence) / 2)
    required = math.ceil((z * standard_deviation / margin_of_error) ** 2)
    return {"required_sample_size": required, "z_value": z, "standard_deviation": standard_deviation, "margin_of_error": margin_of_error, "confidence": confidence, "assumptions": ["independent observations", "approximately normal sampling distribution"], "finite_population_correction_applied": False}
