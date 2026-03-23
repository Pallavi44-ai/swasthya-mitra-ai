import streamlit as st
from google import genai
from datetime import datetime

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Swasthya Mitra AI",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ─── SYSTEM PROMPT ──────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
Follow all instructions strictly. Do not ignore any rule.

You are "Swasthya Mitra AI", a compassionate, multilingual AI assistant designed for rural elderly users with low literacy and limited internet access.

Your purpose:
- Provide basic health guidance (NOT diagnosis)
- Act as a friendly emotional companion
- Help manage medicine routines and reminders
- Read and explain doctor prescriptions (from OCR text)
- Detect emotional state (loneliness, sadness)
- Communicate respectfully based on gender and culture

LANGUAGE RULES:
Always respond in the SAME language as the user input.
Supported languages: English, Kannada, Hindi, Telugu
If user mixes languages respond in dominant language.
Use VERY SIMPLE words. Avoid medical jargon.

RESPECT & GENDER HANDLING:
Male use: "Sir", "Anna", "Uncle"
Female use: "Madam", "Akka", "Aunty"
Unknown: polite neutral tone
Always be respectful, warm, and calm.

CORE BEHAVIOR RULES:
NEVER give final medical diagnosis.
ALWAYS include: "Please consult a doctor if symptoms persist."
Keep responses SHORT and voice-friendly.
Speak like a caring human, not a robot.

HEALTH MODE:
If user mentions symptoms:
- Identify common possible issue at simple level
- Give basic home advice like rest, water, etc.
- Suggest doctor visit if needed
- Keep explanation simple and short

PRESCRIPTION MODE:
If input looks like a prescription or OCR text:
- DO NOT change medicine names
- Explain dosage clearly: Morning, Afternoon, Night
- Convert medical abbreviations: BD means 2 times a day, OD means once daily, TDS means 3 times a day
- Keep explanation simple
Then ask: "Should I set reminders for these medicines?"

MEDICINE REMINDER MODE:
If user says "Remind me to take medicine at 8":
Respond: "Okay, I will remind you at 8."

EMOTIONAL COMPANION MODE:
If user sounds sad or lonely:
- Respond with empathy
- Offer conversation
- Say things like: "I am here with you." or "Would you like to talk or hear a story?"
If repeated sadness: Gently suggest contacting family.

EMERGENCY MODE:
If user says chest pain, can't breathe, or emergency:
Respond urgently:
"Please go to the nearest hospital immediately."
Suggest calling family member and calling 108.

OUTPUT STYLE:
- Plain text only
- Short sentences
- Easy to understand
- Friendly and human-like tone
- Optimized for voice playback

PRIORITY: CARE + CLARITY + RESPECT + SIMPLICITY

