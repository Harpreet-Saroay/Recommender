import pickle
import requests
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
import time

def selected_page():

    # === Load Data ===
    with open('game_data.pkl', 'rb') as f:
        games_data = pickle.load(f)

    with open('tfidf_matrix.pkl', 'rb') as f:
        tfidf_matrix = pickle.load(f)

    # === IGDB API Credentials ===
    client_id = 'lddwqtxxrkvy61djfkbsf26g1q1m4w'
    client_secret = 'ulwemt0qpihxgaulm69h6fkfj685ea'

    # === Giant Bomb API ===
    GIANTBOMB_API_KEY = "6ebac43bc4c9720f4036f5f44c43999819920e4f"
    GB_BASE_URL = "https://www.giantbomb.com/api"
    GB_HEADERS = {"User-Agent": "GameRecBot/1.0"}

    # === Get IGDB Token ===
    def get_igdb_token(client_id, client_secret):
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        }
        response = requests.post(url, data=params)
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            st.error("❌ Failed to get IGDB token.")
            return None

    access_token = get_igdb_token(client_id, client_secret)

    # === IGDB Fetch Game Info ===
    def get_game_info_from_igdb(game_name, client_id, access_token):
        headers = {
            'Client-ID': client_id,
            'Authorization': f'Bearer {access_token}'
        }
        query = f'''
            search "{game_name}";
            fields name, url, cover.url;
            limit 1;
        '''
        response = requests.post('https://api.igdb.com/v4/games', headers=headers, data=query)
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            game_url = data.get('url', 'https://www.igdb.com/')
            cover_url = None
            if 'cover' in data:
                cover_id = data['cover']['id']
                cover_resp = requests.post(
                    'https://api.igdb.com/v4/covers',
                    headers=headers,
                    data=f'fields url; where id = {cover_id};'
                )
                if cover_resp.status_code == 200 and cover_resp.json():
                    cover_url = cover_resp.json()[0]['url'].replace('t_thumb', 't_cover_big')
            return cover_url, game_url
        return None, None

    # === Giant Bomb Game Info ===
    def search_game(query):
        url = f"{GB_BASE_URL}/search/"
        params = {
            "api_key": GIANTBOMB_API_KEY,
            "format": "json",
            "query": query,
            "resources": "game"
        }
        response = requests.get(url, headers=GB_HEADERS, params=params)
        data = response.json()
        if data['results']:
            return data['results'][0]['guid']
        return None

    def get_game_details(guid):
        url = f"{GB_BASE_URL}/game/{guid}/"
        params = {
            "api_key": GIANTBOMB_API_KEY,
            "format": "json"
        }
        response = requests.get(url, headers=GB_HEADERS, params=params)
        data = response.json()
        if 'results' in data:
            d = data['results']
            return {
                "Title": d.get("name", "N/A"),
                "Description": d.get("deck", "No description available."),
                "Genres": ", ".join([g['name'] for g in d.get("genres", [])]) if d.get("genres") else "N/A",
                "Platforms": ", ".join([p['name'] for p in d.get("platforms", [])]) if d.get("platforms") else "N/A",
                "Release Date": d.get("original_release_date", "N/A"),
                "Image": d.get("image", {}).get("super_url", "no cover.png"),
                "URL": d.get("site_detail_url", "#")
            }
        return None

    # === Unified Game Info with Fallback ===
    def get_game_info_combined(game_name, client_id, access_token):
        cover_url, game_url = get_game_info_from_igdb(game_name, client_id, access_token)
        if cover_url:
            return f"https:{cover_url}", game_url
        guid = search_game(game_name)
        if guid:
            details = get_game_details(guid)
            if details:
                return details.get("Image", "no cover.png"), details.get("URL", "https://www.giantbomb.com/")
        return "no cover.png", "https://www.giantbomb.com/"

    # === Recommendation Logic ===
    def recommend_games(game_name, top_n=5):
        if game_name not in games_data['name'].values:
            return []
        idx = games_data[games_data['name'] == game_name].index[0]
        cosine_sim = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
        similar_indices = cosine_sim.argsort()[-top_n-1:-1][::-1]
        return games_data.iloc[similar_indices]['name'].values

    st.title("🎮 Game Recommendation System")

    with st.form("game_recommender_form"):
        game_list = games_data['name'].values
        selected_game = st.selectbox("🎮 Select a game to get similar recommendations:", game_list)
        num_recommendations = st.slider("📊 Number of Recommendations", 5, 15)
        submit = st.form_submit_button("🚀 Show Game Recommendations")

        if submit:
            with st.spinner('Fetching your recommendations...'):
                time.sleep(1.5)

                st.markdown("---")

                no_cover_image_path = "no cover.png"
                recommendations = recommend_games(selected_game, top_n=num_recommendations)

                selected_cover_url, selected_game_url = get_game_info_combined(selected_game, client_id, access_token)
                selected_poster = selected_cover_url if selected_cover_url else no_cover_image_path

                st.markdown("### 🎮 Selected Game:")
                st.image(selected_poster, width=200)
                st.markdown(
                    f"<div style='text-align: left; font-size:18px;'><a href='{selected_game_url}' target='_blank'>{selected_game}</a></div>",
                    unsafe_allow_html=True
                )
                st.markdown("---")
                st.markdown("### 🎯 Recommendations Just for You:")

                cols_per_row = 5
                names, posters, links = [], [], []

                for game in recommendations:
                    cover_url, game_url = get_game_info_combined(game, client_id, access_token)
                    names.append(game)
                    posters.append(cover_url if cover_url else no_cover_image_path)
                    links.append(game_url or "https://www.igdb.com/")

                for i in range(0, len(names), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for col, name, poster, link in zip(cols, names[i:i+cols_per_row], posters[i:i+cols_per_row], links[i:i+cols_per_row]):
                        with col:
                            st.image(poster, use_container_width=True)
                            st.markdown(
                                f"<div style='text-align: center;'><a href='{link}' target='_blank'>{name}</a></div>",
                                unsafe_allow_html=True
                            )
    st.markdown("---")
    st.info("Note: Recommendations are based on content similarity and may not always be accurate.")

