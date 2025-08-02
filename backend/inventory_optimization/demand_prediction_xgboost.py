# import pandas as pd
# import numpy as np
# from sklearn.model_selection import train_test_split, GridSearchCV
# from sklearn.metrics import (
#     mean_absolute_error,
#     mean_absolute_percentage_error,
#     mean_squared_error,
#     r2_score
# )
# from xgboost import XGBRegressor
# import joblib
# import matplotlib.pyplot as plt
# from sklearn.preprocessing import RobustScaler
# from sklearn.pipeline import Pipeline

# def load_data(filepath):
#     df = pd.read_csv(filepath)
#     df['Date'] = pd.to_datetime(df['Date'])

#     # Temporal features
#     df['DayOfWeek'] = df['Date'].dt.dayofweek
#     df['DayOfMonth'] = df['Date'].dt.day
#     df['WeekOfYear'] = df['Date'].dt.isocalendar().week.astype(int)
#     df['Quarter'] = df['Date'].dt.quarter

#     # Sort & create lags/rolling
#     df = df.sort_values(['Product ID', 'Date']).reset_index(drop=True)
#     df['Demand_t-1'] = df.groupby('Product ID')['Demand'].shift(1)
#     df['Demand_t-7'] = df.groupby('Product ID')['Demand'].shift(7)
#     df['RollingMean_7'] = df.groupby('Product ID')['Demand'].rolling(7).mean().reset_index(0, drop=True)
#     df['RollingStd_7'] = df.groupby('Product ID')['Demand'].rolling(7).std().reset_index(0, drop=True)

#     df.dropna(inplace=True)
#     return df

# def train_model(X_train, y_train):
#     pipeline = Pipeline([
#         ('scaler', RobustScaler()),
#         ('xgb', XGBRegressor(random_state=42))
#     ])

#     param_grid = {
#         'xgb__n_estimators': [300],
#         'xgb__max_depth': [6, 9],
#         'xgb__learning_rate': [0.05],
#         'xgb__subsample': [0.8],
#         'xgb__colsample_bytree': [0.8]
#     }

#     grid_search = GridSearchCV(
#         estimator=pipeline,
#         param_grid=param_grid,
#         cv=3,
#         scoring='neg_mean_absolute_error',
#         n_jobs=-1,
#         verbose=1
#     )

#     print("Training XGBoost model...")
#     grid_search.fit(X_train, y_train)
#     print("Best parameters:", grid_search.best_params_)
#     return grid_search.best_estimator_

# def calculate_metrics(y_true, y_pred):
#     metrics = {
#         'MAE': mean_absolute_error(y_true, y_pred),
#         'MAPE (%)': mean_absolute_percentage_error(y_true[y_true > 0], y_pred[y_true > 0]) * 100,
#         'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
#         'R² Score': r2_score(y_true, y_pred),
#         # 'Perfect Predictions': sum(y_true == y_pred),
#         # 'Perfect Prediction Rate': f"{100 * sum(y_true == y_pred)/len(y_true):.2f}%"
#     }

#     print("\nModel Evaluation:")
#     for k, v in metrics.items():
#         print(f"{k}: {v}")
#     return metrics

# def generate_predictions(model, df, X, y):
#     df = df.copy()
#     df['Predicted_Demand_Raw'] = model.predict(X)
#     df['Predicted_Demand'] = np.round(df['Predicted_Demand_Raw'])
#     df['Absolute_Error'] = np.abs(y - df['Predicted_Demand'])
#     df['Percentage_Error'] = np.where(
#         y > 0,
#         (df['Absolute_Error'] / y) * 100,
#         np.nan
#     )
#     return df

# if __name__ == "__main__":
#     DATA_PATH = "../data/ecommerce_demand_data.csv"
#     OUTPUT_PATH = "xgboost_advanced_predictions.csv"
#     MODEL_PATH = "xgboost_advanced_model.pkl"
#     # FEATURE_IMPORTANCE_PATH = "xgboost_advanced_feature_importance.png"

#     print("Loading and preprocessing data...")
#     df = load_data(DATA_PATH)

#     target = df['Demand']
#     features = df.drop(columns=['Demand', 'Date', 'Product ID','Units Sold','Units Ordered'])

