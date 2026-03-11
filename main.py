#!/usr/bin/env python3
"""PlantTime — Hydroponic sensor monitor.

Reads pH, EC, and water level sensors and stores readings in InfluxDB.
"""

import logging
import signal
import sys
import time

import yaml

from database import Database
from sensors.ph import PhSensor
from sensors.ec import EcSensor
from sensors.water_level import WaterLevelSensor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

running = True


def shutdown(signum, frame):
    global running
    log.info("Shutting down...")
    running = False


def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def init_adc(cfg: dict):
    """Initialize ADS1115 ADC over I2C."""
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS

    i2c = busio.I2C(board.SCL, board.SDA)
    adc = ADS.ADS1115(i2c, address=cfg["adc"]["i2c_address"])
    adc.gain = cfg["adc"]["gain"]
    return adc


def main():
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    cfg = load_config()
    log.info("PlantTime starting")

    # Initialize ADC
    adc = init_adc(cfg)

    # Initialize sensors
    ph_cfg = cfg["sensors"]["ph"]
    ph_sensor = PhSensor(
        adc=adc,
        channel=ph_cfg["adc_channel"],
        slope=ph_cfg["calibration"]["slope"],
        intercept=ph_cfg["calibration"]["intercept"],
    )

    ec_cfg = cfg["sensors"]["ec"]
    ec_sensor = EcSensor(
        adc=adc,
        channel=ec_cfg["adc_channel"],
        k=ec_cfg["calibration"]["k"],
        offset=ec_cfg["calibration"]["offset"],
    )

    wl_cfg = cfg["sensors"]["water_level"]
    wl_sensor = WaterLevelSensor(
        port=wl_cfg["serial_port"],
        baud_rate=wl_cfg["baud_rate"],
        tank_height_mm=wl_cfg["tank_height_mm"],
    )

    # Initialize database
    db_cfg = cfg["influxdb"]
    db = Database(
        url=db_cfg["url"],
        token=db_cfg["token"],
        org=db_cfg["org"],
        bucket=db_cfg["bucket"],
    )

    interval = cfg["read_interval_seconds"]
    log.info("Reading sensors every %ds", interval)

    try:
        while running:
            # Read sensors
            ph = ph_sensor.read()
            ec = ec_sensor.read()
            water_level = wl_sensor.read()

            # Log to console
            wl_str = f"{water_level:.0f} mm" if water_level is not None else "N/A"
            log.info("pH=%.2f  EC=%.2f mS/cm  Water=%s", ph, ec, wl_str)

            # Write to InfluxDB
            db.write_reading("ph", ph)
            db.write_reading("ec", ec)
            if water_level is not None:
                db.write_reading("water_level", water_level)

            time.sleep(interval)
    finally:
        wl_sensor.close()
        db.close()
        log.info("PlantTime stopped")


if __name__ == "__main__":
    main()
