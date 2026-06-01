from apple_ble.models import AirPodsData


def test_airpods_data_holds_fields():
    data = AirPodsData(
        model="AirPods Pro",
        left_battery=90,
        right_battery=100,
        case_battery=None,
        left_charging=False,
        right_charging=True,
        case_charging=False,
    )
    assert data.model == "AirPods Pro"
    assert data.left_battery == 90
    assert data.case_battery is None
    assert data.right_charging is True


def test_airpods_data_is_frozen():
    data = AirPodsData(
        model="AirPods Pro",
        left_battery=None,
        right_battery=None,
        case_battery=None,
        left_charging=False,
        right_charging=False,
        case_charging=False,
    )
    try:
        data.model = "x"  # type: ignore[misc]
    except Exception as exc:  # frozen dataclass raises FrozenInstanceError
        assert "cannot assign" in str(exc).lower() or "frozen" in str(exc).lower()
    else:
        raise AssertionError("AirPodsData should be immutable")
