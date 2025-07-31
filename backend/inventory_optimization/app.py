# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import pandas as pd
# import numpy as np

# app = Flask(__name__)
# CORS(app)

# df = pd.read_csv("xgboost_advanced_predictions.csv")
# df.columns = df.columns.str.strip()
# df['Date'] = pd.to_datetime(df['Date'])

# def calculate_inventory_metrics(demand_forecast, holding_cost, lead_time, ordering_cost, service_level=0.95):
#     avg_demand = demand_forecast.mean()
#     demand_std = demand_forecast.std()
#     z = 1.65 if service_level == 0.95 else 1.28

#     eoq = np.sqrt((2 * avg_demand * ordering_cost) / holding_cost)
#     safety_stock = z * demand_std * np.sqrt(lead_time)
#     reorder_point = avg_demand * lead_time + safety_stock

#     return round(eoq, 2), round(safety_stock, 2), round(reorder_point, 2)


# @app.route('/forecast-inventory', methods=['GET'])
# def forecast_inventory():
#     pid = request.args.get('product_id', type=int)
#     region = request.args.get('region', type=int)
#     if pid is None or region is None:
#         return jsonify({"error": "Missing product_id or region"}), 400

#     filtered = df[(df['Product ID'] == pid) & (df['Region'] == region)]

#     if filtered.empty:
#         return jsonify({"error": "No data found for given product_id and region"}), 404

#     latest = filtered['Date'].max()
#     last_30 = filtered[filtered['Date'] >= latest - pd.Timedelta(days=29)]

#     if last_30.empty:
#         return jsonify({"error": "No data found for the last 30 days"}), 404

#     try:
#         hc = filtered['Holding Cost per Unit'].iloc[0]
#         lt = filtered['Lead Time (Days)'].iloc[0]
#         oc = filtered.get('Ordering Cost', pd.Series([0])).iloc[0]  # default 0 if not present

#         forecast = last_30['Predicted_Demand']
#         actual = last_30['Demand']
#         units_sold = last_30['Units Sold']
#         inv = filtered.iloc[-1]['Inventory Level']
#     except Exception as e:
#         return jsonify({"error": f"Data extraction error: {str(e)}"}), 500

#     eoq, ss, rop = calculate_inventory_metrics(forecast, hc, lt, oc)
#     reorder_flag = bool(inv <= rop)


#     chart = last_30[['Date']].copy()
#     chart['actual'] = actual.values
#     chart['predicted'] = forecast.values
#     chart['Date'] = chart['Date'].dt.strftime('%Y-%m-%d')
#     chart['units_sold'] = units_sold.values

#     return jsonify({
#         "product_id": pid,
#         "region": region,
#         "date_range": {
#             "from": chart['Date'].iat[0],
#             "to": chart['Date'].iat[-1]
#         },
#         "forecast_avg": round(float(forecast.mean()), 2),
#         "units_sold": actual.tolist(), 
#         "actual_avg": round(float(actual.mean()), 2),
#         "holding_cost": float(hc),
#         "ordering_cost": float(oc),
#         "lead_time": int(lt),
#         "eoq": eoq,
#         "safety_stock": ss,
#         "reorder_point": rop,
#         "latest_inventory": float(inv),
#         "reorder_needed": reorder_flag,
#         "chart": chart.to_dict(orient='records')
#     })

# if __name__ == "__main__":
#     app.run(debug=True)


# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import pandas as pd
# import numpy as np

# app = Flask(__name__)
# CORS(app)

# df = pd.read_csv("xgboost_advanced_predictions.csv")
# df.columns = df.columns.str.strip()
# df['Date'] = pd.to_datetime(df['Date'])

# def calculate_inventory_metrics(demand_forecast, holding_cost, lead_time, ordering_cost, service_level=0.95):
#     avg_demand = demand_forecast.mean()
#     demand_std = demand_forecast.std()
#     z = 1.65 if service_level == 0.95 else 1.28

#     eoq = np.sqrt((2 * avg_demand * ordering_cost) / holding_cost)
#     safety_stock = z * demand_std * np.sqrt(lead_time)
#     reorder_point = avg_demand * lead_time + safety_stock

#     return round(eoq, 2), round(safety_stock, 2), round(reorder_point, 2)


# @app.route('/forecast-inventory', methods=['GET'])
# def forecast_inventory():
#     pid = request.args.get('product_id', type=int)
#     store_id = request.args.get('store_id', type=int)   # Changed here
#     if pid is None or store_id is None:
#         return jsonify({"error": "Missing product_id or store_id"}), 400

#     # Filter by Product ID and Store ID instead of Region
#     filtered = df[(df['Product ID'] == pid) & (df['Store ID'] == store_id)]

#     if filtered.empty:
#         return jsonify({"error": "No data found for given product_id and store_id"}), 404

#     latest = filtered['Date'].max()
#     last_30 = filtered[filtered['Date'] >= latest - pd.Timedelta(days=29)]

