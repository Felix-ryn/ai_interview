import React, { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom'; // Import useLocation
import { getFinalFeedback } from '../services/api'; // Ganti dengan getFinalFeedback
import ScoreCard from '../components/feedback/ScoreCard';
import NarrativeFeedback from '../components/feedback/NarrativeFeedback';
import DetailedRubric from '../components/feedback/DetailedRubric';

// Fungsi helper untuk mengurai URL query string
const useQuery = () => {
  return new URLSearchParams(useLocation().search);
}

const FeedbackPage = () => {
  // Kita mengambil ID yang diperlukan dari query string (misal: ?user=1&mq=1&role=5&level=3)
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
  }, [userId, mainQuestionId, roleId, levelId]); // Dependencies harus lengkap

  if (loading) return <div className="p-8 text-center">Memuat Laporan dan Mengevaluasi Jawaban...</div>;
  if (error) return <div className="p-8 text-center text-red-600">{error}</div>;
  if (!report) return <div className="p-8 text-center">Laporan tidak tersedia.</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-5xl mx-auto space-y-10">
        <h1 className="text-4xl font-extrabold text-gray-900 text-center">Hasil Wawancaramu</h1>

        {/* Skor Total: report.score_overall (sesuai FinalFeedback Pydantic) */}
        <ScoreCard totalScore={report.score_overall} />

        {/* Feedback Naratif: report.feedback_narrative */}
        <NarrativeFeedback feedbackText={report.feedback_narrative} />

        {/* Rubrik Penilaian Detil: report.score_metrics */}
        {/* Kita konversi objek score_metrics menjadi array yang dapat di-map */}
        <DetailedRubric scoreMetrics={report.score_metrics} />

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
