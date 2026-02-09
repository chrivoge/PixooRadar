# Pixoo Flight Tracker

A real-time flight tracker display for the Pixoo64 LED matrix. Shows information about the closest aircraft to your location, including airline logo, route, and flight details.

<img src="display.png" width="50%">

## Features

- Displays airline logo (automatically fetched and cached)
- Shows origin and destination airport codes with animated route indicator
- Rotating information display:
  - Flight number and altitude
  - Aircraft type and registration
  - Ground speed and heading
- Automatic data refresh (only updates when a new aircraft is detected)
- macOS sleep prevention with `--caffeinate` flag

## Requirements

- Python 3.10+
- Pixoo64 LED display on your local network
- Internet connection (for FlightRadar24 API)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/chrivoge/PixooRadar.git
   cd PixooRadar
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

   To prevent macOS from sleeping while the tracker runs:
   ```bash
   python display_flight_data_pizoo.py --caffeinate
   ```

## Configuration

Edit `config.py` to customize the flight tracker:

### Device Settings
```python
PIXOO_IP = "192.168.x.x"  # Your Pixoo's IP address
```

### Location
Set your coordinates to track flights overhead:
```python
LATITUDE = 52.520    # Your latitude
LONGITUDE = 13.405   # Your longitude
```

### Timing
```python
DATA_REFRESH_SECONDS = 60    # How often to check for new flights (seconds)
ANIMATION_FRAME_SPEED = 300  # Animation frame speed in milliseconds
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
PixooRadar/
├── config.py                    # Configuration settings
├── display_flight_data_pizoo.py # Main display script
├── flight_data.py               # FlightRadar24 API wrapper
├── fonts/
│   └── splitflap.bdf            # BDF font for the display
├── airline_logos/                # Cached airline logos (auto-created)
├── requirements.txt
└── README.md
```

## How It Works

1. The tracker queries FlightRadar24 for flights within 100km of your location
2. It finds the closest flight with valid airline information
3. Flight details are fetched, including airline logo (resized and cached locally)
4. All animation frames are pre-computed and sent to the Pixoo as a native animation
5. Data refreshes automatically based on `DATA_REFRESH_SECONDS`, but only re-sends the animation when a different aircraft becomes the closest

## Credits

- [pizzoo](https://github.com/pabletos/pizzoo) - Pixoo display library
- [FlightRadar24](https://github.com/JeanExtique/FlightRadar24-API) - Flight data API
- NOAA - METAR weather data
