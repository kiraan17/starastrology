from __future__ import annotations

from dataclasses import dataclass

from bhava360.kernel.derived import house_index_for_longitude, whole_sign_cusp_longitudes
from bhava360.kernel.models import HouseSystem, HouseSystemResult, PlanetName, PlanetPosition


@dataclass(slots=True)
class HouseMapping:
    planet: PlanetName
    rasi_house: int
    bhava_chalit_house: int
    rasi_sign: str
    longitude_sidereal_deg: float
    differs: bool

    def to_dict(self) -> dict:
        return {
            "planet": self.planet.value,
            "rasi_house": self.rasi_house,
            "bhava_chalit_house": self.bhava_chalit_house,
            "rasi_sign": self.rasi_sign,
            "longitude_sidereal_deg": self.longitude_sidereal_deg,
            "differs": self.differs,
        }


def rasi_house_from_asc(ascendant_sidereal_deg: float, planet_longitude: float) -> int:
    cusps = whole_sign_cusp_longitudes(ascendant_sidereal_deg)
    return house_index_for_longitude(planet_longitude, cusps)


def map_rasi_vs_bhava(
    planet: PlanetPosition,
    houses_whole_sign: HouseSystemResult,
    houses_cuspal: HouseSystemResult,
) -> HouseMapping:
    """Compare whole-sign (Rasi) house vs cusp-based Bhava Chalit house."""
    if houses_whole_sign.system != HouseSystem.WHOLE_SIGN:
        # Still allow using provided cusps as whole-sign equivalent if caller constructed them.
        pass
    rasi = house_index_for_longitude(
        planet.longitude_sidereal_deg,
        [c.longitude_sidereal_deg for c in houses_whole_sign.cusps],
    )
    bhava = house_index_for_longitude(
        planet.longitude_sidereal_deg,
        [c.longitude_sidereal_deg for c in houses_cuspal.cusps],
    )
    return HouseMapping(
        planet=planet.planet,
        rasi_house=rasi,
        bhava_chalit_house=bhava,
        rasi_sign=planet.sign,
        longitude_sidereal_deg=planet.longitude_sidereal_deg,
        differs=rasi != bhava,
    )
