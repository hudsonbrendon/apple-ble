"""AirPods proximity-pairing keys: RPA resolution (IRK) and payload decryption (EncKey).

Both keys are per-AirPods 16-byte values that Apple shares with every paired
host. On a Mac they live in the login keychain item ``MobileBluetooth`` /
``<AirPods classic address>`` (XML plist, ``MagicAccIRK`` / ``MagicAccEncKey``,
written as ``"FE-47-…"``). Use them exactly as stored there; the byte-order
quirks below are handled here.
"""

from __future__ import annotations

from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from .parser import ENCRYPTED_SLICE


def parse_key(text: str) -> bytes:
    """Accept ``FE-47-…``, ``fe:47:…``, ``fe 47 …`` or plain hex; return 16 bytes."""
    raw = bytes.fromhex("".join(c for c in text if c not in "-: \t").removeprefix("0x"))
    if len(raw) != 16:
        raise ValueError("key must be 16 bytes")
    return raw


def _aes_ecb(key: bytes, block: bytes, *, decrypt: bool = False) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.ECB())  # noqa: S305 - Apple's format
    ctx = cipher.decryptor() if decrypt else cipher.encryptor()
    return ctx.update(block) + ctx.finalize()


def resolve_rpa(address: str, irk: bytes) -> bool:
    """True if the random BLE ``address`` (``AA:BB:…``) was generated from ``irk``.

    Bluetooth Core ah(): hash = AES(IRK, 0^13 || prand)[-3:]. The keychain
    stores the IRK little-endian, so it is reversed before use.
    """
    addr = bytes.fromhex(address.replace(":", ""))
    if len(addr) != 6 or addr[0] >> 6 != 0b01:  # resolvable private address only
        return False
    return _aes_ecb(irk[::-1], bytes(13) + addr[:3])[-3:] == addr[3:]


@dataclass(frozen=True, slots=True)
class DecryptedStatus:
    """Fields from the AES-encrypted half of a proximity-pairing advert.

    Battery values are exact percentages (0-100) or None (0xFF / not present).
    ``host_suffix`` is the last 3 bytes of the BT address of the host the
    AirPods are connected to (e.g. ``"BC:CF:27"``), or None when not connected.
    """

    left_battery: int | None
    right_battery: int | None
    case_battery: int | None
    left_charging: bool
    right_charging: bool
    case_charging: bool
    host_suffix: str | None
    raw: bytes


def _pct(b: int) -> tuple[int | None, bool]:
    # ponytail: bit7 = charging, low 7 bits = percent; 0x7F/0xFF = absent.
    value = b & 0x7F
    return (value if value <= 100 else None), bool(b & 0x80) and value <= 100


def decrypt_status(data: bytes, enc_key: bytes, *, flipped: bool) -> DecryptedStatus | None:
    """Decrypt bytes 11..26 of ``manufacturer_data[76]`` with the AirPods EncKey.

    ``flipped`` must come from the clear part (``AirPodsData.flipped``): it
    swaps which byte is the left pod, exactly like the battery nibbles.
    Returns None when the payload is too short or the key is wrong.
    """
    block = data[ENCRYPTED_SLICE]
    if len(block) != 16:
        return None
    dec = _aes_ecb(enc_key, block, decrypt=True)
    # A wrong key yields noise; the three always-zero bytes catch that.
    if dec[7:10] != b"\x00\x00\x00":
        return None
    first, second = _pct(dec[1]), _pct(dec[2])
    (left, lc), (right, rc) = (second, first) if flipped else (first, second)
    case, cc = _pct(dec[3])
    host = dec[4:7]
    return DecryptedStatus(
        left_battery=left,
        right_battery=right,
        case_battery=case,
        left_charging=lc,
        right_charging=rc,
        case_charging=cc,
        host_suffix=None if host in (b"\x00\x00\x00", b"\xff\xff\xff") else host.hex(":").upper(),
        raw=dec,
    )
