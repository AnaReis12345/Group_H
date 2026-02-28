import os
from pathlib import Path
import pandas as pd
import geopandas as gpd
import requests
import zipfile

def datasets_download(download_dir):
    # Create downloads directory
    Path(download_dir).mkdir(parents=True, exist_ok=True)
    
    print("1- Downloading datasets")

    # List of dataset URLs
    dataset_urls = [
        "https://ourworldindata.org/grapher/coverage-by-protected-areas-of-important-sites-for-mountain-biodiversity.csv?v=1&csvType=full&useColumnShortNames=true",
        "https://ourworldindata.org/grapher/annual-change-forest-area.csv?v=1&csvType=full&useColumnShortNames=true",
        "https://ourworldindata.org/grapher/annual-deforestation.csv?v=1&csvType=full&useColumnShortNames=true",
        "https://ourworldindata.org/grapher/terrestrial-protected-areas.csv?v=1&csvType=full&useColumnShortNames=true",
        "https://ourworldindata.org/grapher/share-degraded-land.csv?v=1&csvType=full&useColumnShortNames=true",
    ]
    
    # Corresponding filenames
    filenames = [
        "coverage_by_protected_areas.csv",
        "annual_change_forest_area.csv",
        "annual_deforestation.csv",
        "share_land_protected.csv",
        "share_degraded_land.csv",
    ]
    
    # Loop through and download each dataset
    for i, url in enumerate(dataset_urls):
        filepath = os.path.join(download_dir, filenames[i])

        
        try:
            # Read directly from URL
            df = pd.read_csv(url, storage_options={'User-Agent': 'Our World In Data data fetch/1.0'})
            
            # Save to file
            df.to_csv(filepath, index=False)
            print(f"Downloaded {filenames[i]}")
            print(f"Columns: {list(df.columns)}")
            print(f"Rows: {len(df)}")
            print(df.head())
        except Exception as e:
            print(f"Error downloading {filenames[i]}: {e}")
            print(f"URL: {url}")
    
    # Download the map
    print(" 2- Downloading World Map")
    
    map_url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
    map_zip_path = os.path.join(download_dir, "ne_110m_admin_0_countries.zip")
    
    response = requests.get(map_url)
    
    with open(map_zip_path, 'wb') as f:
        f.write(response.content)
    print(f"Downloaded map ({len(response.content)} bytes)")
    
    # Test reading with geopandas
    world = gpd.read_file(map_zip_path)
    print(f"\nMap loaded successfully!")
    print(f"Number of countries: {len(world)}")
    print(f"Map columns: {list(world.columns)}")
    
    print("\n" )
    print("Download completed of the map")

    # Code searching

    print("3- Searching for code column possibilities")
  
    # Analyze each dataset's 'code' column
    print("\n DATASETS - Unique values in 'code' column:")

    dataset_display_names = [
        "Protected Areas Coverage",
        "Annual Change in Forest Area",
        "Annual Deforestation",
        "Share of Land Protected",
        "Share of Land Degraded",
    ]
    
    for i, filename in enumerate(filenames):
        filepath = os.path.join(download_dir, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            unique_codes = df['code'].nunique()
            total_rows = len(df)
            sample_codes = df['code'].dropna().unique()[:5].tolist()
            
            print(f"\n{i+1}. {dataset_display_names[i]}:")
            print(f"   - File: {filename}")
            print(f"   - Total rows: {total_rows}")
            print(f"   - Unique country codes: {unique_codes}")
            print(f"   - Sample codes: {sample_codes}")
    
    # Analyze map's 3-letter country code columns
    print("\n")
    print("MAP - 3-letter country code columns:")
    
    # Find all 3-letter code columns in map
    three_letter_cols = [col for col in world.columns if any(x in col for x in ['A3', 'A_3'])]
    
    for col in three_letter_cols:
        unique_map_codes = world[col].nunique()
        total_countries = len(world)
        sample_map_codes = world[col].dropna().unique()[:5].tolist()
        
        print(f"\n Column: {col}")
        print(f"   - Total countries: {total_countries}")
        print(f"   - Unique codes: {unique_map_codes}")
        print(f"   - Sample codes: {sample_map_codes}")
    
    # Show best match for merging (using first dataset as reference)
    if len(filenames) > 0:
        print(" Best column for merging")
        
        first_dataset_path = os.path.join(download_dir, filenames[0])
        if os.path.exists(first_dataset_path):
            first_dataset = pd.read_csv(first_dataset_path)
            dataset_codes = set(first_dataset['code'].dropna().unique())
            
            best_match = None
            best_match_count = 0
            best_match_col = None
            
            for col in three_letter_cols:
                map_codes = set(world[col].dropna().unique())
                common = dataset_codes.intersection(map_codes)
                if len(common) > best_match_count:
                    best_match_count = len(common)
                    best_match_col = col
            
            if best_match_col:
                map_codes = set(world[best_match_col].dropna().unique())
                common = dataset_codes.intersection(map_codes)
                
                print(f"\n Best match: {best_match_col}")
                print(f"   - Dataset codes: {len(dataset_codes)}")
                print(f"   - Map codes in {best_match_col}: {len(map_codes)}")
                print(f"   - Common codes: {best_match_count}")
                print(f"   - Match rate: {best_match_count/len(dataset_codes)*100:.1f}%")
                
                if best_match_count > 0:
                    print(f"\n   Sample matching codes: {list(common)[:10]}")
    
    
 
    # RENAME COLUMNS IN DATASETS

    print("4- Renaming couple columns")
    
    column_renames = {
        "annual_deforestation.csv": {
            "_1d_deforestation": "deforestation"
        },
        "share_land_protected.csv": {
            "er_lnd_ptld_zs": "Terrestrial protected areas (% of total land area)"
        },
        "share_degraded_land.csv": {
            "_15_3_1__ag_lnd_dgrd": "Proportion of land that is degraded over total land area (%)"
        },
        "coverage_by_protected_areas.csv": {
            "_15_4_1__er_ptd_mtn": "Average proportion of Mountain Key Biodiversity Areas (KBAs) covered by protected areas (%)"
        }
    }
    
    for filename, renames in column_renames.items():
        filepath = os.path.join(download_dir, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            for old_name, new_name in renames.items():
                if old_name in df.columns:
                    df.rename(columns={old_name: new_name}, inplace=True)
                    print(f"\n {filename}: '{old_name}' → '{new_name}'")
            df.to_csv(filepath, index=False)
            print(f"   Updated file saved")

if __name__ == "__main__":
    datasets_download()