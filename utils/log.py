import sqlite3
from dataclasses import asdict, dataclass
from collections import defaultdict
from utils.sim_types import ResourceType
from resources import RAW_RESOURCES

MAX_CACHE = 32


@dataclass(slots=True)
class LogGeneric:
    turn: int
    location: str
    TYPE = "generic"


@dataclass(slots=True)
class LogGenericResource(LogGeneric):
    resource: str
    amount: float
    TYPE = "resource"


@dataclass(slots=True)
class LogResource(LogGenericResource):
    price: float
    TYPE = "resource"


@dataclass(slots=True)
class LogTrade(LogGenericResource):
    price: float
    destination: str
    travel_time: int
    walking: int
    TYPE = "trade"


@dataclass(slots=True)
class LogProduction(LogGenericResource):
    TYPE = "production"


@dataclass(slots=True)
class LogPopulation(LogGeneric):
    population: int
    TYPE = "population"


@dataclass(slots=True)
class LogConsumption(LogGenericResource):
    TYPE = "consumption"


@dataclass(slots=True)
class LogEvent(LogGeneric):
    description: str
    TYPE = "event"


@dataclass(slots=True)
class LogCityEstablishment(LogGeneric):
    land_id: float
    ocean_id: float
    X: int
    Y: int
    TYPE = "city"


@dataclass(slots=True)
class LogCulture(LogGeneric):
    traits: list[float]
    TYPE = "culture"

@dataclass(slots=True)
class LogBankruptcy(LogGeneric):
    TYPE = "bankruptcy"

@dataclass(slots=True)
class LogCityCollapse(LogGeneric):
    TYPE = "city_collapse"

@dataclass(slots=True)
class LogFamine(LogGeneric):
    amount: int
    TYPE = "famine"


