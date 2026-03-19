// ============================================================
//  IndiaWeather POC — Frontend App
//  Calls Python FastAPI backend for weather data
// ============================================================

// ─── Indian Cities Dataset ───────────────────────────────────
const INDIA_CITIES = [
  // Metros & major cities
  { name: "Mumbai",      state: "Maharashtra",      lat: 19.0760, lng: 72.8777, zone: "Tropical Wet & Dry",    rainfall: "2167 mm", season: "Pre-Monsoon" },
  { name: "Delhi",       state: "Delhi NCR",         lat: 28.6139, lng: 77.2090, zone: "Humid Subtropical",     rainfall: "797 mm",  season: "Summer" },
  { name: "Bengaluru",   state: "Karnataka",         lat: 12.9716, lng: 77.5946, zone: "Tropical Wet & Dry",   rainfall: "970 mm",  season: "Inter-Monsoon" },
  { name: "Chennai",     state: "Tamil Nadu",        lat: 13.0827, lng: 80.2707, zone: "Tropical Wet & Dry",   rainfall: "1400 mm", season: "Pre-Monsoon" },
  { name: "Kolkata",     state: "West Bengal",       lat: 22.5726, lng: 88.3639, zone: "Humid Subtropical",    rainfall: "1582 mm", season: "Pre-Monsoon" },
  { name: "Hyderabad",   state: "Telangana",         lat: 17.3850, lng: 78.4867, zone: "Semi-Arid",            rainfall: "812 mm",  season: "Pre-Monsoon" },
  { name: "Pune",        state: "Maharashtra",       lat: 18.5204, lng: 73.8567, zone: "Semi-Arid",            rainfall: "722 mm",  season: "Pre-Monsoon" },
  { name: "Ahmedabad",   state: "Gujarat",           lat: 23.0225, lng: 72.5714, zone: "Arid",                 rainfall: "782 mm",  season: "Summer" },
  { name: "Jaipur",      state: "Rajasthan",         lat: 26.9124, lng: 75.7873, zone: "Arid",                 rainfall: "650 mm",  season: "Summer" },
  { name: "Lucknow",     state: "Uttar Pradesh",     lat: 26.8467, lng: 80.9462, zone: "Humid Subtropical",    rainfall: "889 mm",  season: "Summer" },
  // Hill stations & montane
  { name: "Shimla",      state: "Himachal Pradesh",  lat: 31.1048, lng: 77.1734, zone: "Montane",              rainfall: "1575 mm", season: "Spring" },
  { name: "Darjeeling",  state: "West Bengal",       lat: 27.0360, lng: 88.2627, zone: "Montane",              rainfall: "3090 mm", season: "Spring" },
  { name: "Srinagar",    state: "Jammu & Kashmir",   lat: 34.0836, lng: 74.7973, zone: "Montane",              rainfall: "664 mm",  season: "Spring" },
  { name: "Manali",      state: "Himachal Pradesh",  lat: 32.2432, lng: 77.1892, zone: "Montane",              rainfall: "1250 mm", season: "Spring" },
  // Coastal & south
  { name: "Kochi",       state: "Kerala",            lat: 9.9312,  lng: 76.2673, zone: "Tropical Wet",         rainfall: "3200 mm", season: "Monsoon" },
  { name: "Thiruvananthapuram", state: "Kerala",     lat: 8.5241,  lng: 76.9366, zone: "Tropical Wet",         rainfall: "1800 mm", season: "Monsoon" },
  { name: "Goa",         state: "Goa",               lat: 15.2993, lng: 74.1240, zone: "Tropical Wet",         rainfall: "2932 mm", season: "Pre-Monsoon" },
  { name: "Bhubaneswar", state: "Odisha",            lat: 20.2961, lng: 85.8245, zone: "Tropical Monsoon",     rainfall: "1538 mm", season: "Pre-Monsoon" },
  // Northeast
  { name: "Guwahati",    state: "Assam",             lat: 26.1445, lng: 91.7362, zone: "Tropical Monsoon",     rainfall: "1690 mm", season: "Pre-Monsoon" },
  { name: "Shillong",    state: "Meghalaya",         lat: 25.5788, lng: 91.8933, zone: "Tropical Monsoon",     rainfall: "2530 mm", season: "Pre-Monsoon" },
  // Desert & arid
  { name: "Jodhpur",     state: "Rajasthan",         lat: 26.2389, lng: 73.0243, zone: "Arid",                 rainfall: "362 mm",  season: "Summer" },
  { name: "Bikaner",     state: "Rajasthan",         lat: 28.0229, lng: 73.3119, zone: "Arid",                 rainfall: "290 mm",  season: "Summer" },
  // Central India
  { name: "Nagpur",      state: "Maharashtra",       lat: 21.1458, lng: 79.0882, zone: "Tropical Wet & Dry",   rainfall: "1205 mm", season: "Pre-Monsoon" },
  { name: "Bhopal",      state: "Madhya Pradesh",    lat: 23.2599, lng: 77.4126, zone: "Semi-Arid",            rainfall: "1146 mm", season: "Summer" },
  { name: "Raipur",      state: "Chhattisgarh",      lat: 21.2514, lng: 81.6296, zone: "Tropical Wet & Dry",   rainfall: "1338 mm", season: "Pre-Monsoon" },
];

