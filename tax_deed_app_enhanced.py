#!/usr/bin/env python3.11

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io
import os

# Page configuration
st.set_page_config(
    page_title="Tax Deed Properties Manager",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for card styling and editing interface
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
    
    .edit-section {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border: 2px dashed #dee2e6;
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
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 10px 0;
    }
    
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_modified' not in st.session_state:
    st.session_state.data_modified = False
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

@st.cache_data
def load_data():
    """Load the tax deed property data"""
    try:
        df = pd.read_csv('/home/ubuntu/tax_deed_properties.csv')
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please ensure tax_deed_properties.csv exists.")
        return pd.DataFrame()

def save_data(df):
    """Save the modified data back to CSV"""
    try:
        df.to_csv('/home/ubuntu/tax_deed_properties.csv', index=False)
        return True
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
        return False

def format_currency(amount):
    """Format currency values"""
    return f"${amount:,.2f}"

def create_property_card(property_data, show_edit_button=True):
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

def edit_property_form(property_data, index):
    """Create an edit form for a property"""
    st.markdown(f"### ✏️ Edit Property: {property_data['parcel_no']}")
    
    with st.form(f"edit_form_{index}"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_address = st.text_area("Address", value=property_data['address'], height=100)
            new_opening_bid = st.number_input("Opening Bid ($)", value=float(property_data['opening_bid']), min_value=0.0, step=0.01)
            new_case_no = st.text_input("Case Number", value=property_data['case_no'])
        
        with col2:
            new_defendant = st.text_area("Defendant", value=property_data['defendant'], height=100)
            new_status = st.selectbox("Status", ["Available", "Sold", "Pending"], index=["Available", "Sold", "Pending"].index(property_data['status']))
            new_property_type = st.text_input("Property Type", value=property_data['property_type'])
            new_sale_date = st.text_input("Sale Date", value=property_data['sale_date'])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            save_changes = st.form_submit_button("💾 Save Changes", type="primary")
        
        with col2:
            cancel_edit = st.form_submit_button("❌ Cancel")
        
        with col3:
            delete_property = st.form_submit_button("🗑️ Delete Property", type="secondary")
        
        if save_changes:
            return {
                'action': 'save',
                'data': {
                    'address': new_address,
                    'opening_bid': new_opening_bid,
                    'case_no': new_case_no,
                    'defendant': new_defendant,
                    'status': new_status,
                    'property_type': new_property_type,
                    'sale_date': new_sale_date
                }
            }
        elif cancel_edit:
            return {'action': 'cancel'}
        elif delete_property:
            return {'action': 'delete'}
        
        return None

def add_new_property_form():
    """Form to add a new property"""
    st.markdown("### ➕ Add New Property")
    
    with st.form("add_new_property"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_parcel_no = st.text_input("Parcel Number*", placeholder="XXX-XX-XXX")
            new_address = st.text_area("Address*", height=100)
            new_opening_bid = st.number_input("Opening Bid ($)*", min_value=0.0, step=0.01)
            new_case_no = st.text_input("Case Number*", placeholder="CVXXXXXX")
        
        with col2:
            new_defendant = st.text_area("Defendant*", height=100)
            new_status = st.selectbox("Status", ["Available", "Sold", "Pending"])
            new_property_type = st.text_input("Property Type", value="land")
            new_sale_date = st.selectbox("Sale Date", ["September 3, 2025", "September 4, 2025"])
        
        add_property = st.form_submit_button("➕ Add Property", type="primary")
        
        if add_property:
            if new_parcel_no and new_address and new_case_no and new_defendant:
                return {
                    'parcel_no': new_parcel_no,
                    'address': new_address,
                    'case_no': new_case_no,
                    'defendant': new_defendant,
                    'opening_bid': new_opening_bid,
                    'property_type': new_property_type,
                    'sale_date': new_sale_date,
                    'status': new_status
                }
            else:
                st.error("Please fill in all required fields marked with *")
        
        return None

def main():
    # Header
    st.title("🏠 Tax Deed Properties Manager")
    st.markdown("**2025 Cuyahoga County Forfeited Land Sale - Live Data Management**")
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.warning("No data available.")
        return
    
    # Clear cache if data was modified
    if st.session_state.data_modified:
        load_data.clear()
        df = load_data()
        st.session_state.data_modified = False
    
    # Main navigation
    tab1, tab2, tab3 = st.tabs(["📋 View Properties", "✏️ Edit Properties", "➕ Add Property"])
    
    with tab1:
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
    
    with tab2:
        st.subheader("✏️ Edit Properties")
        st.markdown("Select a property to edit by searching or browsing:")
        
        # Search for property to edit
        edit_search = st.text_input("🔍 Search property to edit (Parcel Number, Address, etc.)")
        
        edit_filtered_df = df.copy()
        if edit_search:
            mask = (
                edit_filtered_df['address'].str.contains(edit_search, case=False, na=False) |
                edit_filtered_df['parcel_no'].str.contains(edit_search, case=False, na=False) |
                edit_filtered_df['defendant'].str.contains(edit_search, case=False, na=False)
            )
            edit_filtered_df = edit_filtered_df[mask]
        
        if not edit_filtered_df.empty:
            # Select property to edit
            property_options = [f"{row['parcel_no']} - {row['address'][:50]}..." for _, row in edit_filtered_df.iterrows()]
            selected_property_idx = st.selectbox("Select property to edit:", range(len(property_options)), format_func=lambda x: property_options[x])
            
            if selected_property_idx is not None:
                selected_property = edit_filtered_df.iloc[selected_property_idx]
                original_index = edit_filtered_df.index[selected_property_idx]
                
                # Show current property card
                st.markdown("#### Current Property:")
                st.markdown(create_property_card(selected_property), unsafe_allow_html=True)
                
                # Edit form
                st.markdown('<div class="edit-section">', unsafe_allow_html=True)
                edit_result = edit_property_form(selected_property, original_index)
                st.markdown('</div>', unsafe_allow_html=True)
                
                if edit_result:
                    if edit_result['action'] == 'save':
                        # Update the dataframe
                        for key, value in edit_result['data'].items():
                            df.loc[original_index, key] = value
                        
                        # Save to file
                        if save_data(df):
                            st.success("✅ Property updated successfully!")
                            st.session_state.data_modified = True
                            st.rerun()
                        else:
                            st.error("❌ Failed to save changes.")
                    
                    elif edit_result['action'] == 'delete':
                        # Confirm deletion
                        if st.button("⚠️ Confirm Delete", type="secondary"):
                            df = df.drop(original_index)
                            if save_data(df):
                                st.success("✅ Property deleted successfully!")
                                st.session_state.data_modified = True
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete property.")
                    
                    elif edit_result['action'] == 'cancel':
                        st.info("Edit cancelled.")
        else:
            st.info("No properties found matching your search.")
    
    with tab3:
        st.subheader("➕ Add New Property")
        
        new_property_data = add_new_property_form()
        
        if new_property_data:
            # Check if parcel number already exists
            if new_property_data['parcel_no'] in df['parcel_no'].values:
                st.error("❌ A property with this parcel number already exists!")
            else:
                # Add new property to dataframe
                new_row = pd.DataFrame([new_property_data])
                df = pd.concat([df, new_row], ignore_index=True)
                
                # Save to file
                if save_data(df):
                    st.success("✅ New property added successfully!")
                    st.session_state.data_modified = True
                    st.rerun()
                else:
                    st.error("❌ Failed to add new property.")

if __name__ == "__main__":
    main()

