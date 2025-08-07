import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping

def load_and_preprocess(filepath, product_id, sequence_length=14):
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Filter for one product
    df = df[df['Product ID'] == product_id].sort_values('Date').reset_index(drop=True)

    # Define categorical and numeric features
    categorical_features = ['Store ID', 'Category', 'Region', 'Weather Condition', 'Holiday/Promotion']
    numeric_features = ['Inventory Level', 'Units Sold', 'Units Ordered', 'Price', 'Discount',
                        'Competitor Pricing', 'Seasonality', 'Holding Cost per Unit', 'Lead Time (Days)', 'Ordering Cost', 'Demand']

    # Separate features and target
    X_cat = df[categorical_features]
    X_num = df[numeric_features]
    
    # One-hot encode categorical features
    ohe = OneHotEncoder(handle_unknown='ignore')
    X_cat_encoded = ohe.fit_transform(X_cat).toarray()  # Convert sparse matrix to dense
    
    # Scale numeric features (including Demand for input)
    scaler = MinMaxScaler()
    X_num_scaled = scaler.fit_transform(X_num)

    # Combine encoded categorical and scaled numeric features
    X_all = np.hstack([X_num_scaled, X_cat_encoded])

    # Create sequences for LSTM
    X_seq, y = [], []
    demand_idx = numeric_features.index('Demand')  # index of demand in numeric features
    
    for i in range(sequence_length, len(X_all)):
        X_seq.append(X_all[i-sequence_length:i])
        y.append(X_all[i, demand_idx])  # Demand value scaled at time i

    X_seq = np.array(X_seq)
    y = np.array(y)

    # Split train/test 80/20
    split = int(len(X_seq)*0.8)
    X_train, X_test = X_seq[:split], X_seq[split:]
    y_train, y_test = y[:split], y[split:]

    return X_train, y_train, X_test, y_test, scaler, ohe, categorical_features, numeric_features

def build_lstm_model(input_shape):
    """
    Build LSTM model.
    """
    model = Sequential()
    model.add(LSTM(64, activation='relu', input_shape=input_shape, return_sequences=True))
    model.add(LSTM(32, activation='relu'))
    model.add(Dense(1))  # Output: predicted scaled demand
    model.compile(optimizer='adam', loss='mse')
    return model

def inverse_scale_demand(scaler, y_scaled, numeric_features):

     # Inverse transform scaled demand back to original scale.

    dummy = np.zeros((len(y_scaled), len(numeric_features)))
    demand_idx = numeric_features.index('Demand')
    dummy[:, demand_idx] = y_scaled
    y_inv = scaler.inverse_transform(dummy)[:, demand_idx]
    return y_inv

if __name__ == "__main__":
    DATA_PATH = "../data/ecommerce_demand_data.csv"
    PRODUCT_ID = int(input("Enter Product ID for LSTM "))
    SEQUENCE_LENGTH = 14

    print("Loading and preprocessing data...")
    X_train, y_train, X_test, y_test, scaler, ohe, cat_features, num_features = load_and_preprocess(DATA_PATH, PRODUCT_ID, SEQUENCE_LENGTH)

    print(f"Training data shape: {X_train.shape}, {y_train.shape}")
    print(f"Testing data shape: {X_test.shape}, {y_test.shape}")

    model = build_lstm_model(input_shape=(X_train.shape[1], X_train.shape[2]))

    early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

    print("Training LSTM model...")
    history = model.fit(
        X_train, y_train,
        validation_split=0.2,
        epochs=100,
        batch_size=32,
        callbacks=[early_stop],
        verbose=1
    )

    print("Predicting on test set...")
    y_pred_scaled = model.predict(X_test).flatten()
    y_test_inv = inverse_scale_demand(scaler, y_test, num_features)
    y_pred_inv = inverse_scale_demand(scaler, y_pred_scaled, num_features)

    mae = mean_absolute_error(y_test_inv, y_pred_inv)
    rmse = np.sqrt(mean_squared_error(y_test_inv, y_pred_inv))
    r2 = r2_score(y_test_inv, y_pred_inv)

    print("\nLSTM Model Evaluation:")
    print(f"Test MAE: {mae:.2f}")
    print(f"Test RMSE: {rmse:.2f}")
    print(f"Test R2: {r2:.3f}")

    plt.figure(figsize=(12,6))
    plt.plot(y_test_inv, label='Actual Demand')
    plt.plot(y_pred_inv, label='Predicted Demand')
    plt.title(f'Actual vs Predicted Demand for Product {PRODUCT_ID}')
    plt.xlabel('Time Step')
    plt.ylabel('Demand')
    plt.legend()
    plt.show()
