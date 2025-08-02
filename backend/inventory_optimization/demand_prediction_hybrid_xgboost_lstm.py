import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error, r2_score
from xgboost import XGBRegressor
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping

# ------------------------ Load Data & Feature Engineering ------------------------
def load_data(filepath):
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])

    df['DayOfWeek'] = df['Date'].dt.dayofweek
    df['DayOfMonth'] = df['Date'].dt.day
    df['WeekOfYear'] = df['Date'].dt.isocalendar().week.astype(int)
    df['Quarter'] = df['Date'].dt.quarter

    df = df.sort_values(['Product ID', 'Date']).reset_index(drop=True)
    df['Demand_t-1'] = df.groupby('Product ID')['Demand'].shift(1)
    df['Demand_t-7'] = df.groupby('Product ID')['Demand'].shift(7)
    df['RollingMean_7'] = df.groupby('Product ID')['Demand'].rolling(7).mean().reset_index(0, drop=True)
    df['RollingStd_7'] = df.groupby('Product ID')['Demand'].rolling(7).std().reset_index(0, drop=True)

    df.dropna(inplace=True)
    return df

# ------------------------ XGBoost Model ------------------------
def train_xgboost(X_train, y_train):
    model = XGBRegressor(n_estimators=300, max_depth=6, learning_rate=0.05,
                         subsample=0.8, colsample_bytree=0.8, random_state=42)
    model.fit(X_train, y_train)
    return model

# ------------------------ LSTM Model ------------------------
def create_lstm_data(X, y, timesteps=5):
    Xs, ys = [], []
    for i in range(timesteps, len(X)):
        Xs.append(X[i-timesteps:i])
        ys.append(y[i])
    return np.array(Xs), np.array(ys)

def train_lstm(X_train_seq, y_train_seq, input_shape):
    model = Sequential()
    model.add(LSTM(64, activation='relu', input_shape=input_shape))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')

    model.fit(X_train_seq, y_train_seq, epochs=50, batch_size=16,
              validation_split=0.1, callbacks=[EarlyStopping(patience=5)], verbose=0)
    return model

# ------------------------ Evaluation ------------------------
def calculate_metrics(y_true, y_pred):
    return {
        'MAE': mean_absolute_error(y_true, y_pred),
        'MAPE (%)': mean_absolute_percentage_error(y_true[y_true > 0], y_pred[y_true > 0]) * 100,
        'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
        'R² Score': r2_score(y_true, y_pred)
    }

# ------------------------ Main Pipeline ------------------------
if __name__ == "__main__":
    df = load_data("../data/ecommerce_demand_data.csv")

    target = df['Demand']
    features = df.drop(columns=['Demand', 'Date', 'Product ID'])

    # Scaling for LSTM
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(features)

    # Split for both models
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # ----------------- XGBoost -----------------
    xgb_model = train_xgboost(X_train, y_train)
    xgb_preds = np.round(xgb_model.predict(X_test))

    # ----------------- LSTM -----------------
    timesteps = 5
    X_seq, y_seq = create_lstm_data(X_scaled, target.values, timesteps)

    split_index = int(0.8 * len(X_seq))
    X_train_seq, X_test_seq = X_seq[:split_index], X_seq[split_index:]
    y_train_seq, y_test_seq = y_seq[:split_index], y_seq[split_index:]

    lstm_model = train_lstm(X_train_seq, y_train_seq, input_shape=(timesteps, X_train_seq.shape[2]))
    lstm_preds = np.round(lstm_model.predict(X_test_seq).flatten())

    # Align XGBoost and LSTM predictions for hybrid
    min_len = min(len(xgb_preds), len(lstm_preds))
    hybrid_preds = (xgb_preds[:min_len] + lstm_preds[:min_len]) / 2
    y_true = y_test.values[-min_len:]

    # ----------------- Evaluation -----------------
    print("\n📊 XGBoost Performance:")
    print(calculate_metrics(y_true, xgb_preds[:min_len]))

    print("\n📊 LSTM Performance:")
    print(calculate_metrics(y_true, lstm_preds[:min_len]))

    print("\n📊 Hybrid (XGB + LSTM) Performance:")
    metrics = calculate_metrics(y_true, hybrid_preds)
    print(metrics)

    # ----------------- Visualization -----------------
    plt.figure(figsize=(12, 6))
    plt.plot(y_true, label="Actual", marker='o')
    plt.plot(xgb_preds[:min_len], label="XGBoost", linestyle='--')
    plt.plot(lstm_preds[:min_len], label="LSTM", linestyle=':')
    plt.plot(hybrid_preds, label="Hybrid", linestyle='-')
    plt.title("Actual vs Predictions (Hybrid Model)")
    plt.xlabel("Sample Index")
    plt.ylabel("Demand")
    plt.legend()
    plt.tight_layout()
    plt.savefig("hybrid_xgb_lstm_results.png", dpi=300)
    plt.show()
