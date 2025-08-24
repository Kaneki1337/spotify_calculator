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

# 🎧 Spotify Hesaplama
st.subheader("🎧 Spotify Hesaplama")

col1, col2 = st.columns(2)

with col1:
    raw_input = st.text_input("Toplam Spotify Dinlenme Sayısı (örn: 1.000.000)", value="")

with col2:
    selected_regions = st.multiselect(
        "Dinleyici Bölgeleri",
        list(region_rates.keys()),
        default=["Amerika", "Türkiye"]
    )

if st.button("Spotify Gelirini Hesapla"):
    try:
        streams = int(raw_input.replace(".", "").replace(",", ""))
        if streams <= 0:
            st.warning("Lütfen pozitif bir stream sayısı girin.")
        elif not selected_regions:
            st.warning("En az bir bölge seçmelisiniz.")
        else:
            # Her ülke için ayrı gelir hesabı
            results = []
            for region in selected_regions:
                income = streams * region_rates[region]
                income_try = income * exchange_rate
                results.append({
                    "Bölge": region,
                    "Stream": f"{streams:,}".replace(",", "."),
                    "Gelir ($)": f"{income:,.2f}",
                    "Gelir (₺)": f"{income_try:,.2f}"
                })

            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)

            # Özet
            total_usd = sum([streams * region_rates[r] for r in selected_regions])
            total_try = total_usd * exchange_rate
            st.success(f"Toplam Gelir: {currency_symbol}{total_usd:,.2f} ≈ ₺{total_try:,.2f}")

            # Excel indir
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="Spotify", index=False)
            st.download_button("📥 Spotify Excel indir", data=buffer.getvalue(), file_name="spotify_geliri.xlsx")

    except ValueError:
        st.error("Lütfen geçerli bir sayı girin.")
