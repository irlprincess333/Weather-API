import requests
from flask import Flask, jsonify, redirect, render_template, request

app = Flask(__name__)

OHIO_CITIES = {
    "Alliance": (40.9153, -81.1059),
    "Akron": (41.0814, -81.5190),
    "Canton": (40.7989, -81.3784),
    "Cincinnati": (39.1031, -84.5120),
    "Cleveland": (41.4993, -81.6944),
    "Columbus": (39.9612, -82.9988),
    "Dayton": (39.7589, -84.1916),
    "Toledo": (41.6528, -83.5379),
}

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Foggy",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Rain showers",
    82: "Heavy rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with hail",
}


@app.route("/")
def root():
    return redirect("/abbyann333weatherapi")


@app.route("/abbyann333weatherapi")
@app.route("/Abbyann333-Weather-API")
def home():
    import os
    api_base = os.environ.get("PUBLIC_API_BASE", "")
    return render_template("index.html", cities=sorted(OHIO_CITIES.keys()), api_base=api_base)
@app.route("/weather")
def weather():
    city = request.args.get("city", "Columbus")
    if city not in OHIO_CITIES:
        return jsonify({"error": f"Unknown city: {city}"}), 404

    lat, lon = OHIO_CITIES[city]
    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
            },
            timeout=10,
        )
        response.raise_for_status()
        current = response.json()["current"]
    except requests.RequestException:
        return jsonify({"error": "Could not reach weather service"}), 502

    code = current.get("weather_code", 0)
    return jsonify({
        "city": city,
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "wind_speed": current["wind_speed_10m"],
        "condition": WEATHER_CODES.get(code, "Unknown"),
    })


if __name__ == "__main__":
    print("Starting server at http://127.0.0.1:5001/abbyann333weatherapi")
    app.run(debug=False, host="127.0.0.1", port=5001)
