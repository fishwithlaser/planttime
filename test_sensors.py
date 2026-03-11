#!/usr/bin/env python3
"""Quick test script to read all connected sensors."""

import board
import busio
import glob
import serial
import time

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_bme280 import basic as adafruit_bme280


def read_bme280(i2c):
    try:
        bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x77)
        print(f"  Temperature: {bme.temperature:.1f} °C")
        print(f"  Humidity:    {bme.relative_humidity:.1f} %")
        print(f"  Pressure:    {bme.pressure:.1f} hPa")
    except Exception as e:
        print(f"  FAILED: {e}")


def read_ads1115(i2c):
    try:
        adc = ADS.ADS1115(i2c)
        ph_chan = AnalogIn(adc, 0)
        ec_chan = AnalogIn(adc, 1)
        print(f"  pH  (A0): {ph_chan.voltage:.4f} V  (raw: {ph_chan.value})")
        print(f"  EC  (A1): {ec_chan.voltage:.4f} V  (raw: {ec_chan.value})")
    except Exception as e:
        print(f"  FAILED: {e}")


def read_ds18b20():
    try:
        devices = glob.glob("/sys/bus/w1/devices/28-*/w1_slave")
        if not devices:
            print("  No DS18B20 found")
            return
        with open(devices[0]) as f:
            lines = f.readlines()
        if "YES" not in lines[0]:
            print("  DS18B20 read error")
            return
        temp_str = lines[1].split("t=")[1].strip()
        temp_c = float(temp_str) / 1000.0
        print(f"  Water temp: {temp_c:.1f} °C")
    except Exception as e:
        print(f"  FAILED: {e}")


def read_a02yyuw():
    try:
        ser = serial.Serial("/dev/serial0", 9600, timeout=3)
        time.sleep(1)
        ser.reset_input_buffer()
        data = ser.read(20)
        ser.close()

        if len(data) == 0:
            print("  No data received (check wiring: TX -> Pi pin 10)")
            return

        for i in range(len(data) - 3):
            if data[i] == 0xFF:
                h, l, cs = data[i + 1], data[i + 2], data[i + 3]
                if (0xFF + h + l) & 0xFF == cs:
                    dist = (h << 8) + l
                    print(f"  Distance: {dist} mm")
                    return

        print(f"  No valid frame (got {len(data)} bytes: {data.hex()})")
    except Exception as e:
        print(f"  FAILED: {e}")


def main():
    i2c = busio.I2C(board.SCL, board.SDA)

    print("--- BME280 (temp/humidity/pressure) ---")
    read_bme280(i2c)

    print("--- ADS1115 (pH + EC voltage) ---")
    read_ads1115(i2c)

    print("--- DS18B20 (water temp) ---")
    read_ds18b20()

    print("--- A02YYUW (water level) ---")
    read_a02yyuw()


if __name__ == "__main__":
    main()
