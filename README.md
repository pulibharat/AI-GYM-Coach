<div align="center">

# 🏋️‍♂️ AI GYM Coach

### Real-time pose detection with proactive AI voice coaching

*Turn your webcam into a personal trainer — form correction, rep counting, and live voice feedback, all powered by computer vision and LLMs.*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.54-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-00A98F?style=flat&logo=google&logoColor=white)](https://developers.google.com/mediapipe)
[![Groq](https://img.shields.io/badge/LLM-Groq-F55036?style=flat&logo=groq&logoColor=white)](https://groq.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](#-license)
[![Stars](https://img.shields.io/github/stars/pulibharat/AI-GYM-Coach?style=social)](https://github.com/pulibharat/AI-GYM-Coach/stargazers)

</div>

---

## 🎯 Overview

**AI GYM Coach** is a Streamlit web app that watches you work out through your webcam, tracks your joint angles in real time, and gives you spoken feedback — like having a coach in the room. It uses **MediaPipe** for pose estimation, computes exercise-specific biomechanics (angles, alignment, tempo), and pipes progress events through a **Groq-powered LLM** to generate natural coaching cues, which are converted to speech with **gTTS** and played back live in the browser.

Every set, rep, and session is logged to a local database so you can review your workout history over time.

---

## ✨ Features

- 🎥 **Real-time pose tracking** — Live webcam analysis via `streamlit-webrtc` + MediaPipe, no video upload needed
- 🏋️ **Multi-exercise support** — Squats, Push-ups, Biceps Curls (Dumbbell), Shoulder Press, and Lunges
- 📐 **Form analysis per exercise** — Joint-angle and alignment checks tailored to each movement:
  | Exercise | Tracked Metrics |
  |---|---|
  | Squats | Knee angle, back angle, depth status |
  | Push-ups | Elbow angle, body alignment, hip position |
  | Biceps Curls | Elbow angle, shoulder stability, swing detection |
  | Shoulder Press | Elbow angle, arm extension, back arch |
  | Lunges | Front knee angle, torso angle, balance status |
- 🗣️ **AI voice coaching** — An LLM (via Groq) reacts to workout events (start, set completed, workout finished) with encouraging, context-aware feedback spoken aloud
- 🔢 **Automatic rep & set counting** — Live tracking of reps within a set and sets within a session
- 🔐 **Login wall** — Simple authentication gate before accessing the coach
- 📊 **Workout history & analytics** — Session data persisted to SQLite, aggregated and displayed as a history table
- 🎨 **Custom UI** — Branded styling with custom fonts and CSS injected into the Streamlit app

---

## 🧠 How It Works

```
Webcam Feed
    │
    ▼
streamlit-webrtc  ──▶  MediaPipe Pose Landmarks
    │
    ▼
Exercise-specific angle & form detectors (detectors/)
    │
    ▼
Rep/Set counting + live metrics (core/, services/tracking)
    │
    ├──▶  SQLite persistence (services/persistence)
    │
    ▼
Event triggers (set complete, workout done, etc.)
    │
    ▼
Groq LLM Coach  ──▶  gTTS  ──▶  Autoplayed voice feedback
```

---

## 📁 Project Structure

```
AI-GYM-Coach/
├── core/                # Core app/session logic
├── detectors/           # Exercise-specific pose & form detection logic
├── ml_models/           # Pose estimation / ML model assets
├── services/
│   ├── auth/            # Login wall
│   ├── config/          # Exercise options & app config
│   ├── coaching/        # LLM coach, TTS, voice pipeline
│   ├── persistence/     # SQLite exercise repository
│   ├── state/           # Session state defaults
│   ├── tracking/        # Live metrics syncing
│   ├── ui/              # CSS/font loading, WebRTC styling
│   └── vision/          # Video processor for pose analysis
├── static/              # CSS, fonts, and static assets
├── main.py              # Streamlit app entry point
├── requirements.txt     # Python dependencies
├── packages.txt         # System-level packages (for deployment)
└── data.db              # SQLite database (workout history)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| UI / App framework | [Streamlit](https://streamlit.io/) |
| Live video | [streamlit-webrtc](https://github.com/whitphx/streamlit-webrtc) |
| Pose estimation | [MediaPipe](https://developers.google.com/mediapipe) |
| Computer vision | [OpenCV](https://opencv.org/) (headless) |
| AI coaching (LLM) | [Groq API](https://groq.com/) |
| Text-to-speech | [gTTS](https://pypi.org/project/gTTS/) |
| Data handling | [pandas](https://pandas.pydata.org/) |
| Persistence | SQLite |
| Config | python-dotenv |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A webcam
- A [Groq API key](https://console.groq.com/) for the voice coaching feature

### Installation

```bash
# Clone the repository
git clone https://github.com/pulibharat/AI-GYM-Coach.git
cd AI-GYM-Coach

# (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> Alternatively, if deploying on Streamlit Community Cloud, add `GROQ_API_KEY` to your app's `secrets.toml`.

### Run the app

```bash
streamlit run main.py
```

Then open the local URL Streamlit prints (typically `http://localhost:8501`) in your browser, log in, choose your exercise, sets, and reps in the sidebar, and hit **Start Workout**.

---

## 🎮 Usage

1. **Log in** through the login wall.
2. **Set your plan** — pick an exercise, number of sets, and reps per set in the sidebar.
3. **Start Workout** — this activates your webcam and the AI coach.
4. **Perform your exercise** — the app tracks your form in real time and shows live metrics (angles, alignment, depth/balance status).
5. **Listen to your coach** — voice feedback plays automatically at key moments (workout start, set milestones, completion).
6. **End Workout** — review total reps, sets completed, and see your session added to your workout history table below.

---

## 🗺️ Roadmap Ideas

- [ ] Additional exercises (deadlifts, planks, lateral raises)
- [ ] Rep-quality scoring and progress trends over time
- [ ] Downloadable workout reports
- [ ] Mobile-friendly camera support

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request for bug fixes, new exercise detectors, or UI improvements.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/new-exercise`)
3. Commit your changes
4. Push and open a PR

---

## 📄 License

This project is available under the [MIT License](LICENSE).

---

<div align="center">

Made with ❤️, OpenCV, and a bit of AI hype by [pulibharat](https://github.com/pulibharat)

</div>
