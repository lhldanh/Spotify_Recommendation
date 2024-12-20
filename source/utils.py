import re

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

CLIENT_ID = "ea1014b7e00244639c8a4e1662892df5"
CLIENT_SECRET = "6f83fc7f62b9425398f6590543d010e0"
REDIRECT_URI = "http://localhost:8888/callback"
SCOPE = "user-library-read playlist-read-private"

# Xác thực với Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))

# Lấy thông tin người dùng
user = sp.current_user()
print(f"Logged in as: {user['display_name']}")

def is_valid_spotify_playlist_url(url):
    # Regex để kiểm tra URL Spotify hợp lệ
    pattern = r"^https://open\.spotify\.com/playlist/[a-zA-Z0-9]+(\?si=[a-zA-Z0-9]+)?$"
    if re.match(pattern, url):
        return True
    return False


def get_track_from_playlist(url):
    id = []
    try:
        results = sp.playlist_items(url)
        print("Playlist items fetched successfully.")
        for item in results['items']:
            track = item['track']
            id.append(track['uri'])
            # print(f"Track: {track['name']} by {track['artists'][0]['name']}")
        return id
    except spotipy.exceptions.SpotifyException as e:
        return 0
    except Exception as ex:
        return 0

def recommend_songs(df, playvec_list, k=10):
    features = ['danceability', 'energy', 'key', 'loudness', 'mode',
                'speechiness', 'acousticness', 'instrumentalness',
                'liveness', 'valence', 'tempo', 'time_signature']
    
    playvec = df[df['track_uri'].isin(playvec_list)]
    print(len(playvec), len(playvec_list))
    print(playvec['track_uri'])
    if playvec.empty:
        return -1
    df = df[~df['track_name'].isin(playvec['track_name'])].copy()
    
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df[features])
    playvec_scaled = scaler.transform(playvec[features])

    similarity_matrix = cosine_similarity(df_scaled, playvec_scaled)
    df['cosine_similarity'] = similarity_matrix.mean(axis=1)  # Trung bình similarity với tất cả bài hát trong playvec

    df = df.sort_values(by='cosine_similarity', ascending=False)

    artist_limit = max(1, int(0.1 * k))
    recommended_songs = df.groupby('artist_name').head(artist_limit)

    final_recommendations = recommended_songs.head(k)

    return final_recommendations[['track_name', 'artist_name', 'track_uri', 'cosine_similarity']]