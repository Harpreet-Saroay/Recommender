import requests

# Replace this with your actual API key
API_KEY = "6ebac43bc4c9720f4036f5f44c43999819920e4f"
BASE_URL = "https://www.giantbomb.com/api"
HEADERS = {
    "User-Agent": "GameRecBot/1.0"
}

def search_game(query):
    """Search for a game and return the first match's GUID"""
    url = f"{BASE_URL}/search/"
    params = {
        "api_key": API_KEY,
        "format": "json",
        "query": query,
        "resources": "game"
    }
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()
    
    if data['results']:
        first_game = data['results'][0]
        print(f"Found: {first_game['name']}")
        return first_game['guid']
    else:
        print("No results found.")
        return None

def get_game_details(guid):
    """Fetch detailed info for a specific game using its GUID"""
    url = f"{BASE_URL}/game/{guid}/"
    params = {
        "api_key": API_KEY,
        "format": "json"
    }
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()
    
    if 'results' in data:
        details = data['results']
        print(f"Title: {details['name']}")
        print(f"Deck (Short Description): {details.get('deck', 'No description')}")
        print(f"Genres: {[g['name'] for g in details.get('genres', [])]}")
        print(f"Platforms: {[p['name'] for p in details.get('platforms', [])]}")
        print(f"Release Date: {details.get('original_release_date', 'N/A')}")
    else:
        print("Error fetching game details.")

# 🔍 Example usage:
game_query = "Celeste"
guid = search_game(game_query)
if guid:
    get_game_details(guid)


client_id = 'lddwqtxxrkvy61djfkbsf26g1q1m4w'
client_secert = 'ulwemt0qpihxgaulm69h6fkfj685ea'

import requests

# Replace with your actual client ID and secret
client_id = 'lddwqtxxrkvy61djfkbsf26g1q1m4w'
client_secret = 'ulwemt0qpihxgaulm69h6fkfj685ea'

def get_twitch_access_token(client_id, client_secret):
    """Fetch an access token from Twitch API"""
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, data=params)
    if response.status_code == 200:
        data = response.json()
        print(f"Access Token: {data['access_token']}")
        return data['access_token']
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

# Example usage
access_token = get_twitch_access_token(client_id, client_secret)