"""Compare outputs from multiple configured models without voting on truth."""
from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Callable, Any
import json


@dataclass(frozen=True)
class ModelOutput:
    model_id: str
    provider: str
    status: str
    output: str
    output_hash: str
    error_type: str = ""


@dataclass(frozen=True)
class ModelComparison:
    comparison_id: str
    prompt: str
    outputs: tuple[ModelOutput, ...]
    agreement: str
    distinct_output_count: int
    warnings: tuple[str, ...]
    interpretation: str


class MultiModelComparator:
    """Run explicitly supplied callables and report agreement/divergence.

    This component does not claim statistical independence, rank model quality,
    choose a winner, or infer scientific truth from majority agreement.
    """

    def compare(
        self,
        comparison_id: str,
        prompt: str,
        models: dict[str, tuple[str, Callable[[str], Any]]],
    ) -> ModelComparison:
        if not comparison_id.strip() or not prompt.strip():
            raise ValueError("comparison_id and prompt are required")
        if len(models) < 2:
            raise ValueError("At least two configured models are required")
        outputs: list[ModelOutput] = []
        for model_id, (provider, invoke) in models.items():
            if not model_id.strip() or not provider.strip() or not callable(invoke):
                raise ValueError("Each model needs an ID, provider name and callable")
            try:
                raw = invoke(prompt)
                if isinstance(raw, str):
                    rendered = raw.strip()
                elif hasattr(raw, "summary"):
                    rendered = str(raw.summary).strip()
                else:
                    rendered = json.dumps(raw, ensure_ascii=False, sort_keys=True, default=str)
                digest = sha256(rendered.encode("utf-8")).hexdigest()
                outputs.append(ModelOutput(
                    model_id, provider, "completed", rendered, digest
                ))
            except Exception as exc:
                outputs.append(ModelOutput(
                    model_id, provider, "failed", "",
                    sha256(b"").hexdigest(), type(exc).__name__,
                ))

        successful = [item for item in outputs if item.status == "completed"]
        distinct = len({item.output_hash for item in successful})
        if len(successful) < 2:
            agreement = "insufficient_outputs"
        elif distinct == 1:
            agreement = "identical_outputs"
        else:
            agreement = "divergent_outputs"

        warnings = [
            "Agreement between model outputs is not independent scientific evidence or proof.",
            "Model independence is not established by different model IDs or provider labels.",
            "Outputs are drafts; check factual claims against traceable primary sources.",
        ]
        if any(item.status == "failed" for item in outputs):
            warnings.append("At least one model failed; the comparison is incomplete.")
        if distinct > 1:
            warnings.append("Different outputs require claim-by-claim review; disagreement alone does not identify which output is correct.")

        interpretation = {
            "insufficient_outputs": "Fewer than two models completed; no meaningful comparison can be made.",
            "identical_outputs": "Completed outputs are textually identical. This does not validate their content.",
            "divergent_outputs": "Completed outputs differ. Preserve each version and investigate the specific disagreements.",
        }[agreement]
        return ModelComparison(
            comparison_id, prompt, tuple(outputs), agreement, distinct,
            tuple(warnings), interpretation,
        )

    @staticmethod
    def to_dict(comparison: ModelComparison) -> dict:
        return asdict(comparison)
