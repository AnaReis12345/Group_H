import os
import requests
import pandas as pd
from pathlib import Path


def datasets_download(download_dir: str) -> None:
    """Download all required datasets and world map into download_dir."""
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    dataset_urls = [
        "https://ourworldindata.org/grapher/coverage-by-protected-areas-of-important-sites-for-mountain-biodiversity.csv?v=1&csvType=full&useColumnShortNames=true",
        "https://ourworldindata.org/grapher/annual-change-forest-area.csv?v=1&csvType=full&useColumnShortNames=true",
        "https://ourworldindata.org/grapher/annual-deforestation.csv?v=1&csvType=full&useColumnShortNames=true",
        "https://ourworldindata.org/grapher/terrestrial-protected-areas.csv?v=1&csvType=full&useColumnShortNames=true",
        "https://ourworldindata.org/grapher/share-degraded-land.csv?v=1&csvType=full&useColumnShortNames=true",
    ]

    filenames = [
        "coverage_by_protected_areas.csv",
        "annual_change_forest_area.csv",
        "annual_deforestation.csv",
        "share_land_protected.csv",
        "share_degraded_land.csv",
    ]

    column_renames = {
        "annual_deforestation.csv": {"_1d_deforestation": "deforestation"},
        "share_land_protected.csv": {"er_lnd_ptld_zs": "Terrestrial protected areas (% of total land area)"},
        "share_degraded_land.csv": {"_15_3_1__ag_lnd_dgrd": "Proportion of land that is degraded over total land area (%)"},
        "coverage_by_protected_areas.csv": {"_15_4_1__er_ptd_mtn": "Average proportion of Mountain Key Biodiversity Areas (KBAs) covered by protected areas (%)"},
    }

    for url, filename in zip(dataset_urls, filenames):
        filepath = os.path.join(download_dir, filename)
        try:
            df = pd.read_csv(url, storage_options={"User-Agent": "Our World In Data data fetch/1.0"})
            if filename in column_renames:
                df.rename(columns=column_renames[filename], inplace=True)
            df.to_csv(filepath, index=False)
            print(f"Downloaded: {filename}")
        except Exception as e:
            print(f"Error downloading {filename}: {e}")

    map_url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
    map_path = os.path.join(download_dir, "ne_110m_admin_0_countries.zip")
    response = requests.get(map_url)
    with open(map_path, "wb") as f:
        f.write(response.content)
    print("Downloaded: world map")