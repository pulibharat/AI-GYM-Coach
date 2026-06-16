import os
import streamlit as st
from services.auth.login_wall import render_login_wall
from services.state.session_defaults import initial_session_defaults
from services.config.workout_config import EXERCISE_OPTIONS
from services.ui.style_loader import load_css, inject_local_font, inject_webrtc_styles
from services.persistence.exercise_repo import init_db
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from services.vision.exercise_process import VideoProcessorClass


def main():

    st.set_page_config(
        page_title="AI GYM Coach",
        page_icon="🏋️‍♂️",
        layout="centered",
        initial_sidebar_state="expanded")
    load_css(os.path.join(os.getcwd(), "static", "style.css"))
    inject_local_font(os.path.join(os.getcwd(), "static",
                      "AdobeClean.otf"), "AdobeClean")

    init_db()  # Initialize the database

    if not render_login_wall():
        return  # Stop rendering the rest of the app if not logged in

    initial_session_defaults()  # Set up session state defaults

    workout_started = st.session_state.get("workout_started", False)

    with st.sidebar:
        st.title("🏋️‍♂️ AI GYM Coach")
        # st.markdown("Your personal workout assistant powered by AI.")

        if st.session_state.username:
            st.caption("Logged in as: " + st.session_state.username)

        st.divider()

        st.subheader("Workout Plan")

        if not workout_started:
            st.selectbox("Exercise", options=EXERCISE_OPTIONS,
                         key="plan_exercise")

            st.number_input("Sets", min_value=1, max_value=50,
                            value=3, step=1, key="plan_sets")

            st.number_input("Reps per Set", min_value=1,
                            max_value=100, value=10, step=1, key="plan_reps")

            st.markdown("")

            start_session_button = st.button("Start Workout", width="stretch",
                                             key="start_workout_button")

            if start_session_button:
                st.session_state["workout_started"] = True
                st.rerun()

        else:
            exercise = st.session_state.get("plan_exercise", "N/A")
            sets = st.session_state.get("plan_sets", 0)
            reps = st.session_state.get("plan_reps", 0)

            st.info(f"**{exercise}** - {sets} sets of {reps} reps")

            end_session_btn = st.button(
                "End Workout", key="end_session_button", width="stretch")
            if end_session_btn:
                st.session_state["workout_started"] = False
                st.session_state["workout_complete"] = True
                st.success("Workout session ended. Great job!")
                st.rerun()
        if workout_started:
            st.divider()

            exercise = st.session_state.get("plan_exercise")

            total_reps = st.session_state.get("reps")
            current_set_reps = st.session_state.get("current_set_reps")
            reps_per_set = st.session_state.get("plan_reps")
            sets_completed = st.session_state.get("sets_completed")

            target_sets = st.session_state.get("plan_sets")

            st.subheader("Session Status")

            st.metric("Total-Reps", f"{total_reps}")
            st.metric("Current Set Reps",
                      f"{current_set_reps} / {reps_per_set}")
            st.metric("Sets Completed", f"{sets_completed} / {target_sets}")

            st.divider()

            if exercise == "Squats":
                st.subheader("Squat Metrics")
                st.metric("Knee Angle", f"{st.session_state.knee_angle}°")
                st.metric("Back Angle", f"{st.session_state.back_angle}°")
                st.metric("Depth Status", st.session_state.depth_status)

            elif exercise == "Push-ups":
                st.subheader("Push-up Metrics")
                st.metric("Elbow Angle", f"{st.session_state.elbow_angle}°")
                st.metric("Body Alignment", st.session_state.body_alignment)
                st.metric("Hip Position", st.session_state.hip_status)

            elif exercise == "Biceps Curls (Dumbbell)":
                st.subheader("Curl Metrics")
                st.metric("Elbow Angle", f"{st.session_state.elbow_angle}°")
                st.metric("Shoulder Stability",
                          st.session_state.shoulder_status)
                st.metric("Swing Detection", st.session_state.swing_status)

            elif exercise == "Shoulder Press":
                st.subheader("Shoulder Press Metrics")
                st.metric("Elbow Angle", f"{st.session_state.elbow_angle}°")
                st.metric("Arm Extension", st.session_state.extension_status)
                st.metric("Back Arch", st.session_state.back_arch_status)

            elif exercise == "Lunges":
                st.subheader("Lunge Metrics")
                st.metric("Front Knee Angle",
                          f"{st.session_state.front_knee_angle}°")
                st.metric("Torso Angle", f"{st.session_state.torso_angle}°")
                st.metric("Balance Status", st.session_state.balance_status)

    # st.write("Welcome to the AI GYM Coach! You are now logged in.")
    # Here you can add the rest of your app's functionality

    st.title("AI Real-time GYM Coach")
    st.markdown("### Real-time pose detection with proactive AI voice coaching")

    if not workout_started:
        st.markdown(
            """
            <div style="
                border: 10px dashed #444;
                border-radius: 0px;
                padding: 48px 32px;
                text-align: center;
                color: #888;
                margin-top: 32px;
                margin-bottom: 32px;
            ">
                <h2 style="color:#ccc; margin-bottom:8px;">👈 Set your workout plan</h2>
                <p style="font-size:1.05rem;">
                    Choose your exercise, sets and reps in the sidebar,<br>
                    then click <strong>Start Workout</strong> to activate the camera and AI coach.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:
        context = webrtc_streamer(
            key="exercise-analysis",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=VideoProcessorClass,
            rtc_configuration={"iceServers": [
                {"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints={
                "video": True,
                "audio": False
            },
            async_processing=True
        )

        st.markdown("### Workout History")

        inject_webrtc_styles()


if __name__ == "__main__":
    main()
