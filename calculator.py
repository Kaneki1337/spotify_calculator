import streamlit as st
import pandas as pd

# Sayfa ayarı
st.set_page_config(page_title="Gelir Hesaplayıcı", layout="wide")

# --- Kurlar ---
usd_to_try = 40.17
eur_to_try = 43.20
gbp_to_try = 51.00  # örnek değer, gerekirse güncelle

# Döviz seçimi
currency_option = st.sidebar.selectbox("💱 Döviz Cinsi", ["USD", "EUR", "GBP"])
if currency_option == "USD":
    exchange_rate = usd_to_try
    currency_symbol = "$"
elif currency_option == "EUR":
    exchange_rate = eur_to_try
    currency_symbol = "€"
else:
    exchange_rate = gbp_to_try
    currency_symbol = "£"

# --- Gelir oranları (ülke bazlı örnek değerler) ---
region_rates = {
    "ABD": 0.0040,
    "Türkiye": 0.0010,
    "Almanya": 0.0039,
    "Fransa": 0.0038,
    "İngiltere": 0.0041,
    "Kanada": 0.0037,
    "Avustralya": 0.0036,
    "İspanya": 0.0035,
    "İtalya": 0.0034,
    "Hindistan": 0.0012,
    "Çin": 0.0011,
    "Japonya": 0.0030,
    "Brezilya": 0.0020,
    "Rusya": 0.0015,
    "Meksika": 0.0022,
    "Dünya Geneli": 0.00238
}

# Platform oranları (ortalama)
yt_rate = 0.00069
reels_rate = 0.0002
tt_rate = 0.0007

# Başlık
st.markdown("<h1 style='text-align:center; color:#7e3ff2;'>🎵 Çoklu Platform Gelir Hesaplayıcı</h1>", unsafe_allow_html=True)
st.caption("*Not: Oranlar örnektir ve platform/pazar dinamiklerine göre değişebilir.*")
st.markdown("---")

# --- Spotify Hesaplama ---
st.subheader("🎧 Spotify Hesaplama")
col1, col2 = st.columns(2)
with col1:
    raw_input = st.text_input("Toplam Spotify Dinlenme Sayısı (örn: 1.000.000)", value="")
with col2:
    selected_regions = st.multiselect(
        "Dinleyici Bölgeleri",
        list(region_rates.keys()),
        default=["ABD", "Türkiye"]
    )

# Özel oran kullanımı
use_custom = st.checkbox("Bu hesaplama için seçili ülkelerde **özel oran** kullan", value=False)
custom_rates = {}
if use_custom and selected_regions:
    st.info("Seçtiğin ülkeler için USD başına stream gelir oranını gir. (Örn: 0.0035)")
    for r in selected_regions:
        custom_rates[r] = st.number_input(f"{r} oranı ($/stream)", min_value=0.0, value=float(region_rates[r]), step=0.0001, format="%.5f")

# State başlangıçları
st.session_state.setdefault("spotify_total_usd", 0.0)
st.session_state.setdefault("yt_total_usd", 0.0)
st.session_state.setdefault("social_total_usd", 0.0)

spotify_df = None

