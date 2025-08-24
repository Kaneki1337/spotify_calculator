import streamlit as st
import pandas as pd
import io

# Sayfa ayarı
st.set_page_config(page_title="Gelir Hesaplayıcı", layout="wide")

# Sabit kur bilgileri (manuel güncellenmeli)
usd_to_try = 40.17
eur_to_try = 43.20

# Döviz seçimi
currency_option = st.sidebar.selectbox("💱 Döviz Cinsi", ["USD", "EUR"])
exchange_rate = usd_to_try if currency_option == "USD" else eur_to_try
currency_symbol = "$" if currency_option == "USD" else "€"

# Bölge bazlı stream başı gelir oranları (2025 tahmini değerler)
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
tt_rate = 0.0007

# Menü
menu = st.sidebar.selectbox("📊 Menü", ["🎵 Spotify Hesaplama", "▶️ YouTube Hesaplama", "📱 Sosyal Medya Hesaplama"])

if menu == "🎵 Spotify Hesaplama":
    st.header("🎵 Spotify Dinlenme ile Gelir Hesapla")

    # Manuel stream girişi
    raw_input = st.text_input("Toplam Spotify Dinlenme Sayısı (örn: 1.000.000)", value="")
    streams = 0
    valid_input = False

    if raw_input:
        try:
            streams = int(raw_input.replace(".", "").replace(",", ""))
            valid_input = True
            st.markdown(f"**Girdiğiniz sayı:** `{streams:,}`".replace(",", "."))
        except ValueError:
            st.warning("Lütfen sadece sayı girin (örn: 1.000.000)")

    # Bölge yüzdeli dağılım
    st.subheader("🌍 Dinleyici Bölge Dağılımı (%)")
    col1, col2, col3, col4 = st.columns(4)
    amerika = col1.number_input("Amerika %", min_value=0, max_value=100, value=40)
    turkiye = col2.number_input("Türkiye %", min_value=0, max_value=100, value=20)
    avrupa = col3.number_input("Avrupa %", min_value=0, max_value=100, value=30)
    asya = col4.number_input("Asya %", min_value=0, max_value=100, value=10)

    toplam_yuzde = amerika + turkiye + avrupa + asya
    if toplam_yuzde != 100:
        st.warning("Bölge yüzdelerinin toplamı 100 olmalı!")

    if st.button("Hesapla") and valid_input and toplam_yuzde == 100:
        # Bölgesel gelir hesabı
        gelir_amer = streams * (amerika/100) * region_rates["Amerika"]
        gelir_tr   = streams * (turkiye/100) * region_rates["Türkiye"]
        gelir_eur  = streams * (avrupa/100) * region_rates["Avrupa"]
        gelir_asya = streams * (asya/100) * region_rates["Asya"]

        total_income = gelir_amer + gelir_tr + gelir_eur + gelir_asya
        total_income_try = total_income * exchange_rate

        # Özet kutucuklar
        col_a, col_b = st.columns(2)
        col_a.metric("Toplam Gelir", f"{currency_symbol}{total_income:,.2f}")
        col_b.metric("TL Karşılığı", f"₺{total_income_try:,.2f}")

        # Detaylı tablo
        data = {
            "Bölge": ["Amerika", "Türkiye", "Avrupa", "Asya"],
            "Yüzde": [amerika, turkiye, avrupa, asya],
            "Gelir ($)": [gelir_amer, gelir_tr, gelir_eur, gelir_asya]
        }
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

        # Excel çıktısı
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Gelir Hesabı", index=False)
        st.download_button("📥 Excel indir", data=buffer.getvalue(), file_name="gelir_hesabi.xlsx")

elif menu == "▶️ YouTube Hesaplama":
    st.header("▶️ YouTube Görüntülenme ile Gelir")
    yt_views = st.number_input("YouTube Görüntülenme", min_value=0)
    if st.button("Hesapla"):
        yt_income = yt_views * yt_rate
        yt_income_try = yt_income * exchange_rate
        st.success(f"YouTube Topic geliri: {currency_symbol}{yt_income:,.2f} ≈ ₺{yt_income_try:,.2f} TL")

elif menu == "📱 Sosyal Medya Hesaplama":
    st.header("📱 Reels ve TikTok Görüntülenme ile Gelir")
    reels_views = st.number_input("Instagram Reels Görüntülenme", min_value=0)
    tt_views = st.number_input("TikTok Görüntülenme", min_value=0)
    if st.button("Hesapla"):
        reels_income = reels_views * reels_rate
        tt_income = tt_views * tt_rate
        total_income = reels_income + tt_income
        total_income_try = total_income * exchange_rate
        st.success(f"Toplam gelir: {currency_symbol}{total_income:,.2f} ≈ ₺{total_income_try:,.2f} TL")
