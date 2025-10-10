// src/hooks/useInterviewSession.js
import { useState, useCallback } from 'react';
import { startInterview, submitAnswer } from '../services/api';
import { useNavigate } from 'react-router-dom';

export const useInterviewSession = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleStartSession = useCallback(async (role, level) => {
    setLoading(true);
    setError(null);
    try {
      const data = await startInterview(role, level);
      // Backend mengembalikan session_id untuk memulai wawancara
      navigate(`/interview/${data.session_id}`); 
    } catch (err) {
      setError("Gagal memulai sesi. Pastikan backend berjalan.");
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  return { loading, error, handleStartSession };
};