from apple_ble.parser import decode_battery_nibble
from apple_ble.parser import parse_proximity_pairing


def test_full_battery():
    assert decode_battery_nibble(10) == 100


def test_mid_battery():
    assert decode_battery_nibble(9) == 90
    assert decode_battery_nibble(5) == 50


def test_empty_battery():
    assert decode_battery_nibble(0) == 0


def test_unknown_nibble_is_none():
    assert decode_battery_nibble(15) is None
    assert decode_battery_nibble(11) is None


# A 27-byte (54 hex char) proximity-pairing advert.
# Layout (nibble indices): model@7='e' (AirPods Pro), flip@10='7',
# right@12='a'(=10 ->100%), left@13='9'(->90%), charge@14='3'
# (bit0 set, bit1 set, bit2 clear), case@15='6'(->60%).


def _sample_bytes() -> bytes:
    # Nibble layout: type@0-1='07', model@7='e'(AirPods Pro), flip@10='7'(not flipped),
    # right@12='a'(->100%), left@13='9'(->90%), charge@14='3'(L+R charging, case not),
    # case@15='6'(->60%).
    hexstr = "0719070e2070a93601000045121212"
    hexstr = hexstr + "0" * (54 - len(hexstr))  # right-pad nibbles to 54 chars
    return bytes.fromhex(hexstr)


def test_parses_model_and_batteries():
    data = parse_proximity_pairing(_sample_bytes())
    assert data is not None
    assert data.model == "AirPods Pro"
    # flip nibble @10 = '7'; int('7',16)&0x02 == 2 (nonzero) -> NOT flipped
    # not flipped: left=idx13, right=idx12
    assert data.right_battery == 100   # idx12 = 'a' = 10 -> 100
    assert data.left_battery == 90     # idx13 = '9' -> 90


def test_parses_charging_flags():
    data = parse_proximity_pairing(_sample_bytes())
    assert data is not None
    # charge nibble @14 = '3' = 0b0011, not flipped:
    assert data.left_charging is True    # bit0
    assert data.right_charging is True   # bit1
    assert data.case_charging is False   # bit2


def test_case_battery():
    data = parse_proximity_pairing(_sample_bytes())
    assert data is not None
    assert data.case_battery == 60   # idx15 = '6' -> 60


def test_rejects_non_proximity_pairing():
    # Type byte 0x10 (not 0x07) -> not a proximity pairing message.
    assert parse_proximity_pairing(bytes.fromhex("10" + "0" * 52)) is None


def test_rejects_wrong_length():
    assert parse_proximity_pairing(bytes.fromhex("0719")) is None


def test_rejects_empty():
    assert parse_proximity_pairing(b"") is None


def test_public_api_exports():
    import apple_ble

    assert hasattr(apple_ble, "parse_proximity_pairing")
    assert hasattr(apple_ble, "AirPodsData")
    assert apple_ble.APPLE_MANUFACTURER_ID == 76


def _make_hexstr(charge_nibble: str, left_nibble: str = "9", right_nibble: str = "a",
                  flip_nibble: str = "7") -> bytes:
    """Build a NOT-flipped (flip_nibble='7') advert with custom charge/battery nibbles.

    Hex layout (indices):
      0-1: type '07'
      2-5: '1907'  (payload length + subtype)
      6-7: '0e'    model byte (idx6='0', idx7='e' -> AirPods Pro)
      8-9: '20'
      10:  flip_nibble  (default '7' = 0b0111, bit1 set -> NOT flipped)
      11:  '0'
      12:  right_nibble (IDX_RIGHT_NOFLIP)
      13:  left_nibble  (IDX_LEFT_NOFLIP)
      14:  charge_nibble
      15:  '6'  case battery -> 60%
      16+: zeros padded to 54 chars
    """
    s = "071907" + "0e" + "20" + flip_nibble + "0" + right_nibble + left_nibble + charge_nibble + "6"
    s = s + "0" * (54 - len(s))
    return bytes.fromhex(s)


# --- Charging-bit attribution tests (NOT flipped, flip nibble = '7') ---

def test_charging_only_left():
    # charge nibble '1' = 0b0001; not flipped: left_bit=0b0001, right_bit=0b0010
    # -> left_charging True, right_charging False, case_charging False
    data = parse_proximity_pairing(_make_hexstr(charge_nibble="1", left_nibble="5", right_nibble="8"))
    assert data is not None
    assert data.left_charging is True
    assert data.right_charging is False
    assert data.case_charging is False
    # Confirm batteries are correctly read (distinct nibbles, not-flipped)
    assert data.left_battery == 50   # idx13='5'
    assert data.right_battery == 80  # idx12='8'


def test_charging_only_right():
    # charge nibble '2' = 0b0010; not flipped: left_bit=0b0001, right_bit=0b0010
    # -> left_charging False, right_charging True
    data = parse_proximity_pairing(_make_hexstr(charge_nibble="2", left_nibble="3", right_nibble="7"))
    assert data is not None
    assert data.left_charging is False
    assert data.right_charging is True


def test_charging_only_case():
    # charge nibble '4' = 0b0100; case_bit=0b0100
    # -> case_charging True, left/right False
    data = parse_proximity_pairing(_make_hexstr(charge_nibble="4", left_nibble="2", right_nibble="6"))
    assert data is not None
    assert data.left_charging is False
    assert data.right_charging is False
    assert data.case_charging is True


# --- Flipped-orientation test ---

def test_flipped_swaps_indices_and_charging_bits():
    # flip_nibble '4' = 0b0100; bit1 clear (0x02 & 0x04 == 0) -> FLIPPED
    # In flipped mode: left reads IDX_RIGHT_NOFLIP (idx12), right reads IDX_LEFT_NOFLIP (idx13)
    # idx12='2' -> 20%, idx13='8' -> 80%
    # charge nibble '1' = 0b0001; flipped: left_bit=0b0010, right_bit=0b0001
    # -> bit0 set hits right_bit -> right_charging True, left_charging False
    data = parse_proximity_pairing(_make_hexstr(
        charge_nibble="1", left_nibble="8", right_nibble="2", flip_nibble="4"
    ))
    assert data is not None
    # Index swap: left reads idx12='2'->20, right reads idx13='8'->80
    assert data.left_battery == 20
    assert data.right_battery == 80
    # Bit swap: charge bit 0b0001 -> right_charging (not left) when flipped
    assert data.left_charging is False
    assert data.right_charging is True
