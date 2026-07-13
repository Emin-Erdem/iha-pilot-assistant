from dataclasses import dataclass


@dataclass
class FlightStatistics:
    """
    Stores statistics collected during a mission.
    """

    distance_travelled: float = 0.0

    battery_used: float = 0.0

    max_altitude: float = 0.0

    commands_executed: int = 0