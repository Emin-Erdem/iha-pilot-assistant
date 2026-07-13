from infrastructure.simulator import Simulator

from domain.command import Command
from domain.mission import Mission
from domain.enums import CommandType

mission = Mission(
    name="Demo Mission"
)

mission.commands.append(

    Command(
        command_type=CommandType.TAKEOFF,
        parameters={
            "altitude": 20
        }
    )

)

mission.commands.append(

    Command(
        command_type=CommandType.GOTO,
        parameters={
            "x": 100,
            "y": 50
        }
    )

)

mission.commands.append(

    Command(
        command_type=CommandType.HOVER,
        parameters={
            "duration": 5
        }
    )

)

mission.commands.append(

    Command(
        command_type=CommandType.RETURN_HOME
    )

)

mission.commands.append(

    Command(
        command_type=CommandType.LAND
    )

)

simulator = Simulator()

simulator.run(mission)