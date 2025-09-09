# dashboard.py - Enhanced Version
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
import os

# Set page config
st.set_page_config(
    page_title="COVID-19 Advanced Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stApp { max-width: 1800px; margin: 0 auto; }
    .stMetric { background-color: white; border-radius: 10px; padding: 15px; margin: 5px; }
    .stPlotlyChart { background-color: white; border-radius: 10px; padding: 15px; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { height: 50px; }
    </style>
""", unsafe_allow_html=True)

# Load and preprocess data
@st.cache_data
def load_data():
    try:
        data_path = os.path.join('data', 'owid-covid-data.csv')
        if not os.path.exists(data_path):
            st.error(f"Data file not found at: {os.path.abspath(data_path)}")
            return None
            
        df = pd.read_csv(data_path)
        df['date'] = pd.to_datetime(df['date'])
        
        # Calculate additional metrics with error handling
        df['mortality_rate'] = (df['total_deaths'] / df['total_cases']) * 100
        
        # Calculate recovery rate (approximate if recoveries data isn't available)
        if 'total_recoveries' in df.columns:
            df['recovery_rate'] = (df['total_cases'] - df['total_deaths']) / df['total_cases'] * 100
            df['active_cases'] = df['total_cases'] - df['total_deaths'] - df['total_recoveries']
        else:
            # If recoveries data isn't available, estimate active cases
            df['recovery_rate'] = (df['total_cases'] - df['total_deaths']) / df['total_cases'] * 100
            df['active_cases'] = df['total_cases'] - df['total_deaths']
            
        df['case_fatality_ratio'] = (df['total_deaths'] / df['total_cases']) * 100
        
        # Add wave detection with error handling
        try:
            df = detect_waves(df)
        except Exception as e:
            st.warning(f"Wave detection skipped: {str(e)}")
            
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}\n\nPlease ensure the data file exists at: {os.path.abspath(data_path) if 'data_path' in locals() else 'data/owid-covid-data.csv'}")
        return None

def detect_waves(df, window=30):
    """Detect COVID-19 waves based on new cases"""
    df = df.sort_values(['location', 'date'])
    df['new_cases_ma'] = df.groupby('location')['new_cases'].transform(
        lambda x: x.rolling(window=window, min_periods=1).mean()
    )
    df['wave'] = df.groupby('location')['new_cases_ma'].transform(
        lambda x: (x.diff() > 0).cumsum()
    )
    return df

def train_prediction_model(df, country, metric='new_cases', days=30):
    """Train a simple prediction model"""
    try:
        country_df = df[df['location'] == country].dropna(subset=[metric])
        if len(country_df) < 10:
            return None
            
        X = np.arange(len(country_df)).reshape(-1, 1)
        y = country_df[metric].values
        
        # Use polynomial regression
        model = make_pipeline(
            PolynomialFeatures(degree=3),
            LinearRegression()
        )
        model.fit(X, y)
        
        # Predict next 'days' days
        future_X = np.arange(len(country_df), len(country_df) + days).reshape(-1, 1)
        future_dates = pd.date_range(
            start=country_df['date'].iloc[-1],
            periods=days + 1
        )[1:]
        
        predictions = model.predict(future_X)
        return future_dates, predictions
    except:
        return None

# Main app
def main():
    st.title("🌍 Advanced COVID-19 Analytics Dashboard")
    
    # Load data
    df = load_data()
    if df is None:
        st.error("Failed to load data. Please check the data file.")
        return
        
    # Sidebar
    st.sidebar.header("Dashboard Controls")
    
    # Country selection
    countries = sorted(df['location'].unique())
    selected_countries = st.sidebar.multiselect(
        "Select Countries",
        options=countries,
        default=['United States', 'India', 'Brazil', 'United Kingdom', 'Kenya'],
        max_selections=5
    )
    
    # Date range selection
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(max_date - timedelta(days=180), max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Metric selection
    metric_categories = {
        'Cases': ['new_cases', 'total_cases', 'new_cases_smoothed', 'active_cases'],
        'Deaths': ['new_deaths', 'total_deaths', 'new_deaths_smoothed', 'mortality_rate'],
        'Vaccinations': ['people_vaccinated', 'people_fully_vaccinated', 'total_vaccinations'],
        'Healthcare': ['icu_patients', 'hosp_patients', 'weekly_icu_admissions'],
        'Demographics': ['population_density', 'median_age', 'aged_65_older']
    }
    
    selected_category = st.sidebar.selectbox("Select Metric Category", list(metric_categories.keys()))
    selected_metric = st.sidebar.selectbox("Select Metric", metric_categories[selected_category])
    
    # Filter data
    start_date, end_date = date_range if len(date_range) == 2 else (min_date, max_date)
    filtered_df = df[
        (df['location'].isin(selected_countries)) & 
        (df['date'].between(pd.to_datetime(start_date), pd.to_datetime(end_date)))
    ]
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", 
        "📈 Trends & Predictions", 
        "🌐 Geographic Analysis",
        "📥 Export Data"
    ])
    
    with tab1:  # Overview tab
        st.header("Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        latest_data = filtered_df[filtered_df['date'] == filtered_df['date'].max()]
        
        with col1:
            st.metric("Total Countries", len(selected_countries))
        with col2:
            st.metric("Date Range", f"{start_date.strftime('%b %d, %Y')} to {end_date.strftime('%b %d, %Y')}")
        with col3:
            st.metric("Latest Data", latest_data['date'].iloc[0].strftime('%b %d, %Y'))
        with col4:
            if selected_metric in latest_data.columns:
                total = latest_data[selected_metric].sum()
                st.metric(f"Total {selected_metric.replace('_', ' ').title()}", f"{total:,.0f}")
        
        # Time series chart
        st.subheader("Time Series Analysis")
        fig = px.line(
            filtered_df,
            x='date',
            y=selected_metric,
            color='location',
            title=f"{selected_metric.replace('_', ' ').title()} Over Time",
            labels={'date': 'Date', selected_metric: selected_metric.replace('_', ' ').title()},
            hover_data={
                'date': '|%b %d, %Y',
                selected_metric: ':.2f',
                'location': True
            }
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Metrics comparison
        st.subheader("Metrics Comparison")
        metrics_to_compare = st.multiselect(
            "Select up to 3 metrics to compare",
            options=[m for sublist in metric_categories.values() for m in sublist],
            default=[selected_metric],
            max_selections=3
        )
        
        if metrics_to_compare:
            fig = go.Figure()
            for metric in metrics_to_compare:
                for country in selected_countries:
                    country_data = filtered_df[filtered_df['location'] == country]
                    fig.add_trace(go.Scatter(
                        x=country_data['date'],
                        y=country_data[metric],
                        name=f"{country} - {metric.replace('_', ' ').title()}",
                        mode='lines'
                    ))
            fig.update_layout(
                title="Multiple Metrics Comparison",
                xaxis_title="Date",
                yaxis_title="Value",
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:  # Trends & Predictions
        st.header("Trend Analysis & Predictions")
        
        # Prediction section
        st.subheader("30-Day Prediction")
        pred_country = st.selectbox("Select Country for Prediction", selected_countries)
        
        if st.button("Generate Prediction"):
            with st.spinner("Training prediction model..."):
                future_dates, predictions = train_prediction_model(
                    df, pred_country, selected_metric
                )
                
                if future_dates is not None:
                    # Get historical data
                    hist_data = filtered_df[filtered_df['location'] == pred_country]
                    
                    # Create figure
                    fig = go.Figure()
                    
                    # Add historical data
                    fig.add_trace(go.Scatter(
                        x=hist_data['date'],
                        y=hist_data[selected_metric],
                        name='Historical Data',
                        line=dict(color='blue')
                    ))
                    
                    # Add prediction
                    fig.add_trace(go.Scatter(
                        x=future_dates,
                        y=predictions,
                        name='Prediction',
                        line=dict(color='red', dash='dash')
                    ))
                    
                    # Update layout
                    fig.update_layout(
                        title=f"30-Day {selected_metric.replace('_', ' ').title()} Prediction for {pred_country}",
                        xaxis_title="Date",
                        yaxis_title=selected_metric.replace('_', ' ').title(),
                        hovermode="x unified"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show prediction metrics
                    last_actual = hist_data[selected_metric].iloc[-1]
                    pred_change = ((predictions[-1] - last_actual) / last_actual) * 100
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Last Actual Value", f"{last_actual:,.2f}")
                    with col2:
                        st.metric(
                            f"Predicted in 30 Days", 
                            f"{predictions[-1]:,.2f}",
                            delta=f"{pred_change:.2f}%"
                        )
                else:
                    st.warning("Not enough data to generate prediction for this country and metric.")
        
        # Wave analysis
        st.subheader("Pandemic Wave Analysis")
        wave_country = st.selectbox("Select Country for Wave Analysis", selected_countries)
        
        wave_data = df[df['location'] == wave_country].copy()
        if not wave_data.empty:
            fig = px.line(
                wave_data,
                x='date',
                y='new_cases_ma',
                title=f"COVID-19 Waves in {wave_country}",
                labels={'new_cases_ma': '7-Day Moving Average of New Cases', 'date': 'Date'}
            )
            
            # Add wave annotations
            waves = wave_data.groupby('wave')['date'].agg(['min', 'max'])
            for _, wave in waves.iterrows():
                fig.add_vrect(
                    x0=wave['min'], x1=wave['max'],
                    fillcolor="lightgray", opacity=0.2,
                    layer="below", line_width=0
                )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:  # Geographic Analysis
        st.header("Geographic Analysis")
        
        # World map
        st.subheader("Global Distribution")
        latest_global = df[df['date'] == df['date'].max()]
        
        fig = px.choropleth(
            latest_global,
            locations='location',
            locationmode='country names',
            color=selected_metric,
            hover_name='location',
            color_continuous_scale='Viridis',
            title=f'Global {selected_metric.replace("_", " ").title()} as of {latest_global["date"].iloc[0].strftime("%b %d, %Y")}',
            labels={selected_metric: selected_metric.replace('_', ' ').title()},
            hover_data={
                selected_metric: ':.2f',
                'population': ':,.0f',
                'date': False
            }
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Scatter plot for correlation analysis
        st.subheader("Correlation Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            x_axis = st.selectbox(
                "X-Axis",
                options=['population_density', 'median_age', 'gdp_per_capita', 'life_expectancy'],
                index=0
            )
        
        with col2:
            y_axis = st.selectbox(
                "Y-Axis",
                options=['total_cases_per_million', 'total_deaths_per_million', 'people_fully_vaccinated_per_hundred'],
                index=0
            )
        
        if x_axis and y_axis:
            fig = px.scatter(
                latest_global,
                x=x_axis,
                y=y_axis,
                color='continent',
                size='population',
                hover_name='location',
                log_x=True,
                log_y=True,
                title=f"{x_axis.replace('_', ' ').title()} vs {y_axis.replace('_', ' ').title()}",
                labels={
                    x_axis: x_axis.replace('_', ' ').title(),
                    y_axis: y_axis.replace('_', ' ').title(),
                    'continent': 'Continent'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:  # Export Data
        st.header("Export Data")
        
        st.subheader("Filtered Data")
        st.dataframe(
            filtered_df,
            column_config={
                'date': st.column_config.DateColumn('Date'),
                'location': 'Country',
                'total_cases': st.column_config.NumberColumn('Total Cases', format='%,d'),
                'total_deaths': st.column_config.NumberColumn('Total Deaths', format='%,d')
            },
            use_container_width=True
        )
        
        # Export options
        export_format = st.selectbox("Select Export Format", ['CSV', 'Excel', 'JSON'])
        filename = st.text_input("Filename", "covid19_data_export")
        
        if st.button("Export Data"):
            try:
                if export_format == 'CSV':
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"{filename}.csv",
                        mime="text/csv"
                    )
                elif export_format == 'Excel':
                    excel = filtered_df.to_excel(f"{filename}.xlsx", index=False)
                    with open(f"{filename}.xlsx", "rb") as f:
                        st.download_button(
                            label="Download Excel",
                            data=f,
                            file_name=f"{filename}.xlsx",
                            mime="application/vnd.ms-excel"
                        )
                elif export_format == 'JSON':
                    json_data = filtered_df.to_json(orient="records")
                    st.download_button(
                        label="Download JSON",
                        data=json_data,
                        file_name=f"{filename}.json",
                        mime="application/json"
                    )
                st.success("Export completed successfully!")
            except Exception as e:
                st.error(f"Error during export: {str(e)}")
    
    # Add footer
    st.markdown("---")
    st.markdown("""
    ### 📝 Data Sources and Notes
    - **Data Source:** [Our World in Data](https://ourworldindata.org/coronavirus)
    - **Last Updated:** {}
    - **Note:** All metrics are based on the latest available data for the selected date range.
    """.format(max_date.strftime("%B %d, %Y")))

if __name__ == "__main__":
    main()