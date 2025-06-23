import pandas as pd
from pathlib import Path


if __name__ == "__main__":

    ROOT_DIR = Path(__file__).resolve().parents[2]  # go up to the project root
    DATA_DIR = ROOT_DIR / "data"
    CSV_PATH = DATA_DIR / "amazon_top50_laptops.csv"
    OUTPUT_PATH = ROOT_DIR / "results/amazon_top50_laptops.csv"

    df = pd.read_csv(CSV_PATH)

    rename_columns = {
        "Rating (out of 5)": "Average Rating (e.g., 4.5 out of 5)",
        "URL": "Link to Amazon Page (URL)",
        "Praise Summary": "Summary of Praises (Product-specific)",
        "Complaint Summary": "Summary of Complaints (Product-specific)"
    }

    df_final = df.rename(columns=rename_columns)

    columns = [
        "Brand",
        "Model",
        "Price (€)",
        "Average Rating (e.g., 4.5 out of 5)",
        "Number of Reviews",
        "Link to Amazon Page (URL)",
        "Summary of Praises (Product-specific)",
        "Summary of Complaints (Product-specific)"
    ]

    df_final = df_final[columns]
    df_final.to_csv(OUTPUT_PATH)

