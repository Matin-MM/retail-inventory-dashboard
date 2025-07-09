#%% 0. Imports
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime, timedelta
from io import BytesIO

#%% 1. Data generation
@st.cache_data
def generate_inventory_data(n=5000):
    start = datetime(2024, 1, 1)
    categories = ['Electronics','Clothing','Furniture','Toys','Groceries']
    regions = ['North','South','East','West']
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

# Load data
df_inventory = generate_inventory_data()

#%% 2. App header
st.title("Retail Inventory Dashboard")
st.markdown("""
This interactive dashboard visualizes synthetic retail inventory data with filtering options.  
Use the sidebar to filter by region, category, and date range.
""")

#%% 3. Sidebar filters (Functionality 1, 2, 3)
st.sidebar.header("Filter Options")

regions = df_inventory['region'].unique()
selected_regions = st.sidebar.multiselect("Select Region(s):", regions, default=regions)

categories = df_inventory['category'].unique()
selected_category = st.sidebar.selectbox("Select Category:", np.append(['All'], categories))

min_date = df_inventory['date'].min()
max_date = df_inventory['date'].max()
date_range = st.sidebar.date_input("Select Date Range:", [min_date, max_date], min_value=min_date, max_value=max_date)

show_data = st.sidebar.checkbox("Show Raw Data", False)  # Functionality 4

#%% 4. Apply filters
filtered_df = df_inventory[
    (df_inventory['region'].isin(selected_regions)) &
    (df_inventory['date'] >= pd.Timestamp(date_range[0])) &
    (df_inventory['date'] <= pd.Timestamp(date_range[1]))
]
if selected_category != 'All':
    filtered_df = filtered_df[filtered_df['category'] == selected_category]

#%% 5. KPIs
total_sales = filtered_df['sales'].sum()
total_revenue = filtered_df['revenue'].sum()
average_discount = filtered_df['discount'].mean()

st.subheader("📈 Key Performance Indicators")
col1, col2, col3 = st.columns(3)
col1.metric("🛒 Total Sales", f"{total_sales:,}")
col2.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
col3.metric("🏷️ Avg Discount", f"{average_discount*100:.2f}%")

#%% 6. Show raw data
if show_data:
    st.subheader("🔎 Raw Filtered Data")
    st.dataframe(filtered_df)

    # Download button
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name='filtered_inventory_data.csv',
        mime='text/csv'
    )

#%% 7. Plots

st.header("📊 Visualizations")

# Plot 1: Total Sales by Category
st.subheader("Total Sales by Category")
category_sales = filtered_df.groupby('category')['sales'].sum().sort_values()
fig1, ax1 = plt.subplots(figsize=(8,4))
ax1.bar(category_sales.index, category_sales.values, color='cornflowerblue')
ax1.set_title('Total Sales by Category')
ax1.set_xlabel('Category')
ax1.set_ylabel('Sales')
st.pyplot(fig1)

# Plot 2: Stock Distribution by Region
st.subheader("Stock Distribution by Region")
region_stock = filtered_df.groupby('region')['stock_level'].sum().reset_index()
fig2 = px.pie(region_stock, names='region', values='stock_level', title='Stock Distribution by Region')
st.plotly_chart(fig2)

# Plot 3: Histogram of Transaction Amount
st.subheader("Transaction Amount Distribution")
fig3, ax3 = plt.subplots(figsize=(8,4))
ax3.hist(filtered_df['sales'], bins=50, color='skyblue')
ax3.set_title('Transaction Amount Distribution')
ax3.set_xlabel('Amount')
ax3.set_ylabel('Frequency')
st.pyplot(fig3)

# Plot 4: Revenue by Category and Region
st.subheader("Revenue by Category and Region")
sunburst_data = filtered_df.groupby(['category','region']).agg({'revenue':'sum'}).reset_index()
fig4 = px.sunburst(sunburst_data, path=['category', 'region'], values='revenue', title='Revenue by Category and Region')
st.plotly_chart(fig4)

# Plot 5: Monthly Revenue Trend
st.subheader("Monthly Revenue Trend")
monthly_revenue = filtered_df.groupby('month')['revenue'].sum().reset_index()
fig5 = px.line(monthly_revenue, x='month', y='revenue', title='Monthly Revenue Trend')
fig5.update_layout(xaxis_title='Month', yaxis_title='Total Revenue ($)')
st.plotly_chart(fig5)
