from flask import Flask
from backend.sales_prediction.routes import sales_prediction_bp
#from backend.inventory_optimization.routes import inventory_optimization_bp
#from backend.customer_segmentation.routes import customer_segmentation_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(sales_prediction_bp, url_prefix='/sales_prediction')
#app.register_blueprint(inventory_optimization_bp, url_prefix='/inventory_optimization')
#app.register_blueprint(customer_segmentation_bp, url_prefix='/customer_segmentation')

if __name__ == '__main__':
    app.run(debug=True)
