// src/pages/InterviewPage.jsx (VERSI DIPERBAIKI)
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getReport, submitAnswer } from '../services/api';
import ProgressIndicator from '../components/common/ProgressIndicator';
import QuestionCard from '../components/interview/QuestionCard';
import Button from '../components/common/Button';

const MAX_QUESTIONS = 5;

const InterviewPage = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [questionNumber, setQuestionNumber] = useState(1);
  // 💡 PERBAIKAN: Tambahkan state untuk ID Pertanyaan saat ini
  const [currentQuestionId, setCurrentQuestionId] = useState(null); 
  const [currentQuestion, setCurrentQuestion] = useState("Memuat pertanyaan pertama...");
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // 💡 LOGIKA PERBAIKAN: Ambil ID Pertanyaan pertama dari sessionId saat komponen di-mount
    // Format sessionId yang kita buat: sess_{main_question_id}_{Role}_{Level}
    const parts = sessionId.split('_');
    if (parts.length > 1 && !currentQuestionId) {
        // Bagian kedua (indeks 1) adalah main_question_id dari pertanyaan pertama
        setCurrentQuestionId(parseInt(parts[1], 10));
    }
    // ASUMSI: Teks pertanyaan pertama (`currentQuestion`) diisi dari state global/local storage
    // atau dikirim sebagai prop saat navigasi dari HomePage.
  }, [sessionId]); // Tambahkan currentQuestionId ke dependency array jika diperlukan

  const handleSubmit = async () => {
    if (!answer.trim()) return alert("Jawaban tidak boleh kosong.");
    // 💡 PENTING: Pastikan ID pertanyaan tersedia
    if (!currentQuestionId) return setError("Kesalahan sesi: ID pertanyaan tidak ditemukan. Coba mulai sesi lagi.");

    setLoading(true);
    setError(null);

    try {
      // 💡 PERBAIKAN: Kirimkan ID Pertanyaan saat ini ke submitAnswer
      const data = await submitAnswer(sessionId, answer, currentQuestionId);

      if (questionNumber >= MAX_QUESTIONS) {
        // Sesi Selesai, navigasi ke Feedback
        navigate(`/feedback/${sessionId}`);
      } else {
        // 💡 LOGIKA PERBAIKAN: Ambil pertanyaan dan ID berikutnya dari response backend
        // Backend Anda mengembalikan generated_questions sebagai array. Kita ambil elemen pertama.
        const nextQuestionObj = data.generated_questions && data.generated_questions[0];

        if (nextQuestionObj) {
            // Lanjut ke pertanyaan berikutnya
            setQuestionNumber(prev => prev + 1);
            setCurrentQuestion(nextQuestionObj.question); // Ambil teks pertanyaan berikutnya
            setCurrentQuestionId(nextQuestionObj.id); // **UPDATE ID PERTANYAAN**
            setAnswer(''); // Reset input jawaban
        } else {
            // Skenario: LLM gagal menghasilkan pertanyaan berikutnya
            setError("Gagal mendapatkan pertanyaan lanjutan dari AI.");
            setLoading(false);
            return;
        }
      }
    } catch (err) {
      console.error("Error submitting answer:", err);
      setError("Gagal mengirim jawaban. Coba lagi.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <ProgressIndicator current={questionNumber} total={MAX_QUESTIONS} />
      
      <div className="max-w-4xl mx-auto mt-8">
        <h2 className="text-xl font-semibold text-gray-600 mb-4">Wawancara: Data Analyst</h2>
        <QuestionCard 
          questionNumber={questionNumber}
          questionText={currentQuestion}
        />
        
        <div className="mt-8 bg-white p-6 rounded-lg shadow-md">
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            rows="8"
            placeholder="Ketik jawaban Anda di sini..."
            className="w-full border border-gray-300 rounded-lg p-3 focus:ring-blue-500 focus:border-blue-500 text-sm"
            disabled={loading}
          />
          {error && <p className="text-red-500 mt-2">{error}</p>}
          
          <div className="flex justify-end mt-4">
            <Button onClick={handleSubmit} disabled={loading}>
              {loading 
                ? 'Mengirim & Menganalisis...' 
                : (questionNumber === MAX_QUESTIONS ? 'Selesai & Lihat Hasil' : 'Kirim Jawaban & Lanjut')}
            </Button>
          </div>
        </div>
        {/* TipBox akan ditambahkan di sini */}
      </div>
    </div>
  );
};

export default InterviewPage;