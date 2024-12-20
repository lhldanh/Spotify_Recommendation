import streamlit as st
from utils import *
import pandas as pd

def embed_spotify_tracks(tracks_df, width=300, height=80):
    if not isinstance(tracks_df, pd.DataFrame):
        st.warning('No track in your playlist exist in my data')
        return
    st.write("## :rainbow[Recommended Songs] 🎵")
    for _, row in tracks_df.iterrows():
        track_uri = row['track_uri']
        track_id = track_uri.split(":")[-1]

        spotify_embed_url = f"https://open.spotify.com/embed/track/{track_id}"

        col1, col2 = st.columns([4, 1])
        with col1:
            iframe_code = f"""
                <iframe src="{spotify_embed_url}" width="{width}" height="{height}" frameborder="0" 
                allowtransparency="true" allow="encrypted-media"></iframe>
            """
            st.markdown(iframe_code, unsafe_allow_html=True)
        with col2:
            st.write('')
            st.write(f"**Similarity:** {row['cosine_similarity']:.4f}")
def main():
    # Title
    st.title(':green[Spotify Recommendation System] 🎵')
    
    # Load track data
    tracks_df = pd.read_csv('dataforapp.csv')
    recommend = ''
    if "input_type" not in st.session_state:
        st.session_state["input_type"] = ''

    if st.session_state["input_type"] == '':
        select_input_type = st.selectbox(label = 'Select an input type', options=['Import URL', 'Create Playlist'], index=0)
        input_btn = st.button('OK')
        if input_btn:
            st.session_state["input_type"] = select_input_type
            st.rerun()

    if st.session_state["input_type"] == 'Import URL':
        back_btn = st.button('Back to select input type')
        if back_btn:
            st.session_state["input_type"] = ''
            st.rerun()

        # Initial URL 
        st.write('## :blue[Import a spotify playlist]')
        st.write('Enter URL')
        col1, col2 = st.columns([4, 1], gap="small")
        with col1:
            playlist_url = st.text_input(label = 'url_tbox', label_visibility='collapsed', placeholder='Example: https://open.spotify.com/playlist/6EOen9n2Q1aXkAZsJoDrBp')

        with col2:
            url_btn = st.button('Get', use_container_width=True)
        
        # Solve URL
        if url_btn:
            if playlist_url:
                if is_valid_spotify_playlist_url(playlist_url):
                    track_uris = get_track_from_playlist(playlist_url)
                    if track_uris == 0:
                        st.error('track_uris == 0')
                    else:
                        st.success('Waiting for the song....')
                        recommend = recommend_songs(tracks_df, track_uris)
                        embed_spotify_tracks(recommend)
                        # if not recommend.empty:
                        #     st.warning('No tracks in your playlist exist in my data')
                        # else:
                        #     embed_spotify_tracks(recommend)
                else:
                    st.error('Unvalid url')
            else:
                st.error('Please enter an url')

    if st.session_state['input_type'] == 'Create Playlist':
        back_btn = st.button('Back to select input type')
        if back_btn:
            st.session_state["input_type"] = ''
            st.rerun()

        # Gộp track_name, artist_name và track_uri từ tracks_df
        track_list = list(zip(tracks_df['track_name'], tracks_df['artist_name'], tracks_df['track_uri']))

        def search_tracks(search_query, tracks):
            """Tìm kiếm bài hát theo query và trả về danh sách (name, artist, uri)."""
            return [(name, artist, uri) for name, artist, uri in tracks if search_query.lower() in name.lower()] if search_query else []

        # Input để nhập từ khóa tìm kiếm
        search_query = st.text_input("Search for a song:")

        # Lọc danh sách gợi ý dựa trên input
        filtered_tracks = search_tracks(search_query, track_list)

        # Chỉ hiển thị tên bài hát và nghệ sĩ trong selectbox
        selected_display = [f"{name} - {artist}" for name, artist, uri in filtered_tracks]
        selected_track = st.selectbox("Select songs:", options=selected_display)

        # Khởi tạo session state nếu chưa có
        if "created_playlist" not in st.session_state:
            st.session_state["created_playlist"] = []  # Danh sách tên + nghệ sĩ
        if "created_playlist_uri" not in st.session_state:
            st.session_state["created_playlist_uri"] = []  # Danh sách track_uri

        # Xử lý thêm bài hát
        if selected_track:
            col1, col2 = st.columns([3, 1], gap='small')
            with col1:
                st.write(f"Add :green[{selected_track}] to your playlist?")
            with col2:
                add_btn = st.button('Add', use_container_width=True)
                if add_btn:
                    # Tìm track_uri và artist tương ứng với selected_track
                    for name, artist, uri in filtered_tracks:
                        if f"{name} - {artist}" == selected_track:
                            track_display = f"{name} - {artist}"
                            track_uri = uri
                            break

                    # Thêm vào playlist nếu chưa tồn tại
                    if track_display not in st.session_state.created_playlist:
                        st.session_state.created_playlist.append(track_display)
                        st.session_state.created_playlist_uri.append(track_uri)

        # Hiển thị playlist hiện tại
        st.write('Your current playlist:')
        st.write(st.session_state.created_playlist)
        recommend_btn = st.button('Get Recommendation')
        if recommend_btn:
            recommend = recommend_songs(tracks_df, st.session_state.created_playlist_uri)
            embed_spotify_tracks(recommend)

if __name__ == '__main__':
    main()