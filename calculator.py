import streamlit as st
from dotenv import load_dotenv
import os
import requests
import base64
from urllib.parse import urlparse
import pandas as pd
import altair as alt

# --- .env yükle
load_dotenv()
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

# --- Sayfa Ayarları ---
st.set_page_config(page_title="KXNEKIPASA Calculator", layout="wide")
st.markdown("""
    <h1 style='text-align: center; color:#b266ff;'>KXNEKIPASA CALCULATOR</h1>
""", unsafe_allow_html=True)

# --- Menü Seçimi (session_state ile)
if "menu" not in st.session_state:
    st.session_state.menu = "profil"

# --- Buton Tasarımı (CSS) ---
st.markdown("""
<style>
div.stButton > button {
    background-color: white;
    color: #7e3ff2;
    border: 2px solid #7e3ff2;
    border-radius: 15px;
    padding: 0.75rem 1.5rem;
    font-weight: bold;
    transition: 0.3s ease;
    margin: 10px;
}
div.stButton > button:hover {
    background-color: #7e3ff2;
    color: white;
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

# --- Menü Butonları ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("PROFİL HESAPLAMA"):
        st.session_state.menu = "profil"

with col2:
    if st.button("STREAM HESAPLAMA"):
        st.session_state.menu = "stream"

with col3:
    if st.button("YOUTUBE HESAPLAMA"):
        st.session_state.menu = "youtube"

with col4:
    if st.button("INSTAGRAM VE TIKTOK HESAPLAMA"):
        st.session_state.menu = "sosyal"

selected = st.session_state.menu

# --- Bölgesel Kazanç Oranları ---
region_rates = {
    "Amerika": 0.0035,
    "Türkiye": 0.0010,
    "Avrupa": 0.0025,
    "Asya": 0.0015,
    "Dünya Geneli": 0.0020
}

# --- Yardımcı Fonksiyonlar ---
def extract_artist_id(spotify_url):
    try:
        path = urlparse(spotify_url).path
        return path.split("/")[-1]
    except:
        return None

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
    return r.json().get("access_token")

def get_artist_data_from_api(artist_id, token):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    return r.json() if r.status_code == 200 else None

def get_artist_top_tracks(artist_id, token):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=US"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    return r.json().get("tracks", []) if r.status_code == 200 else []

# --- Seçilen Menüye Göre İçerik ---
if selected == "profil":
    st.header("🎵 Spotify Sanatçı Linki ile Hesaplama")

    options = {
        "KXNEKIPASA": "https://open.spotify.com/intl-tr/artist/0pZpo1DFnOHkcSQB2NT1GA?si=oyWBZfU2QxSCqKFqgtQL1A",
        "Başka bir link gireceğim": ""
    }

    choice = st.selectbox("Sanatçı seçin veya özel link girin", options.keys())
    spotify_url = st.text_input("Spotify Sanatçı Linki", value=options[choice])
    region = st.selectbox("Dinleyici kitlesi bölgesi", list(region_rates.keys()))

    if st.button("💰 Hesapla"):
        artist_id = extract_artist_id(spotify_url)
        if artist_id:
            with st.spinner("Veri çekiliyor..."):
                token = get_spotify_token(client_id, client_secret)
                artist_data = get_artist_data_from_api(artist_id, token)
                top_tracks = get_artist_top_tracks(artist_id, token)

                if artist_data and top_tracks:
                    followers = artist_data.get("followers", {}).get("total", 0)
                    # Kazanç tahmini için sadece popülariteye dayalı kabaca toplam skor
                    total_popularity = sum([t.get("popularity", 0) for t in top_tracks])
                    estimated_income = total_popularity * 1000 * region_rates[region]  # pop score * 1K stream * rate

                    st.markdown("""
                    <h2 style='text-align: center;'>💰 Tahmini Gelir: ${:,.2f} USD</h2>
                    """.format(estimated_income), unsafe_allow_html=True)

                    st.markdown("---")
                    st.subheader("🎧 En Popüler Şarkılar (Popülerliğe Göre Sıralı)")
                    data = []
                    for t in sorted(top_tracks, key=lambda x: x['popularity'], reverse=True):
                        data.append({
                            "Şarkı": t["name"],
                            "Popülarite": t["popularity"],
                            "Albüm": t["album"]["name"],
                            "Süre (dk)": round(t["duration_ms"] / 60000, 2)
                        })
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.error("Veri alınamadı.")
        else:
            st.warning("Geçerli bir Spotify sanatçı linki girin.")

elif selected == "stream":
    st.header("📝 Manuel Spotify Dinlenme ile Hesapla")
    manual_streams = st.number_input("Toplam Dinlenme Sayısı", min_value=0)
    manual_region = st.selectbox("Bölge", list(region_rates.keys()), key="manual")
    manual_income = manual_streams * region_rates[manual_region]
    st.success(f"{manual_region} için tahmini gelir: ${manual_income:,.2f} USD")

elif selected == "youtube":
    st.header("▶️ YouTube Topic Görüntülenme ile Gelir")
    yt_views = st.number_input("YouTube Topic Görüntülenme", min_value=0)
    yt_income = yt_views * 0.00069
    st.success(f"YouTube Topic geliri: ${yt_income:,.2f} USD")

elif selected == "sosyal":
    st.header("📱 Reels ve TikTok Görüntülenme ile Gelir")
    reels_views = st.number_input("Instagram Reels Görüntülenme", min_value=0)
    reels_income = reels_views * 0.002
    st.success(f"Instagram Reels geliri: ${reels_income:,.2f} USD")

    tt_views = st.number_input("TikTok Görüntülenme", min_value=0)
    tt_income = tt_views * 0.015
    st.success(f"TikTok geliri: ${tt_income:,.2f} USD")

# --- Alt Bilgi ---
st.info("💡 Hesaplamalar tahmini verilere dayalıdır. Gerçek gelirler anlaşmalara ve platformlara göre değişebilir.")
