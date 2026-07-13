from dataclasses import dataclass, field


@dataclass
class SafetyReport:
    """
    Represents the result of a safety validation.
    """

    safe: bool

    reasons: list[str] = field(default_factory=list)

    recommendations: list[str] = field(default_factory=list)

    risk_score: float = 0.0