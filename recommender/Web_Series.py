import streamlit as st
import pandas as pd
import pickle
import requests

def selected_page():
    # OMDb API Key
    API_KEY = "12ad0b3"

    no_cover_image_path = "no cover.png"
    # Fetch full series info
    def fetch_series_info(title, api_key=API_KEY):
        url = f"http://www.omdbapi.com/?t={title}&apikey={api_key}"
        response = requests.get(url)

        if response.status_code != 200 or response.json().get("Response") == "False":
            return {
                "poster":no_cover_image_path,
                "imdb_link": "",
                "seasons": "N/A",
                "genre": "N/A",
                "plot": "N/A",
                "rating": "N/A"
            }

        data = response.json()
        return {
            "poster": data.get("Poster", "https://via.placeholder.com/300x450?text=No+Poster"),
            "imdb_link": f"https://www.imdb.com/title/{data.get('imdbID', '')}/" if data.get("imdbID") else "",
            "seasons": data.get("totalSeasons", "N/A"),
            "genre": data.get("Genre", "N/A"),
            "plot": data.get("Plot", "N/A"),
            "rating": data.get("imdbRating", "N/A")
        }

    # Load data (assuming it's a tuple: (DataFrame, similarity matrix))
    try:
        with open('web_series.pkl', 'rb') as f:
            web_series = pickle.load(f)
    except FileNotFoundError:
        st.error("Error: 'web_series.pkl' not found. Please make sure the file is in the correct directory.")
        return
    except Exception as e:
        st.error(f"Error loading 'web_series.pkl': {e}")
        return

    try:
        with open('similarity.pkl', 'rb') as f:
            similarity = pickle.load(f)
    except FileNotFoundError:
        st.error("Error: 'similarity.pkl' not found. Please make sure the file is in the correct directory.")
        return
    except Exception as e:
        st.error(f"Error loading 'similarity.pkl': {e}")
        return

    # Recommendation function with fix
    def get_recommendations(name, num_recommendations=5, cosine_sim=similarity):
        if not isinstance(web_series, pd.DataFrame) or 'name' not in web_series.columns:
            return "Error: The 'web_series' data is not in the expected format."

        if name not in web_series['name'].values:
            return f"No recommendations found for '{name}'. Please check the show name."

        try:
            idx = web_series[web_series['name'] == name].index[0]
        except IndexError:
            return f"Could not find index for '{name}' in the web series data."

        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Filter only valid indices
        valid_indices = [i[0] for i in sim_scores[1:] if i[0] < len(web_series)]
        valid_indices = valid_indices[:num_recommendations]

        if not valid_indices:
            return "No valid recommendations found."

        return web_series['name'].iloc[valid_indices]

    # Streamlit UI
    st.title("📺 Web Series Recommender")

    with st.form("recommendation_form"):
        if isinstance(web_series, pd.DataFrame) and 'name' in web_series.columns:
            selected_series = st.selectbox("🎬 Choose a Web Series", web_series['name'].values)
            num_recommend = st.slider("🔢 How many recommendations do you want?", 5,15)
            submitted = st.form_submit_button("🚀 Show Web Series Recommendation")
        else:
            st.warning("Web series data could not be loaded properly. Please check the data files.")
            submitted = False

        if submitted:
            # Show selected series info
            selected_info = fetch_series_info(selected_series)
            st.subheader(f"📌 Details for: {selected_series}")
            st.image(selected_info['poster'], width=200)
            st.markdown(f"**Genre:** {selected_info['genre']}")
            st.markdown(f"**Seasons:** {selected_info['seasons']}")
            st.markdown(f"**Rating:** {selected_info['rating']}")
            st.markdown(f"**Plot:** {selected_info['plot']}")
            if selected_info['imdb_link']:
                st.markdown(f"[🔗 IMDb Page]({selected_info['imdb_link']})", unsafe_allow_html=True)

            st.markdown("---")
            st.subheader("🎯 You might also like:")

            recommendations = get_recommendations(selected_series, num_recommendations=num_recommend)

            if isinstance(recommendations, str):
                st.warning(recommendations)
            else:
                max_cols = 5
                for i in range(0, len(recommendations), max_cols):
                    cols = st.columns(max_cols)
                    for j, title in enumerate(recommendations[i:i+max_cols]):
                        info = fetch_series_info(title)
                        with cols[j]:
                            st.image(info['poster'], caption=title, use_container_width=True)
                            st.markdown(f"**Genre:** {info['genre']}")
                            st.markdown(f"**Seasons:** {info['seasons']}")
                            st.markdown(f"**Rating:** {info['rating']}")
                            if info['imdb_link']:
                                st.markdown(f"[🔗 IMDb Link]({info['imdb_link']})", unsafe_allow_html=True)

    st.markdown("---")
    st.info("**Note:** Recommendations are based on content similarity and may not always be accurate.")