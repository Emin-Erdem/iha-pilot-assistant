import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";


const DEFAULT_TELEMETRY_INTERVAL = 1000;
const MINIMUM_ANIMATION_DURATION = 180;
const MAXIMUM_ANIMATION_DURATION = 1800;
const TELEMETRY_DURATION_MULTIPLIER = 0.92;
const MINIMUM_MOVEMENT_DISTANCE = 0.05;
const TELEMETRY_INTERVAL_SMOOTHING = 0.25;


/*
 * Gelen koordinatı güvenli bir sayısal
 * pozisyon nesnesine dönüştürür.
 */
function normalizePosition(position) {
  const x = Number(position?.x ?? 0);
  const y = Number(position?.y ?? 0);

  return {
    x: Number.isFinite(x) ? x : 0,
    y: Number.isFinite(y) ? y : 0,
  };
}


/*
 * İki koordinatın aynı olup olmadığını
 * kontrol eder.
 */
function positionsAreEqual(
  firstPosition,
  secondPosition
) {
  return (
    firstPosition.x === secondPosition.x &&
    firstPosition.y === secondPosition.y
  );
}


/*
 * İki koordinat arasındaki mesafeyi
 * hesaplar.
 */
function calculateDistance(
  firstPosition,
  secondPosition
) {
  return Math.hypot(
    secondPosition.x - firstPosition.x,
    secondPosition.y - firstPosition.y
  );
}


/*
 * Drone'un hareket yönünü derece
 * cinsinden hesaplar.
 */
function calculateHeading(
  firstPosition,
  secondPosition
) {
  const xDifference =
    secondPosition.x - firstPosition.x;

  const yDifference =
    secondPosition.y - firstPosition.y;

  if (
    xDifference === 0 &&
    yDifference === 0
  ) {
    return null;
  }

  return (
    Math.atan2(
      -yDifference,
      xDifference
    ) *
      (180 / Math.PI) +
    90
  );
}


/*
 * Animasyon süresini güvenli sınırlar
 * içerisinde tutar.
 */
function limitAnimationDuration(duration) {
  return Math.min(
    MAXIMUM_ANIMATION_DURATION,
    Math.max(
      MINIMUM_ANIMATION_DURATION,
      duration
    )
  );
}


/*
 * İki koordinat arasında doğrusal bir
 * ara konum hesaplar.
 *
 * Doğrusal ilerleme özellikle kullanılıyor.
 * Her telemetri parçasında tekrar hızlanıp
 * yavaşlama olmadığı için dur-kalk etkisi
 * oluşmaz.
 */
function interpolatePosition(
  startingPosition,
  targetPosition,
  progress
) {
  return {
    x:
      startingPosition.x +
      (
        targetPosition.x -
        startingPosition.x
      ) *
        progress,

    y:
      startingPosition.y +
      (
        targetPosition.y -
        startingPosition.y
      ) *
        progress,
  };
}