// ─── State ───────────────────────────────────────────────────
let map, markersLayer;
let activeLayer = "temperature";
let cityWeatherData = {};
let selectedCity = null;

// ─── Init ─────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  initMap();
  attachEvents();
  loadAllCityWeather();
  setInterval(loadAllCityWeather, CONFIG.REFRESH_INTERVAL);
});

// ─── Map Setup ───────────────────────────────────────────────
function initMap() {
  map = L.map("map", {
    center: [CONFIG.DEFAULT_LAT, CONFIG.DEFAULT_LNG],
    zoom: CONFIG.DEFAULT_ZOOM,
    zoomControl: true,
  });

  // OpenStreetMap tiles (always available, no key needed)
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '© <a href="https://openstreetmap.org">OpenStreetMap</a>',
    subdomains: "abc",
    maxZoom: 19,
  }).addTo(map);

  markersLayer = L.layerGroup().addTo(map);
}

// ─── Load All City Weather via Python Backend ─────────────────
async function loadAllCityWeather() {
  showLoading(true);
  updateTimestamp("Loading...");

  try {
    const res = await fetch(`${CONFIG.API_BASE_URL}/weather/all`);
    if (!res.ok) throw new Error(`Backend error: ${res.status}`);
    const data = await res.json();

    // Check if API key has activated (data has real temps)
    const hasLiveData = data.cities.some(c => c.temp > 0);
    if (!hasLiveData) {
      console.warn("API key not yet active, using mock data");
      loadMockData();
      return;
    }

    cityWeatherData = {};
    data.cities.forEach(c => { cityWeatherData[c.name] = c; });

    renderMarkers();
    updateStatsBar(data.cities);
    updateTimestamp("Live — " + new Date().toLocaleTimeString("en-IN"));
    document.getElementById("statCities").textContent = data.cities.length;

  } catch (err) {
    console.warn("Backend unavailable, loading mock data:", err.message);
    loadMockData();
  } finally {
    showLoading(false);
  }
}

// ─── Fallback Mock Data (works offline/before backend) ────────
function loadMockData() {
  const mockData = INDIA_CITIES.map(city => ({
    ...city,
    temp:       Math.round(18 + Math.random() * 22),
    feels_like: Math.round(16 + Math.random() * 24),
    humidity:   Math.round(40 + Math.random() * 50),
    wind_speed: Math.round(5  + Math.random() * 25),
    pressure:   Math.round(1005 + Math.random() * 20),
    visibility: Math.round(5  + Math.random() * 15),
    rain_1h:    Math.random() > 0.6 ? parseFloat((Math.random() * 15).toFixed(1)) : 0,
    aqi:        Math.round(30 + Math.random() * 200),
    description: ["Clear sky", "Partly cloudy", "Scattered clouds", "Light rain", "Overcast"][Math.floor(Math.random() * 5)],
    icon:       ["☀️", "⛅", "🌤️", "🌧️", "☁️"][Math.floor(Math.random() * 5)],
    forecast:   generateMockForecast(),
  }));

  cityWeatherData = {};
  mockData.forEach(c => { cityWeatherData[c.name] = c; });

  renderMarkers();
  updateStatsBar(mockData);
  updateTimestamp("Mock data (start backend for live)");
  document.getElementById("statCities").textContent = mockData.length;
}

