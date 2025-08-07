from flask import Blueprint, request, jsonify
import pandas as pd
import numpy as np

# Create a Flask blueprint for inventory-related routes
inventory_bp = Blueprint('inventory', __name__)

# Load the inventory optimization dataset once
df = pd.read_csv('./inventory_optimization/data/inventory_optimization.csv')
df.columns = df.columns.str.strip()
df['Date'] = pd.to_datetime(df['Date'])

# Function to calculate EOQ, Safety Stock, and Reorder Point series
def calculate_daily_inventory_metrics(daily_forecast, holding_cost, lead_time, ordering_cost, service_level=0.95):
    avg_demand = daily_forecast.mean()
    demand_std = daily_forecast.std()
    z = 1.65 if service_level == 0.95 else 1.28  # Z-score for desired service level

    # Economic Order Quantity (EOQ) formula
    eoq = np.sqrt((2 * avg_demand * ordering_cost) / holding_cost) if holding_cost > 0 else 0

    # Safety stock formula
    safety_stock = z * demand_std * np.sqrt(lead_time)

    # Reorder point for each day = forecast * lead_time + safety stock
    reorder_points = daily_forecast * lead_time + safety_stock

    return eoq, safety_stock, reorder_points

# Route to forecast inventory and compute inventory optimization metrics
@inventory_bp.route('/forecast-inventory', methods=['GET'])
def forecast_inventory():
    # Get product_id and store_id from query parameters
    pid = request.args.get('product_id', type=int)
    store_id = request.args.get('store_id', type=int)

    if pid is None or store_id is None:
        return jsonify({"error": "Missing product_id or store_id"}), 400

    # Filter dataset by product ID and store ID
    filtered = df[(df['Product ID'] == pid) & (df['Store ID'] == store_id)]

    if filtered.empty:
        return jsonify({"error": "No data found for given product_id and store_id"}), 404

    # Get the last 30 days of data
    latest = filtered['Date'].max()
    last_30 = filtered[filtered['Date'] >= latest - pd.Timedelta(days=29)]

    if last_30.empty:
        return jsonify({"error": "No data found for the last 30 days"}), 404

    try:
        # Extract required cost and lead time values
        hc = filtered['Holding Cost per Unit'].iloc[0]
        lt = int(filtered['Lead Time (Days)'].iloc[0])
        oc = filtered['Ordering Cost'].iloc[0] if 'Ordering Cost' in filtered.columns else 0

        # Extract relevant series
        forecast = last_30['Predicted_Demand']
        actual_raw = last_30['Demand']
        units_sold = last_30['Units Sold']
        inventory = last_30['Inventory Level']
        xgb_raw = last_30['XGB_Sales_Pred'] if 'XGB_Sales_Pred' in last_30.columns else pd.Series([None] * len(last_30))

        # Convert to integers for actual and predicted sales
        actual = actual_raw.apply(lambda x: int(round(float(x))) if pd.notna(x) else None)
        xgb_sales_pred = xgb_raw.apply(lambda x: int(round(float(x))) if pd.notna(x) else None)

    except Exception as e:
        return jsonify({"error": f"Data extraction error: {str(e)}"}), 500

    # Calculate EOQ, Safety Stock, and Reorder Points
    eoq, ss, rop_series = calculate_daily_inventory_metrics(forecast, hc, lt, oc)
    eoq = int(round(float(eoq)))
    ss = int(round(float(ss)))
    rop_series = rop_series.fillna(0).apply(lambda x: int(round(x)))

    # Determine if reorder is needed based on latest inventory vs ROP
    latest_inventory = inventory.iloc[-1]
    reorder_flag = bool(latest_inventory <= rop_series.iloc[-1])

    # Estimate number of orders and total costs
    estimated_orders = np.ceil(forecast.sum() / eoq) if eoq > 0 else 0
    total_holding_cost = int(round(float(inventory.mean() * hc)))
    total_ordering_cost = int(round(float(estimated_orders * oc)))

    # Prepare chart data
    chart = last_30[['Date']].copy()
    chart['actual'] = actual
    chart['predicted'] = forecast.apply(lambda x: int(round(float(x))) if pd.notna(x) else None)
    chart['xgb_sales_pred'] = xgb_sales_pred
    chart['units_sold'] = units_sold.apply(lambda x: int(round(float(x))) if pd.notna(x) else None)
    chart['inventory_level'] = inventory.apply(lambda x: int(round(float(x))) if pd.notna(x) else None)
    chart['eoq'] = [eoq] * len(chart)
    chart['safety_stock'] = [ss] * len(chart)
    chart['rop'] = rop_series.tolist()
    chart['Date'] = chart['Date'].dt.strftime('%Y-%m-%d')

    # Predict inventory levels by subtracting predicted sales (XGB) from current inventory
    predicted_inventory = []
    current_inventory = float(latest_inventory)
    for pred_sale in xgb_sales_pred:
        if pd.isna(pred_sale):
            predicted_inventory.append(None)
        else:
            current_inventory -= pred_sale
            predicted_inventory.append(int(round(current_inventory)))
    chart['predicted_inventory'] = predicted_inventory

    # Calculate stockout and overstock days
    stockout_days = sum(inv < ss for inv in chart['inventory_level'] if inv is not None)
    overstock_threshold = ss + eoq
    overstock_days = sum(inv > overstock_threshold for inv in chart['inventory_level'] if inv is not None)

    # Return JSON response with all calculated inventory metrics
    return jsonify({
        "product_id": pid,
        "store_id": store_id,
        "date_range": {
            "from": chart['Date'].iat[0],
            "to": chart['Date'].iat[-1]
        },
        "forecast_avg": int(round(float(forecast.mean()))),
        "units_sold": actual.tolist(),
        "xgb_sales_pred": xgb_sales_pred.tolist(),
        "predicted_inventory_levels": predicted_inventory,
        "actual_avg": int(round(float(actual_raw.mean()))),
        "holding_cost": int(round(float(hc))),
        "ordering_cost": int(round(float(oc))),
        "lead_time": int(lt),
        "eoq": eoq,
        "safety_stock": ss,
        "reorder_point_daily": rop_series.tolist(),
        "reorder_needed": reorder_flag,
        "total_holding_cost": total_holding_cost,
        "total_ordering_cost": total_ordering_cost,
        "daily_inventory_levels": chart['inventory_level'].tolist(),
        "stockout_days": stockout_days,
        "overstock_days": overstock_days,
        "chart": chart.to_dict(orient='records')
    })
