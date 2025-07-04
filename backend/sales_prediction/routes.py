from flask import Blueprint, jsonify
from .train_model import train_forecast_model

sales_bp = Blueprint("sales", __name__)

@sales_bp.route("/", methods=["GET"])
def get_sales_forecast():
    try:
        forecast = train_forecast_model()
        return jsonify(forecast)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
