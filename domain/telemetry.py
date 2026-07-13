from dataclasses import dataclass, field
from datetime import datetime

from domain.position import Position
from domain.enums import FlightMode


@dataclass
class Telemetry:
    """
    Represents a telemetry snapshot of the drone.
    """

    position: Position

    altitude: float

    battery_level: float

    speed: float

    mode: FlightMode

    timestamp: datetime = field(default_factory=datetime.now)