from operator import index
from re import X
import streamlit as st
import pandas as pd
import datetime
    
# Get data
@st.cache(show_spinner=False)
def _load_data(url):
    data = pd.read_csv(url)
    return data

def load_old_data():
    data_path = r"data/2022_LoL_esports_match_data_from_OraclesElixir_20220228.csv"
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

def choose_data():
    st.write("---")
    st.subheader("Data")

    load_old_data()
    choose_data = st.radio("Choose type of Data", ('Old Data', 'Latest Data (Data might take a few minutes to load)'))

    if choose_data == 'Old Data':
        load_old_data()
    else:
        load_latest_data()

    st.markdown(f"""* __Data Source__: [oracleselixir.com](https://oracleselixir.com/) ([_Click to download data used_]({data_link}))""")

    st.write(f"*_Data as of {date_textual}_")
    st.write("---")