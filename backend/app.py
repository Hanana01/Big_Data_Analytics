from flask import Flask
from flask_cors import CORS
from sales_prediction.routes import sales_bp
#from backend.inventory_optimization.routes import inventory_optimization_bp
#from backend.customer_segmentation.routes import customer_segmentation_bp

app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(sales_bp, url_prefix='/sales_prediction')
#app.register_blueprint(inventory_optimization_bp, url_prefix='/inventory_optimization')
#app.register_blueprint(customer_segmentation_bp, url_prefix='/customer_segmentation')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
