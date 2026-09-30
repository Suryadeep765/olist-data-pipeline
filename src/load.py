from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

PROCESSED_DIR = Path("data/processed")

load_dotenv()

DB_PASSWORD = os.getenv("DB_PASSWORD")

if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD not found in .env")


def get_engine():
    connection_url = URL.create(
        drivername="postgresql+psycopg2",
        username="postgres",
        password=DB_PASSWORD,
        host="localhost",
        port=5432,
        database="olist"
    )

    return create_engine(connection_url)


def create_tables(engine):
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id VARCHAR(50) PRIMARY KEY,
                customer_unique_id VARCHAR(50),
                customer_zip_code_prefix INTEGER,
                customer_city VARCHAR(100),
                customer_state VARCHAR(10)
            );

            CREATE TABLE IF NOT EXISTS sellers (
                seller_id VARCHAR(50) PRIMARY KEY,
                seller_zip_code_prefix INTEGER,
                seller_city VARCHAR(100),
                seller_state VARCHAR(10)
            );

            CREATE TABLE IF NOT EXISTS products (
                product_id VARCHAR(50) PRIMARY KEY,
                product_category_name VARCHAR(150),
                product_name_lenght INTEGER,
                product_description_lenght INTEGER,
                product_photos_qty INTEGER,
                product_weight_g NUMERIC,
                product_length_cm NUMERIC,
                product_height_cm NUMERIC,
                product_width_cm NUMERIC,
                product_category_name_english VARCHAR(150)
            );

            CREATE TABLE IF NOT EXISTS orders (
                order_id VARCHAR(50) PRIMARY KEY,
                customer_id VARCHAR(50),
                order_status VARCHAR(50),
                order_purchase_timestamp TIMESTAMP,
                order_approved_at TIMESTAMP,
                order_delivered_carrier_date TIMESTAMP,
                order_delivered_customer_date TIMESTAMP,
                order_estimated_delivery_date TIMESTAMP,
                delivery_days NUMERIC,
                delay_flag INTEGER,
                FOREIGN KEY (customer_id)
                    REFERENCES customers(customer_id)
            );

            CREATE TABLE IF NOT EXISTS order_items (
                order_id VARCHAR(50),
                order_item_id INTEGER,
                product_id VARCHAR(50),
                seller_id VARCHAR(50),
                shipping_limit_date TIMESTAMP,
                price NUMERIC,
                freight_value NUMERIC,
                revenue NUMERIC,
                PRIMARY KEY (order_id, order_item_id),
                FOREIGN KEY (order_id)
                    REFERENCES orders(order_id),
                FOREIGN KEY (product_id)
                    REFERENCES products(product_id),
                FOREIGN KEY (seller_id)
                    REFERENCES sellers(seller_id)
            );
        """))


def load_table(engine, filename, table_name):
    df = pd.read_csv(PROCESSED_DIR / filename)

    with engine.begin() as connection:
        connection.execute(
            text(f"TRUNCATE TABLE {table_name} CASCADE")
        )

    df.to_sql(
        table_name,
        engine,
        if_exists="append",
        index=False
    )

    print(f"Loaded {table_name}: {len(df):,} rows")


def load_data():
    engine = get_engine()

    print("Creating database tables...")
    create_tables(engine)

    print("Loading data...")

    load_table(engine, "customers.csv", "customers")
    load_table(engine, "sellers.csv", "sellers")
    load_table(engine, "products.csv", "products")
    load_table(engine, "orders.csv", "orders")
    load_table(engine, "order_items.csv", "order_items")

    print("Database loading completed.")


if __name__ == "__main__":
    load_data()