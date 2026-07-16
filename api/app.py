import asyncio

from fastapi import (
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import (
    AICopilotRequest,
    AICopilotResponse,
    AIMissionRequest,
    AIMissionResponse,
    MissionRequest,
)
from api.services import ApiMissionService

from application.ai_copilot_service import (
    AICopilotService,
)
from application.ai_mission_service import (
    AIMissionService,
)
from exceptions.drone_exception import DroneException


app = FastAPI(
    title="IHA Pilot Assistant API",
    description=(
        "API for the AI-assisted drone mission system."
    ),
    version="0.7.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mission_service = ApiMissionService()
ai_mission_service = AIMissionService()
ai_copilot_service = AICopilotService()


@app.get("/")
def read_root() -> dict[str, str]:
    """
    Returns basic API status information.
    """

    return {
        "message": (
            "IHA Pilot Assistant API is running."
        )
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    """
    Returns the health status of the API.
    """

    return {
        "status": "healthy"
    }


@app.post(
    "/ai/mission",
    response_model=AIMissionResponse,
)
def generate_ai_mission(
    request: AIMissionRequest,
) -> AIMissionResponse:
    """
    Converts a natural-language instruction into
    a structured mission plan.
    """

    try:
        return ai_mission_service.generate_mission(
            request
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@app.post(
    "/ai/copilot",
    response_model=AICopilotResponse,
)
def ask_ai_copilot(
    request: AICopilotRequest,
) -> AICopilotResponse:
    """
    Answers a Turkish pilot question using the
    provided telemetry, mission and report context.
    """

    try:
        return ai_copilot_service.answer_question(
            request
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=(
                "Yapay zekâ uçuş asistanı şu anda "
                "kullanılamıyor."
            ),
        ) from error


@app.post("/missions/run")
def run_mission(
    request: MissionRequest,
) -> dict:
    """
    Runs a mission synchronously.
    """

    try:
        return mission_service.run_mission(
            request
        )

    except DroneException as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except KeyError as error:
        raise HTTPException(
            status_code=422,
            detail=(
                "Missing command parameter: "
                f"{error.args[0]}"
            ),
        ) from error


@app.post("/missions/start")
def start_mission(
    request: MissionRequest,
) -> dict:
    """
    Starts a mission in the background.
    """

    try:
        return mission_service.start_mission(
            request,
            command_delay=1.0,
        )

    except DroneException as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except KeyError as error:
        raise HTTPException(
            status_code=422,
            detail=(
                "Missing command parameter: "
                f"{error.args[0]}"
            ),
        ) from error

    except RuntimeError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error


@app.get("/missions/status")
def get_mission_status() -> dict:
    """
    Returns the current background mission status.
    """

    return mission_service.get_status()


@app.post("/system/reset")
def reset_system() -> dict[str, str]:
    """
    Resets the drone, telemetry, mission state,
    and latest flight report.
    """

    try:
        mission_service.reset()

        return {
            "status": "reset",
            "message": (
                "Drone system reset successfully."
            ),
        }

    except RuntimeError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error


@app.get("/telemetry")
def get_telemetry() -> dict:
    """
    Returns the latest telemetry snapshot.
    """

    telemetry = (
        mission_service.get_latest_telemetry()
    )

    if telemetry is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "No telemetry is available yet."
            ),
        )

    return telemetry


@app.get("/reports/latest")
def get_latest_report() -> dict:
    """
    Returns the latest flight report.
    """

    report = (
        mission_service.get_latest_report()
    )

    if report is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "No flight report is available yet."
            ),
        )

    return report


@app.websocket("/ws/telemetry")
async def telemetry_websocket(
    websocket: WebSocket,
) -> None:
    """
    Continuously sends the latest telemetry while
    the client remains connected.
    """

    await websocket.accept()

    try:
        while True:
            telemetry = (
                mission_service
                .get_latest_telemetry()
            )

            if telemetry is None:
                await websocket.send_json(
                    {
                        "status": "waiting",
                        "message": (
                            "No telemetry is "
                            "available yet."
                        ),
                    }
                )
            else:
                await websocket.send_json(
                    {
                        "status": "connected",
                        "telemetry": telemetry,
                    }
                )

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        return