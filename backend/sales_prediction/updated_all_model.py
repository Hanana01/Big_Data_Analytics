import os
import pandas as pd
import numpy as np
from math import sqrt

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from statsmodels.tsa.statespace.sarimax import SARIMAX
from prophet import Prophet

from xgboost import XGBRegressor

import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

# === Load ===
df = pd.read_csv("data/cleaned_sales.csv")
df['ds'] = pd.to_datetime(df['ds'])
df = df.sort_values('ds')

# === Feature Engineering ===
df['y_lag1'] = df.groupby(['Store_ID', 'Product_ID'])['y'].shift(1)
df['y_lag7'] = df.groupby(['Store_ID', 'Product_ID'])['y'].shift(7)
df['y_roll7'] = df.groupby(['Store_ID', 'Product_ID'])['y'].transform(lambda x: x.rolling(7, min_periods=1).mean())
df['y_roll30'] = df.groupby(['Store_ID', 'Product_ID'])['y'].transform(lambda x: x.rolling(30, min_periods=1).mean())
df = df.dropna().reset_index(drop=True)

df['Store_ID_str'] = df['Store_ID'].astype(str)
df['Product_ID_str'] = df['Product_ID'].astype(str)
df['Store_ID_enc'] = df['Store_ID_str'].astype('category').cat.codes
df['Product_ID_enc'] = df['Product_ID_str'].astype('category').cat.codes

features = [
    'Store_ID_enc', 'Product_ID_enc', 'Category_Code', 'Region_Code',
    'Price', 'Discount', 'Weather_Code', 'Promotion',
    'Competitor_Pricing', 'Seasonality_Code',
    'y_lag1', 'y_lag7', 'y_roll7', 'y_roll30'
]
exog_cols = [
    'Price', 'Discount', 'Weather_Code', 'Promotion',
    'Competitor_Pricing', 'Seasonality_Code'
]

# === Make output folders ===
os.makedirs("results_per_product", exist_ok=True)
os.makedirs("accuracy_per_product", exist_ok=True)
os.makedirs("store_predictions", exist_ok=True)

accuracy_rows = []
groups = df.groupby(['Store_ID_str', 'Product_ID_str'])

lookback = 30

# === Safe eval ===
def eval(y_true, y_pred):
    mask = y_true != 0
    mae = mean_absolute_error(y_true, y_pred)
    rmse = sqrt(mean_squared_error(y_true, y_pred))
    if mask.sum() > 0:
        mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    else:
        mape = np.nan
    r2 = r2_score(y_true, y_pred)
    return mae, rmse, mape, r2

