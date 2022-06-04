import streamlit as st
from st_aggrid import AgGrid
import pandas as pd
import matplotlib.pyplot as plt
from data import load_data
import pages_config

# Configure webpage structure
pages_config.webpage_config()

# Analysis page description
st.title("Analysis")
st.write("""
Some basic analysis. (To be improved in the future)
""")

# Get data
load_data.choose_data()

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

        AgGrid(winrate_table[['Champion','Games played','Winrate']])

    
    def _result_correlation(self):
        st.markdown(f"##### Best predictors of winning in patch {self.patch}")

        cor = self.df.iloc[:, 24:].corr()['result'].sort_values().nlargest(6)
        fig, ax = plt.subplots(figsize=(8,3))
        ax.bar(cor.index[1:6], cor.values[1:6], width=0.5)

        st.pyplot(fig)


    def run(self):
        self._choose_patch()
        self._generate_winrate_table()
        self._result_correlation()  


analysis_class = analysis(load_data.data)
analysis_class.run()

# Contact me
pages_config.contact_me()