import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error

# Set style for visualizations
sns.set_style("whitegrid")
plt.figure(figsize=(10, 6))

# Load the data
df = pd.read_csv('xgboost_advanced_predictions.csv')

# 1. Calculate Demand Prediction Error Metrics
df['Absolute_Error'] = np.abs(df['Predicted_Demand'] - df['Demand'])
df['Percentage_Error'] = (df['Absolute_Error'] / df['Demand']) * 100

# Handle division by zero for products with zero demand
df['Percentage_Error'] = np.where(
    df['Demand'] == 0,
    np.nan,  # Mark as NaN if no demand occurred
    df['Percentage_Error']
)


# Calculate overall metrics
mae = mean_absolute_error(df['Demand'], df['Predicted_Demand'])
mape = mean_absolute_percentage_error(
    df[df['Demand'] > 0]['Demand'],  # Exclude zero demand
    df[df['Demand'] > 0]['Predicted_Demand']
)

print("="*50)
print("DEMAND PREDICTION ACCURACY REPORT")
print("="*50)
print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"Mean Absolute Percentage Error (MAPE): {mape:.1f}%")
print(f"Total Products Analyzed: {len(df)}")
# print(f"Products with Perfect Prediction: {(df['Absolute_Error'] == 0).sum()}")
# print(f"Products Over-Predicted: {(df['Predicted_Demand'] > df['Demand']).sum()}")
# print(f"Products Under-Predicted: {(df['Predicted_Demand'] < df['Demand']).sum()}")

# 2. Visualize Predicted vs Actual Demand
plt.figure(figsize=(12, 8))
sns.scatterplot(
    x='Predicted_Demand',
    y='Demand',
    data=df,
    hue='Category',
    palette='viridis',
    alpha=0.7,
    s=100
)

# Add perfect prediction line
max_val = max(df['Predicted_Demand'].max(), df['Demand'].max())
plt.plot([0, max_val], [0, max_val], 'r--', label='Perfect Prediction')

plt.title('Predicted vs Actual Demand', fontsize=16)
plt.xlabel('Predicted Demand', fontsize=14)
plt.ylabel('Actual Demand', fontsize=14)
plt.legend(title='Product Category')
plt.tight_layout()
plt.savefig('predicted_vs_actual_demand.png', dpi=300)
plt.show()

# 3. Error Distribution Analysis
plt.figure(figsize=(12, 6))
sns.histplot(
    df['Absolute_Error'],
    bins=30,
    kde=True,
    color='royalblue'
)
plt.title('Distribution of Prediction Errors', fontsize=16)
plt.xlabel('Absolute Prediction Error', fontsize=14)
plt.ylabel('Frequency', fontsize=14)
plt.savefig('error_distribution_demand.png', dpi=300)
plt.show()

# 4. Worst/Best Performing Predictions
worst_predictions = df.nlargest(10, 'Absolute_Error')[['Product ID', 'Category', 'Region', 
                                                   'Predicted_Demand', 'Demand', 'Absolute_Error']]
best_predictions = df.nsmallest(10, 'Absolute_Error')[['Product ID', 'Category', 'Region',
                                                   'Predicted_Demand', 'Demand', 'Absolute_Error']]

print("\nTOP 10 WORST PREDICTIONS:")
print(worst_predictions.to_string(index=False))

print("\nTOP 10 BEST PREDICTIONS:")
print(best_predictions.to_string(index=False))

# 5. Error Analysis by Category and Region
error_by_category = df.groupby('Category').agg({
    'Absolute_Error': 'mean',
    'Percentage_Error': 'mean'
}).rename(columns={
    'Absolute_Error': 'Mean_Absolute_Error',
    'Percentage_Error': 'Mean_Percentage_Error'
}).reset_index()

error_by_region = df.groupby('Region').agg({
    'Absolute_Error': 'mean',
    'Percentage_Error': 'mean'
}).rename(columns={
    'Absolute_Error': 'Mean_Absolute_Error',
    'Percentage_Error': 'Mean_Percentage_Error'
}).reset_index()

print("\nPREDICTION ERROR BY CATEGORY:")
print(error_by_category.to_string(index=False))

print("\nPREDICTION ERROR BY REGION:")
print(error_by_region.to_string(index=False))

# 6. Time Series Analysis (if date columns available)
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'])
    monthly_errors = df.groupby(pd.Grouper(key='Date', freq='M'))['Absolute_Error'].mean().reset_index()
    
    plt.figure(figsize=(12, 6))
    sns.lineplot(
        x='Date',
        y='Absolute_Error',
        data=monthly_errors,
        marker='o',
        color='darkorange'
    )
    plt.title('Monthly Average Prediction Error Over Time', fontsize=16)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Mean Absolute Error', fontsize=14)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('monthly_error_trend_demand.png', dpi=300)
    plt.show()

# Save the enhanced dataset
df.to_csv('inventory_data_with_demand_analysis.csv', index=False)
print("\nAnalysis complete. Results saved to:")
print("- predicted_vs_actual_demand.png")
print("- error_distribution_demand.png")
print("- monthly_error_trend_demand.png (if date column present)")
print("- inventory_data_with_demand_analysis.csv")