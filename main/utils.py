import re
import pandas as pd


# Extract ASIN from Amazon product URL
def extract_asin(url):
    match = re.search(r'/dp/([A-Z0-9]{10})', url)
    return match.group(1) if match else None


def parse_rating(rating_str):
    if pd.isna(rating_str):
        return None
    match = re.search(r"([\d,]+)", rating_str)
    if match:
        return float(match.group(1).replace(",", "."))
    return None


def clean_summary(text):
    # Remove markdown-style headers
    text = re.sub(r"\*\*Summary of Praises:\*\*", "", text)
    text = re.sub(r"\*\*Summary of Complaints:\*\*", "", text)

    # Remove bullet points
    text = re.sub(r"(?m)^- ", "", text)
    text = re.sub(r"\n- ", "\n", text)

    # Final cleanup
    text = text.strip()

    # Return None if the cleaned summary is empty
    return text if text else "NaN"


if __name__ == "__main__":

    pass

