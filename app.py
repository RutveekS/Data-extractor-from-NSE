import streamlit as st
import pandas as pd
import requests
import urllib3
import io
import time

urllib3.disable_warnings()

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="Nifty TRI Downloader",
    layout="wide"
)

# =====================================================
# FETCH INDEX LIST
# =====================================================

@st.cache_data(ttl=3600)
def get_all_indices():

    session = requests.Session()

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": "https://www.niftyindices.com",
        "Referer": "https://www.niftyindices.com/reports/historical-data",
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest"
    }

    session.get(
        "https://www.niftyindices.com/reports/historical-data",
        headers=headers,
        verify=False
    )

    #
    # IMPORTANT
    #
    # You may need to adjust this endpoint & payload after
    # investigating the category APIs further.
    #
    # For now this uses the endpoint you discovered.
    #

    payload = {
        "name": "Broad Market Indices"
    }

    try:

        response = session.post(
            "https://www.niftyindices.com/BackPage/gethistoricaltypeindexdata",
            json=payload,
            headers=headers,
            verify=False,
            timeout=60
        )

        data = response.json()

        indices = sorted(
            list(
                {
                    item["indextype"]
                    for item in data
                    if item.get("indextype")
                }
            )
        )

        return indices

    except:
        return []

# =====================================================
# DOWNLOAD TRI
# =====================================================

def get_nifty_tri(index_name, start_date, end_date):

    session = requests.Session()

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": "https://www.niftyindices.com",
        "Referer": "https://www.niftyindices.com/reports/historical-data",
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest"
    }

    session.get(
        "https://www.niftyindices.com/reports/historical-data",
        headers=headers,
        verify=False
    )

    payload = {
        "cinfo": (
            f"{{'name':'{index_name}',"
            f"'startDate':'{start_date}',"
            f"'endDate':'{end_date}',"
            f"'indexName':'{index_name}'}}"
        )
    }

    response = session.post(
        "https://www.niftyindices.com/BackPage/getTotalReturnIndexString",
        json=payload,
        headers=headers,
        verify=False,
        timeout=60
    )

    data = response.json()

    df = pd.DataFrame(data)

    if len(df) == 0:
        return pd.DataFrame()

    df["Date"] = pd.to_datetime(
        df["Date"],
        format="%d %b %Y"
    )

    df["TotalReturnsIndex"] = pd.to_numeric(
        df["TotalReturnsIndex"],
        errors="coerce"
    )

    df = df[["Date", "TotalReturnsIndex"]]

    df.rename(
        columns={
            "TotalReturnsIndex": index_name
        },
        inplace=True
    )

    return df

# =====================================================
# UI
# =====================================================

