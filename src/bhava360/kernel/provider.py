from __future__ import annotations

from typing import Iterable

import swisseph as swe

from bhava360.kernel.derived import nakshatra_from_longitude, sign_from_longitude
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import (
    AyanamsaMode,
    ChartConfig,
    EphemerisMode,
    NodeType,
    PlanetName,
    PlanetPosition,
    SubjectInput,
)
from bhava360.kernel.timeutil import resolve_subject_time

PLANET_TO_SWE = {
    PlanetName.SUN: swe.SUN,
    PlanetName.MOON: swe.MOON,
    PlanetName.MARS: swe.MARS,
    PlanetName.MERCURY: swe.MERCURY,
    PlanetName.JUPITER: swe.JUPITER,
    PlanetName.VENUS: swe.VENUS,
    PlanetName.SATURN: swe.SATURN,
}


class SwissEphemerisProvider:
    """IAstronomyProvider implementation backed by pyswisseph."""

    def __init__(self, config: ChartConfig | None = None) -> None:
        self.config = config or ChartConfig()
        self._configure_backend()

    def _configure_backend(self) -> None:
        if self.config.ephemeris_mode == EphemerisMode.SWISSEPH_FILES:
            if not self.config.ephemeris_path:
                raise KernelError(
                    KernelErrorCode.UNSUPPORTED_CONFIG,
                    "ephemeris_path required for swisseph_files mode",
                )
            swe.set_ephe_path(self.config.ephemeris_path)
        # Moshier needs no path.

        if self.config.ayanamsa == AyanamsaMode.LAHIRI:
            swe.set_sid_mode(swe.SIDM_LAHIRI)
        elif self.config.ayanamsa == AyanamsaMode.KP:
            # KP New ayanamsa constant in SE; keep explicit for school isolation later.
            swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
        else:  # pragma: no cover
            raise KernelError(
                KernelErrorCode.UNSUPPORTED_CONFIG,
                f"unsupported ayanamsa {self.config.ayanamsa}",
            )

    def _flags(self, *, sidereal: bool) -> int:
        if self.config.ephemeris_mode == EphemerisMode.MOSHIER:
            base = swe.FLG_MOSEPH
        elif self.config.ephemeris_mode == EphemerisMode.SWISSEPH_FILES:
            base = swe.FLG_SWIEPH
        else:  # pragma: no cover
            raise KernelError(
                KernelErrorCode.UNSUPPORTED_CONFIG,
                f"unsupported ephemeris mode {self.config.ephemeris_mode}",
            )
        flags = base | swe.FLG_SPEED
        if sidereal:
            flags |= swe.FLG_SIDEREAL
        return flags

    def library_stamp(self) -> dict[str, str]:
        return {
            "pyswisseph_version": getattr(swe, "version", "unknown"),
            "ephemeris_mode": self.config.ephemeris_mode.value,
            "ayanamsa": self.config.ayanamsa.value,
            "node_type": self.config.node_type.value,
            "calc_library_version": self.config.calc_library_version,
        }

    def ayanamsa_degrees(self, julian_day_ut: float) -> float:
        return float(swe.get_ayanamsa_ut(julian_day_ut))

    def planet_position(self, subject: SubjectInput, planet: PlanetName) -> PlanetPosition:
        resolved = resolve_subject_time(subject)
        jd = resolved.julian_day_ut
        flags_sid = self._flags(sidereal=True)
        flags_trop = self._flags(sidereal=False)

        try:
            if planet == PlanetName.KETU:
                node = self._node_body()
                xx, _ret = swe.calc_ut(jd, node, flags_sid)
                lon_sid = (xx[0] + 180.0) % 360.0
                lat = -float(xx[1])
                speed = float(xx[3])
                xx_t, _ = swe.calc_ut(jd, node, flags_trop)
                lon_trop = (xx_t[0] + 180.0) % 360.0
            elif planet == PlanetName.RAHU:
                node = self._node_body()
                xx, _ret = swe.calc_ut(jd, node, flags_sid)
                lon_sid = xx[0] % 360.0
                lat = float(xx[1])
                speed = float(xx[3])
                xx_t, _ = swe.calc_ut(jd, node, flags_trop)
                lon_trop = xx_t[0] % 360.0
            else:
                ipl = PLANET_TO_SWE.get(planet)
                if ipl is None:
                    raise KernelError(
                        KernelErrorCode.UNSUPPORTED_PLANET,
                        f"unsupported planet {planet}",
                    )
                xx, _ret = swe.calc_ut(jd, ipl, flags_sid)
                lon_sid = xx[0] % 360.0
                lat = float(xx[1])
                speed = float(xx[3])
                xx_t, _ = swe.calc_ut(jd, ipl, flags_trop)
                lon_trop = xx_t[0] % 360.0
        except KernelError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise KernelError(
                KernelErrorCode.CALCULATION_FAILED,
                "Swiss Ephemeris calculation failed",
                {"planet": planet.value, "error": str(exc)},
            ) from exc

        sign, sign_deg = sign_from_longitude(lon_sid)
        nak, pada, label = nakshatra_from_longitude(lon_sid)
        return PlanetPosition(
            planet=planet,
            longitude_sidereal_deg=lon_sid,
            longitude_tropical_deg=lon_trop,
            latitude_deg=lat,
            speed_longitude=speed,
            is_retrograde=speed < 0,
            sign=sign,
            sign_degree=sign_deg,
            nakshatra=nak,
            pada=pada,
            nakshatra_label=label,
        )

    def all_planet_positions(
        self,
        subject: SubjectInput,
        planets: Iterable[PlanetName] | None = None,
    ) -> list[PlanetPosition]:
        selected = list(planets) if planets is not None else list(PlanetName)
        return [self.planet_position(subject, p) for p in selected]

    def _node_body(self) -> int:
        if self.config.node_type == NodeType.MEAN:
            return swe.MEAN_NODE
        if self.config.node_type == NodeType.TRUE:
            return swe.TRUE_NODE
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            f"unsupported node type {self.config.node_type}",
        )
