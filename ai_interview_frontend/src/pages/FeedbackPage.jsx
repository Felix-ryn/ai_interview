// src/pages/FeedbackPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getReport } from '../services/api';
import ScoreCard from '../components/feedback/ScoreCard';
import NarrativeFeedback from '../components/feedback/NarrativeFeedback';
import DetailedRubric from '../components/feedback/DetailedRubric';

const FeedbackPage = () => {
  const { sessionId } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const data = await getReport(sessionId);
        setReport(data);
      } catch (err) {
        setError("Gagal memuat laporan. ID Sesi mungkin tidak valid.");
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, [sessionId]);

  if (loading) return <div className="p-8 text-center">Memuat Laporan...</div>;
  if (error) return <div className="p-8 text-center text-red-600">{error}</div>;
  if (!report) return <div className="p-8 text-center">Laporan tidak tersedia.</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-5xl mx-auto space-y-10">
        <h1 className="text-4xl font-extrabold text-gray-900 text-center">Hasil Wawancaramu</h1>

        {/* Skor Total */}
        <ScoreCard totalScore={report.total_score} /> 

        {/* Feedback Naratif dari LLM */}
        <NarrativeFeedback feedbackText={report.narrative_feedback} />

        {/* Rubrik Penilaian Detil */}
        <DetailedRubric aspects={report.aspect_scores} />

        {/* Tombol kembali ke home atau lihat riwayat */}
        <div className="text-center pt-5">
            <a href="/" className="text-blue-600 hover:text-blue-800 font-medium">
                Kembali ke Halaman Utama
            </a>
        </div>
      </div>
    </div>
  );
};

export default FeedbackPage;