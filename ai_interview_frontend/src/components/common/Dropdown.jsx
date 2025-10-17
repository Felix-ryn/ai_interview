// src/components/common/Dropdown.jsx
import React from 'react';

// options: Array of { id: number, name: string }
// selectedId: number (ID yang dipilih)
// setSelectedId: function untuk mengubah ID yang dipilih
const Dropdown = ({ label, options, selectedId, setSelectedId, nameKey, idKey }) => {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      <select
        value={selectedId}
        onChange={(e) => setSelectedId(parseInt(e.target.value))} // Wajib parse ke Integer
        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-3 focus:ring-blue-500 focus:border-blue-500 appearance-none"
      >
        {/* Tambahkan opsi default kosong jika perlu, atau pastikan options selalu ada */}
        {options.map(option => (
          <option key={option[idKey]} value={option[idKey]}>
            {option[nameKey]}
          </option>
        ))}
      </select>
    </div>
  );
};

export default Dropdown;