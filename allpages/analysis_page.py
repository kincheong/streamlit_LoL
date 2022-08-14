import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from data import load_data

def app():

    # Analysis page description
    st.title("Analysis")
    st.write("""
    Some basic analysis. (To be improved in the future)
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

    # Real time analysis
    class analysis:
        
        def __init__(self, df):
            self.df = df
            
            # We want individual champion data and not team data
            self.df = self.df[self.df['champion'].notna()]
            
            # Remove rows with missing patch
            self.df = self.df[self.df['patch'].notna()]
    
    
        def _choose_patch(self):
            """
            Find the latest 5 patches for users to filter.
            """            
            patch_options = sorted(self.df['patch'].unique())[:-6:-1]
            self.patch = st.sidebar.selectbox('Choose Patch', options = patch_options)
            self.df = self.df[(self.df['patch'].isin([self.patch]))]
             
            
        def _generate_winrate_table(self):
            """
            Generate winrate table of champions within a selected patch.
            """
            st.markdown(f"##### Champion winrate in patch {self.patch}")
            
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

        
        def _result_correlation(self):
            st.markdown(f"##### Best predictors of winning in patch {self.patch}")

            cor = self.df.iloc[:, 24:].corr()['result'].sort_values()
            fig, ax = plt.subplots(figsize=(8,3))
            ax.bar(cor.index[0:5], cor.values[0:5], width=0.5)

            st.pyplot(fig)


        def run(self):
            self._choose_patch()
            self._generate_winrate_table()
            self._result_correlation()  


    analysis_class = analysis(load_data.data)
    analysis_class.run()

    st.write("---")
    st.subheader("Contact Me")
    linkedin, facebook, fill, fill, fill = st.columns(5)
    
    with linkedin:
        st.write("[Linkedin](https://www.linkedin.com/in/jacob-low/)")
        st.image("https://cdn-icons-png.flaticon.com/512/174/174857.png", width=30)
    
    with facebook:
        st.write("[Facebook](https://www.facebook.com/jacob.low.374/)")
        st.image("https://cdn3.iconfinder.com/data/icons/capsocial-round/500/facebook-512.png", width=30)