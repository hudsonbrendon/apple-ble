"""Optional standalone BLE scanner CLI (requires the `cli` extra: bleak)."""

from __future__ import annotations

import asyncio

from . import const
from .models import AirPodsData
from .parser import parse_proximity_pairing


def _fmt(v: int | None) -> str:
    """Format a battery percentage for display; absent pods show '--'."""
    return "--" if v is None else f"{v}%"


def advert_to_airpods(advertisement_data) -> AirPodsData | None:
    """Extract AirPodsData from a bleak AdvertisementData-like object."""
    mfr = getattr(advertisement_data, "manufacturer_data", {}) or {}
    payload = mfr.get(const.APPLE_MANUFACTURER_ID)
    if payload is None:
        return None
    return parse_proximity_pairing(bytes(payload))


async def _scan(seconds: float) -> None:
    from bleak import BleakScanner  # imported lazily so core lib has no dep

    seen: dict[str, AirPodsData] = {}

    def _cb(device, advertisement_data) -> None:
        data = advert_to_airpods(advertisement_data)
        if data is not None:
            seen[device.address] = data
            print(
                f"[{advertisement_data.rssi} dBm] {data.model}: "
                f"L={_fmt(data.left_battery)} R={_fmt(data.right_battery)} "
                f"case={_fmt(data.case_battery)} "
                f"(charging L/R/case={data.left_charging}/"
                f"{data.right_charging}/{data.case_charging})"
            )

    scanner = BleakScanner(detection_callback=_cb)
    await scanner.start()
    await asyncio.sleep(seconds)
    await scanner.stop()
    if not seen:
        print("No AirPods adverts seen. Open the lid near the scanner and retry.")


def main() -> None:
    """Console entry point: `apple-ble`."""
    asyncio.run(_scan(15.0))


if __name__ == "__main__":
    main()
