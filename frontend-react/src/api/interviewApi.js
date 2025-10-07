// src/services/interviewAPI.js
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000/api/v1/questions'; // sesuai main.py

// Pastikan main_question_id / ml_question_id TIDAK null
export const submitAnswers = async ({ user_id, role, level, answers = [], ai_answers = [] }) => {
  const payload = {
    user_id: Number(user_id),
    role,
    level,
    answers: answers
      .filter(a => a.main_question_id !== undefined && a.main_question_id !== null)
      .map(a => ({
        main_question_id: Number(a.main_question_id),
        answer_text: a.answer_text?.trim() || ""
      })),
    ai_answers: ai_answers
      .filter(a => a.ml_question_id !== undefined && a.ml_question_id !== null)
      .map(a => ({
        ml_question_id: Number(a.ml_question_id),
        answer_text: a.answer_text?.trim() || ""
      }))
  };

  console.log("Payload dikirim ke backend:", payload);

  try {
    const res = await axios.post(`${API_BASE}/answers`, payload, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    return res.data;
  } catch (error) {
    console.error("Gagal mengirim jawaban ke backend:", error.message);
    console.error("Detail error:", error.response?.data || error);
    throw error;
  }
};

// Ambil pertanyaan dasar
export const getBaseQuestions = async (role, level) => {
  try {
    const res = await axios.get(`${API_BASE}/base`, { params: { role, level } });
    return res.data;
  } catch (error) {
    console.error("Gagal ambil pertanyaan dasar:", error.message);
    throw error;
  }
};
