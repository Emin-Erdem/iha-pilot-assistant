import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";


const DEFAULT_MINIMUM_ZOOM = 1;
const DEFAULT_MAXIMUM_ZOOM = 4;
const DEFAULT_ZOOM_STEP = 0.25;
const DEFAULT_FOLLOW_ZOOM_LEVEL = 2;


function useMapNavigation({
  mapWidth,
  mapHeight,
  droneX,
  droneY,
  minimumZoom = DEFAULT_MINIMUM_ZOOM,
  maximumZoom = DEFAULT_MAXIMUM_ZOOM,
  zoomStep = DEFAULT_ZOOM_STEP,
  followZoomLevel =
    DEFAULT_FOLLOW_ZOOM_LEVEL,
}) {
  const svgReference = useRef(null);

  const [zoomLevel, setZoomLevel] =
    useState(minimumZoom);

  const [panPosition, setPanPosition] =
    useState({
      x: 0,
      y: 0,
    });

  const [dragState, setDragState] =
    useState(null);

  const [
    isFollowingDrone,
    setIsFollowingDrone,
  ] = useState(false);


  const limitZoom = useCallback(
    (nextZoom) =>
      Math.min(
        maximumZoom,
        Math.max(
          minimumZoom,
          nextZoom
        )
      ),
    [
      maximumZoom,
      minimumZoom,
    ]
  );


  const limitPan = useCallback(
    (
      nextPan,
      nextZoom = zoomLevel
    ) => {
      if (nextZoom <= minimumZoom) {
        return {
          x: 0,
          y: 0,
        };
      }

      const visibleWidth =
        mapWidth / nextZoom;

      const visibleHeight =
        mapHeight / nextZoom;

      const maximumPanX =
        (mapWidth - visibleWidth) / 2;

      const maximumPanY =
        (mapHeight - visibleHeight) / 2;

      return {
        x: Math.min(
          maximumPanX,
          Math.max(
            -maximumPanX,
            Number(nextPan?.x ?? 0)
          )
        ),

        y: Math.min(
          maximumPanY,
          Math.max(
            -maximumPanY,
            Number(nextPan?.y ?? 0)
          )
        ),
      };
    },
    [
      mapHeight,
      mapWidth,
      minimumZoom,
      zoomLevel,
    ]
  );


  const getDroneCenteredPan =
    useCallback(
      (
        nextDroneX,
        nextDroneY,
        nextZoom = zoomLevel
      ) =>
        limitPan(
          {
            x:
              mapWidth / 2 -
              nextDroneX,

            y:
              mapHeight / 2 -
              nextDroneY,
          },
          nextZoom
        ),
      [
        limitPan,
        mapHeight,
        mapWidth,
        zoomLevel,
      ]
    );


  const changeZoom = useCallback(
    (nextZoomValue) => {
      const nextZoom =
        limitZoom(nextZoomValue);

      setZoomLevel(nextZoom);

      setPanPosition(
        (currentPan) => {
          if (isFollowingDrone) {
            return getDroneCenteredPan(
              droneX,
              droneY,
              nextZoom
            );
          }

          return limitPan(
            currentPan,
            nextZoom
          );
        }
      );
    },
    [
      droneX,
      droneY,
      getDroneCenteredPan,
      isFollowingDrone,
      limitPan,
      limitZoom,
    ]
  );


  const handleZoomIn =
    useCallback(() => {
      changeZoom(
        zoomLevel + zoomStep
      );
    }, [
      changeZoom,
      zoomLevel,
      zoomStep,
    ]);


  const handleZoomOut =
    useCallback(() => {
      changeZoom(
        zoomLevel - zoomStep
      );
    }, [
      changeZoom,
      zoomLevel,
      zoomStep,
    ]);


  const handleMapReset =
    useCallback(() => {
      setZoomLevel(minimumZoom);

      setPanPosition({
        x: 0,
        y: 0,
      });

      setDragState(null);
      setIsFollowingDrone(false);
    }, [minimumZoom]);


  const handleFollowDrone =
    useCallback(() => {
      if (isFollowingDrone) {
        setIsFollowingDrone(false);
        return;
      }

      const nextZoom =
        zoomLevel <= minimumZoom
          ? limitZoom(
              followZoomLevel
            )
          : zoomLevel;

      setZoomLevel(nextZoom);

      setPanPosition(
        getDroneCenteredPan(
          droneX,
          droneY,
          nextZoom
        )
      );

      setDragState(null);
      setIsFollowingDrone(true);
    }, [
      droneX,
      droneY,
      followZoomLevel,
      getDroneCenteredPan,
      isFollowingDrone,
      limitZoom,
      minimumZoom,
      zoomLevel,
    ]);


  const handleWheel =
    useCallback(
      (event) => {
        event.preventDefault();

        const zoomDirection =
          event.deltaY < 0
            ? zoomStep
            : -zoomStep;

        changeZoom(
          zoomLevel +
            zoomDirection
        );
      },
      [
        changeZoom,
        zoomLevel,
        zoomStep,
      ]
    );


  const handlePointerDown =
    useCallback(
      (event) => {
        if (event.button !== 0) {
          return;
        }

        if (isFollowingDrone) {
          setIsFollowingDrone(false);
        }

        event.currentTarget.setPointerCapture(
          event.pointerId
        );

        setDragState({
          pointerId:
            event.pointerId,

          clientX:
            event.clientX,

          clientY:
            event.clientY,

          startingPanX:
            panPosition.x,

          startingPanY:
            panPosition.y,
        });
      },
      [
        isFollowingDrone,
        panPosition.x,
        panPosition.y,
      ]
    );


  const handlePointerMove =
    useCallback(
      (event) => {
        if (
          !dragState ||
          dragState.pointerId !==
            event.pointerId
        ) {
          return;
        }

        const svgElement =
          svgReference.current;

        if (!svgElement) {
          return;
        }

        const bounds =
          svgElement.getBoundingClientRect();

        if (
          bounds.width === 0 ||
          bounds.height === 0
        ) {
          return;
        }

        const visibleWidth =
          mapWidth / zoomLevel;

        const visibleHeight =
          mapHeight / zoomLevel;

        const horizontalDifference =
          event.clientX -
          dragState.clientX;

        const verticalDifference =
          event.clientY -
          dragState.clientY;

        const horizontalMapDifference =
          horizontalDifference *
          (
            visibleWidth /
            bounds.width
          );

        const verticalMapDifference =
          verticalDifference *
          (
            visibleHeight /
            bounds.height
          );

        const nextPan = {
          x:
            dragState.startingPanX +
            horizontalMapDifference,

          y:
            dragState.startingPanY +
            verticalMapDifference,
        };

        setPanPosition(
          limitPan(nextPan)
        );
      },
      [
        dragState,
        limitPan,
        mapHeight,
        mapWidth,
        zoomLevel,
      ]
    );


  const finishDragging =
    useCallback(
      (event) => {
        if (
          !dragState ||
          dragState.pointerId !==
            event.pointerId
        ) {
          return;
        }

        if (
          event.currentTarget.hasPointerCapture(
            event.pointerId
          )
        ) {
          event.currentTarget.releasePointerCapture(
            event.pointerId
          );
        }

        setDragState(null);
      },
      [dragState]
    );


  /*
   * Takip modu açıksa drone hareket ettikçe
   * harita görünümü drone merkezli kalır.
   */
  useEffect(() => {
    if (!isFollowingDrone) {
      return;
    }

    setPanPosition(
      getDroneCenteredPan(
        droneX,
        droneY,
        zoomLevel
      )
    );
  }, [
    droneX,
    droneY,
    getDroneCenteredPan,
    isFollowingDrone,
    zoomLevel,
  ]);


  /*
   * Zoom değiştiğinde mevcut pan değerinin
   * yeni sınırlar içerisinde kalmasını sağlar.
   */
  useEffect(() => {
    setPanPosition(
      (currentPan) =>
        limitPan(
          currentPan,
          zoomLevel
        )
    );
  }, [
    limitPan,
    zoomLevel,
  ]);


  const visibleWidth =
    mapWidth / zoomLevel;

  const visibleHeight =
    mapHeight / zoomLevel;

  const viewBoxX =
    (
      mapWidth -
      visibleWidth
    ) /
      2 -
    panPosition.x;

  const viewBoxY =
    (
      mapHeight -
      visibleHeight
    ) /
      2 -
    panPosition.y;

  const mapViewBox =
    `${viewBoxX} ${viewBoxY} ` +
    `${visibleWidth} ${visibleHeight}`;

  const isDragging =
    dragState !== null;

  const canZoomIn =
    zoomLevel < maximumZoom;

  const canZoomOut =
    zoomLevel > minimumZoom;

  const canReset =
    zoomLevel !== minimumZoom ||
    panPosition.x !== 0 ||
    panPosition.y !== 0 ||
    isFollowingDrone;


  return {
    svgReference,

    zoomLevel,
    panPosition,
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
  };
}


export default useMapNavigation;