import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { startInterview } from '../services/api';

export const useInterviewSession = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleStartSession = async (role, level) => {
        setLoading(true);
        setError(null);

        try {
            // 1. Panggil API startInterview (Backend merespons 200 OK)
            // response.data berisi { session_id, base_questions: [...] }
            const response = await startInterview(role, level);

            // 2. ***KRITIS: Simpan data sesi ke Local Storage***
            // Gunakan kunci 'interviewData' yang dibaca oleh InterviewPage.jsx
            localStorage.setItem('interviewData', JSON.stringify({
                sessionId: response.session_id,
                base_questions: response.base_questions // Simpan array 2 pertanyaan dari DB
            }));

            // 3. Navigasi ke halaman wawancara
            navigate(`/interview/${response.session_id}`);

        } catch (err) {
            console.error("Error starting session:", err);
            // Tangani error jika koneksi gagal atau 404 dari backend (tidak ada pertanyaan)
            const errorMessage = err.response?.data?.detail || "Gagal memulai sesi. Coba periksa koneksi backend.";
            setError(errorMessage);
            setLoading(false);
        }
    };

    return { loading, error, handleStartSession };
};
