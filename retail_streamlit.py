#%% 0. Imports
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import random

#%% 1. Page config
st.set_page_config(
    page_title="Retail Inventory Dashboard",
    layout="wide",
    page_icon="📦",
)

#%% 2. Data generation
@st.cache_data
def generate_inventory_data(n=5000):
    start = datetime(2024, 1, 1)
    categories = ['Electronics', 'Clothing', 'Furniture', 'Toys', 'Groceries']
    regions = ['North', 'South', 'East', 'West']
    records = []
    for i in range(n):
        product_id = i + 1
        category = np.random.choice(categories)
        region = np.random.choice(regions)
        date = start + timedelta(days=np.random.randint(0, 180))
        stock_level = np.random.randint(0, 500)
        sales = np.random.randint(0, stock_level + 1)
        price = np.random.uniform(10, 1000)
        cost = price * np.random.uniform(0.4, 0.6)
        revenue = sales * (price - cost)
        discount = np.random.uniform(0, 0.3)
        records.append({
            'product_id': product_id,
            'category': category,
            'region': region,
            'date': date,
            'stock_level': stock_level,
            'sales': sales,
            'price': price,
            'cost': cost,
            'revenue': revenue,
            'discount': discount
        })
    df = pd.DataFrame(records)
    df['month'] = df['date'].dt.to_period('M').astype(str)
    return df

df_inventory = generate_inventory_data()

#%% 3. Sidebar filters
st.sidebar.markdown("## 🛠️ Filter Options")
regions = df_inventory['region'].unique()
selected_regions = st.sidebar.multiselect("Select Region(s):", regions, default=regions)

categories = df_inventory['category'].unique()
selected_category = st.sidebar.selectbox("Select Category:", np.append(['All'], categories))

min_date = df_inventory['date'].min()
max_date = df_inventory['date'].max()
date_range = st.sidebar.date_input("Select Date Range:", [min_date, max_date], min_value=min_date, max_value=max_date)

show_data = st.sidebar.checkbox("🔎 Show Raw Data")

#%% 4. Apply filters
filtered_df = df_inventory[
    (df_inventory['region'].isin(selected_regions)) & 
    (df_inventory['date'] >= pd.Timestamp(date_range[0])) & 
    (df_inventory['date'] <= pd.Timestamp(date_range[1]))
]
if selected_category != 'All':
    filtered_df = filtered_df[filtered_df['category'] == selected_category]

#%% 5. App Header with Dynamic Colors
st.title("📦 Retail Inventory Dashboard")

# Function to generate random colors
def random_color():
    return f"#{random.randint(0, 0xFFFFFF):06x}"

# Dynamic background color for header
header_color = random_color()
st.markdown(f"<div style='background-color:{header_color}; padding:10px; text-align:center; color:white;'>Welcome to the interactive **Retail Inventory Dashboard**</div>", unsafe_allow_html=True)

#%% 6. KPIs
total_sales = filtered_df['sales'].sum()
total_revenue = filtered_df['revenue'].sum()
average_discount = filtered_df['discount'].mean()

st.markdown(f"### 📈 Key Performance Indicators", unsafe_allow_html=True)
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("🛒 Total Sales", f"{total_sales:,}")
kpi2.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
kpi3.metric("🏷️ Avg Discount", f"{average_discount*100:.2f}%")

#%% 7. Show raw data + download
if show_data:
    st.markdown("---")
    st.subheader("📄 Raw Filtered Data")
    st.dataframe(filtered_df)
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name='filtered_inventory_data.csv',
        mime='text/csv'
    )

st.markdown("---")
st.header("📊 Interactive Visualizations")

#%% 8. Plot 1: Total Sales by Category
st.subheader("🗂️ Total Sales by Category")
category_sales = filtered_df.groupby('category')['sales'].sum().reset_index()
fig1 = px.bar(
    category_sales,
    x='category',
    y='sales',
    color='category',
    title='Total Sales by Category',
    labels={'sales': 'Total Sales', 'category': 'Category'}
)
st.plotly_chart(fig1, use_container_width=True)

#%% 9. Plot 2: Stock Distribution by Region
st.subheader("🌍 Stock Distribution by Region")
region_stock = filtered_df.groupby('region')['stock_level'].sum().reset_index()
fig2 = px.pie(
    region_stock,
    names='region',
    values='stock_level',
    title='Stock Distribution by Region',
    hole=0.4
)
st.plotly_chart(fig2, use_container_width=True)

#%% 10. Plot 3: Sales Distribution Histogram
st.subheader("📦 Sales Transaction Amount Distribution")
fig3 = px.histogram(
    filtered_df,
    x='sales',
    nbins=50,
    title='Transaction Amount Distribution',
    labels={'sales': 'Units Sold'}
)
fig3.update_traces(marker_color='lightskyblue')
st.plotly_chart(fig3, use_container_width=True)

#%% 11. Plot 4: Revenue Sunburst
st.subheader("🌞 Revenue by Category and Region")
sunburst_data = filtered_df.groupby(['category', 'region']).agg({'revenue': 'sum'}).reset_index()
fig4 = px.sunburst(
    sunburst_data,
    path=['category', 'region'],
    values='revenue',
    title='Revenue by Category and Region'
)
st.plotly_chart(fig4, use_container_width=True)

#%% 12. Plot 5: Monthly Revenue Trend
st.subheader("📈 Monthly Revenue Trend")
monthly_revenue = filtered_df.groupby('month')['revenue'].sum().reset_index()
fig5 = px.line(
    monthly_revenue,
    x='month',
    y='revenue',
    markers=True,
    title='Monthly Revenue Trend',
    labels={'month': 'Month', 'revenue': 'Total Revenue'}
)
fig5.update_traces(line_color='mediumseagreen')
st.plotly_chart(fig5, use_container_width=True)

#%% 13. Footer with Dynamic Color
st.markdown(f"---\n<span style='color:{random_color()}'>Built with ❤️ using Streamlit and Plotly</span>", unsafe_allow_html=True)
