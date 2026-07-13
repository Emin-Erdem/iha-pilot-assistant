from datetime import datetime
from dataclasses import dataclass, field

from domain.enums import CommandType


@dataclass
class Command:
    """
    Represents a validated command produced by the language model.
    """

    command_type: CommandType

    parameters: dict[str, object] = field(default_factory=dict)

    original_text: str = ""

    confidence: float = 1.0

    timestamp: datetime = field(default_factory=datetime.now)