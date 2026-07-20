import { useState } from "react";

import { resetSystem } from "../services/api";


function useSystemReset(onResetComplete) {
  const [isResetting, setIsResetting] =
    useState(false);

  const [resetError, setResetError] =
    useState("");

  async function handleReset() {
    try {
      setIsResetting(true);
      setResetError("");

      await resetSystem();

      if (onResetComplete) {
        onResetComplete();
      }
    } catch (error) {
      setResetError(
        error instanceof Error
          ? error.message
          : "Drone system could not be reset."
      );
    } finally {
      setIsResetting(false);
    }
  }

  return {
    isResetting,
    resetError,
    handleReset,
  };
}

export default useSystemReset;