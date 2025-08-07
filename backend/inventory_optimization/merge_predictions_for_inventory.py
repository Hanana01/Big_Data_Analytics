import pandas as pd

# Load both CSV files
df1 = pd.read_csv("../data/xgboost_testset_predictions.csv")
df2 = pd.read_csv("../data/predicted_sales.csv")

# Clean headers (optional but recommended)
df1.columns = df1.columns.str.strip()
df2.columns = df2.columns.str.strip()

# Check row alignment
if len(df1) != len(df2):
    raise ValueError("CSV files do not have the same number of rows. Cannot merge directly.")

# Add 'XGB_Sales_Pred' column from df2 to df1
if 'XGB_Sales_Pred' not in df2.columns:
    raise KeyError("'XGB_Sales_Pred' column not found in df2.")

df1['XGB_Sales_Pred'] = df2['XGB_Sales_Pred'].values

# Save the final merged file
df1.to_csv("../data/inventory_optimization.csv", index=False)

print("✅ Merged file saved as 'inventory_optimization.csv'")
