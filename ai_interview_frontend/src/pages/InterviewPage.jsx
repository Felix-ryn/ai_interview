// src/pages/InterviewPage.jsx

import React, { useState, useEffect, useRef } from 'react'; 
import { useParams, useNavigate } from 'react-router-dom';
import { submitAnswer } from '../services/api'; 
import ProgressIndicator from '../components/common/ProgressIndicator';
import QuestionCard from '../components/interview/QuestionCard';
import Button from '../components/common/Button';

const MAX_QUESTIONS = 5;

const InterviewPage = () => {
    const { sessionId } = useParams();
    const navigate = useNavigate();
    const [questionNumber, setQuestionNumber] = useState(1);
    const [allBaseQuestions, setAllBaseQuestions] = useState([]);
    const [currentQuestionId, setCurrentQuestionId] = useState(null);
    const [currentQuestion, setCurrentQuestion] = useState("Memuat pertanyaan pertama...");
    const [answer, setAnswer] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Ref sudah ada untuk menampung ID yang diperlukan
    const userIdRef = useRef(null);
    const roleRef = useRef(""); 
    const roleIdRef = useRef(null); 
    const levelIdRef = useRef(null); 

    useEffect(() => {
        const interviewDataString = localStorage.getItem('interviewData');

        if (interviewDataString) {
            try {
                const data = JSON.parse(interviewDataString);

                // AMBIL SEMUA ID DAN ROLE DARI LOCALSTORAGE
                userIdRef.current = data.userId; 
                roleRef.current = data.role;     
                
                // 💡 INI AKAN SUKSES SETELAH useInterviewSession.js diperbaiki
                roleIdRef.current = data.roleId; 
                levelIdRef.current = data.levelId; 

                // Validasi data
                if (!data.userId || !data.roleId || !data.levelId) {
                    setError("Data sesi tidak lengkap (User/Role/Level ID hilang). Silakan mulai ulang.");
                    return;
                }

                const allQs = data.base_questions;

                if (allQs && allQs.length >= 1) {
                    setAllBaseQuestions(allQs);

                    const firstQuestion = allQs[0];
                    setCurrentQuestion(firstQuestion.question);
                    setCurrentQuestionId(firstQuestion.id);
                    setError(null); 
                } else {
                    setError("Data pertanyaan dasar tidak ditemukan. Periksa konfigurasi role/level.");
                }
            } catch (e) {
                setError("Gagal memproses data sesi dari penyimpanan lokal.");
            }
        } else {
            setError("Sesi tidak valid atau data sesi hilang. Silakan mulai wawancara baru.");
        }
    }, [sessionId]);


    const handleSubmit = async () => {
        if (!answer.trim()) return setError("Jawaban tidak boleh kosong.");

        if (!currentQuestionId || !userIdRef.current) { 
            setError("Kesalahan sesi: ID Pertanyaan atau User ID hilang. Coba mulai sesi lagi.");
            return;
        }

        // Ambil ID dari Ref yang sudah di-load di useEffect
        const mainQuestionId = allBaseQuestions[0]?.id;
        const userId = userIdRef.current;
        const roleId = roleIdRef.current;
        const levelId = levelIdRef.current;

        if (questionNumber === MAX_QUESTIONS) {
            // KASUS 3: Sesi Selesai (Menjawab Q5)
            setLoading(true);
            
            try {
                // 1. Kirim jawaban terakhir
                await submitAnswer(
                    userId,
                    sessionId,
                    answer,
                    currentQuestionId
                );

                // 2. Navigasi ke FeedbackPage dengan Query Params yang benar
                if (mainQuestionId && roleId && levelId) {
                    navigate(`/feedback?user=${userId}&mq=${mainQuestionId}&role=${roleId}&level=${levelId}`);
                } else {
                    // Tampilkan error yang sama jika ada ref yang null
                    setError("Data sesi tidak lengkap untuk melihat hasil.");
                }

            } catch (err) {
                console.error("Error submitting final answer:", err);
                setError("Gagal mengirim jawaban terakhir. Silakan coba lagi.");
            } finally {
                setLoading(false);
            }
            return; 
        }

        // ... (Logika untuk mengirim jawaban dan melanjutkan tetap sama) ...
        setLoading(true);
        setError(null);

        try {
            // 1. Kirim jawaban saat ini
            const data = await submitAnswer(
                userId, 
                sessionId,
                answer,
                currentQuestionId
            );

            const nextIndex = questionNumber;

            // KASUS 1 & 2: Lanjut ke pertanyaan berikutnya
            if (nextIndex < allBaseQuestions.length) {
                // KASUS 1: Pindah dari Q1 ke Q2 (Mengambil dari array lokal DB)
                const nextQ = allBaseQuestions[nextIndex];

                setQuestionNumber(prev => prev + 1);
                setCurrentQuestion(nextQ.question);
                setCurrentQuestionId(nextQ.id);
                setAnswer('');
            } else if (questionNumber < MAX_QUESTIONS) {
                // KASUS 2: Pindah ke Pertanyaan AI (Q3/Q4)
                const nextQuestionText = data.generated_questions && data.generated_questions[0];
                const nextQuestionId = data.generated_questions_ids && data.generated_questions_ids[0];

                const fallbackText = "Pertanyaan lanjutan AI gagal dimuat. Sesi dilanjutkan dengan pertanyaan fallback."
                const questionToDisplay = nextQuestionText || fallbackText;
                const idToUse = nextQuestionId || currentQuestionId + 1; 

                if (nextQuestionText || nextQuestionId) {
                    setQuestionNumber(prev => prev + 1);
                    setCurrentQuestion(questionToDisplay);
                    setCurrentQuestionId(idToUse);
                    setAnswer('');
                } else {
                    setError(fallbackText + " Silakan coba klik Kirim lagi.");
                }
            } 
            
        } catch (err) {
            console.error("Error submitting answer:", err);
            setError("Gagal mengirim jawaban. Coba periksa koneksi atau response backend.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 p-8">
            <ProgressIndicator current={questionNumber} total={MAX_QUESTIONS} />

            <div className="max-w-4xl mx-auto mt-8">
                <h2 className="text-xl font-semibold text-gray-600 mb-4">
                    Wawancara: {roleRef.current || 'Memuat...'}
                </h2>
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
                    {/* Pesan Error UI */}
                    {error && <p className="text-sm font-medium text-red-600 bg-red-100 p-2 rounded-lg mt-3 border border-red-300">{error}</p>}

                    <div className="flex justify-end mt-4">
                        <Button onClick={handleSubmit} disabled={loading}>
                            {loading
                                ? 'Mengirim & Menganalisis...'
                                : (questionNumber === MAX_QUESTIONS ? 'Selesai & Lihat Hasil' : 'Kirim Jawaban & Lanjut')}
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default InterviewPage;