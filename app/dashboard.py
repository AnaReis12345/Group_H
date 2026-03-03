import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from app.environmental_data import EnvironmentalDataAnalyzer

# Page Setup
st.set_page_config(page_title="Okavango Dashboard", layout="wide")
st.title("Project Okavango: Environmental Dashboard 🌍")

# Loading the Data Engine (With caching so it only downloads once)
@st.cache_resource
def load_data():
    engine = EnvironmentalDataAnalyzer()
    return engine

data_engine = load_data()

# Dropdown Menu
st.subheader("Select an Environmental Map")

dataset_options = {
    "Annual Deforestation": "annual_deforestation",
    "Annual Change in Forest Area": "annual_change_forest_area",
    "Share of Land Protected": "share_land_protected",
    "Share of Degraded Land": "share_degraded_land",
    "Mountain Biodiversity Coverage": "coverage_by_protected_areas"
}
choice_label = st.selectbox("Choose a dataset to view:", list(dataset_options.keys()))
chosen_filename = dataset_options[choice_label]

# Access merged data from class
merged_map = data_engine.merged_data[chosen_filename]
year_col = 'Year' if 'Year' in merged_map.columns else 'year'
latest_year = merged_map[year_col].max()
merged_map = merged_map[merged_map[year_col] == latest_year]
data_column = data_engine.datasets[chosen_filename].columns[-1]

## Preparing and cleaning most recent data
#world_map = data_engine.world_map
#raw_data = data_engine.datasets[chosen_filename]
#year_col = 'Year' if 'Year' in raw_data.columns else 'year'
#code_col = 'Code' if 'Code' in raw_data.columns else 'code'
#latest_data = raw_data.sort_values(year_col).groupby(code_col).tail(1)

# Merging the map and the data together
#merged_map = world_map.merge(latest_data, left_on="ISO_A3_EH", right_on=code_col, how="left")
#data_column = latest_data.columns[-1]

st.write(f"### World Map: {choice_label}")
fig_map, ax_map = plt.subplots(figsize=(15, 8))

# Drawing map with a clean legend title
merged_map.plot(
    column=data_column, 
    ax=ax_map, 
    legend=True, 
    missing_kwds={'color': 'lightgrey'},
    cmap='OrRd',
    legend_kwds={'label': f'{choice_label} (Total Value)'} 
)
ax_map.set_axis_off() 
st.pyplot(fig_map)

# Custom graphs
st.divider()
st.subheader(f"More about {choice_label}")

# Removing empty shapes
graph_data = merged_map.dropna(subset=[data_column]).copy()
country_name_col = 'NAME' if 'NAME' in graph_data.columns else 'ADMIN'

# Calculating area to make some comparative analysis
graph_data['area_km2'] = graph_data.geometry.to_crs(epsg=6933).area / 10**6

# Continents setup (Separating Central America from North America, removing 7 seas and Antartica)
if 'CONTINENT' in graph_data.columns:
    def get_clean_continent(row):
        if row.get('SUBREGION') == 'Central America':
            return 'Central America'
        return row.get('CONTINENT')
    
    graph_data['Clean_Continent'] = graph_data.apply(get_clean_continent, axis=1)
    graph_data = graph_data[~graph_data['Clean_Continent'].isin(['Seven seas (open ocean)', 'Antarctica'])]

# Area weighted averages
def calc_weighted_avg(group):
    return (group[data_column] * group['area_km2']).sum() / group['area_km2'].sum()

# Show the Histogram for the datasets that need it
if choice_label in ["Share of Land Protected", "Share of Degraded Land", "Mountain Biodiversity Coverage"]:
    graph_view = st.radio(
        "Select your analysis view:", 
        ["Relevant Insights", "Global Distribution"],
        horizontal=True
    )
else:
    graph_view = "Relevant Insights"
if graph_view == "Global Distribution":
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.hist(graph_data[data_column], bins=20, color='coral', edgecolor='black')
    ax.set_xlabel("Data Value")
    ax.set_ylabel("Number of Countries")
    ax.set_title(f"Global Distribution of {choice_label}")
    
    # Removes scientific notation
    ax.ticklabel_format(style='plain', axis='both')
    if choice_label == "Share of Land Protected":
        ax.axvline(30, color='red', linestyle='dashed', linewidth=2, label='UN 30% Target')
        ax.legend()   
    st.pyplot(fig)
