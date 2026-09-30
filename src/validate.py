from pathlib import Path
import pandas as pd

PROCESSED_DIR = Path("data/processed")


def check_required_nulls(df, columns):
    return {
        column: int(df[column].isna().sum())
        for column in columns
        if column in df.columns
    }


def check_duplicate_keys(df, key):
    return int(df[key].duplicated().sum())


def check_orphan_keys(child_df, child_key, parent_df, parent_key):
    child_values = set(child_df[child_key].dropna())
    parent_values = set(parent_df[parent_key].dropna())
    return len(child_values - parent_values)


def check_invalid_values(data):
    results = {}

    orders = data["orders"]

    purchase = pd.to_datetime(
        orders["order_purchase_timestamp"], errors="coerce"
    )
    delivered = pd.to_datetime(
        orders["order_delivered_customer_date"], errors="coerce"
    )

    results["delivery_before_purchase"] = int(
        (delivered.notna() & purchase.notna() & (delivered < purchase)).sum()
    )

    order_items = data["order_items"]

    results["negative_price"] = int(
        (order_items["price"] < 0).sum()
    )

    results["negative_freight"] = int(
        (order_items["freight_value"] < 0).sum()
    )

    return results


def generate_quality_report(data):
    report = []

    report.append("OLIST DATA QUALITY REPORT")
    report.append("=" * 60)

    report.append("\nROW COUNTS")
    report.append("-" * 60)

    for name, df in data.items():
        report.append(f"{name}: {len(df):,}")

    report.append("\nREQUIRED FIELD NULLS")
    report.append("-" * 60)

    required_fields = {
        "customers": ["customer_id", "customer_unique_id"],
        "orders": ["order_id", "customer_id"],
        "order_items": ["order_id", "order_item_id", "product_id", "seller_id"],
        "products": ["product_id"],
        "sellers": ["seller_id"],
    }

    for table, columns in required_fields.items():
        results = check_required_nulls(data[table], columns)

        for column, count in results.items():
            report.append(f"{table}.{column}: {count:,}")

    report.append("\nDUPLICATE KEYS")
    report.append("-" * 60)

    primary_keys = {
        "customers": "customer_id",
        "orders": "order_id",
        "products": "product_id",
        "sellers": "seller_id",
    }

    for table, key in primary_keys.items():
        count = check_duplicate_keys(data[table], key)
        report.append(f"{table}.{key}: {count:,}")

    report.append("\nORPHAN FOREIGN KEYS")
    report.append("-" * 60)

    relationships = [
        ("orders", "customer_id", "customers", "customer_id"),
        ("order_items", "order_id", "orders", "order_id"),
        ("order_items", "product_id", "products", "product_id"),
        ("order_items", "seller_id", "sellers", "seller_id"),
    ]

    for child_table, child_key, parent_table, parent_key in relationships:
        count = check_orphan_keys(
            data[child_table],
            child_key,
            data[parent_table],
            parent_key
        )

        report.append(
            f"{child_table}.{child_key} -> "
            f"{parent_table}.{parent_key}: {count:,}"
        )

    report.append("\nINVALID BUSINESS VALUES")
    report.append("-" * 60)

    invalid = check_invalid_values(data)

    for name, count in invalid.items():
        report.append(f"{name}: {count:,}")

    output_path = PROCESSED_DIR / "quality_report.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text("\n".join(report), encoding="utf-8")

    return "\n".join(report)


if __name__ == "__main__":
    from src.ingest import load_data

    data = load_data()

    report = generate_quality_report(data)

    print(report)
    print(f"\nSaved to {PROCESSED_DIR / 'quality_report.txt'}")