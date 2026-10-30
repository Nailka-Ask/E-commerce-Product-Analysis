-- 1. Monthly revenue and number of orders
SELECT date_trunc('month', order_date)::date AS month,
       SUM(revenue) AS revenue,
       COUNT(DISTINCT order_id) AS orders_count
FROM orders
WHERE status = 'completed'
GROUP BY 1
ORDER BY 1;

-- 2. Revenue by product category
SELECT p.category,
       SUM(o.revenue) AS revenue,
       SUM(o.quantity) AS units_sold
FROM orders o
JOIN products p USING (product_id)
WHERE o.status = 'completed'
GROUP BY p.category
ORDER BY revenue DESC;

-- 3. Average order value (AOV)
WITH order_totals AS (
    SELECT order_id, SUM(revenue) AS order_revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY order_id
)
SELECT AVG(order_revenue) AS average_order_value
FROM order_totals;

-- 4. Repeat purchase rate
WITH customer_orders AS (
    SELECT customer_id, COUNT(DISTINCT order_id) AS orders_count
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
)
SELECT COUNT(*) FILTER (WHERE orders_count > 1)::numeric
       / NULLIF(COUNT(*), 0) AS repeat_customer_share
FROM customer_orders;

-- 5. Revenue and customers by acquisition channel
SELECT c.acquisition_channel,
       COUNT(DISTINCT c.customer_id) AS customers,
       COALESCE(SUM(o.revenue), 0) AS revenue,
       COALESCE(SUM(o.revenue), 0) / NULLIF(COUNT(DISTINCT c.customer_id), 0) AS revenue_per_customer
FROM customers c
LEFT JOIN orders o
       ON c.customer_id = o.customer_id
      AND o.status = 'completed'
GROUP BY c.acquisition_channel
ORDER BY revenue_per_customer DESC NULLS LAST;

-- 6. Customer-level order sequence using a window function
SELECT order_id, customer_id, order_date, revenue,
       ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS order_number,
       LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS previous_order_date
FROM orders
WHERE status = 'completed'
ORDER BY customer_id, order_date;
