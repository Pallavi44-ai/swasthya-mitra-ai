# 🌿 Swasthya Mitra AI — Google Gemini Edition

A compassionate, multilingual AI health companion for rural elderly users.
Built with Streamlit + Google Gemini 1.5 Flash (FREE API).

## Features
- 🌍 English, Kannada, Hindi, Telugu
- 🩺 Basic health guidance
- 🧾 Prescription reader
- ⏰ Medicine reminder sidebar
- 🤝 Emotional companion
- 🚨 Emergency detection (auto)
- ✨ Powered by Gemini 1.5 Flash (free tier)

## Step 1 — Get Free Google Gemini API Key
1. Go to https://aistudio.google.com
2. Sign in with your Google account
3. Click "Get API Key" → "Create API Key"
4. Copy the key (starts with AIzaSy...)

## Step 2 — Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501 and paste your API key in the sidebar.

## Step 3 — Deploy to Streamlit Cloud (Free)
1. Push to GitHub
2. Go to https://share.streamlit.io → New App
3. Connect repo, select app.py
4. Add Secret:  GOOGLE_API_KEY = "AIzaSy..."
5. Deploy!

## Emergency
- Ambulance: 108
- Police: 100
