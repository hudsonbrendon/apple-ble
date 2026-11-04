"""Pure-Python parser for Apple Continuity BLE proximity-pairing adverts."""

from .const import APPLE_MANUFACTURER_ID, MODEL_BY_CHAR
from .crypto import DecryptedStatus, decrypt_status, parse_key, resolve_rpa
from .models import AirPodsData, AppleAdvert
from .parser import decode_battery_nibble, parse_proximity_pairing

__version__ = "0.2.0"

__all__ = [
    "APPLE_MANUFACTURER_ID",
    "MODEL_BY_CHAR",
    "AirPodsData",
    "AppleAdvert",
    "DecryptedStatus",
    "decrypt_status",
    "parse_key",
    "resolve_rpa",
    "decode_battery_nibble",
    "parse_proximity_pairing",
]
