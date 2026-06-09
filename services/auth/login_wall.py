import streamlit as st


def render_login_wall():

    if st.session_state.get("user_id") is not None:
        return True  # User is already logged in

    st.title("🏋️‍♂️ AI Real-time GYM Trainer")
    st.markdown("### Welcome! Please enter a username to start.")

    with st.form("login_form", clear_on_submit=False):
        st.write("Please log in to access the AI GYM Coach features.")

        username = st.text_input("Name (Unique)", placeholder="puli bharat")
        submit_button = st.form_submit_button(
            "Start Coaching", width="stretch")

        if submit_button:
            # Here you would normally validate the username and password
            # For demonstration, we will just set a dummy user_id
            if not username:  # Simple check for non-empty field
                st.error("Please enter your name.")
                return False

            st.session_state["username"] = username  # Set a dummy user ID
            st.session_state["user_id"] = "1"  # Set a dummy user ID
            st.success("Logged in successfully!")

            st.rerun()  # Rerun to update the UI after form submission

    return False  # User is not logged in
