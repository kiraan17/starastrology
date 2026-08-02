"""Freeze-candidate manifest loader (P24a) — never implies Frozen/Approved."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from bhava360.kernel.errors import KernelError, KernelErrorCode

def default_manifest_path() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "release" / "freeze-candidate-manifest-v0.1.json"
        if candidate.is_file():
            return candidate
    return here.parents[3] / "release" / "freeze-candidate-manifest-v0.1.json"


@lru_cache(maxsize=4)
def load_freeze_candidate_manifest(path: str | None = None) -> dict[str, Any]:
    """Load the freeze-candidate JSON. Does not unlock public API."""
    p = Path(path) if path else default_manifest_path()
    if not p.is_file():
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "freeze-candidate manifest not found",
            {"path": str(p)},
        )
    data = json.loads(p.read_text(encoding="utf-8"))
    if data.get("frozen") is True:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "manifest claims frozen=true but freeze authority has not run — refuse to load",
            {"manifest_id": data.get("manifest_id")},
        )
    if data.get("freeze_status") != "candidate":
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "only freeze_status=candidate manifests are loadable in this package",
            {"freeze_status": data.get("freeze_status")},
        )
    if data.get("expert_approved") is True:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "manifest claims expert_approved without recorded reviews — refuse to load",
            {"manifest_id": data.get("manifest_id")},
        )
    if data.get("public_api_eligible") is True:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "candidate manifest must not set public_api_eligible=true",
            {"manifest_id": data.get("manifest_id")},
        )
    return data


def freeze_candidate_summary(path: str | None = None) -> dict[str, Any]:
    """Compact readiness fields for health / public_api_readiness."""
    m = load_freeze_candidate_manifest(path)
    engines = m.get("engines") or []
    return {
        "manifest_id": m.get("manifest_id"),
        "manifest_version": m.get("manifest_version"),
        "freeze_status": m.get("freeze_status"),
        "frozen": bool(m.get("frozen")),
        "expert_approved": bool(m.get("expert_approved")),
        "public_api_eligible": bool(m.get("public_api_eligible")),
        "engine_count": len(engines),
        "blocked_reasons": list(m.get("blocked_reasons") or []),
        "programme_gates": dict(m.get("programme_gates") or {}),
    }


def clear_manifest_cache() -> None:
    load_freeze_candidate_manifest.cache_clear()


__all__ = [
    "clear_manifest_cache",
    "default_manifest_path",
    "freeze_candidate_summary",
    "load_freeze_candidate_manifest",
]
