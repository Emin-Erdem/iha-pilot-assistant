from application.mission_runner import MissionRunner

from domain.command import Command
from domain.drone import Drone
from domain.enums import CommandType
from domain.mission import Mission

from api.schemas import MissionRequest


class ApiMissionService:
    """
    Converts API requests into domain missions and executes them.
    """

    def __init__(self):
        self.drone = Drone()
        self.runner = MissionRunner(self.drone)
        self.latest_report: dict | None = None

    def run_mission(self, request: MissionRequest) -> dict:
        """
        Converts a mission request into domain objects and runs it.
        """

        commands: list[Command] = []

        for command_request in request.commands:
            try:
                command_type = CommandType[command_request.type.upper()]
            except KeyError as error:
                raise ValueError(
                    f"Unsupported command type: {command_request.type}"
                ) from error

            commands.append(
                Command(
                    command_type=command_type,
                    parameters=command_request.parameters
                )
            )

        mission = Mission(
            name=request.name,
            commands=commands
        )

        report = self.runner.run(mission)
        self.latest_report = report

        return report

    def get_latest_telemetry(self) -> dict | None:
        """
        Returns the latest telemetry snapshot as a JSON-compatible dictionary.
        """

        telemetry = self.runner.last_telemetry()

        if telemetry is None:
            return None

        return {
            "position": {
                "x": telemetry.position.x,
                "y": telemetry.position.y,
            },
            "altitude": telemetry.altitude,
            "battery_level": telemetry.battery_level,
            "speed": telemetry.speed,
            "mode": telemetry.mode.value,
            "timestamp": telemetry.timestamp.isoformat(),
        }

    def get_latest_report(self) -> dict | None:
        """
        Returns the most recently generated flight report.
        """

        return self.latest_report