import streamlit as st
import pandas as pd
import pickle
import requests

# Function to fetch anime details from Jikan API
@st.cache_data
def fetch_anime_details(anime_name):
    url = f"https://api.jikan.moe/v4/anime?q={anime_name}&limit=1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get('data')
        if data:
            return data[0]
    return None

def selected_page():
    # Load model and data
    @st.cache_resource
    def load_model():
        with open("anime_model.pkl", "rb") as f:
            df, tfidf, cosine_sim = pickle.load(f)
        indices = pd.Series(df.index, index=df['Name'].str.lower())
        return df, cosine_sim, indices

    df, cosine_sim, indices = load_model()
    no_cover_image_path = "no cover.png"

    # Get anime poster and link from Jikan API
    @st.cache_data
    def get_anime_info(anime_name):
        anime_data = fetch_anime_details(anime_name)
        if anime_data:
            poster = anime_data['images']['jpg']['image_url']
            link = anime_data['url']
            manga = anime_data.get('source', 'Unknown')
            rating = anime_data.get('score')
            episodes = anime_data.get('episodes')
            plot = anime_data.get('synopsis', 'No synopsis available.')
            return poster, link, manga, rating, episodes, plot
        return no_cover_image_path, None, None, None, None, None

    # Recommend function
    def recommend(title, top_n=5, genre_filter=None, type_filter=None, manga_only=False):
        title = title.lower()
        if title not in indices:
            return []
        idx = indices[title]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:]

        results = []
        for i, _ in sim_scores:
            anime = df.iloc[i]
            anime_title = anime['Name']
            genres = anime.get('Genres', '')
            anime_type = anime.get('Type', '')
            source = anime.get('Source', '')

            if genre_filter and genre_filter not in genres:
                continue
            if type_filter and anime_type != type_filter:
                continue
            if manga_only and "manga" not in str(source).lower():
                continue

            poster, link, manga, rating, episodes, plot = get_anime_info(anime_title)
            results.append((anime_title, poster, link, manga, rating, episodes, plot))
            if len(results) == top_n:
                break
        return results

    # UI Title and Icon
    st.title("🎬 Anime Recommender")
    st.markdown("Find similar anime based on what you like.")

    # Form for user input
    with st.form(key='anime_selection_form'):
        anime_list = df['Name'].unique()
        selected_anime = st.selectbox("🎬 Choose an Anime you like:", anime_list)

        genre_list = sorted(set(g.strip() for g_list in df['Genres'].dropna().str.split(',') for g in g_list))
        selected_genre = st.selectbox("Filter by Genre (optional):", ["Any"] + genre_list)
        genre_filter = None if selected_genre == "Any" else selected_genre

        top_n = st.slider("🔢 How many recommendations do you want?", 5, 15)
        submit_button = st.form_submit_button(" 🚀 Show Anime Recommendations")

        # Recommendations
        if submit_button:
            with st.spinner("Finding recommendations..."):
                recommendations = recommend(
                    selected_anime,
                    top_n=top_n,
                    genre_filter=genre_filter,
                )

                # Show selected anime
                st.markdown("### Your Selected Anime:")
                selected_poster, selected_link, selected_manga, selected_rating, selected_episodes, selected_plot = get_anime_info(selected_anime)
                col1, col2 = st.columns([1, 3])
                with col1:
                    if selected_poster:
                        st.image(selected_poster, use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/200x300?text=No+Image", use_container_width=True)
                with col2:
                    st.subheader(selected_anime)
                    st.write(f"[Link to Anime]({selected_link})")
                    st.write(f"Source: {selected_manga}")
                    if selected_rating:
                        st.write(f"Rating: {selected_rating}/10")
                    if selected_episodes is not None:
                        st.write(f"Episodes: {selected_episodes}")
                    if 'Genres' in df.columns:
                        st.write(f"Genres: {df[df['Name'] == selected_anime]['Genres'].values[0]}")
                    if selected_plot:
                        with st.expander("Summary:"):
                            st.write(selected_plot)

                st.markdown("---")
                st.markdown("### Recommended Anime:")

                # Show recommendations in 5 columns, padded for symmetry
                if recommendations:
                    num_cols = 5
                    padded_recs = recommendations[:]

                    # Pad the last row with empty items if needed
                    while len(padded_recs) % num_cols != 0:
                        padded_recs.append(("", None, None, None, None, None, None))

                    # Display in rows of 5
                    for i in range(0, len(padded_recs), num_cols):
                        cols = st.columns(num_cols)
                        for j in range(num_cols):
                            title, poster, link, manga, rating, episodes, plot = padded_recs[i + j]
                            with cols[j]:
                                if title:
                                    st.subheader(title)
                                    if poster:
                                        st.image(poster, use_container_width=True)
                                    else:
                                        st.image("https://via.placeholder.com/200x300?text=No+Image", use_container_width=True)
                                    st.markdown(f"[Anime link]({link})")
                                    if rating:
                                        st.markdown(f"Rating: {rating}/10")
                                    if episodes is not None:
                                        st.markdown(f"Episodes: {episodes}")
                                else:
                                    st.markdown("---")
                else:
                    st.error("No recommendations found based on your selection and filters.")
    st.markdown("---")
    st.info("Note: Recommendations are based on content similarity and may not always be perfectly accurate.")

