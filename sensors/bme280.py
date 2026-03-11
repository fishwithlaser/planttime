import logging

log = logging.getLogger(__name__)


class Bme280Sensor:
    """BME280 environmental sensor (temperature, humidity, pressure) via I2C."""

    def __init__(self, i2c, address: int = 0x77):
        from adafruit_bme280 import basic as adafruit_bme280

        self.bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=address)

    def read(self) -> dict:
        """Read temperature, humidity, and pressure.

        Returns dict with keys: temperature, humidity, pressure
        """
        data = {
            "temperature": round(self.bme.temperature, 1),
            "humidity": round(self.bme.relative_humidity, 1),
            "pressure": round(self.bme.pressure, 1),
        }
        log.debug(
            "BME280 temp=%.1f°C humidity=%.1f%% pressure=%.1fhPa",
            data["temperature"], data["humidity"], data["pressure"],
        )
        return data
