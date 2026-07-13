import json


class MissionRecorder:
    """
    Saves mission reports to a JSON file.
    """

    def save(self, report: dict, file_path: str) -> None:
        """
        Saves the report as JSON.
        """

        with open(file_path, "w", encoding="utf-8") as file:

            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False
            )