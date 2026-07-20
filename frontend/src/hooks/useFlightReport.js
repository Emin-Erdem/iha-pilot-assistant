import { useEffect, useState } from "react";

import { getLatestReport } from "../services/api";


function useFlightReport(missionStatus) {
  const [report, setReport] = useState(null);
  const [reportStatus, setReportStatus] =
    useState("Waiting");

  useEffect(() => {
    if (missionStatus !== "Completed") {
      setReport(null);
      setReportStatus("Waiting");
      return;
    }

    async function loadReport() {
      try {
        setReportStatus("Loading");

        const data = await getLatestReport();

        setReport(data);
        setReportStatus("Ready");
      } catch {
        setReport(null);
        setReportStatus("Unavailable");
      }
    }

    loadReport();
  }, [missionStatus]);

  return {
    report,
    reportStatus,
  };
}

export default useFlightReport;