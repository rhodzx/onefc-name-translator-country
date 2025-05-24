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
            "engine": "google"
        }
        response = requests.get("https://serpapi.com/search", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Try direct answer
        answer_box = data.get("answer_box", {})
        if "answer" in answer_box:
            return answer_box["answer"]

        # Try nationality list like ["Italian", "Moroccan"]
        if "list" in answer_box:
            return ", ".join(answer_box["list"])

        # Fallback to scanning snippet for country names
        if "organic_results" in data:
            snippet = data["organic_results"][0].get("snippet", "").lower()
            known_countries = [
                "Thailand", "United States", "Brazil", "Japan", "China", "Russia",
                "Italy", "Morocco", "Philippines", "France", "India", "Singapore"
            ]
            for country in known_countries:
                if country.lower() in snippet:
                    return country

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
        country = fetch_country_from_google(slug, st.secrets["SERPAPI_KEY"])

    st.markdown(f"**🌍 Country:** `{country}`")
    df = pd.DataFrame(results.items(), columns=["Language", "Name"])
    st.dataframe(df)