#     X_train, X_test, y_train, y_test = train_test_split(
#         features, target, test_size=0.2, random_state=42
#     )

#     model = train_model(X_train, y_train)
#     joblib.dump(model, MODEL_PATH)

#     y_pred = model.predict(X_test)
#     y_pred_rounded = np.round(y_pred)
#     y_true_rounded = np.round(y_test)
#     calculate_metrics(y_true_rounded, y_pred_rounded)

#     print("\nGenerating predictions for full dataset...")
#     full_predictions = generate_predictions(model, df, features, target)
#     full_predictions.to_csv(OUTPUT_PATH, index=False)

#     perfect_preds = full_predictions[full_predictions['Absolute_Error'] == 0]
#     print(f"\nPerfect predictions analysis:")
#     # print(f"Total perfect predictions: {len(perfect_preds)}")
#     # print(f"Perfect prediction rate: {100*len(perfect_preds)/len(full_predictions):.2f}%")

#     # Feature importance
#     plt.figure(figsize=(12, 8))
#     feat_importances = pd.Series(
#         model.named_steps['xgb'].feature_importances_,
#         index=features.columns
#     )
#     feat_importances.nlargest(15).plot(kind='barh')
#     plt.title('XGBoost Feature Importance')
#     plt.tight_layout()
#     # plt.savefig(FEATURE_IMPORTANCE_PATH, dpi=300)
#     plt.close()

#     # Last 30 days prediction & visualization per Product ID
#     product_id_input = input("Enter the Product ID to predict last 30 days demand for: ")
#     try:
#         product_id = int(product_id_input)
#     except ValueError:
#         print("Invalid Product ID entered. Exiting.")
#         exit(1)

#     df_product = df[df['Product ID'] == product_id].copy()
#     if df_product.empty:
#         print(f"No data found for Product ID {product_id}. Exiting.")
#         exit(1)

#     last_30_days = df_product[df_product['Date'] >= (df_product['Date'].max() - pd.Timedelta(days=29))].copy()
#     if last_30_days.empty:
#         print(f"No data available for the last 30 days for Product ID {product_id}. Exiting.")
#         exit(1)

#     X_last_30 = last_30_days.drop(columns=['Demand', 'Date', 'Product ID','Units Sold','Units Ordered'])
#     y_last_30 = last_30_days['Demand']

#     y_pred_last_30 = model.predict(X_last_30)
#     y_pred_last_30_rounded = np.round(y_pred_last_30)

#     plt.figure(figsize=(14, 7))
#     plt.plot(last_30_days['Date'], y_last_30, label='Actual Demand', marker='o')
#     plt.plot(last_30_days['Date'], y_pred_last_30_rounded, label='Predicted Demand', marker='x')
#     plt.xticks(rotation=45)
#     plt.xlabel('Date')
#     plt.ylabel('Demand')
#     plt.title(f'Actual vs Predicted Demand - Last 30 Days - Product {product_id}')
#     plt.legend()
#     plt.tight_layout()
#     plt.savefig(f"last_30_days_demand_prediction_product_{product_id}.png", dpi=300)
#     plt.show()

#     print(f"\nLast 30 days prediction visualization saved as last_30_days_demand_prediction_product_{product_id}.png")
#     print("\nTraining complete. Files saved:")
#     print(f"- {OUTPUT_PATH}")
#     print(f"- {MODEL_PATH}")
#     # print(f"- {FEATURE_IMPORTANCE_PATH}")

import pandas as pd
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    r2_score
)
from xgboost import XGBRegressor
import joblib
import matplotlib.pyplot as plt
from sklearn.preprocessing import RobustScaler
from sklearn.pipeline import Pipeline

