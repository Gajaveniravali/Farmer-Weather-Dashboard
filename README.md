# Farmer Weather Dashboard

A weather dashboard for farmers with multi-language support (English, Telugu, Hindi) to suggest appropriate crops based on weather conditions.

## Project Structure

```
Farmer-Weather-Dashboard/
├── backend/
│   └── app.py                 # Flask backend with routing and logic
├── frontend/
│   ├── templates/
│   │   └── index.html         # Main HTML template
│   └── static/
│       ├── script.js          # Frontend JavaScript (voice recognition, TTS)
│       └── style.css          # Stylesheet
├── run.py                     # Entry point for the application
├── requirements.txt           # Python dependencies
├── README.md
└── .gitignore
```

## Features
- 🌤️ Real-time weather data via OpenWeather API
- 🎤 Voice input for location, crop, and season
- 🌐 Multi-language UI (English, Telugu, Hindi)
- 💾 Season history with crop recommendations
- 🌾 Intelligent crop suggestions based on weather conditions

## Prerequisites
- Python 3.8+
- Virtual environment (recommended)

## Quick Start

1. **Clone and set up the environment:**

```powershell
cd Farmer-Weather-Dashboard
python -m venv venv
& venv\Scripts\Activate.ps1
```

2. **Install dependencies:**

```powershell
pip install -r requirements.txt
```

3. **Run the application:**

```powershell
python run.py
```

The app will start on `http://127.0.0.1:5000`.

## Usage
1. Select your language (English, తెలుగు, हिन्दी)
2. Enter a city name
3. (Optional) Enter a crop name and/or season preference
4. Use 🎤 button for voice input or click "Get Weather"
5. View crop recommendations based on current weather

## Configuration
- **API Key**: The OpenWeather API key is stored in `backend/app.py` (line ~8)
  - Consider moving this to an environment variable for production
- **Secret Key**: Change the Flask secret key in `backend/app.py` before deployment

## Development Notes
- Backend logic: `backend/app.py`
- Frontend UI: `frontend/templates/index.html`
- Frontend interactions: `frontend/static/script.js` (voice recognition, TTS)
- Styling: `frontend/static/style.css`
