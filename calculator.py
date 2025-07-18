import streamlit as st
from dotenv import load_dotenv
import os
import requests
import base64
from urllib.parse import urlparse
import pandas as pd
import json
import time
import io
import sys

# Sayfa ayarı
st.set_page_config(page_title="KXNEKIPASA", layout="wide")

# Ortam değişkenleri
load_dotenv()
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

# Sabit kur bilgileri (güncel değerler girilmeli)
usd_to_try = 40.17
eur_to_try = 43.20

# Döviz türü seçimi
currency_option = st.sidebar.selectbox("💱 Döviz Cinsi", ["USD", "EUR"])
exchange_rate = usd_to_try if currency_option == "USD" else eur_to_try
currency_symbol = "$" if currency_option == "USD" else "€"

# Spotify API Fonksiyonları
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

# Bölge bazlı stream başı gelir oranları (2025 güncel veriler)
region_rates = {
    "Amerika": 0.0040,
    "Türkiye": 0.0010,
    "Avrupa": 0.0039,
    "Asya": 0.0012,
    "Dünya Geneli": 0.00238
}

# Ek platform gelir oranları
yt_rate = 0.00069
reels_rate = 0.0002
tt_rate = 0.0007  # TikTok Rewards baz alındı

# Ana menü
menu = st.sidebar.selectbox("📊 Ana Menü", ["🎿 Hesaplama Sayfası", "💻 Kod Çalıştır"])

if menu == "🎿 Hesaplama Sayfası":

    if "menu" not in st.session_state:
        st.session_state.menu = "profil"

    st.markdown(f"<h1 style='text-align: center; color:#b266ff;'>Hoş geldin!</h1>", unsafe_allow_html=True)
    st.markdown("---")

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
                        total_estimated_streams = total_popularity * 1000
                        estimated_income = total_estimated_streams * region_rates[region]
                        estimated_income_try = estimated_income * exchange_rate

                        st.markdown(f"<h2 style='text-align: center;'>💰 Tahmini Gelir: {currency_symbol}{estimated_income:,.2f} ≈ ₺{estimated_income_try:,.2f} TL</h2>", unsafe_allow_html=True)
                        st.markdown("---")

                        st.subheader("🎷 En Popüler Şarkılar")
                        st.markdown("""
                        <div style='padding: 1rem; background-color: #828023; border-left: 5px solid #7e3ff2;'>
                            <strong>ℹ️ Bilgi:</strong> Her <strong>1 popülerlik puanı ≈ 1000 stream</strong> olarak varsayılmıştır.
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"<h4 style='color:#7e3ff2;'>📊 Tahmini Toplam Stream: {total_estimated_streams:,.0f}</h4>", unsafe_allow_html=True)

                        data = [{
                            "Şarkı": t["name"],
                            "Popülerlik": t["popularity"],
                            "Albüm": t["album"]["name"],
                            "Süre (dk)": round(t["duration_ms"] / 60000, 2),
                            "Tahmini Stream": f"{t['popularity'] * 1000:,}".replace(",", ".")
                        } for t in sorted(top_tracks, key=lambda x: x['popularity'], reverse=True)]

                        df = pd.DataFrame(data)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.error("Veri alınamadı.")
                else:
                    st.warning("Geçerli bir Spotify sanatçı linki girin.")

    elif selected == "stream":
        st.header("📝 Manuel Spotify Dinlenme ile Hesapla")

        raw_input = st.text_input("Toplam Dinlenme Sayısı (\u00f6rn: 100.000)", value="")
        manual_streams = 0
        valid_input = False

        if raw_input:
            try:
                manual_streams = int(raw_input.replace(".", "").replace(",", ""))
                valid_input = True
                st.markdown(f"**Girdiğiniz sayı:** `{manual_streams:,}`".replace(",", "."))
            except ValueError:
                st.warning("Lütfen sadece sayı girin (\u00f6rn: 100.000)")

        manual_region = st.selectbox("Bölge", list(region_rates.keys()), key="manual")

        if st.button("Hesapla") and valid_input:
            income = manual_streams * region_rates[manual_region]
            income_try = income * exchange_rate
            st.success(f"Tahmini gelir: {currency_symbol}{income:,.2f} ≈ ₺{income_try:,.2f} TL")

    elif selected == "youtube":
        st.header("▶️ YouTube Topic Görüntülenme ile Gelir")
        yt_views = st.number_input("YouTube Görüntülenme", min_value=0)
        if st.button("Hesapla"):
            yt_income = yt_views * yt_rate
            yt_income_try = yt_income * exchange_rate
            st.success(f"YouTube Topic geliri: {currency_symbol}{yt_income:,.2f} ≈ ₺{yt_income_try:,.2f} TL")

    elif selected == "sosyal":
        st.header("📱 Reels ve TikTok Görüntülenme ile Gelir")
        reels_views = st.number_input("Instagram Reels Görüntülenme", min_value=0)
        tt_views = st.number_input("TikTok Görüntülenme", min_value=0)
        if st.button("Hesapla"):
            reels_income = reels_views * reels_rate
            tt_income = tt_views * tt_rate
            total_income = reels_income + tt_income
            total_income_try = total_income * exchange_rate
            st.success(f"Toplam gelir: {currency_symbol}{total_income:,.2f} ≈ ₺{total_income_try:,.2f} TL")

elif menu == "💻 Kod Çalıştır":
    st.title("💻 Python Kodu Çalıştır")
    st.markdown("Python kodunu aşağıya yaz ve çalıştır butonuna bas.")
    code_input = st.text_area("Kodunuzu girin:", height=200)
    if st.button("Çalıştır"):
        output = io.StringIO()
        try:
            with st.spinner("Çalıştırılıyor..."):
                with io.StringIO() as buf, io.StringIO() as err_buf:
                    sys.stdout = buf
                    sys.stderr = err_buf
                    exec(code_input, {})
                    sys.stdout = sys.__stdout__
                    sys.stderr = sys.__stderr__
                    output_text = buf.getvalue()
                    error_text = err_buf.getvalue()
            if error_text:
                st.error(f"Hata:\n```\n{error_text}\n```")```")
            elif output_text:
                st.success("Kod çalıştırıldı:")
                st.code(output_text)
            else:
                st.info("Kod çalıştı ama çıktı üretmedi.")
        except Exception as e:
            st.error(f"Beklenmeyen Hata:\n```
{e}
```)
