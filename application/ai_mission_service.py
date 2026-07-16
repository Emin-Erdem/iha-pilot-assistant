import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from pydantic import ValidationError

from api.schemas import (
    AIMissionRequest,
    AIMissionResponse,
    CommandRequest,
)
from config.settings import Settings


load_dotenv()


class AIMissionService:
    """
    Converts Turkish natural-language instructions
    into validated drone mission plans.

    NVIDIA NIM is used as the primary provider.
    Deterministic parsing rules are used as a fallback.
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("NVIDIA_API_KEY")

        self.base_url = os.getenv(
            "NVIDIA_BASE_URL",
            "https://integrate.api.nvidia.com/v1",
        )

        self.model = os.getenv(
            "NVIDIA_MODEL",
            "openai/gpt-oss-120b",
        )

        self.client: OpenAI | None = None

    def generate_mission(
        self,
        request: AIMissionRequest,
    ) -> AIMissionResponse:
        """
        Generates a mission from a Turkish
        natural-language instruction.

        NVIDIA NIM is attempted first. If it is unavailable
        or returns an invalid result, deterministic rules
        are used as a fallback.
        """

        instruction = request.instruction.strip()

        if not instruction:
            raise ValueError(
                "Görev talimatı boş olamaz."
            )

        try:
            return self._generate_with_nvidia(
                instruction
            )

        except (
            OpenAIError,
            json.JSONDecodeError,
            ValidationError,
            ValueError,
            TypeError,
            KeyError,
            IndexError,
        ):
            return self._generate_with_rules(
                instruction
            )

    def _generate_with_nvidia(
        self,
        instruction: str,
    ) -> AIMissionResponse:
        """
        Generates a structured mission using NVIDIA NIM.
        """

        if not self.api_key:
            raise ValueError(
                "NVIDIA API anahtarı yapılandırılmamış."
            )

        client = self._get_client()

        response = client.chat.completions.create(
            model=self.model,
            temperature=0.1,
            max_tokens=1000,
            messages=[
                {
                    "role": "system",
                    "content": self._build_system_prompt(),
                },
                {
                    "role": "user",
                    "content": instruction,
                },
            ],
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError(
                "NVIDIA modeli boş yanıt döndürdü."
            )

        cleaned_content = self._clean_json_content(
            content
        )

        mission_data = json.loads(
            cleaned_content
        )

        mission = AIMissionResponse(
            **mission_data
        )

        self._validate_generated_mission(
            mission
        )

        return mission

    def _get_client(self) -> OpenAI:
        """
        Creates the NVIDIA API client only when needed.
        """

        if self.client is None:
            if not self.api_key:
                raise ValueError(
                    "NVIDIA_API_KEY bulunamadı."
                )

            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=30.0,
                max_retries=1,
            )

        return self.client

    def _build_system_prompt(self) -> str:
        """
        Returns the system prompt used by NVIDIA NIM.
        """

        return f"""
Sen bir İHA görev planlama asistanısın.

Kullanıcı sana Türkçe bir görev talimatı verecek.
Talimatı çalıştırılabilir bir İHA görev planına dönüştür.

Yalnızca geçerli JSON döndür.
Markdown, açıklama, yorum veya kod bloğu kullanma.

Çıktı şeması:

{{
  "name": "Kısa Türkçe görev adı",
  "commands": [
    {{
      "type": "TAKEOFF",
      "parameters": {{
        "altitude": 20
      }}
    }}
  ]
}}

Desteklenen komutlar ve parametreleri:

1. TAKEOFF
   {{"altitude": sayı}}

2. GOTO
   {{"x": sayı, "y": sayı}}

3. HOVER
   {{"duration": sayı}}

4. RETURN_HOME
   {{}}

5. LAND
   {{}}

Kurallar:

Kurallar:

- Komut type değerleri yalnızca TAKEOFF, GOTO,
  HOVER, RETURN_HOME veya LAND olabilir.
- Bütün komutlarda parameters alanı bulunmalıdır.
- Kullanıcının verdiği işlem sırasını koru.
- Kullanıcının istemediği hareketleri ekleme.
- Kalkış irtifası sıfırdan büyük olmalıdır.
- Kalkış irtifası en fazla
  {Settings.MAX_ALTITUDE} metre olabilir.