Always behave like a caring assistant who supports both HEALTH and EMOTIONAL WELL-BEING of the elderly user.
"""

# ─── CSS STYLING ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

:root {
    --saffron:    #E8752A;
    --deep-green: #1A6B3C;
    --soft-green: #2E9E5B;
    --cream:      #FDF8F0;
    --warm-white: #FFFDF7;
    --text-dark:  #1C2B1E;
    --text-mid:   #3D5A42;
    --border:     #D4E8D8;
    --shadow:     rgba(26,107,60,0.12);
    --google-blue: #4285F4;
}

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
    background-color: var(--cream);
}

.main-header {
    background: linear-gradient(135deg, var(--deep-green) 0%, var(--soft-green) 100%);
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 24px;
    box-shadow: 0 8px 32px var(--shadow);
    display: flex;
    align-items: center;
    gap: 16px;
    position: relative;
    overflow: hidden;
}

.main-header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 160px; height: 160px;
    background: rgba(255,255,255,0.06);
    border-radius: 50%;
}

.header-icon { font-size: 52px; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2)); }

.header-text h1 { color: white; font-size: 26px; font-weight: 800; margin: 0; }
.header-text p  { color: rgba(255,255,255,0.82); font-size: 13px; margin: 4px 0 0 0; }

.gemini-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(66,133,244,0.15);
    border: 1px solid rgba(66,133,244,0.4);
    color: #4285F4;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 50px;
    letter-spacing: 0.5px;
    margin-top: 6px;
}

.user-bubble {
    background: linear-gradient(135deg, var(--saffron) 0%, #D4621E 100%);
    color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 14px 18px;
    margin: 8px 0 8px 60px;
    font-size: 15px;
    line-height: 1.6;
    box-shadow: 0 3px 12px rgba(232,117,42,0.3);
    word-wrap: break-word;
}

.bot-bubble {
    background: var(--warm-white);
    color: var(--text-dark);
    border-radius: 18px 18px 18px 4px;
    padding: 14px 18px;
    margin: 8px 60px 8px 0;
    font-size: 15px;
    line-height: 1.7;
    box-shadow: 0 3px 12px var(--shadow);
    border: 1px solid var(--border);
    word-wrap: break-word;
}

.emergency-bubble {
    background: linear-gradient(135deg, #D32F2F, #B71C1C);
    color: white;
    border-radius: 18px;
    padding: 16px 20px;
    margin: 8px 0;
    font-size: 15px;
    font-weight: 700;
    line-height: 1.6;
    border-left: 5px solid #FF5252;
    box-shadow: 0 4px 16px rgba(211,47,47,0.35);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { box-shadow: 0 4px 16px rgba(211,47,47,0.35); }
    50%       { box-shadow: 0 4px 28px rgba(211,47,47,0.65); }
}

.msg-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 4px;
    opacity: 0.65;
}

[data-testid="stSidebar"] {
    background: var(--warm-white);
    border-right: 1px solid var(--border);
}

.sidebar-title {
    font-size: 13px;
    font-weight: 800;
    color: var(--deep-green);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 10px;
}

.reminder-card {
    background: white;
    border-radius: 10px;
    padding: 10px 14px;
    margin: 6px 0;
    border-left: 4px solid var(--soft-green);
    font-size: 13px;
    color: var(--text-dark);
    box-shadow: 0 2px 8px var(--shadow);
}

.tip-card {
    background: linear-gradient(135deg, #E8F5E9, #F1F8E9);
    border-radius: 12px;
    padding: 14px;
    font-size: 13px;
    color: var(--text-mid);
    border: 1px solid #C8E6C9;
    line-height: 1.6;
}

.stTextArea textarea {
    border-radius: 14px !important;
    border: 2px solid var(--border) !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 15px !important;
    background: var(--warm-white) !important;
}

.stTextArea textarea:focus {
    border-color: var(--soft-green) !important;
    box-shadow: 0 0 0 3px rgba(46,158,91,0.15) !important;
}

.stButton > button {
    border-radius: 50px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px var(--shadow) !important;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #E8F5E9;
    color: var(--deep-green);
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 50px;
    letter-spacing: 0.5px;
}

.status-dot {
    width: 7px; height: 7px;
    background: var(--soft-green);
    border-radius: 50%;
    animation: blink 1.5s infinite;
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTS ───────────────────────────────────────────────────────────────
EMERGENCY_KEYWORDS = [
    "chest pain", "can't breathe", "cannot breathe",
    "emergency", "heart attack", "unconscious", "stroke",
    "ಎದೆ ನೋವು", "ಉಸಿರಾಟ", "ಅಪಾಯ",
    "सीने में दर्द", "सांस नहीं", "आपातकाल",
    "గుండె నొప్పి", "శ్వాస", "అత్యవసర"
]

QUICK_PROMPTS = {
    "English": ["I have a headache 🤕", "I feel lonely 😔", "Explain my prescription 📄", "Set medicine reminder ⏰"],
    "Kannada": ["ನನಗೆ ತಲೆನೋವು 🤕", "ನಾನು ಒಂಟಿಯಾಗಿದ್ದೇನೆ 😔", "ನನ್ನ ಪ್ರಿಸ್ಕ್ರಿಪ್ಶನ್ ವಿವರಿಸಿ 📄", "ಔಷಧ ರಿಮೈಂಡರ್ ⏰"],
    "Hindi":   ["मुझे सिरदर्द है 🤕", "मैं अकेला हूं 😔", "प्रिस्क्रिप्शन समझाइए 📄", "दवाई याद दिलाइए ⏰"],
    "Telugu":  ["నాకు తలనొప్పి 🤕", "నేను ఒంటరిగా ఉన్నాను 😔", "ప్రిస్క్రిప్షన్ వివరించండి 📄", "మందు రిమైండర్ ⏰"],
}

DAILY_TIPS = {
    "English": "💧 Drink 6–8 glasses of water daily. Stay hydrated for good health!",
    "Kannada": "💧 ದಿನಕ್ಕೆ 6-8 ಲೋಟ ನೀರು ಕುಡಿಯಿರಿ. ಆರೋಗ್ಯಕ್ಕಾಗಿ ನೀರು ಮುಖ್ಯ!",
    "Hindi":   "💧 रोज 6-8 गिलास पानी पीएं। स्वस्थ रहें!",
    "Telugu":  "💧 రోజూ 6-8 గ్లాసుల నీరు తాగండి. ఆరోగ్యంగా ఉండండి!",
}

WELCOME_MSG = {
    "English": "🙏 Namaste! I am Swasthya Mitra, your health companion.\n\nI can help you with:\n• Health questions & advice\n• Reading prescriptions\n• Medicine reminders\n• Talking when you feel lonely\n\nHow can I help you today?",
    "Kannada": "🙏 ನಮಸ್ಕಾರ! ನಾನು ಸ್ವಾಸ್ಥ್ಯ ಮಿತ್ರ.\n\n• ಆರೋಗ್ಯ ಸಲಹೆ\n• ಪ್ರಿಸ್ಕ್ರಿಪ್ಶನ್ ಓದುವುದು\n• ಔಷಧ ರಿಮೈಂಡರ್\n• ಮಾತನಾಡಲು\n\nಇಂದು ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?",
    "Hindi":   "🙏 नमस्ते! मैं स्वास्थ्य मित्र हूं।\n\n• स्वास्थ्य सलाह\n• प्रिस्क्रिप्शन पढ़ना\n• दवाई याद दिलाना\n• बात करना\n\nआज कैसे मदद करूं?",
    "Telugu":  "🙏 నమస్కారం! నేను స్వాస్థ్య మిత్ర.\n\n• ఆరోగ్య సలహా\n• ప్రిస్క్రిప్షన్ చదవడం\n• మందు రిమైండర్\n• మాట్లాడడం\n\nఈరోజు ఎలా సహాయపడాలి?",
}

EMERGENCY_RESPONSE = {
    "English": "🚨 EMERGENCY ALERT!\n\nPlease go to the nearest hospital IMMEDIATELY.\n📞 Call 108 (Ambulance) right now.\nAsk a family member or neighbour to help you.",
    "Kannada": "🚨 ತುರ್ತು ಸ್ಥಿತಿ!\n\nತಕ್ಷಣ ಹತ್ತಿರದ ಆಸ್ಪತ್ರೆಗೆ ಹೋಗಿ.\n📞 108 ಕರೆ ಮಾಡಿ.\nಕುಟುಂಬ ಸದಸ್ಯರನ್ನು ಕರೆಯಿರಿ.",
    "Hindi":   "🚨 आपातकाल!\n\nतुरंत नजदीकी अस्पताल जाएं।\n📞 अभी 108 पर कॉल करें।\nपरिवार के किसी सदस्य को बुलाएं।",
    "Telugu":  "🚨 అత్యవసర పరిస్థితి!\n\nవెంటనే దగ్గరలోని ఆసుపత్రికి వెళ్ళండి.\n📞 ఇప్పుడే 108 కు కాల్ చేయండి.\nకుటుంబ సభ్యుడిని పిలవండి.",
}

# ─── SESSION STATE ────────────────────────────────────────────────────────────
if "messages"  not in st.session_state: st.session_state.messages  = []
if "language"  not in st.session_state: st.session_state.language  = "English"
if "reminders" not in st.session_state: st.session_state.reminders = []
if "api_key"   not in st.session_state: st.session_state.api_key   = ""

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def is_emergency(text: str) -> bool:
    return any(kw in text.lower() for kw in EMERGENCY_KEYWORDS)

def get_gemini_response(user_message: str) -> str:
    """Send message to Gemini and return full response."""
    
    from google import genai

    API_KEY = st.session_state.get("api_key")

    client = genai.Client(api_key=API_KEY)

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=user_message
    )

    return response.text
    # Build history for Gemini (role: user / model)
    history = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})

    chat = model.start_chat(history=history)
    response = chat.send_message(user_message)
    return response.text

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">⚙️ Settings</div>', unsafe_allow_html=True)

    # 🔑 API Key input
    api_input = st.text_input(
        "AIzaSyDszupZPws04WRcldiQwubzddAVCJkk7-k",
        type="password",
        value=st.session_state.get("api_key", ""),
        placeholder="Paste your API key here...",
        help="Get free key at https://aistudio.google.com"
    )

    if api_input:
        st.session_state.api_key = api_input
        st.success("✅ Key saved!", icon="🔐")

    st.caption("👉 Get free key: https://aistudio.google.com")

    st.markdown("---")

    # 🌍 Language
    st.markdown('<div class="sidebar-title">🌍 Language</div>', unsafe_allow_html=True)

    lang_options = ["English", "Kannada", "Hindi", "Telugu"]

    lang = st.selectbox(
        "Language",
        lang_options,
        index=lang_options.index(st.session_state.get("language", "English")),
        label_visibility="collapsed"
    )

    st.session_state.language = lang

    st.markdown("---")
    
    API_KEY = st.session_state.get("api_key")

if not API_KEY:
    st.warning("⚠️ Please enter your API key in the sidebar")
    st.stop()

    # Medicine Reminders
    st.markdown('<div class="sidebar-title">⏰ Medicine Reminders</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        med_name = st.text_input("Medicine", placeholder="e.g. Metformin", label_visibility="collapsed")
    with col2:
        med_time = st.text_input("Time", placeholder="8:00 AM", label_visibility="collapsed")

    if st.button("➕ Add Reminder", use_container_width=True):
        if med_name and med_time:
            st.session_state.reminders.append({"name": med_name, "time": med_time})
            st.success(f"✅ Reminder set for {med_name} at {med_time}!")
        else:
            st.warning("Enter both medicine name and time.")

    for i, r in enumerate(st.session_state.reminders):
        col_r, col_d = st.columns([4, 1])
        with col_r:
            st.markdown(f'<div class="reminder-card">💊 <b>{r["name"]}</b> — {r["time"]}</div>', unsafe_allow_html=True)
        with col_d:
            if st.button("✕", key=f"del_{i}"):
                st.session_state.reminders.pop(i)
                st.rerun()

    if not st.session_state.reminders:
        st.caption("No reminders yet. Add one above.")

    st.markdown("---")

    # Daily Tip
    st.markdown('<div class="sidebar-title">💡 Daily Health Tip</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="tip-card">{DAILY_TIPS.get(lang, DAILY_TIPS["English"])}</div>', unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown(
        '<div style="font-size:11px;color:#888;text-align:center;margin-top:10px;">Swasthya Mitra AI v1.0<br>Powered by Google Gemini ✨</div>',
        unsafe_allow_html=True
    )

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <div class="header-icon">🌿</div>
    <div class="header-text">
        <h1>Swasthya Mitra AI</h1>
        <p>Your caring health companion · स्वास्थ्य मित्र · ಆರೋಗ್ಯ ಮಿತ್ರ · స్వాస్థ్య మిత్ర</p>
        <span class="gemini-badge">✨ Powered by Google Gemini</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Status row
col_s1, col_s2 = st.columns([1, 1])
with col_s1:
    st.markdown('<span class="status-badge"><span class="status-dot"></span>Online · Ready to help</span>', unsafe_allow_html=True)
with col_s2:
    st.markdown(f'<div style="text-align:right;font-size:12px;color:#888;">{datetime.now().strftime("%d %b %Y, %I:%M %p")}</div>', unsafe_allow_html=True)

# API key warning
if not st.session_state.api_key:
    st.warning("⚠️ Enter your **Google Gemini API Key** in the sidebar to start. It's FREE at [aistudio.google.com](https://aistudio.google.com)", icon="🔑")

# ─── CHAT HISTORY ─────────────────────────────────────────────────────────────
with st.container():
    if not st.session_state.messages:
        welcome = WELCOME_MSG.get(st.session_state.language, WELCOME_MSG["English"])
        st.markdown(
            f'<div class="bot-bubble"><div class="msg-label">🌿 Swasthya Mitra</div>{welcome}</div>',
            unsafe_allow_html=True
        )

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="user-bubble"><div class="msg-label" style="opacity:0.7">You</div>{msg["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            is_emerg = any(kw in msg["content"] for kw in ["🚨", "hospital IMMEDIATELY", "108"])
            bubble = "emergency-bubble" if is_emerg else "bot-bubble"
            st.markdown(
                f'<div class="{bubble}"><div class="msg-label">🌿 Swasthya Mitra</div>{msg["content"]}</div>',
                unsafe_allow_html=True
            )

# ─── QUICK PROMPTS ────────────────────────────────────────────────────────────
st.markdown("<br>**Quick prompts:**", unsafe_allow_html=True)
prompts = QUICK_PROMPTS.get(st.session_state.language, QUICK_PROMPTS["English"])
cols = st.columns(len(prompts))
for i, (col, prompt) in enumerate(zip(cols, prompts)):
    with col:
        if st.button(prompt, key=f"qp_{i}", use_container_width=True):
            st.session_state["quick_prompt"] = prompt

# ─── INPUT AREA ───────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

PLACEHOLDERS = {
    "English": "Type here... (health question, prescription text, or just talk 🙏)",
    "Kannada": "ಇಲ್ಲಿ ಟೈಪ್ ಮಾಡಿ...",
    "Hindi":   "यहाँ लिखें...",
    "Telugu":  "ఇక్కడ టైప్ చేయండి...",
}

default_val = st.session_state.pop("quick_prompt", "")

user_input = st.text_area(
    "Message",
    value=default_val,
    placeholder=PLACEHOLDERS.get(st.session_state.language, PLACEHOLDERS["English"]),
    height=100,
    label_visibility="collapsed",
)

col_a, col_b = st.columns([3, 1])
with col_a:
    send = st.button("🌿 Send Message", type="primary", use_container_width=True)
with col_b:
    if st.button("✕ Clear", use_container_width=True):
        st.rerun()

# ─── SEND LOGIC ───────────────────────────────────────────────────────────────
if send and user_input.strip():
    if not st.session_state.api_key:
        st.error("Please enter your Google Gemini API key in the sidebar first.")
    else:
        text = user_input.strip()
        st.session_state.messages.append({"role": "user", "content": text})

        if is_emergency(text):
            reply = EMERGENCY_RESPONSE.get(st.session_state.language, EMERGENCY_RESPONSE["English"])
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()
        else:
            with st.spinner("Swasthya Mitra is thinking... 🌿"):
                try:
                    reply = get_gemini_response(text)
                    st.session_state.messages.append({"role": "assistant", "content": reply})

                    if any(kw in text.lower() for kw in ["remind", "reminder", "याद", "ರಿಮೈಂಡರ್", "రిమైండర్"]):
                        st.toast("💊 Add reminders quickly in the sidebar!", icon="⏰")

                except Exception as e:
                    err = str(e)
                    if "API_KEY" in err.upper() or "invalid" in err.lower():
                        st.error("❌ Invalid API key. Please check your Gemini key in the sidebar.")
                    elif "quota" in err.lower():
                        st.error("❌ API quota exceeded. Try again later or check your Google AI Studio plan.")
                    else:
                        st.error(f"❌ Error: {err}")
                    st.session_state.messages.pop()  # remove failed user message

            st.rerun()

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    '<div style="text-align:center;font-size:12px;color:#aaa;padding:10px;">'
    '⚕️ Swasthya Mitra AI provides general health guidance only — not medical diagnosis.<br>'
    'Always consult a qualified doctor for medical advice. &nbsp;|&nbsp; Emergency: Call <b>108</b>'
    '</div>',
    unsafe_allow_html=True
)
