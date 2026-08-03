from bhava360.kernel.derived import house_index_for_longitude, whole_sign_cusp_longitudes


def test_house_index_wrap_across_zero():
    # Capricorn whole-sign chart: house1=270 ... house4=0, house5=30
    cusps = whole_sign_cusp_longitudes(280.0)
    assert cusps[0] == 270.0
    assert house_index_for_longitude(275.0, cusps) == 1
    assert house_index_for_longitude(5.0, cusps) == 4
    assert house_index_for_longitude(359.0, cusps) == 3
