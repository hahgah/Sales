import sqlite3, pandas as pd, plotly.express as px, streamlit as st

st.set_page_config(page_title="Sales Dashboard", page_icon="📈", layout="wide")
st.title("📈 Sales Data Analysis & Dashboard")
st.caption("Data analysis project · SQL, Python (Pandas), Plotly · Superstore sales data")

@st.cache_data
def load():
    d = pd.read_csv("data/superstore.csv", encoding="latin1")
    d.columns = [c.strip().lower().replace(" ", "_").replace("-", "_") for c in d.columns]
    d["order_date"] = pd.to_datetime(d["order_date"], format="mixed")
    d = d.dropna(subset=["order_id", "sales"])   # data cleaning: file has ~800 empty rows
    return d.drop_duplicates()
df = load()

# Load into an in-memory SQL database so the analysis runs on real SQL
con = sqlite3.connect(":memory:", check_same_thread=False)
df.assign(order_date=df.order_date.dt.strftime("%Y-%m-%d")).to_sql("orders", con, index=False)
q = lambda sql: pd.read_sql(sql, con)

st.sidebar.header("Filters")
years = sorted(df.order_date.dt.year.unique())
yr = st.sidebar.multiselect("Year", years, default=years)
reg = st.sidebar.multiselect("Region", sorted(df.region.unique()), default=sorted(df.region.unique()))
f = df[df.order_date.dt.year.isin(yr) & df.region.isin(reg)]

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total sales", f"${f.sales.sum():,.0f}"); k2.metric("Total profit", f"${f.profit.sum():,.0f}")
k3.metric("Profit margin", f"{f.profit.sum() / f.sales.sum():.1%}"); k4.metric("Orders", f"{f.order_id.nunique():,}")

tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🧮 SQL analysis", "💡 Insights"])
with tab1:
    m = f.set_index("order_date").resample("MS").sales.sum().reset_index()
    st.plotly_chart(px.line(m, x="order_date", y="sales", title="Monthly sales trend"), width="stretch")
    a, b = st.columns(2)
    sub = f.groupby("sub_category")[["sales", "profit"]].sum().sort_values("sales").tail(10).reset_index()
    a.plotly_chart(px.bar(sub, x="sales", y="sub_category", orientation="h", title="Top 10 sub-categories by sales"), width="stretch")
    r = f.groupby("region")[["sales", "profit"]].sum().reset_index()
    b.plotly_chart(px.bar(r, x="region", y="profit", color="profit", title="Profit by region"), width="stretch")
    st.plotly_chart(px.scatter(f.sample(min(2000, len(f)), random_state=1), x="discount", y="profit", color="category",
                               title="Discount vs profit (sample)"), width="stretch")

with tab2:
    st.write("Queries run against the `orders` table (also in `sql_queries.sql`).")
    for title, sql in {
        "Sales & profit by category": "SELECT category, ROUND(SUM(sales),2) AS total_sales, ROUND(SUM(profit),2) AS total_profit FROM orders GROUP BY category ORDER BY total_sales DESC",
        "Regions ranked by profit margin (%)": "SELECT region, ROUND(SUM(profit)*100.0/SUM(sales),1) AS margin_pct FROM orders GROUP BY region ORDER BY margin_pct DESC",
        "Top 10 customers by sales": "SELECT customer_name, ROUND(SUM(sales),2) AS total_sales FROM orders GROUP BY customer_name ORDER BY total_sales DESC LIMIT 10"}.items():
        st.subheader(title); st.code(sql, language="sql"); st.dataframe(q(sql), width="stretch", hide_index=True)

with tab3:
    d = df.copy(); hi = d[d.discount >= .3]
    st.markdown(f"""
- Orders with **30%+ discount** average a profit of **${hi.profit.mean():,.2f}** vs **${d[d.discount < .3].profit.mean():,.2f}** for the rest: deep discounts hurt profit.
- The most profitable category is **{d.groupby('category').profit.sum().idxmax()}**; the highest-margin region is **{(d.groupby('region').profit.sum() / d.groupby('region').sales.sum()).idxmax()}**.
- Sales peak in Q4 each year, so stock and marketing should be planned ahead of November.
""")
