import streamlit as st
import pandas as pd
import joblib
import streamlit.components.v1 as components
from datetime import datetime

# ================================
# Load Model
# ================================
model = joblib.load("suicide_risk_model.pkl")

# ================================
# Custom Styling
# ================================
st.markdown(
    """
    <style>
    .stApp { background-color: #FFFFFF; }
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        color: #2F4F4F;
    }
    h1, h2, h3, h4 {
        color: #008080 !important;
        font-weight: 700;
    }
    .stButton>button {
        background-color: #CFE3E2;
        color: #2F4F4F;
        border-radius: 10px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #A8C8C6;
        color: #2F4F4F;
    }
    .stMarkdown, .stText { color: #2F4F4F; }
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
            step_display += f"**{step_name}** → "
        else:
            step_display += f"{step_name} → "
    st.markdown(step_display.rstrip(" → "))


# ================================
# Step 1: Introduction Page
# ================================
if st.session_state.step == "intro":
    show_step_tracker()

    st.markdown(
        "<h2 style='text-align: center;'>Tell Me WAI: Your Personal AI Mental Wellness Companion</h2>",
        unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center;'>Invest in your mental health today. "
        "Take a quick check-in to understand your well-being and explore supportive resources.</p>",
        unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("Tell Me WAI logo.png", width=300)

    # Start assessment
    if st.button("Start"):
        st.session_state.step = "predictor"

    # View appointments directly from main page
    if st.button("📋 View My Appointments"):
        if st.session_state.appointments:
            st.subheader("Your Appointments")
            df = pd.DataFrame(st.session_state.appointments)
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

    st.write("💙 It's okay to ask for help. Here are some solutions you can explore:")

    if st.button("🎵 Music Therapy"): st.session_state.solution = "playlist"
    if st.button("🤖  AI Consultant"): st.session_state.solution = "chatbot"
    if st.button("📅 Teleconsultant"): st.session_state.solution = "teleconsult"
    if st.button("⬅ Back to Main Page"): back_to_mainpage()


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
        if st.button("⬅ Back to Results"): back_to_result()
    with col2:
        if st.button("🏠 Back to Main Page"): back_to_mainpage()


# ================================
# Step 4B: Music Therapy Playlist
# ================================
elif st.session_state.solution == "playlist":
    st.header("🎵 AI-Curated Relaxing Playlist")
    st.markdown("Here’s a calming playlist designed to help you relax and reduce stress 💆‍♀️✨")

    playlist = [
        {"title": "Weightless", "artist": "Marconi Union", "link": "https://www.youtube.com/watch?v=UfcAVejslrU"},
        {"title": "Clair de Lune", "artist": "Claude Debussy", "link": "https://www.youtube.com/watch?v=CvFH_6DNRCY"},
        {"title": "Sunset Lover", "artist": "Petit Biscuit", "link": "https://www.youtube.com/watch?v=GrAchTdepsU"},
        {"title": "River Flows in You", "artist": "Yiruma", "link": "https://www.youtube.com/watch?v=7maJOI3QMu0"},
        {"title": "Bloom", "artist": "ODESZA", "link": "https://www.youtube.com/watch?v=wvUQcnfwUUM"}
    ]
    for track in playlist:
        st.markdown(f"🎧 [{track['title']} - {track['artist']}]({track['link']})")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ Back to Results"): back_to_result()
    with col2:
        if st.button("🏠 Back to Main Page"): back_to_mainpage()


# ================================
# Step 4C: Teleconsultant Booking
# ================================
elif st.session_state.solution == "teleconsult":
    st.header("📅 Book a Teleconsultation")
    st.markdown("Schedule a teleconsultation with a certified mental health professional 🩺")

    name = st.text_input("Your Name")
    email = st.text_input("Email Address")
    date = st.date_input("Preferred Date", min_value=datetime.today())
    time = st.time_input("Preferred Time")

    if st.button("Book Appointment"):
        if name and email:
            appointment = {"Name": name, "Email": email, "Date": str(date), "Time": str(time)}
            st.session_state.appointments.append(appointment)
            st.success(f"✅ Appointment booked successfully for {name} on {date} at {time}. Confirmation will be sent to {email}.")
        else:
            st.warning("⚠ Please fill in your name and email before booking.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ Back to Results"): back_to_result()
    with col2:
        if st.button("🏠 Back to Main Page"): back_to_mainpage()







