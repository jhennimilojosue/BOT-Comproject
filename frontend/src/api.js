const API_BASE = "/api/v1";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json") ? await response.json() : await response.text();

  if (!response.ok) {
    let message = `Error ${response.status}`;
    if (body && typeof body === "object") {
      message = body.message || body.detail?.message || body.detail || message;
    } else if (body) {
      message = String(body);
    }
    const error = new Error(message);
    error.status = response.status;
    error.body = body;
    throw error;
  }

  return body;
}

export function uploadExcel(file) {
  const formData = new FormData();
  formData.append("file", file);
  return request("/uploads", {
    method: "POST",
    body: formData,
  });
}

export function getResponsibles(uploadId) {
  const query = uploadId ? `?upload_id=${encodeURIComponent(uploadId)}` : "";
  return request(`/cases/responsible${query}`);
}

export function processResponsible(uploadId, responsibleName) {
  return request("/ai/process-responsible", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      upload_id: uploadId,
      responsible_name: responsibleName,
    }),
  });
}

export function getResults(processingId, fechaInicio, fechaFin) {
  const params = new URLSearchParams();
  if (fechaInicio) params.set("fecha_inicio", fechaInicio);
  if (fechaFin) params.set("fecha_fin", fechaFin);
  const query = params.toString() ? `?${params.toString()}` : "";
  return request(`/ai/results/${processingId}${query}`);
}

export function getProcessing(processingId) {
  return request(`/processing/${processingId}`);
}

export default {
  uploadExcel,
  getResponsibles,
  processResponsible,
  getResults,
  getProcessing,
};