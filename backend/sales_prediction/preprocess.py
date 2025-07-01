import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import os

def preprocess_data():
    # Load dataset
    current_dir = os.path.dirname(__file__)
    data_path = os.path.join(current_dir, 'data/sales.csv')
    df = pd.read_csv(data_path)

    # Drop irrelevant columns
    df.drop(columns=['Sales ID'], inplace=True)

    # Convert Date column to datetime format
    df['Date'] = pd.to_datetime(df['Date'])

    # Handle missing values
    df.fillna({
        'Price': df['Price'].median(),
        'Discount': df['Discount'].median(),
        'Weather Condition': df['Weather Condition'].mode()[0],
        'Holiday/Promotion': 0,
        'Competitor Pricing': df['Competitor Pricing'].median(),
        'Seasonality': df['Seasonality'].mode()[0]
    }, inplace=True)

    # Encode categorical variables
    categorical_cols = ['Store ID', 'Product ID', 'Category', 'Region', 'Weather Condition', 'Seasonality']
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le  # Store encoders for later use

    # Feature Engineering: Extract time-based features
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Weekday'] = df['Date'].dt.weekday
    df['Quarter'] = df['Date'].dt.quarter
    df['Is_Weekend'] = df['Weekday'].apply(lambda x: 1 if x >= 5 else 0)

    # Scaling numerical features
    numerical_cols = ['Price', 'Discount', 'Competitor Pricing']
    scaler = StandardScaler()
    df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

    # Save processed data
    processed_path = os.path.join(current_dir, 'data/processed_sales.csv')
    df.to_csv(processed_path, index=False)

    print("Preprocessing completed successfully!")

# Run preprocessing
if __name__ == '__main__':
    preprocess_data()
