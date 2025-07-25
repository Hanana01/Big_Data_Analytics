import pandas as pd

def clean_sales():
    # Correct path
    df = pd.read_csv("../data/sales.csv")

    df.columns = [col.strip().replace(" ", "_") for col in df.columns]
    df = df.rename(columns={'Date': 'ds', 'Units_Sold': 'y'})
    df['ds'] = pd.to_datetime(df['ds'], format="%m/%d/%Y")

    weather_map = {'Sunny': 0, 'Rainy': 1, 'Cloudy': 2, 'Snowy': 3}
    df['Weather_Code'] = df['Weather_Condition'].map(weather_map)

    season_map = {'Spring': 0, 'Summer': 1, 'Autumn': 2, 'Winter': 3}
    df['Seasonality_Code'] = df['Seasonality'].map(season_map)

    region_map = {'North': 0, 'South': 1, 'East': 2, 'West': 3}
    df['Region_Code'] = df['Region'].map(region_map)

    category_map = {'Outerwear': 0, 'Clothing': 1, 'Accessories': 2}
    df['Category_Code'] = df['Category'].map(category_map)

    df['Promotion'] = df['Holiday/Promotion']

    # ✅ Add Product Name (optional)
    product_names = [
        "Coat", "Hoodie", "Jacket", "Overcoat", "Blazer",
        "Blouse", "Shirt", "Jeans", "Trousers", "T-shirt",
        "Shorts", "Skirt", "Saree", "Bag", "Belt",
        "Gloves", "Fragrances", "Wristwear", "Sunglasses", "Hat"
    ]
    product_name_map = {i+1: name for i, name in enumerate(product_names)}
    df['Product_Name'] = df['Product_ID'].map(product_name_map)

    cleaned = df[['ds', 'Store_ID', 'Product_ID', 'Product_Name',
                  'Category_Code', 'Region_Code',
                  'y', 'Price', 'Discount',
                  'Weather_Code', 'Promotion', 'Competitor_Pricing',
                  'Seasonality_Code']]

    cleaned.to_csv("../data/cleaned_sales.csv", index=False)
    print("✅ Cleaned sales data saved as cleaned_sales.csv")

if __name__ == "__main__":
    clean_sales()
