export function setToken(token) {
  localStorage.setItem("access", token);
}
export function getToken() {
  return localStorage.getItem("access") || "";
}
export function clearToken() {
  localStorage.removeItem("access");
}
