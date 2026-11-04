import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from apple_ble import decrypt_status, parse_key, parse_proximity_pairing, resolve_rpa

# Clear half captured from a real AirPods Pro 2 (both buds in ears, case away).
CLEAR = bytes.fromhex("07190114202b888f100009")


def _aes(key: bytes, block: bytes) -> bytes:
    e = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
    return e.update(block) + e.finalize()


def _advert(enc_key: bytes, plain: bytes) -> bytes:
    return CLEAR + _aes(enc_key, plain)


def test_parse_key_formats():
    raw = bytes(range(16))
    for text in (raw.hex(), raw.hex("-").upper(), raw.hex(":"), "0x" + raw.hex()):
        assert parse_key(text) == raw


def test_parse_key_rejects_wrong_length():
    try:
        parse_key("00-11")
    except ValueError:
        return
    raise AssertionError("short key accepted")


def test_resolve_rpa_roundtrip():
    irk_le = os.urandom(16)  # as stored in the keychain (little-endian)
    prand = bytes([0x40 | 0x2F, 0xAF, 0x23])  # top bits 01 = resolvable
    addr = prand + _aes(irk_le[::-1], bytes(13) + prand)[-3:]
    assert resolve_rpa(addr.hex(":"), irk_le)
    assert not resolve_rpa(addr.hex(":"), os.urandom(16))
    assert not resolve_rpa("C0:" + addr.hex(":")[3:], irk_le)  # static random


def test_decrypt_real_layout():
    key = os.urandom(16)
    # Layout seen on hardware: flags, L%, R%, case%, host[3], 000000, 2B, 4B nonce
    plain = bytes.fromhex("09" "54" "56" "ff" "bccf27" "000000" "261c" "fb80b07a")
    st = decrypt_status(_advert(key, plain), key, flipped=False)
    assert st is not None
    assert (st.left_battery, st.right_battery, st.case_battery) == (84, 86, None)
    assert not (st.left_charging or st.right_charging or st.case_charging)
    assert st.host_suffix == "BC:CF:27"


def test_decrypt_flipped_and_charging():
    key = os.urandom(16)
    plain = bytes.fromhex("09" "d4" "32" "e3" "000000" "000000" "261c" "00000000")
    st = decrypt_status(_advert(key, plain), key, flipped=True)
    assert st is not None
    assert (st.left_battery, st.right_battery, st.case_battery) == (50, 84, 99)
    assert (st.left_charging, st.right_charging, st.case_charging) == (False, True, True)
    assert st.host_suffix is None


def test_decrypt_wrong_key_is_none():
    plain = bytes.fromhex("09545 6ffbccf27000000261cfb80b07a".replace(" ", ""))
    assert decrypt_status(_advert(os.urandom(16), plain), os.urandom(16), flipped=False) is None


def test_clear_part_real_capture():
    d = parse_proximity_pairing(CLEAR + bytes(16))
    assert d is not None
    assert d.model == "AirPods Pro 2" and d.model_id == 0x2014
    assert not d.flipped
    assert d.left_in_ear and d.right_in_ear
    assert d.pods_in_case == 0
    assert (d.left_battery, d.right_battery, d.case_battery) == (80, 80, None)
    assert d.color == 0


def _status(clear_hex: str):
    return parse_proximity_pairing(bytes.fromhex("0719011420" + clear_hex + "04") + bytes(16))


def test_hardware_states():
    # (status..color, left_in_ear, right_in_ear, pods_in_case, lid_open) captured 04/11
    cases = [
        ("0b878f1100", True, True, 0, None),     # both in ears (right advertising)
        ("03878f1100", False, True, 0, None),    # left in hand
        ("73789f5100", False, True, 1, True),    # left in open case (left adv.)
        ("1387a71100", False, True, 1, True),    # same, right advertising
        ("7378975900", False, True, 1, False),   # lid closed
        ("02f78f1100", False, True, 0, None),    # right only sees itself
        ("1587b75200", False, False, 2, True),   # both in open case
    ]
    for clear, le, re_, n, lid in cases:
        d = _status(clear)
        assert (d.left_in_ear, d.right_in_ear, d.pods_in_case, d.lid_open) == (le, re_, n, lid), clear


def test_hardware_charging():
    d = _status("7588f75200")  # both buds + case charging, left advertising
    assert (d.left_charging, d.right_charging, d.case_charging) == (True, True, True)
    assert (d.left_battery, d.right_battery, d.case_battery) == (80, 80, 70)
    d = _status("1387a71100")  # right advertising (flipped), left charging in case
    assert (d.left_charging, d.right_charging, d.case_charging) == (True, False, False)
    assert (d.left_battery, d.right_battery) == (80, 70)
