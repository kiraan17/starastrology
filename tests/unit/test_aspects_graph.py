from __future__ import annotations

from datetime import datetime

from bhava360.chart.aspects import (
    build_relationship_graph,
    compute_graha_aspects,
    jaimini_rashi_aspect_targets,
    relative_house,
)
from bhava360.chart.builder import ChartConstructor
from bhava360.kernel.models import PlanetName, SubjectInput


def test_jupiter_aspects_5_7_9():
    # Jupiter in Aries aspects Leo(5), Libra(7), Sagittarius(9)
    aspects = compute_graha_aspects(
        {
            "Jupiter": "Aries",
            "Sun": "Leo",
            "Moon": "Taurus",
            "Mars": "Libra",
            "Saturn": "Sagittarius",
            "Mercury": "Gemini",
            "Venus": "Cancer",
            "Rahu": "Capricorn",
            "Ketu": "Cancer",
        }
    )
    jup = [a for a in aspects if a["from_planet"] == "Jupiter"]
    targets = {a["to_planet"]: a["matched_house"] for a in jup}
    assert targets["Sun"] == 5
    assert targets["Mars"] == 7
    assert targets["Saturn"] == 9
    assert "Moon" not in targets


def test_mars_special_aspects_4_8():
    aspects = compute_graha_aspects({"Mars": "Aries", "Moon": "Cancer", "Sun": "Scorpio", "Mercury": "Libra"})
    mars = {a["to_planet"]: a["matched_house"] for a in aspects if a["from_planet"] == "Mars"}
    assert mars["Moon"] == 4
    assert mars["Mercury"] == 7
    assert mars["Sun"] == 8


def test_jaimini_aries_aspects_fixed_except_taurus():
    targets = jaimini_rashi_aspect_targets("Aries")
    assert set(targets) == {"Leo", "Scorpio", "Aquarius"}
    assert "Taurus" not in targets


def test_jaimini_gemini_aspects_other_duals():
    targets = jaimini_rashi_aspect_targets("Gemini")
    assert set(targets) == {"Virgo", "Sagittarius", "Pisces"}


def test_relationship_graph_has_dispositor_and_edges():
    graph = build_relationship_graph(
        {
            "Sun": "Leo",  # own sign, dispositor Sun (loop)
            "Moon": "Taurus",  # Venus
            "Venus": "Libra",
            "Mars": "Aries",
            "Mercury": "Virgo",
            "Jupiter": "Sagittarius",
            "Saturn": "Capricorn",
            "Rahu": "Aquarius",
            "Ketu": "Leo",
        }
    )
    assert any(e["type"] == "dispositor" and e["from"] == "Moon" and e["to"] == "Venus" for e in graph["edges"])
    assert graph["dispositor_chains"]["Moon"][0] == "Moon"
    assert "Venus" in graph["dispositor_chains"]["Moon"]
    assert graph["conjunctions"]  # Ketu+Sun in Leo
    assert "graha_aspects" in graph
    assert graph["rashi_aspects"]["system"] == "jaimini_rashi"
    assert "Gemini" not in str(graph["notes"]).lower() or "not 'Gemini'" in " ".join(graph["notes"])


def test_relative_house_opposite_is_7():
    assert relative_house("Aries", "Libra") == 7
    assert relative_house("Aries", "Aries") == 1


def test_chart_constructor_includes_relationships():
    subject = SubjectInput(
        local_datetime=datetime(1990, 8, 15, 12, 0),
        timezone_offset_minutes=330,
        latitude=13.0827,
        longitude=80.2707,
    )
    chart = ChartConstructor().build(subject, include_vimshottari=False).to_dict()
    assert chart["config"]["calc_library_version"] == "bhava360-kernel-0.5.0"
    assert chart["relationships"] is not None
    assert "edges" in chart["relationships"]
    assert "graha_aspects" in chart["relationships"]
