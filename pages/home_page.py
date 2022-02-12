# -*- coding: utf-8 -*-
"""
Created on Mon Aug 16 18:52:30 2021

@author: Jacob
"""

import streamlit as st
import pandas as pd
import datetime
from data import load_data

def app():
        
    # Webpage description
    st.title("League of Legends Prediction App")
    st.markdown(f"""
    Hi, welcome to my web app 
                
    * __Data Source__: [oracleselixir.com](https://oracleselixir.com/) ([_Click to download data used_]({load_data.data_link}))  
        
    """)
    st.write(f"*_Data as of {load_data.date_textual}_")
    
    # Real time prediction
    class home:
        
        def __init__(self, df):
            self.df = df
            
            # We want individual champion data and not team data
            self.df = self.df[self.df['champion'].notna()]
            
            # Remove rows with missing patch
            self.df = self.df[self.df['patch'].notna()]
    
    
        def _choose_patch(self):            
            # Finds the latest 5 patches
            patch_options = sorted(self.df['patch'].unique())[:-6:-1]
            self.patch = st.sidebar.selectbox('Choose Patch', options = patch_options)
            self.df = self.df[(self.df['patch'].isin([self.patch]))]
             
            
        def _generate_winrate_table(self):
            st.subheader(f"Champion winrate in patch {self.patch}")
            
            # Find games played for each champion
            champion_play_count = self.df['champion'].value_counts()
            
            # Find total wins for each champion
            champion_wins = self.df.groupby(['champion'])[['result']].sum()
            
            # Concatenate the above 2 calculated columns 
            winrate_table = pd.concat([champion_play_count, champion_wins], axis = 1).reset_index()
            winrate_table.columns = ['Champion', 'Games played', 'Games won']
                    
            # Find winrate for each champion
            winrate_table["Winrate"] = winrate_table["Games won"].div(winrate_table["Games played"].values)
            
            st.dataframe(winrate_table[['Champion','Games played','Winrate']])

            
        def run(self):
            self._choose_patch()
            self._generate_winrate_table()        
        
    home_class = home(load_data.data)
    home_class.run()
    
    st.write("---")
    st.subheader("Contact Me")
    linkedin, facebook, fill, fill, fill = st.columns(5)
    
    with linkedin:
        st.write("[Linkedin](https://www.linkedin.com/in/jacob-low/)")
        st.image("https://cdn-icons-png.flaticon.com/512/174/174857.png", width=30)
    
    with facebook:
        st.write("[Facebook](https://www.facebook.com/jacob.low.374/)")
        st.image("https://cdn3.iconfinder.com/data/icons/capsocial-round/500/facebook-512.png", width=30)
