import streamlit as st
import requests
import base64
from streamlit_lottie import st_lottie

def selected_page():
    def load_lottie_url(url: str):
        try:
            r = requests.get(url)
            r.raise_for_status()
            return r.json()
        except (requests.exceptions.RequestException, ValueError):
            return None

    def get_image_base64(image_path):
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        return encoded

    image_base64 = get_image_base64("Designer.png")

    # ---------------- UI HEADER ----------------
    with st.container():
        st.markdown(
            f"""
            <div style='
                padding: 1rem 2rem;
                border-radius: 16px;
                display: flex;
                align-items: center;
                gap: 1.5rem;
            '>
                <img src="data:image/png;base64,{image_base64}"
                     style="height: 120px; border-radius: 10px;" />
                <h1 style="color: white; font-size: 4rem;">TunePics Recommender</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ---------- MUSIC-THEMED ANIMATION ----------
    lottie_animation = load_lottie_url("https://assets4.lottiefiles.com/packages/lf20_j1adxtyb.json")

    if lottie_animation:
        st_lottie(lottie_animation, speed=1, width=400, height=200, key="music_animation")
    else:
        st.warning("⚠️ Animation failed to load. Please check the Lottie URL or your internet connection.")

    # ----------- PAGE CONTENT -------------
    st.markdown("<h1 style='text-align: wide; color: White; font-size: 2rem'>🎵🎬 Welcome to TunePics Recommender! 🎮📺</h1>", unsafe_allow_html=True)

    st.subheader(
        """
        Welcome to **TunePics** – your personalized gateway to a universe of entertainment.  
        Ever loved a song so much that you wished you could live in its world? Now you can.

        ### 🌟 What We Do:
        TunePics analyzes the **lyrics**, **mood**, and **themes** of your favorite songs to recommend:
        - 🎬 **Movies** that echo the same emotions  
        - 📺 **Web Series** with matching vibes or story arcs  
        - 🎮 **Games** that capture the energy or atmosphere  
        - 🎵 And of course, **new songs** that feel like your favorites  

        ### 💡 How It Works:
        By combining music intelligence with deep content matching, TunePics transforms your playlists into watchlists and game nights:
        - Feel a connection with a heartbreak anthem? We’ll find you a touching drama.  
        - Vibing to high-energy rap? Here comes a fast-paced action game.  
        - In love with dreamy indie tracks? Cue a whimsical fantasy series.  

        ### 🚀 Why You'll Love It:
        - Personalized, vibe-based recommendations  
        - Multimodal discovery: Music → Movies, Series, Games  
        - Mood-first, not just popularity-driven  

        ---
        🎯 Whether you're chasing feels, thrills, or chills, **TunePics** curates an experience built around *you*.  
        So turn up the volume... and let us recommend your next obsession. 🔥
        """
    )
