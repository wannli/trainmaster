from dataclasses import dataclass, field
from typing import List, Union
import simpy
import simpy.rt
import random
from random import randint


@dataclass
class Universe:
    Stations: List["Station"] = field(default_factory=list)
    Trains: List["Train"] = field(default_factory=list)


def match():
    for station in Stations:
        for train in Trains:
            if station.x == train.x and station.y == train.y:
                station.hold.append(train)


def find_station(x: int, y: int) -> Union["Station", None]:
    return next(
        (station for station in Stations if station.x == x and station.y == y), None
    )

    # def register(self, registered):
    # if isinstance(registered, Station):
    # self.Stations.append(registered)
    # elif isinstance(registered, Train):
    # self.Trains.append(registered)


Trains = []
Stations = []


@dataclass
class Train:
    x: int
    y: int
    id: str

    def __post_init__(self):
        Trains.append(self)

    def reserve(self, station: "Station"):
        station.hold.append(self)
        # print(f'{env.now:03d} {self.id} | +Hold {station.id}')

    def exit(self, station: "Station"):
        station.hold.remove(self)
        # print(f'{env.now:03d} {self.id} | -Hold {station.id}')

    def move(self, env, i, j):
        self._x = self.x
        self._y = self.y
        # print(self._x, self._y)
        a = find_station(x=self._x, y=self._y)
        b = find_station(x=i, y=j)
        if isinstance(b, Station) and b.permit_entry():
            # print('b,permit')
            if a:
                self.exit(a)
            self.reserve(b)
            print(f"{env.now:03d} {self.id} | D ({self._x},{self._y})->({i},{j})")
            self.x, self.y = 0, 0
            yield env.timeout(abs(i - self._x))
            yield env.timeout(abs(j - self._y))
            print(f"{env.now:03d} {self.id} | A ({i},{j})<-({self._x},{self._y})")
            self.x, self.y = i, j
            # print('debug',self.x,self._x,self.y,self._y)
        elif isinstance(b, Station) and not b.permit_entry() and self not in b.no_go:
            print(f"{env.now:03d} {self.id} | No-go to {b.id}")
            b.no_go.append(self)
        else:
            if a:
                self.exit(a)
            print(f"{env.now:03d} {self.id} | D ({self._x},{self._y})->({i},{j})")
            self.x, self.y = 0, 0
            yield env.timeout(abs(i - self.x))
            yield env.timeout(abs(j - self.y))
            print(f"{env.now:03d} {self.id} | A ({i},{j})<-({self._x},{self._y})")
            self.x, self.y = i, j


@dataclass
class Station:
    x: int
    y: int
    id: str
    depth: int = 1
    # occupied: bool = False
    hold: List[Train] = field(default_factory=list)
    no_go: List[Train] = field(default_factory=list)

    def __post_init__(self):
        Stations.append(self)

    def permit_entry(self) -> bool:
        if len(self.hold) < self.depth:
            return True
        else:
            return False


def trains_at_location(x: int, y: int):
    for t in Trains:
        if t.x == x and t.y == y:
            yield t


def stationmaster(env, station: Station):
    while True:
        yield env.timeout(5)
        _trains = list(trains_at_location(station.x, station.y))
        if station.depth == len(_trains):
            print(f"{env.now:03d} ==== | {station.id} at capacity")
            # print(station.hold)
            # print(Trains)
            for train in _trains:
                if random.choice([True, False]):
                    env.process(train.move(env, randint(1, 50), randint(1, 50)))
                else:
                    env.process(train.move(env, 20, 20))
                if (
                    len(station.no_go) > 0
                ):  # TODO: now picks up trains that are underway
                    # print(env.now,'pop',station.id,station.no_go)
                    popped_train = station.no_go.pop(0)
                    env.process(popped_train.move(env, station.x, station.y))

            # for train in station.no_go[:station.depth]:
            # station.no_go.remove(train)
            # env.process(train.move(env,station.x,station.y))


if __name__ == "__main__":
    print("=== ==== | =========================")
    env = simpy.Environment()
    random.seed(421)
    t = [Train(x=33, y=33, id="Ic01")] + [
        Train(x=randint(1, 20), y=randint(1, 20), id=f"Spr{_}") for _ in range(9)
    ]
    den_helder = Station(1, 33, id="Den Helder", depth=1)
    too_small = Station(7, 5, id="Breda", depth=randint(2, 4))
    arnhem = Station(20, 20, id="Arnhem", depth=2)
    for train in t:
        env.process(train.move(env, 7, 5))
    match()
    env.process(stationmaster(env, too_small))
    env.process(stationmaster(env, arnhem))
    env.run(until=300)


# def test_permit_entry_no():
#     too_small = Station(1, 1, id="Breda")
#     train = Train(x=10, y=5, id="SprinterTest")
#     assert too_small.permit_entry() == True
#     train.reserve(too_small)
#     assert too_small.permit_entry() == False


# def test_permit_entry_yes():
#     right_size = Station(2, 2, depth=2, id="Breda")
#     train = Train(x=10, y=5, id="SprinterTest")
#     assert right_size.permit_entry() == True
#     train.reserve(right_size)
#     assert right_size.permit_entry() == True
