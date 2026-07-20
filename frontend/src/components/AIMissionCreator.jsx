import { useState } from "react";


function AIMissionCreator({
  onGenerateMission,
  disabled = false,
}) {
  const [instruction, setInstruction] =
    useState("");

  const [errorMessage, setErrorMessage] =
    useState("");

  function handleGenerate() {
    const trimmedInstruction =
      instruction.trim();

    if (!trimmedInstruction) {
      setErrorMessage(
        "Please enter a mission instruction."
      );

      return;
    }

    setErrorMessage("");

    if (onGenerateMission) {
      onGenerateMission(trimmedInstruction);
    }
  }

  return (
    <section className="ai-mission-section">
      <div className="ai-mission-header">
        <div>
          <p className="section-label">
            AI PILOT ASSISTANT
          </p>

          <h2>AI Mission Creator</h2>
        </div>

        <span>Natural Language</span>
      </div>

      <p className="ai-mission-description">
        Describe the mission in natural language.
        The assistant will convert it into drone
        commands.
      </p>

      <label className="ai-instruction-field">
        <span>Mission Instruction</span>

        <textarea
          value={instruction}
          onChange={(event) =>
            setInstruction(event.target.value)
          }
          disabled={disabled}
          rows={5}
          placeholder={
            "Take off to 20 meters, go to " +
            "x 100 y 50, hover for 5 seconds, " +
            "return home and land."
          }
        />
      </label>

      {errorMessage && (
        <p className="ai-mission-error">
          {errorMessage}
        </p>
      )}

      <div className="ai-mission-examples">
        <span>Example:</span>

        <button
          type="button"
          disabled={disabled}
          onClick={() =>
            setInstruction(
              "Take off to 15 meters, go to " +
              "x 40 y 25, hover for 3 seconds, " +
              "return home and land."
            )
          }
        >
          Inspection mission
        </button>

        <button
          type="button"
          disabled={disabled}
          onClick={() =>
            setInstruction(
              "Take off to 25 meters, go to " +
              "x 80 y 40, then go to x 120 y 70, " +
              "return home and land."
            )
          }
        >
          Two-point mission
        </button>
      </div>

      <button
        className="generate-mission-button"
        type="button"
        onClick={handleGenerate}
        disabled={disabled}
      >
        Generate Mission
      </button>
    </section>
  );
}

export default AIMissionCreator;