import os

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from api.schemas import (
    AICopilotRequest,
    AICopilotResponse,
)


load_dotenv()


class AICopilotService:
    """
    Answers Turkish pilot questions using the current
    telemetry, mission and flight report context.

    NVIDIA NIM is used when available.
    A deterministic local response is used as fallback.
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

    def answer_question(
        self,
        request: AICopilotRequest,
    ) -> AICopilotResponse:
        """
        Produces a Turkish answer using the provided
        drone system context.
        """

        question = request.question.strip()

        if not question:
            raise ValueError(
                "Soru boş olamaz."
            )

        try:
            return self._answer_with_nvidia(
                request
            )

        except (
            OpenAIError,
            ValueError,
            TypeError,
            KeyError,
            IndexError,
        ):
            return self._answer_with_rules(
                request
            )

    def _answer_with_nvidia(
        self,
        request: AICopilotRequest,
    ) -> AICopilotResponse:
        """
        Uses NVIDIA NIM to answer the user's question.
        """

        if not self.api_key:
            raise ValueError(
                "NVIDIA API anahtarı yapılandırılmamış."
            )

        client = self._get_client()

        response = client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            max_tokens=350,
            messages=[
                {
                    "role": "system",
                    "content": self._build_system_prompt(),
                },
                {
                    "role": "user",
                    "content": self._build_user_context(
                        request
                    ),
                },
            ],
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError(
                "Yapay zekâ boş bir yanıt döndürdü."
            )

        return AICopilotResponse(
            answer=content.strip()
        )

    def _get_client(self) -> OpenAI:
        """
        Creates the NVIDIA client only when needed.
        """

        if self.client is None:
            if not self.api_key:
                raise ValueError(
                    "NVIDIA_API_KEY bulunamadı."
                )

            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=15.0,
                max_retries=0,
            )

        return self.client

    def _build_system_prompt(self) -> str:
        """
        Returns the copilot system prompt.
        """

        return """
Sen bir İHA uçuş asistanısın.

Kullanıcı sana Türkçe sorular soracak.
Her zaman Türkçe cevap ver.

Kurallar:

- Cevapların kısa, açık ve pilot odaklı olsun.
- Yalnızca verilen telemetri, görev ve rapor
  bilgilerini kullan.
- Bilmediğin konuda tahmin yürütme.
- Veride olmayan bilgileri uydurma.
- Gerektiğinde güvenlik uyarısı yap.
- Teknik komut adlarını TAKEOFF, GOTO, HOVER,
  RETURN_HOME ve LAND biçiminde bırakabilirsin.
- Konum bilgisini X ve Y koordinatlarıyla açıkla.
- Batarya yüzde 20 veya altındaysa bunu düşük
  batarya olarak değerlendir.
- Görev durumu Failed veya Unavailable ise
  bunun bir sorun olduğunu açıkça belirt.
- Kullanıcı son görevi sorarsa rapor verilerini
  kısa şekilde özetle.
""".strip()

    def _build_user_context(
        self,
        request: AICopilotRequest,
    ) -> str:
        """
        Converts the request context into readable text
        for the language model.
        """

        telemetry = request.telemetry
        mission = request.mission
        report = request.report

        mission_name = (
            mission.name
            if mission and mission.name
            else "Bilinmiyor"
        )

        mission_status = (
            mission.status
            if mission
            else "Bilinmiyor"
        )

        command_count = (
            len(mission.commands)
            if mission
            else 0
        )

        report_text = (
            "Son uçuş raporu bulunmuyor."
        )

        if report is not None:
            report_text = (
                f"Görev adı: "
                f"{report.mission_name or 'Bilinmiyor'}\n"
                f"Çalıştırılan komut sayısı: "
                f"{report.commands_executed}\n"
                f"Kat edilen mesafe: "
                f"{report.distance_travelled}\n"
                f"Maksimum irtifa: "
                f"{report.max_altitude}\n"
                f"Kullanılan batarya: "
                f"{report.battery_used}\n"
                f"Son batarya: "
                f"{report.final_battery}\n"
                f"Son irtifa: "
                f"{report.final_altitude}\n"
                f"Son konum: "
                f"{report.final_position}\n"
                f"Son uçuş modu: "
                f"{report.flight_mode}"
            )

        return f"""
