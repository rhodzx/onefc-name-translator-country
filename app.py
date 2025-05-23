
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from urllib.parse import urlparse
import time

st.set_page_config(page_title="ONE FC Name + Country", page_icon="🌍")
st.title("🌍 ONE FC Athlete Name Translator + Country")

url = st.text_input("Paste the ONE FC athlete URL:", "https://www.onefc.com/athletes/rodtang/")

def fetch_name_country(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    time.sleep(2)

    try:
        name = driver.find_element(By.TAG_NAME, "h1").text
    except:
        name = "Name not found"

    try:
        country = driver.find_element(By.XPATH, "//h6[text()='COUNTRY']/following-sibling::div").text
    except:
        country = "Country not found"

    driver.quit()
    return name, country

if "/athletes/" in url:
    parsed = urlparse(url)
    slug = parsed.path.strip('/').split('/')[-1]
    langs = {
        "English": f"https://www.onefc.com/athletes/{slug}/",
        "Thai": f"https://www.onefc.com/th/athletes/{slug}/",
        "Japanese": f"https://www.onefc.com/jp/athletes/{slug}/",
        "Chinese": f"https://www.onefc.com/cn/athletes/{slug}/"
    }

    with st.spinner("Fetching names and country..."):
        results = {}
        country = "Not found"
        for lang, link in langs.items():
            name, extracted_country = fetch_name_country(link)
            results[lang] = name
            if lang == "English":
                country = extracted_country

    st.markdown(f"**🌍 Country:** `{country}`")
    df = pd.DataFrame(results.items(), columns=["Language", "Name"])
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="onefc_names_country.csv", mime="text/csv")
