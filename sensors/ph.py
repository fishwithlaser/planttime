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
        import adafruit_ads1x15.analog_in as AnalogIn
        import adafruit_ads1x15.ads1115 as ADS

        channels = [ADS.P0, ADS.P1, ADS.P2, ADS.P3]
        self.analog_in = AnalogIn.AnalogIn(adc, channels[channel])
        self.slope = slope
        self.intercept = intercept

    def read_voltage(self) -> float:
        """Read raw voltage from the pH probe."""
        return self.analog_in.voltage

    def read(self) -> float:
        """Read pH value (0-14) using calibration coefficients."""
        voltage = self.read_voltage()
        ph = self.slope * voltage + self.intercept
        ph = max(0.0, min(14.0, ph))
        log.debug("pH voltage=%.4f pH=%.2f", voltage, ph)
        return round(ph, 2)
