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
 * 2. Mengirim Jawaban (POST /v1/questions/answers)
 * Catatan: Backend saat ini (app/main.py) didesain untuk menerima batch answers.
 * Kita harus membuat payload yang sesuai.
 * @param {string} sessionId - Format: sess_{main_question_id}_{Role}_{Level}
 * @param {string} answerText - Jawaban yang diinput pengguna
 * @param {number} currentQuestionId - ID dari pertanyaan yang baru saja dijawab
 * @returns {Promise<Object>} - Mengandung generated_questions dan feedback
 */
export const submitAnswer = async (sessionId, answerText, currentQuestionId) => {
    // 1. URAIKAN SESSION ID untuk mendapatkan ROLE dan LEVEL
    const parts = sessionId.split('_');
    // Session ID format: sess_{main_question_id}_{Role}_{Level}
    // Ganti %20 (jika ada) kembali ke spasi
    const role = parts[2].replace(/%20/g, ' '); 
    const level = parts[3].replace(/%20/g, ' '); 
    
    // 2. BUAT PAYLOAD SESUAI BACKEND (SubmitAnswersRequest)
    const payload = {
        user_id: 1, // <--- GANTI JIKA ADA LOGIKA LOGIN! Saat ini hardcode 1
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
        // **PERBAIKAN KRITIS: Ganti URL ke endpoint yang benar di backend**
        const response = await api.post('/v1/questions/answers', payload);
        
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