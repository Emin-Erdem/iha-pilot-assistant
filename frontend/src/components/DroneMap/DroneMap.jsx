import {
  useMemo,
} from "react";

import useDroneAnimation from "./useDroneAnimation";
import useMapNavigation from "./useMapNavigation";

import "./DroneMap.css";


const MAP_WIDTH = 1000;
const MAP_HEIGHT = 500;
const MAP_PADDING = 55;

const HOME_POSITION = {
  x: 0,
  y: 0,
};


function normalizePosition(position) {
  return {
    x: Number(position?.x ?? 0),
    y: Number(position?.y ?? 0),
  };
}


function positionsAreEqual(
  firstPosition,
  secondPosition
) {
  return (
    firstPosition.x === secondPosition.x &&
    firstPosition.y === secondPosition.y
  );
}


function removeConsecutiveDuplicates(
  positions
) {
  return positions.filter(
    (position, index) => {
      if (index === 0) {
        return true;
      }

      return !positionsAreEqual(
        position,
        positions[index - 1]
      );
    }
  );
}


function calculateDistance(
  firstPosition,
  secondPosition
) {
  return Math.hypot(
    secondPosition.x -
      firstPosition.x,
    secondPosition.y -
      firstPosition.y
  );
}


function DroneMap({
  telemetry,
  telemetryHistory = [],
  missionCommands = [],
}) {
  const currentPosition = useMemo(
    () =>
      normalizePosition(
        telemetry?.position
      ),
    [
      telemetry?.position?.x,
      telemetry?.position?.y,
    ]
  );

  const {
    animatedPosition,
    droneHeading,
  } = useDroneAnimation(
    currentPosition
  );

  const displayedPosition = useMemo(
    () =>
      normalizePosition(
        animatedPosition
      ),
    [
      animatedPosition?.x,
      animatedPosition?.y,
    ]
  );

  const historyPositions =
    useMemo(
      () =>
        telemetryHistory.map(
          (item) =>
            normalizePosition(
              item?.position
            )
        ),
      [telemetryHistory]
    );

  const completedRoutePositions =
    useMemo(
      () =>
        removeConsecutiveDuplicates([
          HOME_POSITION,
          ...historyPositions,
          currentPosition,
        ]),
      [
        historyPositions,
        currentPosition,
      ]
    );

  const plannedWaypoints =
    useMemo(
      () =>
        missionCommands
          .filter(
            (command) =>
              command?.type ===
              "GOTO"
          )
          .map(
            (
              command,
              index
            ) => ({
              id:
                `waypoint-${index}`,
              x: Number(
                command
                  ?.parameters
                  ?.x ?? 0
              ),
              y: Number(
                command
                  ?.parameters
                  ?.y ?? 0
              ),
            })
          ),
      [missionCommands]
    );

  const missionReturnsHome =
    useMemo(
      () =>
        missionCommands.some(
          (command) =>
            command?.type ===
            "RETURN_HOME"
        ),
      [missionCommands]
    );

  const plannedRoutePositions =
    useMemo(() => {
      const route = [
        HOME_POSITION,
        ...plannedWaypoints,
      ];

      if (
        missionReturnsHome &&
        route.length > 1 &&
        !positionsAreEqual(
          route[
            route.length - 1
          ],
          HOME_POSITION
        )
      ) {
        route.push(
          HOME_POSITION
        );
      }

      return removeConsecutiveDuplicates(
        route
      );
    }, [
      plannedWaypoints,
      missionReturnsHome,
    ]);

  const mapPositions = useMemo(
    () => [
      HOME_POSITION,
      ...plannedRoutePositions,
      ...completedRoutePositions,
      displayedPosition,
      currentPosition,
    ],
    [
      plannedRoutePositions,
      completedRoutePositions,
      displayedPosition,
      currentPosition,
    ]
  );

  const xValues =
    mapPositions.map(
      (position) => position.x
    );

  const yValues =
    mapPositions.map(
      (position) => position.y
    );

  const minimumX = Math.min(
    ...xValues,
    0
  );

  const maximumX = Math.max(
    ...xValues,
    100
  );

  const minimumY = Math.min(
    ...yValues,
    0
  );

  const maximumY = Math.max(
    ...yValues,
    50
  );

  const horizontalRange =
    Math.max(
      maximumX - minimumX,
      1
    );

  const verticalRange =
    Math.max(
      maximumY - minimumY,
      1
    );

  function convertX(xPosition) {
    return (
      MAP_PADDING +
      (
        (xPosition - minimumX) /
        horizontalRange
      ) *
        (
          MAP_WIDTH -
          MAP_PADDING * 2
        )
    );
  }

  function convertY(yPosition) {
    return (
      MAP_HEIGHT -
      MAP_PADDING -
      (
        (yPosition - minimumY) /
        verticalRange
      ) *
        (
          MAP_HEIGHT -
          MAP_PADDING * 2
        )
    );
  }

  const droneX = convertX(
    displayedPosition.x
  );

  const droneY = convertY(
    displayedPosition.y
  );

  const {
    svgReference,
    zoomLevel,
    mapViewBox,
    isDragging,
    isFollowingDrone,
    canZoomIn,
    canZoomOut,
    canReset,
    handleZoomIn,
    handleZoomOut,
    handleMapReset,
    handleFollowDrone,
    handleWheel,
    handlePointerDown,
    handlePointerMove,
    finishDragging,
  } = useMapNavigation({
    mapWidth: MAP_WIDTH,
    mapHeight: MAP_HEIGHT,
    droneX,
    droneY,
  });

  const plannedDistance =
    useMemo(
      () =>
        plannedRoutePositions.reduce(
          (
            total,
            position,
            index
          ) => {
            if (index === 0) {
              return total;
            }

            return (
              total +
              calculateDistance(
                plannedRoutePositions[
                  index - 1
                ],
                position
              )
            );
          },
          0
        ),
      [plannedRoutePositions]
    );

  const homeX = convertX(
    HOME_POSITION.x
  );

  const homeY = convertY(
    HOME_POSITION.y
  );

  const finalPlannedPosition =
    plannedRoutePositions[
      plannedRoutePositions.length -
        1
    ] ?? HOME_POSITION;

  const finalPlannedPositionIsHome =
    positionsAreEqual(
      finalPlannedPosition,
      HOME_POSITION
    );

  const modeText =
    telemetry?.mode ?? "IDLE";

  const altitude = Number(
    telemetry?.altitude ?? 0
  );

  const batteryLevel = Number(
    telemetry?.battery_level ?? 0
  );

  const speed = Number(
    telemetry?.speed ?? 0
  );

  return (
    <section className="drone-map-section">
      <div className="drone-map-header">
        <div>
          <p className="section-label">
            CANLI KONUM
          </p>

          <h2>
            Drone Uçuş Haritası
          </h2>
        </div>

        <span>
          X:{" "}
          {displayedPosition.x.toFixed(
            1
          )}
          {" · "}
          Y:{" "}
          {displayedPosition.y.toFixed(
            1
          )}
        </span>
      </div>

      <div className="drone-map">
        <div className="map-navigation-bar">
          <div className="map-navigation-info">
            <span>
              Harita görünümü
            </span>

            <strong>
              %
              {Math.round(
                zoomLevel * 100
              )}
            </strong>

            {isFollowingDrone && (
              <strong className="map-follow-status">
                DRONE TAKİP EDİLİYOR
              </strong>
            )}
          </div>

          <div className="map-navigation-buttons">
            <button
              type="button"
              onClick={handleZoomOut}
              disabled={!canZoomOut}
              aria-label="Haritayı uzaklaştır"
              title="Uzaklaştır"
            >
              −
            </button>

            <button
              type="button"
              onClick={handleZoomIn}
              disabled={!canZoomIn}
              aria-label="Haritayı yakınlaştır"
              title="Yakınlaştır"
            >
              +
            </button>

            <button
              type="button"
              className={
                isFollowingDrone
                  ? "map-follow-button map-follow-button-active"
                  : "map-follow-button"
              }
              onClick={
                handleFollowDrone
              }
              aria-pressed={
                isFollowingDrone
              }
              title={
                isFollowingDrone
                  ? "Drone takibini kapat"
                  : "Drone konumunu takip et"
              }
            >
              {isFollowingDrone
                ? "Takibi Kapat"
                : "Drone’u Takip Et"}
            </button>

            <button
              type="button"
              onClick={handleMapReset}
              disabled={!canReset}
            >
              Sıfırla
            </button>
          </div>
        </div>

        <svg
          ref={svgReference}
          viewBox={mapViewBox}
          role="img"
          aria-label="Canlı drone konum haritası"
          onWheel={handleWheel}
          onPointerDown={
            handlePointerDown
          }
          onPointerMove={
            handlePointerMove
          }
          onPointerUp={
            finishDragging
          }
          onPointerCancel={
            finishDragging
          }
          onDoubleClick={
            handleMapReset
          }
          style={{
            cursor: isDragging
              ? "grabbing"
              : "grab",
            touchAction: "none",
            userSelect: "none",
          }}
        >
          <defs>
            <pattern
              id="grid"
              width="50"
              height="50"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 50 0 L 0 0 0 50"
                className="map-grid-line"
                fill="none"
              />
            </pattern>

            <filter id="droneGlow">
              <feGaussianBlur
                stdDeviation="7"
                result="blur"
              />

              <feMerge>
                <feMergeNode in="blur" />

                <feMergeNode
                  in="SourceGraphic"
                />
              </feMerge>
            </filter>

            <filter id="pointGlow">
              <feGaussianBlur
                stdDeviation="3"
                result="blur"
              />

              <feMerge>
                <feMergeNode in="blur" />

                <feMergeNode
                  in="SourceGraphic"
                />
              </feMerge>
            </filter>
          </defs>

          <rect
            width={MAP_WIDTH}
            height={MAP_HEIGHT}
            className="map-background"
          />

          <rect
            width={MAP_WIDTH}
            height={MAP_HEIGHT}
            fill="url(#grid)"
          />

          {plannedRoutePositions
            .slice(1)
            .map(
              (
                position,
                index
              ) => {
                const previousPosition =
                  plannedRoutePositions[
                    index
                  ];

                return (
                  <line
                    key={
                      `planned-` +
                      `${index}-` +
                      `${previousPosition.x}-` +
                      `${previousPosition.y}-` +
                      `${position.x}-` +
                      `${position.y}`
                    }
                    x1={convertX(
                      previousPosition.x
                    )}
                    y1={convertY(
                      previousPosition.y
                    )}
                    x2={convertX(
                      position.x
                    )}
                    y2={convertY(
                      position.y
                    )}
                    className="flight-path flight-path-planned"
                  />
                );
              }
            )}

          {completedRoutePositions
            .slice(1)
            .map(
              (
                position,
                index
              ) => {
                const previousPosition =
                  completedRoutePositions[
                    index
                  ];

                return (
                  <line
                    key={
                      `completed-` +
                      `${index}-` +
                      `${previousPosition.x}-` +
                      `${previousPosition.y}-` +
                      `${position.x}-` +
                      `${position.y}`
                    }
                    x1={convertX(
                      previousPosition.x
                    )}
                    y1={convertY(
                      previousPosition.y
                    )}
                    x2={convertX(
                      position.x
                    )}
                    y2={convertY(
                      position.y
                    )}
                    className="flight-path flight-path-completed"
                  />
                );
              }
            )}

          <circle
            cx={homeX}
            cy={homeY}
            r="13"
            className="home-point"
          />

          <circle
            cx={homeX}
            cy={homeY}
            r="25"
            className="home-point-ring"
          />

          <text
            x={homeX + 20}
            y={homeY - 18}
            className="map-label"
          >
            ANA ÜS
          </text>

          {plannedWaypoints.map(
            (position, index) => {
              const waypointX =
                convertX(
                  position.x
                );

              const waypointY =
                convertY(
                  position.y
                );

              return (
                <g
                  key={position.id}
                  className="waypoint-marker"
                  transform={
                    `translate(` +
                    `${waypointX} ` +
                    `${waypointY})`
                  }
                >
                  <circle
                    r="13"
                    className="waypoint-circle"
                    filter="url(#pointGlow)"
                  />

                  <text
                    y="4"
                    textAnchor="middle"
                    className="waypoint-number"
                  >
                    {index + 1}
                  </text>
                </g>
              );
            }
          )}

          {plannedRoutePositions.length >
            1 &&
            !finalPlannedPositionIsHome && (
              <g
                className="end-marker"
                transform={
                  `translate(` +
                  `${convertX(
                    finalPlannedPosition.x
                  )} ` +
                  `${convertY(
                    finalPlannedPosition.y
                  )})`
                }
              >
                <path
                  d="M 0 14 L 0 -18 L 25 -10 L 0 -2"
                  className="end-flag"
                />

                <circle
                  cy="15"
                  r="4"
                  className="end-point"
                />
              </g>
            )}

          <g
            className="drone-position-layer"
            transform={
              `translate(` +
              `${droneX} ` +
              `${droneY})`
            }
          >
            <g className="drone-radar">
              <circle
                r="36"
                className="drone-radar-ring drone-radar-ring-one"
              />

              <circle
                r="52"
                className="drone-radar-ring drone-radar-ring-two"
              />
            </g>

            <g
              className="drone-marker"
              transform={
                `rotate(` +
                `${droneHeading})`
              }
              filter="url(#droneGlow)"
            >
              <circle
                r="22"
                className="drone-marker-ring"
              />

              <circle
                r="10"
                className="drone-marker-core"
              />

              <path
                d="M -25 0 L 25 0 M 0 -25 L 0 25"
                className="drone-marker-arms"
              />

              <circle
                cx="-25"
                cy="0"
                r="5"
                className="drone-propeller"
              />

              <circle
                cx="25"
                cy="0"
                r="5"
                className="drone-propeller"
              />

              <circle
                cx="0"
                cy="-25"
                r="5"
                className="drone-propeller"
              />

              <circle
                cx="0"
                cy="25"
                r="5"
                className="drone-propeller"
              />

              <path
                d="M 0 -38 L -8 -25 L 8 -25 Z"
                className="drone-direction-indicator"
              />
            </g>
          </g>
        </svg>

        <div className="map-hud">
          <div>
            <span>Waypoint</span>

            <strong>
              {plannedWaypoints.length}
            </strong>
          </div>

          <div>
            <span>
              Planlı Mesafe
            </span>

            <strong>
              {plannedDistance.toFixed(
                1
              )}{" "}
              m
            </strong>
          </div>

          <div>
            <span>İrtifa</span>

            <strong>
              {altitude.toFixed(1)} m
            </strong>
          </div>

          <div>
            <span>Hız</span>

            <strong>
              {speed.toFixed(1)} m/s
            </strong>
          </div>

          <div>
            <span>Batarya</span>

            <strong>
              %
              {batteryLevel.toFixed(
                0
              )}
            </strong>
          </div>

          <div>
            <span>Mod</span>

            <strong>
              {modeText}
            </strong>
          </div>
        </div>

        <div className="map-legend">
          <span>
            <i className="legend-home" />
            Ana üs
          </span>

          <span>
            <i className="legend-drone" />
            Drone
          </span>

          <span>
            <i className="legend-planned-path" />
            Planlanan rota
          </span>

          <span>
            <i className="legend-path" />
            Geçilen rota
          </span>

          <span>
            <i className="legend-waypoint" />
            Waypoint
          </span>

          <span>
            <i className="legend-end" />
            Bitiş
          </span>
        </div>
      </div>
    </section>
  );
}


export default DroneMap;