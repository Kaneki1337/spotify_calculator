import streamlit as st
import pandas as pd

# =====================
# PAGE
# =====================
st.set_page_config(page_title="Gelir Dashboard", layout="wide")

st.title("💰 Gelir Dashboard")

# =====================
# RATE
# =====================
exchange_rate = 46.06
symbol = "$"

region_rates = {
    "ABD": 0.0040,
    "Türkiye": 0.0010,
    "İsviçre": 0.0030,
    "Almanya": 0.0039
}

yt_rate = 0.00069
reels_rate = 0.0002
tt_rate = 0.0007

# =====================
# STATE
# =====================
for k in ["spotify", "yt", "social"]:
    st.session_state.setdefault(k, 0.0)

# =====================
# SPOTIFY FIXED
# =====================
st.header("🎧 Spotify")

streams = st.number_input("Toplam Stream", min_value=0, step=1000, value=0)

regions = st.multiselect(
    "Bölgeler",
    list(region_rates.keys()),
    default=["ABD", "Türkiye"]
)

use_custom = st.checkbox("Custom rate")

custom_rates = {}

if use_custom:
    for r in regions:
        custom_rates[r] = st.number_input(
            f"{r} rate",
            value=float(region_rates[r]),
            step=0.0001,
            format="%.5f",
            key=f"rate_{r}"
        )

if st.button("Spotify Hesapla"):

    if streams <= 0 or len(regions) == 0:
        st.warning("Stream veya bölge eksik")

    else:

        # 🔥 KRİTİK FIX: stream bölünmüyor, yanlış büyüme yok
        region_share = 1 / len(regions)

        rows = []
        total_usd = 0.0

        for r in regions:

            rate = custom_rates[r] if use_custom and r in custom_rates else region_rates[r]

            region_streams = streams * region_share  # ✔ doğru dağıtım

            income = region_streams * rate
            total_usd += income

            rows.append({
                "Bölge": r,
                "Stream": int(region_streams),
                "Oran": rate,
                "Gelir USD": income
            })

        df = pd.DataFrame(rows)
        df["Gelir TL"] = df["Gelir USD"] * exchange_rate

        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.set_index("Bölge")["Gelir USD"])

        st.session_state.spotify = total_usd

        st.success(f"Spotify Toplam: {symbol}{total_usd:,.2f}")

# =====================
# YOUTUBE
# =====================
st.header("▶️ YouTube")

yt_views = st.number_input("Views", min_value=0)

if st.button("YouTube"):
    income = yt_views * yt_rate
    st.session_state.yt = income
    st.metric("YouTube", f"{symbol}{income:,.2f}")

# =====================
# SOCIAL
# =====================
st.header("📱 Sosyal")

reels = st.number_input("Reels", min_value=0)
tt = st.number_input("TikTok", min_value=0)

if st.button("Sosyal"):
    income = reels * reels_rate + tt * tt_rate
    st.session_state.social = income
    st.metric("Sosyal", f"{symbol}{income:,.2f}")

# =====================
# TOTAL
# =====================
st.header("📊 Toplam")

total = st.session_state.spotify + st.session_state.yt + st.session_state.social

col1, col2, col3, col4 = st.columns(4)

col1.metric("Spotify", f"₺{st.session_state.spotify * exchange_rate:,.2f}")
col2.metric("YouTube", f"₺{st.session_state.yt * exchange_rate:,.2f}")
col3.metric("Sosyal", f"₺{st.session_state.social * exchange_rate:,.2f}")
col4.metric("GENEL", f"₺{total * exchange_rate:,.2f}")
