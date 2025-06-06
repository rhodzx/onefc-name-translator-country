import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd
import pycountry

st.set_page_config(page_title="ONE Athlete Profile", page_icon="🥊")
st.title("🥊 ONE Athlete Profile")

url = st.text_input("Paste the ONE athlete URL:", "https://www.onefc.com/athletes/rodtang/")

# Convert country name to flag emoji
def country_to_flag(country_name):
    try:
        country = pycountry.countries.get(name=country_name)
        if not country:
            for c in pycountry.countries:
                if country_name.lower() in c.name.lower():
                    country = c
                    break
        if country:
            code = country.alpha_2.upper()
            return chr(127397 + ord(code[0])) + chr(127397 + ord(code[1]))
        return ""
    except:
        return ""

# Fetch the country from the ONE athlete page
def fetch_country_from_page(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, 'html.parser')

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

# Fetch name from localized pages
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

if "/athletes/" in url:
    parsed = urlparse(url)
    slug = parsed.path.strip('/').split('/')[-1].lower()

    langs = {
        "English": f"https://www.onefc.com/athletes/{slug}/",
        "Thai": f"https://www.onefc.com/th/athletes/{slug}/",
        "Japanese": f"https://www.onefc.com/jp/athletes/{slug}/",
        "Chinese": f"https://www.onefc.com/cn/athletes/{slug}/"
    }

    with st.spinner("Fetching names and nationality..."):
        results = {lang: fetch_name(link) for lang, link in langs.items()}
        country = fetch_country_from_page(url)
        flag = country_to_flag(country)

    st.markdown(f"**🌍 Nationality:** `{country}` {flag}")
    df = pd.DataFrame(results.items(), columns=["Language", "Name"])
    st.dataframe(df)
