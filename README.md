<p align="center">
  <img src="assets/apple-logo.png" alt="Apple" width="320">
</p>

# apple-ble

[![CI](https://github.com/hudsonbrendon/apple-ble/actions/workflows/ci.yml/badge.svg)](https://github.com/hudsonbrendon/apple-ble/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/apple-ble)](https://pypi.org/project/apple-ble/)
[![Python](https://img.shields.io/pypi/pyversions/apple-ble)](https://pypi.org/project/apple-ble/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Read **AirPods battery** (case / left / right + charging) and detect nearby
**Apple devices** from Python, straight off the unencrypted Apple Continuity
*proximity-pairing* BLE advertisement — no pairing, no connection.

This library powers the
[**Apple BLE Home Assistant integration**](https://github.com/hudsonbrendon/ha-apple-ble),
but works standalone in any Python project (or straight from the command line).
The parser is pure and dependency-free; `bleak` is only needed for the optional
scanner CLI.

> **What works:** AirPods broadcast their battery in an unencrypted Continuity
> advert when the lid is opened. **What doesn't:** Apple Watch / iPhone do **not**
> put battery in their adverts — BLE can only tell you an Apple device is *nearby*.
> Apple rotates the BLE MAC (~15 min), so there is no stable per-device id.

## Features

- 🔋 **AirPods battery** — case, left, and right levels plus per-pod and case
  charging flags, decoded from the manufacturer-`0x004C` proximity-pairing advert.
- 🎧 **Model detection** — AirPods 1/2/3, Pro, Pro 2, Max.
- 📡 **Presence-friendly** — exposes the Apple manufacturer id so callers can count
  nearby Apple devices.
- 🧪 **Pure parser** — `parse_proximity_pairing(bytes) -> AirPodsData | None`, no I/O,
  trivially unit-testable.
- 🖥️ **CLI** — `apple-ble` scans and prints any AirPods it sees (needs the `cli` extra).

## Requirements

- Python **3.12** or newer.
- A Bluetooth LE adapter (built-in or USB) — only for live scanning; the parser
  itself needs nothing.

## Installation

```bash
pip install apple-ble            # core (parsing only)
pip install "apple-ble[cli]"     # + bleak scanner CLI
```

## CLI usage

```bash
apple-ble    # 15s BLE scan; open your AirPods lid nearby and watch the battery
```

## Library usage

```python
from apple_ble import parse_proximity_pairing, APPLE_MANUFACTURER_ID

# `payload` is manufacturer_data[76] from any BLE stack (bleak, Home Assistant, ...)
data = parse_proximity_pairing(payload)
if data:
    print(data.model, data.left_battery, data.right_battery, data.case_battery)
    print(data.left_charging, data.right_charging, data.case_charging)
```

`parse_proximity_pairing` returns `None` for anything that isn't a complete
AirPods proximity-pairing advert, so it is safe to feed it every Apple advert you
see and keep the non-`None` results.

### API

| Symbol | Description |
|---|---|
| `parse_proximity_pairing(data)` | Parse `manufacturer_data[76]` bytes into `AirPodsData`, or `None` if it isn't AirPods. |
| `AirPodsData` | Frozen dataclass: `model`, `left_battery`, `right_battery`, `case_battery` (`int %` or `None`), `left_charging`, `right_charging`, `case_charging`. |
| `decode_battery_nibble(nibble)` | Pure helper: a `0x0`–`0xF` battery nibble to a percentage (`None` when not present). |
| `APPLE_MANUFACTURER_ID` | `76` (`0x004C`) — Apple's Bluetooth company id. |
| `MODEL_BY_CHAR` | Mapping of the model nibble to a human model name. |

## Credits

Continuity reverse-engineering:
[furiousMAC/continuity](https://github.com/furiousMAC/continuity),
[kavishdevar/librepods](https://github.com/kavishdevar/librepods),
[delphiki/AirStatus](https://github.com/delphiki/AirStatus),
[d4rken-org/capod](https://github.com/d4rken-org/capod).
Author [@hudsonbrendon](https://github.com/hudsonbrendon).

## License

MIT — see [LICENSE](LICENSE).
