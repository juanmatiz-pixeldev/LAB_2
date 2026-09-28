"""Create the SQLite star schema (dimensions first, then the fact table)."""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "retail_dw.db")

DDL = """
DROP TABLE IF EXISTS FactSales;
DROP TABLE IF EXISTS DimDate;
DROP TABLE IF EXISTS DimStore;
DROP TABLE IF EXISTS DimChannel;
DROP TABLE IF EXISTS DimProduct;
DROP TABLE IF EXISTS DimPromotion;

-- R1, R2, R5: time analysis (monthly trend, store/channel over time, margin by month)
CREATE TABLE DimDate (
    date_key      INTEGER PRIMARY KEY,           -- surrogate key
    full_date     TEXT    NOT NULL UNIQUE,       -- YYYY-MM-DD
    year          INTEGER NOT NULL,
    quarter       INTEGER NOT NULL,
    month_number  INTEGER NOT NULL,
    month_name    TEXT    NOT NULL,
    year_month    TEXT    NOT NULL,              -- YYYY-MM (sortable month label)
    day_of_month  INTEGER NOT NULL,
    day_name      TEXT    NOT NULL
);

-- R2, R5: compare stores
CREATE TABLE DimStore (
    store_key   INTEGER PRIMARY KEY,             -- surrogate key
    store_id    TEXT    NOT NULL UNIQUE,         -- business key
    store_name  TEXT    NOT NULL,
    city        TEXT    NOT NULL,
    region      TEXT    NOT NULL
);

-- R2: compare sales channels
CREATE TABLE DimChannel (
    channel_key   INTEGER PRIMARY KEY,           -- surrogate key
    channel_id    TEXT    NOT NULL UNIQUE,       -- business key
    channel_name  TEXT    NOT NULL
);

-- R3, R5: categories and brands
CREATE TABLE DimProduct (
    product_key   INTEGER PRIMARY KEY,           -- surrogate key
    product_id    TEXT    NOT NULL UNIQUE,       -- business key
    product_name  TEXT    NOT NULL,
    category      TEXT    NOT NULL,
    brand         TEXT    NOT NULL
);

-- R4: promotion types
CREATE TABLE DimPromotion (
    promotion_key   INTEGER PRIMARY KEY,         -- surrogate key
    promotion_id    TEXT    NOT NULL UNIQUE,     -- business key
    promotion_name  TEXT    NOT NULL,
    discount_pct    REAL    NOT NULL
);

-- Grain: one row per sales line (one product on one sales transaction)
CREATE TABLE FactSales (
    sales_key        INTEGER PRIMARY KEY,        -- surrogate key of the fact row
    sale_line_id     TEXT    NOT NULL UNIQUE,    -- degenerate dimension: enforces the grain
    date_key         INTEGER NOT NULL REFERENCES DimDate(date_key),
    store_key        INTEGER NOT NULL REFERENCES DimStore(store_key),
    channel_key      INTEGER NOT NULL REFERENCES DimChannel(channel_key),
    product_key      INTEGER NOT NULL REFERENCES DimProduct(product_key),
    promotion_key    INTEGER NOT NULL REFERENCES DimPromotion(promotion_key),
    quantity         INTEGER NOT NULL CHECK (quantity > 0),
    gross_sales      INTEGER NOT NULL,           -- quantity * list_price (COP)
    net_sales        INTEGER NOT NULL,           -- quantity * unit_price_sale (COP)
    discount_amount  INTEGER NOT NULL,           -- gross_sales - net_sales
    cost_amount      INTEGER NOT NULL,           -- quantity * unit_cost
    gross_profit     INTEGER NOT NULL            -- net_sales - cost_amount
);

CREATE INDEX ix_fact_date      ON FactSales(date_key);
CREATE INDEX ix_fact_store     ON FactSales(store_key);
CREATE INDEX ix_fact_channel   ON FactSales(channel_key);
CREATE INDEX ix_fact_product   ON FactSales(product_key);
CREATE INDEX ix_fact_promotion ON FactSales(promotion_key);
"""


def get_connection(db_path=DB_PATH):
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn):
    conn.executescript(DDL)
    conn.commit()
    print("[schema] star schema created")


if __name__ == "__main__":
    with get_connection() as c:
        create_schema(c)
