from dataclasses import dataclass, asdict
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


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


class Logger:
    def __init__(self, name: str):
        # DataFrames replace SQL tables
        self.types = pd.DataFrame(columns=["id", "type"])
        self.locations = pd.DataFrame(columns=["id", "location"])
        self.resources = pd.DataFrame(columns=["id", "resource"])
        self.city_locations = pd.DataFrame(columns=["location", "land_id", "ocean_id", "X", "Y"])
        self.logs = pd.DataFrame()

        # Caches
        self.locations_cache = {}
        self.resources_cache = {}
        self.type_cache = {}

        # Auto‑increment counters
        self._type_id = 1
        self._location_id = 1
        self._resource_id = 1

    # -----------------------------
    # ID lookup helpers
    # -----------------------------
    def _get_type_id(self, log_obj: LogGeneric):
        t = log_obj.TYPE
        if t in self.type_cache:
            return self.type_cache[t]

        existing = self.types[self.types["type"] == t]
        if not existing.empty:
            tid = int(existing.iloc[0]["id"])
        else:
            tid = self._type_id
            self.types.loc[len(self.types)] = [tid, t]
            self._type_id += 1

        self.type_cache[t] = tid
        return tid

    def _get_location_id(self, location: str):
        if location in self.locations_cache:
            return self.locations_cache[location]

        existing = self.locations[self.locations["location"] == location]
        if not existing.empty:
            lid = int(existing.iloc[0]["id"])
        else:
            lid = self._location_id
            self.locations.loc[len(self.locations)] = [lid, location]
            self._location_id += 1

        self.locations_cache[location] = lid
        return lid

    def _get_resource_id(self, resource: str):
        if resource in self.resources_cache:
            return self.resources_cache[resource]

        existing = self.resources[self.resources["resource"] == resource]
        if not existing.empty:
            rid = int(existing.iloc[0]["id"])
        else:
            rid = self._resource_id
            self.resources.loc[len(self.resources)] = [rid, resource]
            self._resource_id += 1

        self.resources_cache[resource] = rid
        return rid

    # -----------------------------
    # Normalization
    # -----------------------------
    def _normalize_log(self, log_obj: LogGeneric):
        data = asdict(log_obj)

        data["type"] = self._get_type_id(log_obj)
        data["location"] = self._get_location_id(log_obj.location)

        if hasattr(log_obj, "resource"):
            data["resource"] = self._get_resource_id(log_obj.resource)

        if hasattr(log_obj, "destination"):
            data["destination"] = self._get_location_id(log_obj.destination)

        return data

    # -----------------------------
    # Save methods
    # -----------------------------
    def save_log(self, log_obj: LogGeneric):
        data = self._normalize_log(log_obj)
        self.logs = pd.concat([self.logs, pd.DataFrame([data])], ignore_index=True)

    def save_logs(self, log_list: list[LogGeneric]):
        rows = [self._normalize_log(log) for log in log_list]
        self.logs = pd.concat([self.logs, pd.DataFrame(rows)], ignore_index=True)

    def save_log_est(self, log: LogCityEstablishment):
        location_id = self._get_location_id(log.location)
        self.city_locations.loc[len(self.city_locations)] = [
            location_id, log.land_id, log.ocean_id, log.X, log.Y
        ]

    def plot_logs(self,
                filter_city=None,
                filter_resources=None,
                figsize=(14, 10)):

        # -----------------------------
        # Helpers
        # -----------------------------
        def normalize_filter(x):
            if x is None or x == "all":
                return None
            if isinstance(x, str):
                return [x]
            return list(x)

        # -----------------------------
        # Build a readable DataFrame
        # -----------------------------
        df = self.logs.copy()

        if df.empty:
            print("No logs available.")
            return

        # Merge type names
        df = df.merge(self.types, left_on="type", right_on="id", how="left", suffixes=("", "_type"))
        df.rename(columns={"type": "type_id", "type_type": "log_type"}, inplace=True)

        # Merge location names
        df = df.merge(self.locations, left_on="location", right_on="id", how="left", suffixes=("", "_loc"))
        df.rename(columns={"location": "location_id", "location_loc": "city"}, inplace=True)

        # Merge resource names (if present)
        if "resource" in df.columns:
            df = df.merge(self.resources, left_on="resource", right_on="id", how="left", suffixes=("", "_res"))
            df.rename(columns={"resource": "resource_id", "resource_res": "resource"}, inplace=True)

        # Destination city (trade logs)
        if "destination" in df.columns:
            # Create a renamed copy of locations for a clean merge
            dest_locs = self.locations.rename(
                columns={
                    "id": "destination_id",
                    "location": "destination_city",
                }
            )
            df = df.merge(
                dest_locs,
                left_on="destination",
                right_on="destination_id",
                how="left",
            )

        # -----------------------------
        # Filtering
        # -----------------------------
        filter_city = normalize_filter(filter_city)
        filter_resources = normalize_filter(filter_resources)

        if filter_city:
            df = df[df["city"].isin(filter_city)]

        if filter_resources:
            df = df[df["resource"].isin(filter_resources)]

        if df.empty:
            print("No matching logs found.")
            return

        # -----------------------------
        # Resource palette
        # -----------------------------
        resources = list(df["resource"].dropna().unique())
        df["resource"] = pd.Categorical(df["resource"], categories=resources, ordered=True)

        palette = sns.color_palette("tab10", n_colors=len(resources))
        resource_colors = dict(zip(resources, palette))

        # -----------------------------
        # Plotting
        # -----------------------------
        fig, axes = plt.subplots(2, 3, figsize=figsize)
        axes = axes.flatten()

        # 1. Resource amount over time
        df_res = df[(df["log_type"] == "resource") & df["amount"].notna()]

        if not df_res.empty:
            sns.lineplot(
                data=df_res,
                x="turn",
                y="amount",
                hue="resource",
                hue_order=resources,
                palette=resource_colors,
                ax=axes[0],
            )
            axes[0].set_title("Resource Amount Over Time")
            axes[0].set_xlabel("Turn")
            axes[0].set_ylabel("Amount")

        # 2. Net production (production - consumption)
        df_pc = df[df["log_type"].isin(["production", "consumption"])].copy()
        df_pc["signed_amount"] = df_pc.apply(
            lambda row: row["amount"] if row["log_type"] == "production" else -row["amount"],
            axis=1
        )

        net_df = df_pc.groupby(["turn", "city", "resource"], as_index=False)["signed_amount"].sum()

        if not net_df.empty:
            sns.lineplot(
                data=net_df,
                x="turn",
                y="signed_amount",
                hue="resource",
                hue_order=resources,
                palette=resource_colors,
                ax=axes[1]
            )
            axes[1].set_title("Net Production")
            axes[1].set_xlabel("Turn")
            axes[1].set_ylabel("Net Amount")

        # 3. Prices over time
        df_price = df[df["price"].notna()]
        if not df_price.empty:
            sns.lineplot(
                data=df_price,
                x="turn",
                y="price",
                hue="resource",
                hue_order=resources,
                palette=resource_colors,
                ax=axes[2]
            )
            axes[2].set_title("Resource Prices")

        # 4. Population over time
        df_pop = df[df["population"].notna()]
        if not df_pop.empty:
            sns.lineplot(
                data=df_pop,
                x="turn",
                y="population",
                hue="city",
                ax=axes[3]
            )
            axes[3].set_title("Population")

        # 5. Trade matrix (origin → destination)
        if filter_resources is None and "destination_city" in df.columns:
            df_trade = df[df["log_type"] == "trade"].copy()
            if not df_trade.empty:
                df_trade["value"] = df_trade["amount"] * df_trade["price"]

                matrix = df_trade.pivot_table(
                    index="city",
                    columns="destination_city",
                    values="value",
                    aggfunc="sum",
                    fill_value=0
                )

                sns.heatmap(matrix, annot=True, fmt="g", cmap="viridis", ax=axes[4])
                axes[4].set_title("Trade Value Matrix")
                axes[4].set_xlabel("Destination")
                axes[4].set_ylabel("Origin")


        plt.tight_layout()
        plt.show()
        plt.savefig("visualization/prices.png")
