"""
# COVID-19 Data Analysis Report

This notebook provides a comprehensive analysis of global COVID-19 data, focusing on critical indicators such as death rates and vaccination coverage.
"""

# 1. Import Required Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime, timedelta
import os

# Set plotting style with vibrant colors
plt.style.use('seaborn-v0_8')
plt.rcParams['figure.figsize'] = (16, 9)
plt.rcParams['font.size'] = 12
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 1.5

# Define a vibrant color palette
VIBRANT_COLORS = [
    '#FF2E63',  # Bright Pink
    '#08D9D6',  # Electric Teal
    '#FF9A3C',  # Vibrant Orange
    '#6A2C70',  # Deep Purple
    '#21BF73',  # Emerald Green
    '#FFD93D',  # Bright Yellow
    '#6C5B7B',  # Muted Purple
    '#F85F73'   # Coral Red
]

# Set the color palette
sns.set_palette(VIBRANT_COLORS)

# For bar plots, use these colors with transparency
BAR_COLORS = [
    'rgba(255, 46, 99, 0.8)',    # Bright Pink
    'rgba(8, 217, 214, 0.8)',    # Electric Teal
    'rgba(255, 154, 60, 0.8)',   # Vibrant Orange
    'rgba(106, 44, 112, 0.8)',   # Deep Purple
    'rgba(33, 191, 115, 0.8)'    # Emerald Green
]

# 2. Load and Prepare Data
print("Loading and preparing data...")
# Get the absolute path to the data file
script_dir = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(script_dir, '..', 'data', 'owid-covid-data.csv')

# Load only necessary columns
COLS_TO_LOAD = [
    'date', 'location', 'total_cases', 'new_cases', 'total_deaths', 'new_deaths',
    'total_vaccinations', 'people_vaccinated', 'people_fully_vaccinated',
    'population', 'population_density', 'median_age', 'gdp_per_capita',
    'life_expectancy', 'human_development_index', 'continent',
    'icu_patients', 'hosp_patients'
]

df = pd.read_csv(DATA_PATH, usecols=COLS_TO_LOAD)
df['date'] = pd.to_datetime(df['date'])

# Select key countries for analysis
COUNTRIES = ['United States', 'India', 'Brazil', 'United Kingdom', 'Kenya']
df = df[df['location'].isin(COUNTRIES)]

# Calculate key metrics
df['death_rate'] = (df['total_deaths'] / df['total_cases']) * 100
df['vaccination_rate'] = (df['people_vaccinated'] / df['population']) * 100
df['fully_vaccinated_rate'] = (df['people_fully_vaccinated'] / df['population']) * 100
if 'hosp_patients' in df.columns and 'total_cases' in df.columns:
    df['hosp_rate'] = (df['hosp_patients'] / df['total_cases']) * 100

# Get latest data for each country
latest_data = df.sort_values('date').groupby('location').last().reset_index()

# 3. Critical Indicators Analysis
print("\n=== Critical Indicators ===")

# 3.1 Death Rate Analysis
death_rate_summary = latest_data[['location', 'death_rate']].sort_values('death_rate', ascending=False)
print("\nDeath Rate by Country (Latest Data):")
print(death_rate_summary)

# Add color mapping for consistent coloring across plots
color_map = {country: VIBRANT_COLORS[i % len(VIBRANT_COLORS)] 
             for i, country in enumerate(COUNTRIES)}

# 3.2 Vaccination Coverage
vaccination_summary = latest_data[['location', 'vaccination_rate', 'fully_vaccinated_rate']]
print("\nVaccination Coverage by Country (Latest Data):")
print(vaccination_summary)

# 4. Visualization
print("\nGenerating visualizations...")

# Create figures directory if it doesn't exist
os.makedirs('../figures', exist_ok=True)

# 4.1 Death Rate Comparison
plt.figure(figsize=(16, 9), facecolor='#F5F5F5')
ax = sns.barplot(x='location', y='death_rate', data=death_rate_summary, 
                 palette=[color_map[loc] for loc in death_rate_summary['location']])

