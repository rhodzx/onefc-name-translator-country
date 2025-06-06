import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd

st.set_page_config(page_title="ONE Athlete Profile", page_icon="🥊")
st.title("🥊 ONE Athlete Profile")

url = st.text_input("Paste the ONE athlete URL:", "https://www.onefc.com/athletes/rodtang/")

# Hardcoded emoji flags (expand as needed)
country_flags = {
    "Thailand": "🇹🇭",
    "Philippines": "🇵🇭",
    "Japan": "🇯🇵",
    "China": "🇨🇳",
    "Singapore": "🇸🇬",
    "United States": "🇺🇸",
    "Malaysia": "🇲🇾",
    "Brazil": "🇧🇷",
    "India": "🇮🇳",
    "Russia": "🇷🇺",
    "South Korea": "🇰🇷",
    "Vietnam": "🇻🇳",
    "France": "🇫🇷",
    "Azerbaijan": "🇦🇿",
    "Belarus": "🇧🇾",
    "Canada": "🇨🇦",
    "Italy": "🇮🇹",
    "United Kingdom": "🇬🇧",
    "Morocco": "🇲🇦",
    "Algeria": "🇩🇿",
    "Senegal": "🇸🇳",
    "Hong Kong SAR China": "🇭🇰",
    "Australia": "🇦🇺",
    "Germany": "🇩🇪",
    "Netherlands": "🇳🇱",
    "Argentina": "🇦🇷",
    "Colombia": "🇨🇴",
    "Myanmar": "🇲🇲",
    "Indonesia": "🇮🇩",
    "Kazakhstan": "🇰🇿",
    "Ukraine": "🇺🇦",
    "South Africa": "🇿🇦",
    "Turkey": "🇹🇷",
    "Iran": "🇮🇷",
    "Pakistan": "🇵🇰",
    "Nepal": "🇳🇵",
    "Cambodia": "🇰🇭",
    "Laos": "🇱🇦",
    "Taiwan": "🇹🇼",
    "Mongolia": "🇲🇳",
    "New Zealand": "🇳🇿",
    "Spain": "🇪🇸",
    "Portugal": "🇵🇹",
    "Sweden": "🇸🇪",
    "Norway": "🇳🇴",
    "Denmark": "🇩🇰",
    "Finland": "🇫🇮",
    "Poland": "🇵🇱",
    "Czech Republic": "🇨🇿",
    "Slovakia": "🇸🇰",
    "Hungary": "🇭🇺",
    "Romania": "🇷🇴",
    "Bulgaria": "🇧🇬",
    "Greece": "🇬🇷",
    "Serbia": "🇷🇸",
    "Croatia": "🇭🇷",
    "Slovenia": "🇸🇮",
    "Bosnia and Herzegovina": "🇧🇦",
    "North Macedonia": "🇲🇰",
    "Albania": "🇦🇱",
    "Georgia": "🇬🇪",
    "Armenia": "🇦🇲",
    "Azerbaijan": "🇦🇿",
    "Uzbekistan": "🇺🇿",
    "Turkmenistan": "🇹🇲",
    "Kyrgyzstan": "🇰🇬",
    "Tajikistan": "🇹🇯",
    "Afghanistan": "🇦🇫",
    "Iraq": "🇮🇶",
    "Syria": "🇸🇾",
    "Lebanon": "🇱🇧",
    "Jordan": "🇯🇴",
    "Israel": "🇮🇱",
    "Palestine": "🇵🇸",
    "Saudi Arabia": "🇸🇦",
    "United Arab Emirates": "🇦🇪",
    "Qatar": "🇶🇦",
    "Kuwait": "🇰🇼",
    "Bahrain": "🇧🇭",
    "Oman": "🇴🇲",
    "Yemen": "🇾🇪",
    "Egypt": "🇪🇬",
    "Tunisia": "🇹🇳",
    "Algeria": "🇩🇿",
    "Morocco": "🇲🇦",
    "Libya": "🇱🇾",
    "Sudan": "🇸🇩",
    "Ethiopia": "🇪🇹",
    "Kenya": "🇰🇪",
    "Uganda": "🇺🇬",
    "Tanzania": "🇹🇿",
    "Rwanda": "🇷🇼",
    "Burundi": "🇧🇮",
    "Democratic Republic of the Congo": "🇨🇩",
    "Republic of the Congo": "🇨🇬",
    "Gabon": "🇬🇦",
    "Equatorial Guinea": "🇬🇶",
    "Cameroon": "🇨🇲",
    "Nigeria": "🇳🇬",
    "Ghana": "🇬🇭",
    "Ivory Coast": "🇨🇮",
    "Senegal": "🇸🇳",
    "Mali": "🇲🇱",
    "Niger": "🇳🇪",
    "Burkina Faso": "🇧🇫",
    "Togo": "🇹🇬",
    "Benin": "🇧🇯",
    "Sierra Leone": "🇸🇱",
    "Liberia": "🇱🇷",
    "Guinea": "🇬🇳",
    "Guinea-Bissau": "🇬🇼",
    "Gambia": "🇬🇲",
    "Cape Verde": "🇨🇻",
    "Mauritania": "🇲🇷",
    "Namibia": "🇳🇦",
    "Botswana": "🇧🇼",
    "Zimbabwe": "🇿🇼",
    "Zambia": "🇿🇲",
    "Malawi": "🇲🇼",
    "Mozambique": "🇲🇿",
    "Angola": "🇦🇴",
    "South Sudan": "🇸🇸",
    "Lesotho": "🇱🇸",
    "Eswatini": "🇸🇿",
    "Madagascar": "🇲🇬",
    "Mauritius": "🇲🇺",
    "Seychelles": "🇸🇨",
    "Comoros": "🇰🇲",
    "Maldives": "🇲🇻",
    "Sri Lanka": "🇱🇰",
    "Bangladesh": "🇧🇩",
    "Bhutan": "🇧🇹",
    "Nepal": "🇳🇵",
    "Mongolia": "🇲🇳",
    "North Korea": "🇰🇵",
    "South Korea": "🇰🇷",
    "Taiwan": "🇹🇼",
    "Hong Kong SAR China": "🇭🇰",
    "Macau SAR China": "🇲🇴",
    "Brunei": "🇧🇳",
    "Timor-Leste": "🇹🇱",
    "Papua New Guinea": "🇵🇬",
    "Fiji": "🇫🇯",
    "Samoa": "🇼🇸",
    "Tonga": "🇹🇴",
    "Vanuatu": "🇻🇺",
    "Solomon Islands": "🇸🇧",
    "Micronesia": "🇫🇲",
    "Palau": "🇵🇼",
    "Marshall Islands": "🇲🇭",
    "Nauru": "🇳🇷",
    "Tuvalu": "🇹🇻",
    "Kiribati": "🇰🇮",
    "Cook Islands": "🇨🇰",
    "Niue": "🇳🇺",
    "Tokelau": "🇹🇰",
    "Wallis and Futuna": "🇼🇫",
    "New Caledonia": "🇳🇨",
    "French Polynesia": "🇵🇫",
    "Guam": "🇬🇺",
    "Northern Mariana Islands": "🇲🇵",
    "American Samoa": "🇦🇸",
    "Puerto Rico": "🇵🇷",
    "U.S. Virgin Islands": "🇻🇮",
    "British Virgin Islands": "🇻🇬",
    "Cayman Islands": "🇰🇾",
    "Bermuda": "🇧🇲",
    "Greenland": "🇬🇱",
    "Faroe Islands": "🇫🇴",
    "Isle of Man": "🇮🇲",
    "Jersey": "🇯🇪",
    "Guernsey": "🇬🇬",
    "Gibraltar": "🇬🇮",
    "San Marino": "🇸🇲",
    "Monaco": "🇲🇨",
    "Liechtenstein": "🇱🇮",
    "Andorra": "🇦🇩",
    "Vatican City": "🇻🇦",
    "Luxembourg": "🇱🇺",
    "Malta": "🇲🇹",
    "Iceland": "🇮🇸",
    "Estonia": "🇪🇪",
    "Latvia": "🇱🇻",
    "Lithuania": "🇱🇹",
    "Belarus": "🇧🇾",
    "Moldova": "🇲🇩",
    "Armenia": "🇦🇲",
    "Azerbaijan": "🇦🇿",
    "Georgia": "🇬🇪",
    "Kazakhstan": "🇰🇿",
    "Kyrgyzstan": "🇰🇬",
    "Tajikistan": "🇹🇯",
    "Turkmenistan": "🇹🇲",
    "Uzbekistan": "🇺🇿"
}


