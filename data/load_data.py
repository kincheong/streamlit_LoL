import streamlit as st
import pandas as pd
import datetime
    
# Get data
@st.cache(show_spinner=False)
def _load_data(url):
    data = pd.read_csv(url)
    return data

def load_old_data():
    data_path = r"2022_LoL_esports_match_data_from_OraclesElixir_20220228.csv"
    year = data_path[-12:-8]
    day = data_path[-12:-4]
    day_textual = datetime.datetime.strptime(day, "%Y%m%d")
    day_textual = day_textual.strftime("%d %B %Y") 

    url = "https://oracleselixir-downloadable-match-data.s3-us-west-2.amazonaws.com/" + year + "_LoL_esports_match_data_from_OraclesElixir_" + day + ".csv"

    with st.spinner("Loading Data"):
        global date_textual, data_link, data
        date_textual = day_textual
        data_link = url
        data = _load_data(data_path)

def load_latest_data():
    current_date = datetime.date.today()
    year = current_date.strftime("%Y")
    yesterday = current_date - datetime.timedelta(days=1)
    yesterday_textual = yesterday.strftime("%d %B %Y")
    yesterday = yesterday.strftime("%Y%m%d")

    url = "https://oracleselixir-downloadable-match-data.s3-us-west-2.amazonaws.com/" + year + "_LoL_esports_match_data_from_OraclesElixir_" + yesterday + ".csv"

    with st.spinner("Loading Data"):
        try:
            global date_textual, data_link, data
            date_textual = yesterday_textual
            data_link = url
            data = _load_data(data_link) 
        except:
            st.error("Error in retrieving Latest Data, go back to Old Data!")
            st.stop()


