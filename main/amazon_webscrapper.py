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


    urls = [
        "https://www.amazon.nl/gp/bestsellers/electronics/16366027031"
        # "https://www.amazon.nl/gp/bestsellers/electronics/16366027031?pg=1"
        # "https://www.amazon.nl/gp/bestsellers/electronics/16366027031?pg=2"
    ]

    data = []

    for url in urls:
        driver.get(url)
        time.sleep(5)  # allow full render
        soup = BeautifulSoup(driver.page_source, "html.parser")

        items = soup.select('div.zg-grid-general-faceout, div.p13n-grid-content')  # robust selection

        for item in items:

            # print("========== RAW HTML ==========")
            # print(item.prettify())
            # break

            # Title from image alt
            img_tag = item.select_one('img')
            title = img_tag['alt'] if img_tag and img_tag.has_attr('alt') else None

            # URL
            link_tag = item.select_one('a.a-link-normal')
            url = f"https://www.amazon.nl{link_tag['href']}" if link_tag and link_tag.has_attr("href") else None

            # Price (finally working)
            # Try standard price class first
            price_tag = item.select_one('span._cDEzb_p13n-sc-price_3mJ9Z')

            # Fallback to a-offscreen
            if not price_tag:
                price_tag = item.select_one('span.a-offscreen')

            # Fallback to price-whole + price-fraction
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

            # try:
            #     table = driver.find_element(By.ID, "productDetails_detailBullets_sections1")
            #     rows = table.find_elements(By.TAG_NAME, "tr")
            #     bestseller_rank = None
            #     for row in rows:
            #         header = row.find_element(By.TAG_NAME, "th").text.strip()
            #         if "Best verkochte rang" in header:
            #             value = row.find_element(By.TAG_NAME, "td").text.strip()
            #             bestseller_rank = value
            #             break
            #     print(f"📦 Bestseller Rank: {bestseller_rank}")
            # except Exception as e:
            #     print(f"⚠️ Could not extract bestseller rank: {e}")

            data.append({
                "Title": title,
                "Price (€)": price,
                "Rating": rating,
                # "Bestseller rank": bestseller_rank,
                "URL": url
            })

    driver.quit()

    # Save to CSV and preview
    df = pd.DataFrame(data)
    df["Rating (out of 5)"] = df["Rating"].apply(parse_rating)
    df["ASIN"] = df["URL"].apply(extract_asin)
    # Drop duplicates by ASIN
    df = df.drop_duplicates(subset="ASIN").reset_index(drop=True)
    df.to_csv(output_path/"amazon_top50_laptops.csv", index=False)
    print("✅ Saved to amazon_top50_laptops.csv")

