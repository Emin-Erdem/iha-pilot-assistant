from threading import Lock, Thread

from application.mission_runner import MissionRunner

from domain.drone import Drone
from domain.mission import Mission


class MissionService:
    """
    Provides high-level mission operations.
    """

    def __init__(self):
        self._lock = Lock()

        self.drone = Drone()
        self.runner = MissionRunner(self.drone)

        self.latest_report: dict | None = None
        self.latest_error: str | None = None
        self.is_running: bool = False

    def run(self, mission: Mission) -> dict:
        """
        Runs a mission synchronously and stores the generated report.
        """

        report = self.runner.run(mission)

        self.latest_report = report
        self.latest_error = None

        return report

    def start(
        self,
        mission: Mission,
        command_delay: float = 1.0
    ) -> None:
        """
        Starts a mission in a background thread.
        """

        with self._lock:
            if self.is_running:
                raise RuntimeError(
                    "A mission is already running."
                )

            self.is_running = True
            self.latest_report = None
            self.latest_error = None

        thread = Thread(
            target=self._run_in_background,
            args=(mission, command_delay),
            daemon=True
        )

        thread.start()

    def _run_in_background(
        self,
        mission: Mission,
        command_delay: float
    ) -> None:
        """
        Runs the mission inside a background thread.
        """

        try:
            report = self.runner.run(
                mission,
                command_delay=command_delay
            )

            with self._lock:
                self.latest_report = report
                self.latest_error = None

        except Exception as error:
            with self._lock:
                self.latest_error = str(error)

        finally:
            with self._lock:
                self.is_running = False

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

    def get_status(self) -> dict:
        """
        Returns the current mission execution status.
        """

        return {
            "is_running": self.is_running,
            "has_report": self.latest_report is not None,
            "error": self.latest_error
        }

    def reset(self) -> None:
        """
        Resets the drone and mission state.
        """

        with self._lock:
            if self.is_running:
                raise RuntimeError(
                    "Cannot reset while a mission is running."
                )

            self.drone = Drone()
            self.runner = MissionRunner(self.drone)
            self.latest_report = None
            self.latest_error = None