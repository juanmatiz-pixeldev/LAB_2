"""Draw docs/star_schema.png (helper script; the same schema is also in README as Mermaid)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

T = {
 "DimDate": (0.02, 0.55, ["date_key (PK)", "full_date", "year", "quarter", "month_number", "month_name", "year_month", "day_of_month", "day_name"], "#dbeafe"),
 "DimStore": (0.02, 0.10, ["store_key (PK)", "store_id (BK)", "store_name", "city", "region"], "#dbeafe"),
 "DimChannel": (0.36, 0.01, ["channel_key (PK)", "channel_id (BK)", "channel_name"], "#dbeafe"),
 "DimProduct": (0.72, 0.10, ["product_key (PK)", "product_id (BK)", "product_name", "category", "brand"], "#dbeafe"),
 "DimPromotion": (0.72, 0.55, ["promotion_key (PK)", "promotion_id (BK)", "promotion_name", "discount_pct"], "#dbeafe"),
 "FactSales": (0.36, 0.30, ["sales_key (PK)", "sale_line_id (degenerate, UNIQUE)", "date_key (FK)", "store_key (FK)", "channel_key (FK)",
     "product_key (FK)", "promotion_key (FK)", "-- measures --", "quantity", "gross_sales", "net_sales", "discount_amount", "cost_amount", "gross_profit"], "#fde68a"),
}
W = {"FactSales": 0.28}
RH = 0.040
fig, ax = plt.subplots(figsize=(14, 9)); ax.axis("off")
pos = {}
for name, (x, y, cols, color) in T.items():
    w = W.get(name, 0.24); h = RH * (len(cols) + 1)
    if name == "FactSales": y = 0.20
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.005", fc=color, ec="#333", lw=1.5))
    ax.text(x + w / 2, y + h - 0.028, name, ha="center", va="center", fontsize=12, fontweight="bold")
    for i, c in enumerate(cols):
        ax.text(x + 0.01, y + h - 0.065 - i * RH, c, fontsize=9.5, va="center", family="monospace",
                fontweight="bold" if "(PK)" in c or "(FK)" in c else "normal")
    pos[name] = (x, y, w, h)
fx, fy, fw, fh = pos["FactSales"]
for d, (side) in {"DimDate": "l", "DimStore": "l", "DimChannel": "b", "DimProduct": "r", "DimPromotion": "r"}.items():
    x, y, w, h = pos[d]
    a = (x + w / 2, y + h / 2)
    if side == "l": b = (fx, fy + fh / 2)
    elif side == "r": b = (fx + fw, fy + fh / 2)
    else: b = (fx + fw / 2, fy)
    ax.annotate("", xy=b, xytext=((x if side == "r" else x + w) if side != "b" else x + w / 2, y + h / 2 if side != "b" else y + h),
                arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.5))
ax.set_xlim(0, 1); ax.set_ylim(0, 1.0)
ax.set_title("Retail DW - Star Schema (grain: one row per sales line)", fontsize=14, fontweight="bold", y=0.99)
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "docs"), exist_ok=True)
fig.savefig(os.path.join(os.path.dirname(__file__), "..", "docs", "star_schema.png"), dpi=140, bbox_inches="tight")
