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
    """Generate synthetic inventory data for the dashboard."""
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
        sales = np.random.randint(0, min(stock_level + 1, 100))  # More realistic sales
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

# Generate data
df_inventory = generate_inventory_data()

#%% 3. Sidebar filters
st.sidebar.markdown("## 🛠 Filter Options")

# Region filter
regions = df_inventory['region'].unique()
selected_regions = st.sidebar.multiselect("Select Region(s):", regions, default=regions)

# Category filter
categories = df_inventory['category'].unique()
selected_category = st.sidebar.selectbox("Select Category:", np.append(['All'], categories))

# Date range filter
min_date = df_inventory['date'].min()
max_date = df_inventory['date'].max()
date_range = st.sidebar.date_input(
    "Select Date Range:", 
    [min_date, max_date], 
    min_value=min_date, 
    max_value=max_date
)

# Handle single date selection
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

show_data = st.sidebar.checkbox("🔎 Show Raw Data")

#%% 4. Apply filters
filtered_df = df_inventory[
    (df_inventory['region'].isin(selected_regions)) &
    (df_inventory['date'] >= pd.Timestamp(start_date)) &
    (df_inventory['date'] <= pd.Timestamp(end_date))
]

if selected_category != 'All':
    filtered_df = filtered_df[filtered_df['category'] == selected_category]

#%% 5. App Header
st.title("📦 Retail Inventory Dashboard")
st.markdown("""
Welcome to the interactive Retail Inventory Dashboard.  
Explore sales, stock levels, and revenue trends with dynamic filters and interactive visualizations.
""")

#%% 6. Calculate KPIs
total_sales = filtered_df['sales'].sum()
total_revenue = filtered_df['revenue'].sum()
average_discount = filtered_df['discount'].mean()
total_stock = filtered_df['stock_level'].sum()

# Simulate previous values for delta calculation
previous_sales = max(0, total_sales - np.random.randint(100, 1000))
previous_revenue = max(0, total_revenue - np.random.randint(1000, 10000))
previous_discount = max(0, average_discount - np.random.uniform(-0.05, 0.05))

# Calculate deltas
sales_delta = total_sales - previous_sales
revenue_delta = total_revenue - previous_revenue
discount_delta = average_discount - previous_discount

#%% 7. KPIs Display
st.markdown("### 📈 Key Performance Indicators")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        "🛒 Total Sales", 
        f"{total_sales:,}", 
        delta=f"{sales_delta:,}"
    )

with kpi2:
    st.metric(
        "💰 Total Revenue", 
        f"${total_revenue:,.2f}", 
        delta=f"${revenue_delta:,.2f}"
    )

with kpi3:
    st.metric(
        "🏷 Avg Discount", 
        f"{average_discount*100:.1f}%", 
        delta=f"{discount_delta*100:.1f}%"
    )

with kpi4:
    st.metric(
        "📦 Total Stock", 
        f"{total_stock:,}"
    )

#%% 8. Show raw data + download
if show_data:
    st.markdown("---")
    st.markdown("### 📄 Raw Filtered Data")
    st.dataframe(filtered_df, use_container_width=True)
    
    # Download button
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name='filtered_inventory_data.csv',
        mime='text/csv'
    )

#%% 9. Visualizations
st.markdown("---")
st.header("📊 Interactive Visualizations")

# Create two columns for better layout
col1, col2 = st.columns(2)

#%% 10. Plot 1: Total Sales by Category
with col1:
    st.subheader("🗂 Total Sales by Category")
    if not filtered_df.empty:
        category_sales = filtered_df.groupby('category')['sales'].sum().reset_index()
        fig1 = px.bar(
            category_sales,
            x='category',
            y='sales',
            color='category',
            title='Total Sales by Category',
            labels={'sales': 'Total Sales', 'category': 'Category'},
            template="plotly_white"
        )
        fig1.update_layout(showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")

#%% 11. Plot 2: Stock Distribution by Region
with col2:
    st.subheader("🌍 Stock Distribution by Region")
    if not filtered_df.empty:
        region_stock = filtered_df.groupby('region')['stock_level'].sum().reset_index()
        fig2 = px.pie(
            region_stock,
            names='region',
            values='stock_level',
            title='Stock Distribution by Region',
            hole=0.4,
            template="plotly_white"
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")

#%% 12. Plot 3: Sales Distribution Histogram
st.subheader("📦 Sales Transaction Amount Distribution")
if not filtered_df.empty:
    fig3 = px.histogram(
        filtered_df,
        x='sales',
        nbins=30,
        title='Sales Units Distribution',
        labels={'sales': 'Units Sold', 'count': 'Frequency'},
        template="plotly_white"
    )
    fig3.update_traces(marker_color='lightblue', opacity=0.7)
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("No data available for the selected filters.")

#%% 13. Plot 4: Revenue Sunburst
col3, col4 = st.columns(2)

with col3:
    st.subheader("🌞 Revenue by Category and Region")
    if not filtered_df.empty:
        sunburst_data = filtered_df.groupby(['category','region']).agg({'revenue':'sum'}).reset_index()
        sunburst_data = sunburst_data[sunburst_data['revenue'] > 0]  # Filter out zero revenue
        
        if not sunburst_data.empty:
            fig4 = px.sunburst(
                sunburst_data,
                path=['category', 'region'],
                values='revenue',
                title='Revenue by Category and Region',
                template="plotly_white"
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.warning("No revenue data available for the selected filters.")
    else:
        st.warning("No data available for the selected filters.")

#%% 14. Plot 5: Monthly Revenue Trend
with col4:
    st.subheader("📈 Monthly Revenue Trend")
    if not filtered_df.empty:
        monthly_revenue = filtered_df.groupby('month')['revenue'].sum().reset_index()
        monthly_revenue = monthly_revenue.sort_values('month')
        
        fig5 = px.line(
            monthly_revenue,
            x='month',
            y='revenue',
            markers=True,
            title='Monthly Revenue Trend',
            labels={'month': 'Month', 'revenue': 'Total Revenue'},
            template="plotly_white"
        )
        fig5.update_traces(line_color='mediumseagreen', line_width=3)
        fig5.update_layout(xaxis_title="Month", yaxis_title="Revenue ($)")
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")

#%% 15. Additional Analytics
st.markdown("---")
st.header("🔍 Additional Analytics")

col5, col6 = st.columns(2)

with col5:
    st.subheader("💡 Top Performing Categories")
    if not filtered_df.empty:
        top_categories = filtered_df.groupby('category').agg({
            'revenue': 'sum',
            'sales': 'sum'
        }).sort_values('revenue', ascending=False)
        
        st.dataframe(
            top_categories.style.format({
                'revenue': '${:,.2f}',
                'sales': '{:,}'
            }),
            use_container_width=True
        )

with col6:
    st.subheader("🌟 Regional Performance")
    if not filtered_df.empty:
        regional_performance = filtered_df.groupby('region').agg({
            'revenue': 'sum',
            'sales': 'sum',
            'stock_level': 'sum'
        }).sort_values('revenue', ascending=False)
        
        st.dataframe(
            regional_performance.style.format({
                'revenue': '${:,.2f}',
                'sales': '{:,}',
                'stock_level': '{:,}'
            }),
            use_container_width=True
        )

#%% 16. Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and Plotly")
st.markdown("Data shown is synthetically generated for demonstration purposes.")
