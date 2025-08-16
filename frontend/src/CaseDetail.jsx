import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";


const [tenant, setTenant] = useState(null);
useEffect(() => {
  fetch("/api/tenant/")
    .then(r => r.json())
    .then(setTenant)
    .catch(() => setTenant(null));
}, []);

function CaseDetail() {
  const { id } = useParams();
  const [caseData, setCaseData] = useState(null);

  useEffect(() => {
    fetch(`/api/cases/${id}/`)
      .then((res) => res.json())
      .then((data) => setCaseData(data));
  }, [id]);

  if (!caseData) return <p>Yükleniyor...</p>;

  return (
    <div>
      <h1>{caseData.title}</h1>
      <p>Durum: {caseData.status}</p>
      <p>Son güncelleme: {caseData.updated_at}</p>
    </div>
  );
}

export default CaseDetail;
