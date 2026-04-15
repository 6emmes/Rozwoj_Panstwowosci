import os
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


MIN_TRADE_VALUE = 50


def load_logs(db_path: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)

    df = pd.read_sql_query("""
        SELECT 
            logs.turn,
            logs.price,
            logs.amount,
            logs.population,
            logs.description,
            logs.destination,
            logs.travel_time,
            types.type AS log_type,
            resources.resource AS resource,
            resources.tier AS resource_tier,
            src.location AS city,
            dst.location AS destination_city
        FROM logs
        LEFT JOIN types ON logs.type = types.id
        LEFT JOIN locations AS src ON logs.location = src.id
        LEFT JOIN resources ON logs.resource = resources.id
        LEFT JOIN locations AS dst ON logs.destination = dst.id
        ORDER BY logs.turn ASC
    """, conn)


    conn.close()
    return df


def plot_logs(db_path: str,
              filter_city=None,
              filter_resources=None,
              figsize=(14, 10)):

    def normalize_filter(x):
        if x is None or x == "all":
            return None
        if isinstance(x, str):
            return [x]
        return list(x) 

    df = load_logs(db_path)
    

    resources = list(df["resource"].dropna().unique())
    df["resource"] = pd.Categorical(
        df["resource"],
        categories=resources,
        ordered=True
    )
    palette = sns.color_palette("tab10", n_colors=len(resources))
    resource_colors = dict(zip(resources, palette))


    filter_city = normalize_filter(filter_city)
    filter_resources = normalize_filter(filter_resources)
    if filter_city:
        df = df[df["city"].isin(filter_city)]
    if filter_resources:
        df = df[df["resource"].isin(filter_resources)]

    if df.empty:
        print("No matching logs found.")
        return

    fig, axes = plt.subplots(1, 1, figsize=figsize)
    axes_index = 0

    # 5. Trades (amount vs travel time or destination)
    df_trade = df[df["log_type"] == "trade"].copy()
    df_trade["value"] = df_trade["amount"] * df_trade["price"]

    matrix = df_trade.pivot_table(
        index="city",
        columns="destination_city",
        values="value",
        aggfunc="sum",
        fill_value=0
    )

    filtered_matrix = matrix.loc[
    (matrix > MIN_TRADE_VALUE).any(axis=1),   #  rows
    (matrix > MIN_TRADE_VALUE).any(axis=0)    #  columns
    ]

    combined = filtered_matrix - filtered_matrix.T
    triangular = combined.where(
    np.tril(np.ones(combined.shape), k=-1).astype(bool)
    )
    triangular = triangular.dropna(how="all").dropna(how="all", axis=1)
    sns.heatmap(
        triangular,
        annot=True,
        fmt="g",
        cmap="viridis",
        ax=axes
    )



    # sns.heatmap(filtered_matrix, annot=True, fmt="g", cmap="viridis", ax=axes)
    axes.set_title("Trade Value Matrix")
    axes.set_xlabel("Destination")
    axes.set_ylabel("Origin")



    plt.tight_layout()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(script_dir, "..", "visualization", "plots_trd.png")
    plt.savefig(img_path, dpi=200)
    plt.show()


if __name__=="__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "log.sqlite")

    plot_logs(db_path)
    # plot_logs("../log.sqlite", None, ["marble", "silver"])
    # plot_logs("../log.sqlite", "Prosperidad")
    # plot_logs("../log.sqlite", None, ["food", "wood_coni", "wood_deci"])