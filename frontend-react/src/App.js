// src/App.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const roles = [
  'Android Developer', 'Backend Developer', 'Data Analyst',
  'Data Engineer', 'Data Scientist', 'DevOps',
  'Frontend Developer', 'Fullstack Developer'
];
const levels = ['Junior', 'Mid-Level', 'Senior'];

function App() {
  const [userId] = useState(1);
  const [selectedRole, setSelectedRole] = useState(roles[0]);
  const [selectedLevel, setSelectedLevel] = useState(levels[0]);

  const [baseQuestions, setBaseQuestions] = useState([]);
  const [generatedQuestions, setGeneratedQuestions] = useState([]);
  const [answers, setAnswers] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Ambil 2 pertanyaan dasar saat role/level berubah
  useEffect(() => {
    const fetchBaseQuestions = async () => {
      try {
        setIsLoading(true);
        const res = await axios.get('http://127.0.0.1:8000/api/v1/questions/base', {
          params: { role: selectedRole, level: selectedLevel }
        });
        setBaseQuestions(res.data);

        // Inisialisasi jawaban untuk pertanyaan dasar
        const initialAnswers = res.data.map(q => ({
          main_question_id: q.id,
          ml_question_id: null,
          answer_text: ''
        }));
        setAnswers(initialAnswers);
        setGeneratedQuestions([]);
      } catch (err) {
        console.error(err);
        setError('Gagal memuat pertanyaan dasar.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchBaseQuestions();
  }, [selectedRole, selectedLevel]);

  const handleAnswerChange = (index, text) => {
    const updated = [...answers];
    updated[index].answer_text = text;
    setAnswers(updated);
  };

  // Submit jawaban & generate pertanyaan AI
  const handleSubmitAnswers = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Persiapkan payload sesuai schema backend
      const payload = {
        user_id: userId,
        role: selectedRole,
        level: selectedLevel,
        answers: answers
          .slice(0, baseQuestions.length)
          .map(a => ({
            main_question_id: a.main_question_id,
            answer_text: a.answer_text
          })),
        ai_answers: answers
          .slice(baseQuestions.length)
          .filter(a => a.ml_question_id !== null)
          .map(a => ({
            ml_question_id: a.ml_question_id,
            answer_text: a.answer_text
          }))
      };

      // Kirim ke backend
      const res = await axios.post('http://127.0.0.1:8000/api/v1/questions/answers', payload);
      const data = res.data;

      // Update pertanyaan AI
      setGeneratedQuestions(data.generated_questions || []);

      // Tambahkan jawaban kosong untuk pertanyaan AI
      const aiAnswers = (data.generated_questions || []).map((q, idx) => ({
        ml_question_id: data.generated_questions_ids[idx], // HARUS integer
        answer_text: ''
      }));

      // Gabungkan jawaban pertanyaan dasar + AI
      setAnswers(prev => [...prev.slice(0, baseQuestions.length), ...aiAnswers]);
    } catch (err) {
      console.error(err);
      setError('Gagal mengirim jawaban ke backend.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderQuestion = (index) => {
    const isAI = index >= baseQuestions.length;
    const qText = isAI
      ? generatedQuestions[index - baseQuestions.length]
      : baseQuestions[index].question;

    return (
      <div key={index} className="question-area" style={{ marginTop: '20px' }}>
        <h2>{isAI ? `Pertanyaan AI #${index - baseQuestions.length + 1}` : `Pertanyaan #${index + 1}`}</h2>
        <p>{qText}</p>
        <textarea
          value={answers[index]?.answer_text || ''}
          onChange={(e) => handleAnswerChange(index, e.target.value)}
          rows={4}
          style={{ width: '100%', marginTop: '8px' }}
          placeholder="Tulis jawaban Anda di sini..."
        />
      </div>
    );
  };

  return (
    <div className="interview-container">
      <h1>Simulasi Wawancara - {selectedRole} ({selectedLevel})</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {/* Pilihan role/level */}
      <div style={{ display: 'flex', gap: '15px', marginBottom: '20px' }}>
        <select value={selectedRole} onChange={(e) => setSelectedRole(e.target.value)}>
          {roles.map(role => <option key={role} value={role}>{role}</option>)}
        </select>
        <select value={selectedLevel} onChange={(e) => setSelectedLevel(e.target.value)}>
          {levels.map(level => <option key={level} value={level}>{level}</option>)}
        </select>
      </div>

      {/* Render semua pertanyaan */}
      {[...baseQuestions, ...generatedQuestions].map((_, idx) => renderQuestion(idx))}

      <button
        onClick={handleSubmitAnswers}
        disabled={isLoading || answers.some(a => !a.answer_text)}
        style={{ marginTop: '15px', padding: '10px 20px', cursor: 'pointer' }}
      >
        {isLoading ? 'Mengirim jawaban...' : 'Kirim Semua Jawaban'}
      </button>
    </div>
  );
}

export default App;
