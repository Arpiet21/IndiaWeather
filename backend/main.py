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
OWM_API_KEY    = os.getenv("OWM_API_KEY", "YOUR_OPENWEATHERMAP_API_KEY")
OWM_BASE       = "https://api.openweathermap.org/data/2.5"
OWM_FORECAST   = "https://api.openweathermap.org/data/2.5/forecast"
AQI_BASE       = "https://api.openweathermap.org/data/2.5/air_pollution"
OPEN_METEO     = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_AIR = "https://air-quality-api.open-meteo.com/v1/air-quality"

# In-memory store for user weather reports
user_reports: list[dict] = []

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
    # Sagar district — village-level coverage
    {"name": "Sagar",       "state": "Madhya Pradesh",   "lat": 23.8388, "lng": 78.7378, "zone": "Semi-Arid",            "annual_rainfall": "1143 mm"},
    {"name": "Bareli",      "state": "Madhya Pradesh",   "lat": 23.6500, "lng": 79.0167, "zone": "Semi-Arid",            "annual_rainfall": "1120 mm"},
    {"name": "Silwani",     "state": "Madhya Pradesh",   "lat": 23.3167, "lng": 78.8333, "zone": "Semi-Arid",            "annual_rainfall": "1100 mm"},
    {"name": "Raisen",      "state": "Madhya Pradesh",   "lat": 23.3325, "lng": 77.7893, "zone": "Semi-Arid",            "annual_rainfall": "1130 mm"},
    {"name": "Damoh",       "state": "Madhya Pradesh",   "lat": 23.8327, "lng": 79.4419, "zone": "Semi-Arid",            "annual_rainfall": "1165 mm"},
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


