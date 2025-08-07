import pandas as pd

# Load CSV
df = pd.read_csv("../data/xgboost_testset_predictions.csv")
df.columns = [col.strip() for col in df.columns]  

df['Date'] = pd.to_datetime(df['Date'])
df['Store ID'] = df['Store ID'].astype(int)
df['Product ID'] = df['Product ID'].astype(int)

# Optional: Preview counts
print("Original record count:", len(df))

# Sort
df = df.sort_values(['Date', 'Store ID', 'Product ID'])

# Reorder columns: Date, Store ID, Product ID first
cols = df.columns.tolist()
first_cols = ['Date', 'Store ID', 'Product ID']
other_cols = [col for col in cols if col not in first_cols]
df = df[first_cols + other_cols]

# Save to CSV
df.to_csv("../data/ordered_data.csv", index=False)

# Check final count
print("Final record count:", len(df))
print(df.head(10))
