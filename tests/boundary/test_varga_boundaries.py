from bhava360.chart.vargas import VargaId, varga_sign


def test_navamsa_sign_transition_at_exactly_320():
    part = 30.0 / 9.0
    before = varga_sign(part - 1e-9, VargaId.D9)
    after = varga_sign(part, VargaId.D9)
    assert before.sign == "Aries"
    assert after.sign == "Taurus"


def test_drekkana_transitions_at_10_and_20():
    assert varga_sign(9.999, VargaId.D3).sign == "Aries"
    assert varga_sign(10.0, VargaId.D3).sign == "Leo"  # 5th from Aries
    assert varga_sign(20.0, VargaId.D3).sign == "Sagittarius"  # 9th from Aries
