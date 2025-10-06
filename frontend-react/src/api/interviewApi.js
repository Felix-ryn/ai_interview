import axios from 'axios';

// Fungsi untuk memanggil backend FastAPI
export const generateNextQuestion = async (userId, role, level, answers = []) => {
  try {
    const response = await axios.post(
      'http://127.0.0.1:8000/api/v1/questions/answers',
      {
        user_id: userId,
        role: role,
        level: level,
        answers: answers  // ✅ wajib
      }
    );
    return response.data;
  } catch (error) {
    console.error('Gagal memanggil API:', error.response?.data || error.message);
    throw error;
  }
};
