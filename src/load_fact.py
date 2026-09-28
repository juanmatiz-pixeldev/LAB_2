"""Load FactSales: map business keys to surrogate keys and calculate measures."""


def load_fact(conn, ref, sales, keys):
    prod = {p["product_id"]: p for p in ref["products"]}  # list_price / unit_cost used only for measures
    rows = []
    for r in sales.itertuples(index=False):
        p = prod[r.product_id]
        gross = int(r.quantity * p["list_price"])
        net = int(r.quantity * r.unit_price_sale)
        cost = int(r.quantity * p["unit_cost"])
        rows.append((
            r.sale_line_id,
            keys["date"][r.sale_date], keys["store"][r.store_id], keys["channel"][r.channel_id],
            keys["product"][r.product_id], keys["promotion"][r.promotion_id],
            int(r.quantity), gross, net, gross - net, cost, net - cost,
        ))  # a KeyError here means an unmapped identifier -> load fails loudly
    conn.executemany(
        """INSERT INTO FactSales (sale_line_id, date_key, store_key, channel_key, product_key,
               promotion_key, quantity, gross_sales, net_sales, discount_amount, cost_amount, gross_profit)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", rows)
    conn.commit()
    print(f"[fact] {len(rows)} rows loaded into FactSales")
