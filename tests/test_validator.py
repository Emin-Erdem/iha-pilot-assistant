from application.validator import Validator

from domain.command import Command
from domain.drone import Drone
from domain.enums import CommandType


def main():

    drone = Drone(
        battery_level=15
    )

    command = Command(
        command_type=CommandType.TAKEOFF,
        parameters={
            "altitude": 20
        }
    )

    validator = Validator()

    report = validator.validate(drone, command)

    print("Safe:", report.safe)
    print("Reasons:", report.reasons)
    print("Recommendations:", report.recommendations)
    print("Risk Score:", report.risk_score)


if __name__ == "__main__":
    main()