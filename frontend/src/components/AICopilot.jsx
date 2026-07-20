import {
  useEffect,
  useRef,
  useState,
} from "react";


const suggestedQuestions = [
  "Drone şu an nerede?",
  "Batarya seviyesi yeterli mi?",
  "Görev şu an ne durumda?",
  "Son görevi özetle.",
  "Mevcut uçuş modunu açıkla.",
];


function AICopilot({
  messages,
  isLoading,
  disabled = false,
  onAsk,
  onClear,
}) {
  const [question, setQuestion] =
    useState("");

  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, isLoading]);

  function submitQuestion(value) {
    const trimmedQuestion = value.trim();

    if (
      !trimmedQuestion ||
      isLoading ||
      disabled
    ) {
      return;
    }

    onAsk(trimmedQuestion);
    setQuestion("");
  }

  function handleSubmit(event) {
    event.preventDefault();
    submitQuestion(question);
  }

  function handleKeyDown(event) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      submitQuestion(question);
    }
  }

  return (
    <section className="copilot-section">
      <div className="copilot-header">
        <div>
          <p className="section-label">
            YAPAY ZEKÂ UÇUŞ ASİSTANI
          </p>

          <h2>AI Copilot</h2>
        </div>

        <div className="copilot-header-actions">
          <span
            className={
              disabled
                ? "copilot-status offline"
                : "copilot-status online"
            }
          >
            {disabled
              ? "Kullanılamıyor"
              : "Hazır"}
          </span>

          <button
            className="copilot-clear-button"
            type="button"
            onClick={onClear}
            disabled={
              disabled ||
              isLoading ||
              messages.length === 0
            }
          >
            Sohbeti Temizle
          </button>
        </div>
      </div>

      <p className="copilot-description">
        Canlı telemetri, görev durumu ve son uçuş
        raporu hakkında Türkçe sorular sorabilirsiniz.
      </p>

      <div className="copilot-suggestions">
        {suggestedQuestions.map(
          (suggestedQuestion) => (
            <button
              key={suggestedQuestion}
              type="button"
              disabled={disabled || isLoading}
              onClick={() =>
                submitQuestion(
                  suggestedQuestion
                )
              }
            >
              {suggestedQuestion}
            </button>
          )
        )}
      </div>

      <div className="copilot-chat">
        {messages.length === 0 && (
          <div className="copilot-empty">
            <div className="copilot-empty-icon">
              AI
            </div>

            <strong>
              Uçuş asistanı hazır
            </strong>

            <p>
              Drone konumu, batarya, irtifa,
              görev durumu veya son uçuş raporu
              hakkında soru sorun.
            </p>
          </div>
        )}

        {messages.map((message) => (
          <article
            key={message.id}
            className={
              `copilot-message ${message.role}` +
              (message.isError
                ? " error"
                : "")
            }
          >
            <div className="copilot-avatar">
              {message.role === "user"
                ? "S"
                : "AI"}
            </div>

            <div className="copilot-message-content">
              <span>
                {message.role === "user"
                  ? "Siz"
                  : "Uçuş Asistanı"}
              </span>

              <p>{message.content}</p>
            </div>
          </article>
        ))}

        {isLoading && (
          <article className="copilot-message assistant">
            <div className="copilot-avatar">
              AI
            </div>

            <div className="copilot-message-content">
              <span>Uçuş Asistanı</span>

              <div className="copilot-typing">
                <i />
                <i />
                <i />
              </div>
            </div>
          </article>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form
        className="copilot-form"
        onSubmit={handleSubmit}
      >
        <label className="copilot-input-field">
          <span>Sorunuz</span>

          <textarea
            rows={3}
            value={question}
            disabled={disabled || isLoading}
            placeholder={
              "Örneğin: Batarya seviyesi " +
              "eve dönmek için yeterli mi?"
            }
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            onKeyDown={handleKeyDown}
          />
        </label>

        <button
          className="copilot-send-button"
          type="submit"
          disabled={
            disabled ||
            isLoading ||
            !question.trim()
          }
        >
          {isLoading
            ? "Yanıt hazırlanıyor..."
            : "Soruyu Gönder"}
        </button>
      </form>
    </section>
  );
}

export default AICopilot;