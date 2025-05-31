import streamlit as st
import pickle
import spotipy
import requests
from spotipy.oauth2 import SpotifyClientCredentials
import pyttsx3
import webbrowser
import speech_recognition as sr
import lyricsgenius

def selected_page():
    st.title("🎵 Music Recommender System")

    # Text-to-speech
    def talk(text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    # Voice input
    def get_voice_input():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening... Please speak now.")
            try:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio)
                st.success(f"You said: {text}")
                return text
            except sr.UnknownValueError:
                st.error("Sorry, I could not understand the audio.")
            except sr.RequestError:
                st.error("Could not request results. Check your internet.")
            except sr.WaitTimeoutError:
                st.error("Listening timed out.")
        return ""

    class MusicRecommenderApp:
        def __init__(self, music_data_path, similarity_data_path, client_id, client_secret):
            self.music = pickle.load(open(music_data_path, 'rb'))
            self.similarity = pickle.load(open(similarity_data_path, 'rb'))
            self.sp = spotipy.Spotify(
                client_credentials_manager=SpotifyClientCredentials(
                    client_id=client_id, client_secret=client_secret
                )
            )

        def play_podcast(self, podcast_name):
            if podcast_name:
                st.write(f"Playing the podcast: {podcast_name}")
                talk(f"Playing the podcast {podcast_name}")
                url = f"https://www.youtube.com/results?search_query={podcast_name}"
                webbrowser.open(url)

        def get_song_info(self, song_name, artist_name):
            search_query = f"track:{song_name} artist:{artist_name}"
            results = self.sp.search(q=search_query, type="track")
            if results and results["tracks"]["items"]:
                track = results["tracks"]["items"][0]
                album_name = track["album"]["name"]
                album_url = track["album"]["images"][0]["url"]
                spotify_url = track["external_urls"]["spotify"]
                return album_name, album_url, spotify_url
            else:
                return "Unknown Album", "https://i.postimg.cc/0QNxYz4V/social.png", "#"

        def recommend(self, song, num_recommendations=5):
            index = self.music[self.music['song'] == song].index[0]
            distances = sorted(
                list(enumerate(self.similarity[index])), reverse=True, key=lambda x: x[1]
            )
            recommended_music_data = []

            for i in distances[1:num_recommendations + 1]:
                artist = self.music.iloc[i[0]].artist
                song_name = self.music.iloc[i[0]].song
                album_name, poster_url, spotify_url = self.get_song_info(song_name, artist)
                recommended_music_data.append({
                    'artist': artist,
                    'song': song_name,
                    'album': album_name,
                    'poster_url': poster_url,
                    'spotify_url': spotify_url
                })
            return recommended_music_data

        def run(self):
            music_list = self.music['song'].values

            with st.form("recommendation_form"):
                selected_song = st.selectbox("🎶 Choose a song:", music_list)
                num_recommend = st.slider("🎯 Number of recommendations", 5, 15)
                submitted = st.form_submit_button("🚀 Show Music Recommendations")

                if submitted:
                    song_row = self.music[self.music['song'] == selected_song].iloc[0]
                    artist_name = song_row.artist
                    album_name, poster_url, spotify_url = self.get_song_info(selected_song, artist_name)

                    st.markdown("## 🎧 Selected Song")
                    st.image(poster_url, width=300)
                    st.markdown(f"**{selected_song}**")
                    st.markdown(f"by **{artist_name}**")
                    st.markdown(f"Album: *{album_name}*")
                    st.markdown(f"[Listen on Spotify]({spotify_url})", unsafe_allow_html=True)
                    st.markdown("---")

                    recommendations = self.recommend(selected_song, num_recommend)
                    if recommendations:
                        st.markdown("### 🔁 Recommended Songs")
                        for i in range(0, len(recommendations), 5):
                            row_recommendations = recommendations[i:i+5]
                            cols = st.columns(len(row_recommendations))
                            for col, rec in zip(cols, row_recommendations):
                                with col:
                                    st.markdown(f"[![{rec['song']}]({rec['poster_url']})]({rec['spotify_url']})", unsafe_allow_html=True)
                                    st.markdown(f"[{rec['song']}]({rec['spotify_url']})", unsafe_allow_html=True)
                                    st.markdown(f"by *{rec['artist']}*")
                                    st.markdown(f"Album: *{rec['album']}*")
                    else:
                        st.warning("No recommendations found for this song.")

            st.markdown("---")
            st.info("**Note:** Recommendations are based on content similarity and may not always be accurate.")

    # Constants
    MUSIC_DATA_PATH = "songdf.pkl"
    SIMILARITY_DATA_PATH = "songsimilarity.pkl"
    CLIENT_ID = "70a9fb89662f4dac8d07321b259eaad7"
    CLIENT_SECRET = "4d6710460d764fbbb8d8753dc094d131"
    GENIUS_ACCESS_TOKEN = "CaUlsSrNOHG2Vp9kv7v_Q_h0HE8gSS8p1ol9CbCmhmtHsKMbIcezZQWfVimzPoeT"

    genius = lyricsgenius.Genius(
        GENIUS_ACCESS_TOKEN,
        skip_non_songs=True,
        excluded_terms=["(Remix)", "(Live)"]
    )

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

    def recommend_one(user_input):
        result = sp.search(q=user_input, type='track', limit=1)
        if not result['tracks']['items']:
            return None

        track = result['tracks']['items'][0]
        name = track['name']
        artist = track['artists'][0]['name']
        album_cover = track['album']['images'][0]['url'] if track['album']['images'] else None
        url = track['external_urls']['spotify']

        try:
            song = genius.search_song(name, artist)
            lyrics = song.lyrics if song else "Lyrics not found."
        except Exception:
            lyrics = "Lyrics not available."

        return {
            'name': name,
            'artist': artist,
            'url': url,
            'album_cover': album_cover,
            'lyrics': lyrics
        }

    # Run Music App
    app = MusicRecommenderApp(MUSIC_DATA_PATH, SIMILARITY_DATA_PATH, CLIENT_ID, CLIENT_SECRET)
    app.run()

    # Single song search with optional voice input
    st.title("🎶 Single Song Recommender")
    user_input = st.text_input("Enter a song or artist:", placeholder="e.g., Taylor Swift or Blinding Lights")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Use Voice Input"):
            user_input = get_voice_input()
            if user_input:
                talk(f"You said: {user_input}")
                song = recommend_one(user_input)
                if song:
                    st.subheader(f"🎵 {song['name']} - {song['artist']}")
                    if song['album_cover']:
                        st.image(song['album_cover'], width=300)
                    st.markdown(f"[Listen on Spotify]({song['url']})")
                    st.subheader("📝 Lyrics")
                    st.text(song['lyrics'])
                else:
                    st.warning("No matching song found.")

    with col2:
        
            if user_input:
                song = recommend_one(user_input)
                if song:
                    st.subheader(f"🎵 {song['name']} - {song['artist']}")
                    if song['album_cover']:
                        st.image(song['album_cover'], width=300)
                    st.markdown(f"[Listen on Spotify]({song['url']})")
                    st.subheader("📝 Lyrics")
                    with st.expander("Show Lyrics"):
                        st.text(song['lyrics'])
                else:
                    st.warning("No matching song found.")
