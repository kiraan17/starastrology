from datetime import datetime

from bhava360.kernel.models import SubjectInput
from bhava360.kernel.snapshot import build_planet_snapshot


def test_snapshot_contains_version_stamp():
    snap = build_planet_snapshot(
        SubjectInput(
            local_datetime=datetime(1990, 8, 15, 12, 0),
            timezone_offset_minutes=330,
            location_label="Chennai",
        )
    )
    data = snap.to_dict()
    assert data["config"]["ephemeris_mode"] == "moshier"
    assert data["config"]["ayanamsa"] == "lahiri"
    assert "pyswisseph_version" in data["library"]
    assert len(data["planets"]) == 9
