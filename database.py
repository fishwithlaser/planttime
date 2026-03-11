import logging
from datetime import datetime, timezone

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

log = logging.getLogger(__name__)


class Database:
    """InfluxDB 2.x client for storing sensor readings."""

    def __init__(self, url: str, token: str, org: str, bucket: str):
        self.bucket = bucket
        self.org = org
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def write_reading(self, sensor_type: str, value: float):
        """Write a single sensor reading to InfluxDB.

        Args:
            sensor_type: One of 'ph', 'ec', 'water_level'
            value: The sensor reading
        """
        point = (
            Point("sensors")
            .tag("sensor_type", sensor_type)
            .field("value", value)
            .time(datetime.now(timezone.utc), WritePrecision.S)
        )
        try:
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            log.debug("Wrote %s=%.2f to InfluxDB", sensor_type, value)
        except Exception:
            log.exception("Failed to write %s to InfluxDB", sensor_type)

    def close(self):
        """Close the InfluxDB client."""
        self.client.close()
