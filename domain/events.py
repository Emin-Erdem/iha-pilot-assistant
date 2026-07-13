from domain.command import Command


class MissionRecorder:
    """
    Records every executed command during a mission.
    """

    def __init__(self):
        self._commands: list[Command] = []

    def record(self, command: Command) -> None:
        """
        Records an executed command.
        """
        self._commands.append(command)

    def get_all(self) -> list[Command]:
        """
        Returns all recorded commands.
        """
        return self._commands.copy()

    def clear(self) -> None:
        """
        Clears the recorded commands.
        """
        self._commands.clear()