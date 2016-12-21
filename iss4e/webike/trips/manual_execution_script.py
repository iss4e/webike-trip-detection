from  itertools import chain
from iss4e.db import influxdb
from iss4e.util import BraceMessage as __, logging
from iss4e.util.config import load_config

from iss4e.webike.trips import module_locator, TripDetector
from iss4e.webike.trips.imei import IMEI

config = load_config(module_locator.module_path())
logger = logging.getLogger("iss4e.webike.db")



with influxdb.connect(**config["webike.influx"]) as client:
    measurement = client.stream_measurement(measurement="sensor_data",
                                            fields=["time", "discharge_current", "linear_acceleration_x",
                                                    "linear_acceleration_y", "linear_acceleration_z"])
    for _, series, samples in measurement:
        trips = TripDetector(IMEI(series)).processSamples(samples)
        points = chain.from_iterable((trip.to_points() for trip in trips))
        client.write_points(points)