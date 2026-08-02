from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from bhava360.chart.aspects import build_relationship_graph
from bhava360.chart.bhava import HouseMapping, map_rasi_vs_bhava
from bhava360.chart.dignity import DignityResult, classify_dignity, sign_lord
from bhava360.chart.vargas import DEFAULT_VARGAS, VargaId, compute_vargas
from bhava360.kernel.models import ChartConfig, HouseSystem, PlanetName, SubjectInput
from bhava360.kernel.provider import SwissEphemerisProvider
from bhava360.kernel.timeutil import resolve_subject_time
from bhava360.timing.vimshottari import DashaLevel, build_vimshottari_tree


@dataclass(slots=True)
class ConstructedChart:
    chart_id: str
    created_at_utc: str
    input: dict[str, Any]
    config: dict[str, Any]
    resolved_time: dict[str, Any]
    library: dict[str, str]
    ayanamsa_degrees: float
    angles: dict[str, Any]
    planets: list[dict[str, Any]]
    house_mappings: list[dict[str, Any]]
    day_window: dict[str, Any] | None
    dashas: dict[str, Any] | None = None
    relationships: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "chart_id": self.chart_id,
            "created_at_utc": self.created_at_utc,
            "input": self.input,
            "config": self.config,
            "resolved_time": self.resolved_time,
            "library": self.library,
            "ayanamsa_degrees": self.ayanamsa_degrees,
            "angles": self.angles,
            "planets": self.planets,
            "house_mappings": self.house_mappings,
            "day_window": self.day_window,
            "dashas": self.dashas,
            "relationships": self.relationships,
        }


class ChartConstructor:
    """Build derived chart structures from the astronomy kernel (no school verdicts)."""

    def __init__(self, config: ChartConfig | None = None) -> None:
        self.config = config or ChartConfig()
        self.config.calc_library_version = "bhava360-kernel-0.5.0"
        self.provider = SwissEphemerisProvider(self.config)

    def build(
        self,
        subject: SubjectInput,
        *,
        vargas: tuple[VargaId, ...] | list[VargaId] | None = None,
        include_d150: bool = False,
        force_d150: bool = False,
        bhava_system: HouseSystem = HouseSystem.PLACIDUS,
        include_vimshottari: bool = True,
        dasha_depth: DashaLevel = DashaLevel.ANTAR,
        dasha_years_ahead: float = 120.0,
        include_relationships: bool = True,
    ) -> ConstructedChart:
        resolved = resolve_subject_time(subject)
        positions = self.provider.all_planet_positions(subject)
        whole = self.provider.houses(subject, HouseSystem.WHOLE_SIGN)
        bhava_houses = self.provider.houses(subject, bhava_system)
        sun = next(p for p in positions if p.planet == PlanetName.SUN)

        planet_rows: list[dict[str, Any]] = []
        mappings: list[HouseMapping] = []
        for pos in positions:
            dignity: DignityResult = classify_dignity(
                pos.planet,
                pos.longitude_sidereal_deg,
                sun_longitude_sidereal_deg=sun.longitude_sidereal_deg,
            )
            varga_map = compute_vargas(
                pos.longitude_sidereal_deg,
                vargas=vargas or DEFAULT_VARGAS,
                birth_time_uncertainty_minutes=subject.birth_time_uncertainty_minutes,
                include_d150=include_d150,
                force_d150=force_d150,
            )
            mapping = map_rasi_vs_bhava(pos, whole, bhava_houses)
            mappings.append(mapping)
            lord = sign_lord(pos.sign)
            planet_rows.append(
                {
                    **pos.to_dict(),
                    "dignity": dignity.to_dict(),
                    "sign_lord": lord.value if lord else None,
                    "vargas": varga_map,
                    "houses": mapping.to_dict(),
                }
            )

        day_window = None
        if subject.latitude is not None and subject.longitude is not None:
            day_window = self.provider.day_window(subject).to_dict()

        moon = next(p for p in positions if p.planet == PlanetName.MOON)
        dashas = None
        if include_vimshottari:
            dashas = build_vimshottari_tree(
                resolved.utc_datetime,
                moon.longitude_sidereal_deg,
                depth=dasha_depth,
                years_ahead=dasha_years_ahead,
            )

        relationships = None
        if include_relationships:
            planet_signs = {p.planet.value: p.sign for p in positions}
            relationships = build_relationship_graph(planet_signs)

        return ConstructedChart(
            chart_id=str(uuid4()),
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            input={
                "input_kind": subject.input_kind,
                "local_datetime": subject.local_datetime.isoformat(sep=" "),
                "timezone_offset_minutes": subject.timezone_offset_minutes,
                "latitude": subject.latitude,
                "longitude": subject.longitude,
                "location_label": subject.location_label,
                "birth_time_uncertainty_minutes": subject.birth_time_uncertainty_minutes,
            },
            config={
                **self.config.stamp(),
                "bhava_chalit_system": bhava_system.value,
                "vargas": [v.value for v in (vargas or DEFAULT_VARGAS)],
                "include_d150": include_d150,
                "include_vimshottari": include_vimshottari,
                "dasha_depth": dasha_depth.value,
                "dasha_years_ahead": dasha_years_ahead,
                "include_relationships": include_relationships,
            },
            resolved_time=resolved.to_dict(),
            library=self.provider.library_stamp(),
            ayanamsa_degrees=self.provider.ayanamsa_degrees(resolved.julian_day_ut),
            angles={
                "whole_sign": whole.to_dict(),
                "bhava_chalit": bhava_houses.to_dict(),
            },
            planets=planet_rows,
            house_mappings=[m.to_dict() for m in mappings],
            day_window=day_window,
            dashas=dashas,
            relationships=relationships,
        )
