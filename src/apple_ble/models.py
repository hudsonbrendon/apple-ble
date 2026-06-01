"""Immutable data models returned by the parser."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AirPodsData:
    """Parsed AirPods proximity-pairing state.

    Battery values are integer percentages in 10% steps, or None when the
    pod/case is not present or the value is unknown (nibble 0x0F).
    """

    model: str
    left_battery: int | None
    right_battery: int | None
    case_battery: int | None
    left_charging: bool
    right_charging: bool
    case_charging: bool


@dataclass(frozen=True, slots=True)
class AppleAdvert:
    """A minimal record of any Apple manufacturer-76 advertisement seen."""

    address: str
    rssi: int
    is_proximity_pairing: bool
