from dataclasses import dataclass


@dataclass
class Position:
    """
    Represents the position of the drone in the simulation.
    """

    x: float
    y: float