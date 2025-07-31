import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    r2_score
)
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping

def load_data(filepath):
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])

    # Temporal features
    df['DayOfWeek'] = df['Date'].dt.dayofweek
    df['DayOfMonth'] = df['Date'].dt.day
    df['WeekOfYear'] = df['Date'].dt.isocalendar().week.astype(int)
    df['Quarter'] = df['Date'].dt.quarter

    # Sort & create lag/rolling features
    df = df.sort_values(['Product ID', 'Date']).reset_index(drop=True)
    df['Demand_t-1'] = df.groupby('Product ID')['Demand'].shift(1)
    df['Demand_t-7'] = df.groupby('Product ID')['Demand'].shift(7)
    df['RollingMean_7'] = df.groupby('Product ID')['Demand'].rolling(7).mean().reset_index(0, drop=True)
    df['RollingStd_7'] = df.groupby('Product ID')['Demand'].rolling(7).std().reset_index(0, drop=True)

    df.dropna(inplace=True)
    return df

def create_lstm_sequences(X, y, timesteps=1):
    Xs, ys = [], []
    for i in range(len(X) - timesteps):
        Xs.append(X[i:i+timesteps])
        ys.append(y[i+timesteps])
    return np.array(Xs), np.array(ys)

def calculate_metrics(y_true, y_pred):
    metrics = {
        'MAE': mean_absolute_error(y_true, y_pred),
        'MAPE (%)': mean_absolute_percentage_error(y_true[y_true > 0], y_pred[y_true > 0]) * 100,
        'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
        'R² Score': r2_score(y_true, y_pred),
        'Perfect Predictions': sum(np.round(y_true) == np.round(y_pred)),
        'Perfect Prediction Rate': f"{100 * sum(np.round(y_true) == np.round(y_pred)) / len(y_true):.2f}%"
    }

    print("\nModel Evaluation (LSTM):")
    for k, v in metrics.items():
        print(f"{k}: {v}")
    return metrics

if __name__ == "__main__":
    DATA_PATH = "../data/ecommerce_demand_data.csv"
    OUTPUT_PATH = "lstm_advanced_predictions.csv"

    print("Loading and preprocessing data...")
    df = load_data(DATA_PATH)

    target = df['Demand']
    features = df.drop(columns=['Demand', 'Date', 'Product ID'])

    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(features)
    y = target.values

    time_steps = 7
    X_seq, y_seq = create_lstm_sequences(X_scaled, y, time_steps)

    split_index = int(len(X_seq) * 0.8)
    X_train, X_test = X_seq[:split_index], X_seq[split_index:]
    y_train, y_test = y_seq[:split_index], y_seq[split_index:]

    model = Sequential()
    model.add(LSTM(64, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')

    print("Training LSTM model...")
    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    model.fit(X_train, y_train, validation_data=(X_test, y_test),
              epochs=50, batch_size=32, verbose=0, callbacks=[early_stop])

    y_pred = model.predict(X_test).flatten()
    y_pred_rounded = np.round(y_pred)
    y_true_rounded = np.round(y_test)

    calculate_metrics(y_true_rounded, y_pred_rounded)

    # Full prediction
    full_pred = model.predict(X_seq).flatten()
    full_pred_rounded = np.round(full_pred)

    df_out = df.iloc[time_steps:].copy()
    df_out['Predicted_Demand_Raw'] = full_pred
    df_out['Predicted_Demand'] = full_pred_rounded
    df_out['Absolute_Error'] = np.abs(df_out['Demand'] - df_out['Predicted_Demand'])
    df_out['Percentage_Error'] = np.where(
        df_out['Demand'] > 0,
        (df_out['Absolute_Error'] / df_out['Demand']) * 100,
        np.nan
    )
    df_out.to_csv(OUTPUT_PATH, index=False)

    perfect_preds = df_out[df_out['Absolute_Error'] == 0]
    print(f"\nPerfect predictions analysis:")
    print(f"Total perfect predictions: {len(perfect_preds)}")
    print(f"Perfect prediction rate: {100*len(perfect_preds)/len(df_out):.2f}%")

    # Last 30 days for one product
    product_id_input = input("Enter the Product ID to predict last 30 days demand for: ")
    try:
        product_id = int(product_id_input)
    except ValueError:
        print("Invalid Product ID entered. Exiting.")
        exit(1)

    df_product = df_out[df_out['Product ID'] == product_id]
    if df_product.empty:
        print(f"No data found for Product ID {product_id}. Exiting.")
        exit(1)

    last_30 = df_product[df_product['Date'] >= (df_product['Date'].max() - pd.Timedelta(days=29))]

    if last_30.empty:
        print(f"No data available for the last 30 days for Product ID {product_id}. Exiting.")
        exit(1)

    plt.figure(figsize=(14, 7))
    plt.plot(last_30['Date'], last_30['Demand'], label='Actual Demand', marker='o')
    plt.plot(last_30['Date'], last_30['Predicted_Demand'], label='Predicted Demand', marker='x')
    plt.xticks(rotation=45)
    plt.xlabel('Date')
    plt.ylabel('Demand')
    plt.title(f'Actual vs Predicted Demand (LSTM) - Last 30 Days - Product {product_id}')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"last_30_days_demand_prediction_LSTM_product_{product_id}.png", dpi=300)
    plt.show()

    print(f"\nLast 30 days prediction visualization saved as last_30_days_demand_prediction_LSTM_product_{product_id}.png")
    print("\nTraining complete. Files saved:")
    print(f"- {OUTPUT_PATH}")

