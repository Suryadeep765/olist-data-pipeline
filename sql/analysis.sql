-- 1. Monthly revenue and average order value
WITH monthly_orders AS (
    SELECT
        DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
        COUNT(DISTINCT o.order_id) AS orders,
        SUM(oi.revenue) AS revenue
    FROM orders o
    JOIN order_items oi
        ON o.order_id = oi.order_id
    GROUP BY 1
)
SELECT
    month,
    orders,
    ROUND(revenue::numeric, 2) AS revenue,
    ROUND((revenue / NULLIF(orders, 0))::numeric, 2) AS average_order_value
FROM monthly_orders
ORDER BY month;


-- 2. Top product categories by revenue
SELECT
    p.product_category_name_english AS category,
    ROUND(SUM(oi.revenue)::numeric, 2) AS revenue
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
GROUP BY p.product_category_name_english
ORDER BY revenue DESC
LIMIT 10;


-- 3. Revenue by customer state
SELECT
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(oi.revenue)::numeric, 2) AS revenue
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
JOIN order_items oi
    ON o.order_id = oi.order_id
GROUP BY c.customer_state
ORDER BY revenue DESC;


-- 4. Delivery performance
SELECT
    COUNT(*) AS total_orders,
    SUM(CASE WHEN delay_flag THEN 1 ELSE 0 END) AS delayed_orders,
    ROUND(
        100.0 * SUM(CASE WHEN delay_flag THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0),
        2
    ) AS delayed_percentage,
    ROUND(AVG(delivery_days)::numeric, 2) AS average_delivery_days
FROM orders
WHERE delivery_days IS NOT NULL;


-- 5. Category revenue ranking using a window function
WITH category_revenue AS (
    SELECT
        p.product_category_name_english AS category,
        SUM(oi.revenue) AS revenue
    FROM order_items oi
    JOIN products p
        ON oi.product_id = p.product_id
    GROUP BY p.product_category_name_english
)
SELECT
    category,
    ROUND(revenue::numeric, 2) AS revenue,
    RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
FROM category_revenue
ORDER BY revenue_rank;