# === Loop through each Store-Product group ===
for (store, product), group in groups:
    group = group.sort_values('ds').reset_index(drop=True)
    split_idx = int(len(group) * 0.8)

    if split_idx <= lookback + 1:
        print(f"Skipping Store {store} Product {product} due to insufficient rows")
        continue

    print(f"Processing Store {store} Product {product}")

    train = group.iloc[:split_idx]
    test = group.iloc[split_idx:]

    X_train = train[features]
    y_train = train['y']
    X_test = test[features]
    y_test = test['y']

    # === Train models ===
    rf = RandomForestRegressor(n_estimators=100, random_state=42).fit(X_train, y_train)
    gb = GradientBoostingRegressor(n_estimators=100, random_state=42).fit(X_train, y_train)
    xgb = XGBRegressor(n_estimators=100, random_state=42).fit(X_train, y_train)

    prophet = Prophet(yearly_seasonality=True, weekly_seasonality=True)
    for col in exog_cols + ['y_lag1', 'y_lag7', 'y_roll7', 'y_roll30']:
        prophet.add_regressor(col)
    prophet_train = train[['ds', 'y'] + exog_cols + ['y_lag1', 'y_lag7', 'y_roll7', 'y_roll30']]
    prophet.fit(prophet_train)
    future = pd.concat([train[['ds']], test[['ds']]]).reset_index(drop=True)
    future_exog = pd.concat([
        train[exog_cols + ['y_lag1', 'y_lag7', 'y_roll7', 'y_roll30']],
        test[exog_cols + ['y_lag1', 'y_lag7', 'y_roll7', 'y_roll30']]
    ]).reset_index(drop=True)
    future = pd.concat([future, future_exog], axis=1)
    forecast = prophet.predict(future)
    prophet_pred = forecast[forecast['ds'].isin(test['ds'])].reset_index(drop=True)['yhat'].values

    sarimax = SARIMAX(
        train['y'],
        exog=train[exog_cols + ['y_lag1', 'y_lag7']],
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 7)
    ).fit(disp=False)
    sarimax_pred = sarimax.predict(
        start=len(train),
        end=len(train) + len(test) - 1,
        exog=test[exog_cols + ['y_lag1', 'y_lag7']]
    )

    all_preds = {
        'RF': rf.predict(X_test),
        'GB': gb.predict(X_test),
        'XGB': xgb.predict(X_test),
        'Prophet': prophet_pred,
        'SARIMAX': sarimax_pred
    }

    # === Evaluate sales metrics for all models ===
    metrics = {model: eval(y_test.values, yhat) for model, yhat in all_preds.items()}
    sorted_models = sorted(metrics.items(), key=lambda x: x[1][0])  # sort by MAE
    top2 = sorted_models[:2]

    # === Get best 2 model names and predictions ===
    best1_name, best1_metrics = top2[0]
    best2_name, best2_metrics = top2[1]
    best1_pred = all_preds[best1_name]
    best2_pred = all_preds[best2_name]

    # === Calculate profit (sales * price) for actual and predicted ===
    actual_profit = y_test.values * test['Price'].values
    pred_profit_best1 = best1_pred * test['Price'].values
    pred_profit_best2 = best2_pred * test['Price'].values

    # === Evaluate profit metrics for best 2 models ===
    profit_metrics_best1 = eval(actual_profit, pred_profit_best1)
    profit_metrics_best2 = eval(actual_profit, pred_profit_best2)

    # === Append all metrics to accuracy list ===
    accuracy_rows.append([
        store, product,
        best1_name, *best1_metrics, *profit_metrics_best1,
        best2_name, *best2_metrics, *profit_metrics_best2
    ])

    # === Save predictions CSV with sales only ===
    results_df = pd.DataFrame({
        'ds': test['ds'].values,
        'Actual_Sales': y_test.values,
        best1_name + '_Sales_Pred': best1_pred,
        best2_name + '_Sales_Pred': best2_pred,
        'Price': test['Price'].values,
        'Actual_Profit': actual_profit,
        best1_name + '_Profit_Pred': pred_profit_best1,
        best2_name + '_Profit_Pred': pred_profit_best2
    })
    results_df.to_csv(f"store_predictions/Store_{store}_Product_{product}_predictions.csv", index=False)

    # === Plot Actual + Best2 Sales ===
    plt.figure(figsize=(14, 7))
    plt.plot(test['ds'], y_test.values, label="Actual Sales", color="blue", linewidth=2, marker='o')
    plt.plot(test['ds'], best1_pred, label=f"{best1_name} Sales", color="green", linewidth=1, marker='o')
    plt.plot(test['ds'], best2_pred, label=f"{best2_name} Sales", color="red", linewidth=1, marker='o')
    plt.title(f"Store {store} Product {product} - Actual vs Best2 Sales")
    plt.xlabel("Date")
    plt.ylabel("Sales")
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"results_per_product/Store_{store}_Product_{product}_actual_vs_best2_sales.png")
    plt.close()

    # === Plot Actual + Best2 Profit ===
    plt.figure(figsize=(14, 7))
    plt.plot(test['ds'], actual_profit, label="Actual Profit", color="blue", linewidth=2, marker='o')
    plt.plot(test['ds'], pred_profit_best1, label=f"{best1_name} Profit", color="green", linewidth=1, marker='o')
    plt.plot(test['ds'], pred_profit_best2, label=f"{best2_name} Profit", color="red", linewidth=1, marker='o')
    plt.title(f"Store {store} Product {product} - Actual vs Best2 Profit")
    plt.xlabel("Date")
    plt.ylabel("Profit")
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"results_per_product/Store_{store}_Product_{product}_actual_vs_best2_profit.png")
    plt.close()

# === Save accuracy summary with profit metrics ===
accuracy_df = pd.DataFrame(accuracy_rows, columns=[
    'Store_ID', 'Product_ID',
    'Best_Model_1', 'Best1_MAE_Sales', 'Best1_RMSE_Sales', 'Best1_MAPE_Sales', 'Best1_R2_Sales',
    'Best1_MAE_Profit', 'Best1_RMSE_Profit', 'Best1_MAPE_Profit', 'Best1_R2_Profit',
    'Best_Model_2', 'Best2_MAE_Sales', 'Best2_RMSE_Sales', 'Best2_MAPE_Sales', 'Best2_R2_Sales',
    'Best2_MAE_Profit', 'Best2_RMSE_Profit', 'Best2_MAPE_Profit', 'Best2_R2_Profit'
])
accuracy_df.to_csv("accuracy_per_product/top2_model_summary.csv", index=False)
