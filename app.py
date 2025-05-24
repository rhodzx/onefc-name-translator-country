import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd

st.set_page_config(page_title="ONE FC Name Translator + Country", page_icon="🏋️")
st.title("🏋️ ONE FC Athlete Name Translator + Country")

url = st.text_input("Paste the ONE FC athlete URL:", "https://www.onefc.com/athletes/rodtang/")

# Use SerpAPI to get nationality based on slug
def fetch_country_from_google_serpapi(slug):
    try:
        name_query = slug  # use hyphenated slug directly
        params = {
            "q": f"{name_query} nationality",
            "api_key": "8333c89f61cbe6836cd0f1739fe6d95be169c1611c263218abf9e2eb0c4350ad",
            "engine": "google",
            "hl": "en"
        }
        resp = requests.get("https://serpapi.com/search", params=params, timeout=10)
        data = resp.json()

        if "answer_box" in data:
            abox = data["answer_box"]
            if "answer" in abox:
                return abox["answer"]
            elif "snippet" in abox:
                return abox["snippet"]

        if "organic_results" in data:
            for result in data["organic_results"]:
                snippet = result.get("snippet", "")
                for country in ["china", "thailand", "philippines", "japan", "united states", "russia", "brazil", "india", "france", "uk", "england"]:
                    if country in snippet.lower():
                        return country.title()

        return "Not found"
    except Exception:
        return "Not found"

# Scrape name from each language version of the ONE FC page
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

# Main logic
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
        country = fetch_country_from_google_serpapi(slug)

    st.markdown(f"**🌍 Country:** `{country}`")
    df = pd.DataFrame(results.items(), columns=["Language", "Name"])
    st.dataframe(df)
