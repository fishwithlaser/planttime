#!/usr/bin/env python3
"""Control a WiZ smart plug by MAC address (stable across IP changes).

Usage:
    python plug_control.py light on
    python plug_control.py pump off
    python plug_control.py <mac> on
"""

import asyncio
import os
import sys

import yaml
from pywizlight import wizlight
from pywizlight.discovery import discover_lights

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")

BROADCAST_SPACE = "192.168.18.255"

# Friendly names → MAC addresses
PLUGS = {
    "light": "cc4085b0d55c",
    "pump":  "cc4085b10db8",
}


async def find_plug_by_mac(mac: str) -> wizlight | None:
    """Discover plugs on the network and return the one with matching MAC."""
    mac = mac.lower().replace(":", "")
    bulbs = await discover_lights(broadcast_space=BROADCAST_SPACE)
    for bulb in bulbs:
        if bulb.mac.lower().replace(":", "") == mac:
            return bulb
    return None


async def main():
    if len(sys.argv) != 3 or sys.argv[2] not in ("on", "off"):
        print("Usage: python plug_control.py <light|pump|MAC> <on|off>")
        sys.exit(1)

    name_or_mac = sys.argv[1].lower()
    action = sys.argv[2]

    mac = PLUGS.get(name_or_mac, name_or_mac)
    plug = await find_plug_by_mac(mac)

    if plug is None:
        print(f"ERROR: plug with MAC {mac} not found on network")
        sys.exit(1)

    if action == "on":
        await plug.turn_on()
    else:
        await plug.turn_off()

    print(f"{name_or_mac} ({plug.ip}) -> {action.upper()}")

    # Log state to InfluxDB so dashboards can overlay pump/light activity
    try:
        log_state(name_or_mac, action)
    except Exception as e:
        print(f"(influxdb logging skipped: {e})")


def log_state(name: str, action: str):
    """Write plug state change to InfluxDB."""
    from influxdb_client import InfluxDBClient, Point, WritePrecision
    from influxdb_client.client.write_api import SYNCHRONOUS
    from datetime import datetime, timezone

    with open(CONFIG_PATH) as f:
        cfg = yaml.safe_load(f)

    db_cfg = cfg["influxdb"]
    value = 1 if action == "on" else 0

    with InfluxDBClient(url=db_cfg["url"], token=db_cfg["token"], org=db_cfg["org"]) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        point = (
            Point("plug_state")
            .tag("plug", name)
            .field("state", value)
            .time(datetime.now(timezone.utc), WritePrecision.S)
        )
        write_api.write(bucket=db_cfg["bucket"], org=db_cfg["org"], record=point)


if __name__ == "__main__":
    asyncio.run(main())
