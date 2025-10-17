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
 * Mengambil daftar Role dari backend.
 * @returns {Promise<Array<{id: number, role_name: string}>>}
 */
export const fetchRoles = async () => {
  try {
    const response = await api.get('/v1/roles');
    return response.data;
  } catch (error) {
    console.error("Error fetching roles:", error);
    throw error;
  }
};

/**
 * Mengambil daftar Level dari backend.
 * @returns {Promise<Array<{id: number, level_name: string}>>}
 */
export const fetchLevels = async () => {
  try {
    const response = await api.get('/v1/levels');
    return response.data;
  } catch (error) {
    console.error("Error fetching levels:", error);
    throw error;
  }
};

/**
 * Mendaftarkan user baru sebelum sesi wawancara.
 * @param {string} name - Nama pengguna
 * @param {number} roleId - ID Role (ref_role_id)
 * @param {number} levelId - ID Level (ref_level_id)
 * @returns {Promise<{user_id: number, name: string, message: string}>}
 */
export const registerUser = async (name, roleId, levelId) => {
  try {
    const response = await api.post('/v1/register', {
      name,
      role_id: roleId,
      level_id: levelId
    });
    return response.data;
  } catch (error) {
    console.error("Error registering user:", error);
    // Tangani pesan error dari backend
    if (error.response && error.response.data && error.response.data.detail) {
      throw new Error(error.response.data.detail);
    }
    throw error;
  }
};

export const startInterview = async (role, level) => {
  try {
    const response = await api.post('/sessions/start', { role, level });
    return response.data;
  } catch (error) {
    console.error("Error starting interview:", error);
    throw error;
  }
};

/**
 * 2. Mengirim Jawaban (POST /v1/questions/answers)
 * @param {number} userId - ID User yang baru terdaftar. 👈 **BARU**
 * @param {string} sessionId - Format: sess_{main_question_id}_{Role}_{Level}
 * @param {string} answerText - Jawaban yang diinput pengguna
 * @param {number} currentQuestionId - ID dari pertanyaan yang baru saja dijawab
 * @returns {Promise<Object>} - Mengandung generated_questions dan feedback
 */
export const submitAnswer = async (userId, sessionId, answerText, currentQuestionId) => { // 👈 **MENERIMA userId**
  // 1. URAIKAN SESSION ID untuk mendapatkan ROLE dan LEVEL
  const parts = sessionId.split('_');
  // Session ID format: sess_{main_question_id}_{Role}_{Level}
  const role = parts[2].replace(/%20/g, ' ');
  const level = parts[3].replace(/%20/g, ' ');

  // 2. BUAT PAYLOAD SESUAI BACKEND (SubmitAnswersRequest)
  const payload = {
    user_id: userId, // 👈 **MENGGUNAKAN userId YANG DITERIMA**
    role: role,
    level: level,
    // Backend mengharapkan array answers. Kita kirim jawaban saat ini.
    answers: [{
      main_question_id: currentQuestionId,
      answer_text: answerText
    }],
    // Backend mengharapkan array ai_answers, yang kosong di tahap ini
    ai_answers: []
  };

  try {
    // Endpoint yang benar untuk submit jawaban dan generate pertanyaan/feedback
    const response = await api.post('/v1/questions/answers', payload);

    return response.data;
  } catch (error) {
    console.error("Error submitting answer:", error);
    throw error;
  }
};


/**
 * 3. Mendapatkan Laporan Akhir (GET /sessions/{id}/report)
 */
export const getReport = async (sessionId) => {
  try {
    const response = await api.get(`/sessions/${sessionId}/report`);
    return response.data;
  } catch (error) {
    console.error("Error fetching report:", error);
    throw error;
  }
};

export default api;