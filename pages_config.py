import streamlit as st

def webpage_config():
    # Webpage configuration
    try:
        st.set_page_config(
            page_title = "Prediction App",
            page_icon = "https://icon-library.com/images/league-of-legends-icon-transparent/league-of-legends-icon-transparent-0.jpg")
    except:
        pass

    # Hide main menu
    hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

def contact_me():
    st.write("---")
    st.subheader("Contact Me")
    linkedin, facebook, fill, fill, fill = st.columns(5)

    with linkedin:
        st.write("[Linkedin](https://www.linkedin.com/in/jacob-low/)")
        st.image("https://cdn-icons-png.flaticon.com/512/174/174857.png", width=30)

    with facebook:
        st.write("[Facebook](https://www.facebook.com/jacob.low.374/)")
        st.image("https://cdn3.iconfinder.com/data/icons/capsocial-round/500/facebook-512.png", width=30)