@app.get("/location/weather/accurate", tags=["Weather"])
async def get_accurate_location_weather(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
):
    """
    High-accuracy weather using Open-Meteo (satellite + radar).
    Better for villages and rural areas with no nearby weather stations.
    Cross-checks OWM + Open-Meteo and returns merged result.
    """
    async with httpx.AsyncClient(timeout=15.0) as client:
        # Open-Meteo — satellite based, no API key needed
        om_task = client.get(OPEN_METEO, params={
            "latitude": lat, "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m,surface_pressure,visibility,weather_code",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code,wind_speed_10m_max",
            "timezone": "Asia/Kolkata",
            "forecast_days": 7,
        })
        # OWM for cross-check
        owm_task = client.get(f"{OWM_BASE}/weather", params={
            "lat": lat, "lon": lon, "appid": OWM_API_KEY, "units": "metric",
        })
        # AQI from Open-Meteo
        aqi_task = client.get(OPEN_METEO_AIR, params={
            "latitude": lat, "longitude": lon,
            "current": "pm2_5,pm10,european_aqi",
            "timezone": "Asia/Kolkata",
        })

        om_r, owm_r, aqi_r = await asyncio.gather(om_task, owm_task, aqi_task)

    om   = om_r.json()
    owm  = owm_r.json() if owm_r.status_code == 200 else {}
    aqi_data = aqi_r.json() if aqi_r.status_code == 200 else {}

    cur = om.get("current", {})
    daily = om.get("daily", {})

    # Weather code → description + emoji
    WMO_MAP = {
        0: ("Clear Sky", "☀️"),      1: ("Mainly Clear", "🌤️"),
        2: ("Partly Cloudy", "⛅"),   3: ("Overcast", "☁️"),
        45: ("Foggy", "🌫️"),          48: ("Icy Fog", "🌫️"),
        51: ("Light Drizzle", "🌦️"),  53: ("Drizzle", "🌦️"),
        55: ("Heavy Drizzle", "🌧️"),  61: ("Light Rain", "🌧️"),
        63: ("Rain", "🌧️"),           65: ("Heavy Rain", "🌧️"),
        71: ("Light Snow", "❄️"),     73: ("Snow", "❄️"),
        75: ("Heavy Snow", "❄️"),     80: ("Rain Showers", "🌦️"),
        81: ("Showers", "🌧️"),        82: ("Heavy Showers", "⛈️"),
        95: ("Thunderstorm", "⛈️"),   96: ("Thunderstorm+Hail", "⛈️"),
    }
    wcode = cur.get("weather_code", 0)
    desc, icon = WMO_MAP.get(wcode, ("Unknown", "🌤️"))

    # Cross-validate rain: use max of OWM + Open-Meteo
    om_rain  = cur.get("rain", 0) or cur.get("precipitation", 0)
    owm_rain = owm.get("rain", {}).get("1h", 0) if owm else 0
    rain_val = max(om_rain, owm_rain)

    # AQI from Open-Meteo air quality
    aqi_cur  = aqi_data.get("current", {})
    aqi_val  = aqi_cur.get("european_aqi", None)
    pm25     = aqi_cur.get("pm2_5", None)
    pm10     = aqi_cur.get("pm10", None)

    # Build 7-day forecast from Open-Meteo daily
    days_list = daily.get("time", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    precip    = daily.get("precipitation_sum", [])
    wcodes    = daily.get("weather_code", [])
    winds     = daily.get("wind_speed_10m_max", [])

    forecast = []
    for i, date_str in enumerate(days_list[:7]):
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        wc = wcodes[i] if i < len(wcodes) else 0
        fdesc, ficon = WMO_MAP.get(wc, ("--", "🌤️"))
        forecast.append({
            "day": dt.strftime("%a"),
            "date": date_str,
            "icon": ficon,
            "description": fdesc,
            "hi": round(max_temps[i], 1) if i < len(max_temps) else "--",
            "lo": round(min_temps[i], 1) if i < len(min_temps) else "--",
            "rain": round(precip[i], 1) if i < len(precip) else 0,
            "wind_speed": round(winds[i], 1) if i < len(winds) else "--",
        })

    owm_name = owm.get("name", "") if owm else ""
    return {
        "name": owm_name or "Your Location",
        "lat": lat, "lon": lon,
        "source": "Open-Meteo (satellite) + OpenWeatherMap",
        "temp": round(cur.get("temperature_2m", 0), 1),
        "feels_like": round(cur.get("temperature_2m", 0) - 1.5, 1),
        "humidity": cur.get("relative_humidity_2m", 0),
        "wind_speed": round(cur.get("wind_speed_10m", 0), 1),
        "pressure": round(cur.get("surface_pressure", 0)),
        "visibility": round((cur.get("visibility", 10000)) / 1000, 1),
        "rain_1h": round(rain_val, 1),
        "rain_detected": rain_val > 0,
        "aqi": aqi_val,
        "pm2_5": pm25,
        "pm10": pm10,
        "description": desc,
        "icon": icon,
        "forecast": forecast,
        "owm_cross_check": {
            "temp": owm.get("main", {}).get("temp") if owm else None,
            "rain": owm_rain,
            "description": owm.get("weather", [{}])[0].get("description", "--").title() if owm else "--",
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/report/weather", tags=["Community"])
async def report_weather(report: dict):
    """
    User submits actual observed weather for their location.
    Crowd-sourced accuracy correction — shown alongside API data.
    """
    report["id"] = f"report_{len(user_reports)+1:04d}"
    report["submitted_at"] = datetime.utcnow().isoformat()
    user_reports.append(report)
    return {"status": "ok", "message": "Thank you! Your report helps improve accuracy.", "id": report["id"]}


@app.get("/report/weather", tags=["Community"])
async def get_reports(
    lat: float = Query(None), lon: float = Query(None), radius_km: float = 50
):
    """Get recent community weather reports near a location."""
    if lat is None or lon is None:
        return {"reports": user_reports[-20:], "total": len(user_reports)}

    def dist(r):
        return ((r.get("lat", 0) - lat)**2 + (r.get("lon", 0) - lon)**2) ** 0.5 * 111

    nearby = [r for r in user_reports if dist(r) <= radius_km]
    return {"reports": nearby[-20:], "total": len(nearby)}


@app.get("/location/hourly", tags=["Weather"])
async def get_hourly_forecast(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    hours: int = Query(24, description="Hours ahead, max 48"),
):
    """
    Hourly rain + temperature forecast for any location.
    Answers: 'When will it rain today?' — satellite accuracy, village-level.
    """
    hours = min(hours, 48)
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(OPEN_METEO, params={
            "latitude": lat, "longitude": lon,
            "hourly": "temperature_2m,precipitation_probability,precipitation,rain,weather_code,wind_speed_10m",
            "timezone": "Asia/Kolkata",
            "forecast_days": 2,
        })
    data = r.json()
    hourly = data.get("hourly", {})

    times  = hourly.get("time", [])[:hours]
    temps  = hourly.get("temperature_2m", [])[:hours]
    prob   = hourly.get("precipitation_probability", [])[:hours]
    rain   = hourly.get("rain", [])[:hours]
    precip = hourly.get("precipitation", [])[:hours]
    wcodes = hourly.get("weather_code", [])[:hours]
    winds  = hourly.get("wind_speed_10m", [])[:hours]

    WMO_MAP = {
        0: ("Clear", "☀️"), 1: ("Mainly Clear", "🌤️"), 2: ("Partly Cloudy", "⛅"),
        3: ("Overcast", "☁️"), 45: ("Foggy", "🌫️"), 51: ("Light Drizzle", "🌦️"),
        53: ("Drizzle", "🌦️"), 55: ("Heavy Drizzle", "🌧️"), 61: ("Light Rain", "🌧️"),
        63: ("Rain", "🌧️"), 65: ("Heavy Rain", "🌧️"), 80: ("Showers", "🌦️"),
        81: ("Showers", "🌧️"), 82: ("Heavy Showers", "⛈️"), 95: ("Thunderstorm", "⛈️"),
    }

    result = []
    for i, t in enumerate(times):
        wc = wcodes[i] if i < len(wcodes) else 0
        desc, icon = WMO_MAP.get(wc, ("--", "🌤️"))
        rain_mm = rain[i] if i < len(rain) else 0
        result.append({
            "time": t,
            "hour": datetime.strptime(t, "%Y-%m-%dT%H:%M").strftime("%I %p"),
            "temp": round(temps[i], 1) if i < len(temps) else "--",
            "rain_mm": round(rain_mm, 2),
            "rain_chance": prob[i] if i < len(prob) else 0,
            "will_rain": (prob[i] if i < len(prob) else 0) >= 40 or rain_mm > 0,
            "description": desc,
            "icon": icon,
            "wind_speed": round(winds[i], 1) if i < len(winds) else "--",
        })

    # Find next rain window
    next_rain = next((h for h in result if h["will_rain"]), None)

    return {
        "lat": lat, "lon": lon,
        "hours": result,
        "next_rain": next_rain,
        "rain_today": any(h["will_rain"] for h in result[:24]),
        "total_rain_24h": round(sum(h["rain_mm"] for h in result[:24]), 1),
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
