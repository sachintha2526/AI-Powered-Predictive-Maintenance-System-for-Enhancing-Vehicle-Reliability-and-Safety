import streamlit as st
import pandas as pd
from datetime import datetime, time

# ─── Mock Data for Booking ────────────────────────────────────────────────────
VEHICLES = ["VH-201 (Truck)", "VH-202 (Bus)", "VH-203 (Van)", "VH-204 (Car)"]
TECHNICIANS = ["Kamal Fernando", "Ruwan Herath", "Nimal Wijesinghe", "Priya Kumari"]

# ─── CSS Styling ─────────────────────────────────────────────────────────────
BOOKING_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.booking-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}
.booking-header {
    font-size: 1.5rem; font-weight: 800; color: #f1f5f9;
    margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;
}
.booking-section-title {
    font-size: 0.9rem; font-weight: 700; color: #38bdf8;
    text-transform: uppercase; letter-spacing: 0.8px;
    margin: 1.5rem 0 0.8rem;
}
.confirmation-panel {
    background: #0f172a;
    border: 1px solid #10b981;
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 1.5rem;
    animation: fadeIn 0.5s ease-out;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.conf-title {
    color: #10b981; font-size: 1.1rem; font-weight: 700;
    margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.5rem;
}
.conf-item {
    font-size: 0.9rem; color: #94a3b8; margin-bottom: 0.4rem;
}
.conf-value {
    color: #f1f5f9; font-weight: 600;
}
</style>
"""

def show_service_booking():
    st.markdown(BOOKING_CSS, unsafe_allow_html=True)
    
    # Init session state for booking
    if "booking_confirmed" not in st.session_state:
        st.session_state.booking_confirmed = False
    if "last_booking" not in st.session_state:
        st.session_state.last_booking = None

    st.markdown("<div class='booking-header'> Service Booking UI</div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='booking-card'>", unsafe_allow_html=True)
        
        # ── Vehicle and Issue ───────────────────────────────────────────────
        st.markdown("<div class='booking-section-title'>Vehicle & Issue Details</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            vehicle = st.selectbox("Select Vehicle", VEHICLES, help="Select the vehicle that needs maintenance.")
        with col2:
            tech = st.selectbox("Assign Technician", TECHNICIANS, help="Choose an available technician.")
            
        issue = st.text_area("Problem Description", placeholder="Describe the issues or symptoms in detail...", height=100)
        
        # ── Scheduling ──────────────────────────────────────────────────────
        st.markdown("<div class='booking-section-title'>Schedule Maintenance</div>", unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        with col3:
            book_date = st.date_input("Preferred Date", min_value=datetime.today())
        with col4:
            book_time = st.time_input("Preferred Time", value=time(9, 0))
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ── Action ──────────────────────────────────────────────────────────
        if st.button("Confirm Service Booking", use_container_width=True):
            if not issue:
                st.error("Please provide a description of the issue.")
            else:
                booking_details = {
                    "vehicle": vehicle,
                    "issue": issue,
                    "date": book_date.strftime("%A, %d %B %Y"),
                    "time": book_time.strftime("%I:%M %p"),
                    "tech": tech,
                    "ref": f"BK-{datetime.now().strftime('%M%S')}"
                }
                st.session_state.last_booking = booking_details
                st.session_state.booking_confirmed = True
        
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Confirmation Panel ────────────────────────────────────────────────────
    if st.session_state.booking_confirmed and st.session_state.last_booking:
        b = st.session_state.last_booking
        st.markdown(f"""
        <div class='confirmation-panel'>
            <div class='conf-title'>✅ Booking Confirmed Successfully!</div>
            <div class='conf-item'>Reference Number: <span class='conf-value'>{b['ref']}</span></div>
            <div class='conf-item'>Vehicle: <span class='conf-value'>{b['vehicle']}</span></div>
            <div class='conf-item'>Description: <span class='conf-value'>{b['issue']}</span></div>
            <div class='conf-item'>Scheduled For: <span class='conf-value'>{b['date']} at {b['time']}</span></div>
            <div class='conf-item'>Assigned Technician: <span class='conf-value'>{b['tech']}</span></div>
            <div style='font-size: 0.75rem; color: #64748b; margin-top: 1rem; font-style: italic;'>
                * A confirmation email has been sent to the service department.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Create Another Booking"):
            st.session_state.booking_confirmed = False
            st.rerun()
