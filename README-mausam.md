# Mausam Agent — Weather & Day-Planning AI Agent

An AI agent built with Python and Google Gemini that plans your day around real weather data.

## What it does
- Live weather for any city, town or valley (it understands misspelled place names)
- Air quality (AQI) with health advice
- Tomorrow and day-after-tomorrow forecast
- Sunrise and sunset times
- Remembers your last checked place — just say "mera sheher"
- Gives short, practical advice in Roman Urdu: jacket or not, umbrella or not, good time to go out

## How it works
User place -> Gemini identifies the place (name, country, latitude, longitude) -> Open-Meteo tools fetch real weather, AQI, forecast and sun times -> Gemini turns the data into simple advice. Includes input validation, retries, error handling and logging.

## Run it
1. Install Python 3
2. pip install google-genai
3. Put your own Gemini API key in mausam.py (replace YOUR_GEMINI_API_KEY)
4. python mausam.py

Weather data: Open-Meteo (free, no key needed)
