function MissionButton({
  buttonText,
  onClick,
  disabled,
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
    >
      {buttonText}
    </button>
  );
}

export default MissionButton;