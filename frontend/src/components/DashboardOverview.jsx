import DashboardCard from "./DashboardCard";

function DashboardOverview({
  apiStatus,
  missionStatus,
  webSocketStatus,
  telemetry,
}) {
  const batteryLevel = Math.max(
    0,
    Math.min(
      100,
      Number(telemetry.battery_level) || 0
    )
  );

  return (
    <section className="dashboard-cards-grid">
      <DashboardCard
        title="API Status"
        value={apiStatus}
      />

      <DashboardCard
        title="Mission Status"
        value={missionStatus}
      />

      <DashboardCard
        title="WebSocket"
        value={webSocketStatus}
      />

      <DashboardCard
        title="Battery"
        value={`${batteryLevel}%`}
        progress={batteryLevel}
      />

      <DashboardCard
        title="Altitude"
        value={`${telemetry.altitude} m`}
      />

      <DashboardCard
        title="Position"
        value={
          `(${telemetry.position.x}, ` +
          `${telemetry.position.y})`
        }
      />

      <DashboardCard
        title="Flight Mode"
        value={telemetry.mode}
      />

      <DashboardCard
        title="Speed"
        value={`${telemetry.speed} m/s`}
      />
    </section>
  );
}

export default DashboardOverview;