import streamlit as st
import pandas as pd
import joblib
import streamlit.components.v1 as components
from datetime import datetime
import os
import requests  # moved to top

# ================================
# Load Model
# ================================
model = joblib.load("suicide_risk_model.pkl")

APPOINTMENTS_FILE = "Appointments.xlsx"

# ================================
# Custom Styling
# ================================
st.markdown(
    """
    <style>
    /* Import Open Sans */
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans&display=swap');

    /* General app */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
        font-family: 'Open Sans', sans-serif;
    }

    html, body, [class*="css"] {
        font-family: 'Open Sans', sans-serif;
        color: var(--text-color);
    }

    h1, h2, h3, h4 {
        color: #008080 !important;   /* Teal */
        font-weight: 700;
    }

    .subtitle {
        color: #56A1A4 !important;
        text-align: center;
        font-style: italic;
        font-size: 16px;
    }

    /* Buttons */
    .stButton>button {
        background-color: #008080;   /* Teal */
        color: #FFFFFF;              /* White text */
        border-radius: 10px;
        border: none;
        font-weight: bold;
        padding: 0.5em 1em;
        margin: 0.3em;
        width: 100%;
        transition: background-color 0.3s, transform 0.1s;
    }

    .stButton>button:hover {
        background-color: #006666;   /* Darker teal */
        color: #FFFFFF;
        transform: scale(1.02);
        cursor: pointer;
    }

    /* Step tracker */
    .step-tracker {
        color: #008080;              
        text-align: center;
        font-size: 18px;
        margin-bottom: 20px;
    }
    .current-step {
        font-weight: bold;
        color: #008080;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ================================
# Session State Initialization
# ================================
if "step" not in st.session_state:
    st.session_state.step = "intro"
if "risk" not in st.session_state:
    st.session_state.risk = None
if "solution" not in st.session_state:
    st.session_state.solution = None
if "appointments" not in st.session_state:
    st.session_state.appointments = []
if "playlist_index" not in st.session_state:
    st.session_state.playlist_index = {}

# ---------------- Helpers ----------------
def back_to_result():
    st.session_state.solution = None
    st.session_state.step = "result"

def back_to_intro():
    st.session_state.solution = None
    st.session_state.step = "intro"

def back_to_mainpage():
    st.session_state.step = "intro"
    st.session_state.solution = None

def show_step_tracker():
    steps = ["1️⃣ Introduction", "2️⃣ Assessment", "3️⃣ Result"]
    current = st.session_state.step
    step_display = ""
    for i, step_name in enumerate(steps):
        if (current == "intro" and i == 0) or (current == "predictor" and i == 1) or (current == "result" and i == 2):
            step_display += f"<span class='current-step'>{step_name}</span> → "
        else:
            step_display += f"{step_name} → "
    st.markdown(
        f"<p class='step-tracker'>{step_display.rstrip(' → ')}</p>",
        unsafe_allow_html=True
    )

# ================================
# Step 1: Introduction Page
# ================================
if st.session_state.step == "intro":
    show_step_tracker()
    st.markdown(
        "<h2 style='text-align: center; color: #008080;'>Tell Me WAI: Your Personal AI Mental Wellness Companion</h2>",
        unsafe_allow_html=True)
    st.markdown(
        "<p class='subtitle'>Invest in your mental health today. "
        "Take a quick check-in to understand your well-being and explore supportive resources.</p>",
        unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("Tell Me WAI logo.png", width=300)

    if st.button("Start"):
        st.session_state.step = "predictor"

    if st.button("📋 View My Appointments"):
        if st.session_state.appointments:
            st.subheader("Your Appointments")
            df = pd.DataFrame(st.session_state.appointments)
            df.index = df.index + 1
            st.table(df)
        else:
            st.info("No appointments booked yet.")

# ================================
# Step 2: Predictor Page
# ================================
elif st.session_state.step == "predictor":
    show_step_tracker()
    st.header("🌱 How are things going for you right now?")

    gender = st.selectbox("Gender", ["Male", "Female"])
    age = st.number_input("Age", min_value=10, max_value=100, value=20)
    academic_pressure = st.slider("Academic Pressure (1-5)", 1, 5, 3)
    study_satisfaction = st.slider("Study Satisfaction (1-5)", 1, 5, 3)
    sleep_duration = st.selectbox("Sleep Duration",
                                  ["less than 5 hours", "5 - 6 hours", "7 - 8 hours", "more than 8 hours"])
    dietary_habits = st.selectbox("Dietary Habits", ["unhealthy", "moderate", "healthy"])
    suicidal_thoughts = st.selectbox("Suicidal Thoughts", ["yes", "no"])
    study_hours = st.number_input("Study Hours per Day", min_value=0, max_value=24, value=5)
    financial_stress = st.slider("Financial Stress (1-5)", 1, 5, 3)
    family_history = st.selectbox("Family History of Mental Illness", ["yes", "no"])
    depression = st.selectbox("Depression", ["yes", "no"])

    encode_dict = {
        "Gender": {"Male": 1, "Female": 0},
        "Sleep_Duration": {"less than 5 hours": 0, "5 - 6 hours": 1, "7 - 8 hours": 2, "more than 8 hours": 3},
        "Dietary_Habits": {"unhealthy": 0, "moderate": 1, "healthy": 2},
        "Suicidal_Thoughts": {"no": 0, "yes": 1},
        "Family_History_of_Mental_Illness": {"no": 0, "yes": 1},
        "Depression": {"no": 0, "yes": 1}
    }

    input_data = pd.DataFrame([{
        "Gender": encode_dict["Gender"][gender],
        "Age": age,
        "Academic_Pressure": academic_pressure,
        "Study_Satisfaction": study_satisfaction,
        "Sleep_Duration": encode_dict["Sleep_Duration"][sleep_duration],
        "Dietary_Habits": encode_dict["Dietary_Habits"][dietary_habits],
        "Suicidal_Thoughts": encode_dict["Suicidal_Thoughts"][suicidal_thoughts],
        "Study_Hours": study_hours,
        "Financial_Stress": financial_stress,
        "Family_History_of_Mental_Illness": encode_dict["Family_History_of_Mental_Illness"][family_history],
        "Depression": encode_dict["Depression"][depression]
    }])

    if st.button("Submit"):
        prediction = model.predict(input_data)[0]
        risk_map = {0: "Low", 1: "Medium", 2: "High"}
        st.session_state.risk = risk_map[prediction]
        st.session_state.step = "result"

# ================================
# Step 3: Result Page
# ================================
elif st.session_state.step == "result" and st.session_state.solution is None:
    show_step_tracker()
    risk = st.session_state.risk

    if risk == "Low":
        st.success("🟢 You seem to be doing well right now. Keep taking care of yourself 💚")
    elif risk == "Medium":
        st.info("🟤 It looks like you may be under some stress. Taking small steps can really help 💛")
    elif risk == "High":
        st.error("🔴 Your results suggest that you may need extra support right now. Reaching out is a brave step ❤️")

    st.markdown("<p class='subtitle'>💙 It's okay to ask for help. Here are some solutions you can explore:</p>",
                unsafe_allow_html=True)

    if st.button("🎵 Music Therapy"):
        st.session_state.solution = "playlist"
    if st.button("🤖 AI Consultant"):
        st.session_state.solution = "chatbot"
    if st.button("📅 Teleconsultant"):
        st.session_state.solution = "teleconsult"
    if st.button("⬅ Back to Main Page"):
        back_to_mainpage()

# ================================
# Step 4A: AI Consultant Chatbot
# ================================
elif st.session_state.solution == "chatbot":
    st.header("🤖 AI Consultant")
    with open("embedBot.html", "r", encoding="utf-8") as f:
        chatbot_html = f.read()
    components.html(chatbot_html, height=700, scrolling=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ Back to Results"):
            back_to_result()
    with col2:
        if st.button("🏠 Back to Main Page"):
            back_to_mainpage()

# ================================
# Step 4B: Music Therapy
# ================================
elif st.session_state.solution == "playlist":
    st.header("🎵 AI-Curated Music Therapy")
    st.markdown(
        "<p class='subtitle'>Select how you're feeling right now and we'll recommend calming songs for you 💆‍♀️✨</p>",
        unsafe_allow_html=True
    )

    # Mood keywords for dynamic YouTube search
    mood_search_terms = {
        "Sad": ["uplifting music", "happy songs", "songs to feel better"],
        "Anxious": ["calm instrumental", "relaxing piano", "meditation music"],
        "Low Energy": ["energetic songs playlist", "motivational music", "pop upbeat"],
        "Stress": ["stress relief music", "nature sounds", "ambient calm music"]
    }

    # YouTube API key from secrets
    YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]

    # Function to fetch YouTube videos
    def search_youtube_videos(query, max_results=5):
        search_url = (
            "https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&maxResults={max_results}&q={query}&type=video&key={YOUTUBE_API_KEY}"
        )
        resp = requests.get(search_url).json()
        videos = []
        for item in resp.get("items", []):
            vid_id = item["id"].get("videoId")
            if vid_id:
                videos.append(f"https://www.youtube.com/watch?v={vid_id}")
        return videos

    mood = st.selectbox("💙 How are you feeling?", list(mood_search_terms.keys()))

    if mood:
        # initialize playlist_index for mood
        if mood not in st.session_state.playlist_index:
            st.session_state.playlist_index[mood] = 0

        # pick a search term (rotate)
        search_terms = mood_search_terms[mood]
        term_index = st.session_state.playlist_index[mood] % len(search_terms)
        search_query = search_terms[term_index]

        # fetch videos
        videos = search_youtube_videos(search_query, max_results=10)

        if videos:
            # rotate through videos
            video_index = st.session_state.playlist_index[mood] % len(videos)
            video_url = videos[video_index]
            st.video(video_url)
        else:
            st.warning("⚠️ No playable video found for this mood right now. Please try again or refresh the playlist.")

        # Refresh button rotates search term or video
        if st.button("🔄 Refresh Playlist"):
            st.session_state.playlist_index[mood] += 1
            st.rerun()

    # Back buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ Back to Results"):
            back_to_result()
    with col2:
        if st.button("🏠 Back to Main Page"):
            back_to_mainpage()

# ================================
# Step 4C: Teleconsultant Booking
# ================================
elif st.session_state.solution == "teleconsult":
    st.header("📅 Book a Teleconsultation")
    st.markdown("<p class='subtitle'>Schedule a teleconsultation with a certified mental health professional 🩺</p>",
                unsafe_allow_html=True)

    name = st.text_input("Your Name")
    email = st.text_input("Email Address")
    date = st.date_input("Preferred Date", min_value=datetime.today())
    time = st.time_input("Preferred Time")

    if st.button("Book Appointment"):
        if name and email:
            appointment = {"Name": name, "Email": email, "Date": str(date), "Time": str(time)}

            # Save in session state
            st.session_state.appointments.append(appointment)

            # Save to Excel file
            new_booking = pd.DataFrame([appointment])
            if os.path.exists(APPOINTMENTS_FILE):
                existing = pd.read_excel(APPOINTMENTS_FILE)
                updated = pd.concat([existing, new_booking], ignore_index=True)
            else:
                updated = new_booking

            updated.to_excel(APPOINTMENTS_FILE, index=False)
            st.success(f"✅ Appointment booked successfully for {name} on {date} at {time}. Confirmation will be sent to {email}.")
        else:
            st.warning("⚠ Please fill in your name and email before booking.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ Back to Results"):
            back_to_result()
    with col2:
        if st.button("🏠 Back to Main Page"):
            back_to_mainpage()
