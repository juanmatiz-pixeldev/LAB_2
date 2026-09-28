"""Load the five dimension tables and return {business_key: surrogate_key} maps."""
import json
import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def read_reference(data_dir=DATA_DIR):
    with open(os.path.join(data_dir, "reference_data.json"), encoding="utf-8") as f:
        return json.load(f)


def read_sales(data_dir=DATA_DIR):
    return pd.read_csv(os.path.join(data_dir, "sales_transactions.csv"))


def _load(conn, table, cols, rows, key_col, bk_col):
    conn.executemany(
        f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})", rows
    )
    conn.commit()
    return dict(conn.execute(f"SELECT {bk_col}, {key_col} FROM {table}").fetchall())


def load_dimensions(conn, ref, sales):
    keys = {}

    # DimDate: built from the distinct sale_date values (surrogate keys assigned in date order)
    dates = pd.to_datetime(sorted(sales["sale_date"].unique()))
    rows = [(d.strftime("%Y-%m-%d"), d.year, (d.month - 1) // 3 + 1, d.month, d.strftime("%B"),
             d.strftime("%Y-%m"), d.day, d.strftime("%A")) for d in dates]
    keys["date"] = _load(conn, "DimDate",
                         ["full_date", "year", "quarter", "month_number", "month_name",
                          "year_month", "day_of_month", "day_name"],
                         rows, "date_key", "full_date")

    keys["store"] = _load(conn, "DimStore", ["store_id", "store_name", "city", "region"],
                          [(s["store_id"], s["store_name"], s["city"], s["region"]) for s in ref["stores"]],
                          "store_key", "store_id")
    keys["channel"] = _load(conn, "DimChannel", ["channel_id", "channel_name"],
                            [(c["channel_id"], c["channel_name"]) for c in ref["channels"]],
                            "channel_key", "channel_id")
    keys["product"] = _load(conn, "DimProduct", ["product_id", "product_name", "category", "brand"],
                            [(p["product_id"], p["product_name"], p["category"], p["brand"]) for p in ref["products"]],
                            "product_key", "product_id")
    keys["promotion"] = _load(conn, "DimPromotion", ["promotion_id", "promotion_name", "discount_pct"],
                              [(p["promotion_id"], p["promotion_name"], p["discount_pct"]) for p in ref["promotions"]],
                              "promotion_key", "promotion_id")
    print({k: len(v) for k, v in keys.items()}, "<- dimension rows loaded")
    return keys
