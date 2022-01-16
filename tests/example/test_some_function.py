# -*- coding: utf-8 -*-

import pytest

from trainmaster.main import *


@pytest.mark.parametrize(
    ("first", "second", "expected"),
    [
        (1, 2, 3),
        (2, 4, 6),
        (-2, -3, -5),
        (-5, 5, 0),
    ],
)
def test_some_function(first, second, expected):
    """Example test with parametrization."""
    assert first + second == expected


def test_permit_entry_and_reserve_and_enter():
    too_small = Station(1, 1, id="Breda")
    train = Train(x=10, y=5, id="SprinterTest")
    train2 = Train(x=10, y=5, id="SprinterTest2")
    assert too_small.permit_entry() == True
    if too_small.permit_entry():
        train.reserve(too_small)

    assert train in too_small.reserved
    assert too_small.permit_entry() == False
    train.enter(too_small)
    assert train in too_small.hold
    assert train not in too_small.reserved
    assert too_small.permit_entry() == False
    if too_small.permit_entry():
        train2.reserve(too_small)
    assert train2 not in too_small.hold
    assert too_small.permit_entry() == False
