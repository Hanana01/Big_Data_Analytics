from flask import Blueprint, jsonify, send_from_directory
import pandas as pd
import os

sales_bp = Blueprint("sales_bp", __name__)

DATA_PATH = "./data/sales.csv"  

@sales_bp.route("/stores")
def get_stores():
    df = pd.read_csv(DATA_PATH)
    stores = sorted(df["Store ID"].dropna().unique().tolist())
    return jsonify(stores)

@sales_bp.route("/products")
def get_products():
    df = pd.read_csv(DATA_PATH)

    products_df = df[["Product ID", "Product_Name"]].dropna().drop_duplicates()

    products_df = products_df.sort_values("Product_Name")

    products = products_df.rename(columns={"Product ID": "id", "Product_Name": "name"}).to_dict(orient="records")

    return jsonify(products)


@sales_bp.route("/summary")
def summary():
    summary_path = "accuracy_per_product/top2_model_summary.csv"
    if os.path.exists(summary_path):
        df = pd.read_csv(summary_path)
        return jsonify(df.to_dict(orient="records"))
    return jsonify([])

@sales_bp.route("/predictions/<int:store>/<product>")
def predictions(store, product):
    filename = f"store_predictions/Store_{store}_Product_{product}_predictions.csv"
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        return jsonify(df.to_dict(orient="records"))
    return jsonify({"error": "File not found"}), 404

@sales_bp.route("/images/<int:store>/<product>/<chart_type>")
def get_chart(store, product, chart_type):
    folder = "results_per_product"
    filename = f"Store_{store}_Product_{product}_actual_vs_best2_{chart_type}.png"
    filepath = os.path.join(folder, filename)
    if os.path.exists(filepath):
        return send_from_directory(folder, filename)
    return jsonify({"error": "Image not found"}), 404

@sales_bp.route("/download/<int:store>/<product>")
def download_csv(store, product):
    folder = "store_predictions"
    filename = f"Store_{store}_Product_{product}_predictions.csv"
    filepath = os.path.join(folder, filename)
    if os.path.exists(filepath):
        return send_from_directory(folder, filename, as_attachment=True)
    return jsonify({"error": "CSV not found"}), 404
