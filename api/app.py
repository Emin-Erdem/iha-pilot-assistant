import asyncio

from fastapi import (
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)

from api.schemas import MissionRequest
from api.services import ApiMissionService

from exceptions.drone_exception import DroneException


app = FastAPI(
    title="IHA Pilot Assistant API",
    description="API for the AI-assisted drone mission system.",
    version="0.5.0",
)

mission_service = ApiMissionService()


@app.get("/")
def read_root() -> dict[str, str]:
    """
    Returns basic API status information.
    """

    return {
        "message": "IHA Pilot Assistant API is running."
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    """
    Returns the health status of the API.
    """

    return {
        "status": "healthy"
    }


@app.post("/missions/run")
def run_mission(request: MissionRequest) -> dict:
    """
    Runs a mission synchronously.
    """

    try:
        return mission_service.run_mission(request)

    except DroneException as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    except KeyError as error:
        raise HTTPException(
            status_code=422,
            detail=f"Missing command parameter: {error.args[0]}"
        ) from error


@app.post("/missions/start")
def start_mission(request: MissionRequest) -> dict:
    """
    Starts a mission in the background.
    """

    try:
        return mission_service.start_mission(
            request,
            command_delay=1.0
        )

    except DroneException as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    except KeyError as error:
        raise HTTPException(
            status_code=422,
            detail=f"Missing command parameter: {error.args[0]}"
        ) from error

    except RuntimeError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error)
        ) from error


@app.get("/missions/status")
def get_mission_status() -> dict:
    """
    Returns the current background mission status.
    """

    return mission_service.get_status()


@app.get("/telemetry")
def get_telemetry() -> dict:
    """
    Returns the latest telemetry snapshot.
    """

    telemetry = mission_service.get_latest_telemetry()

    if telemetry is None:
        raise HTTPException(
            status_code=404,
            detail="No telemetry is available yet."
        )

    return telemetry


@app.get("/reports/latest")
def get_latest_report() -> dict:
    """
    Returns the latest flight report.
    """

    report = mission_service.get_latest_report()

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="No flight report is available yet."
        )

    return report


@app.websocket("/ws/telemetry")
async def telemetry_websocket(
    websocket: WebSocket
) -> None:
    """
    Continuously sends the latest telemetry while the client
    remains connected.
    """

    await websocket.accept()

    try:
        while True:
            telemetry = mission_service.get_latest_telemetry()

            if telemetry is None:
                await websocket.send_json(
                    {
                        "status": "waiting",
                        "message": (
                            "No telemetry is available yet."
                        )
                    }
                )
            else:
                await websocket.send_json(
                    {
                        "status": "connected",
                        "telemetry": telemetry
                    }
                )

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        return