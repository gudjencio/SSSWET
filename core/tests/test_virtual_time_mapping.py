from ssswet_core.virtual_time_mapping import TemporalObservation, VirtualTimeMap


def test_virtual_time_map_filters_uncertain_observations():
    m = VirtualTimeMap()
    m.add(TemporalObservation("2020-01-01", "A", "s1", 2))
    m.add(TemporalObservation("2021-01-01", "B", "s2", 20))
    assert [x.source_id for x in m.window(max_uncertainty_seconds=5)] == ["s1"]


def test_virtual_time_map_requires_provenance():
    m = VirtualTimeMap()
    try:
        m.add(TemporalObservation("2020", "A", "", 0))
    except ValueError:
        pass
    else:
        raise AssertionError("expected source validation")
