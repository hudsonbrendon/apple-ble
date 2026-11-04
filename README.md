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
- 👂 **In-ear / in-case / lid** — which bud is in an ear, how many are in the case,
  and whether the case lid is open (layout verified on real AirPods Pro 2).
- 🔐 **Exact battery with the AirPods keys** — `decrypt_status()` decrypts the
  AES half of the advert (1 % battery, charging, connected host) and
  `resolve_rpa()` recognises *your* AirPods behind the rotating address.
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

With the per-AirPods keys (on a Mac: keychain item `MobileBluetooth`, account =
AirPods address, fields `MagicAccIRK` / `MagicAccEncKey`):

```python
from apple_ble import decrypt_status, parse_key, resolve_rpa

irk, enc = parse_key(irk_text), parse_key(enc_text)   # accepts "FE-47-…" or hex
if resolve_rpa(address, irk):                          # these are *your* AirPods
    st = decrypt_status(payload, enc, flipped=data.flipped)
    print(st.left_battery, st.right_battery, st.case_battery, st.host_suffix)
```

`parse_proximity_pairing` returns `None` for anything that isn't a complete
AirPods proximity-pairing advert, so it is safe to feed it every Apple advert you
see and keep the non-`None` results.

### API

| Symbol | Description |
|---|---|
| `parse_proximity_pairing(data)` | Parse `manufacturer_data[76]` bytes into `AirPodsData`, or `None` if it isn't AirPods. |
| `AirPodsData` | Frozen dataclass: `model`, `left_battery`, `right_battery`, `case_battery` (`int %` or `None`), `left_charging`, `right_charging`, `case_charging`, `model_id`, `flipped`, `left_in_ear`, `right_in_ear`, `pods_in_case`, `lid_open` (`None` when no bud in the case is visible), `color`. |
| `decrypt_status(data, enc_key, *, flipped)` | Decrypt bytes 11–26 → `DecryptedStatus` (exact `%`, charging, `host_suffix`), or `None` on a wrong key. |
| `resolve_rpa(address, irk)` | `True` if the random address was generated from this IRK (keychain byte order). |
| `parse_key(text)` | Parse a 16-byte key from `FE-47-…`, `fe:47:…` or plain hex. |
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
