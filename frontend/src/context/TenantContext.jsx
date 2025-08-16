// frontend/src/context/TenantContext.jsx
import React, { createContext, useContext, useEffect, useState } from "react";
import { apiGet } from "../api";

const TenantContext = createContext(null);

export function TenantProvider({ children }) {
  const [tenant, setTenant] = useState(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  useEffect(() => {
  let alive = true;
  (async () => {
    try {
      const info = await apiGet("/tenant-info/");
      if (!alive) return;

      setTenant(info?.tenant || null);

      // Tema değişkenleri
      if (info?.theme) {
        applyCssVars(info.theme);
      }
    } catch (e) {
      setErr(e.message || "tenant-info alınamadı");
    } finally {
      setLoading(false);
    }
  })();
  return () => { alive = false; };
}, []);

  return (
    <TenantContext.Provider value={{ tenant, loading, error: err }}>
      {children}
    </TenantContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useTenant() {
  return useContext(TenantContext);
}

function hexToRgbTriplet(hex) {
  const m = hex?.replace("#", "")?.match(/.{1,2}/g);
  if (!m) return null;
  const [r, g, b] = m.map(h => parseInt(h, 16));
  return `${r} ${g} ${b}`;
}

function applyCssVars(theme) {
  const root = document.documentElement;
  for (const [k, v] of Object.entries(theme)) {
    if (!v) continue;
    root.style.setProperty(`--color-${k}`, v);
    const triplet = hexToRgbTriplet(v);
    if (triplet) root.style.setProperty(`--color-${k}-rgb`, triplet);
  }
}
