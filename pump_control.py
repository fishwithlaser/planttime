#!/usr/bin/env python3
"""Control a single pump by name via the relay.

Usage:
    python pump_control.py <name> <on|off>
    python pump_control.py <name> <seconds>    # run for N seconds then stop

Names map to GPIO pins (config.yaml pumps section):
    nutrient_a -> GPIO 17 (K1)
    nutrient_b -> GPIO 27 (K2)
    ph_down    -> GPIO 22 (K3)
    ph_up      -> GPIO 23 (K4)

Relay is active LOW: LOW = ON, HIGH = OFF.
"""

import sys
import time

import RPi.GPIO as GPIO
import yaml

CONFIG_PATH = "/home/thomas/planttime/config.yaml"


def load_pumps():
    with open(CONFIG_PATH) as f:
        cfg = yaml.safe_load(f)
    return {name: p["gpio_pin"] for name, p in cfg["pumps"].items()}


def set_pump(pin: int, on: bool):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW if on else GPIO.HIGH)


def main():
    if len(sys.argv) != 3:
        print("Usage: python pump_control.py <name> <on|off|seconds>")
        sys.exit(1)

    name = sys.argv[1]
    action = sys.argv[2]
    pumps = load_pumps()

    if name not in pumps:
        print(f"Unknown pump '{name}'. Available: {', '.join(pumps)}")
        sys.exit(1)

    pin = pumps[name]

    if action == "on":
        set_pump(pin, True)
        print(f"{name} (GPIO {pin}) -> ON")
    elif action == "off":
        set_pump(pin, False)
        print(f"{name} (GPIO {pin}) -> OFF")
    else:
        try:
            duration = float(action)
        except ValueError:
            print("Action must be 'on', 'off', or number of seconds")
            sys.exit(1)

        print(f"{name} (GPIO {pin}) -> ON for {duration}s")
        set_pump(pin, True)
        try:
            time.sleep(duration)
        finally:
            set_pump(pin, False)
            print(f"{name} (GPIO {pin}) -> OFF")


if __name__ == "__main__":
    main()
