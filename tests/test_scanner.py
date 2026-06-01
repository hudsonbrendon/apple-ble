from apple_ble.scanner import advert_to_airpods


class _FakeAdvData:
    def __init__(self, manufacturer_data):
        self.manufacturer_data = manufacturer_data


def test_advert_to_airpods_parses_apple_data():
    hexstr = "0719070e2070a93601000045121212"
    hexstr = hexstr + "0" * (54 - len(hexstr))
    adv = _FakeAdvData({76: bytes.fromhex(hexstr)})
    data = advert_to_airpods(adv)
    assert data is not None
    assert data.model == "AirPods Pro"


def test_advert_to_airpods_ignores_non_apple():
    adv = _FakeAdvData({6: b"\x01\x02"})  # Microsoft, not Apple
    assert advert_to_airpods(adv) is None
