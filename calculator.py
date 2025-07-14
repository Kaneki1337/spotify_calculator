# calculator.py

import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Spotify dinleyici çekme fonksiyonu
def get_spotify_monthly_listeners(artist_url):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        driver.get(artist_url)
        wait = WebDriverWait(driver, 10)

        # Spotify'daki dinleyici sayısı bilgisi
        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="monthly-listeners"]')))
        text = element.text  # Örn: "20,518 monthly listeners"
        driver.quit()

        listeners = text.split(" ")[0].replace(",", "")
        return int(listeners)
    except Exception:
        return None


# Kazanç katsayıları (ülkeye göre)
region_rates = {
    "Amerika": 0.0035,
    "Türkiye": 0.0010,
    "Avrupa": 0.0025,
    "Asya": 0.0015,
    "Dünya Geneli": 0.0020
}


# --- Streamlit UI ---
st.set_page_config(page_title="🎵 Müzik ve Sosyal Medya Gelir Hesaplama", layout="centered")
st.title("🎧 Spotify & Sosyal Medya Gelir Hesaplayıcı")


# --- 1. Otomatik Spotify Profil Hesaplama ---
st.header("1️⃣ Spotify Profil Linki ile Otomatik Hesapla")

with st.expander("🔗 Sanatçı profil linkini girerek gelir hesapla"):
    spotify_link = st.text_input("🎵 Spotify Sanatçı Linki", placeholder="https://open.spotify.com/artist/...")
    avg_streams_per_listener = st.slider("Kişi başı ortalama dinlenme sayısı", 1, 20, 5)
    
    if st.button("🔍 Spotify Verilerini Çek ve Hesapla"):
        if spotify_link:
            with st.spinner("Veri çekiliyor..."):
                listeners = get_spotify_monthly_listeners(spotify_link)
                if listeners:
                    total_streams = listeners * avg_streams_per_listener
                    income = total_streams * 0.003  # ortalama değer
                    st.success(f"🧑‍🎤 Aylık dinleyici: **{listeners:,}**")
                    st.success(f"📊 Tahmini toplam stream: **{total_streams:,}**")
                    st.success(f"💰 Tahmini Spotify geliri: **${income:,.2f} USD**")
                else:
                    st.error("❌ Dinleyici bilgisi alınamadı. Link doğru mu?")
        else:
            st.warning("⚠️ Lütfen bir Spotify sanatçı linki girin.")


# --- 2. Manuel Spotify Hesaplama + Ülke Seçimi ---
st.header("2️⃣ Manuel Spotify Dinlenme ile Hesapla")

with st.expander("🎧 Dinlenme sayılarını ve ülkeyi seçerek gelir hesapla"):
    platform = st.selectbox("Platform Seçin", ["Spotify", "YouTube (Topic)"])
    
    if platform == "Spotify":
        streams = st.number_input("Toplam Dinlenme Sayısı", min_value=0, value=0)
        region = st.selectbox("Hedef Kitle Bölgesi", list(region_rates.keys()))
        rate = region_rates[region]
        income = streams * rate
        st.success(f"📍 {region} için Spotify geliri: **${income:,.2f} USD**")

    elif platform == "YouTube (Topic)":
        views = st.number_input("Topic Video Görüntülenme", min_value=0, value=0)
        income = views * 0.002
        st.success(f"▶️ Tahmini YouTube Topic geliri: **${income:,.2f} USD**")


# --- 3. Sosyal Medya Geliri (Instagram & TikTok) ---
st.header("3️⃣ Sosyal Medya Geliri (TikTok & Instagram)")

with st.expander("📱 Takipçi ve etkileşim bilgilerine göre gelir tahmini"):
    social = st.selectbox("Sosyal Platform Seçin", ["Instagram", "TikTok"])
    
    if social == "Instagram":
        followers = st.number_input("📸 Takipçi Sayısı", min_value=0)
        engagement = st.slider("💬 Etkileşim Oranı (%)", 0.0, 20.0, 3.0)
        income = followers * (engagement / 100) * 0.02
        st.success(f"💰 Instagram geliri: **${income:,.2f} USD**")

    elif social == "TikTok":
        followers = st.number_input("🎥 Takipçi Sayısı", min_value=0)
        avg_views = st.number_input("📊 Ortalama Görüntülenme", min_value=0)
        income = avg_views * 0.015
        st.success(f"💰 TikTok geliri: **${income:,.2f} USD**")