- İrtifa belirtilmemişse 20 metre kullan.
- Bekleme süresi belirtilmemişse 5 saniye kullan.
- Bekleme süresi sıfırdan büyük olmalıdır.
- Görev adı kısa ve Türkçe olmalıdır.
- Kullanıcı eve dönmek isterse RETURN_HOME ekle.
- Kullanıcı iniş isterse LAND ekle.
- Devriye, dolaşım, keşif, tarama veya benzeri görevler tamamlandıktan sonra,
  kullanıcı aksini belirtmedikçe görevi RETURN_HOME ve LAND komutları ile bitir.
- Eğer görev sonlandırılacaksa son iki komut daima RETURN_HOME ve LAND olmalıdır.
""".strip()

    def _clean_json_content(
        self,
        content: str,
    ) -> str:
        """
        Removes optional Markdown fences and extracts
        the JSON object from the model response.
        """

        cleaned = content.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]

        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]

        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        cleaned = cleaned.strip()

        first_brace = cleaned.find("{")
        last_brace = cleaned.rfind("}")

        if (
            first_brace == -1
            or last_brace == -1
            or last_brace < first_brace
        ):
            raise ValueError(
                "Model yanıtında geçerli JSON bulunamadı."
            )

        return cleaned[
            first_brace:last_brace + 1
        ]

    def _validate_generated_mission(
        self,
        mission: AIMissionResponse,
    ) -> None:
        """
        Performs domain-level validation on the
        generated mission.
        """

        supported_commands = {
            "TAKEOFF",
            "GOTO",
            "HOVER",
            "RETURN_HOME",
            "LAND",
        }

        for command in mission.commands:
            command_type = command.type.upper()
            parameters = command.parameters

            if command_type not in supported_commands:
                raise ValueError(
                    "Desteklenmeyen komut üretildi: "
                    f"{command.type}"
                )

            command.type = command_type

            if command_type == "TAKEOFF":
                altitude = parameters.get(
                    "altitude"
                )

                if altitude is None:
                    raise ValueError(
                        "TAKEOFF komutunda altitude eksik."
                    )

                altitude = float(altitude)

                if altitude <= 0:
                    raise ValueError(
                        "Kalkış irtifası sıfırdan "
                        "büyük olmalıdır."
                    )

                if altitude > Settings.MAX_ALTITUDE:
                    raise ValueError(
                        "Kalkış irtifası güvenli "
                        "sınırı aşıyor."
                    )

                parameters["altitude"] = altitude

            elif command_type == "GOTO":
                if "x" not in parameters:
                    raise ValueError(
                        "GOTO komutunda x eksik."
                    )

                if "y" not in parameters:
                    raise ValueError(
                        "GOTO komutunda y eksik."
                    )

                parameters["x"] = float(
                    parameters["x"]
                )

                parameters["y"] = float(
                    parameters["y"]
                )

            elif command_type == "HOVER":
                duration = parameters.get(
                    "duration"
                )

                if duration is None:
                    raise ValueError(
                        "HOVER komutunda duration eksik."
                    )

                duration = float(duration)

                if duration <= 0:
                    raise ValueError(
                        "Bekleme süresi sıfırdan "
                        "büyük olmalıdır."
                    )

                parameters["duration"] = duration

            else:
                command.parameters = {}

    def _generate_with_rules(
        self,
        instruction: str,
    ) -> AIMissionResponse:
        """
        Generates a mission using deterministic parsing
        rules when NVIDIA is unavailable.
        """

        normalized_instruction = (
            instruction
            .lower()
            .replace("â", "a")
        )

        commands: list[CommandRequest] = []

        self._add_takeoff_command(
            normalized_instruction,
            commands,
        )

        self._add_goto_commands(
            normalized_instruction,
            commands,
        )

        self._add_hover_command(
            normalized_instruction,
            commands,
        )

        self._add_return_home_command(
            normalized_instruction,
            commands,
        )

        self._add_land_command(
            normalized_instruction,
            commands,
        )

        if not commands:
            raise ValueError(
                "Desteklenen bir görev komutu bulunamadı."
            )

        mission = AIMissionResponse(
            name="Yapay Zekâ Görevi",
            commands=commands,
        )

        self._validate_generated_mission(
            mission
        )

        return mission

    def _add_takeoff_command(
        self,
        instruction: str,
        commands: list[CommandRequest],
    ) -> None:
        """
        Adds a TAKEOFF command when Turkish or English
        takeoff intent is detected.
        """

        takeoff_requested = any(
            phrase in instruction
            for phrase in (
                "take off",
                "takeoff",
                "kalk",
                "kalkış",
                "havalan",
                "yüksel",
                "yuksel",
            )
        )

        if not takeoff_requested:
            return

        altitude = self._extract_first_number(
            instruction,
            (
                r"(?:"
                r"take\s*off|takeoff|"
                r"kalk(?:ış)?|kalkis|"
                r"havalan|yüksel|yuksel"
                r")"
                r"[^\d-]*"
                r"(-?\d+(?:[.,]\d+)?)"
            ),
        )

        if altitude is None:
            altitude = self._extract_first_number(
                instruction,
                (
                    r"(-?\d+(?:[.,]\d+)?)"
                    r"\s*(?:metre|meter|m)"
                ),
            )

        commands.append(
            CommandRequest(
                type="TAKEOFF",
                parameters={
                    "altitude": (
                        altitude
                        if altitude is not None
                        else 20.0
                    )
                },
            )
        )

    def _add_goto_commands(
        self,
        instruction: str,
        commands: list[CommandRequest],
    ) -> None:
        """
        Adds every detected Turkish or English
        GOTO command.
        """

        pattern = re.compile(
            r"(?:"
            r"go|fly|move|git|ilerle|uç|uc"
            r")"
            r"(?:\s+(?:to|towards|konumuna|noktasına|noktasina))?"
            r"[^\d-]*"
            r"x\s*[=:]?\s*"
            r"(-?\d+(?:[.,]\d+)?)"
            r"\s*(?:,|ve|and)?\s*"
            r"y\s*[=:]?\s*"
            r"(-?\d+(?:[.,]\d+)?)"
        )

        for match in pattern.finditer(instruction):
            x = self._to_float(
                match.group(1)
            )

            y = self._to_float(
                match.group(2)
            )

            commands.append(
                CommandRequest(
                    type="GOTO",
                    parameters={
                        "x": x,
                        "y": y,
                    },
                )
            )

    def _add_hover_command(
        self,
        instruction: str,
        commands: list[CommandRequest],
    ) -> None:
        """
        Adds a HOVER command when Turkish or English
        hover intent is detected.
        """

        hover_requested = any(
            phrase in instruction
            for phrase in (
                "hover",
                "bekle",
                "havada kal",
                "sabit kal",
            )
        )

        if not hover_requested:
            return

        duration = self._extract_first_number(
            instruction,
            (
                r"(?:hover|bekle|havada\s+kal|sabit\s+kal)"
                r"[^\d-]*"
                r"(-?\d+(?:[.,]\d+)?)"
            ),
        )

        if duration is None:
            duration = self._extract_first_number(
                instruction,
                (
                    r"(-?\d+(?:[.,]\d+)?)"
                    r"\s*(?:saniye|second|seconds|sn)"
                ),
            )

        commands.append(
            CommandRequest(
                type="HOVER",
                parameters={
                    "duration": (
                        duration
                        if duration is not None
                        else 5.0
                    )
                },
            )
        )

    def _add_return_home_command(
        self,
        instruction: str,
        commands: list[CommandRequest],
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
                "eve dön",
                "eve don",
                "başlangıç noktasına dön",
                "baslangic noktasina don",
                "geri dön",
                "geri don",
            )
        )

        if not return_home_requested:
            return

        commands.append(
            CommandRequest(
                type="RETURN_HOME",
                parameters={},
            )
        )

    def _add_land_command(
        self,
        instruction: str,
        commands: list[CommandRequest],
    ) -> None:
        """
        Adds a LAND command.
        """

        land_requested = any(
            phrase in instruction
            for phrase in (
                "land",
                "iniş yap",
                "inis yap",
                "yere in",
                "alçal ve in",
                "alcal ve in",
            )
        )

        if not land_requested:
            return

        commands.append(
            CommandRequest(
                type="LAND",
                parameters={},
            )
        )

    def _extract_first_number(
        self,
        text: str,
        pattern: str,
    ) -> float | None:
        """
        Extracts the first numeric value matching
        a regular-expression pattern.
        """

        match = re.search(
            pattern,
            text,
        )

        if match is None:
            return None

        return self._to_float(
            match.group(1)
        )

    def _to_float(
        self,
        value: str,
    ) -> float:
        """
        Converts numbers containing a comma or dot
        decimal separator into a float.
        """

        normalized_value = value.replace(
            ",",
            ".",
        )

        return float(normalized_value)