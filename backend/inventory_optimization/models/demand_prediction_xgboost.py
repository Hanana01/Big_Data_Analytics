import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    r2_score
)
from xgboost import XGBRegressor
import joblib
import matplotlib.pyplot as plt
from sklearn.preprocessing import RobustScaler
from sklearn.pipeline import Pipeline

def load_data(filepath):
    # Load dataset from CSV and create date-related features
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])

    # Create temporal features for better time series modeling
    df['DayOfWeek'] = df['Date'].dt.dayofweek
    df['DayOfMonth'] = df['Date'].dt.day
    df['WeekOfYear'] = df['Date'].dt.isocalendar().week.astype(int)
    df['Quarter'] = df['Date'].dt.quarter

    # Sort data by Product and Date for lag features
    df = df.sort_values(['Product ID', 'Date']).reset_index(drop=True)

    # Lag features: previous day demand and demand one week ago
    df['Demand_t-1'] = df.groupby('Product ID')['Demand'].shift(1)
    df['Demand_t-7'] = df.groupby('Product ID')['Demand'].shift(7)

    # Rolling window features: mean and std demand of last 7 days per product
    df['RollingMean_7'] = df.groupby('Product ID')['Demand'].rolling(7).mean().reset_index(0, drop=True)
    df['RollingStd_7'] = df.groupby('Product ID')['Demand'].rolling(7).std().reset_index(0, drop=True)

    # Drop rows with NaN values created by lag and rolling window calculations
    df.dropna(inplace=True)
    return df

def train_model(X_train, y_train):
    # Build pipeline with robust scaler and XGBoost regressor
    pipeline = Pipeline([
        ('scaler', RobustScaler()),
        ('xgb', XGBRegressor(random_state=42))
    ])

    # Hyperparameter grid for tuning
    param_grid = {
        'xgb__n_estimators': [20],
        'xgb__max_depth': [2],
        'xgb__learning_rate': [0.3],
        'xgb__subsample': [0.3],
        'xgb__colsample_bytree': [0.3],
        'xgb__reg_alpha': [20],
        'xgb__reg_lambda': [20]
    }

    # Grid search with 3-fold CV optimizing for negative mean absolute error
    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        cv=3,
        scoring='neg_mean_absolute_error',
        n_jobs=-1,
        verbose=1
    )

    print("Training XGBoost model...")
    grid_search.fit(X_train, y_train)
    print("Best parameters:", grid_search.best_params_)
    return grid_search.best_estimator_

def calculate_metrics(y_true, y_pred):
    # Calculate and print common regression metrics
    metrics = {
        'MAE': mean_absolute_error(y_true, y_pred),
        'MAPE (%)': mean_absolute_percentage_error(y_true[y_true > 0], y_pred[y_true > 0]) * 100,
        'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
        'R² Score': r2_score(y_true, y_pred),
    }

    print("\nXGBoost Model Evaluation:")
    for k, v in metrics.items():
        print(f"{k}: {v}")
    return metrics

def generate_predictions(model, df, X, y):
    # Generate predictions and calculate errors on a dataframe
    df = df.copy()
    df['Predicted_Demand_Raw'] = model.predict(X)
    df['Predicted_Demand'] = np.round(df['Predicted_Demand_Raw'])
    df['Absolute_Error'] = np.abs(y - df['Predicted_Demand'])
    df['Percentage_Error'] = np.where(
        y > 0,
        (df['Absolute_Error'] / y) * 100,
        np.nan
    )
    return df

