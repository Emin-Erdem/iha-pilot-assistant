function ResetButton({
  onClick,
  disabled,
  isResetting,
}) {
  return (
    <button
      className="reset-button"
      type="button"
      onClick={onClick}
      disabled={disabled}
    >
      {isResetting
        ? "Resetting..."
        : "Reset Drone"}
    </button>
  );
}

export default ResetButton;