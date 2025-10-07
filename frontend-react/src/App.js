import React, { useState, useEffect } from 'react';
import axios from 'axios';

function InterviewSimulation() {
  const roles = [
    'Android Developer', 'Backend Developer', 'Data Analyst',
    'Data Engineer', 'Data Scientist', 'DevOps',
    'Frontend Developer', 'Fullstack Developer'
  ];
  const levels = ['Junior', 'Mid-Level', 'Senior'];

  const [userId] = useState(1);
  const [selectedRole, setSelectedRole] = useState(roles[0]);
  const [selectedLevel, setSelectedLevel] = useState(levels[0]);
  const [baseQuestions, setBaseQuestions] = useState([]);
  const [generatedQuestions, setGeneratedQuestions] = useState([]);
  const [answers, setAnswers] = useState([]);
  const [feedbacks, setFeedbacks] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Ambil pertanyaan dasar
  useEffect(() => {
    const fetchBaseQuestions = async () => {
      try {
        setIsLoading(true);
        const res = await axios.get('http://127.0.0.1:8000/api/v1/questions/base', {
          params: { role: selectedRole, level: selectedLevel }
        });
        setBaseQuestions(res.data);
        const initialAnswers = res.data.map(q => ({
          main_question_id: q.id,
          ml_question_id: null,
          answer_text: ''
        }));
        setAnswers(initialAnswers);
        setGeneratedQuestions([]);
        setFeedbacks([]);
      } catch (err) {
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

  // Submit jawaban ke backend
  const handleSubmitAnswers = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const payload = {
        user_id: userId,
        role: selectedRole,
        level: selectedLevel,
        answers: answers.map(a => ({
          main_question_id: a.main_question_id,
          answer_text: a.answer_text
        })),
        ai_answers: []
      };

      const res = await axios.post('http://127.0.0.1:8000/api/v1/questions/answers', payload);
      const data = res.data;

      // Simpan hasil generate dan feedback
      setGeneratedQuestions(data.generated_questions || []);
      setFeedbacks(data.feedback || []);

      // Tambahkan pertanyaan AI kosong untuk dijawab
      const newAIQuestions = (data.generated_questions || []).map((q, i) => ({
        ml_question_id: data.generated_questions_ids?.[i] || i + 1,
        answer_text: ''
      }));

      setAnswers(prev => [...prev, ...newAIQuestions]);
    } catch (err) {
      console.error(err);
      setError('Gagal mengirim jawaban ke backend.');
    } finally {
      setIsLoading(false);
    }
  };

  // Render pertanyaan + feedback
  const renderQuestion = (index) => {
    const isAI = index >= baseQuestions.length;
    const qText = isAI
      ? generatedQuestions[index - baseQuestions.length]
      : baseQuestions[index].question;

    const feedbackText = feedbacks[index]?.feedback_text;

    return (
      <div key={index} style={{
        background: '#f9f9f9',
        padding: 15,
        borderRadius: 8,
        marginTop: 15,
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      }}>
        <h2>{isAI ? `Pertanyaan AI #${index - baseQuestions.length + 1}` : `Pertanyaan #${index + 1}`}</h2>
        <p>{qText}</p>
        <textarea
          value={answers[index]?.answer_text || ''}
          onChange={(e) => handleAnswerChange(index, e.target.value)}
          rows={4}
          style={{ width: '100%', marginTop: '8px' }}
          placeholder="Tulis jawaban Anda di sini..."
        />
        {feedbackText && (
          <div style={{
            background: '#eef7ff',
            padding: '10px',
            borderRadius: '6px',
            marginTop: '10px'
          }}>
            <strong>💬 Feedback AI:</strong>
            <p>{feedbackText}</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: 'auto' }}>
      <h1>Simulasi Wawancara - {selectedRole} ({selectedLevel})</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}

      <div style={{ display: 'flex', gap: '15px', marginBottom: '20px' }}>
        <select value={selectedRole} onChange={(e) => setSelectedRole(e.target.value)}>
          {roles.map(role => <option key={role} value={role}>{role}</option>)}
        </select>
        <select value={selectedLevel} onChange={(e) => setSelectedLevel(e.target.value)}>
          {levels.map(level => <option key={level} value={level}>{level}</option>)}
        </select>
      </div>

      {[...baseQuestions, ...generatedQuestions].map((_, idx) => renderQuestion(idx))}

      <button
        onClick={handleSubmitAnswers}
        disabled={isLoading || answers.some(a => !a.answer_text)}
        style={{
          marginTop: '15px',
          padding: '10px 20px',
          cursor: 'pointer',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '5px'
        }}
      >
        {isLoading ? 'Mengirim jawaban...' : 'Kirim Semua Jawaban'}
      </button>
    </div>
  );
}

export default InterviewSimulation;
