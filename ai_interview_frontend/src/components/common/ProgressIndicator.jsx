// src/components/common/ProgressIndicator.jsx
import React from 'react';

const ProgressIndicator = ({ current = 0, total = 5 }) => {
  // Hitung persentase progress untuk bilah
  const progress = (current / total) * 100;
  
  return (
    <div className="flex items-center space-x-4 mb-6 max-w-lg mx-auto">
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div 
          // Style lebar menggunakan persentase yang dihitung
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-500" 
          style={{ width: `${progress}%` }}
          role="progressbar"
          aria-valuenow={current}
          aria-valuemax={total}
        ></div>
      </div>
      <p className="text-sm font-medium text-gray-700 whitespace-nowrap">
        {current} dari {total} ({Math.round(progress)}%)
      </p>
    </div>
  );
};

// <--- INI ADALAH EKSPOR DEFAULT YANG MENYELESAIKAN ERROR ANDA --->
export default ProgressIndicator;