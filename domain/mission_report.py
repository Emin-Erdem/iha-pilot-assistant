from dataclasses import dataclass, field


@dataclass
class MissionReport:
    """
    Represents the result of mission-level validation.
    """

    valid: bool

    reasons: list[str] = field(default_factory=list)

    recommendations: list[str] = field(default_factory=list)