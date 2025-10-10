// src/components/feedback/DetailedRubric.jsx
import React from 'react';

const DetailedRubric = ({ aspects }) => {
  // Data dummy jika report.aspect_scores belum terisi
  const dummyAspects = [
    { name: 'Relevance', score: 85, metric: 'Cosine Similarity, Keyword Coverage', focus: 'Kesesuaian jawaban' },
    { name: 'Clarity', score: 78, metric: 'Filler Ratio, Linguistic Complexity', focus: 'Kejelasan penyampaian' },
    { name: 'Structure', score: 92, metric: 'Deteksi Pola STAR', focus: 'Keteraturan alur jawaban' },
    { name: 'Confidence', score: 70, metric: 'Analisis hedging', focus: 'Tingkat keyakinan' },
    { name: 'Conciseness', score: 88, metric: 'Perbandingan Word Count', focus: 'Keringkasan penyampaian' },
  ];
  
  const data = aspects || dummyAspects;

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