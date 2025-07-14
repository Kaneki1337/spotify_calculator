# calculator.py

import streamlit as st
import requests
from bs4 import BeautifulSoup

# Spotify artist ID ayıklama

def extract_artist_id(spotify_url):
    try:
        return spotify_url.split("/")[-1].split("?")[0]
    except:
        return None

# SpotOnTrack scraping fonksiyonu

def get_spotify_listeners_spotontrack(artist_id):
    try:
        url = f"https://www.spotontrack.com/artist/{artist_id}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        element = soup.find("div", class_="artist__monthly_listeners")

        if element:
            text = element.get_text(strip=True).replace(",", "").replace(" listeners", "")
            return int(text)
        else:
            return None
    except:
        return None

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
    spotify_url = st.text_input("Spotify Sanatçı Linki", placeholder="https://open.spotify.com/artist/...")
    avg_streams_per_listener = st.slider("Kişi başı ortalama dinlenme", 1, 20, 5)
    region = st.selectbox("Dinleyici kitlesi bölgesi", list(region_rates.keys()))

    if st.button("Veriyi Çek ve Hesapla"):
        artist_id = extract_artist_id(spotify_url)
        if artist_id:
            with st.spinner("Veri çekiliyor..."):
                listeners = get_spotify_listeners_spotontrack(artist_id)
                if listeners:
                    total_streams = listeners * avg_streams_per_listener
                    income = total_streams * region_rates[region]
                    st.success(f"Aylık dinleyici: {listeners:,}")
                    st.success(f"Toplam stream tahmini: {total_streams:,}")
                    st.success(f"{region} için tahmini gelir: ${income:,.2f} USD")
                else:
                    st.error("Dinleyici bilgisi alınamadı. Sanatçı SpotOnTrack'te olmayabilir.")
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
