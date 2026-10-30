from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

customers = pd.read_csv(DATA / "customers.csv", parse_dates=["signup_date"])
products = pd.read_csv(DATA / "products.csv")
orders = pd.read_csv(DATA / "orders.csv", parse_dates=["order_date"])
orders = orders.loc[orders["status"].eq("completed")].copy()
orders["revenue"] = orders["quantity"] * orders["unit_price"]
orders = orders.merge(products[["product_id", "product_name", "category"]], on="product_id", how="left")
orders = orders.merge(customers[["customer_id", "acquisition_channel", "region"]], on="customer_id", how="left")

if orders.empty:
    raise SystemExit("Нет заказов для анализа.")

monthly = orders.assign(month=orders["order_date"].dt.to_period("M").dt.to_timestamp()).groupby("month", as_index=False).agg(
    revenue=("revenue", "sum"),
    orders=("order_id", "nunique")
)
order_totals = orders.groupby("order_id", as_index=False)["revenue"].sum()
customer_orders = orders.groupby("customer_id")["order_id"].nunique()
repeat_share = (customer_orders > 1).mean()
aov = order_totals["revenue"].mean()
category_revenue = orders.groupby("category")["revenue"].sum().sort_values(ascending=False)
channel_revenue = orders.groupby("acquisition_channel").agg(
    revenue=("revenue", "sum"),
    ordering_customers=("customer_id", "nunique")
).sort_values("revenue", ascending=False)

monthly.to_csv(REPORTS / "monthly_revenue.csv", index=False)
category_revenue.rename("revenue").to_csv(REPORTS / "revenue_by_category.csv")
channel_revenue.to_csv(REPORTS / "revenue_by_channel.csv")

plt.figure(figsize=(9, 5))
plt.plot(monthly["month"], monthly["revenue"], marker="o")
plt.title("Monthly revenue (synthetic data)")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(REPORTS / "monthly_revenue.png", dpi=150)
plt.close()

plt.figure(figsize=(8, 5))
category_revenue.sort_values().plot(kind="barh")
plt.title("Revenue by category (synthetic data)")
plt.xlabel("Revenue")
plt.tight_layout()
plt.savefig(REPORTS / "revenue_by_category.png", dpi=150)
plt.close()

print("=== E-commerce analysis ===")
print(f"Completed orders: {orders['order_id'].nunique():,}")
print(f"Revenue: {orders['revenue'].sum():,.0f}")
print(f"Average order value: {aov:,.2f}")
print(f"Repeat-customer share among customers with at least one order: {repeat_share:.1%}")
print("\nRevenue by category:")
print(category_revenue.to_string())
print("\nRevenue by acquisition channel:")
print(channel_revenue.to_string())
print(f"\nCharts and CSV summaries saved to: {REPORTS}")
