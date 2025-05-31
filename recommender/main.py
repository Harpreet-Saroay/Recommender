import streamlit as st
from streamlit_option_menu import option_menu
import Home, Music, Movie, Web_Series, Podcast, About, Games, Anime, Chatbot

st.set_page_config(page_title="Tune-Pics", page_icon="tune-pics.jpg", layout="wide")

class MultiPageApp:
    def __init__(self):
        self.pages = {
            "Home": Home,
            "Music": Music,
            "Movie": Movie,
            "Web Series": Web_Series,
            "Anime": Anime,
            "Games": Games,
            "Chatbot AI": Chatbot,
            "Podcast": Podcast,
            "About": About,
        
        }

    def run(self):
        # Create a sidebar menu for navigation
        with st.sidebar:
            selected_page = option_menu(
                menu_title="Main Menu",
                options=list(self.pages.keys()),
                icons=["house", "music-note", "film", "tv","play-circle","controller", "robot face", "mic", "info-circle"],
                default_index=0,
                styles={
                    "container": {"padding": "5!important", "background-color": ""},
                    "icon": {"color": "", "font-size": "25px"},
                    "nav-link": {"font-size": "15px", "text-align": "left", "margin": "0px"},
                    "nav-link-selected": {"background-color": "#007bff", "color": "white"},
                    "nav-link-hover": {"background-color": "#007bff", "color": "white"}
                }
            )

        # Dynamically load selected page
        self.pages[selected_page].selected_page()

# Ensure this block is at the global level
if __name__ == "__main__":
    app = MultiPageApp()
    app.run()
 