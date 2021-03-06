from dataclasses import dataclass, field
from typing import List, Union
import simpy
import simpy.rt
import random
import logging
from rich.logging import RichHandler
from random import randint

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

log = logging.getLogger("rich")

TRAINS: List["Train"] = []
STATIONS: List["Station"] = []


def match():
    for station in STATIONS:
        for train in TRAINS:
            if station.x == train.x and station.y == train.y:
                station.hold.append(train)


def find_station(x: int, y: int) -> Union["Station", None]:
    return next(
        (station for station in STATIONS if station.x == x and station.y == y), None
    )


def logt(now, object: str, message: str, type: str = "info"):
    if type == "debug":
        log.debug(f"{now:03d} {object[0:4]} | {message}")
    else:
        log.info(f"{now:03d} {object[0:4]} | {message}")


def msg(now, train: "Train", type: str, message: str):
    if train.log and type == "info":
        log.info(f"{now:03d} {train.id[0:4]} | {message}")
    elif train.log and type == "debug":
        log.debug(f"{now:03d} {train.id[0:4]} | {message}")


@dataclass
class Train:
    x: int
    y: int
    id: str
    log: bool = False

    def __post_init__(self):
        TRAINS.append(self)

    def __repr__(self):
        return f"{self.id}({self.x},{self.y})"

    def reserve(self, station: "Station") -> None:
        station.reserved.append(self)
        # print(f'{env.now:03d} {self.id} | +Hold {station.id}')

    def enter(self, station: "Station") -> None:
        station.reserved.remove(self)
        station.hold.append(self)

    def exit(self, station: "Station") -> None:
        station.hold.remove(self)
        # print(f'{env.now:03d} {self.id} | -Hold {station.id}')

    def move(self, env, i, j):
        msg(env.now, self, "debug", f"Command: move {self.x},{self.y} to {i},{j}")
        if self.x == 0 and self.y == 0:
            return "Hello"
        self._x = self.x
        self._y = self.y
        # print(self._x, self._y)
        station_from = find_station(x=self._x, y=self._y)
        station_to = find_station(x=i, y=j)
        if isinstance(station_to, Station) and station_to.permit_entry():
            # print('b,permit')
            if station_from:
                self.exit(station_from)
            self.reserve(station_to)
            logt(env.now, self.id, f"D ({self._x},{self._y})->({i},{j})")
            self.x, self.y = 0, 0
            yield env.timeout(abs(i - self._x))
            yield env.timeout(abs(j - self._y))
            logt(env.now, self.id, f"A ({i},{j})<-({self._x},{self._y})")
            self.x, self.y = i, j
            self.enter(station_to)
            # print('debug',self.x,self._x,self.y,self._y)
        elif (
            isinstance(station_to, Station)
            and not station_to.permit_entry()
            and self not in station_to.no_go
        ):
            msg(env.now, self, "info", f"No-go to {station_to}")
            station_to.no_go.append(self)
        else:
            if station_from:
                self.exit(station_from)
            logt(env.now, self.id, f"D ({self._x},{self._y})->({i},{j})")
            self.x, self.y = 0, 0
            yield env.timeout(abs(i - self.x))
            yield env.timeout(abs(j - self.y))
            logt(env.now, self.id, f"A ({i},{j})<-({self._x},{self._y})")
            self.x, self.y = i, j


@dataclass
class Station:
    x: int
    y: int
    id: str
    depth: int = 1
    # occupied: bool = False
    reserved: List["Train"] = field(default_factory=list)
    hold: List[Train] = field(default_factory=list)
    no_go: List[Train] = field(default_factory=list)

    def __post_init__(self):
        STATIONS.append(self)

    def __repr__(self):
        return f"{self.id}({self.x},{self.y})"

    def permit_entry(self) -> bool:
        if len(self.hold) + len(self.reserved) < self.depth:
            return True
        else:
            return False


def trains_at_location(x: int, y: int):
    for t in TRAINS:
        if t.x == x and t.y == y:
            yield t


def stationmaster(env, station: Station):
    """
    Stationmaster that dispatches trains to random locations when the station is full.
    """
    while True:
        yield env.timeout(1)
        _trains = list(trains_at_location(station.x, station.y))
        if station.depth == len(_trains):  # station is full
            logt(
                env.now,
                station.id,
                f"Stationmaster's whistle ({len(_trains)}/{station.depth})",
            )
            for train in _trains:
                # if random.choice([True, False]):
                # msg(env.now, train,"info",  "Opt 1")
                # env.process(train.move(env, 20, 20))
                # else:
                # msg(env.now, train,"info",  "Opt 2")
                env.process(train.move(env, randint(1, 50), randint(1, 50)))

            yield env.timeout(1)
            _trains = list(trains_at_location(station.x, station.y))
            logt(env.now, station.id, f"Capacity ({len(_trains)})", "debug")
            empty_slots = station.depth - len(_trains)
            if empty_slots > 0:
                for _ in range(empty_slots):
                    if len(station.no_go) > 0:
                        popped_train = station.no_go.pop(0)
                        msg(
                            env.now,
                            popped_train,
                            "debug",
                            "popped "
                            + str(popped_train)
                            + " from no-go "
                            + str(station),
                        )
                        env.process(popped_train.move(env, station.x, station.y))


def schedulemaster(env):
    """
    Schedulemaster that schedules trains.
    """
    while True:
        yield env.timeout(1)


def grid() -> str:
    conclusion = ""
    for _ in range(50):
        for __ in range(50):
            coo = "__"
            for train in TRAINS:
                if train.x == __ and train.y == _:
                    coo = "Tr"
            for station in STATIONS:
                if station.x == __ and station.y == _:
                    if coo == "Tr":
                        coo = "Xx"
                    else:
                        coo = "S"
            conclusion += coo
        conclusion += "\n"
    return conclusion


if __name__ == "__main__":
    print("=== ==== | =========================")
    env = simpy.Environment()
    random.seed(421)
    t = [Train(x=33, y=33, id="Ic01")] + [
        Train(x=randint(1, 20), y=randint(1, 20), id=f"Spr{_}", log=True)
        for _ in range(9)
    ]
    den_helder = Station(1, 33, id="Den Helder", depth=1)
    breda = Station(7, 5, id="Breda", depth=randint(2, 4))
    arnhem = Station(20, 20, id="Arnhem", depth=2)
    match()
    for train in t:
        env.process(train.move(env, 7, 5))
    for train in t:
        env.process(train.move(env, 20, 20))
    for station in STATIONS:
        env.process(stationmaster(env, station))
    env.process(schedulemaster(env))
    env.run(until=180)
    logt(env.now, "====", f"Trains: {TRAINS}")
    logt(env.now, "====", f"Stations: {STATIONS}")


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
