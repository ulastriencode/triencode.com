import React, { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { clearToken } from "../auth";

export default function Shell() {
  const [tenant, setTenant] = useState(null);

  useEffect(() => {
    fetch("/api/tenant/").then(r => r.json()).then(setTenant).catch(()=>{});
  }, []);

  return (
    <div className="min-h-screen flex bg-gray-50">
      {/* Sidebar */}
      <aside className="w-60 bg-white border-r">
        <div className="px-4 py-4 font-semibold">FİRMA LOGO</div>
        <nav className="px-2 space-y-1">
          <NavLink
            to="/"
            end
            className={({isActive}) =>
              "block px-3 py-2 rounded hover:bg-gray-100 " + (isActive ? "bg-gray-100 font-medium" : "")
            }
          >
            Dava takip
          </NavLink>
          <NavLink
            to="/cases"
            className={({isActive}) =>
              "block px-3 py-2 rounded hover:bg-gray-100 " + (isActive ? "bg-gray-100 font-medium" : "")
            }
          >
            Dava sorgula
          </NavLink>
        </nav>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="h-14 bg-white border-b flex items-center justify-between px-4">
          <div className="text-sm text-gray-600">
            Aktif firma: <b>{tenant?.name || "-"}</b>{" "}
            <span className="text-gray-400">({tenant?.domain || window.location.hostname})</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-500">Hesabım</span>
            <button
              onClick={() => { clearToken(); window.location.href="/login"; }}
              className="text-sm px-3 py-1 rounded bg-gray-100 hover:bg-gray-200"
            >
              Çıkış
            </button>
          </div>
        </header>

        {/* Content */}
        <main className="p-4">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
