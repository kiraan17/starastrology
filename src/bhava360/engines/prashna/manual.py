"""Manual Prashna inputs — never fabricated (TEC-088 / AGENTS hard rule)."""

from __future__ import annotations

from typing import Any

from bhava360.kernel.errors import KernelError, KernelErrorCode

ASHTAMANGALA_MANUAL_VARIANT = "ashtamangala_manual_passthrough_v1"


def normalize_ashtamangala_counts(raw: Any) -> dict[str, Any]:
    """
    Accept explicit shell/cowrie counts from the operator.

    Never invent counts from birth or query chart data.
    """
    if raw is None or raw == "" or raw == {}:
        return {
            "provided": False,
            "status": "awaiting_manual_input",
            "counts": None,
            "variant": ASHTAMANGALA_MANUAL_VARIANT,
            "notes": [
                "Ashtamangala shell counts must be entered by the operator.",
                "Engine will not fabricate ritual counts from chart data.",
            ],
        }

    if isinstance(raw, str):
        parts = [p.strip() for p in raw.replace(";", ",").split(",") if p.strip()]
        try:
            counts = [int(p) for p in parts]
        except ValueError as exc:
            raise KernelError(
                KernelErrorCode.UNSUPPORTED_CONFIG,
                "ashtamangala_counts must be comma-separated integers",
                {"raw": raw},
            ) from exc
    elif isinstance(raw, (list, tuple)):
        counts = [int(x) for x in raw]
    elif isinstance(raw, dict):
        # Preserve named buckets if provided.
        return {
            "provided": True,
            "status": "manual_input_recorded",
            "counts": {str(k): int(v) for k, v in raw.items()},
            "variant": ASHTAMANGALA_MANUAL_VARIANT,
            "notes": ["Operator-supplied named counts recorded without interpretation."],
        }
    else:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "ashtamangala_counts must be list, dict, or comma-separated string",
            {"type": type(raw).__name__},
        )

    if not counts:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "ashtamangala_counts empty",
        )
    if any(c < 0 for c in counts):
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "ashtamangala_counts must be non-negative",
            {"counts": counts},
        )

    return {
        "provided": True,
        "status": "manual_input_recorded",
        "counts": counts,
        "count_total": sum(counts),
        "variant": ASHTAMANGALA_MANUAL_VARIANT,
        "notes": [
            "Operator-supplied counts recorded without fabricating or interpreting outcomes.",
            "Full Ashtamangala verdict rules deferred (TEC-088).",
        ],
    }


__all__ = ["ASHTAMANGALA_MANUAL_VARIANT", "normalize_ashtamangala_counts"]
