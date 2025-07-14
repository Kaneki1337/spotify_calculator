# calculator.py

import streamlit as st
import requests
import base64
from urllib.parse import urlparse

# Spotify artist ID ayıklama

def extract_artist_id(spotify_url):
    try:
        path = urlparse(spotify_url).path
        return path.split("/")[-1]
    except:
        return None

# Spotify API token alma

def get_spotify_token(client_id, client_secret):
    auth_str = f"{client_id}:{client_secret}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }

    r = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    token = r.json().get("access_token")
    return token

# Spotify API'den sanatçı verisi alma

def get_artist_data_from_api(artist_id, token):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

# Spotify API'den sanatçının en popüler şarkılarının popularity skorlarını al

def get_artist_top_tracks(artist_id, token):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=US"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("tracks", [])
    return []

# Popularity değerini yaklaşık stream sayısına çevir

def estimate_streams_from_popularity(popularity):
    return int((popularity / 100) * 5_000_000)  # örnek oran

# Ülkeye göre stream kazanç oranları

region_rates = {
    "Amerika": 0.0035,
    "Türkiye": 0.0010,
    "Avrupa": 0.0025,
    "Asya": 0.0015,
    "Dünya Geneli": 0.0020
}

# --- Streamlit UI ---

st.set_page_config(page_title="Müzik Gelir Hesaplama", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #0d1117;
        color: white;
    }
    .block-container {
        padding-top: 2rem;
    }
    .stButton > button {
        color: white;
        background: linear-gradient(90deg, #1db954, #191414);
        border: none;
        padding: 0.5em 1.2em;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🔍 Menü")
page = st.sidebar.radio("Gitmek istediğiniz bölümü seçin:", [
    "Spotify Sanatçı Hesapla",
    "Instagram & TikTok",
    "Manuel Spotify",
    "YouTube Topic",
    "Toplam Özet"
])

client_id = "3bcaf5a985fa491c8b573f9df6fe6e22"
client_secret = "1de40bfcf93d4bb28eec7ee6f2a660a6"

spotify_income = reels_income = tt_income = manual_income = yt_income = 0

if page == "Spotify Sanatçı Hesapla":
    st.title("🎵 Spotify Sanatçı Linki ile Otomatik Hesapla")
    spotify_url = st.text_input("Spotify Sanatçı Linki", placeholder="https://open.spotify.com/artist/...")
    region = st.selectbox("Dinleyici kitlesi bölgesi", list(region_rates.keys()))
    if st.button("Veriyi Çek ve Hesapla"):
        artist_id = extract_artist_id(spotify_url)
        if artist_id:
            with st.spinner("Veri çekiliyor..."):
                token = get_spotify_token(client_id, client_secret)
                artist_data = get_artist_data_from_api(artist_id, token)
                top_tracks = get_artist_top_tracks(artist_id, token)
                if artist_data and top_tracks:
                    followers = artist_data.get("followers", {}).get("total", 0)
                    estimated_total_streams = sum(estimate_streams_from_popularity(track.get("popularity", 0)) for track in top_tracks)
                    spotify_income = estimated_total_streams * region_rates[region]
                    st.metric("👥 Takipçi Sayısı", f"{followers:,}")
                    st.metric("🎶 Tahmini Stream", f"{estimated_total_streams:,}")
                    st.metric(f"💰 Tahmini Gelir ({region})", f"${spotify_income:,.2f}")
                else:
                    st.error("Spotify verisi alınamadı.")
        else:
            st.warning("Geçerli bir Spotify sanatçı linki girin.")

elif page == "Instagram & TikTok":
    st.title("📱 Reels & TikTok Şarkı Geliri")
    reels_views = st.number_input("Instagram Reels Görüntülenme", min_value=0)
    tt_views = st.number_input("TikTok Görüntülenme", min_value=0)
    reels_income = reels_views * 0.002
    tt_income = tt_views * 0.015
    st.metric("Instagram Geliri", f"${reels_income:,.2f}")
    st.metric("TikTok Geliri", f"${tt_income:,.2f}")

elif page == "Manuel Spotify":
    st.title("📝 Manuel Spotify Stream Hesaplama")
    manual_streams = st.number_input("Toplam Dinlenme", min_value=0)
    manual_region = st.selectbox("Bölge", list(region_rates.keys()), key="manual")
    manual_income = manual_streams * region_rates[manual_region]
    st.metric(f"{manual_region} için Gelir", f"${manual_income:,.2f}")

elif page == "YouTube Topic":
    st.title("▶️ YouTube Topic Şarkı Geliri")
    yt_views = st.number_input("YouTube Topic Görüntülenme", min_value=0)
    yt_income = yt_views * 0.00069
    st.metric("YouTube Topic Geliri", f"${yt_income:,.2f}")

elif page == "Toplam Özet":
    st.title("📊 Toplam Gelir Özeti")
    total_income = spotify_income + reels_income + tt_income + manual_income + yt_income
    st.success(f"🎧 Toplam Tahmini Gelir: ${total_income:,.2f} USD")
