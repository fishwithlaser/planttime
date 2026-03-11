import logging
import serial

log = logging.getLogger(__name__)

FRAME_HEADER = 0xFF
FRAME_LENGTH = 4


class WaterLevelSensor:
    """A02YYUW Waterproof Ultrasonic Distance Sensor (UART)."""

    def __init__(self, port: str, baud_rate: int, tank_height_mm: int):
        """
        Args:
            port: Serial port (e.g. /dev/serial0)
            baud_rate: Baud rate (typically 9600)
            tank_height_mm: Distance from sensor to bottom of empty tank in mm
        """
        self.tank_height_mm = tank_height_mm
        self.ser = serial.Serial(
            port=port,
            baudrate=baud_rate,
            timeout=1,
        )

    def read_distance_mm(self) -> int | None:
        """Read raw distance in mm from the ultrasonic sensor.

        Returns distance in mm, or None if no valid frame received.
        Frame format: [0xFF, DATA_H, DATA_L, CHECKSUM]
        """
        # Flush stale data
        self.ser.reset_input_buffer()

        # Read until we find a valid frame (up to 2x frame length of bytes)
        data = self.ser.read(FRAME_LENGTH * 2)
        if len(data) < FRAME_LENGTH:
            log.warning("Ultrasonic sensor: not enough data received")
            return None

        # Scan for frame header
        for i in range(len(data) - FRAME_LENGTH + 1):
            if data[i] == FRAME_HEADER:
                frame = data[i : i + FRAME_LENGTH]
                data_h = frame[1]
                data_l = frame[2]
                checksum = frame[3]

                # Verify checksum (low byte of sum)
                if (FRAME_HEADER + data_h + data_l) & 0xFF == checksum:
                    distance = (data_h << 8) + data_l
                    if 30 <= distance <= 4500:
                        log.debug("Ultrasonic distance=%d mm", distance)
                        return distance
                    else:
                        log.warning("Ultrasonic distance out of range: %d mm", distance)
                        return None

        log.warning("Ultrasonic sensor: no valid frame found")
        return None

    def read(self) -> float | None:
        """Read water level as mm from the bottom of the tank.

        Returns water level in mm, or None if reading failed.
        """
        distance = self.read_distance_mm()
        if distance is None:
            return None

        water_level = self.tank_height_mm - distance
        water_level = max(0, water_level)
        log.debug("Water level=%d mm (distance=%d, tank=%d)", water_level, distance, self.tank_height_mm)
        return float(water_level)

    def close(self):
        """Close the serial port."""
        if self.ser and self.ser.is_open:
            self.ser.close()
