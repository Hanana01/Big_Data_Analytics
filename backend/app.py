from flask import Flask
from flask_cors import CORS

# Import blueprints from their respective modules
from sales_prediction.routes import sales_bp
from inventory_optimization.routes import inventory_bp

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for all routes

# Register sales prediction routes under /api/sales
app.register_blueprint(sales_bp, url_prefix="/api/sales")

# Register inventory optimization routes under /api/inventory
app.register_blueprint(inventory_bp, url_prefix="/api/inventory")

if __name__ == '__main__':
    # Run the app on port 5000 with debug mode enabled
    app.run(debug=True, port=5000)

