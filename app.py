import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd

# ✅ Set up Streamlit
st.set_page_config(page_title="ONE FC Name Translator + Country", page_icon="🏋️")
st.title("🏋️ ONE FC Athlete Name Translator + Country")

# ✅ Paste URL
url = st.text_input("Paste the ONE FC athlete URL:", "https://www.onefc.com/athletes/rodtang/")

# ✅ Fetch from SerpAPI (Google)
def fetch_country_from_google_serpapi(slug):
    try:
        name_query = slug.replace('-', ' ')
        params = {
            "q": f"{name_query} nationality",
            "api_key": "8333c89f61cbe6836cd0f1739fe6d95be169c1611c263218abf9e2eb0c4350ad",
            "engine": "google",
            "hl": "en"
        }
        resp = requests.get("https://serpapi.com/search", params=params, timeout=10)
        data = resp.json()

        # Try to extract from "answer box" or organic snippet
        if "answer_box" in data and "answer" in data["answer_box"]:
            return data["answer_box"]["answer"]
        elif "answer_box" in data and "snippet" in data["answer_box"]:
            return data["answer_box"]["snippet"]
        elif "organic_results" in data and len(data["organic_results"]) > 0:
            snippet = data["organic_results"][0].get("snippet", "")
            return snippet.split('.')[0] if snippet else "Not found"
        else:
            return "Not found"
    except Exception:
        return "Not found"

# ✅ Scrape ONEFC name
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

# ✅ Execute only if valid URL
if "/athletes/" in url:
    parsed = urlparse(url)
    slug = parsed.path.strip('/').split('/')[-1].lower()

    langs = {
        "English": f"https://www.onefc.com/athletes/{slug}/",
        "Thai": f"https://www.onefc.com/th/athletes/{slug}/",
        "Japanese": f"https://www.onefc.com/jp/athletes/{slug}/",
        "Chinese": f"https://www.onefc.com/cn/athletes/{slug}/"
    }

    with st.spinner("Fetching translations and nationality..."):
        results = {lang: fetch_name(link) for lang, link in langs.items()}
        country = fetch_country_from_google_serpapi(slug)

    st.markdown(f"**🌍 Country:** `{country}`")
    df = pd.DataFrame(results.items(), columns=["Language", "Name"])
    st.dataframe(df)

