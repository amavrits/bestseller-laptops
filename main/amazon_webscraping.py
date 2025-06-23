from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
from pathlib import Path
import time
from main.utils import *


if __name__ == "__main__":

    output_path = Path("../data")
    output_path.mkdir(parents=True, exist_ok=True)

    # Setup headless Chrome
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    url = "https://www.amazon.nl/gp/bestsellers/electronics/16366027031"
    driver.get(url)

    # 🔽 Scroll slowly to trigger lazy loading of all 50 laptops
    scroll_pause_time = 1.0
    scroll_increment = 500
    current_position = 0
    max_scrolls = 30

    for _ in range(max_scrolls):
        driver.execute_script(f"window.scrollTo(0, {current_position});")
        time.sleep(scroll_pause_time)
        current_position += scroll_increment

    soup = BeautifulSoup(driver.page_source, "html.parser")
    items = soup.select('div.zg-grid-general-faceout, div.p13n-grid-content')  # robust selection

    data = []

    for item in items:

        # Title from image alt
        img_tag = item.select_one('img')
        title = img_tag['alt'] if img_tag and img_tag.has_attr('alt') else None

        # URL
        link_tag = item.select_one('a.a-link-normal')
        url = f"https://www.amazon.nl{link_tag['href']}" if link_tag and link_tag.has_attr("href") else None

        # Price
        price_tag = item.select_one('span._cDEzb_p13n-sc-price_3mJ9Z')
        if not price_tag:
            price_tag = item.select_one('span.a-offscreen')
        if not price_tag:
            whole = item.select_one('span.a-price-whole')
            frac = item.select_one('span.a-price-fraction')
            if whole:
                price = f"{whole.text.strip()}.{frac.text.strip() if frac else '00'}"
            else:
                price = None
        else:
            price = (
                price_tag.get_text(strip=True)
                .replace("€", "")
                .replace("\xa0", "")
                .replace(",", ".")
            )

        # Rating
        rating_tag = item.select_one('span.a-icon-alt')
        rating = rating_tag.get_text(strip=True) if rating_tag else None

        data.append({
            "Title": title,
            "Price (€)": price,
            "Rating": rating,
            "URL": url
        })

    driver.quit()

    # Save to CSV
    df = pd.DataFrame(data)
    df["Rating (out of 5)"] = df["Rating"].apply(parse_rating)
    df["ASIN"] = df["URL"].apply(extract_asin)
    df = df.drop_duplicates(subset="ASIN").reset_index(drop=True)
    df.to_csv(output_path / "amazon_top50_laptops.csv", index=False)
    print("✅ Saved to amazon_top50_laptops.csv")

