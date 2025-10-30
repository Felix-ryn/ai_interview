import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { getFinalFeedback } from '../services/api';
import ScoreCard from '../components/feedback/ScoreCard';
import NarrativeFeedback from '../components/feedback/NarrativeFeedback';
import DetailedRubric from '../components/feedback/DetailedRubric';

// Fungsi helper untuk mengurai URL query string
const useQuery = () => {
  return new URLSearchParams(useLocation().search);
}

const FeedbackPage = () => {
  // Kita mengambil ID yang diperlukan dari query string
  const query = useQuery();
  const userId = parseInt(query.get('user'));
  const mainQuestionId = parseInt(query.get('mq'));
  const roleId = parseInt(query.get('role'));
  const levelId = parseInt(query.get('level'));

  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Cek jika ada ID yang hilang
    if (!userId || !mainQuestionId || !roleId || !levelId) {
      setError("Parameter ID sesi (user, mq, role, level) tidak lengkap.");
      setLoading(false);
      return;
    }

    const fetchReport = async () => {
      try {
        // Panggil fungsi baru dengan semua ID yang dibutuhkan
        const data = await getFinalFeedback(userId, mainQuestionId, roleId, levelId);
        setReport(data);
      } catch (err) {
        console.error("Fetch report error:", err);
        setError("Gagal memuat laporan. Ada masalah saat memproses evaluasi final di server.");
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, [userId, mainQuestionId, roleId, levelId]);

  if (loading) return <div className="p-8 text-center text-xl font-medium text-blue-600 min-h-screen bg-gray-50 flex items-center justify-center">Memuat Laporan dan Mengevaluasi Jawaban...</div>;
  if (error) return <div className="p-8 text-center text-red-600 min-h-screen bg-gray-50 flex items-center justify-center">{error}</div>;
  if (!report) return <div className="p-8 text-center">Laporan tidak tersedia.</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-5xl mx-auto space-y-10">
        <h1 className="text-4xl font-extrabold text-gray-900 text-center border-b pb-4">Hasil Wawancaramu</h1>

        {/* Skor Total */}
        <ScoreCard totalScore={report.score_overall} />

        {/* Feedback Naratif */}
        <NarrativeFeedback feedbackText={report.feedback_narrative} />

        {/* Rubrik Penilaian Detil */}
        <DetailedRubric scoreMetrics={report.score_metrics} />

        {/* Tombol kembali ke home atau lihat riwayat */}
        <div className="text-center pt-5">
          <a href="/" className="text-blue-600 hover:text-blue-800 font-medium text-lg flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor"><path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" /></svg>
            Kembali ke Halaman Utama
          </a>
        </div>
      </div>
    </div>
  );
};

export default FeedbackPage;