// src/components/InterviewSimulation.jsx
import React, { useState, useEffect } from 'react';
import { getBaseQuestions, submitAnswers } from '../api/interviewApi';

const InterviewSimulation = ({ userId = 1, initialRole = 'Android Developer', initialLevel = 'Junior' }) => {
  const [role, setRole] = useState(initialRole);
  const [level, setLevel] = useState(initialLevel);
  const [baseQuestions, setBaseQuestions] = useState([]);
  const [generatedQuestions, setGeneratedQuestions] = useState([]);
  const [answers, setAnswers] = useState([]);
  const [feedbacks, setFeedbacks] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load base questions
  useEffect(() => {
    const load = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getBaseQuestions(role, level);
        setBaseQuestions(data);

        // Jawaban dasar dengan main_question_id valid
        setAnswers(data.map(q => ({
          main_question_id: Number(q.id),
          answer_text: ''
        })));

        setGeneratedQuestions([]);
        setFeedbacks([]);
      } catch (err) {
        console.error("Gagal mengambil pertanyaan dasar:", err);
        setError('Gagal mengambil pertanyaan dasar.');
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, [role, level]);

  const handleAnswerChange = (index, text) => {
    setAnswers(prev => {
      const copy = [...prev];
      copy[index] = { ...copy[index], answer_text: text || '' };
      return copy;
    });
  };

  // Generate pertanyaan AI
  const handleGenerateAI = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const mainAnswers = answers
        .filter(a => a.main_question_id !== undefined && a.main_question_id !== null)
        .map(a => ({
          main_question_id: Number(a.main_question_id),
          answer_text: a.answer_text?.trim() || ''
        }));

      console.log("Payload generate AI:", { user_id: userId, role, level, answers: mainAnswers, ai_answers: [] });

      const res = await submitAnswers({
        user_id: userId,
        role,
        level,
        answers: mainAnswers,
        ai_answers: []
      });

      const genQs = res.generated_questions || [];
      const genIds = res.generated_questions_ids?.map(Number) || [];

      setGeneratedQuestions(genIds.map((id, i) => ({ id, question: genQs[i] || '' })));
      setFeedbacks(res.feedback || []);

      // Placeholder jawaban AI
      const aiPlaceholders = genIds.map(id => ({
        ml_question_id: Number(id),
        answer_text: ''
      }));

      // gabungkan jawaban dasar + AI placeholders
      setAnswers(prev => [
        ...prev.slice(0, baseQuestions.length),
        ...aiPlaceholders
      ]);
    } catch (err) {
      console.error("Gagal generate pertanyaan AI:", err);
      setError('Gagal generate pertanyaan AI.');
    } finally {
      setIsLoading(false);
    }
  };

  // Submit semua jawaban (final)
  const handleSubmitAll = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const mainAnswers = answers
        .filter(a => a.main_question_id !== undefined && a.main_question_id !== null)
        .map(a => ({
          main_question_id: Number(a.main_question_id),
          answer_text: a.answer_text?.trim() || ''
        }));

      const aiAnswers = answers
        .filter(a => a.ml_question_id !== undefined && a.ml_question_id !== null)
        .map(a => ({
          ml_question_id: Number(a.ml_question_id),
          answer_text: a.answer_text?.trim() || ''
        }));

      console.log("Payload submit all:", { user_id: userId, role, level, answers: mainAnswers, ai_answers: aiAnswers });

      const res = await submitAnswers({
        user_id: userId,
        role,
        level,
        answers: mainAnswers,
        ai_answers: aiAnswers
      });

      setFeedbacks(res.feedback || []);
      setGeneratedQuestions(res.generated_questions || generatedQuestions);
      alert('Jawaban terkirim. Feedback diperbarui.');
    } catch (err) {
      console.error("Gagal mengirim semua jawaban:", err);
      setError('Gagal mengirim semua jawaban.');
    } finally {
      setIsLoading(false);
    }
  };

  const findFeedbackFor = (idx) => {
    const isAI = idx >= baseQuestions.length;
    const id = isAI ? answers[idx]?.ml_question_id : answers[idx]?.main_question_id;
    if (!id) return null;
    const needle = isAI ? `AI ID ${id}` : `ID ${id}`;
    const found = (feedbacks || []).find(f => (f.question || '').includes(needle));
    return found?.feedback_text ?? null;
  };

  return (
    <div style={{ padding: 20, maxWidth: 900, margin: 'auto' }}>
      <h1>Simulasi Wawancara - {role} ({level})</h1>

      <div style={{ marginBottom: 12 }}>
        <label>Role: </label>
        <select value={role} onChange={e => setRole(e.target.value)} style={{ marginRight: 10 }}>
          <option>Android Developer</option>
          <option>Backend Developer</option>
          <option>Data Analyst</option>
          <option>Data Engineer</option>
          <option>Data Scientist</option>
          <option>DevOps</option>
          <option>Frontend Developer</option>
          <option>Fullstack Developer</option>
        </select>

        <label>Level: </label>
        <select value={level} onChange={e => setLevel(e.target.value)}>
          <option>Junior</option>
          <option>Mid-Level</option>
          <option>Senior</option>
        </select>
      </div>

      {[...baseQuestions.map(b => b.question), ...generatedQuestions.map(g => g.question)].map((qText, idx) => {
        const isAI = idx >= baseQuestions.length;
        const number = isAI ? idx - baseQuestions.length + 1 : idx + 1;
        return (
          <div key={idx} style={{ border: '1px solid #ddd', padding: 12, borderRadius: 6, marginBottom: 12 }}>
            <h3>{isAI ? `Pertanyaan AI #${number}` : `Pertanyaan #${number}`}</h3>
            <p style={{ whiteSpace: 'pre-wrap' }}>{qText}</p>
            <textarea
              rows={4}
              style={{ width: '100%' }}
              placeholder="Tulis jawaban Anda di sini..."
              value={answers[idx]?.answer_text || ''}
              onChange={e => handleAnswerChange(idx, e.target.value)}
            />
            {findFeedbackFor(idx) && (
              <div style={{ marginTop: 10, background: '#f6fafe', padding: 10, borderRadius: 6 }}>
                <strong>Feedback:</strong>
                <div style={{ marginTop: 6 }}>{findFeedbackFor(idx)}</div>
              </div>
            )}
          </div>
        );
      })}

      <div style={{ display: 'flex', gap: 12 }}>
        {generatedQuestions.length === 0 ? (
          <button
            onClick={handleGenerateAI}
            disabled={isLoading || answers.slice(0, baseQuestions.length).some(a => !a.answer_text)}
          >
            {isLoading ? 'Mengenerate...' : 'Kirim Jawaban Dasar & Generate AI'}
          </button>
        ) : (
          <button
            onClick={handleSubmitAll}
            disabled={isLoading || answers.slice(baseQuestions.length).some(a => !a.answer_text)}
          >
            {isLoading ? 'Mengirim semua...' : 'Kirim Semua Jawaban (Final)'}
          </button>
        )}
      </div>

      {error && <div style={{ color: 'red', marginTop: 10 }}>{error}</div>}
    </div>
  );
};

export default InterviewSimulation;
