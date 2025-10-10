// src/pages/InterviewPage.jsx
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
  const [currentQuestion, setCurrentQuestion] = useState("Memuat pertanyaan pertama...");
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Logic untuk memuat pertanyaan pertama di sini jika belum dimuat di HomePage
    // Karena kita sudah memuatnya di useInterviewSession, ini akan disederhanakan
    // ASUMSI: Pertanyaan pertama sudah dimasukkan ke state di backend atau di startInterview
    // Jika tidak, Anda perlu membuat endpoint GET /sessions/{id}/current_question
  }, [sessionId]);


  const handleSubmit = async () => {
    if (!answer.trim()) return alert("Jawaban tidak boleh kosong.");

    setLoading(true);
    setError(null);

    try {
      const data = await submitAnswer(sessionId, answer);

      if (questionNumber >= MAX_QUESTIONS) {
        // Sesi Selesai, navigasi ke Feedback
        navigate(`/feedback/${sessionId}`);
      } else {
        // Lanjut ke pertanyaan berikutnya
        setQuestionNumber(prev => prev + 1);
        setCurrentQuestion(data.next_question); // Ambil dari respons backend
        setAnswer(''); // Reset input jawaban
      }
    } catch (err) {
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