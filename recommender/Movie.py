import pickle 
import requests
import pandas as pd 
import time  
import streamlit as st 

def selected_page():
    st.title("🎬 Movie Recommendation System")
    API_KEY = "12ad0b3"

    def fetch_movie_details(title, api_key):
        url = f"http://www.omdbapi.com/?t={title}&apikey={api_key}"
        response = requests.get(url)
        data = response.json()
        poster = data.get("Poster", "https://via.placeholder.com/300x450?text=Poster+Not+Available")
        imdb_id = data.get("imdbID", "")
        imdb_link = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else ""
        genre = data.get("Genre", "N/A")
        rating = data.get("imdbRating", "N/A")
        return poster, imdb_link, genre, rating

    try:
        movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
        movies = pd.DataFrame(movies_dict)
        similarity = pickle.load(open('similarity.pkl', 'rb'))
    except FileNotFoundError:
        st.error("Required files are missing.")
        st.stop()

    movie_podcast_links = {
        "inception": "https://www.youtube.com/watch?v=8hP9D6kZseM",
        "interstellar": "https://www.youtube.com/watch?v=zSWdZVtXT7E",
        "the dark knight": "https://www.youtube.com/watch?v=EXeTwQWrcwY",
        "titanic": "https://www.youtube.com/watch?v=kVrqfYjkTdQ",
        "avatar": "https://www.youtube.com/watch?v=5PSNL1qE6VY"
    }

    with st.form("movie_selection_form"):
        selected_movie_name = st.selectbox('🍿 Choose a movie you like:', movies['title'].values)
        num_recs = st.slider("🎯 Number of recommendations:", min_value=5, max_value=20, value=10, step=1)
        submitted = st.form_submit_button("🚀 Show Movie Recommendations")

        if submitted:
            with st.spinner('Fetching your recommendations...'):
                time.sleep(1.5)
                selected_poster, selected_link, selected_genre, selected_rating = fetch_movie_details(selected_movie_name, API_KEY)
                st.markdown("### 🎥 Selected Movie")
                st.image(selected_poster, width=200)
                st.markdown(f"**{selected_movie_name}**")
                st.markdown(f"**Genre:** {selected_genre}")
                st.markdown(f"**IMDb Rating:** {selected_rating}")
                st.markdown(f"[View on IMDb]({selected_link})", unsafe_allow_html=True)

                def fetch_recommendations(movie_name, num_recommendations=10):
                    try:
                        movie_index = movies[movies['title'] == movie_name].index[0]
                        distances = similarity[movie_index]
                        recommended = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:num_recommendations + 1]

                        recommendation_details = []
                        for i in recommended:
                            title = movies.iloc[i[0]].title
                            poster, imdb_link, genre, rating = fetch_movie_details(title, API_KEY)
                            recommendation_details.append({'title': title, 'poster': poster, 'link': imdb_link, 'genre': genre, 'rating': rating})
                        return recommendation_details
                    except IndexError:
                        st.error(f"Could not find movie: {movie_name}")
                        return []

                recommendations = fetch_recommendations(selected_movie_name, num_recs)
                if recommendations:
                    st.markdown("### 🔁 Movie Recommendations")
                    cols_per_row = 5
                    for i in range(0, len(recommendations), cols_per_row):
                        cols = st.columns(cols_per_row)
                        for col_idx, recommendation in enumerate(recommendations[i:i+cols_per_row]):
                            with cols[col_idx % cols_per_row]:
                                st.image(recommendation['poster'], use_container_width=True)
                                st.markdown(f"[{recommendation['title']}]({recommendation['link']})", unsafe_allow_html=True)
                                st.markdown(f"**Genre:** {recommendation['genre']}")
                                st.markdown(f"**IMDb Rating:** {recommendation['rating']}")
                                podcast_link = movie_podcast_links.get(recommendation['title'].strip().lower())
                                if podcast_link:
                                    st.markdown(f"[🎧 Listen to Podcast]({podcast_link})", unsafe_allow_html=True)
    st.markdown("---")
    st.info("**Note:** Recommendations are based on content similarity and may not always be accurate.")