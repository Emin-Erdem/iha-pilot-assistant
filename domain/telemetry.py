from dataclasses import dataclass

from domain.position import Position
from domain.enums import FlightMode


@dataclass
class Telemetry:
    """
    Represents the telemetry data received from the drone.
    """

    position: Position
    altitude: float
    battery: float
    speed: float
    mode: FlightMode