Kullanıcının sorusu:
{request.question}

Canlı telemetri:
- Batarya: %{telemetry.battery_level}
- İrtifa: {telemetry.altitude} metre
- Konum: X={telemetry.position.get("x", 0)},
  Y={telemetry.position.get("y", 0)}
- Hız: {telemetry.speed} m/s
- Uçuş modu: {telemetry.mode}
- Zaman: {telemetry.timestamp or "Bilinmiyor"}

Aktif görev:
- Görev adı: {mission_name}
- Görev durumu: {mission_status}
- Komut sayısı: {command_count}

Son uçuş raporu:
{report_text}
""".strip()

    def _answer_with_rules(
        self,
        request: AICopilotRequest,
    ) -> AICopilotResponse:
        """
        Provides fast local answers when NVIDIA is
        unavailable.
        """

        question = request.question.lower()
        telemetry = request.telemetry
        mission = request.mission
        report = request.report

        if any(
            phrase in question
            for phrase in (
                "nerede",
                "konum",
                "pozisyon",
            )
        ):
            x = telemetry.position.get("x", 0)
            y = telemetry.position.get("y", 0)

            return AICopilotResponse(
                answer=(
                    f"Drone şu anda X={x}, Y={y} "
                    f"konumunda ve "
                    f"{telemetry.altitude} metre "
                    f"irtifada."
                )
            )

        if any(
            phrase in question
            for phrase in (
                "batarya",
                "şarj",
                "sarj",
                "pil",
            )
        ):
            battery = telemetry.battery_level

            if battery <= 20:
                answer = (
                    f"Batarya seviyesi %{battery}. "
                    "Batarya düşük; yeni görev "
                    "başlatılmamalı ve dönüş "
                    "değerlendirilmelidir."
                )
            else:
                answer = (
                    f"Batarya seviyesi %{battery}. "
                    "Mevcut verilere göre batarya "
                    "kritik seviyede değil."
                )

            return AICopilotResponse(
                answer=answer
            )

        if any(
            phrase in question
            for phrase in (
                "irtifa",
                "yükseklik",
                "yukseklik",
            )
        ):
            return AICopilotResponse(
                answer=(
                    f"Drone şu anda "
                    f"{telemetry.altitude} metre "
                    f"irtifada."
                )
            )

        if any(
            phrase in question
            for phrase in (
                "hız",
                "hiz",
                "ne kadar hızlı",
            )
        ):
            return AICopilotResponse(
                answer=(
                    f"Drone'un mevcut hızı "
                    f"{telemetry.speed} m/s."
                )
            )

        if any(
            phrase in question
            for phrase in (
                "uçuş modu",
                "ucus modu",
                "modu",
            )
        ):
            return AICopilotResponse(
                answer=(
                    f"Mevcut uçuş modu "
                    f"{telemetry.mode}."
                )
            )

        if any(
            phrase in question
            for phrase in (
                "görev durumu",
                "gorev durumu",
                "görev ne durumda",
                "gorev ne durumda",
            )
        ):
            status = (
                mission.status
                if mission
                else "Bilinmiyor"
            )

            return AICopilotResponse(
                answer=(
                    f"Mevcut görev durumu: "
                    f"{status}."
                )
            )

        if any(
            phrase in question
            for phrase in (
                "son görevi özetle",
                "son gorevi ozetle",
                "raporu özetle",
                "raporu ozetle",
            )
        ):
            if report is None:
                return AICopilotResponse(
                    answer=(
                        "Henüz kullanılabilir bir "
                        "uçuş raporu bulunmuyor."
                    )
                )

            return AICopilotResponse(
                answer=(
                    f"{report.mission_name or 'Son görev'} "
                    f"tamamlandı. "
                    f"{report.commands_executed or 0} komut "
                    f"çalıştırıldı, "
                    f"{report.distance_travelled or 0} metre "
                    f"mesafe kat edildi ve son batarya "
                    f"seviyesi %{report.final_battery or 0}."
                )
            )

        return AICopilotResponse(
            answer=(
                "Bu soruyu mevcut yerel kurallarla "
                "yanıtlayamadım. Konum, batarya, "
                "irtifa, hız, görev durumu veya son "
                "uçuş raporu hakkında soru sorabilirsiniz."
            )
        )