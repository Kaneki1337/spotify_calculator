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

# Sayfa ayari
st.set_page_config(page_title="KXNEKIPASA", layout="wide")

# Ortam degiskenleri
load_dotenv()
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

# Spotify API Fonksiyonlari
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

# Menu secenekleri
menu = st.sidebar.selectbox("\ud83d\udcca Ana Menu", ["\ud83c\udfb7 Hesaplama Sayfasi", "\ud83d\udcbb Kod Calistir"])

if menu == "\ud83c\udfb7 Hesaplama Sayfasi":

    if "menu" not in st.session_state:
        st.session_state.menu = "profil"

    st.markdown(f"<h1 style='text-align: center; color:#b266ff;'>Hos geldin!</h1>", unsafe_allow_html=True)
    st.markdown("---")

    region_rates = {
        "Amerika": 0.0035,
        "Turkiye": 0.0010,
        "Avrupa": 0.0025,
        "Asya": 0.0015,
        "Dunya Geneli": 0.0020
    }

    exchange_rate = st.number_input("\ud83d\udcb1 Dolar/TL kuru", value=33.00, step=0.1, format="%.2f")

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
        if st.button("PROFIL HESAPLAMA"):
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
        st.header("\ud83c\udfb5 Spotify Sanatci Linki ile Hesaplama")
        options = {
            "KXNEKIPASA": "https://open.spotify.com/intl-tr/artist/0pZpo1DFnOHkcSQB2NT1GA",
            "Baska bir link girecegim": ""
        }
        choice = st.selectbox("Sanatci secin veya ozel link girin", options.keys())
        spotify_url = st.text_input("Spotify Sanatci Linki", value=options[choice])
        region = st.selectbox("Dinleyici kitlesi bolgesi", list(region_rates.keys()))

        if st.button("Hesapla"):
            with st.spinner("Veri cekiliyor..."):
                time.sleep(0.5)
                artist_id = extract_artist_id(spotify_url)
                if artist_id:
                    token = get_spotify_token(client_id, client_secret)
                    artist_data = get_artist_data_from_api(artist_id, token)
                    top_tracks = get_artist_top_tracks(artist_id, token)

                    if artist_data and top_tracks:
                        total_popularity = sum([t.get("popularity", 0) for t in top_tracks])
                        estimated_income = total_popularity * 1000 * region_rates[region]
                        total_estimated_streams = total_popularity * 1000

                        st.markdown(f"<h2 style='text-align: center;'>\ud83d\udcb0 Tahmini Gelir: ${estimated_income:,.2f} USD (~{estimated_income * exchange_rate:,.2f} TL)</h2>", unsafe_allow_html=True)
                        st.markdown("---")

                        st.subheader("\ud83c\udfb7 En Populer Sarkilar")

                        st.markdown("""
                        <div style='padding: 1rem; background-color: #828023; border-left: 5px solid #7e3ff2;'>
                            <strong>\u2139\ufe0f Bilgi:</strong> Her <strong>1 populerlik puani \u2248 1000 stream</strong> olarak varsayilmistir.
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                        <h4 style='color:#7e3ff2;'>\ud83d\udcca Tahmini Toplam Stream: {total_estimated_streams:,.0f}</h4>
                        """, unsafe_allow_html=True)

                        data = [{
                            "Sarki": t["name"],
                            "Populerlik": t["popularity"],
                            "Album": t["album"]["name"],
                            "Sure (dk)": round(t["duration_ms"] / 60000, 2),
                            "Tahmini Stream": f"{t['popularity'] * 1000:,}".replace(",", ".")
                        } for t in sorted(top_tracks, key=lambda x: x['popularity'], reverse=True)]

                        df = pd.DataFrame(data)
                        st.dataframe(df, use_container_width=True)

                    else:
                        st.error("Veri alinamadi.")
                else:
                    st.warning("Gecerli bir Spotify sanatci linki girin.")

    elif selected == "stream":
        st.header("\ud83d\udcdd Manuel Spotify Dinlenme ile Hesapla")
        raw_input = st.text_input("Toplam Dinlenme Sayisi (orn: 100.000)", value="")
        manual_streams = 0
        valid_input = False

        if raw_input:
            try:
                manual_streams = int(raw_input.replace(".", "").replace(",", ""))
                valid_input = True
                st.markdown(f"**Girdiginiz sayi:** `{manual_streams:,}`".replace(",", "."))
            except ValueError:
                st.warning("Lutfen sadece sayi girin (orn: 100.000)")

        manual_region = st.selectbox("Bolge", list(region_rates.keys()), key="manual")

        if st.button("Hesapla") and valid_input:
            income = manual_streams * region_rates[manual_region]
            st.success(f"Tahmini gelir: ${income:,.2f} USD (~{income * exchange_rate:,.2f} TL)")

    elif selected == "youtube":
        st.header("\u25b6\ufe0f YouTube Topic Goruntulenme ile Gelir")
        yt_views = st.number_input("YouTube Goruntulenme", min_value=0)
        if st.button("Hesapla"):
            yt_income = yt_views * 0.00069
            st.success(f"YouTube Topic geliri: ${yt_income:,.2f} USD (~{yt_income * exchange_rate:,.2f} TL)")

    elif selected == "sosyal":
        st.header("\ud83d\udcf1 Reels ve TikTok Goruntulenme ile Gelir")
        reels_views = st.number_input("Instagram Reels Goruntulenme", min_value=0)
        tt_views = st.number_input("TikTok Goruntulenme", min_value=0)
        if st.button("Hesapla"):
            reels_income = reels_views * 0.002
            tt_income = tt_views * 0.015
            total_income = reels_income + tt_income
            st.success(f"Toplam gelir: ${total_income:,.2f} USD (~{total_income * exchange_rate:,.2f} TL)")

elif menu == "\ud83d\udcbb Kod Calistir":
    st.title("\ud83d\udcbb Python Kodu Calistir")
    st.markdown("Python kodunu asagiya yaz ve calistir butonuna bas.")
    code_input = st.text_area("Kodunuzu girin:", height=200)

    if st.button("Calistir"):
        output = io.StringIO()
        try:
            with st.spinner("Calistiriliyor..."):
                with io.StringIO() as buf, io.StringIO() as err_buf:
                    sys.stdout = buf
                    sys.stderr = err_buf
                    exec(code_input, {})
                    sys.stdout = sys.__stdout__
                    sys.stderr = sys.__stderr__
                    output_text = buf.getvalue()
                    error_text = err_buf.getvalue()
            if error_text:
                st.error(f"Hata:\n```\n{error_text}\n```")
            elif output_text:
                st.success("Kod calistirildi:")
                st.code(output_text)
            else:
                st.info("Kod calisti ama cikti uretmedi.")
        except Exception as e:
            st.error(f"Beklenmeyen Hata:\n```\n{e}\n```)
