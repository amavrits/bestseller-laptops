import pandas as pd
import json
from pathlib import Path
from utils import clean_summary


if __name__ == "__main__":

    # === Paths ===
    ROOT_DIR = Path(__file__).resolve().parents[2]  # go up to the project root
    DATA_DIR = ROOT_DIR / "data"
    CSV_PATH = DATA_DIR / "amazon_top50_laptops.csv"
    SUMMARY_DIR = DATA_DIR / "laptop_review_summaries"

    # === Load main dataset ===
    df = pd.read_csv(CSV_PATH)

    # Ensure ASIN column exists (if not, extract from URL)
    if "ASIN" not in df.columns:
        def extract_asin(url):
            try:
                return url.split("/dp/")[1].split("/")[0]
            except:
                return None
        df["ASIN"] = df["URL"].apply(extract_asin)

    # === Load summaries ===
    summaries = {}
    for file in summary_dir.glob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            summaries[data["ASIN"]] = {
                "Praise Summary": clean_summary(data.get("Praise Summary", "")),
                "Complaint Summary": clean_summary(data.get("Complaint Summary", ""))
            }

    # === Merge into dataframe ===
    df["Praise Summary"] = df["ASIN"].map(lambda asin: summaries.get(asin, {}).get("Praise Summary", ""))
    df["Complaint Summary"] = df["ASIN"].map(lambda asin: summaries.get(asin, {}).get("Complaint Summary", ""))

    # === Save final merged file ===
    df = df.drop(columns=["Rating"])
    df.to_csv(CSV_PATH, index=False)
    print(f"✅ Merged summaries into: {CSV_PATH}")
