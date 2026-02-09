"""
Configuration settings for Pixoo Flight Tracker.

Modify these values to customize the flight tracker for your setup.
"""

# =============================================================================
# Pixoo Device Settings
# =============================================================================
PIXOO_IP = "192.168.x.x"   # Replace with your Pixoo's IP address
PIXOO_PORT = 80

# =============================================================================
# Location for Flight Tracking
# =============================================================================
# Set your location to track flights overhead
LATITUDE = 52.520    # Replace with your latitude
LONGITUDE = 13.405   # Replace with your longitude

# =============================================================================
# Display Settings
# =============================================================================
FONT_NAME = "splitflap"
FONT_PATH = "./fonts/splitflap.bdf"
LOGO_DIR = "airline_logos"

# =============================================================================
# Timing
# =============================================================================
# How often to fetch new flight data (in seconds)
DATA_REFRESH_SECONDS = 60

# Animation frame speed in milliseconds (how fast the airplane moves)
# Higher = slower airplane but longer per info page
# At 400ms × 9 frames per page = ~3.6s per page, ~10.8s full cycle
ANIMATION_FRAME_SPEED = 300

# =============================================================================
# Colors
# =============================================================================
COLOR_TEXT = "#FFFF00"           # Yellow - main text color
COLOR_ACCENT = "#00BA0F"         # Green - animation accent
COLOR_BACKGROUND = "#BABABA"     # Light gray - display background
COLOR_BOX = "#454545"            # Dark gray - info boxes

# =============================================================================
# Logo Processing
# =============================================================================
# Background color for airline logos (RGBA)
# Should match COLOR_BACKGROUND for seamless display
LOGO_BG_COLOR = (186, 186, 186, 255)
