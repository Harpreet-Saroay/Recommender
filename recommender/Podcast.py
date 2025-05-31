import streamlit as st
import pyttsx3
import webbrowser
import requests
from streamlit_lottie import st_lottie

def selected_page():
    st.title("🎙️ Standalone Podcast Player")
    st.markdown("---")
    st.write("This is a standalone podcast player that can be used to listen to your favorite podcasts")


    # Load Lottie Animation
    def load_lottie_url(url):
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()

    lottie_podcast = load_lottie_url("https://assets7.lottiefiles.com/packages/lf20_jcikwtux.json")

    # Display Lottie Animation
    st_lottie(lottie_podcast, height=200, key="podcast")

    # Text-to-speech
    def talk(text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
            
    # Play podcast function
    def play_podcast(podcast_name):
        if podcast_name:
            st.success(f"🎧 Opening podcast: {podcast_name}")
            talk(f"Playing the podcast {podcast_name}")
            search_url = f"https://www.youtube.com/results?search_query={podcast_name}+podcast"
            webbrowser.open(search_url)
        else:
            st.warning("⚠️ Please enter a podcast name.")
            talk("Please enter a podcast name.")
    
    # Podcast input form
    with st.form("podcast_form"):
        podcast_name = st.text_input("🔎 Enter a Podcast Name", placeholder="e.g., Avatar, Joe Rogan")
        submitted = st.form_submit_button("▶️ Play Podcast")
        
        if submitted:
            play_podcast(podcast_name)
    
    st.markdown("---")

