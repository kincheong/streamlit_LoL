# -*- coding: utf-8 -*-
"""
Created on Mon Aug 16 18:52:30 2021

@author: Jacob
"""

import streamlit as st
import pandas as pd
import numpy as np
import shap
import xgboost as xgb
from data import load_data
pd.options.mode.chained_assignment = None
st.set_option('deprecation.showPyplotGlobalUse', False)

def app():

    # Webpage description
    st.title("Prediction!")
    st.markdown("""
    Win prediction based on team composition
    * __Data Source__: [oracleselixir.com](https://oracleselixir.com/)  
    
    ---
    """)
    
    
    # Real time prediction
    class prediction:
        
        def __init__(self, df):
            self.df = df
            self.allow_for_prediction = False
            
            # We want individual champion data and not team data
            self.df = self.df[self.df['champion'].notna()]
    
        def _choose_patch(self):
            # Finds the latest 5 patches
            patch_options = sorted(self.df['patch'].unique())[:-6:-1]
            self.patch = st.sidebar.selectbox('Choose Patch', options = patch_options)
            self.df = self.df[(self.df['patch'].isin([self.patch]))]


        def _clean_data(self):
            # We want only data of champions that has more than 15 games for each role
            filter_champs = self.df.groupby(['position','champion']).size().reset_index(name = 'Games played')
            filter_champs = filter_champs[filter_champs['Games played'] > 15]
            
            self.df = self.df.merge(filter_champs, on = ['position','champion'], how='inner')   
            
        
        def _train_data(self):
            train_df = self.df[['gameid','side','position','champion','result']]
            train_df['champion'] = train_df['position'] + '_' + train_df['champion']
            train_df = train_df.drop(['position'], axis = 1)
            
            # Encode
            encode = ['champion']
            
            for col in encode:
                dummy = pd.get_dummies(train_df[col], prefix = col)
                train_df = pd.concat([train_df, dummy], axis = 1)
                del train_df[col]
                        
            train_df = train_df.groupby(['gameid','side','result']).sum().reset_index()
            train_df = train_df.drop(['gameid','side'], axis = 1)
            
            X = train_df.drop(['result'], axis = 1)
            Y = train_df[['result']].values.ravel()   
            
            dtrain = xgb.DMatrix(X, label = Y)
            params = {
                        "eta": 0.5,
                        "max_depth": 4,
                        "objective": "binary:logistic",
                        "base_score": np.mean(Y),
                        "eval_metric": "logloss"
                    }
                                
            self.model = xgb.train(params, dtrain)    
    
            explainer = shap.Explainer(self.model)
            shap_values = explainer.shap_values(X, approximate = True)
            #fig = shap.summary_plot(shap_values, X, show = False)
            #st.pyplot(fig)
            
        def _pick_champions(self):
            # Filter champion options for each role
            top_options = sorted(self.df[self.df['position'] == 'top']['champion'].unique())
            jng_options = sorted(self.df[self.df['position'] == 'jng']['champion'].unique())
            mid_options = sorted(self.df[self.df['position'] == 'mid']['champion'].unique())
            adc_options = sorted(self.df[self.df['position'] == 'bot']['champion'].unique())
            sp_options = sorted(self.df[self.df['position'] == 'sup']['champion'].unique())
            
            # Selectbox for each role on the webapp
            top, jng, mid, adc, sp = st.columns(5)
            top_pick = top.selectbox('Select Top', options = ['<select>'] + top_options)
            jng_pick = jng.selectbox('Select Jungle', options = ['<select>'] + jng_options)
            mid_pick = mid.selectbox('Select Mid', options = ['<select>'] + mid_options)
            adc_pick = adc.selectbox('Select ADC', options = ['<select>'] + adc_options)
            sp_pick = sp.selectbox('Select Support', options = ['<select>'] + sp_options)
            
            champ_list = [top_pick, jng_pick, mid_pick, adc_pick, sp_pick]
            champ_list = ['-' if (x == '<select>') else x for x in champ_list]
    
            self.user_df = pd.DataFrame({'champion': ['-', '-', '-', '-', '-']},
                                        index = ['Top', 'Jungle', 'Mid', 'ADC', 'Support'])
            self.user_df.loc['Top', 'champion'] = champ_list[0]
            self.user_df.loc['Jungle', 'champion'] = champ_list[1]
            self.user_df.loc['Mid', 'champion'] = champ_list[2]
            self.user_df.loc['ADC', 'champion'] = champ_list[3]
            self.user_df.loc['Support', 'champion'] = champ_list[4]   
            
    # =============================================================================
    #         def color_dupes(x):
    #             c1='background-color:red'
    #             c2=''
    #             cond=x.stack().duplicated(keep=False).unstack()
    #             df1 = pd.DataFrame(np.where(cond,c1,c2),columns=x.columns,index=x.index)
    #             return df1        
    # =============================================================================
    
            if '-' in champ_list:
                self.allow_for_prediction = False
                champ_list = [x for x in champ_list if x != '-']
                if champ_list is not None:
                    if len(champ_list) != len(set(champ_list)):
                        st.error("You can only pick one champion for each role!")
            else:
                if len(champ_list) == len(set(champ_list)):
                    self.allow_for_prediction = True
                else:
                    self.allow_for_prediction = False
                    st.error("You can only pick one champion for each role!")
                    #self.user_df = self.user_df.style.apply(color_dupes,axis=None)            
                    
            st.subheader("User chosen champions")
            st.dataframe(self.user_df)            
            
            
        def _predict(self):
            user_champ_df = self.user_df
            user_champ_df.loc['Top', 'champion'] = 'top_' + user_champ_df.loc['Top', 'champion']
            user_champ_df.loc['Jungle', 'champion'] = 'jng_' + user_champ_df.loc['Jungle', 'champion']
            user_champ_df.loc['Mid', 'champion'] = 'mid_' + user_champ_df.loc['Mid', 'champion']
            user_champ_df.loc['ADC', 'champion'] = 'bot_' + user_champ_df.loc['ADC', 'champion']
            user_champ_df.loc['Support', 'champion'] = 'sup_' + user_champ_df.loc['Support', 'champion']
            
            # Create a dataframe containing column for all champions in a particular patch
            champions = self.df['position'] + '_' + self.df['champion']
            champions = champions.unique()
            champ_df = pd.DataFrame(champions)
            champ_df.columns = ['champion']
            
            # Encode 'champion' column
            encode = ['champion']
            for col in encode:
                dummy = pd.get_dummies(champ_df[col], prefix = col)
                champ_df = pd.concat([champ_df, dummy], axis = 1)
                del champ_df[col] 
                    
                dummy = pd.get_dummies(user_champ_df[col], prefix = col)
                user_champ_df = pd.concat([user_champ_df, dummy], axis = 1)
                del user_champ_df[col] 
            
            # Get only first row of champ_df and set all column values to 0
            champ_df = champ_df[0:0]
            champ_df.loc[len(champ_df)] = 0
            
            # Sum all rows in user_champ_df to output only 1 row
            user_champ_df['id'] = 1
            user_champ_df = user_champ_df.groupby(['id']).sum().reset_index()
            user_champ_df = user_champ_df.drop(['id'], axis = 1)
            
            # Concatenate champ_df and user_champ_df
            final_champ_df = pd.concat([champ_df, user_champ_df], axis = 0)
    
            # Sum all rows in final_champ_df to output only 1 row
            final_champ_df['id'] = 1
            final_champ_df = final_champ_df.groupby(['id']).sum().reset_index()
            final_champ_df = final_champ_df.drop(['id'], axis = 1)
            
            final_champ_df = xgb.DMatrix(final_champ_df)
                        
            # Prediction        
            st.subheader("Probability of winning")
            prediction = self.model.predict(final_champ_df)
            st.write(prediction)
            #win_pct = prediction[:,1][0]
                        
            #st.write("{0:.0%}".format(win_pct))
            
            
        def run(self):
            self._choose_patch()
            self._clean_data()
            
            if len(self.df['gameid'].unique()) > 100:
                self._train_data()
                self._pick_champions()
            else:
                st.subheader("Not enough data for prediction")
            
            if self.allow_for_prediction == True:
                if st.button("Predict!"):
                    self._predict()
        
    prediction_class = prediction(load_data.data)
    prediction_class.run()


