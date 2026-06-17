# import os
# import cv2  # Drawing on frames
# import av  # Video frames for Streamlit
# import numpy as np
# import mediapipe as mp  # Pose detection
# import threading  # Safe shared data
# from streamlit_webrtc import VideoProcessorBase
# from mediapipe.tasks import python
# from mediapipe.tasks.python import vision
# from detectors.squat import SquatDetector
# from detectors.pushup import PushUpDetector
# from detectors.biceps_curl import BicepsCurlDetector
# from detectors.shoulder_press import ShoulderPressDetector
# from detectors.lunges import LungesDetector
# from services.config.workout_config import POSE_CONNECTIONS


# class VideoProcessorClass(VideoProcessorBase):

#     def __init__(self):
#         # Used to prevent two threads changing data at the same time.
#         self._lock = threading.Lock()
#         self._latest_metrics = None  # Stores latest result.
#         # default exercise type, can be changed by main app.
#         self._exercise_type = "Squats"

#         model_path = os.path.join(
#             os.getcwd(), "ml_models", "pose_landmarker_full.task")
#         # Tells MediaPipe which model to load.
#         base_option = python.BaseOptions(model_asset_path=model_path)

#         # Configuration Landmarkers
#         options = vision.PoseLandmarkerOptions(
#             base_options=base_option,
#             running_mode=vision.RunningMode.VIDEO,
#             min_pose_detection_confidence=0.7,
#             min_pose_presence_confidence=0.7,
#             min_tracking_confidence=0.7,
#             output_segmentation_masks=False
#         )

#         # Creates the MediaPipe pose detector.
#         self._landmarker = vision.PoseLandmarker.create_from_options(options)

#         self._detectors = {
#             "Squats": SquatDetector(),
#             "Push-ups": PushUpDetector(),
#             "Biceps Curls (Dumbbell)": BicepsCurlDetector(),
#             "Shoulder Press": ShoulderPressDetector(),
#             "Lunges": LungesDetector(),
#         }

#         # MediaPipe Video Mode requires timestamps
#         self._frame_timestamps_ms = 0

#     # Stores latest detector result.
#     def set_latest_metrics(self, metrics):
#         with self._lock:
#             self._latest_metrics = metrics.copy()

#     # gets latest detector result.
#     def get_latest_metrics(self):
#         with self._lock:
#             return None if self._latest_metrics is None else self._latest_metrics.copy()

#     # Sets the exercise type for the processor, called from the main app
#     def set_exercise(self, exercise_type):
#         with self._lock:
#             self._exercise_type = exercise_type

#     # Gets the exercise type for the processor
#     def get_exercise(self):
#         with self._lock:
#             return self._exercise_type

#     # draws the skeleton on the frame based on the detected landmarks and the defined connections
#     def _draw_skeleton(self, img, landmarks):
#         h, w = img.shape[:2]

#         for start_idx, end_idx in POSE_CONNECTIONS:
#             p1 = landmarks[start_idx]
#             p2 = landmarks[end_idx]

#             if p1.visibility > 0.7 and p2.visibility > 0.7:
#                 cv2.line(
#                     img,
#                     (int(p1.x * w), int(p1.y * h)),
#                     (int(p2.x * w), int(p2.y * h)),
#                     (0, 255, 0),
#                     8
#                 )

#         for lm in landmarks:
#             if lm.visibility > 0.7:
#                 cv2.circle(
#                     img,
#                     (int(lm.x * w), int(lm.y * h)),
#                     8,
#                     (255, 0, 0),
#                     -1
#                 )

#     def _draw_no_pose_warnings(self, img):
#         cv2.putText(
#             img,
#             "NO POSE DETECTED",
#             (30, 50),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0, 255, 0),
#             2,
#             cv2.LINE_AA,
#         )

#         cv2.putText(
#             img,
#             "PLEASE FACE THE CAMERA",
#             (30, 100),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0, 255, 0),
#             2,
#             cv2.LINE_AA,
#         )

#     # exercise-specific overlay drawing functions, called based on the current exercise type
#     def _draw_overlays(self, img, metrics, ex_type):
#         if ex_type == "Squats":
#             self._draw_squats_overlays(img, metrics)
#         elif ex_type == "Push-ups":
#             self._draw_pushup_overlays(img, metrics)
#         elif ex_type == "Biceps Curls (Dumbbell)":
#             self._draw_curl_overlays(img, metrics)
#         elif ex_type == "Shoulder Press":
#             self._draw_press_overlays(img, metrics)
#         elif ex_type == "Lunges":
#             self._draw_lunge_overlays(img, metrics)

#     def _draw_squats_overlays(self, img, metrics):
#         h, _ = img.shape[:2]

#         cv2.putText(
#             img,
#             f"DEPTH: {metrics['depth_status']}",
#             (20, h - 20),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0, 255, 0),
#             2,
#         )