ALL_INDICES = sorted([

    "NIFTY 50",
    "NIFTY NEXT 50",
    "NIFTY NEXT 100",
    "NIFTY 100",
    "NIFTY 200",
    "NIFTY 500",
    "NIFTY INDIA FPI 150",
    "NIFTY LARGEMIDCAP 250",
    "NIFTY MICROCAP 250",
    "NIFTY MIDCAP 50",
    "NIFTY MIDCAP 100",
    "NIFTY MIDCAP 150",
    "NIFTY MIDCAP SELECT",
    "NIFTY SMALLCAP 50",
    "NIFTY SMALLCAP 100",
    "NIFTY SMALLCAP 250",
    "NIFTY SMALLCAP 500",
    "NIFTY MIDSMALLCAP 400",
    "NIFTY TOTAL MARKET",

    "NIFTY AUTO",
    "NIFTY BANK",
    "NIFTY CAPITAL GOODS",
    "NIFTY CEMENT",
    "NIFTY CHEMICALS",
    "NIFTY CONSTRUCTION",
    "NIFTY CONSUMER DURABLES",
    "NIFTY FINANCIAL SERVICES",
    "NIFTY FMCG",
    "NIFTY HEALTHCARE",
    "NIFTY IT",
    "NIFTY MEDIA",
    "NIFTY METAL",
    "NIFTY OIL & GAS",
    "NIFTY PHARMA",
    "NIFTY POWER",
    "NIFTY PRIVATE BANK",
    "NIFTY PSU BANK",
    "NIFTY REALTY",
    "NIFTY TELECOMMUNICATIONS",

    "NIFTY ALPHA 50",
    "NIFTY LOW VOLATILITY 50",
    "NIFTY HIGH BETA 50",
    "NIFTY100 ALPHA 30",
    "NIFTY100 LOW VOLATILITY 30",
    "NIFTY100 QUALITY 30",
    "NIFTY100 EQUAL WEIGHT",
    "NIFTY200 ALPHA 30",
    "NIFTY200 MOMENTUM 30",
    "NIFTY200 QUALITY 30",
    "NIFTY200 VALUE 30",
    "NIFTY50 EQUAL WEIGHT",
    "NIFTY50 VALUE 20",
    "NIFTY500 EQUAL WEIGHT",
    "NIFTY500 MOMENTUM 50",
    "NIFTY500 QUALITY 50",
    "NIFTY500 LOW VOLATILITY 50",
    "NIFTY500 VALUE 50",

    "NIFTY ENERGY",
    "NIFTY COMMODITIES",
    "NIFTY CPSE",
    "NIFTY PSE",
    "NIFTY INDIA CONSUMPTION",
    "NIFTY INDIA DIGITAL",
    "NIFTY INDIA INTERNET",
    "NIFTY INDIA MANUFACTURING",
    "NIFTY INDIA DEFENCE",
    "NIFTY INDIA DEFENCE EQUAL WEIGHT",
    "NIFTY INDIA INFRASTRUCTURE & LOGISTICS",
    "NIFTY INDIA TOURISM",
    "NIFTY INFRASTRUCTURE",
    "NIFTY IPO",
    "NIFTY MNC",
    "NIFTY MOBILITY",
    "NIFTY SERVICES SECTOR",

    "NIFTY100 ESG",
    "NIFTY100 ENHANCED ESG",
    "NIFTY500 AHIMSA",

    "NIFTY50 SHARIAH",
    "NIFTY500 SHARIAH"
])

st.title("📈 Index TRI Downloader")


selected_indices = st.multiselect(
    "Select Indices",
    options=ALL_INDICES,
    placeholder="Type to search indices..."
)

from datetime import date

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input(
        "Start Date",
        value=date(2010, 1, 1),
        min_value=date(1990, 1, 1),
        max_value=date(2100, 12, 31)
    )

with col2:
    end_date = st.date_input(
        "End Date",
        value=date.today(),
        min_value=date(1990, 1, 1),
        max_value=date(2100, 12, 31)
    )

st.write(
    f"Selected indices: {len(selected_indices)}"
)
# =====================================================
# DOWNLOAD
# =====================================================

if st.button("Download Data"):

    if len(selected_indices) == 0:

        st.error("Please select at least one index.")

    else:

        all_data = []

        progress = st.progress(0)

        for i, index_name in enumerate(selected_indices):

            df = get_nifty_tri(
                index_name,
                start_date.strftime("%d-%b-%Y"),
                end_date.strftime("%d-%b-%Y")
            )

            all_data.append(df)

            progress.progress(
                (i + 1) / len(selected_indices)
            )

            time.sleep(0.5)

        final_df = all_data[0]

        for df in all_data[1:]:

            final_df = pd.merge(
                final_df,
                df,
                on="Date",
                how="outer"
            )

        final_df.sort_values(
            "Date",
            inplace=True
        )

        st.success(
            f"Downloaded {len(selected_indices)} indices."
        )

        st.dataframe(
            final_df.head()
        )

        output = io.BytesIO()

        with pd.ExcelWriter(
            output,
            engine="xlsxwriter"
        ) as writer:

            final_df.to_excel(
                writer,
                sheet_name="TRI Data",
                index=False
            )

        st.download_button(
            label="📥 Download Excel",
            data=output.getvalue(),
            file_name="Nifty_TRI_Database.xlsx",
            mime=(
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            )
        )