if __name__ == "__main__":
    DATA_PATH = "../data/ecommerce_demand_data.csv"            
    MODEL_PATH = "xgboost_advanced_model.pkl"                    
    TEST_PREDICTIONS_PATH = "../data/xgboost_testset_predictions.csv"  

    print("Loading and preprocessing data...")
    df = load_data(DATA_PATH)  # Load and preprocess data

    # Time-based train-test split (80% train, 20% test) to avoid leakage
    df_sorted = df.sort_values('Date').reset_index(drop=True)
    split_index = int(len(df_sorted) * 0.8)

    train_df = df_sorted.iloc[:split_index]
    test_df = df_sorted.iloc[split_index:]

    # Prepare features and targets, dropping columns not used in training
    X_train = train_df.drop(columns=['Demand','Units Sold','Units Ordered','Inventory Level'])
    y_train = train_df['Demand']
    X_test = test_df.drop(columns=['Demand','Units Sold','Units Ordered','Inventory Level'])
    y_test = test_df['Demand']

    # Train the model and save it
    model = train_model(X_train, y_train)
    joblib.dump(model, MODEL_PATH)

    # Evaluate model on test set
    y_pred = model.predict(X_test)
    y_pred_rounded = np.round(y_pred)
    y_true_rounded = np.round(y_test)
    calculate_metrics(y_true_rounded, y_pred_rounded)

    # Drop unnecessary columns before saving predictions
    drop_cols = ['Demand_t-1', 'Demand_t-7', 'RollingMean_7', 'RollingStd_7',
                 'Predicted_Demand_Raw', 'Absolute_Error', 'Percentage_Error']

    # Save test set predictions with error calculations
    test_predictions_df = test_df.copy()
    test_predictions_df['Predicted_Demand_Raw'] = y_pred
    test_predictions_df['Predicted_Demand'] = y_pred_rounded
    test_predictions_df['Absolute_Error'] = np.abs(y_test - y_pred_rounded)
    test_predictions_df['Percentage_Error'] = np.where(
        y_test > 0,
        (test_predictions_df['Absolute_Error'] / y_test) * 100,
        np.nan
    )
    test_predictions_df = test_predictions_df.drop(columns=[c for c in drop_cols if c in test_predictions_df.columns])
    test_predictions_df.to_csv(TEST_PREDICTIONS_PATH, index=False)
    print(f"\nTest set predictions saved to {TEST_PREDICTIONS_PATH}")

    # Generate predictions on full dataset for visualization or further use
    print("\nGenerating predictions for full dataset...")
    features_full = df.drop(columns=['Demand', 'Date', 'Product ID','Units Sold','Units Ordered','Inventory Level'])
    # (You can add code here if you want to use these predictions)

    # Visualization for the last 30 days demand prediction for a specific product
    product_id_input = input("Enter the Product ID to predict last 30 days demand for: ")
    try:
        product_id = int(product_id_input)
    except ValueError:
        print("Invalid Product ID entered. Exiting.")
        exit(1)

    df_product = df[df['Product ID'] == product_id].copy()
    if df_product.empty:
        print(f"No data found for Product ID {product_id}. Exiting.")
        exit(1)

    # Filter last 30 days data for selected product
    last_30_days = df_product[df_product['Date'] >= (df_product['Date'].max() - pd.Timedelta(days=29))].copy()
    if last_30_days.empty:
        print(f"No data available for the last 30 days for Product ID {product_id}. Exiting.")
        exit(1)

    X_last_30 = last_30_days.drop(columns=['Demand','Units Sold','Units Ordered','Inventory Level'])
    y_last_30 = last_30_days['Demand']
    y_pred_last_30 = model.predict(X_last_30)
    y_pred_last_30_rounded = np.round(y_pred_last_30)

    # Plot actual vs predicted demand for last 30 days
    plt.figure(figsize=(14, 7))
    plt.plot(last_30_days['Date'], y_last_30, label='Actual Demand', marker='o')
    plt.plot(last_30_days['Date'], y_pred_last_30_rounded, label='Predicted Demand', marker='x')
    plt.xticks(rotation=45)
    plt.xlabel('Date')
    plt.ylabel('Demand')
    plt.title(f'Actual vs Predicted Demand - Last 30 Days - Product {product_id}')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"../images/last_30_days_demand_prediction_product_{product_id}.png", dpi=300)
    plt.show()

    print(f"\nLast 30 days prediction visualization saved as last_30_days_demand_prediction_product_{product_id}.png")
    print("\nTraining complete. Files saved:")
    print(f"- {MODEL_PATH}")
    print(f"- {TEST_PREDICTIONS_PATH}")
    print(f"- last_30_days_demand_prediction_product_{product_id}.png")
