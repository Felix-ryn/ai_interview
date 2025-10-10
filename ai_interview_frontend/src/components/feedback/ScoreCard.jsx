// src/components/feedback/ScoreCard.jsx
import React from 'react';

const ScoreCard = ({ totalScore }) => {
  const score = totalScore !== undefined && totalScore !== null ? Math.round(totalScore) : 0;
  const scoreColor = score >= 80 ? 'text-green-600' : score >= 60 ? 'text-yellow-600' : 'text-red-600';
  
  return (
    <div className="bg-white p-8 rounded-xl shadow-2xl text-center border-t-8 border-blue-600">
      <p className="text-xl font-semibold text-gray-500 mb-3">Skor Kompetensi Total</p>
      <div className={`text-8xl font-black ${scoreColor}`}>
        {score} / 100
      </div>
      <p className="mt-4 text-gray-600 italic">
        {score >= 80 
          ? "Luar biasa! Kompetensi Anda sangat kuat." 
          : score >= 60 
          ? "Bagus, namun ada ruang untuk peningkatan." 
          : "Fokus pada peningkatan di area kunci."}
      </p>
    </div>
  );
};

export default ScoreCard;