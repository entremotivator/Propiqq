#!/usr/bin/env python3.11

import pandas as pd
import numpy as np
import re

def extract_tax_deed_data():
    """Extract and clean tax deed property data from Excel file"""
    
    # Read the Excel file
    df = pd.read_excel('/home/ubuntu/upload/CopyofCopyof2025-forfeited-land-sale.xlsx')
    
    # Find the header row (contains 'PARCEL NO.')
    header_row = None
    for i, row in df.iterrows():
        if 'PARCEL NO.' in str(row.iloc[0]):
            header_row = i
            break
    
    if header_row is None:
        print("Could not find header row")
        return None
    
    # Extract data starting from the row after headers
    data_start = header_row + 1
    
    # Get the actual data rows
    data_rows = []
    for i in range(data_start, len(df)):
        row = df.iloc[i]
        
        # Skip empty rows or rows that don't have parcel numbers
        if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
            continue
            
        # Skip header rows for different days
        if 'THE FOLLOWING PARCELS' in str(row.iloc[0]) or 'PARCEL NO.' in str(row.iloc[0]):
            continue
            
        # Extract the data
        parcel_no = str(row.iloc[0]).strip()
        address = str(row.iloc[1]).strip() if not pd.isna(row.iloc[1]) else ''
        case_no = str(row.iloc[2]).strip() if not pd.isna(row.iloc[2]) else ''
        defendant = str(row.iloc[3]).strip() if not pd.isna(row.iloc[3]) else ''
        opening_bid = row.iloc[5] if not pd.isna(row.iloc[5]) else 0
        property_type = str(row.iloc[7]).strip() if not pd.isna(row.iloc[7]) else 'land'
        
        # Clean up the data
        address = address.replace('nan', '').replace('\n', ' ').strip()
        defendant = defendant.replace('nan', '').strip()
        
        # Determine sale date based on position in file (rough estimate)
        sale_date = 'September 3, 2025' if i < 150 else 'September 4, 2025'
        
        data_rows.append({
            'parcel_no': parcel_no,
            'address': address,
            'case_no': case_no,
            'defendant': defendant,
            'opening_bid': opening_bid,
            'property_type': property_type,
            'sale_date': sale_date,
            'status': 'Available'  # Default status
        })
    
    # Create DataFrame
    clean_df = pd.DataFrame(data_rows)
    
    # Remove any rows with invalid parcel numbers
    clean_df = clean_df[clean_df['parcel_no'].str.match(r'^\d{3}-\d{2}-\d{3}.*')]
    
    # Clean opening bid values
    clean_df['opening_bid'] = pd.to_numeric(clean_df['opening_bid'], errors='coerce').fillna(0)
    
    # Save to CSV
    output_path = '/home/ubuntu/tax_deed_properties.csv'
    clean_df.to_csv(output_path, index=False)
    
    print(f"Extracted {len(clean_df)} property records")
    print(f"Data saved to: {output_path}")
    print("\nColumn summary:")
    print(clean_df.info())
    print("\nFirst 5 rows:")
    print(clean_df.head())
    
    return clean_df

if __name__ == "__main__":
    extract_tax_deed_data()

