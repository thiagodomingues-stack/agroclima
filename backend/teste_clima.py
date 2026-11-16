import requests

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": -21.97,
    "longitude": -46.80,
    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
    "timezone": "America/Sao_Paulo",
}
r = requests.get(url, params=params, timeout=30)
print(r.status_code)
print(r.json()["daily"])