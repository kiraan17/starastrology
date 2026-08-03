"""Public API activation helpers — blocked until ADR-002 evidence is filed."""

from __future__ import annotations

from typing import Any

from bhava360.api.freeze_manifest import freeze_candidate_summary
from bhava360.licensing import assert_public_activation_allowed, load_se_license_status


def public_api_readiness() -> dict[str, Any]:
    """Return readiness report without raising (for health/console)."""
    status = load_se_license_status()
    freeze = freeze_candidate_summary()
    ready = bool(status.public_api_allowed) and bool(freeze.get("public_api_eligible"))
    blocked: list[str] = []
    if not status.public_api_allowed:
        blocked.append("ADR-002 license gate blocked")
    if not freeze.get("public_api_eligible"):
        blocked.extend(list(freeze.get("blocked_reasons") or []))
    return {
        "ready": ready,
        "license_gate": status.to_dict(),
        "freeze_candidate": freeze,
        "blocked_reasons": blocked,
        "message": (
            "Public API activation allowed under filed ADR-002 evidence and freeze eligibility"
            if ready
            else "Public API not ready — see blocked_reasons (license + freeze-candidate gates)"
        ),
    }


def enable_public_api_surface() -> dict[str, Any]:
    """Gatekeeper entrypoint for future public routers/services.

    Raises LICENSE_GATE_BLOCKED until status JSON is flipped with evidence.
    Also refuses while freeze-candidate is not public_api_eligible (engineering gate).
    """
    status = assert_public_activation_allowed(purpose="public_api_surface")
    freeze = freeze_candidate_summary()
    if not freeze.get("public_api_eligible"):
        from bhava360.kernel.errors import KernelError, KernelErrorCode

        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "Public API surface blocked by freeze-candidate package",
            {
                "freeze_candidate": freeze,
                "hint": "Complete expert freeze + ADR-002; do not flip public_api_eligible casually",
            },
        )
    return {
        "enabled": True,
        "license_gate": status.to_dict(),
        "freeze_candidate": freeze,
    }
