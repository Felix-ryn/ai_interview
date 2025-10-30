// src/pages/InterviewPage.jsx

import React, { useState, useEffect, useRef } from 'react'; 
import { useParams, useNavigate } from 'react-router-dom';
import { submitAnswer } from '../services/api'; 
import ProgressIndicator from '../components/common/ProgressIndicator';
import QuestionCard from '../components/interview/QuestionCard';
import TipBox from '../components/interview/TipBox';
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
    
    // Simulasi tips
    const currentTip = "Berikan jawaban yang detail dan spesifik. Gunakan contoh nyata dari pengalaman Anda untuk membuat jawaban lebih meyakinkan.";

    // Ref untuk menyimpan data penting dari Local Storage
    const userIdRef = useRef(null);
    const roleNameRef = useRef(""); // BARU: Nama Role
    const levelNameRef = useRef(""); // BARU: Nama Level
    const roleIdRef = useRef(null); 
    const levelIdRef = useRef(null); 
    const mainQuestionIdRef = useRef(null); 

    useEffect(() => {
        const interviewDataString = localStorage.getItem('interviewData');

        if (interviewDataString) {
            try {
                const data = JSON.parse(interviewDataString);

                // AMBIL SEMUA ID DAN NAMA DARI LOCALSTORAGE
                userIdRef.current = data.userId; 
                roleNameRef.current = data.roleName;    // Set Nama Role
                levelNameRef.current = data.levelName;   // Set Nama Level
                roleIdRef.current = data.roleId; 
                levelIdRef.current = data.levelId; 

                // Validasi data
                if (!data.userId || !data.roleId || !data.levelId || !data.roleName || !data.levelName) {
                    setError("Data sesi tidak lengkap (User/Role/Level ID atau Nama hilang). Silakan mulai ulang.");
                    return;
                }

                const allQs = data.base_questions;

                if (allQs && allQs.length >= 1) {
                    setAllBaseQuestions(allQs);
                    mainQuestionIdRef.current = allQs[0].id; // Set ID Pertanyaan Utama (digunakan di FeedbackPage)

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

        const userId = userIdRef.current;
        const roleName = roleNameRef.current; // Digunakan di submitAnswer
        const levelName = levelNameRef.current; // Digunakan di submitAnswer
        const currentQId = currentQuestionId;
        const mainQId = mainQuestionIdRef.current;
        const roleId = roleIdRef.current;
        const levelId = levelIdRef.current;


        if (!currentQId || !userId || !roleName || !levelName || !mainQId || !roleId || !levelId) { 
            setError("Kesalahan sesi: ID Pertanyaan atau User/Role/Level data hilang. Coba mulai sesi lagi.");
            return;
        }

        setLoading(true);
        setError(null);

        try {
            // 1. Kirim jawaban saat ini
            const data = await submitAnswer(
                userId, 
                roleName, // BARU: Kirim nama role
                levelName, // BARU: Kirim nama level
                answer,
                currentQId
            );

            // 2. Pindah ke pertanyaan berikutnya (atau selesai)
            if (questionNumber === MAX_QUESTIONS) {
                // KASUS 3: Sesi Selesai (Menjawab Q5)
                localStorage.removeItem('interviewData'); // Clear storage setelah selesai
                
                // Kirim ID (user, mq, role, level) ke FeedbackPage
                navigate(`/feedback?user=${userId}&mq=${mainQId}&role=${roleId}&level=${levelId}`);
                return; 
            }

            // Dapatkan pertanyaan lanjutan AI
            const generatedQuestions = data.generated_questions || [];
            const generatedIds = data.generated_questions_ids || [];

            const nextIndex = questionNumber;

            if (nextIndex < allBaseQuestions.length) {
                // KASUS 1: Pindah dari Q1 ke Q2 (Mengambil dari array lokal DB)
                const nextQ = allBaseQuestions[nextIndex];

                setQuestionNumber(prev => prev + 1);
                setCurrentQuestion(nextQ.question);
                setCurrentQuestionId(nextQ.id);
                setAnswer('');
            } else if (questionNumber < MAX_QUESTIONS && generatedQuestions.length > 0) {
                // KASUS 2: Pindah ke Pertanyaan AI (Q3, Q4, atau Q5)
                const nextQuestionText = generatedQuestions[0];
                const nextQuestionId = generatedIds[0];
                
                // Jika API memberikan pertanyaan AI baru
                if (nextQuestionText && nextQuestionId) {
                    setQuestionNumber(prev => prev + 1);
                    setCurrentQuestion(nextQuestionText);
                    setCurrentQuestionId(nextQuestionId);
                    setAnswer('');
                } 
            } else {
                // Fallback jika API gagal memberi pertanyaan, namun belum MAX_QUESTIONS
                setQuestionNumber(prev => prev + 1);
                setCurrentQuestion(`Pertanyaan Lanjutan ${questionNumber + 1}: Mohon berikan ringkasan atau poin penutup dari wawancara Anda.`);
                setCurrentQuestionId(currentQId + 1); // ID dinaikkan secara lokal (semoga sesuai dengan ID yang diharapkan backend)
                setAnswer('');
                setError("Backend tidak memberikan pertanyaan lanjutan AI, menggunakan pertanyaan fallback. Pastikan backend berfungsi dengan baik.");
            }
            
        } catch (err) {
            console.error("Error submitting answer:", err);
            const apiError = err.response?.data?.detail || err.message || "Gagal mengirim jawaban. Coba periksa koneksi atau response backend.";
            setError(apiError);
        } finally {
            setLoading(false);
        }
    };

    const isFinished = questionNumber === MAX_QUESTIONS;
    const buttonText = isFinished ? "Kirim & Lihat Hasil" : "Kirim Jawaban";

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-8">
            <div className="max-w-4xl mx-auto space-y-6">
                
                {/* Header & Progress */}
                <header className="flex justify-between items-end border-b pb-4 border-gray-200">
                    <div>
                        <h1 className="text-3xl font-extrabold text-gray-900">Interview: {roleNameRef.current || 'Memuat...'}</h1>
                        <p className="text-sm text-gray-500">Kandidat: {userIdRef.current || 'N/A'} • Level: {levelNameRef.current || 'N/A'}</p>
                    </div>
                    <div className="text-right">
                        <ProgressIndicator current={questionNumber} total={MAX_QUESTIONS} />
                    </div>
                </header>

                {/* Question Card */}
                <QuestionCard
                    questionNumber={questionNumber}
                    questionText={currentQuestion}
                />

                {/* Area Input Jawaban */}
                <div className="mt-8 bg-white p-6 rounded-xl shadow-lg border-t-2 border-gray-100">
                    <label htmlFor="answer" className="block text-sm font-semibold text-gray-700 mb-2">Jawaban Anda</label>
                    <textarea
                        id="answer"
                        value={answer}
                        onChange={(e) => setAnswer(e.target.value)}
                        placeholder="Ketik jawaban Anda di sini..."
                        rows={8}
                        className="block w-full border border-gray-200 rounded-lg p-3 focus:ring-blue-500 focus:border-blue-500 transition duration-150 text-gray-800 resize-none"
                        disabled={loading}
                    />
                    <p className="mt-1 text-xs text-gray-500 text-right">{answer.length} karakter</p>

                    {/* Tombol Aksi */}
                    <div className="mt-4 flex space-x-4">
                        <div className="w-full">
                            <Button onClick={handleSubmit} disabled={loading || !answer.trim()}>
                                {loading ? (
                                    <span className="flex items-center justify-center">
                                        <svg className="animate-spin h-5 w-5 mr-3 text-white" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path></svg>
                                        Mengirim Jawaban...
                                    </span>
                                ) : (
                                    <span className="flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor"><path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l.493-.198a1 1 0 00.704-.984V14l4.322-4.322a1 1 0 011.414 0L14 14v2.586a1 1 0 00.704.984l.493.198a1 1 0 001.169-1.409l-7-14z"/></svg>
                                        {buttonText}
                                    </span>
                                )}
                            </Button>
                        </div>
                    </div>
                </div>

                {/* Tip Box */}
                <TipBox tipText={currentTip} />

                {error && (
                    <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                        {error}
                    </div>
                )}
            </div>
        </div>
    );
};

export default InterviewPage;