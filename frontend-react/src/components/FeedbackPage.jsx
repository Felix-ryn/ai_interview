// src/components/FeedbackPage.jsx
import React from 'react';

const FeedbackPage = ({ feedbacks = [], generatedQuestions = [], baseQuestions = [], onBack }) => {
  return (
    <div style={{ padding: 20, maxWidth: 900, margin: 'auto' }}>
      <h1>Feedback Jawaban</h1>

      {feedbacks.length === 0 ? (
        <p>Belum ada feedback.</p>
      ) : feedbacks.map((fb, idx) => (
        <div key={idx} style={{ border: '1px solid #ddd', padding: 12, borderRadius: 6, marginTop: 10 }}>
          <h3>Pertanyaan {idx + 1}</h3>
          <p><strong>Pertanyaan:</strong> {generatedQuestions[idx] ?? baseQuestions[idx]?.question ?? '(tidak tersedia)'}</p>
          <p><strong>Feedback:</strong> {fb.feedback_text}</p>
        </div>
      ))}

      {onBack && <button onClick={onBack} style={{ marginTop: 20 }}>Kembali</button>}
    </div>
  );
};

export default FeedbackPage;
