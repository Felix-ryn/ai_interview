// src/pages/HomePage.jsx
import React, { useState } from 'react';
import { useInterviewSession } from '../hooks/useInterviewSession';
import Dropdown from '../components/common/Dropdown';
import Button from '../components/common/Button'; 

const ROLES = ['Data Analyst', 'Data Scientist', 'ML Engineer']; // Contoh
const LEVELS = ['Entry Level', 'Mid Level', 'Senior']; // Contoh

const HomePage = () => {
  const [name, setName] = useState('');
  const [role, setRole] = useState(ROLES[0]);
  const [level, setLevel] = useState(LEVELS[0]);
  const { loading, error, handleStartSession } = useInterviewSession();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (name && role && level) {
      // Panggil hook untuk memulai sesi dan navigasi
      handleStartSession(role, level);
    } else {
      alert("Mohon isi semua data.");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-4">
      <div className="w-full max-w-lg p-8 space-y-6 bg-white rounded-xl shadow-2xl">
        <h1 className="text-3xl font-bold text-center text-blue-800">Mulai Wawancara AI</h1>
        {error && <p className="text-red-500 text-center">{error}</p>}
        
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700">Nama</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Masukkan Nama Anda"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-3 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <Dropdown label="Pilih Posisi" options={ROLES} selected={role} setSelected={setRole} />
          <Dropdown label="Pilih Level" options={LEVELS} selected={level} setSelected={setLevel} />

          <Button type="submit" disabled={loading}>
            {loading ? 'Memulai...' : 'Mulai Wawancara'}
          </Button>
        </form>
      </div>
    </div>
  );
};

export default HomePage;