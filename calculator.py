import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Spotify calculator", layout="centered")

st.title("🎧 Spotify Calculator")

st.markdown("""
Bu panelde Spotify ve YouTube gelirlerinizi tahmini olarak hesaplayabilirsiniz.
Ülke bazlı dinlenme sayısı girerek Spotify gelirini, toplam izlenmeyle de YouTube gelirini öğrenebilirsiniz.
""")

st.divider()

st.header("Spotify Dinlenme Verileri")
ulke_listesi = ["USA", "UK", "Germany", "Turkey", "India", "Other"]
oranlar = {
    "USA": 0.004,
    "UK": 0.0045,
    "Germany": 0.004,
    "Turkey": 0.0012,
    "India": 0.0008,
    "Other": 0.003
}

col1, col2 = st.columns(2)
dinlenmeler = {}

with col1:
    for ulke in ulke_listesi[:len(ulke_listesi)//2]:
        sayi = st.number_input(f"{ulke} dinlenme sayısı", min_value=0, step=1000, key=ulke)
        dinlenmeler[ulke] = sayi

with col2:
    for ulke in ulke_listesi[len(ulke_listesi)//2:]:
        sayi = st.number_input(f"{ulke} dinlenme sayısı", min_value=0, step=1000, key=ulke)
        dinlenmeler[ulke] = sayi

spotify_gelir = sum(dinlenmeler[ulke] * oranlar.get(ulke, 0.003) for ulke in dinlenmeler)

# --- YouTube Bölümü ---
st.header("YouTube İzlenme Verisi")
yt_izlenme = st.number_input("Toplam izlenme sayısı", min_value=0, step=1000)
yt_oran = st.number_input("1 izlenmeden kazanılan gelir ($)", min_value=0.0, value=0.0015, step=0.0001)
youtube_gelir = yt_izlenme * yt_oran

# --- Sonuç ---
st.divider()
st.subheader("💰 Tahmini Gelir Sonuçları")
st.metric("Spotify Geliri", f"${spotify_gelir:,.2f}")
st.metric("YouTube Geliri", f"${youtube_gelir:,.2f}")
st.success(f"Toplam Tahmini Gelir: ${spotify_gelir + youtube_gelir:,.2f}")

# --- Grafik ---
if spotify_gelir > 0:
    st.subheader("📊 Ülke Bazlı Spotify Gelir Dağılımı")
    df = pd.DataFrame({
        "Ülke": list(dinlenmeler.keys()),
        "Gelir ($)": [dinlenmeler[u] * oranlar.get(u, 0.003) for u in dinlenmeler]
    })
    fig, ax = plt.subplots()
    ax.bar(df["Ülke"], df["Gelir ($)"], color="skyblue")
    ax.set_ylabel("Gelir ($)")
    ax.set_title("Spotify Geliri Ülkelere Göre")
    st.pyplot(fig)

# --- İpucu ---
st.info("Sanatçı profiline özel hale getirmek için bu sayfayı paylaşabilir ya da verileri önceden girip ekran görüntüsü alabilirsin.")
