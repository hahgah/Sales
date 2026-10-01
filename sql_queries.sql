-- Queries used in the dashboard (SQLite / MySQL compatible, table: orders)
-- 1. Sales and profit by category
SELECT category, ROUND(SUM(sales),2) AS total_sales, ROUND(SUM(profit),2) AS total_profit
FROM orders GROUP BY category ORDER BY total_sales DESC;

-- 2. Top 10 sub-categories by sales
SELECT sub_category, ROUND(SUM(sales),2) AS total_sales, ROUND(SUM(profit),2) AS total_profit
FROM orders GROUP BY sub_category ORDER BY total_sales DESC LIMIT 10;

-- 3. Monthly sales trend
SELECT strftime('%Y-%m', order_date) AS month, ROUND(SUM(sales),2) AS total_sales
FROM orders GROUP BY month ORDER BY month;

-- 4. Regions ranked by profit margin
SELECT region, ROUND(SUM(profit)*100.0/SUM(sales),1) AS margin_pct
FROM orders GROUP BY region ORDER BY margin_pct DESC;

-- 5. Top 10 customers by sales (JOIN-style aggregation on a customer summary)
SELECT c.customer_name, c.total_sales FROM (
  SELECT customer_name, ROUND(SUM(sales),2) AS total_sales FROM orders GROUP BY customer_name) c
ORDER BY c.total_sales DESC LIMIT 10;
