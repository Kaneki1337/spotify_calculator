import streamlit as st
import pandas as pd

# --------------------
# PAGE CONFIG
# --------------------
st.set_page_config(
    page_title="Gelir Dashboard",
    layout="wide",
    page_icon="💰"
)

# --------------------
# STYLE (basit modern görünüm)
# --------------------
st.markdown("""
<style>
.main-title {
    text-align:center;
    font-size:42px;
    font-weight:700;
    color:#7e3ff2;
    margin-bottom:10px;
}
.card {
    background-color:#111827;
    padding:20px;
    border-radius:15px;
    margin-bottom:15px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">💰 Gelir Dashboard Pro</div>', unsafe_allow_html=True)

# --------------------
# EXCHANGE RATES
# --------------------
exchange_rates = {
    "USD": 46.06,
    "EUR": 53.43,
    "GBP": 51.00
}

currency = st.sidebar.selectbox("💱 Para Birimi", list(exchange_rates.keys()))
exchange_rate = exchange_rates[currency]
symbol = {"USD": "$", "EUR": "€", "GBP": "£"}[currency]

# --------------------
# PLATFORM RATES
# --------------------
region_rates = {
    "ABD": 0.0040, "Türkiye": 0.0010, "Almanya": 0.0039,
    "Fransa": 0.0038, "İngiltere": 0.0041, "Kanada": 0.0037,
    "Avustralya": 0.0036, "İspanya": 0.0035, "İtalya": 0.0034,
    "Hindistan": 0.0012, "Çin": 0.0011, "Japonya": 0.0030,
    "Brezilya": 0.0020, "Rusya": 0.0015, "Meksika": 0.0022,
    "Dünya Geneli": 0.00238, "İsviçre": 0.0030
}

yt_rate = 0.00069
reels_rate = 0.0002
tt_rate = 0.0007

# --------------------
# SESSION STATE
# --------------------
for k in ["spotify", "yt", "social"]:
    st.session_state.setdefault(k, 0.0)

# =========================
# SPOTIFY
# =========================
st.markdown("## 🎧 Spotify")

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        streams = st.number_input("Toplam Stream", min_value=0, step=1000)

    with col2:
        regions = st.multiselect("Bölgeler", list(region_rates.keys()), default=["ABD", "Türkiye"])

use_custom = st.checkbox("Özel oran kullan")

custom = {}
if use_custom:
    for r in regions:
        custom[r] = st.slider(f"{r} oranı", 0.0001, 0.01, region_rates[r])

if st.button("Spotify Hesapla") and streams > 0 and regions:

    per_region = streams / len(regions)

    data = []
    total = 0

    for r in regions:
        rate = custom.get(r, region_rates[r]) if use_custom else region_rates[r]

        income = per_region * rate
        total += income

        data.append([r, per_region, rate, income])

    df = pd.DataFrame(data, columns=["Bölge", "Stream", "Oran", "Gelir USD"])

    df["Gelir TL"] = df["Gelir USD"] * exchange_rate

    st.session_state.spotify = total

    st.dataframe(df, use_container_width=True)
    st.bar_chart(df.set_index("Bölge")["Gelir USD"])

    st.success(f"Spotify Gelir: {symbol}{total:,.2f}")

# =========================
# YOUTUBE
# =========================
st.markdown("## ▶️ YouTube")

yt_views = st.number_input("Görüntülenme", min_value=0)

if st.button("YouTube Hesapla"):
    income = yt_views * yt_rate
    st.session_state.yt = income

    col1, col2 = st.columns(2)
    col1.metric("YouTube", f"{symbol}{income:,.2f}")
    col2.metric("TL", f"₺{income * exchange_rate:,.2f}")

# =========================
# SOCIAL
# =========================
st.markdown("## 📱 Sosyal Medya")

c1, c2 = st.columns(2)

reels = c1.number_input("Reels Views", min_value=0)
tt = c2.number_input("TikTok Views", min_value=0)

if st.button("Sosyal Hesapla"):
    income = reels * reels_rate + tt * tt_rate
    st.session_state.social = income

    st.metric("Toplam", f"{symbol}{income:,.2f}")

# =========================
# DASHBOARD
# =========================
st.markdown("## 📊 Özet")

total = st.session_state.spotify + st.session_state.yt + st.session_state.social

col1, col2, col3 = st.columns(3)

col1.metric("Spotify", f"₺{st.session_state.spotify * exchange_rate:,.2f}")
col2.metric("YouTube", f"₺{st.session_state.yt * exchange_rate:,.2f}")
col3.metric("Sosyal", f"₺{st.session_state.social * exchange_rate:,.2f}")

st.markdown("---")

st.metric("GENEL TOPLAM", f"₺{total * exchange_rate:,.2f}")
