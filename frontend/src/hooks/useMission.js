import { useEffect, useState } from "react";

import {
  getMissionStatus,
  startMission,
} from "../services/api";


function useMission(
  onMissionStart,
  missionPayload
) {
  const [missionStatus, setMissionStatus] =
    useState("Waiting");

  const [buttonText, setButtonText] =
    useState("Start Mission");

  const [isStarting, setIsStarting] =
    useState(false);

  const [errorMessage, setErrorMessage] =
    useState("");

  useEffect(() => {
    async function updateMissionStatus() {
      try {
        const status = await getMissionStatus();

        if (status.is_running) {
          setMissionStatus("Running");
          setButtonText("Mission Running...");
          setErrorMessage("");
        } else if (status.error) {
          setMissionStatus("Failed");
          setButtonText("Start Mission");
          setErrorMessage(status.error);
        } else if (status.has_report) {
          setMissionStatus("Completed");
          setButtonText("Start New Mission");
          setErrorMessage("");
        } else {
          setMissionStatus("Waiting");
          setButtonText("Start Mission");
          setErrorMessage("");
        }
      } catch {
        setMissionStatus("Unavailable");
        setButtonText("Start Mission");
      }
    }

    updateMissionStatus();

    const intervalId = setInterval(
      updateMissionStatus,
      1000
    );

    return () => {
      clearInterval(intervalId);
    };
  }, []);

  async function handleStartMission() {
    try {
      if (!missionPayload) {
        throw new Error(
          "Mission data is unavailable."
        );
      }

      if (!missionPayload.name.trim()) {
        throw new Error(
          "Mission name is required."
        );
      }

      if (missionPayload.commands.length === 0) {
        throw new Error(
          "Mission must contain at least one command."
        );
      }

      setIsStarting(true);
      setErrorMessage("");
      setButtonText("Starting...");

      if (onMissionStart) {
        onMissionStart();
      }

      await startMission(missionPayload);

      setMissionStatus("Running");
      setButtonText("Mission Running...");
    } catch (error) {
      setMissionStatus("Failed");
      setButtonText("Start Mission");

      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Mission could not be started."
      );
    } finally {
      setIsStarting(false);
    }
  }

  function resetMissionState() {
    setMissionStatus("Waiting");
    setButtonText("Start Mission");
    setIsStarting(false);
    setErrorMessage("");
  }

  return {
    missionStatus,
    buttonText,
    isStarting,
    errorMessage,
    handleStartMission,
    resetMissionState,
  };
}

export default useMission;