else:

    # Annual deforestation
    if choice_label == "Annual Deforestation":
        fig, ax = plt.subplots(figsize=(10, 5))
        if 'Clean_Continent' in graph_data.columns:
            # Dividing by 1 Million for clean reading
            continent_data = (graph_data.groupby('Clean_Continent')[data_column].sum() / 1e6).sort_values(ascending=False)
            continent_data = continent_data[continent_data > 0]
            ax.bar(continent_data.index, continent_data.values, color='firebrick')
            plt.xticks(rotation=45, ha='right')
            ax.set_ylabel("Total Deforestation (Millions of Hectares)")
            ax.set_title("Total Annual Deforestation by Continent") 
        st.pyplot(fig)

    # Absolute vs Proportional change
    elif choice_label == "Annual Change in Forest Area":
        graph_data['prop_change_percent'] = ((graph_data[data_column] * 0.01) / graph_data['area_km2']) * 100
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Absolute Change, scaled to millions
        top_gainers_abs = graph_data.nlargest(10, data_column).copy()
        top_losers_abs = graph_data.nsmallest(10, data_column).sort_values(by=data_column, ascending=False).copy()
        comb_abs = pd.concat([top_gainers_abs, top_losers_abs])
        comb_abs['data_in_millions'] = comb_abs[data_column] / 1e6
        colors_abs = ['forestgreen' if val > 0 else 'firebrick' for val in comb_abs['data_in_millions']]
        ax1.bar(comb_abs[country_name_col], comb_abs['data_in_millions'], color=colors_abs)
        ax1.tick_params(axis='x', rotation=45)
        ax1.set_ylabel("Change in Forest Area (Millions of Hectares)")
        ax1.set_title("Absolute Impact: Top 10 Gainers & Losers")

        # Proportional Change
        top_gainers_prop = graph_data.nlargest(10, 'prop_change_percent')
        top_losers_prop = graph_data.nsmallest(10, 'prop_change_percent').sort_values(by='prop_change_percent', ascending=False)
        comb_prop = pd.concat([top_gainers_prop, top_losers_prop])
        colors_prop = ['forestgreen' if val > 0 else 'firebrick' for val in comb_prop['prop_change_percent']]
        ax2.bar(comb_prop[country_name_col], comb_prop['prop_change_percent'], color=colors_prop)
        ax2.tick_params(axis='x', rotation=45)
        ax2.set_ylabel("Change as % of Country Area")
        ax2.set_title("Proportional Impact (Relative to Country Size)")
        plt.tight_layout() 
        st.pyplot(fig)

    # Share of Land Protected
    elif choice_label == "Share of Land Protected":
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Top 5 vs Bottom 5
        top_5 = graph_data.nlargest(5, data_column)
        bottom_5 = graph_data.nsmallest(5, data_column).sort_values(by=data_column, ascending=True)
        comb = pd.concat([top_5, bottom_5])
        ax1.bar(comb[country_name_col], comb[data_column], color='mediumseagreen')
        ax1.tick_params(axis='x', rotation=45)
        ax1.set_ylabel("Percentage of Land Protected (%)")
        ax1.set_title("Top 5 and Bottom 5 Countries")

        # Continent area-weighted average
        if 'Clean_Continent' in graph_data.columns:
            cont_avg = graph_data.groupby('Clean_Continent').apply(calc_weighted_avg).sort_values(ascending=False)
            ax2.bar(cont_avg.index, cont_avg.values, color='seagreen')
            ax2.tick_params(axis='x', rotation=45)
            ax2.set_ylabel("Weighted Average (%)")
            ax2.set_title("Area-Weighted Share Protected by Continent")
        plt.tight_layout()
        st.pyplot(fig)

    # Share of Degraded Land
    elif choice_label == "Share of Degraded Land":
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Top 5 vs Bottom 5
        top_5 = graph_data.nlargest(5, data_column)
        bottom_5 = graph_data.nsmallest(5, data_column).sort_values(by=data_column, ascending=True)
        comb = pd.concat([top_5, bottom_5])
        ax1.bar(comb[country_name_col], comb[data_column], color='sandybrown')
        ax1.tick_params(axis='x', rotation=45)
        ax1.set_ylabel("Percentage of Degraded Land (%)")
        ax1.set_title("Top 5 Most and Least Degraded Countries")

        # Continent area-weighted average
        if 'Clean_Continent' in graph_data.columns:
            cont_avg = graph_data.groupby('Clean_Continent').apply(calc_weighted_avg).sort_values(ascending=False)
            ax2.bar(cont_avg.index, cont_avg.values, color='sienna')
            ax2.tick_params(axis='x', rotation=45)
            ax2.set_ylabel("Weighted Average (%)")
            ax2.set_title("Area-Weighted Share Degraded by Continent")           
        plt.tight_layout()
        st.pyplot(fig)

    # Weighted average mountain coverage
    elif choice_label == "Mountain Biodiversity Coverage":
        fig, ax = plt.subplots(figsize=(10, 5))
        if 'Clean_Continent' in graph_data.columns:
            cont_avg = graph_data.groupby('Clean_Continent').apply(calc_weighted_avg).sort_values(ascending=False)
            ax.bar(cont_avg.index, cont_avg.values, color='steelblue')
            plt.xticks(rotation=45, ha='right')
            ax.set_ylabel("Weighted Average Coverage (%)")
            ax.set_title("Area-Weighted Mountain Protection by Continent")   
        st.pyplot(fig)


