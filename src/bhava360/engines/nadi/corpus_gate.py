"""Nakshatra Nadi corpus gate (P13 / SRC-009)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from bhava360.kernel.errors import KernelError, KernelErrorCode

CorpusStatus = Literal["blocked", "approved"]

STATUS_FILENAME = "nakshatra_nadi_corpus_status.json"
_PACKAGE_STATUS = Path(__file__).with_name(STATUS_FILENAME)


@dataclass(frozen=True, slots=True)
class NadiCorpusStatus:
    source_id: str
    technique_ids: tuple[str, ...]
    corpus_status: CorpusStatus
    corpus_id: str | None
    approval_status: str
    approved_by: tuple[str, ...]
    approved_at: str | None
    notes: str
    schema_version: int
    status_file: str

    @property
    def interpretive_rules_allowed(self) -> bool:
        return self.corpus_status == "approved"

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "technique_ids": list(self.technique_ids),
            "corpus_status": self.corpus_status,
            "corpus_id": self.corpus_id,
            "approval_status": self.approval_status,
            "approved_by": list(self.approved_by),
            "approved_at": self.approved_at,
            "notes": self.notes,
            "schema_version": self.schema_version,
            "status_file": self.status_file,
            "interpretive_rules_allowed": self.interpretive_rules_allowed,
        }


def _load_raw(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise KernelError(
            KernelErrorCode.CORPUS_GATE_BLOCKED,
            "Nakshatra Nadi corpus status file missing",
            {"path": str(path)},
        ) from exc
    except json.JSONDecodeError as exc:
        raise KernelError(
            KernelErrorCode.CORPUS_GATE_BLOCKED,
            "Nakshatra Nadi corpus status file is not valid JSON",
            {"path": str(path), "error": str(exc)},
        ) from exc
    if not isinstance(data, dict):
        raise KernelError(
            KernelErrorCode.CORPUS_GATE_BLOCKED,
            "Nakshatra Nadi corpus status root must be an object",
            {"path": str(path)},
        )
    return data


def _validate_approved(data: dict[str, Any], *, path: Path) -> None:
    if not data.get("corpus_id"):
        raise KernelError(
            KernelErrorCode.CORPUS_GATE_BLOCKED,
            "approved Nadi corpus requires corpus_id",
            {"path": str(path)},
        )
    if data.get("approval_status") != "Approved":
        raise KernelError(
            KernelErrorCode.CORPUS_GATE_BLOCKED,
            "approved Nadi corpus requires approval_status=Approved",
            {"path": str(path), "approval_status": data.get("approval_status")},
        )
    approved_by = data.get("approved_by") or []
    if not isinstance(approved_by, list) or not approved_by:
        raise KernelError(
            KernelErrorCode.CORPUS_GATE_BLOCKED,
            "approved Nadi corpus requires approved_by entries",
            {"path": str(path)},
        )
    if not data.get("approved_at"):
        raise KernelError(
            KernelErrorCode.CORPUS_GATE_BLOCKED,
            "approved Nadi corpus requires approved_at",
            {"path": str(path)},
        )


def load_nadi_corpus_status(status_path: Path | None = None) -> NadiCorpusStatus:
    path = status_path or _PACKAGE_STATUS
    data = _load_raw(path)
    status = data.get("corpus_status", "blocked")
    if status not in {"blocked", "approved"}:
        raise KernelError(
            KernelErrorCode.CORPUS_GATE_BLOCKED,
            "corpus_status must be blocked|approved",
            {"path": str(path), "corpus_status": status},
        )
    if status == "approved":
        _validate_approved(data, path=path)

    return NadiCorpusStatus(
        source_id=str(data.get("source_id", "SRC-009")),
        technique_ids=tuple(str(x) for x in (data.get("technique_ids") or ["TEC-054", "TEC-055"])),
        corpus_status=status,  # type: ignore[arg-type]
        corpus_id=data.get("corpus_id"),
        approval_status=str(data.get("approval_status") or "Candidate"),
        approved_by=tuple(str(x) for x in (data.get("approved_by") or [])),
        approved_at=data.get("approved_at"),
        notes=str(data.get("notes") or ""),
        schema_version=int(data.get("schema_version") or 1),
        status_file=str(path),
    )


def is_nadi_corpus_approved(status_path: Path | None = None) -> bool:
    return load_nadi_corpus_status(status_path).interpretive_rules_allowed


def assert_nadi_corpus_approved(
    *,
    status_path: Path | None = None,
    purpose: str = "nakshatra_nadi_chains",
) -> NadiCorpusStatus:
    status = load_nadi_corpus_status(status_path)
    if not status.interpretive_rules_allowed:
        raise KernelError(
            KernelErrorCode.CORPUS_GATE_BLOCKED,
            "Nakshatra Nadi interpretive rules blocked until Approved corpus is filed",
            {
                "purpose": purpose,
                "source_id": status.source_id,
                "corpus_status": status.corpus_status,
                "corpus_id": status.corpus_id,
                "status_file": status.status_file,
                "notes": status.notes,
                "hint": "Complete docs/sources/nadi-corpus/SRC-009-APPROVAL-CHECKLIST.md then flip status JSON under review",
            },
        )
    return status
