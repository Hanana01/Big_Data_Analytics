import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import matplotlib.pyplot as plt  # Importing matplotlib for plotting

def train_model():
    # Load dataset
    current_dir = os.path.dirname(__file__)
    data_path = os.path.join(current_dir, 'data/processed_sales.csv')
    df = pd.read_csv(data_path)

    # Define features and target variable
    X = df.drop(columns=['Units Sold', 'Date'])  # Exclude target & date
    y = df['Units Sold']  # Target variable

    # Split data (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train Random Forest model
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)

    # Model evaluation
    y_pred = rf.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    # Save the trained model
    model_path = os.path.join(current_dir, 'data/random_forest_model.pkl')
    joblib.dump(rf, model_path)

    # Save predictions
    predictions_df = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})
    predictions_df.to_csv(os.path.join(current_dir, 'data/predictions.csv'), index=False)

    # Save model performance metrics
    performance_path = os.path.join(current_dir, 'data/model_performance.txt')
    with open(performance_path, 'w') as f:
        f.write(f"R² Score: {r2:.4f}\n")
        f.write(f"Mean Absolute Error (MAE): {mae:.4f}\n")

    # Feature importance visualization
    feature_importance = pd.DataFrame({'Feature': X.columns, 'Importance': rf.feature_importances_})
    feature_importance = feature_importance.sort_values(by='Importance', ascending=False)

    # Plotting the feature importance
    plt.figure(figsize=(10, 6))
    plt.barh(feature_importance['Feature'], feature_importance['Importance'], color='skyblue')
    plt.xlabel('Importance')
    plt.ylabel('Feature')
    plt.title('Feature Importance - Random Forest Model')
    plt.gca().invert_yaxis()  # To display the most important feature at the top
    plt.show()

    print(f"\n Model training completed.")
    print(f" R² Score: {r2:.4f}")
    print(f" Mean Absolute Error (MAE): {mae:.4f}")
    print(f" Model saved at: {model_path}")
    print(f" Predictions saved at: {os.path.join(current_dir, 'data/predictions.csv')}")
    print(f" Model performance saved at: {performance_path}")

# Run training
if __name__ == '__main__':
    train_model()
