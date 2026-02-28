import geopandas as gpd
import pandas as pd
import os


def merge_map_with_datasets(map_path, datasets_dir):

    print("P2: Merging map with datasets")
    
    # Load map 
    world = gpd.read_file(map_path)
    
    # Find all CSV datasets
    csv_files = [f for f in os.listdir(datasets_dir) if f.endswith('.csv')]
    
    # Merge each dataset with map
    for csv_file in csv_files:
        csv_path = os.path.join(datasets_dir, csv_file)
        df = pd.read_csv(csv_path)
        
        
        # Left dataframe is geopandas dataframe
        merged = world.merge(
            df,
            left_on="ISO_A3_EH",
            right_on="code",
            how="left"
        )
        
        print(f"Merged shape: {merged.shape}")