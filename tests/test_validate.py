import pandas as pd

from src.validate import (
    check_required_nulls,
    check_duplicate_keys,
    check_orphan_keys,
    check_invalid_values,
)


def test_required_nulls():
    df = pd.DataFrame({
        "id": [1, 2, None]
    })

    result = check_required_nulls(df, ["id"])

    assert result["id"] == 1


def test_duplicate_keys():
    df = pd.DataFrame({
        "id": [1, 2, 2, 3]
    })

    assert check_duplicate_keys(df, "id") == 1


def test_orphan_keys():
    child = pd.DataFrame({
        "customer_id": [1, 2, 5]
    })

    parent = pd.DataFrame({
        "customer_id": [1, 2, 3]
    })

    assert check_orphan_keys(
        child,
        "customer_id",
        parent,
        "customer_id"
    ) == 1


def test_negative_price():
    data = {
        "orders": pd.DataFrame({
            "order_purchase_timestamp": ["2020-01-01"],
            "order_delivered_customer_date": ["2020-01-02"]
        }),
        "order_items": pd.DataFrame({
            "price": [10, -5],
            "freight_value": [2, 3]
        })
    }

    result = check_invalid_values(data)

    assert result["negative_price"] == 1


def test_delivery_before_purchase():
    data = {
        "orders": pd.DataFrame({
            "order_purchase_timestamp": [
                "2020-01-02",
                "2020-01-05"
            ],
            "order_delivered_customer_date": [
                "2020-01-01",
                "2020-01-06"
            ]
        }),
        "order_items": pd.DataFrame({
            "price": [10],
            "freight_value": [2]
        })
    }

    result = check_invalid_values(data)

    assert result["delivery_before_purchase"] == 1