function generateMockForecast() {
  const days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
  const today = new Date().getDay();
  const icons = ["☀️","⛅","🌧️","⛈️","🌤️","🌦️","☁️"];
  const descs = ["Sunny","Partly cloudy","Rain","Thunderstorm","Mostly clear","Showers","Cloudy"];
  return Array.from({length: 7}, (_, i) => ({
    day:  days[(today + i) % 7],
    icon: icons[Math.floor(Math.random() * icons.length)],
    desc: descs[Math.floor(Math.random() * descs.length)],
    hi:   Math.round(25 + Math.random() * 15),
    lo:   Math.round(15 + Math.random() * 10),
  }));
}

// ─── Render Markers ───────────────────────────────────────────
function renderMarkers() {
  markersLayer.clearLayers();

  INDIA_CITIES.forEach(city => {
    const data = cityWeatherData[city.name];
    if (!data) return;

    const value  = getLayerValue(data);
    const color  = getMarkerColor(data, activeLayer);
    const label  = getLayerLabel(data, activeLayer);

    const icon = L.divIcon({
      className: "",
      html: `<div class="weather-marker" style="border-color:${color};background:rgba(22,27,34,0.9)" title="${city.name}">
               <span style="color:${color}">${label}</span>
             </div>`,
      iconAnchor: [28, 10],
    });

    const marker = L.marker([city.lat, city.lng], { icon })
      .addTo(markersLayer)
      .on("click", () => showCityDetail(city.name));

    marker.bindTooltip(`<b>${city.name}</b><br>${city.state}`, {
      direction: "top", offset: [0, -8],
      className: "dark-tooltip",
    });
  });
}

// ─── Layer Value Helpers ──────────────────────────────────────
function getLayerValue(data) {
  switch (activeLayer) {
    case "temperature": return data.temp;
    case "rainfall":    return data.rain_1h;
    case "wind":        return data.wind_speed;
    case "humidity":    return data.humidity;
    case "aqi":         return data.aqi;
    default:            return data.temp;
  }
}

function getLayerLabel(data, layer) {
  switch (layer) {
    case "temperature": return `${data.temp}°C`;
    case "rainfall":    return `${data.rain_1h}mm`;
    case "wind":        return `${data.wind_speed}km/h`;
    case "humidity":    return `${data.humidity}%`;
    case "aqi":         return `AQI ${data.aqi}`;
    default:            return `${data.temp}°C`;
  }
}

function getMarkerColor(data, layer) {
  switch (layer) {
    case "temperature":
      if (data.temp >= 40) return "#d73027";
      if (data.temp >= 35) return "#f46d43";
      if (data.temp >= 30) return "#fdae61";
      if (data.temp >= 25) return "#fee090";
      if (data.temp >= 20) return "#abd9e9";
      if (data.temp >= 15) return "#74add1";
      return "#4575b4";
    case "rainfall":
      if (data.rain_1h > 10) return "#08519c";
      if (data.rain_1h > 5)  return "#3182bd";
      if (data.rain_1h > 1)  return "#6baed6";
      return "#c6dbef";
    case "wind":
      if (data.wind_speed > 50) return "#d73027";
      if (data.wind_speed > 30) return "#f46d43";
      if (data.wind_speed > 15) return "#fdae61";
      return "#3fb950";
    case "humidity":
      if (data.humidity > 80) return "#08519c";
      if (data.humidity > 60) return "#3182bd";
      if (data.humidity > 40) return "#9ecae1";
      return "#fdae61";
    case "aqi":
      if (data.aqi > 200) return "#7e0023";
      if (data.aqi > 150) return "#d73027";
      if (data.aqi > 100) return "#f46d43";
      if (data.aqi > 50)  return "#fdae61";
      return "#3fb950";
    default:
      return "#388bfd";
  }
}

