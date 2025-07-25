import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    df = pd.read_csv("accuracy_per_product/top2_model_summary.csv")
    print(df.columns)

    models = ['RF', 'GB', 'XGB', 'Prophet', 'SARIMAX']
    summary_rows = []

    for model in models:
        mask1 = df['Best_Model_1'] == model
        mask2 = df['Best_Model_2'] == model

        mae_sales = pd.concat([df.loc[mask1, 'Best1_MAE_Sales'], df.loc[mask2, 'Best2_MAE_Sales']])
        rmse_sales = pd.concat([df.loc[mask1, 'Best1_RMSE_Sales'], df.loc[mask2, 'Best2_RMSE_Sales']])
        mape_sales = pd.concat([df.loc[mask1, 'Best1_MAPE_Sales'], df.loc[mask2, 'Best2_MAPE_Sales']])
        mape_sales = mape_sales.replace([np.inf, -np.inf], np.nan).dropna()
        r2_sales = pd.concat([df.loc[mask1, 'Best1_R2_Sales'], df.loc[mask2, 'Best2_R2_Sales']])

        mae_profit = pd.concat([df.loc[mask1, 'Best1_MAE_Profit'], df.loc[mask2, 'Best2_MAE_Profit']])
        rmse_profit = pd.concat([df.loc[mask1, 'Best1_RMSE_Profit'], df.loc[mask2, 'Best2_RMSE_Profit']])
        mape_profit = pd.concat([df.loc[mask1, 'Best1_MAPE_Profit'], df.loc[mask2, 'Best2_MAPE_Profit']])
        mape_profit = mape_profit.replace([np.inf, -np.inf], np.nan).dropna()
        r2_profit = pd.concat([df.loc[mask1, 'Best1_R2_Profit'], df.loc[mask2, 'Best2_R2_Profit']])

        summary_rows.append({
            'Model': model,
            'Avg_MAE_Sales': mae_sales.mean(),
            'Avg_RMSE_Sales': rmse_sales.mean(),
            'Avg_MAPE_Sales': mape_sales.mean(),
            'Avg_R2_Sales': r2_sales.mean(),
            'Avg_MAE_Profit': mae_profit.mean(),
            'Avg_RMSE_Profit': rmse_profit.mean(),
            'Avg_MAPE_Profit': mape_profit.mean(),
            'Avg_R2_Profit': r2_profit.mean()
        })

    summary = pd.DataFrame(summary_rows)

    print("\n=== Model Performance Summary ===")
    print(summary)

    sns.set(style="whitegrid")
    fig, axes = plt.subplots(2, 4, figsize=(22, 10))

    sns.barplot(data=summary, x='Model', y='Avg_MAE_Sales', ax=axes[0, 0], palette='Blues_d')
    axes[0, 0].set_title('Avg MAE - Sales')

    sns.barplot(data=summary, x='Model', y='Avg_RMSE_Sales', ax=axes[0, 1], palette='Greens_d')
    axes[0, 1].set_title('Avg RMSE - Sales')

    sns.barplot(data=summary, x='Model', y='Avg_MAPE_Sales', ax=axes[0, 2], palette='Reds_d')
    axes[0, 2].set_title('Avg MAPE % - Sales')

    sns.barplot(data=summary, x='Model', y='Avg_R2_Sales', ax=axes[0, 3], palette='Purples_d')
    axes[0, 3].set_title('Avg R² - Sales')

    sns.barplot(data=summary, x='Model', y='Avg_MAE_Profit', ax=axes[1, 0], palette='Blues')
    axes[1, 0].set_title('Avg MAE - Profit')

    sns.barplot(data=summary, x='Model', y='Avg_RMSE_Profit', ax=axes[1, 1], palette='Greens')
    axes[1, 1].set_title('Avg RMSE - Profit')

    sns.barplot(data=summary, x='Model', y='Avg_MAPE_Profit', ax=axes[1, 2], palette='Oranges')
    axes[1, 2].set_title('Avg MAPE % - Profit')

    sns.barplot(data=summary, x='Model', y='Avg_R2_Profit', ax=axes[1, 3], palette='Purples')
    axes[1, 3].set_title('Avg R² - Profit')

    plt.tight_layout()
    plt.savefig("accuracy_per_product/top2_models_full_summary_plot.png")
    plt.show()

if __name__ == "__main__":
    main()
