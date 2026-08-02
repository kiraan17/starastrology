"""Swiss Ephemeris public-activation license gate (ADR-002)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from bhava360.kernel.errors import KernelError, KernelErrorCode

PublicActivation = Literal["blocked", "allowed"]
LicensePath = Literal["L1_AGPL", "L2_COMMERCIAL"]

STATUS_FILENAME = "adr002_public_status.json"
_PACKAGE_STATUS = Path(__file__).with_name(STATUS_FILENAME)


@dataclass(frozen=True, slots=True)
class SeLicenseStatus:
    adr: str
    public_activation: PublicActivation
    chosen_path: str | None
    evidence_ids: tuple[str, ...]
    approved_by: tuple[str, ...]
    approved_at: str | None
    notes: str
    schema_version: int
    status_file: str

    @property
    def public_api_allowed(self) -> bool:
        return self.public_activation == "allowed"

    def to_dict(self) -> dict[str, Any]:
        return {
            "adr": self.adr,
            "public_activation": self.public_activation,
            "chosen_path": self.chosen_path,
            "evidence_ids": list(self.evidence_ids),
            "approved_by": list(self.approved_by),
            "approved_at": self.approved_at,
            "notes": self.notes,
            "schema_version": self.schema_version,
            "status_file": self.status_file,
            "public_api_allowed": self.public_api_allowed,
        }


def _load_raw(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise KernelError(
            KernelErrorCode.LICENSE_GATE_BLOCKED,
            "ADR-002 public status file missing",
            {"path": str(path)},
        ) from exc
    except json.JSONDecodeError as exc:
        raise KernelError(
            KernelErrorCode.LICENSE_GATE_BLOCKED,
            "ADR-002 public status file is not valid JSON",
            {"path": str(path), "error": str(exc)},
        ) from exc
    if not isinstance(data, dict):
        raise KernelError(
            KernelErrorCode.LICENSE_GATE_BLOCKED,
            "ADR-002 public status root must be an object",
            {"path": str(path)},
        )
    return data


def _validate_allowed(data: dict[str, Any], *, path: Path) -> None:
    """Hard requirements before public_activation may be 'allowed'."""
    chosen = data.get("chosen_path")
    if chosen not in {"L1_AGPL", "L2_COMMERCIAL"}:
        raise KernelError(
            KernelErrorCode.LICENSE_GATE_BLOCKED,
            "public activation requires chosen_path L1_AGPL or L2_COMMERCIAL",
            {"path": str(path), "chosen_path": chosen},
        )
    evidence = data.get("evidence_ids") or []
    if not isinstance(evidence, list) or not evidence:
        raise KernelError(
            KernelErrorCode.LICENSE_GATE_BLOCKED,
            "public activation requires non-empty evidence_ids",
            {"path": str(path)},
        )
    approved_by = data.get("approved_by") or []
    if not isinstance(approved_by, list) or not approved_by:
        raise KernelError(
            KernelErrorCode.LICENSE_GATE_BLOCKED,
            "public activation requires approved_by entries (incl. legal)",
            {"path": str(path)},
        )
    if not data.get("approved_at"):
        raise KernelError(
            KernelErrorCode.LICENSE_GATE_BLOCKED,
            "public activation requires approved_at timestamp",
            {"path": str(path)},
        )


def load_se_license_status(status_path: Path | None = None) -> SeLicenseStatus:
    path = status_path or _PACKAGE_STATUS
    data = _load_raw(path)
    activation = data.get("public_activation", "blocked")
    if activation not in {"blocked", "allowed"}:
        raise KernelError(
            KernelErrorCode.LICENSE_GATE_BLOCKED,
            "public_activation must be blocked|allowed",
            {"path": str(path), "public_activation": activation},
        )
    if activation == "allowed":
        _validate_allowed(data, path=path)

    return SeLicenseStatus(
        adr=str(data.get("adr", "ADR-002")),
        public_activation=activation,  # type: ignore[arg-type]
        chosen_path=data.get("chosen_path"),
        evidence_ids=tuple(str(x) for x in (data.get("evidence_ids") or [])),
        approved_by=tuple(str(x) for x in (data.get("approved_by") or [])),
        approved_at=data.get("approved_at"),
        notes=str(data.get("notes") or ""),
        schema_version=int(data.get("schema_version") or 1),
        status_file=str(path),
    )


def is_public_api_allowed(status_path: Path | None = None) -> bool:
    return load_se_license_status(status_path).public_api_allowed


def assert_public_activation_allowed(
    *,
    status_path: Path | None = None,
    purpose: str = "public_api",
) -> SeLicenseStatus:
    """Raise LICENSE_GATE_BLOCKED unless ADR-002 public evidence is filed.

    Environment note: `BHAVA360_PUBLIC_API=1` does **not** bypass this gate.
    Only a reviewed status file flip (with path/evidence/approvals) unlocks activation.
    """
    # Explicitly ignore naive env overrides — document that they cannot bypass.
    _ = os.environ.get("BHAVA360_PUBLIC_API")
    status = load_se_license_status(status_path)
    if not status.public_api_allowed:
        raise KernelError(
            KernelErrorCode.LICENSE_GATE_BLOCKED,
            "Swiss Ephemeris public activation blocked by ADR-002",
            {
                "purpose": purpose,
                "adr": status.adr,
                "public_activation": status.public_activation,
                "chosen_path": status.chosen_path,
                "status_file": status.status_file,
                "notes": status.notes,
                "hint": "File Path L1 or L2 evidence under docs/decisions/adr-002-evidence/ then update adr002_public_status.json via review",
            },
        )
    return status
