import React from 'react';

const Dropdown = ({ label, placeholder, options, selectedId, setSelectedId, nameKey, idKey, disabled = false }) => {
  return (
    <div>
      <label className="block text-sm font-semibold text-gray-700 mb-1">{label}</label>
      <select
        value={selectedId || ''} 
        onChange={(e) => setSelectedId(e.target.value ? parseInt(e.target.value) : null)}
        disabled={disabled}
        className={`mt-1 block w-full border border-gray-200 rounded-xl shadow-inner p-3 
          text-gray-800
          focus:ring-blue-500 focus:border-blue-500 appearance-none bg-white transition duration-150
          ${disabled ? 'bg-gray-100 cursor-not-allowed' : ''}
        `}
      >
        {(!selectedId || options.length === 0) && <option value="" disabled>{placeholder || `Pilih ${label}...`}</option>}

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