"""Constants for the Apple Continuity proximity-pairing protocol."""

# Apple's Bluetooth company identifier (0x004C).
APPLE_MANUFACTURER_ID: int = 76

# Continuity message type for AirPods battery/proximity pairing.
MSG_TYPE_PROXIMITY_PAIRING: int = 0x07

# A proximity-pairing payload (after the company id) is 27 bytes = 54 hex chars.
PROXIMITY_PAIRING_HEX_LEN: int = 54

# Nibble indices into the 54-char hex string of manufacturer_data[76].
# These mirror the well-tested AirStatus layout.
IDX_MODEL: int = 7
IDX_FLIP: int = 10
IDX_LEFT_NOFLIP: int = 13
IDX_RIGHT_NOFLIP: int = 12
IDX_CHARGE: int = 14
IDX_CASE: int = 15

# Battery nibble value 0x0F means "not present / unknown".
NIBBLE_UNKNOWN: int = 0x0F

# Model is identified by the single hex char at IDX_MODEL.
MODEL_BY_CHAR: dict[str, str] = {
    "2": "AirPods (1st gen)",
    "f": "AirPods (2nd gen)",
    "3": "AirPods (3rd gen)",
    "e": "AirPods Pro",
    "a": "AirPods Max",
}
