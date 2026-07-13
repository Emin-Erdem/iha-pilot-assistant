from domain.enums import CommandType
from domain.mission import Mission
from domain.mission_report import MissionReport


class MissionValidator:
    """
    Validates the logical consistency of a mission.
    """

    def validate(self, mission: Mission) -> MissionReport:
        """
        Validates the overall mission sequence.
        """

        report = MissionReport(valid=True)

        if not mission.commands:

            report.valid = False

            report.reasons.append(
                "Mission does not contain any commands."
            )

            report.recommendations.append(
                "Add at least one command to the mission."
            )

            return report

        first_command = mission.commands[0]

        if first_command.command_type != CommandType.TAKEOFF:

            report.valid = False

            report.reasons.append(
                "The first command must be TAKEOFF."
            )

            report.recommendations.append(
                "Start the mission with a TAKEOFF command."
            )

        return report