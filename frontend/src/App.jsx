import {
  useLayoutEffect,
  useRef,
  useState,
} from "react";

import AICopilot from "./components/AICopilot";
import AIMissionCreator from "./components/AIMissionCreator";
import DashboardHeader from "./components/DashboardHeader";
import DashboardOverview from "./components/DashboardOverview";
import DroneMap from "./components/DroneMap/DroneMap";
import FlightReportPanel from "./components/FlightReportPanel";
import MissionButton from "./components/MissionButton";
import MissionEditor from "./components/MissionEditor";
import ResetButton from "./components/ResetButton";
import TelemetryCharts from "./components/TelemetryCharts";
import TelemetryTimeline from "./components/TelemetryTimeline";

import useFlightReport from "./hooks/useFlightReport";
import useHealth from "./hooks/useHealth";
import useMission from "./hooks/useMission";
import useSystemReset from "./hooks/useSystemReset";
import useTelemetry from "./hooks/useTelemetry";

import {
  askCopilot,
  generateMission,
} from "./services/api";


const initialMissionPayload = {
  name: "Custom Drone Mission",
  commands: [
    {
      type: "TAKEOFF",
      parameters: {
        altitude: 20,
      },
    },
    {
      type: "GOTO",
      parameters: {
        x: 100,
        y: 50,
      },
    },
    {
      type: "HOVER",
      parameters: {
        duration: 5,
      },
    },
    {
      type: "RETURN_HOME",
      parameters: {},
    },
    {
      type: "LAND",
      parameters: {},
    },
  ],
};


