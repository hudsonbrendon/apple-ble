from apple_ble import const


def test_apple_manufacturer_id_is_76():
    assert const.APPLE_MANUFACTURER_ID == 76


def test_proximity_pairing_type_is_0x07():
    assert const.MSG_TYPE_PROXIMITY_PAIRING == 0x07


def test_model_map_covers_known_airpods():
    assert const.MODEL_BY_CHAR["e"] == "AirPods Pro"
    assert const.MODEL_BY_CHAR["a"] == "AirPods Max"
    assert const.MODEL_BY_CHAR["2"] == "AirPods (1st gen)"


def test_nibble_indices():
    assert const.IDX_MODEL == 7
    assert const.IDX_FLIP == 10
    assert const.IDX_LEFT_NOFLIP == 13
    assert const.IDX_RIGHT_NOFLIP == 12
    assert const.IDX_CHARGE == 14
    assert const.IDX_CASE == 15