#     def _draw_pushup_overlays(self, img, metrics):
#         h, _ = img.shape[:2]

#         cv2.putText(
#             img,
#             f"BODY: {metrics['body_alignment']} | HIP: {metrics['hip_status']}",
#             (20, h - 20),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0, 255, 0),
#             2,
#         )

#     def _draw_curl_overlays(self, img, metrics):
#         h, _ = img.shape[:2]

#         cv2.putText(
#             img,
#             f"SWING: {metrics['swing_status']}",
#             (20, h - 20),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0, 255, 0),
#             2,
#         )

#     def _draw_press_overlays(self, img, metrics):
#         h, _ = img.shape[:2]

#         cv2.putText(
#             img,
#             f"EXT: {metrics['extension_status']} | BACK: {metrics['back_arch_status']}",
#             (20, h - 20),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0, 255, 0),
#             2,
#         )

#     def _draw_lunge_overlays(self, img, metrics):
#         h, _ = img.shape[:2]

#         cv2.putText(
#             img,
#             f"BALANCE: {metrics['balance_status']}",
#             (20, h - 20),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0, 255, 0),
#             2,
#         )

#     # This is the MOST IMPORTANT function.
#     # It is called for every frame of the video stream.
#     # Camera Frame -> Process -> Return Frame

#     def recv(self, frame):
#         image = np.asarray(
#             # flip horizontally to act as a mirror
#             cv2.flip(frame.to_ndarray(format="bgr24"), 1),
#             dtype=np.uint8
#         )

#         # MediaPipe needs its own image format.
#         # We also convert back to BGR here because OpenCV uses BGR and MediaPipe uses RGB, so we want to avoid doing multiple conversions.
#         mp_image = mp.Image(
#             image_format=mp.ImageFormat.SRGB,
#             data=cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
#         )

#         self._frame_timestamps_ms += 30  # Increment timestamp for MediaPipe, assuming ~30fps. This is needed for the pose landmarker to work in video mode, as it relies on timestamps to process frames correctly. In a real implementation, you might want to use actual timestamps based on the system clock or frame capture time for more accuracy, but this simple increment works for a consistent frame rate.

#         # detect poses and get landmarks for the current frame using MediaPipe(shoulder,hips,legs,wrist .. etc)
#         result = self._landmarker.detect_for_video(
#             mp_image, self._frame_timestamps_ms)

#         # result = PoseLandmarkerResult(
#         #     pose_landmarks=[
#         #         [landmark0, landmark1, ..., landmark32]
#         #     ],
#         #     pose_world_landmarks=[
#         #         [world_landmark0, world_landmark1, ..., world_landmark32]
#         #     ],
#         #     segmentation_masks=None
#         # )
#         if result.pose_landmarks:  # result is a PoseLandmarkerResult object.

#             landmarks = result.pose_landmarks[0]  # 33 body points

#             self._draw_skeleton(image, landmarks)

#             ex_type = self.get_exercise()

#             detector = self._detectors.get(ex_type)

#             if detector:
#                 metrics = detector.process_frame(landmarks)

#                 # Add pose detection status to the metrics dictionary for UI/display logic, metrics is a dict
#                 metrics["pose_detected"] = True

#                 self._draw_overlays(image, metrics, ex_type)

#                 self.set_latest_metrics(metrics)
#         else:
#             self._draw_no_pose_warnings(image)

#             with self._lock:  # ?? why lock used on else only - because if no pose is detected, we want to update the latest metrics to indicate that no pose is detected. This is important for the main app to know so it can display appropriate messages or take actions based on whether a pose is currently being detected or not. We use the lock here to ensure that this update to the shared _latest_metrics variable is thread-safe, preventing
#                 if self._latest_metrics is not None:  # This is called a race condition - if the main app is trying to read the latest metrics at the same time as we are updating it here, it could cause inconsistent or corrupted data. By using a lock, we ensure that only one thread can access or modify _latest_metrics at a time, preventing these issues.
#                     self._latest_metrics["pose_detected"] = False
#                 else:
#                     self._latest_metrics = {"pose_detected": False}

#         return av.VideoFrame.from_ndarray(image, format="bgr24")

import os
import cv2
import av
import numpy as np
import mediapipe as mp
import threading
from streamlit_webrtc import VideoProcessorBase
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from detectors.squat import SquatDetector
from detectors.pushup import PushUpDetector
from detectors.biceps_curl import BicepsCurlDetector
from detectors.shoulder_press import ShoulderPressDetector
from detectors.lunges import LungesDetector
from services.config.workout_config import POSE_CONNECTIONS