// ─── City Detail Panel ────────────────────────────────────────
function showCityDetail(cityName) {
  const data   = cityWeatherData[cityName];
  const meta   = INDIA_CITIES.find(c => c.name === cityName);
  if (!data || !meta) return;

  selectedCity = cityName;

  // Header
  document.getElementById("cityName").textContent  = cityName;
  document.getElementById("cityState").textContent = meta.state;
  document.getElementById("cityIcon").innerHTML    = `<span style="font-size:2rem">${data.icon || "🌤️"}</span>`;

  // Current weather
  document.getElementById("tempValue").textContent  = data.temp;
  document.getElementById("weatherDesc").textContent = data.description;
  document.getElementById("feelsLike").textContent  = `Feels like: ${data.feels_like}°C`;
  document.getElementById("humidity").textContent   = `${data.humidity}%`;
  document.getElementById("windSpeed").textContent  = `${data.wind_speed} km/h`;
  document.getElementById("rainfall").textContent   = `${data.rain_1h || 0} mm`;
  document.getElementById("visibility").textContent = `${data.visibility} km`;
  document.getElementById("pressure").textContent   = `${data.pressure} hPa`;
  document.getElementById("aqiValue").textContent   = aqiLabel(data.aqi);
  updateAqiPanel(data.aqi);

  // Color temp
  const tempEl = document.getElementById("tempValue");
  if (data.temp >= 40) tempEl.style.color = "#f85149";
  else if (data.temp >= 35) tempEl.style.color = "#f78166";
  else if (data.temp >= 25) tempEl.style.color = "#d29922";
  else tempEl.style.color = "#79c0ff";

  // Forecast
  renderForecast(data.forecast);

  // Climate info
  document.querySelector(".zone-badge").textContent = meta.zone;
  document.getElementById("annualRainfall").textContent = meta.rainfall;
  document.getElementById("currentSeason").textContent  = meta.season;

  // Pan map
  map.panTo([meta.lat, meta.lng], { animate: true, duration: 0.8 });
}

function aqiInfo(aqi) {
  if (!aqi || aqi === 0) return { label: "--", category: "Unknown", color: "#8b949e", advice: "No data", emoji: "❓", who: "--" };
  if (aqi > 400) return { label: `${aqi}`, category: "Severe",    color: "#7e0023", advice: "Stay indoors. Avoid all outdoor activity.", emoji: "⚫", who: "Everyone seriously affected" };
  if (aqi > 300) return { label: `${aqi}`, category: "Very Poor", color: "#d73027", advice: "Avoid outdoor exposure. Use N95 mask.",    emoji: "🟣", who: "Health impact on all" };
  if (aqi > 200) return { label: `${aqi}`, category: "Poor",      color: "#f46d43", advice: "Limit outdoor activity. Wear a mask.",      emoji: "🔴", who: "Breathing discomfort for most" };
  if (aqi > 100) return { label: `${aqi}`, category: "Moderate",  color: "#d29922", advice: "Sensitive groups should limit time outdoors.", emoji: "🟠", who: "Asthma, elderly, children" };
  if (aqi > 50)  return { label: `${aqi}`, category: "Satisfactory", color: "#3fb950", advice: "Acceptable. Sensitive people take care.",   emoji: "🟡", who: "Very sensitive individuals" };
  return           { label: `${aqi}`, category: "Good",         color: "#3fb950", advice: "Air quality is great. Enjoy outdoors!",      emoji: "🟢", who: "No health impact" };
}

function aqiLabel(aqi) {
  const info = aqiInfo(aqi);
  return `${info.emoji} ${info.label} — ${info.category}`;
}

