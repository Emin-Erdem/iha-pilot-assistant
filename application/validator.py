from domain.command import Command
from domain.drone import Drone
from domain.enums import CommandType
from domain.safety_report import SafetyReport


class Validator:
    """
    Validates commands before execution.
    """

    MAX_ALTITUDE = 50.0
    MIN_BATTERY = 20.0

    def validate(self, drone: Drone, command: Command) -> SafetyReport:
        """
        Executes all safety checks and returns a safety report.
        """

        report = SafetyReport(safe=True)

        self.check_battery(drone, report)
        self.check_altitude(command, report)
        self.check_destination(command, report)
        self.check_parameters(command, report)

        return report

    def check_battery(self, drone: Drone, report: SafetyReport) -> None:
        """Checks whether the battery level is sufficient."""

        if drone.battery_level < self.MIN_BATTERY:
            report.safe = False

            report.reasons.append(
                f"Battery level is too low ({drone.battery_level}%)."
            )

            report.recommendations.append(
                "Recharge the battery before starting the mission."
            )

            report.risk_score = max(report.risk_score, 0.9)

    def check_altitude(self, command: Command, report: SafetyReport) -> None:
        """Checks whether the requested altitude is within limits."""

        altitude = command.parameters.get("altitude")

        if altitude is None:
            return

        if altitude > self.MAX_ALTITUDE:
            report.safe = False

            report.reasons.append(
                f"Requested altitude ({altitude} m) exceeds the maximum allowed altitude ({self.MAX_ALTITUDE} m)."
            )

            report.recommendations.append(
                f"Reduce the altitude to {self.MAX_ALTITUDE} meters or below."
            )

            report.risk_score = max(report.risk_score, 0.8)

    def check_destination(self, command: Command, report: SafetyReport) -> None:
        """Checks whether the destination exists."""

        if command.command_type != CommandType.GOTO:
            return

        destination = command.parameters.get("destination")

        if destination is None:
            return

    def check_parameters(self, command: Command, report: SafetyReport) -> None:
        """Checks whether all required parameters are present."""

        if command.command_type == CommandType.TAKEOFF:

            if "altitude" not in command.parameters:

                report.safe = False

                report.reasons.append(
                    "Missing required parameter: altitude."
                )

                report.recommendations.append(
                    "Specify the target altitude."
                )

                report.risk_score = max(report.risk_score, 0.6)

        elif command.command_type == CommandType.GOTO:

            if "destination" not in command.parameters:

                report.safe = False

                report.reasons.append(
                    "Missing required parameter: destination."
                )

                report.recommendations.append(
                    "Specify the destination."
                )

                report.risk_score = max(report.risk_score, 0.6)