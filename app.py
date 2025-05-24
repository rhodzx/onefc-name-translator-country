import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd

st.set_page_config(page_title="ONE FC Name Translator + Country", page_icon="🏋️")
st.title("🏋️ ONE FC Athlete Name Translator + Country")

url = st.text_input("Paste the ONE FC athlete URL:", "https://www.onefc.com/athletes/rodtang/")

@st.cache_data(ttl=86400)
def fetch_slug_country_mapping():
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get("https://www.onefc.com/athletes/", headers=headers, timeout=10)
    soup = BeautifulSoup(r.content, 'html.parser')
    cards = soup.select("a.c-card-athlete__link")
    mapping = {}
    for card in cards:
        href = card.get("href")
        country_tag = card.select_one(".c-card-athlete__country")
        if href and country_tag:
            slug = href.strip('/').split('/')[-1].lower()
            country = country_tag.get_text(strip=True)
            mapping[slug] = country
    return mapping

slug_to_country = fetch_slug_country_mapping()

def fetch_name(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, 'html.parser')

        h1 = soup.find('h1', {'class': 'use-letter-spacing-hint my-4'}) or soup.find('h1')
        return h1.get_text(strip=True) if h1 else "Name not found"
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

    with st.spinner("Fetching names..."):
        results = {lang: fetch_name(link) for lang, link in langs.items()}
        country = slug_to_country.get(slug, "Not found")

    st.markdown(f"**🌍 Country:** `{country}`")
    df = pd.DataFrame(results.items(), columns=["Language", "Name"])
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("🗕️ Download CSV", data=csv, file_name="onefc_names_country.csv", mime="text/csv")
