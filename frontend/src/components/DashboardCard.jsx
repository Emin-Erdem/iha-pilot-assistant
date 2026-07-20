function DashboardCard({
  title,
  value,
  progress,
}) {
  return (
    <article className="dashboard-card">
      <h2>{title}</h2>

      <p>{value}</p>

      {progress !== undefined && (
        <div className="dashboard-progress">
          <div
            className="dashboard-progress-fill"
            style={{
              width: `${Math.max(
                0,
                Math.min(100, progress)
              )}%`,
            }}
          />
        </div>
      )}
    </article>
  );
}

export default DashboardCard;