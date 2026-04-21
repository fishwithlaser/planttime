#!/usr/bin/env python3
"""Control a WiZ smart plug by MAC address (stable across IP changes).

Usage:
    python plug_control.py light on
    python plug_control.py pump off
    python plug_control.py <mac> on
"""

import asyncio
import sys

from pywizlight import wizlight
from pywizlight.discovery import discover_lights

BROADCAST_SPACE = "192.168.18.255"

# Friendly names → MAC addresses
PLUGS = {
    "light": "cc4085b10db8",
    "pump":  "cc4085b0d55c",
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


if __name__ == "__main__":
    asyncio.run(main())
