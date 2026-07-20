function TelemetryTimeline({
  telemetryHistory,
  formatTime,
}) {
  return (
    <section className="timeline-section">
      <div className="timeline-header">
        <div>
          <p className="section-label">
            FLIGHT DATA
          </p>

          <h2>Telemetry Timeline</h2>
        </div>

        <span>
          {telemetryHistory.length} records
        </span>
      </div>

      {telemetryHistory.length === 0 ? (
        <div className="timeline-empty">
          Start a mission to collect telemetry.
        </div>
      ) : (
        <div className="timeline-list">
          {telemetryHistory.map(
            (item, index) => (
              <article
                className="timeline-item"
                key={`${item.timestamp}-${index}`}
              >
                <div className="timeline-marker">
                  {index + 1}
                </div>

                <div className="timeline-content">
                  <div className="timeline-item-header">
                    <strong>{item.mode}</strong>

                    <time>
                      {formatTime(item.timestamp)}
                    </time>
                  </div>

                  <div className="timeline-values">
                    <span>
                      Battery: {item.battery_level}%
                    </span>

                    <span>
                      Altitude: {item.altitude} m
                    </span>

                    <span>
                      Position: (
                      {item.position.x},
                      {" "}
                      {item.position.y})
                    </span>

                    <span>
                      Speed: {item.speed} m/s
                    </span>
                  </div>
                </div>
              </article>
            )
          )}
        </div>
      )}
    </section>
  );
}

export default TelemetryTimeline;