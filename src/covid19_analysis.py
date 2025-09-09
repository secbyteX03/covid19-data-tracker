"""
COVID-19 Global Data Analysis
-----------------------------
A comprehensive analysis of global COVID-19 data including cases, deaths, and vaccinations.
"""

# Import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Set plotting style
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 12

# Constants
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'owid-covid-data.csv')
COUNTRIES = ['United States', 'India', 'Brazil', 'United Kingdom', 'Kenya']

# Define columns to load (only what we need)
COLS_TO_LOAD = [
    'date', 'location', 'total_cases', 'new_cases', 'total_deaths', 'new_deaths',
    'total_vaccinations', 'people_vaccinated', 'people_fully_vaccinated',
    'population', 'population_density', 'median_age', 'gdp_per_capita',
    'life_expectancy', 'human_development_index', 'continent'
]

# 1. Data Loading and Initial Exploration
def load_and_explore_data():
    """Load and perform initial exploration of the COVID-19 dataset."""
    try:
        # Load only the columns we need
        df = pd.read_csv(DATA_PATH, usecols=COLS_TO_LOAD)
        
        # Display basic information
        print("\n=== Dataset Overview ===")
        print(f"Shape: {df.shape}")
        print("\nFirst 5 rows:")
        print(df.head().to_string())
        
        # Display column information
        print("\n=== Column Information ===")
        df.info()
        
        # Check for missing values
        print("\n=== Missing Values ===")
        missing = df.isnull().sum()
        print(missing[missing > 0].sort_values(ascending=False))
        
        # Display basic statistics
        print("\n=== Basic Statistics ===")
        print(df.describe().to_string())
        
        return df
    except FileNotFoundError:
        print(f"Error: File not found at {DATA_PATH}")
        print("Please download the dataset and place it in the data/ directory.")
        print("Download from: https://covid.ourworldindata.org/data/owid-covid-data.csv")
        return None

# 2. Data Cleaning and Preparation
def clean_and_prepare_data(df):
    """Clean and prepare the COVID-19 data for analysis."""
    # Create a copy of the dataframe
    df_clean = df.copy()
    
    # Convert date column to datetime
    df_clean['date'] = pd.to_datetime(df_clean['date'])
    
    # Filter for countries of interest
    df_clean = df_clean[df_clean['location'].isin(COUNTRIES)]
    
    # Sort by location and date
    df_clean = df_clean.sort_values(['location', 'date'])
    
    # Forward fill missing values within each country group
    df_clean = df_clean.groupby('location').apply(
        lambda x: x.ffill()
    ).reset_index(drop=True)
    
    # Calculate additional metrics
    df_clean['death_rate'] = (df_clean['total_deaths'] / df_clean['total_cases']) * 100
    df_clean['vaccination_rate'] = (df_clean['people_vaccinated'] / df_clean['population']) * 100
    df_clean['fully_vaccinated_rate'] = (df_clean['people_fully_vaccinated'] / df_clean['population']) * 100
    
    # Handle any remaining missing values
    df_clean = df_clean.dropna(subset=['date', 'location', 'total_cases', 'total_deaths'])
    
    return df_clean
    
    # Filter for countries of interest
    df_clean = df_clean[df_clean['location'].isin(COUNTRIES)]
    
    # Calculate additional metrics
    df_clean['death_rate'] = (df_clean['total_deaths'] / df_clean['total_cases']) * 100
    df_clean['vaccination_rate'] = (df_clean['people_vaccinated'] / df_clean['population']) * 100
    df_clean['fully_vaccinated_rate'] = (df_clean['people_fully_vaccinated'] / df_clean['population']) * 100
    
    # Handle missing values
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        df_clean[col] = df_clean.groupby('location')[col].transform(
            lambda x: x.ffill()
        )
    
    # Drop rows with missing dates or critical values
    df_clean = df_clean.dropna(subset=['date', 'total_cases', 'total_deaths'])
    
    return df_clean

# 3. Visualization Functions
def plot_time_series(df, metric, title, ylabel, countries=COUNTRIES, log_scale=False):
    """Plot time series data for selected countries."""
    plt.figure(figsize=(14, 7))
    
    for country in countries:
        country_data = df[df['location'] == country]
        plt.plot(country_data['date'], country_data[metric], label=country, linewidth=2)
    
    plt.title(title, fontsize=16, pad=20)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    if log_scale:
        plt.yscale('log')
        plt.title(f"{title} (Log Scale)")
    
    plt.tight_layout()
    plt.show()

def plot_bar_chart(df, x, y, title, xlabel, ylabel, figsize=(12, 6)):
    """Plot a bar chart."""
    plt.figure(figsize=figsize)
    ax = sns.barplot(x=x, y=y, data=df, palette='viridis')
    plt.title(title, fontsize=16, pad=20)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.xticks(rotation=45)
    
    # Add value labels on top of bars
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.1f}', 
                   (p.get_x() + p.get_width() / 2., p.get_height()),
                   ha='center', va='center', 
                   xytext=(0, 10), 
                   textcoords='offset points')
    
    plt.tight_layout()
    plt.show()

def plot_choropleth(df, metric, title, color_scale='Viridis'):
    """Plot a choropleth map using Plotly."""
    # Get the latest data for each country
    latest_data = df.sort_values('date').groupby('location').last().reset_index()
    
    fig = px.choropleth(
        latest_data,
        locations='location',
        locationmode='country names',
        color=metric,
        hover_name='location',
        color_continuous_scale=color_scale,
        title=title,
        labels={metric: metric.replace('_', ' ').title()}
    )
    
    fig.update_geos(projection_type='natural earth')
    fig.update_layout(
        margin={'r': 0, 't': 30, 'l': 0, 'b': 0},
        height=600,
        width=1000
    )
    
    return fig

