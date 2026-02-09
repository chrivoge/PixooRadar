"""
Pixoo Flight Tracker Display

Displays real-time flight information on a Pixoo64 LED display in a
flight-strip style layout inspired by ATC radar displays.

Uses pre-buffered animation: all frames are computed upfront and sent
to the device at once. The Pixoo loops the animation natively for
smooth playback without continuous network traffic.

The lower half emulates an airport departure board, cycling through
flight details one at a time with centered text — no overlap possible.

Usage:
    python display_flight_data_pizoo.py
    python display_flight_data_pizoo.py --caffeinate   # prevent macOS sleep

Configuration:
    Edit config.py to set your Pixoo IP address, location coordinates, and display preferences.
"""

import argparse
import os
import subprocess
import sys
from time import sleep

from PIL import Image
from pizzoo import Pizzoo

from config import (
    ANIMATION_FRAME_SPEED,
    COLOR_BOX,
    COLOR_TEXT,
    DATA_REFRESH_SECONDS,
    FONT_NAME,
    FONT_PATH,
    LATITUDE,
    LOGO_DIR,
    LONGITUDE,
    PIXOO_IP,
)
from flight_data import FlightData

# Aviation-style colors
COLOR_ROUTE_LINE = "#666666"      # Dim gray for route line
COLOR_PLANE = "#FFFFFF"           # White for airplane icon
COLOR_SEPARATOR = "#555555"       # Separator lines
COLOR_LABEL = "#999999"           # Muted gray for info labels

# Airplane animation constants
PLANE_WIDTH = 5
ROUTE_START = 21
ROUTE_END = 43
ROUTE_WIDTH = ROUTE_END - ROUTE_START
AIRPLANE_CYCLE = ROUTE_WIDTH + PLANE_WIDTH  # 27 frames per airplane loop

# Total frames = 1 airplane cycle (27 frames). Device is unreliable above ~40 frames
# since each frame is a separate HTTP request. Info pages: 27 / 3 = 9 frames per page.
# At 400ms per frame: ~3.6s per page, ~10.8s full cycle.
TOTAL_FRAMES = AIRPLANE_CYCLE  # 27


def _measure_text_width(text: str) -> int:
    """Estimate text width in pixels (5px char + 1px spacing)."""
    return max(1, len(str(text)) * 6 - 1)


