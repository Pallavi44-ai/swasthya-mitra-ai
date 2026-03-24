import streamlit as st
from google import genai
from datetime import datetime

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Swasthya Mitra AI",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── SYSTEM PROMPT ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are "Swasthya Mitra AI", a compassionate, multilingual AI health assistant for rural elderly users.

LANGUAGE: Always reply in the SAME language the user writes in.
Supported: English, Kannada, Hindi, Telugu. Use very simple words.

RESPECT: 
- Male → Sir, Anna, Uncle
- Female → Madam, Akka, Aunty
- Always warm, calm, respectful.

RULES:
- NEVER give a medical diagnosis.
- ALWAYS say: "Please consult a doctor if symptoms persist."
- Keep responses SHORT and simple.
- Speak like a caring human, not a robot.

HEALTH: If user mentions symptoms → give simple home advice (rest, water) → suggest doctor.

PRESCRIPTION: If user pastes prescription text →
- Explain each medicine simply (morning/afternoon/night)
- BD = 2 times a day, OD = once a day, TDS = 3 times a day
- Ask: "Should I set reminders for these medicines?"

EMOTIONAL: If user sounds sad or lonely → respond with empathy → offer to talk.

EMERGENCY: If user says chest pain / can't breathe / emergency →
Immediately say: "Please go to the nearest hospital! Call 108 now!"

