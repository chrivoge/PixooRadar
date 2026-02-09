# Pixoo Flight Tracker

A real-time flight tracker display for the Pixoo64 LED matrix. Shows information about the closest aircraft to your location, including airline logo, route, and flight details.

<img src="display" width="50%">

## Features

- Displays airline logo (automatically fetched and cached)
- Shows origin and destination airport codes with animated route indicator
- Rotating information display:
  - Flight number
  - Aircraft type (ICAO code)
  - Aircraft registration
  - Altitude
  - Ground speed
- Automatic data refresh
- Fetches METAR weather data for destination airport

## Requirements

- Python 3.10+
- Pixoo64 LED display on your local network
- Internet connection (for FlightRadar24 API)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/pixoo-flight-tracker.git
   cd pixoo-flight-tracker
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure your settings in `config.py` (see Configuration below)

4. Run the tracker:
   ```bash
   python display_flight_data_pizoo.py
   ```

## Configuration

Edit `config.py` to customize the flight tracker:

### Device Settings
```python
PIXOO_IP = "192.168.178.36"  # Your Pixoo's IP address
PIXOO_PORT = 80               # Usually 80
```

### Location
Set your coordinates to track flights overhead:
```python
LATITUDE = 52.363
LONGITUDE = 14.060
```

### Timing
```python
DATA_REFRESH_SECONDS = 60      # How often to check for new flights (seconds)
ANIMATION_FRAME_SPEED = 200    # Animation frame speed in milliseconds (95-280ms recommended)
```

### Colors
```python
COLOR_TEXT = "#FFFF00"       # Yellow - main text
COLOR_ACCENT = "#00BA0F"     # Green - animation accent
COLOR_BACKGROUND = "#BABABA" # Light gray - background
COLOR_BOX = "#454545"        # Dark gray - info boxes
```

## Project Structure

```
pixoo-flight-tracker/
├── config.py                    # Configuration settings
├── display_flight_data_pizoo.py # Main display script
├── flight_data.py               # FlightRadar24 API wrapper
├── fonts/                       # BDF font files
│   └── splitflap.bdf
├── airline_logos/               # Cached airline logos (auto-created)
├── requirements.txt
└── README.md
```

## How It Works

1. The tracker queries FlightRadar24 for flights within 100km of your location
2. It finds the closest flight with valid airline information
3. Flight details are fetched, including airline logo
4. The display shows an animated view with the information
5. Data refreshes automatically based on `DATA_REFRESH_ITERATIONS`

## Credits

- [pizzoo](https://github.com/pabletos/pizzoo) - Pixoo display library
- [FlightRadar24](https://github.com/JeanExtique/FlightRadar24-API) - Flight data API
- NOAA - METAR weather data
