# calculator.py

import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# 🧠 Spotify scraping fonksiyonu
def get_spotify_monthly_listeners(artist_url):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(artist_url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        text = soup.get_text()

        for line in text.split('\n'):
            if 'monthly listeners' in line:
                parts = line.strip().split(' ')
                for i, part in enumerate(parts):
                    if 'monthly' in part:
                        try:
                            listeners = parts[i-1].replace(',', '')
                            listeners = int(float(listeners) * 1000) if 'K' in listeners else \
                                        int(float(listeners) * 1_000_000) if 'M' in listeners else int(listeners)
                            driver.quit()
                            return listeners
                        except:
                            continue
        driver.quit()
    except Exception as e:
        return None

st.set_page_config(page_title="Müzik Gelir Hesaplayıcı", layout="centered")
st.title("🎧 Spotify & Sosyal Medya Gelir Hesaplayıcı")

st.header("1️⃣ Spotify Sanatçı Profil Linki ile Hesapla")

with st.expander("🎵 Spotify profil linkini gir, gelir otomatik hesaplansın"):
    spotify_link = st.text_input("Spotify Sanatçı Linki (örn: https://open.spotify.com/artist/...)")
    avg_streams_per_listener = st.slider("Kişi başı ortalama dinleme", 1, 20, 5)
    if st.button("🔍 Veriyi Çek ve Hesapla"):
        if spotify_link:
            listeners = get_spotify_monthly_listeners(spotify_link)
            if listeners:
                total_streams = listeners * avg_streams_per_listener
                income = total_streams * 0.003  # Ortalama kazanç
                st.success(f"Aylık dinleyici: **{listeners:,}**")
                st.success(f"Tahmini toplam stream: **{total_streams:,}**")
                st.success(f"Tahmini Spotify geliri: **${income:,.2f} USD**")
            else:
                st.error("Dinleyici sayısı çekilemedi. Linki kontrol et.")
        else:
            st.warning("Lütfen bir Spotify sanatçı linki girin.")

# 🌍 Ülke kazanç oranları
region_rates = {
    "Amerika": 0.0035,
    "Türkiye": 0.0010,
    "Avrupa": 0.0025,
    "Asya": 0.0015,
    "Dünya Geneli": 0.0020
}

st.header("2️⃣ Manuel Dinlenme ile Hesapla")

with st.expander("🎧 Dinlenme sayılarını manuel gir, ülkeye göre kazanç hesapla"):
    platform = st.selectbox("Platform Seçin", ["Spotify", "YouTube (Topic)"], key="manual")

    if platform == "Spotify":
        streams = st.number_input("Toplam Dinlenme", min_value=0)
        region = st.selectbox("Hedef Kitle Bölgesi", list(region_rates.keys()))
        rate = region_rates[region]
        income = streams * rate
        st.success(f"{region} için tahmini Spotify geliri: **${income:,.2f} USD**")

    elif platform == "YouTube (Topic)":
        views = st.number_input("Toplam Topic Video İzlenme", min_value=0)
        income = views * 0.002
        st.success(f"Tahmini YouTube Topic geliri: **${income:,.2f} USD**")
