// src/components/feedback/DetailedRubric.jsx
import React from 'react';

// Fungsi helper untuk mengonversi objek score_metrics ke array yang dapat dibaca
const formatMetrics = (scoreMetrics) => {
  if (!scoreMetrics) return [];

  // Mapping kriteria teknis sesuai proposal/rubrik
  const aspectDetails = {
    relevance: { name: 'Relevance', focus: 'Kesesuaian & Kebenaran Teknis', metric: 'Cosine Similarity, Keyword Coverage' },
    clarity: { name: 'Clarity', focus: 'Kejelasan Penyampaian', metric: 'Filler Ratio, Linguistic Complexity' },
    structure: { name: 'Structure', focus: 'Keteraturan Alur (Pola STAR)', metric: 'Deteksi Pola STAR' },
    confidence: { name: 'Confidence', focus: 'Tingkat Keyakinan (Diksi)', metric: 'Analisis leksikal/hedging' },
    conciseness: { name: 'Conciseness', focus: 'Keringkasan Penyampaian', metric: 'Perbandingan Word Count' },
  };

  return Object.keys(scoreMetrics).map(key => {
    const details = aspectDetails[key.toLowerCase()] || { name: key, focus: 'N/A', metric: 'N/A' };
    return {
      ...details,
      score: Math.round(scoreMetrics[key]), // Ambil skor dari objek
    };
  });
};

const DetailedRubric = ({ scoreMetrics }) => {
  // Gunakan fungsi helper untuk mendapatkan data yang siap ditampilkan
  const data = formatMetrics(scoreMetrics);

  if (data.length === 0) {
    return <div className="p-6 bg-white rounded-xl shadow-lg text-center text-gray-500">
      Data rubrik penilaian belum tersedia.
    </div>;
  }

  return (
    <div className="bg-white p-6 rounded-xl shadow-lg">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Matriks Penilaian Terperinci</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-blue-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Aspek Penilaian</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fokus Utama (Kriteria)</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Metrik Evaluasi Teknis</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Skor</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((aspect) => (
              <tr key={aspect.name} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{aspect.name}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{aspect.focus}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{aspect.metric}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-blue-600">{aspect.score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DetailedRubric;