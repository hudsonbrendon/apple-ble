# apple-ble

Pure-Python parser for Apple Continuity BLE *proximity-pairing* advertisements.
Reads AirPods battery (case / left / right) and charging state from the
unencrypted manufacturer-76 advert. No connection required, no HA dependency.

## Install
```bash
pip install apple-ble            # core (parsing only)
pip install "apple-ble[cli]"     # + bleak scanner CLI
```

## Use as a library
```python
from apple_ble import parse_proximity_pairing, APPLE_MANUFACTURER_ID

# `payload` is manufacturer_data[76] from any BLE stack (bleak, HA, etc.)
data = parse_proximity_pairing(payload)
if data:
    print(data.model, data.left_battery, data.right_battery, data.case_battery)
```

## Scan from the terminal
```bash
apple-ble   # opens a 15s BLE scan, prints AirPods it sees
```

## Limitations
- Only AirPods expose battery over BLE. Apple Watch / iPhone do **not**.
- Apple rotates the BLE MAC (~15 min); there is no stable per-device id in the advert.
- Battery is reported in coarse 10% steps.

Reverse-engineering credit: furiousMAC/continuity, kavishdevar/librepods,
delphiki/AirStatus, d4rken-org/capod.
