import streamlit as st

# ─── User Credentials Database ──────────────────────────────────────────────
USERS = {
    "admin":      {"password": "Admin-Secure@2026",    "role": "Admin"},
    "manager":    {"password": "Manager-Auth#2026",    "role": "Manager"},
    "engineer":   {"password": "Engineer-Diag!2026",   "role": "Engineer"},
    "technician": {"password": "Tech-Field^2026",      "role": "Technician"},
}

ROLE_PERMISSIONS = {
    "Admin":      {"description": "Full system access — manage users, models & all data.",      "icon": "", "color": "#ef4444"},
    "Manager":    {"description": "View dashboards, reports, and approve maintenance alerts.",   "icon": "", "color": "#f59e0b"},
    "Engineer":   {"description": "Run model predictions, upload datasets, analyse trends.",     "icon": "", "color": "#3b82f6"},
    "Technician": {"description": "View predictions and anomaly alerts for assigned vehicles.", "icon": "", "color": "#10b981"},
}

# ─── CSS Styling ─────────────────────────────────────────────────────────────
def inject_css(dark_mode: bool):
    if dark_mode:
        bg_primary   = "#0f172a"
        bg_card      = "#1e293b"
        bg_input     = "#0f172a"
        text_primary = "#f1f5f9"
        text_muted   = "#94a3b8"
        border_color = "#334155"
        accent       = "#38bdf8"
        accent2      = "#818cf8"
    else:
        bg_primary   = "#f0f4f8"
        bg_card      = "#ffffff"
        bg_input     = "#f8fafc"
        text_primary = "#0f172a"
        text_muted   = "#64748b"
        border_color = "#e2e8f0"
        accent       = "#0ea5e9"
        accent2      = "#6366f1"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Global Reset ── */
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        background-color: {bg_primary};
        color: {text_primary};
    }}
    .stApp {{
        background: {bg_primary};
    }}
    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer, header {{ visibility: hidden; }}

    /* ── Page wrapper ── */
    .login-wrapper {{
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem 1rem;
    }}

    /* ── Card ── */
    .login-card {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 20px;
        padding: 2.5rem 3rem;
        max-width: 460px;
        width: 100%;
        box-shadow: 0 25px 60px rgba(0,0,0,0.18);
        margin: auto;
    }}

    /* ── Header ── */
    .brand-header {{
        text-align: center;
        margin-bottom: 2rem;
    }}
    .brand-icon {{
        font-size: 3.5rem;
        display: block;
        margin-bottom: .5rem;
        animation: pulse 3s ease-in-out infinite;
    }}
    @keyframes pulse {{
        0%,100% {{ transform: scale(1);   opacity:1;   }}
        50%      {{ transform: scale(1.08); opacity:.85; }}
    }}
    .brand-title {{
        font-size: 2.2rem;
        font-weight: 800;
        color: white;
        margin: 0;
        line-height: 1.2;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }}
    .brand-sub {{
        color: {text_muted};
        font-size: .8rem;
        margin-top: .3rem;
        letter-spacing: .5px;
    }}

    /* ── Divider ── */
    .divider {{
        border: none;
        border-top: 1px solid {border_color};
        margin: 1.5rem 0;
    }}

    /* ── Role cards ── */
    .role-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: .6rem;
        margin: 1rem 0 1.5rem;
    }}
    .role-pill {{
        background: {bg_input};
        border: 1px solid {border_color};
        border-radius: 10px;
        padding: .5rem .75rem;
        font-size: .78rem;
        color: {text_muted};
        display: flex;
        align-items: center;
        gap: .4rem;
    }}
    .role-pill span.dot {{
        width:8px; height:8px; border-radius:50%;
        display:inline-block; flex-shrink:0;
    }}

    /* ── Status badge ── */
    .status-bar {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: .5rem;
        padding: .5rem 1rem;
        background: {bg_input};
        border: 1px solid {border_color};
        border-radius: 50px;
        font-size: .75rem;
        color: {text_muted};
        margin-bottom: 1.5rem;
    }}
    .status-dot {{
        width: 8px; height: 8px; border-radius: 50%;
        background: #10b981;
        box-shadow: 0 0 6px #10b981;
        animation: blink 1.5s ease-in-out infinite;
    }}
    @keyframes blink {{
        0%,100% {{ opacity:1; }} 50% {{ opacity:.35; }}
    }}

    /* ── Form Fields override ── */
    .stTextInput > label, .stSelectbox > label {{
        font-size: .82rem;
        font-weight: 600;
        color: {text_muted};
        letter-spacing: .4px;
        text-transform: uppercase;
    }}
    .stTextInput > div > div > input {{
        background: {bg_input} !important;
        border: 1.5px solid {border_color} !important;
        border-radius: 10px !important;
        color: {text_primary} !important;
        font-size: .95rem !important;
        padding: .55rem .9rem !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: {accent} !important;
        box-shadow: 0 0 0 3px {accent}33 !important;
    }}
    .stSelectbox > div > div {{
        background: {bg_input} !important;
        border: 1.5px solid {border_color} !important;
        border-radius: 10px !important;
        color: {text_primary} !important;
    }}

    /* ── Login button ── */
    .stButton > button {{
        width: 100% !important;
        background: linear-gradient(135deg, {accent}, {accent2}) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: .72rem 1.5rem !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        letter-spacing: .4px !important;
        cursor: pointer !important;
        transition: opacity .2s, transform .15s !important;
        margin-top: .5rem !important;
    }}
    .stButton > button:hover {{
        opacity: .9 !important;
        transform: translateY(-1px) !important;
    }}

    /* ── Footer note ── */
    .login-footer {{
        text-align: center;
        font-size: .73rem;
        color: {text_muted};
        margin-top: 1.8rem;
    }}
    .login-footer a {{ color: {accent}; text-decoration: none; }}
    </style>
    """, unsafe_allow_html=True)


# ─── Login Logic ─────────────────────────────────────────────────────────────
def show_login_page():
    # ── Dark mode toggle (top-right sidebar) ─────────────────────────────────
    with st.sidebar:
        st.markdown("### Display")
        dark_mode = st.toggle("🌙 Dark Mode", value=True)
        st.markdown("---")
        st.markdown("**Demo credentials**")
        for uname, info in USERS.items():
            role_info = ROLE_PERMISSIONS[info["role"]]
            st.markdown(f"{role_info['icon']} `{uname}` / `{info['password']}`")

    inject_css(dark_mode)

    # ── Brand header ─────────────────────────────────────────────────────────
    st.markdown("""
    <div class='brand-header'>
        <p class='brand-title'>
            AI-Powered Predictive Maintenance System for <br>
            Enhancing Vehicle Reliability and Safety
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Status indicator ─────────────────────────────────────────────────────
    st.markdown("""
    <div class='status-bar'>
        <span class='status-dot'></span>
        AI Engine Online &nbsp;·&nbsp; Secure Connection
    </div>
    """, unsafe_allow_html=True)

    # ── Role info cards ───────────────────────────────────────────────────────
    with st.expander("Available Roles", expanded=False):
        cols = st.columns(2)
        for i, (role, info) in enumerate(ROLE_PERMISSIONS.items()):
            with cols[i % 2]:
                st.markdown(f"""
                <div style='background:{"#1e293b" if dark_mode else "#f8fafc"};
                            border:1px solid {"#334155" if dark_mode else "#e2e8f0"};
                            border-left: 3px solid {info["color"]};
                            border-radius:10px; padding:.75rem; margin-bottom:.5rem;'>
                    <div style='font-size:1.2rem'><strong style='font-size:.9rem'>{role}</strong></div>
                    <div style='font-size:.75rem; color:{"#94a3b8" if dark_mode else "#64748b"}; margin-top:.3rem'>{info["description"]}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Login form ────────────────────────────────────────────────────────────
    with st.form("login_form", clear_on_submit=False):
        role_choice = st.selectbox(" Select Your Role", list(ROLE_PERMISSIONS.keys()))
        username    = st.text_input(" Username", placeholder="Enter your username")
        password    = st.text_input(" Password", type="password", placeholder="Enter your password")
        submitted   = st.form_submit_button(" Sign In to Dashboard")

    if submitted:
        if not username or not password:
            st.error("⚠️ Please fill in both username and password.")
        elif username in USERS:
            user = USERS[username]
            if user["password"] == password:
                if user["role"] == role_choice:
                    # ── Successful login ──────────────────────────────────
                    st.session_state.logged_in   = True
                    st.session_state.username    = username
                    st.session_state.role        = user["role"]
                    st.session_state.dark_mode   = dark_mode
                    st.success(f"Welcome back, **{username.capitalize()}**! Redirecting…")
                    st.rerun()
                else:
                    st.error(f"❌ Role mismatch. Your account is assigned to **{user['role']}**, not {role_choice}.")
            else:
                st.error("❌ Incorrect password. Please try again.")
        else:
            st.error("❌ Username not found. Please check your credentials.")

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class='login-footer'>
        🔐 Protected System &nbsp;·&nbsp; Unauthorized access is prohibited<br>
        <a href='#'>Privacy Policy</a> &nbsp;·&nbsp; <a href='#'>Support</a>
    </div>
    """, unsafe_allow_html=True)
