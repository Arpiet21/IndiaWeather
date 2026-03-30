// ============================================================
//  IndiaWeather POC — Configuration
//  Replace placeholder keys with your real API keys
// ============================================================

const CONFIG = {
  // Auto-switch: localhost in dev, Render URL in production
  API_BASE_URL: window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://localhost:8000"
    : "https://indiaweather-api.onrender.com",

  // OpenWeatherMap API key (get free key at openweathermap.org)
  OWM_API_KEY: "6ad009b9b9276360ac5d9d6accb14595",

  // Map refresh interval in milliseconds (10 minutes)
  REFRESH_INTERVAL: 10 * 60 * 1000,

  // Default map center (India)
  DEFAULT_LAT: 22.5,
  DEFAULT_LNG: 82.5,
  DEFAULT_ZOOM: 5,
};
