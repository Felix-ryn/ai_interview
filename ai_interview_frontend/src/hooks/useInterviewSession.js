// src/hooks/useInterviewSession.js (Perbaikan)

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { startInterview } from '../services/api';

export const useInterviewSession = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // 💡 PERBAIKAN: Tambahkan roleId dan levelId di parameter
    const handleStartSession = async (role, level, userId, roleId, levelId) => { 
        setLoading(true);
        setError(null);

        try {
            // 1. Panggil API startInterview 
            const response = await startInterview(role, level);

            // 2. ***KRITIS: Simpan data sesi ke Local Storage***
            // Sekarang kita menyimpan roleId dan levelId!
            localStorage.setItem('interviewData', JSON.stringify({
                userId: userId, 
                roleId: roleId,     // 🟢 Data yang hilang, sekarang ditambahkan
                levelId: levelId,   // 🟢 Data yang hilang, sekarang ditambahkan
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