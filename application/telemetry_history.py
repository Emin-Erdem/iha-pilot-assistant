from domain.telemetry import Telemetry


class TelemetryHistory:
    """
    Stores telemetry snapshots generated during a mission.
    """

    def __init__(self):
        self._history: list[Telemetry] = []

    def add(self, telemetry: Telemetry) -> None:
        """
        Adds a telemetry snapshot to the history.
        """
        self._history.append(telemetry)

    def get_all(self) -> list[Telemetry]:
        """
        Returns all telemetry snapshots.
        """
        return self._history.copy()

    def clear(self) -> None:
        """
        Clears the telemetry history.
        """
        self._history.clear()

    def last(self) -> Telemetry | None:
        """
        Returns the latest telemetry snapshot.
        """
        if not self._history:
            return None

        return self._history[-1]