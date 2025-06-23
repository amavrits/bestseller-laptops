import os
import pandas as pd
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
from main.find_bestsellers.utils import parse_brand_model


def build_brand_model_prompt(title):
    return f"""
You are an expert in laptop product identification.

Given this product title from Amazon:

"{title}"

Extract:
1. Brand name (e.g., Apple, ASUS, HP)
2. Laptop model (e.g., MacBook Air M2, ZenBook 14, HP Pavilion 15-eg)

Respond in this format:
Brand: <brand>
Model: <model>
"""


if __name__ == "__main__":

    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    ROOT_DIR = Path(__file__).resolve().parents[2]  # go up to the project root
    DATA_DIR = ROOT_DIR / "data"
    CSV_PATH = DATA_DIR / "amazon_top50_laptops.csv"

    df = pd.read_csv(CSV_PATH)
    df["Brand"] = ""
    df["Model"] = ""

    for index, row in df.iterrows():

        title = row["Title"]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You extract brand and model names from product titles."},
                {"role": "user", "content": build_brand_model_prompt(title)}
            ],
            temperature=0,
            max_tokens=100
        )

        result = response.choices[0].message.content.strip()

        brand, model = parse_brand_model(result)
        df.loc[index, "Brand"] = brand
        df.loc[index, "Model"] = model

        print(f"[{index + 1}/{len(df)}] ✅ Extracted {title}")

    df.to_csv(CSV_PATH, index=False)

