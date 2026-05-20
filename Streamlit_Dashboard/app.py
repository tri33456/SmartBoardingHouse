import streamlit as st
from auth import login

from landlord_dashboard import show_landlord_dashboard
from tenant_dashboard import show_tenant_dashboard
from streamlit_autorefresh import st_autorefresh
# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Smart Boarding House",
    layout="wide"
)

# =====================================
# SESSION
# =====================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

# =====================================
# LOGIN PAGE
# =====================================

if not st.session_state.logged_in:

    st.title("🏠 Smart Boarding House")

    st.subheader("Login")
    phone = st.text_input("Phone Number")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        user = login(phone, password)

        if user is not None:

            st.session_state.logged_in = True
            st.session_state.user = user

            st.rerun()

        else:

            st.error("Invalid phone or password")

# =====================================
# DASHBOARD
# =====================================

else:

    user = st.session_state.user
    # =====================================
    # AUTO REFRESH EVERY 5 SECONDS
    # =====================================

    st_autorefresh(
        interval=5000,
        key="dashboard_refresh"
    )
    role = user["role"]

    st.sidebar.title("Smart Boarding House")

    st.sidebar.write(f"User: {user['full_name']}")
    st.sidebar.write(f"Role: {role}")

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.user = None

        st.rerun()

    # =====================================
    # LANDLORD DASHBOARD
    # =====================================

    if role == "landlord":

        show_landlord_dashboard()

    # =====================================
    # TENANT DASHBOARD
    # =====================================

    elif role == "tenant":

        show_tenant_dashboard(user)