def load_data(filepath):
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])

    # Temporal features
    df['DayOfWeek'] = df['Date'].dt.dayofweek
    df['DayOfMonth'] = df['Date'].dt.day
    df['WeekOfYear'] = df['Date'].dt.isocalendar().week.astype(int)
    df['Quarter'] = df['Date'].dt.quarter

    # Sort & create lags/rolling
    df = df.sort_values(['Product ID', 'Date']).reset_index(drop=True)
    df['Demand_t-1'] = df.groupby('Product ID')['Demand'].shift(1)
    df['Demand_t-7'] = df.groupby('Product ID')['Demand'].shift(7)
    df['RollingMean_7'] = df.groupby('Product ID')['Demand'].rolling(7).mean().reset_index(0, drop=True)
    df['RollingStd_7'] = df.groupby('Product ID')['Demand'].rolling(7).std().reset_index(0, drop=True)

    df.dropna(inplace=True)
    return df

def train_model(X_train, y_train):
    pipeline = Pipeline([
        ('scaler', RobustScaler()),
        ('xgb', XGBRegressor(random_state=42))
    ])

    param_grid = {
        'xgb__n_estimators': [300],
        'xgb__max_depth': [6, 9],
        'xgb__learning_rate': [0.05],
        'xgb__subsample': [0.8],
        'xgb__colsample_bytree': [0.8]
    }
#     param_grid = {
#     'xgb__n_estimators': [50],          
#     'xgb__max_depth': [2],               
#     'xgb__learning_rate': [0.1],        
#     'xgb__subsample': [0.4],            
#     'xgb__colsample_bytree': [0.4],      
#     'xgb__reg_alpha': [5],               
#     'xgb__reg_lambda': [10]              
# }


    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        cv=3,
        scoring='neg_mean_absolute_error',
        n_jobs=-1,
        verbose=1
    )

    print("Training XGBoost model...")
    grid_search.fit(X_train, y_train)
    print("Best parameters:", grid_search.best_params_)
    return grid_search.best_estimator_

def calculate_metrics(y_true, y_pred):
    metrics = {
        'MAE': mean_absolute_error(y_true, y_pred),
        'MAPE (%)': mean_absolute_percentage_error(y_true[y_true > 0], y_pred[y_true > 0]) * 100,
        'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
        'R² Score': r2_score(y_true, y_pred),
    }

    print("\nModel Evaluation:")
    for k, v in metrics.items():
        print(f"{k}: {v}")
    return metrics

def generate_predictions(model, df, X, y):
    df = df.copy()
    df['Predicted_Demand'] = np.round(model.predict(X))
    # df['Predicted_Demand_Raw'] = model.predict(X)
    # df['Predicted_Demand'] = np.round(df['Predicted_Demand_Raw'])
    # df['Absolute_Error'] = np.abs(y - df['Predicted_Demand'])
    # df['Percentage_Error'] = np.where(
    #     y > 0,
    #     (df['Absolute_Error'] / y) * 100,
    #     np.nan
    # )
    return df

