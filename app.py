

import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd

st.set_page_config(page_title="ONE Athlete Profile", page_icon="🥊")
st.title("🥊 ONE Athlete Profile")

url = st.text_input("Paste the ONE athlete URL:", "https://www.onefc.com/athletes/rodtang/")

def fetch_name(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, 'html.parser')
        h1 = soup.find('h1', {'class': 'use-letter-spacing-hint my-4'}) or soup.find('h1')
        return h1.get_text(strip=True) if h1 else "Name not found"
    except Exception as e:
        return "Error: " + str(e)

def fetch_country_from_page(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, 'html.parser')

        # Search for ALL "attr" blocks
        attr_blocks = soup.select("div.attr")
        for block in attr_blocks:
            title = block.find("h5", class_="title")
            if title and "country" in title.get_text(strip=True).lower():
                value = block.find("div", class_="value")
                if value and value.a:
                    return value.a.get_text(strip=True)

        return "Country not found"
    except Exception as e:
        return f"Error: {e}"

if "/athletes/" in url:
    parsed = urlparse(url)
    slug = parsed.path.strip('/').split('/')[-1].lower()

    langs = {
        "English": f"https://www.onefc.com/athletes/{slug}/",
        "Thai": f"https://www.onefc.com/th/athletes/{slug}/",
        "Japanese": f"https://www.onefc.com/jp/athletes/{slug}/",
        "Chinese": f"https://www.onefc.com/cn/athletes/{slug}/"
    }

    with st.spinner("Fetching names and country..."):
        results = {lang: fetch_name(link) for lang, link in langs.items()}
        country = fetch_country_from_page(url)

    st.markdown(f"**🌍 Nationality:** `{country}`")
    df = pd.DataFrame(results.items(), columns=["Language", "Name"])
    st.dataframe(df)
