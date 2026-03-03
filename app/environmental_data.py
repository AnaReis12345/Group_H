import os
import geopandas as gpd
import pandas as pd

from app.data_downloader import datasets_download
from app.data_merger import merge_map_with_datasets


class EnvironmentalDataAnalyzer:
    """Handles downloading, loading, and merging of environmental datasets with a world map."""

    def __init__(self, data_dir: str = "downloads") -> None:
        self.data_dir = data_dir
        self.world_map: gpd.GeoDataFrame | None = None
        self.datasets: dict[str, pd.DataFrame] = {}
        self.merged_data: dict[str, gpd.GeoDataFrame] = {}

        datasets_download(self.data_dir)
        self._read_dataframes()
        self.merged_data = merge_map_with_datasets(self.world_map, self.datasets)

    def _read_dataframes(self) -> None:
        """Read the downloaded map and CSV files into class attributes."""
        map_path = os.path.join(self.data_dir, "ne_110m_admin_0_countries.zip")
        self.world_map = gpd.read_file(map_path)

        for filename in os.listdir(self.data_dir):
            if filename.endswith(".csv"):
                filepath = os.path.join(self.data_dir, filename)
                name = filename.replace(".csv", "")
                self.datasets[name] = pd.read_csv(filepath)
                print(f"Loaded dataset: {name}")