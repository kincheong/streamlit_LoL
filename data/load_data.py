# -*- coding: utf-8 -*-
"""
Created on Mon Aug 23 22:47:13 2021

@author: Jacob
"""
import streamlit as st
import pandas as pd
import datetime
    
# Get data
@st.experimental_memo(show_spinner=False)
def _load_data(url):
    data = pd.read_csv(url)
    return data

current_date = datetime.date.today()
year = current_date.strftime("%Y")
today = current_date.strftime("%Y%m%d")
today_textual = current_date.strftime("%d %B %Y")

yesterday = current_date - datetime.timedelta(days=1)
yesterday_textual = yesterday.strftime("%d %B %Y")
yesterday = yesterday.strftime("%Y%m%d")

url = "https://oracleselixir-downloadable-match-data.s3-us-west-2.amazonaws.com/" + year + "_LoL_esports_match_data_from_OraclesElixir_"

try:
    with st.spinner("Loading Data"):
        df = _load_data(f"{url}{yesterday}.csv")       
except:
    with st.spinner("Loading Data"):
        df = _load_data(r"C:\Users\Jacob\Desktop\streamlit_LoL\data\2021_LoL_esports_match_data_from_OraclesElixir_20210816.csv")

data = df