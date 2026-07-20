import {
  useEffect,
  useRef,
  useState,
} from "react";

import { connectTelemetry } from "../services/websocket";


const initialTelemetry = {
  battery_level: 100,
  altitude: 0,
  position: {
    x: 0,
    y: 0,
  },
  speed: 0,
  mode: "IDLE",
  timestamp: null,
};


function useTelemetry() {
  const [webSocketStatus, setWebSocketStatus] =
    useState("Connecting...");

  const [telemetry, setTelemetry] =
    useState(initialTelemetry);

  const [telemetryHistory, setTelemetryHistory] =
    useState([]);

  const [isReplaying, setIsReplaying] =
    useState(false);

  const [replayProgress, setReplayProgress] =
    useState(0);

  const replayTimerRef = useRef(null);
  const isReplayingRef = useRef(false);

  const latestLiveTelemetryRef = useRef(
    initialTelemetry
  );

  useEffect(() => {
    const socket = connectTelemetry((message) => {
      if (
        message.status === "connected" &&
        message.telemetry
      ) {
        const newTelemetry = message.telemetry;

        latestLiveTelemetryRef.current =
          newTelemetry;

        setWebSocketStatus("Connected ✅");

        if (!isReplayingRef.current) {
          setTelemetry(newTelemetry);

          setTelemetryHistory(
            (currentHistory) => {
              const lastItem =
                currentHistory[
                  currentHistory.length - 1
                ];

              if (
                lastItem?.timestamp ===
                newTelemetry.timestamp
              ) {
                return currentHistory;
              }

              const updatedHistory = [
                ...currentHistory,
                newTelemetry,
              ];

              return updatedHistory.slice(-20);
            }
          );
        }
      } else if (message.status === "waiting") {
        setWebSocketStatus("Waiting");
      }
    });

    socket.onopen = () => {
      setWebSocketStatus("Connected ✅");
    };

    socket.onerror = () => {
      setWebSocketStatus("Error ❌");
    };

    socket.onclose = () => {
      setWebSocketStatus("Disconnected");
    };

    return () => {
      socket.close();

      if (replayTimerRef.current) {
        clearTimeout(replayTimerRef.current);
      }
    };
  }, []);

  function stopReplay() {
    if (replayTimerRef.current) {
      clearTimeout(replayTimerRef.current);
      replayTimerRef.current = null;
    }

    isReplayingRef.current = false;

    setIsReplaying(false);
    setReplayProgress(0);

    setTelemetry(
      latestLiveTelemetryRef.current
    );
  }

  function startReplay(interval = 1100) {
    if (
      isReplayingRef.current ||
      telemetryHistory.length === 0
    ) {
      return false;
    }

    const replayFrames = [
      {
        ...initialTelemetry,
        position: {
          ...initialTelemetry.position,
        },
      },
      ...telemetryHistory.map((item) => ({
        ...item,
        position: {
          ...item.position,
        },
      })),
    ];

    let currentIndex = 0;

    isReplayingRef.current = true;

    setIsReplaying(true);
    setReplayProgress(0);
    setTelemetry(replayFrames[0]);

    function playNextFrame() {
      currentIndex += 1;

      if (currentIndex >= replayFrames.length) {
        stopReplay();
        return;
      }

      setTelemetry(
        replayFrames[currentIndex]
      );

      const progress =
        (currentIndex /
          (replayFrames.length - 1)) *
        100;

      setReplayProgress(progress);

      replayTimerRef.current = setTimeout(
        playNextFrame,
        interval
      );
    }

    replayTimerRef.current = setTimeout(
      playNextFrame,
      interval
    );

    return true;
  }

  function clearTelemetryHistory() {
    stopReplay();
    setTelemetryHistory([]);
  }

  function resetTelemetryState() {
    stopReplay();

    latestLiveTelemetryRef.current = {
      ...initialTelemetry,
      position: {
        ...initialTelemetry.position,
      },
    };

    setTelemetry({
      ...initialTelemetry,
      position: {
        ...initialTelemetry.position,
      },
    });

    setTelemetryHistory([]);
  }

  return {
    telemetry,
    telemetryHistory,
    webSocketStatus,
    isReplaying,
    replayProgress,
    startReplay,
    stopReplay,
    clearTelemetryHistory,
    resetTelemetryState,
  };
}

export default useTelemetry;