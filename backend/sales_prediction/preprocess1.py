import pandas as pd

def clean_sales():
    # Load the raw sales data CSV
    df = pd.read_csv("data/sales.csv")

    # Clean up column names (remove spaces, replace with underscores)
    df.columns = [col.strip().replace(" ", "_") for col in df.columns]

    # Rename columns for time series (Prophet style)
    df = df.rename(columns={
        'Date': 'ds',
        'Units_Sold': 'y'
    })

    # Convert ds to datetime
    df['ds'] = pd.to_datetime(df['ds'], format="%m/%d/%Y")

    # Encode Weather_Condition to numeric codes
    weather_map = {'Sunny': 0, 'Rainy': 1, 'Cloudy': 2, 'Snowy': 3}
    df['Weather_Code'] = df['Weather_Condition'].map(weather_map)

    # Encode Seasonality
    season_map = {'Spring': 0, 'Summer': 1, 'Autumn': 2, 'Winter': 3}
    df['Seasonality_Code'] = df['Seasonality'].map(season_map)

    # Encode Region
    region_map = {'North': 0, 'South': 1, 'East': 2, 'West': 3}
    df['Region_Code'] = df['Region'].map(region_map)

    # Encode Category
    category_map = {'Outerwear': 0, 'Clothing': 1, 'Accessories': 2}
    df['Category_Code'] = df['Category'].map(category_map)

    # Copy Holiday/Promotion column to Promotion (optional)
    df['Promotion'] = df['Holiday/Promotion']

    # Final cleaned dataframe with selected columns
    cleaned = df[['ds', 'Store_ID', 'Product_ID', 'Category_Code', 'Region_Code',
                  'y', 'Price', 'Discount',
                  'Weather_Code', 'Promotion', 'Competitor_Pricing',
                  'Seasonality_Code']]

    # Save to new CSV
    cleaned.to_csv("backend/data/cleaned_sales.csv", index=False)

    print("✅ Cleaned sales data saved as cleaned_sales.csv")

if __name__ == "__main__":
    clean_sales()
