from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")


def load_csv(filename):
    path = RAW_DIR / filename
    return pd.read_csv(path)


def load_data():
    data = {
        "customers": load_csv("olist_customers_dataset.csv"),
        "geolocation": load_csv("olist_geolocation_dataset.csv"),
        "order_items": load_csv("olist_order_items_dataset.csv"),
        "order_payments": load_csv("olist_order_payments_dataset.csv"),
        "order_reviews": load_csv("olist_order_reviews_dataset.csv"),
        "orders": load_csv("olist_orders_dataset.csv"),
        "products": load_csv("olist_products_dataset.csv"),
        "sellers": load_csv("olist_sellers_dataset.csv"),
        "category_translation": load_csv(
            "product_category_name_translation.csv"
        ),
    }

    return data


def save_products_as_json(products):
    output_path = RAW_DIR / "products.json"
    products.to_json(output_path, orient="records", indent=2)
    return output_path


if __name__ == "__main__":
    data = load_data()

    for name, df in data.items():
        print(f"{name}: {df.shape}")

    save_products_as_json(data["products"])

    print("\nProducts converted to JSON.")