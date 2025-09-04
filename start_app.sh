#!/bin/bash

# Tax Deed Properties Manager - Startup Script
echo "Starting Tax Deed Properties Manager..."
echo "========================================="

# Check if Streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "Installing Streamlit..."
    pip3 install streamlit
fi

# Check if data file exists
if [ ! -f "tax_deed_properties.csv" ]; then
    echo "Extracting data from Excel file..."
    python3.11 extract_data.py
fi

echo "Starting Streamlit application..."
echo "The application will be available at: http://localhost:8501"
echo "Press Ctrl+C to stop the application"
echo ""

# Start the Streamlit application
streamlit run tax_deed_app_enhanced.py --server.port 8501 --server.address 0.0.0.0

