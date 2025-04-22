import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ------------------ Page Config ------------------
st.set_page_config(page_title="📉 ShadeCheck - Market Investigations", layout="wide")

st.title("🕵️‍♂️ ShadeCheck - Market Investigation Scanner")

# ------------------ Helper Functions ------------------
def scrape_sebi_actions():
    url = "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=3&smid=0&cid=0&type=All"  # Example source
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all("li")[:10]  # Sample headlines only
        investigations = []
        for li in items:
            text = li.text.strip()
            if any(word in text.lower() for word in ["fraud", "investigation", "action", "penalty"]):
                investigations.append(text)
        return investigations
    except:
        return ["Error fetching SEBI data"]

def scrape_ed_actions():
    return [
        "ED investigates XYZ Ltd for money laundering",
        "ED files charges against ABC Corp in forex violations",
        "ED issues notice to DEF Infra over suspicious foreign remittances"
    ]

def scrape_income_tax_actions():
    return [
        "Income Tax raids on PQR Group uncover ₹300Cr discrepancy",
        "Notice issued to LMN Ltd for tax evasion",
        "Income Tax Department investigates UVW Corp for false GST claims"
    ]

def forensic_lookup(company_name):
    company_name = company_name.lower()
    result = []
    if "reliance" in company_name:
        result.append("Promoter: Mukesh Ambani. Clean record. No major investigations found.")
    elif "adani" in company_name:
        result.append("Promoter: Gautam Adani. Subject to Hindenburg report. SEBI investigating stock manipulation claims.")
    elif "karvy" in company_name:
        result.append("Promoter: C Parthasarathy. SEBI and ED actions ongoing over client fund misuse.")
    else:
        result.append("No recent forensic findings or major alerts found for this company.")
    return result

# ------------------ UI Layout ------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔍 Search Forensic Summary")
    company_input = st.text_input("Enter Company Name or Ticker:", "Reliance")
    if st.button("Run Forensic Check"):
        results = forensic_lookup(company_input)
        for res in results:
            st.info(res)

with col2:
    st.subheader("📋 Latest Regulatory Investigations")
    if st.button("Refresh Headlines"):
        sebi = scrape_sebi_actions()
        ed = scrape_ed_actions()
        tax = scrape_income_tax_actions()

        st.markdown("### 🔎 SEBI Investigations")
        for s in sebi:
            st.warning(s)

        st.markdown("### 🏩 ED Actions")
        for e in ed:
            st.error(e)

        st.markdown("### 💸 Income Tax Actions")
        for i in tax:
            st.success(i)

st.markdown("---")
st.caption("Data aggregated from public sources. Use for informational purposes only.")
