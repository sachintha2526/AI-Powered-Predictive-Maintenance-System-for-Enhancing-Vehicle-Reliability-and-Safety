import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# ─── CSS ─────────────────────────────────────────────────────────────────────
PAYMENT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Fault card ── */
.fault-card {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border: 1px solid #334155;
    border-left: 4px solid;
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: .7rem;
}
.fault-title  { font-size:.95rem; font-weight:700; color:#f1f5f9; margin-bottom:.25rem; }
.fault-detail { font-size:.78rem; color:#94a3b8; }

/* ── Recommendation card ── */
.rec-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: .9rem 1.1rem;
    margin-bottom: .5rem;
    display: flex;
    gap: .9rem;
    align-items: flex-start;
}
.rec-icon  { font-size:1.4rem; flex-shrink:0; margin-top:.1rem; }
.rec-title { font-size:.88rem; font-weight:700; color:#f1f5f9; }
.rec-sub   { font-size:.75rem; color:#64748b; margin-top:.15rem; }
.rec-cost  { font-size:.88rem; font-weight:800; color:#38bdf8; white-space:nowrap; }

/* ── Invoice box ── */
.invoice-box {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 1.5rem 1.8rem;
    margin: 1rem 0;
}
.invoice-header {
    display:flex; justify-content:space-between; align-items:flex-start;
    margin-bottom:1.2rem;
}
.invoice-brand { font-size:1.1rem; font-weight:800; color:#38bdf8; }
.invoice-sub   { font-size:.72rem; color:#475569; margin-top:.2rem; }
.invoice-id    { font-size:.8rem; color:#64748b; text-align:right; }
.invoice-row {
    display:flex; justify-content:space-between;
    padding:.45rem 0; border-bottom:1px solid #1e293b;
    font-size:.83rem; color:#94a3b8;
}
.invoice-row.total {
    border-top:2px solid #334155; border-bottom:none;
    margin-top:.5rem; padding-top:.7rem;
    font-size:1rem; font-weight:800; color:#f1f5f9;
}
.invoice-row span:last-child { color:#f1f5f9; font-weight:600; }
.invoice-row.total span:last-child { color:#38bdf8; font-size:1.1rem; }

/* ── Payment method card ── */
.method-card {
    background: #1e293b;
    border: 2px solid #334155;
    border-radius: 14px;
    padding: 1rem 1.2rem;
    cursor: pointer;
    text-align: center;
    transition: border-color .2s, transform .15s;
}
.method-card:hover { border-color:#38bdf8; transform:translateY(-2px); }
.method-card.selected { border-color:#38bdf8; background:#0f172a; }
.method-icon  { font-size:2rem; margin-bottom:.4rem; }
.method-label { font-size:.82rem; font-weight:700; color:#f1f5f9; }
.method-sub   { font-size:.7rem; color:#64748b; margin-top:.2rem; }

/* ── Status badge ── */
.status-badge {
    display:inline-flex; align-items:center; gap:.4rem;
    padding:.3rem .9rem; border-radius:50px;
    font-size:.78rem; font-weight:700;
}

/* ── Section heading ── */
.pay-section-head {
    font-size:.82rem; font-weight:700; color:#64748b;
    text-transform:uppercase; letter-spacing:.7px;
    margin:1.4rem 0 .7rem; border-left:3px solid #38bdf8;
    padding-left:.6rem;
}

/* ── Proceed button override ── */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: .95rem !important;
    padding: .65rem 1.5rem !important;
    transition: opacity .2s, transform .15s !important;
}
.stButton > button:hover {
    opacity: .88 !important;
    transform: translateY(-1px) !important;
}
</style>
"""

# ─── Synthetic maintenance requests ──────────────────────────────────────────
FAULTS = [
    {"id":"F-001","vehicle":"VH-203","severity":"Critical","fault":"Critical Coolant Temperature","detail":"Coolant temp exceeded 235°F — immediate risk of engine seizure.","color":"#ef4444"},
    {"id":"F-002","vehicle":"VH-203","severity":"Warning","fault":"Low Oil Pressure","detail":"Oil pressure at 28 PSI — below safe threshold of 30 PSI.","color":"#f59e0b"},
    {"id":"F-003","vehicle":"VH-206","severity":"Warning","fault":"Irregular Fuel Pressure","detail":"Fuel pressure fluctuating between 31–38 PSI (normal: 43–47 PSI).","color":"#f59e0b"},
]

RECOMMENDATIONS = [
    {"title":"Coolant System Flush & Refill",     "detail":"Full coolant drain, system flush and refill with OEM-spec coolant.","cost":85,  "urgency":"Urgent"},
    {"title":"Thermostat Replacement",            "detail":"Replace faulty thermostat — primary cause of temp spike.","cost":120, "urgency":"Urgent"},
    {"title":"Oil Pressure Sensor Replacement",  "detail":"Replace oil pressure sensor and top-up engine oil to safe level.","cost":65,  "urgency":"High"},
    {"title":"Fuel Injector Cleaning",            "detail":"Professional ultrasonic fuel injector cleaning service.","cost":95,  "urgency":"Medium"},
    {"title":"Full Diagnostic Scan",              "detail":"Comprehensive 50-point engine health diagnostic scan & report.","cost":45,  "urgency":"Recommended"},
]

HISTORY = [
    {"inv":"INV-2891","date":"2026-03-15","desc":"Oil Change + Filter Replacement","amount":95,  "status":"Paid"},
    {"inv":"INV-2756","date":"2026-02-20","desc":"Brake Pad Replacement (Front)",   "amount":180, "status":"Paid"},
    {"inv":"INV-2701","date":"2026-01-28","desc":"Tyre Rotation & Alignment",       "amount":70,  "status":"Paid"},
]

URGENCY_COLORS = {"Urgent":"#ef4444","High":"#f59e0b","Medium":"#3b82f6","Recommended":"#10b981"}

# ─── Session helpers ──────────────────────────────────────────────────────────
def init_payment_state():
    if "pay_selected"  not in st.session_state: st.session_state.pay_selected  = [False]*len(RECOMMENDATIONS)
    if "paid_items"    not in st.session_state: st.session_state.paid_items    = [False]*len(RECOMMENDATIONS)
    if "pay_method"    not in st.session_state: st.session_state.pay_method    = "💳 Credit / Debit Card"
    if "pay_status"    not in st.session_state: st.session_state.pay_status    = "Pending"
    if "pay_confirmed" not in st.session_state: st.session_state.pay_confirmed = False
    if "inv_number"    not in st.session_state: st.session_state.inv_number    = f"INV-{random.randint(3000,3999)}"

# ─── Main Page ────────────────────────────────────────────────────────────────
def show_payment_page():
    st.markdown(PAYMENT_CSS, unsafe_allow_html=True)
    init_payment_state()

    # ── Page header ───────────────────────────────────────────────────────────
    st.markdown("""
    <div style='background:linear-gradient(135deg,#1e293b,#0f172a);
                border:1px solid #334155;border-radius:16px;
                padding:1.3rem 1.6rem;margin-bottom:1.5rem;
                display:flex;justify-content:space-between;align-items:center;'>
        <div>
            <div style='font-size:1.3rem;font-weight:800;color:#f1f5f9;'>Maintenance Request & Payment</div>
            <div style='font-size:.75rem;color:#64748b;margin-top:.3rem;'>
                Vehicle: <strong style='color:#38bdf8'>VH-203</strong> &nbsp;·&nbsp;
                Generated: <strong style='color:#94a3b8'>""" + datetime.now().strftime("%d %b %Y, %I:%M %p") + """</strong>
            </div>
        </div>
        <div style='text-align:right;'>
            <div style='font-size:.72rem;color:#64748b;'>Payment Status</div>
            <span class='status-badge' style='background:""" + ("#10b98122" if st.session_state.pay_status=="Paid" else "#f59e0b22") + """;
                  color:""" + ("#10b981" if st.session_state.pay_status=="Paid" else "#f59e0b") + """;
                  border:1px solid """ + ("#10b98144" if st.session_state.pay_status=="Paid" else "#f59e0b44") + """'>
                """ + ("✅ " if st.session_state.pay_status=="Paid" else "") + st.session_state.pay_status + """
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Two-column layout: left=faults+recs, right=invoice+payment ───────────
    left, right = st.columns([1.1, 1], gap="large")

    # ═══════════════════════════════════════════════════════════════════════════
    # LEFT COLUMN
    # ═══════════════════════════════════════════════════════════════════════════
    with left:

        # ── Detected faults ───────────────────────────────────────────────────
        st.markdown("<div class='pay-section-head'>Detected Engine Faults</div>", unsafe_allow_html=True)
        for f in FAULTS:
            sev_color = "#ef4444" if f["severity"]=="Critical" else "#f59e0b"
            st.markdown(f"""
            <div class='fault-card' style='border-left-color:{f["color"]}'>
                <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:.3rem'>
                    <div class='fault-title'>{f["fault"]}</div>
                    <span style='background:{sev_color}22;color:{sev_color};border:1px solid {sev_color}44;
                                 border-radius:20px;padding:.15rem .65rem;font-size:.7rem;font-weight:700'>
                        {f["severity"]}
                    </span>
                </div>
                <div class='fault-detail'>{f["detail"]}</div>
                <div style='font-size:.7rem;color:#475569;margin-top:.4rem'>Vehicle: {f["vehicle"]} &nbsp;·&nbsp; Fault ID: {f["id"]}</div>
            </div>
            """, unsafe_allow_html=True)

        # ── Repair recommendations ─────────────────────────────────────────────
        st.markdown("<div class='pay-section-head'>Repair Recommendations</div>", unsafe_allow_html=True)
        st.caption("Select the services you want to include in this request:")

        total = 0
        for i, rec in enumerate(RECOMMENDATIONS):
            uc = URGENCY_COLORS.get(rec["urgency"], "#94a3b8")
            is_already_paid = st.session_state.paid_items[i]
            
            if is_already_paid:
                st.markdown(f"""
                <div class='rec-card' style='opacity:0.7; border-left: 4px solid #10b981'>
                    <div style='flex:1'>
                        <div class='rec-title'>{rec["title"]} <span style='color:#10b981; font-size:0.75rem; margin-left:10px;'>✅ PAID</span></div>
                        <div class='rec-sub'>{rec["detail"]}</div>
                    </div>
                    <div class='rec-cost'>${rec["cost"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                check = st.checkbox(f"**{rec['title']}** — ${rec['cost']}",
                                    value=st.session_state.pay_selected[i],
                                    key=f"rec_check_{i}")
                st.session_state.pay_selected[i] = check
                
                if check:
                    total += rec["cost"]
                    st.markdown(f"""
                    <div class='rec-card' style='border-left: 4px solid #38bdf8'>
                        <div style='flex:1'>
                            <div class='rec-title'>{rec["title"]}</div>
                            <div class='rec-sub'>{rec["detail"]}</div>
                            <span style='background:{uc}22;color:{uc};border:1px solid {uc}44;
                                         border-radius:20px;padding:.12rem .55rem;font-size:.68rem;font-weight:700;margin-top:.3rem;display:inline-block'>
                                {rec["urgency"]}
                            </span>
                        </div>
                        <div class='rec-cost'>${rec["cost"]}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # ── Service history ────────────────────────────────────────────────────
        with st.expander("Previous Service History", expanded=False):
            for h in HISTORY:
                sc = "#10b981" if h["status"]=="Paid" else "#f59e0b"
                st.markdown(f"""
                <div style='display:flex;justify-content:space-between;align-items:center;
                            background:#0f172a;border:1px solid #1e293b;border-radius:10px;
                            padding:.55rem .9rem;margin-bottom:.4rem;'>
                    <div>
                        <div style='font-size:.82rem;font-weight:600;color:#f1f5f9'>{h["desc"]}</div>
                        <div style='font-size:.7rem;color:#475569'>{h["inv"]} &nbsp;·&nbsp; {h["date"]}</div>
                    </div>
                    <div style='text-align:right'>
                        <div style='font-size:.9rem;font-weight:800;color:#f1f5f9'>${h["amount"]}</div>
                        <span style='font-size:.68rem;font-weight:700;color:{sc}'>{h["status"]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # RIGHT COLUMN
    # ═══════════════════════════════════════════════════════════════════════════
    with right:

        # ── Invoice ────────────────────────────────────────────────────────────
        st.markdown("<div class='pay-section-head'> Invoice Summary</div>", unsafe_allow_html=True)

        tax     = round(total * 0.08, 2)
        grand   = round(total + tax, 2)
        items   = [(rec["title"], f"${rec['cost']}") for i,rec in enumerate(RECOMMENDATIONS) if st.session_state.pay_selected[i]]

        inv_rows = "".join([f"<div class='invoice-row'><span>{title}</span><span>{cost}</span></div>" for title,cost in items])
        if not items:
            inv_rows = "<div style='color:#475569;font-size:.82rem;text-align:center;padding:.8rem 0'>No services selected.</div>"

        st.markdown(f"""
        <div class='invoice-box'>
            <div class='invoice-header'>
                <div>
                    <div class='invoice-brand'> AI Maintenance</div>
                    <div class='invoice-sub'>Vehicle Reliability & Safety System</div>
                </div>
                <div class='invoice-id'>
                    <div style='font-weight:700;color:#f1f5f9'>{st.session_state.inv_number}</div>
                    <div>Date: {datetime.now().strftime("%d %b %Y")}</div>
                    <div>Due: {(datetime.now()+timedelta(days=7)).strftime("%d %b %Y")}</div>
                </div>
            </div>
            <div style='font-size:.7rem;color:#475569;margin-bottom:.8rem'>
                Client: <strong style='color:#94a3b8'>{st.session_state.get("username","User").capitalize()}</strong>
                &nbsp;·&nbsp; Vehicle: <strong style='color:#94a3b8'>VH-203</strong>
            </div>
            {inv_rows}
            <div class='invoice-row'><span>Subtotal</span><span>${total:.2f}</span></div>
            <div class='invoice-row'><span>Tax (8%)</span><span>${tax:.2f}</span></div>
            <div class='invoice-row total'><span>Total Due</span><span>${grand:.2f}</span></div>
        </div>
        """, unsafe_allow_html=True)

        # ── Export invoice ─────────────────────────────────────────────────────
        inv_df = pd.DataFrame(items, columns=["Service","Cost"])
        inv_df = pd.concat([inv_df,
            pd.DataFrame([["Subtotal", f"${total:.2f}"],["Tax (8%)", f"${tax:.2f}"],["Total", f"${grand:.2f}"]], columns=["Service","Cost"])
        ], ignore_index=True)
        st.download_button("Download Invoice (CSV)",
                           inv_df.to_csv(index=False).encode(),
                           f"{st.session_state.inv_number}.csv", "text/csv",
                           use_container_width=True)

        st.markdown("<div class='pay-section-head'>💳 Payment Method</div>", unsafe_allow_html=True)

        # ── Payment method selector ────────────────────────────────────────────
        methods = ["💳 Credit / Debit Card","🏦 Bank Transfer","📱 Mobile Payment","💰 Cash on Service"]
        pm_cols = st.columns(2)
        for idx, method in enumerate(methods):
            with pm_cols[idx % 2]:
                is_sel = st.session_state.pay_method == method
                border = "#38bdf8" if is_sel else "#334155"
                bg     = "#0f172a" if is_sel else "#1e293b"
                icons  = ["💳","🏦","📱","💰"]
                labels = ["Card","Bank Transfer","Mobile Pay","Cash"]
                subs   = ["Visa, Mastercard, Amex","Direct bank wire","PayPal, Apple Pay","Pay at workshop"]
                st.markdown(f"""
                <div class='method-card' style='border-color:{border};background:{bg}'>
                    <div class='method-icon'>{icons[idx]}</div>
                    <div class='method-label'>{labels[idx]}</div>
                    <div class='method-sub'>{subs[idx]}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Select", key=f"pm_{idx}", use_container_width=True):
                    st.session_state.pay_method = method
                    st.rerun()

        st.markdown(f"""
        <div style='background:#1e293b;border:1px solid #334155;border-radius:10px;
                    padding:.65rem 1rem;margin:.8rem 0;font-size:.82rem;color:#94a3b8;'>
            ✅ Selected: <strong style='color:#38bdf8'>{st.session_state.pay_method}</strong>
        </div>
        """, unsafe_allow_html=True)

        # ── Payment detail form ────────────────────────────────────────────────
        if st.session_state.pay_method == "💳 Credit / Debit Card":
            with st.form("card_payment_form"):
                st.text_input("Cardholder Name", placeholder="e.g. Ashan Perera")
                cc1, cc2 = st.columns([2,1])
                cc1.text_input("Card Number", placeholder="•••• •••• •••• ••••", max_chars=19)
                cc2.text_input("CVV", placeholder="•••", type="password", max_chars=3)
                cd1, cd2 = st.columns(2)
                cd1.text_input("Expiry (MM/YY)", placeholder="MM/YY")
                cd2.selectbox("Card Type", ["Visa","Mastercard","American Express"])
                pay_btn = st.form_submit_button(f"🔒 Pay ${grand:.2f}", use_container_width=True)
                if pay_btn:
                    if grand == 0:
                        st.error("⚠️ Please select at least one service to proceed.")
                    else:
                        # Update specific items to Paid status
                        for i, is_selected in enumerate(st.session_state.pay_selected):
                            if is_selected:
                                st.session_state.paid_items[i] = True
                                st.session_state.pay_selected[i] = False # Uncheck for next time
                        
                        st.session_state.pay_status    = "Paid"
                        st.session_state.pay_confirmed = True
                        st.rerun()

        elif st.session_state.pay_method == "🏦 Bank Transfer":
            st.markdown("""
            <div style='background:#0f172a;border:1px solid #334155;border-radius:12px;padding:1rem 1.2rem;'>
                <div style='font-size:.82rem;color:#94a3b8;margin-bottom:.5rem;'>Transfer funds to the following account:</div>
                <div style='font-size:.85rem;color:#f1f5f9;'><strong>Bank:</strong> Commercial Bank of Ceylon</div>
                <div style='font-size:.85rem;color:#f1f5f9;'><strong>Account Name:</strong> AI Maintenance System (Pvt) Ltd</div>
                <div style='font-size:.85rem;color:#f1f5f9;'><strong>Account No:</strong> 1234-5678-9012</div>
                <div style='font-size:.85rem;color:#f1f5f9;'><strong>Reference:</strong> """ + st.session_state.inv_number + """</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"✅ Mark as Transferred — ${grand:.2f}", use_container_width=True):
                st.session_state.pay_status    = "Paid"
                st.session_state.pay_confirmed = True
                st.rerun()

        elif st.session_state.pay_method == "📱 Mobile Payment":
            st.info("📲 You will be redirected to the mobile payment gateway after confirming.")
            if st.button(f"📱 Proceed to Mobile Pay — ${grand:.2f}", use_container_width=True):
                st.session_state.pay_status    = "Paid"
                st.session_state.pay_confirmed = True
                st.rerun()

        else:  # Cash
            st.info("💰 Please visit your nearest service workshop with your invoice reference.")
            if st.button(f"Confirm Cash Appointment — ${grand:.2f}", use_container_width=True):
                st.session_state.pay_status    = "Pending"
                st.rerun()

        # ── Payment confirmed banner ───────────────────────────────────────────
        if st.session_state.pay_confirmed:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#052e16,#166534);
                        border:1px solid #16a34a;border-radius:14px;
                        padding:1.2rem 1.5rem;margin-top:1rem;text-align:center;'>
                <div style='font-size:2rem;margin-bottom:.4rem'>✅</div>
                <div style='font-size:1.05rem;font-weight:800;color:#4ade80;'>Payment Successful!</div>
                <div style='font-size:.8rem;color:#86efac;margin-top:.4rem;'>
                    Invoice <strong>{st.session_state.inv_number}</strong> — ${grand:.2f} paid via {st.session_state.pay_method}
                </div>
                <div style='font-size:.75rem;color:#4ade80;margin-top:.3rem;'>
                    A maintenance appointment has been scheduled. Our team will contact you shortly.
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Start New Request", use_container_width=True):
                for key in ["pay_selected","pay_method","pay_status","pay_confirmed","inv_number"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
