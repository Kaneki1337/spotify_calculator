# calculator.py

import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

def get_spotify_monthly_listeners(artist_url):
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(artist_url)
        wait = WebDriverWait(driver, 10)

        # Beklenen CSS class'ı
        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="monthly-listeners"]')))
        text = element.text  # Örn: "20,518 monthly listeners"
        driver.quit()

        listeners = text.split(" ")[0].replace(",", "")
        return int(listeners)
    except Exception as e:
        return None

st.header("3️⃣ Sosyal Medya Gelir Hesaplayıcı")

with st.expander("📱 Instagram ve TikTok gelirini hesapla"):
    social = st.selectbox("Platform Seçin", ["Instagram", "TikTok"])

    if social == "Instagram":
        followers = st.number_input("Takipçi Sayısı", min_value=0, key="ig_followers")
        engagement = st.slider("Etkileşim Oranı (%)", 0.0, 20.0, 3.0, key="ig_engage")
        income = followers * (engagement / 100) * 0.02
        st.success(f"Tahmini Instagram geliri: **${income:,.2f} USD**")

    elif social == "TikTok":
        followers = st.number_input("Takipçi Sayısı", min_value=0, key="tt_followers")
        avg_views = st.number_input("Ortalama Görüntülenme", min_value=0, key="tt_views")
        income = avg_views * 0.015
        st.success(f"Tahmini TikTok geliri: **${income:,.2f} USD**")

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
