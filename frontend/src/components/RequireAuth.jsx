import React from "react";
import { Navigate, useLocation } from "react-router-dom";

function getToken() {
  return localStorage.getItem("access") || "";
}

export default function RequireAuth({ children }) {
  const token = getToken();
  const loc = useLocation();

  if (!token) {
    return <Navigate to="/login" replace state={{ from: loc }} />;
  }
  return children;
}
