import os
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


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

    fig, axes = plt.subplots(2, 3, figsize=figsize)
    axes = axes.flatten()
    axes_index = 0

    # Primary Resource amount over time (only specific log types)
    valid_amount_types = ["resource"]
    df_res = df[df["log_type"].isin(valid_amount_types) & df["amount"].notna()]
    df_res = df_res[df_res["resource_tier"]==0]
    if not df_res.empty:
        sns.lineplot(
            data=df_res,
            x="turn",
            y="amount",
            hue="resource",
            hue_order=resources,
            palette=resource_colors,
            ax=axes[axes_index],
        )
        axes[axes_index].set_title("Primary Resource Amount Over Time")
        axes[axes_index].set_xlabel("Turn")
        axes[axes_index].set_ylabel("Amount")
        axes[axes_index].set_ylim(0, 1_000)
        axes_index += 1

    # Net primary resource income
    
    df_pc = df[df["log_type"].isin(["production", "consumption"])].copy()
    df_pc = df_pc[df_pc["resource_tier"]==0]
    df_pc["signed_amount"] = df_pc.apply(
        lambda row: row["amount"] if row["log_type"] == "production" else -row["amount"],
        axis=1
    )
    net_df = df_pc.groupby(["turn", "city", "resource"], as_index=False, observed=True)["signed_amount"].sum()

    if not net_df.empty:
        sns.lineplot(
            data=net_df,
            x="turn",
            y="signed_amount",
            hue="resource",
            hue_order=resources,
            palette=resource_colors,
            ax=axes[axes_index]
        )

        axes[axes_index].set_title("Net Primary Resource Production")
        axes[axes_index].set_xlabel("Turn")
        axes[axes_index].set_ylabel("Net Amount")
        axes_index += 1

    # Primary Prices over time
    df_price = df[df["price"].notna()]
    df_price = df_price[df_price["resource_tier"]==0]
    if not df_price.empty:
        sns.lineplot(
            data=df_price,
            x="turn",
            y="price",
            hue="resource",
            hue_order=resources,
            palette=resource_colors,
            ax=axes[axes_index])
        axes[axes_index].set_title("Primary Resource Prices")
        axes[axes_index].set_ylim(0, 25)
        axes_index += 1

    # Secondary Resource amount over time
    valid_amount_types = ["resource"]
    df_res = df[df["log_type"].isin(valid_amount_types) & df["amount"].notna()]
    df_res = df_res[df_res["resource_tier"]==1]

    if not df_res.empty:
        sns.lineplot(
            data=df_res,
            x="turn",
            y="amount",
            hue="resource",
            hue_order=resources,
            palette=resource_colors,
            ax=axes[axes_index],
        )
        axes[axes_index].set_title("Secondary Resource Amount Over Time")
        axes[axes_index].set_xlabel("Turn")
        axes[axes_index].set_ylabel("Amount")
        axes[axes_index].set_ylim(0, 10_000)
        axes_index += 1

    # Net secondary resource income

    df_pc = df[df["log_type"].isin(["production", "consumption"])].copy()
    df_pc = df_pc[df_pc["resource_tier"]==1]
    df_pc["signed_amount"] = df_pc.apply(
        lambda row: row["amount"] if row["log_type"] == "production" else -row["amount"],
        axis=1
    )
    net_df = df_pc.groupby(["turn", "city", "resource"], as_index=False, observed=True)["signed_amount"].sum()

    if not net_df.empty:
        sns.lineplot(
            data=net_df,
            x="turn",
            y="signed_amount",
            hue="resource",
            hue_order=resources,
            palette=resource_colors,
            ax=axes[axes_index]
        )

        axes[axes_index].set_title("Net Secondary Resource Production")
        axes[axes_index].set_xlabel("Turn")
        axes[axes_index].set_ylabel("Net Amount")
        axes_index += 1

    # Secondary Prices over time
    df_price = df[df["price"].notna()]
    df_price = df_price[df_price["resource_tier"]==1]
    if not df_price.empty:
        sns.lineplot(
            data=df_price,
            x="turn",
            y="price",
            hue="resource",
            hue_order=resources,
            palette=resource_colors,
            ax=axes[axes_index])
        axes[axes_index].set_title("Secondary Resource Prices")
        axes[axes_index].set_ylim(0, 25)
        axes_index += 1


    plt.tight_layout()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(script_dir, "..", "visualization", "plots_res.png")
    plt.savefig(img_path, dpi=200)
    plt.show()


if __name__=="__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "log.sqlite")

    plot_logs(db_path)
    # plot_logs("../log.sqlite", None, ["marble", "silver"])
    # plot_logs("../log.sqlite", "Prosperidad")
    # plot_logs("../log.sqlite", None, ["food", "wood_coni", "wood_deci"])