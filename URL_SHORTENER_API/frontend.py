import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="URL Shortener", layout="wide")

# ---------- STYLING ----------
st.markdown("""
<style>
.big-title {
    font-size: 40px;
    font-weight: bold;
}
.card {
    padding: 15px;
    border-radius: 10px;
    background-color: #1e1e1e;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION ----------
if "token" not in st.session_state:
    st.session_state.token = None

# 🔥 LOAD TOKEN FROM URL (persist login)
query_params = st.query_params
if "token" in query_params and not st.session_state.token:
    st.session_state.token = query_params["token"]

# ---------- HEADER ----------
st.markdown('<p class="big-title">🚀 URL Shortener</p>', unsafe_allow_html=True)

menu = st.sidebar.radio("Navigation", ["Login", "Register", "Dashboard"])

# ---------- REGISTER ----------
if menu == "Register":
    st.subheader("Create Account")

    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input("Email")
    with col2:
        password = st.text_input("Password", type="password")

    if st.button("Register"):
        res = requests.post(f"{BASE_URL}/auth/register", json={
            "email": email,
            "password": password
        })

        if res.status_code == 200:
            st.success("Account created successfully!")
        else:
            st.error(res.text)

# ---------- LOGIN ----------
elif menu == "Login":
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.post(f"{BASE_URL}/auth/login", data={
            "username": email,
            "password": password
        })

        if res.status_code == 200:
            token = res.json()["access_token"]

            # 🔥 store in session
            st.session_state.token = token

            # 🔥 store in URL (persist after refresh)
            st.query_params["token"] = token

            st.success("Logged in!")
            st.rerun()
        else:
            st.error("Invalid credentials")

# ---------- DASHBOARD ----------
elif menu == "Dashboard":

    if not st.session_state.token:
        st.warning("Please login first")
        st.stop()

    headers = {
        "Authorization": f"Bearer {st.session_state.token}"
    }

    # 🔥 REFRESH BUTTON
    colA, colB = st.columns([6,1])
    with colB:
        if st.button("🔄 Refresh"):
            st.rerun()

    st.subheader("Create Short URL")

    col1, col2 = st.columns([3,1])

    with col1:
        target_url = st.text_input("Enter URL to shorten")

    with col2:
        st.write("")
        st.write("")
        shorten = st.button("Shorten")

    if shorten:
        res = requests.post(
            f"{BASE_URL}/urls",
            json={"target_url": target_url},
            headers=headers
        )

        if res.status_code == 200:
            data = res.json()
            short_url = f"{BASE_URL}/u/{data['short_code']}"

            st.success("URL Created!")

            col1, col2 = st.columns([4,1])
            with col1:
                st.code(short_url)
            with col2:
                st.button("Copy", on_click=lambda: st.toast("Copied!"))
        else:
            st.error(res.text)

    st.divider()

    st.subheader("Your Links")

    with st.spinner("Loading..."):
        res = requests.get(f"{BASE_URL}/urls", headers=headers)

    if res.status_code == 200:
        urls = res.json()

        if not urls:
            st.info("No URLs yet")

        for url in urls:
            short_url = f"{BASE_URL}/u/{url['short_code']}"

            st.markdown(f"""
            <div class="card">
                <b>🔗 {short_url}</b><br>
                <small>{url['target_url']}</small><br><br>
                📊 Clicks: {url['clicks']}
            </div>
            """, unsafe_allow_html=True)

    else:
        st.error("Failed to load URLs")