import streamlit as st
from datetime import datetime, timedelta

def init_alerts():
    if "system_alerts" not in st.session_state:
        st.session_state.system_alerts = [
            {"id": 1, "priority": "High", "icon": "", "msg": "Critical Coolant Temp - VH-203", "time": "2 mins ago", "read": False},
            {"id": 2, "priority": "Medium", "icon": "", "msg": "Low Oil Pressure Warning - VH-202", "time": "15 mins ago", "read": False},
            {"id": 3, "priority": "High", "icon": "", "msg": "Engine Misfire Detected - VH-204", "time": "28 mins ago", "read": False},
            {"id": 4, "priority": "Low", "icon": "", "msg": "Scheduled Service Due - VH-201", "time": "1h ago", "read": False},
            {"id": 5, "priority": "Medium", "icon": "", "msg": "Fuel System Fluctuation - VH-206", "time": "3h ago", "read": True},
        ]

# ─── CSS ─────────────────────────────────────────────────────────────────────
ALERT_CSS = """
<style>
.alert-container {
    padding: 0.8rem;
    border-radius: 12px;
    margin-bottom: 0.6rem;
    border: 1px solid;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: transform 0.2s;
}
.alert-container:hover { transform: translateX(4px); }

.alert-high { background: #ef444415; border-color: #ef444444; color: #fecaca; }
.alert-med  { background: #f59e0b15; border-color: #f59e0b44; color: #fde68a; }
.alert-low  { background: #3b82f615; border-color: #3b82f644; color: #bfdbfe; }

.alert-dot {
    width: 8px; height: 8px; border-radius: 50%; display: inline-block;
}
.dot-high { background: #ef4444; box-shadow: 0 0 10px #ef4444; }
.dot-med  { background: #f59e0b; }
.dot-low  { background: #3b82f6; }

.alert-info { flex: 1; }
.alert-msg  { font-size: 0.85rem; font-weight: 700; }
.alert-time { font-size: 0.72rem; color: #64748b; margin-top: 2px; }

.notif-badge-header {
    background: #ef4444; color: white; padding: 1px 6px;
    border-radius: 50%; font-size: 0.65rem; font-weight: 800;
    position: relative; top: -10px; left: -10px;
}
</style>
"""

def show_alerts_panel(compact=False):
    init_alerts()
    st.markdown(ALERT_CSS, unsafe_allow_html=True)
    
    unread_count = len([a for a in st.session_state.system_alerts if not a["read"]])
    
    if not compact:
        st.markdown(f"#### Notifications ({unread_count} Unread)")
    
    for idx, alert in enumerate(st.session_state.system_alerts):
        # Determine priority style
        priority_class = "alert-high" if alert["priority"] == "High" else "alert-med" if alert["priority"] == "Medium" else "alert-low"
        dot_class = "dot-high" if alert["priority"] == "High" else "dot-med" if alert["priority"] == "Medium" else "dot-low"
        
        # Dim if read
        opacity = "1" if not alert["read"] else "0.6"
        
        with st.container():
            st.markdown(f"""
            <div class='alert-container {priority_class}' style='opacity: {opacity}'>
                <div style='font-size: 1.2rem;'></div>
                <div class='alert-info'>
                    <div class='alert-msg'>{alert['msg']}</div>
                    <div class='alert-time'><span class='alert-dot {dot_class}'></span> {alert['priority']} Priority &nbsp;·&nbsp; {alert['time']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns([4, 1])
            with c2:
                if not alert["read"]:
                    if st.button("Mark Read", key=f"read_{alert['id']}_{idx}"):
                        st.session_state.system_alerts[idx]["read"] = True
                        st.rerun()
                else:
                    if st.button("Dismiss", key=f"dismiss_{alert['id']}_{idx}"):
                        st.session_state.system_alerts.pop(idx)
                        st.rerun()

def get_unread_count():
    init_alerts()
    return len([a for a in st.session_state.system_alerts if not a["read"]])