def _center_x(rect_width: int, text: str) -> int:
    """Calculate x-coordinate to center text within a given width."""
    text_width = _measure_text_width(text)
    return max(0, (rect_width - text_width) // 2)


def _draw_airplane_icon(pizzoo: Pizzoo, x: int, y: int, clip_left: int = 0,
                       clip_right: int = 64, color: str = COLOR_PLANE) -> None:
    """
    Draw a small 5x5 airplane icon pointing right with clipping support.

    The icon looks like:
       #
      ###
     #####
      ###
       #
    """
    # Fuselage (horizontal line) - x to x+4, y+2
    for px in range(x, x + 5):
        if clip_left <= px < clip_right:
            pizzoo.draw_rectangle(xy=(px, y + 2), width=1, height=1, color=color, filled=True)

    # Wings (vertical line in middle) - x+2, y to y+4
    if clip_left <= x + 2 < clip_right:
        pizzoo.draw_rectangle(xy=(x + 2, y), width=1, height=5, color=color, filled=True)

    # Tail (small vertical at back) - x, y+1 to y+3
    if clip_left <= x < clip_right:
        pizzoo.draw_rectangle(xy=(x, y + 1), width=1, height=3, color=color, filled=True)


def _draw_top_section(pizzoo: Pizzoo, logo: str, origin: str, destination: str,
                      airline_name: str = "", y_route: int = 20) -> None:
    """Draw the top section: airline logo and route display (y=0-33)."""
    # === AIRLINE LOGO (y=0-19) ===
    if logo:
        pizzoo.draw_image(logo, xy=(0, 0), size=(64, 20), resample_method=Image.LANCZOS)
    elif airline_name:
        name = airline_name[:10]
        pizzoo.draw_text(name, xy=(_center_x(64, name), 7), font=FONT_NAME, color="#FFFFFF")

    # === SEPARATOR after logo ===
    _draw_separator_line(pizzoo, y=20, style="dashed")

    # === ROUTE DISPLAY background (y=21-31) ===
    pizzoo.draw_rectangle(xy=(0, 21), width=64, height=11, color=COLOR_BOX, filled=True)

    # Origin and destination text
    pizzoo.draw_text(origin, xy=(2, y_route), font=FONT_NAME, color=COLOR_TEXT)
    dest_width = _measure_text_width(destination)
    pizzoo.draw_text(destination, xy=(62 - dest_width, y_route), font=FONT_NAME, color=COLOR_TEXT)

    # Route line (dashed)
    for i in range(ROUTE_START, ROUTE_END, 3):
        pizzoo.draw_rectangle(xy=(i, y_route + 6), width=2, height=1, color=COLOR_ROUTE_LINE, filled=True)


def _draw_label_value(pizzoo: Pizzoo, label: str, value: str, y: int) -> None:
    """Draw a label in muted gray and value in yellow, centered as a unit."""
    full_text = f"{label} {value}"
    x_start = _center_x(64, full_text)
    pizzoo.draw_text(label, xy=(x_start, y), font=FONT_NAME, color=COLOR_LABEL)
    value_x = x_start + (len(label) + 1) * 6  # label chars + space, each 6px wide
    pizzoo.draw_text(value, xy=(value_x, y), font=FONT_NAME, color=COLOR_TEXT)


def _draw_info_page(pizzoo: Pizzoo, upper_pair: tuple, lower_pair: tuple) -> None:
    """
    Draw a departure board info page in the lower section (y=33-63).

    Each pair is (label, value) drawn with label in muted gray and value in yellow,
    like an airport split-flap display (e.g., ("FLT", "FR2263") / ("ALT", "FL034")).
    """
    # Background
    pizzoo.draw_rectangle(xy=(0, 33), width=64, height=31, color=COLOR_BOX, filled=True)

    # Separator between route and info area
    _draw_separator_line(pizzoo, y=32, style="dashed")

    # Upper row (centered)
    _draw_label_value(pizzoo, upper_pair[0], upper_pair[1], y=34)

    # Separator between rows
    _draw_separator_line(pizzoo, y=48, style="dashed")

    # Lower row (centered)
    _draw_label_value(pizzoo, lower_pair[0], lower_pair[1], y=50)


def _draw_separator_line(pizzoo: Pizzoo, y: int, style: str = "solid") -> None:
    """Draw a horizontal separator line across the display."""
    if style == "solid":
        pizzoo.draw_rectangle(xy=(0, y), width=64, height=1, color=COLOR_SEPARATOR, filled=True)
    elif style == "dashed":
        for x in range(0, 64, 4):
            pizzoo.draw_rectangle(xy=(x, y), width=2, height=1, color=COLOR_SEPARATOR, filled=True)


def _format_flight_level(altitude_ft: int) -> str:
    """Convert altitude in feet to flight level format (e.g., FL350)."""
    if altitude_ft is None or altitude_ft < 1000:
        return "GND"
    fl = altitude_ft // 100
    return f"FL{fl:03d}"


def _format_speed(speed_kts: int) -> str:
    """Format ground speed with KT suffix."""
    if speed_kts is None:
        return "---KT"
    return f"{speed_kts}KT"


def _format_heading(heading: int) -> str:
    """Format heading as 3-digit degrees."""
    if heading is None:
        return "---"
    return f"{heading:03d}"


def _build_and_send_animation(pizzoo: Pizzoo, data: dict) -> None:
    """Pre-compute all animation frames and send them to the device.

    Builds TOTAL_FRAMES frames combining:
    - Smooth airplane animation (loops every AIRPLANE_CYCLE frames)
    - Departure board info cycling (one page per info item)
    """
    logo = data.get("airline_logo_path", "")
    airline_name = str(data.get("airline", "") or "")
    origin = str(data.get("origin", "---"))[:3]
    destination = str(data.get("destination", "---"))[:3]
    flight_num = str(data.get("flight_number", "----"))[:7]
    aircraft = str(data.get("aircraft_type_icao", "----"))[:4]
    registration = str(data.get("registration", "------"))[:7]
    altitude = data.get("altitude", 0) or 0
    speed = data.get("ground_speed", 0) or 0
    heading = data.get("heading")

    # Departure board pages: ((upper_label, upper_value), (lower_label, lower_value))
    # Two rows cycling together — 3 pages shown for ~3.6s each
    info_pages = [
        (("FLT", flight_num), ("ALT", _format_flight_level(altitude))),
        (("TYPE", aircraft), ("REG", registration)),
        (("SPD", _format_speed(speed)), ("HDG", _format_heading(heading))),
    ]

    frames_per_page = TOTAL_FRAMES // len(info_pages)
    y_route = 20

    # Frame 0 is created automatically by pizzoo
    for frame_idx in range(TOTAL_FRAMES):
        pizzoo.cls()

        # Top section: logo + route + animated airplane
        _draw_top_section(pizzoo, logo, origin, destination, airline_name, y_route)

        plane_x = ROUTE_START - PLANE_WIDTH + (frame_idx % AIRPLANE_CYCLE)
        _draw_airplane_icon(pizzoo, plane_x, y_route + 4,
                           clip_left=ROUTE_START, clip_right=ROUTE_END, color=COLOR_PLANE)

        # Bottom section: departure board with two info rows
        page_idx = min(frame_idx // frames_per_page, len(info_pages) - 1)
        upper_pair, lower_pair = info_pages[page_idx]
        _draw_info_page(pizzoo, upper_pair, lower_pair)

        if frame_idx < TOTAL_FRAMES - 1:
            pizzoo.add_frame()

    print(f"Sending {TOTAL_FRAMES} frames to device (frame speed: {ANIMATION_FRAME_SPEED}ms)...")
    pizzoo.render(frame_speed=ANIMATION_FRAME_SPEED)


def main():
    """Main function to run the flight tracker display."""
    parser = argparse.ArgumentParser(description="Pixoo Flight Tracker Display")
    parser.add_argument("--caffeinate", action="store_true",
                        help="Prevent macOS from sleeping while the tracker runs")
    args = parser.parse_args()

    if args.caffeinate:
        sys.exit(subprocess.call(
            ["caffeinate", "-i", sys.executable, os.path.abspath(__file__)]
        ))

    pizzoo = Pizzoo(PIXOO_IP, debug=True)
    fd = FlightData(save_logo_dir=LOGO_DIR)
    pizzoo.load_font(FONT_NAME, FONT_PATH)

    current_flight_id = None

    while True:
        data = fd.get_closest_flight_data(LATITUDE, LONGITUDE)

        if not data:
            print("No flight data available, retrying...")
            sleep(5)
            continue

        # Identify the flight by ICAO24 transponder address (unique per aircraft)
        new_flight_id = data.get("icao24")

        if new_flight_id == current_flight_id:
            # Same aircraft still closest — let the animation keep playing
            print(f"Still tracking: {data.get('flight_number')} — animation unchanged")
            sleep(DATA_REFRESH_SECONDS)
            continue

        # New flight detected — rebuild and send animation
        current_flight_id = new_flight_id
        print(f"New flight: {data.get('flight_number')} ({data.get('origin')} -> {data.get('destination')})")

        _build_and_send_animation(pizzoo, data)
        print(f"Animation playing. Next check in {DATA_REFRESH_SECONDS}s...")

        sleep(DATA_REFRESH_SECONDS)


if __name__ == "__main__":
    main()
