// Weather Prediction System - JavaScript Application

document.addEventListener("DOMContentLoaded", function () {
  initializeApp();
  addRippleEffect();
});

// 🌍 Base URL for backend (Django)
const API_BASE = "http://127.0.0.1:8000";

// Initialize the application
function initializeApp() {
  const form = document.getElementById("predictionForm");
  const cityInput = document.getElementById("cityInput");

  if (!form || !cityInput) {
    console.error("❌ Missing form or input element in HTML");
    return;
  }

  form.addEventListener("submit", handlePredictionSubmit);

  // Check system health on load
  checkSystemHealth();

  // Enter key submits form
  cityInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      form.dispatchEvent(new Event("submit"));
    }
  });
}

// Handle form submission
async function handlePredictionSubmit(event) {
  event.preventDefault();

  const cityInput = document.getElementById("cityInput");
  const cityName = cityInput.value.trim();

  if (!cityName) {
    showError("Please enter a city name.");
    return;
  }

  // Show loading state
  showLoadingState(true);
  hideError();
  hideResults();

  try {
    const response = await fetch(`${API_BASE}/api/predict/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ city: cityName }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`❌ Server Error ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    console.log("✅ API Response:", data);

    if (data.prediction || data.predicted_temperature) {
      displayResults(data);
    } else {
      showError(data.error || "An error occurred while making the prediction.");
    }
  } catch (error) {
    console.error("Prediction error:", error);
    showError("Network error. Please check your connection and try again.");
  } finally {
    showLoadingState(false);
  }
}

// Display prediction results
function displayResults(data) {
  const predictedTemp = data.prediction ?? data.predicted_temperature ?? null;

  if (predictedTemp !== null && !isNaN(predictedTemp)) {
    document.getElementById("predictedTemp").textContent =
      `${parseFloat(predictedTemp).toFixed(2)}°C`;
  } else {
    document.getElementById("predictedTemp").textContent = "N/A";
  }

  document.getElementById("cityName").textContent = data.city ?? "Unknown";

  // Update metrics safely
  document.getElementById("mseValue").textContent =
    data.metrics?.mse !== undefined ? data.metrics.mse.toFixed(4) : "N/A";
  document.getElementById("maeValue").textContent =
    data.metrics?.mae !== undefined ? data.metrics.mae.toFixed(4) : "N/A";
  document.getElementById("r2Value").textContent =
    data.metrics?.r2_score !== undefined ? data.metrics.r2_score.toFixed(4) : "N/A";

  // Update model info
  document.getElementById("trainingSamples").textContent =
    data.model_evaluation?.training_samples ?? "--";

  // Weather chart
  if (Array.isArray(data.historical_data) && data.historical_data.length > 0) {
    createWeatherChart(data.historical_data, predictedTemp, data.city);
  }

  // Show results section
  showResults();
}

// Create interactive weather chart using Plotly
function createWeatherChart(historicalData, predictedTemp, cityName) {
  const dates = historicalData.map((d) => d.date);
  const temperatures = historicalData.map((d) => d.temperature);
  const humidity = historicalData.map((d) => d.humidity ?? null);
  const windSpeed = historicalData.map((d) => d.wind_speed ?? null);

  const traces = [
    {
      x: dates,
      y: temperatures,
      type: "scatter",
      mode: "lines+markers",
      name: "Historical Temperature",
      line: { color: "#667eea", width: 3 },
      marker: { size: 8 },
    },
  ];

  if (predictedTemp !== null && !isNaN(predictedTemp)) {
    const lastDate = new Date(dates[dates.length - 1]);
    lastDate.setDate(lastDate.getDate() + 1);

    traces.push({
      x: [lastDate.toISOString().split("T")[0]],
      y: [predictedTemp],
      type: "scatter",
      mode: "markers",
      name: "Predicted Temperature",
      marker: { size: 15, color: "#e53e3e", symbol: "star" },
    });
  }

  if (humidity.some((h) => h !== null)) {
    traces.push({
      x: dates,
      y: humidity,
      type: "scatter",
      mode: "lines",
      name: "Humidity (%)",
      line: { color: "#38b2ac", width: 2 },
      yaxis: "y2",
      opacity: 0.7,
    });
  }

  if (windSpeed.some((ws) => ws !== null)) {
    traces.push({
      x: dates,
      y: windSpeed,
      type: "scatter",
      mode: "lines",
      name: "Wind Speed (m/s)",
      line: { color: "#f6ad55", width: 2 },
      yaxis: "y3",
      opacity: 0.7,
    });
  }

  const layout = {
    title: {
      text: `Weather Data & Prediction for ${cityName ?? "City"}`,
      font: { size: 18, color: "#2d3748" },
    },
    xaxis: { title: "Date", type: "date" },
    yaxis: {
      title: "Temperature (°C)",
      titlefont: { color: "#667eea" },
      tickfont: { color: "#667eea" },
    },
    yaxis2: {
      title: "Humidity (%)",
      titlefont: { color: "#38b2ac" },
      tickfont: { color: "#38b2ac" },
      overlaying: "y",
      side: "right",
      position: 0.85,
    },
    yaxis3: {
      title: "Wind Speed (m/s)",
      titlefont: { color: "#f6ad55" },
      tickfont: { color: "#f6ad55" },
      overlaying: "y",
      side: "right",
    },
    legend: {
      x: 0.02,
      y: 0.98,
      bgcolor: "rgba(255,255,255,0.8)",
      bordercolor: "#e2e8f0",
      borderwidth: 1,
    },
    margin: { t: 50, l: 50, r: 80, b: 50 },
    hovermode: "x unified",
  };

  Plotly.newPlot("weatherChart", traces, layout, {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
  });
}

// UI Helpers
function showLoadingState(loading) {
  const btn = document.getElementById("predictBtn");
  const btnText = document.getElementById("btnText");
  const loader = document.getElementById("loader");

  if (!btn || !btnText || !loader) return;

  if (loading) {
    btn.disabled = true;
    btnText.textContent = "Predicting...";
    loader.classList.remove("hidden");
  } else {
    btn.disabled = false;
    btnText.textContent = "🔮 Predict Weather";
    loader.classList.add("hidden");
  }
}

function showResults() {
  const resultsSection = document.getElementById("resultsSection");
  if (resultsSection) resultsSection.classList.remove("hidden");
}

function hideResults() {
  const resultsSection = document.getElementById("resultsSection");
  if (resultsSection) resultsSection.classList.add("hidden");
}

function showError(message) {
  const errorSection = document.getElementById("errorSection");
  const errorMessage = document.getElementById("errorMessage");

  if (errorMessage) errorMessage.textContent = message;
  if (errorSection) errorSection.classList.remove("hidden");
}

function hideError() {
  const errorSection = document.getElementById("errorSection");
  if (errorSection) errorSection.classList.add("hidden");
}

// Check system health
async function checkSystemHealth() {
  try {
    const response = await fetch(`${API_BASE}/api/health/`);
    const data = await response.json();
    if (!data.models_loaded) {
      console.warn("⚠️ Models are still loading...");
    }
  } catch (error) {
    console.error("Health check failed:", error);
  }
}

// Ripple effect for buttons
function addRippleEffect() {
  const buttons = document.querySelectorAll(".predict-btn, .retry-btn");
  buttons.forEach((button) => button.addEventListener("click", createRipple));
}

function createRipple(event) {
  const button = event.currentTarget;
  const circle = document.createElement("span");
  const diameter = Math.max(button.clientWidth, button.clientHeight);
  const radius = diameter / 2;

  circle.style.width = circle.style.height = `${diameter}px`;
  circle.style.left = `${event.clientX - button.offsetLeft - radius}px`;
  circle.style.top = `${event.clientY - button.offsetTop - radius}px`;
  circle.classList.add("ripple");

  const existingRipple = button.getElementsByClassName("ripple")[0];
  if (existingRipple) existingRipple.remove();

  button.appendChild(circle);
  setTimeout(() => circle.remove(), 600);
}

// Add ripple animation CSS
const rippleCSS = `
.ripple {
    position: absolute;
    border-radius: 50%;
    transform: scale(0);
    animation: ripple 600ms linear;
    background-color: rgba(255, 255, 255, 0.6);
}
@keyframes ripple {
    to { transform: scale(4); opacity: 0; }
}`;
const style = document.createElement("style");
style.textContent = rippleCSS;
document.head.appendChild(style);
