// src/components/feedback/NarrativeFeedback.jsx
import React from 'react';

const NarrativeFeedback = ({ feedbackText }) => {
  return (
    <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-yellow-500">
      <h2 className="text-2xl font-bold mb-4 text-gray-800 flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2m-9 0V3h4v2m-4 0h4" />
        </svg>
        Feedback Naratif AI
      </h2>
      <div className="text-gray-700 space-y-4 leading-relaxed whitespace-pre-wrap">
        {/* Menggunakan whitespace-pre-wrap untuk mempertahankan format paragraf dari LLM */}
        {feedbackText || "Laporan naratif sedang diproses. Mohon tunggu laporan dari backend..."}
      </div>
    </div>
  );
};

export default NarrativeFeedback;