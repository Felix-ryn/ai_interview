// src/components/InterviewSimulation.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const InterviewSimulation = ({ userId, role, level }) => {
    const [baseQuestions, setBaseQuestions] = useState([]);
    const [generatedQuestions, setGeneratedQuestions] = useState([]);
    const [answers, setAnswers] = useState([]); // gabungan jawaban dasar + AI
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    // Ambil pertanyaan dasar
    useEffect(() => {
        const fetchBaseQuestions = async () => {
            try {
                setIsLoading(true);
                const res = await axios.get('http://127.0.0.1:8000/api/v1/questions/base', {
                    params: { role, level }
                });
                setBaseQuestions(res.data);

                // Inisialisasi jawaban kosong untuk pertanyaan dasar
                const initialAnswers = res.data.map(q => ({
                    main_question_id: q.id,
                    answer_text: ''
                }));
                setAnswers(initialAnswers);

            } catch (err) {
                console.error(err);
                setError('Gagal memuat pertanyaan dasar.');
            } finally {
                setIsLoading(false);
            }
        };
        fetchBaseQuestions();
    }, [role, level]);

    // Update jawaban
    const handleAnswerChange = (index, text) => {
        const updated = [...answers];
        updated[index].answer_text = text;
        setAnswers(updated);
    };

    // Submit jawaban + generate pertanyaan AI
    const handleSubmitAnswers = async () => {
        setIsLoading(true);
        setError(null);
        try {
            // Pisahkan jawaban dasar
            const baseAnswers = answers.slice(0, baseQuestions.length).map(a => ({
                main_question_id: a.main_question_id,
                answer_text: a.answer_text
            }));

            // Kirim jawaban dasar ke backend untuk generate AI
            const response = await axios.post('http://127.0.0.1:8000/api/v1/questions/answers', {
                user_id: userId,
                role,
                level,
                answers: baseAnswers,
                ai_answers: [] // awalnya kosong
            });

            const data = response.data;

            // Set pertanyaan AI
            setGeneratedQuestions(data.generated_questions || []);

            // Tambahkan jawaban kosong untuk pertanyaan AI di state
            const aiAnswers = (data.generated_questions || []).map((q, idx) => ({
                ml_question_id: data.generated_questions_ids[idx],
                answer_text: ''
            }));

            setAnswers(prev => [...prev.slice(0, baseQuestions.length), ...aiAnswers]);

        } catch (err) {
            console.error(err);
            setError('Gagal mengirim jawaban ke backend.');
        } finally {
            setIsLoading(false);
        }
    };

    // Submit jawaban lengkap (termasuk AI) ke backend
    const handleSubmitAllAnswers = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const baseAnswers = answers.slice(0, baseQuestions.length).map(a => ({
                main_question_id: a.main_question_id,
                answer_text: a.answer_text
            }));

            const aiAnswers = answers.slice(baseQuestions.length).map(a => ({
                ml_question_id: a.ml_question_id,
                answer_text: a.answer_text
            }));

            await axios.post('http://127.0.0.1:8000/api/v1/questions/answers', {
                user_id: userId,
                role,
                level,
                answers: baseAnswers,
                ai_answers: aiAnswers
            });

            alert('Jawaban berhasil dikirim!');
        } catch (err) {
            console.error(err);
            setError('Gagal mengirim jawaban AI ke backend.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="interview-container">
            <h1>Simulasi Wawancara - {role} ({level})</h1>
            {error && <p style={{ color: 'red' }}>{error}</p>}

            {/* Render pertanyaan dasar + AI */}
            {[...baseQuestions, ...generatedQuestions].map((q, idx) => {
                const isAI = idx >= baseQuestions.length;
                return (
                    <div key={idx} className="question-area" style={{ marginTop: '20px' }}>
                        <h2>{isAI ? `Pertanyaan AI #${idx - baseQuestions.length + 1}` : `Pertanyaan #${idx + 1}`}</h2>
                        <p>{isAI ? q : q.question}</p>
                        <textarea
                            value={answers[idx]?.answer_text || ''}
                            onChange={(e) => handleAnswerChange(idx, e.target.value)}
                            rows={4}
                            style={{ width: '100%', marginTop: '8px' }}
                            placeholder="Tulis jawaban Anda di sini..."
                        />
                    </div>
                );
            })}

            {/* Tombol submit untuk generate AI */}
            {generatedQuestions.length === 0 && (
                <button
                    onClick={handleSubmitAnswers}
                    disabled={isLoading || answers.some(a => !a.answer_text)}
                    style={{ marginTop: '15px', padding: '10px 20px', cursor: 'pointer' }}
                >
                    {isLoading ? 'Mengirim jawaban...' : 'Kirim Jawaban Dasar & Generate AI'}
                </button>
            )}

            {/* Tombol submit jawaban AI */}
            {generatedQuestions.length > 0 && (
                <button
                    onClick={handleSubmitAllAnswers}
                    disabled={isLoading || answers.slice(baseQuestions.length).some(a => !a.answer_text)}
                    style={{ marginTop: '15px', padding: '10px 20px', cursor: 'pointer' }}
                >
                    {isLoading ? 'Mengirim jawaban AI...' : 'Kirim Semua Jawaban'}
                </button>
            )}
        </div>
    );
};

export default InterviewSimulation;
