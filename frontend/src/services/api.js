const API_BASE_URL = "http://127.0.0.1:8000";

async function parseResponse(response) {
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const message =
      data?.detail ??
      `Request failed: ${response.status}`;

    throw new Error(message);
  }

  return data;
}

async function request(endpoint) {
  const response = await fetch(
    `${API_BASE_URL}${endpoint}`
  );

  return parseResponse(response);
}

async function post(endpoint, body) {
  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    }
  );

  return parseResponse(response);
}

export async function getHealth() {
  return request("/health");
}

export async function getMissionStatus() {
  return request("/missions/status");
}

export async function getTelemetry() {
  return request("/telemetry");
}

export async function getLatestReport() {
  return request("/reports/latest");
}

export async function startMission(missionPayload) {
  if (!missionPayload) {
    throw new Error(
      "Görev verisi bulunamadı."
    );
  }

  return post(
    "/missions/start",
    missionPayload
  );
}

export async function resetSystem() {
  return post("/system/reset", {});
}

export async function generateMission(instruction) {
  if (!instruction?.trim()) {
    throw new Error(
      "Görev talimatı boş olamaz."
    );
  }

  return post("/ai/mission", {
    instruction: instruction.trim(),
  });
}

export async function askCopilot(copilotPayload) {
  if (!copilotPayload) {
    throw new Error(
      "Copilot verisi bulunamadı."
    );
  }

  if (!copilotPayload.question?.trim()) {
    throw new Error(
      "Lütfen bir soru yazın."
    );
  }

  if (!copilotPayload.telemetry) {
    throw new Error(
      "Telemetri verisi bulunamadı."
    );
  }

  return post("/ai/copilot", {
    ...copilotPayload,
    question: copilotPayload.question.trim(),
  });
}