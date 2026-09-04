"""
Snap — a Streamlit frontend for the URL Shortener API.
Run:  streamlit run app.py
"""

from datetime import datetime
from io import BytesIO
from urllib.parse import urlparse

import requests
import streamlit as st
from streamlit_option_menu import option_menu

try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False


import os

DEFAULT_BASE_URL = "https://url-shortener-api-backend-5.onrender.com"


def resolve_base_url() -> str:
    """Backend location is a deployment detail, never a user-facing setting.
    Resolved once, in this order: Streamlit secrets -> env var -> default."""
    try:
        if "API_BASE_URL" in st.secrets:
            return str(st.secrets["API_BASE_URL"]).rstrip("/")
    except Exception:
        pass
    return os.environ.get("API_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


BASE_URL = resolve_base_url()

st.set_page_config(page_title="Snap · Link Manager", page_icon="⚡", layout="wide")


# =========================================================================
# THEME
# =========================================================================
INK = "#0B0B12"
PANEL = "#13131F"
PANEL_2 = "#191927"
BORDER = "rgba(255,255,255,0.07)"
TEXT = "#EDEBF7"
MUTED = "#8B87A3"
ACCENT = "#7C5CFF"
ACCENT_2 = "#00D4B5"
DANGER = "#FF6B7A"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
    code, pre, .stCode {{ font-family: 'JetBrains Mono', monospace !important; }}

    #MainMenu, footer, header {{ visibility: hidden; }}
    .block-container {{ padding-top: 1.4rem; max-width: 1180px; }}

    .stApp {{
        background:
            radial-gradient(900px circle at 10% -10%, rgba(124,92,255,0.16), transparent 55%),
            radial-gradient(900px circle at 100% 10%, rgba(0,212,181,0.10), transparent 50%),
            {INK};
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-radius: 20px !important;
        border: 1px solid {BORDER} !important;
        background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.005));
        box-shadow: 0 1px 0 rgba(255,255,255,0.03) inset;
    }}

    .stButton>button, .stFormSubmitButton>button, .stLinkButton>a {{
        border-radius: 11px !important;
        font-weight: 600 !important;
        border: 1px solid {BORDER} !important;
        color: {TEXT} !important;
        background: {PANEL_2} !important;
        transition: all .14s ease !important;
    }}
    .stButton>button:hover, .stFormSubmitButton>button:hover, .stLinkButton>a:hover {{
        border-color: rgba(124,92,255,0.55) !important;
        box-shadow: 0 6px 20px rgba(124,92,255,0.22) !important;
        transform: translateY(-1px);
    }}
    .stButton>button[kind="primary"], .stFormSubmitButton>button[kind="primary"] {{
        background: linear-gradient(90deg, {ACCENT}, #6247E0) !important;
        border: none !important;
        color: white !important;
    }}
    div[data-testid="stPopover"]>button {{ border-radius: 11px !important; }}

    .stTextInput>div>div>input, .stTextArea textarea {{
        border-radius: 11px !important;
        background: {PANEL} !important;
        border: 1px solid {BORDER} !important;
    }}
    .stTextInput>div>div>input:focus, .stTextArea textarea:focus {{
        border-color: {ACCENT} !important;
        box-shadow: 0 0 0 3px rgba(124,92,255,0.18) !important;
    }}

    div[data-testid="stMetricValue"] {{ font-size: 1.7rem; font-weight: 800; color: {TEXT}; }}
    div[data-testid="stMetricLabel"] {{ color: {MUTED}; font-size: 0.82rem; }}

    .eyebrow {{
        display: inline-flex; align-items: center; gap: 6px;
        padding: 5px 12px; border-radius: 999px;
        background: rgba(124,92,255,0.14); border: 1px solid rgba(124,92,255,0.30);
        color: #C9BFFF; font-size: 0.72rem; font-weight: 700; letter-spacing: .06em;
        text-transform: uppercase; margin-bottom: 14px;
    }}
    .hero-title {{
        font-size: 2.9rem; font-weight: 800; line-height: 1.08; letter-spacing: -0.02em;
        color: {TEXT}; margin-bottom: 10px;
    }}
    .hero-title span {{
        background: linear-gradient(90deg, #C9BFFF, {ACCENT} 55%, {ACCENT_2});
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    .hero-sub {{ color: {MUTED}; font-size: 1.02rem; max-width: 460px; line-height: 1.55; }}
    .section-title {{ font-size: 1.05rem; font-weight: 700; color: {TEXT}; margin: 0 0 2px 0; }}
    .section-sub {{ color: {MUTED}; font-size: 0.85rem; margin-bottom: 4px; }}

    .link-row-code {{
        font-family: 'JetBrains Mono', monospace; font-weight: 600; font-size: 0.95rem; color: {TEXT};
    }}
    .link-row-target {{ color: {MUTED}; font-size: 0.82rem; word-break: break-all; }}
    .chip {{
        display: inline-flex; align-items: center; gap: 5px; padding: 3px 10px; border-radius: 999px;
        font-size: 0.68rem; font-weight: 700; letter-spacing: .03em;
    }}
    .chip-hot {{ background: rgba(255,107,122,0.14); color: {DANGER}; border: 1px solid rgba(255,107,122,0.3); }}
    .chip-live {{ background: rgba(0,212,181,0.14); color: {ACCENT_2}; border: 1px solid rgba(0,212,181,0.3); }}

    .stat-icon {{
        width: 38px; height: 38px; border-radius: 11px; display: flex; align-items: center;
        justify-content: center; font-size: 1.1rem; margin-bottom: 6px;
    }}

    .brand {{ font-weight: 800; font-size: 1.25rem; letter-spacing: -0.01em; color: {TEXT}; }}
    .brand span {{ color: {ACCENT}; }}

    hr {{ border-color: {BORDER}; margin: 0.6rem 0; }}

    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-track {{ background: {INK}; }}
    ::-webkit-scrollbar-thumb {{ background: #2A2A3D; border-radius: 10px; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================================
# STATE
# =========================================================================
for k, v in {
    "token": None, "email": None,
    "last_created": None, "sort_mode": "Newest", "search_q": "", "nav": "Overview",
}.items():
    st.session_state.setdefault(k, v)

qp = st.query_params
if "token" in qp and not st.session_state.token:
    st.session_state.token = qp["token"]


def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def api_url(path: str) -> str:
    return f"{BASE_URL}{path}"


def do_logout():
    st.session_state.token = None
    st.session_state.email = None
    if "token" in st.query_params:
        del st.query_params["token"]


def make_qr(data: str) -> bytes:
    img = qrcode.make(data, border=2)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def error_detail(res: requests.Response) -> str:
    try:
        d = res.json().get("detail")
        return d if isinstance(d, str) else str(d)
    except Exception:
        return res.text or f"Request failed ({res.status_code})"


def favicon_for(url: str) -> str:
    try:
        domain = urlparse(url).netloc
    except Exception:
        domain = ""
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=64" if domain else ""


# =========================================================================
# LOGGED-OUT VIEW
# =========================================================================
if not st.session_state.token:
    left, right = st.columns([1.05, 1], gap="large")

    with left:
        st.markdown('<div class="eyebrow">⚡ Fast · Private · Yours</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hero-title">Shorten links.<br>Track every <span>click</span>.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="hero-sub">Snap turns long, messy URLs into clean short links you can '
            'share anywhere — and see exactly how they perform.</div>',
            unsafe_allow_html=True,
        )
        st.write("")

        with st.container(border=True):
            fcols = st.columns(3)
            for col, (icon, label, sub) in zip(fcols, [
                ("🚀", "Instant", "One click to shorten"),
                ("📊", "Tracked", "Live click counts"),
                ("🔒", "Secured", "JWT-protected account"),
            ]):
                with col:
                    st.markdown(f"<div style='font-size:1.4rem'>{icon}</div>", unsafe_allow_html=True)
                    st.markdown(f"**{label}**")
                    st.caption(sub)

    with right:
        with st.container(border=True):
            choice = option_menu(
                None, ["Login", "Register", "Google / token"],
                icons=["box-arrow-in-right", "person-plus", "google"],
                orientation="horizontal", default_index=0,
                styles={
                    "container": {"padding": "0", "background-color": "transparent"},
                    "icon": {"font-size": "14px"},
                    "nav-link": {
                        "font-size": "13px", "font-weight": "600", "border-radius": "10px",
                        "color": MUTED, "background-color": "transparent", "margin": "2px",
                    },
                    "nav-link-selected": {"background-color": ACCENT, "color": "white"},
                },
            )
            st.write("")

            if choice == "Login":
                with st.form("login_form", border=False):
                    email = st.text_input("Email", placeholder="you@example.com")
                    password = st.text_input("Password", type="password", placeholder="••••••••")
                    submitted = st.form_submit_button("Log in", type="primary", use_container_width=True)

                if submitted:
                    if not email or not password:
                        st.warning("Please fill in both fields.")
                    else:
                        with st.spinner("Signing you in..."):
                            try:
                                res = requests.post(
                                    api_url("/auth/login"),
                                    json={"email": email, "password": password}, timeout=15,
                                )
                            except requests.RequestException as e:
                                res = None
                                st.error(f"Couldn't reach the API: {e}")
                        if res is not None:
                            if res.status_code == 200:
                                token = res.json()["access_token"]
                                st.session_state.token = token
                                st.session_state.email = email
                                st.query_params["token"] = token
                                st.rerun()
                            else:
                                st.error(error_detail(res))

            elif choice == "Register":
                with st.form("register_form", border=False):
                    r_email = st.text_input("Email", placeholder="you@example.com", key="r_email")
                    r_pw1 = st.text_input("Password", type="password", key="r_pw1")
                    r_pw2 = st.text_input("Confirm password", type="password", key="r_pw2")
                    r_submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)

                if r_submitted:
                    if not r_email or not r_pw1:
                        st.warning("Please fill in all fields.")
                    elif r_pw1 != r_pw2:
                        st.warning("Passwords don't match.")
                    else:
                        with st.spinner("Creating your account..."):
                            try:
                                res = requests.post(
                                    api_url("/auth/register"),
                                    json={"email": r_email, "password": r_pw1}, timeout=15,
                                )
                            except requests.RequestException as e:
                                res = None
                                st.error(f"Couldn't reach the API: {e}")
                        if res is not None:
                            if res.status_code == 200:
                                st.success("Account created — switch to Login to sign in.")
                            else:
                                st.error(error_detail(res))

            else:  # Google / token
                st.markdown("**Continue with Google**")
                st.caption(
                    "Opens Google sign-in on the API server. Note: the backend's callback "
                    "currently returns the token as raw JSON rather than redirecting back "
                    "here — copy that token and paste it below."
                )
                st.link_button("Continue with Google", api_url("/auth/google/login"), use_container_width=True)
                st.write("")
                with st.form("token_form", border=False):
                    pasted = st.text_input("Access token", type="password")
                    t_submitted = st.form_submit_button("Use this token", use_container_width=True)
                if t_submitted:
                    if pasted:
                        st.session_state.token = pasted
                        st.query_params["token"] = pasted
                        st.rerun()
                    else:
                        st.warning("Paste a token first.")

    st.stop()


# =========================================================================
# LOGGED-IN VIEW
# =========================================================================
with st.spinner("Loading your links..."):
    try:
        list_res = requests.get(api_url("/urls"), headers=auth_headers(), timeout=15)
    except requests.RequestException as e:
        list_res = None
        st.error(f"Couldn't reach the API: {e}")

urls = []
if list_res is not None:
    if list_res.status_code == 200:
        urls = list_res.json()
    elif list_res.status_code == 401:
        st.warning("Your session expired. Please log in again.")
        do_logout()
        st.rerun()
    else:
        st.error(error_detail(list_res))

# ---- top bar ----
tb1, tb2, tb3 = st.columns([1.6, 3.2, 1.2])
with tb1:
    st.markdown('<div class="brand">⚡ Snap<span>.</span></div>', unsafe_allow_html=True)
with tb2:
    nav = option_menu(
        None, ["Overview", "All links", "Analytics"],
        icons=["grid", "link-45deg", "bar-chart-line"],
        orientation="horizontal", default_index=["Overview", "All links", "Analytics"].index(st.session_state.nav),
        styles={
            "container": {"padding": "0", "background-color": "transparent"},
            "icon": {"font-size": "14px"},
            "nav-link": {
                "font-size": "13.5px", "font-weight": "600", "border-radius": "10px",
                "color": MUTED, "background-color": "transparent", "margin": "0 3px",
                "padding": "8px 14px",
            },
            "nav-link-selected": {"background-color": ACCENT, "color": "white"},
        },
    )
    st.session_state.nav = nav
with tb3:
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("↻", use_container_width=True, help="Refresh"):
            st.rerun()
    with c2:
        if st.button("Log out", use_container_width=True):
            do_logout()
            st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)
st.write("")

# ---- derived stats ----
total_links = len(urls)
total_clicks = sum(u.get("clicks", 0) for u in urls)
avg_clicks = round(total_clicks / total_links, 1) if total_links else 0
top_link = max(urls, key=lambda u: u.get("clicks", 0)) if urls else None
max_clicks = max((u.get("clicks", 0) for u in urls), default=0)


def stat_card(icon, bg, label, value):
    with st.container(border=True):
        st.markdown(
            f'<div class="stat-icon" style="background:{bg}20;">{icon}</div>',
            unsafe_allow_html=True,
        )
        st.metric(label, value, label_visibility="visible")


# =========================================================================
# OVERVIEW
# =========================================================================
if st.session_state.nav == "Overview":
    s1, s2, s3, s4 = st.columns(4)
    with s1: stat_card("🔗", ACCENT, "Total links", total_links)
    with s2: stat_card("👆", ACCENT_2, "Total clicks", total_clicks)
    with s3: stat_card("📈", "#FFD166", "Avg clicks / link", avg_clicks)
    with s4: stat_card("🏆", DANGER, "Top link", f"/{top_link['short_code']}" if top_link else "—")

    st.write("")

    with st.container(border=True):
        st.markdown('<p class="section-title">✂️ Shorten a new link</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-sub">Paste any URL — you\'ll get a short, shareable link instantly.</p>', unsafe_allow_html=True)
        with st.form("create_form", border=False):
            c1, c2 = st.columns([4, 1])
            with c1:
                target_url = st.text_input(
                    "Long URL", placeholder="https://example.com/a/very/long/path?with=params",
                    label_visibility="collapsed",
                )
            with c2:
                create_clicked = st.form_submit_button("⚡ Shorten", type="primary", use_container_width=True)

        if create_clicked:
            if not target_url:
                st.warning("Paste a URL first.")
            else:
                with st.spinner("Snapping your link..."):
                    try:
                        res = requests.post(
                            api_url("/urls"), json={"target_url": target_url},
                            headers=auth_headers(), timeout=15,
                        )
                    except requests.RequestException as e:
                        res = None
                        st.error(f"Couldn't reach the API: {e}")
                if res is not None:
                    if res.status_code == 200:
                        st.session_state.last_created = res.json()
                        st.rerun()
                    elif res.status_code == 401:
                        st.warning("Your session expired. Please log in again.")
                        do_logout()
                        st.rerun()
                    else:
                        st.error(error_detail(res))

        if st.session_state.last_created:
            data = st.session_state.last_created
            short_url = api_url(f"/u/{data['short_code']}")
            st.write("")
            sc1, sc2 = st.columns([3, 1])
            with sc1:
                st.markdown('<span class="chip chip-live">● JUST CREATED</span>', unsafe_allow_html=True)
                st.code(short_url, language=None)
                st.markdown(f'<span class="link-row-target">↳ {data["target_url"]}</span>', unsafe_allow_html=True)
            with sc2:
                if QR_AVAILABLE:
                    st.image(make_qr(short_url), width=100)

    st.write("")

    with st.container(border=True):
        st.markdown('<p class="section-title">🏅 Your best performers</p>', unsafe_allow_html=True)
        if not urls:
            st.info("No links yet — create your first one above.")
        else:
            top5 = sorted(urls, key=lambda u: u.get("clicks", 0), reverse=True)[:5]
            for u in top5:
                short_url = api_url(f"/u/{u['short_code']}")
                fav = favicon_for(u["target_url"])
                rc1, rc2, rc3 = st.columns([0.4, 3, 1])
                with rc1:
                    if fav:
                        st.image(fav, width=26)
                with rc2:
                    st.markdown(f'<span class="link-row-code">/{u["short_code"]}</span>', unsafe_allow_html=True)
                    st.markdown(f'<span class="link-row-target">{u["target_url"][:70]}</span>', unsafe_allow_html=True)
                with rc3:
                    st.markdown(f"<div style='text-align:right; padding-top:6px;'><b>{u.get('clicks',0)}</b> <span style='color:{MUTED}'>clicks</span></div>", unsafe_allow_html=True)

# =========================================================================
# ALL LINKS
# =========================================================================
elif st.session_state.nav == "All links":
    with st.container(border=True):
        hdr1, hdr2, hdr3 = st.columns([2, 1.6, 1.2])
        with hdr1:
            st.markdown('<p class="section-title">🗂️ All your links</p>', unsafe_allow_html=True)
        with hdr2:
            st.session_state.search_q = st.text_input(
                "Search", value=st.session_state.search_q, placeholder="🔍 Search by code or URL",
                label_visibility="collapsed",
            )
        with hdr3:
            st.session_state.sort_mode = st.selectbox(
                "Sort", ["Newest", "Most clicks", "Least clicks"], label_visibility="collapsed"
            )

        filtered = urls
        q = st.session_state.search_q.strip().lower()
        if q:
            filtered = [u for u in filtered if q in u.get("short_code", "").lower() or q in u.get("target_url", "").lower()]

        if st.session_state.sort_mode == "Most clicks":
            filtered = sorted(filtered, key=lambda u: u.get("clicks", 0), reverse=True)
        elif st.session_state.sort_mode == "Least clicks":
            filtered = sorted(filtered, key=lambda u: u.get("clicks", 0))
        else:
            filtered = sorted(filtered, key=lambda u: u.get("id", 0), reverse=True)

        st.write("")

        if not urls:
            st.info("No links yet — head to **Overview** to create your first one.")
        elif not filtered:
            st.info("Nothing matches your search.")
        else:
            for u in filtered:
                short_url = api_url(f"/u/{u['short_code']}")
                fav = favicon_for(u["target_url"])
                is_top = max_clicks > 0 and u.get("clicks", 0) == max_clicks
                with st.container(border=True):
                    lc0, lc1, lc2, lc3 = st.columns([0.35, 3, 0.9, 1.6])
                    with lc0:
                        if fav:
                            st.image(fav, width=28)
                    with lc1:
                        badge = '<span class="chip chip-hot">🔥 TOP</span> ' if is_top else ""
                        st.markdown(f'{badge}<span class="link-row-code">/{u["short_code"]}</span>', unsafe_allow_html=True)
                        st.markdown(f'<span class="link-row-target">{u["target_url"]}</span>', unsafe_allow_html=True)
                    with lc2:
                        st.markdown(
                            f"<div style='text-align:center; padding-top:10px;'>"
                            f"<b style='font-size:1.1rem'>{u.get('clicks',0)}</b><br>"
                            f"<span style='color:{MUTED}; font-size:0.72rem;'>clicks</span></div>",
                            unsafe_allow_html=True,
                        )
                    with lc3:
                        b1, b2 = st.columns(2)
                        with b1:
                            st.link_button("Open", short_url, use_container_width=True)
                        with b2:
                            with st.popover("Copy", use_container_width=True):
                                st.code(short_url, language=None)
                                if QR_AVAILABLE:
                                    st.image(make_qr(short_url), width=140)

# =========================================================================
# ANALYTICS
# =========================================================================
else:
    s1, s2, s3 = st.columns(3)
    with s1: stat_card("🔗", ACCENT, "Total links", total_links)
    with s2: stat_card("👆", ACCENT_2, "Total clicks", total_clicks)
    with s3: stat_card("📈", "#FFD166", "Avg clicks / link", avg_clicks)

    st.write("")
    with st.container(border=True):
        st.markdown('<p class="section-title">📊 Clicks by link</p>', unsafe_allow_html=True)
        if urls:
            chart_data = {
                f"/{u['short_code']}": u.get("clicks", 0)
                for u in sorted(urls, key=lambda u: u.get("clicks", 0), reverse=True)[:12]
            }
            st.bar_chart(chart_data, color=ACCENT)
        else:
            st.info("Create some links to see analytics here.")

    st.write("")
    with st.container(border=True):
        st.markdown('<p class="section-title">🥧 Click distribution</p>', unsafe_allow_html=True)
        if urls and total_clicks > 0:
            top_n = sorted(urls, key=lambda u: u.get("clicks", 0), reverse=True)[:8]
            for u in top_n:
                pct = round(u.get("clicks", 0) / total_clicks * 100, 1)
                st.markdown(f"**/{u['short_code']}** &nbsp; <span style='color:{MUTED}'>{pct}%</span>", unsafe_allow_html=True)
                st.progress(min(pct / 100, 1.0))
        else:
            st.caption("No clicks recorded yet.")

st.write("")
st.caption(f"Snap · {datetime.now().strftime('%Y-%m-%d %H:%M')}")