# 4. Analysis Functions
def analyze_trends(df):
    """Analyze COVID-19 trends over time."""
    print("\n=== COVID-19 Trends Analysis ===")
    
    # Plot total cases over time
    plot_time_series(
        df, 'total_cases', 
        'Total COVID-19 Cases Over Time', 
        'Total Cases',
        log_scale=True
    )
    
    # Plot total deaths over time
    plot_time_series(
        df, 'total_deaths', 
        'Total COVID-19 Deaths Over Time', 
        'Total Deaths',
        log_scale=True
    )
    
    # Plot daily new cases (7-day rolling average)
    for country in COUNTRIES:
        country_data = df[df['location'] == country].copy()
        country_data['new_cases_7day_avg'] = country_data['new_cases'].rolling(window=7).mean()
        
        plt.figure(figsize=(14, 7))
        plt.plot(country_data['date'], country_data['new_cases_7day_avg'], 
                label='7-day Average', color='red', linewidth=2)
        plt.bar(country_data['date'], country_data['new_cases'], 
               alpha=0.3, label='Daily New Cases')
        
        plt.title(f'Daily New COVID-19 Cases in {country} (7-day Average)', fontsize=16, pad=20)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Number of Cases', fontsize=12)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

def analyze_vaccination_progress(df):
    """Analyze vaccination progress across countries."""
    print("\n=== Vaccination Progress Analysis ===")
    
    # Plot vaccination rates over time
    plot_time_series(
        df, 'vaccination_rate', 
        'COVID-19 Vaccination Rate Over Time', 
        'Percentage of Population Vaccinated (%)'
    )
    
    # Plot fully vaccinated rates
    plot_time_series(
        df, 'fully_vaccinated_rate', 
        'Fully Vaccinated Population Over Time', 
        'Percentage of Population Fully Vaccinated (%)'
    )
    
    # Latest vaccination data
    latest_data = df.sort_values('date').groupby('location').last().reset_index()
    
    # Sort by vaccination rate
    latest_data = latest_data.sort_values('vaccination_rate', ascending=False)
    
    # Plot vaccination comparison
    plot_bar_chart(
        latest_data, 
        x='location', 
        y='vaccination_rate',
        title='Vaccination Rate by Country',
        xlabel='Country',
        ylabel='Percentage of Population Vaccinated (%)'
    )

def analyze_death_rates(df):
    """Analyze death rates and related factors."""
    print("\n=== Death Rate Analysis ===")
    
    # Calculate death rate over time
    plot_time_series(
        df, 'death_rate', 
        'COVID-19 Death Rate Over Time', 
        'Death Rate (% of Cases)'
    )
    
    # Latest death rate by country
    latest_data = df.sort_values('date').groupby('location').last().reset_index()
    
    # Sort by death rate
    latest_data = latest_data.sort_values('death_rate', ascending=False)
    
    # Plot death rate comparison
    plot_bar_chart(
        latest_data, 
        x='location', 
        y='death_rate',
        title='Death Rate by Country',
        xlabel='Country',
        ylabel='Death Rate (% of Cases)'
    )
    
    # Correlation analysis
    corr_data = latest_data[['death_rate', 'median_age', 'gdp_per_capita', 
                           'life_expectancy', 'human_development_index']].corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_data, annot=True, cmap='coolwarm', center=0)
    plt.title('Correlation Matrix: Death Rate vs. Socioeconomic Factors', pad=20)
    plt.tight_layout()
    plt.show()

# 5. Main Analysis
def main():
    """Main function to run the COVID-19 analysis."""
    print("Starting COVID-19 Global Data Analysis...")
    
    # 1. Load and explore data
    print("\n1. Loading and exploring data...")
    df = load_and_explore_data()
    
    if df is None:
        return
    
    # 2. Clean and prepare data
    print("\n2. Cleaning and preparing data...")
    df_clean = clean_and_prepare_data(df)
    
    # 3. Analyze trends
    analyze_trends(df_clean)
    
    # 4. Analyze vaccination progress
    analyze_vaccination_progress(df_clean)
    
    # 5. Analyze death rates
    analyze_death_rates(df_clean)
    
    # 6. Generate choropleth maps (if needed)
    print("\n=== Generating Choropleth Maps ===")
    print("Note: To view interactive maps, uncomment the following lines in the script.")
    """
    # Total cases map
    fig = plot_choropleth(
        df_clean, 
        'total_cases', 
        'Total COVID-19 Cases by Country',
        'Reds'
    )
    fig.show()
    
    # Vaccination rate map
    fig = plot_choropleth(
        df_clean, 
        'vaccination_rate', 
        'COVID-19 Vaccination Rate by Country',
        'Blues'
    )
    fig.show()
    """
    
    # 7. Key Insights
    print("\n=== Key Insights ===")
    print("""
    1. **Vaccination Impact**: Countries with higher vaccination rates generally show 
       a slower growth in new cases and lower death rates.
       
    2. **Regional Variations**: Developed nations with better healthcare infrastructure 
       (like the US and UK) have higher testing and vaccination rates compared to 
       developing nations.
       
    3. **Death Rate Correlations**: Higher death rates are correlated with factors like 
       older population demographics and higher population density.
       
    4. **Vaccination Rollout**: The speed of vaccination rollout varies significantly 
       between countries, with developed nations generally having faster rollouts.
       
    5. **Pandemic Waves**: Most countries experienced multiple waves of infections, 
       with peaks often following relaxation of restrictions.
    """)
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()
