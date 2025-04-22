import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import quote

# ------------------ Page Config ------------------
st.set_page_config(page_title="📉 ShadeCheck - Market Investigations", layout="wide")

st.title("🕵️‍♂️ ShadeCheck - Market Investigation Scanner")

# ------------------ Helper Functions ------------------
def scrape_sebi_actions():
    url = "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=3&smid=0&cid=0&type=All"
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all("li")
        investigations = []
        for li in items:
            text = li.text.strip()
            if any(word in text.lower() for word in ["fraud", "investigation", "action", "penalty"]):
                investigations.append(text)
        return investigations[:10]  # Return top 10
    except:
        return ["Error fetching SEBI data"]

def scrape_ed_actions():
    try:
        ed_news = []
        response = requests.get("https://www.enforcementdirectorate.gov.in/press-release")
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all("li")
        for li in items:
            text = li.text.strip()
            if any(word in text.lower() for word in ["money laundering", "probe", "notice", "raid", "chargesheet"]):
                ed_news.append(text)
        return ed_news[:10]
    except:
        return ["Could not fetch ED updates"]

def scrape_income_tax_actions():
    try:
        tax_news = []
        response = requests.get("https://incometaxindia.gov.in/pages/press-releases.aspx")
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all("li")
        for li in items:
            text = li.text.strip()
            if any(word in text.lower() for word in ["raid", "evasion", "notice", "discrepancy"]):
                tax_news.append(text)
        return tax_news[:10]
    except:
        return ["Could not fetch Income Tax updates"]

def forensic_lookup(company_name):
    search_query = quote(company_name)
    try:
        search_url = f"https://www.screener.in/api/company/search/?q={search_query}"
        search_response = requests.get(search_url).json()
        if not search_response:
            return ["No company found. Please try another name."]

        company_code = search_response[0]['slug']
        company_url = f"https://www.screener.in/company/{company_code}/"
        r = requests.get(company_url)
        soup = BeautifulSoup(r.text, "html.parser")

        about = soup.find("div", class_="company-profile")
        about_text = about.text.strip() if about else "No company description found."

        ratios_section = soup.find("section", id="top-ratios")
        ratios = ratios_section.text.strip() if ratios_section else "Key ratios not available."

        promoter_section = soup.find("section", id="promoters")
        promoters_text = promoter_section.text.strip() if promoter_section else "Promoter data not available."

        sector = soup.find("a", href=lambda x: x and "/sector/" in x)
        sector_name = sector.text.strip() if sector else "Sector info unavailable."

        return [
            f"**About Company:** {about_text}",
            f"**Sector:** {sector_name}",
            f"**Key Financial Ratios:** {ratios}",
            f"**Promoter and Board Info:** {promoters_text}",
            f"🔗 [Visit Screener Page]({company_url})"
        ]
    except Exception as e:
        return [f"Error retrieving data: {str(e)}"]

# ------------------ UI Layout ------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔍 Search Forensic Summary")
    company_input = st.text_input("Enter Company Name or NSE Code:", "Reliance")
    if st.button("Run Forensic Check"):
        with st.spinner("Gathering forensic insights..."):
            results = forensic_lookup(company_input)
            for res in results:
                st.markdown(res)

with col2:
    st.subheader("📋 Latest Regulatory Investigations")
    if st.button("Refresh Headlines"):
        with st.spinner("Fetching latest updates from regulatory bodies..."):
            sebi = scrape_sebi_actions()
            ed = scrape_ed_actions()
            tax = scrape_income_tax_actions()

            st.markdown("### 🔎 SEBI Investigations")
            for s in sebi:
                st.warning(s)

            st.markdown("### 🏛️ ED Actions")
            for e in ed:
                st.error(e)

            st.markdown("### 💸 Income Tax Actions")
            for i in tax:
                st.success(i)

st.markdown("---")
st.caption("Data aggregated from public sources including SEBI, ED, Income Tax Dept., and Screener.in")
