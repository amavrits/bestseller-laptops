import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import re


# Prompt template
def build_prompt(title, reviews):
    reviews_text = "\n\n".join(reviews)
    return f"""
You are an expert product reviewer. Analyze real customer reviews for the laptop titled:

"{title}"

Your task:
- Summarize the key **praises** and **complaints** based only on product features (performance, battery, display, keyboard, etc).
- Ignore seller, shipping, packaging, price, or service issues.

Return your result as a JSON object with exactly two keys:
- "Praise Summary"
- "Complaint Summary"

Example:
{{
  "Praise Summary": "...",
  "Complaint Summary": "..."
}}

Reviews:
{reviews_text}
"""


if __name__ == "__main__":

    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    ROOT_DIR = Path(__file__).resolve().parents[2]  # go up to the project root
    DATA_DIR = ROOT_DIR / "data"
    REVIEWS_DIR = DATA_DIR / "laptop_reviews"
    SUMMARY_DIR = DATA_DIR / "laptop_review_summaries"
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

    review_items = os.listdir(reviews_dir)
    n_items = len(review_items)
    for i, filename in enumerate(review_items):
        if filename.endswith(".json"):
            with open(reviews_dir / filename, "r", encoding="utf-8") as f:
                data = json.load(f)

            reviews = data.get("Reviews", [])
            if not reviews:
                continue

            prompt = build_prompt(data["Title"], reviews)

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You summarize product reviews into pros and cons."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=600
            )

            result = response.choices[0].message.content.strip()
            result = result.replace("json", "")
            result = result.replace("\n", "")
            result = result.replace("`", "")

            summary_obj = json.loads(result)
            praise = summary_obj.get("Praise Summary", "").strip() or None
            complaint = summary_obj.get("Complaint Summary", "").strip() or None

            summary_data = {
                "ASIN": data["ASIN"],
                "Title": data["Title"],
                "Number of Reviews": len(reviews),
                "Praise Summary": praise,
                "Complaint Summary": complaint
            }

            with open(SUMMARY_DIR / f"{data['ASIN']}.json", "w", encoding="utf-8") as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2)

            print(f"[{i + 1}/{n_items}] ✅ Summarized reviews for: {filename}")

    print(f"\n✅ All GPT summaries extracted!")