if __name__ == "__main__":
    DATA_PATH = "../data/ecommerce_demand_data.csv"
    MODEL_PATH = "xgboost_advanced_model.pkl"
    FULL_PREDICTIONS_PATH = "../data/xgboost_advanced_predictions.csv"
    TEST_PREDICTIONS_PATH = "../data/xgboost_testset_predictions.csv"

    print("Loading and preprocessing data...")
    df = load_data(DATA_PATH)

    # Time-based split
    df_sorted = df.sort_values('Date').reset_index(drop=True)
    split_index = int(len(df_sorted) * 0.8)

    train_df = df_sorted.iloc[:split_index]
    test_df = df_sorted.iloc[split_index:]

    X_train = train_df.drop(columns=['Demand', 'Date', 'Product ID'])
    y_train = train_df['Demand']
    X_test = test_df.drop(columns=['Demand', 'Date', 'Product ID'])
    y_test = test_df['Demand']

    model = train_model(X_train, y_train)
    joblib.dump(model, MODEL_PATH)

    # Evaluate model on test set
    y_pred = model.predict(X_test)
    y_pred_rounded = np.round(y_pred)
    y_true_rounded = np.round(y_test)
    calculate_metrics(y_true_rounded, y_pred_rounded)

    # Save predictions on test set
    test_predictions_df = test_df.copy()
    test_predictions_df['Predicted_Demand_Raw'] = y_pred
    test_predictions_df['Predicted_Demand'] = y_pred_rounded
    test_predictions_df['Absolute_Error'] = np.abs(y_test - y_pred_rounded)
    test_predictions_df['Percentage_Error'] = np.where(
        y_test > 0,
        (test_predictions_df['Absolute_Error'] / y_test) * 100,
        np.nan
    )
    test_predictions_df.to_csv(TEST_PREDICTIONS_PATH, index=False)
    print(f"\nTest set predictions saved to {TEST_PREDICTIONS_PATH}")

    # Full dataset predictions
    print("\nGenerating predictions for full dataset...")
    features_full = df.drop(columns=['Demand', 'Date', 'Product ID'])
    target_full = df['Demand']
    full_predictions = generate_predictions(model, df, features_full, target_full)
    full_predictions.to_csv(FULL_PREDICTIONS_PATH, index=False)

    # Feature importance
    plt.figure(figsize=(12, 8))
    feat_importances = pd.Series(
        model.named_steps['xgb'].feature_importances_,
        index=features_full.columns
    )
    feat_importances.nlargest(15).plot(kind='barh')
    plt.title('XGBoost Feature Importance')
    plt.tight_layout()
    plt.savefig("xgboost_feature_importance.png", dpi=300)
    plt.close()

    # Last 30 days visualization
    product_id_input = input("Enter the Product ID to predict last 30 days demand for: ")
    try:
        product_id = int(product_id_input)
    except ValueError:
        print("Invalid Product ID entered. Exiting.")
        exit(1)

    df_product = df[df['Product ID'] == product_id].copy()
    if df_product.empty:
        print(f"No data found for Product ID {product_id}. Exiting.")
        exit(1)

    last_30_days = df_product[df_product['Date'] >= (df_product['Date'].max() - pd.Timedelta(days=29))].copy()
    if last_30_days.empty:
        print(f"No data available for the last 30 days for Product ID {product_id}. Exiting.")
        exit(1)

    X_last_30 = last_30_days.drop(columns=['Demand', 'Date', 'Product ID'])
    y_last_30 = last_30_days['Demand']
    y_pred_last_30 = model.predict(X_last_30)
    y_pred_last_30_rounded = np.round(y_pred_last_30)

    plt.figure(figsize=(14, 7))
    plt.plot(last_30_days['Date'], y_last_30, label='Actual Demand', marker='o')
    plt.plot(last_30_days['Date'], y_pred_last_30_rounded, label='Predicted Demand', marker='x')
    plt.xticks(rotation=45)
    plt.xlabel('Date')
    plt.ylabel('Demand')
    plt.title(f'Actual vs Predicted Demand - Last 30 Days - Product {product_id}')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"last_30_days_demand_prediction_product_{product_id}.png", dpi=300)
    plt.show()

    print(f"\nLast 30 days prediction visualization saved as last_30_days_demand_prediction_product_{product_id}.png")
    print("\nTraining complete. Files saved:")
    print(f"- {MODEL_PATH}")
    print(f"- {FULL_PREDICTIONS_PATH}")
    print(f"- {TEST_PREDICTIONS_PATH}")
    print(f"- last_30_days_demand_prediction_product_{product_id}.png")
    print(f"- xgboost_feature_importance.png")


# import pandas as pd
# import numpy as np
# from sklearn.metrics import (
#     mean_absolute_error,
#     mean_absolute_percentage_error,
#     mean_squared_error,
#     r2_score
# )
# from xgboost import XGBRegressor
# import joblib
# import matplotlib.pyplot as plt
# from sklearn.preprocessing import RobustScaler
# from sklearn.pipeline import Pipeline
# from sklearn.model_selection import GridSearchCV

# def load_data(filepath):
#     df = pd.read_csv(filepath)
#     df['Date'] = pd.to_datetime(df['Date'])

#     # Temporal features
#     df['DayOfWeek'] = df['Date'].dt.dayofweek
#     df['DayOfMonth'] = df['Date'].dt.day
#     df['WeekOfYear'] = df['Date'].dt.isocalendar().week.astype(int)
#     df['Quarter'] = df['Date'].dt.quarter

