# 📈 Amazon Laptop Market Analysis

This project automates the process of scraping, analyzing, and summarizing customer reviews of the top-selling laptops on Amazon.nl, with a focus on extracting product-specific insights using GPT-4o.

---

## 🚀 Pipeline Overview

### 1. Scrape Bestselling Laptops
- Source: [Amazon.nl Bestsellers - Laptops](https://www.amazon.nl/gp/bestsellers/electronics/16366027031)
- Data collected: Title, URL, price, rating, and ASIN.
- Output: `data/amazon_top50_laptops.csv`

### 2. Collect Reviews
- For each ASIN, fetch customer reviews using Selenium and BeautifulSoup.
- Output: `data/laptop_reviews/{ASIN}.json`

### 3. Summarize Reviews with GPT-4o
- **GPT-4o** is used to extract product-specific **praises** and **complaints**, excluding unrelated content (e.g. shipping, seller).
- Input: JSON reviews per product.
- Output: `results/laptop_review_summaries/{ASIN}.json`

### 4. Merge Summaries with Metadata
- Combines review summaries with price, rating, and ASIN from original CSV.
- Adds brand and model parsed from title.
- Final output: `results/final_laptop_dataset.csv`

---

## 💡 Highlight: GPT-4o Summarization

We use GPT-4o to:
- Parse dozens of user reviews.
- Extract only meaningful, **product-specific** comments.
- Output structured, interpretable summaries for business insight.

This approach avoids noisy data from non-product-related content and makes the dataset highly usable for ML or analysis.

---

## 📁 Project Structure

```
main/
│
├── find_bestsellers/
│   ├── amazon_webscrapping.py
│   ├── collect_reviews.py
│   ├── summarize_reviews.py
│   ├── merge_summaries.py
│   ├── extract_brand_model.py
│   └── finalize_csv.py
│
├── utils.py
├── run_pipeline.sh
├── data/
├── results/
└── README.md
```

---

## ✅ Requirements

- Python 3.11+
- [Poetry](https://python-poetry.org/)
- Google Chrome + chromedriver
- OpenAI API key (with access to GPT-4o)

---

## 📦 Installation

```bash
poetry install
```

## 🔑 API Key

Set your OpenAI API key via `.env` file:

```env
OPENAI_API_KEY=your_key_here
```

---

## 🧪 Run Pipeline

```bash
bash main/run_pipeline.sh
```

This will execute the full process from scraping to review summarization.

---

## 📊 Output

The final dataset is stored in:

```
results/final_laptop_dataset.csv
```

You can use it for downstream analysis, dashboards, or ML pipelines.

---
