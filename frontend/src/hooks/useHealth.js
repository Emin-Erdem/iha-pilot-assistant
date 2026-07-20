import { useEffect, useState } from "react";

import { getHealth } from "../services/api";

function useHealth() {
  const [apiStatus, setApiStatus] =
    useState("Checking...");

  useEffect(() => {
    async function checkApi() {
      try {
        const data = await getHealth();

        if (data.status === "healthy") {
          setApiStatus("Healthy ✅");
        } else {
          setApiStatus("Unavailable ❌");
        }
      } catch {
        setApiStatus("Offline ❌");
      }
    }

    checkApi();
  }, []);

  return apiStatus;
}

export default useHealth;