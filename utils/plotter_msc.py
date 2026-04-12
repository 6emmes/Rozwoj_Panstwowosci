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
    df["resource"] = pd.Categorical(
        df["resource"], categories=resources, ordered=True)
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

    fig, axes = plt.subplots(1, 3, figsize=figsize)
    axes = axes.flatten()

    # 4. Population over time
    df_pop = df[df["population"].notna()]
    df_pop = df_pop[df_pop["population"] > 25]
    if not df_pop.empty:
        sns.lineplot(data=df_pop,
                     x="turn",
                     y="population",
                     hue="city",
                    legend = False,
                     ax=axes[0])
        axes[0].set_title("Population")

        # 5. Resource amount over time
    df_res = df[df["amount"].notna()]
    df_res = df_res[df_res["resource"] == "score"]
    if not df_res.empty:
        sns.lineplot(
            data=df_res,
            x="turn",
            y="amount",
            hue="city",
            ax=axes[1],
        )
        axes[1].set_title("Score")

    plt.tight_layout()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(script_dir, "..", "visualization", "plots_msc.png")
    plt.savefig(img_path, dpi=200)
    plt.show()


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "log.sqlite")

    plot_logs(db_path)
    # plot_logs("log.sqlite", "Prosperidad")
    # plot_logs("log.sqlite", None, ["food", "wood"])
