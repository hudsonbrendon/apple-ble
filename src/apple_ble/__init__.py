"""Pure-Python parser for Apple Continuity BLE proximity-pairing adverts."""

from .const import APPLE_MANUFACTURER_ID, MODEL_BY_CHAR
from .models import AirPodsData, AppleAdvert
from .parser import decode_battery_nibble, parse_proximity_pairing

__version__ = "0.1.1"

__all__ = [
    "APPLE_MANUFACTURER_ID",
    "MODEL_BY_CHAR",
    "AirPodsData",
    "AppleAdvert",
    "decode_battery_nibble",
    "parse_proximity_pairing",
]