# Function to fetch all countries from ONE site
def fetch_countries_from_page(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, 'html.parser')

        countries = []
        attr_blocks = soup.select("div.attr")
        for block in attr_blocks:
            title = block.find("h5", class_="title")
            if title and "country" in title.get_text(strip=True).lower():
                value = block.find("div", class_="value")
                if value:
                    countries = [a.get_text(strip=True) for a in value.find_all("a")]
                break
        return countries or ["Country not found"]
    except Exception as e:
        return [f"Error: {e}"]

# Function to fetch name from localized pages
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

# Main app logic
if "/athletes/" in url:
    parsed = urlparse(url)
    slug = parsed.path.strip('/').split('/')[-1].lower()

    langs = {
        "English": f"https://www.onefc.com/athletes/{slug}/",
        "Thai": f"https://www.onefc.com/th/athletes/{slug}/",
        "Japanese": f"https://www.onefc.com/jp/athletes/{slug}/",
        "Chinese": f"https://www.onefc.com/cn/athletes/{slug}/"
    }

    with st.spinner("Fetching names and nationalities..."):
        results = {lang: fetch_name(link) for lang, link in langs.items()}
        countries = fetch_countries_from_page(url)
        flags = [country_flags.get(c, "") for c in countries]
        joined = " / ".join(f"`{c}` {f}" for c, f in zip(countries, flags))

    st.markdown(f"**🌍 Nationality:** {joined}")
    df = pd.DataFrame(results.items(), columns=["Language", "Name"])
    st.dataframe(df)
