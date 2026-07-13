from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from domain.command import Command
from domain.enums import MissionStatus


@dataclass
class Mission:
    """
    Represents a mission consisting of one or more commands.
    """

    id: str = field(default_factory=lambda: str(uuid4()))

    name: str = "Untitled Mission"

    commands: list[Command] = field(default_factory=list)

    status: MissionStatus = MissionStatus.PENDING

    created_at: datetime = field(default_factory=datetime.now)