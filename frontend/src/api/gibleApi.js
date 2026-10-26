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

export async function generateTrainingDeal(payload, signal) {
  return requestJson("POST", "/api/training/deal", payload, signal);
}

export async function analyzeContracts(payload, signal) {
  return requestJson("POST", "/api/analysis/contracts", payload, signal);
}

export async function analyzeRoutes(payload, signal) {
  return requestJson("POST", "/api/analysis/routes", payload, signal);
}

export async function listScannerReports() {
  return getJson("/api/scanner/reports");
}

export async function readScannerReport(reportId) {
  return getJson(`/api/scanner/reports/${encodeURIComponent(reportId)}`);
}

export async function scannerRunStatus() {
  return getJson("/api/scanner/runs/current");
}

export async function startScannerRun(payload) {
  return postJson("/api/scanner/runs", payload);
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

async function requestJson(method, path, payload, signal) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      method,
      headers: payload ? { "Content-Type": "application/json" } : undefined,
      body: payload ? JSON.stringify(payload) : undefined,
      signal,
    });
  } catch (error) {
    if (error?.name === "AbortError") throw error;
    throw new Error("Backend is not running. Start gible.cmd (or python gible.py) and keep that window open.");
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
    return "That Gible workspace endpoint is not available.";
  }
  if (response.status === 403) return "Gible blocked that file path.";
  if (data.message) return data.message;
  if (data.error) return String(data.error).replaceAll("_", " ");
  return "Gible could not complete that request.";
}