function updateAqiPanel(aqi) {
  const info = aqiInfo(aqi);
  const el = document.getElementById("aqiPanel");
  if (!el) return;
  el.innerHTML = `
    <div class="aqi-bar">
      <div class="aqi-number" style="color:${info.color}">${info.emoji} ${info.label}</div>
      <div class="aqi-category" style="color:${info.color}">${info.category}</div>
    </div>
    <div class="aqi-scale">
      <div class="aqi-scale-item ${aqi <= 50   ? 'aqi-active' : ''}" style="background:#3fb950">Good<br>0–50</div>
      <div class="aqi-scale-item ${aqi > 50 && aqi <= 100  ? 'aqi-active' : ''}" style="background:#a8d500">Satisfactory<br>51–100</div>
      <div class="aqi-scale-item ${aqi > 100 && aqi <= 200 ? 'aqi-active' : ''}" style="background:#d29922">Moderate<br>101–200</div>
      <div class="aqi-scale-item ${aqi > 200 && aqi <= 300 ? 'aqi-active' : ''}" style="background:#f46d43">Poor<br>201–300</div>
      <div class="aqi-scale-item ${aqi > 300 && aqi <= 400 ? 'aqi-active' : ''}" style="background:#d73027">Very Poor<br>301–400</div>
      <div class="aqi-scale-item ${aqi > 400               ? 'aqi-active' : ''}" style="background:#7e0023">Severe<br>401+</div>
    </div>
    <div class="aqi-details">
      <div class="aqi-row"><i class="fa-solid fa-user-group"></i> <span>Who's affected:</span><strong>${info.who}</strong></div>
      <div class="aqi-row"><i class="fa-solid fa-shield-heart"></i> <span>Advice:</span><strong>${info.advice}</strong></div>
      <div class="aqi-row"><i class="fa-solid fa-location-dot"></i> <span>Main pollutants (MP):</span><strong>PM2.5, PM10, Dust</strong></div>
    </div>
  `;
}

function renderForecast(forecast) {
  const el = document.getElementById("forecastList");
  if (!forecast || !forecast.length) {
    el.innerHTML = `<p class="placeholder-text">Forecast unavailable</p>`;
    return;
  }
  el.innerHTML = forecast.map(f => `
    <div class="forecast-row">
      <span class="day">${f.day}</span>
      <span class="icon">${f.icon}</span>
      <span class="desc">${f.desc || f.description || ""}</span>
      <div class="temps">
        <span class="hi">${f.hi}°</span>
        <span class="lo">${f.lo}°</span>
      </div>
    </div>
  `).join("");
}

// ─── Stats Bar ────────────────────────────────────────────────
function updateStatsBar(cities) {
  if (!cities || !cities.length) return;
  const sorted = [...cities].sort((a, b) => b.temp - a.temp);
  document.getElementById("statHighest").textContent = `${sorted[0].temp}°C — ${sorted[0].name}`;
  document.getElementById("statLowest").textContent  = `${sorted[sorted.length-1].temp}°C — ${sorted[sorted.length-1].name}`;

  const rainCity = [...cities].sort((a, b) => (b.rain_1h || 0) - (a.rain_1h || 0))[0];
  document.getElementById("statRainfall").textContent = `${rainCity.rain_1h || 0}mm — ${rainCity.name}`;

  const aqiCity = [...cities].sort((a, b) => (b.aqi || 0) - (a.aqi || 0))[0];
  document.getElementById("statAqi").textContent = `${aqiCity.aqi || "--"} — ${aqiCity.name}`;
}

// ─── Legend Update ────────────────────────────────────────────
const LEGENDS = {
  temperature: {
    title: "Temperature (°C)",
    items: [
      { color:"#313695", label:"<10" }, { color:"#4575b4", label:"10-15" },
      { color:"#74add1", label:"15-20" },{ color:"#abd9e9", label:"20-25" },
      { color:"#fee090", label:"25-30" },{ color:"#fdae61", label:"30-35" },
      { color:"#f46d43", label:"35-40" },{ color:"#d73027", label:"40+" },
    ]
  },
  rainfall: {
    title: "Rainfall (mm/hr)",
    items: [
      { color:"#c6dbef", label:"0" },{ color:"#6baed6", label:"1-5" },
      { color:"#3182bd", label:"5-10" },{ color:"#08519c", label:"10+" },
    ]
  },
  wind: {
    title: "Wind Speed (km/h)",
    items: [
      { color:"#3fb950", label:"<15" },{ color:"#fdae61", label:"15-30" },
      { color:"#f46d43", label:"30-50" },{ color:"#d73027", label:"50+" },
    ]
  },
  humidity: {
    title: "Humidity (%)",
    items: [
      { color:"#fdae61", label:"<40" },{ color:"#9ecae1", label:"40-60" },
      { color:"#3182bd", label:"60-80" },{ color:"#08519c", label:"80+" },
    ]
  },
  aqi: {
    title: "Air Quality Index",
    items: [
      { color:"#3fb950", label:"Good" },{ color:"#fdae61", label:"Mod" },
      { color:"#f46d43", label:"Poor" },{ color:"#d73027", label:"Severe" },
    ]
  },
};

