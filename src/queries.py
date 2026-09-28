"""Requirement-driven SQL queries executed against the Data Warehouse only."""
import pandas as pd

QUERIES = {
    "R1_monthly_net_sales": """
        SELECT d.year_month,
               SUM(f.net_sales) AS net_sales,
               ROUND(100.0 * (SUM(f.net_sales) - LAG(SUM(f.net_sales)) OVER (ORDER BY d.year_month))
                     / LAG(SUM(f.net_sales)) OVER (ORDER BY d.year_month), 1) AS mom_growth_pct
        FROM FactSales f JOIN DimDate d ON d.date_key = f.date_key
        GROUP BY d.year_month ORDER BY d.year_month""",

    "R2a_sales_by_store_channel": """
        SELECT s.store_name, c.channel_name,
               COUNT(*) AS sales_lines, SUM(f.quantity) AS units, SUM(f.net_sales) AS net_sales
        FROM FactSales f
        JOIN DimStore s   ON s.store_key = f.store_key
        JOIN DimChannel c ON c.channel_key = f.channel_key
        GROUP BY s.store_name, c.channel_name ORDER BY net_sales DESC""",

    "R2b_sales_by_store_month": """
        SELECT d.year_month, s.store_name, SUM(f.net_sales) AS net_sales
        FROM FactSales f
        JOIN DimDate d  ON d.date_key = f.date_key
        JOIN DimStore s ON s.store_key = f.store_key
        GROUP BY d.year_month, s.store_name ORDER BY d.year_month, s.store_name""",

    "R2c_sales_by_channel_month": """
        SELECT d.year_month, c.channel_name, SUM(f.net_sales) AS net_sales
        FROM FactSales f
        JOIN DimDate d    ON d.date_key = f.date_key
        JOIN DimChannel c ON c.channel_key = f.channel_key
        GROUP BY d.year_month, c.channel_name ORDER BY d.year_month, c.channel_name""",

    "R3a_sales_units_by_category": """
        SELECT p.category, SUM(f.quantity) AS units, SUM(f.net_sales) AS net_sales
        FROM FactSales f JOIN DimProduct p ON p.product_key = f.product_key
        GROUP BY p.category ORDER BY net_sales DESC""",

    "R3b_sales_units_by_brand": """
        SELECT p.brand, SUM(f.quantity) AS units, SUM(f.net_sales) AS net_sales
        FROM FactSales f JOIN DimProduct p ON p.product_key = f.product_key
        GROUP BY p.brand ORDER BY net_sales DESC""",

    "R3c_sales_units_by_category_brand": """
        SELECT p.category, p.brand, SUM(f.quantity) AS units, SUM(f.net_sales) AS net_sales
        FROM FactSales f JOIN DimProduct p ON p.product_key = f.product_key
        GROUP BY p.category, p.brand ORDER BY net_sales DESC LIMIT 10""",

    "R4_promotion_performance": """
        SELECT pr.promotion_name, pr.discount_pct,
               COUNT(*) AS sales_lines, SUM(f.quantity) AS units,
               SUM(f.gross_sales) AS gross_sales, SUM(f.net_sales) AS net_sales,
               SUM(f.discount_amount) AS discount_amount
        FROM FactSales f JOIN DimPromotion pr ON pr.promotion_key = f.promotion_key
        GROUP BY pr.promotion_name, pr.discount_pct ORDER BY pr.discount_pct""",

    "R5a_margin_by_category": """
        SELECT p.category, SUM(f.net_sales) AS net_sales, SUM(f.gross_profit) AS gross_profit,
               ROUND(100.0 * SUM(f.gross_profit) / SUM(f.net_sales), 2) AS gross_margin_pct
        FROM FactSales f JOIN DimProduct p ON p.product_key = f.product_key
        GROUP BY p.category ORDER BY gross_margin_pct DESC""",

    "R5b_margin_by_store": """
        SELECT s.store_name, SUM(f.net_sales) AS net_sales, SUM(f.gross_profit) AS gross_profit,
               ROUND(100.0 * SUM(f.gross_profit) / SUM(f.net_sales), 2) AS gross_margin_pct
        FROM FactSales f JOIN DimStore s ON s.store_key = f.store_key
        GROUP BY s.store_name ORDER BY gross_margin_pct DESC""",

    "R5c_margin_by_month": """
        SELECT d.year_month, SUM(f.net_sales) AS net_sales, SUM(f.gross_profit) AS gross_profit,
               ROUND(100.0 * SUM(f.gross_profit) / SUM(f.net_sales), 2) AS gross_margin_pct
        FROM FactSales f JOIN DimDate d ON d.date_key = f.date_key
        GROUP BY d.year_month ORDER BY d.year_month""",

    "R5d_margin_category_store_month": """
        SELECT d.year_month, s.store_name, p.category,
               SUM(f.gross_profit) AS gross_profit,
               ROUND(100.0 * SUM(f.gross_profit) / SUM(f.net_sales), 2) AS gross_margin_pct
        FROM FactSales f
        JOIN DimDate d    ON d.date_key = f.date_key
        JOIN DimStore s   ON s.store_key = f.store_key
        JOIN DimProduct p ON p.product_key = f.product_key
        GROUP BY d.year_month, s.store_name, p.category
        ORDER BY d.year_month, s.store_name, p.category LIMIT 12""",
}


def run_query(conn, name):
    return pd.read_sql_query(QUERIES[name], conn)


def run_all(conn):
    return {name: run_query(conn, name) for name in QUERIES}
