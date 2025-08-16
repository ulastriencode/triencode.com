import React, { useEffect, useState, useCallback } from "react";
import { getToken } from "./auth";

export default function CaseList() {

  
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setErr("");
    try {
      const res = await fetch("/api/cases/", {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      if (!res.ok) {
        if (res.status === 401) throw new Error("Oturum geçersiz (401)");
        if (res.status === 403) throw new Error("Yetkiniz yok (403)");
        throw new Error(`API ${res.status}`);
      }
      const data = await res.json();
      setCases(Array.isArray(data) ? data : data.results || []);
    } catch (e) {
      setErr(e.message || "Liste alınamadı");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  if (loading) return <p>Yükleniyor…</p>;
  if (err) return (
    <div>
      <p style={{ color: "red" }}>{err}</p>
      <button onClick={load}>Tekrar Dene</button>
    </div>
  );

  return (
    <div>
      <h1>Dava Listesi</h1>
      <ul>
        {cases.map((c) => (
          <li key={c.id}><strong>{c.title}</strong> – {c.status}</li>
        ))}
      </ul>
      {!cases.length && <p>Bu firmaya ait dava yok.</p>}
    </div>
  );
}
