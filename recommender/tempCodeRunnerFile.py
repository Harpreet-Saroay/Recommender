import pandas as pd
import numpy as np
import pickle
import requests
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
import time

# === Load Data ===
with open('game_data.pkl', 'rb') as f:
    games_data = pickle.load(f)

with open('tfidf_matrix.pkl', 'rb') as f:
    tfidf_matrix = pickle.load(f)

# === IGDB API Credentials ===
client_id = 'lddwqtxxrkvy61djfkbsf26g1q1m4w'
client_secret = 'ulwemt0qpihxgaulm69h6fkfj685ea'

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

# === Fetch Game Info (Poster + Link) ===
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
    else:
        return None, None

# === Recommendation Logic ===
def recommend_games(game_name, top_n=5):
    if game_name not in games_data['name'].values:
        return []
    idx = games_data[games_data['name'] == game_name].index[0]
    cosine_sim = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    similar_indices = cosine_sim.argsort()[-top_n-1:-1][::-1]
    return games_data.iloc[similar_indices]['name'].values

# === Streamlit UI ===
st.set_page_config(page_title="🎮 Game Recommender", layout="wide")
st.title("🎮 Game Recommendation System")

# === UI Elements ===
game_list = games_data['name'].values
selected_game = st.selectbox("🎮 Select a game to get similar recommendations:", game_list)
num_recommendations = st.selectbox("📊 Number of Recommendations", [5, 10, 15], index=0)

if st.button('🚀 Recommend Games'):
    with st.spinner('Fetching your recommendations...'):
        time.sleep(1.5)  # Simulate loading delay

        st.markdown("---")

        recommendations = recommend_games(selected_game, top_n=num_recommendations)


        st.markdown("### 🎯 Recommendations Just for You:")

        cols_per_row = 5
        names, posters, links = [], [], []

        # Load fallback image path
        no_cover_image_path = "no cover.png"  # Make sure this file is in your project folder

        # Fetch all game info
        for game in recommendations:
            cover_url, game_url = get_game_info_from_igdb(game, client_id, access_token)
            names.append(game)
            posters.append(f"https:{cover_url}" if cover_url else no_cover_image_path)
            links.append(game_url or "https://www.igdb.com/")

        # Display in rows
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