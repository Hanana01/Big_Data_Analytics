import pandas as pd
from sklearn.impute import SimpleImputer

# Load the dataset
df = pd.read_csv('./data/inventory_data.csv')

# Drop Product Name
df.drop(columns=['Product Name'], inplace=True)


# Handle missing values for numerical columns
numerical_cols = ['Inventory Level', 'Units Ordered', 'Demand', 'Price', 'Discount',
                  'Competitor Pricing', 'Holding Cost per Unit', 'Lead Time (Days)','Ordering Cost']
imputer = SimpleImputer(strategy='mean')
df[numerical_cols] = imputer.fit_transform(df[numerical_cols])

# Encode Category
category_map = {'Accessories': 1, 'Clothing': 2, 'Outerwear': 3}
df['Category'] = df['Category'].map(category_map)

# Encode Region
region_map = {'North': 1, 'South': 2, 'East': 3, 'West': 4}
df['Region'] = df['Region'].map(region_map)

# Encode Weather Condition
weather_map = {'Sunny': 1, 'Cloudy': 2, 'Rainy': 3, 'Snowy': 4}
df['Weather Condition'] = df['Weather Condition'].map(weather_map)

# Encode Holiday/Promotion (already 0 or 1)
df['Holiday/Promotion'] = df['Holiday/Promotion'].astype(int)

# Encode Seasonality
season_map = {'Spring': 1, 'Summer': 2, 'Autumn': 3, 'Winter': 4}
df['Seasonality'] = df['Seasonality'].map(season_map)

# Check the result
print(df.head())

# Save the preprocessed dataset
df.to_csv('./data/ecommerce_demand_data.csv', index=False)
