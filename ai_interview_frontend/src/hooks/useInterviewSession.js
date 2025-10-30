// src/hooks/useInterviewSession.js

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { startInterview } from '../services/api'; 

export const useInterviewSession = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Sekarang menerima roleName dan levelName
    const handleStartSession = async (roleName, levelName, userId, roleId, levelId) => { 
        setLoading(true);
        setError(null);

        try {
            // 1. Panggil API startInterview dengan NAMA role dan level
            const response = await startInterview(roleName, levelName);

            // 2. Simpan SEMUA data sesi (ID dan NAMA) ke Local Storage
            localStorage.setItem('interviewData', JSON.stringify({
                userId: userId, 
                roleId: roleId, 
                levelId: levelId, 
                sessionId: response.session_id,
                roleName: roleName, // NAMA ROLE
                levelName: levelName, // NAMA LEVEL
                base_questions: response.base_questions
            }));

            // 3. Navigasi ke halaman wawancara
            navigate(`/interview/${response.session_id}`);

        } catch (err) {
            console.error("Error starting session:", err);
            const errorMessage = err.message || "Gagal memulai sesi. Coba periksa koneksi backend.";
            setError(errorMessage);
            setLoading(false);
        }
    };

    return { loading, setLoading, error, setError, handleStartSession };
};