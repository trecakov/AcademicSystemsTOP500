#
# This script extracts geographic statistics from AllListsAcademia directory and outputs the csv with counts per country and continent.
#
# To run script 'python3.6 geographic_distribution.py'
#

import pandas as pd
import os
import glob
import re

def extract_geographic_distribution(input_dir="AllListsAcademia", output_file="geographic_distribution.csv"):
    
    # Get all CSV files in the directory
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {input_dir}")
        return
    
    print(f"Found {len(csv_files)} CSV files")
    
    # Mapping of countries to continents
    country_to_continent = {
        # North America
        'United States': 'North America', 'USA': 'North America', 'Canada': 'North America', 'Mexico': 'North America',
        # Europe
        'Germany': 'Europe', 'United Kingdom': 'Europe', 'UK': 'Europe', 'France': 'Europe', 
        'Italy': 'Europe', 'Spain': 'Europe', 'Netherlands': 'Europe', 'Switzerland': 'Europe',
        'Sweden': 'Europe', 'Norway': 'Europe', 'Finland': 'Europe', 'Denmark': 'Europe',
        'Belgium': 'Europe', 'Austria': 'Europe', 'Poland': 'Europe', 'Russia': 'Europe',
        'Czech Republic': 'Europe', 'Ireland': 'Europe', 'Portugal': 'Europe', 'Greece': 'Europe',
        'Hungary': 'Europe', 'Romania': 'Europe', 'Bulgaria': 'Europe', 'Croatia': 'Europe',
        'Slovakia': 'Europe', 'Slovenia': 'Europe', 'Luxembourg': 'Europe', 'Iceland': 'Europe',
        # Asia
        'China': 'Asia', 'Japan': 'Asia', 'South Korea': 'Asia', 'India': 'Asia',
        'Taiwan': 'Asia', 'Singapore': 'Asia', 'Hong Kong': 'Asia', 'Thailand': 'Asia',
        'Malaysia': 'Asia', 'Vietnam': 'Asia', 'Indonesia': 'Asia', 'Philippines': 'Asia',
        'Pakistan': 'Asia', 'Bangladesh': 'Asia', 'Saudi Arabia': 'Asia', 'UAE': 'Asia',
        'Israel': 'Asia', 'Turkey': 'Asia', 'Iran': 'Asia', 'Kazakhstan': 'Asia',
        # Oceania
        'Australia': 'Oceania', 'New Zealand': 'Oceania',
        # South America
        'Brazil': 'South America', 'Argentina': 'South America', 'Chile': 'South America',
        'Colombia': 'South America', 'Peru': 'South America', 'Venezuela': 'South America',
        # Africa
        'South Africa': 'Africa', 'Egypt': 'Africa', 'Morocco': 'Africa', 'Kenya': 'Africa',
        'Nigeria': 'Africa', 'Tunisia': 'Africa'
    }
    
    results = []
    
    # Process each CSV file
    for csv_file in sorted(csv_files):
        try:
            filename = os.path.basename(csv_file)
            list_id = os.path.splitext(filename)[0]
            
            # Extract date code from filename
            date_match = re.search(r'(\d{6})', list_id)
            date_code = date_match.group(1) if date_match else None
            
            print(f"\nProcessing {filename} (date code: {date_code})")
            
            # Read CSV file
            df = pd.read_csv(csv_file)
            
            # Find Country column
            country_column = None
            possible_names = ['Country', 'country', 'COUNTRY', 'Country/Region']
            
            for col_name in possible_names:
                if col_name in df.columns:
                    country_column = col_name
                    break
            
            if country_column is None:
                print(f"  Warning: 'Country' column not found, skipping...")
                print(f"  Available columns: {', '.join(df.columns[:15])}...")
                continue
            
            # Count systems by country
            country_counts = df[country_column].value_counts().to_dict()
            
            # Initialize continent counts
            continent_counts = {}
            
            # Map countries to continents and count
            for country, count in country_counts.items():
                if pd.isna(country):
                    continue
                    
                country_str = str(country).strip()
                
                # Find continent
                continent = country_to_continent.get(country_str, 'Unknown')
                
                if continent not in continent_counts:
                    continent_counts[continent] = 0
                continent_counts[continent] += count
            
            # Create result entry
            result = {
                'List': list_id,
                'Date': date_code,
                'Total_Systems': len(df)
            }
            
            # Add continent counts
            for continent in ['North America', 'Europe', 'Asia', 'Oceania', 'South America', 'Africa', 'Unknown']:
                result[f'Continent_{continent.replace(" ", "_")}'] = continent_counts.get(continent, 0)
            
            # Add individual country counts (top countries)
            for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True):
                if pd.isna(country):
                    continue
                country_str = str(country).strip()
                result[f'Country_{country_str.replace(" ", "_")}'] = count
            
            results.append(result)
            
        except Exception as e:
            print(f"  Error processing {filename}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    # Create DataFrame from results
    results_df = pd.DataFrame(results)
    
    # Fill NaN values with 0 (countries that don't appear in all lists)
    results_df = results_df.fillna(0)
    
    # Convert count columns to integers
    for col in results_df.columns:
        if col.startswith('Continent_') or col.startswith('Country_'):
            results_df[col] = results_df[col].astype(int)
    
    # Save to CSV
    results_df.to_csv(output_file, index=False)
    
    return results_df

if __name__ == "__main__":
    df = extract_geographic_distribution()
