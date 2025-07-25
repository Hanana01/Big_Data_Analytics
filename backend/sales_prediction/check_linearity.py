import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

# === CONFIG ===
INPUT_FILE = "data/cleaned_sales.csv"
OUTPUT_FOLDER = "linearity_check"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === LOAD DATA ===
df = pd.read_csv(INPUT_FILE)
df['ds'] = pd.to_datetime(df['ds'])
df = df.sort_values('ds')

# === GROUP BY Store & Product ===
groups = df.groupby(['Store_ID', 'Product_ID'])

results = []

for (store, product), group in groups:
    group = group.sort_values('ds').reset_index(drop=True)
    group['t'] = np.arange(len(group))  # simple time index

    X_time = group[['t']]
    y_series = group['y']

    # Fit linear trend
    lr = LinearRegression().fit(X_time, y_series)
    y_trend = lr.predict(X_time)

    # R² score
    r2 = r2_score(y_series, y_trend)

    # Residuals
    group['Residuals'] = y_series - y_trend

    # Save results
    results.append([store, product, len(group), r2])

    print(f"Store {store} Product {product} | R² = {r2:.4f} | Rows: {len(group)}")

    # === PLOT ===
    plt.figure(figsize=(12, 6))
    plt.plot(group['ds'], y_series, label="Actual", marker='o')
    plt.plot(group['ds'], y_trend, label="Linear Trend", linestyle='--')
    plt.title(f"Store {store} Product {product} - Trend R²: {r2:.3f}")
    plt.xlabel("Date")
    plt.ylabel("Sales")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_FOLDER}/Store_{store}_Product_{product}_trend_fit.png")
    plt.close()

    # === Residual plot ===
    plt.figure(figsize=(12, 4))
    plt.plot(group['ds'], group['Residuals'], marker='o')
    plt.axhline(0, color='red', linestyle='--')
    plt.title(f"Residuals - Store {store} Product {product}")
    plt.xlabel("Date")
    plt.ylabel("Residuals")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_FOLDER}/Store_{store}_Product_{product}_residuals.png")
    plt.close()

# === Save summary ===
results_df = pd.DataFrame(results, columns=['Store_ID', 'Product_ID', 'Num_Rows', 'R2_Trend'])
results_df['Trend_Type'] = np.where(results_df['R2_Trend'] >= 0.8, 'Linear', 'Non-Linear')
results_df.to_csv(f"{OUTPUT_FOLDER}/trend_summary.csv", index=False)

print(f"\n✅ All done! Trend summary saved to: {OUTPUT_FOLDER}/trend_summary.csv")
