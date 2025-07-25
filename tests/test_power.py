import pytest


def test_init(mocker, multiple_devices):
    from krux.power import PowerManager

    manager = PowerManager()

    assert isinstance(manager, PowerManager)


def test_pmu(mocker, multiple_devices):
    from krux.power import PowerManager
    import board

    manager = PowerManager()

    if board.config["type"] in ("dock", "yahboom", "wonder_mv"):
        assert manager.pmu is None
        manager.has_battery() is False
    else:
        assert manager.pmu is not None
        manager.has_battery() is True


def test_charge_remaining(mocker, multiple_devices):
    from krux.power import PowerManager
    import board

    manager = PowerManager()

    if manager.pmu is not None:
        manager.pmu.get_battery_voltage = mocker.MagicMock(return_value=4000)

    if board.config["type"] == "amigo":
        assert manager.battery_charge_remaining() == 0.9
    elif board.config["type"] in ("m5stickv", "cube"):
        assert round(manager.battery_charge_remaining(), 2) == 0.75


def test_charge_has_no_battery(mocker, multiple_devices):
    from krux.power import PowerManager
    import board

    manager = PowerManager()

    # M5StickV, Amigo and Cube have battery
    # and calls get_battery_voltage
    if board.config["type"] in ("amigo", "m5stickv", "cube"):
        manager.pmu.get_battery_voltage = mocker.MagicMock(return_value=0)
        assert not manager.has_battery()
        manager.pmu.get_battery_voltage.assert_called_once()

    # Dock, Yahboom and WonderMV do not have battery
    # it just raises an exception and returns False
    else:
        with pytest.raises(AttributeError) as exc_info:
            assert not manager.has_battery()
            assert (
                str(exc_info.exception)
                == "get_battery_voltage() not implemented for this board"
            )


def test_shutdown(mocker, m5stickv):
    mocker.patch("sys.exit")
    import krux
    from krux.power import PowerManager

    manager = PowerManager()

    manager.shutdown()

    krux.power.machine.reset.assert_called()
    krux.power.sys.exit.assert_called()


def test_shutdown_with_amigo(mocker, amigo):
    mocker.patch("sys.exit")
    import krux
    from krux.power import PowerManager

    manager = PowerManager()

    manager.shutdown()

    krux.power.machine.reset.assert_called()
    krux.power.sys.exit.assert_called()


def test_shutdown_without_pmu(mocker, m5stickv):
    mocker.patch("sys.exit")
    import krux
    import sys

    if "pmu" in sys.modules:
        del sys.modules["pmu"]
    from krux.power import PowerManager

    manager = PowerManager()

    manager.shutdown()

    krux.power.machine.reset.assert_called()
    krux.power.sys.exit.assert_called()


def test_reboot(mocker, m5stickv):
    mocker.patch("sys.exit")
    import krux
    from krux.power import PowerManager

    manager = PowerManager()

    manager.reboot()

    krux.power.machine.reset.assert_called()
    krux.power.sys.exit.assert_called()


def test_reboot_with_amigo(mocker, amigo):
    mocker.patch("sys.exit")
    import krux
    from krux.power import PowerManager

    manager = PowerManager()

    manager.reboot()

    krux.power.machine.reset.assert_called()
    krux.power.sys.exit.assert_called()


def test_reboot_without_pmu(mocker, m5stickv):
    mocker.patch("sys.exit")
    import krux
    import sys

    if "pmu" in sys.modules:
        del sys.modules["pmu"]
    from krux.power import PowerManager

    manager = PowerManager()

    manager.reboot()

    krux.power.machine.reset.assert_called()
    krux.power.sys.exit.assert_called()


def test_battery_charge_remaining_with_charging(mocker, multiple_devices):
    from krux.power import PowerManager
    import board

    manager = PowerManager()

    if manager.pmu is not None:
        manager.pmu.get_battery_voltage.return_value = 4000
        manager.pmu.charging.return_value = True

        charge = manager.battery_charge_remaining()

        assert charge <= 0.9


@pytest.mark.parametrize(
    "voltage,expected",
    [
        (3000, 0.0),
        (3600, 0.5),
        (4200, 1.0),
    ],
)
def test_battery_charge_remaining_formula(mocker, multiple_devices, voltage, expected):
    from krux.power import PowerManager
    import board

    manager = PowerManager()

    if manager.pmu is not None:
        manager.pmu.get_battery_voltage.return_value = voltage
        manager.pmu.charging.return_value = False

        charge = manager.battery_charge_remaining()

        if board.config["type"] in ("amigo", "m5stickv", "cube"):
            assert 0.0 <= charge <= 1.0
        else:
            assert charge == expected


def test_usb_connected(mocker, multiple_devices):
    from krux.power import PowerManager

    manager = PowerManager()

    if manager.pmu is not None:
        manager.pmu.usb_connected.return_value = True
        assert manager.usb_connected() is True
        manager.pmu.usb_connected.assert_called_once()

        manager.pmu.usb_connected.reset_mock()
        manager.pmu.usb_connected.return_value = False
        assert manager.usb_connected() is False
        manager.pmu.usb_connected.assert_called_once()
