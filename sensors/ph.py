import logging

log = logging.getLogger(__name__)


class PhSensor:
    """DFRobot Gravity Analog pH Sensor (SEN0161) via ADS1115."""

    def __init__(self, adc, channel: int, slope: float, intercept: float):
        """
        Args:
            adc: ADS1115 analog input (adafruit AnalogIn instance)
            channel: ADS1115 channel number (0-3)
            slope: Calibration slope (voltage -> pH)
            intercept: Calibration intercept
        """
        from adafruit_ads1x15.analog_in import AnalogIn

        self.analog_in = AnalogIn(adc, channel)
        self.slope = slope
        self.intercept = intercept

    def read_voltage(self) -> float:
        """Read raw voltage from the pH probe.

        Computes voltage manually from the raw ADC value to avoid
        a library bug where .voltage can return stale data when
        reading multiple channels in rapid succession.
        """
        raw = self.analog_in.value
        return raw * 4.096 / 32767

    def read(self) -> float:
        """Read pH value (0-14) using calibration coefficients."""
        voltage = self.read_voltage()
        ph = self.slope * voltage + self.intercept
        ph = max(0.0, min(14.0, ph))
        log.debug("pH voltage=%.4f pH=%.2f", voltage, ph)
        return round(ph, 2)
