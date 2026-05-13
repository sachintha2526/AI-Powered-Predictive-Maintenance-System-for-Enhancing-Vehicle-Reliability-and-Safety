import streamlit as st
import pandas as pd
from datetime import datetime
from maintenance_history import show_maintenance_history

# ─── CSS ─────────────────────────────────────────────────────────────────────
TECH_CSS = """
<style>
.task-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
}
.status-pill {
    padding: 0.2rem 0.6rem; border-radius: 50px; font-size: 0.7rem; font-weight: 700;
}
.status-pending     { background: #ef444422; color: #ef4444; border: 1px solid #ef444444; }
.status-in-progress { background: #3b82f622; color: #3b82f6; border: 1px solid #3b82f644; }
.status-completed   { background: #10b98122; color: #10b981; border: 1px solid #10b98144; }
</style>
"""

def show_technician_dashboard():
    # ─── Mock Data for Tasks ──────────────────────────────────────────────────
    if "tech_tasks" not in st.session_state:
        st.session_state.tech_tasks = [
            {"id": "TK-101", "vehicle": "VH-203", "fault": "Coolant Temp critical", "status": "Pending", "desc": "Check for leaks in the primary radiator hose."},
            {"id": "TK-102", "vehicle": "VH-202", "fault": "Oil Pressure low", "status": "In Progress", "desc": "Possible sensor failure or oil pump issue."},
            {"id": "TK-103", "vehicle": "VH-207", "fault": "Brake system alert", "status": "Pending", "desc": "Front left pad thickness below 3mm."},
        ]

    st.markdown(TECH_CSS, unsafe_allow_html=True)
    
    # ── Sidebar Navigation ────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center;padding:1rem 0;'>
            <div style='font-size:2.5rem'></div>
            <div style='font-weight:800;font-size:1.1rem;color:#f1f5f9;'>Maintenance Technician</div>
            <div style='font-size:0.75rem;color:#64748b;'>Field Operations</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        if st.button("Back to Login / Logout", key="technician_logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 14px; padding: 1rem 1.5rem; margin-bottom: 1.5rem;'>
        <div style='font-size: 1.3rem; font-weight: 800; color: #f1f5f9;'> Assigned Maintenance Tasks</div>
        <div style='font-size: 0.8rem; color: #64748b; margin-top: 4px;'>Assigned to: {st.session_state.get('username','Technician').capitalize()}  •  {datetime.now().strftime("%d %b %Y")}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tasks List ────────────────────────────────────────────────────────────
    for idx, task in enumerate(st.session_state.tech_tasks):
        with st.container():
            st.markdown(f"<div class='task-card'>", unsafe_allow_html=True)
            
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**{task['id']}** &nbsp;·&nbsp; {task['vehicle']}")
                st.markdown(f"#### {task['fault']}")
                st.markdown(f"<span style='color: #94a3b8; font-size: 0.85rem;'>{task['desc']}</span>", unsafe_allow_html=True)
            with c2:
                s_cls = f"status-{task['status'].lower().replace(' ', '-')}"
                st.markdown(f"<div style='text-align:right;'><span class='status-pill {s_cls}'>{task['status'].upper()}</span></div>", unsafe_allow_html=True)
            
            # Checklist & Actions
            with st.expander("Repair Checklist & Logs"):
                st.checkbox("Safety gear equipped", key=f"check1_{idx}")
                st.checkbox("Vehicle isolated & powered down", key=f"check2_{idx}")
                st.checkbox("Primary inspection completed", key=f"check3_{idx}")
                st.checkbox("Fault pinpointed & verified", key=f"check4_{idx}")
                
                st.text_area("Maintenance Logs / Notes", placeholder="Note down your findings here...", key=f"log_{idx}")
                
                # Update status
                st.markdown("**Update Task Status:**")
                bt1, bt2, bt3 = st.columns(3)
                if bt1.button("Pending", key=f"pend_{idx}"):
                    st.session_state.tech_tasks[idx]['status'] = "Pending"
                    st.rerun()
                if bt2.button("In Progress", key=f"prog_{idx}"):
                    st.session_state.tech_tasks[idx]['status'] = "In Progress"
                    st.rerun()
                if bt3.button("Completed", key=f"comp_{idx}"):
                    st.session_state.tech_tasks[idx]['status'] = "Completed"
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

    # ── Uptime Graph ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Your Performance Stats")
    p1, p2, p3 = st.columns(3)
    p1.metric("Tasks Completed", "12", delta="+2 this week")
    p2.metric("Avg Repair Time", "45m", delta="-5m")
    # ── Personal Work History ────────────────────────────────────────────────
    st.markdown("---")
    show_maintenance_history(user_role="Technician")
