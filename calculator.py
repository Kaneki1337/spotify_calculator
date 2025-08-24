import streamlit as st
import pandas as pd
import io

# Sayfa ayarı
st.set_page_config(page_title="Gelir Hesaplayıcı", layout="wide")

# Sabit kur bilgileri
usd_to_try = 40.17
eur_to_try = 43.20

# Döviz seçimi
currency_option = st.sidebar.selectbox("💱 Döviz Cinsi", ["USD", "EUR"])
exchange_rate = usd_to_try if currency_option == "USD" else eur_to_try
currency_symbol = "$" if currency_option == "USD" else "€"

# Gelir oranları
region_rates = {
    "Amerika": 0.0040,
    "Türkiye": 0.0010,
    "Avrupa": 0.0039,
    "Asya": 0.0012,
    "Dünya Geneli": 0.00238
}
yt_rate = 0.00069
reels_rate = 0.0002
tt_rate = 0.0007

# Başlık
st.markdown("<h1 style='text-align:center; color:#7e3ff2;'>🎵 Çoklu Platform Gelir Hesaplayıcı</h1>", unsafe_allow_html=True)
st.markdown("---")

# Spotify Hesaplama
st.subheader("🎧 Spotify Hesaplama")
col1, col2 = st.columns(2)

with col1:
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

with col2:
    selected_regions = st.multiselect(
        "Dinleyici Bölgeleri",
        list(region_rates.keys()),
        default=["Amerika", "Avrupa"]
    )

if valid_input and selected_regions:
    gelir_list = []
    pay = 1 / len(selected_regions)  # Seçilen bölgeler eşit bölüşülüyor
    for region in selected_regions:
        gelir = streams * pay * region_rates[region]
        gelir_list.append([region, f"{pay*100:.0f}%", gelir])

    df = pd.DataFrame(gelir_list, columns=["Bölge", "Pay", "Gelir ($)"])
    total_income = df["Gelir ($)"].sum()
    total_income_try = total_income * exchange_rate

    col_a, col_b = st.columns(2)
    col_a.metric("Spotify Geliri", f"{currency_symbol}{total_income:,.2f}")
    col_b.metric("TL Karşılığı", f"₺{total_income_try:,.2f}")

    st.dataframe(df, use_container_width=True)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Spotify", index=False)
    st.download_button("📥 Spotify Excel indir", data=buffer.getvalue(), file_name="spotify_geliri.xlsx")

st.markdown("---")

# YouTube Hesaplama
st.subheader("▶️ YouTube Hesaplama")
yt_views = st.number_input("YouTube Görüntülenme", min_value=0, value=0)
if yt_views > 0:
    yt_income = yt_views * yt_rate
    yt_income_try = yt_income * exchange_rate
    col1, col2 = st.columns(2)
    col1.metric("YouTube Geliri", f"{currency_symbol}{yt_income:,.2f}")
    col2.metric("TL Karşılığı", f"₺{yt_income_try:,.2f}")

st.markdown("---")

# Sosyal Medya Hesaplama
st.subheader("📱 Instagram & TikTok Hesaplama")
col1, col2 = st.columns(2)
reels_views = col1.number_input("Instagram Reels Görüntülenme", min_value=0, value=0)
tt_views = col2.number_input("TikTok Görüntülenme", min_value=0, value=0)

if reels_views > 0 or tt_views > 0:
    reels_income = reels_views * reels_rate
    tt_income = tt_views * tt_rate
    total_income = reels_income + tt_income
    total_income_try = total_income * exchange_rate
    col1.metric("Sosyal Medya Geliri", f"{currency_symbol}{total_income:,.2f}")
    col2.metric("TL Karşılığı", f"₺{total_income_try:,.2f}")

st.markdown("---")

# Genel Özet
st.subheader("📊 Genel Özet")
summary_data = {
    "Platform": ["Spotify", "YouTube", "Instagram Reels", "TikTok"],
    "Gelir Oranı ($)": [0.00238, yt_rate, reels_rate, tt_rate]
}
summary_df = pd.DataFrame(summary_data)
st.dataframe(summary_df, use_container_width=True)
