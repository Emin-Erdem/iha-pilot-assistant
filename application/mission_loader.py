import json

from domain.mission import Mission
from domain.command import Command
from domain.enums import CommandType


class MissionLoader:
    """
    Loads missions from JSON files.
    """

    def load(self, file_path: str) -> Mission:
        """
        Loads a mission from a JSON file.
        """

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        mission = Mission(
            name=data["name"]
        )

        for command_data in data["commands"]:

            command = Command(
                command_type=CommandType[command_data["type"]],
                parameters={
                    key: value
                    for key, value in command_data.items()
                    if key != "type"
                }
            )

            mission.commands.append(command)

        return mission