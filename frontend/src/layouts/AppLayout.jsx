import React, { useEffect, useState } from "react";
import { Outlet } from "react-router-dom";
import Header from "../components/Header";

export default function AppLayout() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const host = window.location.hostname; // ör: firma1.localhost
    const API_BASE = `http://${host}:8000/api/`;
    console.log("[API] BASE_URL =", API_BASE);

    fetch(`${API_BASE}tenant-info/`)
      .then((r) => r.json())
      .then(setData)
      .catch((e) => console.error(e));
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <Header data={data} />
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}
