import logging

log = logging.getLogger(__name__)


class EcSensor:
    """DFRobot Lab Grade Analog EC Sensor (K=1) via ADS1115."""

    def __init__(self, adc, channel: int, k: float, offset: float, temp_c: float = 25.0):
        """
        Args:
            adc: ADS1115 instance
            channel: ADS1115 channel number (0-3)
            k: Calibration coefficient
            offset: Calibration offset
            temp_c: Temperature for compensation (default 25°C)
        """
        import adafruit_ads1x15.analog_in as AnalogIn
        import adafruit_ads1x15.ads1115 as ADS

        channels = [ADS.P0, ADS.P1, ADS.P2, ADS.P3]
        self.analog_in = AnalogIn.AnalogIn(adc, channels[channel])
        self.k = k
        self.offset = offset
        self.temp_c = temp_c

    def read_voltage(self) -> float:
        """Read raw voltage from the EC probe."""
        return self.analog_in.voltage

    def read(self) -> float:
        """Read EC value in mS/cm with temperature compensation."""
        voltage = self.read_voltage()

        # Temperature compensation coefficient (referenced to 25°C)
        temp_coeff = 1.0 + 0.0185 * (self.temp_c - 25.0)

        # Convert voltage to EC using calibration
        ec = (voltage * self.k + self.offset) / temp_coeff

        ec = max(0.0, ec)
        log.debug("EC voltage=%.4f ec=%.2f mS/cm (temp=%.1f°C)", voltage, ec, self.temp_c)
        return round(ec, 2)
