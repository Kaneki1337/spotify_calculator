# calculator.py
from dotenv import load_dotenv
import os

load_dotenv()

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

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
st.set_page_config(page_title="Müzik Gelir Hesaplama", layout="centered")
st.title("\U0001F3A7 Spotify & Sosyal Medya Gelir Hesaplayıcı")

# --- 1. Spotify Sanatçı Profili ile Otomatik Hesaplama ---
st.header("1️⃣ Spotify Sanatçı Linki ile Otomatik Hesapla")

with st.expander("🎵 Spotify sanatçı linkini girerek gelir hesapla"):
    client_id = "3bcaf5a985fa491c8b573f9df6fe6e22"
    client_secret = "1de40bfcf93d4bb28eec7ee6f2a660a6"

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

                    estimated_total_streams = 0
                    for track in top_tracks:
                        popularity = track.get("popularity", 0)
                        estimated_streams = estimate_streams_from_popularity(popularity)
                        estimated_total_streams += estimated_streams

                    income = estimated_total_streams * region_rates[region]
                    st.success(f"Spotify takipçi sayısı: {followers:,}")
                    st.success(f"En popüler 10 şarkıya göre tahmini toplam stream: {estimated_total_streams:,}")
                    st.success(f"{region} için tahmini gelir: ${income:,.2f} USD")
                else:
                    st.error("Spotify verisi alınamadı. Artist ID veya token hatalı olabilir.")
        else:
            st.warning("Geçerli bir Spotify sanatçı linki girin.")

# --- 2. Reels & TikTok Geliri ---
st.header("2️⃣ Instagram Reels ve TikTok Şarkı Geliri")

with st.expander("📱 Reels & TikTok görüntülenme ile gelir hesapla"):
    reels_views = st.number_input("Instagram Reels Görüntülenme", min_value=0)
    reels_income = reels_views * 0.002
    st.success(f"Instagram Reels şarkı geliri: ${reels_income:,.2f} USD")

    tt_views = st.number_input("TikTok Video Görüntülenme", min_value=0)
    tt_income = tt_views * 0.015
    st.success(f"TikTok şarkı geliri: ${tt_income:,.2f} USD")

# --- 3. Manuel Spotify Dinlenme Hesabı ---
st.header("3️⃣ Manuel Spotify Dinlenme ile Hesapla")

with st.expander("📝 Manuel stream girerek hesapla"):
    manual_streams = st.number_input("Toplam Dinlenme Sayısı", min_value=0)
    manual_region = st.selectbox("Bölge", list(region_rates.keys()), key="manual")
    manual_income = manual_streams * region_rates[manual_region]
    st.success(f"{manual_region} için tahmini gelir: ${manual_income:,.2f} USD")

# --- 4. YouTube Topic Şarkı Geliri ---
st.header("4️⃣ YouTube Topic Geliri")

with st.expander("▶️ YouTube Topic görüntülenme ile gelir hesapla"):
    yt_views = st.number_input("YouTube Topic Görüntülenme", min_value=0)
    yt_income = yt_views * 0.00069  # Ortalama YouTube Music gelir oranı
    st.success(f"YouTube Topic şarkı geliri: ${yt_income:,.2f} USD")
