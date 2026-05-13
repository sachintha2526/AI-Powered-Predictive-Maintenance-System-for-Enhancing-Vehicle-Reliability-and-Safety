import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from user_management import show_user_management
from payment_page import show_payment_page
from service_booking import show_service_booking
from maintenance_history import show_maintenance_history
from report_generation import show_report_generation
from train_model import generate_sample_data, preprocess_data, train_model

# ─── Styling ──────────────────────────────────────────────────────────────────
ADMIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family:'Inter',sans-serif; }
.stApp { background:#0f172a; color:#f1f5f9; }
#MainMenu, footer, header { visibility:hidden; }

/* ── Top header bar ── */
.top-header {
    background: linear-gradient(135deg,#1e293b,#0f172a);
    border-bottom: 1px solid #334155;
    border-radius: 14px;
    padding: 1rem 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}
.header-title { font-size:1.3rem; font-weight:800; color:#f1f5f9; }
.header-sub   { font-size:.75rem; color:#64748b; margin-top:2px; }

/* ── KPI cards ── */
.kpi-card {
    background: linear-gradient(135deg,#1e293b,#0f172a);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 1.3rem 1.5rem;
    margin-bottom: .5rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content:''; position:absolute; top:-30px; right:-30px;
    width:90px; height:90px; border-radius:50%;
    opacity:.12;
}
.kpi-label { font-size:.75rem; font-weight:600; color:#64748b; text-transform:uppercase; letter-spacing:.5px; }
.kpi-value { font-size:2.2rem; font-weight:800; color:#f1f5f9; margin:.3rem 0; }
.kpi-delta { font-size:.78rem; font-weight:500; }
.kpi-icon  { font-size:2rem; float:right; margin-top:-3rem; opacity:.7; }

/* ── Section heading ── */
.section-head {
    font-size:.9rem; font-weight:700; color:#94a3b8;
    text-transform:uppercase; letter-spacing:.8px;
    margin: 1.5rem 0 .8rem; border-left:3px solid #38bdf8;
    padding-left:.7rem;
}

/* ── Activity log table ── */
.activity-row {
    display:flex; align-items:center; gap:.9rem;
    background:#1e293b; border:1px solid #334155;
    border-radius:10px; padding:.7rem 1rem; margin-bottom:.5rem;
}
.activity-dot { width:10px;height:10px;border-radius:50%;flex-shrink:0; }
.activity-text { font-size:.83rem; color:#cbd5e1; flex:1; }
.activity-time { font-size:.72rem; color:#475569; white-space:nowrap; }

/* ── Nav pills ── */
.stRadio > div { gap:.4rem !important; }
.stRadio label {
    background:#1e293b !important; border:1px solid #334155 !important;
    border-radius:10px !important; padding:.5rem 1rem !important;
    color:#94a3b8 !important; font-size:.85rem !important;
    transition:.2s !important;
}
.stRadio label:hover { border-color:#38bdf8 !important; color:#f1f5f9 !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] { background:#1e293b; border-right:1px solid #334155; }

/* ── Plotly chart background ── */
.js-plotly-plot .plotly { border-radius:14px; }
</style>
"""

# ─── Synthetic Data ────────────────────────────────────────────────────────────
np.random.seed(7)

USERS_DATA = pd.DataFrame({
    "ID":       [f"U{100+i}" for i in range(10)],
    "Name":     ["Ashan Perera","Nirosh Silva","Kamal Fernando","Suresh Bandara",
                 "Dilani Jayawardena","Ruwan Herath","Thilini Mendis","Kasun Ranasinghe",
                 "Nimal Wijesinghe","Priya Kumari"],
    "Role":     ["Admin","Engineer","Technician","Manager","Engineer","Technician",
                 "Manager","Engineer","Technician","Engineer"],
    "Status":   ["Active","Active","Active","Active","Inactive","Active","Active","Active","Inactive","Active"],
    "Joined":   pd.date_range("2024-01-10", periods=10, freq="25D").strftime("%Y-%m-%d"),
})

VEHICLES_DATA = pd.DataFrame({
    "Vehicle ID":  [f"VH-{200+i:03d}" for i in range(8)],
    "Type":        ["Truck","Bus","Van","Car","Truck","Bus","Car","Van"],
    "Status":      ["Normal","Warning","Normal","Fault","Normal","Normal","Warning","Normal"],
    "Last Check":  pd.date_range("2026-03-28", periods=8, freq="3D").strftime("%Y-%m-%d"),
    "Health %":    [94, 62, 88, 31, 97, 85, 70, 91],
})

PAYMENTS_DATA = pd.DataFrame({
    "Invoice":    [f"INV-{300+i}" for i in range(6)],
    "User":       ["Ashan Perera","Kamal Fernando","Ruwan Herath","Suresh Bandara","Thilini Mendis","Kasun Ranasinghe"],
    "Amount":     ["$240","$180","$320","$150","$210","$290"],
    "Status":     ["Paid","Pending","Paid","Paid","Overdue","Paid"],
    "Date":       pd.date_range("2026-03-01", periods=6, freq="8D").strftime("%Y-%m-%d"),
})

ACTIVITY_LOG = [
    {"color":"#10b981","text":"Ashan Perera logged in from 192.168.1.10","time":"2 min ago"},
    {"color":"#ef4444","text":"ALERT: Vehicle VH-203 entered Fault state — Coolant Temp critical","time":"11 min ago"},
    {"color":"#f59e0b","text":"Vehicle VH-202 downgraded to Warning — Oil Pressure low","time":"28 min ago"},
    {"color":"#3b82f6","text":"Model retrained on new dataset uploaded by Kasun R.","time":"1 hr ago"},
    {"color":"#10b981","text":"Invoice INV-301 payment confirmed — Kamal Fernando","time":"2 hr ago"},
    {"color":"#ef4444","text":"Failed login attempt for user 'admin' from 10.0.0.45","time":"3 hr ago"},
    {"color":"#94a3b8","text":"System health check passed — all services operational","time":"5 hr ago"},
    {"color":"#3b82f6","text":"New Engineer account created: Thilini Mendis","time":"Yesterday"},
]

# ─── Chart helpers ─────────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#94a3b8", size=12),
    margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
)

def alerts_trend_chart():
    days   = pd.date_range(end=datetime.today(), periods=30, freq="D")
    normal = np.random.randint(10, 30, 30)
    warn   = np.random.randint(3, 12, 30)
    fault  = np.random.randint(0, 5, 30)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=days, y=normal, name="Normal",  fill="tozeroy", line=dict(color="#10b981",width=2), fillcolor="rgba(16,185,129,.12)"))
    fig.add_trace(go.Scatter(x=days, y=warn,   name="Warning", fill="tozeroy", line=dict(color="#f59e0b",width=2), fillcolor="rgba(245,158,11,.12)"))
    fig.add_trace(go.Scatter(x=days, y=fault,  name="Fault",   fill="tozeroy", line=dict(color="#ef4444",width=2), fillcolor="rgba(239,68,68,.12)"))
    fig.update_layout(title="Engine Alerts — Last 30 Days", **CHART_LAYOUT,
                      xaxis=dict(gridcolor="#1e293b"), yaxis=dict(gridcolor="#1e293b"))
    return fig

def vehicle_health_bar():
    df  = VEHICLES_DATA.sort_values("Health %")
    clr = ["#ef4444" if h<50 else "#f59e0b" if h<80 else "#10b981" for h in df["Health %"]]
    fig = go.Figure(go.Bar(x=df["Health %"], y=df["Vehicle ID"], orientation="h",
                           marker_color=clr, text=[f"{v}%" for v in df["Health %"]],
                           textposition="outside", textfont=dict(color="#f1f5f9")))
    fig.update_layout(title="Vehicle Health Scores", **CHART_LAYOUT,
                      xaxis=dict(range=[0,110], gridcolor="#1e293b"),
                      yaxis=dict(gridcolor="#1e293b"))
    return fig

def role_donut():
    roles = USERS_DATA["Role"].value_counts()
    fig = go.Figure(go.Pie(labels=roles.index, values=roles.values, hole=.55,
                           marker=dict(colors=["#38bdf8","#818cf8","#10b981","#f59e0b"]),
                           textinfo="label+percent"))
    fig.update_layout(title="Users by Role", **CHART_LAYOUT,
                      showlegend=True)
    return fig

def monthly_revenue_chart():
    months = ["Oct","Nov","Dec","Jan","Feb","Mar","Apr"]
    rev    = [3200, 4100, 3800, 5200, 4800, 6100, 5600]
    fig = go.Figure(go.Bar(x=months, y=rev, marker_color="#38bdf8",
                           text=[f"${v:,}" for v in rev], textposition="outside",
                           textfont=dict(color="#f1f5f9")))
    fig.update_layout(title="Monthly Revenue ($)", **CHART_LAYOUT,
                      yaxis=dict(gridcolor="#1e293b"), xaxis=dict(gridcolor="#1e293b"))
    return fig

# ─── Main Dashboard ────────────────────────────────────────────────────────────
def show_admin_dashboard():
    if "admin_page" not in st.session_state:
        st.session_state.admin_page = "Overview"
    st.markdown(ADMIN_CSS, unsafe_allow_html=True)

    # ── Sidebar navigation ────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center;padding:1rem 0 1.5rem;'>
            <div style='font-size:2.5rem'></div>
            <div style='font-weight:800;font-size:.95rem;color:#f1f5f9;'>Admin Console</div>
            <div style='font-size:.72rem;color:#475569;margin-top:2px;'>AI Maintenance System</div>
        </div>
        """, unsafe_allow_html=True)

        nav = st.radio("Navigation", ["Overview","Users","Vehicles",
                                       "Bookings", "Payments","Reports","Settings"],
                       label_visibility="collapsed")
        st.markdown("---")
        
        if st.button("Back to Login / Logout", key="admin_logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown("---")

        # Quick stats
        st.markdown("<div style='font-size:.72rem;color:#475569;font-weight:600;text-transform:uppercase;letter-spacing:.5px;margin-bottom:.5rem'>System Status</div>", unsafe_allow_html=True)
        for label, val, color in [("AI Model","Online","#10b981"),("DB Connection","Stable","#10b981"),("Last Backup","2h ago","#f59e0b"),("Uptime","99.8%","#10b981")]:
            st.markdown(f"""
            <div style='display:flex;justify-content:space-between;background:#0f172a;
                        border-radius:8px;padding:.4rem .8rem;margin-bottom:.4rem;font-size:.78rem;'>
                <span style='color:#94a3b8'>{label}</span>
                <span style='color:{color};font-weight:600'>{val}</span>
            </div>""", unsafe_allow_html=True)

    # ── Top header ────────────────────────────────────────────────────────────
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(f"""
        <div class='top-header'>
            <div>
                <div class='header-title'> Admin Dashboard</div>
                <div class='header-sub'>{datetime.now().strftime("%A, %d %B %Y  •  %I:%M %p")} &nbsp;·&nbsp; Welcome back, {st.session_state.get('username','Admin').capitalize()}</div>
            </div>
            <div style='display:flex;gap:1.2rem;align-items:center;'>
                <div style='background:#38bdf8;color:#0f172a;font-weight:700;border-radius:50%;
                            width:36px;height:36px;display:flex;align-items:center;
                            justify-content:center;font-size:.9rem;'>
                    {st.session_state.get('username','A')[0].upper()}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE: OVERVIEW
    # ═══════════════════════════════════════════════════════════════════════════
    if nav == "Overview":

        # ── KPI Cards ────────────────────────────────────────────────────────
        k1, k2, k3, k4 = st.columns(4)
        kpis = [
            (k1, "Total Users",     "10",   "+2 this month",  "#38bdf8", "#ef4444 if False else #10b981"),
            (k2, "Active Vehicles", "8",    "6 Normal, 2 Alert","#818cf8","#f59e0b"),
            (k3, "System Alerts",   "3",    "1 Critical Fault", "#ef4444","#ef4444"),
            (k4, "Revenue (Apr)",   "$5,600","↑ 12% vs Mar",   "#10b981","#10b981"),
        ]
        for col, label, value, delta, border_color, delta_color in kpis:
            with col:
                st.markdown(f"""
                <div class='kpi-card' style='border-top:3px solid {border_color};'>
                    <div class='kpi-label'>{label}</div>
                    <div class='kpi-value'>{value}</div>
                    <div class='kpi-delta' style='color:{delta_color}'>{delta}</div>
                </div>""", unsafe_allow_html=True)

        # ── Charts row 1 ─────────────────────────────────────────────────────
        st.markdown("<div class='section-head'>Engine Health Analytics</div>", unsafe_allow_html=True)
        c1, c2 = st.columns([2, 1])
        with c1:
            st.plotly_chart(alerts_trend_chart(), use_container_width=True)
        with c2:
            st.plotly_chart(role_donut(), use_container_width=True)

        # ── Charts row 2 ─────────────────────────────────────────────────────
        c3, c4 = st.columns([1, 2])
        with c3:
            # Vehicle status summary
            statuses = VEHICLES_DATA["Status"].value_counts()
            colors   = {"Normal":"#10b981","Warning":"#f59e0b","Fault":"#ef4444"}
            for status, count in statuses.items():
                pct = count / len(VEHICLES_DATA)
                st.markdown(f"""
                <div style='background:#1e293b;border:1px solid #334155;border-left:3px solid {colors[status]};
                            border-radius:10px;padding:.7rem 1rem;margin-bottom:.5rem;
                            display:flex;justify-content:space-between;align-items:center;'>
                    <span style='color:#f1f5f9;font-weight:600'>{status}</span>
                    <span style='color:{colors[status]};font-weight:800;font-size:1.2rem'>{count}</span>
                </div>""", unsafe_allow_html=True)
        with c4:
            st.plotly_chart(vehicle_health_bar(), use_container_width=True)


    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE: USERS
    # ═══════════════════════════════════════════════════════════════════════════
    elif nav == "Users":
        show_user_management()

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE: VEHICLES
    # ═══════════════════════════════════════════════════════════════════════════
    elif nav == "Vehicles":
        st.markdown("<div class='section-head'>Fleet Management</div>", unsafe_allow_html=True)

        v1, v2, v3 = st.columns(3)
        v1.metric("Total Fleet",    f"{len(VEHICLES_DATA)} Vehicles")
        v2.metric("Active Alerts",  f"{(VEHICLES_DATA['Status']!='Normal').sum()} Vehicles")
        v3.metric("Avg Health",     f"{VEHICLES_DATA['Health %'].mean():.0f}%")

        st.plotly_chart(vehicle_health_bar(), use_container_width=True)

        def style_vehicle(val):
            c = {"Normal":"#10b981","Warning":"#f59e0b","Fault":"#ef4444"}.get(val,"#fff")
            return f"color:{c};font-weight:700"
        st.dataframe(VEHICLES_DATA.style.map(style_vehicle, subset=["Status"]),
                     use_container_width=True, hide_index=True)
    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE: BOOKINGS
    # ═══════════════════════════════════════════════════════════════════════════
    elif nav == "Bookings":
        show_service_booking()

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE: PAYMENTS
    # ═══════════════════════════════════════════════════════════════════════════
    elif nav == "Payments":
        show_payment_page()

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE: REPORTS
    # ═══════════════════════════════════════════════════════════════════════════
    # ─── PAGE: REPORTS ────────────────────────────────────────────────────────
    elif nav == "Reports":
        # Ensure data is available for reporting
        if 'df' not in st.session_state:
            df_temp = generate_sample_data(n_samples=200)
            st.session_state.df = preprocess_data(df_temp)
            model, scaler, metrics = train_model(st.session_state.df)
            st.session_state.metrics = metrics
            st.session_state.model = model
            st.session_state.scaler = scaler

        show_report_generation(st.session_state.df, st.session_state.metrics)

    elif st.session_state.admin_page == "History":
        show_maintenance_history(user_role="Admin")

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE: SETTINGS
    # ═══════════════════════════════════════════════════════════════════════════
    elif nav == "Settings":
        st.markdown("<div class='section-head'>System Configuration</div>", unsafe_allow_html=True)

        with st.form("settings_form"):
            s1, s2 = st.columns(2)
            s1.text_input("System Name",  value="AI Predictive Maintenance System")
            s2.text_input("Admin Email",  value="admin@maintenance.ai")
            s1.number_input("Alert Threshold (% Fault Risk)", 0, 100, 70)
            s2.number_input("Model Retrain Interval (days)",  1, 90,  7)
            s1.selectbox("Default Data Source", ["Sample Data","Uploaded CSV"])
            s2.selectbox("Notification Mode",   ["Email","SMS","Both","None"])
            st.toggle("Enable Anomaly Detection",    value=True)
            st.toggle("Enable Batch Predictions",    value=True)
            st.toggle("Enable Login Audit Logging",  value=True)

            if st.form_submit_button("Save Settings"):
                st.success("Settings saved successfully!")
