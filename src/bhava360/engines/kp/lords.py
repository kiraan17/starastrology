from __future__ import annotations

from dataclasses import dataclass

from bhava360.kernel.derived import NAKSHATRA_SPAN, nakshatra_from_longitude, normalize_longitude
from bhava360.kernel.models import NAKSHATRAS_VEDASTRO, PlanetName
from bhava360.timing.vimshottari import (
    TOTAL_YEARS,
    VIMSHOTTARI_ORDER,
    VIMSHOTTARI_YEARS,
    lord_sequence_from,
    nakshatra_lord,
)


@dataclass(slots=True)
class LordSpan:
    lord: PlanetName
    start_offset_deg: float
    end_offset_deg: float

    @property
    def span_deg(self) -> float:
        return self.end_offset_deg - self.start_offset_deg


@dataclass(slots=True)
class KPLordChain:
    longitude_sidereal_deg: float
    nakshatra: str
    nakshatra_index: int
    pada: int
    star_lord: PlanetName
    sub_lord: PlanetName
    sub_sub_lord: PlanetName
    offset_in_nakshatra_deg: float
    offset_in_sub_deg: float

    def to_dict(self) -> dict:
        return {
            "longitude_sidereal_deg": self.longitude_sidereal_deg,
            "nakshatra": self.nakshatra,
            "nakshatra_index": self.nakshatra_index,
            "pada": self.pada,
            "star_lord": self.star_lord.value,
            "sub_lord": self.sub_lord.value,
            "sub_sub_lord": self.sub_sub_lord.value,
            "offset_in_nakshatra_deg": self.offset_in_nakshatra_deg,
            "offset_in_sub_deg": self.offset_in_sub_deg,
        }


def _proportional_spans(start_lord: PlanetName, total_span_deg: float) -> list[LordSpan]:
    """Divide a span by Vimshottari year proportions, starting at start_lord."""
    lords = lord_sequence_from(start_lord)
    spans: list[LordSpan] = []
    cursor = 0.0
    for lord in lords:
        width = total_span_deg * VIMSHOTTARI_YEARS[lord] / TOTAL_YEARS
        spans.append(LordSpan(lord=lord, start_offset_deg=cursor, end_offset_deg=cursor + width))
        cursor += width
    # Fix float drift on last edge.
    if spans:
        spans[-1] = LordSpan(
            lord=spans[-1].lord,
            start_offset_deg=spans[-1].start_offset_deg,
            end_offset_deg=total_span_deg,
        )
    return spans


def _locate(offset: float, spans: list[LordSpan]) -> tuple[LordSpan, float]:
    """Return spanning lord and offset within that span."""
    for i, span in enumerate(spans):
        # Last span is closed on the right.
        if i < len(spans) - 1:
            if span.start_offset_deg <= offset < span.end_offset_deg:
                return span, offset - span.start_offset_deg
        else:
            if span.start_offset_deg <= offset <= span.end_offset_deg + 1e-12:
                return span, min(offset - span.start_offset_deg, span.span_deg)
    # Clamp to last for float edge cases.
    last = spans[-1]
    return last, last.span_deg


def kp_lord_chain(longitude_sidereal_deg: float) -> KPLordChain:
    """Compute KP star / sub / sub-sub lords for a sidereal longitude."""
    lon = normalize_longitude(longitude_sidereal_deg)
    name, pada, _label = nakshatra_from_longitude(lon)
    idx = NAKSHATRAS_VEDASTRO.index(name)
    star = nakshatra_lord(idx)
    offset_nak = lon % NAKSHATRA_SPAN

    sub_spans = _proportional_spans(star, NAKSHATRA_SPAN)
    sub_span, offset_sub = _locate(offset_nak, sub_spans)

    sub_sub_spans = _proportional_spans(sub_span.lord, sub_span.span_deg)
    sub_sub_span, _offset_ss = _locate(offset_sub, sub_sub_spans)

    return KPLordChain(
        longitude_sidereal_deg=lon,
        nakshatra=name,
        nakshatra_index=idx,
        pada=pada,
        star_lord=star,
        sub_lord=sub_span.lord,
        sub_sub_lord=sub_sub_span.lord,
        offset_in_nakshatra_deg=offset_nak,
        offset_in_sub_deg=offset_sub,
    )
