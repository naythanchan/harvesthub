import streamlit as st
from auth import authentication
from dashboard import dashboard
from firebase_config import db

# ✅ Properly initialize session state variables at the start
if "authenticated" not in st.session_state:
    authentication()
else:
    dashboard()
