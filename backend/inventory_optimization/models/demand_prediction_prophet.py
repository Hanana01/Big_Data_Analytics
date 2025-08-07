import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt

def load_data_prophet_all_features(filepath):

    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])

    # Temporal features based on date
    df['DayOfWeek'] = df['Date'].dt.dayofweek
    df['DayOfMonth'] = df['Date'].dt.day
    df['WeekOfYear'] = df['Date'].dt.isocalendar().week.astype(int)
    df['Quarter'] = df['Date'].dt.quarter

    # Sort by Product and Date for lag calculations
    df = df.sort_values(['Product ID', 'Date']).reset_index(drop=True)

    # Lag features: previous day and previous week demand
    df['Demand_t-1'] = df.groupby('Product ID')['Demand'].shift(1)
    df['Demand_t-7'] = df.groupby('Product ID')['Demand'].shift(7)

    # Rolling window statistics for demand (mean and std dev over past 7 days)
    df['RollingMean_7'] = df.groupby('Product ID')['Demand'].rolling(7).mean().reset_index(0, drop=True)
    df['RollingStd_7'] = df.groupby('Product ID')['Demand'].rolling(7).std().reset_index(0, drop=True)

    # Drop rows with missing values created by lags/rolling calculations
    df.dropna(inplace=True)

    # Categorical variables: convert to strings for get_dummies
    categorical_cols = ['Store ID', 'Category', 'Region', 'Weather Condition', 'Holiday/Promotion']
    for col in categorical_cols:
        df[col] = df[col].astype(str)

    # One-hot encode categorical columns to use as regressors in Prophet
    df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

    # Drop 'Units Sold' and 'Units Ordered' as features
    df_encoded = df_encoded.drop(columns=['Units Sold', 'Units Ordered'], errors='ignore')

    return df_encoded

def prepare_prophet_df_all_features(df, product_id):
    # Filter dataset for a specific product and prepare DataFrame for Prophet.

    df_product = df[df['Product ID'] == product_id].copy()
    if df_product.empty:
        raise ValueError(f"No data for Product ID {product_id}")

    # Rename for Prophet: ds = datetime, y = target variable
    df_product = df_product.rename(columns={'Date': 'ds', 'Demand': 'y'})

    exclude_cols = ['ds', 'y', 'Units Sold', 'Units Ordered','Inventory Level']
    regressors = [col for col in df_product.columns if col not in exclude_cols]

    df_prophet = df_product[['ds', 'y'] + regressors]
    return df_prophet, regressors

def train_prophet_model(df_prophet, regressors):
    """
    Instantiate and train Prophet model with additional regressors.
    """
    m = Prophet()

    for reg in regressors:
        m.add_regressor(reg)

    m.fit(df_prophet)
    return m

def predict_prophet(m, df_pred, regressors):
    forecast = m.predict(df_pred)
    y_pred = np.round(forecast['yhat'].values)
    return y_pred, forecast

def calculate_metrics(y_true, y_pred):

    mask = y_true > 0
    metrics = {
        'MAE': mean_absolute_error(y_true, y_pred),
        'MAPE (%)': mean_absolute_percentage_error(y_true[mask], y_pred[mask]) * 100,
        'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
        'R² Score': r2_score(y_true, y_pred),
    }
    print("\nProphet Model Evaluation:")
    for k, v in metrics.items():
        print(f"{k}: {v}")
    return metrics

if __name__ == "__main__":
    DATA_PATH = "../data/ecommerce_demand_data.csv"
    TEST_PREDICTIONS_PATH = "../data/prophet_testset_predictions.csv"

    print("Loading and preprocessing data...")
    df = load_data_prophet_all_features(DATA_PATH)

    df_sorted = df.sort_values('Date').reset_index(drop=True)
    split_index = int(len(df_sorted) * 0.8)
    train_df = df_sorted.iloc[:split_index]
    test_df = df_sorted.iloc[split_index:]

    product_id_input = input("Enter the Product ID to train and predict with Prophet: ")
    try:
        product_id = int(product_id_input)
    except ValueError:
        print("Invalid Product ID. Exiting.")
        exit(1)

    df_train, regressors = prepare_prophet_df_all_features(train_df, product_id)
    df_test, _ = prepare_prophet_df_all_features(test_df, product_id)

    print("Training Prophet model with all features...")
    model = train_prophet_model(df_train, regressors)

    print("Predicting on test set...")
    y_test_true = df_test['y'].values
    y_test_pred, forecast_test = predict_prophet(model, df_test, regressors)

    calculate_metrics(y_test_true, y_test_pred)

    df_test_out = df_test.copy()
    df_test_out['Predicted_Demand'] = y_test_pred
    df_test_out.to_csv(TEST_PREDICTIONS_PATH, index=False)
    print(f"Test predictions saved to {TEST_PREDICTIONS_PATH}")

    print("Generating full dataset predictions...")
    df_full, _ = prepare_prophet_df_all_features(df, product_id)
    y_full_pred, forecast_full = predict_prophet(model, df_full, regressors)

    df_full_out = df_full.copy()
    df_full_out['Predicted_Demand'] = y_full_pred

    last_30_days = df_full_out[df_full_out['ds'] >= (df_full_out['ds'].max() - pd.Timedelta(days=29))].copy()
    if last_30_days.empty:
        print("No last 30 days data available. Exiting.")
        exit(1)

    plt.figure(figsize=(14,7))
    plt.plot(last_30_days['ds'], last_30_days['y'], label='Actual Demand', marker='o')
    plt.plot(last_30_days['ds'], last_30_days['Predicted_Demand'], label='Predicted Demand', marker='x')
    plt.xticks(rotation=45)
    plt.xlabel('Date')
    plt.ylabel('Demand')
    plt.title(f'Actual vs Predicted Demand - Last 30 Days - Product {product_id}')
    plt.legend()
    plt.tight_layout()
    # plt.savefig(f"prophet_last_30_days_all_features_product_{product_id}.png", dpi=300)
    plt.show()

    print(f"Visualization saved as prophet_last_30_days_all_features_product_{product_id}.png")
