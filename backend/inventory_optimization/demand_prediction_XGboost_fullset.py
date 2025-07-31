import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
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
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])

    # Temporal features
    df['DayOfWeek'] = df['Date'].dt.dayofweek
    df['DayOfMonth'] = df['Date'].dt.day
    df['WeekOfYear'] = df['Date'].dt.isocalendar().week.astype(int)
    df['Quarter'] = df['Date'].dt.quarter

    # Sort & create lags/rolling
    df = df.sort_values(['Product ID', 'Date']).reset_index(drop=True)
    df['Demand_t-1'] = df.groupby('Product ID')['Demand'].shift(1)
    df['Demand_t-7'] = df.groupby('Product ID')['Demand'].shift(7)
    df['RollingMean_7'] = df.groupby('Product ID')['Demand'].rolling(7).mean().reset_index(0, drop=True)
    df['RollingStd_7'] = df.groupby('Product ID')['Demand'].rolling(7).std().reset_index(0, drop=True)

    df.dropna(inplace=True)
    return df

def train_model(X_train, y_train):
    pipeline = Pipeline([
        ('scaler', RobustScaler()),
        ('xgb', XGBRegressor(random_state=42))
    ])

    param_grid = {
        'xgb__n_estimators': [300],
        'xgb__max_depth': [6, 9],
        'xgb__learning_rate': [0.05],
        'xgb__subsample': [0.8],
        'xgb__colsample_bytree': [0.8]
    }

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
    metrics = {
        'MAE': mean_absolute_error(y_true, y_pred),
        'MAPE (%)': mean_absolute_percentage_error(y_true[y_true > 0], y_pred[y_true > 0]) * 100,
        'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
        'R² Score': r2_score(y_true, y_pred),
        'Perfect Predictions': sum(y_true == y_pred),
        'Perfect Prediction Rate': f"{100 * sum(y_true == y_pred)/len(y_true):.2f}%"
    }

    print("\nModel Evaluation:")
    for k, v in metrics.items():
        print(f"{k}: {v}")
    return metrics

if __name__ == "__main__":
    DATA_PATH = "../data/ecommerce_demand_data.csv"
    OUTPUT_TEST_CSV = "xgboost_full_test_predictions.csv"
    MODEL_PATH = "xgboost_advanced_model.pkl"
    FEATURE_IMPORTANCE_PATH = "xgboost_advanced_feature_importance.png"

    print("Loading and preprocessing data...")
    df = load_data(DATA_PATH)

    target = df['Demand']
    features = df.drop(columns=['Demand', 'Date', 'Product ID'])

    X_train, X_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42
    )

    model = train_model(X_train, y_train)
    joblib.dump(model, MODEL_PATH)

    y_pred = model.predict(X_test)
    y_pred_rounded = np.round(y_pred)
    y_true_rounded = np.round(y_test)
    calculate_metrics(y_true_rounded, y_pred_rounded)

    # Merge test set with original Product ID and Date
    df_features = df.drop(columns=['Demand'])
    X_test_full = df_features.loc[X_test.index].copy()

    X_test_full['Actual_Demand'] = y_test.values
    X_test_full['Predicted_Demand'] = y_pred_rounded
    X_test_full['Absolute_Error'] = np.abs(X_test_full['Actual_Demand'] - X_test_full['Predicted_Demand'])
    X_test_full['Percentage_Error'] = np.where(
        X_test_full['Actual_Demand'] > 0,
        (X_test_full['Absolute_Error'] / X_test_full['Actual_Demand']) * 100,
        np.nan
    )

    X_test_full.to_csv(OUTPUT_TEST_CSV, index=False)
    print(f"\nTest predictions saved to {OUTPUT_TEST_CSV}")

    # Feature importance
    plt.figure(figsize=(12, 8))
    feat_importances = pd.Series(
        model.named_steps['xgb'].feature_importances_,
        index=features.columns
    )
    feat_importances.nlargest(15).plot(kind='barh')
    plt.title('XGBoost Feature Importance')
    plt.tight_layout()
    plt.savefig(FEATURE_IMPORTANCE_PATH, dpi=300)
    plt.close()

    # Visualization for selected Product ID from test set
    try:
        product_id_input = input("Enter Product ID to visualize full test predictions: ")
        product_id = int(product_id_input)
    except ValueError:
        print("Invalid Product ID entered. Exiting.")
        exit(1)

    product_test = X_test_full[X_test_full['Product ID'] == product_id]

    if product_test.empty:
        print(f"No test data for Product ID {product_id}. Exiting.")
        exit(1)

    product_test = product_test.sort_values('Date')

    plt.figure(figsize=(14, 6))
    plt.plot(product_test['Date'], product_test['Actual_Demand'], label='Actual Demand', marker='o')
    plt.plot(product_test['Date'], product_test['Predicted_Demand'], label='Predicted Demand', marker='x')
    plt.xticks(rotation=45)
    plt.title(f"Actual vs Predicted Demand - Full Test Set - Product {product_id}")
    plt.xlabel("Date")
    plt.ylabel("Demand")
    plt.legend()
    plt.tight_layout()
    plot_path = f"full_test_demand_prediction_product_{product_id}.png"
    plt.savefig(plot_path, dpi=300)
    plt.show()

    print(f"\nPrediction visualization saved as {plot_path}")