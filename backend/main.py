"""
IndiaWeather POC — Python FastAPI Backend
=========================================
Mobile-compatible REST API (iOS & Android ready via React Native / Flutter)
Run: uvicorn main:app --reload --host 0.0.0.0 --port 8000
Docs: http://localhost:8000/docs
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()  # reads backend/.env automatically
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ─── App Setup ────────────────────────────────────────────────
app = FastAPI(
    title="IndiaWeather API",
    description="Real-time Indian Climate data — Web, iOS & Android compatible",
    version="1.0.0",
)

# CORS — allow web app, React Native (Expo), Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Config ───────────────────────────────────────────────────
OWM_API_KEY  = os.getenv("OWM_API_KEY", "YOUR_OPENWEATHERMAP_API_KEY")
OWM_BASE     = "https://api.openweathermap.org/data/2.5"
OWM_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"
AQI_BASE     = "https://api.openweathermap.org/data/2.5/air_pollution"

# ─── Indian Cities Dataset ────────────────────────────────────
INDIA_CITIES = [
    {"name": "Mumbai",      "state": "Maharashtra",      "lat": 19.0760, "lng": 72.8777, "zone": "Tropical Wet & Dry",   "annual_rainfall": "2167 mm"},
    {"name": "Delhi",       "state": "Delhi NCR",        "lat": 28.6139, "lng": 77.2090, "zone": "Humid Subtropical",    "annual_rainfall": "797 mm"},
    {"name": "Bengaluru",   "state": "Karnataka",        "lat": 12.9716, "lng": 77.5946, "zone": "Tropical Wet & Dry",   "annual_rainfall": "970 mm"},
    {"name": "Chennai",     "state": "Tamil Nadu",       "lat": 13.0827, "lng": 80.2707, "zone": "Tropical Wet & Dry",   "annual_rainfall": "1400 mm"},
    {"name": "Kolkata",     "state": "West Bengal",      "lat": 22.5726, "lng": 88.3639, "zone": "Humid Subtropical",    "annual_rainfall": "1582 mm"},
    {"name": "Hyderabad",   "state": "Telangana",        "lat": 17.3850, "lng": 78.4867, "zone": "Semi-Arid",            "annual_rainfall": "812 mm"},
    {"name": "Pune",        "state": "Maharashtra",      "lat": 18.5204, "lng": 73.8567, "zone": "Semi-Arid",            "annual_rainfall": "722 mm"},
    {"name": "Ahmedabad",   "state": "Gujarat",          "lat": 23.0225, "lng": 72.5714, "zone": "Arid",                 "annual_rainfall": "782 mm"},
    {"name": "Jaipur",      "state": "Rajasthan",        "lat": 26.9124, "lng": 75.7873, "zone": "Arid",                 "annual_rainfall": "650 mm"},
    {"name": "Lucknow",     "state": "Uttar Pradesh",    "lat": 26.8467, "lng": 80.9462, "zone": "Humid Subtropical",    "annual_rainfall": "889 mm"},
    {"name": "Shimla",      "state": "Himachal Pradesh", "lat": 31.1048, "lng": 77.1734, "zone": "Montane",              "annual_rainfall": "1575 mm"},
    {"name": "Darjeeling",  "state": "West Bengal",      "lat": 27.0360, "lng": 88.2627, "zone": "Montane",              "annual_rainfall": "3090 mm"},
    {"name": "Srinagar",    "state": "Jammu & Kashmir",  "lat": 34.0836, "lng": 74.7973, "zone": "Montane",              "annual_rainfall": "664 mm"},
    {"name": "Kochi",       "state": "Kerala",           "lat": 9.9312,  "lng": 76.2673, "zone": "Tropical Wet",         "annual_rainfall": "3200 mm"},
    {"name": "Goa",         "state": "Goa",              "lat": 15.2993, "lng": 74.1240, "zone": "Tropical Wet",         "annual_rainfall": "2932 mm"},
    {"name": "Guwahati",    "state": "Assam",            "lat": 26.1445, "lng": 91.7362, "zone": "Tropical Monsoon",     "annual_rainfall": "1690 mm"},
    {"name": "Jodhpur",     "state": "Rajasthan",        "lat": 26.2389, "lng": 73.0243, "zone": "Arid",                 "annual_rainfall": "362 mm"},
    {"name": "Nagpur",      "state": "Maharashtra",      "lat": 21.1458, "lng": 79.0882, "zone": "Tropical Wet & Dry",   "annual_rainfall": "1205 mm"},
    {"name": "Bhopal",      "state": "Madhya Pradesh",   "lat": 23.2599, "lng": 77.4126, "zone": "Semi-Arid",            "annual_rainfall": "1146 mm"},
    {"name": "Bhubaneswar", "state": "Odisha",           "lat": 20.2961, "lng": 85.8245, "zone": "Tropical Monsoon",     "annual_rainfall": "1538 mm"},
]

# ─── Models (mobile-friendly JSON contracts) ──────────────────
class WeatherData(BaseModel):
    name: str
    state: str
    lat: float
    lng: float
    zone: str
    annual_rainfall: str
    temp: float
    feels_like: float
    humidity: int
    wind_speed: float
    pressure: int
    visibility: float
    rain_1h: float
    aqi: Optional[int]
    description: str
    icon: str
    icon_url: Optional[str]
    timestamp: str

class AllCitiesResponse(BaseModel):
    cities: list[WeatherData]
    total: int
    updated_at: str

class ForecastDay(BaseModel):
    day: str
    date: str
    icon: str
    icon_url: str
    description: str
    hi: float
    lo: float
    humidity: int
    wind_speed: float
    rain: float

class ForecastResponse(BaseModel):
    city: str
    state: str
    forecast: list[ForecastDay]

class AlertsResponse(BaseModel):
    alerts: list[dict]
    updated_at: str

# ─── OWM Helpers ──────────────────────────────────────────────
WEATHER_EMOJI = {
    "01": "☀️", "02": "⛅", "03": "☁️", "04": "☁️",
    "09": "🌧️", "10": "🌦️", "11": "⛈️", "13": "❄️", "50": "🌫️",
}

def emoji_for(icon_code: str) -> str:
    return WEATHER_EMOJI.get(icon_code[:2], "🌤️")

async def fetch_current(client: httpx.AsyncClient, city: dict) -> WeatherData:
    """Fetch current weather from OWM for one city."""
    try:
        r = await client.get(f"{OWM_BASE}/weather", params={
            "lat": city["lat"], "lon": city["lng"],
            "appid": OWM_API_KEY, "units": "metric",
        })
        r.raise_for_status()
        d = r.json()

        # AQI call
        aqi_val = None
        try:
            aqi_r = await client.get(AQI_BASE, params={
                "lat": city["lat"], "lon": city["lng"], "appid": OWM_API_KEY,
            })
            aqi_r.raise_for_status()
            aqi_val = aqi_r.json()["list"][0]["main"]["aqi"] * 50  # normalize
        except Exception:
            pass

        icon_code = d["weather"][0]["icon"]
        return WeatherData(
            name=city["name"], state=city["state"],
            lat=city["lat"], lng=city["lng"],
            zone=city["zone"], annual_rainfall=city["annual_rainfall"],
            temp=round(d["main"]["temp"], 1),
            feels_like=round(d["main"]["feels_like"], 1),
            humidity=d["main"]["humidity"],
            wind_speed=round(d["wind"]["speed"] * 3.6, 1),   # m/s → km/h
            pressure=d["main"]["pressure"],
            visibility=round(d.get("visibility", 10000) / 1000, 1),
            rain_1h=round(d.get("rain", {}).get("1h", 0), 1),
            aqi=aqi_val,
            description=d["weather"][0]["description"].title(),
            icon=emoji_for(icon_code),
            icon_url=f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
            timestamp=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        print(f"[ERROR] {city['name']}: {e}")
        return WeatherData(
            name=city["name"], state=city["state"],
            lat=city["lat"], lng=city["lng"],
            zone=city["zone"], annual_rainfall=city["annual_rainfall"],
            temp=0, feels_like=0, humidity=0, wind_speed=0,
            pressure=0, visibility=0, rain_1h=0, aqi=None,
            description="Data unavailable", icon="❓", icon_url=None,
            timestamp=datetime.utcnow().isoformat(),
        )

# ─── Routes ───────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    """Health check — confirm backend is running."""
    return {
        "service": "IndiaWeather API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": ["/weather/all", "/weather/{city}", "/forecast/{city}", "/alerts"],
    }

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.get("/weather/all", response_model=AllCitiesResponse, tags=["Weather"])
async def get_all_cities():
    """
    Fetch current weather for all 20+ Indian cities in parallel.
    Used by web map, React Native, and Flutter apps.
    """
    async with httpx.AsyncClient(timeout=15.0) as client:
        tasks = [fetch_current(client, city) for city in INDIA_CITIES]
        results = await asyncio.gather(*tasks)

    return AllCitiesResponse(
        cities=results,
        total=len(results),
        updated_at=datetime.utcnow().isoformat(),
    )


@app.get("/weather/{city_name}", response_model=WeatherData, tags=["Weather"])
async def get_city_weather(city_name: str):
    """
    Fetch weather for a specific Indian city by name.
    Mobile apps call this on city tap/select.
    """
    city = next((c for c in INDIA_CITIES if c["name"].lower() == city_name.lower()), None)
    if not city:
        raise HTTPException(status_code=404, detail=f"City '{city_name}' not found in dataset.")
    async with httpx.AsyncClient(timeout=15.0) as client:
        return await fetch_current(client, city)


@app.get("/forecast/{city_name}", response_model=ForecastResponse, tags=["Forecast"])
async def get_forecast(city_name: str):
    """
    5-day / 3-hour forecast for a city, collapsed to daily.
    Used by mobile detail screens.
    """
    city = next((c for c in INDIA_CITIES if c["name"].lower() == city_name.lower()), None)
    if not city:
        raise HTTPException(status_code=404, detail=f"City '{city_name}' not found.")

    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(OWM_FORECAST, params={
            "lat": city["lat"], "lon": city["lng"],
            "appid": OWM_API_KEY, "units": "metric",
        })
        r.raise_for_status()
        raw = r.json()

    # Collapse 3-hourly to daily
    daily: dict[str, list] = {}
    for item in raw["list"]:
        day = item["dt_txt"][:10]
        daily.setdefault(day, []).append(item)

    forecast = []
    for date_str, items in list(daily.items())[:7]:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        temps = [i["main"]["temp"] for i in items]
        winds = [i["wind"]["speed"] * 3.6 for i in items]
        rains = [i.get("rain", {}).get("3h", 0) for i in items]
        icon_code = items[len(items)//2]["weather"][0]["icon"]
        forecast.append(ForecastDay(
            day=dt.strftime("%a"),
            date=date_str,
            icon=emoji_for(icon_code),
            icon_url=f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
            description=items[len(items)//2]["weather"][0]["description"].title(),
            hi=round(max(temps), 1),
            lo=round(min(temps), 1),
            humidity=items[len(items)//2]["main"]["humidity"],
            wind_speed=round(sum(winds)/len(winds), 1),
            rain=round(sum(rains), 1),
        ))

    return ForecastResponse(city=city["name"], state=city["state"], forecast=forecast)


@app.get("/location/weather", tags=["Weather"])
async def get_weather_by_location(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
):
    """
    Get current weather + 7-day forecast for ANY coordinates.
    Used by 'My Location' button — works for villages, remote areas.
    """
    async with httpx.AsyncClient(timeout=15.0) as client:
        # Current weather
        r = await client.get(f"{OWM_BASE}/weather", params={
            "lat": lat, "lon": lon, "appid": OWM_API_KEY, "units": "metric",
        })
        r.raise_for_status()
        d = r.json()

        # Forecast
        fr = await client.get(OWM_FORECAST, params={
            "lat": lat, "lon": lon, "appid": OWM_API_KEY, "units": "metric",
        })
        fr.raise_for_status()
        raw_forecast = fr.json()

        # AQI
        aqi_val = None
        try:
            aqi_r = await client.get(AQI_BASE, params={
                "lat": lat, "lon": lon, "appid": OWM_API_KEY,
            })
            aqi_val = aqi_r.json()["list"][0]["main"]["aqi"] * 50
        except Exception:
            pass

    # Collapse forecast to daily
    daily: dict[str, list] = {}
    for item in raw_forecast["list"]:
        day = item["dt_txt"][:10]
        daily.setdefault(day, []).append(item)

    forecast = []
    for date_str, items in list(daily.items())[:7]:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        temps = [i["main"]["temp"] for i in items]
        icon_code = items[len(items)//2]["weather"][0]["icon"]
        forecast.append({
            "day": dt.strftime("%a"),
            "date": date_str,
            "icon": emoji_for(icon_code),
            "icon_url": f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
            "description": items[len(items)//2]["weather"][0]["description"].title(),
            "hi": round(max(temps), 1),
            "lo": round(min(temps), 1),
            "humidity": items[len(items)//2]["main"]["humidity"],
            "wind_speed": round(items[len(items)//2]["wind"]["speed"] * 3.6, 1),
            "rain": round(sum(i.get("rain", {}).get("3h", 0) for i in items), 1),
        })

    icon_code = d["weather"][0]["icon"]
    location_name = d.get("name") or "Your Location"
    return {
        "name": location_name,
        "lat": lat,
        "lon": lon,
        "temp": round(d["main"]["temp"], 1),
        "feels_like": round(d["main"]["feels_like"], 1),
        "humidity": d["main"]["humidity"],
        "wind_speed": round(d["wind"]["speed"] * 3.6, 1),
        "pressure": d["main"]["pressure"],
        "visibility": round(d.get("visibility", 10000) / 1000, 1),
        "rain_1h": round(d.get("rain", {}).get("1h", 0), 1),
        "aqi": aqi_val,
        "description": d["weather"][0]["description"].title(),
        "icon": emoji_for(icon_code),
        "icon_url": f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
        "forecast": forecast,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/alerts", response_model=AlertsResponse, tags=["Alerts"])
async def get_alerts():
    """
    Active IMD-style weather alerts for India.
    Push-notification ready for mobile apps.
    """
    # In production: parse IMD RSS feed or OWM one-call alerts
    alerts = [
        {
            "id": "alert_001",
            "type": "heatwave",
            "severity": "orange",
            "title": "Heatwave Warning",
            "description": "Temperatures above 42°C expected in Rajasthan and Gujarat",
            "states": ["Rajasthan", "Gujarat"],
            "valid_until": "2026-03-21T18:00:00Z",
            "icon": "🔥",
        },
        {
            "id": "alert_002",
            "type": "heavy_rain",
            "severity": "yellow",
            "title": "Heavy Rainfall Alert",
            "description": "Isolated heavy to very heavy rainfall over Kerala and coastal Karnataka",
            "states": ["Kerala", "Karnataka"],
            "valid_until": "2026-03-20T06:00:00Z",
            "icon": "🌧️",
        },
        {
            "id": "alert_003",
            "type": "cyclone_watch",
            "severity": "red",
            "title": "Cyclone Watch",
            "description": "Low pressure system developing over Bay of Bengal. Monitor closely.",
            "states": ["Odisha", "West Bengal", "Andhra Pradesh"],
            "valid_until": "2026-03-22T12:00:00Z",
            "icon": "🌀",
        },
    ]
    return AlertsResponse(alerts=alerts, updated_at=datetime.utcnow().isoformat())


@app.get("/cities", tags=["Reference"])
async def list_cities(zone: Optional[str] = Query(None, description="Filter by climate zone")):
    """
    List all cities with metadata.
    Used by mobile search/filter screens.
    """
    cities = INDIA_CITIES
    if zone:
        cities = [c for c in cities if zone.lower() in c["zone"].lower()]
    return {"cities": cities, "total": len(cities)}


@app.get("/monsoon", tags=["Climate"])
async def monsoon_status():
    """
    Current monsoon status — onset, withdrawal, coverage.
    Featured widget on mobile home screen.
    """
    return {
        "southwest_monsoon": {
            "status": "Active",
            "onset_kerala": "2025-06-01",
            "current_coverage": "68%",
            "rainfall_anomaly": "+12%",
            "normal_rainfall": "887 mm",
            "actual_rainfall": "993 mm",
        },
        "northeast_monsoon": {
            "status": "Inactive",
            "expected_onset": "2025-10-01",
        },
        "updated_at": datetime.utcnow().isoformat(),
    }
