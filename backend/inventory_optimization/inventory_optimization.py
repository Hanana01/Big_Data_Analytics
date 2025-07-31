
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_inventory_metrics(demand_forecast, holding_cost, lead_time, ordering_cost, service_level=0.95):
    avg_demand = demand_forecast.mean()
    demand_std = demand_forecast.std()
    z = 1.65 if service_level == 0.95 else 1.28

    eoq = np.sqrt((2 * avg_demand * ordering_cost) / holding_cost)
    safety_stock = z * demand_std * np.sqrt(lead_time)
    reorder_point = avg_demand * lead_time + safety_stock

    return round(eoq, 2), round(safety_stock, 2), round(reorder_point, 2)

def main():
    try:
        df = pd.read_csv("xgboost_advanced_predictions.csv")
        df.columns = df.columns.str.strip()
    except FileNotFoundError:
        print("❌ File 'xgboost_advanced_predictions.csv' not found.")
        return

    df['Date'] = pd.to_datetime(df['Date'])

    try:
        product_id = int(input("Enter Product ID: "))
        region = int(input("Enter Region: "))
    except ValueError:
        print("❌ Invalid input.")
        return

    filtered_df = df[(df['Product ID'] == product_id) & (df['Region'] == region)].copy()

    if filtered_df.empty:
        print(f"❌ No data for Product ID {product_id} in Region {region}.")
        return

    latest_date = filtered_df['Date'].max()
    cutoff_date = latest_date - pd.Timedelta(days=29)
    last_30_days = filtered_df[filtered_df['Date'] >= cutoff_date]

    if last_30_days.empty:
        print("❌ No recent data found for last 30 days.")
        return

    required_cols = ['Predicted_Demand', 'Units Sold', 'Holding Cost per Unit', 'Lead Time (Days)', 'Inventory Level', 'Ordering Cost']
    for col in required_cols:
        if col not in filtered_df.columns:
            print(f"❌ Missing column: {col}")
            return

    holding_cost = filtered_df['Holding Cost per Unit'].iloc[0]
    lead_time = filtered_df['Lead Time (Days)'].iloc[0]
    ordering_cost = filtered_df['Ordering Cost'].iloc[0]
    forecasted_demand = last_30_days['Predicted_Demand']
    actual_sales = last_30_days['Units Sold']
    latest_inventory = filtered_df.iloc[-1]['Inventory Level']

    eoq, safety_stock, reorder_point = calculate_inventory_metrics(
        forecasted_demand, holding_cost, lead_time, ordering_cost
    )

    print(f"\n📦 Inventory Optimization for Product ID {product_id} in Region {region}")
    print(f"📅 Data Range: {last_30_days['Date'].min().date()} to {last_30_days['Date'].max().date()}")
    print(f"🔢 Avg Daily Forecasted Demand: {forecasted_demand.mean():.2f}")
    print(f"🔢 Avg Daily Actual Sales (Units Sold): {actual_sales.mean():.2f}")
    print(f"💰 Holding Cost: {holding_cost}, 🧾 Ordering Cost: {ordering_cost}, 📦 Lead Time: {lead_time}")
    print("----------------------------------------------------")
    print(f"✅ EOQ: {eoq}")
    print(f"🛡️  Safety Stock: {safety_stock}")
    print(f"🔁 Reorder Point (ROP): {reorder_point}")
    print(f"📦 Current Inventory Level: {latest_inventory}")
    print("----------------------------------------------------")

    if latest_inventory <= reorder_point:
        print("🚨 ALERT: Inventory is at/below ROP! Reorder Needed.")
    else:
        print("✅ Inventory level is sufficient.\n")
        
    # ---------- 📈 Visualization ----------
    plt.figure(figsize=(12, 6))
    plt.plot(last_30_days['Date'], forecasted_demand, label='Predicted Demand', marker='o')
    plt.plot(last_30_days['Date'], actual_sales, label='Actual Sales (Units Sold)', color='brown', linestyle='--')
    plt.axhline(y=reorder_point, color='red', linestyle='--', label='Reorder Point (ROP)')
    plt.axhline(y=safety_stock, color='orange', linestyle='--', label='Safety Stock')
    plt.axhline(y=eoq, color='green', linestyle='--', label='EOQ')
    plt.axhline(y=latest_inventory, color='purple', linestyle='--', label='Current Inventory Level')

    plt.title(f"📈 Inventory Metrics - Product {product_id}, Region {region}")
    plt.xlabel("Date")
    plt.ylabel("Units")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
