import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";


function TelemetryCharts({ telemetryHistory }) {
  const chartData = telemetryHistory.map(
    (item, index) => ({
      step: index + 1,
      battery: item.battery_level,
      altitude: item.altitude,
    })
  );

  return (
    <section className="charts-section">
      <div className="charts-header">
        <div>
          <p className="section-label">
            FLIGHT ANALYTICS
          </p>

          <h2>Telemetry Charts</h2>
        </div>

        <span>
          {chartData.length} samples
        </span>
      </div>

      {chartData.length === 0 ? (
        <div className="charts-empty">
          Start a mission to generate chart data.
        </div>
      ) : (
        <div className="charts-grid">
          <article className="chart-card">
            <div className="chart-title">
              <div>
                <p>Battery Level</p>
                <strong>
                  {chartData[
                    chartData.length - 1
                  ]?.battery ?? 100}
                  %
                </strong>
              </div>
            </div>

            <div className="chart-container">
              <ResponsiveContainer
                width="100%"
                height={280}
              >
                <LineChart data={chartData}>
                  <CartesianGrid
                    strokeDasharray="4 4"
                    vertical={false}
                    stroke="rgba(143, 169, 199, 0.14)"
                  />

                  <XAxis
                    dataKey="step"
                    stroke="#7791ad"
                    tickLine={false}
                    axisLine={false}
                  />

                  <YAxis
                    domain={[0, 100]}
                    stroke="#7791ad"
                    tickLine={false}
                    axisLine={false}
                    width={36}
                  />

                  <Tooltip
                    contentStyle={{
                      background: "#0f1f34",
                      border:
                        "1px solid rgba(120, 170, 255, 0.2)",
                      borderRadius: "10px",
                    }}
                    labelStyle={{
                      color: "#d8e9fa",
                    }}
                  />

                  <Line
                    type="monotone"
                    dataKey="battery"
                    name="Battery"
                    stroke="#58c9ff"
                    strokeWidth={3}
                    dot={false}
                    activeDot={{ r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </article>

          <article className="chart-card">
            <div className="chart-title">
              <div>
                <p>Altitude</p>
                <strong>
                  {chartData[
                    chartData.length - 1
                  ]?.altitude ?? 0}
                  {" "}m
                </strong>
              </div>
            </div>

            <div className="chart-container">
              <ResponsiveContainer
                width="100%"
                height={280}
              >
                <LineChart data={chartData}>
                  <CartesianGrid
                    strokeDasharray="4 4"
                    vertical={false}
                    stroke="rgba(143, 169, 199, 0.14)"
                  />

                  <XAxis
                    dataKey="step"
                    stroke="#7791ad"
                    tickLine={false}
                    axisLine={false}
                  />

                  <YAxis
                    stroke="#7791ad"
                    tickLine={false}
                    axisLine={false}
                    width={36}
                  />

                  <Tooltip
                    contentStyle={{
                      background: "#0f1f34",
                      border:
                        "1px solid rgba(120, 170, 255, 0.2)",
                      borderRadius: "10px",
                    }}
                    labelStyle={{
                      color: "#d8e9fa",
                    }}
                  />

                  <Line
                    type="monotone"
                    dataKey="altitude"
                    name="Altitude"
                    stroke="#8c7cff"
                    strokeWidth={3}
                    dot={false}
                    activeDot={{ r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </article>
        </div>
      )}
    </section>
  );
}

export default TelemetryCharts;