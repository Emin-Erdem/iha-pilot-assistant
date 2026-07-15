import re

from api.schemas import (
    AIMissionRequest,
    AIMissionResponse,
    CommandRequest,
)


class AIMissionService:
    """
    Converts natural-language instructions into mission plans.

    This first version uses deterministic parsing rules.
    It can later be replaced or extended with an LLM provider.
    """

    def generate_mission(
        self,
        request: AIMissionRequest
    ) -> AIMissionResponse:
        """
        Generates a mission plan from a natural-language instruction.
        """

        instruction = request.instruction.strip()

        if not instruction:
            raise ValueError(
                "Mission instruction cannot be empty."
            )

        normalized_instruction = instruction.lower()

        commands: list[CommandRequest] = []

        self._add_takeoff_command(
            normalized_instruction,
            commands
        )

        self._add_goto_commands(
            normalized_instruction,
            commands
        )

        self._add_hover_command(
            normalized_instruction,
            commands
        )

        self._add_return_home_command(
            normalized_instruction,
            commands
        )

        self._add_land_command(
            normalized_instruction,
            commands
        )

        if not commands:
            raise ValueError(
                "No supported mission commands were found."
            )

        return AIMissionResponse(
            name="AI Generated Mission",
            commands=commands
        )

    def _add_takeoff_command(
        self,
        instruction: str,
        commands: list[CommandRequest]
    ) -> None:
        """
        Adds a TAKEOFF command when takeoff intent is detected.
        """

        takeoff_requested = (
            "take off" in instruction or
            "takeoff" in instruction
        )

        if not takeoff_requested:
            return

        altitude = self._extract_first_number(
            instruction,
            (
                r"(?:take\s*off|takeoff)"
                r"[^\d-]*(-?\d+(?:\.\d+)?)"
            )
        )

        commands.append(
            CommandRequest(
                type="TAKEOFF",
                parameters={
                    "altitude": (
                        altitude
                        if altitude is not None
                        else 20
                    )
                }
            )
        )

    def _add_goto_commands(
        self,
        instruction: str,
        commands: list[CommandRequest]
    ) -> None:
        """
        Adds every detected GOTO command.
        """

        pattern = re.compile(
            r"(?:go|fly|move)"
            r"(?:\s+to)?"
            r"\s+x\s*[=:]?\s*"
            r"(-?\d+(?:\.\d+)?)"
            r"\s*(?:,|and)?\s*"
            r"y\s*[=:]?\s*"
            r"(-?\d+(?:\.\d+)?)"
        )

        for match in pattern.finditer(instruction):
            x = float(match.group(1))
            y = float(match.group(2))

            commands.append(
                CommandRequest(
                    type="GOTO",
                    parameters={
                        "x": x,
                        "y": y,
                    }
                )
            )

    def _add_hover_command(
        self,
        instruction: str,
        commands: list[CommandRequest]
    ) -> None:
        """
        Adds a HOVER command when hover intent is detected.
        """

        if "hover" not in instruction:
            return

        duration = self._extract_first_number(
            instruction,
            r"hover[^\d-]*(-?\d+(?:\.\d+)?)"
        )

        commands.append(
            CommandRequest(
                type="HOVER",
                parameters={
                    "duration": (
                        duration
                        if duration is not None
                        else 5
                    )
                }
            )
        )

    def _add_return_home_command(
        self,
        instruction: str,
        commands: list[CommandRequest]
    ) -> None:
        """
        Adds a RETURN_HOME command.
        """

        return_home_requested = any(
            phrase in instruction
            for phrase in (
                "return home",
                "return to home",
                "go home",
            )
        )

        if not return_home_requested:
            return

        commands.append(
            CommandRequest(
                type="RETURN_HOME",
                parameters={}
            )
        )

    def _add_land_command(
        self,
        instruction: str,
        commands: list[CommandRequest]
    ) -> None:
        """
        Adds a LAND command when land intent is detected.
        """

        if "land" not in instruction:
            return

        commands.append(
            CommandRequest(
                type="LAND",
                parameters={}
            )
        )

    def _extract_first_number(
        self,
        text: str,
        pattern: str
    ) -> float | None:
        """
        Extracts the first numeric value matching a pattern.
        """

        match = re.search(pattern, text)

        if match is None:
            return None

        value = float(match.group(1))

        return value