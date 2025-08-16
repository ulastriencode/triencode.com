// frontend/src/api/index.js

function ensureTrailingSlash(u) {
  return u.endsWith("/") ? u : u + "/";
}

// Varsayılan: bulunduğun hostname + :8000 + /api/
const DEFAULT_BASE = `${window.location.protocol}//${window.location.hostname}:8000/api/`;

function resolveBase() {
  // ENV varsa kullan; ama *.localhost üzerinde farklı host'a zorlamayalım
  let raw = import.meta?.env?.VITE_API_BASE?.trim();
  if (!raw) return DEFAULT_BASE;

  try {
    const candidate = new URL(ensureTrailingSlash(raw));
    // Dev ortamı için güvenlik: firmaX.localhost'taysak, o host'a git
    if (candidate.hostname.endsWith(".localhost") &&
        candidate.hostname !== window.location.hostname) {
      return DEFAULT_BASE;
    }
    return candidate.toString();
  } catch {
    return DEFAULT_BASE;
  }
}

export const BASE_URL = resolveBase();

// Güvenli URL birleştirme: slash sorunlarını çözer
export function urlJoin(path) {
  const clean = (path || "").replace(/^\//, "");
  return new URL(clean, BASE_URL).toString();
}

function authHeader() {
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// NOT: backend 'X-Tenant-Domain' için sadece hostname istiyor (portsuz)
const tenantHeader = { "X-Tenant-Domain": window.location.hostname };

export async function apiGet(path, opts = {}) {
  const res = await fetch(urlJoin(path), {
    method: "GET",
    // tenant-info public olduğu için cred gerekmez; diğer endpointlerde de çalışır
    credentials: "omit",
    headers: {
      "Content-Type": "application/json",
      ...tenantHeader,
      ...authHeader(),
      ...(opts.headers || {}),
    },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status} ${res.statusText} – ${text}`);
  }
  return res.json();
}

export async function apiPost(path, body, opts = {}) {
  const res = await fetch(urlJoin(path), {
    method: "POST",
    credentials: "omit",
    headers: {
      "Content-Type": "application/json",
      ...tenantHeader,
      ...authHeader(),
      ...(opts.headers || {}),
    },
    body: JSON.stringify(body ?? {}),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status} ${res.statusText} – ${text}`);
  }
  return res.json();
}

// Debug için: doğru base'i görüyor musun?
console.log("[API] BASE_URL =", BASE_URL);
