import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from notifications import show_alerts_panel
from maintenance_history import show_maintenance_history
from report_generation import show_report_generation
from train_model import generate_sample_data, preprocess_data, train_model

# ─── Mock Data for Manager ────────────────────────────────────────────────────
VEHICLES_DATA = pd.DataFrame({
    "Vehicle ID":  ["VH-201", "VH-202", "VH-203", "VH-204", "VH-205", "VH-206", "VH-207", "VH-208"],
    "Type":        ["Truck", "Bus", "Van", "Car", "Truck", "Bus", "Car", "Van"],
    "Status":      ["Normal", "Warning", "Normal", "Fault", "Normal", "Normal", "Warning", "Normal"],
    "Health %":    [94, 62, 88, 31, 97, 85, 70, 91],
    "Uptime":      ["99%", "82%", "94%", "45%", "99%", "91%", "88%", "96%"]
})

COST_DATA = pd.DataFrame({
    "Month": ["Jan", "Feb", "Mar", "Apr"],
    "Maintenance Cost": [4500, 5200, 4800, 6100],
    "Repair Budget": [8000, 8000, 8000, 8000]
})

# ─── CSS ─────────────────────────────────────────────────────────────────────
MANAGER_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.manager-card {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.kpi-title { font-size: 0.8rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
.kpi-value { font-size: 2rem; font-weight: 800; color: #f1f5f9; margin: 0.5rem 0; }
.kpi-subtitle { font-size: 0.75rem; color: #64748b; }

.status-indicator {
    padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.75rem; font-weight: 700;
}
.status-normal  { background: #10b98122; color: #10b981; border: 1px solid #10b98144; }
.status-warning { background: #f59e0b22; color: #f59e0b; border: 1px solid #f59e0b44; }
.status-fault   { background: #ef444422; color: #ef4444; border: 1px solid #ef444444; }
</style>
"""

def show_manager_dashboard():
    st.markdown(MANAGER_CSS, unsafe_allow_html=True)
    
    # ── Sidebar Navigation ────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center;padding:1rem 0 1.5rem;'>
            <div style='font-size:2.5rem'></div>
            <div style='font-weight:800;font-size:1.1rem;color:#f1f5f9;'>Fleet Manager</div>
            <div style='font-size:0.75rem;color:#64748b;'>Operational Dashboard</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("Back to Login / Logout", key="manager_logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #1e293b, #0f172a); border-bottom: 1px solid #334155; border-radius: 14px; padding: 1rem 1.5rem; margin-bottom: 1.5rem;'>
        <div style='font-size: 1.4rem; font-weight: 800; color: #f1f5f9;'> Fleet Management Overview</div>
        <div style='font-size: 0.8rem; color: #64748b; margin-top: 4px;'>Manager Console  •  {datetime.now().strftime("%A, %d %B %Y")}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class='manager-card' style='border-top: 4px solid #38bdf8;'>
            <div class='kpi-title'>Total Assets</div>
            <div class='kpi-value'>08</div>
            <div class='kpi-subtitle'>Active Vehicles</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class='manager-card' style='border-top: 4px solid #10b981;'>
            <div class='kpi-title'>Fleet Health</div>
            <div class='kpi-value'>84%</div>
            <div class='kpi-subtitle'>Average Score</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class='manager-card' style='border-top: 4px solid #ef4444;'>
            <div class='kpi-title'>Critical Alerts</div>
            <div class='kpi-value'>01</div>
            <div class='kpi-subtitle'>Requires Attention</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class='manager-card' style='border-top: 4px solid #f59e0b;'>
            <div class='kpi-title'>Repair Costs</div>
            <div class='kpi-value'>$6.1k</div>
            <div class='kpi-subtitle'>MTD Spending</div>
        </div>""", unsafe_allow_html=True)

    # ── Charts ────────────────────────────────────────────────────────────────
    c1, c2 = st.columns([1, 1])
    
    with c1:
        # Risk levels pie chart
        status_counts = VEHICLES_DATA["Status"].value_counts()
        fig_risk = px.pie(
            values=status_counts.values, 
            names=status_counts.index, 
            title="Fleet Risk Distribution",
            color=status_counts.index,
            color_discrete_map={"Normal": "#10b981", "Warning": "#f59e0b", "Fault": "#ef4444"},
            hole=0.6
        )
        fig_risk.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
        st.plotly_chart(fig_risk, use_container_width=True)

    with c2:
        # Cost trend chart
        fig_cost = go.Figure()
        fig_cost.add_trace(go.Bar(x=COST_DATA["Month"], y=COST_DATA["Maintenance Cost"], name="Actual Cost", marker_color="#38bdf8"))
        fig_cost.add_trace(go.Scatter(x=COST_DATA["Month"], y=COST_DATA["Repair Budget"], name="Repair Budget", line=dict(color="#ef4444", dash='dash')))
        fig_cost.update_layout(
            title="Maintenance Cost vs Budget",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color="#94a3b8",
            xaxis=dict(gridcolor="#1e293b"), yaxis=dict(gridcolor="#1e293b")
        )
        st.plotly_chart(fig_cost, use_container_width=True)

    # ── Vehicle Health Details ───────────────────────────────────────────────
    st.markdown("<div style='font-size: 1rem; font-weight: 700; color: #94a3b8; margin: 1rem 0;'> Vehicle Health & Performance</div>", unsafe_allow_html=True)
    
    for _, row in VEHICLES_DATA.iterrows():
        status_class = "status-normal" if row["Status"] == "Normal" else "status-warning" if row["Status"] == "Warning" else "status-fault"
        
        with st.container():
            st.markdown(f"""
            <div style='background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 1rem; margin-bottom: 0.5rem; display: flex; align-items: center; justify-content: space-between;'>
                <div style='flex: 1;'>
                    <div style='font-weight: 700; color: #f1f5f9;'>{row["Vehicle ID"]} <span style='font-weight: 400; color: #64748b; font-size: 0.8rem;'>({row["Type"]})</span></div>
                    <div style='font-size: 0.75rem; color: #94a3b8; margin-top: 4px;'>Uptime: {row["Uptime"]}</div>
                </div>
                <div style='flex: 2; margin: 0 2rem;'>
                    <div style='font-size: 0.7rem; color: #64748b; margin-bottom: 4px; display: flex; justify-content: space-between;'>
                        <span>Health Indicator</span>
                        <span>{row["Health %"]}%</span>
                    </div>
                </div>
                <div style='flex: 0; text-align: right;'>
                    <span class='status-indicator {status_class}'>{row["Status"].upper()}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            # Add progress bar separately as it doesn't work inside HTML markdown
            st.progress(row["Health %"] / 100.0)

    # ── Alerts Section ────────────────────────────────────────────────────────
    st.markdown("---")
    # ── History Section ───────────────────────────────────────────────────────
    st.markdown("---")
    show_maintenance_history(user_role="Manager")

    # ── Professional Reporting Section ──────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Advanced Fleet Analytics & Reporting")
    # Ensure sensor data exists for reporting
    if 'df' not in st.session_state:
        df_temp = generate_sample_data(n_samples=200)
        st.session_state.df = preprocess_data(df_temp)
        model, scaler, metrics = train_model(st.session_state.df)
        st.session_state.metrics = metrics
        st.session_state.model = model
        st.session_state.scaler = scaler
    
    show_report_generation(st.session_state.df, st.session_state.metrics)

