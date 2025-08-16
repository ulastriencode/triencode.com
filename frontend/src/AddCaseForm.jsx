import { useState } from "react";
import { getToken } from "./auth";

export default function AddCaseForm({ onCreated }) {
  const [title, setTitle] = useState("");
  const [status, setStatus] = useState("open");
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setError("");

    const resp = await fetch("/api/cases/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getToken()}`, // <-- token burada
      },
      body: JSON.stringify({ title, status }),
    });

    if (!resp.ok) {
      setError("Kaydedilemedi: HTTP " + resp.status);
      return;
    }

    setTitle("");
    setStatus("open");
    onCreated?.(); // listeyi yenile
  };

  return (
    <form onSubmit={submit} style={{ marginBottom: 16 }}>
      <div style={{ marginBottom: 8 }}>
        <label>Başlık&nbsp;</label>
        <input
          placeholder="Örn: Yeni Dava"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          style={{ width: 260 }}
        />
      </div>
      <div style={{ marginBottom: 8 }}>
        <label>Durum&nbsp;</label>
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="open">open</option>
          <option value="closed">closed</option>
        </select>
      </div>
      <button type="submit">Kaydet</button>
      {error && <div style={{ color: "tomato", marginTop: 8 }}>{error}</div>}
    </form>
  );
}
