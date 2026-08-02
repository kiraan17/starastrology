"""Public API activation helpers — blocked until ADR-002 evidence is filed."""

from __future__ import annotations

from typing import Any

from bhava360.licensing import assert_public_activation_allowed, load_se_license_status


def public_api_readiness() -> dict[str, Any]:
    """Return readiness report without raising (for health/console)."""
    status = load_se_license_status()
    return {
        "ready": status.public_api_allowed,
        "license_gate": status.to_dict(),
        "message": (
            "Public API activation allowed under filed ADR-002 evidence"
            if status.public_api_allowed
            else "Public API activation blocked — file ADR-002 Path L1 or L2 evidence"
        ),
    }


def enable_public_api_surface() -> dict[str, Any]:
    """Gatekeeper entrypoint for future public routers/services.

    Raises LICENSE_GATE_BLOCKED until status JSON is flipped with evidence.
    """
    status = assert_public_activation_allowed(purpose="public_api_surface")
    return {
        "enabled": True,
        "license_gate": status.to_dict(),
    }
