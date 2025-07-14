import streamlit as st
import os
import json
import requests
import base64
from urllib.parse import urlparse
from dotenv import load_dotenv
import pandas as pd
import time

# --- .env yükle
load_dotenv()
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
WEBHOOK_URL = "https://canary.discord.com/api/webhooks/1394242204628946974/6CZf6_OXWY5SLXPZZm3DWd3Y3XER3eHIiuzvCVBNcS44DfrbGYloC8-XH4VuKxhgfhgV"  # <-- Buraya webhook URL'ni koy

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

def send_to_webhook(event_type, username, email):
    data = {
        "content": f"🔔 **{event_type}**\n👤 Kullanıcı: `{username}`\n📧 E-posta: `{email}`"
    }
    try:
        requests.post(WEBHOOK_URL, json=data)
    except:
        pass  # Sessiz hata yönetimi

def register(username, email, password):
    users = load_users()
    if username in users:
        return False, "Bu kullanıcı adı zaten kayıtlı."
    users[username] = {"email": email, "password": password}
    save_users(users)
    send_to_webhook("Yeni Kayıt", username, email)
    return True, "Kayıt başarılı."

def login(username, password):
    users = load_users()
    if username in users and users[username]["password"] == password:
        send_to_webhook("Giriş Yapıldı", username, users[username]["email"])
        return True, users[username]
    return False, None

# --- Sayfa Ayarları ---
st.set_page_config(page_title="KXNEKIPASA Calculator", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- Giriş/Kayıt Ekranı ---
if not st.session_state.logged_in:
    st.title("🔐 KXNEKIPASA Giriş / Kayıt")
    auth_tab = st.radio("Seçim Yap", ["Giriş Yap", "Kayıt Ol"])

    if auth_tab == "Giriş Yap":
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap"):
            success, user_data = login(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.user = {"username": username, "email": user_data["email"]}
                st.success("Giriş başarılı!")
                st.experimental_rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı.")
    else:
        username = st.text_input("Kullanıcı Adı")
        email = st.text_input("E-posta")
        password = st.text_input("Şifre", type="password")
        if st.button("Kayıt Ol"):
            success, msg = register(username, email, password)
            if success:
                st.success(msg)
            else:
                st.warning(msg)

# --- Ana Uygulama ---
else:
    st.markdown(f"""
    <h1 style='text-align: center; color:#b266ff;'>KXNEKIPASA CALCULATOR</h1>
    <p style='text-align: center;'>👤 {st.session_state.user['username']} ({st.session_state.user['email']})</p>
    """, unsafe_allow_html=True)

    if st.button("🔓 Çıkış Yap"):
        st.session_state.logged_in = False
        st.experimental_rerun()

    # --- Menü Seçimi ---
    if "menu" not in st.session_state:
        st.session_state.menu = "profil"

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
        if st.button("INSTAGRAM VE TIKTOK HESAPLAMA"):
            st.session_state.menu = "sosyal"

    selected = st.session_state.menu

    region_rates = {
        "Amerika": 0.0035,
        "Türkiye": 0.0010,
        "Avrupa": 0.0025,
        "Asya": 0.0015,
        "Dünya Geneli": 0.0020
    }

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

    # --- PROFİL HESAPLAMA ---
    if selected == "profil":
        st.header("🎵 Spotify Sanatçı Linki ile Hesaplama")

        options = {
            "KXNEKIPASA": "https://open.spotify.com/intl-tr/artist/0pZpo1DFnOHkcSQB2NT1GA?si=oyWBZfU2QxSCqKFqgtQL1A",
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
                        st.subheader("🎧 En Popüler Şarkılar (Popülerliğe Göre Sıralı)")
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
            with st.spinner("Hesaplanıyor..."):
                time.sleep(0.5)
                manual_income = manual_streams * region_rates[manual_region]
                st.markdown(f"<h2 style='text-align: center;'>💰 Tahmini Gelir: ${manual_income:,.2f} USD</h2>", unsafe_allow_html=True)

    elif selected == "youtube":
        st.header("▶️ YouTube Topic Görüntülenme ile Gelir")
        yt_views = st.number_input("YouTube Topic Görüntülenme", min_value=0)

        if st.button("Hesapla"):
            with st.spinner("Hesaplanıyor..."):
                time.sleep(0.5)
                yt_income = yt_views * 0.00069
                st.markdown(f"<h2 style='text-align: center;'>💰 Tahmini Gelir: ${yt_income:,.2f} USD</h2>", unsafe_allow_html=True)

    elif selected == "sosyal":
        st.header("📱 Reels ve TikTok Görüntülenme ile Gelir")
        reels_views = st.number_input("Instagram Reels Görüntülenme", min_value=0)
        tt_views = st.number_input("TikTok Görüntülenme", min_value=0)

        if st.button("Hesapla"):
            with st.spinner("Hesaplanıyor..."):
                time.sleep(0.5)
                reels_income = reels_views * 0.002
                tt_income = tt_views * 0.015
                total_income = reels_income + tt_income
                st.markdown(f"<h2 style='text-align: center;'>💰 Tahmini Gelir: ${total_income:,.2f} USD</h2>", unsafe_allow_html=True)

    st.info("💡 Hesaplamalar tahmini verilere dayalıdır. Gerçek gelirler anlaşmalara ve platformlara göre değişebilir.")