function useDroneAnimation(targetPosition) {
  const initialPosition =
    normalizePosition(targetPosition);

  const [
    animatedPosition,
    setAnimatedPosition,
  ] = useState(initialPosition);

  const [
    droneHeading,
    setDroneHeading,
  ] = useState(0);

  const [
    isDroneMoving,
    setIsDroneMoving,
  ] = useState(false);

  const animationFrameReference =
    useRef(null);

  const currentPositionReference =
    useRef(initialPosition);

  const animationStartPositionReference =
    useRef(initialPosition);

  const animationTargetReference =
    useRef(initialPosition);

  const animationStartTimeReference =
    useRef(null);

  const animationDurationReference =
    useRef(DEFAULT_TELEMETRY_INTERVAL);

  const lastReceivedTargetReference =
    useRef(initialPosition);

  const lastTargetReceivedTimeReference =
    useRef(null);

  const estimatedTelemetryIntervalReference =
    useRef(DEFAULT_TELEMETRY_INTERVAL);

  const isInitializedReference =
    useRef(false);

  const isAnimatingReference =
    useRef(false);

  const isMountedReference =
    useRef(true);


  /*
   * React state'i ile animasyonda kullanılan
   * güncel pozisyon referansını birlikte
   * günceller.
   */
  const updateAnimatedPosition =
    useCallback((nextPosition) => {
      const normalizedPosition =
        normalizePosition(nextPosition);

      currentPositionReference.current =
        normalizedPosition;

      if (isMountedReference.current) {
        setAnimatedPosition(
          normalizedPosition
        );
      }
    }, []);


  /*
   * Çalışan animasyon karesini güvenli
   * şekilde iptal eder.
   */
  const cancelAnimationFrame =
    useCallback(() => {
      if (
        animationFrameReference.current ===
        null
      ) {
        return;
      }

      window.cancelAnimationFrame(
        animationFrameReference.current
      );

      animationFrameReference.current =
        null;
    }, []);


  /*
   * Telemetri mesajlarının ortalama geliş
   * aralığını günceller.
   *
   * Tek bir gecikmenin animasyonu aniden
   * değiştirmemesi için yumuşatılmış ortalama
   * kullanılır.
   */
  const updateTelemetryInterval =
    useCallback((receivedTime) => {
      const previousReceivedTime =
        lastTargetReceivedTimeReference.current;

      lastTargetReceivedTimeReference.current =
        receivedTime;

      if (previousReceivedTime === null) {
        return;
      }

      const measuredInterval =
        receivedTime - previousReceivedTime;

      if (
        measuredInterval <= 0 ||
        measuredInterval >
          MAXIMUM_ANIMATION_DURATION * 4
      ) {
        return;
      }

      const currentEstimate =
        estimatedTelemetryIntervalReference.current;

      estimatedTelemetryIntervalReference.current =
        currentEstimate *
          (
            1 -
            TELEMETRY_INTERVAL_SMOOTHING
          ) +
        measuredInterval *
          TELEMETRY_INTERVAL_SMOOTHING;
    }, []);


  /*
   * Drone'u güncel hedefe doğru hareket
   * ettiren sürekli animasyon döngüsü.
   */
  const runAnimation =
    useCallback(
      (timestamp) => {
        if (!isMountedReference.current) {
          return;
        }

        if (
          animationStartTimeReference.current ===
          null
        ) {
          animationStartTimeReference.current =
            timestamp;
        }

        const elapsedTime =
          timestamp -
          animationStartTimeReference.current;

        const duration =
          animationDurationReference.current;

        const progress = Math.min(
          elapsedTime / duration,
          1
        );

        const nextPosition =
          interpolatePosition(
            animationStartPositionReference.current,
            animationTargetReference.current,
            progress
          );

        updateAnimatedPosition(
          nextPosition
        );

        if (progress < 1) {
          animationFrameReference.current =
            window.requestAnimationFrame(
              runAnimation
            );

          return;
        }

        updateAnimatedPosition(
          animationTargetReference.current
        );

        animationFrameReference.current =
          null;

        animationStartTimeReference.current =
          null;

        isAnimatingReference.current =
          false;

        if (isMountedReference.current) {
          setIsDroneMoving(false);
        }
      },
      [updateAnimatedPosition]
    );


  /*
   * Yeni telemetri hedefi geldiğinde eski
   * animasyonu mevcut görsel konumdan devam
   * edecek şekilde yeniden hedefler.
   *
   * Böylece hedefler bir kuyrukta ayrı ayrı
   * oynatılmaz ve hareket parçalanmaz.
   */
  const moveToTarget =
    useCallback(
      (
        nextTargetPosition,
        receivedTime
      ) => {
        const normalizedTarget =
          normalizePosition(
            nextTargetPosition
          );

        updateTelemetryInterval(
          receivedTime
        );

        const startingPosition = {
          ...currentPositionReference.current,
        };

        const distance =
          calculateDistance(
            startingPosition,
            normalizedTarget
          );

        cancelAnimationFrame();

        animationStartTimeReference.current =
          null;

        if (
          distance <
          MINIMUM_MOVEMENT_DISTANCE
        ) {
          animationStartPositionReference.current =
            normalizedTarget;

          animationTargetReference.current =
            normalizedTarget;

          isAnimatingReference.current =
            false;

          updateAnimatedPosition(
            normalizedTarget
          );

          if (isMountedReference.current) {
            setIsDroneMoving(false);
          }

          return;
        }

        const nextHeading =
          calculateHeading(
            startingPosition,
            normalizedTarget
          );

        if (
          nextHeading !== null &&
          isMountedReference.current
        ) {
          setDroneHeading(
            nextHeading
          );
        }

        const estimatedInterval =
          estimatedTelemetryIntervalReference.current;

        const animationDuration =
          limitAnimationDuration(
            estimatedInterval *
              TELEMETRY_DURATION_MULTIPLIER
          );

        animationStartPositionReference.current =
          startingPosition;

        animationTargetReference.current =
          normalizedTarget;

        animationDurationReference.current =
          animationDuration;

        isAnimatingReference.current =
          true;

        if (isMountedReference.current) {
          setIsDroneMoving(true);
        }

        animationFrameReference.current =
          window.requestAnimationFrame(
            runAnimation
          );
      },
      [
        cancelAnimationFrame,
        runAnimation,
        updateAnimatedPosition,
        updateTelemetryInterval,
      ]
    );


  useEffect(() => {
    const normalizedTarget =
      normalizePosition(targetPosition);

    /*
     * İlk telemetri koordinatı başlangıç
     * konumu olarak doğrudan uygulanır.
     */
    if (
      !isInitializedReference.current
    ) {
      isInitializedReference.current =
        true;

      lastReceivedTargetReference.current =
        normalizedTarget;

      lastTargetReceivedTimeReference.current =
        performance.now();

      animationStartPositionReference.current =
        normalizedTarget;

      animationTargetReference.current =
        normalizedTarget;

      updateAnimatedPosition(
        normalizedTarget
      );

      return;
    }

    /*
     * Aynı telemetri değeri tekrar geldiyse
     * yeni hareket başlatılmaz.
     *
     * Bu sayede HOVER veya waypoint üzerinde
     * bekleme davranışı doğal biçimde korunur.
     */
    if (
      positionsAreEqual(
        lastReceivedTargetReference.current,
        normalizedTarget
      )
    ) {
      return;
    }

    lastReceivedTargetReference.current =
      normalizedTarget;

    moveToTarget(
      normalizedTarget,
      performance.now()
    );
  }, [
    targetPosition?.x,
    targetPosition?.y,
    moveToTarget,
    updateAnimatedPosition,
  ]);


  /*
   * Component kapatıldığında çalışan
   * animasyonu ve referansları temizler.
   */
  useEffect(() => {
    isMountedReference.current = true;

    return () => {
      isMountedReference.current = false;

      cancelAnimationFrame();

      isAnimatingReference.current =
        false;

      animationStartTimeReference.current =
        null;
    };
  }, [cancelAnimationFrame]);


  return {
    animatedPosition,
    droneHeading,
    isDroneMoving,
  };
}


export default useDroneAnimation;