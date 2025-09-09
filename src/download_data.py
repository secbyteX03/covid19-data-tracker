import os
import pandas as pd
import requests
from pathlib import Path
import zipfile
import io

def download_covid_data():
    """
    Download the latest COVID-19 data from Kaggle
    """
    # Create data directory if it doesn't exist
    data_dir = Path(__file__).parent.parent / 'data'
    data_dir.mkdir(exist_ok=True)
    
    # Kaggle dataset URL
    kaggle_url = 'https://www.kaggle.com/datasets/kalilurrahman/covid19-coronavirus-dataset-by-owid/download?datasetVersionNumber=1'
    
    # Local file path
    zip_path = data_dir / 'covid19-data.zip'
    csv_path = data_dir / 'owid-covid-data.csv'
    
    try:
        print("Note: To download the dataset, please follow these steps:")
        print("1. Visit: https://www.kaggle.com/datasets/kalilurrahman/covid19-coronavirus-dataset-by-owid")
        print("2. Click the 'Download' button (requires Kaggle login)")
        print(f"3. Save the zip file to: {zip_path}")
        print("4. The script will extract and process the data")
        
        # Check if zip file exists
        if not zip_path.exists():
            print("\nError: Dataset zip file not found.")
            print(f"Please download the dataset and save it as: {zip_path}")
            return False
            
        # Extract the zip file
        print(f"\nExtracting data from {zip_path}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(data_dir)
        
        # Check if the CSV was extracted
        if not csv_path.exists():
            print("Error: Could not find owid-covid-data.csv in the downloaded zip file.")
            return False
            
        print(f"\nData successfully extracted to: {csv_path}")
        
        # Load and verify the data
        try:
            df = pd.read_csv(csv_path)
            print(f"\nDataset loaded successfully with {len(df)} rows and {len(df.columns)} columns.")
            print("\nFirst few rows:")
            print(df.head())
            return True
            
        except Exception as e:
            print(f"Error reading the CSV file: {e}")
            return False
            
    except Exception as e:
        print(f"Error processing the dataset: {e}")
        return False

def load_covid_data():
    """Load the COVID-19 data from the local file."""
    data_dir = Path(__file__).parent.parent / 'data'
    csv_path = data_dir / 'owid-covid-data.csv'
    
    if not csv_path.exists():
        print(f"Error: Data file not found at {csv_path}")
        print("Please run download_covid_data() first to download the dataset.")
        return None
        
    try:
        return pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error loading the dataset: {e}")
        return None

if __name__ == "__main__":
    download_covid_data()
