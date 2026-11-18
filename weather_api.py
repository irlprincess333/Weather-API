
from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__)

CITIES = {
    "Canton": {"latitude": 40.7989, "longitude": -81.3784},
    "Louisville": {"latitude": 40.8370, "longitude": -81.2596},
    "North Canton": {"latitude": 40.8759, "longitude": -81.4023},
    "Massillon": {"latitude": 40.7967, "longitude": -81.5215},
    "Akron": {"latitude": 41.0814, "longitude": -81.5190},
    "Cleveland": {"latitude": 41.4993, "longitude": -81.6944},
    "Columbus": {"latitude": 39.9612, "longitude": -82.9988},
    "Green": {"latitude": 40.9459, "longitude": -81.4832},
    "Alliance": {"latitude": 40.9153, "longitude": -81.1059},
    "Massillon": {"latitude": 40.7967, "longitude": -81.5215},
}

RAIN_CODES = {51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99}
SNOW_CODES = {71, 73, 75, 77, 85, 86}
CLOUDY_CODES = {2, 3, 45, 48}


def get_weather(city):
    if city not in CITIES:
        return None

    coordinates = CITIES[city]

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": coordinates["latitude"],
        "longitude": coordinates["longitude"],
        "current": (
            "temperature_2m,relative_humidity_2m,weather_code,"
            "wind_speed_10m,precipitation,rain,snowfall,is_day,cloud_cover"
        ),
        "hourly": (
            "precipitation_probability,rain_probability,"
            "snowfall_probability,snowfall,precipitation,rain,"
            "weather_code,cloud_cover,is_day"
        ),
        "daily": "precipitation_probability_max,snowfall_sum",
        "forecast_days": 1,
        "timezone": "auto",
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    weather = response.json()

    current = weather["current"]
    daily = weather.get("daily", {})

    code = int(current.get("weather_code", 0))
    rain_amount = float(current.get("rain", 0) or 0)
    snow_amount = float(current.get("snowfall", 0) or 0)
    cloud_cover = int(current.get("cloud_cover", 0) or 0)

    is_raining = rain_amount > 0 or code in RAIN_CODES
    is_snowing = snow_amount > 0 or code in SNOW_CODES
    is_cloudy = cloud_cover >= 45 or code in CLOUDY_CODES

    condition = "Clear"
    if code in {1}:
        condition = "Mainly clear"
    elif code in {2}:
        condition = "Partly cloudy"
    elif code in {3}:
        condition = "Overcast"
    elif code in {45, 48}:
        condition = "Foggy"
    elif code in RAIN_CODES:
        condition = "Rain"
    elif code in SNOW_CODES:
        condition = "Snow"
    elif code in {0}:
        condition = "Clear"

    precipitation_chance = 0
    if daily.get("precipitation_probability_max"):
        precipitation_chance = daily["precipitation_probability_max"][0] or 0

    snowfall_forecast = 0
    if daily.get("snowfall_sum"):
        snowfall_forecast = daily["snowfall_sum"][0] or 0

    return {
        "city": city,
        "temperature": round(current.get("temperature_2m", 0)),
        "humidity": current.get("relative_humidity_2m", 0),
        "wind_speed": round(current.get("wind_speed_10m", 0)),
        "condition": condition,
        "weather_code": code,
        "weather_time": current.get("time"),
        "is_day": current.get("is_day", 1),
        "cloud_cover": cloud_cover,
        "is_cloudy": is_cloudy,
        "is_raining": is_raining,
        "is_snowing": is_snowing,
        "precipitation": current.get("precipitation", 0),
        "rain": rain_amount,
        "current_snowfall": snow_amount,
        "precipitation_chance": precipitation_chance,
        "snowfall_amount": snowfall_forecast,
        "snow_forecast": snowfall_forecast > 0,
    }


@app.route("/")
def home():
    return render_template("index.html", api_base="")


@app.route("/abbyann333weatherapi")
def weather_page():
    return render_template("index.html", api_base="")


@app.route("/api/weather")
def weather_api():
    from flask import request

    city = request.args.get("city", "Canton")
    try:
        result = get_weather(city)
        if result is None:
            return jsonify({"error": "City not found"}), 404
        return jsonify(result)
    except requests.RequestException as error:
        return jsonify({"error": f"Weather service unavailable: {error}"}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
