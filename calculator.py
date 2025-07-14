import streamlit as st
import json
import os
import requests

WEBHOOK_URL = "https://canary.discord.com/api/webhooks/1394242204628946974/6CZf6_OXWY5SLXPZZm3DWd3Y3XER3eHIiuzvCVBNcS44DfrbGYloC8-XH4VuKxhgfhgV"  # Buraya kendi webhook'unu koy

USER_DB = "users.json"
if not os.path.exists(USER_DB):
    with open(USER_DB, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USER_DB, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=4)

def send_webhook(event, username, email):
    try:
        requests.post(WEBHOOK_URL, json={"content": f"📢 **{event}**\n👤 Kullanıcı: `{username}`\n📧 {email}"})
    except Exception as e:
        print("Webhook hatası:", e)

def register_user(username, email, password):
    users = load_users()
    if username in users:
        return False, "Kullanıcı adı zaten kayıtlı."
    users[username] = {"email": email, "password": password}
    save_users(users)
    send_webhook("Yeni Kayıt", username, email)
    return True, "Kayıt başarılı."

def login_user(username, password):
    users = load_users()
    if username in users and users[username]["password"] == password:
        send_webhook("Giriş Yapıldı", username, users[username]["email"])
        return True, users[username]
    return False, None

# --- Streamlit Arayüzü ---

st.set_page_config("Giriş/Kayıt", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 KXNEKIPASA Giriş / Kayıt")

    tab = st.radio("Seçim Yap", ["Giriş Yap", "Kayıt Ol"])

    if tab == "Giriş Yap":
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap"):
            success, user = login_user(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.user = {"username": username, "email": user["email"]}
                st.success("✅ Giriş başarılı!")
                st.experimental_rerun()
            else:
                st.error("❌ Kullanıcı adı veya şifre hatalı.")
    else:
        username = st.text_input("Yeni Kullanıcı Adı")
        email = st.text_input("E-posta")
        password = st.text_input("Şifre", type="password")
        if st.button("Kayıt Ol"):
            success, msg = register_user(username, email, password)
            if success:
                st.success(msg)
            else:
                st.warning(msg)

else:
    st.success(f"🎉 Hoş geldin, {st.session_state.user['username']}!")
    if st.button("🔓 Çıkış Yap"):
        st.session_state.logged_in = False
        st.experimental_rerun()
    st.write("Uygulaman burada çalışacak.")
