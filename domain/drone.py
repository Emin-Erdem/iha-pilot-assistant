from dataclasses import dataclass, field

from domain.position import Position
from domain.enums import FlightMode


@dataclass
class Drone:
    """
    Represents the current state of the drone.
    """

    position: Position = field(default_factory=lambda: Position(0.0, 0.0))
    altitude: float = 0.0
    battery_level: float = 100.0
    speed: float = 0.0
    mode: FlightMode = FlightMode.IDLE