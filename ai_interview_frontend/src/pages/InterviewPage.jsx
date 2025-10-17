// src/pages/InterviewPage.jsx

import React, { useState, useEffect, useRef } from 'react'; // Menambahkan useRef
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
    const [allBaseQuestions, setAllBaseQuestions] = useState([]);
    const [currentQuestionId, setCurrentQuestionId] = useState(null);
    const [currentQuestion, setCurrentQuestion] = useState("Memuat pertanyaan pertama...");
    const [answer, setAnswer] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // 💡 KRITIS: Gunakan useRef untuk menyimpan USER ID
    const userIdRef = useRef(null);
    const roleRef = useRef(""); // Simpan Role untuk judul

    useEffect(() => {
        // Logika ini membaca data yang disimpan oleh useInterviewSession.js
        const interviewDataString = localStorage.getItem('interviewData');

        if (interviewDataString) {
            try {
                const data = JSON.parse(interviewDataString);

                // 💡 AMBIL USER ID DAN ROLE DARI LOCALSTORAGE
                userIdRef.current = data.userId; // Simpan user ID di ref
                roleRef.current = data.role;     // Simpan Role di ref

                // Validasi data
                if (!data.userId) {
                    setError("Data sesi tidak lengkap (User ID hilang). Silakan mulai ulang.");
                    return;
                }

                const allQs = data.base_questions;

                if (allQs && allQs.length >= 1) {
                    setAllBaseQuestions(allQs);

                    // Inisialisasi: Tampilkan pertanyaan pertama (index 0)
                    const firstQuestion = allQs[0];
                    setCurrentQuestion(firstQuestion.question);
                    setCurrentQuestionId(firstQuestion.id);
                    setError(null); // Hapus error jika berhasil dimuat
                } else {
                    setError("Data pertanyaan dasar tidak ditemukan. Periksa konfigurasi role/level.");
                }
            } catch (e) {
                // Ini menangani error jika JSON.parse gagal
                setError("Gagal memproses data sesi dari penyimpanan lokal.");
            }
        } else {
            // Ini menangani error jika 'interviewData' belum ada di localStorage
            setError("Sesi tidak valid atau data sesi hilang. Silakan mulai wawancara baru.");
        }
    }, [sessionId]);


    const handleSubmit = async () => {
        if (!answer.trim()) return setError("Jawaban tidak boleh kosong.");

        if (!currentQuestionId || !userIdRef.current) { // 💡 VALIDASI USER ID
            setError("Kesalahan sesi: ID Pertanyaan atau User ID hilang. Coba mulai sesi lagi.");
            return;
        }

        setLoading(true);
        setError(null);

        try {
            // 1. Kirim jawaban saat ini
            // 💡 PERUBAHAN KRITIS: Kirim userIdRef.current
            const data = await submitAnswer(
                userIdRef.current, // 👈 KIRIM USER ID YANG BENAR
                sessionId,
                answer,
                currentQuestionId
            );

            const nextIndex = questionNumber;

            // Cek apakah ada pertanyaan berikutnya di array lokal (untuk Q2)
            if (nextIndex < allBaseQuestions.length) {
                // KASUS 1: Pindah dari Q1 ke Q2 (Mengambil dari array lokal DB)

                const nextQ = allBaseQuestions[nextIndex];

                setQuestionNumber(prev => prev + 1);
                setCurrentQuestion(nextQ.question);
                setCurrentQuestionId(nextQ.id);
                setAnswer('');

            } else if (questionNumber < MAX_QUESTIONS) {
                // KASUS 2: Pindah dari Q2 ke Q3 (Mengambil dari response AI)
                // Backend merespons generated_questions (teks) dan generated_questions_ids (ID)

                const nextQuestionText = data.generated_questions && data.generated_questions[0];
                const nextQuestionId = data.generated_questions_ids && data.generated_questions_ids[0];

                // 💡 Fallback jika AI gagal (karena Quota 429)
                const fallbackText = "Pertanyaan lanjutan AI gagal dimuat. Sesi dilanjutkan dengan pertanyaan fallback."
                const questionToDisplay = nextQuestionText || fallbackText;
                const idToUse = nextQuestionId || currentQuestionId + 1; // ID sementara jika ID AI hilang

                if (nextQuestionText || nextQuestionId) {
                    setQuestionNumber(prev => prev + 1);
                    setCurrentQuestion(questionToDisplay);
                    setCurrentQuestionId(idToUse); // Gunakan ID yang dikembalikan AI
                    setAnswer('');
                } else {
                    // Jika LLM gagal memberikan pertanyaan baru, kita tunjukkan error
                    setError(fallbackText + " Silakan coba klik Kirim lagi.");
                }
            } else {
                // KASUS 3: Sesi Selesai (Menjawab Q5)
                navigate(`/feedback/${sessionId}`);
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