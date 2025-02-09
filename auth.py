import streamlit as st
from firebase_config import auth, db


def login():
    """Handles user login and session management."""
    st.subheader("Login to HarvestHub")

    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email and password:
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                user_info = (
                    db.child("users")
                    .child(user["localId"])
                    .child("user_info")
                    .get()
                    .val()
                )

                # Store login info in session state
                st.session_state.authenticated = True
                st.session_state.user_info = user_info
                st.session_state.localId = user["localId"]
                st.success("Login successful! Redirecting...")
                st.rerun()

            except Exception as e:
                st.error(f"Login failed: {e}")
        else:
            st.error("Please enter both email and password.")


def signup():
    """Handles user sign-up."""
    st.subheader("Sign Up for HarvestHub")

    name = st.text_input("Name")
    location = st.text_input("Location (County, State)")
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        if name and location and email and password:
            try:
                user = auth.create_user_with_email_and_password(email, password)
                user_data = {"name": name, "location": location, "email": email}
                db.child("users").child(user["localId"]).child("user_info").set(
                    user_data
                )
                st.success("Account created! You can now log in.")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please fill out all fields.")


def authentication():
    """Main authentication function to switch between login and sign-up."""
    st.title("HarvestHub 🌱")

    option = st.radio("Choose an option:", ("Login", "Sign Up"))

    if option == "Login":
        login()
    else:
        signup()
