// src/components/interview/QuestionCard.jsx
import React from 'react';

const QuestionCard = ({ questionNumber, questionText }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-xl border-t-4 border-blue-500">
      <h3 className="text-xl font-bold mb-3 text-gray-800">
        Pertanyaan {questionNumber}
      </h3>
      <p className="text-lg text-gray-700">
        {questionText || "Pertanyaan belum dimuat. Mohon tunggu."}
      </p>
    </div>
  );
};

export default QuestionCard;