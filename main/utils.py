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


if __name__ == "__main__":

    pass

