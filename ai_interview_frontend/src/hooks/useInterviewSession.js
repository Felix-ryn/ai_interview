// src/hooks/useInterviewSession.js 

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { startInterview } from '../services/api';

export const useInterviewSession = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleStartSession = async (role, level, userId) => {
        setLoading(true);
        setError(null);

        try {
            // 1. Panggil API startInterview 
            const response = await startInterview(role, level);

            // 2. ***KRITIS: Simpan data sesi ke Local Storage***
            // Tambahkan userId ke data sesi
            localStorage.setItem('interviewData', JSON.stringify({
                userId: userId, // <<< TAMBAH USER ID
                sessionId: response.session_id,
                role: role,
                level: level,
                base_questions: response.base_questions
            }));

            // 3. Navigasi ke halaman wawancara
            navigate(`/interview/${response.session_id}`);

        } catch (err) {
            console.error("Error starting session:", err);
            const errorMessage = err.response?.data?.detail || "Gagal memulai sesi. Coba periksa koneksi backend.";
            setError(errorMessage);
            setLoading(false);
        }
    };

    return { loading, setLoading, error, setError, handleStartSession };
};