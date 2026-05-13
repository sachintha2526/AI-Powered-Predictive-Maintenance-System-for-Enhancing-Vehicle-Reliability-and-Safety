import streamlit as st
import pandas as pd
from datetime import datetime

# ─── Default users stored in session state ────────────────────────────────────
DEFAULT_USERS = [
    {"id": "U101", "name": "Ashan Perera",       "username": "ashan",    "email": "ashan@maint.ai",    "role": "Manager",    "status": "Active",   "joined": "2024-01-10"},
    {"id": "U102", "name": "Nirosh Silva",        "username": "nirosh",   "email": "nirosh@maint.ai",   "role": "Engineer",   "status": "Active",   "joined": "2024-02-04"},
    {"id": "U103", "name": "Kamal Fernando",      "username": "kamal",    "email": "kamal@maint.ai",    "role": "Technician", "status": "Active",   "joined": "2024-03-01"},
    {"id": "U104", "name": "Suresh Bandara",      "username": "suresh",   "email": "suresh@maint.ai",   "role": "Manager",    "status": "Active",   "joined": "2024-03-26"},
    {"id": "U105", "name": "Dilani Jayawardena",  "username": "dilani",   "email": "dilani@maint.ai",   "role": "Engineer",   "status": "Inactive", "joined": "2024-04-20"},
    {"id": "U106", "name": "Ruwan Herath",        "username": "ruwan",    "email": "ruwan@maint.ai",    "role": "Technician", "status": "Active",   "joined": "2024-05-15"},
    {"id": "U107", "name": "Thilini Mendis",      "username": "thilini",  "email": "thilini@maint.ai",  "role": "Manager",    "status": "Active",   "joined": "2024-06-09"},
    {"id": "U108", "name": "Kasun Ranasinghe",    "username": "kasun",    "email": "kasun@maint.ai",    "role": "Engineer",   "status": "Active",   "joined": "2024-07-03"},
    {"id": "U109", "name": "Nimal Wijesinghe",    "username": "nimal",    "email": "nimal@maint.ai",    "role": "Technician", "status": "Inactive", "joined": "2024-07-28"},
    {"id": "U110", "name": "Priya Kumari",        "username": "priya",    "email": "priya@maint.ai",    "role": "Engineer",   "status": "Active",   "joined": "2024-08-22"},
]

ROLES   = ["Manager", "Engineer", "Technician"]
STATUSES = ["Active", "Inactive"]

ROLE_COLORS   = {"Manager": "#38bdf8", "Engineer": "#818cf8", "Technician": "#10b981"}
STATUS_COLORS = {"Active": "#10b981",  "Inactive": "#ef4444"}

