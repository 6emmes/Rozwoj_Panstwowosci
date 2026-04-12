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

    df = load_logs(img_path)

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

    total_plots = num_traits
    rows = max(2, math.ceil(total_plots / 3))
    fig, axes = plt.subplots(rows, 3, figsize=(figsize[0], 5 * rows))
    axes = axes.flatten()

    # 6. Culture traits over time
    if not df_culture.empty and num_traits > 0:
        for i in range(num_traits):
            ax_idx = i
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
