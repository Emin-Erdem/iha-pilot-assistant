from domain.command import Command
from domain.mission import Mission

from application.mission_validator import MissionValidator


class MissionPlanner:
    """
    Creates and prepares missions before execution.
    """

    def __init__(self):

        self.validator = MissionValidator()

    def create_mission(
        self,
        commands: list[Command],
        name: str = "Generated Mission"
    ) -> Mission:

        mission = Mission(
            name=name,
            commands=commands
        )

        return mission

    def validate_mission(self, mission: Mission):

        return self.validator.validate(mission)

    def optimize_mission(self, mission: Mission) -> Mission:

        return mission