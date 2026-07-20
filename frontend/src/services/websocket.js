const WS_URL = "ws://127.0.0.1:8000/ws/telemetry";

export function connectTelemetry(onMessage) {
  const socket = new WebSocket(WS_URL);

  socket.onopen = () => {
    console.log("WebSocket connected.");
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    onMessage(data);
  };

  socket.onerror = (error) => {
    console.error(error);
  };

  socket.onclose = () => {
    console.log("WebSocket disconnected.");
  };

  return socket;
}