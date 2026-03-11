#!/usr/bin/env python3
"""Interactive calibration tool for pH and EC sensors.

Reads raw voltages and computes calibration coefficients,
then saves them to config.yaml.
"""

import statistics
import time

import yaml

CONFIG_PATH = "config.yaml"
SAMPLES = 10
SAMPLE_DELAY = 0.5  # seconds between samples


def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False)


def init_adc(cfg):
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS

    i2c = busio.I2C(board.SCL, board.SDA)
    adc = ADS.ADS1115(i2c, address=cfg["adc"]["i2c_address"])
    adc.gain = cfg["adc"]["gain"]
    return adc


def read_avg_voltage(adc, channel: int) -> float:
    """Read average voltage over multiple samples."""
    from adafruit_ads1x15.analog_in import AnalogIn

    analog_in = AnalogIn(adc, channel)

    readings = []
    for i in range(SAMPLES):
        readings.append(analog_in.voltage)
        if i < SAMPLES - 1:
            time.sleep(SAMPLE_DELAY)

    avg = statistics.mean(readings)
    std = statistics.stdev(readings) if len(readings) > 1 else 0
    print(f"  Voltage: {avg:.4f}V (std: {std:.4f}, n={SAMPLES})")
    return avg


def calibrate_ph(adc, cfg):
    """Two-point pH calibration using pH 7.0 and pH 4.0 buffers."""
    channel = cfg["sensors"]["ph"]["adc_channel"]

    print("\n=== pH Calibration ===")
    print("You'll need pH 7.0 and pH 4.0 buffer solutions.\n")

    # Point 1: pH 7.0
    input("Place the pH probe in pH 7.0 buffer and press Enter...")
    print(f"Reading {SAMPLES} samples...")
    v7 = read_avg_voltage(adc, channel)

    # Point 2: pH 4.0
    input("\nPlace the pH probe in pH 4.0 buffer and press Enter...")
    print(f"Reading {SAMPLES} samples...")
    v4 = read_avg_voltage(adc, channel)

    # Linear calibration: pH = slope * voltage + intercept
    # Two points: (v7, 7.0) and (v4, 4.0)
    if abs(v7 - v4) < 0.01:
        print("ERROR: Voltages too similar. Check probe connection.")
        return

    slope = (7.0 - 4.0) / (v7 - v4)
    intercept = 7.0 - slope * v7

    print(f"\nCalibration results:")
    print(f"  Slope:     {slope:.4f}")
    print(f"  Intercept: {intercept:.4f}")
    print(f"  Check: V={v7:.4f} -> pH {slope * v7 + intercept:.2f} (expect 7.00)")
    print(f"  Check: V={v4:.4f} -> pH {slope * v4 + intercept:.2f} (expect 4.00)")

    cfg["sensors"]["ph"]["calibration"]["slope"] = round(slope, 4)
    cfg["sensors"]["ph"]["calibration"]["intercept"] = round(intercept, 4)
    save_config(cfg)
    print("Saved to config.yaml")


def calibrate_ec(adc, cfg):
    """EC calibration using a known EC solution."""
    channel = cfg["sensors"]["ec"]["adc_channel"]

    print("\n=== EC Calibration ===")
    print("You'll need an EC calibration solution (e.g. 1.413 mS/cm).\n")

    # Read in dry air (zero point)
    input("Leave the EC probe in air (dry) and press Enter...")
    print(f"Reading {SAMPLES} samples...")
    v_dry = read_avg_voltage(adc, channel)

    # Read in calibration solution
    known_ec = float(input("\nEnter the EC value of your calibration solution (mS/cm): "))
    input(f"Place the EC probe in the {known_ec} mS/cm solution and press Enter...")
    print(f"Reading {SAMPLES} samples...")
    v_cal = read_avg_voltage(adc, channel)

    if abs(v_cal - v_dry) < 0.01:
        print("ERROR: Voltages too similar. Check probe connection.")
        return

    # Linear: EC = k * voltage + offset
    # In air: EC = 0, so offset = -k * v_dry
    # In solution: known_ec = k * v_cal + offset
    k = known_ec / (v_cal - v_dry)
    offset = -k * v_dry

    print(f"\nCalibration results:")
    print(f"  K:      {k:.4f}")
    print(f"  Offset: {offset:.4f}")
    print(f"  Check: V={v_dry:.4f} -> EC {k * v_dry + offset:.2f} mS/cm (expect ~0.00)")
    print(f"  Check: V={v_cal:.4f} -> EC {k * v_cal + offset:.2f} mS/cm (expect {known_ec:.2f})")

    cfg["sensors"]["ec"]["calibration"]["k"] = round(k, 4)
    cfg["sensors"]["ec"]["calibration"]["offset"] = round(offset, 4)
    save_config(cfg)
    print("Saved to config.yaml")


def main():
    cfg = load_config()
    adc = init_adc(cfg)

    print("PlantTime Sensor Calibration")
    print("1) Calibrate pH")
    print("2) Calibrate EC")
    print("3) Both")

    choice = input("\nSelect (1/2/3): ").strip()

    if choice in ("1", "3"):
        calibrate_ph(adc, cfg)
    if choice in ("2", "3"):
        # Reload config in case pH cal just saved
        if choice == "3":
            cfg = load_config()
        calibrate_ec(adc, cfg)

    print("\nDone!")


if __name__ == "__main__":
    main()
