// src/services/api.js
import axios from 'axios';

// **SESUAIKAN BASE_URL INI DENGAN ALAMAT BACKEND ANDA**
const BASE_URL = 'http://localhost:8000/api'; 

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * 1. Memulai Sesi Wawancara (POST /sessions/start)
 * @param {string} role - Posisi yang dipilih (e.g., 'Data Analyst')
 * @param {string} level - Level yang dipilih (e.g., 'Entry Level')
 * @returns {Promise<{session_id: string, first_question: string}>}
 */
export const startInterview = async (role, level) => {
  try {
    const response = await api.post('/sessions/start', { role, level });
    // Asumsi backend mengembalikan ID sesi dan pertanyaan pertama
    return response.data; 
  } catch (error) {
    console.error("Error starting interview:", error);
    throw error;
  }
};

/**
 * 2. Mengirim Jawaban (POST /sessions/{id}/answer)
 * @param {string} sessionId
 * @param {string} answerText - Jawaban yang diinput pengguna
 * @returns {Promise<{question_number: number, next_question: string | null}>}
 */
export const submitAnswer = async (sessionId, answerText) => {
  try {
    const response = await api.post(`/sessions/${sessionId}/answer`, { answer: answerText });
    // Backend harus mengembalikan pertanyaan berikutnya atau sinyal selesai
    return response.data; 
  } catch (error) {
    console.error("Error submitting answer:", error);
    throw error;
  }
};

/**
 * 3. Mendapatkan Laporan Akhir (GET /sessions/{id}/report)
 * @param {string} sessionId
 * @returns {Promise<Object>} - Mengandung skor, feedback naratif, dan rubrik detail
 */
export const getReport = async (sessionId) => {
  try {
    const response = await api.get(`/sessions/${sessionId}/report`);
    return response.data; // Data lengkap untuk halaman feedback
  } catch (error) {
    console.error("Error fetching report:", error);
    throw error;
  }
};

export default api;