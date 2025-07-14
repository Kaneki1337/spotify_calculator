# calculator.py

import streamlit as st

st.set_page_config(page_title="Spotify Calculator", layout="centered")
st.title("🎧 Porno Seks Goruntule")

st.markdown("Manuel giriş yaparak Spotify, YouTube Topic, Instagram ve TikTok için tahmini gelir hesaplayabilirsiniz.")

st.header("1️⃣ Profil Bilgisi ile Hesaplama")

with st.expander("Sanatçı profili üzerinden tahmini gelir hesapla (manuel)"):
    platform = st.selectbox("Platform Seçin", ["Spotify", "YouTube (Topic)", "Instagram", "TikTok"])

    if platform == "Spotify":
        monthly_listeners = st.number_input("Aylık Dinleyici Sayısı", min_value=0)
        avg_streams_per_listener = st.slider("Kişi başı ortalama dinleme", 1, 20, 5)
        total_streams = monthly_listeners * avg_streams_per_listener
        spotify_income = total_streams * 0.003  # 0.003 USD per stream
        st.success(f"Tahmini Spotify gelir: **${spotify_income:,.2f} USD**")

    elif platform == "YouTube (Topic)":
        subs = st.number_input("Abone Sayısı", min_value=0)
        avg_views = st.number_input("Ortalama Video İzlenme", min_value=0)
        topic_income = avg_views * 0.002
        st.success(f"Tahmini YouTube Topic geliri: **${topic_income:,.2f} USD**")

    elif platform == "Instagram":
        followers = st.number_input("Takipçi Sayısı", min_value=0)
        engagement = st.slider("Etkileşim Oranı (%)", 0.0, 20.0, 3.0)
        insta_income = followers * (engagement / 100) * 0.02
        st.success(f"Tahmini Instagram geliri: **${insta_income:,.2f} USD**")

    elif platform == "TikTok":
        followers = st.number_input("Takipçi Sayısı", min_value=0)
        avg_views = st.number_input("Ortalama Video İzlenme", min_value=0)
        tiktok_income = avg_views * 0.015
        st.success(f"Tahmini TikTok geliri: **${tiktok_income:,.2f} USD**")

st.header("2️⃣ Doğrudan Veri Girişi ile Hesaplama")

with st.expander("Dinlenme / Görüntülenme sayısı girerek hesapla"):
    platform2 = st.selectbox("Platform Seçin", ["Spotify", "YouTube (Topic)", "Instagram", "TikTok"], key="manual")

    if platform2 == "Spotify":
        streams = st.number_input("Toplam Dinlenme", min_value=0, key="spotify_streams")
        income = streams * 0.003
        st.success(f"Tahmini Spotify geliri: **${income:,.2f} USD**")

    elif platform2 == "YouTube (Topic)":
        views = st.number_input("Toplam Topic Video İzlenme", min_value=0, key="yt_views")
        income = views * 0.002
        st.success(f"Tahmini YouTube Topic geliri: **${income:,.2f} USD**")

    elif platform2 == "Instagram":
        followers = st.number_input("Takipçi Sayısı", min_value=0, key="ig_followers")
        engagement = st.slider("Etkileşim Oranı (%)", min_value=0.0, max_value=20.0, value=3.0, key="ig_engage")
        income = followers * (engagement / 100) * 0.02
        st.success(f"Tahmini Instagram geliri: **${income:,.2f} USD**")

    elif platform2 == "TikTok":
        followers = st.number_input("Takipçi Sayısı", min_value=0, key="tt_followers")
        avg_views = st.number_input("Ortalama Görüntülenme", min_value=0, key="tt_views")
        income = avg_views * 0.015
        st.success(f"Tahmini TikTok geliri: **${income:,.2f} USD**")