# ─── CSS ─────────────────────────────────────────────────────────────────────
UM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.um-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}
.um-title {
    font-size: 1.25rem; font-weight: 800; color: #f1f5f9;
    border-left: 4px solid #38bdf8; padding-left: .7rem;
    margin-bottom: 1.2rem;
}
.um-kpi {
    background: #0f172a; border: 1px solid #334155;
    border-radius: 12px; padding: .85rem 1.1rem;
    text-align: center;
}
.um-kpi-val  { font-size: 1.8rem; font-weight: 800; color: #f1f5f9; }
.um-kpi-lbl  { font-size: .72rem; color: #64748b; text-transform:uppercase; letter-spacing:.5px; }

/* ── User row card ── */
.user-row {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: .75rem 1.1rem;
    margin-bottom: .5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: border-color .2s;
}
.user-row:hover { border-color: #38bdf8; }
.avatar {
    width: 40px; height: 40px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 1rem; flex-shrink: 0; color: #0f172a;
}
.user-name  { font-size: .9rem;  font-weight: 700; color: #f1f5f9; }
.user-email { font-size: .75rem; color: #64748b; }
.role-badge {
    border-radius: 20px; padding: .22rem .7rem;
    font-size: .72rem; font-weight: 700; white-space:nowrap;
}
.status-badge {
    border-radius: 20px; padding: .22rem .7rem;
    font-size: .72rem; font-weight: 700; white-space:nowrap;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 9px !important;
    font-size: .82rem !important;
    font-weight: 600 !important;
    padding: .4rem .9rem !important;
    transition: opacity .2s, transform .15s !important;
}
.stButton > button:hover { opacity:.85 !important; transform:translateY(-1px) !important; }

/* ── Form ── */
.stTextInput > label, .stSelectbox > label {
    font-size:.78rem; font-weight:600; color:#94a3b8;
    text-transform:uppercase; letter-spacing:.4px;
}
.stTextInput > div > div > input {
    background:#0f172a !important; border:1.5px solid #334155 !important;
    border-radius:10px !important; color:#f1f5f9 !important;
}
.stTextInput > div > div > input:focus { border-color:#38bdf8 !important; }
.stSelectbox > div > div {
    background:#0f172a !important; border:1.5px solid #334155 !important;
    border-radius:10px !important; color:#f1f5f9 !important;
}
.stExpander { background:#1e293b !important; border:1px solid #334155 !important; border-radius:12px !important; }
</style>
"""

# ─── Helpers ──────────────────────────────────────────────────────────────────
def init_users():
    if "um_users" not in st.session_state:
        st.session_state.um_users = DEFAULT_USERS.copy()
    if "um_edit_id" not in st.session_state:
        st.session_state.um_edit_id = None
    if "um_confirm_delete" not in st.session_state:
        st.session_state.um_confirm_delete = None

def get_users() -> list:
    return st.session_state.um_users

def next_id() -> str:
    ids = [int(u["id"][1:]) for u in get_users()]
    return f"U{max(ids)+1}" if ids else "U101"

def avatar_color(role: str) -> str:
    return ROLE_COLORS.get(role, "#64748b")

def add_user(name, username, email, role, status):
    get_users().append({
        "id":       next_id(),
        "name":     name,
        "username": username,
        "email":    email,
        "role":     role,
        "status":   status,
        "joined":   datetime.today().strftime("%Y-%m-%d"),
    })

def update_user(uid, name, username, email, role, status):
    for u in get_users():
        if u["id"] == uid:
            u.update({"name":name,"username":username,"email":email,"role":role,"status":status})
            break

def delete_user(uid):
    st.session_state.um_users = [u for u in get_users() if u["id"] != uid]

# ─── Main Interface ────────────────────────────────────────────────────────────
def show_user_management():
    st.markdown(UM_CSS, unsafe_allow_html=True)
    init_users()

    st.markdown("<div class='um-title'> User Management</div>", unsafe_allow_html=True)

    # ── KPI strip ─────────────────────────────────────────────────────────────
    users = get_users()
    k1, k2, k3, k4, k5 = st.columns(5)
    kpi_data = [
        (k1, len(users),                                               "Total Users",   "#38bdf8"),
        (k2, sum(u["status"]=="Active"   for u in users),             "Active",        "#10b981"),
        (k3, sum(u["status"]=="Inactive" for u in users),             "Inactive",      "#ef4444"),
        (k4, sum(u["role"]=="Engineer"   for u in users),             "Engineers",     "#818cf8"),
        (k5, sum(u["role"]=="Technician" for u in users),             "Technicians",   "#10b981"),
    ]
    for col, val, lbl, clr in kpi_data:
        with col:
            st.markdown(f"""
            <div class='um-kpi' style='border-top:3px solid {clr};'>
                <div class='um-kpi-val' style='color:{clr}'>{val}</div>
                <div class='um-kpi-lbl'>{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Search + Filter row ───────────────────────────────────────────────────
    fc1, fc2, fc3, fc4 = st.columns([3, 1, 1, 1])
    search     = fc1.text_input("🔍 Search", placeholder="Search by name, username or email…", label_visibility="collapsed")
    role_filt  = fc2.selectbox("Role",   ["All Roles"]   + ROLES,    label_visibility="collapsed")
    stat_filt  = fc3.selectbox("Status", ["All Statuses"]+ STATUSES, label_visibility="collapsed")
    sort_by    = fc4.selectbox("Sort by",["Name","Role","Joined"],    label_visibility="collapsed")

    # ── Add User expander ─────────────────────────────────────────────────────
    with st.expander("Add New User", expanded=False):
        with st.form("add_user_form", clear_on_submit=True):
            a1, a2 = st.columns(2)
            a_name    = a1.text_input("Full Name")
            a_uname   = a2.text_input("Username")
            a3, a4    = st.columns(2)
            a_email   = a3.text_input("Email Address")
            a_role    = a4.selectbox("Role", ROLES)
            a5, a6    = st.columns(2)
            a_status  = a5.selectbox("Status", STATUSES)
            a_pwd     = a6.text_input("Password", type="password")

            submitted = st.form_submit_button("✅ Create User", use_container_width=True)
            if submitted:
                if not a_name or not a_uname or not a_email:
                    st.error("⚠️ Name, username and email are required.")
                elif any(u["username"] == a_uname for u in get_users()):
                    st.error(f"❌ Username '{a_uname}' is already taken.")
                else:
                    add_user(a_name, a_uname, a_email, a_role, a_status)
                    st.success(f"✅ User **{a_name}** created successfully!")
                    st.rerun()

    st.markdown("---")

    # ── Filter + sort users ───────────────────────────────────────────────────
    visible = get_users()
    if search:
        q = search.lower()
        visible = [u for u in visible if q in u["name"].lower()
                   or q in u["username"].lower() or q in u["email"].lower()]
    if role_filt != "All Roles":
        visible = [u for u in visible if u["role"] == role_filt]
    if stat_filt != "All Statuses":
        visible = [u for u in visible if u["status"] == stat_filt]
    if sort_by == "Name":
        visible = sorted(visible, key=lambda u: u["name"])
    elif sort_by == "Role":
        visible = sorted(visible, key=lambda u: u["role"])
    else:
        visible = sorted(visible, key=lambda u: u["joined"], reverse=True)

    # ── Column headers ────────────────────────────────────────────────────────
    h0, h1, h2, h3, h4, h5, h6 = st.columns([.4, 2, 1.3, 1.8, 1, 1, 1.6])
    for col, label in zip([h0,h1,h2,h3,h4,h5,h6],
                          ["","User","Username","Email","Role","Status","Actions"]):
        col.markdown(f"<span style='font-size:.72rem;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:.5px'>{label}</span>",
                     unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#334155;margin:.4rem 0 .6rem'>", unsafe_allow_html=True)

    # ── User rows ─────────────────────────────────────────────────────────────
    if not visible:
        st.info("No users match the current filters.")
    else:
        for u in visible:
            c0, c1, c2, c3, c4, c5, c6 = st.columns([.4, 2, 1.3, 1.8, 1, 1, 1.6])
            clr = avatar_color(u["role"])

            # Avatar
            c0.markdown(f"""
            <div class='avatar' style='background:{clr};'>
                {u["name"][0].upper()}
            </div>""", unsafe_allow_html=True)

            # Name
            c1.markdown(f"""
            <div class='user-name'>{u["name"]}</div>
            <div class='user-email'>Joined {u["joined"]}</div>""", unsafe_allow_html=True)

            c2.markdown(f"<div style='color:#94a3b8;font-size:.85rem;padding-top:.45rem'>`{u['username']}`</div>", unsafe_allow_html=True)
            c3.markdown(f"<div style='color:#94a3b8;font-size:.82rem;padding-top:.45rem'>{u['email']}</div>", unsafe_allow_html=True)

            # Role badge
            rc = ROLE_COLORS.get(u["role"], "#94a3b8")
            c4.markdown(f"<div style='padding-top:.35rem'><span class='role-badge' style='background:{rc}22;color:{rc};border:1px solid {rc}44'>{u['role']}</span></div>", unsafe_allow_html=True)

            # Status badge
            sc = STATUS_COLORS.get(u["status"], "#94a3b8")
            c5.markdown(f"<div style='padding-top:.35rem'><span class='status-badge' style='background:{sc}22;color:{sc};border:1px solid {sc}44'>{u['status']}</span></div>", unsafe_allow_html=True)

            # Action buttons
            btn_e, btn_d = c6.columns(2)
            if btn_e.button("Edit", key=f"edit_{u['id']}", help="Edit user"):
                st.session_state.um_edit_id = u["id"]
                st.session_state.um_confirm_delete = None

            if btn_d.button("Delete", key=f"del_{u['id']}", help="Delete user"):
                st.session_state.um_confirm_delete = u["id"]
                st.session_state.um_edit_id = None

            # ── Inline delete confirmation ────────────────────────────────
            if st.session_state.um_confirm_delete == u["id"]:
                with st.container():
                    st.warning(f"⚠️ Are you sure you want to delete **{u['name']}**?")
                    dc1, dc2, _ = st.columns([1, 1, 4])
                    if dc1.button("✅ Confirm", key=f"conf_{u['id']}"):
                        delete_user(u["id"])
                        st.session_state.um_confirm_delete = None
                        st.rerun()
                    if dc2.button("❌ Cancel", key=f"canc_{u['id']}"):
                        st.session_state.um_confirm_delete = None
                        st.rerun()

            # ── Inline edit form ──────────────────────────────────────────
            if st.session_state.um_edit_id == u["id"]:
                with st.expander(f"✏️ Editing — {u['name']}", expanded=True):
                    with st.form(f"edit_form_{u['id']}"):
                        e1, e2 = st.columns(2)
                        e_name   = e1.text_input("Full Name",     value=u["name"])
                        e_uname  = e2.text_input("Username",      value=u["username"])
                        e3, e4   = st.columns(2)
                        e_email  = e3.text_input("Email Address", value=u["email"])
                        e_role   = e4.selectbox("Role",   ROLES,    index=ROLES.index(u["role"]))
                        e5, e6   = st.columns(2)
                        e_status = e5.selectbox("Status", STATUSES, index=STATUSES.index(u["status"]))
                        e6.text_input("New Password (optional)", type="password")

                        sb1, sb2 = st.columns(2)
                        if sb1.form_submit_button("Save Changes", use_container_width=True):
                            update_user(u["id"], e_name, e_uname, e_email, e_role, e_status)
                            st.session_state.um_edit_id = None
                            st.rerun()
                        if sb2.form_submit_button("Cancel", use_container_width=True):
                            st.session_state.um_edit_id = None
                            st.rerun()

            st.markdown("<hr style='border-color:#1e293b;margin:.3rem 0'>", unsafe_allow_html=True)

    # ── Bulk export ───────────────────────────────────────────────────────────
    st.markdown("---")
    ex1, ex2, _ = st.columns([1, 1, 3])
    export_df = pd.DataFrame(get_users()).drop(columns=["id"])
    ex1.download_button("Export All Users (CSV)",
                        export_df.to_csv(index=False).encode(),
                        "users_export.csv", "text/csv",
                        use_container_width=True)
    filtered_df = pd.DataFrame(visible).drop(columns=["id"]) if visible else export_df
    ex2.download_button("Export Filtered View (CSV)",
                        filtered_df.to_csv(index=False).encode(),
                        "users_filtered.csv", "text/csv",
                        use_container_width=True)
