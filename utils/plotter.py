import json
import math
import os
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def load_logs(db_path: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)

    df = pd.read_sql_query(
        """
        SELECT 
            logs.turn,
            logs.price,
            logs.amount,
            logs.population,
            logs.description,
            logs.destination,
            logs.travel_time,
            logs.traits,
            types.type AS log_type,
            resources.resource AS resource,
            src.location AS city,
            dst.location AS destination_city
        FROM logs
        LEFT JOIN types ON logs.type = types.id
        LEFT JOIN locations AS src ON logs.location = src.id
        LEFT JOIN resources ON logs.resource = resources.id
        LEFT JOIN locations AS dst ON logs.destination = dst.id
        ORDER BY logs.turn ASC
    """,
        conn,
    )

    conn.close()
    return df


def plot_logs(img_path: str, filter_city=None, filter_resources=None, figsize=(14, 10)):

    def normalize_filter(x):
        if x is None or x == "all":
            return None
        if isinstance(x, str):
            return [x]
        return list(x)

    df = load_logs(img_path)

    resources = list(df["resource"].dropna().unique())
    df["resource"] = pd.Categorical(df["resource"], categories=resources, ordered=True)
    palette = sns.color_palette("tab10", n_colors=len(resources))
    resource_colors = dict(zip(resources, palette))

    filter_city = normalize_filter(filter_city)
    filter_resources = normalize_filter(filter_resources)
    if filter_city:
        df = df[df["city"].isin(filter_city)]
    if filter_resources:
        df = df[df["resource"].isin(filter_resources) | df["resource"].isna()]

    if df.empty:
        print("No matching logs found.")
        return

    # Pre-parse culture traits to determine dynamic grid size
    df_culture = df[df["log_type"] == "culture"].copy()
    num_traits = 0
    if not df_culture.empty and "traits" in df_culture.columns:

        def parse_traits(val):
            if pd.isna(val):
                return []
            try:
                return json.loads(val)
            except:
                return []

        df_culture["traits"] = df_culture["traits"].apply(parse_traits)
        if not df_culture.empty:
            num_traits = df_culture["traits"].apply(len).max()

    total_plots = 5 + num_traits
    rows = max(2, math.ceil(total_plots / 3))
    fig, axes = plt.subplots(rows, 3, figsize=(figsize[0], 5 * rows))
    axes = axes.flatten()

    # 1. Resource amount over time (only specific log types)
    valid_amount_types = ["resource"]
    df_res = df[df["log_type"].isin(valid_amount_types) & df["amount"].notna()]

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
        axes[0].set_ylim(0, 10_000)

    # 2. Net resource income

    df_pc = df[df["log_type"].isin(["production", "consumption"])].copy()
    df_pc["signed_amount"] = df_pc.apply(
        lambda row: (
            row["amount"] if row["log_type"] == "production" else -row["amount"]
        ),
        axis=1,
    )
    net_df = df_pc.groupby(["turn", "city", "resource"], as_index=False, observed=True)[
        "signed_amount"
    ].sum()

    if not net_df.empty:
        sns.lineplot(
            data=net_df,
            x="turn",
            y="signed_amount",
            hue="resource",
            hue_order=resources,
            palette=resource_colors,
            ax=axes[1],
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
            ax=axes[2],
        )
        axes[2].set_title("Resource Prices")

    # 4. Population over time
    df_pop = df[df["population"].notna()]
    df_pop = df_pop[df_pop["population"] > 25]
    if not df_pop.empty:
        sns.lineplot(data=df_pop, x="turn", y="population", hue="city", ax=axes[3])
        axes[3].set_title("Population")

    # 5. Trades (amount vs travel time or destination)
    if filter_resources is None:
        df_trade = df[df["log_type"] == "trade"].copy()
        df_trade["value"] = df_trade["amount"] * df_trade["price"]

        matrix = df_trade.pivot_table(
            index="city",
            columns="destination_city",
            values="value",
            aggfunc="sum",
            fill_value=0,
        )

        sns.heatmap(matrix, annot=True, fmt="g", cmap="viridis", ax=axes[4])
        axes[4].set_title("Trade Value Matrix")
        axes[4].set_xlabel("Destination")
        axes[4].set_ylabel("Origin")

    # 6. Culture traits over time
    if not df_culture.empty and num_traits > 0:
        for i in range(num_traits):
            ax_idx = 5 + i
            dim_col = f"Trait {i}"
            df_culture[dim_col] = df_culture["traits"].apply(
                lambda t: t[i] if len(t) > i else None
            )

            sns.lineplot(
                data=df_culture,
                x="turn",
                y=dim_col,
                hue="city",
                ax=axes[ax_idx],
                legend=False,
            )
            axes[ax_idx].set_title(f"Culture Trait {i} Over Time")
            axes[ax_idx].set_xlabel("Turn")
            axes[ax_idx].set_ylabel(f"Value (Dim {i})")

    # Hide any unused subplots
    for i in range(total_plots, len(axes)):
        axes[i].set_visible(False)

    plt.tight_layout()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(script_dir, "..", "visualization", "plots.png")
    plt.savefig(img_path, dpi=200)
    plt.show()


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "log.sqlite")

    plot_logs(db_path)
    # plot_logs("log.sqlite", "Prosperidad")
    # plot_logs("log.sqlite", None, ["food", "wood"])
