#!/usr/bin/env python3
"""Discover WiZ plugs on the network and show their IPs and MACs.

Usage: python plug_discover.py
"""

import asyncio

from pywizlight.discovery import discover_lights

BROADCAST_SPACE = "192.168.18.255"

# Friendly names → MAC addresses
PLUGS = {
    "light": "cc4085b0d55c",
    "pump":  "cc4085b10db8",
}


async def main():
    bulbs = await discover_lights(broadcast_space=BROADCAST_SPACE)
    if not bulbs:
        print("No WiZ plugs found on the network.")
        return

    mac_to_name = {mac.lower(): name for name, mac in PLUGS.items()}

    print(f"{'NAME':<8} {'MAC':<16} {'IP':<16}")
    print("-" * 42)
    for bulb in bulbs:
        mac = bulb.mac.lower().replace(":", "")
        name = mac_to_name.get(mac, "unknown")
        print(f"{name:<8} {mac:<16} {bulb.ip:<16}")


if __name__ == "__main__":
    asyncio.run(main())
