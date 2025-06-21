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
You are an expert product reviewer. Summarize the following real customer reviews for the laptop titled:

"{title}"

Instructions:
- Focus ONLY on product-related features: screen, keyboard, speed, battery, build quality, thermal performance, etc.
- Do NOT include shipping, packaging, pricing, seller issues, or Amazon service.
- Write two brief, accurate, and specific summaries:
  1. Summary of Praises
  2. Summary of Complaints

Reviews:
{reviews_text}
"""

if __name__ == "__main__":
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    reviews_dir = Path("../data/laptop_reviews")
    summary_path = Path("../results/laptop_review_summaries")
    summary_path.mkdir(parents=True, exist_ok=True)

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

            try:
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

                # # Parse summaries
                # match = re.search(r"1\.\s*Summary of Praises[:\n]*(.*)2\.\s*Summary of Complaints[:\n]*(.*)", result,
                #                   re.DOTALL)
                # if match:
                #     praise = match.group(1).strip()
                #     complaint = match.group(2).strip()
                # else:
                #     # fallback in case GPT format is unexpected
                #     praise, complaint = result.strip(), ""

                # Extract sections more reliably
                praise = ""
                complaint = ""

                # Pattern matches both numbered and markdown headers
                pattern = re.search(
                    r"(?:1\.|###)\s*Summary of Praises[:\n]*(.*?)(?:2\.|###)\s*Summary of Complaints[:\n]*(.*)",
                    result,
                    re.DOTALL,
                )

                if pattern:
                    praise = pattern.group(1).strip()
                    complaint = pattern.group(2).strip()

                    # Clean up bullet characters or excessive line breaks
                    complaint = re.sub(r"\n- ?", "\n", complaint)
                    complaint = re.sub(r"^- ?", "", complaint)
                    complaint = re.sub(r"\s+", " ", complaint).strip()

                    praise = re.sub(r"\n- ?", "\n", praise)
                    praise = re.sub(r"^- ?", "", praise)
                    praise = re.sub(r"\s+", " ", praise).strip()
                else:
                    # fallback in case the format is not matched
                    praise, complaint = result.strip(), ""

                # Write to JSON
                summary_data = {
                    "ASIN": data["ASIN"],
                    "Title": data["Title"],
                    "Number of Reviews": len(reviews),
                    "Praise Summary": praise,
                    "Complaint Summary": complaint
                }
                with open(summary_path / f"{data['ASIN']}.json", "w", encoding="utf-8") as f:
                    json.dump(summary_data, f, ensure_ascii=False, indent=2)

                print(f"[{i+1}/{n_items}] ✅ Summarized: {data['Title'][:60]}")
            except Exception as e:
                print(f"❌ Error summarizing {filename}: {e}")

    print(f"\n✅ All GPT summaries extracted!")