PRIORITY: CARE + CLARITY + RESPECT + SIMPLICITY
"""

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif !important;
}

/* Header banner */
.app-header {
    background: linear-gradient(135deg, #1A6B3C, #2E9E5B);
    border-radius: 18px;
    padding: 22px 28px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 14px;
    box-shadow: 0 6px 24px rgba(26,107,60,0.25);
}
.app-header h1 { color: white; font-size: 22px; font-weight: 800; margin: 0; }
.app-header p  { color: rgba(255,255,255,0.85); font-size: 12px; margin: 3px 0 0; }
.badge {
    display:inline-block;
    background:rgba(66,133,244,0.25);
    border:1px solid rgba(66,133,244,0.5);
    color:#90CAF9; font-size:10px; font-weight:700;
    padding:2px 8px; border-radius:50px; margin-top:5px;
}

/* Native chat message tweaks */
[data-testid="stChatMessage"] {
    border-radius: 16px !important;
    padding: 4px 8px !important;
}

/* Chat input box — make it very visible */
[data-testid="stChatInput"] textarea {
    background: white !important;
    color: #1C2B1E !important;
    border: 2.5px solid #2E9E5B !important;
    border-radius: 14px !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 16px !important;
    min-height: 54px !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #1A6B3C !important;
    box-shadow: 0 0 0 3px rgba(46,158,91,0.2) !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #7DAF87 !important;
    font-size: 14px !important;
}

/* Send button inside chat input */
[data-testid="stChatInputSubmitButton"] {
    background: #2E9E5B !important;
    border-radius: 10px !important;
}

/* Quick prompt buttons */
div[data-testid="column"] .stButton > button {
    border-radius: 50px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    border: 1.5px solid #A8D5B5 !important;
    background: white !important;
    color: #1A6B3C !important;
    transition: all 0.2s !important;
}
div[data-testid="column"] .stButton > button:hover {
    background: #E8F5E9 !important;
    border-color: #2E9E5B !important;
    transform: translateY(-1px) !important;
}

/* Mic section */
.mic-box {
    background: white;
    border: 2px dashed #2E9E5B;
    border-radius: 14px;
    padding: 12px 16px;
    margin-bottom: 10px;
    text-align: center;
}
.mic-title {
    font-size: 13px; font-weight: 800;
    color: #1A6B3C; margin-bottom: 8px;
}
.mic-result {
    background: #E8F5E9; border-radius: 10px;
    padding: 10px 14px; font-size: 14px;
    color: #1A6B3C; font-weight: 600;
    border-left: 4px solid #2E9E5B;
    margin-top: 8px; text-align: left;
}

/* Reminder card */
.reminder-card {
    background: white; border-radius: 10px;
    padding: 9px 13px; margin: 5px 0;
    border-left: 4px solid #2E9E5B;
    font-size: 13px; color: #1C2B1E;
    box-shadow: 0 2px 8px rgba(26,107,60,0.1);
}
.tip-card {
    background: linear-gradient(135deg,#E8F5E9,#F1F8E9);
    border-radius: 12px; padding: 12px;
    font-size: 13px; color: #3D5A42;
    border: 1px solid #C8E6C9; line-height: 1.6;
}
.sidebar-title {
    font-size: 12px; font-weight: 800; color: #1A6B3C;
    text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;
}
.status-dot {
    display:inline-block; width:8px; height:8px;
    background:#2E9E5B; border-radius:50%;
    animation: blink 1.5s infinite; margin-right:5px;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; max-width: 780px !important; }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
EMERGENCY_KEYWORDS = [
    "chest pain","can't breathe","cannot breathe","heart attack",
    "emergency","unconscious","stroke","not breathing",
    "ಎದೆ ನೋವು","ಉಸಿರಾಟ","ಅಪಾಯ",
    "सीने में दर्द","सांस नहीं","आपातकाल",
    "గుండె నొప్పి","శ్వాస","అత్యవసర"
]

EMERGENCY_RESPONSE = {
    "English": "🚨 **EMERGENCY!**\n\nPlease go to the **nearest hospital IMMEDIATELY!**\n\n📞 **Call 108** (Ambulance) right now!\n\nAsk a family member or neighbour to help you. Do not wait!",
    "Kannada": "🚨 **ತುರ್ತು ಸ್ಥಿತಿ!**\n\nತಕ್ಷಣ ಹತ್ತಿರದ ಆಸ್ಪತ್ರೆಗೆ ಹೋಗಿ!\n\n📞 **108** ಕರೆ ಮಾಡಿ!\n\nಕುಟುಂಬ ಸದಸ್ಯರನ್ನು ಕರೆಯಿರಿ!",
    "Hindi":   "🚨 **आपातकाल!**\n\nतुरंत नजदीकी अस्पताल जाएं!\n\n📞 **108** पर अभी कॉल करें!\n\nपरिवार को बुलाएं!",
    "Telugu":  "🚨 **అత్యవసరం!**\n\nవెంటనే దగ్గరలోని ఆసుపత్రికి వెళ్ళండి!\n\n📞 **108** కు ఇప్పుడే కాల్ చేయండి!\n\nకుటుంబ సభ్యుడిని పిలవండి!",
}

WELCOME = {
    "English": "🙏 Namaste! I am **Swasthya Mitra**, your health companion.\n\nI can help you with:\n- ❓ Health questions & advice\n- 🧾 Reading & explaining prescriptions\n- ⏰ Medicine reminders\n- 🤝 Talking when you feel lonely\n\n**How can I help you today?**",
    "Kannada": "🙏 ನಮಸ್ಕಾರ! ನಾನು **ಸ್ವಾಸ್ಥ್ಯ ಮಿತ್ರ**.\n\n- ❓ ಆರೋಗ್ಯ ಸಲಹೆ\n- 🧾 ಪ್ರಿಸ್ಕ್ರಿಪ್ಶನ್ ವಿವರಣೆ\n- ⏰ ಔಷಧ ರಿಮೈಂಡರ್\n- 🤝 ಮಾತನಾಡಲು\n\n**ಇಂದು ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?**",
    "Hindi":   "🙏 नमस्ते! मैं **स्वास्थ्य मित्र** हूं।\n\n- ❓ स्वास्थ्य सलाह\n- 🧾 प्रिस्क्रिप्शन पढ़ना\n- ⏰ दवाई याद दिलाना\n- 🤝 बात करना\n\n**आज कैसे मदद करूं?**",
    "Telugu":  "🙏 నమస్కారం! నేను **స్వాస్థ్య మిత్ర**.\n\n- ❓ ఆరోగ్య సలహా\n- 🧾 ప్రిస్క్రిప్షన్ వివరణ\n- ⏰ మందు రిమైండర్\n- 🤝 మాట్లాడడం\n\n**ఈరోజు ఎలా సహాయపడాలి?**",
}

QUICK_PROMPTS = {
    "English": ["🤕 I have a headache", "😔 I feel lonely", "📄 Explain my prescription", "⏰ Medicine reminder"],
    "Kannada": ["🤕 ತಲೆನೋವು ಇದೆ",    "😔 ಒಂಟಿಯಾಗಿದ್ದೇನೆ",     "📄 ಪ್ರಿಸ್ಕ್ರಿಪ್ಶನ್ ವಿವರಿಸಿ","⏰ ಔಷಧ ರಿಮೈಂಡರ್"],
    "Hindi":   ["🤕 सिरदर्द है",       "😔 अकेला/अकेली हूं",     "📄 प्रिस्क्रिप्शन समझाइए", "⏰ दवाई याद दिलाइए"],
    "Telugu":  ["🤕 తలనొప్పి",         "😔 ఒంటరిగా ఉన్నాను",    "📄 ప్రిస్క్రిప్షన్ వివరించండి","⏰ మందు రిమైండర్"],
}

DAILY_TIPS = {
    "English": "💧 Drink 6–8 glasses of water daily. Stay hydrated!",
    "Kannada": "💧 ದಿನಕ್ಕೆ 6-8 ಲೋಟ ನೀರು ಕುಡಿಯಿರಿ!",
    "Hindi":   "💧 रोज 6-8 गिलास पानी पीएं!",
    "Telugu":  "💧 రోజూ 6-8 గ్లాసుల నీరు తాగండి!",
}

PLACEHOLDERS = {
    "English": "Type your message here and press Enter ↵  (or use mic below)",
    "Kannada": "ಇಲ್ಲಿ ಸಂದೇಶ ಟೈಪ್ ಮಾಡಿ ಮತ್ತು Enter ↵ ಒತ್ತಿ",
    "Hindi":   "यहाँ संदेश लिखें और Enter ↵ दबाएं",
    "Telugu":  "ఇక్కడ సందేశం టైప్ చేసి Enter ↵ నొక్కండి",
}

MIC_LANGS = {"English":"en-IN","Kannada":"kn-IN","Hindi":"hi-IN","Telugu":"te-IN"}

# ── SESSION STATE ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "messages":  [],
        "language":  "English",
        "reminders": [],
        "api_key":   "",
        "pending_prompt": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── HELPERS ───────────────────────────────────────────────────────────────────
def is_emergency(text: str) -> bool:
    return any(kw in text.lower() for kw in EMERGENCY_KEYWORDS)

def call_gemini(user_text: str) -> str:
    """Call Gemini and return the reply string."""

    from google import genai

    API_KEY = st.session_state.get("api_key")

    client = genai.Client(api_key=API_KEY)

    response = client.models.generate_content(
        model_name="gemini-2.0-flash",
        contents=user_text
    )

    return response.text
    # Build history (all previous turns)
    history = []
    for m in st.session_state.messages:
        role = "user" if m["role"] == "user" else "model"
        history.append({"role": role, "parts": [m["content"]]})

    chat = model.start_chat(history=history)
    resp = chat.send_message(user_text)
    return resp.text

def process_message(user_text: str):
    """Add user msg, call AI or emergency, add reply — then rerun."""
    user_text = user_text.strip()
    if not user_text:
        return

    # 1. Save user message
    st.session_state.messages.append({"role": "user", "content": user_text})

    # 2. Emergency check
    if is_emergency(user_text):
        reply = EMERGENCY_RESPONSE.get(st.session_state.language, EMERGENCY_RESPONSE["English"])
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()
        return

    # 3. Call Gemini
    try:
        reply = call_gemini(user_text)
    except Exception as e:
        err = str(e)
        if "API_KEY" in err.upper() or "invalid" in err.lower():
            reply = "❌ Invalid API key. Please check your Gemini key in the sidebar."
        elif "quota" in err.lower():
            reply = "❌ API quota exceeded. Please try again later."
        else:
            reply = f"❌ Something went wrong: {err}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # API Key
    st.markdown('<div class="sidebar-title">⚙️ API Key</div>', unsafe_allow_html=True)
    api_in = st.text_input("Gemini Key", type="password",
                           value=st.session_state.api_key,
                           placeholder="AIzaSy...",
                           label_visibility="collapsed")
    if api_in:
        st.session_state.api_key = api_in
        st.success("✅ Key saved!", icon="🔐")
    st.caption("Free key → [aistudio.google.com](https://aistudio.google.com)")

    st.divider()

    # Language
    st.markdown('<div class="sidebar-title">🌍 Language</div>', unsafe_allow_html=True)
    langs = ["English","Kannada","Hindi","Telugu"]
    st.session_state.language = st.selectbox(
        "Lang", langs,
        index=langs.index(st.session_state.language),
        label_visibility="collapsed"
    )

    st.divider()

    # Reminders
    st.markdown('<div class="sidebar-title">⏰ Medicine Reminders</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: mname = st.text_input("Med", placeholder="e.g. Paracetamol", label_visibility="collapsed")
    with c2: mtime = st.text_input("Time", placeholder="8:00 AM", label_visibility="collapsed")

    if st.button("➕ Add Reminder", use_container_width=True):
        if mname and mtime:
            st.session_state.reminders.append({"name": mname, "time": mtime})
            st.success(f"✅ {mname} at {mtime}")
        else:
            st.warning("Enter medicine name and time.")

    for i, r in enumerate(st.session_state.reminders):
        ca, cb = st.columns([4,1])
        with ca:
            st.markdown(f'<div class="reminder-card">💊 <b>{r["name"]}</b> — {r["time"]}</div>', unsafe_allow_html=True)
        with cb:
            if st.button("✕", key=f"del{i}"):
                st.session_state.reminders.pop(i)
                st.rerun()

    if not st.session_state.reminders:
        st.caption("No reminders yet.")

    st.divider()

    # Daily tip
    st.markdown('<div class="sidebar-title">💡 Daily Tip</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="tip-card">{DAILY_TIPS[st.session_state.language]}</div>', unsafe_allow_html=True)

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown('<div style="font-size:11px;color:#aaa;text-align:center;margin-top:6px;">Swasthya Mitra AI v2.0<br>✨ Google Gemini</div>', unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="app-header">
    <div style="font-size:46px">🌿</div>
    <div>
        <h1>Swasthya Mitra AI</h1>
        <p>Your caring health companion · स्वास्थ्य मित्र · ಆರೋಗ್ಯ ಮಿತ್ರ · స్వాస్థ్య మిత్ర</p>
        <span class="badge">✨ Google Gemini · {datetime.now().strftime("%d %b %Y")}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Status + API warning
col1, col2 = st.columns([1,1])
with col1:
    st.markdown('<span class="status-dot"></span><span style="font-size:12px;font-weight:700;color:#1A6B3C;">Online · Ready</span>', unsafe_allow_html=True)
with col2:
    if not st.session_state.api_key:
        st.error("⚠️ Add API key in sidebar →", icon="🔑")

st.divider()

# ── CHAT HISTORY (uses st.chat_message — always renders correctly) ─────────────
lang = st.session_state.language

# Show welcome if no messages yet
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🌿"):
        st.markdown(WELCOME[lang])

# Render all stored messages
for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "🌿"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ── QUICK PROMPTS ─────────────────────────────────────────────────────────────
st.markdown("**Quick prompts:**")
prompts = QUICK_PROMPTS[lang]
qc = st.columns(len(prompts))
for i, (col, p) in enumerate(zip(qc, prompts)):
    with col:
        if st.button(p, key=f"qp{i}", use_container_width=True):
            st.session_state.pending_prompt = p

# ── MIC INPUT (optional voice) ────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

try:
    from streamlit_mic_recorder import mic_recorder
    import speech_recognition as sr, io

    with st.expander("🎤 Voice Input — Click to expand and record"):
        st.markdown(f"**Speak in {lang}** → recording will convert to text automatically")
        audio = mic_recorder(
            start_prompt="🎤 Start Speaking",
            stop_prompt="⏹️ Stop Recording",
            just_once=True,
            use_container_width=True,
            key="mic"
        )
        if audio and audio.get("bytes"):
            recognizer = sr.Recognizer()
            try:
                audio_file = io.BytesIO(audio["bytes"])
                with sr.AudioFile(audio_file) as source:
                    audio_data = recognizer.record(source)
                transcript = recognizer.recognize_google(
                    audio_data, language=MIC_LANGS.get(lang, "en-IN")
                )
                if transcript:
                    st.success(f'🎤 Heard: **"{transcript}"**')
                    st.session_state.pending_prompt = transcript
                    st.rerun()
            except sr.UnknownValueError:
                st.warning("Could not understand. Please speak clearly and try again.")
            except Exception as e:
                st.error(f"Voice error: {e}")
except ImportError:
    with st.expander("🎤 Voice Input — Install to enable"):
        st.info("Run this to enable voice:\n```\npip install streamlit-mic-recorder SpeechRecognition\n```")

# ── PROCESS PENDING PROMPT (from quick button or mic) ─────────────────────────
if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
    if st.session_state.api_key:
        with st.spinner("🌿 Swasthya Mitra is thinking..."):
            process_message(prompt)
    else:
        st.warning("Please add your Gemini API key in the sidebar first.")

# ── CHAT INPUT (always visible at bottom, native Streamlit) ───────────────────
user_input = st.chat_input(
    placeholder=PLACEHOLDERS.get(lang, PLACEHOLDERS["English"])
)

if user_input:
    if not st.session_state.api_key:
        st.warning("⚠️ Please enter your Gemini API key in the sidebar first.")
        st.stop()
    with st.spinner("🌿 Swasthya Mitra is thinking..."):
        process_message(user_input)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="text-align:center;font-size:11px;color:#bbb;padding:12px 0 4px;">'
    '⚕️ General health guidance only — not a medical diagnosis. '
    'Always consult a qualified doctor. | Emergency: <b>108</b>'
    '</div>',
    unsafe_allow_html=True
)
