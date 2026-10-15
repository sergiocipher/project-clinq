/**
 * WHY THIS FILE EXISTS:
 * Central API client using relative URLs (/api/...) so the browser always
 * talks to whatever host served the page. Nginx (or Vite's dev proxy) then
 * forwards /api requests to the backend — the frontend never hard-codes
 * the backend hostname.
 */

const BASE = "/api/appointments";

async function request(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  list: (params = {}) => {
    const qs = new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([, v]) => v != null && v !== ""))
    ).toString();
    return request(`${BASE}${qs ? `?${qs}` : ""}`);
  },
  stats: () => request(`${BASE}/stats`),
  get: (id) => request(`${BASE}/${id}`),
  create: (data) => request(BASE, { method: "POST", body: JSON.stringify(data) }),
  update: (id, data) =>
    request(`${BASE}/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  remove: (id) => request(`${BASE}/${id}`, { method: "DELETE" }),
};
