import geopandas as gpd
import pandas as pd
from shiny import App, ui, render
import matplotlib.pyplot as plt

data_path = '/Users/kevinxu/Desktop/Final Project Raw Data/merged_data.csv'
heatmap_data = pd.read_csv(data_path)
shapefile_path = '/Users/kevinxu/Desktop/Final Project Data Cleaning/ca_counties/CA_Counties.shp'
california_shape = gpd.read_file(shapefile_path)
california_shape = california_shape.to_crs(epsg=4326)

damage_map = {
    "No Damage": 0,
    "Affected (1-9%)": 5,
    "Minor (10-25%)": 17.5,
    "Major (26-50%)": 38,
    "Destroyed (>50%)": 75
}
heatmap_data['Damage Score'] = heatmap_data['* Damage'].map(damage_map)

gdf_heatmap = gpd.GeoDataFrame(
    heatmap_data,
    geometry=gpd.points_from_xy(
        heatmap_data['Longitude'], heatmap_data['Latitude']),
    crs="EPSG:4326"
)
merged = gpd.sjoin(gdf_heatmap, california_shape,
                   how="left", predicate="within")

app_ui = ui.page_fluid(
    ui.panel_title("California Damage Heatmap with Urbanization"),
    ui.input_select("damage_level", "Select Damage Level:",
                    choices=[
                        "All", "No Damage", "Affected (1-9%)", "Minor (10-25%)", "Major (26-50%)", "Destroyed (>50%)"],
                    selected="All"),
    ui.input_select("urbanization", "Select Urbanization Type:",
                    choices=["All", "Urban", "Suburban", "Rural"], selected="All"),
    ui.input_slider("grid_size", "Grid Size:", min=10, max=100, value=50),
    ui.output_plot("heatmap_plot"),
    ui.output_text("data_summary")
)


def server(input, output, session):
    def get_filtered_data():
        # Filter data based on selected damage level
        if input.damage_level() == "All":
            filtered = heatmap_data
        else:
            filtered = heatmap_data[heatmap_data['* Damage']
                                    == input.damage_level()]

        # Filter data based on selected urbanization type
        if input.urbanization() != "All":
            filtered = filtered[filtered['geographic type']
                                == input.urbanization()]

        return filtered

    @render.plot
    def heatmap_plot():
        filtered_data = get_filtered_data()

        fig, ax = plt.subplots(figsize=(16, 16))
        california_shape.boundary.plot(ax=ax, color='black', linewidth=0.8)

        if not filtered_data.empty:
            hb = ax.hexbin(
                filtered_data['Longitude'], filtered_data['Latitude'],
                C=filtered_data['Damage Score'],
                gridsize=input.grid_size(), cmap='YlOrRd', reduce_C_function=max,
                vmin=0, vmax=100
            )
            fig.colorbar(hb, ax=ax, label="Damage Score")
        else:
            ax.text(0.5, 0.5, 'No data available for the selected filters',
                    fontsize=14, ha='center', va='center', transform=ax.transAxes)

        ax.set_title(f"California Property Damage Heatmap\nDamage Level: {input.damage_level()}, Urbanization: {input.urbanization()}",
                     fontsize=16, fontweight="bold")
        ax.set_xlabel("Longitude", fontsize=12)
        ax.set_ylabel("Latitude", fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.5)

        ax.set_xlim(-125, -113)
        ax.set_ylim(32, 42)

        return fig

    @render.text
    def data_summary():
        filtered_data = get_filtered_data()
        count = len(filtered_data)
        return f"Number of incidents matching filters: {count}"

    output.heatmap_plot = heatmap_plot
    output.data_summary = data_summary


app = App(app_ui, server)
