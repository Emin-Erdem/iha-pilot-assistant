from dataclasses import dataclass

from domain.position import Position


@dataclass
class Location:
    """
    Represents a named location in the simulation.
    """

    name: str
    position: Position
    description: str = ""