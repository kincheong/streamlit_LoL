import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from treeinterpreter import treeinterpreter as ti
from data import load_data
pd.options.mode.chained_assignment = None   
st.set_option('deprecation.showPyplotGlobalUse', False) 

def app():

    # Home page description
    st.title("League of Legends Prediction App")
    st.write("""
    Welcome to my first ever web-app! This app is aimed to help League of Legends players gauge their chances of winning a match
    based on historical competitive data. It is mainly a platform for me to upskill in simple web development, data wrangling,
    and machine learning. 
    """)

    # Data
    st.write("---")
    st.subheader("Data")
    choose_data = st.radio("Choose type of Data", ('Old Data', 'Latest Data (Data might take a few minutes to load)'))
    if choose_data == 'Old Data':
        load_data.load_old_data()
    elif choose_data == 'Latest Data (Data might take a few minutes to load)':
        load_data.load_latest_data()

    st.markdown(f"""* __Data Source__: [oracleselixir.com](https://oracleselixir.com/) ([_Click to download data used_]({load_data.data_link}))""")

    st.write(f"*_Data as of {load_data.date_textual}_")
    st.write("---")

    st.subheader("""Win prediction based on team composition""")
    # Real time prediction
    class home:
        
        def __init__(self, df):
            self.df = df
            self.allow_for_prediction = False
            
            # We want individual champion data and not team data
            self.df = self.df[self.df['champion'].notna()]
    
            # Remove rows with missing patch
            self.df = self.df[self.df['patch'].notna()]


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
            Y = train_df[['result']].values
            
            self.clf = RandomForestClassifier(random_state=42)
            self.clf.fit(X, Y)
            
            
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
                    
            st.markdown("##### User chosen champions")
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
            self.final_champ_df = pd.concat([champ_df, user_champ_df], axis = 0)
    
            # Sum all rows in final_champ_df to output only 1 row
            self.final_champ_df['id'] = 1
            self.final_champ_df = self.final_champ_df.groupby(['id']).sum().reset_index()
            self.final_champ_df = self.final_champ_df.drop(['id'], axis = 1)
                        
            # Prediction        
            st.markdown("##### Probability of winning")
            prediction = self.clf.predict_proba(self.final_champ_df)
            win_pct = round(prediction[:,1][0], 2) ## round to 2 decimal points

            if win_pct < 0.5:
                st.write(f"<font color='red'>{win_pct * 100}%</font>", unsafe_allow_html=True)
            else:
                st.write(f"<font color='green'>{win_pct * 100}%</font>", unsafe_allow_html=True)


        def _champion_importance(self):  
            st.markdown("##### Impact of champion on winning")     

            data_point = self.final_champ_df
            data_point.set_axis(['value_variable']) # Once transposed, it will be the column name
            prediction, bias, contributions = ti.predict(self.clf, data_point)
            local_interpretation = data_point.append(
                pd.DataFrame([[round(c[1],3) for c in contributions[0]]], columns=data_point.columns.tolist(), index=['contribution_variable'])
            ).T.sort_values('contribution_variable', ascending=False)
            
            local_interpretation = local_interpretation[local_interpretation[0]==1].reset_index()

            top_contribution = local_interpretation[local_interpretation['index'].str[9:12]=="top"]['contribution_variable'].values[0]
            top_champion = local_interpretation[local_interpretation['index'].str[9:12]=="top"]['index'].str[13:].values[0]
            jng_contribution = local_interpretation[local_interpretation['index'].str[9:12]=="jng"]['contribution_variable'].values[0]
            jng_champion = local_interpretation[local_interpretation['index'].str[9:12]=="jng"]['index'].str[13:].values[0]
            mid_contribution = local_interpretation[local_interpretation['index'].str[9:12]=="mid"]['contribution_variable'].values[0]
            mid_champion = local_interpretation[local_interpretation['index'].str[9:12]=="mid"]['index'].str[13:].values[0]
            adc_contribution = local_interpretation[local_interpretation['index'].str[9:12]=="bot"]['contribution_variable'].values[0]
            adc_champion = local_interpretation[local_interpretation['index'].str[9:12]=="bot"]['index'].str[13:].values[0]        
            sup_contribution = local_interpretation[local_interpretation['index'].str[9:12]=="sup"]['contribution_variable'].values[0]
            sup_champion = local_interpretation[local_interpretation['index'].str[9:12]=="sup"]['index'].str[13:].values[0]

            top, jng, mid, adc, sup = st.columns(5)
            top.metric(top_champion, "Top", top_contribution)
            jng.metric(jng_champion, "Jungle", jng_contribution)
            mid.metric(mid_champion, "Mid", mid_contribution)
            adc.metric(adc_champion, "ADC", adc_contribution)
            sup.metric(sup_champion, "Support", sup_contribution)
            
            st.caption("""<font color='green'>Upwards green arrow signifies this champion increases the probability of winning for this team composition.</font> 
            <br><font color='red'>Downwards red arrow signifies this champion decreases the probability of winning for this team composition.</font>""", unsafe_allow_html=True)
            

        def run(self):
            self._choose_patch()
            self._clean_data()
            
            if len(self.df['gameid'].unique()) >= 100:
                self._train_data()
                self._pick_champions()
            else:
                st.error("Not enough data for prediction, try another patch from the left panel! (Check FAQ)")
            
            if self.allow_for_prediction == True:
                if st.button("Predict!"):
                    self._predict()
                    self._champion_importance()


    home_class = home(load_data.data)
    home_class.run()

    st.write("---")
    st.subheader("FAQ")
    with st.expander("How does prediction work?"):
        st.write("""
        There are several rules to prediction,
        - Data used in training is subsetted to the patch selected. 
        - Only champions with more than 15 unique games played are used in training and prediction.
        Training is done using a simple Random Forest Classifier.
        """)

    with st.expander("Why is there not enough data for prediction?"):
        st.write("""
        If, for a given patch, less than 100 unique games are played, this is considered insufficient data for prediction.
        """)

    with st.expander("How is the 'Impact of champion on winning' calculated?"):
        st.write("""
        Impact is calculated using the [treeinterpreter](https://github.com/andosa/treeinterpreter) library in Python,
        it computes the impact of each feature (champion) on the target variable (win or lose) for the Random Forest Classifier.
        
        In this case, it tells us if picking a champion would increase or decrease the probability of winning in a certain
        team composition.
        """)
    
    st.write("---")
    st.subheader("Contact Me")
    linkedin, facebook, fill, fill, fill = st.columns(5)
    
    with linkedin:
        st.write("[Linkedin](https://www.linkedin.com/in/jacob-low/)")
        st.image("https://cdn-icons-png.flaticon.com/512/174/174857.png", width=30)
    
    with facebook:
        st.write("[Facebook](https://www.facebook.com/jacob.low.374/)")
        st.image("https://cdn3.iconfinder.com/data/icons/capsocial-round/500/facebook-512.png", width=30)
