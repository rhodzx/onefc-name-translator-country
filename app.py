import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd

st.set_page_config(page_title="ONE FC Name Translator + Country", page_icon="🏋️")
st.title("🏋️ ONE FC Athlete Name Translator + Country")

url = st.text_input("Paste the ONE FC athlete URL:", "https://www.onefc.com/athletes/rodtang/")

@st.cache_data(show_spinner=False)
def get_all_slug_country():
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get("https://www.onefc.com/athletes/", headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    slug_country = {}
    cards = soup.select("a.c-card-athlete__link")
    for card in cards:
        href = card.get("href")
        country_tag = card.select_one(".c-card-athlete__country")
        if href and country_tag:
            slug = href.strip("/").split("/")[-1]
            slug_country[slug] = country_tag.text.strip()
    return slug_country

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

    with st.spinner("Fetching names and country..."):
        results = {lang: fetch_name(link) for lang, link in langs.items()}
        slug_country_map = get_all_slug_country()
        country = slug_country_map.get(slug, "Not found")

    st.markdown(f"**🌍 Country:** `{country}`")
    df = pd.DataFrame(results.items(), columns=["Language", "Name"])
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📅 Download CSV", data=csv, file_name="onefc_names_country.csv", mime="text/csv")
