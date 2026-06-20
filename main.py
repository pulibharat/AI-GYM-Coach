import os
import time
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from services.auth.login_wall import render_login_wall
from services.state.session_defaults import initial_session_defaults
from services.config.workout_config import EXERCISE_OPTIONS
from services.tracking.metrics import sync_metrics_update
from services.ui.style_loader import load_css, inject_local_font, inject_webrtc_styles
from services.persistence.exercise_repo import init_db
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from services.vision.exercise_process import VideoProcessorClass
from services.persistence.exercise_repo import get_users_exercises
from groq import Groq
from services.coaching.llm import LLMCoach
from services.coaching.tts import TextToSpeech
from services.coaching.voice_pipeline import VoicePipeline, autoplay_audio

# Load environment variables
load_dotenv()



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

    if "voice_pipeline" not in st.session_state:
        try:
            api_key = os.environ.get("GROQ_API_KEY", "")

            if not api_key and hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                api_key = st.secrets["GROQ_API_KEY"]

            groq_client = Groq(api_key=api_key)
            llm_coach = LLMCoach(groq_client)
            tts = TextToSpeech()
            st.session_state.voice_pipeline = VoicePipeline(llm_coach, tts)
        except Exception as e:
            st.session_state.voice_pipeline = None

    workout_started = st.session_state.get("workout_started", False)

    with st.sidebar:
        st.title("🏋️‍♂️ AI GYM Coach")
        # st.markdown("Your personal workout assistant powered by AI.")

        if st.session_state.username:
            st.caption(f"👤 Login as {st.session_state.username}")

        st.divider()

        st.subheader("Workout Plan")

        if not workout_started:

            plan_exercise = st.selectbox(
                "Exercise", options=EXERCISE_OPTIONS, key="plan_exercise_input")

            plan_sets = st.number_input(
                "Sets", min_value=1, max_value=50, value=3, step=1, key="plan_sets_input")

            plan_reps = st.number_input(
                "Reps per Set", min_value=1, max_value=100, value=10, step=1, key="plan_reps_input")

            st.markdown("")

            start_session_button = st.button(
                "Start Workout", width="stretch", key="start_workout_button")

            # if start_session_button:
            #     st.session_state.exercise_type = plan_exercise
            #     st.session_state.target_sets = int(plan_sets)
            #     st.session_state.reps_per_set = int(plan_reps)
            #     st.session_state.plan_exercise = plan_exercise
            #     st.session_state.plan_sets = int(plan_sets)
            #     st.session_state.plan_reps = int(plan_reps)

            #     st.session_state.reps = 0
            #     st.session_state.sets_completed = 0
            #     st.session_state.current_set_reps = 0
            #     st.session_state.workout_complete = False
            #     st.session_state.workout_started = True
            #     st.session_state.set_cycle_started_at = time.time()

            #     st.session_state.last_saved_sets_completed = 0
            #     st.session_state.last_notified_sets_completed = 0
            #     st.session_state.last_notified_workout_complete = False
            #     st.rerun()
            if start_session_button:
                st.session_state.exercise_type = plan_exercise
                st.session_state.target_sets = int(plan_sets)
                st.session_state.reps_per_set = int(plan_reps)
                st.session_state.reps = 0
                st.session_state.workout_started = True
                st.session_state.set_cycle_started_at = time.time()
                st.session_state.last_saved_sets_completed = 0

                if st.session_state.voice_pipeline:
                    result = st.session_state.voice_pipeline.process_event(
                        event="workout_started",
                        exercise=plan_exercise,
                        metrics={}
                    )

                    if result:
                        st.session_state.audio_to_play, st.session_state.coach_feedback = result
                        autoplay_audio(st.session_state.audio_to_play)

                st.session_state.last_notified_sets_completed = 0
                st.session_state.last_notified_workout_complete = False
                st.rerun()

        else:
            exercise = st.session_state.get("plan_exercise", "N/A")
            sets = st.session_state.get("plan_sets", 0)
            reps = st.session_state.get("plan_reps", 0)

            st.info(f"**{exercise}** -- {sets} Sets of {reps} Reps")

            end_session_btn = st.button(
                "End Workout", key="end_session_button", width="stretch")

            if end_session_btn:
                st.session_state.workout_started = False
                # st.session_state["workout_started"] = False
                # st.session_state["workout_complete"] = True
                # st.success("Workout session ended. Great job!")
                if st.session_state.voice_pipeline:
                    result = st.session_state.voice_pipeline.process_event(
                        event="workout_completed",
                        exercise=exercise,
                        metrics={}
                    )
                    if result:
                        st.session_state.audio_to_play, st.session_state.coach_feedback = result
                st.rerun()

        if workout_started:
            st.divider()

            exercise = st.session_state.get("exercise_type", "N/A")

            total_reps = st.session_state.get("reps")
            current_set_reps = st.session_state.get("current_set_reps")
            reps_per_set = st.session_state.get("reps_per_set")
            sets_completed = st.session_state.get("sets_completed")

            target_sets = st.session_state.get("target_sets")

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

    workout_started = st.session_state.get("workout_started", False)

    # st.write("Welcome to the AI GYM Coach! You are now logged in.")
    # Here you can add the rest of your app's functionality

    st.title("AI Real-time GYM Coach")
    st.markdown("### Real-time pose detection with proactive AI voice coaching")

    # Process newly queued audio
    if st.session_state.get("audio_to_play"):
        autoplay_audio(st.session_state.audio_to_play)

    # Persistently render the audio element while it is active to prevent cutoff
    if st.session_state.get("currently_playing_audio"):
        if time.time() < st.session_state.get("skip_fast_rerun_until", 0):
            st.audio(
                st.session_state.currently_playing_audio,
                format="audio/mp3",
                autoplay=True
            )
        else:
            # Clean up after playback duration ends
            st.session_state.currently_playing_audio = None
            st.session_state.audio_key = None


    if st.session_state.get("coach_feedback"):
        st.markdown("")
        st.success(f"🤖 **Coach:** {st.session_state.coach_feedback}")

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
            rtc_configuration={
                "iceServers": [
                    {"urls": ["stun:stun.l.google.com:19302"]},
                    {
                        "urls": [
                            "turn:openrelay.metered.ca:80",
                            "turn:openrelay.metered.ca:443",
                            "turn:openrelay.metered.ca:443?transport=tcp"
                        ],
                        "username": "openrelayproject",
                        "credential": "openrelayproject"
                    }
                ]
            },
            media_stream_constraints={
                "video": True,
                "audio": False
            },
            async_processing=True
        )

        sync_metrics_update(context)

        if context.state.playing:
            time.sleep(0.25)
            st.rerun()

        inject_webrtc_styles()

        # if st.session_state.get("audio_to_play"):
        #     autoplay_audio(st.session_state.audio_to_play)

        # if context.state.playing:
        #     if time.time() < st.session_state.get("skip_fast_rerun_until", 0):
        #         time.sleep(0.5)
        #     else:
        #         time.sleep(0.25)
        #     st.rerun()

        # inject_webrtc_styles()

        st.divider()

        st.markdown("### Workout History")
        user_id = st.session_state.get("user_id", 0)

        if isinstance(user_id, int):
            history_rows = get_users_exercises(user_id)

            arr = [
                {
                    "Exercise": row['exercise_name'],
                    "Reps": row['reps'],
                    "Sets": row['sets'],
                    "Time (sec)": row['time'],
                    "Date": row['created_at']
                }
                for row in history_rows
            ]

            df = pd.DataFrame(arr)

            if not df.empty:
                df["Date"] = pd.to_datetime(df["Date"]).dt.date
                agg_df = df.groupby(["Exercise", "Date"]).agg({
                    "Reps": 'sum',
                    "Sets": "sum",
                    "Time (sec)": "sum"
                }).reset_index()
                agg_df.index += 1
                st.table(agg_df, border="horizontal")
            else:
                st.info("No workout history found.")


if __name__ == "__main__":
    main()
