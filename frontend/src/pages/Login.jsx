import React, { useState, useEffect } from "react";
import { setToken } from "../auth.jsx";
import "../index.css";

// Vite: import.meta.env.VITE_API_BASE
const API_BASE = (() => {
  // örn: firma1.localhost:3000  ->  firma1.localhost:8000
  const host = window.location.host.replace(":3000", ":8000");
  const protocol = window.location.protocol; // http:
  return `${protocol}//${host}`;
})();

export default function LoginForm() {
  const [username, setU] = useState("");
  const [password, setP] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // 👇 Tenant (firma) bilgisi
  const [tenant, setTenant] = useState(null);
  const [tenantLoading, setTenantLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const r = await fetch(`${API_BASE}/api/tenant-info/`, {
          headers: { "Accept": "application/json" },
        });
        if (!r.ok) throw new Error(`Tenant info alınamadı (${r.status})`);
        const info = await r.json();
        if (!alive) return;

        setTenant(info || null);

        // Sayfa başlığını ve favicon'u firmaya göre ayarla (varsa)
        if (info?.name) document.title = `${info.name} | Legal Manager`;
        // if (info?.favicon_url) {
        //   let link = document.querySelector("link[rel~='icon']");
        //   if (!link) {
        //     link = document.createElement("link");
        //     link.rel = "icon";
        //     document.head.appendChild(link);
        //   }
        //   link.href = info.favicon_url;
        // }

        // (Opsiyonel) Tema renklerini CSS değişkenlerine uygula
        // if (info?.theme) {
        //   const root = document.documentElement.style;
        //   Object.entries(info.theme).forEach(([k, v]) => {
        //     root.setProperty(`--${k}`, String(v));
        //   });
        // }
      } catch (e) {
        console.warn(e);
      } finally {
        setTenantLoading(false);
      }
    })();
    return () => { alive = false; };
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const r = await fetch(`${API_BASE}/api/auth/token/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const contentType = r.headers.get("content-type") || "";

      if (!r.ok) {
        let msg = `Giriş başarısız: ${r.status}`;
        if (contentType.includes("application/json")) {
          const j = await r.json().catch(() => null);
          if (j?.detail === "Tenant uyuşmuyor.") {
            msg = "Bu firma için yetkiniz yok. Lütfen doğru firmadan giriş yapın.";
          } else if (j?.detail) {
            msg = j.detail;
          }
        }
        throw new Error(msg);
      }

      const data = contentType.includes("application/json")
        ? await r.json()
        : (() => { throw new Error("Sunucudan beklenmeyen cevap (JSON değil)."); })();

      if (!data?.access) throw new Error("Token alınamadı.");

      setToken(data.access);
      if (data.refresh) {
        try { localStorage.setItem("refresh", data.refresh); } catch { /* ignore */ }
      }

      window.location.href = "/";
    } catch (err) {
      setError(err?.message || "Giriş başarısız");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-blue-900 relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-10 left-10 w-72 h-72 bg-blue-500 rounded-full mix-blend-screen filter blur-xl animate-blob"></div>
        <div className="absolute top-20 right-10 w-72 h-72 bg-purple-500 rounded-full mix-blend-screen filter blur-xl animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-indigo-500 rounded-full mix-blend-screen filter blur-xl animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative flex items-center justify-center min-h-screen p-4">
        <div className="w-full max-w-md">
          {/* Firma / Marka alanı */}
          <div className="text-center mb-8">
            {tenantLoading ? (
              <div className="animate-pulse">
                <div className="w-20 h-20 bg-gray-800/80 rounded-3xl mx-auto mb-4 backdrop-blur-sm border border-gray-700"></div>
                <div className="h-7 bg-gray-800/80 rounded-lg w-48 mx-auto mb-2 backdrop-blur-sm"></div>
                <div className="h-5 bg-gray-800/60 rounded-lg w-32 mx-auto backdrop-blur-sm"></div>
              </div>
            ) : (
              <>
                {tenant?.logo_url ? (
                  <div className="inline-block p-4 bg-white/95 backdrop-blur-lg rounded-3xl shadow-2xl mb-4 border border-gray-300/50">
                    <img
                      src={tenant.logo_url}
                      alt={`${tenant?.name || "Firma"} Logosu`}
                      className="h-16 w-auto max-w-[120px] object-contain"
                      draggable={false}
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                    {/* Fallback icon */}
                    <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl hidden items-center justify-center">
                      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <polyline points="14,2 14,8 20,8"/>
                        <line x1="16" y1="13" x2="8" y2="13"/>
                        <line x1="16" y1="17" x2="8" y2="17"/>
                      </svg>
                    </div>
                  </div>
                ) : (
                  <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-3xl mb-4 shadow-2xl border-4 border-blue-400/30">
                    <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <polyline points="14,2 14,8 20,8"/>
                      <line x1="16" y1="13" x2="8" y2="13"/>
                      <line x1="16" y1="17" x2="8" y2="17"/>
                    </svg>
                  </div>
                )}

                <h1 className="text-3xl font-bold bg-gradient-to-r from-white via-blue-200 to-purple-200 bg-clip-text text-transparent mb-2">
                  {tenant?.name || "Triencode"}
                </h1>
                <p className="text-gray-300 font-medium">
                  {tenant?.tagline || "Dava Takip Sistemi"}
                </p>
              </>
            )}
          </div>

          {/* Login Card */}
          <div className="bg-gray-900/95 backdrop-blur-xl shadow-2xl rounded-3xl border border-gray-700/50 overflow-hidden">
            <div className="p-8">
              <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-white mb-2">Hoş Geldiniz</h2>
                <p className="text-gray-300">Hesabınıza giriş yapın</p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                {error && (
                  <div className="bg-red-900/50 backdrop-blur-sm border border-red-500/30 rounded-xl p-4 flex items-start gap-3 animate-shake">
                    <div className="flex-shrink-0">
                      <svg className="w-5 h-5 text-red-400 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="15" y1="9" x2="9" y2="15"/>
                        <line x1="9" y1="9" x2="15" y2="15"/>
                      </svg>
                    </div>
                    <div className="text-sm text-red-300 font-medium">{error}</div>
                  </div>
                )}

                <div className="space-y-5">
                  <div className="group">
                    <label htmlFor="username" className="block text-sm font-semibold text-gray-300 mb-2 transition-colors group-focus-within:text-blue-400">
                      Kullanıcı Adı
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none transition-colors group-focus-within:text-blue-400">
                        <svg className="h-5 w-5 text-gray-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                          <circle cx="12" cy="7" r="4"/>
                        </svg>
                      </div>
                      <input
                        id="username"
                        type="text"
                        value={username}
                        onChange={(e) => setU(e.target.value)}
                        placeholder="Kullanıcı adınızı girin"
                        required
                        disabled={isLoading}
                        className="block w-full pl-10 pr-4 py-3.5 border-2 border-gray-600 rounded-xl text-white placeholder-gray-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed bg-gray-800/50 backdrop-blur-sm"
                      />
                    </div>
                  </div>

                  <div className="group">
                    <label htmlFor="password" className="block text-sm font-semibold text-gray-300 mb-2 transition-colors group-focus-within:text-blue-400">
                      Şifre
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none transition-colors group-focus-within:text-blue-400">
                        <svg className="h-5 w-5 text-gray-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                          <circle cx="12" cy="16" r="1"/>
                          <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                        </svg>
                      </div>
                      <input
                        id="password"
                        type="password"
                        value={password}
                        onChange={(e) => setP(e.target.value)}
                        placeholder="Şifrenizi girin"
                        required
                        disabled={isLoading}
                        className="block w-full pl-10 pr-4 py-3.5 border-2 border-gray-600 rounded-xl text-white placeholder-gray-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed bg-gray-800/50 backdrop-blur-sm"
                      />
                    </div>
                  </div>
                </div>

                <div className="pt-2">
                  <button
                    type="submit"
                    disabled={isLoading || !username.trim() || !password.trim()}
                    className="w-full flex items-center justify-center gap-2 px-6 py-3.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-purple-700 focus:ring-4 focus:ring-blue-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-blue-500/25 transform hover:-translate-y-0.5 disabled:transform-none active:scale-95"
                  >
                    {isLoading ? (
                      <>
                        <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24">
                          <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" strokeWidth="4" opacity="0.25"/>
                          <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" opacity="0.75"/>
                        </svg>
                        Giriş yapılıyor...
                      </>
                    ) : (
                      <>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/>
                          <polyline points="10,17 15,12 10,7"/>
                          <line x1="15" y1="12" x2="3" y2="12"/>
                        </svg>
                        Giriş Yap
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>

          {/* Footer */}
          <div className="text-center mt-8">
            <p className="text-sm text-gray-400 backdrop-blur-sm">
              © 2025 {tenant?.name ? `${tenant.name} · ` : ""}Triencode. Tüm hakları saklıdır.
            </p>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes blob {
          0% { transform: translate(0px, 0px) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
          100% { transform: translate(0px, 0px) scale(1); }
        }
        
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          10%, 30%, 50%, 70%, 90% { transform: translateX(-2px); }
          20%, 40%, 60%, 80% { transform: translateX(2px); }
        }
        
        .animate-blob {
          animation: blob 7s infinite;
        }
        
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        
        .animation-delay-4000 {
          animation-delay: 4s;
        }
        
        .animate-shake {
          animation: shake 0.5s ease-in-out;
        }
      `}</style>
    </div>
  );
}