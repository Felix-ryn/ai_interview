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
    // Pastikan response.data memiliki user_id
    return response.data;
  } catch (error) {
    console.error("Error registering user:", error);
    if (error.response && error.response.data && error.response.data.detail) {
      throw new Error(error.response.data.detail);
    }
    throw error;
  }
};

/**
 * Memulai sesi wawancara.
 * @param {string} role - Nama Role
 * @param {string} level - Nama Level
 * @returns {Promise<{session_id: string, base_questions: Array<Object>}>}
 */
export const startInterview = async (role, level) => {
  try {
    // Endpoint lama: /sessions/start
    // Endpoint baru: /v1/sessions/start (disesuaikan dengan skema v1 Anda)
    const response = await api.post('/v1/sessions/start', { role, level });
    return response.data;
  } catch (error) {
    console.error("Error starting interview:", error);
    throw error;
  }
};

/**
 * Mengirim Jawaban (POST /v1/questions/answers)
 * @param {number} userId - ID User
 * @param {string} roleName - Nama Role
 * @param {string} levelName - Nama Level
 * @param {string} answerText - Teks jawaban
 * @param {number} currentQuestionId - ID pertanyaan yang sedang dijawab
 * @returns {Promise<Object>} - Respons dari backend
 */
export const submitAnswer = async (userId, roleName, levelName, answerText, currentQuestionId) => {
  // Perbaikan: Ambil roleName dan levelName sebagai parameter langsung dari hook/page.
  const payload = {
    user_id: userId,
    role: roleName, // Dikirim langsung
    level: levelName, // Dikirim langsung
    answers: [{
      main_question_id: currentQuestionId, // ID Pertanyaan saat ini
      answer_text: answerText
    }],
    ai_answers: []
  };

  try {
    const response = await api.post('/v1/questions/answers', payload);

    return response.data;
  } catch (error) {
    console.error("Error submitting answer:", error);
    throw error;
  }
};


/**
 * Mendapatkan Laporan Akhir (POST /v1/feedback)
 * @param {number} userId - ID User
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
    const response = await api.post('/v1/feedback', payload);
    return response.data;
  } catch (error) {
    console.error("Error fetching final feedback:", error);
    throw error;
  }
};

export default api;