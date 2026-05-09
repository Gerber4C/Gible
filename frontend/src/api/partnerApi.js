const API_BASE = "http://127.0.0.1:8765";

export async function listProfiles() {
  return getJson("/api/profiles");
}

export async function listProfileFiles(profileId) {
  return getJson(`/api/profiles/${encodeURIComponent(profileId)}/files`);
}

export async function readProfileFile(profileId, path) {
  return getJson(`/api/profiles/${encodeURIComponent(profileId)}/file?path=${encodeURIComponent(path)}`);
}

export async function writeProfileFile(profileId, path, content) {
  return postJson(`/api/profiles/${encodeURIComponent(profileId)}/file`, { path, content });
}

export async function deleteProfileFile(profileId, path) {
  return deleteJson(`/api/profiles/${encodeURIComponent(profileId)}/file?path=${encodeURIComponent(path)}`);
}

export async function chooseBid(payload) {
  return postJson("/api/bid", payload);
}

export async function simulateAuction(payload) {
  return postJson("/api/simulate", payload);
}

async function getJson(path) {
  return requestJson("GET", path);
}

async function postJson(path, payload) {
  return requestJson("POST", path, payload);
}

async function deleteJson(path) {
  return requestJson("DELETE", path);
}

async function requestJson(method, path, payload) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      method,
      headers: payload ? { "Content-Type": "application/json" } : undefined,
      body: payload ? JSON.stringify(payload) : undefined,
    });
  } catch {
    throw new Error("Backend is not running. Start run_local.cmd and keep that window open.");
  }
  return parseResponse(response, path);
}

async function parseResponse(response, path) {
  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error("Backend returned a response the app could not read.");
  }
  if (!response.ok || data.error) {
    throw new Error(friendlyApiMessage(response, data, path));
  }
  return data;
}

function friendlyApiMessage(response, data, path) {
  if (response.status === 404 || data.error === "not_found") {
    if (path.includes("/file")) return "That file is not in this profile.";
    return "That Partner workspace endpoint is not available.";
  }
  if (response.status === 403) return "Partner blocked that file path.";
  if (data.message) return data.message;
  if (data.error) return String(data.error).replaceAll("_", " ");
  return "Partner could not complete that request.";
}
