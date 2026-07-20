function FlightReportPanel({
  report,
  reportStatus,
}) {
  return (
    <section className="report-section">
      <div className="report-header">
        <div>
          <p className="section-label">
            MISSION SUMMARY
          </p>

          <h2>Flight Report</h2>
        </div>

        <span>{reportStatus}</span>
      </div>

      {reportStatus === "Waiting" && (
        <div className="report-empty">
          Complete a mission to generate a flight report.
        </div>
      )}

      {reportStatus === "Loading" && (
        <div className="report-empty">
          Loading flight report...
        </div>
      )}

      {reportStatus === "Unavailable" && (
        <div className="report-empty">
          Flight report is unavailable.
        </div>
      )}

      {reportStatus === "Ready" && report && (
        <div className="report-grid">
          <article className="report-item">
            <span>Mission Name</span>
            <strong>{report.mission_name}</strong>
          </article>

          <article className="report-item">
            <span>Commands Executed</span>
            <strong>{report.commands_executed}</strong>
          </article>

          <article className="report-item">
            <span>Distance Travelled</span>
            <strong>
              {Number(
                report.distance_travelled
              ).toFixed(2)}{" "}
              m
            </strong>
          </article>

          <article className="report-item">
            <span>Maximum Altitude</span>
            <strong>
              {report.max_altitude} m
            </strong>
          </article>

          <article className="report-item">
            <span>Battery Used</span>
            <strong>
              {report.battery_used}%
            </strong>
          </article>

          <article className="report-item">
            <span>Final Battery</span>
            <strong>
              {report.final_battery}%
            </strong>
          </article>

          <article className="report-item">
            <span>Final Altitude</span>
            <strong>
              {report.final_altitude} m
            </strong>
          </article>

          <article className="report-item">
            <span>Final Position</span>
            <strong>
              ({report.final_position[0]},{" "}
              {report.final_position[1]})
            </strong>
          </article>

          <article className="report-item">
            <span>Flight Mode</span>
            <strong>{report.flight_mode}</strong>
          </article>
        </div>
      )}
    </section>
  );
}

export default FlightReportPanel;