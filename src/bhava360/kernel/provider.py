from __future__ import annotations

from datetime import timedelta, timezone
from typing import Iterable

import swisseph as swe

from bhava360.kernel.derived import (
    house_index_for_longitude,
    nakshatra_from_longitude,
    normalize_longitude,
    sign_from_longitude,
    whole_sign_cusp_longitudes,
)
from bhava360.kernel.errors import KernelError, KernelErrorCode
from bhava360.kernel.models import (
    AnglePoint,
    AyanamsaMode,
    ChartConfig,
    DayWindow,
    EphemerisMode,
    HouseCusp,
    HouseSystem,
    HouseSystemResult,
    NodeType,
    PlanetName,
    PlanetPosition,
    SubjectInput,
)
from bhava360.kernel.timeutil import (
    julian_day_to_utc,
    require_coordinates,
    resolve_subject_time,
)

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

        if self.config.ayanamsa == AyanamsaMode.LAHIRI:
            swe.set_sid_mode(swe.SIDM_LAHIRI)
        elif self.config.ayanamsa == AyanamsaMode.KP:
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

    def houses(self, subject: SubjectInput, system: HouseSystem | None = None) -> HouseSystemResult:
        """Compute Asc/MC and house cusps. Vedic whole-sign is computed locally; Placidus via SE."""
        chosen = system or self.config.house_system
        lat, lon = require_coordinates(subject)
        resolved = resolve_subject_time(subject)
        jd = resolved.julian_day_ut

        try:
            # Asc/MC from SE sidereal houses_ex using Placidus geometry for angles.
            cusps_raw, ascmc = swe.houses_ex(jd, lat, lon, b"P", swe.FLG_SIDEREAL)
            # pyswisseph returns 12 cusps at indices 0..11 (cusp1 == Asc).
            asc_lon = normalize_longitude(float(ascmc[0]))
            mc_lon = normalize_longitude(float(ascmc[1]))
        except Exception as exc:  # noqa: BLE001
            raise KernelError(
                KernelErrorCode.CALCULATION_FAILED,
                "failed to compute Asc/MC",
                {"error": str(exc)},
            ) from exc

        if chosen == HouseSystem.WHOLE_SIGN:
            cusp_lons = whole_sign_cusp_longitudes(asc_lon)
        elif chosen == HouseSystem.PLACIDUS:
            try:
                if len(cusps_raw) < 12:
                    raise KernelError(
                        KernelErrorCode.CALCULATION_FAILED,
                        "unexpected Placidus cusp array length",
                        {"length": len(cusps_raw)},
                    )
                cusp_lons = [normalize_longitude(float(cusps_raw[i])) for i in range(12)]
            except KernelError:
                raise
            except Exception as exc:  # noqa: BLE001
                raise KernelError(
                    KernelErrorCode.CALCULATION_FAILED,
                    "failed to compute Placidus cusps",
                    {"error": str(exc)},
                ) from exc
        else:  # pragma: no cover
            raise KernelError(
                KernelErrorCode.UNSUPPORTED_CONFIG,
                f"unsupported house system {chosen}",
            )

        return HouseSystemResult(
            system=chosen,
            ascendant=self._angle_point("Ascendant", asc_lon),
            midheaven=self._angle_point("Midheaven", mc_lon),
            cusps=[
                HouseCusp(
                    house=i + 1,
                    longitude_sidereal_deg=cusp_lons[i],
                    sign=sign_from_longitude(cusp_lons[i])[0],
                    sign_degree=sign_from_longitude(cusp_lons[i])[1],
                )
                for i in range(12)
            ],
        )

    def planet_house(
        self,
        subject: SubjectInput,
        planet: PlanetName,
        system: HouseSystem | None = None,
    ) -> int:
        houses = self.houses(subject, system)
        position = self.planet_position(subject, planet)
        cusp_lons = [c.longitude_sidereal_deg for c in houses.cusps]
        return house_index_for_longitude(position.longitude_sidereal_deg, cusp_lons)

    def day_window(self, subject: SubjectInput) -> DayWindow:
        """Sunrise/sunset for the local civil date of the subject (disc center)."""
        lat, lon = require_coordinates(subject)
        resolved = resolve_subject_time(subject)
        # Search from previous UTC noon-ish relative to local date start.
        local_date = subject.local_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
        offset = timezone(timedelta(minutes=subject.timezone_offset_minutes))
        local_midnight = local_date.replace(tzinfo=offset)
        utc_midnight = local_midnight.astimezone(timezone.utc)
        hour = utc_midnight.hour + utc_midnight.minute / 60.0
        jd0 = swe.julday(utc_midnight.year, utc_midnight.month, utc_midnight.day, hour)

        geopos = (lon, lat, 0.0)
        try:
            # Start at local midnight; then find sunset after that sunrise.
            rise_rc, rise_vals = swe.rise_trans(
                jd0,
                swe.SUN,
                swe.CALC_RISE | swe.BIT_DISC_CENTER,
                geopos,
            )
            if rise_rc < 0:
                raise KernelError(
                    KernelErrorCode.CALCULATION_FAILED,
                    "sunrise not available for location/date",
                    {"rise_rc": rise_rc},
                )
            rise_jd = float(rise_vals[0])
            set_rc, set_vals = swe.rise_trans(
                rise_jd,
                swe.SUN,
                swe.CALC_SET | swe.BIT_DISC_CENTER,
                geopos,
            )
        except KernelError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise KernelError(
                KernelErrorCode.CALCULATION_FAILED,
                "failed to compute sunrise/sunset",
                {"error": str(exc)},
            ) from exc

        if set_rc < 0:
            raise KernelError(
                KernelErrorCode.CALCULATION_FAILED,
                "sunset not available for location/date",
                {"set_rc": set_rc},
            )

        set_jd = float(set_vals[0])
        if set_jd <= rise_jd:
            raise KernelError(
                KernelErrorCode.CALCULATION_FAILED,
                "sunset is not after sunrise",
                {"rise_jd": rise_jd, "set_jd": set_jd},
            )
        rise_utc = julian_day_to_utc(rise_jd)
        set_utc = julian_day_to_utc(set_jd)
        rise_local = rise_utc.astimezone(offset)
        set_local = set_utc.astimezone(offset)
        return DayWindow(
            sunrise_jd_ut=rise_jd,
            sunset_jd_ut=set_jd,
            sunrise_utc=rise_utc.isoformat(),
            sunset_utc=set_utc.isoformat(),
            sunrise_local=rise_local.isoformat(sep=" "),
            sunset_local=set_local.isoformat(sep=" "),
        )

    def _angle_point(self, name: str, lon: float) -> AnglePoint:
        sign, sign_deg = sign_from_longitude(lon)
        nak, pada, label = nakshatra_from_longitude(lon)
        return AnglePoint(
            name=name,
            longitude_sidereal_deg=lon,
            sign=sign,
            sign_degree=sign_deg,
            nakshatra=nak,
            pada=pada,
            nakshatra_label=label,
        )

    def _node_body(self) -> int:
        if self.config.node_type == NodeType.MEAN:
            return swe.MEAN_NODE
        if self.config.node_type == NodeType.TRUE:
            return swe.TRUE_NODE
        raise KernelError(
            KernelErrorCode.UNSUPPORTED_CONFIG,
            f"unsupported node type {self.config.node_type}",
        )
