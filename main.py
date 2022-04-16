import streamlit as st
from multipage import MultiPage
from pages import home_page, analysis_page

# Webpage configuration
try:
    st.set_page_config(
         page_title = "Prediction App",
         page_icon = "https://icon-library.com/images/league-of-legends-icon-transparent/league-of-legends-icon-transparent-0.jpg",
         initial_sidebar_state = "expanded")
except:
    pass

# Adjust width of page
max_width_str = "max-width: 1000px;"
st.markdown(
	f"""
		<style>
			.reportview-container .main .block-container {{{max_width_str}}}
		</style>    
	""",
	unsafe_allow_html=True
)

# Hide main menu
hide_menu_style = """
	<style>
	#MainMenu {visibility: hidden;}
	footer {visibility: hidden;}
	</style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

app = MultiPage()

st.sidebar.header("Menu")
app.add_page("Home", home_page.app)
app.add_page("Analysis", analysis_page.app)

app.run()
