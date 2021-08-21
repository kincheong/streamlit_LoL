# -*- coding: utf-8 -*-
"""
Created on Mon Aug 16 18:52:30 2021

@author: Jacob
"""

import streamlit as st
import pandas as pd

# Webpage title
st.title("Test App")

# Webpage description
st.markdown("""
Win prediction based on team composition
* **Data Source**: [oracleselixir.com](https://oracleselixir.com/)  

""")


# data
#ori_df = pd.read_csv("https://oracleselixir-downloadable-match-data.s3-us-west-2.amazonaws.com/2021_LoL_esports_match_data_from_OraclesElixir_20210820.csv")

@st.cache
def load_data(url):
    data = pd.read_csv(url)
    return data

df = load_data("https://oracleselixir-downloadable-match-data.s3-us-west-2.amazonaws.com/2021_LoL_esports_match_data_from_OraclesElixir_20210819.csv")

# Real time prediction
class lol:
    
    def __init__(self, df):
        self.df = df
        self.patch = 11.15
        self.user_df = []
        
        # We want individual champion data and not team data
        self.df = self.df[self.df['champion'].notna()]

        
    def choose_patch(self):
        st.sidebar.header('Filter')
        
        # Finds the latest 5 patches
        patch_options = sorted(self.df['patch'].unique())[:-6:-1]
        self.patch = st.sidebar.selectbox('Choose Patch', options = patch_options)
        self.df = self.df[(self.df['patch'].isin([self.patch]))]
         
        
    def generate_winrate_table(self):
        st.subheader(f"Champion winrate in patch {self.patch}")
        
        champion_play_count = self.df['champion'].value_counts()
        champion_wins = self.df.groupby(['champion'])[['result']].sum()
        
        winrate_table = pd.concat([champion_play_count, champion_wins], axis = 1).reset_index()
        
        winrate_table.columns = ['Champion', 'Games played', 'Games won']
                
        winrate_table["Winrate"] = winrate_table["Games won"].div(winrate_table["Games played"].values)
        
        st.dataframe(winrate_table[['Champion','Games played','Winrate']])

        
    def train_data(self):
        train_df = self.df[['gameid','side','champion','result']]
        train_df = train_df[train_df['champion'].notna()]
        
        # Encode
        encode = ['champion']
        
        for col in encode:
            dummy = pd.get_dummies(train_df[col], prefix = col)
            train_df = pd.concat([train_df, dummy], axis = 1)
            del train_df[col]
        
        train_df = train_df.groupby(['gameid','side','result']).sum().reset_index()
        
        train_df = train_df.drop(['gameid','side'], axis = 1)
        X = train_df.drop(['result'], axis = 1)
        Y = train_df[['result']]
                
        from sklearn.ensemble import RandomForestClassifier
        self.clf = RandomForestClassifier()
        self.clf.fit(X, Y)
                
        
    def pick_champions(self):
        test = sorted(self.df['champion'].unique())

        champion_1 = st.selectbox('Select Champion 1', options = ['<select>'] + test)
        champion_2 = st.selectbox('Select Champion 2', options = ['<select>'] + test)
        champion_3 = st.selectbox('Select Champion 3', options = ['<select>'] + test)
        champion_4 = st.selectbox('Select Champion 4', options = ['<select>'] + test)
        champion_5 = st.selectbox('Select Champion 5', options = ['<select>'] + test)
        
        self.user_df = pd.DataFrame({'champion': [champion_1, champion_2, champion_3, champion_4, champion_5]})
        
        st.subheader("User chosen champions")
        st.dataframe(self.user_df)
        
    def prediction(self):
        pred_df_1 = self.user_df
        
        pred_df = self.df
        pred_df = pred_df[pred_df['champion'].notna()]
        
        champions = pred_df['champion'].unique()
        pred_df = pd.DataFrame(champions)
        pred_df.columns = ['champion']
        
        encode = ['champion']
        
        for col in encode:
            dummy = pd.get_dummies(pred_df[col], prefix = col)
            pred_df = pd.concat([pred_df, dummy], axis = 1)
            del pred_df[col] 
            
            
            dummy = pd.get_dummies(pred_df_1[col], prefix = col)
            pred_df_1 = pd.concat([pred_df_1, dummy], axis = 1)
            del pred_df_1[col] 
        
        pred_df = pred_df[0:0]
        pred_df.loc[len(pred_df)] = 0
            
            
        pred_df_1['id'] = 1
        pred_df_1 = pred_df_1.groupby(['id']).sum().reset_index()
        pred_df_1 = pred_df_1.drop(['id'], axis = 1)
        
        pred_df = pd.concat([pred_df, pred_df_1], axis = 0)

        pred_df['id'] = 1
        pred_df = pred_df.groupby(['id']).sum().reset_index()
        pred_df = pred_df.drop(['id'], axis = 1)

        
        # Prediction        
        st.subheader("Probability of winning")
        prediction = self.clf.predict_proba(pred_df)
        st.dataframe(prediction)
        
        
    def run(self):
        self.choose_patch()
        self.generate_winrate_table()
        
        self.train_data()
        self.pick_champions()
        
        if "<select>" not in self.user_df.values:
            if st.button("Predict!"):
                self.prediction()
    
    
data = lol(df)
data.run()


