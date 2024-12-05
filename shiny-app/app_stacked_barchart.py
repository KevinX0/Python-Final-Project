import pandas as pd
from shiny import App, ui, render
import matplotlib.pyplot as plt

# Load the dataset
data_path = '/Users/kevinxu/Desktop/Final Project Raw Data/merged_data.csv'
heatmap_data = pd.read_csv(data_path)

# Ensure categorical ordering
damage_order = ["No Damage", "Affected (1-9%)", "Minor (10-25%)", "Major (26-50%)", "Destroyed (>50%)"]
heatmap_data['* Damage'] = pd.Categorical(heatmap_data['* Damage'], categories=damage_order, ordered=True)

# Define custom colors
custom_colors = ['lightgray', 'yellowgreen', 'gold', 'orange', 'red']

# Define the UI
app_ui = ui.page_fluid(
    ui.panel_title("Damage Distribution by Geographic Type"),
    ui.output_plot("stacked_bar_chart")
)

# Define the Server
def server(input, output, session):
    @render.plot
    def stacked_bar_chart():
        # Aggregate data by geographic type and damage level
        damage_distribution = heatmap_data.groupby(
            ['geographic type', '* Damage']).size().unstack(fill_value=0)

        # Plot stacked bar chart
        fig, ax = plt.subplots(figsize=(12, 8))
        damage_distribution.plot(
            kind='bar', stacked=True, ax=ax, color=custom_colors)

        # Customize plot
        ax.set_title("Damage Distribution by Geographic Type",
                     fontsize=16, fontweight='bold')
        ax.set_xlabel("Geographic Type", fontsize=14)
        ax.set_ylabel("Number of Incidents", fontsize=14)
        ax.legend(title="Damage Level", fontsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        return fig

    output.stacked_bar_chart = stacked_bar_chart

# Define the app
app = App(app_ui, server)
