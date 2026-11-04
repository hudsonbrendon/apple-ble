"""Parse Apple Continuity proximity-pairing advertisements into AirPodsData."""

from __future__ import annotations

from . import const
from .models import AirPodsData

# Bytes of manufacturer_data[76] that are AES-128 encrypted with the EncKey.
ENCRYPTED_SLICE = slice(11, 27)

# Byte offsets (manufacturer_data[76], type byte = 0).
_STATUS, _LID, _COLOR = 5, 8, 9


def decode_battery_nibble(nibble: int) -> int | None:
    """Convert a 0x0-0xF battery nibble to a percentage in 10% steps.

    Apple reports battery in deciles: 0..10 -> 0..100%. Values 11-15 mean
    "not present / unknown" and yield None.
    """
    if nibble > 10:
        return None
    return nibble * 10


def _is_flipped(hexstr: str) -> bool:
    """AirPods report L/R swapped depending on orientation bit."""
    return (int(hexstr[const.IDX_FLIP], 16) & 0x02) == 0


def parse_proximity_pairing(data: bytes) -> AirPodsData | None:
    """Parse manufacturer_data[76] bytes into AirPodsData, or None if not AirPods.

    `data` must be the bytes that follow Apple's company id (i.e. starting with
    the message type byte). Returns None for any advert that is not a complete
    proximity-pairing message.
    """
    if not data or data[0] != const.MSG_TYPE_PROXIMITY_PAIRING:
        return None

    hexstr = data.hex()
    if len(hexstr) < const.PROXIMITY_PAIRING_HEX_LEN:
        return None

    model = const.MODEL_BY_CHAR.get(hexstr[const.IDX_MODEL], "AirPods")

    flipped = _is_flipped(hexstr)
    left_idx = const.IDX_RIGHT_NOFLIP if flipped else const.IDX_LEFT_NOFLIP
    right_idx = const.IDX_LEFT_NOFLIP if flipped else const.IDX_RIGHT_NOFLIP

    left_battery = decode_battery_nibble(int(hexstr[left_idx], 16))
    right_battery = decode_battery_nibble(int(hexstr[right_idx], 16))
    case_battery = decode_battery_nibble(int(hexstr[const.IDX_CASE], 16))

    charge = int(hexstr[const.IDX_CHARGE], 16)
    left_bit = 0b0010 if flipped else 0b0001
    right_bit = 0b0001 if flipped else 0b0010
    left_charging = bool(charge & left_bit)
    right_charging = bool(charge & right_bit)
    case_charging = bool(charge & 0b0100)

    status = data[_STATUS]
    # Bit 6: the advertising pod is in the case; together with the flip bit it
    # decides which of bits 1/3 is the left pod.
    swap = flipped != bool(status & 0x40)
    left_in_ear = bool(status & (0x08 if swap else 0x02))
    right_in_ear = bool(status & (0x02 if swap else 0x08))
    pods_in_case = 2 if status & 0x04 else 1 if status & 0x10 else 0
    lid = data[_LID]

    return AirPodsData(
        model=model,
        left_battery=left_battery,
        right_battery=right_battery,
        case_battery=case_battery,
        left_charging=left_charging,
        right_charging=right_charging,
        case_charging=case_charging,
        model_id=data[3] | data[4] << 8,
        flipped=flipped,
        left_in_ear=left_in_ear,
        right_in_ear=right_in_ear,
        pods_in_case=pods_in_case,
        lid_open=not lid & 0x08,
        lid_open_count=lid & 0x07,
        color=data[_COLOR],
    )
