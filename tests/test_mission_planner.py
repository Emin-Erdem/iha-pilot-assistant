from application.mission_planner import MissionPlanner

from domain.command import Command
from domain.enums import CommandType


def main():

    planner = MissionPlanner()

    commands = [

        Command(
            command_type=CommandType.TAKEOFF,
            parameters={
                "altitude": 20
            }
        ),

        Command(
            command_type=CommandType.RETURN_HOME
        )

    ]

    mission = planner.create_mission(commands)

    report = planner.validate_mission(mission)

    print("Mission Name :", mission.name)
    print("Command Count:", len(mission.commands))
    print("Mission Valid:", report.valid)
    print("Reasons:", report.reasons)


if __name__ == "__main__":
    main()