#     # Lag & rolling
#     df = df.sort_values(['Product ID', 'Date']).reset_index(drop=True)
#     df['Demand_t-1'] = df.groupby('Product ID')['Demand'].shift(1)
#     df['Demand_t-7'] = df.groupby('Product ID')['Demand'].shift(7)
#     df['RollingMean_7'] = df.groupby('Product ID')['Demand'].rolling(7).mean().reset_index(0, drop=True)
#     df['RollingStd_7'] = df.groupby('Product ID')['Demand'].rolling(7).std().reset_index(0, drop=True)

#     df.dropna(inplace=True)
#     return df

# def train_model(X_train, y_train):
#     pipeline = Pipeline([
#         ('scaler', RobustScaler()),
#         ('xgb', XGBRegressor(random_state=42))
#     ])

#     param_grid = {
#         'xgb__n_estimators': [300],
#         'xgb__max_depth': [6, 9],
#         'xgb__learning_rate': [0.05],
#         'xgb__subsample': [0.8],
#         'xgb__colsample_bytree': [0.8]
#     }

#     grid_search = GridSearchCV(
#         estimator=pipeline,
#         param_grid=param_grid,
#         cv=3,
#         scoring='neg_mean_absolute_error',
#         n_jobs=-1,
#         verbose=1
#     )

#     print("Training XGBoost model...")
#     grid_search.fit(X_train, y_train)
#     print("Best parameters:", grid_search.best_params_)
#     return grid_search.best_estimator_

# def calculate_metrics(y_true, y_pred):
#     metrics = {
#         'MAE': mean_absolute_error(y_true, y_pred),
#         'MAPE (%)': mean_absolute_percentage_error(y_true[y_true > 0], y_pred[y_true > 0]) * 100,
#         'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
#         'R² Score': r2_score(y_true, y_pred),
#     }

#     print("\nModel Evaluation:")
#     for k, v in metrics.items():
#         print(f"{k}: {v:.2f}")
#     return metrics

# def generate_predictions(model, df, X, y):
#     df = df.copy()
#     df['Predicted_Demand_Raw'] = model.predict(X)
#     df['Predicted_Demand'] = np.round(df['Predicted_Demand_Raw'])
#     df['Absolute_Error'] = np.abs(y - df['Predicted_Demand'])
#     df['Percentage_Error'] = np.where(
#         y > 0,
#         (df['Absolute_Error'] / y) * 100,
#         np.nan
#     )
#     return df

# if __name__ == "__main__":
#     DATA_PATH = "../data/ecommerce_demand_data.csv"
#     OUTPUT_PATH = "xgboost_testset_predictions.csv"
#     MODEL_PATH = "xgboost_model.pkl"

#     print("Loading and preprocessing data...")
#     df = load_data(DATA_PATH)

#     target = df['Demand']
#     features = df.drop(columns=['Demand', 'Date', 'Product ID', 'Units Sold', 'Units Ordered'])

#     # Time-based train/test split (first 80% for train, last 20% for test)
#     split_index = int(len(df) * 0.8)
#     X_train, X_test = features.iloc[:split_index], features.iloc[split_index:]
#     y_train, y_test = target.iloc[:split_index], target.iloc[split_index:]
#     df_test = df.iloc[split_index:]

#     model = train_model(X_train, y_train)
#     joblib.dump(model, MODEL_PATH)

#     y_pred = model.predict(X_test)
#     y_pred_rounded = np.round(y_pred)
#     y_true_rounded = np.round(y_test)
#     calculate_metrics(y_true_rounded, y_pred_rounded)

#     print("\nSaving test set predictions...")
#     df_test_result = df_test.copy()
#     df_test_result['Predicted_Demand'] = y_pred_rounded
#     df_test_result['Absolute_Error'] = np.abs(df_test_result['Demand'] - df_test_result['Predicted_Demand'])
#     df_test_result['Percentage_Error'] = np.where(
#         df_test_result['Demand'] > 0,
#         (df_test_result['Absolute_Error'] / df_test_result['Demand']) * 100,
#         np.nan
#     )
#     df_test_result.to_csv(OUTPUT_PATH, index=False)

#     print(f"✅ Test set predictions saved to: {OUTPUT_PATH}")
#     print(f"✅ Trained model saved to: {MODEL_PATH}")

