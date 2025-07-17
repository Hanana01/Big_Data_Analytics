def load_and_merge_sales():
    import pandas as pd

    sales = pd.read_csv("data/sales.csv")
    products = pd.read_csv("data/products.csv")

    # Remove any leading/trailing spaces in column names
    sales.columns = sales.columns.str.strip()
    products.columns = products.columns.str.strip()

    # Ensure matching dtypes for merge
    sales["Product ID"] = sales["Product ID"].astype(str)
    products["Product ID"] = products["Product ID"].astype(str)

    sales["Date"] = pd.to_datetime(sales["Date"])
    products["Date"] = pd.to_datetime(products["Date"])

    sales["Store ID"] = sales["Store ID"].astype(str)
    products["Store ID"] = products["Store ID"].astype(str)

    merged = sales.merge(products, on=["Product ID", "Date", "Store ID"], how="left")
    
    # Optional: print merged columns for debugging
    print("Merged Columns:", merged.columns.tolist())

    return merged
