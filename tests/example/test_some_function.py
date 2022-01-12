# -*- coding: utf-8 -*-

import pytest
from trainmaster.main import *

# from trainmaster import Station, Train


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


# @pytest.mark.parametrize(
#     ("first", "second", "expected"),
#     [
#         (1, 2, 3),
#         (2, 4, 6),
#         (-2, -3, -5),
#         (-5, 5, 0),
#     ],
# )
def test_another_function():
    too_small = Station(1, 1, id="Breda")
    train = Train(x=10, y=5, id="SprinterTest")
    assert too_small.permit_entry() == True
    train.reserve(too_small)
    assert too_small.permit_entry() == False
