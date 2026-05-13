import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# ─── Mock Historical Data ────────────────────────────────────────────────────
def get_mock_history_data():
    today = datetime.today()
    data = [
        {"id": "HT-001", "vehicle": "VH-203", "issue": "Radiator Leak", "date": today - timedelta(days=5), "cost": 450, "status": "Completed", "tech": "Tech Alpha"},
        {"id": "HT-002", "vehicle": "VH-201", "issue": "Oil Filter Replacement", "date": today - timedelta(days=12), "cost": 85, "status": "Completed", "tech": "Tech Beta"},
        {"id": "HT-003", "vehicle": "VH-205", "issue": "Brake Pad Change", "date": today - timedelta(days=20), "cost": 220, "status": "Completed", "tech": "Tech Gamma"},
        {"id": "HT-004", "vehicle": "VH-203", "issue": "Sensor Recalibration", "date": today - timedelta(days=45), "cost": 150, "status": "Completed", "tech": "Tech Alpha"},
        {"id": "HT-005", "vehicle": "VH-210", "issue": "Gearbox Flush", "date": today - timedelta(days=60), "cost": 890, "status": "Failed", "tech": "Tech Delta"},
        {"id": "HT-006", "vehicle": "VH-202", "issue": "Battery Replacement", "date": today - timedelta(days=90), "cost": 310, "status": "Completed", "tech": "Tech Alpha"},
        {"id": "HT-007", "vehicle": "VH-206", "issue": "Turbocharger Repair", "date": today - timedelta(days=120), "cost": 1200, "status": "Completed", "tech": "Tech Beta"},
        {"id": "HT-008", "vehicle": "VH-207", "issue": "Suspension Alignment", "date": today - timedelta(days=150), "cost": 400, "status": "Completed", "tech": "Tech Gamma"},
    ]
    return pd.DataFrame(data)

# ─── CSS ─────────────────────────────────────────────────────────────────────
HIST_CSS = """
<style>
.hist-card {
    background: #0f172a; border: 1px solid #1e293b; border-radius: 10px;
    padding: 1rem; margin-bottom: 0.8rem;
}
.cost-tag { color: #10b981; font-weight: 700; }
.status-tag { 
    background: #334155; padding: 2px 8px; border-radius: 4px; 
    font-size: 0.7rem; color: #f1f5f9; text-transform: uppercase;
}
</style>
"""

def show_maintenance_history(user_role="Admin"):
    st.markdown(HIST_CSS, unsafe_allow_html=True)
    df = get_mock_history_data()

    st.markdown(f"###  Maintenance History Registry ({user_role} View)")
    
    # ── Filters & Search ─────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([2, 1, 1])
    search_query = c1.text_input("Search Vehicle ID", placeholder="Ex: VH-203")
    status_filter = c2.selectbox("Repair Status", ["All", "Completed", "Failed"])
    date_range = c3.date_input("Date Range", [df["date"].min(), df["date"].max()])

    # Filtering Logic
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[filtered_df["vehicle"].str.contains(search_query, case=False)]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["status"] == status_filter]
    
    # ── Analytics & Timeline ─────────────────────────────────────────────────
    st.markdown("####  Timeline Analysis & Trends")
    fig_timeline = px.scatter(filtered_df, x="date", y="cost", color="status",
                              size="cost", hover_data=["vehicle", "issue"],
                              title="Repair Incidents over time by Cost",
                              color_discrete_map={"Completed": "#10b981", "Failed": "#ef4444"})
    fig_timeline.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#94a3b8")
    st.plotly_chart(fig_timeline, use_container_width=True)

    # ── Data Table ───────────────────────────────────────────────────────────
    st.markdown("####  Service Logs")
    
    # Advanced styling for the table
    def style_status(val):
        color = '#10b981' if val == 'Completed' else '#ef4444'
        return f'color: {color}; font-weight: bold'

    # Prepare display dataframe
    display_df = filtered_df.copy()
    if user_role == "Technician":
        if "tech" in display_df.columns:
            display_df = display_df.drop(columns=["tech"])

    st.dataframe(
        display_df.style.applymap(style_status, subset=['status'])
        .format({"cost": "${:.2f}", "date": lambda x: x.strftime("%Y-%m-%d")}),
        use_container_width=True
    )

    # Summary Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Repair Cost", f"${filtered_df['cost'].sum():,.2f}")
    m2.metric("Total Jobs", len(filtered_df))
    m3.metric("Avg Cost per Job", f"${filtered_df['cost'].mean():,.2f}")
