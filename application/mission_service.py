from application.mission_runner import MissionRunner

from domain.drone import Drone
from domain.mission import Mission


class MissionService:
    """
    Provides high-level mission operations.
    """

    def __init__(self):
        self.drone = Drone()
        self.runner = MissionRunner(self.drone)
        self.latest_report: dict | None = None

    def run(self, mission: Mission) -> dict:
        """
        Runs a mission and stores the generated report.
        """

        report = self.runner.run(mission)

        self.latest_report = report

        return report

    def get_latest_telemetry(self) -> dict | None:
        """
        Returns the latest telemetry snapshot as a dictionary.
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

    def reset(self) -> None:
        """
        Resets the drone and mission state.
        """

        self.drone = Drone()
        self.runner = MissionRunner(self.drone)
        self.latest_report = None