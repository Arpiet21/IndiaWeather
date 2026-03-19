# IndiaWeather POC
Real-time Indian Climate Map — Web + iOS + Android compatible

## Project Structure
```
Weather App/
├── index.html              # Web frontend (Leaflet map)
├── css/style.css           # Dark theme UI
├── js/
│   ├── config.js           # API endpoint config
│   └── app.js              # Map logic + API calls
└── backend/
    ├── main.py             # Python FastAPI backend
    ├── requirements.txt    # Python dependencies
    └── .env.example        # Environment variables template
```

## Quick Start

### 1. Get API Key
- Sign up at https://openweathermap.org/api (free tier works)
- Copy your API key

### 2. Start Python Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env → add your OWM_API_KEY
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Open the Web App
Open `index.html` in your browser directly.
The app works with mock data even without the backend running.

### 4. API Explorer
Visit http://localhost:8000/docs for interactive Swagger UI.

## API Endpoints

| Method | Endpoint             | Description                        |
|--------|---------------------|------------------------------------|
| GET    | /                   | Health check                       |
| GET    | /weather/all        | All 20+ cities current weather     |
| GET    | /weather/{city}     | Single city weather                |
| GET    | /forecast/{city}    | 7-day forecast                     |
| GET    | /alerts             | Active IMD-style alerts            |
| GET    | /monsoon            | Monsoon tracker status             |
| GET    | /cities             | City list with climate metadata    |

## Mobile App (iOS & Android)

The FastAPI backend is designed as a mobile-ready REST API.

### React Native (Expo)
```bash
npx create-expo-app IndiaWeatherMobile
# Use fetch() to call http://YOUR_MACHINE_IP:8000/weather/all
```

### Flutter
```bash
flutter create india_weather_app
# Use http package → GET http://YOUR_MACHINE_IP:8000/weather/all
```

### Key mobile endpoints used:
- `/weather/all` → home screen city list
- `/weather/{city}` → city detail screen
- `/forecast/{city}` → forecast screen
- `/alerts` → push notification triggers
- `/monsoon` → monsoon widget

## Features (POC)
- 25 Indian cities across all 7 climate zones
- Real-time temperature, humidity, wind, rainfall, AQI
- 5 map layers: Temperature / Rainfall / Wind / Humidity / AQI
- Monsoon tracker widget
- Active weather alerts
- 7-day forecast
- City search
- Browser geolocation
- Mock data fallback (works offline)

## Climate Zones Covered
- Tropical Wet (Kerala, Goa)
- Tropical Wet & Dry (Maharashtra, Karnataka, Tamil Nadu)
- Arid (Rajasthan, Gujarat)
- Semi-Arid (MP, Telangana)
- Humid Subtropical (Delhi, UP, West Bengal)
- Montane (J&K, Himachal Pradesh, Uttarakhand)
- Tropical Monsoon (Assam, Odisha)
