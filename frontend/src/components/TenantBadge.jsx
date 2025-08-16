import React from "react";
import { useTenant } from "../context/TenantContext";

export default function TenantBadge() {
  const { tenant, loading, error } = useTenant();

  if (loading) return <span>Tenant yükleniyor…</span>;
  if (error) return <span style={{color:'crimson'}}>Hata: {error}</span>;
  if (!tenant) return <span>Tenant bulunamadı</span>;

  return (
    <span style={{
      padding: "6px 10px",
      borderRadius: 8,
      background: "rgba(var(--color-primary-rgb, 0 0 0) / .08)"
    }}>
      Aktif Tenant: <b>{tenant.name}</b> (id: {tenant.id})
    </span>
  );
}
