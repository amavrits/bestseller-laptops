import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import json
from pathlib import Path
from main.find_bestsellers.utils import extract_asin


if __name__ == "__main__":

    ROOT_DIR = Path(__file__).resolve().parents[2]  # go up to the project root
    DATA_DIR = ROOT_DIR / "data"
    CSV_PATH = DATA_DIR / "amazon_top50_laptops.csv"
    REVIEWS_DIR = DATA_DIR / "laptop_reviews"

    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)

    # Load laptop CSV
    df = pd.read_csv(CSV_PATH)
    df["Number of Reviews"] = 0

    # Headless Chrome setup
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.amazon.nl/product-reviews/B0DZDD4M3Z")
    input("🔐 Please log in to Amazon in the browser, then press ENTER here to continue...")

    # Loop through each product
    for index, row in df.iterrows():
        asin = extract_asin(row["URL"])
        if not asin:
            continue

        review_url = f"https://www.amazon.nl/product-reviews/{asin}?sortBy=recent"
        print(f"[{index + 1}/{len(df)}] Collecting reviews for: {row['Title'][:60]}")

        reviews = []
        driver.get(review_url)
        time.sleep(3)

        for _ in range(3):  # Collect up to 3 pages
            soup = BeautifulSoup(driver.page_source, "html.parser")
            review_elements = driver.find_elements(By.CSS_SELECTOR, "span[data-hook='review-body']")
            reviews = [el.text.strip() for el in review_elements]

            # Go to next page if available
            next_button = soup.select_one("li.a-last > a")
            if next_button and 'href' in next_button.attrs:
                next_link = "https://www.amazon.nl" + next_button['href']
                driver.get(next_link)
                time.sleep(2)
            else:
                break

        # Save reviews to a file
        data = {
            "Title": row["Title"],
            "ASIN": asin,
            "URL": row["URL"],
            "Reviews": reviews
        }

        number_of_reviews = len(reviews)
        df.loc[index, "Number of Reviews"] = number_of_reviews

        with open(REVIEWS_DIR/f"{asin}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    driver.quit()
    print("✅ Saved all reviews!")

    df.to_csv(CSV_PATH, index=False)
    print("✅ Saved laptops with number of reviews to amazon_top50_laptops.csv")
