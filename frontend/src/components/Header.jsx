import React from "react";

export default function Header({ data }) {
  const logoUrl = data?.tenant?.logo_url;
  const firmName = data?.tenant?.name || "Firma Adı";

  return (
    <header className="flex items-center justify-between p-4 bg-gray-900 text-white shadow-md">
      <div className="flex items-center gap-3">
        {logoUrl ? (
          <img
            src={logoUrl}
            alt={`${firmName} Logosu`}
            className="h-12 w-auto object-contain"
            draggable={false}
          />
        ) : (
          <div className="h-12 w-12 flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
            <span className="text-xs text-white">Logo</span>
          </div>
        )}
        <span className="text-lg font-semibold">{firmName}</span>
      </div>
    </header>
  );
}