function updateLegend() {
  const legend = LEGENDS[activeLayer];
  document.querySelector(".map-legend h4").textContent = legend.title;
  document.querySelector(".legend-scale").innerHTML = legend.items.map(i =>
    `<div class="legend-item" style="background:${i.color}">
       <span>${i.label}</span>
     </div>`
  ).join("");
}

// ─── UI Events ────────────────────────────────────────────────
function attachEvents() {
  // Layer buttons
  document.querySelectorAll(".layer-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".layer-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activeLayer = btn.dataset.layer;
      renderMarkers();
      updateLegend();
    });
  });

  // Search
  document.getElementById("searchBtn").addEventListener("click", doSearch);
  document.getElementById("searchInput").addEventListener("keydown", e => {
    if (e.key === "Enter") doSearch();
  });

  // Locate me — fetch real weather for exact GPS position
  document.getElementById("locateBtn").addEventListener("click", () => {
    if (!navigator.geolocation) return alert("Geolocation not supported.");
    updateTimestamp("Getting your location...");
    navigator.geolocation.getCurrentPosition(async pos => {
      const { latitude: lat, longitude: lon } = pos.coords;
      map.setView([lat, lon], 11, { animate: true });

      // Add a pin marker
      L.marker([lat, lon], {
        icon: L.divIcon({
          className: "",
          html: `<div class="weather-marker" style="border-color:#3fb950;background:rgba(22,27,34,0.95)">
                   <span style="color:#3fb950">📍 You</span>
                 </div>`,
          iconAnchor: [28, 10],
        })
      }).addTo(map);

      try {
        const res = await fetch(`${CONFIG.API_BASE_URL}/location/weather?lat=${lat}&lon=${lon}`);
        if (!res.ok) throw new Error("Location weather fetch failed");
        const data = await res.json();

        // Show in right panel
        document.getElementById("cityName").textContent  = data.name || "Your Location";
        document.getElementById("cityState").textContent = `${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E`;
        document.getElementById("cityIcon").innerHTML    = `<span style="font-size:2rem">${data.icon}</span>`;
        document.getElementById("tempValue").textContent  = data.temp;
        document.getElementById("weatherDesc").textContent = data.description;
        document.getElementById("feelsLike").textContent  = `Feels like: ${data.feels_like}°C`;
        document.getElementById("humidity").textContent   = `${data.humidity}%`;
        document.getElementById("windSpeed").textContent  = `${data.wind_speed} km/h`;
        document.getElementById("rainfall").textContent   = `${data.rain_1h} mm`;
        document.getElementById("visibility").textContent = `${data.visibility} km`;
        document.getElementById("pressure").textContent   = `${data.pressure} hPa`;
        document.getElementById("aqiValue").textContent   = aqiLabel(data.aqi);
        updateAqiPanel(data.aqi);
        renderForecast(data.forecast);
        document.querySelector(".zone-badge").textContent = "Your Location";
        document.getElementById("annualRainfall").textContent = "--";
        document.getElementById("currentSeason").textContent  = "Live";
        updateTimestamp("Live — " + new Date().toLocaleTimeString("en-IN"));
      } catch (e) {
        updateTimestamp("Live data needs active API key");
      }
    }, () => alert("Could not get your location. Please allow location access."));
  });
}

function doSearch() {
  const q = document.getElementById("searchInput").value.trim().toLowerCase();
  if (!q) return;
  const city = INDIA_CITIES.find(c =>
    c.name.toLowerCase().includes(q) || c.state.toLowerCase().includes(q)
  );
  if (city) {
    map.setView([city.lat, city.lng], 9, { animate: true });
    showCityDetail(city.name);
  } else {
    alert(`City "${q}" not found in POC dataset.`);
  }
}

// ─── Helpers ──────────────────────────────────────────────────
function showLoading(state) {
  document.getElementById("loadingOverlay").classList.toggle("hidden", !state);
}

function updateTimestamp(text) {
  document.getElementById("lastUpdated").textContent = text;
}
