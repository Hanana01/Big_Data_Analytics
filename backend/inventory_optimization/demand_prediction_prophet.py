import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from prophet import Prophet
from sklearn.metrics import (
    mean_absolute_error, mean_absolute_percentage_error,
    mean_squared_error, r2_score
)

def evaluate(y_true, y_pred):
    metrics = {
        'MAE': mean_absolute_error(y_true, y_pred),
        'MAPE (%)': mean_absolute_percentage_error(y_true[y_true > 0], y_pred[y_true > 0]) * 100,
        'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
        'R² Score': r2_score(y_true, y_pred),
        'Perfect Predictions': sum(np.round(y_true) == np.round(y_pred)),
        'Perfect Prediction Rate': f"{100 * sum(np.round(y_true) == np.round(y_pred)) / len(y_true):.2f}%"
    }
    print("\nModel Evaluation (Prophet):")
    for k, v in metrics.items():
        print(f"{k}: {v}")
    return metrics

def run_prophet_forecast(filepath):
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])

    product_id = input("Enter Product ID to forecast (Prophet): ")
    product_id = int(product_id)
    product_df = df[df['Product ID'] == product_id][['Date', 'Demand']].rename(columns={"Date": "ds", "Demand": "y"})

    if product_df.empty:
        print("No data found for this Product ID.")
        return

    model = Prophet()
    model.fit(product_df)

    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    merged = product_df.merge(forecast[['ds', 'yhat']], on='ds', how='left')
    merged.dropna(inplace=True)

    evaluate(merged['y'], merged['yhat'])

    plt.figure(figsize=(14, 6))
    plt.plot(merged['ds'], merged['y'], label='Actual')
    plt.plot(merged['ds'], merged['yhat'], label='Predicted')
    plt.axvline(x=merged['ds'].max() - pd.Timedelta(days=30), color='gray', linestyle='--')
    plt.title(f'Prophet Forecast - Product {product_id}')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"prophet_forecast_product_{product_id}.png", dpi=300)
    plt.show()

if __name__ == "__main__":
    run_prophet_forecast("ecommerce_demand_data.csv")