function App() {
  const resetScrollPositionReference =
    useRef(0);

  useLayoutEffect(() => {
    if ("scrollRestoration" in window.history) {
      window.history.scrollRestoration =
        "manual";
    }

    const scrollToTop = () => {
      window.scrollTo({
        top: 0,
        left: 0,
        behavior: "auto",
      });
    };

    scrollToTop();

    const animationFrameId =
      window.requestAnimationFrame(
        scrollToTop
      );

    const timeoutId = window.setTimeout(
      scrollToTop,
      50
    );

    window.addEventListener(
      "load",
      scrollToTop
    );

    return () => {
      window.cancelAnimationFrame(
        animationFrameId
      );

      window.clearTimeout(timeoutId);

      window.removeEventListener(
        "load",
        scrollToTop
      );
    };
  }, []);

  const apiStatus = useHealth();

  const [
    missionPayload,
    setMissionPayload,
  ] = useState(initialMissionPayload);

  const [
    aiMessage,
    setAiMessage,
  ] = useState("");

  const [
    isGeneratingMission,
    setIsGeneratingMission,
  ] = useState(false);

  const [
    copilotMessages,
    setCopilotMessages,
  ] = useState([]);

  const [
    isCopilotLoading,
    setIsCopilotLoading,
  ] = useState(false);

  const {
    telemetry,
    telemetryHistory,
    webSocketStatus,
    isReplaying,
    replayProgress,
    startReplay,
    stopReplay,
    clearTelemetryHistory,
    resetTelemetryState,
  } = useTelemetry();

  const {
    missionStatus,
    buttonText,
    isStarting,
    errorMessage,
    handleStartMission,
    resetMissionState,
  } = useMission(
    clearTelemetryHistory,
    missionPayload
  );

  const {
    report,
    reportStatus,
  } = useFlightReport(missionStatus);

  function handleResetComplete() {
    stopReplay();
    resetTelemetryState();
    resetMissionState();
    setAiMessage("");
    setCopilotMessages([]);
  }

  const {
    isResetting,
    resetError,
    handleReset,
  } = useSystemReset(
    handleResetComplete
  );

  async function handleSystemReset() {
    resetScrollPositionReference.current =
      window.scrollY;

    await handleReset();

    const restoreScrollPosition = () => {
      window.scrollTo({
        top:
          resetScrollPositionReference.current,
        left: 0,
        behavior: "auto",
      });
    };

    window.requestAnimationFrame(() => {
      restoreScrollPosition();

      window.requestAnimationFrame(
        restoreScrollPosition
      );
    });

    window.setTimeout(
      restoreScrollPosition,
      100
    );

    window.setTimeout(
      restoreScrollPosition,
      250
    );
  }

  async function handleGenerateMission(
    instruction
  ) {
    try {
      setIsGeneratingMission(true);
      setAiMessage(
        "Görev oluşturuluyor..."
      );

      const generatedMission =
        await generateMission(
          instruction
        );

      setMissionPayload(
        generatedMission
      );

      setAiMessage(
        `${generatedMission.commands.length} ` +
          "komut başarıyla oluşturuldu."
      );
    } catch (error) {
      setAiMessage(
        error instanceof Error
          ? error.message
          : "Görev oluşturulamadı."
      );
    } finally {
      setIsGeneratingMission(false);
    }
  }

  async function handleAskCopilot(
    question
  ) {
    const trimmedQuestion =
      question.trim();

    if (
      !trimmedQuestion ||
      isCopilotLoading
    ) {
      return;
    }

    const userMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmedQuestion,
    };

    setCopilotMessages(
      (currentMessages) => [
        ...currentMessages,
        userMessage,
      ]
    );

    try {
      setIsCopilotLoading(true);

      const response =
        await askCopilot({
          question: trimmedQuestion,
          telemetry,
          mission: {
            name: missionPayload.name,
            status: isReplaying
              ? "Replaying"
              : missionStatus,
            commands:
              missionPayload.commands,
          },
          report:
            reportStatus === "Ready"
              ? report
              : null,
        });

      const assistantMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.answer,
      };

      setCopilotMessages(
        (currentMessages) => [
          ...currentMessages,
          assistantMessage,
        ]
      );
    } catch (error) {
      const copilotErrorMessage =
        error instanceof Error
          ? error.message
          : "Uçuş asistanına ulaşılamadı.";

      const assistantMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content:
          copilotErrorMessage,
        isError: true,
      };

      setCopilotMessages(
        (currentMessages) => [
          ...currentMessages,
          assistantMessage,
        ]
      );
    } finally {
      setIsCopilotLoading(false);
    }
  }

  function handleClearCopilot() {
    setCopilotMessages([]);
  }

  function handleMissionChange(
    nextMission
  ) {
    setMissionPayload(nextMission);
    setAiMessage("");
  }

  function handleReplay() {
    if (isReplaying) {
      stopReplay();
      return;
    }

    startReplay();
  }

  function formatTime(timestamp) {
    if (!timestamp) {
      return "--:--:--";
    }

    return new Date(
      timestamp
    ).toLocaleTimeString();
  }

  const missionIsRunning =
    missionStatus === "Running";

  const missionIsCompleted =
    missionStatus === "Completed";

  const missionIsInvalid =
    !missionPayload.name.trim() ||
    missionPayload.commands.length === 0;

  const controlsDisabled =
    isStarting ||
    isResetting ||
    isGeneratingMission ||
    isReplaying ||
    missionIsRunning;

  const missionButtonDisabled =
    controlsDisabled ||
    missionIsInvalid ||
    apiStatus !== "Healthy ✅";

  const resetButtonDisabled =
    isStarting ||
    isResetting ||
    isGeneratingMission ||
    missionIsRunning ||
    apiStatus !== "Healthy ✅";

  const replayButtonDisabled =
    !isReplaying &&
    (
      !missionIsCompleted ||
      telemetryHistory.length === 0 ||
      isStarting ||
      isResetting ||
      isGeneratingMission ||
      missionIsRunning
    );

  const copilotDisabled =
    apiStatus !== "Healthy ✅" ||
    isResetting;

  return (
    <div className="dashboard">
      <DashboardHeader />

      <DashboardOverview
        apiStatus={apiStatus}
        missionStatus={
          isReplaying
            ? "Replaying"
            : missionStatus
        }
        webSocketStatus={
          webSocketStatus
        }
        telemetry={telemetry}
      />

      {errorMessage && (
        <p className="error-message">
          {errorMessage}
        </p>
      )}

      {resetError && (
        <p className="error-message">
          {resetError}
        </p>
      )}

      <div className="mission-actions">
        <MissionButton
          buttonText={buttonText}
          onClick={
            handleStartMission
          }
          disabled={
            missionButtonDisabled
          }
        />

        <ResetButton
          onClick={
            handleSystemReset
          }
          disabled={
            resetButtonDisabled
          }
          isResetting={isResetting}
        />
      </div>

      <AIMissionCreator
        onGenerateMission={
          handleGenerateMission
        }
        disabled={controlsDisabled}
      />

      {aiMessage && (
        <p className="ai-generation-message">
          {aiMessage}
        </p>
      )}

      <MissionEditor
        mission={missionPayload}
        onMissionChange={
          handleMissionChange
        }
        disabled={controlsDisabled}
      />

      <AICopilot
        messages={copilotMessages}
        isLoading={
          isCopilotLoading
        }
        disabled={copilotDisabled}
        onAsk={handleAskCopilot}
        onClear={
          handleClearCopilot
        }
      />

      <DroneMap
        telemetry={telemetry}
        telemetryHistory={
          telemetryHistory
        }
        missionCommands={
          missionPayload.commands
        }
      />

      <section className="replay-section">
        <div className="replay-header">
          <div>
            <p className="section-label">
              MISSION PLAYBACK
            </p>

            <h2>Flight Replay</h2>
          </div>

          <span>
            {Math.round(
              replayProgress
            )}
            %
          </span>
        </div>

        <p className="replay-description">
          Replay the latest mission
          using the recorded telemetry
          data.
        </p>

        <div className="replay-progress">
          <div
            className="replay-progress-fill"
            style={{
              width:
                `${replayProgress}%`,
            }}
          />
        </div>

        <button
          className="replay-button"
          type="button"
          onClick={handleReplay}
          disabled={
            replayButtonDisabled
          }
        >
          {isReplaying
            ? "Stop Replay"
            : "Replay Mission"}
        </button>

        {!missionIsCompleted &&
          !isReplaying && (
            <p className="replay-hint">
              Complete a mission to
              enable replay.
            </p>
          )}

        {missionIsCompleted &&
          telemetryHistory.length ===
            0 &&
          !isReplaying && (
            <p className="replay-hint">
              No telemetry recording is
              available.
            </p>
          )}
      </section>

      <TelemetryCharts
        telemetryHistory={
          telemetryHistory
        }
      />

      <FlightReportPanel
        report={report}
        reportStatus={reportStatus}
      />

      <TelemetryTimeline
        telemetryHistory={
          telemetryHistory
        }
        formatTime={formatTime}
      />
    </div>
  );
}

export default App;