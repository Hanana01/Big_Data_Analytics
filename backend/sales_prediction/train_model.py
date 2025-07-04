import pandas as pd
from prophet import Prophet
from .preprocess import load_and_merge_sales

def train_forecast_model():
    df = load_and_merge_sales()
    df["Date"] = pd.to_datetime(df["Date"])

    # Use the correct column name
    product_sales = df.groupby("Date")["Units Sold_x"].sum().reset_index()
    product_sales.columns = ["ds", "y"]

    model = Prophet(daily_seasonality=True, yearly_seasonality=True, weekly_seasonality=True)
    model.fit(product_sales)

    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    return forecast[["ds", "yhat"]].tail(30).to_dict(orient="records")