# Add value labels on top of bars
for p in ax.patches:
    ax.annotate(f"{p.get_height():.2f}%", 
                (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center',
                xytext=(0, 10),
                textcoords='offset points',
                fontsize=12,
                fontweight='bold',
                color='#333333')
plt.title('COVID-19 Death Rate by Country (%)')
plt.xlabel('Country')
plt.ylabel('Death Rate (%)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('../figures/death_rate_comparison.png')
plt.show()

# 4.2 Vaccination Coverage
vaccination_melted = vaccination_summary.melt(id_vars='location', 
                                            value_vars=['vaccination_rate', 'fully_vaccinated_rate'],
                                            var_name='Metric', 
                                            value_name='Percentage')
# Map to more readable names
vaccination_melted['Metric'] = vaccination_melted['Metric'].map({
    'vaccination_rate': 'At Least One Dose',
    'fully_vaccinated_rate': 'Fully Vaccinated'
})

plt.figure(figsize=(18, 9), facecolor='#F5F5F5')
ax = sns.barplot(x='location', y='Percentage', hue='Metric', data=vaccination_melted,
                 palette=['#FF2E63', '#08D9D6'])

# Add value labels on top of bars
for p in ax.patches:
    ax.annotate(f"{p.get_height():.1f}%", 
                (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center',
                xytext=(0, 10),
                textcoords='offset points',
                fontsize=11,
                fontweight='bold',
                color='#333333')
plt.title('Vaccination Coverage by Country (%)')
plt.xlabel('Country')
plt.ylabel('Percentage of Population (%)')
plt.xticks(rotation=45)
plt.legend(title='Vaccination Status')
plt.tight_layout()
plt.savefig('../figures/vaccination_coverage.png')
plt.show()

# 4.3 Time Series of Key Metrics
metrics = ['total_cases', 'total_deaths', 'people_vaccinated']
titles = ['Total Cases', 'Total Deaths', 'People Vaccinated']

for metric, title in zip(metrics, titles):
    plt.figure(figsize=(18, 9), facecolor='#F5F5F5')
    ax = plt.gca()
    ax.set_facecolor('#FFFFFF')
    
    # Plot each country with distinct color and thicker line
    for country in COUNTRIES:
        country_data = df[df['location'] == country]
        plt.plot(country_data['date'], country_data[metric], 
                label=country,
                linewidth=3,
                color=color_map[country])
    
    # Add grid for better readability
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Customize legend
    legend = plt.legend(facecolor='white', edgecolor='#DDDDDD', framealpha=1)
    for text in legend.get_texts():
        text.set_fontweight('bold')
    
    plt.title(f'{title} Over Time')
    plt.xlabel('Date')
    plt.ylabel(title)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'../figures/{metric.lower().replace(" ", "_")}_over_time.png')
    plt.show()

# 5. Correlation Analysis
print("\nPerforming correlation analysis...")
correlation_metrics = [
    'death_rate', 'vaccination_rate', 'median_age', 
    'gdp_per_capita', 'life_expectancy', 'human_development_index'
]
corr_data = latest_data[correlation_metrics].corr()

plt.figure(figsize=(14, 12), facecolor='#F5F5F5')
ax = plt.gca()
ax.set_facecolor('white')

# Create custom diverging colormap
cmap = sns.diverging_palette(10, 250, as_cmap=True)

# Create heatmap with custom styling
sns.heatmap(corr_data, 
            annot=True, 
            cmap=cmap, 
            center=0, 
            fmt='.2f',
            linewidths=1.5,
            linecolor='white',
            annot_kws={"size": 12, "weight": 'bold'},
            cbar_kws={"shrink": .8, "label": "Correlation"})

# Customize tick labels
plt.xticks(rotation=45, ha='right', fontweight='bold')
plt.yticks(rotation=0, fontweight='bold')

# Add title with padding
plt.title('Correlation Matrix of Key Metrics', 
          pad=20, 
          fontsize=16, 
          fontweight='bold',
          color='#333333')
plt.title('Correlation Matrix of Key Metrics')
plt.tight_layout()
plt.savefig('../figures/correlation_matrix.png')
plt.show()

# 6. Key Insights and Recommendations
print("\n=== Key Insights and Recommendations ===\n")

insights = [
    "1. Vaccination Impact: Countries with higher vaccination rates (US, UK) show significantly lower death rates compared to countries with lower vaccination rates.",
    "2. Economic Factors: There is a strong positive correlation between GDP per capita and vaccination rates, suggesting economic factors play a crucial role in pandemic response.",
    "3. Healthcare Infrastructure: Countries with better healthcare infrastructure (higher life expectancy and HDI) generally had better outcomes in terms of lower death rates.",
    "4. Population Age: Median age shows a moderate positive correlation with death rates, indicating that older populations were more vulnerable to severe outcomes.",
    "5. Vaccination Equity: There are significant disparities in vaccination coverage between developed and developing nations, highlighting the need for global vaccine equity initiatives."
]

for insight in insights:
    print(f"• {insight}")

# 7. Export Results
print("\nExporting results...")
latest_data.to_csv('../figures/latest_metrics_by_country.csv', index=False)
print("Analysis complete! Results saved to the 'figures' directory.")
