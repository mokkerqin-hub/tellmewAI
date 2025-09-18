import os
import requests
import joblib
import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.express as px

# ================================
# Load Model
# ================================
model = joblib.load("suicide_risk_model.pkl")

APPOINTMENTS_FILE = "Appointments.xlsx"
USERS_FILE = "UserRecords.xlsx"

# ================================
# Custom Styling
# ================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans&display=swap');

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
        color: #008080 !important;
        font-weight: 700;
    }

    .subtitle {
        color: #56A1A4 !important;
        text-align: center;
        font-style: italic;
        font-size: 16px;
    }

    .stButton > button {
        background-color: #008080;
        color: #FFFFFF;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        padding: 0.5em 1em;
        margin: 0.3em;
        width: 100%;
    }

    .stButton > button:hover {
        background-color: #006666;
        color: #FFFFFF;
        transform: scale(1.02);
        cursor: pointer;
    }

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
for key, default in {
    "step": "intro",
    "risk": None,
    "solution": None,
    "appointments": [],
    "playlist_index": {},
    "dashboard_auth": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ================================
# Helper Functions
# ================================
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
    display = ""

    for i, step_name in enumerate(steps):
        if (current == "intro" and i == 0) or (current == "predictor" and i == 1) or (current == "result" and i == 2):
            display += f"<span class='current-step'>{step_name}</span> → "
        else:
            display += f"{step_name} → "

    st.markdown(
        f"<p class='step-tracker'>{display.rstrip(' → ')}</p>",
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

    # Introductory description
    st.markdown(
        """
        <div style='text-align: justify; font-size: 14px; color: #008080; font-style: italic;'>
        <b>Tell Me WAI</b> is a personalized AI-powered mental wellness companion 
        designed to help students and individuals reflect on their emotional well-being. 
        It provides a quick <b>screening</b> based on lifestyle and mental health indicators, 
        and connects users to supportive resources such as music therapy, AI consultation, 
        and teleconsultation with professionals.  
        <br><br>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Add disclaimer
    st.markdown(
        "<p style='text-align: center; color: #FF0000; font-weight: bold;'>"
        "⚠️ Disclaimer: This tool is for educational and informational purposes only. "
        "It is not a medical diagnostic tool and cannot replace professional mental health advice.</p>"
        "</div>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("Tell Me WAI logo.png", width=300)

    if st.button("Start"):
        st.session_state.step = "predictor"

    if st.button("📋 View My Appointments"):
        st.session_state.step = "appointments"

    if st.button("📊 Staff Dashboard"):
        st.session_state.step = "dashboard"

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

        # Save user input & result to Excel
        record = input_data.copy()
        record["Predicted_Risk"] = st.session_state.risk
        record["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if os.path.exists(USERS_FILE):
            existing_users = pd.read_excel(USERS_FILE)
            updated_users = pd.concat([existing_users, record], ignore_index=True)
        else:
            updated_users = record

        updated_users.to_excel(USERS_FILE, index=False)

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

    # Full-width, non-scrollable iframe
    st.components.v1.html(
        f"""
        <iframe src="https://mental-health-chatbot-2zpe.onrender.com/" 
                width="100%" 
                height="800" 
                style="border:none;">
        </iframe>
        """,
        height=820,  # give extra room for padding
    )

    # Navigation buttons
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
    st.header("🎵 Music Therapy")
    st.markdown(
        "<p class='subtitle'>Select how you're feeling right now and we'll recommend calming songs for you 💆‍♀️✨</p>",
        unsafe_allow_html=True
    )

    # Mood keywords for dynamic YouTube search
    mood_search_terms = {
        "Stress": ["stress relief music", "nature sounds", "ambient calm music"],
        "Sad": ["uplifting music", "happy songs", "songs to feel better"],
        "Anxious": ["calm instrumental", "relaxing piano", "meditation music"],
        "Low Energy": ["energetic songs playlist", "motivational music", "pop upbeat"]
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

    # Force "Stress" as first and default
    mood_options = list(mood_search_terms.keys())
    mood = st.selectbox("💙 How are you feeling?", mood_options, index=0)

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
    contact_number = st.text_input("Your Contact Number")
    email = st.text_input("Email Address")
    date = st.date_input("Preferred Date", min_value=datetime.today())
    time = st.time_input("Preferred Time")

    if st.button("Book Appointment"):
        if name and email:
            appointment = {
                "Name": name,
                "Contact Number": contact_number,
                "Email": email,
                "Date": str(date),
                "Time": str(time)
            }

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

            # Success message with WhatsApp reconfirmation note
            st.success(
                f"✅ Appointment booked successfully for {name} on {date} at {time}. "
                f"You will also be notified via WhatsApp for reconfirmation 📲."
            )
        else:
            st.warning("⚠ Please fill in your name and email before booking.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ Back to Results"):
            back_to_result()
    with col2:
        if st.button("🏠 Back to Main Page"):
            back_to_mainpage()

# ================================
# Step 5: View My Appointments (Users)
# ================================
elif st.session_state.step == "appointments":
    st.header("📅 My Appointments")

    user_name = st.text_input("Enter your Name (as used during booking):")

    if user_name:
        if os.path.exists(APPOINTMENTS_FILE):
            df_appointments = pd.read_excel(APPOINTMENTS_FILE)

            if "Name" in df_appointments.columns:
                # Exact name match (case-insensitive)
                user_appointments = df_appointments[
                    df_appointments["Name"].str.lower() == user_name.lower()
                ]
            else:
                user_appointments = pd.DataFrame()

            if user_appointments.empty:
                st.warning("❌ No appointments found under this name.")
            else:
                st.subheader("📋 Your Appointment(s)")
                user_appointments.index = user_appointments.index + 1
                st.dataframe(user_appointments, use_container_width=True)
        else:
            st.info("No appointments have been booked yet.")
    else:
        st.info("Please enter your Name to check your appointments.")

    if st.button("⬅ Back to Main Page"):
        back_to_mainpage()

# ===============================
# 📊 Staff Dashboard
# ===============================
elif st.session_state.step == "dashboard":
    st.header("📊 Staff Dashboard")

    # Password protection
    password = st.text_input("Enter Staff Password:", type="password")
    if password == "tellmewai":

        # User Records
        st.subheader("📋 User Records")
        if os.path.exists(USERS_FILE):
            df = pd.read_excel(USERS_FILE)

            # Convert categorical 0/1 values into readable labels
            if "Gender" in df.columns:
                df["Gender"] = df["Gender"].replace({0: "Male", 1: "Female"})
            if "Depression" in df.columns:
                df["Depression"] = df["Depression"].replace({0: "No", 1: "Yes"})
            if "Suicidal_Thoughts" in df.columns:
                df["Suicidal_Thoughts"] = df["Suicidal_Thoughts"].replace({0: "No", 1: "Yes"})
            if "Family_History_of_Mental_Illness" in df.columns:
                df["Family_History_of_Mental_Illness"] = df["Family_History_of_Mental_Illness"].replace({0: "No", 1: "Yes"})

            # Reset index to start from 1
            df.index = df.index + 1
            st.dataframe(df, use_container_width=True)

            st.markdown("---")
            st.subheader("📊 Insights")

            # Suicide Risk Distribution
            risk_counts = df["Predicted_Risk"].value_counts()
            fig_risk = px.bar(
                risk_counts,
                x=risk_counts.index,
                y=risk_counts.values,
                title="Suicide Risk Distribution",
                labels={"x": "Risk Level", "y": "Count"},
                color=risk_counts.index,
                color_discrete_map={"Low": "green", "Medium": "orange", "High": "red"}
            )
            st.plotly_chart(fig_risk, use_container_width=True)

            # Gender Distribution (Pie)
            gender_counts = df["Gender"].value_counts()
            fig_gender = px.pie(
                names=gender_counts.index,
                values=gender_counts.values,
                title="Gender Distribution",
                color=gender_counts.index,
                color_discrete_map={"Male": "blue", "Female": "pink"}
            )

            # Academic Pressure (Stacked Bar by Risk Level)
            pressure_risk = df.groupby(["Academic_Pressure", "Predicted_Risk"]).size().reset_index(name="Count")
            fig_pressure = px.bar(
                pressure_risk,
                x="Academic_Pressure",
                y="Count",
                color="Predicted_Risk",
                title="Academic Pressure by Risk Level",
                barmode="stack",
                color_discrete_map={"Low": "green", "Medium": "orange", "High": "red"}
            )

            col1, col2 = st.columns(2)
            col1.plotly_chart(fig_gender, use_container_width=True)
            col2.plotly_chart(fig_pressure, use_container_width=True)

            # Depression
            depression_counts = df["Depression"].value_counts()
            fig_depression = px.bar(
                x=depression_counts.index,
                y=depression_counts.values,
                title="Depression Distribution",
                labels={"x": "Depression", "y": "Count"},
                color=depression_counts.index,
                color_discrete_map={"No": "blue", "Yes": "red"}
            )

            # Suicidal Thoughts
            suicide_counts = df["Suicidal_Thoughts"].value_counts()
            fig_suicide = px.bar(
                x=suicide_counts.index,
                y=suicide_counts.values,
                title="Suicidal Thoughts Distribution",
                labels={"x": "Suicidal Thoughts", "y": "Count"},
                color=suicide_counts.index,
                color_discrete_map={"No": "blue", "Yes": "red"}
            )

            col3, col4 = st.columns(2)
            col3.plotly_chart(fig_depression, use_container_width=True)
            col4.plotly_chart(fig_suicide, use_container_width=True)

    else:
        st.warning("Staff access only. Please enter the correct password.")

    if st.button("⬅ Back to Main Page"):
        back_to_mainpage()



