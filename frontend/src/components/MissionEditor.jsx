function createCommand(type = "TAKEOFF") {
  return {
    type,
    parameters: getDefaultParameters(type),
  };
}

function getDefaultParameters(commandType) {
  if (commandType === "TAKEOFF") {
    return {
      altitude: 20,
    };
  }

  if (commandType === "GOTO") {
    return {
      x: 0,
      y: 0,
    };
  }

  if (commandType === "HOVER") {
    return {
      duration: 5,
    };
  }

  return {};
}

function MissionEditor({
  mission,
  onMissionChange,
  disabled = false,
}) {
  const commands = mission?.commands ?? [];

  function updateMission(nextName, nextCommands) {
    onMissionChange({
      name: nextName,
      commands: nextCommands,
    });
  }

  function handleMissionNameChange(event) {
    updateMission(
      event.target.value,
      commands
    );
  }

  function handleNumberFocus(event) {
    event.currentTarget.select();
  }

  function handleInputKeyDown(event) {
    if (event.key === "Enter") {
      event.preventDefault();
      event.currentTarget.blur();
    }
  }

  function updateCommandType(
    commandIndex,
    newType
  ) {
    const updatedCommands = commands.map(
      (command, index) => {
        if (index !== commandIndex) {
          return command;
        }

        return {
          type: newType,
          parameters: getDefaultParameters(
            newType
          ),
        };
      }
    );

    updateMission(
      mission.name,
      updatedCommands
    );
  }

  function updateParameter(
    commandIndex,
    parameterName,
    value
  ) {
    const numericValue = Number(value);

    if (!Number.isFinite(numericValue)) {
      return;
    }

    const updatedCommands = commands.map(
      (command, index) => {
        if (index !== commandIndex) {
          return command;
        }

        return {
          ...command,
          parameters: {
            ...command.parameters,
            [parameterName]: numericValue,
          },
        };
      }
    );

    updateMission(
      mission.name,
      updatedCommands
    );
  }

  function addCommand() {
    updateMission(
      mission.name,
      [
        ...commands,
        createCommand(),
      ]
    );
  }

  function removeCommand(commandIndex) {
    const updatedCommands = commands.filter(
      (_, index) => index !== commandIndex
    );

    updateMission(
      mission.name,
      updatedCommands
    );
  }

  return (
    <section className="mission-editor-section">
      <div className="mission-editor-header">
        <div>
          <p className="section-label">
            MISSION PLANNING
          </p>

          <h2>Mission Editor</h2>
        </div>

        <span>
          {commands.length} commands
        </span>
      </div>

      <label className="mission-name-field">
        <span>Mission Name</span>

        <input
          type="text"
          value={mission.name}
          disabled={disabled}
          onChange={handleMissionNameChange}
          onKeyDown={handleInputKeyDown}
        />
      </label>

      <div className="command-list">
        {commands.map((command, index) => (
          <article
            className="command-item"
            key={`${command.type}-${index}`}
          >
            <div className="command-number">
              {index + 1}
            </div>

            <div className="command-content">
              <label>
                <span>Command</span>

                <select
                  value={command.type}
                  disabled={disabled}
                  onChange={(event) =>
                    updateCommandType(
                      index,
                      event.target.value
                    )
                  }
                >
                  <option value="TAKEOFF">
                    TAKEOFF
                  </option>

                  <option value="GOTO">
                    GOTO
                  </option>

                  <option value="HOVER">
                    HOVER
                  </option>

                  <option value="RETURN_HOME">
                    RETURN_HOME
                  </option>

                  <option value="LAND">
                    LAND
                  </option>
                </select>
              </label>

              {command.type === "TAKEOFF" && (
                <label>
                  <span>Altitude</span>

                  <input
                    type="number"
                    value={
                      command.parameters.altitude
                    }
                    disabled={disabled}
                    onFocus={handleNumberFocus}
                    onKeyDown={handleInputKeyDown}
                    onChange={(event) =>
                      updateParameter(
                        index,
                        "altitude",
                        event.target.value
                      )
                    }
                  />
                </label>
              )}

              {command.type === "GOTO" && (
                <>
                  <label>
                    <span>X Position</span>

                    <input
                      type="number"
                      value={command.parameters.x}
                      disabled={disabled}
                      onFocus={handleNumberFocus}
                      onKeyDown={handleInputKeyDown}
                      onChange={(event) =>
                        updateParameter(
                          index,
                          "x",
                          event.target.value
                        )
                      }
                    />
                  </label>

                  <label>
                    <span>Y Position</span>

                    <input
                      type="number"
                      value={command.parameters.y}
                      disabled={disabled}
                      onFocus={handleNumberFocus}
                      onKeyDown={handleInputKeyDown}
                      onChange={(event) =>
                        updateParameter(
                          index,
                          "y",
                          event.target.value
                        )
                      }
                    />
                  </label>
                </>
              )}

              {command.type === "HOVER" && (
                <label>
                  <span>Duration</span>

                  <input
                    type="number"
                    value={
                      command.parameters.duration
                    }
                    disabled={disabled}
                    onFocus={handleNumberFocus}
                    onKeyDown={handleInputKeyDown}
                    onChange={(event) =>
                      updateParameter(
                        index,
                        "duration",
                        event.target.value
                      )
                    }
                  />
                </label>
              )}
            </div>

            <button
              className="remove-command-button"
              type="button"
              disabled={
                disabled ||
                commands.length === 1
              }
              onClick={() =>
                removeCommand(index)
              }
            >
              Remove
            </button>
          </article>
        ))}
      </div>

      <button
        className="add-command-button"
        type="button"
        onClick={addCommand}
        disabled={disabled}
      >
        Add Command
      </button>
    </section>
  );
}

export default MissionEditor;