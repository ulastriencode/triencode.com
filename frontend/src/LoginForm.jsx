// import React, { useState } from "react";
// import { setToken } from "./auth";

// // Vite: import.meta.env.VITE_API_BASE
// const API_BASE = (() => {
//   // örn: firma1.localhost:3000  ->  firma1.localhost:8000
//   const host = window.location.host.replace(":3000", ":8000");
//   const protocol = window.location.protocol; // http:
//   return `${protocol}//${host}`;
// })();

// export default function LoginForm() {
//   const [username, setU] = useState("");
//   const [password, setP] = useState("");
//   const [error, setError] = useState("");
//   const [isLoading, setIsLoading] = useState(false);

//   async function handleSubmit(e) {
//     e.preventDefault();
//     setError("");
//     setIsLoading(true);

//     try {
//       const r = await fetch(`${API_BASE}/api/auth/token/`, {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ username, password }),
//       });
//       const contentType = r.headers.get("content-type") || "";

//       if (!r.ok) {
//         let msg = `Giriş başarısız: ${r.status}`;
//         const ct = r.headers.get("content-type") || "";
//         if (ct.includes("application/json")) {
//           const j = await r.json().catch(() => null);
//           if (j?.detail === "Tenant uyuşmuyor.") {
//             msg =
//               "Bu firma için yetkiniz yok. Lütfen doğru firmadan giriş yapın.";
//           } else if (j?.detail) {
//             msg = j.detail;
//           }
//         }
//         throw new Error(msg);
//       }

//       const data = contentType.includes("application/json")
//         ? await r.json()
//         : (() => {
//             throw new Error("Sunucudan beklenmeyen cevap (JSON değil).");
//           })();

//       if (!data?.access) throw new Error("Token alınamadı.");

//       setToken(data.access);
//       if (data.refresh) {
//         try {
//           localStorage.setItem("refresh", data.refresh);
//         } catch (e) {
//           console.log(
//             "Refresh token saklanamadı, tarayıcı depolama dolu olabilir.",
//             e
//           );
//         }
//       }

//       window.location.href = "/";
//     } catch (err) {
//       setError(err?.message || "Giriş başarısız");
//     } finally {
//       setIsLoading(false);
//     }
//   }

//   return (
//     <div className="login-container">
//       <div className="login-card">
//         <div className="login-header">
//           <h2>Hoş Geldiniz</h2>
//           <p>Hesabınıza giriş yapın</p>
//         </div>

//         <form onSubmit={handleSubmit} className="login-form">
//           {error && (
//             <div className="error-message">
//               <svg
//                 width="16"
//                 height="16"
//                 viewBox="0 0 24 24"
//                 fill="none"
//                 stroke="currentColor"
//                 strokeWidth="2"
//               >
//                 <circle cx="12" cy="12" r="10" />
//                 <line x1="15" y1="9" x2="9" y2="15" />
//                 <line x1="9" y1="9" x2="15" y2="15" />
//               </svg>
//               {error}
//             </div>
//           )}

//           <div className="form-group">
//             <label htmlFor="username">Kullanıcı Adı</label>
//             <input
//               id="username"
//               type="text"
//               value={username}
//               onChange={(e) => setU(e.target.value)}
//               placeholder="Kullanıcı adınızı girin"
//               required
//               disabled={isLoading}
//             />
//           </div>

//           <div className="form-group">
//             <label htmlFor="password">Şifre</label>
//             <input
//               id="password"
//               type="password"
//               value={password}
//               onChange={(e) => setP(e.target.value)}
//               placeholder="Şifrenizi girin"
//               required
//               disabled={isLoading}
//             />
//           </div>

//           <button type="submit" className="login-button" disabled={isLoading}>
//             {isLoading ? (
//               <>
//                 <svg
//                   className="spinner"
//                   width="16"
//                   height="16"
//                   viewBox="0 0 24 24"
//                 >
//                   <circle
//                     cx="12"
//                     cy="12"
//                     r="10"
//                     fill="none"
//                     stroke="currentColor"
//                     strokeWidth="4"
//                     opacity="0.25"
//                   />
//                   <path
//                     fill="currentColor"
//                     d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
//                     opacity="0.75"
//                   />
//                 </svg>
//                 Giriş yapılıyor...
//               </>
//             ) : (
//               "Giriş Yap"
//             )}
//           </button>
//         </form>
//       </div>
//     </div>
//   );
// }
