import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd

st.set_page_config(page_title="ONE FC Name Translator + Country", page_icon="🏋️")
st.title("🏋️ ONE FC Athlete Name Translator + Country")

url = st.text_input("Paste the ONE FC athlete URL:", "https://www.onefc.com/athletes/rodtang/")

def fetch_country_from_google(slug, api_key):
    try:
        query = f"{slug.replace('-', ' ')} nationality"
        params = {
            "q": query,
            "api_key": api_key,
            "engine": "google",
            "hl": "en"
        }
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        results = response.json()

        # 1. Look in answer_box if present
        if 'answer_box' in results:
            ab = results['answer_box']
            for key in ['answer', 'snippet', 'highlighted_words']:
                if key in ab:
                    val = ab[key]
                    if isinstance(val, list):
                        return ', '.join(val)
                    return val

        # 2. Try the organic results for any line that mentions 'nationality'
        for result in results.get('organic_results', []):
            snippet = result.get('snippet', '').lower()
            if 'nationality' in snippet:
                return result.get('snippet')

        return "Not found"
    except Exception as e:
        return "Not found"

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

    with st.spinner("Fetching names and country..."):
        results = {lang: fetch_name(link) for lang, link in langs.items()}
        country = fetch_country_from_google(slug, st.secrets["SERPAPI_KEY"])

    st.markdown(f"**🌍 Country:** `{country}`")
    df = pd.DataFrame(results.items(), columns=["Language", "Name"])
    st.dataframe(df)