if st.button("Spotify Gelirini Hesapla"):
    try:
        streams = int(raw_input.replace(".", "").replace(",", ""))
        if streams <= 0:
            st.warning("Lütfen pozitif bir stream sayısı girin.")
        elif not selected_regions:
            st.warning("En az bir bölge seçmelisiniz.")
        else:
            # Hesaplama (numeric df + gösterim için formatlı kopya)
            rows = []
            for region in selected_regions:
                rate = custom_rates.get(region, region_rates[region]) if use_custom else region_rates[region]
                income_usd = streams * rate
                income_try = income_usd * exchange_rate
                rows.append({
                    "Bölge": region,
                    "Stream": streams,
                    "Oran ($)": rate,
                    "Gelir_USD": income_usd,
                    "Gelir_TL": income_try,
                })
            spotify_df = pd.DataFrame(rows)

            # Gösterim
            display_df = spotify_df.copy()
            display_df["Stream"] = display_df["Stream"].map(lambda x: f"{x:,}".replace(",", "."))
            display_df["Oran ($)"] = display_df["Oran ($)"].map(lambda x: f"{x:,.5f}")
            display_df["Gelir ($)"] = spotify_df["Gelir_USD"].map(lambda x: f"{x:,.2f}")
            display_df["Gelir (₺)"] = spotify_df["Gelir_TL"].map(lambda x: f"{x:,.2f}")
            display_df = display_df[["Bölge", "Stream", "Oran ($)", "Gelir ($)", "Gelir (₺)"]]
            st.dataframe(display_df, use_container_width=True)

            # Özet
            total_usd = float(spotify_df["Gelir_USD"].sum())
            total_try = total_usd * exchange_rate
            st.session_state["spotify_total_usd"] = total_usd
            st.success(f"Toplam Spotify Geliri: {currency_symbol}{total_usd:,.2f} ≈ ₺{total_try:,.2f}")

            # Grafik
            chart_df = spotify_df.set_index("Bölge")["Gelir_USD"]
            st.bar_chart(chart_df)

            # CSV indir
            csv_data = display_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Spotify CSV indir", data=csv_data, file_name="spotify_geliri.csv", mime="text/csv")

    except ValueError:
        st.error("Lütfen geçerli bir sayı girin.")

st.markdown("---")

# --- YouTube Hesaplama ---
st.subheader("▶️ YouTube Hesaplama")
yt_views = st.number_input("YouTube Görüntülenme", min_value=0, value=0)
if st.button("YouTube Gelirini Hesapla"):
    yt_income = yt_views * yt_rate
    yt_income_try = yt_income * exchange_rate
    st.session_state["yt_total_usd"] = float(yt_income)
    col1, col2 = st.columns(2)
    col1.metric("YouTube Geliri", f"{currency_symbol}{yt_income:,.2f}")
    col2.metric("TL Karşılığı", f"₺{yt_income_try:,.2f}")

st.markdown("---")

# --- Instagram & TikTok Hesaplama ---
st.subheader("📱 Instagram & TikTok Hesaplama")
col1, col2 = st.columns(2)
reels_views = col1.number_input("Instagram Reels Görüntülenme", min_value=0, value=0)
tt_views = col2.number_input("TikTok Görüntülenme", min_value=0, value=0)

if st.button("Sosyal Medya Gelirini Hesapla"):
    reels_income = reels_views * reels_rate
    tt_income = tt_views * tt_rate
    total_income = reels_income + tt_income
    total_income_try = total_income * exchange_rate
    st.session_state["social_total_usd"] = float(total_income)
    col1.metric("Sosyal Medya Geliri", f"{currency_symbol}{total_income:,.2f}")
    col2.metric("TL Karşılığı", f"₺{total_income_try:,.2f}")

st.markdown("---")

# --- Genel Özet (platformların toplamı) ---
st.subheader("📊 Genel Özet")
col_a, col_b, col_c, col_d = st.columns(4)
spotify_total = st.session_state.get("spotify_total_usd", 0.0)
yt_total = st.session_state.get("yt_total_usd", 0.0)
social_total = st.session_state.get("social_total_usd", 0.0)
grand_total = spotify_total + yt_total + social_total

col_a.metric("Spotify Toplam", f"{currency_symbol}{spotify_total:,.2f}")
col_b.metric("YouTube Toplam", f"{currency_symbol}{yt_total:,.2f}")
col_c.metric("Sosyal Toplam", f"{currency_symbol}{social_total:,.2f}")
col_d.metric("GENEL TOPLAM", f"{currency_symbol}{grand_total:,.2f}", help="Spotify + YouTube + Instagram Reels + TikTok")

st.caption("Hesaplamalar seçili döviz cinsine göre gösterilir ve yaklaşık değerlerdir.")
