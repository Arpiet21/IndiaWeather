# IndiaWeather POC — Project Summary

## Stack
- Frontend: HTML + Leaflet.js + OpenStreetMap tiles
- Backend: Python FastAPI (port 8000)
- Weather Data: OpenWeatherMap API + Open-Meteo (satellite, no key needed)
- Rain Radar: RainViewer tiles (free, no key)
- Repo: https://github.com/Arpiet21/IndiaWeather
- Live: https://indiaweather.vercel.app

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
6. Hourly rain forecast — every hour for 24h via Open-Meteo, with Today/Tomorrow date separators
7. Today's hourly table — Time, Icon, Temp, Feels Like, Rain%, mm, Humidity, Wind direction
8. AQI detail panel — color-coded scale 0–500, category, who's affected, health advice
9. 7-day forecast — date, icon, description, humidity, rain, wind, hi/lo per day
10. Monsoon tracker, active alerts sidebar, stats bar across India
11. Report Actual Weather modal — crowd-sourced ground truth for rural accuracy
12. My Location — reverse geocodes GPS to real village name via Nominatim (not OWM station name)
13. OWM direct fallback — app works fully on Vercel without backend (calls OWM from browser)
14. Mobile-friendly — responsive layout, PWA meta tags, installable on iPhone/Android
15. Deployed to Vercel: https://indiaweather.vercel.app

## Known Limitation Fixed
- OWM uses nearest weather station (40–80 km away for villages like Arjani)
- Fixed by switching to Open-Meteo satellite data + cross-validating both sources
- My Location now shows real village name (Arjani/Gundrai) not OWM station name (Sodarpur)

## Next
16. Mobile App — React Native or Flutter using same FastAPI endpoints
17. Deploy backend — Render/Railway so satellite accuracy works on live site
18. IMD integration — official India Met Department bulletins for state-level alerts
19. Persist community reports — PostgreSQL instead of in-memory store
20. Expand cities — grow from 25 to 100+ districts across India