#     if last_30.empty:
#         return jsonify({"error": "No data found for the last 30 days"}), 404

#     try:
#         hc = filtered['Holding Cost per Unit'].iloc[0]
#         lt = filtered['Lead Time (Days)'].iloc[0]
#         oc = filtered.get('Ordering Cost', pd.Series([0])).iloc[0]  # default 0 if not present

#         forecast = last_30['Predicted_Demand']
#         actual = last_30['Demand']
#         units_sold = last_30['Units Sold']
#         inv = filtered.iloc[-1]['Inventory Level']
#     except Exception as e:
#         return jsonify({"error": f"Data extraction error: {str(e)}"}), 500

#     eoq, ss, rop = calculate_inventory_metrics(forecast, hc, lt, oc)
#     reorder_flag = bool(inv <= rop)

#     chart = last_30[['Date']].copy()
#     chart['actual'] = actual.values
#     chart['predicted'] = forecast.values
#     chart['Date'] = chart['Date'].dt.strftime('%Y-%m-%d')
#     chart['units_sold'] = units_sold.values

#     return jsonify({
#         "product_id": pid,
#         "store_id": store_id,
#         "date_range": {
#             "from": chart['Date'].iat[0],
#             "to": chart['Date'].iat[-1]
#         },
#         "forecast_avg": round(float(forecast.mean()), 2),
#         "units_sold": actual.tolist(),
#         "actualavg": round(float(actual.mean()), 2),
#         "holding_cost": float(hc),
#         "ordering_cost": float(oc),
#         "lead_time": int(lt),
#         "eoq": eoq,
#         "safety_stock": ss,
#         "reorder_point": rop,
#         "latest_inventory": float(inv),
#         "reorder_needed": reorder_flag,
#         "chart": chart.to_dict(orient='records')
#     })

# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)

df = pd.read_csv("xgboost_advanced_predictions.csv")
df.columns = df.columns.str.strip()
df['Date'] = pd.to_datetime(df['Date'])

def calculate_inventory_metrics(demand_forecast, holding_cost, lead_time, ordering_cost, service_level=0.95):
    avg_demand = demand_forecast.mean()
    demand_std = demand_forecast.std()
    z = 1.65 if service_level == 0.95 else 1.28

    eoq = np.sqrt((2 * avg_demand * ordering_cost) / holding_cost)
    safety_stock = z * demand_std * np.sqrt(lead_time)
    reorder_point = avg_demand * lead_time + safety_stock

    return round(eoq, 2), round(safety_stock, 2), round(reorder_point, 2)

@app.route('/forecast-inventory', methods=['GET'])
def forecast_inventory():
    pid = request.args.get('product_id', type=int)
    store_id = request.args.get('store_id', type=int)

    if pid is None or store_id is None:
        return jsonify({"error": "Missing product_id or store_id"}), 400

    filtered = df[(df['Product ID'] == pid) & (df['Store ID'] == store_id)]

    if filtered.empty:
        return jsonify({"error": "No data found for given product_id and store_id"}), 404

    latest = filtered['Date'].max()
    last_30 = filtered[filtered['Date'] >= latest - pd.Timedelta(days=29)]

    if last_30.empty:
        return jsonify({"error": "No data found for the last 30 days"}), 404

    try:
        hc = filtered['Holding Cost per Unit'].iloc[0]
        lt = filtered['Lead Time (Days)'].iloc[0]
        oc = filtered.get('Ordering Cost', pd.Series([0])).iloc[0]

        forecast = last_30['Predicted_Demand']
        actual = last_30['Demand']
        units_sold = last_30['Units Sold']
        inventory = last_30['Inventory Level']
    except Exception as e:
        return jsonify({"error": f"Data extraction error: {str(e)}"}), 500

    eoq, ss, rop = calculate_inventory_metrics(forecast, hc, lt, oc)
    latest_inventory = inventory.iloc[-1]
    reorder_flag = bool(latest_inventory <= rop)

    chart = last_30[['Date']].copy()
    chart['actual'] = actual.values
    chart['predicted'] = forecast.values
    chart['units_sold'] = units_sold.values
    chart['inventory_level'] = inventory.values
    chart['Date'] = chart['Date'].dt.strftime('%Y-%m-%d')

    return jsonify({
        "product_id": pid,
        "store_id": store_id,
        "date_range": {
            "from": chart['Date'].iat[0],
            "to": chart['Date'].iat[-1]
        },
        "forecast_avg": round(float(forecast.mean()), 2),
        "units_sold": actual.tolist(),
        "actual_avg": round(float(actual.mean()), 2),
        "holding_cost": float(hc),
        "ordering_cost": float(oc),
        "lead_time": int(lt),
        "eoq": eoq,
        "safety_stock": ss,
        "reorder_point": rop,
        "latest_inventory": float(latest_inventory),
        "reorder_needed": reorder_flag,
        "daily_inventory_levels": inventory.tolist(),
        "chart": chart.to_dict(orient='records')
    })

if __name__ == "__main__":
    app.run(debug=True)
