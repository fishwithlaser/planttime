import glob
import logging

log = logging.getLogger(__name__)

DEVICE_PATH = "/sys/bus/w1/devices/28-*/w1_slave"


class Ds18b20Sensor:
    """DS18B20 waterproof temperature sensor (one-wire)."""

    def __init__(self):
        devices = glob.glob(DEVICE_PATH)
        if not devices:
            raise RuntimeError("No DS18B20 sensor found. Check wiring and one-wire overlay.")
        self.device_path = devices[0]
        log.info("DS18B20 found at %s", self.device_path)

    def read(self) -> float | None:
        """Read water temperature in °C."""
        with open(self.device_path) as f:
            lines = f.readlines()

        if "YES" not in lines[0]:
            log.warning("DS18B20 CRC check failed")
            return None

        temp_str = lines[1].split("t=")[1].strip()
        temp_c = round(float(temp_str) / 1000.0, 1)
        log.debug("DS18B20 water_temp=%.1f°C", temp_c)
        return temp_c
