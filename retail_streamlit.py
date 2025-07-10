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
st.markdown("""
Welcome to the **interactive Retail Inventory Dashboard**.  
Explore sales, stock levels, and revenue trends with dynamic filters and interactive visualizations.
""")

#%% 6. Dynamic Titles and Headers Colors
# Random color generator function for dynamic header background and titles
def random_color():
    return f"#{random.randint(0, 0xFFFFFF):06x}"

header_color = random_color()
subheader_color = random_color()

#%% 7. KPIs with Delta and Dynamic Colors (fixed for delta_color)
# Calculate the current total values first
total_sales = filtered_df['sales'].sum()
total_revenue = filtered_df['revenue'].sum()
average_discount = filtered_df['discount'].mean()

# Simulate previous values for the delta calculation
previous_sales = total_sales - 1000  # Example: previous value is 1000 less
previous_revenue = total_revenue - 5000  # Example: previous value is 5000 less
previous_discount = average_discount - 0.01  # Example: previous value is 1% less

# Predefined list of colors for delta_color
color_list = ['green', 'red', 'blue', 'orange', 'purple', 'yellow']

# Function to randomly pick a color from the list for delta_color
def random_kpi_color():
    return random.choice(color_list)

# Calculate deltas (change from previous value)
sales_delta = total_sales - previous_sales
revenue_delta = total_revenue - previous_revenue
discount_delta = average_discount - previous_discount

# Determine the delta color based on whether the value increased or decreased
def get_delta_color(delta):
    # Ensure only valid color strings are returned
    if delta > 0:
        return 'green'
    else:
        return 'red'

# Display the KPIs with their respective delta and delta_color
st.markdown(f"### <span style='color:{header_color}'>📈 Key Performance Indicators</span>", unsafe_allow_html=True)

kpi1, kpi2, kpi3 = st.columns(3)

# Total Sales KPI with delta color
kpi1.metric(
    "🛒 Total Sales", 
    f"{total_sales:,}", 
    delta=f"{sales_delta:,}", 
    delta_color=get_delta_color(sales_delta)  # Ensure delta_color is either 'green' or 'red'
)

# Total Revenue KPI with delta color
kpi2.metric(
    "💰 Total Revenue", 
    f"${total_revenue:,.2f}", 
    delta=f"${revenue_delta:,.2f}", 
    delta_color=get_delta_color(revenue_delta)  # Ensure delta_color is either 'green' or 'red'
)

# Avg Discount KPI with delta color
kpi3.metric(
    "🏷️ Avg Discount", 
    f"{average_discount*100:.2f}%", 
    delta=f"{discount_delta*100:.2f}%", 
    delta_color=get_delta_color(discount_delta)  # Ensure delta_color is either 'green' or 'red'
)



#%% 8. Show raw data + download
if show_data:
    st.markdown(f"---\n### <span style='color:{subheader_color}'>📄 Raw Filtered Data</span>", unsafe_allow_html=True)
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

#%% 9. Plot 1: Total Sales by Category
st.subheader(f"🗂️ <span style='color:{random_color()}'>Total Sales by Category</span>", unsafe_allow_html=True)
category_sales = filtered_df.groupby('category')['sales'].sum().reset_index()
fig1 = px.bar(
    category_sales,
    x='category',
    y='sales',
    color='category',
    title='Total Sales by Category',
    labels={'sales': 'Total Sales', 'category': 'Category'},
    template="plotly"
)
st.plotly_chart(fig1, use_container_width=True)

#%% 10. Plot 2: Stock Distribution by Region
st.subheader(f"🌍 <span style='color:{random_color()}'>Stock Distribution by Region</span>", unsafe_allow_html=True)
region_stock = filtered_df.groupby('region')['stock_level'].sum().reset_index()
fig2 = px.pie(
    region_stock,
    names='region',
    values='stock_level',
    title='Stock Distribution by Region',
    hole=0.4,
    template="plotly"
)
st.plotly_chart(fig2, use_container_width=True)

#%% 11. Plot 3: Sales Distribution Histogram
st.subheader(f"📦 <span style='color:{random_color()}'>Sales Transaction Amount Distribution</span>", unsafe_allow_html=True)
fig3 = px.histogram(
    filtered_df,
    x='sales',
    nbins=50,
    title='Transaction Amount Distribution',
    labels={'sales': 'Units Sold'},
    template="plotly"
)
fig3.update_traces(marker_color='lightskyblue')
st.plotly_chart(fig3, use_container_width=True)

#%% 12. Plot 4: Revenue Sunburst
st.subheader(f"🌞 <span style='color:{random_color()}'>Revenue by Category and Region</span>", unsafe_allow_html=True)
sunburst_data = filtered_df.groupby(['category','region']).agg({'revenue':'sum'}).reset_index()
fig4 = px.sunburst(
    sunburst_data,
    path=['category', 'region'],
    values='revenue',
    title='Revenue by Category and Region',
    template="plotly"
)
st.plotly_chart(fig4, use_container_width=True)

#%% 13. Plot 5: Monthly Revenue Trend
st.subheader(f"📈 <span style='color:{random_color()}'>Monthly Revenue Trend</span>", unsafe_allow_html=True)
monthly_revenue = filtered_df.groupby('month')['revenue'].sum().reset_index()
fig5 = px.line(
    monthly_revenue,
    x='month',
    y='revenue',
    markers=True,
    title='Monthly Revenue Trend',
    labels={'month': 'Month', 'revenue': 'Total Revenue'},
    template="plotly"
)
fig5.update_traces(line_color='mediumseagreen')
st.plotly_chart(fig5, use_container_width=True)

#%% 14. Footer with Dynamic Color
st.markdown(f"---\n<span style='color:{random_color()}'>Built with ❤️ using Streamlit and Plotly</span>", unsafe_allow_html=True)

