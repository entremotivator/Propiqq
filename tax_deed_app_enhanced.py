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

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

def create_sample_data():
    """Create sample data if CSV file is not available"""
    sample_data = [
        {
            'parcel_no': '008-24-064',
            'address': '2469 DOBSON CT CLEVELAND, OH. 44109',
            'case_no': 'CV983792',
            'defendant': 'OH REAL ESTATE INVEST LLC, ET AL.',
            'opening_bid': 3658.02,
            'property_type': 'land',
            'sale_date': 'September 3, 2025',
            'status': 'Available'
        },
        {
            'parcel_no': '015-04-051',
            'address': '3305 W 34 ST CLEVELAND, OH. 44109',
            'case_no': 'CV970324',
            'defendant': 'ORMANDY ERNEST, ET AL.',
            'opening_bid': 8692.61,
            'property_type': 'land',
            'sale_date': 'September 3, 2025',
            'status': 'Available'
        },
        {
            'parcel_no': '016-10-088',
            'address': '3255 W 54 ST CLEVELAND, OH. 44102',
            'case_no': 'CV948201',
            'defendant': 'KENNETH HUDSON, ET AL.',
            'opening_bid': 24095.32,
            'property_type': 'land',
            'sale_date': 'September 3, 2025',
            'status': 'Available'
        },
        {
            'parcel_no': '105-20-013',
            'address': '8215 ST CLAIR AVE CLEVELAND, OH. 44103',
            'case_no': 'CV948061',
            'defendant': 'BOB NANCE BASKETBALL ACADEMY, ET AL',
            'opening_bid': 212204.35,
            'property_type': 'land',
            'sale_date': 'September 3, 2025',
            'status': 'Available'
        },
        {
            'parcel_no': '144-12-025',
            'address': '13514 CORMERE RD CLEVELAND, OH. 44120',
            'case_no': 'CV985815',
            'defendant': 'EVANS, GRADY, ET AL.',
            'opening_bid': 169608.48,
            'property_type': 'land',
            'sale_date': 'September 4, 2025',
            'status': 'Available'
        }
    ]
    return pd.DataFrame(sample_data)

def load_data():
    """Load the tax deed property data with fallback options"""
    # Try different possible file locations
    possible_paths = [
        'tax_deed_properties.csv',
        './tax_deed_properties.csv',
        'data/tax_deed_properties.csv',
        os.path.join(os.path.dirname(__file__), 'tax_deed_properties.csv')
    ]
    
    for path in possible_paths:
        try:
            if os.path.exists(path):
                df = pd.read_csv(path)
                st.success(f"✅ Data loaded successfully from {path}")
                return df
        except Exception as e:
            continue
    
    # If no CSV file found, create sample data
    st.warning("⚠️ CSV file not found. Using sample data. Please upload your tax_deed_properties.csv file.")
    return create_sample_data()

def save_data(df):
    """Save the modified data back to CSV"""
    try:
        df.to_csv('tax_deed_properties.csv', index=False)
        return True
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
        return False

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

def file_uploader_section():
    """File upload section for CSV data"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📁 Data Management")
    
    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV file",
        type=['csv'],
        help="Upload your tax_deed_properties.csv file"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.df = df
            st.session_state.data_loaded = True
            st.sidebar.success("✅ File uploaded successfully!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error reading file: {str(e)}")

def main():
    # Header
    st.title("🏠 Tax Deed Properties Manager")
    st.markdown("**2025 Cuyahoga County Forfeited Land Sale - Live Data Management**")
    
    # Load data if not already loaded
    if not st.session_state.data_loaded:
        st.session_state.df = load_data()
        st.session_state.data_loaded = True
    
    df = st.session_state.df
    
    if df.empty:
        st.error("No data available. Please upload a CSV file using the sidebar.")
        file_uploader_section()
        return
    
    # File uploader in sidebar
    file_uploader_section()
    
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
        st.info("💡 Editing functionality is available when running locally. Upload your CSV file to view and manage data.")
        
        # Show current data in a table for editing reference
        if not df.empty:
            st.dataframe(df, use_container_width=True)
    
    with tab3:
        st.subheader("➕ Add New Property")
        st.info("💡 Adding functionality is available when running locally. Upload your CSV file to manage data.")
        
        # Show sample data structure
        st.markdown("**Expected Data Structure:**")
        sample_df = pd.DataFrame([{
            'parcel_no': 'XXX-XX-XXX',
            'address': 'Property Address',
            'case_no': 'CVXXXXXX',
            'defendant': 'Defendant Name',
            'opening_bid': 0.00,
            'property_type': 'land',
            'sale_date': 'September 3, 2025',
            'status': 'Available'
        }])
        st.dataframe(sample_df, use_container_width=True)

if __name__ == "__main__":
    main()

