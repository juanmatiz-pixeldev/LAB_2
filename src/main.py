"""End-to-end run: schema -> dimensions -> fact -> validation -> queries -> charts."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from create_schema import get_connection, create_schema
from load_dimensions import read_reference, read_sales, load_dimensions
from load_fact import load_fact
from queries import run_all, run_query

DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")


def validate(conn, sales):
    n = conn.execute("SELECT COUNT(*) FROM FactSales").fetchone()[0]
    assert n == len(sales) == sales["sale_line_id"].nunique(), "grain violated"
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == [], "FK violation"
    src = int((sales["quantity"] * sales["unit_price_sale"]).sum())
    assert conn.execute("SELECT SUM(net_sales) FROM FactSales").fetchone()[0] == src, "net sales mismatch"
    print(f"[validate] OK: {n} fact rows = {n} source lines, FKs valid, net sales reconciles ({src:,} COP)")


def charts(conn):
    os.makedirs(DOCS, exist_ok=True)
    # Visualization 1 (R1, temporal): monthly net sales trend
    m = run_query(conn, "R1_monthly_net_sales")
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.plot(m["year_month"], m["net_sales"] / 1e6, marker="o", color="#1f77b4")
    for x, y in zip(m["year_month"], m["net_sales"] / 1e6):
        ax.annotate(f"{y:,.0f}", (x, y), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=8)
    ax.set(title="R1 - Monthly net sales (Jan-Jun 2026)", xlabel="Month", ylabel="Net sales (million COP)")
    ax.grid(alpha=.3); ax.set_ylim(0, (m["net_sales"] / 1e6).max() * 1.2)
    fig.tight_layout(); fig.savefig(os.path.join(DOCS, "viz1_monthly_net_sales.png"), dpi=150); plt.close(fig)

    # Visualization 2 (R2, comparative): net sales by store and month
    s = run_query(conn, "R2b_sales_by_store_month").pivot(index="year_month", columns="store_name", values="net_sales") / 1e6
    ax = s.plot(kind="bar", figsize=(8, 4.2), width=.8)
    ax.set(title="R2 - Net sales by store and month", xlabel="Month", ylabel="Net sales (million COP)")
    ax.tick_params(axis="x", rotation=0); ax.grid(axis="y", alpha=.3); ax.legend(title="Store")
    plt.tight_layout(); plt.savefig(os.path.join(DOCS, "viz2_sales_by_store_month.png"), dpi=150); plt.close()
    print("[charts] saved to docs/")


def main():
    ref, sales = read_reference(), read_sales()
    with get_connection() as conn:
        create_schema(conn)
        keys = load_dimensions(conn, ref, sales)   # dimensions BEFORE the fact table
        load_fact(conn, ref, sales, keys)
        validate(conn, sales)
        results = run_all(conn)
        for name, df in results.items():
            print(f"\n--- {name} ---\n{df.to_string(index=False)}")
        charts(conn)


if __name__ == "__main__":
    main()
