# IndiaWeather POC — Project Summary

## Stack
- Frontend: HTML + Leaflet.js + OpenStreetMap tiles
- Backend: Python FastAPI (port 8000)
- Weather Data: OpenWeatherMap API + Open-Meteo (satellite, no key needed)
- Rain Radar: RainViewer tiles (free, no key)
- Repo: https://github.com/Arpiet21/IndiaWeather

## Run Locally
- Backend: `cd backend && python -m uvicorn main:app --reload --port 8000`
- Frontend: `cd "Weather App" && python -m http.server 3000` → open `http://localhost:3000`
- API Docs: `http://localhost:8000/docs`

## API Endpoints
| Endpoint | Description |
|----------|-------------|
| GET /weather/all | All 25 cities live weather |
| GET /weather/{city} | Single city weather |
| GET /forecast/{city} | 7-day forecast |
| GET /location/weather | GPS location weather (OWM) |
| GET /location/weather/accurate | Satellite-based village-level weather (Open-Meteo + OWM cross-validated) |
| GET /location/hourly | 24–48hr hourly rain probability + mm |
| POST /report/weather | Submit crowd-sourced ground truth report |
| GET /report/weather | Get nearby community reports |
| GET /alerts | Active IMD-style alerts |
| GET /monsoon | Monsoon tracker status |
| GET /cities | City list with climate metadata |

## Done
1. 25 Indian cities across all 7 climate zones with live OpenWeatherMap data
2. Interactive India map — 5 layer toggles: Temperature, Rainfall, Wind, Humidity, AQI
3. GPS "My Location" — satellite-accurate weather for any coordinates including villages
4. Dual-source accuracy — Open-Meteo (satellite) + OWM cross-validated, takes max rain value
5. Rain Radar toggle — live RainViewer precipitation overlay on map
6. Hourly rain forecast panel — 24hr rain probability bars, next rain window, total mm
7. AQI detail panel — color-coded scale 0–500, category, who's affected, health advice
8. 7-day forecast — day, icon, description, high/low temps
9. Monsoon tracker, active alerts sidebar, stats bar across India
10. Report Actual Weather modal — crowd-sourced ground truth for rural accuracy
11. Mobile-ready REST API — all endpoints usable from React Native / Flutter
12. Pushed to GitHub: https://github.com/Arpiet21/IndiaWeather

## Known Limitation Fixed
- OWM uses nearest weather station (40–80 km away for villages like Arjani)
- Fixed by switching to Open-Meteo satellite data + cross-validating both sources

## Next
13. Mobile App — React Native or Flutter using same FastAPI endpoints
14. Deploy — backend to Render/Railway, frontend to Vercel for public access
15. IMD integration — official India Met Department bulletins for state-level alerts
16. Persist community reports — PostgreSQL instead of in-memory store
17. Expand cities — grow from 25 to 100+ districts across India
