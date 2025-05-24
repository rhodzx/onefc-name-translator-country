import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd

st.set_page_config(page_title="ONE FC Name Translator + Country", page_icon="🏋️")
st.title("🏋️ ONE FC Athlete Name Translator + Country")

url = st.text_input("Paste the ONE FC athlete URL:", "https://www.onefc.com/athletes/rodtang/")

# ✅ NEW: Improved Bing nationality extractor
def fetch_country_from_bing(slug):
    try:
        query = f"{slug.replace('-', ' ')} ONE Championship fighter nationality"
        search_url = f"https://www.bing.com/search?q={requests.utils.quote(query)}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(search_url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')

        # Try Bing's Knowledge Panel
        kp = soup.find('div', {'class': 'b_vPanel'}) or soup.find('div', {'class': 'b_entityTP'})
        if kp:
            lines = kp.get_text(separator='|').split('|')
            for line in lines:
                if 'Nationality' in line:
                    return line.replace('Nationality', '').strip()

        # Fallback: parse snippet in first result
        result = soup.find('li', {'class': 'b_algo'})
        if result:
            snippet = result.find('p')
            if snippet:
                text = snippet.get_text(strip=True)
                for word in text.split():
                    if word.lower() in [
                        "thai", "filipino", "filipina", "american", "brazilian",
                        "russian", "japanese", "chinese", "indian", "singaporean",
                        "indonesian", "malaysian", "australian", "british", "french"
                    ]:
                        return word.capitalize()
        return "Not found"
    except Exception:
        return "Not found"

# Fetch translated name per localized ONE FC page
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

# 🔁 Main execution
if "/athletes/" in url:
    parsed = urlparse(url)
    slug = parsed.path.strip('/').split('/')[-1].lower()

    langs = {
        "English": f"https://www.onefc.com/athletes/{slug}/",
        "Thai": f"https://www.onefc.com/th/athletes/{slug}/",
        "Japanese": f"https://www.onefc.com/jp/athletes/{slug}/",
        "Chinese": f"https://www.onefc.com/cn/athletes/{slug}/"
    }

    with st.spinner("Fetching names and nationality from Bing..."):
        results = {lang: fetch_name(link) for lang, link in langs.items()}
        country = fetch_country_from_bing(slug)

    st.markdown(f"**🌍 Country:** `{country}`")
    df = pd.DataFrame(results.items(), columns=["Language", "Name"])
    st.dataframe(df)
