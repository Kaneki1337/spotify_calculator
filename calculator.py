import streamlit as st
import pandas as pd

# =====================
# PAGE CONFIG
# =====================
st.set_page_config(page_title="Pro Gelir Dashboard", layout="wide")

st.title("💰 Pro Gelir Dashboard")

# =====================
# EXCHANGE RATE
# =====================
exchange_rate = 46.06
symbol = "$"

# =====================
# REGION DATA
# =====================
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
    "Dünya Geneli": 0.00238,
    "İsviçre": 0.0030
}

# =====================
# STATE
# =====================
for k in ["spotify_total", "yt_total", "social_total"]:
    st.session_state.setdefault(k, 0.0)

# =====================
# SPOTIFY PRO MODEL
# =====================
st.header("🎧 Spotify Pro Model")

streams = st.number_input("Toplam Stream", min_value=0, step=1000, value=0)

regions = st.multiselect(
    "Bölgeler",
    list(region_rates.keys()),
    default=["ABD", "Türkiye"]
)

use_custom = st.checkbox("Custom rate aktif")

custom_rates = {}

if use_custom:
    st.info("Custom rate gir")
    for r in regions:
        custom_rates[r] = st.number_input(
            f"{r} rate",
            value=float(region_rates[r]),
            step=0.0001,
            format="%.5f",
            key=f"c_{r}"
        )

if st.button("Spotify Hesapla"):

    if streams <= 0 or len(regions) == 0:
        st.warning("Stream ve bölge seç")
    else:

        # =====================
        # PRO MODEL: weighted dağıtım
        # =====================
        weights = {r: 1 for r in regions}
        total_weight = sum(weights.values())

        rows = []
        total_usd = 0.0

        for r in regions:

            share = weights[r] / total_weight
            region_streams = streams * share

            rate = custom_rates[r] if use_custom else region_rates[r]

            income = region_streams * rate
            total_usd += income

            rows.append({
                "Bölge": r,
                "Stream": region_streams,
                "Oran": rate,
                "Gelir USD": income
            })

        df = pd.DataFrame(rows)
        df["Gelir TL"] = df["Gelir USD"] * exchange_rate

        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.set_index("Bölge")["Gelir USD"])

        st.session_state.spotify_total = total_usd

        st.success(f"Spotify Toplam: {symbol}{total_usd:,.2f}")

# =====================
# YOUTUBE
# =====================
st.header("▶️ YouTube")

yt_rate = 0.00069
yt_views = st.number_input("YouTube Views", min_value=0)

if st.button("YouTube Hesapla"):
    yt_income = yt_views * yt_rate
    st.session_state.yt_total = yt_income

    st.metric("YouTube", f"{symbol}{yt_income:,.2f}")

# =====================
# SOCIAL
# =====================
st.header("📱 Sosyal")

reels = st.number_input("Reels Views", min_value=0)
tt = st.number_input("TikTok Views", min_value=0)

if st.button("Sosyal Hesapla"):
    social_income = reels * 0.0002 + tt * 0.0007
    st.session_state.social_total = social_income

    st.metric("Sosyal", f"{symbol}{social_income:,.2f}")

# =====================
# DASHBOARD
# =====================
st.header("📊 Genel Özet")

total = (
    st.session_state.spotify_total +
    st.session_state.yt_total +
    st.session_state.social_total
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Spotify", f"₺{st.session_state.spotify_total * exchange_rate:,.2f}")
col2.metric("YouTube", f"₺{st.session_state.yt_total * exchange_rate:,.2f}")
col3.metric("Sosyal", f"₺{st.session_state.social_total * exchange_rate:,.2f}")
col4.metric("GENEL", f"₺{total * exchange_rate:,.2f}")
