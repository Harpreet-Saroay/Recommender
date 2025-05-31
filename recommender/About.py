import streamlit as st
from streamlit_lottie import st_lottie
import requests

def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def selected_page():
    # Load animation
    lottie_animation = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_myejiggj.json")  # Sample Lottie
    icon_url = "https://cdn-icons-png.flaticon.com/512/727/727248.png"  # Sample icon

    # Display icon and title with white icon using CSS filter
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(
            f"""
            <style>
            .white-icon img {{
                filter: invert(1) brightness(2);
                width: 60px;
            }}
            </style>
            <div class="white-icon">
                <img src="{icon_url}" />
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.title("About TunePics")

    # Display animation
    st_lottie(lottie_animation, height=250, key="tune_animation")

    # Project description
    st.write("""
        TunePics is a project developed by a team of passionate individuals who love movies and music. 
        Our goal is to create a unique experience for users by combining the power of song lyrics with movie recommendations.
    """)

    st.write("""
        We believe that music and movies are two of the most powerful forms of art, and they often go hand in hand. 
        With TunePics, we aim to bridge the gap between these two worlds and help users find their next favorite movie based on their favorite songs and movies.
    """)

    st.write("""
        Our team consists of talented developers, designers, and music enthusiasts who have worked tirelessly to bring this project to life. 
        We are constantly working to improve the app and add new features to enhance the user experience.
    """)

    st.write("""
        TunePics also embraces the broader world of entertainment. Whether you're into immersive music, blockbuster movies, binge-worthy web series, captivating anime, or thrilling games — 
        our goal is to bring all of these experiences into one cohesive platform. We believe that your entertainment preferences across different mediums can work together to help you discover something new and meaningful every time you visit.
    """)

    st.write("""
        Thank you for using TunePics! We hope you enjoy the app as much as we enjoyed creating it.
    """)