class Logger:
    locations_cache = {}
    resources_cache = {}
    type_cache = {}
    log_cache = defaultdict(list)

    def __init__(self, name):
        self.filename = name + ".sqlite"
        self.conn = sqlite3.connect(self.filename)
        self.conn.execute("""DROP TABLE IF EXISTS types""")
        self.conn.execute("""DROP TABLE IF EXISTS locations""")
        self.conn.execute("""DROP TABLE IF EXISTS resources""")
        self.conn.execute("""DROP TABLE IF EXISTS city_locations""")
        self.conn.execute("""DROP TABLE IF EXISTS logs""")
        self.conn.execute("""CREATE TABLE IF NOT EXISTS types
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT UNIQUE)""")
        self.conn.execute("""CREATE TABLE IF NOT EXISTS locations
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, location TEXT UNIQUE)""")
        self.conn.execute("""CREATE TABLE IF NOT EXISTS resources
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, resource TEXT UNIQUE, tier INTEGER)""")
        self.conn.execute("""CREATE TABLE city_locations
                        (location INTEGER, land_id FLOAT, ocean_id FLOAT, X INTEGER, Y INTEGER,
                        FOREIGN KEY(location) REFERENCES locations(id))""")
        self.conn.execute("""CREATE TABLE IF NOT EXISTS logs
                        (type INTEGER, turn INTEGER, location INTEGER, resource INTEGER, price FLOAT, amount FLOAT, destination TEXT, travel_time INTEGER, walking INTEGER, population INTEGER, description TEXT, traits TEXT,
                        FOREIGN KEY(type) REFERENCES types(id),
                        FOREIGN KEY(resource) REFERENCES resources(id),
                        FOREIGN KEY(location) REFERENCES locations(id))""")

    def _get_type_id(self, log_obj: LogGeneric):
        if log_obj.TYPE in self.type_cache:
            return self.type_cache[log_obj.TYPE]
        type_id = self.conn.execute(
            """SELECT id from types where type=?""", (log_obj.TYPE,)
        ).fetchone()
        if type_id is None:
            self.conn.execute(
                """INSERT INTO types (type) VALUES (?)""", (log_obj.TYPE,)
            )
            type_id = self.conn.execute(
                """SELECT id from types where type=?""", (log_obj.TYPE,)
            ).fetchone()
        self.type_cache[log_obj.TYPE] = type_id[0]
        return type_id[0]

    def _get_location_id(self, location: str):
        if location in self.locations_cache:
            return self.locations_cache[location]
        location_id = self.conn.execute(
            """SELECT id from locations where location=?""", (location,)
        ).fetchone()
        if location_id is None:
            self.conn.execute(
                """INSERT INTO locations (location) VALUES (?)""", (location,)
            )
            location_id = self.conn.execute(
                """SELECT id from locations where location=?""", (location,)
            ).fetchone()
        self.locations_cache[location] = location_id[0]
        return location_id[0]

    def _get_resource_id(self, resource: str):
        if resource in self.resources_cache:
            return self.resources_cache[resource]
        resource_id = self.conn.execute(
            """SELECT id from resources where resource=?""", (resource,)
        ).fetchone()
        if resource_id is None:
            if resource == "gold" or resource == "score":
                tier = -1
            else:
                tier = 0 if ResourceType(resource) in RAW_RESOURCES else 1
            self.conn.execute('''INSERT INTO resources (resource, tier) VALUES (?, ?)''', (resource, tier))
            resource_id = self.conn.execute('''SELECT id from resources where resource=?''', (resource,)).fetchone()
        self.resources_cache[resource] = resource_id[0]
        return resource_id[0]

    def _normalize_log(self, log_obj: LogGeneric):
        data = asdict(log_obj)
        data["type"] = self._get_type_id(
            log_obj)  # add the log type explicitly
        data["location"] = self._get_location_id(
            log_obj.location
        )  # convert location to ID
        if hasattr(log_obj, "resource"):
            data["resource"] = self._get_resource_id(
                log_obj.resource
            )  # convert resource to ID
        if hasattr(log_obj, "destination"):
            data["destination"] = self._get_location_id(
                log_obj.destination
            )  # convert destination to ID
        if hasattr(log_obj, "traits"):
            import json

            data["traits"] = json.dumps(log_obj.traits)
        return data

    def save_log(self, log_obj: LogGeneric):
        self.log_cache[type(log_obj).__name__].append(log_obj)

    def save_log_est(self, log: LogCityEstablishment):
        location_id = self._get_location_id(log.location)
        self.conn.execute(
            """INSERT INTO city_locations (location, land_id, ocean_id, X, Y) VALUES (?, ?, ?, ?, ?)""",
            (location_id, log.land_id, log.ocean_id, log.X, log.Y),
        )
        self.conn.commit()

    def save_logs(self, log_list: list[LogGeneric]):
        touched_logs = []
        for log_obj in log_list:
            log_type = type(log_obj).__name__
            if log_type not in touched_logs:
                touched_logs.append(log_type)
            self.log_cache[log_type].append(log_obj)
        for log_type in touched_logs:
            if len(self.log_cache[log_type]) > MAX_CACHE:
                values = []
                for log_obj in self.log_cache[log_type]:
                    data = self._normalize_log(log_obj)
                    columns = ", ".join(data.keys())
                    placeholders = ", ".join("?" for _ in data)
                    values.append(tuple(data.values()))
                self.conn.executemany(
                    f"INSERT INTO logs ({columns}) VALUES ({placeholders})", values
                )
                self.conn.commit()
                self.log_cache[log_type] = []

    def __del__(self):
        for log_type, logs in self.log_cache.items():
            if logs:
                values = []
                for log_obj in logs:
                    data = self._normalize_log(log_obj)
                    values.append(tuple(data.values()))

                columns = ", ".join(data.keys())
                placeholders = ", ".join("?" for _ in data)

                self.conn.executemany(
                    f"INSERT INTO logs ({columns}) VALUES ({placeholders})", values
                )
                self.conn.commit()
        self.conn.close()
