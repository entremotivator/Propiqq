#!/usr/bin/env python3.11

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io

# Page configuration
st.set_page_config(
    page_title="Tax Deed Properties Viewer",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for card styling
st.markdown("""
<style>
    .property-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
        transition: transform 0.2s;
    }
    
    .property-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    
    .card-header {
        font-size: 1.2em;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    
    .card-address {
        font-size: 1.1em;
        color: #333;
        margin-bottom: 8px;
    }
    
    .card-bid {
        font-size: 1.3em;
        font-weight: bold;
        color: #d62728;
        margin: 10px 0;
    }
    
    .card-details {
        font-size: 0.9em;
        color: #666;
        margin: 5px 0;
    }
    
    .status-available {
        background-color: #28a745;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    .status-sold {
        background-color: #dc3545;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    .status-pending {
        background-color: #ffc107;
        color: black;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    .filter-section {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 20px 0;
    }
    
    .stat-box {
        text-align: center;
        padding: 15px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .stat-number {
        font-size: 2em;
        font-weight: bold;
        color: #1f77b4;
    }
    
    .stat-label {
        font-size: 0.9em;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load the tax deed property data"""
    try:
        df = pd.read_csv('/home/ubuntu/tax_deed_properties.csv')
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please ensure tax_deed_properties.csv exists.")
        return pd.DataFrame()

def format_currency(amount):
    """Format currency values"""
    return f"${amount:,.2f}"

def create_property_card(property_data):
    """Create a property card HTML"""
    status_class = f"status-{property_data['status'].lower()}"
    
    card_html = f"""
    <div class="property-card">
        <div class="card-header">
            📍 Parcel: {property_data['parcel_no']}
            <span class="{status_class}" style="float: right;">{property_data['status']}</span>
        </div>
        <div class="card-address">🏠 {property_data['address']}</div>
        <div class="card-bid">💰 Opening Bid: {format_currency(property_data['opening_bid'])}</div>
        <div class="card-details">📋 Case: {property_data['case_no']}</div>
        <div class="card-details">👤 Defendant: {property_data['defendant']}</div>
        <div class="card-details">📅 Sale Date: {property_data['sale_date']}</div>
        <div class="card-details">🏷️ Type: {property_data['property_type']}</div>
    </div>
    """
    return card_html

def main():
    # Header
    st.title("🏠 Tax Deed Properties Viewer")
    st.markdown("**2025 Cuyahoga County Forfeited Land Sale**")
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.warning("No data available.")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Sale date filter
    sale_dates = df['sale_date'].unique()
    selected_date = st.sidebar.selectbox("Sale Date", ["All"] + list(sale_dates))
    
    # Status filter
    statuses = df['status'].unique()
    selected_status = st.sidebar.selectbox("Status", ["All"] + list(statuses))
    
    # Price range filter
    min_bid = float(df['opening_bid'].min())
    max_bid = float(df['opening_bid'].max())
    price_range = st.sidebar.slider(
        "Opening Bid Range",
        min_value=min_bid,
        max_value=max_bid,
        value=(min_bid, max_bid),
        format="$%.2f"
    )
    
    # Property type filter
    property_types = df['property_type'].unique()
    selected_type = st.sidebar.selectbox("Property Type", ["All"] + list(property_types))
    
    # Search filter
    search_term = st.sidebar.text_input("🔍 Search (Address, Parcel, Defendant)")
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_date != "All":
        filtered_df = filtered_df[filtered_df['sale_date'] == selected_date]
    
    if selected_status != "All":
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    
    filtered_df = filtered_df[
        (filtered_df['opening_bid'] >= price_range[0]) & 
        (filtered_df['opening_bid'] <= price_range[1])
    ]
    
    if selected_type != "All":
        filtered_df = filtered_df[filtered_df['property_type'] == selected_type]
    
    if search_term:
        mask = (
            filtered_df['address'].str.contains(search_term, case=False, na=False) |
            filtered_df['parcel_no'].str.contains(search_term, case=False, na=False) |
            filtered_df['defendant'].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{len(filtered_df)}</div>
            <div class="stat-label">Properties</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_bid = filtered_df['opening_bid'].mean() if not filtered_df.empty else 0
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{format_currency(avg_bid)}</div>
            <div class="stat-label">Avg. Bid</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_value = filtered_df['opening_bid'].sum() if not filtered_df.empty else 0
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{format_currency(total_value)}</div>
            <div class="stat-label">Total Value</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        available_count = len(filtered_df[filtered_df['status'] == 'Available']) if not filtered_df.empty else 0
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{available_count}</div>
            <div class="stat-label">Available</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Sort options
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f"📋 Properties ({len(filtered_df)} found)")
    
    with col2:
        sort_by = st.selectbox(
            "Sort by:",
            ["opening_bid", "parcel_no", "address", "sale_date"],
            format_func=lambda x: {
                "opening_bid": "Opening Bid",
                "parcel_no": "Parcel Number",
                "address": "Address",
                "sale_date": "Sale Date"
            }[x]
        )
        
        sort_order = st.checkbox("Descending", value=True)
    
    # Sort the data
    if not filtered_df.empty:
        filtered_df = filtered_df.sort_values(by=sort_by, ascending=not sort_order)
    
    # Display properties as cards
    if filtered_df.empty:
        st.info("No properties match your current filters.")
    else:
        # Pagination
        items_per_page = 20
        total_pages = (len(filtered_df) - 1) // items_per_page + 1
        
        if total_pages > 1:
            page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            page_df = filtered_df.iloc[start_idx:end_idx]
        else:
            page_df = filtered_df
        
        # Display cards
        for _, property_data in page_df.iterrows():
            st.markdown(create_property_card(property_data), unsafe_allow_html=True)
    
    # Export functionality
    st.markdown("---")
    st.subheader("📥 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Download Filtered Data as CSV"):
            csv_buffer = io.StringIO()
            filtered_df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            st.download_button(
                label="💾 Download CSV",
                data=csv_data,
                file_name=f"tax_deed_properties_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📊 Download All Data as CSV"):
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            st.download_button(
                label="💾 Download All CSV",
                data=csv_data,
                file_name=f"tax_deed_properties_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()

