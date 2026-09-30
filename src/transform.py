from pathlib import Path
import pandas as pd

PROCESSED_DIR = Path("data/processed")


def transform_data(data):
    orders = data["orders"].copy()
    items = data["order_items"].copy()
    products = data["products"].copy()
    translation = data["category_translation"].copy()

    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]

    for column in date_columns:
        orders[column] = pd.to_datetime(
            orders[column],
            errors="coerce"
        )

    items["price"] = pd.to_numeric(items["price"], errors="coerce")
    items["freight_value"] = pd.to_numeric(
        items["freight_value"],
        errors="coerce"
    )

    invalid_items = items[
        (items["price"] < 0) |
        (items["freight_value"] < 0)
    ].copy()

    invalid_items["reject_reason"] = "negative price or freight"

    invalid_items.to_csv(
        PROCESSED_DIR / "rejected_order_items.csv",
        index=False
    )

    items = items[
        (items["price"] >= 0) &
        (items["freight_value"] >= 0)
    ].copy()

    items["revenue"] = items["price"] + items["freight_value"]

    orders["delivery_days"] = (
        orders["order_delivered_customer_date"]
        - orders["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400

    orders["delay_flag"] = (
        orders["order_delivered_customer_date"]
        > orders["order_estimated_delivery_date"]
    ).astype(int)

    products = products.merge(
        translation,
        on="product_category_name",
        how="left"
    )

    products["product_category_name_english"] = (
        products["product_category_name_english"]
        .fillna(products["product_category_name"])
    )

    output = {
        "customers": data["customers"],
        "orders": orders,
        "order_items": items,
        "products": products,
        "sellers": data["sellers"],
        "order_payments": data["order_payments"],
        "order_reviews": data["order_reviews"]
    }

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    for name, df in output.items():
        df.to_csv(
            PROCESSED_DIR / f"{name}.csv",
            index=False
        )

    return output


if __name__ == "__main__":
    from src.ingest import load_data

    data = load_data()
    transform_data(data)

    print("Transformation completed.")