class VideoProcessorClass(VideoProcessorBase):
    def __init__(self):
        self._lock = threading.Lock()
        self._latest_metrics = None
        self._exercise_type = "Squats"

        model_path = os.path.join(
            os.getcwd(), "ml_models", "pose_landmarker_full.task")
        base_option = python.BaseOptions(model_asset_path=model_path)

        options = vision.PoseLandmarkerOptions(
            base_options=base_option,
            running_mode=vision.RunningMode.VIDEO,
            min_pose_detection_confidence=0.7,
            min_pose_presence_confidence=0.7,
            min_tracking_confidence=0.7,
            output_segmentation_masks=False
        )

        self._landmarker = vision.PoseLandmarker.create_from_options(options)

        self._detectors = {
            "Squats": SquatDetector(),
            "Push-ups": PushUpDetector(),
            "Biceps Curls (Dumbbell)": BicepsCurlDetector(),
            "Shoulder Press": ShoulderPressDetector(),
            "Lunges": LungesDetector(),
        }

        self._frame_timestamps_ms = 0

    def set_latest_metrics(self, metrics):
        with self._lock:
            self._latest_metrics = metrics.copy()

    def get_latest_metrics(self):
        with self._lock:
            return None if self._latest_metrics is None else self._latest_metrics.copy()

    def set_exercise(self, exercise_type):
        with self._lock:
            self._exercise_type = exercise_type

    def get_exercise(self):
        with self._lock:
            return self._exercise_type

    def _draw_skeleton(self, img, landmarks):
        h, w = img.shape[:2]

        for start_idx, end_idx in POSE_CONNECTIONS:
            p1 = landmarks[start_idx]
            p2 = landmarks[end_idx]

            if p1.visibility > 0.7 and p2.visibility > 0.7:
                cv2.line(
                    img,
                    (int(p1.x * w), int(p1.y * h)),
                    (int(p2.x * w), int(p2.y * h)),
                    (0, 255, 0),
                    8
                )

        for lm in landmarks:
            if lm.visibility > 0.7:
                cv2.circle(
                    img,
                    (int(lm.x * w), int(lm.y * h)),
                    8,
                    (255, 0, 0),
                    -1
                )

    def _draw_no_pose_warnings(self, img):
        cv2.putText(
            img,
            "NO POSE DETECTED",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        cv2.putText(
            img,
            "PLEASE FACE THE CAMERA",
            (30, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

    def _draw_overlays(self, img, metrics, ex_type):
        if ex_type == "Squats":
            self._draw_squats_overlays(img, metrics)
        elif ex_type == "Push-ups":
            self._draw_pushup_overlays(img, metrics)
        elif ex_type == "Biceps Curls (Dumbbell)":
            self._draw_curl_overlays(img, metrics)
        elif ex_type == "Shoulder Press":
            self._draw_press_overlays(img, metrics)
        elif ex_type == "Lunges":
            self._draw_lunge_overlays(img, metrics)

    def _draw_squats_overlays(self, img, metrics):
        h, _ = img.shape[:2]

        cv2.putText(
            img,
            f"DEPTH: {metrics['depth_status']}",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

    def _draw_pushup_overlays(self, img, metrics):
        h, _ = img.shape[:2]

        cv2.putText(
            img,
            f"BODY: {metrics['body_alignment']} | HIP: {metrics['hip_status']}",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

    def _draw_curl_overlays(self, img, metrics):
        h, _ = img.shape[:2]

        cv2.putText(
            img,
            f"SWING: {metrics['swing_status']}",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

    def _draw_press_overlays(self, img, metrics):
        h, _ = img.shape[:2]

        cv2.putText(
            img,
            f"EXT: {metrics['extension_status']} | BACK: {metrics['back_arch_status']}",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

    def _draw_lunge_overlays(self, img, metrics):
        h, _ = img.shape[:2]

        cv2.putText(
            img,
            f"BALANCE: {metrics['balance_status']}",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

    def recv(self, frame):
        image = np.asarray(
            cv2.flip(frame.to_ndarray(format="bgr24"), 1),
            dtype=np.uint8
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        )

        self._frame_timestamps_ms += 30
        result = self._landmarker.detect_for_video(
            mp_image, self._frame_timestamps_ms)

        if result.pose_landmarks:
            landmarks = result.pose_landmarks[0]

            self._draw_skeleton(image, landmarks)

            ex_type = self.get_exercise()

            detector = self._detectors.get(ex_type)

            if detector:
                metrics = detector.process(landmarks)

                metrics["pose_detected"] = True

                self._draw_overlays(image, metrics, ex_type)

                self.set_latest_metrics(metrics)
        else:
            self._draw_no_pose_warnings(image)

            with self._lock:
                if self._latest_metrics is not None:
                    self._latest_metrics["pose_detected"] = False
                else:
                    self._latest_metrics = {"pose_detected": False}

        return av.VideoFrame.from_ndarray(image, format="bgr24")
