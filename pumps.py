import logging

log = logging.getLogger(__name__)


class Pump:
    """Peristaltic pump controlled via GPIO relay (stub implementation)."""

    def __init__(self, name: str, gpio_pin: int):
        self.name = name
        self.gpio_pin = gpio_pin

    def on(self):
        """Turn pump on."""
        log.info("[STUB] Pump '%s' ON (GPIO %d)", self.name, self.gpio_pin)

    def off(self):
        """Turn pump off."""
        log.info("[STUB] Pump '%s' OFF (GPIO %d)", self.name, self.gpio_pin)

    def dose(self, ml: float, flow_rate_ml_per_sec: float = 1.0):
        """Dose a specific amount (stub — logs only)."""
        duration = ml / flow_rate_ml_per_sec
        log.info(
            "[STUB] Pump '%s' dosing %.1f ml (%.1fs at %.1f ml/s)",
            self.name, ml, duration, flow_rate_ml_per_sec,
        )
