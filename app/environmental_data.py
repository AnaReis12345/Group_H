import geopandas as gpd
import pandas as pd
import os

from app.data_downloader import datasets_download
from app.data_merger import merge_map_with_datasets


class EnvironmentalDataAnalyzer:

    def __init__(self, data_dir = "downloads"):

        self.data_dir = data_dir
        self.world_map = None
        self.datasets = {}
        self.merged_data = {}
        
        # Execute Function 1
        datasets_download(self.data_dir)
        
        # Execute Function 2
        map_path = os.path.join(self.data_dir, "ne_110m_admin_0_countries.zip")
        merge_map_with_datasets(map_path, self.data_dir)
        
        # Read datasets into dataframes
        self._read_dataframes()
    
    def _read_dataframes(self):

        # Read map
        map_path = os.path.join(self.data_dir, "ne_110m_admin_0_countries.zip")
        self.world_map = gpd.read_file(map_path)
        
        # Read CSV files
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.csv'):
                filepath = os.path.join(self.data_dir, filename)
                dataset_name = filename.replace('.csv', '')
                self.datasets[dataset_name] = pd.read_csv(filepath)