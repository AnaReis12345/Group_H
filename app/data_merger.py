import geopandas as gpd
import pandas as pd


def merge_map_with_datasets(world_map: gpd.GeoDataFrame, datasets: dict[str, pd.DataFrame]) -> dict[str, gpd.GeoDataFrame]:
    """Merge the world map GeoDataFrame with each dataset. Returns a dict of GeoDataFrames."""
    merged_data = {}

    for name, df in datasets.items():
        merged_data[name] = world_map.merge(
            df,
            left_on="ISO_A3_EH",
            right_on="code",
            how="left"
        )
        print(f"Merged: {name} — shape: {merged_data[name].shape}")

    return merged_data