# -*- coding: utf-8 -*-

import pytest

from trainmaster.main import *


@pytest.mark.parametrize(
    ("depth", "trains"),
    [(1, 3), (3, 1), (1, 1), (2, 2), (2, 0), (0, 2), (0, 0)],
)
def test_station_permit_reserve_enter(depth, trains):
    station = Station(1, 1, id="Breda", depth=depth)
    trains = [Train(x=10, y=5, id=f"Test{_}") for _ in range(trains)]

    if depth > 0:
        assert station.permit_entry() == True
    else:
        assert station.permit_entry() == False

    for i, train in enumerate(trains, start=1):
        if station.permit_entry():
            assert train not in station.reserved
            assert train not in station.hold
            train.reserve(station)
            assert train in station.reserved
            train.enter(station)
            assert train in station.hold
            assert train not in station.reserved

        if depth > i:
            assert station.permit_entry() == True

        else:
            assert station.permit_entry() == False
