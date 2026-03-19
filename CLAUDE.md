# IndiaWeather POC — Project Summary

## Done
1. Full-stack weather app — Python FastAPI backend + HTML/CSS/JS Leaflet frontend
2. 25 Indian cities across all 7 climate zones with live OpenWeatherMap data (key: active)
3. Interactive India map with 5 layer toggles — Temperature, Rainfall, Wind, Humidity, AQI
4. "My Location" button — fetches live weather + 7-day forecast for any GPS coordinates (incl. villages)
5. AQI detail panel — color-coded scale, category, who's affected, health advice
6. 7-day forecast with day, icon, description, high/low temps (undefined bug fixed)
7. Monsoon tracker, active alerts sidebar, stats bar (highest temp, worst AQI across India)

## Running
- Backend: `cd backend && python -m uvicorn main:app --reload --port 8000`
- Frontend: `cd "Weather App" && python -m http.server 3000` → open `http://localhost:3000`

## Next
8. Mobile app — React Native or Flutter using same FastAPI endpoints (`/location/weather`, `/forecast/{city}`, `/alerts`)
9. IMD integration — parse official bulletins for state-level severe weather alerts
10. Deploy — backend to Render/Railway, frontend to Vercel for public access
