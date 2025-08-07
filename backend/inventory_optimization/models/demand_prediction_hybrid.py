import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

# --------- Data Loading and Feature Engineering ---------

def load_data(filepath):
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])

    # Temporal features
    df['DayOfWeek'] = df['Date'].dt.dayofweek
    df['DayOfMonth'] = df['Date'].dt.day
    df['WeekOfYear'] = df['Date'].dt.isocalendar().week.astype(int)
    df['Quarter'] = df['Date'].dt.quarter

    # Sort & lags/rolling
    df = df.sort_values(['Product ID', 'Date']).reset_index(drop=True)
    df['Demand_t-1'] = df.groupby('Product ID')['Demand'].shift(1)
    df['Demand_t-7'] = df.groupby('Product ID')['Demand'].shift(7)
    df['RollingMean_7'] = df.groupby('Product ID')['Demand'].rolling(7).mean().reset_index(0, drop=True)
    df['RollingStd_7'] = df.groupby('Product ID')['Demand'].rolling(7).std().reset_index(0, drop=True)

    df.dropna(inplace=True)
    return df

# --------- LSTM Preparation ---------

def prepare_lstm_data(df, sequence_length=7):
    sequences = []
    targets = []

    grouped = df.groupby('Product ID')
    feature_cols = ['Demand_t-1', 'Demand_t-7', 'RollingMean_7', 'RollingStd_7']

    for _, group in grouped:
        if len(group) < sequence_length + 1:
            continue

        group = group.sort_values('Date')
        features = group[feature_cols].values
        target = group['Demand'].values

        for i in range(sequence_length, len(group)):
            sequences.append(features[i-sequence_length:i])
            targets.append(target[i])

    return np.array(sequences), np.array(targets)

# --------- Train LSTM ---------

def train_lstm(X, y):
    model = Sequential([
        LSTM(64, input_shape=(X.shape[1], X.shape[2]), return_sequences=False),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mae')
    es = EarlyStopping(patience=5, restore_best_weights=True)

    model.fit(X, y, epochs=30, batch_size=32, validation_split=0.2, callbacks=[es], verbose=1)
    return model

# --------- Train XGBoost ---------

def train_xgboost(X_train, y_train):
    model = XGBRegressor(n_estimators=300, max_depth=6, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8)
    model.fit(X_train, y_train)
    return model

# --------- Evaluation ---------

def evaluate(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    print(f"MAE: {mae:.2f}, R²: {r2:.2f}")
    return mae, r2

# --------- Main ---------

if __name__ == "__main__":
    DATA_PATH = "../data/ecommerce_demand_data.csv"
    df = load_data(DATA_PATH)

    # Time-based split
    df_sorted = df.sort_values('Date').reset_index(drop=True)
    split_index = int(len(df_sorted) * 0.8)
    train_df = df_sorted.iloc[:split_index]
    test_df = df_sorted.iloc[split_index:]

    # XGBoost features
    xgb_features = train_df.drop(columns=['Demand', 'Units Ordered', 'Units Sold'])
    xgb_target = train_df['Demand']
    xgb_model = train_xgboost(xgb_features, xgb_target)

    # Prepare LSTM sequences
    X_lstm_train, y_lstm_train = prepare_lstm_data(train_df)
    X_lstm_test, y_lstm_test = prepare_lstm_data(test_df)
    lstm_model = train_lstm(X_lstm_train, y_lstm_train)

    # Predictions
    y_pred_xgb = xgb_model.predict(test_df.drop(columns=['Demand', 'Units Ordered', 'Units Sold'])[:len(y_lstm_test)])
    y_pred_lstm = lstm_model.predict(X_lstm_test).flatten()

    # Hybrid prediction (simple average)
    y_pred_hybrid = (y_pred_xgb + y_pred_lstm) / 2
    y_true = y_lstm_test

    # Evaluate
    print("\nHybrid Model Performance:")
    evaluate(y_true, y_pred_hybrid)

    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(y_true[:100], label='Actual')
    plt.plot(y_pred_hybrid[:100], label='Hybrid Predicted')
    plt.legend()
    plt.title('Hybrid XGBoost + LSTM Prediction (First 100 Samples)')
    plt.show()
