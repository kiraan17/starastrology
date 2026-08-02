"""Birth-time rectification scan helpers — Candidate toolkit (TEC-095)."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from bhava360.chart.builder import ChartConstructor
from bhava360.chart.vargas import VargaId, varga_sign
from bhava360.kernel.derived import normalize_longitude, sign_from_longitude
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import ChartConfig, SubjectInput

RECTIFICATION_VARIANT = "rectification_scan_candidate_v1"

DEFAULT_WINDOW_MINUTES = 15.0
DEFAULT_STEP_MINUTES = 5.0
MAX_SAMPLES = 25

# Fingerprint fields tracked for transitions (structural only).
FINGERPRINT_FIELDS: tuple[str, ...] = (
    "lagna_sign",
    "lagna_nakshatra",
    "lagna_pada",
    "moon_nakshatra",
    "moon_pada",
    "vimshottari_balance_lord",
    "d9_lagna_sign",
    "d60_lagna_sign",
    "kunda_sign",
)


def kunda_from_lagna(lagna_longitude_sidereal_deg: float) -> dict[str, Any]:
    """Kunda point = lagna × 81 (mod 360) — Candidate structural marker."""
    lon = normalize_longitude(float(lagna_longitude_sidereal_deg) * 81.0)
    sign, sign_deg = sign_from_longitude(lon)
    return {
        "longitude_sidereal_deg": lon,
        "sign": sign,
        "sign_degree": sign_deg,
    }


def _clone_subject_at(subject: SubjectInput, local_dt: datetime) -> SubjectInput:
    return SubjectInput(
        local_datetime=local_dt,
        timezone_offset_minutes=subject.timezone_offset_minutes,
        timezone_id=subject.timezone_id,
        dst_ambiguity_policy=subject.dst_ambiguity_policy,
        latitude=subject.latitude,
        longitude=subject.longitude,
        location_label=subject.location_label,
        birth_time_uncertainty_minutes=subject.birth_time_uncertainty_minutes,
        input_kind="rectification_candidate",
    )


def chart_fingerprint(chart: dict[str, Any]) -> dict[str, Any]:
    """Extract structural markers used for sensitivity / transition detection."""
    asc = chart["angles"]["whole_sign"]["ascendant"]
    moon = next(p for p in chart["planets"] if p["planet"] == "Moon")
    lagna_lon = float(asc["longitude_sidereal_deg"])
    kunda = kunda_from_lagna(lagna_lon)
    d9 = varga_sign(lagna_lon, VargaId.D9)
    d60 = varga_sign(lagna_lon, VargaId.D60)
    balance = (chart.get("dashas") or {}).get("balance") or {}
    return {
        "local_datetime": (chart.get("input") or {}).get("local_datetime"),
        "lagna_sign": asc.get("sign"),
        "lagna_sign_degree": asc.get("sign_degree"),
        "lagna_longitude_sidereal_deg": lagna_lon,
        "lagna_nakshatra": asc.get("nakshatra"),
        "lagna_pada": asc.get("pada"),
        "moon_sign": moon.get("sign"),
        "moon_nakshatra": moon.get("nakshatra"),
        "moon_pada": moon.get("pada"),
        "moon_longitude_sidereal_deg": moon.get("longitude_sidereal_deg"),
        "vimshottari_balance_lord": balance.get("lord"),
        "vimshottari_balance_years": balance.get("balance_years"),
        "d9_lagna_sign": d9.sign,
        "d60_lagna_sign": d60.sign,
        "kunda_sign": kunda["sign"],
        "kunda_sign_degree": kunda["sign_degree"],
        "kunda_longitude_sidereal_deg": kunda["longitude_sidereal_deg"],
    }


def resolve_scan_grid(
    *,
    window_minutes: float,
    step_minutes: float,
    max_samples: int = MAX_SAMPLES,
) -> dict[str, Any]:
    """Build inclusive ±window offsets; widen step if sample cap would be exceeded."""
    if window_minutes <= 0:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "window_minutes must be > 0",
            {"window_minutes": window_minutes},
        )
    if step_minutes <= 0:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "step_minutes must be > 0",
            {"step_minutes": step_minutes},
        )
    if max_samples < 3:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "max_samples must be >= 3",
            {"max_samples": max_samples},
        )

    step = float(step_minutes)
    window = float(window_minutes)
    # samples ≈ 2*window/step + 1
    while True:
        n = int(round(2.0 * window / step)) + 1
        if n <= max_samples:
            break
        step *= 2.0
        if step > window:
            # fall back to endpoints + center only
            offsets = [-window, 0.0, window]
            return {
                "window_minutes": window,
                "step_minutes": step,
                "step_adjusted": True,
                "max_samples": max_samples,
                "offsets_minutes": offsets,
            }

    offsets: list[float] = []
    t = -window
    # inclusive end with float tolerance
    while t <= window + 1e-9:
        offsets.append(round(t, 6))
        t += step
    if 0.0 not in offsets:
        offsets.append(0.0)
        offsets.sort()
    return {
        "window_minutes": window,
        "step_minutes": step,
        "step_adjusted": step != float(step_minutes),
        "requested_step_minutes": float(step_minutes),
        "max_samples": max_samples,
        "offsets_minutes": offsets,
    }


def detect_transitions(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """List fingerprint field changes between consecutive samples."""
    transitions: list[dict[str, Any]] = []
    for i in range(1, len(samples)):
        prev = samples[i - 1]["fingerprint"]
        cur = samples[i]["fingerprint"]
        for field in FINGERPRINT_FIELDS:
            a = prev.get(field)
            b = cur.get(field)
            if a != b:
                transitions.append(
                    {
                        "field": field,
                        "from_offset_minutes": samples[i - 1]["offset_minutes"],
                        "to_offset_minutes": samples[i]["offset_minutes"],
                        "from_value": a,
                        "to_value": b,
                        "from_local_datetime": prev.get("local_datetime"),
                        "to_local_datetime": cur.get("local_datetime"),
                    }
                )
    return transitions


def stability_summary(
    samples: list[dict[str, Any]],
    transitions: list[dict[str, Any]],
) -> dict[str, Any]:
    """Per-field unique value counts and whether baseline is unique in window."""
    baseline = next(s for s in samples if s["offset_minutes"] == 0.0)
    bf = baseline["fingerprint"]
    per_field: dict[str, Any] = {}
    for field in FINGERPRINT_FIELDS:
        values = [s["fingerprint"].get(field) for s in samples]
        unique = sorted({str(v) for v in values})
        flipped = any(t["field"] == field for t in transitions)
        per_field[field] = {
            "unique_count": len(set(values)),
            "unique_values": unique,
            "flips_in_window": flipped,
            "baseline_value": bf.get(field),
        }
    return {
        "baseline_offset_minutes": 0.0,
        "sample_count": len(samples),
        "transition_count": len(transitions),
        "fields": per_field,
        "any_lagna_sign_flip": per_field["lagna_sign"]["flips_in_window"],
        "any_d9_lagna_flip": per_field["d9_lagna_sign"]["flips_in_window"],
        "any_d60_lagna_flip": per_field["d60_lagna_sign"]["flips_in_window"],
        "any_kunda_flip": per_field["kunda_sign"]["flips_in_window"],
    }


def normalize_manual_events(events: Any) -> dict[str, Any]:
    """Passthrough for life-event anchors — never scored in this thin slice."""
    if events is None or events == "" or events == []:
        return {
            "provided": False,
            "status": "awaiting_manual_input",
            "events": [],
            "note": "Event-matching rule pack not loaded; anchors are not scored.",
        }
    rows: list[dict[str, Any]] = []
    if isinstance(events, str):
        # "label|YYYY-MM-DD, label2|YYYY-MM-DD"
        for part in events.split(","):
            part = part.strip()
            if not part:
                continue
            if "|" in part:
                label, date = part.split("|", 1)
            else:
                label, date = part, None
            rows.append({"label": label.strip(), "date": (date or "").strip() or None})
    elif isinstance(events, list):
        for item in events:
            if isinstance(item, dict):
                rows.append(
                    {
                        "label": item.get("label") or item.get("name"),
                        "date": item.get("date"),
                    }
                )
            else:
                rows.append({"label": str(item), "date": None})
    else:
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            "rectification events must be a list or comma-separated string",
        )
    return {
        "provided": True,
        "status": "passthrough_unscored",
        "events": rows,
        "note": "Anchors accepted as manual input only — scoring deferred.",
    }


def run_rectification_scan(
    subject: SubjectInput,
    *,
    config: ChartConfig | None = None,
    window_minutes: float | None = None,
    step_minutes: float = DEFAULT_STEP_MINUTES,
    max_samples: int = MAX_SAMPLES,
    events: Any = None,
) -> dict[str, Any]:
    """
    Sample charts across ±window and report fingerprint transitions.

    Does not select or assert a true birth time.
    """
    window = window_minutes
    if window is None:
        if subject.birth_time_uncertainty_minutes and subject.birth_time_uncertainty_minutes > 0:
            window = float(subject.birth_time_uncertainty_minutes)
        else:
            window = DEFAULT_WINDOW_MINUTES

    grid = resolve_scan_grid(
        window_minutes=window,
        step_minutes=step_minutes,
        max_samples=max_samples,
    )
    cfg = config or ChartConfig()
    ctor = ChartConstructor(cfg)

    samples: list[dict[str, Any]] = []
    for offset in grid["offsets_minutes"]:
        local_dt = subject.local_datetime + timedelta(minutes=offset)
        cand = _clone_subject_at(subject, local_dt)
        chart = ctor.build(
            cand,
            include_vimshottari=True,
            include_relationships=False,
            dasha_years_ahead=1.0,
        ).to_dict()
        fp = chart_fingerprint(chart)
        samples.append(
            {
                "offset_minutes": offset,
                "is_baseline": offset == 0.0,
                "fingerprint": fp,
            }
        )

    transitions = detect_transitions(samples)
    stability = stability_summary(samples, transitions)
    manual_events = normalize_manual_events(events)

    baseline = next(s for s in samples if s["is_baseline"])

    return {
        "variant": RECTIFICATION_VARIANT,
        "stated_local_datetime": subject.local_datetime.isoformat(sep=" "),
        "grid": grid,
        "baseline": baseline,
        "samples": samples,
        "transitions": transitions,
        "stability": stability,
        "manual_events": manual_events,
        "summary": {
            "sample_count": len(samples),
            "transition_count": len(transitions),
            "window_minutes": grid["window_minutes"],
            "step_minutes": grid["step_minutes"],
            "lagna_sign_flips": stability["any_lagna_sign_flip"],
            "d9_lagna_flips": stability["any_d9_lagna_flip"],
            "d60_lagna_flips": stability["any_d60_lagna_flip"],
            "kunda_flips": stability["any_kunda_flip"],
            "events_provided": manual_events["provided"],
            "winner_selected": False,
        },
    }


__all__ = [
    "DEFAULT_STEP_MINUTES",
    "DEFAULT_WINDOW_MINUTES",
    "FINGERPRINT_FIELDS",
    "MAX_SAMPLES",
    "RECTIFICATION_VARIANT",
    "chart_fingerprint",
    "detect_transitions",
    "kunda_from_lagna",
    "normalize_manual_events",
    "resolve_scan_grid",
    "run_rectification_scan",
    "stability_summary",
]
