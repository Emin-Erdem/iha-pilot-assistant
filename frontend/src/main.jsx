import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./styles/global.css";
import "./styles/dashboard.css";
import "./styles/cards.css";
import "./styles/button.css";
// import "./styles/drone-map.css";  <-- BUNU SİL
import "./styles/charts.css";
import "./styles/report.css";
import "./styles/timeline.css";
import "./styles/responsive.css";
import "./styles/mission-editor.css";
import "./styles/ai-mission.css";
import "./styles/map.css";
import "./styles/replay.css";
import "./styles/copilot.css";

import App from "./App.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);