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
 * Mengirim Jawaban (POST /v1/questions/answers)
 */
export const submitAnswer = async (userId, sessionId, answerText, currentQuestionId) => {
  // 1. URAIKAN SESSION ID untuk mendapatkan ROLE dan LEVEL
  const parts = sessionId.split('_');
  // Session ID format: sess_{main_question_id}_{Role}_{Level}
  const role = parts[2].replace(/%20/g, ' ');
  const level = parts[3].replace(/%20/g, ' ');

  // 2. BUAT PAYLOAD SESUAI BACKEND (SubmitAnswersRequest)
  const payload = {
    user_id: userId,
    role: role,
    level: level,
    // Backend mengharapkan array answers. Kita kirim jawaban saat ini.
    answers: [{
      main_question_id: currentQuestionId,
      answer_text: answerText
    }],
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
 * BARU/MODIFIKASI: Mendapatkan Laporan Akhir (POST /v1/feedback)
 * Mengirim data ID dan memicu evaluasi final di backend.
 * * @param {number} userId - ID User
 * @param {number} mainQuestionId - ID Pertanyaan Utama (sesi)
 * @param {number} roleId - ID Role
 * @param {number} levelId - ID Level
 * @returns {Promise<FinalFeedback>} - Objek FinalFeedback dari backend
 */
export const getFinalFeedback = async (userId, mainQuestionId, roleId, levelId) => {
  const payload = {
    user_id: userId,
    main_question_id: mainQuestionId,
    role_id: roleId,
    level_id: levelId
  };

  try {
    // Memanggil endpoint /feedback yang memicu proses kalibrasi
    const response = await api.post('/v1/feedback', payload);
    return response.data;
  } catch (error) {
    console.error("Error fetching final feedback:", error);
    // Perlu penanganan error yang lebih spesifik di FeedbackPage
    throw error;
  }
};

export default api;